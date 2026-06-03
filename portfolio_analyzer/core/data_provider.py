"""
Daten-Provider: Abstrakte Basisklasse + yfinance-Implementierung.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from core.portfolio import AssetType, Holding, Position
from utils.constants import (
    COUNTRY_TO_CURRENCY,
    GICS_SECTORS,
    EWMA_LAMBDA,
    STOCK_METADATA,
    YFINANCE_SECTOR_TO_GICS,
    get_etf_country_distribution,
    ETF_TICKER_TO_CANONICAL,
)

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Abstrakte Basisklasse für Datenquellen."""

    @abstractmethod
    def get_security_info(self, ticker: str) -> dict:
        """
        Stammdaten einer Position abrufen.
        Returns: {name, isin, country, currency, gics_sector, asset_type}
        """
        ...

    @abstractmethod
    def get_etf_holdings(self, ticker: str, top_n: int = 50) -> list[dict]:
        """
        Top-N Holdings eines ETF abrufen.
        Returns: [{ticker, name, weight, country, currency, gics_sector}, ...]
        """
        ...

    @abstractmethod
    def get_historical_prices(
        self, tickers: list[str], years: int = 2
    ) -> pd.DataFrame:
        """
        Historische Tagesschlusskurse abrufen.
        Returns: DataFrame mit Datum als Index, Ticker als Spalten.
        """
        ...

    @abstractmethod
    def get_benchmark_prices(
        self, benchmark_ticker: str, years: int = 2
    ) -> pd.Series:
        """Historische Kurse eines Benchmark-Index."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Prüfen ob die Datenquelle verfügbar ist."""
        ...

    def get_etf_sector_weights(self, ticker: str) -> dict[int, float]:
        """
        Sektor-Gewichtungen eines ETF (GICS-Code → Gewicht 0–1).
        Standard-Implementierung gibt leeres Dict zurück.
        Wird von spezifischen Providern überschrieben.
        """
        return {}

    def enrich_position(self, position: Position) -> Position:
        """
        Position mit Stammdaten anreichern (Land, Sektor, Währung, Holdings).
        """
        info = self.get_security_info(position.ticker)

        position.name = info.get("name", position.name) or position.name
        position.isin = info.get("isin", position.isin) or position.isin
        position.country = info.get("country", position.country) or position.country
        position.trade_currency = (
            info.get("currency", position.trade_currency) or position.trade_currency
        )
        position.gics_sector = info.get("gics_sector", position.gics_sector) or 0
        position.gics_sector_name = GICS_SECTORS.get(
            position.gics_sector, "Unbekannt"
        )

        asset_type_str = info.get("asset_type", "")
        if asset_type_str == "ETF":
            position.asset_type = AssetType.ETF
        elif asset_type_str == "STOCK":
            position.asset_type = AssetType.STOCK
        else:
            position.asset_type = AssetType.UNKNOWN

        # ETF-Holdings auflösen
        if position.is_etf:
            try:
                raw_holdings = self.get_etf_holdings(position.ticker)
                position.holdings = [
                    Holding(
                        ticker=h.get("ticker", ""),
                        name=h.get("name", ""),
                        weight=h.get("weight", 0.0),
                        country=h.get("country", ""),
                        currency=h.get("currency", ""),
                        gics_sector=h.get("gics_sector", 0),
                    )
                    for h in raw_holdings
                ]
            except Exception as e:
                logger.warning(f"ETF-Holdings für {position.ticker} nicht verfügbar: {e}")

            # Statische Länderverteilung aus bekannter Datenbank setzen (höchste Priorität)
            position.etf_country_weights = get_etf_country_distribution(position.ticker)

            # ETF-Sektor-Gewichtungen laden (Fallback wenn Holdings keine Sektor-Daten haben)
            try:
                position.etf_sector_weights = self.get_etf_sector_weights(position.ticker)
            except Exception as e:
                logger.debug(f"ETF-Sektor-Gewichtungen für {position.ticker} nicht verfügbar: {e}")

        return position

    def get_returns(
        self, tickers: list[str], years: int = 2
    ) -> pd.DataFrame:
        """
        Tägliche log-Renditen berechnen.
        Returns: DataFrame mit Datum als Index, Ticker als Spalten.
        """
        prices = self.get_historical_prices(tickers, years=years)
        if prices.empty:
            return pd.DataFrame()

        # Log-Renditen: ln(P_t / P_{t-1})
        returns = np.log(prices / prices.shift(1)).dropna()
        return returns


# ---------------------------------------------------------------------------
# Börsen-Suffix → ISO-Ländercode (für ETF-Holdings ohne explizite Country-Angabe)
# ---------------------------------------------------------------------------
_SUFFIX_TO_COUNTRY: dict[str, str] = {
    ".L":   "GB", ".IL":  "GB",
    ".DE":  "DE", ".F":   "DE", ".MU":  "DE", ".BE":  "DE", ".HM":  "DE",
    ".PA":  "FR",
    ".AS":  "NL",
    ".SW":  "CH",
    ".MI":  "IT",
    ".MC":  "ES",
    ".HE":  "FI",
    ".ST":  "SE",
    ".CO":  "DK",
    ".OL":  "NO",
    ".VI":  "AT",
    ".BR":  "BE",
    ".LS":  "PT",
    ".IE":  "IE",
    ".T":   "JP",
    ".HK":  "HK",
    ".AX":  "AU",
    ".SI":  "SG",
    ".KS":  "KR", ".KQ": "KR",
    ".TW":  "TW", ".TWO": "TW",
    ".NS":  "IN", ".BO":  "IN",
    ".SA":  "BR",
    ".MX":  "MX",
    ".JK":  "ID",
    ".BK":  "TH",
    ".KL":  "MY",
    ".PS":  "PH",
    ".SN":  "CL",
    ".BA":  "AR",
    ".TO":  "CA", ".V":   "CA",
    ".TA":  "IL",
    ".WA":  "PL",
    ".PR":  "CZ",
    ".BUD": "HU",
    ".IS":  "TR",
    ".JO":  "ZA",
    ".SG":  "SG",
    ".NZ":  "NZ",
    ".AT":  "AT",
}


# ---------------------------------------------------------------------------
# yfinance-Implementierung
# ---------------------------------------------------------------------------

class YFinanceProvider(DataProvider):
    """
    Fallback-Provider über Yahoo Finance (yfinance).
    Kostenlos, aber limitiert: keine ETF-Holdings, weniger Stammdaten.
    """

    # Börsenkürzel → ISO-Ländercode
    _EXCHANGE_TO_COUNTRY: dict[str, str] = {
        # USA
        "NGM": "US", "NMS": "US", "NYQ": "US", "PCX": "US",
        "BTS": "US", "ASE": "US", "PNK": "US",
        # Europa
        "LSE": "GB", "IOB": "GB",
        "XETRA": "DE", "FRA": "DE", "STU": "DE", "HAM": "DE",
        "PAR": "FR", "AMS": "NL", "BRU": "BE", "LIS": "PT",
        "MIL": "IT", "MCE": "ES", "HEL": "FI", "OSL": "NO",
        "STO": "SE", "CPH": "DK", "VIE": "AT", "ZUR": "CH",
        "WSE": "PL",
        # Asien-Pazifik
        "HKG": "HK", "TSE": "JP", "KSC": "KR", "KOE": "KR",
        "TAI": "TW", "TWO": "TW", "NSI": "IN", "BSE": "IN",
        "ASX": "AU", "SGX": "SG",
        # Sonstige
        "SAO": "BR", "MEX": "MX",
    }
    _MARKET_TO_COUNTRY: dict[str, str] = {
        "us_market": "US", "gb_market": "GB", "de_market": "DE",
        "fr_market": "FR", "jp_market": "JP", "hk_market": "HK",
        "kr_market": "KR", "au_market": "AU", "sg_market": "SG",
        "in_market": "IN", "br_market": "BR", "ca_market": "CA",
        "ch_market": "CH", "nl_market": "NL", "se_market": "SE",
        "dk_market": "DK", "no_market": "NO",
    }

    # Ticker die yfinance fälschlicherweise als EQUITY klassifiziert, aber ETFs/ETCs sind.
    # Wird automatisch mit allen Einträgen aus ETF_TICKER_TO_CANONICAL befüllt.
    _KNOWN_ETFS: set[str] = (
        {t.lower().split(".")[0] for t in ETF_TICKER_TO_CANONICAL}
        | {t.lower() for t in ETF_TICKER_TO_CANONICAL}
        | {
            # Gold/Rohstoff ETCs (Xetra)
            "xad5", "xad6", "xads", "egln", "phau", "igln", "sgln", "4gld",
            "wgld", "gzur", "phag", "crud", "loil",
            # Krypto ETPs
            "btce", "xbte", "ethe", "vbtc",
        }
    )

    def get_security_info(self, ticker: str) -> dict:
        import yfinance as yf
        from utils.search import resolve_to_ticker, _looks_like_isin, _looks_like_wkn
        from utils.search import ISIN_TO_TICKER, WKN_TO_TICKER

        ticker = ticker.strip()
        q_up = ticker.upper()

        # ── ISIN / WKN / Name auflösen ────────────────────────────────────────
        if _looks_like_isin(q_up):
            resolved = ISIN_TO_TICKER.get(q_up) or resolve_to_ticker(q_up)
            if resolved:
                logger.info(f"ISIN {ticker} → {resolved}")
                ticker = resolved
            else:
                return {"name": ticker, "asset_type": "UNKNOWN",
                        "_error": f"ISIN {ticker} nicht auflösbar"}

        elif _looks_like_wkn(q_up):
            resolved = WKN_TO_TICKER.get(q_up) or resolve_to_ticker(q_up)
            if resolved:
                logger.info(f"WKN {ticker} → {resolved}")
                ticker = resolved

        # ── Ticker in yfinance nachschlagen ───────────────────────────────────
        def _fetch(sym: str) -> dict:
            try:
                t = yf.Ticker(sym)
                info = t.fast_info if hasattr(t, "fast_info") else {}
                # fast_info is faster but limited — also grab full info
                full = t.info or {}
                return full
            except Exception as e:
                logger.debug(f"yfinance fetch failed for {sym}: {e}")
                return {}

        info = _fetch(ticker)

        # Wenn kein quoteType → Ticker nicht gefunden. Suffix-Fallback versuchen.
        if not info.get("quoteType") and "." not in ticker:
            for suffix in [".L", ".DE", ".PA", ".AS", ".SW", ".MI", ".MC"]:
                alt_info = _fetch(ticker + suffix)
                if alt_info.get("quoteType"):
                    logger.info(f"{ticker} → {ticker + suffix}")
                    ticker = ticker + suffix
                    info = alt_info
                    break

        # Wenn immer noch kein Ergebnis → Yahoo-Search versuchen
        if not info.get("quoteType"):
            from utils.search import resolve_to_ticker as _resolve
            found = _resolve(ticker)
            if found and found.upper() != ticker.upper():
                logger.info(f"Search: {ticker} → {found}")
                info = _fetch(found)
                if info.get("quoteType"):
                    ticker = found

        # Asset-Typ bestimmen
        # _KNOWN_ETFS überschreibt yfinance wenn dieser fälschlicherweise EQUITY zurückgibt
        base_ticker = ticker.split(".")[0].lower()
        quote_type = info.get("quoteType", "").upper()
        if quote_type == "ETF" or base_ticker in self._KNOWN_ETFS:
            asset_type = "ETF"
        elif quote_type in ("EQUITY", "STOCK"):
            asset_type = "STOCK"
        else:
            asset_type = "UNKNOWN"

        # GICS-Sektor mappen
        sector_name = info.get("sector", "")
        gics_sector = self._map_sector_to_gics(sector_name)

        # Land: erst direktes Country-Feld, dann aus Exchange/Market ableiten
        country = info.get("country", "")
        country_code = self._country_name_to_iso(country)
        if not country_code:
            exchange = info.get("exchange", "")
            market = info.get("market", "")
            country_code = (
                self._EXCHANGE_TO_COUNTRY.get(exchange, "")
                or self._MARKET_TO_COUNTRY.get(market, "")
            )

        return {
            "name": info.get("longName", info.get("shortName", ticker)),
            "isin": info.get("isin", ""),
            "country": country_code,
            "currency": info.get("currency", ""),
            "gics_sector": gics_sector,
            "asset_type": asset_type,
        }

    def get_etf_holdings(self, ticker: str, top_n: int = 50) -> list[dict]:
        """
        ETF-Holdings über yfinance funds_data abrufen.
        Unterstützt yfinance >= 0.2.x (funds_data.top_holdings).
        Hinweis: Für UCITS-ETFs muss das Börsenkürzel angegeben werden
        (z.B. IWDA.L statt IWDA, CSPX.L statt CSPX).
        """
        import yfinance as yf

        try:
            etf = yf.Ticker(ticker)
            df = None

            # Modernes yfinance-API (>= 0.2.x): funds_data.top_holdings
            if hasattr(etf, "funds_data"):
                try:
                    df = etf.funds_data.top_holdings
                except Exception as e:
                    logger.debug(f"funds_data.top_holdings fehlgeschlagen für {ticker}: {e}")

            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                logger.warning(
                    f"ETF-Holdings für {ticker} nicht verfügbar. "
                    f"Für UCITS-ETFs Börsensuffix angeben (z.B. IWDA.L, CSPX.L)."
                )
                return []

            holdings = []
            for symbol, row in df.head(top_n).iterrows():
                weight = float(row.get("Holding Percent", 0) or 0)
                # Normalisieren: yfinance liefert bereits 0-1 (z.B. 0.05 = 5%)
                # aber ältere Versionen liefern 0-100
                if weight > 1.0:
                    weight /= 100.0

                holdings.append({
                    "ticker": str(symbol),
                    "name": str(row.get("Name", symbol)),
                    "weight": weight,
                    "country": "",
                    "currency": "",
                    "gics_sector": 0,
                })

            # Schritt 1: STOCK_METADATA (schnell, kein API-Call)
            for h in holdings:
                t = h["ticker"]
                if t and (not h["country"] or not h["gics_sector"]):
                    meta = STOCK_METADATA.get(t, {})
                    if not h["country"]:
                        h["country"] = meta.get("country", "")
                    if not h["currency"]:
                        h["currency"] = meta.get("currency", "")
                    if not h["gics_sector"]:
                        h["gics_sector"] = meta.get("gics_sector", 0)

            # Schritt 2: Länder aus Börsen-Suffix ableiten (kein API-Call nötig)
            # Tickers ohne Suffix sind fast immer US-gelistet.
            for h in holdings:
                if not h["country"] and h["ticker"]:
                    sym = h["ticker"]
                    if "." in sym:
                        suffix = "." + sym.rsplit(".", 1)[1].upper()
                        h["country"] = _SUFFIX_TO_COUNTRY.get(suffix, "")
                    if not h["country"]:
                        # Kein Suffix → US-gelistete Aktie (AAPL, MSFT, etc.)
                        h["country"] = "US"

            # Schritt 3: Währung aus Land ableiten wenn noch leer
            for h in holdings:
                if not h["currency"] and h["country"]:
                    h["currency"] = COUNTRY_TO_CURRENCY.get(h["country"], "")

            return holdings

        except Exception as e:
            logger.warning(f"ETF-Holdings für {ticker} nicht abrufbar: {e}")
            return []

    def get_etf_sector_weights(self, ticker: str) -> dict[int, float]:
        """ETF-Sektor-Gewichtungen über yfinance funds_data.sector_weightings."""
        import yfinance as yf
        try:
            etf = yf.Ticker(ticker)
            raw = etf.funds_data.sector_weightings
            if not raw:
                return {}
            result: dict[int, float] = {}
            for yf_key, weight in raw.items():
                gics = YFINANCE_SECTOR_TO_GICS.get(yf_key.lower(), 0)
                if gics:
                    result[gics] = result.get(gics, 0) + float(weight)
            return result
        except Exception as e:
            logger.debug(f"funds_data.sector_weightings für {ticker} nicht verfügbar: {e}")
            return {}

    def get_historical_prices(
        self, tickers: list[str], years: int = 2
    ) -> pd.DataFrame:
        import yfinance as yf
        from utils.ticker_matcher import TICKER_TO_YF

        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        def _download(syms: list[str]) -> pd.DataFrame:
            if not syms:
                return pd.DataFrame()
            try:
                data = yf.download(syms, start=start_str, end=end_str,
                                   progress=False, auto_adjust=True)
                if data.empty:
                    return pd.DataFrame()
                if isinstance(data.columns, pd.MultiIndex):
                    return data["Close"]
                return data[["Close"]].rename(columns={"Close": syms[0]})
            except Exception as e:
                logger.warning(f"Download fehlgeschlagen für {syms}: {e}")
                return pd.DataFrame()

        # Schritt 1: Ticker via Lookup-Tabelle auflösen
        resolved: dict[str, str] = {}  # original → yf_symbol
        for t in tickers:
            if "." in t:
                resolved[t] = t                          # Suffix bereits vorhanden
            elif t.upper() in TICKER_TO_YF:
                resolved[t] = TICKER_TO_YF[t.upper()]   # Bekannter UCITS-Ticker
            else:
                resolved[t] = t                          # US-Aktien etc.

        # Schritt 2: Alle auf einmal herunterladen
        yf_to_orig = {v: k for k, v in resolved.items()}
        all_prices = _download(list(resolved.values()))

        if not all_prices.empty:
            all_prices = all_prices.rename(columns=yf_to_orig)

        # Schritt 3: Fehlende Ticker mit Suffix-Fallback nachschlagen
        missing = [t for t in tickers if t not in all_prices.columns
                   or all_prices[t].isna().all()]

        for orig in missing:
            if "." in orig:
                continue
            for suffix in [".L", ".DE", ".PA", ".AS", ".SW", ".MI"]:
                sym = orig + suffix
                df = _download([sym])
                if not df.empty and not df.iloc[:, 0].isna().all():
                    logger.info(f"{orig} → {sym}")
                    col = df.iloc[:, 0].rename(orig)
                    all_prices = pd.concat(
                        [all_prices.drop(columns=[orig], errors="ignore"), col],
                        axis=1,
                    )
                    break

        return all_prices.dropna(how="all") if not all_prices.empty else pd.DataFrame()

    def get_benchmark_prices(
        self, benchmark_ticker: str, years: int = 2
    ) -> pd.Series:
        df = self.get_historical_prices([benchmark_ticker], years=years)
        if df.empty:
            return pd.Series(dtype=float)
        return df.iloc[:, 0].dropna()

    def is_available(self) -> bool:
        """Check if yfinance is importable (connectivity tested on first real use)."""
        try:
            import yfinance as yf  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _map_sector_to_gics(sector_name: str) -> int:
        """Yahoo-Finance-Sektornamen auf GICS-Codes mappen."""
        mapping = {
            "technology": 45, "financial services": 40, "financials": 40,
            "healthcare": 35, "health care": 35, "consumer cyclical": 25,
            "consumer discretionary": 25, "consumer defensive": 30,
            "consumer staples": 30, "industrials": 20, "energy": 10,
            "basic materials": 15, "materials": 15, "real estate": 60,
            "utilities": 55, "communication services": 50,
            "telecommunication services": 50,
        }
        return mapping.get(sector_name.lower().strip(), 0)

    @staticmethod
    def _country_name_to_iso(country_name: str) -> str:
        """Ländernamen in ISO Alpha-2 konvertieren."""
        mapping = {
            "united states": "US", "germany": "DE", "united kingdom": "GB",
            "france": "FR", "japan": "JP", "china": "CN", "canada": "CA",
            "switzerland": "CH", "australia": "AU", "south korea": "KR",
            "netherlands": "NL", "sweden": "SE", "spain": "ES",
            "italy": "IT", "india": "IN", "brazil": "BR", "taiwan": "TW",
            "hong kong": "HK", "denmark": "DK", "norway": "NO",
            "finland": "FI", "ireland": "IE", "belgium": "BE",
            "singapore": "SG", "israel": "IL", "austria": "AT",
            "mexico": "MX", "south africa": "ZA", "portugal": "PT",
            "new zealand": "NZ", "poland": "PL", "turkey": "TR",
            "saudi arabia": "SA", "indonesia": "ID", "thailand": "TH",
            "malaysia": "MY", "philippines": "PH", "chile": "CL",
            "colombia": "CO", "peru": "PE", "argentina": "AR",
            "czech republic": "CZ", "hungary": "HU", "russia": "RU",
        }
        return mapping.get(country_name.lower().strip(), "")


# ---------------------------------------------------------------------------
# Provider-Factory
# ---------------------------------------------------------------------------

def get_data_provider() -> DataProvider:
    """Gibt den yfinance Data-Provider zurück."""
    provider = YFinanceProvider()
    if provider.is_available():
        logger.info("yfinance-Provider aktiv.")
        return provider
    raise RuntimeError("yfinance nicht verfügbar. Bitte installieren: pip install yfinance")
