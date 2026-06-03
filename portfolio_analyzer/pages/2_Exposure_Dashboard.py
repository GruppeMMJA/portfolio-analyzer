"""
Seite 2: Exposure Dashboard

Visualisiert Länder-, Währungs- und Branchen-Exposure des Portfolios.
Weltkarte (Choropleth), Treemap für Sektoren, Balkendiagramme.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from core.portfolio import Portfolio
from core.exposure_engine import ExposureEngine
from utils.constants import SECTOR_COLORS, BENCHMARK_INDICES
from utils.nav import inject_page

st.set_page_config(page_title="Exposure Dashboard", layout="wide", initial_sidebar_state="collapsed")

inject_page("exposure")


# ─────────────────────────────────────────────────────
# Portfolio prüfen
# ─────────────────────────────────────────────────────
if "portfolio" not in st.session_state or st.session_state.portfolio.num_positions == 0:
    st.warning("Kein Portfolio geladen. Bitte zuerst unter **Portfolio Eingabe** Positionen hinzufügen.")
    st.stop()

portfolio: Portfolio = st.session_state.portfolio

st.markdown(f"""
<div class="page-hero anim-0">
  <h1>Exposure Dashboard</h1>
  <p class="page-hero-sub">{portfolio.num_positions} Positionen &nbsp;&middot;&nbsp; Gesamtwert: {portfolio.total_value:,.2f} €</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Auto-Anreicherung: Fehlende Stammdaten nachladen
# ─────────────────────────────────────────────────────
provider = st.session_state.get("data_provider")
_missing = [
    p for p in portfolio.positions
    if not p.country and not p.gics_sector and not p.etf_sector_weights
]
if _missing and provider:
    col_warn, col_btn = st.columns([3, 1])
    with col_warn:
        st.warning(
            f"{len(_missing)} Position(en) haben keine Stammdaten (Land, Sektor, Währung). "
            "Bitte anreichern."
        )
    with col_btn:
        if st.button("Jetzt anreichern", type="primary", use_container_width=True):
            with st.spinner("Lade Stammdaten..."):
                for pos in _missing:
                    try:
                        provider.enrich_position(pos)
                    except Exception as e:
                        st.warning(f"{pos.ticker}: {e}")
            st.rerun()
elif _missing and not provider:
    st.warning(
        "Stammdaten fehlen und keine Datenquelle verbunden. "
        "Bitte auf der Hauptseite eine Datenquelle auswählen und verbinden."
    )

engine = ExposureEngine(portfolio)

# ─────────────────────────────────────────────────────
# Tabs: Länder / Währungen / Branchen
# ─────────────────────────────────────────────────────
tab_countries, tab_currencies, tab_sectors, tab_assetclass = st.tabs(
    ["Länder", "Währungen", "Branchen", "Anlageklassen"]
)

# ─────────────────────────────────────────────────────
# Tab 1: Länder-Exposure
# ─────────────────────────────────────────────────────
with tab_countries:
    country_df = engine.get_country_exposure()

    if country_df.empty:
        st.info("Keine Länderdaten verfügbar. Ist die Datenquelle verbunden?")
    else:
        # Interaktive Weltkarte (zoom + pan)
        st.markdown("### Länder-Exposure")

        map_df = country_df[country_df["ISO_Alpha3"] != ""].copy()

        fig_map = px.choropleth(
            map_df,
            locations="ISO_Alpha3",
            color="Gewicht_pct",
            hover_name="Land",
            hover_data={"Gewicht_pct": ":.2f", "Region": True, "ISO_Alpha3": False},
            color_continuous_scale=[
                [0.0,  "#1a2744"],
                [0.05, "#1e3a6e"],
                [0.15, "#1d5fa8"],
                [0.35, "#2b83d1"],
                [0.60, "#56aee8"],
                [0.80, "#89ccf5"],
                [1.0,  "#c8e9ff"],
            ],
            labels={"Gewicht_pct": "Gewicht (%)"},
        )

        fig_map.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="rgba(255,255,255,.3)",
                projection_type="natural earth",
                bgcolor="rgba(0,0,0,0)",
                landcolor="#0f1923",
                showocean=True,
                oceancolor="#050d18",
                showlakes=False,
                showcountries=True,
                countrycolor="rgba(255,255,255,.1)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", family="Inter, sans-serif"),
            margin=dict(l=0, r=0, t=10, b=0),
            height=480,
            coloraxis_colorbar=dict(
                title="Gewicht (%)",
                ticksuffix="%",
                tickfont=dict(color="#e2e8f0"),
                title_font=dict(color="#e2e8f0"),
            ),
            dragmode="pan",
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": False},
        )

        # Balkendiagramm Top-Länder
        col_bar, col_table = st.columns([2, 1])

        with col_bar:
            top_countries = country_df.head(10)
            fig_bar = px.bar(
                top_countries,
                x="Gewicht_pct",
                y="Land",
                orientation="h",
                color="Region",
                text="Gewicht_pct",
                labels={"Gewicht_pct": "Gewicht (%)", "Land": ""},
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                yaxis=dict(autorange="reversed"),
                showlegend=True,
                legend=dict(orientation="h", y=-0.15),
                margin=dict(l=0, r=40, t=30, b=40),
                height=400,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_table:
            st.markdown("#### Alle Länder")
            display_df = country_df[["Land", "Region", "Gewicht_pct"]].copy()
            display_df.columns = ["Land", "Region", "Gewicht (%)"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Regionen-Zusammenfassung
        st.markdown("#### Regionale Verteilung")
        region_df = country_df.groupby("Region")["Gewicht_pct"].sum().reset_index()
        region_df = region_df.sort_values("Gewicht_pct", ascending=False)

        fig_pie = px.pie(
            region_df,
            values="Gewicht_pct",
            names="Region",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=350,
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ─────────────────────────────────────────────────────
# Tab 2: Währungs-Exposure
# ─────────────────────────────────────────────────────
with tab_currencies:
    currency_df = engine.get_currency_exposure()

    if currency_df.empty:
        st.info("Keine Währungsdaten verfügbar.")
    else:
        st.markdown("### Währungs-Exposure")

        col_chart, col_detail = st.columns([2, 1])

        with col_chart:
            fig_curr = px.bar(
                currency_df.head(10),
                x="Gewicht_pct",
                y="Name",
                orientation="h",
                color="Region",
                text="Gewicht_pct",
                labels={"Gewicht_pct": "Gewicht (%)", "Name": ""},
            )
            fig_curr.update_traces(
                texttemplate="%{text:.1f}%", textposition="outside"
            )
            fig_curr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                yaxis=dict(autorange="reversed"),
                legend=dict(orientation="h", y=-0.15),
                margin=dict(l=0, r=40, t=30, b=40),
                height=400,
            )
            st.plotly_chart(fig_curr, use_container_width=True)

        with col_detail:
            st.markdown("#### Alle Währungen")
            display_curr = currency_df[["Währung", "Name", "Gewicht_pct"]].copy()
            display_curr.columns = ["Code", "Währung", "Gewicht (%)"]
            st.dataframe(display_curr, use_container_width=True, hide_index=True)

        # Regionale Zusammenfassung
        st.markdown("#### Währungsregionen")
        region_curr = currency_df.groupby("Region")["Gewicht_pct"].sum().reset_index()
        region_curr = region_curr.sort_values("Gewicht_pct", ascending=False)

        fig_region = px.pie(
            region_curr,
            values="Gewicht_pct",
            names="Region",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_region.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=350,
        )
        st.plotly_chart(fig_region, use_container_width=True)


# ─────────────────────────────────────────────────────
# Tab 3: Branchen/Sektor-Exposure
# ─────────────────────────────────────────────────────
with tab_sectors:
    sector_df = engine.get_sector_exposure()

    if sector_df.empty:
        st.info("Keine Sektordaten verfügbar.")
    else:
        st.markdown("### Branchen-Exposure (GICS-Sektoren)")

        col_tree, col_bar = st.columns([1, 1])

        with col_tree:
            # Treemap
            fig_tree = px.treemap(
                sector_df[sector_df["Gewicht_pct"] > 0],
                path=["Sektor"],
                values="Gewicht_pct",
                color="Gewicht_pct",
                color_continuous_scale="Blues",
            )
            fig_tree.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=0, r=0, t=30, b=0),
                height=450,
                coloraxis_colorbar=dict(title="Gewicht (%)"),
            )
            fig_tree.update_traces(
                textinfo="label+percent root",
                textfont=dict(size=14),
            )
            st.plotly_chart(fig_tree, use_container_width=True)

        with col_bar:
            # Balkendiagramm
            sector_sorted = sector_df.sort_values("Gewicht_pct", ascending=True)

            colors = [SECTOR_COLORS.get(s, "#718096") for s in sector_sorted["Sektor"]]

            fig_sec_bar = go.Figure(go.Bar(
                x=sector_sorted["Gewicht_pct"],
                y=sector_sorted["Sektor"],
                orientation="h",
                text=[f"{v:.1f}%" for v in sector_sorted["Gewicht_pct"]],
                textposition="outside",
                marker_color=colors,
            ))
            fig_sec_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                margin=dict(l=0, r=40, t=30, b=0),
                height=450,
                xaxis_title="Gewicht (%)",
            )
            st.plotly_chart(fig_sec_bar, use_container_width=True)

        # Detail-Tabelle
        st.markdown("#### Sektor-Details")
        display_sec = sector_df[["Sektor", "Gewicht_pct"]].copy()
        display_sec.columns = ["Sektor", "Gewicht (%)"]
        st.dataframe(display_sec, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────
# Tab 4: Anlageklassen-Exposure
# ─────────────────────────────────────────────────────
with tab_assetclass:
    ac_df = engine.get_asset_class_exposure()

    if ac_df.empty:
        st.info("Keine Daten verfügbar.")
    else:
        st.markdown("### Anlageklassen-Exposure")

        # Farben je Klasse
        _AC_COLORS = {
            "Aktien-ETF":          "#4299e1",
            "Einzelaktie":         "#48bb78",
            "Anleihen-ETF":        "#ed8936",
            "Rohstoff-ETP":        "#ecc94b",
            "Immobilien-ETF":      "#9f7aea",
            "Krypto-ETP":          "#fc8181",
            "Sonstige / Unbekannt": "#718096",
        }
        colors = [_AC_COLORS.get(c, "#718096") for c in ac_df["Anlageklasse"]]

        col_donut, col_bar = st.columns([1, 1])

        with col_donut:
            fig_donut = go.Figure(go.Pie(
                labels=ac_df["Anlageklasse"],
                values=ac_df["Gewicht_pct"],
                hole=0.5,
                marker_colors=colors,
                textinfo="label+percent",
                textfont=dict(size=13),
                hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>",
            ))
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                height=380,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_bar:
            fig_ac_bar = go.Figure(go.Bar(
                x=ac_df["Gewicht_pct"],
                y=ac_df["Anlageklasse"],
                orientation="h",
                marker_color=colors,
                text=[f"{v:.1f}%" for v in ac_df["Gewicht_pct"]],
                textposition="outside",
            ))
            fig_ac_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                xaxis_title="Gewicht (%)",
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=60, t=30, b=0),
                height=380,
            )
            st.plotly_chart(fig_ac_bar, use_container_width=True)

        # KPI-Zeile
        st.markdown("---")
        kpi_cols = st.columns(len(ac_df))
        for col, (_, row) in zip(kpi_cols, ac_df.iterrows()):
            color = _AC_COLORS.get(row["Anlageklasse"], "#718096")
            with col:
                st.markdown(
                    f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:10px;'
                    f'padding:0.8rem;text-align:center;">'
                    f'<div style="color:#a0aec0;font-size:0.7rem;text-transform:uppercase;">{row["Anlageklasse"]}</div>'
                    f'<div style="color:{color};font-size:1.3rem;font-weight:700;">{row["Gewicht_pct"]:.1f}%</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Positions-Tabelle
        st.markdown("#### Positionen")
        pos_rows = [{
            "Ticker": p.ticker,
            "Name": p.name or p.ticker,
            "Typ": p.asset_type.value,
            "Gewicht (%)": round(p.weight * 100, 2),
            "Marktwert (€)": round(p.market_value, 2),
        } for p in portfolio.positions]
        st.dataframe(pd.DataFrame(pos_rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────
# Benchmark-Vergleich (Über-/Untergewichtung)
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Benchmark-Vergleich")
st.markdown("Vergleiche dein Sektor-Exposure mit einem Referenzindex.")

# Referenz-Sektor-Gewichtungen bekannter Indizes
BENCHMARK_SECTOR_WEIGHTS = {
    "MSCI World": {
        "Informationstechnologie": 24.0, "Finanzen": 15.5, "Gesundheit": 12.0,
        "Zyklischer Konsum": 11.0, "Industrie": 10.5, "Kommunikation": 8.0,
        "Basiskonsumgüter": 7.0, "Energie": 4.5, "Grundstoffe": 3.5,
        "Versorger": 2.5, "Immobilien": 2.0,
    },
    "S&P 500": {
        "Informationstechnologie": 31.0, "Finanzen": 13.0, "Gesundheit": 12.0,
        "Zyklischer Konsum": 10.5, "Kommunikation": 9.0, "Industrie": 8.5,
        "Basiskonsumgüter": 6.0, "Energie": 3.5, "Grundstoffe": 2.5,
        "Versorger": 2.5, "Immobilien": 2.0,
    },
    "EURO STOXX 600": {
        "Finanzen": 18.0, "Industrie": 16.0, "Gesundheit": 14.0,
        "Basiskonsumgüter": 10.0, "Informationstechnologie": 9.0,
        "Zyklischer Konsum": 8.5, "Grundstoffe": 7.0, "Energie": 6.0,
        "Versorger": 4.5, "Kommunikation": 3.5, "Immobilien": 3.0,
    },
}

benchmark_choice = st.selectbox(
    "Benchmark-Index",
    list(BENCHMARK_SECTOR_WEIGHTS.keys()),
    index=0,
)

if benchmark_choice and not sector_df.empty:
    bench_sectors = BENCHMARK_SECTOR_WEIGHTS[benchmark_choice]

    # Vergleichs-DataFrame aufbauen
    all_sectors = sorted(set(sector_df["Sektor"].tolist()) | set(bench_sectors.keys()))

    comparison_rows = []
    for sector in all_sectors:
        portfolio_w = float(
            sector_df.loc[sector_df["Sektor"] == sector, "Gewicht_pct"].sum()
        ) if sector in sector_df["Sektor"].values else 0.0
        bench_w = bench_sectors.get(sector, 0.0)
        diff = portfolio_w - bench_w

        comparison_rows.append({
            "Sektor": sector,
            "Portfolio (%)": round(portfolio_w, 1),
            f"{benchmark_choice} (%)": round(bench_w, 1),
            "Differenz (%)": round(diff, 1),
        })

    comp_df = pd.DataFrame(comparison_rows).sort_values(
        "Differenz (%)", ascending=False
    )

    # Butterfly-Chart (Über-/Untergewichtung)
    fig_comp = go.Figure()

    colors = [
        "#48bb78" if d > 0 else "#fc8181"
        for d in comp_df["Differenz (%)"]
    ]

    fig_comp.add_trace(go.Bar(
        x=comp_df["Differenz (%)"],
        y=comp_df["Sektor"],
        orientation="h",
        marker_color=colors,
        text=[f"{d:+.1f}%" for d in comp_df["Differenz (%)"]],
        textposition="outside",
    ))

    fig_comp.update_layout(
        title=f"Über-/Untergewichtung vs. {benchmark_choice}",
        xaxis_title="Differenz (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=50, t=50, b=0),
        height=450,
        shapes=[
            dict(type="line", x0=0, x1=0, y0=-0.5, y1=len(comp_df) - 0.5,
                 line=dict(color="#718096", width=1, dash="dash")),
        ],
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    # Tabelle
    with st.expander("Detail-Tabelle"):
        st.dataframe(
            comp_df.style.map(
                lambda v: "color: #48bb78" if isinstance(v, (int, float)) and v > 0
                else "color: #fc8181" if isinstance(v, (int, float)) and v < 0
                else "",
                subset=["Differenz (%)"],
            ),
            use_container_width=True,
            hide_index=True,
        )
