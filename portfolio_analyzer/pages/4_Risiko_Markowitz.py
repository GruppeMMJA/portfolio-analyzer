"""
Seite 4: Risiko & Markowitz

Volatilität, Sharpe Ratio, Efficient Frontier, Korrelationsmatrix.
Das aktuelle Portfolio als Punkt auf der Frontier.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from core.portfolio import Portfolio
from core.risk_engine import RiskEngine
from utils.constants import BENCHMARK_INDICES
from utils.nav import inject_page

st.set_page_config(page_title="Risiko & Markowitz", layout="wide", initial_sidebar_state="collapsed")

inject_page("risiko")


# ─────────────────────────────────────────────────────
# Portfolio prüfen
# ─────────────────────────────────────────────────────
if "portfolio" not in st.session_state or st.session_state.portfolio.num_positions == 0:
    st.warning("Kein Portfolio geladen. Bitte zuerst Positionen eingeben.")
    st.stop()

portfolio: Portfolio = st.session_state.portfolio

st.markdown("""
<div class="page-hero anim-0">
  <h1>Risiko &amp; Markowitz</h1>
  <p class="page-hero-sub">Volatilität, Sharpe Ratio, Efficient Frontier und Korrelationsmatrix.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Parameter
# ─────────────────────────────────────────────────────
col_params1, col_params2, col_params3 = st.columns(3)

with col_params1:
    risk_free_rate = st.number_input(
        "Risikofreier Zins (%)",
        min_value=0.0, max_value=10.0, value=3.0, step=0.25,
        help="Aktueller risikofreier Zinssatz (z.B. Bundesanleihe 2J)",
    ) / 100

with col_params2:
    history_years = st.selectbox(
        "Historische Daten",
        list(range(1, 11)),
        index=2,
        help="Zeitraum für die Rendite-/Volatilitätsberechnung",
        format_func=lambda x: f"{x} Jahr{'e' if x > 1 else ''}",
    )

with col_params3:
    benchmark_name = st.selectbox(
        "Benchmark",
        ["Kein Benchmark"] + list(BENCHMARK_INDICES.keys()),
        index=0,
        help="Vergleichsindex für die Analyse",
    )

# ─────────────────────────────────────────────────────
# Daten laden
# ─────────────────────────────────────────────────────
provider = st.session_state.get("data_provider")
if not provider:
    st.error("Keine Datenquelle verbunden. Bitte auf der Hauptseite verbinden.")
    st.stop()

# Renditen laden (mit Caching im Session State)
# Cache-Key enthält Ticker-Set damit Portfoliowechsel den Cache invalidiert
_ticker_hash = hash(tuple(sorted(p.ticker for p in portfolio.positions)))
cache_key = f"returns_{history_years}y_{_ticker_hash}"
if cache_key not in st.session_state or st.button("Daten neu laden"):
    with st.spinner(f"Lade historische Renditen ({history_years} Jahre)..."):
        tickers = [p.ticker for p in portfolio.positions]

        try:
            returns_df = provider.get_returns(tickers, years=history_years)

            if returns_df.empty:
                st.error("Keine historischen Daten verfügbar.")
                st.stop()

            st.session_state[cache_key] = returns_df
            st.session_state.returns_loaded = True

            # Info über fehlende Ticker
            missing = set(tickers) - set(returns_df.columns)
            if missing:
                st.warning(
                    f"Keine historischen Daten für: {', '.join(missing)}. "
                    f"Diese Positionen werden bei der Risikoberechnung ignoriert."
                )

        except Exception as e:
            st.error(f"Fehler beim Laden der Renditen: {e}")
            st.stop()

returns_df = st.session_state.get(cache_key)
if returns_df is None or returns_df.empty:
    st.info("Bitte zuerst historische Daten laden (Button oben).")
    st.stop()

# ─────────────────────────────────────────────────────
# Risk Engine initialisieren
# ─────────────────────────────────────────────────────
weights = {p.ticker: p.weight for p in portfolio.positions}

try:
    risk_engine = RiskEngine(
        returns=returns_df,
        weights=weights,
        risk_free_rate=risk_free_rate,
    )
except ValueError as e:
    st.error(f"Fehler bei der Risikoberechnung: {e}")
    st.stop()

# ─────────────────────────────────────────────────────
# KPI-Karten
# ─────────────────────────────────────────────────────
metrics = risk_engine.compute_portfolio_metrics()

# Beta berechnen (nur wenn Benchmark gewählt)
portfolio_beta = None
if benchmark_name != "Kein Benchmark":
    try:
        bench_info = BENCHMARK_INDICES[benchmark_name]
        bench_prices = provider.get_benchmark_prices(bench_info["ticker_yf"], years=history_years)
        if not bench_prices.empty:
            bench_ret_series = np.log(bench_prices / bench_prices.shift(1)).dropna()
            portfolio_beta = risk_engine.compute_beta(bench_ret_series)
    except Exception:
        portfolio_beta = None

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

with col1:
    color = "#48bb78" if metrics.annual_return > 0 else "#fc8181"
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Rendite (p.a.)</div>
        <div style="color:{color};font-size:1.5rem;font-weight:700;">{metrics.annual_return*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Volatilität (p.a.)</div>
        <div style="color:#e2e8f0;font-size:1.5rem;font-weight:700;">{metrics.annual_volatility*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    sr_color = "#48bb78" if metrics.sharpe_ratio > 1 else "#ecc94b" if metrics.sharpe_ratio > 0.5 else "#fc8181"
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Sharpe Ratio</div>
        <div style="color:{sr_color};font-size:1.5rem;font-weight:700;">{metrics.sharpe_ratio:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Max Drawdown</div>
        <div style="color:#fc8181;font-size:1.5rem;font-weight:700;">{metrics.max_drawdown*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">VaR 95% (tägl.)</div>
        <div style="color:#ed8936;font-size:1.5rem;font-weight:700;">{metrics.var_95*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">
        <div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">VaR 99% (tägl.)</div>
        <div style="color:#e53e3e;font-size:1.5rem;font-weight:700;">{metrics.var_99*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    if portfolio_beta is not None and not (isinstance(portfolio_beta, float) and portfolio_beta != portfolio_beta):
        beta_color = "#48bb78" if portfolio_beta < 1.0 else "#ecc94b" if portfolio_beta < 1.3 else "#fc8181"
        beta_val = f"{portfolio_beta:.2f}"
    else:
        beta_color = "#718096"
        beta_val = "—"
    st.markdown(
        f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">'
        f'<div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">Beta (vs. Benchmark)</div>'
        f'<div style="color:{beta_color};font-size:1.5rem;font-weight:700;">{beta_val}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col8:
    st.markdown(
        f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:12px;padding:1rem;text-align:center;">'
        f'<div style="color:#a0aec0;font-size:0.75rem;text-transform:uppercase;">CVaR 95% (tägl.)</div>'
        f'<div style="color:#9f7aea;font-size:1.5rem;font-weight:700;">{metrics.cvar_95*100:.2f}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────────────
# Portfolio Score
# ─────────────────────────────────────────────────────
st.markdown("### Portfolio-Score")

def _score_rendite(annual_return: float) -> float:
    r = annual_return
    if r < 0:
        return max(0.0, 10.0 + r * 100)
    elif r < 0.08:
        return 10.0 + (r / 0.08) * 50.0
    elif r < 0.16:
        return 60.0 + ((r - 0.08) / 0.08) * 35.0
    else:
        return min(100.0, 95.0 + (r - 0.16) * 62.5)

def _score_risiko(annual_vol: float, max_drawdown: float) -> float:
    if annual_vol < 0.10:
        vol_score = 70.0
    elif annual_vol < 0.20:
        vol_score = 70.0 - ((annual_vol - 0.10) / 0.10) * 30.0
    elif annual_vol < 0.35:
        vol_score = 40.0 - ((annual_vol - 0.20) / 0.15) * 30.0
    else:
        vol_score = max(0.0, 10.0 - (annual_vol - 0.35) * 50.0)

    dd = abs(max_drawdown)
    if dd < 0.10:
        dd_score = 30.0
    elif dd < 0.25:
        dd_score = 30.0 - ((dd - 0.10) / 0.15) * 20.0
    elif dd < 0.50:
        dd_score = 10.0 - ((dd - 0.25) / 0.25) * 10.0
    else:
        dd_score = 0.0
    return min(100.0, max(0.0, vol_score + dd_score))

def _score_effizienz(sharpe: float) -> float:
    if sharpe < 0:
        return max(0.0, 10.0 + sharpe * 10.0)
    elif sharpe < 0.5:
        return 10.0 + (sharpe / 0.5) * 25.0
    elif sharpe < 1.0:
        return 35.0 + ((sharpe - 0.5) / 0.5) * 25.0
    elif sharpe < 1.5:
        return 60.0 + ((sharpe - 1.0) / 0.5) * 20.0
    elif sharpe < 2.0:
        return 80.0 + ((sharpe - 1.5) / 0.5) * 10.0
    else:
        return min(100.0, 90.0 + (sharpe - 2.0) * 5.0)

def _score_diversifikation(port, corr_matrix) -> float:
    w_list = [p.weight for p in port.positions]
    n = len(w_list)
    if n == 0:
        return 0.0
    hhi = sum(w ** 2 for w in w_list)
    min_hhi = 1.0 / n
    hhi_norm = (hhi - min_hhi) / (1.0 - min_hhi) if n > 1 else 1.0
    hhi_score = (1.0 - hhi_norm) * 60.0
    n_score = min(20.0, (n - 1) / 19.0 * 20.0)
    corr_score = 20.0
    if corr_matrix is not None and not corr_matrix.empty and len(corr_matrix) > 1:
        vals = corr_matrix.values
        mask = ~np.eye(len(vals), dtype=bool)
        avg_corr = float(np.mean(np.abs(vals[mask])))
        corr_score = (1.0 - avg_corr) * 20.0
    return min(100.0, max(0.0, hhi_score + n_score + corr_score))

def _score_stabilitaet(max_drawdown: float, var_99: float) -> float:
    dd = abs(max_drawdown)
    if dd < 0.10:
        dd_score = 70.0
    elif dd < 0.20:
        dd_score = 70.0 - ((dd - 0.10) / 0.10) * 30.0
    elif dd < 0.40:
        dd_score = 40.0 - ((dd - 0.20) / 0.20) * 30.0
    elif dd < 0.60:
        dd_score = 10.0 - ((dd - 0.40) / 0.20) * 10.0
    else:
        dd_score = 0.0
    v = abs(var_99)
    if v < 0.02:
        var_score = 30.0
    elif v < 0.04:
        var_score = 30.0 - ((v - 0.02) / 0.02) * 15.0
    elif v < 0.06:
        var_score = 15.0 - ((v - 0.04) / 0.02) * 10.0
    else:
        var_score = max(0.0, 5.0 - (v - 0.06) * 100.0)
    return min(100.0, max(0.0, dd_score + var_score))

def _grade(score: float):
    score = round(score)
    if score >= 95:
        return "A+", "Ausgezeichnet", "#48bb78"
    elif score >= 85:
        return "A", "Sehr gut", "#48bb78"
    elif score >= 75:
        return "B", "Gut", "#667eea"
    elif score >= 65:
        return "C", "Befriedigend", "#ed8936"
    elif score >= 55:
        return "D", "Ausreichend", "#ecc94b"
    else:
        return "F", "Ungenügend", "#e53e3e"

# Scores berechnen
corr_matrix_for_score = risk_engine.get_correlation_matrix()

s_rendite      = _score_rendite(metrics.annual_return)
s_risiko       = _score_risiko(metrics.annual_volatility, metrics.max_drawdown)
s_effizienz    = _score_effizienz(metrics.sharpe_ratio)
s_diversi      = _score_diversifikation(portfolio, corr_matrix_for_score)
s_stabilitaet  = _score_stabilitaet(metrics.max_drawdown, metrics.var_99)

overall = round(0.20 * s_rendite + 0.25 * s_risiko + 0.25 * s_effizienz +
                0.15 * s_diversi + 0.15 * s_stabilitaet)

g_overall  = _grade(overall)
g_rendite  = _grade(s_rendite)
g_risiko   = _grade(s_risiko)
g_eff      = _grade(s_effizienz)
g_div      = _grade(s_diversi)
g_stab     = _grade(s_stabilitaet)

# Empfehlung generieren
_dim_scores = {
    "Rendite":        s_rendite,
    "Risiko":         s_risiko,
    "Effizienz":      s_effizienz,
    "Diversifikation": s_diversi,
    "Stabilität":     s_stabilitaet,
}
_weakest = min(_dim_scores, key=_dim_scores.get)
_recommendations = {
    "Rendite":         "Schwächster Bereich: Rendite. Erwäge wachstumsstärkere Positionen oder eine Reduktion defensiver Anlagen.",
    "Risiko":          "Schwächster Bereich: Risiko. Reduziere Konzentration in volatilen Assets oder füge Anleihen/Gold als Puffer hinzu.",
    "Effizienz":       "Schwächster Bereich: Effizienz. Das Rendite-Risiko-Verhältnis ist verbesserungswürdig — Sharpe Ratio erhöhen durch bessere Diversifikation.",
    "Diversifikation": "Schwächster Bereich: Diversifikation. Füge mehr unkorrelierte Positionen oder Anlageklassen hinzu.",
    "Stabilität":      "Schwächster Bereich: Stabilität. Das Portfolio zeigte hohe Verluste in Stressszenarien — defensive Werte oder Hedges prüfen.",
}
_overall_label = g_overall[1]
_recommendation_text = (
    f"Solides Portfolio mit Verbesserungspotenzial. {_recommendations[_weakest]}"
    if overall >= 65
    else f"Portfolio mit deutlichem Verbesserungspotenzial. {_recommendations[_weakest]}"
)

def _bar_row(label: str, subtitle: str, grade: str, label_text: str, color: str, score: float) -> str:
    pct = int(round(score))
    return (
        f'<div style="margin-bottom:1.1rem;">'
        f'<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:0.3rem;">'
        f'<span style="font-weight:600;font-size:0.95rem;color:#e2e8f0;">{label} <span style="font-weight:400;color:#718096;font-size:0.82rem;">— {label_text}</span></span>'
        f'<span style="font-weight:700;font-size:1.05rem;color:{color};">{grade}&nbsp;&nbsp;{pct}</span>'
        f'</div>'
        f'<div style="background:#2d3748;border-radius:6px;height:10px;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{color};border-radius:6px;"></div>'
        f'</div>'
        f'<div style="color:#718096;font-size:0.75rem;margin-top:0.2rem;">{subtitle}</div>'
        f'</div>'
    )

col_score_left, col_score_mid, col_score_right = st.columns([1, 2.5, 1.8])

with col_score_left:
    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1.5rem 0.5rem;">'
        f'<div style="font-size:5rem;font-weight:900;line-height:1;color:{g_overall[2]};">{g_overall[0]}</div>'
        f'<div style="font-size:1.6rem;font-weight:700;color:#e2e8f0;margin-top:0.4rem;">{overall}/100</div>'
        f'<div style="font-size:0.95rem;color:{g_overall[2]};margin-top:0.3rem;font-weight:600;">{g_overall[1]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_score_mid:
    # ── Hilfsfunktion: Detail-Erklärung pro Dimension ──────────────────
    def _detail_rendite(r: float, score: float) -> tuple[str, str]:
        why = f"Dein Portfolio erzielte **{r*100:.1f}% p.a.** historische Rendite. "
        if r >= 0.16:
            why += "Das liegt deutlich über dem Marktdurchschnitt von ~8–10% p.a."
        elif r >= 0.08:
            why += "Das liegt im soliden Marktbereich (8–16% p.a.)."
        elif r >= 0:
            why += "Das liegt unter dem typischen Marktdurchschnitt von ~8% p.a."
        else:
            why += "Das Portfolio hatte im Betrachtungszeitraum negative Rendite."
        tips = []
        if score < 60:
            tips = ["Wachstums-ETFs hinzufügen (z.B. QQQ, IWDA, CSPX)",
                    "Anteil an hochperformenden Einzelaktien erhöhen (z.B. NVDA, AAPL, MSFT)",
                    "Defensivpositionen mit niedrigem Wachstum reduzieren"]
        elif score < 80:
            tips = ["Anteil an Wachstumstiteln leicht erhöhen",
                    "Dividenden-ETFs durch Wachstums-ETFs teilweise ersetzen"]
        else:
            tips = ["Rendite ist bereits sehr stark — Risikomanagement nicht vernachlässigen"]
        return why, tips

    def _detail_risiko(vol: float, dd: float, score: float) -> tuple[str, list]:
        why = (f"Volatilität: **{vol*100:.1f}% p.a.**, Max. Drawdown: **{dd*100:.1f}%**. ")
        if vol > 0.30:
            why += "Sehr hohe Schwankungen — typisch für konzentrierte oder volatile Portfolios."
        elif vol > 0.20:
            why += "Überdurchschnittliche Volatilität, aber noch im Rahmen für Aktienportfolios."
        elif vol > 0.12:
            why += "Moderate Volatilität — gutes Gleichgewicht für einen Aktieninvestor."
        else:
            why += "Niedrige Volatilität — sehr defensives Portfolio."
        tips = []
        if score < 60:
            tips = ["Gold oder Anleihen-ETF beimischen (z.B. PHAU, AGGH) — senkt Korrelation",
                    "Stark volatile Einzelpositionen auf max. 5% Gewicht begrenzen",
                    "Breit diversifizierte ETFs erhöhen (IWDA, VWRL)"]
        elif score < 75:
            tips = ["Anteil stabiler Dividendentitel erhöhen (z.B. JNJ, KO, NESN.SW)",
                    "Gold-ETC als Hedge beimischen (2–5%)"]
        else:
            tips = ["Risikoniveau ist gut — aktuelle Allokation beibehalten"]
        return why, tips

    def _detail_effizienz(sharpe: float, score: float) -> tuple[str, list]:
        why = f"Sharpe Ratio: **{sharpe:.2f}** (Rendite pro Risikoeinheit, risikofreier Zins {risk_free_rate*100:.1f}%). "
        if sharpe >= 1.5:
            why += "Exzellentes Rendite-Risiko-Verhältnis."
        elif sharpe >= 1.0:
            why += "Gutes Rendite-Risiko-Verhältnis — über dem Marktdurchschnitt."
        elif sharpe >= 0.5:
            why += "Mittelmäßiges Rendite-Risiko-Verhältnis. Der Markt (S&P 500) liegt bei ~0.8–1.0."
        else:
            why += "Schlechtes Rendite-Risiko-Verhältnis — zu viel Risiko für die erzielte Rendite."
        tips = []
        if score < 60:
            tips = ["Stark volatile Positionen mit niedriger Rendite herausschneiden",
                    "Breit diversifizierte ETFs erhöhen — sie verbessern Sharpe systematisch",
                    "Gold/Anleihen beimischen — erhöhen Sharpe durch niedrige Korrelation",
                    "Konzentration in wenige Top-Performer statt vieler mittelmäßiger Titel"]
        elif score < 75:
            tips = ["Underperformer (< Benchmark-Rendite bei hoher Vola) reduzieren",
                    "Beimischung von Low-Volatility ETFs prüfen"]
        else:
            tips = ["Effizienz bereits sehr hoch — Allokation beibehalten"]
        return why, tips

    def _detail_diversi(port, corr_mat, score: float) -> tuple[str, list]:
        n = port.num_positions
        w_list = [p.weight for p in port.positions]
        hhi = sum(w**2 for w in w_list)
        top_pos = sorted(port.positions, key=lambda p: p.weight, reverse=True)
        top_name = top_pos[0].ticker if top_pos else "?"
        top_w = top_pos[0].weight * 100 if top_pos else 0
        why = (f"**{n} Positionen**, HHI-Konzentration: **{hhi:.3f}** "
               f"(0 = perfekt diversifiziert, 1 = konzentriert). "
               f"Größte Position: **{top_name}** mit {top_w:.1f}%.")
        tips = []
        if score < 60:
            tips = [f"{top_name} reduzieren (aktuell {top_w:.0f}% — Ziel < 15%)",
                    "Mehr Positionen aus unterschiedlichen Sektoren/Regionen hinzufügen",
                    "EM-ETF beimischen für regionale Diversifikation (z.B. EIMI)",
                    "Anleihen oder Gold für Asset-Klassen-Diversifikation"]
        elif score < 78:
            tips = ["Einzelpositionen > 20% leicht reduzieren",
                    "Weitere Anlageklassen prüfen (Rohstoffe, REITs)"]
        else:
            tips = ["Diversifikation bereits gut — keine großen Änderungen nötig"]
        return why, tips

    def _detail_stabilitaet(dd: float, var99: float, score: float) -> tuple[str, list]:
        why = (f"Max. Drawdown: **{dd*100:.1f}%**, VaR 99%: **{var99*100:.2f}% tägl.** "
               f"(entspricht ~{var99*100*np.sqrt(252):.1f}% p.a.). ")
        if abs(dd) > 0.40:
            why += "Sehr starke historische Verlustphasen — Portfolio reagiert sensitiv auf Krisen."
        elif abs(dd) > 0.25:
            why += "Deutliche Verlustphasen in Stressphasen — typisch für Aktienportfolios."
        elif abs(dd) > 0.15:
            why += "Moderate Verlustphasen — gute Stabilität für ein Aktienportfolio."
        else:
            why += "Geringe historische Verluste — sehr stabiles Portfolio."
        tips = []
        if score < 60:
            tips = ["Gold-ETC beimischen (PHAU, XAD5) — klassischer Krisenhedge",
                    "Anleihen-ETF aufnehmen (z.B. AGGH, IUSB) — senkt Drawdown",
                    "Defensive Aktien erhöhen: Gesundheit (JNJ, LLY), Basiskonsumgüter (KO, PG)",
                    "Stop-Loss oder Rebalancing-Regeln definieren"]
        elif score < 75:
            tips = ["Defensive Beimischung leicht erhöhen (5–10% Gold oder Anleihen)",
                    "Krypto-Anteil begrenzen — erhöht Drawdown stark"]
        else:
            tips = ["Stabilitätsprofil ist gut — aktuelle Schutzmaßnahmen beibehalten"]
        return why, tips

    # ── Dimensionen rendern ─────────────────────────────────────────────
    dims = [
        ("Rendite",         g_rendite,  s_rendite,
         _detail_rendite(metrics.annual_return, s_rendite)),
        ("Risiko",          g_risiko,   s_risiko,
         _detail_risiko(metrics.annual_volatility, metrics.max_drawdown, s_risiko)),
        ("Effizienz",       g_eff,      s_effizienz,
         _detail_effizienz(metrics.sharpe_ratio, s_effizienz)),
        ("Diversifikation", g_div,      s_diversi,
         _detail_diversi(portfolio, corr_matrix_for_score, s_diversi)),
        ("Stabilität",      g_stab,     s_stabilitaet,
         _detail_stabilitaet(metrics.max_drawdown, metrics.var_99, s_stabilitaet)),
    ]

    for label, grade, score, (why, tips) in dims:
        pct = int(round(score))
        color = grade[2]
        bar_html = (
            f'<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:0.3rem;">'
            f'<span style="font-weight:600;font-size:0.95rem;color:#e2e8f0;">{label}</span>'
            f'<span style="font-weight:700;font-size:1.05rem;color:{color};">{grade[0]}&nbsp;&nbsp;{pct}</span>'
            f'</div>'
            f'<div style="background:#2d3748;border-radius:6px;height:10px;overflow:hidden;margin-bottom:0.4rem;">'
            f'<div style="width:{pct}%;height:100%;background:{color};border-radius:6px;"></div>'
            f'</div>'
        )
        st.markdown(bar_html, unsafe_allow_html=True)
        with st.expander("Details & Empfehlungen"):
            st.markdown(f"**Warum dieser Score?**\n\n{why}")
            if tips:
                st.markdown("**So kannst du es verbessern:**")
                for tip in tips:
                    st.markdown(f"- {tip}")
        st.markdown("<div style='margin-bottom:0.6rem;'></div>", unsafe_allow_html=True)

with col_score_right:
    fig_radar = go.Figure(go.Scatterpolar(
        r=[round(s_rendite), round(s_risiko), round(s_effizienz),
           round(s_diversi), round(s_stabilitaet)],
        theta=["Rendite", "Risiko", "Effizienz", "Diversifikation", "Stabilität"],
        fill="toself",
        fillcolor="rgba(237,137,54,0.25)",
        line=dict(color="#ed8936", width=2),
        marker=dict(size=6, color="#ed8936"),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color="#718096"),
                gridcolor="#2d3748",
                linecolor="#2d3748",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#a0aec0"),
                gridcolor="#2d3748",
                linecolor="#2d3748",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=280,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────
# Efficient Frontier
# ─────────────────────────────────────────────────────
st.markdown("### Efficient Frontier — Markowitz-Modell")

col_frontier, col_details = st.columns([3, 1])

with col_frontier:
    with st.spinner("Berechne Efficient Frontier..."):
        # Monte-Carlo Punkte
        mc_df = risk_engine.compute_monte_carlo_frontier(n_simulations=3000)

        # Analytische Frontier
        frontier = risk_engine.compute_efficient_frontier(n_points=80)

        # Spezielle Portfolios
        min_var = risk_engine.find_minimum_variance_portfolio()
        max_sharpe = risk_engine.find_max_sharpe_portfolio()

    # Plot erstellen
    fig = go.Figure()

    # Monte-Carlo Punkte (Hintergrund)
    fig.add_trace(go.Scatter(
        x=mc_df["Volatilität"] * 100,
        y=mc_df["Rendite"] * 100,
        mode="markers",
        marker=dict(
            size=3,
            color=mc_df["Sharpe"],
            colorscale="Viridis",
            colorbar=dict(title="Sharpe", x=1.02),
            opacity=0.4,
        ),
        name="Mögliche Portfolios",
        hovertemplate="Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>",
    ))

    # Efficient Frontier (Linie)
    if frontier:
        frontier_vols = [f.volatility * 100 for f in frontier]
        frontier_rets = [f.return_ * 100 for f in frontier]

        fig.add_trace(go.Scatter(
            x=frontier_vols,
            y=frontier_rets,
            mode="lines",
            line=dict(color="#e53e3e", width=3),
            name="Efficient Frontier",
        ))

    # Aktuelles Portfolio
    fig.add_trace(go.Scatter(
        x=[metrics.annual_volatility * 100],
        y=[metrics.annual_return * 100],
        mode="markers+text",
        marker=dict(size=18, color="#f6e05e", symbol="star", line=dict(width=2, color="#744210")),
        text=["Dein Portfolio"],
        textposition="top center",
        textfont=dict(size=13, color="#f6e05e"),
        name="Dein Portfolio",
        hovertemplate=(
            f"<b>Dein Portfolio</b><br>"
            f"Rendite: {metrics.annual_return * 100:.1f}%<br>"
            f"Volatilität: {metrics.annual_volatility * 100:.1f}%<br>"
            f"Sharpe: {metrics.sharpe_ratio:.2f}<extra></extra>"
        ),
    ))

    # Minimum-Varianz-Portfolio
    if min_var:
        fig.add_trace(go.Scatter(
            x=[min_var.volatility * 100],
            y=[min_var.return_ * 100],
            mode="markers+text",
            marker=dict(size=14, color="#48bb78", symbol="diamond"),
            text=["Min Varianz"],
            textposition="bottom center",
            textfont=dict(size=11, color="#48bb78"),
            name="Min-Varianz Portfolio",
        ))

    # Maximum-Sharpe-Portfolio
    if max_sharpe:
        fig.add_trace(go.Scatter(
            x=[max_sharpe.volatility * 100],
            y=[max_sharpe.return_ * 100],
            mode="markers+text",
            marker=dict(size=14, color="#4299e1", symbol="diamond"),
            text=["Max Sharpe"],
            textposition="top center",
            textfont=dict(size=11, color="#4299e1"),
            name="Max-Sharpe Portfolio",
        ))

    # Benchmark
    if benchmark_name != "Kein Benchmark":
        bench_info = BENCHMARK_INDICES[benchmark_name]
        try:
            bench_ticker = bench_info["ticker_yf"]

            bench_prices = provider.get_benchmark_prices(bench_ticker, years=history_years)
            if not bench_prices.empty:
                bench_returns = np.log(bench_prices / bench_prices.shift(1)).dropna()
                bench_ret = float(bench_returns.mean() * 252)
                bench_vol = float(bench_returns.std() * np.sqrt(252))

                fig.add_trace(go.Scatter(
                    x=[bench_vol * 100],
                    y=[bench_ret * 100],
                    mode="markers+text",
                    marker=dict(size=14, color="#ed8936", symbol="cross"),
                    text=[benchmark_name],
                    textposition="bottom right",
                    textfont=dict(size=11, color="#ed8936"),
                    name=benchmark_name,
                ))
        except Exception as e:
            st.warning(f"Benchmark-Daten nicht verfügbar: {e}")

    fig.update_layout(
        xaxis_title="Volatilität (% p.a.)",
        yaxis_title="Rendite (% p.a.)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#e2e8f0"),
        legend=dict(
            bgcolor="rgba(26,26,46,0.8)",
            bordercolor="#0f3460",
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        xaxis=dict(gridcolor="#1a202c", zeroline=False),
        yaxis=dict(gridcolor="#1a202c", zeroline=False),
    )

    st.plotly_chart(fig, use_container_width=True)

with col_details:
    st.markdown("#### Dein Portfolio")
    st.markdown(f"**Rendite:** {metrics.annual_return * 100:.1f}% p.a.")
    st.markdown(f"**Volatilität:** {metrics.annual_volatility * 100:.1f}% p.a.")
    st.markdown(f"**Sharpe:** {metrics.sharpe_ratio:.2f}")
    st.markdown(f"**Max DD:** {metrics.max_drawdown * 100:.1f}%")

    if max_sharpe:
        st.markdown("---")
        st.markdown("#### Optimales Portfolio")
        st.markdown(f"**Rendite:** {max_sharpe.return_ * 100:.1f}% p.a.")
        st.markdown(f"**Volatilität:** {max_sharpe.volatility * 100:.1f}% p.a.")
        st.markdown(f"**Sharpe:** {max_sharpe.sharpe:.2f}")

        st.markdown("**Gewichtung:**")
        for ticker, weight in sorted(
            max_sharpe.weights.items(), key=lambda x: x[1], reverse=True
        ):
            if weight > 0.01:
                st.markdown(f"- {ticker}: {weight * 100:.1f}%")

    if min_var:
        st.markdown("---")
        st.markdown("#### Min-Varianz Portfolio")
        st.markdown(f"**Volatilität:** {min_var.volatility * 100:.1f}% p.a.")
        st.markdown(f"**Sharpe:** {min_var.sharpe:.2f}")


# ─────────────────────────────────────────────────────
# Korrelationsmatrix
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Korrelationsmatrix (EWMA)")

corr_df = risk_engine.get_correlation_matrix()

fig_corr = go.Figure(data=go.Heatmap(
    z=corr_df.values,
    x=corr_df.columns,
    y=corr_df.index,
    colorscale=[
        [0, "#2b6cb0"],
        [0.5, "#1a202c"],
        [1, "#e53e3e"],
    ],
    zmid=0,
    text=[[f"{v:.2f}" for v in row] for row in corr_df.values],
    texttemplate="%{text}",
    textfont=dict(size=11),
    hovertemplate="%{y} vs %{x}: %{z:.3f}<extra></extra>",
    colorbar=dict(title="Korrelation"),
))

fig_corr.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0"),
    margin=dict(l=0, r=0, t=30, b=0),
    height=max(400, len(corr_df) * 35),
)

st.plotly_chart(fig_corr, use_container_width=True)

# ─────────────────────────────────────────────────────
# Einzelne Positionen: Rendite vs. Risiko
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Einzelne Positionen: Rendite vs. Risiko")

pos_data = []
for ticker in risk_engine.tickers:
    if ticker in returns_df.columns:
        ret = float(returns_df[ticker].mean() * 252)
        vol = float(returns_df[ticker].std() * np.sqrt(252))
        weight = weights.get(ticker, 0)
        pos_data.append({
            "Ticker": ticker,
            "Rendite (%)": round(ret * 100, 1),
            "Volatilität (%)": round(vol * 100, 1),
            "Gewicht (%)": round(weight * 100, 1),
        })

pos_df = pd.DataFrame(pos_data)

if not pos_df.empty:
    fig_scatter = px.scatter(
        pos_df,
        x="Volatilität (%)",
        y="Rendite (%)",
        size="Gewicht (%)",
        text="Ticker",
        size_max=40,
        color="Rendite (%)",
        color_continuous_scale="RdYlGn",
    )

    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#e2e8f0"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=500,
        xaxis=dict(gridcolor="#1a202c"),
        yaxis=dict(gridcolor="#1a202c"),
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────────────
# Zinssensitivität (Monte Carlo)
# ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Zinssensitivität — Monte Carlo Simulation")
st.markdown(
    "Wie reagiert dein Portfolio auf Zinsänderungen? "
    "10.000 simulierte Szenarien basierend auf sektor-spezifischen Sensitivitäten."
)

# Sektor-Gewichte aus ExposureEngine holen
try:
    from core.exposure_engine import ExposureEngine
    _exp_engine = ExposureEngine(portfolio)
    _sector_df = _exp_engine.get_sector_exposure()
    if not _sector_df.empty:
        _sector_weights_dict = {
            int(row["GICS_Code"]): float(row["Gewicht_pct"]) / 100
            for _, row in _sector_df.iterrows()
        }
    else:
        _sector_weights_dict = {0: 1.0}
except Exception:
    _sector_weights_dict = {0: 1.0}

rate_df = risk_engine.compute_rate_sensitivity(_sector_weights_dict, n_simulations=10_000)

# Regressionsgerade für Szenario-Schätzungen
_rate_coef = np.polyfit(rate_df["Zinsänderung_bps"], rate_df["Portfolio_Impact_pct"], 1)
_rate_poly  = np.poly1d(_rate_coef)
_slope      = float(_rate_coef[0])  # % Impact pro bps

col_rate_left, col_rate_right = st.columns([2.5, 1])

with col_rate_left:
    fig_rate = go.Figure()

    # Monte-Carlo Punkte
    fig_rate.add_trace(go.Scatter(
        x=rate_df["Zinsänderung_bps"],
        y=rate_df["Portfolio_Impact_pct"],
        mode="markers",
        marker=dict(
            size=3,
            color=rate_df["Portfolio_Impact_pct"],
            colorscale=[[0.0, "#e53e3e"], [0.5, "#4a5568"], [1.0, "#48bb78"]],
            cmin=rate_df["Portfolio_Impact_pct"].min(),
            cmax=rate_df["Portfolio_Impact_pct"].max(),
            opacity=0.35,
        ),
        name="Monte Carlo Szenarien",
        hovertemplate="Δrate: %{x:.0f} bps<br>Impact: %{y:.2f}%<extra></extra>",
    ))

    # Trend-Linie
    _x_line = np.linspace(-300, 300, 200)
    fig_rate.add_trace(go.Scatter(
        x=_x_line,
        y=_rate_poly(_x_line),
        mode="lines",
        line=dict(color="#667eea", width=2.5, dash="dash"),
        name=f"Trend ({_slope:+.4f}%/bps)",
    ))

    # Nulllinien
    fig_rate.add_hline(y=0, line=dict(color="#4a5568", width=1, dash="dot"))
    fig_rate.add_vline(x=0, line=dict(color="#4a5568", width=1, dash="dot"))

    # Schattierung: negative Impact-Zone
    fig_rate.add_hrect(
        y0=rate_df["Portfolio_Impact_pct"].min(),
        y1=0,
        fillcolor="rgba(229,62,62,0.05)",
        line_width=0,
    )

    fig_rate.update_layout(
        xaxis_title="Zinsänderung (Basispunkte)",
        yaxis_title="Portfolio-Impact (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#e2e8f0"),
        legend=dict(bgcolor="rgba(26,26,46,0.8)", bordercolor="#0f3460", borderwidth=1),
        margin=dict(l=0, r=0, t=30, b=0),
        height=420,
        xaxis=dict(gridcolor="#1a202c", zeroline=False),
        yaxis=dict(gridcolor="#1a202c", zeroline=False),
    )
    st.plotly_chart(fig_rate, use_container_width=True)

with col_rate_right:
    st.markdown("#### Szenarien")

    _scenarios = [
        (-200, "Stark fallend (−200 bps)"),
        (-100, "Fallend (−100 bps)"),
        (+50,  "Leicht steigend (+50 bps)"),
        (+100, "Steigend (+100 bps)"),
        (+200, "Stark steigend (+200 bps)"),
        (+300, "Extremanstieg (+300 bps)"),
    ]

    for shock, label in _scenarios:
        est = float(_rate_poly(shock))
        color = "#48bb78" if est >= 0 else "#fc8181"
        sign  = "+" if est >= 0 else ""
        st.markdown(
            f'<div style="background:#1a1a2e;border:1px solid #0f3460;border-radius:8px;'
            f'padding:0.5rem 0.8rem;margin-bottom:0.4rem;display:flex;justify-content:space-between;">'
            f'<span style="color:#a0aec0;font-size:0.82rem;">{label}</span>'
            f'<span style="color:{color};font-weight:700;font-size:0.95rem;">{sign}{est:.2f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(f"**Sensitivität:** `{_slope:+.4f}% pro bps`")
    st.caption("Portfolioreaktion auf 1 Basispunkt Zinsänderung (annähernd linear).")

    if abs(_slope) > 0.05:
        st.warning("Hohe Zinssensitivität — Portfolio reagiert stark auf Zentralbankentscheidungen.")
    elif abs(_slope) > 0.02:
        st.info("Mittlere Zinssensitivität — üblich für Aktienportfolios.")
    else:
        st.success("Niedrige Zinssensitivität.")
