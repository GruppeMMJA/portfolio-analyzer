"""
AWWWARDS-level design system for Portfolio Analyzer.
Navigation via st.page_link() — preserves session state (no page reload).
"""

import base64
import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR THEMES
# ─────────────────────────────────────────────────────────────────────────────
# Background-focused themes — subtle dark tones, accent colours stay consistent.
# swatch: slightly-lighter shade used for the small colour picker dot in the popover.
THEMES = {
    "midnight": {
        "label": "Midnight", "swatch": "#0e1220",
        "bg": "#03050d",  "bg2": "#070b15",  "nav": "rgba(3,5,13,.8)",
        "orb1": "rgba(99,102,241,.18)", "orb2": "rgba(139,92,246,.14)",
        "orb3": "rgba(6,182,212,.10)",  "orb4": "rgba(236,72,153,.06)",
    },
    "charcoal": {
        "label": "Charcoal", "swatch": "#1a1a1a",
        "bg": "#080808",  "bg2": "#101010",  "nav": "rgba(8,8,8,.88)",
        "orb1": "rgba(99,102,241,.11)", "orb2": "rgba(139,92,246,.08)",
        "orb3": "rgba(6,182,212,.07)",  "orb4": "rgba(236,72,153,.04)",
    },
    "slate": {
        "label": "Slate", "swatch": "#0e1628",
        "bg": "#060b14",  "bg2": "#0a1120",  "nav": "rgba(6,11,20,.88)",
        "orb1": "rgba(99,102,241,.22)", "orb2": "rgba(139,92,246,.16)",
        "orb3": "rgba(6,182,212,.13)",  "orb4": "rgba(236,72,153,.06)",
    },
    "forest": {
        "label": "Forest", "swatch": "#091808",
        "bg": "#040c06",  "bg2": "#07130a",  "nav": "rgba(4,12,6,.88)",
        "orb1": "rgba(16,185,129,.16)", "orb2": "rgba(99,102,241,.11)",
        "orb3": "rgba(6,182,212,.09)",  "orb4": "rgba(16,185,129,.08)",
    },
    "merlot": {
        "label": "Merlot", "swatch": "#1a080c",
        "bg": "#0c0407",  "bg2": "#13060b",  "nav": "rgba(12,4,7,.88)",
        "orb1": "rgba(244,63,94,.14)",  "orb2": "rgba(139,92,246,.12)",
        "orb3": "rgba(244,63,94,.08)",  "orb4": "rgba(236,72,153,.06)",
    },
    "warm": {
        "label": "Warm", "swatch": "#1c1408",
        "bg": "#0d0905",  "bg2": "#140e07",  "nav": "rgba(13,9,5,.88)",
        "orb1": "rgba(245,158,11,.14)", "orb2": "rgba(139,92,246,.11)",
        "orb3": "rgba(6,182,212,.08)",  "orb4": "rgba(245,158,11,.07)",
    },
}


def _theme_override_css(theme_key: str) -> str:
    t = THEMES.get(theme_key, THEMES["midnight"])
    return (
        f"<style>"
        f":root{{--bg:{t['bg']};--bg2:{t['bg2']};}}"
        f"html,body{{background:{t['bg']}!important;}}"
        f".stApp{{background:{t['bg']}!important;}}"
        f".pa-nav{{background:{t['nav']}!important;}}"
        f".pa-bg{{background:radial-gradient(ellipse 120% 80% at 50% 0%,{t['bg2']},{t['bg']} 60%);background-color:{t['bg']}!important;}}"
        f".pa-orb1{{background:radial-gradient(circle,{t['orb1']},transparent 65%)!important;}}"
        f".pa-orb2{{background:radial-gradient(circle,{t['orb2']},transparent 65%)!important;}}"
        f".pa-orb3{{background:radial-gradient(circle,{t['orb3']},transparent 65%)!important;}}"
        f".pa-orb4{{background:radial-gradient(circle,{t['orb4']},transparent 65%)!important;}}"
        f"</style>"
    )


def _save_profile_kv(username: str, key: str, value) -> None:
    from utils.persistence import load_profile, save_profile
    profile = load_profile(username)
    profile[key] = value
    save_profile(username, profile)


def _profile_panel_content() -> None:
    """All profile-dialog widgets — reads everything from session state."""
    username     = st.session_state.get("username", "local")
    display_name = st.session_state.get("name", "")
    theme_key    = st.session_state.get("pa_theme", "midnight")
    avatar_b64   = st.session_state.get("pa_avatar", "")
    from utils.supabase_client import is_configured as _sb_configured
    is_authed = (
        st.session_state.get("authentication_status") is True
        and _sb_configured()
    )
    initial      = (display_name[0] if display_name and display_name != "local" else "?").upper()
    shown_name   = display_name if display_name and display_name != "local" else "Benutzer"

    # ── Avatar header ──────────────────────────────────────────────────────
    avatar_mime = st.session_state.get("pa_avatar_mime", "image/jpeg")
    if avatar_b64:
        avatar_html = (
            f'<img src="data:{avatar_mime};base64,{avatar_b64}" '
            f'style="width:72px;height:72px;border-radius:50%;object-fit:cover;'
            f'border:2px solid var(--c1);display:block;margin:0 auto .5rem;">'
        )
    else:
        avatar_html = (
            f'<div style="width:72px;height:72px;border-radius:50%;margin:0 auto .5rem;'
            f'background:linear-gradient(135deg,var(--c1),var(--c2));'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:1.8rem;font-weight:900;color:#fff;'
            f'box-shadow:0 0 24px var(--glow);">{initial}</div>'
        )
    st.markdown(
        f'<div style="text-align:center;padding-bottom:.9rem;">'
        f'{avatar_html}'
        f'<div style="font-weight:700;color:#f0f4ff;font-size:.95rem;margin-top:.3rem;">{shown_name}</div>'
        f'<div style="color:#7c87a6;font-size:.72rem;margin-top:.1rem;">@{username}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Profile picture ────────────────────────────────────────────────────
    with st.expander("Profilbild ändern"):
        uploaded = st.file_uploader(
            "JPG oder PNG hochladen",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="_avatar_upload_dlg",
        )
        if uploaded is not None:
            mime    = uploaded.type or "image/jpeg"
            new_b64 = base64.b64encode(uploaded.read()).decode()
            st.session_state["pa_avatar"]      = new_b64
            st.session_state["pa_avatar_mime"] = mime
            _save_profile_kv(username, "avatar", new_b64)
            _save_profile_kv(username, "avatar_mime", mime)
            st.rerun()
        if avatar_b64:
            if st.button("Bild entfernen", key="_avatar_rm_dlg", use_container_width=True):
                st.session_state["pa_avatar"] = ""
                _save_profile_kv(username, "avatar", "")
                st.rerun()

    # ── Colour theme ───────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin:.7rem 0 .4rem;font-size:.63rem;font-weight:700;'
        'color:#343d57;letter-spacing:.1em;text-transform:uppercase;">Hintergrund</div>',
        unsafe_allow_html=True,
    )
    swatch_html = "".join(
        f'<span title="{THEMES[tk]["label"]}" style="display:inline-block;'
        f'width:18px;height:18px;border-radius:4px;'
        f'background:{THEMES[tk]["swatch"]};margin-right:5px;vertical-align:middle;'
        f'border:{("2px solid var(--c1)" if tk == theme_key else "1px solid rgba(255,255,255,.18)")};">'
        f'</span>'
        for tk in THEMES
    )
    st.markdown(f'<div style="margin-bottom:.4rem;">{swatch_html}</div>', unsafe_allow_html=True)
    theme_labels = [v["label"] for v in THEMES.values()]
    theme_keys   = list(THEMES.keys())
    cur_idx      = theme_keys.index(theme_key) if theme_key in theme_keys else 0
    chosen = st.radio(
        "Hintergrund", theme_labels, index=cur_idx,
        key="_theme_radio_dlg", label_visibility="collapsed",
    )
    new_key = theme_keys[theme_labels.index(chosen)]
    if new_key != theme_key:
        st.session_state["pa_theme"] = new_key
        _save_profile_kv(username, "theme", new_key)
        st.rerun()

    # ── Logout ────────────────────────────────────────────────────────────
    if is_authed:
        st.markdown("---")
        if st.button("Abmelden", key="_logout_dlg", use_container_width=True):
            from utils.auth import sign_out
            sign_out()
            st.rerun()


@st.dialog("Profil", width="small")
def _pa_open_profile() -> None:
    _profile_panel_content()


# ─────────────────────────────────────────────────────────────────────────────
# CRITICAL EARLY CSS  (hide Streamlit chrome immediately)
# ─────────────────────────────────────────────────────────────────────────────
EARLY_CSS = """<style>
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
section[data-testid="stSidebar"],[data-testid="collapsedControl"],
#MainMenu,footer{display:none!important;}
html,body{background:#03050d!important;}
.stApp{background:transparent!important;}
</style>"""

# ─────────────────────────────────────────────────────────────────────────────
# FULL DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
DESIGN_SYSTEM = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root{
  --bg:#03050d; --bg2:#070b15; --glass:rgba(255,255,255,.033);
  --glass2:rgba(255,255,255,.055); --glass3:rgba(255,255,255,.08);
  --border:rgba(255,255,255,.07); --border2:rgba(255,255,255,.13); --border3:rgba(255,255,255,.2);
  --c1:#6366f1; --c2:#8b5cf6; --c3:#06b6d4; --c4:#ec4899;
  --glow:rgba(99,102,241,.35);
  --text:#f0f4ff; --text2:#7c87a6; --text3:#343d57;
  --green:#34d399; --red:#f87171; --amber:#fbbf24;
  --r:12px; --rsm:8px; --nav:62px;
  --ease:cubic-bezier(.4,0,.2,1); --spring:cubic-bezier(.34,1.56,.64,1);
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}

/* ── Base ── */
html,body{background:var(--bg)!important;}
.stApp{
  background:transparent!important;
  font-family:'Inter',-apple-system,sans-serif!important;
  color:var(--text)!important;
  -webkit-font-smoothing:antialiased;
}

/* ── Hide Streamlit chrome ── */
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
section[data-testid="stSidebar"],[data-testid="collapsedControl"],
#MainMenu,footer{display:none!important;}

/* ── Content offset for fixed navbar ── */
.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"]{
  position:relative!important;
  z-index:0!important;
}
.main .block-container{
  padding-top:calc(var(--nav) + 1.8rem)!important;
  padding-left:clamp(1rem,3vw,2.5rem)!important;
  padding-right:clamp(1rem,3vw,2.5rem)!important;
  max-width:1440px!important;
}
.main .block-container::before{display:none!important;}

/* ── Animated background orbs ── */
.pa-bg{
  position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden;
  background:radial-gradient(ellipse 120% 80% at 50% 0%,#0a0d1f,var(--bg) 60%);
}
.pa-orb{position:absolute;border-radius:50%;filter:blur(100px);will-change:transform;}
.pa-orb1{width:70vw;height:70vw;background:radial-gradient(circle,rgba(99,102,241,.18),transparent 65%);top:-25vw;left:-15vw;animation:orbA 28s ease-in-out infinite alternate;}
.pa-orb2{width:55vw;height:55vw;background:radial-gradient(circle,rgba(139,92,246,.14),transparent 65%);bottom:-20vw;right:-10vw;animation:orbB 34s ease-in-out infinite alternate;}
.pa-orb3{width:40vw;height:40vw;background:radial-gradient(circle,rgba(6,182,212,.1),transparent 65%);top:35%;right:10%;animation:orbC 22s ease-in-out infinite alternate;}
.pa-orb4{width:30vw;height:30vw;background:radial-gradient(circle,rgba(236,72,153,.06),transparent 65%);top:60%;left:25%;animation:orbD 40s ease-in-out infinite alternate;}
@keyframes orbA{0%{transform:translate(0,0) scale(1)}100%{transform:translate(8vw,6vh) scale(1.08)}}
@keyframes orbB{0%{transform:translate(0,0) scale(1)}100%{transform:translate(-6vw,-8vh) scale(1.12)}}
@keyframes orbC{0%{transform:translate(0,0) scale(1)}100%{transform:translate(-5vw,4vh) scale(.92)}}
@keyframes orbD{0%{transform:translate(0,0) scale(1)}100%{transform:translate(4vw,-6vh) scale(1.05)}}

/* ── Particle canvas ── */
#pa-particles{position:fixed;inset:0;z-index:-1;pointer-events:none;}


/* ── Navbar visual background ── */
.pa-nav{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  height:var(--nav);
  background:rgba(3,5,13,.8);
  backdrop-filter:blur(32px) saturate(200%);
  -webkit-backdrop-filter:blur(32px) saturate(200%);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;
  padding:0 clamp(1rem,2.5vw,1.8rem);gap:1rem;
}
.pa-nav::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(99,102,241,.5),rgba(139,92,246,.5),transparent);
  opacity:.6;
}
.pa-nav-brand{display:flex;align-items:center;gap:.6rem;text-decoration:none!important;flex-shrink:0;}
.pa-nav-logo{
  width:30px;height:30px;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  border-radius:9px;display:flex;align-items:center;justify-content:center;
  font-size:.68rem;font-weight:900;color:#fff;letter-spacing:.04em;
  box-shadow:0 0 20px var(--glow),0 0 40px rgba(99,102,241,.15);
  transition:box-shadow .3s,transform .3s var(--spring);
}
.pa-nav-brand:hover .pa-nav-logo{
  box-shadow:0 0 30px rgba(99,102,241,.7),0 0 60px rgba(99,102,241,.25);
  transform:scale(1.08) rotate(-3deg);
}
.pa-nav-name{font-size:.84rem;font-weight:700;color:var(--text);letter-spacing:-.03em;white-space:nowrap;}
.pa-nav-right{display:flex;align-items:center;gap:.6rem;margin-left:auto;flex-shrink:0;}
.pa-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.28rem .75rem;border-radius:20px;font-size:.7rem;font-weight:500;}
.pa-badge-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}
.pa-badge-on{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.2);}
.pa-badge-on .pa-badge-dot{background:var(--green);box-shadow:0 0 6px var(--green);animation:blink 2s ease-in-out infinite;}
.pa-badge-off{background:var(--glass);color:var(--text3);border:1px solid var(--border);}
.pa-badge-off .pa-badge-dot{background:var(--text3);}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ── Nav links (st.page_link — positioned into navbar by JS) ── */
.pa-nav-links-block{
  position:fixed!important;
  top:0!important;left:260px!important;right:155px!important;
  height:var(--nav)!important;
  z-index:10000!important;
  display:flex!important;align-items:center!important;
  gap:0!important;margin:0!important;padding:0!important;
}
.pa-nav-links-block > div[data-testid="column"]{
  padding:0!important;width:auto!important;flex:none!important;min-width:0!important;
}
.pa-nav-links-block [data-testid="stPageLink"]{margin:0!important;padding:0!important;}
.pa-nav-links-block [data-testid="stPageLink-NavLink"]{
  padding:.36rem .86rem!important;border-radius:7px!important;
  font-size:.79rem!important;font-weight:500!important;
  color:rgba(255,255,255,.28)!important;letter-spacing:-.01em!important;
  white-space:nowrap!important;border:none!important;
  text-decoration:none!important;display:block!important;
  transition:color .18s,background .18s!important;
}
.pa-nav-links-block [data-testid="stPageLink-NavLink"]:hover{
  color:rgba(255,255,255,.72)!important;
  background:rgba(255,255,255,.05)!important;
  text-decoration:none!important;
}
.pa-nav-links-block [data-testid="stPageLink-NavLink"][aria-current="page"]{
  color:#fff!important;
  background:rgba(99,102,241,.14)!important;
  font-weight:600!important;
}
.pa-nav-links-block [data-testid="stPageLink-NavLink"][aria-current="page"]::after{
  display:none!important;
}
/* Hide link icons */
.pa-nav-links-block [data-testid="stPageLink-NavLink"] svg,
.pa-nav-links-block [data-testid="stPageLink-NavLink"] [data-testid="stPageLinkIcon"]{
  display:none!important;
}
/* ── Profile avatar — pure HTML in navbar ── */
#pa-avatar-btn{
  transition:box-shadow .25s,transform .2s var(--spring);
}
#pa-avatar-btn:hover{
  box-shadow:0 0 26px var(--glow),0 0 48px rgba(99,102,241,.2)!important;
  transform:scale(1.08);
}

/* ── Gear button — last column in nav-links-block, pushed to right ── */
.pa-nav-links-block > div[data-testid="column"]:last-child{
  margin-left:auto!important;
  flex:none!important;
  width:auto!important;
}
.pa-nav-links-block > div[data-testid="column"]:last-child .stButton>button{
  width:32px!important;height:32px!important;
  min-width:32px!important;max-width:32px!important;
  border-radius:50%!important;padding:0!important;
  background:transparent!important;border:none!important;
  color:rgba(255,255,255,.4)!important;
  font-size:1.1rem!important;line-height:1!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  box-shadow:none!important;
  transition:color .18s,background .18s!important;
}
.pa-nav-links-block > div[data-testid="column"]:last-child .stButton>button:hover{
  color:rgba(255,255,255,.85)!important;
  background:rgba(255,255,255,.08)!important;
  transform:none!important;box-shadow:none!important;
}

/* ── Profile popover panel ── */
[data-testid="stPopoverBody"]{
  background:var(--bg2)!important;
  border:1px solid var(--border2)!important;
  border-radius:var(--r)!important;
  padding:1.1rem 1rem 1rem!important;
  min-width:240px!important;max-width:260px!important;
  box-shadow:0 28px 70px rgba(0,0,0,.85),0 0 0 1px rgba(255,255,255,.05)!important;
}
/* Theme swatch buttons inside popover */
[data-testid="stPopoverBody"] .stButton>button{
  padding:.22rem .5rem!important;font-size:.72rem!important;font-weight:600!important;
  border-radius:6px!important;
}
/* Logout button inside popover */
[data-testid="stPopoverBody"] div[data-testid="column"]:last-of-type .stButton>button{
  background:rgba(248,113,113,.07)!important;
  border-color:rgba(248,113,113,.2)!important;
  color:rgba(248,113,113,.7)!important;
}
[data-testid="stPopoverBody"] div[data-testid="column"]:last-of-type .stButton>button:hover{
  background:rgba(248,113,113,.14)!important;
  border-color:rgba(248,113,113,.4)!important;
  color:rgba(248,113,113,.95)!important;
}

/* ── Typography ── */
h1{
  font-family:'Inter',sans-serif!important;
  font-size:clamp(1.6rem,3vw,2.1rem)!important;
  font-weight:900!important;letter-spacing:-.05em!important;
  line-height:1.1!important;
  background:linear-gradient(135deg,#fff 0%,rgba(255,255,255,.65) 100%);
  -webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;
  background-clip:text!important;
  padding-bottom:0!important;border-bottom:none!important;margin-bottom:.35rem!important;
}
h2{
  font-family:'Inter',sans-serif!important;font-size:.92rem!important;font-weight:600!important;
  color:var(--text)!important;letter-spacing:-.015em!important;
  border-bottom:1px solid var(--border)!important;
  padding-bottom:.5rem!important;margin:1.8rem 0 .9rem!important;
}
h3{
  font-family:'Inter',sans-serif!important;font-size:.63rem!important;font-weight:700!important;
  color:var(--text3)!important;letter-spacing:.1em!important;
  text-transform:uppercase!important;margin-bottom:.6rem!important;
}
p,li{color:var(--text2);line-height:1.7;font-size:.875rem;}

/* ── Page hero ── */
.page-hero{margin-bottom:2rem;animation:fadeUp .5s var(--ease) both;}
.page-hero-sub{font-size:.875rem;color:var(--text2);margin-top:.3rem!important;}

/* ── Glass card base ── */
.glass-card{
  background:var(--glass);backdrop-filter:blur(20px) saturate(180%);
  border:1px solid var(--border);border-radius:var(--r);
  position:relative;overflow:hidden;
  transition:border-color .25s var(--ease),box-shadow .25s var(--ease),transform .22s var(--ease);
}
.glass-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.04) 0%,transparent 50%);
  pointer-events:none;
}
.glass-card:hover{
  border-color:rgba(99,102,241,.3);
  box-shadow:0 0 0 1px rgba(99,102,241,.15),0 20px 60px rgba(0,0,0,.5),0 0 80px rgba(99,102,241,.08);
}

/* ── KPI Cards ── */
.kpi-card{
  background:var(--glass);backdrop-filter:blur(20px) saturate(180%);
  border:1px solid var(--border);border-radius:var(--r);
  padding:1.4rem 1.6rem;position:relative;overflow:hidden;
  cursor:default;will-change:transform;
  transition:border-color .25s var(--ease),box-shadow .25s var(--ease),transform .22s var(--spring);
  animation:fadeUp .45s var(--ease) both;
}
.kpi-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.05) 0%,transparent 50%);pointer-events:none;
}
.kpi-card::after{
  content:'';position:absolute;
  top:-50%;left:-50%;width:200%;height:200%;
  background:conic-gradient(from 180deg,transparent 60%,rgba(99,102,241,.04) 80%,transparent 100%);
  animation:shimmer 8s linear infinite;pointer-events:none;
}
@keyframes shimmer{to{transform:rotate(360deg)}}
.kpi-card:hover{
  border-color:rgba(99,102,241,.35);
  box-shadow:0 0 0 1px rgba(99,102,241,.15),0 24px 64px rgba(0,0,0,.55),0 0 100px rgba(99,102,241,.1);
  transform:translateY(-4px) scale(1.008);
}
.kpi-glow-bar{position:absolute;top:0;left:0;right:0;height:2px;border-radius:var(--r) var(--r) 0 0;}
.kpi-label{font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.6rem;}
.kpi-value{font-size:clamp(1.6rem,3vw,2rem);font-weight:900;letter-spacing:-.05em;line-height:1;color:var(--text);}
.kpi-sub{font-size:.72rem;color:var(--text3);margin-top:.4rem;}

/* ── Step cards ── */
.step-card{
  background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
  padding:1.5rem;position:relative;overflow:hidden;will-change:transform;
  transition:border-color .25s,box-shadow .25s,transform .22s var(--spring);
  animation:fadeUp .45s var(--ease) both;
}
.step-card::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.03) 0%,transparent 60%);pointer-events:none;
}
.step-card:hover{
  border-color:rgba(99,102,241,.3);
  box-shadow:0 16px 48px rgba(0,0,0,.45),0 0 60px rgba(99,102,241,.07);
  transform:translateY(-3px) scale(1.005);
}
.step-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.15rem;margin-bottom:.95rem;}
.step-num{font-size:.58rem;font-weight:800;letter-spacing:.15em;text-transform:uppercase;margin-bottom:.5rem;}
.step-title{font-size:.95rem;font-weight:700;color:var(--text);letter-spacing:-.025em;margin-bottom:.35rem;}
.step-desc{font-size:.8rem;color:var(--text2);line-height:1.6;}

/* ── Buttons ── */
.stButton>button{
  background:var(--glass2)!important;border:1px solid var(--border)!important;
  color:var(--text2)!important;font-family:'Inter',sans-serif!important;
  font-weight:500!important;font-size:.83rem!important;letter-spacing:-.01em!important;
  border-radius:var(--rsm)!important;padding:.48rem 1.1rem!important;
  transition:background .18s var(--ease),border-color .18s var(--ease),
             box-shadow .18s var(--ease),transform .15s var(--spring),color .18s!important;
  position:relative;overflow:hidden;
}
.stButton>button:hover{
  background:var(--glass3)!important;border-color:var(--border2)!important;
  box-shadow:0 8px 24px rgba(0,0,0,.4),0 0 0 1px rgba(255,255,255,.05)!important;
  transform:translateY(-1px)!important;color:var(--text)!important;
}
.stButton>button:active{transform:translateY(0) scale(.98)!important;}
.stButton>button[kind="primary"],
.stButton>button[kind="primary"]:focus,
.stButton>button[kind="primary"]:visited{
  background:#1e40af!important;
  border:2px solid #3b82f6!important;
  color:#ffffff!important;
  font-weight:700!important;
  font-size:.9rem!important;
  box-shadow:none!important;
  text-shadow:none!important;
  -webkit-text-fill-color:#ffffff!important;
}
.stButton>button[kind="primary"] *{
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
}
.stButton>button[kind="primary"]:hover{
  background:#1d4ed8!important;
  border-color:#60a5fa!important;
  transform:translateY(-1px)!important;
}
.stDownloadButton>button{
  background:var(--glass2)!important;border:1px solid var(--border)!important;
  color:var(--text2)!important;font-family:'Inter',sans-serif!important;
  font-weight:500!important;font-size:.83rem!important;border-radius:var(--rsm)!important;
  transition:all .18s var(--ease)!important;
}
.stDownloadButton>button:hover{
  background:var(--glass3)!important;border-color:var(--border2)!important;
  box-shadow:0 8px 24px rgba(0,0,0,.4)!important;
  transform:translateY(-1px)!important;color:var(--text)!important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;gap:0;}
.stTabs [data-baseweb="tab"]{
  background:transparent!important;color:var(--text3)!important;
  font-family:'Inter',sans-serif!important;font-weight:500!important;font-size:.82rem!important;
  padding:.5rem 1.15rem!important;border-bottom:2px solid transparent!important;
  border-radius:0!important;transition:color .18s,background .18s!important;
}
.stTabs [data-baseweb="tab"]:hover{color:var(--text2)!important;background:var(--glass)!important;}
.stTabs [aria-selected="true"]{
  color:var(--text)!important;background:transparent!important;
  border-bottom:2px solid var(--c1)!important;
  text-shadow:0 0 20px rgba(99,102,241,.5);
}

/* ── Metrics ── */
[data-testid="stMetric"]{
  background:var(--glass)!important;backdrop-filter:blur(16px)!important;
  border:1px solid var(--border)!important;border-radius:var(--r)!important;
  padding:1.1rem 1.3rem!important;
  transition:border-color .25s,box-shadow .25s,transform .22s var(--spring)!important;
}
[data-testid="stMetric"]:hover{
  border-color:rgba(99,102,241,.3)!important;
  box-shadow:0 16px 40px rgba(0,0,0,.45),0 0 60px rgba(99,102,241,.07)!important;
  transform:translateY(-2px)!important;
}
[data-testid="stMetricLabel"]>div{color:var(--text3)!important;font-size:.65rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;font-family:'Inter',sans-serif!important;}
[data-testid="stMetricValue"]>div{color:var(--text)!important;font-family:'Inter',sans-serif!important;font-size:1.6rem!important;font-weight:800!important;letter-spacing:-.04em!important;}

/* ── DataFrames ── */
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{
  border:1px solid var(--border)!important;border-radius:var(--r)!important;
  overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,.3);
}

/* ── Inputs ── */
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea textarea{
  background:rgba(255,255,255,.035)!important;border:1px solid var(--border)!important;
  border-radius:var(--rsm)!important;color:var(--text)!important;
  font-family:'Inter',sans-serif!important;font-size:.86rem!important;
  transition:border-color .18s,box-shadow .18s!important;
}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus,.stTextArea textarea:focus{
  border-color:var(--c1)!important;
  box-shadow:0 0 0 3px rgba(99,102,241,.15),0 0 20px rgba(99,102,241,.1)!important;
}
.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div{
  background:rgba(255,255,255,.035)!important;border:1px solid var(--border)!important;
  border-radius:var(--rsm)!important;color:var(--text)!important;transition:border-color .18s!important;
}
.stSelectbox [data-baseweb="select"]>div:hover,.stMultiSelect [data-baseweb="select"]>div:hover{
  border-color:var(--border2)!important;
}
[data-baseweb="popover"],[data-baseweb="menu"]{
  background:#0e1220!important;border:1px solid var(--border)!important;
  border-radius:var(--rsm)!important;box-shadow:0 24px 64px rgba(0,0,0,.7)!important;
}
[role="option"]:hover{background:rgba(99,102,241,.12)!important;}
[aria-selected="true"]{background:rgba(99,102,241,.1)!important;}

/* ── Sliders ── */
[data-baseweb="slider"] [data-baseweb="thumb"]{
  background:var(--c1)!important;border-color:var(--c1)!important;
  box-shadow:0 0 0 4px rgba(99,102,241,.2),0 0 20px rgba(99,102,241,.4)!important;
}
[data-baseweb="slider"] [data-baseweb="thumb"]:hover{box-shadow:0 0 0 6px rgba(99,102,241,.25),0 0 30px rgba(99,102,241,.5)!important;}
[data-baseweb="slider"] [data-baseweb="track-background"]{background:rgba(255,255,255,.06)!important;}
[data-baseweb="slider"] [data-baseweb="track-foreground"]{background:linear-gradient(90deg,var(--c1),var(--c2))!important;}

/* ── Progress ── */
.stProgress>div>div>div{background:linear-gradient(90deg,var(--c1),var(--c2))!important;border-radius:4px!important;box-shadow:0 0 10px rgba(99,102,241,.4);}
.stProgress>div>div{background:rgba(255,255,255,.05)!important;border-radius:4px!important;}

/* ── Expanders ── */
details[data-testid="stExpander"]{
  border:1px solid var(--border)!important;border-radius:var(--r)!important;
  background:var(--glass)!important;overflow:hidden;
  backdrop-filter:blur(16px)!important;transition:border-color .2s,box-shadow .2s!important;
}
details[data-testid="stExpander"]:hover{border-color:rgba(99,102,241,.25)!important;box-shadow:0 8px 32px rgba(0,0,0,.3)!important;}
details[data-testid="stExpander"] summary{
  color:var(--text2)!important;font-family:'Inter',sans-serif!important;
  font-weight:500!important;font-size:.84rem!important;background:transparent!important;
  padding:.78rem 1.1rem!important;transition:color .18s,background .18s!important;
}
details[data-testid="stExpander"] summary:hover{background:var(--glass)!important;color:var(--text)!important;}

/* ── Alerts ── */
[data-testid="stNotificationContentInfo"]{background:rgba(99,102,241,.07)!important;border-left:3px solid var(--c1)!important;border-radius:0 var(--rsm) var(--rsm) 0!important;}
[data-testid="stNotificationContentWarning"]{background:rgba(251,191,36,.07)!important;border-left:3px solid var(--amber)!important;border-radius:0 var(--rsm) var(--rsm) 0!important;}
[data-testid="stNotificationContentError"]{background:rgba(248,113,113,.07)!important;border-left:3px solid var(--red)!important;border-radius:0 var(--rsm) var(--rsm) 0!important;}
[data-testid="stNotificationContentSuccess"]{background:rgba(52,211,153,.07)!important;border-left:3px solid var(--green)!important;border-radius:0 var(--rsm) var(--rsm) 0!important;}

/* ── File uploader ── */
[data-testid="stFileUploader"]{
  border:1.5px dashed rgba(99,102,241,.3)!important;border-radius:var(--r)!important;
  background:rgba(99,102,241,.04)!important;transition:border-color .18s,background .18s,box-shadow .18s!important;
}
[data-testid="stFileUploader"]:hover{
  border-color:rgba(99,102,241,.6)!important;background:rgba(99,102,241,.08)!important;
  box-shadow:0 0 30px rgba(99,102,241,.1)!important;
}

/* ── Labels ── */
label[data-testid="stWidgetLabel"],.stSelectbox label,.stNumberInput label,
.stTextInput label,.stSlider label,.stRadio>label,.stCheckbox>label{
  color:var(--text3)!important;font-size:.7rem!important;font-family:'Inter',sans-serif!important;
  letter-spacing:.07em!important;text-transform:uppercase!important;font-weight:600!important;
}
.stCaption{color:var(--text3)!important;font-size:.72rem!important;}

/* ── Radio ── */
.stRadio [data-baseweb="radio"]>div:first-child{border-color:var(--border)!important;}
.stRadio [data-baseweb="radio"][data-checked="true"]>div:first-child{
  border-color:var(--c1)!important;background:var(--c1)!important;
  box-shadow:0 0 12px rgba(99,102,241,.5)!important;
}

/* ── Divider / scrollbar ── */
hr{border:none!important;border-top:1px solid var(--border)!important;margin:1.5rem 0!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(99,102,241,.2);border-radius:6px;}
::-webkit-scrollbar-thumb:hover{background:rgba(99,102,241,.4);}
.stSpinner>div{border-top-color:var(--c1)!important;filter:drop-shadow(0 0 8px var(--c1));}

/* ── Animations ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.anim-0{animation:fadeUp .5s var(--ease) 0s both;}
.anim-1{animation:fadeUp .5s var(--ease) .08s both;}
.anim-2{animation:fadeUp .5s var(--ease) .16s both;}
.anim-3{animation:fadeUp .5s var(--ease) .24s both;}
.anim-4{animation:fadeUp .5s var(--ease) .32s both;}

/* ── Helpers ── */
.glow-line{height:1px;background:linear-gradient(90deg,transparent,var(--c1) 30%,var(--c2) 70%,transparent);opacity:.35;margin:2rem 0;}
.section-label{display:flex;align-items:center;gap:.7rem;margin:2rem 0 1.1rem;}
.section-label-text{font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;}
.section-label-line{flex:1;height:1px;background:var(--border);}
.provider-bar{background:var(--glass);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:var(--r);padding:.75rem 1.3rem;display:flex;align-items:center;gap:1rem;margin-bottom:1.6rem;animation:fadeUp .4s var(--ease) both;}
.provider-label{font-size:.68rem;font-weight:700;color:var(--text3);letter-spacing:.09em;text-transform:uppercase;white-space:nowrap;}
</style>"""

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND HTML  (CSS-animated — no script tags, safe for st.markdown)
# ─────────────────────────────────────────────────────────────────────────────
EFFECTS = """
<div class="pa-bg">
  <div class="pa-orb pa-orb1"></div><div class="pa-orb pa-orb2"></div>
  <div class="pa-orb pa-orb3"></div><div class="pa-orb pa-orb4"></div>
</div>
<canvas id="pa-particles"></canvas>
"""

# ─────────────────────────────────────────────────────────────────────────────
# JS EFFECTS  — injected via components.v1.html() so <script> actually runs.
# Uses window.parent to reach the Streamlit page DOM from inside the iframe.
# ─────────────────────────────────────────────────────────────────────────────
EFFECTS_JS = """
<script>
(function(){
  var win=window.parent, doc=win.document;
  if(doc.__PA__)return; doc.__PA__=true;

  /* Particles */
  function initParticles(){
    var c=doc.getElementById('pa-particles');if(!c)return;
    var ctx=c.getContext('2d'),W,H,pts=[],mx=null,my=null;
    var COLS=['99,102,241','139,92,246','6,182,212'];
    function resize(){W=c.width=win.innerWidth;H=c.height=win.innerHeight;}
    resize(); win.addEventListener('resize',resize);
    win.addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY;});
    var N=Math.min(28,Math.floor(win.innerWidth*win.innerHeight/40000));
    for(var i=0;i<N;i++)pts.push({
      x:Math.random()*win.innerWidth, y:Math.random()*win.innerHeight,
      vx:(Math.random()-0.5)*0.3,    vy:(Math.random()-0.5)*0.3,
      r:Math.random()*1.2+0.4,       o:Math.random()*0.4+0.12,
      col:COLS[Math.floor(Math.random()*3)]
    });
    var CONN_DIST=110, CONN_DIST2=CONN_DIST*CONN_DIST;
    function loop(){
      ctx.clearRect(0,0,W,H);
      for(var i=0;i<pts.length;i++){
        var p=pts[i];
        p.x+=p.vx; p.y+=p.vy;
        if(p.x<0||p.x>W)p.vx=-p.vx;
        if(p.y<0||p.y>H)p.vy=-p.vy;
        if(mx!=null){
          var dx=mx-p.x,dy=my-p.y,dd=dx*dx+dy*dy;
          if(dd<14400){p.vx+=dx*0.000018;p.vy+=dy*0.000018;}
        }
        var sp=p.vx*p.vx+p.vy*p.vy;
        if(sp>0.64){var sc=0.8/Math.sqrt(sp);p.vx*=sc;p.vy*=sc;}
        for(var j=i+1;j<pts.length;j++){
          var q=pts[j],ex=p.x-q.x,ey=p.y-q.y,ed2=ex*ex+ey*ey;
          if(ed2<CONN_DIST2){
            ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);
            ctx.strokeStyle='rgba(99,102,241,'+(0.09*(1-ed2/CONN_DIST2))+')';
            ctx.lineWidth=0.7;ctx.stroke();
          }
        }
        ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle='rgba('+p.col+','+p.o+')';ctx.fill();
      }
      win.requestAnimationFrame(loop);
    }
    loop();
  }


  /* VanillaTilt */
  function initTilt(){
    function apply(){
      var els=doc.querySelectorAll('.kpi-card,.step-card');if(!els.length)return;
      if(win.VanillaTilt){win.VanillaTilt.init(Array.from(els),{max:8,speed:600,glare:true,'max-glare':0.12,perspective:900,scale:1.02});}
    }
    if(!doc.querySelector('script[data-vt]')){
      var s=doc.createElement('script');
      s.src='https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js';
      s.setAttribute('data-vt','1');s.onload=apply;doc.head.appendChild(s);
    }else{apply();}
  }

  /* Position nav links into the fixed navbar — only writes DOM when class is missing */
  function positionNavLinks(){
    var blocks=doc.querySelectorAll('.main .block-container [data-testid="stHorizontalBlock"]');
    if(blocks.length>0 && !blocks[0].classList.contains('pa-nav-links-block')){
      blocks[0].classList.add('pa-nav-links-block');
      _lastBtn=null; /* force avatar re-style on new DOM */
    }
  }

  /* Track last styled button to avoid redundant DOM writes */
  var _lastBtn=null, _lastSrc='';

  /* Style the gear button as a circle filled with avatar photo */
  function styleProfileAvatar(){
    var block=doc.querySelector('.pa-nav-links-block');
    if(!block)return;
    var cols=block.querySelectorAll('[data-testid="column"]');
    if(!cols.length)return;
    var btn=cols[cols.length-1].querySelector('button');
    if(!btn)return;
    var avatarEl=doc.getElementById('pa-avatar-src');
    var src=(avatarEl&&avatarEl.dataset.src)||'';
    /* Skip if same button already styled with same src */
    if(btn===_lastBtn && src===_lastSrc)return;
    _lastBtn=btn; _lastSrc=src;
    var s=btn.style;
    s.cssText='width:34px!important;height:34px!important;min-width:34px!important;'
      +'max-width:34px!important;border-radius:50%!important;padding:0!important;'
      +'overflow:hidden!important;display:flex!important;align-items:center!important;'
      +'justify-content:center!important;flex-shrink:0!important;'
      +'border:2px solid rgba(255,255,255,.22)!important;'
      +'box-shadow:0 0 16px rgba(99,102,241,.4)!important;cursor:pointer!important;';
    if(src){
      s.cssText+=('background:'+src+' center/cover no-repeat!important;'
        +'color:transparent!important;font-size:0!important;');
      btn.querySelectorAll('p,span').forEach(function(el){
        el.style.setProperty('display','none','important');
      });
    }else{
      s.cssText+=('background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;'
        +'color:#fff!important;font-size:.82rem!important;font-weight:800!important;');
    }
  }

  /* Magnetic primary buttons */
  function initMagnetic(){
    doc.querySelectorAll('.stButton>button[kind="primary"]').forEach(function(el){
      if(el._mag)return;el._mag=true;
      el.addEventListener('mousemove',function(e){
        var r=el.getBoundingClientRect();
        var dx=(e.clientX-r.left-r.width/2)*0.2,dy=(e.clientY-r.top-r.height/2)*0.2;
        el.style.transform='translate('+dx+'px,'+dy+'px)';
      });
      el.addEventListener('mouseleave',function(){el.style.transform='';});
    });
  }

  function boot(){
    initParticles();
    setTimeout(function(){initTilt();positionNavLinks();styleProfileAvatar();initMagnetic();},500);
  }

  if(doc.readyState==='loading'){doc.addEventListener('DOMContentLoaded',boot);}
  else{setTimeout(boot,300);}

  /* Slow poll — only does real work when DOM changed (flags prevent redundant writes) */
  setInterval(function(){positionNavLinks();styleProfileAvatar();},2500);
})();
</script>
"""

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR VISUAL (brand + status — no <a> links)
# ─────────────────────────────────────────────────────────────────────────────
def _nav_visual(provider_name: str, connected: bool, display_name: str = "",
                avatar_b64: str = "", avatar_mime: str = "image/jpeg") -> str:
    if connected:
        badge = (
            f'<span class="pa-badge pa-badge-on">'
            f'<span class="pa-badge-dot"></span>{provider_name}</span>'
        )
    else:
        badge = (
            '<span class="pa-badge pa-badge-off">'
            '<span class="pa-badge-dot"></span>Nicht verbunden</span>'
        )
    initial = (display_name[0] if display_name and display_name != "local" else "?").upper()
    _circle = ("width:34px;height:34px;border-radius:50%;flex-shrink:0;"
                "border:2px solid rgba(255,255,255,.22);box-shadow:0 0 14px rgba(99,102,241,.35);")
    if avatar_b64:
        avatar_data_src = f'url("data:{avatar_mime};base64,{avatar_b64}")'
        avatar_html = (
            f'<img id="pa-avatar-btn" '
            f'src="data:{avatar_mime};base64,{avatar_b64}" '
            f'style="{_circle}object-fit:cover;display:block;">'
        )
    else:
        avatar_data_src = ""
        avatar_html = (
            f'<div id="pa-avatar-btn" '
            f'style="{_circle}background:linear-gradient(135deg,#6366f1,#8b5cf6);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:.82rem;font-weight:800;color:#fff;">{initial}</div>'
        )
    return f"""
<nav class="pa-nav">
  <a href="/" class="pa-nav-brand" target="_self">
    <div class="pa-nav-logo">PA</div>
    <span class="pa-nav-name">Portfolio Analyzer</span>
  </a>
  <div class="pa-nav-right" style="gap:.5rem;">{avatar_html}{badge}</div>
</nav>
<span id="pa-avatar-src" data-src="{avatar_data_src}" data-initial="{initial}" style="display:none;"></span>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

# Page link definitions (path relative to app root, label)
_PAGES = [
    ("pages/0_Anleitung.py",          "Anleitung"),
    ("app.py",                        "Dashboard"),
    ("pages/2_Exposure_Dashboard.py", "Exposure"),
    ("pages/3_Overlap_Analyse.py",    "Overlap"),
    ("pages/4_Risiko_Markowitz.py",   "Risiko"),
    ("pages/6_Overlay_Manager.py",    "Overlay"),
    ("pages/5_Report_Export.py",      "Export"),
]


def inject_page(active: str = "dashboard"):
    """
    Call at the very top of every page (right after set_page_config).
    Injects design system, navbar, nav links, profile popover and theme CSS.
    """
    # 0. Auth guard — runs on every page so subpages are also protected
    from utils.auth import require_auth
    require_auth()

    # 1. Critical early CSS
    st.markdown(EARLY_CSS, unsafe_allow_html=True)

    # 2. Full design system
    st.markdown(DESIGN_SYSTEM, unsafe_allow_html=True)

    # 3. Lazy-load profile from disk (once per session, any page)
    if "pa_profile_loaded" not in st.session_state:
        from utils.persistence import load_profile
        _username = st.session_state.get("username", "local")
        _profile  = load_profile(_username)
        st.session_state["pa_theme"]      = _profile.get("theme", "midnight")
        st.session_state["pa_avatar"]     = _profile.get("avatar", "")
        st.session_state["pa_avatar_mime"] = _profile.get("avatar_mime", "image/jpeg")
        st.session_state["pa_profile_loaded"] = True

    # 4. Apply colour theme override (always inject so non-midnight themes work on all pages)
    theme_key = st.session_state.get("pa_theme", "midnight")
    st.markdown(_theme_override_css(theme_key), unsafe_allow_html=True)

    # 5. Background orbs + particle canvas
    st.markdown(EFFECTS, unsafe_allow_html=True)
    components.html(EFFECTS_JS, height=0, scrolling=False)

    # 6. Visual navbar HTML — avatar rendered directly as pure HTML (no Streamlit component)
    connected     = bool(st.session_state.get("data_provider"))
    provider_name = st.session_state.get("provider_name", "Nicht verbunden")
    display_name  = st.session_state.get("name", "")
    avatar_b64    = st.session_state.get("pa_avatar", "")
    avatar_mime   = st.session_state.get("pa_avatar_mime", "image/jpeg")
    st.markdown(
        _nav_visual(provider_name, connected, display_name, avatar_b64, avatar_mime),
        unsafe_allow_html=True,
    )

    # 7. Nav links + gear in ONE horizontal block → JS positions everything into navbar
    nav_cols = st.columns(len(_PAGES) + 1, gap="small")
    for col, (path, label) in zip(nav_cols, _PAGES):
        with col:
            st.page_link(path, label=label)
    with nav_cols[-1]:
        if st.button("⚙", key="pa_gear_btn"):
            _pa_open_profile()
