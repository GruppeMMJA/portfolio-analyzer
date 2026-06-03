"""
Seite 5: Report Export

Generiert einen PDF-Report mit allen Analysen:
Exposure, Overlap, Risikokennzahlen, Charts.
"""

import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from core.portfolio import Portfolio
from core.exposure_engine import ExposureEngine
from core.overlap_engine import OverlapEngine
from utils.nav import inject_page

st.set_page_config(page_title="Report Export", layout="wide", initial_sidebar_state="collapsed")

inject_page("export")


# ─────────────────────────────────────────────────────
# Portfolio prüfen
# ─────────────────────────────────────────────────────
if "portfolio" not in st.session_state or st.session_state.portfolio.num_positions == 0:
    st.warning("Kein Portfolio geladen. Bitte zuerst Positionen eingeben.")
    st.stop()

portfolio: Portfolio = st.session_state.portfolio

st.markdown("""
<div class="page-hero anim-0">
  <h1>Report Export</h1>
  <p class="page-hero-sub">Portfolio-Analysen als Excel, CSV oder Markdown exportieren.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Excel-Export
# ─────────────────────────────────────────────────────
st.markdown("### Excel-Export")
st.markdown("Exportiert alle Analysedaten als mehrseitiges Excel-File.")

if st.button("Excel generieren", type="primary"):
    with st.spinner("Erstelle Excel-Report..."):
        engine_exp = ExposureEngine(portfolio)
        engine_ovl = OverlapEngine(portfolio)
        engine_ovl.analyze()

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Blatt 1: Portfolio-Übersicht
            portfolio.to_dataframe().to_excel(
                writer, sheet_name="Portfolio", index=False
            )

            # Blatt 2: Länder-Exposure
            country_df = engine_exp.get_country_exposure()
            if not country_df.empty:
                country_df.to_excel(
                    writer, sheet_name="Länder-Exposure", index=False
                )

            # Blatt 3: Währungs-Exposure
            currency_df = engine_exp.get_currency_exposure()
            if not currency_df.empty:
                currency_df.to_excel(
                    writer, sheet_name="Währungs-Exposure", index=False
                )

            # Blatt 4: Sektor-Exposure
            sector_df = engine_exp.get_sector_exposure()
            if not sector_df.empty:
                sector_df.to_excel(
                    writer, sheet_name="Sektor-Exposure", index=False
                )

            # Blatt 5: Effektive Gewichtung
            weights_df = engine_ovl.get_effective_weights(top_n=50)
            if not weights_df.empty:
                weights_df.to_excel(
                    writer, sheet_name="Effektive Gewichtung", index=False
                )

            # Blatt 6: Overlap-Matrix
            matrix_df = engine_ovl.get_etf_overlap_matrix()
            if not matrix_df.empty:
                matrix_df.to_excel(
                    writer, sheet_name="ETF-Overlap-Matrix"
                )

        buffer.seek(0)

        st.download_button(
            label="Excel herunterladen",
            data=buffer,
            file_name="portfolio_analyse.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.success("Excel-Report erstellt!")


# ─────────────────────────────────────────────────────
# CSV-Export (einzelne Tabellen)
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Einzelne Tabellen als CSV")

engine_exp = ExposureEngine(portfolio)
engine_ovl = OverlapEngine(portfolio)
engine_ovl.analyze()

col1, col2, col3 = st.columns(3)

with col1:
    csv_portfolio = portfolio.to_dataframe().to_csv(index=False).encode("utf-8")
    st.download_button(
        "Portfolio",
        data=csv_portfolio,
        file_name="portfolio_positionen.csv",
        mime="text/csv",
        use_container_width=True,
    )

    country_df = engine_exp.get_country_exposure()
    if not country_df.empty:
        csv_country = country_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Länder-Exposure",
            data=csv_country,
            file_name="laender_exposure.csv",
            mime="text/csv",
            use_container_width=True,
        )

with col2:
    currency_df = engine_exp.get_currency_exposure()
    if not currency_df.empty:
        csv_currency = currency_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Währungs-Exposure",
            data=csv_currency,
            file_name="waehrungs_exposure.csv",
            mime="text/csv",
            use_container_width=True,
        )

    sector_df = engine_exp.get_sector_exposure()
    if not sector_df.empty:
        csv_sector = sector_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Sektor-Exposure",
            data=csv_sector,
            file_name="sektor_exposure.csv",
            mime="text/csv",
            use_container_width=True,
        )

with col3:
    weights_df = engine_ovl.get_effective_weights(top_n=50)
    if not weights_df.empty:
        csv_weights = weights_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Effektive Gewichtung",
            data=csv_weights,
            file_name="effektive_gewichtung.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────
# Zusammenfassung als Text
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Portfolio-Zusammenfassung")

country_df = engine_exp.get_country_exposure()
sector_df = engine_exp.get_sector_exposure()
overlaps = engine_ovl.get_overlapping_positions()
concentrations = engine_ovl.get_concentration_warnings()

summary = f"""# Portfolio-Analyse — Zusammenfassung

## Übersicht
- **Anzahl Positionen:** {portfolio.num_positions}
- **Gesamtwert:** {portfolio.total_value:,.2f} €
- **ETFs:** {sum(1 for p in portfolio.positions if p.is_etf)}
- **Einzelaktien:** {sum(1 for p in portfolio.positions if not p.is_etf)}

## Top 5 Länder
"""

if not country_df.empty:
    for _, row in country_df.head(5).iterrows():
        summary += f"- {row['Land']}: {row['Gewicht_pct']:.1f}%\n"

summary += "\n## Top 5 Sektoren\n"
if not sector_df.empty:
    for _, row in sector_df.head(5).iterrows():
        summary += f"- {row['Sektor']}: {row['Gewicht_pct']:.1f}%\n"

if overlaps:
    summary += f"\n## Überschneidungen\n"
    summary += f"- **{len(overlaps)} Aktien** sind aus mehreren Quellen vertreten\n"
    for entry in overlaps[:5]:
        summary += f"- {entry.name} ({entry.ticker}): {entry.total_weight * 100:.1f}% effektiv\n"

if concentrations:
    summary += f"\n## Konzentrationsrisiken\n"
    for entry in concentrations:
        summary += f"- **{entry.name}** ({entry.ticker}): {entry.total_weight * 100:.1f}% effektiv\n"

st.markdown(summary)

st.download_button(
    "Zusammenfassung als Markdown",
    data=summary.encode("utf-8"),
    file_name="portfolio_zusammenfassung.md",
    mime="text/markdown",
    use_container_width=True,
)
