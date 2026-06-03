"""
Security search — resolves ISIN, WKN, Ticker or company name to a Yahoo Finance symbol.

Strategy:
1. Local ISIN lookup (instant)
2. Local WKN lookup (instant)
3. Local alias lookup (company names)
4. Yahoo Finance search API (online, works for all types)
5. Direct ticker fallback
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# ISIN → Yahoo Finance ticker
# ─────────────────────────────────────────────────────────────────────────────
ISIN_TO_TICKER: dict[str, str] = {
    # ── UCITS ETFs (iShares, LSE .L) ─────────────────────────────────────────
    "IE00B4L5Y983": "IWDA.L",    # iShares Core MSCI World
    "IE00B5BMR087": "CSPX.L",    # iShares Core S&P 500
    "IE00BKM4GZ66": "EIMI.L",    # iShares Core MSCI EM IMI
    "IE00B3RBWM25": "VWRL.L",    # Vanguard FTSE All-World
    "IE00B52MJY50": "CNDX.L",    # iShares NASDAQ 100
    "IE00B4L5YX21": "IJPN.L",    # iShares MSCI Japan
    "IE00B3XXRP09": "VUSA.L",    # Vanguard S&P 500 UCITS
    "IE00B3WJKG14": "VEUR.L",    # Vanguard FTSE Developed Europe
    "IE00B9F5YL18": "VAPX.L",    # Vanguard FTSE Dev. Asia Pacific ex Japan
    "IE00B95PGT31": "VJPN.L",    # Vanguard FTSE Japan
    "IE00BG143G97": "VFEM.L",    # Vanguard FTSE Emerging Markets
    "IE00BD4TXV59": "SAGG.L",    # iShares Core Global Aggregate Bond
    "IE00B3F81R35": "IGLN.L",    # iShares Physical Gold
    "IE00B4ND3602": "PHAU.L",    # WisdomTree Physical Gold
    "IE00B4MCHH60": "PHAG.L",    # WisdomTree Physical Silver
    "IE00B1FZS350": "IEMM.L",    # iShares MSCI EM
    "IE00B0M63177": "IMEU.L",    # iShares MSCI Europe
    "IE00B02KXH56": "IUSA.L",    # iShares S&P 500 (older)
    "IE00B53HP851": "AGGH.L",    # iShares Core Global Aggregate Bond
    "IE00BYZK4552": "SPPW.L",    # SPDR S&P World
    "IE00BFY0GT14": "SPYY.L",    # SPDR S&P 500 UCITS
    "IE00B1XNHC34": "IQQW.L",    # iShares MSCI World Quality
    "IE00B52SF786": "MEUD.L",    # Lyxor MSCI World
    "IE00BJ0KDQ92": "XDWL.L",    # Xtrackers MSCI World
    # ── UCITS ETFs (Xtrackers/Amundi, LSE) ───────────────────────────────────
    "LU0392494562": "XDWD.L",    # Xtrackers MSCI World Swap
    "LU0274208692": "EXSA.DE",   # iShares EURO STOXX 50 (Xetra)
    "LU1681043599": "CW8.PA",    # Amundi MSCI World (Paris)
    "LU0136234654": "DBXW.DE",   # Xtrackers MSCI World
    "LU0378449770": "XMEM.L",    # Xtrackers MSCI EM
    "LU0875160326": "LCUW.PA",   # Lyxor MSCI World
    # ── Deutsche ETFs (Xetra .DE) ─────────────────────────────────────────────
    "DE0005933931": "EXS1.DE",   # iShares Core DAX
    "DE000A0F5UF5": "EXXT.DE",   # iShares NASDAQ-100 (Xetra)
    "DE0005933956": "EXS3.DE",   # iShares MDAX
    "DE0005933972": "EUN2.DE",   # iShares EURO STOXX 50
    # ── US ETFs (no suffix) ───────────────────────────────────────────────────
    "US9229087690": "VTI",       # Vanguard Total Stock Market
    "US78462F1030": "SPY",       # SPDR S&P 500
    "US46137V1008": "QQQ",       # Invesco QQQ
    "US4642874329": "IVV",       # iShares Core S&P 500
    "US9219097683": "VOO",       # Vanguard S&P 500
    "US92189F1066": "VT",        # Vanguard Total World
    "US9220427424": "VEA",       # Vanguard FTSE Developed Markets
    "US9220420440": "VWO",       # Vanguard FTSE Emerging Markets
    "US46429B6974": "IEFA",      # iShares Core MSCI EAFE
    "US4642862184": "EEM",       # iShares MSCI EM
    "US78468R6633": "GLD",       # SPDR Gold Shares
    "US46434G8473": "IAU",       # iShares Gold Trust
    "US78468R3779": "SLV",       # iShares Silver Trust
    "US81369Y8030": "SCHD",      # Schwab US Dividend Equity
    "US0378331005": "AAPL",      # Apple
    "US5949181045": "MSFT",      # Microsoft
    "US0231351067": "AMZN",      # Amazon
    "US02079K3059": "GOOGL",     # Alphabet A
    "US30303M1027": "META",      # Meta Platforms
    "US67066G1040": "NVDA",      # NVIDIA
    "US88160R1014": "TSLA",      # Tesla
    "US4592001014": "IBM",       # IBM
    "US4180561072": "HAS",       # Hasbro
    "US46625H1005": "JPM",       # JPMorgan Chase
    "US09075V1026": "BIO",       # Bio-Techne
    "US09702L1008": "COIN",      # Coinbase
    "US22788C1053": "CRWD",      # CrowdStrike
    "US23804L1035": "DDOG",      # Datadog
    "US83406F1021": "SNOW",      # Snowflake
    "US18915M1071": "NET",       # Cloudflare
    # ── Deutsche Aktien (Xetra .DE) ───────────────────────────────────────────
    "DE0007164600": "SAP.DE",    # SAP
    "DE0007236101": "SIE.DE",    # Siemens
    "DE0008404005": "ALV.DE",    # Allianz
    "DE0005140008": "DBK.DE",    # Deutsche Bank
    "DE000BASF111": "BAS.DE",    # BASF
    "DE000BAY0017": "BAYN.DE",   # Bayer
    "DE000A1EWWW0": "ADS.DE",    # Adidas
    "DE0005190003": "BMW.DE",    # BMW
    "DE0007100000": "MBG.DE",    # Mercedes-Benz
    "DE0007664039": "VOW3.DE",   # Volkswagen Vz
    "DE0008469008": "DAX",       # DAX Index (ETF proxy)
    "DE000A0D8Q49": "RHM.DE",    # Rheinmetall
    "DE0005552004": "DTE.DE",    # Deutsche Telekom
    "DE0005785604": "FRE.DE",    # Fresenius
    "DE0008232125": "LHA.DE",    # Lufthansa
    "DE0005435345": "AIXA.DE",   # Aixtron
    "DE0006048432": "HNR1.DE",   # Hannover Rück
    "DE000CBK1001": "CBK.DE",    # Commerzbank
    # ── Schweizer Aktien ──────────────────────────────────────────────────────
    "CH0012221716": "ABB.SW",    # ABB
    "CH0012032048": "ROG.SW",    # Roche
    "CH0038389992": "NESN.SW",   # Nestlé
    "CH0012221716": "ABB.SW",    # ABB
    "CH0244767585": "UHR.SW",    # Swatch
    # ── Niederländische / Europäische Aktien ─────────────────────────────────
    "NL0010273215": "ASML",      # ASML Holding
    "FR0000131104": "BNP.PA",    # BNP Paribas
    "FR0000121014": "MC.PA",     # LVMH
    "FR0000120271": "AI.PA",     # Air Liquide
    "FR0000120578": "SAN.PA",    # Sanofi
    "DK0060534915": "NOVO-B.CO", # Novo Nordisk B
}

# ─────────────────────────────────────────────────────────────────────────────
# WKN → Yahoo Finance ticker
# ─────────────────────────────────────────────────────────────────────────────
WKN_TO_TICKER: dict[str, str] = {
    # ── ETFs ──────────────────────────────────────────────────────────────────
    "A0RPWH": "IWDA.L",     # iShares Core MSCI World
    "A0YEDG": "CSPX.L",     # iShares Core S&P 500
    "A111X9":  "EIMI.L",    # iShares Core MSCI EM IMI
    "A1JX52":  "VWRL.L",    # Vanguard FTSE All-World
    "A0HGWC": "EXSA.DE",    # iShares EURO STOXX 50
    "A0F5UG":  "EXXT.DE",   # iShares NASDAQ-100 (Xetra)
    "593393":  "EXS1.DE",   # iShares Core DAX
    "A0LGQL": "EUN2.DE",    # iShares EURO STOXX 50 (USD)
    "DBX1MW": "XDWD.L",     # Xtrackers MSCI World Swap
    "LYX0YD": "CW8.PA",     # Amundi MSCI World
    "A1C9KK": "VUSA.L",     # Vanguard S&P 500 UCITS
    "A14YPA": "SPPW.L",     # SPDR S&P World
    "A0Q8NE": "PHAU.L",     # WisdomTree Physical Gold
    "A0N62G": "IGLN.L",     # iShares Physical Gold
    # ── Deutsche Aktien ────────────────────────────────────────────────────────
    "716460":  "SAP.DE",     # SAP
    "723610":  "SIE.DE",     # Siemens
    "840400":  "ALV.DE",     # Allianz
    "514000":  "DBK.DE",     # Deutsche Bank
    "BASF11":  "BAS.DE",     # BASF
    "BAY001":  "BAYN.DE",    # Bayer
    "A1EWWW": "ADS.DE",     # Adidas
    "519000":  "BMW.DE",     # BMW
    "710000":  "MBG.DE",     # Mercedes-Benz
    "766403":  "VOW3.DE",    # Volkswagen Vz
    "703000":  "DTE.DE",     # Deutsche Telekom
    "578560":  "FRE.DE",     # Fresenius
    "823212":  "LHA.DE",     # Lufthansa
    "A0D8Q4": "RHM.DE",     # Rheinmetall
    "555200":  "CBK.DE",     # Commerzbank
    # ── US Aktien ─────────────────────────────────────────────────────────────
    "865985":  "AAPL",       # Apple
    "870747":  "MSFT",       # Microsoft
    "906866":  "AMZN",       # Amazon
    "A14Y6F":  "GOOGL",      # Alphabet A
    "A1JWVX":  "META",       # Meta Platforms
    "918422":  "NVDA",       # NVIDIA
    "A1CX3T":  "TSLA",       # Tesla
    "A2QP7J":  "COIN",       # Coinbase
    "A2PZ0R":  "CRWD",       # CrowdStrike
    "A2QMVK": "DDOG",       # Datadog
    "A2QHKM": "SNOW",       # Snowflake
    "A2QHKN": "NET",        # Cloudflare
    "850663":  "JPM",        # JPMorgan Chase
    "A0HL9Z":  "BRK-B",     # Berkshire Hathaway B
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _looks_like_isin(s: str) -> bool:
    return bool(re.match(r'^[A-Z]{2}[A-Z0-9]{10}$', s.upper()))


def _looks_like_wkn(s: str) -> bool:
    """WKN: 6 alphanumeric chars, German securities identifier."""
    return bool(re.match(r'^[A-Z0-9]{6}$', s.upper()))


def _is_valid_result(sym: str, name: str) -> bool:
    """Filtert fehlerhafte oder unbrauchbare Suchergebnisse raus."""
    if not sym or len(sym) > 20:
        return False
    # Keine Einträge die wie Fehlercodes aussehen
    skip = ("error", "invalid", "undefined", "null", "none", "n/a")
    if sym.lower() in skip or name.lower() in skip:
        return False
    # Keine Symbole mit Sonderzeichen außer . und -
    if any(c in sym for c in ("/", "\\", ":", "?", "!", "@")):
        return False
    return True


def _yahoo_search(query: str, max_results: int = 8) -> list[dict]:
    """
    Search Yahoo Finance for a security. Returns list of
    {'symbol', 'name', 'type', 'exchange'} dicts.
    """
    import warnings, io, sys
    results: list[dict] = []

    # Strategy A: yfinance.Search (available in yfinance >= 0.2.37)
    try:
        import yfinance as yf
        if hasattr(yf, "Search"):
            # yfinance kann Warnungen/Fehlermeldungen nach stderr schreiben —
            # diese während der Suche unterdrücken damit Streamlit sie nicht anzeigt
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                _old_stderr = sys.stderr
                sys.stderr = io.StringIO()
                try:
                    sr = yf.Search(query, max_results=max_results, news_count=0)
                    quotes = sr.quotes or []
                finally:
                    sys.stderr = _old_stderr

            for q in quotes:
                sym  = q.get("symbol", "").strip()
                name = q.get("longname") or q.get("shortname") or sym
                if _is_valid_result(sym, name):
                    results.append({
                        "symbol":   sym,
                        "name":     name,
                        "type":     q.get("quoteType", ""),
                        "exchange": q.get("exchange", ""),
                    })
            if results:
                return results
    except Exception as e:
        logger.debug(f"yf.Search failed for '{query}': {e}")

    # Strategy B: direct Yahoo Finance search endpoint
    try:
        import requests
        url = (
            "https://query2.finance.yahoo.com/v1/finance/search"
            f"?q={requests.utils.quote(query)}"
            "&quotesCount=8&newsCount=0&enableFuzzyQuery=false"
        )
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=6)
        resp.raise_for_status()
        for q in resp.json().get("quotes", [])[:max_results]:
            sym  = q.get("symbol", "").strip()
            name = q.get("longname") or q.get("shortname") or sym
            if _is_valid_result(sym, name):
                results.append({
                    "symbol":   sym,
                    "name":     name,
                    "type":     q.get("quoteType", ""),
                    "exchange": q.get("exchange", ""),
                })
        if results:
            return results
    except Exception as e:
        logger.debug(f"Yahoo Finance search API failed for '{query}': {e}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def search_securities(query: str, max_results: int = 8) -> list[dict]:
    """
    Search for securities by ISIN, WKN, ticker or company name.

    Returns list of:
        {
          'symbol':   str,   # Yahoo Finance ticker (e.g. 'AAPL', 'SIE.DE')
          'name':     str,   # Company / fund name
          'type':     str,   # 'EQUITY', 'ETF', 'INDEX', ...
          'exchange': str,   # Exchange code
          'method':   str,   # How it was found
        }
    """
    if not query or not query.strip():
        return []

    q = query.strip()
    q_up = q.upper()

    # ── 1. ISIN local lookup ──────────────────────────────────────────────────
    if _looks_like_isin(q_up):
        local = ISIN_TO_TICKER.get(q_up)
        if local:
            return [{"symbol": local, "name": q_up, "type": "", "exchange": "", "method": "isin_local"}]
        # Not in local dict → search Yahoo with ISIN
        results = _yahoo_search(q_up, max_results)
        for r in results:
            r["method"] = "isin_yahoo"
        return results

    # ── 2. WKN local lookup ───────────────────────────────────────────────────
    if _looks_like_wkn(q_up):
        local = WKN_TO_TICKER.get(q_up)
        if local:
            return [{"symbol": local, "name": q_up, "type": "", "exchange": "", "method": "wkn_local"}]
        # Not in local dict → search Yahoo with WKN
        results = _yahoo_search(q_up, max_results)
        for r in results:
            r["method"] = "wkn_yahoo"
        return results

    # ── 3. Yahoo Finance search (name or ticker fragment) ────────────────────
    results = _yahoo_search(q, max_results)
    for r in results:
        r["method"] = "yahoo_search"
    return results


def resolve_to_ticker(query: str) -> Optional[str]:
    """
    Quick single-result resolve: returns best-match Yahoo Finance ticker or None.
    """
    results = search_securities(query, max_results=1)
    return results[0]["symbol"] if results else None
