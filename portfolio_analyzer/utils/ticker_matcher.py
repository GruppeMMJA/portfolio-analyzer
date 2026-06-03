"""
Ticker-Matcher: Fuzzy-Matching von OCR-Ergebnissen auf echte Ticker.

Verwendet mehrere Strategien:
1. Exaktes Match (Ticker oder ISIN)
2. Fuzzy-Match auf Namen (Levenshtein-Distanz)
3. Bekannte Abkürzungen/Aliase
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Bekannte Abkürzungen und Aliase, wie sie in Broker-Depots auftauchen
KNOWN_ALIASES = {
    # ETFs
    "ishares core msci world": "IWDA",
    "ish. core msci wld": "IWDA",
    "ishares msci world": "IWDA",
    "ishr core msci world": "IWDA",
    "ishares core s&p 500": "CSPX",
    "ish. core s&p 500": "CSPX",
    "ishares s&p 500": "IVV",
    "vanguard s&p 500": "VOO",
    "vanguard ftse all-world": "VWRL",
    "vang. ftse all-world": "VWRL",
    "vanguard total world": "VT",
    "xtrackers msci world": "XDWD",
    "invesco qqq": "QQQ",
    "ishares nasdaq 100": "CNDX",
    "amundi msci world": "CW8",
    "ishares core dax": "EXS1",
    "ishares euro stoxx 50": "SX5S",
    "ishares msci em": "IEEM",
    "ishares core msci em": "EIMI",
    "spdr s&p 500": "SPY",

    # Bekannte Aktien
    "apple": "AAPL",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "alphabet": "GOOGL",
    "google": "GOOGL",
    "meta platforms": "META",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
    "tesla": "TSLA",
    "palantir": "PLTR",
    "palantir technologies": "PLTR",
    "taiwan semiconductor": "TSM",
    "tsmc": "TSM",
    "broadcom": "AVGO",
    "eli lilly": "LLY",
    "jpmorgan chase": "JPM",
    "berkshire hathaway": "BRK-B",
    "johnson & johnson": "JNJ",
    "visa": "V",
    "mastercard": "MA",
    "unitedhealth": "UNH",
    "procter & gamble": "PG",
    "home depot": "HD",
    "coca-cola": "KO",
    "pepsico": "PEP",
    "adobe": "ADBE",
    "salesforce": "CRM",
    "netflix": "NFLX",
    "costco": "COST",
    "walt disney": "DIS",
    "coinbase": "COIN",
    "crowdstrike": "CRWD",
    "datadog": "DDOG",
    "snowflake": "SNOW",
    "cloudflare": "NET",
    "rheinmetall": "RHM.DE",
    "sap": "SAP",
    "siemens": "SIE.DE",
    "allianz": "ALV.DE",
    "deutsche bank": "DBK.DE",
    "basf": "BAS.DE",
    "bayer": "BAYN.DE",
    "adidas": "ADS.DE",
    "mercedes-benz": "MBG.DE",
    "bmw": "BMW.DE",
    "volkswagen": "VOW3.DE",
    "lvmh": "MC.PA",
    "asml": "ASML",
    "novo nordisk": "NOVO-B.CO",
    "nestle": "NESN.SW",
    "roche": "ROG.SW",
}

# Ticker → yfinance-kompatibler Ticker (für UCITS-ETFs ohne Suffix)
TICKER_TO_YF: dict[str, str] = {
    # iShares (LSE)
    "IWDA": "IWDA.L",   "CSPX": "CSPX.L",   "EIMI": "EIMI.L",
    "VWRL": "VWRL.L",   "CNDX": "CNDX.L",   "IEMM": "IEMM.L",
    "RBOT": "RBOT.L",   "IBTU": "IBTU.L",   "AGGH": "AGGH.L",
    "IUSB": "IUSB.L",   "SPPW": "SPPW.L",   "IGLN": "IGLN.L",
    "PHAU": "PHAU.L",   "PHAG": "PHAG.L",   "EGLN": "EGLN.L",
    "VUSA": "VUSA.L",   "VEUR": "VEUR.L",   "VAPX": "VAPX.L",
    "VJPN": "VJPN.L",   "VMID": "VMID.L",   "VFEM": "VFEM.L",
    "IQQW": "IQQW.L",   "MEUD": "MEUD.L",   "IQQH": "IQQH.L",
    # Xtrackers (LSE / Xetra)
    "XDWD": "XDWD.L",   "XDWH": "XDWH.L",   "XMAW": "XMAW.L",
    "XMEM": "XMEM.L",   "XGDU": "XGDU.L",
    # Amundi/Xtrackers Gold/Silber (Xetra)
    "XAD5": "XAD5.DE",  "XAD6": "XAD6.DE",  "XADS": "XADS.DE",
    # iShares Xetra
    "EXSA": "EXSA.DE",  "EXS1": "EXS1.DE",  "EXXT": "EXXT.DE",
    "EUNL": "EUNL.DE",  "EUN2": "EUN2.DE",  "EXHB": "EXHB.DE",
    "DBBX": "DBBX.DE",
    # Krypto ETPs
    "BTCE": "BTCE.DE",  "XBTE": "XBTE.DE",
    # Amundi (Euronext Paris)
    "CW8":  "CW8.PA",   "LCUW": "LCUW.PA",
}

# ISIN → Ticker Mapping für gängige europäische ETFs
ISIN_TO_TICKER = {
    # UCITS-ETFs (Irland/Luxemburg) → London Stock Exchange (.L)
    "IE00B4L5Y983": "IWDA.L",   # iShares Core MSCI World
    "IE00B5BMR087": "CSPX.L",   # iShares Core S&P 500
    "IE00BKM4GZ66": "EIMI.L",   # iShares Core MSCI EM IMI
    "IE00B3RBWM25": "VWRL.L",   # Vanguard FTSE All-World
    "IE00B52MJY50": "CNDX.L",   # iShares NASDAQ 100
    "IE00B4L5YX21": "IJPN.L",   # iShares MSCI Japan
    "IE00BJ0KDQ92": "XDWL.L",   # Xtrackers MSCI World
    "IE00B3XXRP09": "VUSA.L",   # Vanguard S&P 500
    "LU0392494562": "XDWD.L",   # Xtrackers MSCI World Swap
    "LU1681043599": "CW8.PA",   # Amundi MSCI World (Euronext Paris)
    "LU0274208692": "EXSA.DE",  # iShares EURO STOXX 50 (Xetra)
    # Deutsche ETFs → Xetra (.DE)
    "DE0005933931": "EXS1.DE",  # iShares Core DAX
    "DE000A0F5UF5": "EXXT.DE",  # iShares NASDAQ-100 (Xetra)
    # US-ETFs (kein Suffix nötig)
    "US9229087690": "VTI",      # Vanguard Total Stock Market
    "US78462F1030": "SPY",      # SPDR S&P 500
    "US46137V1008": "QQQ",      # Invesco QQQ
    "US4642874329": "IVV",      # iShares Core S&P 500
    "US9219097683": "VOO",      # Vanguard S&P 500
    "US92189F1066": "VT",       # Vanguard Total World
}


@dataclass
class MatchResult:
    """Ergebnis eines Ticker-Matchings."""
    original_name: str       # Originalname aus OCR
    matched_ticker: str      # Gematchter Ticker
    matched_name: str        # Aufgelöster Name
    match_type: str          # "exact_ticker", "isin", "alias", "fuzzy"
    confidence: float        # 0.0 bis 1.0


class TickerMatcher:
    """
    Matched OCR-Ergebnisse auf echte Ticker.
    Kombiniert mehrere Matching-Strategien.
    """

    def match(
        self,
        name: str,
        ticker_hint: str = "",
        isin_hint: str = "",
    ) -> MatchResult:
        """
        Versucht einen Ticker zu matchen.

        Strategie-Reihenfolge:
        1. ISIN → Ticker (exakt)
        2. Ticker-Hint direkt verwenden (wenn vorhanden und plausibel)
        3. Name → Bekannte Aliase
        4. Fuzzy-Match auf Aliase

        Args:
            name: Name des Wertpapiers (z.B. aus OCR)
            ticker_hint: Optionaler Ticker-Hinweis aus OCR
            isin_hint: Optionale ISIN aus OCR

        Returns:
            MatchResult mit dem besten Match.
        """
        # 1. ISIN-Match
        if isin_hint:
            isin_clean = isin_hint.strip().upper()
            if isin_clean in ISIN_TO_TICKER:
                return MatchResult(
                    original_name=name,
                    matched_ticker=ISIN_TO_TICKER[isin_clean],
                    matched_name=name,
                    match_type="isin",
                    confidence=0.99,
                )

        # 2. Ticker-Hint direkt verwenden
        if ticker_hint:
            ticker_clean = ticker_hint.strip().upper()
            if len(ticker_clean) >= 1 and len(ticker_clean) <= 10:
                return MatchResult(
                    original_name=name,
                    matched_ticker=ticker_clean,
                    matched_name=name,
                    match_type="exact_ticker",
                    confidence=0.95,
                )

        # 3. Bekannte Aliase (exakt)
        name_lower = name.lower().strip()
        if name_lower in KNOWN_ALIASES:
            return MatchResult(
                original_name=name,
                matched_ticker=KNOWN_ALIASES[name_lower],
                matched_name=name,
                match_type="alias",
                confidence=0.90,
            )

        # 4. Fuzzy-Match auf Aliase
        best_match = self._fuzzy_match(name_lower)
        if best_match:
            return best_match

        # 5. Kein Match — Name als Ticker verwenden (User muss korrigieren)
        logger.warning(f"Kein Match für '{name}'. Bitte manuell korrigieren.")
        # Versuch: Ersten sinnvollen Teil als Ticker extrahieren
        fallback_ticker = name.split()[0].upper() if name.split() else "UNKNOWN"
        return MatchResult(
            original_name=name,
            matched_ticker=fallback_ticker,
            matched_name=name,
            match_type="unmatched",
            confidence=0.3,
        )

    def _fuzzy_match(self, name: str) -> Optional[MatchResult]:
        """Fuzzy-Matching mit Levenshtein-Distanz."""
        try:
            from thefuzz import fuzz
        except ImportError:
            # Einfaches Substring-Matching als Fallback
            return self._simple_match(name)

        best_score = 0
        best_alias = ""
        best_ticker = ""

        for alias, ticker in KNOWN_ALIASES.items():
            # Kombiniere mehrere Fuzzy-Metriken
            ratio = fuzz.ratio(name, alias)
            partial = fuzz.partial_ratio(name, alias)
            token_sort = fuzz.token_sort_ratio(name, alias)

            # Gewichteter Score
            score = 0.3 * ratio + 0.4 * partial + 0.3 * token_sort

            if score > best_score:
                best_score = score
                best_alias = alias
                best_ticker = ticker

        if best_score >= 70:
            confidence = min(best_score / 100, 0.95)
            return MatchResult(
                original_name=name,
                matched_ticker=best_ticker,
                matched_name=best_alias,
                match_type="fuzzy",
                confidence=round(confidence, 2),
            )

        return None

    def _simple_match(self, name: str) -> Optional[MatchResult]:
        """Einfaches Substring-Matching als Fallback ohne thefuzz."""
        name_words = set(name.lower().split())

        best_overlap = 0
        best_alias = ""
        best_ticker = ""

        for alias, ticker in KNOWN_ALIASES.items():
            alias_words = set(alias.split())
            overlap = len(name_words & alias_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_alias = alias
                best_ticker = ticker

        if best_overlap >= 2:
            return MatchResult(
                original_name=name,
                matched_ticker=best_ticker,
                matched_name=best_alias,
                match_type="fuzzy",
                confidence=0.7,
            )

        return None
