"""
Seite 0: Anleitung — Schritt-für-Schritt Benutzerhandbuch
"""

import streamlit as st
from utils.nav import inject_page

st.set_page_config(page_title="Anleitung", layout="wide", initial_sidebar_state="collapsed")

inject_page("anleitung")

st.markdown("""
<div class="page-hero anim-0">
  <h1>Anleitung</h1>
  <p class="page-hero-sub">Schritt für Schritt erklärt &mdash; vom ersten Start bis zur vollständigen Analyse</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# Inhaltsübersicht
# ─────────────────────────────────────────────────────
st.markdown("""
<div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
  padding:1.4rem 1.8rem;margin-bottom:2rem;animation:fadeUp .4s var(--ease) .05s both;">
  <div style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;
    text-transform:uppercase;margin-bottom:.9rem;">Inhaltsübersicht</div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.5rem .8rem;">
    <a href="#schritt1" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">1. Datenquelle wählen</a>
    <a href="#schritt2" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">2. Portfolio aufbauen</a>
    <a href="#schritt3" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">3. Exposure Dashboard</a>
    <a href="#schritt4" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">4. Overlap Analyse</a>
    <a href="#schritt5" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">5. Risiko &amp; Markowitz</a>
    <a href="#schritt6" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">6. Overlay Manager</a>
    <a href="#schritt7" style="color:var(--c1);text-decoration:none;font-size:.84rem;font-weight:500;">7. Report exportieren</a>
    <a href="#tipps" style="color:var(--c3);text-decoration:none;font-size:.84rem;font-weight:500;">Tipps &amp; Tricks</a>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 1 — Datenquelle wählen
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt1" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 1</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(99,102,241,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🔗</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Datenquelle wählen</div>
      <div style="font-size:.75rem;color:var(--text3);">Dashboard → Verbinden</div>
    </div>
  </div>
  <p style="font-size:.85rem;color:var(--text2);line-height:1.7;margin-bottom:.9rem;">
    Bevor du Wertpapiere hinzufügen kannst, musst du eine Datenquelle verbinden.
    Du hast zwei Optionen:
  </p>
  <div style="border:1px solid rgba(52,211,153,.2);border-radius:var(--rsm);
    background:rgba(52,211,153,.05);padding:.9rem 1rem;margin-bottom:.7rem;">
    <div style="font-weight:700;color:var(--green);font-size:.83rem;margin-bottom:.35rem;">
      Yahoo Finance (empfohlen)
    </div>
    <ul style="color:var(--text2);font-size:.81rem;line-height:1.8;padding-left:1.1rem;margin:0;">
      <li>Live-Kurse direkt von Yahoo Finance</li>
      <li>Automatische Anreicherung mit Stammdaten (Land, Sektor, Asset-Typ)</li>
      <li>Portfolio wird lokal gespeichert &amp; beim nächsten Start wiederhergestellt</li>
      <li>Kurse werden bei jedem Verbinden aktualisiert</li>
      <li>Erfordert eine aktive Internetverbindung</li>
    </ul>
  </div>
  <div style="border:1px solid rgba(99,102,241,.2);border-radius:var(--rsm);
    background:rgba(99,102,241,.05);padding:.9rem 1rem;">
    <div style="font-weight:700;color:var(--c1);font-size:.83rem;margin-bottom:.35rem;">
      Demo-Modus
    </div>
    <ul style="color:var(--text2);font-size:.81rem;line-height:1.8;padding-left:1.1rem;margin:0;">
      <li>Vorgefertigtes Beispiel-Portfolio (keine eigenen Daten nötig)</li>
      <li>Alle Features sofort nutzbar — ideal zum Ausprobieren</li>
      <li>Keine Internetverbindung erforderlich</li>
      <li>Änderungen werden <strong style="color:var(--amber)">nicht</strong> gespeichert</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">So verbindest du Yahoo Finance</div>
  <div style="display:flex;flex-direction:column;gap:.55rem;">
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c1);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">1</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Öffne das <strong style="color:var(--text)">Dashboard</strong> (zweiter Tab in der Navbar)
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c1);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">2</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Wähle im Bereich <strong style="color:var(--text)">Datenquelle</strong>
        den Radio-Button <em>Yahoo Finance</em>
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c1);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">3</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Klicke auf <strong style="color:var(--text)">Verbinden</strong> —
        der Status in der Navbar wechselt auf grün
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c1);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">4</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Falls ein Portfolio gespeichert war, wird es automatisch geladen und mit
        aktuellen Kursen neu angereichert
      </div>
    </div>
  </div>
  <div style="margin-top:1.1rem;padding:.7rem .9rem;border-radius:var(--rsm);
    background:rgba(251,191,36,.06);border:1px solid rgba(251,191,36,.18);">
    <div style="font-size:.75rem;color:var(--amber);font-weight:600;margin-bottom:.25rem;">
      ⚠ Hinweis: Yahoo Finance Rate-Limits
    </div>
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      Yahoo Finance hat inoffizielle Rate-Limits. Bei sehr großen Portfolios (&gt;20 Positionen)
      kann die Anreicherung langsamer sein. Warte in diesem Fall kurz und versuche es erneut.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 2 — Portfolio aufbauen
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt2" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 2</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(6,182,212,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🔍</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Wertpapier suchen</div>
      <div style="font-size:.75rem;color:var(--text3);">Suchfeld im Dashboard</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Im Dashboard findest du die Suchleiste. Du kannst auf vier Arten suchen:
  </p>
  <div style="display:flex;flex-direction:column;gap:.5rem;">
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.72rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.2rem;">Ticker</div>
      <div style="font-size:.81rem;color:var(--text2);">
        z.B. <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">AAPL</code>,
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">MSFT</code>,
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">SAP</code>
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.72rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.2rem;">ISIN</div>
      <div style="font-size:.81rem;color:var(--text2);">
        12-stelliger Code, z.B.
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">IE00B4L5Y983</code>
        (MSCI World ETF)
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.72rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.2rem;">WKN</div>
      <div style="font-size:.81rem;color:var(--text2);">
        6-stellige deutsche Kennnummer, z.B.
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">A0RPWH</code>
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.72rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.2rem;">Unternehmensname</div>
      <div style="font-size:.81rem;color:var(--text2);">
        z.B.
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">Apple</code>,
        <code style="color:var(--c1);background:rgba(99,102,241,.1);
        padding:.1rem .35rem;border-radius:4px;">Siemens</code>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(52,211,153,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">➕</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Position hinzufügen</div>
      <div style="font-size:.75rem;color:var(--text3);">Suchergebnisse → + Button</div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:.55rem;">
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--green);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">1</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Gib den Suchbegriff im Textfeld ein und klicke auf <strong style="color:var(--text)">Suchen</strong>
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--green);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">2</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Die Suchergebnisse erscheinen darunter mit Ticker, Name, Typ und Börse
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--green);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">3</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Trage den <strong style="color:var(--text)">Marktwert in €</strong> ein
        (z.B. 5000 für 5.000 €)
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--green);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">4</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Klicke auf <strong style="color:var(--text)">＋</strong> um die Position
        sofort anzureichern und dem Portfolio hinzuzufügen
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--green);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">5</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Das Dashboard-KPI aktualisiert sich sofort.
        Im Yahoo-Modus wird das Portfolio automatisch gespeichert.
      </div>
    </div>
  </div>
  <div style="margin-top:1rem;padding:.65rem .85rem;border-radius:var(--rsm);
    background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.18);">
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      💡 Ein Wertpapier kann nur <strong style="color:var(--text)">einmal</strong>
      im Portfolio sein. Falls es bereits vorhanden ist, zeigt der Button ein ✓.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .26s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(245,158,11,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">✏️</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Manuell bearbeiten</div>
      <div style="font-size:.75rem;color:var(--text3);">Tabelle direkt editieren</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Unter der Suchleiste findest du die editierbare Portfolio-Tabelle.
    Dort kannst du:
  </p>
  <ul style="color:var(--text2);font-size:.81rem;line-height:1.9;padding-left:1.1rem;margin:0 0 .8rem;">
    <li>Marktwerte direkt in der Tabelle anpassen</li>
    <li>Neue Positionen per Ticker, ISIN oder WKN manuell eintragen</li>
    <li>Positionen durch Löschen einer Zeile entfernen</li>
    <li>Namen frei bearbeiten</li>
  </ul>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Nach der Bearbeitung auf
    <strong style="color:var(--text)">Übernehmen &amp; anreichern</strong>
    klicken — die App löst alle Ticker auf und lädt die Daten.
  </p>
  <div style="padding:.65rem .85rem;border-radius:var(--rsm);
    background:rgba(248,113,113,.06);border:1px solid rgba(248,113,113,.18);">
    <div style="font-size:.75rem;color:var(--red);font-weight:600;margin-bottom:.2rem;">Portfolio leeren</div>
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      Der Button <em>Portfolio leeren</em> entfernt alle Positionen und löscht die gespeicherte Datei.
      Diese Aktion kann nicht rückgängig gemacht werden.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 3 — Exposure Dashboard
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt3" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 3</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(6,182,212,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🌍</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Exposure Dashboard</div>
      <div style="font-size:.75rem;color:var(--text3);">Navbar → Exposure</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.9rem;">
    Das Exposure Dashboard zeigt dir, wie dein Portfolio verteilt ist — welche Länder,
    Währungen und Branchen dominieren.
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem;">
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.7rem .85rem;">
      <div style="font-size:.7rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.35rem;">Weltkarte</div>
      <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
        Choropleth-Karte mit Farbintensität nach Länder-Exposure.
        ETF-Gewichtungen werden automatisch aufgeschlüsselt.
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.7rem .85rem;">
      <div style="font-size:.7rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.35rem;">Sektor-Treemap</div>
      <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
        Visualisiert GICS-Sektoren als Flächen — größere Fläche = höheres Gewicht.
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.7rem .85rem;">
      <div style="font-size:.7rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.35rem;">Währungsverteilung</div>
      <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
        Zeigt das Währungsrisiko deines Portfolios (USD, EUR, etc.).
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.7rem .85rem;">
      <div style="font-size:.7rem;font-weight:700;color:var(--c3);letter-spacing:.06em;
        text-transform:uppercase;margin-bottom:.35rem;">Benchmark-Vergleich</div>
      <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
        Vergleich mit MSCI World, S&amp;P 500 o.ä. per Dropdown auswählbar.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">Was bedeuten die Werte?</div>
  <div style="display:flex;flex-direction:column;gap:.7rem;">
    <div style="padding:.7rem .9rem;border-left:3px solid var(--c1);
      background:rgba(99,102,241,.05);border-radius:0 var(--rsm) var(--rsm) 0;">
      <div style="font-size:.8rem;font-weight:600;color:var(--text);margin-bottom:.2rem;">
        Direktes Exposure
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
        Bei Einzelaktien wird das Land direkt nach dem Firmensitz bestimmt.
        Eine Apple-Aktie = 100% USA.
      </div>
    </div>
    <div style="padding:.7rem .9rem;border-left:3px solid var(--c2);
      background:rgba(139,92,246,.05);border-radius:0 var(--rsm) var(--rsm) 0;">
      <div style="font-size:.8rem;font-weight:600;color:var(--text);margin-bottom:.2rem;">
        ETF-Durchblick
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
        Bei ETFs wird die Länderverteilung aus der hinterlegten ETF-Zusammensetzung
        (z.B. iShares MSCI World = 70% USA, 6% Japan…) automatisch aufgeschlüsselt.
      </div>
    </div>
    <div style="padding:.7rem .9rem;border-left:3px solid var(--c3);
      background:rgba(6,182,212,.05);border-radius:0 var(--rsm) var(--rsm) 0;">
      <div style="font-size:.8rem;font-weight:600;color:var(--text);margin-bottom:.2rem;">
        Gewichtung
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
        Alle Exposures werden nach dem Marktwert-Anteil am Gesamtportfolio gewichtet.
        Prozentwerte addieren sich zu 100%.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 4 — Overlap Analyse
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt4" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 4</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([0.9, 1.1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(236,72,153,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🔄</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Overlap Analyse</div>
      <div style="font-size:.75rem;color:var(--text3);">Navbar → Overlap</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Die Overlap-Analyse zeigt, welche Wertpapiere in mehreren ETFs deines Portfolios vorkommen.
    Damit erkennst du versteckte Klumpenrisiken.
  </p>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.9rem;">
    <strong style="color:var(--text)">Beispiel:</strong> Du hältst den MSCI World ETF und den S&amp;P 500 ETF.
    Beide enthalten große US-Tech-Aktien wie Apple oder Microsoft mit hohem Gewicht —
    dein effektives Exposure in diese Titel ist damit viel höher als gedacht.
  </p>
  <div style="padding:.7rem .9rem;border-radius:var(--rsm);
    background:rgba(236,72,153,.06);border:1px solid rgba(236,72,153,.18);">
    <div style="font-size:.75rem;color:#ec4899;font-weight:600;margin-bottom:.25rem;">
      Overlap Score
    </div>
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      Ein hoher Overlap-Score zwischen zwei ETFs bedeutet, dass diese sich stark überschneiden.
      Werte über 60% gelten als kritisch (redundante Diversifikation).
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">Was du in der Overlap-Analyse siehst</div>
  <div style="display:flex;flex-direction:column;gap:.6rem;">
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="font-size:1.1rem;flex-shrink:0;margin-top:.1rem;">📊</div>
      <div>
        <div style="font-size:.82rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
          Heatmap / Overlap-Matrix
        </div>
        <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
          Jede Zelle zeigt den Überschneidungsgrad zwischen zwei ETFs in Prozent.
          Je dunkler die Farbe, desto höher der Overlap.
        </div>
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="font-size:1.1rem;flex-shrink:0;margin-top:.1rem;">🏆</div>
      <div>
        <div style="font-size:.82rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
          Top überschneidende Holdings
        </div>
        <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
          Liste der einzelnen Aktien, die in den meisten deiner ETFs vorkommen —
          nach effektivem Gewicht sortiert.
        </div>
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="font-size:1.1rem;flex-shrink:0;margin-top:.1rem;">💡</div>
      <div>
        <div style="font-size:.82rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
          Empfehlung
        </div>
        <div style="font-size:.79rem;color:var(--text2);line-height:1.6;">
          Sehr ähnliche ETFs können durch einen einzelnen, breiter gestreuten ETF
          ersetzt werden ohne Diversifikation zu verlieren.
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 5 — Risiko & Markowitz
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt5" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 5</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(251,191,36,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">📈</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Risiko & Markowitz</div>
      <div style="font-size:.75rem;color:var(--text3);">Navbar → Risiko</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Hier werden Risikokennzahlen berechnet und die optimale Portfolio-Gewichtung
    nach der Markowitz-Theorie ermittelt.
  </p>
  <div style="padding:.65rem .85rem;border-radius:var(--rsm);
    background:rgba(251,191,36,.06);border:1px solid rgba(251,191,36,.18);margin-bottom:.7rem;">
    <div style="font-size:.75rem;color:var(--amber);font-weight:600;margin-bottom:.2rem;">
      Voraussetzung: Kursdaten laden
    </div>
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      Für diese Analyse werden historische Kursreihen benötigt.
      Der Button <em>Kursdaten laden</em> lädt die Daten automatisch über Yahoo Finance.
      Dieser Schritt dauert je nach Portfoliogröße 10–60 Sekunden.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;height:100%;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">Risikokennzahlen erklärt</div>
  <div style="display:flex;flex-direction:column;gap:.55rem;">
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Volatilität (σ)
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Streuung der täglichen Renditen. Höhere Volatilität = mehr Schwankung = mehr Risiko.
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Sharpe Ratio
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Rendite pro Risikoeinheit. Je höher, desto besser die risikobereinigte Performance.
        Werte &gt; 1.0 gelten als gut.
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Max Drawdown
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Größter Verlust vom Höchstkurs bis zum Tiefstkurs im Betrachtungszeitraum.
      </div>
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid var(--border);
      border-radius:var(--rsm);padding:.55rem .8rem;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Beta (β)
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Sensitivität gegenüber dem Markt. β=1 = marktkonform, β&gt;1 = aggressiver.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .26s both;height:100%;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">Efficient Frontier</div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Die Efficient Frontier zeigt alle Kombinationen deiner Positionen, die bei einem
    gegebenen Risiko die maximale Rendite erzielen.
  </p>
  <div style="display:flex;flex-direction:column;gap:.55rem;">
    <div style="padding:.65rem .85rem;border-left:3px solid var(--green);
      background:rgba(52,211,153,.05);border-radius:0 var(--rsm) var(--rsm) 0;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Optimales Portfolio (Max Sharpe)
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Gewichtungsvorschlag mit dem besten Rendite/Risiko-Verhältnis.
      </div>
    </div>
    <div style="padding:.65rem .85rem;border-left:3px solid var(--c3);
      background:rgba(6,182,212,.05);border-radius:0 var(--rsm) var(--rsm) 0;">
      <div style="font-size:.79rem;font-weight:600;color:var(--text);margin-bottom:.15rem;">
        Min-Varianz Portfolio
      </div>
      <div style="font-size:.78rem;color:var(--text2);line-height:1.5;">
        Gewichtung mit der kleinstmöglichen Schwankung — ideal für risikoaverse Anleger.
      </div>
    </div>
  </div>
  <div style="margin-top:.8rem;padding:.65rem .85rem;border-radius:var(--rsm);
    background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.18);">
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      💡 Diese Werte sind <strong style="color:var(--text)">Vorschläge</strong> basierend auf
      historischen Daten — keine Anlageberatung.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 6 — Overlay Manager
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt6" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 6</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(139,92,246,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🧩</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Overlay Manager</div>
      <div style="font-size:.75rem;color:var(--text3);">Navbar → Overlay</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Der Overlay Manager erlaubt es dir, ein <strong style="color:var(--text)">hypothetisches
    Wunschportfolio</strong> zu definieren und direkt mit deinem aktuellen Portfolio zu vergleichen.
  </p>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Du siehst auf einen Blick, wo du über- oder untergewichtet bist (Länder, Sektoren),
    und welche Trades du ausführen müsstest um das Ziel-Portfolio zu erreichen.
  </p>
  <div style="padding:.65rem .85rem;border-radius:var(--rsm);
    background:rgba(139,92,246,.06);border:1px solid rgba(139,92,246,.2);">
    <div style="font-size:.78rem;color:var(--text2);line-height:1.6;">
      💡 <strong style="color:var(--text)">Beispiel-Anwendung:</strong> Du möchtest den
      US-Anteil auf max. 50% reduzieren. Der Overlay zeigt dir, welche Positionen du
      verringern oder ersetzen müsstest.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;">
  <div style="font-size:.63rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
    text-transform:uppercase;margin-bottom:.8rem;">So verwendest du den Overlay Manager</div>
  <div style="display:flex;flex-direction:column;gap:.55rem;">
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c2);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">1</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Öffne den <strong style="color:var(--text)">Overlay Manager</strong> in der Navbar
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c2);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">2</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Erstelle ein neues Overlay und gib ihm einen Namen (z.B. <em>Zielportfolio 2025</em>)
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c2);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">3</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Füge Positionen mit Ziel-Gewichtungen oder -Beträgen hinzu
      </div>
    </div>
    <div style="display:flex;gap:.75rem;align-items:flex-start;">
      <div style="width:22px;height:22px;border-radius:50%;background:var(--c2);
        display:flex;align-items:center;justify-content:center;font-size:.7rem;
        font-weight:800;color:#fff;flex-shrink:0;margin-top:1px;">4</div>
      <div style="font-size:.83rem;color:var(--text2);line-height:1.6;">
        Der Vergleich zeigt Differenzen zwischen Ist- und Ziel-Exposure grafisch an
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Schritt 7 — Report Export
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="schritt7" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Schritt 7</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .1s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(52,211,153,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">📁</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Excel-Export</div>
      <div style="font-size:.75rem;color:var(--text3);">.xlsx mit allen Analysen</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Erzeugt eine Excel-Datei mit mehreren Tabellenblättern:
  </p>
  <ul style="color:var(--text2);font-size:.81rem;line-height:1.9;padding-left:1.1rem;margin:0;">
    <li>Portfolio-Übersicht</li>
    <li>Länder-Exposure</li>
    <li>Sektor-Exposition</li>
    <li>Overlap-Matrix</li>
    <li>Risikokennzahlen</li>
  </ul>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .18s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(6,182,212,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">📄</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">CSV-Export</div>
      <div style="font-size:.75rem;color:var(--text3);">Rohdaten als .csv</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Lädt einzelne Datensätze als CSV-Datei herunter:
  </p>
  <ul style="color:var(--text2);font-size:.81rem;line-height:1.9;padding-left:1.1rem;margin:0;">
    <li>Portfolio-Positionen</li>
    <li>Exposure-Tabellen</li>
    <li>Ideal für eigene Weiterverarbeitung in Excel oder Python</li>
  </ul>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="glass-card" style="padding:1.6rem;animation:fadeUp .45s var(--ease) .26s both;height:100%;">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:1rem;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(245,158,11,.12);
      display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">📝</div>
    <div>
      <div style="font-weight:700;color:var(--text);font-size:.95rem;">Markdown-Export</div>
      <div style="font-size:.75rem;color:var(--text3);">Für Notion, Obsidian etc.</div>
    </div>
  </div>
  <p style="font-size:.83rem;color:var(--text2);line-height:1.7;margin-bottom:.8rem;">
    Exportiert einen formatierten Bericht als Markdown-Datei:
  </p>
  <ul style="color:var(--text2);font-size:.81rem;line-height:1.9;padding-left:1.1rem;margin:0;">
    <li>Ideal für Notion, Obsidian oder GitHub</li>
    <li>Enthält alle wesentlichen KPIs und Tabellen</li>
    <li>Einfach in bestehende Notiz-Systeme einfügen</li>
  </ul>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# Tipps & Tricks
# ─────────────────────────────────────────────────────
st.markdown("""
<div id="tipps" style="scroll-margin-top:80px;"></div>
<div style="display:flex;align-items:center;gap:.7rem;margin:2.5rem 0 1.1rem;">
  <span style="font-size:.63rem;font-weight:800;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">Tipps & Tricks</span>
  <div style="flex:1;height:1px;background:var(--border);"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:.9rem;
  margin-bottom:2rem;animation:fadeUp .45s var(--ease) .1s both;">

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      🎨 Theme wechseln
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Klicke auf das <strong style="color:var(--text)">⚙ Symbol</strong> rechts in der Navbar
      um das Farbschema zu ändern (Midnight, Charcoal, Slate, Forest, Merlot, Warm).
    </div>
  </div>

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      💾 Automatisches Speichern
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Im Yahoo Finance Modus wird das Portfolio bei jeder Änderung automatisch gespeichert.
      Beim nächsten Start wird es sofort wiederhergestellt — du musst nichts manuell speichern.
    </div>
  </div>

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      🔢 Ticker für deutsche Börsen
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Für an der Xetra/Frankfurt gehandelte ETFs und Aktien das Suffix
      <code style="color:var(--c1);background:rgba(99,102,241,.1);
      padding:.05rem .3rem;border-radius:3px;">.DE</code> anhängen,
      z.B. <code style="color:var(--c1);background:rgba(99,102,241,.1);
      padding:.05rem .3rem;border-radius:3px;">EXS1.DE</code> für iShares Core MSCI World.
    </div>
  </div>

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      📱 Demo-Modus zum Ausprobieren
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Bevor du dein echtes Portfolio eingibst, teste alle Features im Demo-Modus.
      Er enthält ein realistisches Beispiel-Portfolio und funktioniert ohne Internet.
    </div>
  </div>

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      🔄 Kurse aktualisieren
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Klicke auf <em>Verbinden</em> im Dashboard, um alle Kurse und Stammdaten
      auf den aktuellen Stand zu bringen. Das dauert je nach Portfoliogröße
      einige Sekunden.
    </div>
  </div>

  <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);
    padding:1.2rem 1.4rem;">
    <div style="font-size:.88rem;font-weight:700;color:var(--text);margin-bottom:.5rem;">
      📊 ETF-Daten
    </div>
    <div style="font-size:.81rem;color:var(--text2);line-height:1.7;">
      Die App enthält eine interne Datenbank mit Länder-Gewichtungen für die
      gängigsten ETFs (iShares, Vanguard, Xtrackers etc.). Unbekannte ETFs werden
      als einzelne Position ohne Aufschlüsselung behandelt.
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)
