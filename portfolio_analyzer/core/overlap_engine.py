"""
Overlap Engine: Erkennt Überschneidungen zwischen ETFs und Einzelaktien.

Identifiziert:
1. Aktien, die direkt UND in einem ETF gehalten werden
2. Aktien, die in mehreren ETFs enthalten sind
3. Effektive Gesamtgewichtung pro Einzelunternehmen
"""

from dataclasses import dataclass, field
import pandas as pd

from core.portfolio import Portfolio, Position
from utils.constants import CONCENTRATION_WARNING_THRESHOLD


@dataclass
class OverlapEntry:
    """Ein Unternehmen und seine Quellen im Portfolio."""
    ticker: str
    name: str
    direct_weight: float = 0.0       # Direktes Holding als Einzelaktie
    etf_contributions: dict = field(default_factory=dict)  # {ETF-Ticker: anteiliges Gewicht}

    @property
    def total_weight(self) -> float:
        return self.direct_weight + sum(self.etf_contributions.values())

    @property
    def num_sources(self) -> int:
        """Anzahl der Quellen (direkt + ETFs)."""
        sources = len(self.etf_contributions)
        if self.direct_weight > 0:
            sources += 1
        return sources

    @property
    def is_overlap(self) -> bool:
        """True wenn das Unternehmen aus mehr als einer Quelle kommt."""
        return self.num_sources > 1

    @property
    def has_concentration_risk(self) -> bool:
        return self.total_weight >= CONCENTRATION_WARNING_THRESHOLD


class OverlapEngine:
    """Erkennt und quantifiziert Überschneidungen im Portfolio."""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self._overlap_map: dict[str, OverlapEntry] = {}

    def analyze(self) -> dict[str, OverlapEntry]:
        """
        Vollständige Overlap-Analyse durchführen.
        Returns: Dict {ticker: OverlapEntry} für alle Unternehmen.
        """
        self._overlap_map.clear()

        for pos in self.portfolio.positions:
            if pos.is_etf and pos.holdings:
                # ETF-Holdings durchgehen
                holdings_total_weight = sum(h.weight for h in pos.holdings)
                for holding in pos.holdings:
                    if not holding.ticker:
                        continue

                    ticker = holding.ticker.upper().strip()
                    if ticker not in self._overlap_map:
                        self._overlap_map[ticker] = OverlapEntry(
                            ticker=ticker,
                            name=holding.name,
                        )

                    # Effektives Gewicht: Portfolio-Gewicht × Holding-Gewicht im ETF
                    if holdings_total_weight > 0:
                        effective = pos.weight * (holding.weight / holdings_total_weight)
                    else:
                        effective = 0
                    self._overlap_map[ticker].etf_contributions[pos.ticker] = effective

            elif not pos.is_etf:
                # Einzelaktie
                ticker = pos.ticker.upper().strip()
                if ticker not in self._overlap_map:
                    self._overlap_map[ticker] = OverlapEntry(
                        ticker=ticker,
                        name=pos.name,
                    )
                self._overlap_map[ticker].direct_weight = pos.weight

        return self._overlap_map

    def get_overlapping_positions(self) -> list[OverlapEntry]:
        """Nur die Positionen mit echten Überschneidungen (>1 Quelle)."""
        if not self._overlap_map:
            self.analyze()
        return sorted(
            [e for e in self._overlap_map.values() if e.is_overlap],
            key=lambda e: e.total_weight,
            reverse=True,
        )

    def get_concentration_warnings(self) -> list[OverlapEntry]:
        """Positionen mit Konzentrationsrisiko (>10% effektiv)."""
        if not self._overlap_map:
            self.analyze()
        return sorted(
            [e for e in self._overlap_map.values() if e.has_concentration_risk],
            key=lambda e: e.total_weight,
            reverse=True,
        )

    def get_effective_weights(self, top_n: int = 30) -> pd.DataFrame:
        """
        Effektive Gewichtung pro Unternehmen als DataFrame.
        Zeigt die wahre Konzentration nach Auflösung aller ETFs.
        """
        if not self._overlap_map:
            self.analyze()

        rows = []
        for entry in sorted(
            self._overlap_map.values(),
            key=lambda e: e.total_weight,
            reverse=True,
        )[:top_n]:
            sources = []
            if entry.direct_weight > 0:
                sources.append(f"Direkt: {entry.direct_weight * 100:.1f}%")
            for etf_ticker, w in entry.etf_contributions.items():
                sources.append(f"{etf_ticker}: {w * 100:.2f}%")

            rows.append({
                "Ticker": entry.ticker,
                "Name": entry.name,
                "Effektives Gewicht (%)": round(entry.total_weight * 100, 2),
                "Direkt (%)": round(entry.direct_weight * 100, 2),
                "Via ETFs (%)": round(
                    sum(entry.etf_contributions.values()) * 100, 2
                ),
                "Quellen": len(entry.etf_contributions) + (1 if entry.direct_weight > 0 else 0),
                "Details": " | ".join(sources),
                "Overlap": "⚠️" if entry.is_overlap else "",
                "Konzentration": "🔴" if entry.has_concentration_risk else "",
            })

        return pd.DataFrame(rows)

    def get_etf_overlap_matrix(self) -> pd.DataFrame:
        """
        Overlap-Matrix zwischen allen ETFs im Portfolio.
        Zeigt, wie viele gemeinsame Holdings zwei ETFs haben.
        """
        etfs = [p for p in self.portfolio.positions if p.is_etf and p.holdings]

        if len(etfs) < 2:
            return pd.DataFrame()

        matrix_data = {}
        for etf_a in etfs:
            tickers_a = {h.ticker.upper() for h in etf_a.holdings if h.ticker}
            row = {}
            for etf_b in etfs:
                tickers_b = {h.ticker.upper() for h in etf_b.holdings if h.ticker}
                overlap = tickers_a & tickers_b
                total = tickers_a | tickers_b
                # Jaccard-Ähnlichkeit als Overlap-Maß
                if total:
                    row[etf_b.ticker] = round(len(overlap) / len(total) * 100, 1)
                else:
                    row[etf_b.ticker] = 0.0
            matrix_data[etf_a.ticker] = row

        return pd.DataFrame(matrix_data)

    def get_sankey_data(self) -> dict:
        """
        Daten für Sankey-Diagramm aufbereiten.
        Links: Quellen (ETFs + Direktpositionen)
        Rechts: Unternehmen
        """
        if not self._overlap_map:
            self.analyze()

        sources = []      # Labels der Knoten
        targets = []       # Labels der Zielknoten
        values = []        # Gewichtungen der Verbindungen
        colors = []        # Farben der Verbindungen

        # Nur Overlaps und Top-Positionen für Übersichtlichkeit
        relevant_entries = sorted(
            [e for e in self._overlap_map.values() if e.total_weight > 0.005],
            key=lambda e: e.total_weight,
            reverse=True,
        )[:30]

        all_labels = []
        # Quellen: Alle Portfoliopositionen
        source_labels = [p.ticker for p in self.portfolio.positions]
        all_labels.extend(source_labels)

        # Ziele: Alle aufgelösten Unternehmen
        target_labels = [e.ticker for e in relevant_entries]
        all_labels.extend(target_labels)

        for entry in relevant_entries:
            target_idx = all_labels.index(entry.ticker)

            if entry.direct_weight > 0:
                source_idx = all_labels.index(entry.ticker) if entry.ticker in source_labels else -1
                if source_idx >= 0:
                    sources.append(source_idx)
                    targets.append(target_idx)
                    values.append(round(entry.direct_weight * 100, 2))
                    colors.append("rgba(52, 152, 219, 0.5)")  # Blau für direkt

            for etf_ticker, w in entry.etf_contributions.items():
                if etf_ticker in source_labels and w > 0.001:
                    source_idx = all_labels.index(etf_ticker)
                    sources.append(source_idx)
                    targets.append(target_idx)
                    values.append(round(w * 100, 2))
                    color = (
                        "rgba(231, 76, 60, 0.5)"  # Rot für Overlap
                        if entry.is_overlap
                        else "rgba(46, 204, 113, 0.5)"  # Grün für unique
                    )
                    colors.append(color)

        return {
            "labels": all_labels,
            "sources": sources,
            "targets": targets,
            "values": values,
            "colors": colors,
        }
