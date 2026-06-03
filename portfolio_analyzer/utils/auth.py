"""
Authentication module — Supabase-based login + self-registration.
Falls back to "local" mode when Supabase is not configured.
"""

import logging
import streamlit as st
from utils.supabase_client import get_client, is_configured

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Session helpers
# ─────────────────────────────────────────────────────────────────────────────

def _set_session(user_id: str, email: str, access_token: str = "") -> None:
    st.session_state["sb_user_id"]          = user_id
    st.session_state["sb_user_email"]       = email
    st.session_state["sb_access_token"]     = access_token
    st.session_state["authentication_status"] = True
    st.session_state["username"]            = user_id
    st.session_state["name"]               = email.split("@")[0] if "@" in email else user_id[:8]


def clear_session() -> None:
    """Wipe all auth + portfolio state (used by logout)."""
    keys = (
        "sb_user_id", "sb_user_email", "sb_access_token",
        "authentication_status", "username", "name",
        "pa_profile_loaded", "pa_theme", "pa_avatar", "pa_avatar_mime",
        "portfolio", "data_provider", "provider_name",
        "enriched", "returns_loaded", "pending_positions",
        "restored_from_disk", "search_hits",
    )
    for k in keys:
        st.session_state.pop(k, None)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def require_auth() -> str:
    """
    Call at the top of every page.
    - Returns user_id (UUID) when authenticated via Supabase.
    - Returns "local" when Supabase is not configured (dev mode).
    - Shows login/register form + calls st.stop() when not authenticated.
    """
    if not is_configured():
        return "local"

    if st.session_state.get("authentication_status") is True:
        return st.session_state.get("sb_user_id", "local")

    _render_auth_page()
    st.stop()


def sign_out() -> None:
    """Sign out from Supabase and clear local session."""
    client = get_client("anon")
    if client:
        try:
            client.auth.sign_out()
        except Exception as e:
            logger.warning(f"Supabase sign_out: {e}")
    clear_session()


# ─────────────────────────────────────────────────────────────────────────────
# Auth page UI
# ─────────────────────────────────────────────────────────────────────────────

def _render_auth_page() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],[data-testid="collapsedControl"],
        #MainMenu,footer,header{display:none!important;}
        html,body{background:#03050d!important;}
        .stApp{background:transparent!important;
          font-family:'Inter',-apple-system,sans-serif!important;}
        </style>
        <div style="position:fixed;inset:0;z-index:-1;
          background:radial-gradient(ellipse 130% 90% at 50% -10%,#0d1130,#03050d 65%);"></div>
        <div style="position:fixed;top:-20vw;left:-10vw;width:60vw;height:60vw;
          border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,.13),transparent 65%);
          pointer-events:none;"></div>
        <div style="position:fixed;bottom:-15vw;right:-5vw;width:50vw;height:50vw;
          border-radius:50%;background:radial-gradient(circle,rgba(6,182,212,.09),transparent 65%);
          pointer-events:none;"></div>
        """,
        unsafe_allow_html=True,
    )

    # Logo + title
    st.markdown(
        """
        <div style="text-align:center;padding:4rem 1rem 1.8rem;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
            width:52px;height:52px;border-radius:14px;
            background:linear-gradient(135deg,#6366f1,#8b5cf6);
            font-size:1.1rem;font-weight:900;color:#fff;letter-spacing:.04em;
            box-shadow:0 0 32px rgba(99,102,241,.45);margin-bottom:1.2rem;">PA</div>
          <div style="font-size:2.6rem;font-weight:900;letter-spacing:-.05em;
            background:linear-gradient(135deg,#fff 0%,rgba(255,255,255,.7) 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin-bottom:.45rem;">Portfolio Analyzer</div>
          <div style="color:#7c87a6;font-size:.9rem;">
            Analysiere dein Portfolio &mdash; Laender, Sektoren, Risiko &amp; mehr
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center the form
    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        # Card wrapper
        st.markdown(
            """
            <div style="background:rgba(255,255,255,.033);border:1px solid rgba(255,255,255,.07);
              border-radius:14px;padding:1.8rem 1.8rem .5rem;
              box-shadow:0 24px 60px rgba(0,0,0,.6);">
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Anmelden", "Registrieren"])

        with tab_login:
            _login_form()

        with tab_register:
            _register_form()

        st.markdown("</div>", unsafe_allow_html=True)


def _login_form() -> None:
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    email = st.text_input(
        "E-Mail", placeholder="deine@email.de",
        key="login_email", label_visibility="visible",
    )
    pw = st.text_input(
        "Passwort", type="password", placeholder="Passwort eingeben",
        key="login_pw",
    )
    st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

    if st.button("Anmelden", type="primary", use_container_width=True, key="btn_login"):
        if not email.strip() or not pw:
            st.error("Bitte E-Mail und Passwort eingeben.")
            return

        client = get_client("anon")
        if not client:
            st.error("Supabase nicht konfiguriert.")
            return

        with st.spinner("Anmelden..."):
            try:
                resp = client.auth.sign_in_with_password(
                    {"email": email.strip(), "password": pw}
                )
                _set_session(
                    resp.user.id,
                    resp.user.email,
                    resp.session.access_token,
                )
                st.rerun()
            except Exception as e:
                err = str(e).lower()
                if "invalid" in err or "credentials" in err or "wrong" in err:
                    st.error("Falsche E-Mail oder falsches Passwort.")
                else:
                    st.error(f"Anmeldung fehlgeschlagen: {e}")


def _register_form() -> None:
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    email = st.text_input(
        "E-Mail", placeholder="deine@email.de",
        key="reg_email",
    )
    pw = st.text_input(
        "Passwort", type="password", placeholder="Mindestens 6 Zeichen",
        key="reg_pw",
    )
    pw2 = st.text_input(
        "Passwort bestaetigen", type="password", placeholder="Passwort wiederholen",
        key="reg_pw2",
    )
    st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

    if st.button("Konto erstellen", type="primary", use_container_width=True, key="btn_register"):
        if not email.strip() or not pw:
            st.error("Bitte alle Felder ausfullen.")
            return
        if pw != pw2:
            st.error("Passwoerter stimmen nicht ueberein.")
            return
        if len(pw) < 6:
            st.error("Passwort muss mindestens 6 Zeichen haben.")
            return

        client = get_client("anon")
        if not client:
            st.error("Supabase nicht konfiguriert.")
            return

        with st.spinner("Konto erstellen..."):
            try:
                resp = client.auth.sign_up(
                    {"email": email.strip(), "password": pw}
                )
                if resp.user:
                    if resp.session:
                        # E-Mail-Bestaetigung deaktiviert → direkt einloggen
                        _set_session(
                            resp.user.id,
                            resp.user.email,
                            resp.session.access_token,
                        )
                        st.rerun()
                    else:
                        # E-Mail-Bestaetigung aktiv
                        st.success(
                            "Konto erstellt! Bitte bestatige deine E-Mail-Adresse "
                            "und melde dich dann an."
                        )
                else:
                    st.error("Registrierung fehlgeschlagen. Bitte versuche es erneut.")
            except Exception as e:
                err = str(e).lower()
                if "already" in err or "exists" in err or "registered" in err:
                    st.error("Diese E-Mail ist bereits registriert. Bitte melde dich an.")
                else:
                    st.error(f"Registrierung fehlgeschlagen: {e}")
