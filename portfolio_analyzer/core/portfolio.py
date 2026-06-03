"""
Portfolio-Datenmodell: Zentrale Datenstruktur für alle Analysen.

Ein Portfolio besteht aus Positionen. Jede Position hat:
- Identifikation (Ticker, ISIN, Name)
- Marktwert (aktuell, in Portfolio-Währung)
- Klassifikation (Land, Währung, Sektor)
- Typ (Einzelaktie vs. ETF)
- Bei ETFs: aufgelöste Holdings
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pandas as pd


class AssetType(Enum):
    STOCK = "Einzelaktie"
    ETF = "ETF"
    UNKNOWN = "Unbekannt"


@dataclass
class Holding:
    """Eine einzelne Holding innerhalb eines ETF."""
    ticker: str
    name: str
    weight: float          # Gewichtung im ETF (0.0 bis 1.0)
    country: str = ""      # ISO Alpha-2
    currency: str = ""     # ISO Währungscode
    gics_sector: int = 0   # GICS Sektor-Code


@dataclass
class Position:
    """Eine Position im Portfolio."""
    ticker: str
    name: str = ""
    isin: str = ""
    market_value: float = 0.0       # Aktueller Marktwert in EUR
    currency: str = "EUR"           # Währung des Marktwerts
    asset_type: AssetType = AssetType.UNKNOWN
    country: str = ""               # ISO Alpha-2 Ländercode
    trade_currency: str = ""        # Handelswährung an der Börse
    gics_sector: int = 0            # GICS Sektor-Code
    gics_sector_name: str = ""      # GICS Sektorname
    holdings: list[Holding] = field(default_factory=list)  # ETF-Holdings
    etf_sector_weights: dict = field(default_factory=dict)   # GICS-Code → Gewicht (ETF-Sektoren)
    etf_country_weights: dict = field(default_factory=dict)  # ISO-Alpha2 → Gewicht (ETF-Länder)
    weight: float = 0.0             # Gewicht im Portfolio (0.0 bis 1.0)

    @property
    def is_etf(self) -> bool:
        return self.asset_type == AssetType.ETF


class Portfolio:
    """
    Zentrales Portfolio-Objekt. Hält alle Positionen und berechnet
    abgeleitete Daten wie Gewichtungen.
    """

    def __init__(self, name: str = "Mein Portfolio", base_currency: str = "EUR"):
        self.name = name
        self.base_currency = base_currency
        self.positions: list[Position] = []
        self._returns_df: Optional[pd.DataFrame] = None  # Historische Renditen

    def add_position(self, position: Position) -> None:
        """Position hinzufügen und Gewichtungen neu berechnen."""
        self.positions.append(position)
        self._recalculate_weights()

    def remove_position(self, ticker: str) -> None:
        """Position entfernen."""
        self.positions = [p for p in self.positions if p.ticker != ticker]
        self._recalculate_weights()

    def clear(self) -> None:
        """Alle Positionen entfernen."""
        self.positions.clear()
        self._returns_df = None

    def _recalculate_weights(self) -> None:
        """Gewichtungen auf Basis der Marktwerte neu berechnen."""
        total = self.total_value
        if total > 0:
            for pos in self.positions:
                pos.weight = pos.market_value / total
        else:
            for pos in self.positions:
                pos.weight = 0.0

    @property
    def total_value(self) -> float:
        """Gesamtmarktwert des Portfolios."""
        return sum(p.market_value for p in self.positions)

    @property
    def num_positions(self) -> int:
        return len(self.positions)

    @property
    def returns_df(self) -> Optional[pd.DataFrame]:
        return self._returns_df

    @returns_df.setter
    def returns_df(self, df: pd.DataFrame) -> None:
        self._returns_df = df

    def to_dataframe(self) -> pd.DataFrame:
        """Portfolio als DataFrame für Anzeige und Weiterverarbeitung."""
        if not self.positions:
            return pd.DataFrame(columns=[
                "Ticker", "Name", "ISIN", "Typ", "Marktwert (€)",
                "Gewicht (%)", "Land", "Währung", "Sektor"
            ])

        rows = []
        for p in self.positions:
            rows.append({
                "Ticker": p.ticker,
                "Name": p.name,
                "ISIN": p.isin,
                "Typ": p.asset_type.value,
                "Marktwert (€)": round(p.market_value, 2),
                "Gewicht (%)": round(p.weight * 100, 2),
                "Land": p.country,
                "Währung": p.trade_currency,
                "Sektor": "Diversifiziert" if p.is_etf else p.gics_sector_name,
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("Gewicht (%)", ascending=False).reset_index(drop=True)
        return df

    def get_position_by_ticker(self, ticker: str) -> Optional[Position]:
        """Position nach Ticker suchen."""
        for p in self.positions:
            if p.ticker.upper() == ticker.upper():
                return p
        return None

    def __repr__(self) -> str:
        return (
            f"Portfolio('{self.name}', {self.num_positions} Positionen, "
            f"Gesamtwert: {self.total_value:,.2f} {self.base_currency})"
        )
