"""
Exposure Engine: Berechnet Länder-, Währungs- und Branchen-Exposure.

Bei ETFs werden die Holdings aufgelöst und anteilig zum Portfolio-Exposure
hinzugerechnet. Eine Aktie, die direkt gehalten wird UND in einem ETF
enthalten ist, wird korrekt aggregiert.
"""

import pandas as pd

from core.portfolio import Portfolio, Position
from utils.constants import (
    COUNTRY_MAPPING,
    COUNTRY_TO_CURRENCY,
    CURRENCY_MAPPING,
    GICS_SECTORS,
)


class ExposureEngine:
    """Berechnet die Exposure-Verteilung eines Portfolios."""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def get_country_exposure(self) -> pd.DataFrame:
        """
        Länder-Exposure berechnen.

        Prioritätenreihenfolge für ETFs:
          1. etf_country_weights  (statische Datenbank — präziseste Quelle)
          2. Holdings mit Länderdaten (dynamisch aus yfinance)
          3. "XX" (unbekannt)

        Für Einzelaktien: 100% dem Sitzland zugeordnet.
        """
        exposure: dict[str, float] = {}

        for pos in self.portfolio.positions:
            if not pos.is_etf:
                country = pos.country or "XX"
                exposure[country] = exposure.get(country, 0) + pos.weight
                continue

            # ETF: statische Länderverteilung hat höchste Priorität
            if pos.etf_country_weights:
                for country, frac in pos.etf_country_weights.items():
                    exposure[country] = exposure.get(country, 0) + pos.weight * frac
                continue

            # Fallback: dynamische Holdings
            if pos.holdings:
                total_w = sum(h.weight for h in pos.holdings)
                if total_w <= 0:
                    exposure["XX"] = exposure.get("XX", 0) + pos.weight
                    continue
                # Tatsächliche Gewichte verwenden (nicht normalisieren) + Remainder
                for holding in pos.holdings:
                    country = holding.country or "XX"
                    effective_weight = pos.weight * holding.weight
                    exposure[country] = exposure.get(country, 0) + effective_weight
                remainder = pos.weight * max(0.0, 1.0 - total_w)
                if remainder > 0.001:
                    exposure["XX"] = exposure.get("XX", 0) + remainder
                continue

            # Kein Datensatz vorhanden
            exposure["XX"] = exposure.get("XX", 0) + pos.weight

        return self._build_country_df(exposure)

    def get_currency_exposure(self) -> pd.DataFrame:
        """
        Währungs-Exposure berechnen.

        Prioritätenreihenfolge für ETFs:
          1. etf_country_weights → Währung über COUNTRY_TO_CURRENCY ableiten
          2. Holdings mit Währungsdaten
          3. Handelswährung der ETF-Position

        Returns: DataFrame mit Spalten [Währung, Name, Region, Gewicht_pct]
        """
        exposure: dict[str, float] = {}

        for pos in self.portfolio.positions:
            if not pos.is_etf:
                currency = pos.trade_currency or "XXX"
                exposure[currency] = exposure.get(currency, 0) + pos.weight
                continue

            # ETF: statische Länderverteilung → Währung ableiten
            if pos.etf_country_weights:
                for country, frac in pos.etf_country_weights.items():
                    currency = COUNTRY_TO_CURRENCY.get(country, "XXX")
                    exposure[currency] = exposure.get(currency, 0) + pos.weight * frac
                continue

            # Fallback: dynamische Holdings
            if pos.holdings:
                total_w = sum(h.weight for h in pos.holdings)
                if total_w <= 0:
                    currency = pos.trade_currency or "XXX"
                    exposure[currency] = exposure.get(currency, 0) + pos.weight
                    continue
                for holding in pos.holdings:
                    currency = holding.currency
                    if not currency and holding.country:
                        currency = COUNTRY_TO_CURRENCY.get(holding.country, "")
                    if not currency:
                        currency = pos.trade_currency or "XXX"
                    effective_weight = pos.weight * holding.weight
                    exposure[currency] = exposure.get(currency, 0) + effective_weight
                remainder = pos.weight * max(0.0, 1.0 - total_w)
                if remainder > 0.001:
                    currency = pos.trade_currency or "XXX"
                    exposure[currency] = exposure.get(currency, 0) + remainder
                continue

            # Keine Daten → Handelswährung
            currency = pos.trade_currency or "XXX"
            exposure[currency] = exposure.get(currency, 0) + pos.weight

        return self._build_currency_df(exposure)

    def get_sector_exposure(self) -> pd.DataFrame:
        """
        Branchen/Sektor-Exposure berechnen (GICS-Sektoren).

        Für ETFs: Priorität
          1. Holdings mit bekanntem gics_sector
          2. etf_sector_weights (z.B. aus yfinance funds_data.sector_weightings)
          3. Fallback: alles auf Sektor 0 ("Unbekannt")

        Returns: DataFrame mit Spalten [Sektor, GICS_Code, Gewicht_pct]
        """
        exposure: dict[int, float] = {}

        for pos in self.portfolio.positions:
            if pos.is_etf:
                # Prüfen ob Holdings brauchbare Sektor-Daten haben
                holdings_with_sector = [
                    h for h in pos.holdings if h.gics_sector
                ] if pos.holdings else []

                if holdings_with_sector:
                    # Holdings normalisieren (Top-N extrapoliert auf 100%)
                    total_w = sum(h.weight for h in pos.holdings)
                    if total_w > 0:
                        for holding in pos.holdings:
                            sector = holding.gics_sector or 0
                            effective_weight = pos.weight * (holding.weight / total_w)
                            exposure[sector] = exposure.get(sector, 0) + effective_weight
                    else:
                        exposure[0] = exposure.get(0, 0) + pos.weight

                elif pos.etf_sector_weights:
                    # Direkte ETF-Sektor-Gewichtungen verwenden (z.B. aus yfinance)
                    total_sw = sum(pos.etf_sector_weights.values())
                    for gics_code, sw in pos.etf_sector_weights.items():
                        norm = sw / total_sw if total_sw > 0 else 0
                        exposure[gics_code] = exposure.get(gics_code, 0) + pos.weight * norm

                else:
                    # Kein Sektor-Daten → alles als Unbekannt
                    exposure[0] = exposure.get(0, 0) + pos.weight
            else:
                sector = pos.gics_sector or 0
                exposure[sector] = exposure.get(sector, 0) + pos.weight

        return self._build_sector_df(exposure)

    def get_asset_class_exposure(self) -> pd.DataFrame:
        """
        Anlageklassen-Exposure berechnen.

        Kategorien:
          - Aktien-ETF       : ETF ohne Bond/Rohstoff/Immobilien-Kennzeichen
          - Anleihen-ETF     : ETF mit Bond/Fixed-Income-Kennzeichen
          - Rohstoff-ETF     : ETF mit Commodity/Gold/Rohstoff-Kennzeichen
          - Immobilien-ETF   : ETF mit REIT/Real-Estate-Kennzeichen
          - Krypto-ETF/ETP   : ETF/ETP mit Crypto-Kennzeichen
          - Einzelaktie      : asset_type == STOCK
          - Sonstige/Unbekannt

        Returns: DataFrame mit Spalten [Anlageklasse, Gewicht_absolut, Gewicht_pct]
        """
        # Explizite Ticker → Anlageklasse (höchste Priorität)
        _TICKER_CLASS: dict[str, str] = {
            # Gold ETCs (Xetra / LSE)
            "xad5": "Rohstoff-ETP", "xad5.de": "Rohstoff-ETP",
            "xad6": "Rohstoff-ETP", "xad6.de": "Rohstoff-ETP",
            "egln": "Rohstoff-ETP", "egln.l": "Rohstoff-ETP",
            "phau": "Rohstoff-ETP", "phau.l": "Rohstoff-ETP",
            "igln": "Rohstoff-ETP", "igln.l": "Rohstoff-ETP",
            "sgln": "Rohstoff-ETP", "4gld": "Rohstoff-ETP",
            "wgld": "Rohstoff-ETP", "gzur": "Rohstoff-ETP",
            # Silber ETCs
            "phag": "Rohstoff-ETP", "phag.l": "Rohstoff-ETP",
            "xads": "Rohstoff-ETP",
            # Öl/Energie ETCs
            "crud": "Rohstoff-ETP", "loil": "Rohstoff-ETP",
            # Krypto ETPs
            "btce": "Krypto-ETP", "xbte": "Krypto-ETP",
            "ethe": "Krypto-ETP", "vbtc": "Krypto-ETP",
            # Anleihen ETFs (bekannte Ticker)
            "iusb": "Anleihen-ETF", "aggh": "Anleihen-ETF",
            "embe": "Anleihen-ETF", "ibts": "Anleihen-ETF",
            "exhb": "Anleihen-ETF", "exhb.de": "Anleihen-ETF",
            # Immobilien ETFs
            "iqqp": "Immobilien-ETF", "wrem": "Immobilien-ETF",
        }

        _BOND_KEYWORDS = {
            "bond", "anleihe", "treasury", "gilt", "bund", "aggregate",
            "fixed income", "credit", "corp", "sovereign", "duration",
            "inflation", "tips", "note", "debt",
        }
        _COMMODITY_KEYWORDS = {
            "gold", "silver", "silber", "oil", "öl", "commodity",
            "rohstoff", "metal", "metall", "copper", "platinum",
            "palladium", "natural gas", "physical",
        }
        _REAL_ESTATE_KEYWORDS = {
            "reit", "real estate", "immobilien", "property", "realty",
        }
        _CRYPTO_KEYWORDS = {
            "bitcoin", "ethereum", "crypto", "btc", "eth", "blockchain",
            "digital asset", "xbt",
        }

        def _classify(pos: Position) -> str:
            from core.portfolio import AssetType
            if pos.asset_type == AssetType.STOCK:
                return "Einzelaktie"
            if pos.asset_type == AssetType.ETF:
                # 1. Expliziter Ticker-Lookup (höchste Priorität)
                if pos.ticker.lower() in _TICKER_CLASS:
                    return _TICKER_CLASS[pos.ticker.lower()]
                # 2. Name + Ticker auf Keywords prüfen
                key = (pos.name + " " + pos.ticker).lower()
                if any(k in key for k in _CRYPTO_KEYWORDS):
                    return "Krypto-ETP"
                if any(k in key for k in _REAL_ESTATE_KEYWORDS):
                    return "Immobilien-ETF"
                if any(k in key for k in _COMMODITY_KEYWORDS):
                    return "Rohstoff-ETP"
                if any(k in key for k in _BOND_KEYWORDS):
                    return "Anleihen-ETF"
                return "Aktien-ETF"
            return "Sonstige / Unbekannt"

        exposure: dict[str, float] = {}
        for pos in self.portfolio.positions:
            cls = _classify(pos)
            exposure[cls] = exposure.get(cls, 0.0) + pos.weight

        # Definierte Reihenfolge
        order = [
            "Aktien-ETF", "Einzelaktie", "Anleihen-ETF",
            "Rohstoff-ETP", "Immobilien-ETF", "Krypto-ETP", "Sonstige / Unbekannt",
        ]
        rows = []
        for cls in order:
            if cls in exposure:
                rows.append({
                    "Anlageklasse": cls,
                    "Gewicht_absolut": exposure[cls],
                    "Gewicht_pct": round(exposure[cls] * 100, 2),
                })
        # Alle übrigen (falls neue Kategorie auftaucht)
        for cls, w in exposure.items():
            if cls not in order:
                rows.append({
                    "Anlageklasse": cls,
                    "Gewicht_absolut": w,
                    "Gewicht_pct": round(w * 100, 2),
                })
        return pd.DataFrame(rows)

    # -------------------------------------------------------------------
    # Private Hilfsfunktionen
    # -------------------------------------------------------------------

    @staticmethod
    def _build_country_df(exposure: dict[str, float]) -> pd.DataFrame:
        rows = []
        for country_code, weight in sorted(
            exposure.items(), key=lambda x: x[1], reverse=True
        ):
            info = COUNTRY_MAPPING.get(country_code, {})
            rows.append({
                "Land_Code": country_code,
                "Land": info.get("name", "Sonstige" if country_code == "XX" else country_code),
                "ISO_Alpha3": info.get("alpha3", ""),
                "Region": info.get("region", "Sonstige"),
                "Gewicht_absolut": weight,
                "Gewicht_pct": round(weight * 100, 2),
            })
        return pd.DataFrame(rows)

    @staticmethod
    def _build_currency_df(exposure: dict[str, float]) -> pd.DataFrame:
        rows = []
        for currency_code, weight in sorted(
            exposure.items(), key=lambda x: x[1], reverse=True
        ):
            info = CURRENCY_MAPPING.get(currency_code, {})
            rows.append({
                "Währung": currency_code,
                "Name": info.get("name", currency_code),
                "Symbol": info.get("symbol", ""),
                "Region": info.get("region", "Sonstige"),
                "Gewicht_absolut": weight,
                "Gewicht_pct": round(weight * 100, 2),
            })
        return pd.DataFrame(rows)

    @staticmethod
    def _build_sector_df(exposure: dict[int, float]) -> pd.DataFrame:
        rows = []
        for gics_code, weight in sorted(
            exposure.items(), key=lambda x: x[1], reverse=True
        ):
            rows.append({
                "GICS_Code": gics_code,
                "Sektor": GICS_SECTORS.get(gics_code, "Unbekannt"),
                "Gewicht_absolut": weight,
                "Gewicht_pct": round(weight * 100, 2),
            })
        return pd.DataFrame(rows)
