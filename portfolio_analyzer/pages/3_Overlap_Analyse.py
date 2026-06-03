"""
Seite 3: Overlap-Analyse

Erkennt Überschneidungen zwischen ETFs und Einzelaktien.
Sankey-Diagramm, effektive Gewichtung, Konzentrationsrisiken.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from core.portfolio import Portfolio
from core.overlap_engine import OverlapEngine
from utils.nav import inject_page

st.set_page_config(page_title="Overlap-Analyse", layout="wide", initial_sidebar_state="collapsed")

inject_page("overlap")


# ─────────────────────────────────────────────────────
# Portfolio prüfen
# ─────────────────────────────────────────────────────
if "portfolio" not in st.session_state or st.session_state.portfolio.num_positions == 0:
    st.warning("Kein Portfolio geladen. Bitte zuerst Positionen eingeben.")
    st.stop()

portfolio: Portfolio = st.session_state.portfolio
engine = OverlapEngine(portfolio)

st.markdown("""
<div class="page-hero anim-0">
  <h1>Overlap-Analyse</h1>
  <p class="page-hero-sub">Überschneidungen zwischen ETFs und Einzelaktien erkennen und verstehen.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Analyse ausführen
# ─────────────────────────────────────────────────────
with st.spinner("Analysiere Überschneidungen..."):
    overlap_map = engine.analyze()

# ETFs mit Holdings prüfen
etfs_with_holdings = [p for p in portfolio.positions if p.is_etf and p.holdings]
if not etfs_with_holdings:
    st.info(
        "Keine ETF-Holdings verfügbar. Für die Overlap-Analyse werden "
        "ETF-Holdings benötigt. Bitte Portfolio mit Yahoo Finance anreichern."
    )
    # Trotzdem effektive Gewichtung anzeigen
    st.markdown("### Effektive Gewichtung (nur Einzelaktien)")
    weights_df = engine.get_effective_weights()
    if not weights_df.empty:
        st.dataframe(weights_df, use_container_width=True, hide_index=True)
    st.stop()

# ─────────────────────────────────────────────────────
# Warnungen
# ─────────────────────────────────────────────────────
overlaps = engine.get_overlapping_positions()
concentrations = engine.get_concentration_warnings()

col_warn1, col_warn2, col_warn3 = st.columns(3)

with col_warn1:
    st.metric(
        "Überschneidungen",
        len(overlaps),
        help="Aktien, die aus mehr als einer Quelle kommen",
    )

with col_warn2:
    st.metric(
        "Konzentrationsrisiken",
        len(concentrations),
        help="Positionen mit >10% effektiver Gewichtung",
    )

with col_warn3:
    st.metric(
        "Aufgelöste Holdings",
        sum(len(p.holdings) for p in etfs_with_holdings),
        help="Gesamtzahl der ETF-Holdings im Portfolio",
    )

# ─────────────────────────────────────────────────────
# Konzentrationsrisiken hervorheben
# ─────────────────────────────────────────────────────
if concentrations:
    st.markdown("### Konzentrationsrisiken")
    for entry in concentrations:
        sources_str = []
        if entry.direct_weight > 0:
            sources_str.append(f"**Direkt:** {entry.direct_weight * 100:.1f}%")
        for etf, w in entry.etf_contributions.items():
            sources_str.append(f"**{etf}:** {w * 100:.2f}%")

        with st.expander(
            f"{entry.name} ({entry.ticker}) — {entry.total_weight * 100:.1f}% effektiv",
            expanded=True,
        ):
            st.markdown(f"**Effektives Gewicht:** {entry.total_weight * 100:.1f}%")
            st.markdown("**Quellen:** " + " | ".join(sources_str))
            st.progress(
                min(entry.total_weight, 1.0),
                text=f"{entry.total_weight * 100:.1f}% des Portfolios",
            )


# ─────────────────────────────────────────────────────
# ETF-Overlap-Matrix
# ─────────────────────────────────────────────────────
if len(etfs_with_holdings) >= 2:
    st.markdown("### ETF-Overlap-Matrix")
    st.markdown(
        "Zeigt den Jaccard-Ähnlichkeitsindex zwischen den ETFs "
        "(Anteil gemeinsamer Holdings an allen Holdings)."
    )

    matrix_df = engine.get_etf_overlap_matrix()

    if not matrix_df.empty:
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=matrix_df.values,
            x=matrix_df.columns,
            y=matrix_df.index,
            colorscale="Blues",
            text=[[f"{v:.0f}%" for v in row] for row in matrix_df.values],
            texttemplate="%{text}",
            textfont=dict(size=14),
            hovertemplate="ETF A: %{y}<br>ETF B: %{x}<br>Overlap: %{z:.1f}%<extra></extra>",
        ))

        fig_heatmap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400,
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

# ─────────────────────────────────────────────────────
# Nur Überschneidungen anzeigen
# ─────────────────────────────────────────────────────
if overlaps:
    st.markdown("### Erkannte Überschneidungen")
    st.markdown(
        "Diese Aktien sind aus **mehreren Quellen** in deinem Portfolio vertreten."
    )

    overlap_rows = []
    for entry in overlaps:
        sources = []
        if entry.direct_weight > 0:
            sources.append(f"Direkt ({entry.direct_weight * 100:.1f}%)")
        for etf, w in entry.etf_contributions.items():
            sources.append(f"{etf} ({w * 100:.2f}%)")

        overlap_rows.append({
            "Aktie": f"{entry.name} ({entry.ticker})",
            "Effektives Gewicht (%)": round(entry.total_weight * 100, 2),
            "Direkt (%)": round(entry.direct_weight * 100, 2),
            "Via ETFs (%)": round(sum(entry.etf_contributions.values()) * 100, 2),
            "Quellen": " | ".join(sources),
        })

    overlap_df = pd.DataFrame(overlap_rows)
    st.dataframe(overlap_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────
# Effektive Gesamtgewichtung
# ─────────────────────────────────────────────────────
st.markdown("### Effektive Gewichtung — Top 30 Unternehmen")
st.markdown(
    "Die wahre Konzentration deines Portfolios nach Auflösung aller ETFs."
)

weights_df = engine.get_effective_weights(top_n=30)

if not weights_df.empty:
    # Balkendiagramm der Top 15
    top15 = weights_df.head(15)

    colors = [
        "#e53e3e" if row.get("Konzentration") in ("🔴", "hoch")
        else "#ed8936" if row.get("Overlap") in ("⚠️", "ja")
        else "#3182ce"
        for _, row in top15.iterrows()
    ]

    fig_eff = go.Figure(go.Bar(
        x=top15["Effektives Gewicht (%)"],
        y=top15.apply(lambda r: f"{r['Name'][:20]} ({r['Ticker']})", axis=1),
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in top15["Effektives Gewicht (%)"]],
        textposition="outside",
    ))

    fig_eff.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        yaxis=dict(autorange="reversed"),
        xaxis_title="Effektives Gewicht (%)",
        margin=dict(l=0, r=40, t=30, b=0),
        height=500,
    )

    st.plotly_chart(fig_eff, use_container_width=True)

    # Volle Tabelle
    with st.expander("Vollständige Tabelle"):
        st.dataframe(weights_df, use_container_width=True, hide_index=True)
