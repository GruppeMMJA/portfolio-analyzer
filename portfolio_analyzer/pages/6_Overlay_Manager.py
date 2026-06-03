"""
Seite 6: Overlay Manager

Konzentrations-Alerts, Hedge-Vorschläge und CVaR-Distribution via Monte Carlo.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.exposure_engine import ExposureEngine
from core.portfolio import Portfolio
from core.risk_engine import RiskEngine
from utils.nav import inject_page

st.set_page_config(page_title="Overlay Manager", layout="wide", initial_sidebar_state="collapsed")

inject_page("overlay")


# ─────────────────────────────────────────────────────
# Portfolio prüfen
# ─────────────────────────────────────────────────────
if "portfolio" not in st.session_state or st.session_state.portfolio.num_positions == 0:
    st.warning("Kein Portfolio geladen. Bitte zuerst Positionen eingeben.")
    st.stop()

portfolio: Portfolio = st.session_state.portfolio

st.markdown("""
<div class="page-hero anim-0">
  <h1>Overlay Manager</h1>
  <p class="page-hero-sub">Konzentrationsrisiken erkennen, Hedges planen, CVaR via Monte Carlo simulieren.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Parameter
# ─────────────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    pos_threshold = st.slider(
        "Einzelposition Schwellenwert (%)",
        min_value=5, max_value=40, value=15, step=5,
        help="Alert wenn eine einzelne Position diesen Anteil überschreitet",
    )
with col_p2:
    sector_threshold = st.slider(
        "Sektor Schwellenwert (%)",
        min_value=20, max_value=70, value=35, step=5,
        help="Alert wenn ein Sektor diesen Anteil überschreitet",
    )
with col_p3:
    history_years = st.selectbox(
        "Historischer Zeitraum",
        list(range(1, 11)), index=2,
        format_func=lambda x: f"{x} Jahr{'e' if x > 1 else ''}",
    )

st.markdown("---")

# ─────────────────────────────────────────────────────
# Renditen laden (aus Cache oder neu)
# ─────────────────────────────────────────────────────
provider = st.session_state.get("data_provider")
if not provider:
    st.error("Keine Datenquelle verbunden. Bitte auf der Hauptseite verbinden.")
    st.stop()

_ticker_hash = hash(tuple(sorted(p.ticker for p in portfolio.positions)))
_cache_key = f"returns_{history_years}y_{_ticker_hash}"

if _cache_key not in st.session_state:
    with st.spinner("Lade historische Daten…"):
        tickers = [p.ticker for p in portfolio.positions]
        try:
            returns_df = provider.get_returns(tickers, years=history_years)
            if not returns_df.empty:
                st.session_state[_cache_key] = returns_df
        except Exception as e:
            st.error(f"Fehler beim Laden der Renditen: {e}")
            st.stop()

returns_df: pd.DataFrame = st.session_state.get(_cache_key, pd.DataFrame())
has_returns = not returns_df.empty

# ─────────────────────────────────────────────────────
# Risk Engine initialisieren (wenn Renditen vorhanden)
# ─────────────────────────────────────────────────────
risk_engine = None
metrics = None
if has_returns:
    weights = {p.ticker: p.weight for p in portfolio.positions}
    try:
        risk_engine = RiskEngine(returns=returns_df, weights=weights)
        metrics = risk_engine.compute_portfolio_metrics()
    except ValueError:
        pass

# ─────────────────────────────────────────────────────
# Exposure Engine
# ─────────────────────────────────────────────────────
exp_engine = ExposureEngine(portfolio)
sector_df  = exp_engine.get_sector_exposure()
asset_df   = exp_engine.get_asset_class_exposure()

# ─────────────────────────────────────────────────────
# Alerts berechnen
# ─────────────────────────────────────────────────────
alerts: list[dict] = []

# 1. Einzelpositionen
for pos in sorted(portfolio.positions, key=lambda p: p.weight, reverse=True):
    w_pct = pos.weight * 100
    if w_pct > pos_threshold:
        alerts.append({
            "typ": "Konzentration",
            "level": "high" if w_pct > pos_threshold * 1.5 else "medium",
            "titel": f"Hohe Konzentration: {pos.ticker}",
            "details": (
                f"**{pos.ticker}** macht **{w_pct:.1f}%** des Portfolios aus "
                f"(Schwellenwert: {pos_threshold}%). "
                "Starke Einzelposition erhöht das idiosynkratische Risiko."
            ),
            "ticker": pos.ticker,
            "is_etf": pos.is_etf,
        })

# 2. Sektoren
if not sector_df.empty:
    for _, row in sector_df.iterrows():
        if row["Gewicht_pct"] > sector_threshold:
            alerts.append({
                "typ": "Sektor",
                "level": "high" if row["Gewicht_pct"] > sector_threshold * 1.3 else "medium",
                "titel": f"Sektor-Klumpenrisiko: {row['Sektor']}",
                "details": (
                    f"Sektor **{row['Sektor']}** hat eine Gewichtung von "
                    f"**{row['Gewicht_pct']:.1f}%** (Schwellenwert: {sector_threshold}%). "
                    "Sektorkonzentration kann zu korrelierten Verlusten führen."
                ),
                "gics": int(row["GICS_Code"]),
            })

# 3. Asset-Klassen Checks
if not asset_df.empty:
    ac_dict = dict(zip(asset_df["Anlageklasse"], asset_df["Gewicht_pct"]))

    # Kein Anleihen-Anteil
    bond_pct = ac_dict.get("Anleihen-ETF", 0)
    if bond_pct < 2:
        alerts.append({
            "typ": "Diversifikation",
            "level": "info",
            "titel": "Keine Anleihen im Portfolio",
            "details": (
                "Das Portfolio enthält keine Anleihen-ETFs (< 2%). "
                "Anleihen können die Volatilität in Krisenphasen deutlich senken."
            ),
        })

    # Krypto > 10%
    crypto_pct = ac_dict.get("Krypto-ETP", 0)
    if crypto_pct > 10:
        alerts.append({
            "typ": "Volatilität",
            "level": "high" if crypto_pct > 20 else "medium",
            "titel": f"Hoher Krypto-Anteil: {crypto_pct:.1f}%",
            "details": (
                f"Krypto-ETPs machen **{crypto_pct:.1f}%** des Portfolios aus. "
                "Bitcoin und andere Kryptowährungen können innerhalb weniger Tage "
                "50–80% verlieren und erhöhen den Max. Drawdown erheblich."
            ),
        })

    # Einzelaktien > 50%
    stock_pct = ac_dict.get("Einzelaktie", 0)
    if stock_pct > 50:
        alerts.append({
            "typ": "Konzentration",
            "level": "medium",
            "titel": f"Hoher Einzelaktien-Anteil: {stock_pct:.1f}%",
            "details": (
                f"**{stock_pct:.1f}%** des Portfolios bestehen aus Einzelaktien. "
                "Einzelaktien tragen idiosynkratisches Risiko (Unternehmensrisiko), "
                "das durch ETFs diversifiziert werden könnte."
            ),
        })

# 4. Korrelations-Check (nur wenn Renditen vorhanden)
if has_returns and risk_engine is not None and len(risk_engine.tickers) >= 3:
    corr = risk_engine.get_correlation_matrix()
    vals = corr.values
    mask = ~np.eye(len(vals), dtype=bool)
    avg_corr = float(np.mean(np.abs(vals[mask])))
    if avg_corr > 0.75:
        alerts.append({
            "typ": "Korrelation",
            "level": "medium",
            "titel": f"Hohe Durchschnittskorrelation: {avg_corr:.2f}",
            "details": (
                f"Die durchschnittliche Paarkorrelation der Portfolio-Bestandteile "
                f"beträgt **{avg_corr:.2f}**. Bei einer Korrelation > 0.75 verlieren "
                "Diversifikationseffekte stark an Wirkung — alle Assets fallen gleichzeitig."
            ),
        })

# ─────────────────────────────────────────────────────
# Alerts anzeigen
# ─────────────────────────────────────────────────────
st.markdown("## Risikoanalyse")

_LEVEL_CONFIG = {
    "high":   ("Kritisch", "#e53e3e", "#2d1515"),
    "medium": ("Mittel",   "#ecc94b", "#2d2a12"),
    "info":   ("Info",     "#4299e1", "#12202d"),
}

if not alerts:
    st.success("Keine Konzentrationsrisiken erkannt. Portfolio ist gut aufgestellt.")
else:
    n_high   = sum(1 for a in alerts if a["level"] == "high")
    n_medium = sum(1 for a in alerts if a["level"] == "medium")
    n_info   = sum(1 for a in alerts if a["level"] == "info")

    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.markdown(
            f'<div style="background:#2d1515;border:1px solid #e53e3e;border-radius:10px;'
            f'padding:0.8rem;text-align:center;">'
            f'<div style="color:#e53e3e;font-size:1.8rem;font-weight:700;">{n_high}</div>'
            f'<div style="color:#a0aec0;font-size:0.75rem;">Kritische Alerts</div></div>',
            unsafe_allow_html=True,
        )
    with col_a2:
        st.markdown(
            f'<div style="background:#2d2a12;border:1px solid #ecc94b;border-radius:10px;'
            f'padding:0.8rem;text-align:center;">'
            f'<div style="color:#ecc94b;font-size:1.8rem;font-weight:700;">{n_medium}</div>'
            f'<div style="color:#a0aec0;font-size:0.75rem;">Mittlere Alerts</div></div>',
            unsafe_allow_html=True,
        )
    with col_a3:
        st.markdown(
            f'<div style="background:#12202d;border:1px solid #4299e1;border-radius:10px;'
            f'padding:0.8rem;text-align:center;">'
            f'<div style="color:#4299e1;font-size:1.8rem;font-weight:700;">{n_info}</div>'
            f'<div style="color:#a0aec0;font-size:0.75rem;">Info-Alerts</div></div>',
            unsafe_allow_html=True,
        )
    with col_a4:
        total = len(alerts)
        risk_color = "#e53e3e" if n_high > 0 else "#ecc94b" if n_medium > 0 else "#48bb78"
        st.markdown(
            f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:10px;'
            f'padding:0.8rem;text-align:center;">'
            f'<div style="color:{risk_color};font-size:1.8rem;font-weight:700;">{total}</div>'
            f'<div style="color:#a0aec0;font-size:0.75rem;">Alerts gesamt</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    for alert in sorted(alerts, key=lambda a: {"high": 0, "medium": 1, "info": 2}[a["level"]]):
        icon, color, bg = _LEVEL_CONFIG[alert["level"]]
        st.markdown(
            f'<div style="background:{bg};border-left:4px solid {color};'
            f'border-radius:6px;padding:0.8rem 1rem;margin-bottom:0.6rem;">'
            f'<div style="color:{color};font-weight:700;font-size:0.95rem;">'
            f'{icon} {alert["titel"]}</div>'
            f'<div style="color:#cbd5e0;font-size:0.85rem;margin-top:0.3rem;">'
            f'{alert["details"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────
# Hedge-Vorschläge
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Hedge-Vorschläge")

# Mapping: Hedge-Strategie-Generierung basierend auf Portfolio-Charakteristika
_hedges: list[dict] = []

# Einzelposition-Hedges
for pos in sorted(portfolio.positions, key=lambda p: p.weight, reverse=True):
    w_pct = pos.weight * 100
    if w_pct > pos_threshold and not pos.is_etf:
        hedge_size = round(w_pct * 0.5, 1)  # 50% der Position hedgen
        _hedges.append({
            "titel": f"Absicherung {pos.ticker} — Protective Put",
            "typ": "Optionsstrategie",
            "instrument": f"Put-Option auf {pos.ticker} (ATM, 3–6 Monate Laufzeit)",
            "sizing": f"Absicherung von ~{hedge_size}% des Portfolios (50% der {pos.ticker}-Position)",
            "kosten": "Optionsprämie: ca. 2–5% p.a. abhängig von Volatilität",
            "details": (
                f"Bei einer Gewichtung von {w_pct:.1f}% trägt {pos.ticker} erhebliches "
                "idiosynkratisches Risiko. Eine At-the-Money Put-Option schützt vor "
                "starken Kursrücksetzern (-20% oder mehr)."
            ),
            "color": "#9f7aea",
        })
    elif w_pct > pos_threshold * 1.5 and pos.is_etf:
        # Sehr großer ETF-Anteil — Index-Hedge
        _hedges.append({
            "titel": f"Tail-Risk-Hedge für {pos.ticker}",
            "typ": "ETF-Strategie",
            "instrument": f"Inverse ETF oder Put-Spread auf Index-Basis",
            "sizing": f"5–10% des Portfolios als Gegenposition",
            "kosten": "Inverse ETFs haben erhöhte laufende Kosten (0.5–1% p.a.)",
            "details": (
                f"{pos.ticker} dominiert mit {w_pct:.1f}% das Portfolio. "
                "Ein Tail-Risk-Hedge via Deep-OTM Puts oder inverses ETF schützt "
                "vor Markt-Crashs (−30% oder mehr) zu günstigen Prämien."
            ),
            "color": "#9f7aea",
        })

# Sektor-Hedges
if not sector_df.empty:
    for _, row in sector_df.iterrows():
        if row["Gewicht_pct"] > sector_threshold:
            gics = int(row["GICS_Code"])
            sektor = row["Sektor"]
            _SECTOR_HEDGE: dict[int, tuple[str, str]] = {
                45: ("SQQQ (ProShares UltraPro Short QQQ)", "Stark negativer Hebel auf NASDAQ — nur für kurzfristige Absicherung"),
                40: ("Shorts auf Finanzwerte-Index (z.B. FAZ)", "Bankenindex-Short falls Zinsnormalisierung abrupt endet"),
                60: ("REITs Short-ETF (z.B. SRS)", "REIT-Sektor reagiert sehr sensitiv auf Zinsanstiege"),
                55: ("Short auf Utilities-Index", "Versorger fallen bei Zinsanstieg wie Anleihen"),
                10: ("Öl-Put-Optionen oder Short-ETF (z.B. SCO)", "Energiesektor fällt bei globaler Nachfrageschwäche"),
            }
            instrument, rationale = _SECTOR_HEDGE.get(
                gics,
                (f"Sektor-Diversifikation durch nicht-korrellierte Assets",
                 "Füge Sektoren mit negativer Korrelation hinzu")
            )
            _hedges.append({
                "titel": f"Sektor-Hedge: {sektor}",
                "typ": "Sektor-Diversifikation",
                "instrument": instrument,
                "sizing": f"2–5% des Portfolios als Gegenposition zum {sektor}-Exposure",
                "kosten": "Abhängig vom Instrument (Futures: Marginkosten; ETF: TER + Spread)",
                "details": rationale,
                "color": "#ed8936",
            })

# Allgemeine Empfehlungen
if not asset_df.empty:
    ac_dict = dict(zip(asset_df["Anlageklasse"], asset_df["Gewicht_pct"]))
    bond_pct = ac_dict.get("Anleihen-ETF", 0)
    gold_pct = ac_dict.get("Rohstoff-ETP", 0)

    if bond_pct < 5:
        _hedges.append({
            "titel": "Anleihen-Beimischung als Diversifikation",
            "typ": "Asset-Allokation",
            "instrument": "iShares Global Aggregate Bond ETF (AGGH.L) oder IUSB",
            "sizing": "5–15% Portfolioanteil empfohlen (je nach Risikopräferenz)",
            "kosten": "TER: 0.10% p.a. — sehr kostengünstig",
            "details": (
                "Anleihen-ETFs haben typischerweise eine negative Korrelation zu "
                "Aktien in Krisenzeiten (-0.3 bis -0.6). Sie dämpfen den Max. Drawdown "
                "und reduzieren die Portfolio-Volatilität spürbar."
            ),
            "color": "#48bb78",
        })

    if gold_pct < 3:
        _hedges.append({
            "titel": "Gold als Krisenabsicherung",
            "typ": "Asset-Allokation",
            "instrument": "Invesco Physical Gold ETC (SGLN.L) oder iShares Physical Gold (IGLN.L)",
            "sizing": "3–7% Portfolioanteil als strategischer Hedge",
            "kosten": "TER: 0.12–0.15% p.a.",
            "details": (
                "Gold zeigt in geopolitischen Krisen und Währungsabwertungsphasen "
                "starke Outperformance. Korrelation zu Aktien nahe 0, "
                "was den Diversifikationseffekt maximiert."
            ),
            "color": "#48bb78",
        })

# Krypto-Hedge
if not asset_df.empty:
    ac_dict = dict(zip(asset_df["Anlageklasse"], asset_df["Gewicht_pct"]))
    crypto_pct = ac_dict.get("Krypto-ETP", 0)
    if crypto_pct > 10:
        _hedges.append({
            "titel": "Krypto-Exposure reduzieren / Tail-Risk-Hedge",
            "typ": "Positionsgröße",
            "instrument": "Bitcoin-Position auf max. 5% begrenzen oder Put-Optionen auf BTC",
            "sizing": f"Aktuelle Krypto-Exposure: {crypto_pct:.1f}% — Ziel: ≤ 5%",
            "kosten": "Rebalancing-Kosten: Handelsgebühren + ggf. Steuer auf Gewinne",
            "details": (
                "Bitcoin kann in Bear-Markets 70–80% verlieren. "
                "Bei > 10% Portfolio-Anteil dominiert Krypto den Max. Drawdown. "
                "Empfehlung: schrittweise Reduktion bei Rallys."
            ),
            "color": "#e53e3e",
        })

if not _hedges:
    st.success("Keine spezifischen Hedge-Maßnahmen notwendig — Portfolio ist gut diversifiziert.")
else:
    for hedge in _hedges:
        color = hedge["color"]
        with st.expander(f"{hedge['titel']} — {hedge['typ']}"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(
                    f'<div style="background:#1a1a2e;border:1px solid #0f3460;'
                    f'border-radius:8px;padding:0.8rem;">'
                    f'<div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Instrument</div>'
                    f'<div style="color:#e2e8f0;font-weight:600;margin-top:0.2rem;">{hedge["instrument"]}</div>'
                    f'<div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;margin-top:0.6rem;">Sizing</div>'
                    f'<div style="color:#e2e8f0;margin-top:0.2rem;">{hedge["sizing"]}</div>'
                    f'<div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;margin-top:0.6rem;">Kosten</div>'
                    f'<div style="color:#ecc94b;margin-top:0.2rem;">{hedge["kosten"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(f"**Begründung:** {hedge['details']}")

# ─────────────────────────────────────────────────────
# CVaR Distribution — Monte Carlo Bootstrap
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## CVaR-Verteilung — Monte Carlo Bootstrap")
st.markdown(
    "Bootstrap-Simulation aus historischen Renditen: "
    "Welche täglichen Portfolio-Verluste sind in Extremszenarien möglich?"
)

if not has_returns or risk_engine is None:
    st.info("Historische Renditen werden benötigt. Bitte zuerst die Risiko & Markowitz Seite laden.")
else:
    n_sims = st.select_slider(
        "Anzahl Bootstrap-Simulationen",
        options=[1_000, 5_000, 10_000, 25_000, 50_000],
        value=10_000,
    )

    with st.spinner(f"Bootstrap mit {n_sims:,} Simulationen…"):
        # Portfolio-Tagesrenditen aus Historik
        port_daily = (returns_df[risk_engine.tickers] * risk_engine.w).sum(axis=1).dropna()

        # Bootstrap: zufällig Tagesrenditen ziehen (mit Zurücklegen)
        np.random.seed(42)
        n_obs = len(port_daily)
        boot_indices = np.random.randint(0, n_obs, size=(n_sims,))
        simulated_returns = port_daily.values[boot_indices] * 100  # in %

        # Kennzahlen berechnen
        var_95  = float(np.percentile(simulated_returns, 5))
        var_99  = float(np.percentile(simulated_returns, 1))
        cvar_95 = float(simulated_returns[simulated_returns <= var_95].mean())
        cvar_99 = float(simulated_returns[simulated_returns <= var_99].mean())
        mean_r  = float(np.mean(simulated_returns))

    # Histogram-Plot
    col_hist_main, col_hist_stats = st.columns([3, 1])

    with col_hist_main:
        fig_hist = go.Figure()

        # Haupthistogramm
        fig_hist.add_trace(go.Histogram(
            x=simulated_returns,
            nbinsx=120,
            marker_color="#667eea",
            opacity=0.7,
            name="Rendite-Verteilung",
        ))

        # Verlustzone einfärben (< VaR 95%)
        fig_hist.add_trace(go.Histogram(
            x=simulated_returns[simulated_returns <= var_95],
            nbinsx=40,
            marker_color="#e53e3e",
            opacity=0.8,
            name=f"Verlustzone (< VaR 95%)",
        ))

        # CVaR 95% Linie
        fig_hist.add_vline(
            x=var_95,
            line=dict(color="#ed8936", width=2, dash="dash"),
            annotation_text=f"VaR 95%: {var_95:.2f}%",
            annotation_position="top right",
            annotation_font=dict(color="#ed8936", size=11),
        )
        fig_hist.add_vline(
            x=cvar_95,
            line=dict(color="#e53e3e", width=2, dash="solid"),
            annotation_text=f"CVaR 95%: {cvar_95:.2f}%",
            annotation_position="top left",
            annotation_font=dict(color="#e53e3e", size=11),
        )
        fig_hist.add_vline(
            x=var_99,
            line=dict(color="#9f7aea", width=1.5, dash="dot"),
            annotation_text=f"VaR 99%: {var_99:.2f}%",
            annotation_position="bottom right",
            annotation_font=dict(color="#9f7aea", size=10),
        )
        fig_hist.add_vline(
            x=mean_r,
            line=dict(color="#48bb78", width=1.5, dash="dot"),
            annotation_text=f"Ø Rendite: {mean_r:.3f}%",
            annotation_position="top right",
            annotation_font=dict(color="#48bb78", size=10),
        )

        fig_hist.update_layout(
            xaxis_title="Tägliche Portfolio-Rendite (%)",
            yaxis_title="Häufigkeit",
            barmode="overlay",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0d1117",
            font=dict(color="#e2e8f0"),
            legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="#0f3460", borderwidth=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=420,
            xaxis=dict(gridcolor="#1a202c", zeroline=False),
            yaxis=dict(gridcolor="#1a202c", zeroline=False),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_hist_stats:
        st.markdown("#### Risikokennzahlen")

        _kpi_items = [
            ("Ø Tagesrendite", f"{mean_r:+.3f}%", "#48bb78"),
            ("VaR 95% (tägl.)", f"{var_95:.3f}%", "#ed8936"),
            ("CVaR 95% (tägl.)", f"{cvar_95:.3f}%", "#e53e3e"),
            ("VaR 99% (tägl.)", f"{var_99:.3f}%", "#9f7aea"),
            ("CVaR 99% (tägl.)", f"{cvar_99:.3f}%", "#e53e3e"),
        ]
        for label, value, color in _kpi_items:
            st.markdown(
                f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:8px;'
                f'padding:0.5rem 0.8rem;margin-bottom:0.4rem;display:flex;justify-content:space-between;">'
                f'<span style="color:#a0aec0;font-size:0.82rem;">{label}</span>'
                f'<span style="color:{color};font-weight:700;">{value}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Annualisierte Werte
        st.markdown("---")
        st.markdown("**Annualisiert (×√252):**")
        _kpi_annual = [
            ("VaR 95%", f"{var_95 * np.sqrt(252):.1f}%", "#ed8936"),
            ("CVaR 95%", f"{cvar_95 * np.sqrt(252):.1f}%", "#e53e3e"),
        ]
        for label, value, color in _kpi_annual:
            st.markdown(
                f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:8px;'
                f'padding:0.5rem 0.8rem;margin-bottom:0.4rem;display:flex;justify-content:space-between;">'
                f'<span style="color:#a0aec0;font-size:0.82rem;">{label}</span>'
                f'<span style="color:{color};font-weight:700;">{value}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.caption(
            f"Basierend auf {n_sims:,} Bootstrap-Stichproben aus "
            f"{len(port_daily):,} historischen Tagesrenditen."
        )

        # Interpretation
        st.markdown("---")
        if abs(cvar_95) > 3:
            st.error(
                f"CVaR 95% = **{cvar_95:.2f}%** tägl. bedeutet: "
                "In den schlimmsten 5% der Tage verliert das Portfolio "
                f"im Schnitt **{abs(cvar_95):.2f}%**. Das ist erheblich."
            )
        elif abs(cvar_95) > 1.5:
            st.warning(
                f"CVaR 95% = **{cvar_95:.2f}%** tägl. — "
                "Moderat erhöhtes Tail-Risiko für ein Aktienportfolio."
            )
        else:
            st.success(
                f"CVaR 95% = **{cvar_95:.2f}%** tägl. — "
                "Geringes Tail-Risiko, gut diversifiziertes Portfolio."
            )
