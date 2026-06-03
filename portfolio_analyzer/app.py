"""
Portfolio Analyzer — Dashboard + Portfolio Management
Merged entry point: data provider, KPI overview, portfolio input.
"""

import streamlit as st
import pandas as pd
import logging

from core.portfolio import Portfolio, Position, AssetType
from utils.constants import get_etf_country_distribution
from core.data_provider import get_data_provider
from core.demo_data import DemoDataProvider, create_demo_portfolio
from utils.search import (
    search_securities, ISIN_TO_TICKER,
    _looks_like_isin, _looks_like_wkn, WKN_TO_TICKER, resolve_to_ticker,
)
from utils.persistence import (
    save_portfolio, load_portfolio, delete_saved_portfolio, saved_portfolio_exists,
)
from utils.nav import inject_page
from utils.auth import require_auth

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


_current_user = require_auth()

# ─────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────
# Session state init + portfolio restore
# ─────────────────────────────────────────────────────
def _restore_yahoo_from_disk():
    """Load saved portfolio from disk into session state (Yahoo mode only)."""
    saved = load_portfolio(_current_user)
    if saved:
        st.session_state.portfolio = Portfolio()
        for item in saved:
            pos = Position(
                ticker=item["ticker"],
                name=item.get("name", item["ticker"]),
                market_value=float(item.get("market_value", 0)),
                currency=item.get("currency", "EUR"),
            )
            pos.isin        = item.get("isin", "")
            pos.country     = item.get("country", "")
            pos.gics_sector = int(item.get("gics_sector", 0))
            at = item.get("asset_type", "")
            if at in ("ETF", "AssetType.ETF"):
                pos.asset_type = AssetType.ETF
            elif at in ("STOCK", "AssetType.STOCK"):
                pos.asset_type = AssetType.STOCK
            if pos.is_etf:
                pos.etf_country_weights = get_etf_country_distribution(pos.ticker)
            st.session_state.portfolio.add_position(pos)
        st.session_state.pending_positions = [
            {"Ticker": p.ticker, "Name": p.name or "", "Marktwert (€)": p.market_value}
            for p in st.session_state.portfolio.positions
        ]
        st.session_state.enriched = True
        return True
    return False


def _init():
    if "portfolio"           not in st.session_state:
        st.session_state.portfolio       = Portfolio()
    if "data_provider"       not in st.session_state:
        st.session_state.data_provider   = None
    if "provider_name"       not in st.session_state:
        st.session_state.provider_name   = "Nicht verbunden"
    if "enriched"            not in st.session_state:
        st.session_state.enriched        = False
    if "returns_loaded"      not in st.session_state:
        st.session_state.returns_loaded  = False
    if "pending_positions"   not in st.session_state:
        st.session_state.pending_positions = []
    if "restored_from_disk"  not in st.session_state:
        st.session_state.restored_from_disk = False

    # On first load (not demo, not yet restored): load saved Yahoo portfolio
    if (
        not st.session_state.restored_from_disk
        and st.session_state.provider_name != "Demo-Modus"
    ):
        restored = _restore_yahoo_from_disk()
        if restored:
            st.session_state._show_restore_info = True
        st.session_state.restored_from_disk = True


_init()

# ─────────────────────────────────────────────────────
# Design system + Navbar
# ─────────────────────────────────────────────────────
inject_page("dashboard")

# Always read from session state so we get the live object after every rerun
portfolio = st.session_state.portfolio

# ─────────────────────────────────────────────────────
# Hero header
# ─────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero anim-0">
  <h1>Dashboard</h1>
  <p class="page-hero-sub">Portfolio verwalten &middot; Analysieren &middot; Optimieren</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Restore notification
# ─────────────────────────────────────────────────────
if st.session_state.pop("_show_restore_info", False):
    st.info(
        f"Dein gespeichertes Portfolio wurde wiederhergestellt "
        f"({portfolio.num_positions} Positionen). "
        "Verbinde Yahoo Finance um Kurse & Daten zu aktualisieren."
    )

# ─────────────────────────────────────────────────────
# Data provider bar
# ─────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="provider-bar anim-1">', unsafe_allow_html=True)
    col_lbl, col_src, col_btn, col_spacer = st.columns([1.2, 3, 1.6, 4])
    with col_lbl:
        st.markdown('<span class="provider-label">Datenquelle</span>', unsafe_allow_html=True)
    with col_src:
        source = st.radio(
            "src", ["Yahoo Finance", "Demo-Modus"],
            horizontal=True, label_visibility="collapsed",
        )
    with col_btn:
        connect_clicked = st.button("Verbinden", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if connect_clicked:
    if source == "Demo-Modus":
        # ── Demo mode ────────────────────────────────────────────────────────
        # Use a separate portfolio object — never touches the Yahoo disk save
        st.session_state.data_provider  = DemoDataProvider()
        st.session_state.provider_name  = "Demo-Modus"
        st.session_state.portfolio      = create_demo_portfolio()
        st.session_state.enriched       = True
        st.session_state.returns_loaded = False
        st.session_state.search_hits    = []
        st.rerun()

    else:
        # ── Yahoo Finance ────────────────────────────────────────────────────
        with st.spinner("Verbinde mit Yahoo Finance…"):
            try:
                provider = get_data_provider()
            except Exception as e:
                st.error(f"Yahoo Finance Verbindung fehlgeschlagen: {e}")
                st.stop()

        st.session_state.data_provider  = provider
        st.session_state.provider_name  = "Yahoo Finance"
        st.session_state.returns_loaded = False
        st.session_state.search_hits    = []

        # Always start from the saved Yahoo portfolio (not from whatever
        # was in session — could be demo positions).
        st.session_state.portfolio = Portfolio()
        _restore_yahoo_from_disk()           # loads disk → session
        st.session_state.restored_from_disk = True

        # Re-enrich every restored position with fresh Yahoo data
        if st.session_state.portfolio.num_positions > 0:
            positions = list(st.session_state.portfolio.positions)
            st.session_state.portfolio.clear()
            progress = st.progress(0, text="Aktualisiere Portfolio…")
            for i, pos in enumerate(positions):
                try:
                    pos = provider.enrich_position(pos)
                except Exception as e:
                    logger.warning(f"Re-enrich {pos.ticker}: {e}")
                st.session_state.portfolio.add_position(pos)
                progress.progress(
                    (i + 1) / len(positions),
                    text=f"Aktualisiere {pos.ticker}… ({i + 1}/{len(positions)})",
                )
            progress.empty()
            st.session_state.enriched = True
            save_portfolio(st.session_state.portfolio.positions, _current_user)

        st.rerun()

# ─────────────────────────────────────────────────────
# KPI Cards (when portfolio loaded)
# ─────────────────────────────────────────────────────
if portfolio.num_positions > 0:
    etfs   = sum(1 for p in portfolio.positions if p.is_etf)
    stocks = portfolio.num_positions - etfs
    total  = portfolio.total_value
    avg    = total / portfolio.num_positions if portfolio.num_positions else 0

    kpi_html = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin-bottom:2rem;">

  <div class="kpi-card anim-1">
    <div class="kpi-glow-bar" style="background:linear-gradient(90deg,#6366f1,#8b5cf6);"></div>
    <div class="kpi-label">Gesamtwert</div>
    <div class="kpi-value">{total:,.0f}&nbsp;<span style="font-size:.9rem;font-weight:500;color:var(--text2)">€</span></div>
    <div class="kpi-sub">{portfolio.num_positions} Positionen</div>
  </div>

  <div class="kpi-card anim-2">
    <div class="kpi-glow-bar" style="background:linear-gradient(90deg,#06b6d4,#6366f1);"></div>
    <div class="kpi-label">Positionen</div>
    <div class="kpi-value">{portfolio.num_positions}</div>
    <div class="kpi-sub">Ø {avg:,.0f} € pro Position</div>
  </div>

  <div class="kpi-card anim-3">
    <div class="kpi-glow-bar" style="background:linear-gradient(90deg,#34d399,#06b6d4);"></div>
    <div class="kpi-label">ETFs</div>
    <div class="kpi-value">{etfs}</div>
    <div class="kpi-sub">{etfs/portfolio.num_positions*100:.0f}% des Portfolios</div>
  </div>

  <div class="kpi-card anim-4">
    <div class="kpi-glow-bar" style="background:linear-gradient(90deg,#fbbf24,#ec4899);"></div>
    <div class="kpi-label">Einzelaktien</div>
    <div class="kpi-value">{stocks}</div>
    <div class="kpi-sub">{stocks/portfolio.num_positions*100:.0f}% des Portfolios</div>
  </div>

</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)

    # Positions table
    st.markdown(
        '<div class="section-label">'
        '<span class="section-label-text">Positionen im Portfolio</span>'
        '<div class="section-label-line"></div></div>',
        unsafe_allow_html=True,
    )
    df = portfolio.to_dataframe()
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        column_config={
            "Gewicht (%)": st.column_config.ProgressColumn(
                "Gewicht (%)", min_value=0,
                max_value=df["Gewicht (%)"].max() * 1.1 if not df.empty else 100,
                format="%.1f%%",
            ),
            "Marktwert (€)": st.column_config.NumberColumn("Marktwert (€)", format="%.2f €"),
        },
    )
    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Empty state
# ─────────────────────────────────────────────────────
else:
    if st.session_state.provider_name == "Yahoo Finance":
        # Yahoo connected but portfolio empty → prompt to search
        st.markdown("""
<div style="text-align:center;padding:2.5rem 1rem 1.5rem;">
  <div style="font-size:2.4rem;margin-bottom:.6rem;">&#128269;</div>
  <div style="font-size:1.15rem;font-weight:700;color:var(--text);margin-bottom:.4rem;">
    Yahoo Finance verbunden &mdash; Portfolio ist leer
  </div>
  <div style="font-size:.88rem;color:var(--text2);max-width:480px;margin:0 auto;">
    Suche unten nach Aktien, ETFs oder anderen Wertpapieren und füge sie mit
    <strong style="color:var(--c1)">+</strong> direkt zu deinem Portfolio hinzu.
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin:1.5rem 0 2rem;">
    <div class="step-card anim-1">
      <div class="step-icon" style="background:rgba(99,102,241,.12);color:var(--c1);">&#9654;</div>
      <div class="step-num" style="color:var(--c1);">Schritt 01</div>
      <div class="step-title">Datenquelle verbinden</div>
      <div class="step-desc">Yahoo Finance für Live-Kurse oder Demo-Modus für einen schnellen Einstieg.</div>
    </div>
    <div class="step-card anim-2">
      <div class="step-icon" style="background:rgba(139,92,246,.12);color:var(--c2);">&#9776;</div>
      <div class="step-num" style="color:var(--c2);">Schritt 02</div>
      <div class="step-title">Portfolio aufbauen</div>
      <div class="step-desc">Wertpapiere per ISIN, WKN, Ticker oder Name suchen und hinzufügen.</div>
    </div>
    <div class="step-card anim-3">
      <div class="step-icon" style="background:rgba(6,182,212,.12);color:var(--c3);">&#9733;</div>
      <div class="step-num" style="color:var(--c3);">Schritt 03</div>
      <div class="step-title">Analyse starten</div>
      <div class="step-desc">Exposure, Overlap, Markowitz-Optimierung und Overlay-Manager stehen bereit.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Portfolio input tabs
# ─────────────────────────────────────────────────────
st.markdown(
    '<div class="section-label">'
    '<span class="section-label-text">Portfolio verwalten</span>'
    '<div class="section-label-line"></div></div>',
    unsafe_allow_html=True,
)

with st.container():

    # ── helper: enrich + add one position to the live portfolio ───────────────
    def _add_position_now(ticker: str, name: str, value: float) -> str:
        """
        Resolve ticker, enrich via data_provider if available, add to portfolio,
        sync pending_positions and save to disk.
        Returns "ok" on success or an error string.
        """
        pf = st.session_state.portfolio   # always the live object
        ticker = ticker.strip().upper()

        # Resolve ISIN / WKN
        if _looks_like_isin(ticker):
            resolved = ISIN_TO_TICKER.get(ticker) or resolve_to_ticker(ticker)
            if not resolved:
                return f"ISIN {ticker} konnte nicht aufgelöst werden."
            ticker = resolved
        elif _looks_like_wkn(ticker):
            resolved = WKN_TO_TICKER.get(ticker) or resolve_to_ticker(ticker)
            if resolved:
                ticker = resolved

        # Already in portfolio?
        if any(p.ticker == ticker for p in pf.positions):
            return f"{ticker} ist bereits im Portfolio."

        pos = Position(ticker=ticker, name=name or ticker,
                       market_value=value, currency="EUR")

        # Enrich if provider connected
        if st.session_state.get("data_provider"):
            try:
                pos = st.session_state.data_provider.enrich_position(pos)
            except Exception as e:
                logger.warning(f"Enrich {ticker}: {e}")

        pf.add_position(pos)
        st.session_state.enriched       = True
        st.session_state.returns_loaded = False

        # Keep pending_positions table in sync
        st.session_state.pending_positions = [
            {"Ticker": p.ticker, "Name": p.name or "", "Marktwert (€)": p.market_value}
            for p in pf.positions
        ]

        # Persist to disk (Yahoo mode only)
        if st.session_state.provider_name == "Yahoo Finance":
            save_portfolio(pf.positions, _current_user)

        return "ok"

    # ── Search bar ────────────────────────────────────────────────────────────
    st.markdown("#### Wertpapier suchen")
    st.markdown(
        '<p style="font-size:.82rem;color:var(--text2);margin-top:-.5rem;margin-bottom:.8rem;">'
        "ISIN, WKN, Ticker oder Unternehmensname eingeben — direkt zum Portfolio hinzufügen"
        "</p>",
        unsafe_allow_html=True,
    )

    col_q, col_btn = st.columns([4, 1])
    with col_q:
        search_query = st.text_input(
            "Suche",
            placeholder="z.B. Apple, AAPL, IE00B4L5Y983, A0RPWH, SAP …",
            label_visibility="collapsed",
            key="search_query",
        )
    with col_btn:
        do_search = st.button("Suchen", type="primary", use_container_width=True)

    # Store hits in session_state so they survive reruns triggered by "+"
    if "search_hits" not in st.session_state:
        st.session_state.search_hits = []

    if do_search and search_query.strip():
        with st.spinner("Suche läuft…"):
            st.session_state.search_hits = search_securities(search_query.strip(), max_results=8)
        if not st.session_state.search_hits:
            st.warning("Keine Ergebnisse. Schreibweise prüfen oder direkt den Ticker eingeben.")

    # Render persisted results
    if st.session_state.search_hits:
        already_in = {p.ticker for p in st.session_state.portfolio.positions}
        st.markdown(
            '<p style="font-size:.75rem;color:var(--text3);letter-spacing:.06em;'
            'text-transform:uppercase;font-weight:700;margin-bottom:.4rem;">'
            "Suchergebnisse — Wert eingeben &amp; + drücken"
            "</p>",
            unsafe_allow_html=True,
        )
        for hit in st.session_state.search_hits:
            sym   = hit["symbol"]
            name  = hit["name"] or sym
            htype = hit.get("type", "")
            exch  = hit.get("exchange", "")
            badge = (f" · {htype}" if htype else "") + (f" · {exch}" if exch else "")
            in_portfolio = sym in already_in

            col_info, col_val, col_add = st.columns([3, 1.5, 0.8])
            with col_info:
                check = " ✓" if in_portfolio else ""
                color = "var(--green)" if in_portfolio else "var(--text)"
                st.markdown(
                    f'<div style="padding:.45rem 0;">'
                    f'<span style="font-weight:600;color:{color}">{sym}{check}</span>'
                    f'<span style="color:var(--text2);font-size:.82rem;"> — {name}</span>'
                    f'<span style="color:var(--text3);font-size:.72rem;">{badge}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col_val:
                val_key = f"add_val_{sym}"
                add_val = st.number_input(
                    "€", min_value=0.01,
                    value=1000.0,
                    format="%.2f",
                    label_visibility="collapsed",
                    key=val_key,
                )
            with col_add:
                btn_label = "✓" if in_portfolio else "＋"
                if st.button(btn_label, key=f"add_btn_{sym}",
                             use_container_width=True,
                             disabled=in_portfolio):
                    with st.spinner(f"Füge {sym} hinzu…"):
                        result = _add_position_now(sym, name, float(add_val))
                    if result == "ok":
                        st.rerun()
                    else:
                        st.warning(result)

    st.markdown("---")

    # ── Current portfolio table ───────────────────────────────────────────────
    st.markdown("#### Aktuelles Portfolio")

    # Keep pending_positions in sync with live portfolio
    _pf_live = st.session_state.portfolio
    if _pf_live.num_positions > 0:
        st.session_state.pending_positions = [
            {"Ticker": p.ticker, "Name": p.name or "", "Marktwert (€)": p.market_value}
            for p in _pf_live.positions
        ]

    raw_rows = st.session_state.pending_positions or [
        {"Ticker": "", "Name": "", "Marktwert (€)": 0.0}
    ]

    edited_df = st.data_editor(
        pd.DataFrame(raw_rows),
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Ticker": st.column_config.TextColumn(
                "Ticker / ISIN / WKN",
                help="Ticker (AAPL), ISIN (IE00B4L5Y983) oder WKN (A0RPWH)",
                width="medium",
            ),
            "Name": st.column_config.TextColumn("Name", width="large"),
            "Marktwert (€)": st.column_config.NumberColumn(
                "Marktwert (€)", min_value=0.0, format="%.2f", width="medium"
            ),
        },
        key="manual_editor",
    )

    col_load, col_clear = st.columns([1, 1])
    with col_load:
        # "Anreichern" = re-process table (useful for manual ticker entry or value edits)
        if st.button("Übernehmen & anreichern", type="primary", use_container_width=True):
            valid_rows = edited_df[
                (edited_df["Ticker"].astype(str).str.strip() != "") &
                (edited_df["Marktwert (€)"] > 0)
            ].copy()
            if valid_rows.empty:
                st.error("Keine gültigen Positionen.")
            else:
                portfolio.clear()
                progress = st.progress(0, text="Lade Positionen…")
                errors = []
                for i, (_, row) in enumerate(valid_rows.iterrows()):
                    raw_ticker = str(row["Ticker"]).strip().upper()
                    value      = float(row["Marktwert (€)"])
                    name_hint  = str(row.get("Name", "")).strip()

                    if _looks_like_isin(raw_ticker):
                        resolved = ISIN_TO_TICKER.get(raw_ticker) or resolve_to_ticker(raw_ticker)
                        if resolved:
                            raw_ticker = resolved
                        else:
                            errors.append(f"ISIN {raw_ticker} nicht auflösbar — übersprungen")
                            continue
                    elif _looks_like_wkn(raw_ticker):
                        resolved = WKN_TO_TICKER.get(raw_ticker) or resolve_to_ticker(raw_ticker)
                        if resolved:
                            raw_ticker = resolved

                    pos = Position(ticker=raw_ticker, name=name_hint or raw_ticker,
                                   market_value=value, currency="EUR")
                    if st.session_state.get("data_provider"):
                        try:
                            pos = st.session_state.data_provider.enrich_position(pos)
                        except Exception as e:
                            errors.append(f"{raw_ticker}: {e}")
                    portfolio.add_position(pos)
                    progress.progress((i + 1) / len(valid_rows),
                                      text=f"Lade {raw_ticker}… ({i+1}/{len(valid_rows)})")

                progress.empty()
                for err in errors:
                    st.warning(err)
                st.session_state.enriched       = True
                st.session_state.returns_loaded = False
                if st.session_state.provider_name != "Demo-Modus":
                    save_portfolio(portfolio.positions, _current_user)
                st.success(f"{portfolio.num_positions} Positionen — {portfolio.total_value:,.2f} €")
                st.rerun()

    with col_clear:
        if st.button("Portfolio leeren", use_container_width=True):
            portfolio.clear()
            st.session_state.pending_positions = []
            st.session_state.search_hits       = []
            st.session_state.enriched          = False
            st.session_state.returns_loaded    = False
            if st.session_state.provider_name != "Demo-Modus":
                delete_saved_portfolio(_current_user)
            st.rerun()

