"""
Generates the Portfolio Analyzer presentation PDF.
Run with: python generate_presentation.py
Output: Desktop/Portfolio_Analyzer_Praesentation.pdf
"""

from fpdf import FPDF
from fpdf.enums import RenderStyle
import os

OUTPUT = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "Portfolio_Analyzer_Praesentation.pdf")

# ── Colour palette ──────────────────────────────────────────────────────────
C_BG        = (8, 10, 22)        # near-black navy
C_CARD      = (18, 22, 42)       # dark card
C_ACCENT1   = (99, 102, 241)     # indigo
C_ACCENT2   = (139, 92, 246)     # violet
C_ACCENT3   = (6, 182, 212)      # cyan
C_GREEN     = (52, 211, 153)
C_AMBER     = (251, 191, 36)
C_WHITE     = (240, 244, 255)
C_MUTED     = (124, 135, 166)
C_BORDER    = (35, 40, 65)

W, H = 297, 210   # A4 landscape

class PDF(FPDF):
    def _rr(self, x, y, w, h, r=4, style=RenderStyle.DF):
        self._draw_rounded_rect(x, y, w, h, style, True, r)

    def _card(self, x, y, w, h, radius=4, fill=C_CARD, border=C_BORDER):
        self.set_fill_color(*fill)
        self.set_draw_color(*border)
        self.set_line_width(0.3)
        self._rr(x, y, w, h, radius, RenderStyle.DF)

    def _badge(self, x, y, text, color=C_ACCENT1, text_color=C_WHITE):
        self.set_font("Helvetica", "B", 6.5)
        tw = self.get_string_width(text) + 6
        self.set_fill_color(*color)
        self.set_draw_color(*color)
        self._rr(x, y, tw, 5.5, 2, RenderStyle.F)
        self.set_text_color(*text_color)
        self.set_xy(x + 3, y + 0.9)
        self.cell(tw - 6, 4, text)

    def _dot(self, x, y, r, color):
        self.set_fill_color(*color)
        self.ellipse(x - r, y - r, r * 2, r * 2, style="F")

    def _glow_line(self, x, y, w):
        steps = 60
        for i in range(steps):
            t = i / steps
            if t < 0.5:
                alpha = int(t * 2 * 180)
            else:
                alpha = int((1 - t) * 2 * 180)
            r = int(C_ACCENT1[0] * (1 - t) + C_ACCENT2[0] * t)
            g = int(C_ACCENT1[1] * (1 - t) + C_ACCENT2[1] * t)
            b = int(C_ACCENT1[2] * (1 - t) + C_ACCENT2[2] * t)
            self.set_draw_color(r, g, b)
            self.set_line_width(0.4)
            self.line(x + t * w, y, x + (t + 1 / steps) * w, y)

    def header(self):
        pass

    def footer(self):
        pass


pdf = PDF(orientation="L", unit="mm", format="A4")
pdf.set_auto_page_break(False)
pdf.set_margins(0, 0, 0)


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1 - TITLE
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()

# Background
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")

# Top accent strip
for i, c in enumerate([C_ACCENT1, C_ACCENT2, C_ACCENT3]):
    pdf.set_fill_color(*c)
    pdf.rect(i * (W / 3), 0, W / 3, 1.2, style="F")

# Left glow orb
pdf.set_fill_color(60, 63, 160)
pdf.ellipse(-30, -30, 120, 120, style="F")
pdf.set_fill_color(*C_BG)
pdf.ellipse(-15, -15, 90, 90, style="F")

# PA Logo box
pdf.set_fill_color(*C_ACCENT1)
pdf.set_draw_color(*C_ACCENT2)
pdf.set_line_width(0.5)
pdf._rr(28, 55, 28, 28, 6, RenderStyle.DF)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(28, 63)
pdf.cell(28, 12, "PA", align="C")

# Title
pdf.set_font("Helvetica", "B", 34)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(64, 48)
pdf.cell(160, 18, "Portfolio Analyzer")

# Subtitle
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(65, 68)
pdf.cell(160, 8, "Fullstack Web-App  ·  Gruppenarbeit  ·  Präsentation")

# Glow line under title
pdf._glow_line(64, 80, 180)

# Meta info
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(65, 84)
pdf.cell(60, 5, "Entwicklung mit Unterstützung von")
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*C_ACCENT1)
pdf.set_xy(65, 90)
pdf.cell(60, 5, "Claude (Anthropic AI)")

# Badges
pdf._badge(65, 100, "Python 3.13+", C_ACCENT1)
pdf._badge(98, 100, "Streamlit", C_ACCENT2)
pdf._badge(131, 100, "Yahoo Finance", C_ACCENT3)
pdf._badge(169, 100, "Plotly", (52, 155, 120))
pdf._badge(196, 100, "Pandas", (245, 100, 50))

# Right side - feature list
pdf._card(190, 30, 90, 145, radius=6, fill=(14, 18, 35))

pdf.set_font("Helvetica", "B", 7)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(197, 36)
pdf.cell(76, 5, "FEATURES")

features = [
    (C_ACCENT1, "Dashboard", "KPIs, Portfolio-Übersicht"),
    (C_ACCENT2, "Exposure", "Länder, Sektoren, Währungen"),
    (C_ACCENT3, "Overlap", "ETF-Überschneidungsanalyse"),
    (C_GREEN,   "Risiko",   "Markowitz, Sharpe, Drawdown"),
    (C_AMBER,   "Overlay",  "Zielportfolio-Vergleich"),
    ((248,113,113), "Export","Excel, CSV, Markdown"),
]
for i, (color, title, desc) in enumerate(features):
    y = 44 + i * 19
    pdf._dot(199, y + 5, 2.5, color)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(204, y + 1.5)
    pdf.cell(70, 5, title)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(204, y + 7)
    pdf.cell(70, 4, desc)

# Bottom
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(28, H - 12)
pdf.cell(60, 5, "Folie 1 / 6")
pdf.set_xy(130, H - 12)
pdf.cell(100, 5, "Portfolio Analyzer  ·  Gruppenarbeit", align="C")


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2 - TECH STACK & ARCHITEKTUR
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")

# Header bar
pdf.set_fill_color(*C_CARD)
pdf.rect(0, 0, W, 22, style="F")
pdf._glow_line(0, 22, W)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(15, 6)
pdf.cell(100, 10, "Tech Stack & Architektur")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(220, 8)
pdf.cell(60, 6, "Folie 2 / 6", align="R")

# ── Left: Tech stack cards ──
techs = [
    ("Streamlit", "Web-Framework", "Seiten-Routing, UI-Komponenten,\nSession State, Layouts", C_ACCENT1),
    ("Yahoo Finance\n(yfinance)", "Datenquelle", "Live-Kurse, Historische Reihen,\nStammdaten (Sektor, Land, Typ)", C_ACCENT3),
    ("Pandas", "Datenhaltung", "DataFrames für Portfolio,\nExposure-Berechnungen", (245, 100, 50)),
    ("Plotly", "Visualisierung", "Choropleth-Karte, Treemap,\nEfficient Frontier, Heatmaps", (52, 155, 120)),
    ("SciPy / NumPy", "Numerik", "Kovarianzmatrix, Portfolio-\nOptimierung (Markowitz)", C_ACCENT2),
]
for i, (name, cat, desc, color) in enumerate(techs):
    x = 12 + (i % 3) * 90
    y = 30 + (i // 3) * 52
    pdf._card(x, y, 84, 44, fill=(14, 18, 38))
    pdf.set_fill_color(*color)
    pdf.rect(x, y, 84, 2.5, style="F")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(x + 4, y + 5)
    pdf.multi_cell(76, 5, name)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(x + 4, y + 14)
    pdf.cell(76, 4, cat.upper(), )
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(180, 190, 215)
    pdf.set_xy(x + 4, y + 19)
    pdf.multi_cell(76, 4.5, desc)

# ── Right: Projektstruktur ──
pdf._card(198, 28, 87, 165, fill=(13, 17, 36))
pdf.set_font("Helvetica", "B", 7.5)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(204, 33)
pdf.cell(75, 5, "PROJEKTSTRUKTUR")

structure = [
    ("portfolio_analyzer/",           True,  C_ACCENT1, 0),
    ("+-- app.py",                    False, C_ACCENT2, 1),
    ("+-- pages/",                    True,  C_ACCENT3, 1),
    ("|   +-- 0_Anleitung.py",        False, C_MUTED, 2),
    ("|   +-- 2_Exposure_Dashboard.py",False, C_MUTED, 2),
    ("|   +-- 3_Overlap_Analyse.py",  False, C_MUTED, 2),
    ("|   +-- 4_Risiko_Markowitz.py", False, C_MUTED, 2),
    ("|   +-- 5_Report_Export.py",    False, C_MUTED, 2),
    ("|   `-- 6_Overlay_Manager.py",  False, C_MUTED, 2),
    ("+-- core/",                     True,  C_ACCENT3, 1),
    ("|   +-- portfolio.py",          False, C_MUTED, 2),
    ("|   +-- data_provider.py",      False, C_MUTED, 2),
    ("|   +-- exposure_engine.py",    False, C_MUTED, 2),
    ("|   +-- overlap_engine.py",     False, C_MUTED, 2),
    ("|   +-- risk_engine.py",        False, C_MUTED, 2),
    ("|   `-- ocr_engine.py",         False, C_MUTED, 2),
    ("`-- utils/",                    True,  C_ACCENT3, 1),
    ("    +-- nav.py",                False, C_MUTED, 2),
    ("    +-- persistence.py",        False, C_MUTED, 2),
    ("    `-- search.py",             False, C_MUTED, 2),
]
for i, (label, bold, color, indent) in enumerate(structure):
    y = 41 + i * 7.2
    pdf.set_font("Helvetica", "B" if bold else "", 6.8)
    pdf.set_text_color(*color)
    pdf.set_xy(204, y)
    pdf.cell(75, 5, label)


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3 - BACKEND DEEP DIVE
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")
pdf.set_fill_color(*C_CARD)
pdf.rect(0, 0, W, 22, style="F")
pdf._glow_line(0, 22, W)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(15, 6)
pdf.cell(100, 10, "Backend Deep Dive")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(220, 8)
pdf.cell(60, 6, "Folie 3 / 6", align="R")

modules = [
    {
        "title": "Portfolio & Position",
        "file": "core/portfolio.py",
        "color": C_ACCENT1,
        "lines": [
            "Zentrale Datenmodelle: Portfolio,",
            "Position, AssetType (ETF / Aktie).",
            "Berechnet Gewichte, Gesamtwert,",
            "to_dataframe() für UI-Tabellen.",
        ],
    },
    {
        "title": "DataProvider",
        "file": "core/data_provider.py",
        "color": C_ACCENT3,
        "lines": [
            "Abstraktion über yfinance.",
            "enrich_position() holt Kurs,",
            "Sektor, Land, Asset-Typ.",
            "Demo-Modus: statische Testdaten.",
        ],
    },
    {
        "title": "ExposureEngine",
        "file": "core/exposure_engine.py",
        "color": C_ACCENT2,
        "lines": [
            "Berechnet Länder-, Sektor- und",
            "Währungs-Gewichtungen.",
            "ETF-Durchblick: Gewichte aus",
            "hinterlegter ETF-Datenbank.",
        ],
    },
    {
        "title": "OverlapEngine",
        "file": "core/overlap_engine.py",
        "color": C_GREEN,
        "lines": [
            "Paarweiser Jaccard-/Gewichts-",
            "Overlap zwischen ETFs.",
            "Liefert Overlap-Matrix und",
            "Top-Holdings-Ranking.",
        ],
    },
    {
        "title": "RiskEngine",
        "file": "core/risk_engine.py",
        "color": C_AMBER,
        "lines": [
            "Lädt hist. Kursreihen via yfinance.",
            "Berechnet: Volatilität, Sharpe,",
            "Max Drawdown, Beta, VaR.",
            "Markowitz Efficient Frontier.",
        ],
    },
    {
        "title": "Persistence & Search",
        "file": "utils/persistence.py + search.py",
        "color": (248, 113, 113),
        "lines": [
            "JSON-Speicherung des Portfolios",
            "pro User lokal auf Disk.",
            "Ticker-Auflösung: ISIN, WKN,",
            "Name -> Yahoo-Ticker.",
        ],
    },
]

cols = 3
col_w = 90
for i, m in enumerate(modules):
    col = i % cols
    row = i // cols
    x = 12 + col * (col_w + 3)
    y = 28 + row * 55
    pdf._card(x, y, col_w, 50, fill=(14, 18, 38))
    pdf.set_fill_color(*m["color"])
    pdf.rect(x, y, col_w, 2.5, style="F")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(x + 4, y + 5)
    pdf.cell(col_w - 8, 5, m["title"])
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(x + 4, y + 11)
    pdf.cell(col_w - 8, 4, m["file"])
    for j, line in enumerate(m["lines"]):
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(185, 195, 220)
        pdf.set_xy(x + 4, y + 17 + j * 7)
        pdf.cell(col_w - 8, 5, line)


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4 - HERANGEHENSWEISE MIT CLAUDE AI
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")
pdf.set_fill_color(*C_CARD)
pdf.rect(0, 0, W, 22, style="F")
pdf._glow_line(0, 22, W)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(15, 6)
pdf.cell(120, 10, "Herangehensweise mit Claude AI")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(220, 8)
pdf.cell(60, 6, "Folie 4 / 6", align="R")

# Left column - workflow steps
pdf._card(12, 28, 130, 168, fill=(13, 17, 36))
pdf.set_font("Helvetica", "B", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(18, 33)
pdf.cell(118, 5, "ENTWICKLUNGS-WORKFLOW")

steps = [
    (C_ACCENT1, "1. Anforderungen definieren",
     "Features, Datenquellen und UI-Konzept\nim Gespräch mit Claude strukturiert."),
    (C_ACCENT2, "2. Architektur planen",
     "Modulstruktur (core/, utils/, pages/)\ngemeinsam mit Claude entworfen."),
    (C_ACCENT3, "3. Iterative Implementierung",
     "Jedes Modul Schritt für Schritt gebaut\nund sofort getestet."),
    (C_GREEN,   "4. Design System entwickeln",
     "Komplettes CSS/JS Design-System (Navbar,\nAnimationen, Themes) mit Claude erstellt."),
    (C_AMBER,   "5. Fehler debuggen",
     "Bugs direkt im Chat erklärt bekommen\nund mit Fixes aus dem Kontext gelöst."),
    (C_ACCENT1, "6. Optimierung",
     "Performance-Issues (DOM-Lag, Particles)\nidentifiziert und gemeinsam behoben."),
]
for i, (color, title, desc) in enumerate(steps):
    y = 42 + i * 24
    pdf._dot(22, y + 5, 3, color)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(28, y + 1)
    pdf.cell(108, 5, title)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(28, y + 7)
    pdf.multi_cell(108, 4.5, desc)
    # connector line
    if i < len(steps) - 1:
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.3)
        pdf.line(22, y + 9, 22, y + 24)

# Right column - Claude highlights
pdf._card(150, 28, 135, 80, fill=(14, 18, 38))
pdf.set_fill_color(*C_ACCENT1)
pdf.rect(150, 28, 135, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(156, 33)
pdf.cell(123, 5, "Was Claude konkret beigetragen hat")

highlights = [
    "Vollständiges Multi-Page Streamlit-App Gerüst",
    "Portfolio-Datenmodell (Position, AssetType, Gewichte)",
    "Yahoo Finance Integration & ISIN/WKN-Resolver",
    "Exposure-Engine mit ETF-Durchblick",
    "Markowitz Optimierung + Efficient Frontier Plot",
    "Design System: Navbar, Themes, Glassmorphism CSS",
    "Anleitung-Seite mit detaillierter Dokumentation",
    "Performance-Fixes (DOM-Interval, Particles)",
]
for i, h in enumerate(highlights):
    y = 42 + i * 7.8
    pdf._dot(157, y + 2.5, 1.8, C_ACCENT2)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(185, 195, 220)
    pdf.set_xy(161, y)
    pdf.cell(118, 5, h)

# Lessons learned
pdf._card(150, 115, 135, 82, fill=(14, 18, 38))
pdf.set_fill_color(*C_GREEN)
pdf.rect(150, 115, 135, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(156, 120)
pdf.cell(123, 5, "Lessons Learned")

lessons = [
    (C_GREEN,  "Kontext ist alles",
     "Claude versteht Codeänderungen im Kontext der\ngsamten Codebasis - kein Copy-Paste nötig."),
    (C_ACCENT3,"Iterativ > perfekt",
     "Kleine Schritte, sofort testen, dann weiter -\nfunktioniert besser als Mega-Prompts."),
    (C_AMBER,  "Eigene Entscheidungen treffen",
     "Claude schlägt vor, du entscheidest. Kritisch\nhinterfragen bringt bessere Ergebnisse."),
]
for i, (color, title, desc) in enumerate(lessons):
    y = 128 + i * 21
    pdf._dot(157, y + 3.5, 2.2, color)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(162, y)
    pdf.cell(116, 5, title)
    pdf.set_font("Helvetica", "", 7.3)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(162, y + 6)
    pdf.multi_cell(116, 4.3, desc)


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 5 - DATENFLUSS
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")
pdf.set_fill_color(*C_CARD)
pdf.rect(0, 0, W, 22, style="F")
pdf._glow_line(0, 22, W)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(15, 6)
pdf.cell(100, 10, "Datenfluss & Session State")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(220, 8)
pdf.cell(60, 6, "Folie 5 / 6", align="R")

# Flow diagram
flow_nodes = [
    (30,  90, "User", "Browser",         C_ACCENT1),
    (90,  90, "Streamlit", "Frontend",   C_ACCENT2),
    (155, 90, "DataProvider", "yfinance",C_ACCENT3),
    (218, 90, "Yahoo Finance", "API",    C_GREEN),
]
for x, y, title, sub, color in flow_nodes:
    pdf._card(x - 22, y - 18, 44, 36, fill=(14, 18, 38))
    pdf.set_fill_color(*color)
    pdf.rect(x - 22, y - 18, 44, 2.5, style="F")
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(x - 18, y - 12)
    pdf.cell(36, 5, title, align="C")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(x - 18, y - 5)
    pdf.cell(36, 4, sub, align="C")

# Arrows between nodes
arrow_labels = ["HTTP Request", "enrich_position()", "GET /v8/finance"]
for i in range(len(flow_nodes) - 1):
    x1 = flow_nodes[i][0] + 22
    x2 = flow_nodes[i + 1][0] - 22
    y0 = flow_nodes[i][1]
    pdf.set_draw_color(*C_ACCENT1)
    pdf.set_line_width(0.5)
    pdf.line(x1, y0 - 5, x2, y0 - 5)
    # arrowhead
    pdf.line(x2, y0 - 5, x2 - 3, y0 - 8)
    pdf.line(x2, y0 - 5, x2 - 3, y0 - 2)
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.set_text_color(*C_MUTED)
    mx = (x1 + x2) / 2
    pdf.set_xy(mx - 20, y0 - 14)
    pdf.cell(40, 4, arrow_labels[i], align="C")

# Session State box
pdf._card(12, 130, 120, 62, fill=(13, 17, 36))
pdf.set_fill_color(*C_ACCENT1)
pdf.rect(12, 130, 120, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(18, 135)
pdf.cell(108, 5, "st.session_state - Globaler App-Zustand")
ss_items = [
    ("portfolio",       "Portfolio-Objekt mit allen Positionen"),
    ("data_provider",   "Aktiver DataProvider (Yahoo / Demo / None)"),
    ("provider_name",   "Angezeigter Name in der Navbar"),
    ("enriched",        "Flag: Daten geladen?"),
    ("returns_loaded",  "Flag: Kurshistorie für Risiko verfügbar?"),
    ("pa_theme",        "Gewähltes UI-Theme"),
    ("pa_avatar",       "Profilbild als Base64-String"),
]
for i, (key, desc) in enumerate(ss_items):
    y = 143 + i * 6.8
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*C_ACCENT2)
    pdf.set_xy(18, y)
    pdf.cell(38, 4.5, key)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(57, y)
    pdf.cell(68, 4.5, desc)

# Persistence box
pdf._card(142, 130, 143, 62, fill=(13, 17, 36))
pdf.set_fill_color(*C_GREEN)
pdf.rect(142, 130, 143, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(148, 135)
pdf.cell(131, 5, "Persistenz-Strategie")
persist_items = [
    (C_GREEN,  "JSON auf Disk",
     "Portfolio wird nach jeder Änderung automatisch\nals JSON gespeichert (~/.portfolio_analyzer/<user>.json)"),
    (C_ACCENT3,"Restore on Start",
     "Beim nächsten App-Start wird das Portfolio\nsofort geladen und mit Yahoo-Kursen angereichert."),
    (C_ACCENT2,"Profil-Speicherung",
     "Theme und Profilbild werden separat im\nProfil-JSON gespeichert und wiederhergestellt."),
]
for i, (color, title, desc) in enumerate(persist_items):
    y = 144 + i * 15.5
    pdf._dot(149, y + 3, 2.2, color)
    pdf.set_font("Helvetica", "B", 7.8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(154, y)
    pdf.cell(124, 5, title)
    pdf.set_font("Helvetica", "", 7.2)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(154, y + 6)
    pdf.multi_cell(124, 4, desc)


# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6 - DEPLOYMENT & LAUNCH
# ════════════════════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_fill_color(*C_BG)
pdf.rect(0, 0, W, H, style="F")
pdf.set_fill_color(*C_CARD)
pdf.rect(0, 0, W, 22, style="F")
pdf._glow_line(0, 22, W)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(15, 6)
pdf.cell(100, 10, "Deployment & Launch")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*C_MUTED)
pdf.set_xy(220, 8)
pdf.cell(60, 6, "Folie 6 / 6", align="R")

# Local launch
pdf._card(12, 28, 135, 80, fill=(13, 17, 36))
pdf.set_fill_color(*C_ACCENT1)
pdf.rect(12, 28, 135, 2.5, style="F")
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(18, 33)
pdf.cell(123, 5, "Lokal starten (lokale Entwicklung)")

local_steps = [
    ("1", "Repository klonen / Projekt-Ordner öffnen", ""),
    ("2", "Abhängigkeiten installieren", "pip install -r requirements.txt"),
    ("3", "App starten", "python -m streamlit run portfolio_analyzer/app.py"),
    ("4", "Browser öffnet sich automatisch", "http://localhost:8501"),
]
for i, (num, title, code) in enumerate(local_steps):
    y = 42 + i * 16
    pdf.set_fill_color(*C_ACCENT1)
    pdf.ellipse(19, y + 1, 8, 8, style="F")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(19, y + 1.5)
    pdf.cell(8, 5, num, align="C")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(30, y + 1)
    pdf.cell(110, 5, title)
    if code:
        pdf.set_fill_color(8, 12, 28)
        pdf._rr(30, y + 7, 110, 7, 2, RenderStyle.F)
        pdf.set_font("Courier", "", 7.5)
        pdf.set_text_color(*C_ACCENT3)
        pdf.set_xy(33, y + 9)
        pdf.cell(104, 4, code)

# Streamlit Cloud
pdf._card(155, 28, 130, 80, fill=(13, 17, 36))
pdf.set_fill_color(*C_ACCENT2)
pdf.rect(155, 28, 130, 2.5, style="F")
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(161, 33)
pdf.cell(118, 5, "Streamlit Community Cloud (kostenlos)")

cloud_steps = [
    ("1", "GitHub-Repository erstellen und pushen", ""),
    ("2", "share.streamlit.io aufrufen und anmelden", ""),
    ("3", "New app -> Repo auswählen", "Main file: portfolio_analyzer/app.py"),
    ("4", "Deploy klicken - fertig!", "Öffentliche URL in ~2 Minuten"),
]
for i, (num, title, code) in enumerate(cloud_steps):
    y = 42 + i * 16
    pdf.set_fill_color(*C_ACCENT2)
    pdf.ellipse(162, y + 1, 8, 8, style="F")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(162, y + 1.5)
    pdf.cell(8, 5, num, align="C")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(173, y + 1)
    pdf.cell(105, 5, title)
    if code:
        pdf.set_fill_color(8, 12, 28)
        pdf._rr(173, y + 7, 105, 7, 2, RenderStyle.F)
        pdf.set_font("Helvetica", "", 7.2)
        pdf.set_text_color(*C_ACCENT3)
        pdf.set_xy(176, y + 9)
        pdf.cell(99, 4, code)

# Requirements info
pdf._card(12, 115, 135, 78, fill=(13, 17, 36))
pdf.set_fill_color(*C_AMBER)
pdf.rect(12, 115, 135, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(18, 120)
pdf.cell(123, 5, "requirements.txt (Auszug)")
reqs = [
    "streamlit>=1.32",
    "yfinance>=0.2",
    "pandas>=2.0",
    "plotly>=5.18",
    "numpy>=1.26",
    "scipy>=1.12",
    "openpyxl>=3.1",
    "Pillow>=10.0",
]
for i, r in enumerate(reqs):
    col = i % 2
    row = i // 2
    x = 18 + col * 60
    y = 129 + row * 14
    pdf._card(x, y, 56, 11, fill=(8, 12, 28))
    pdf.set_font("Courier", "", 7.5)
    pdf.set_text_color(*C_ACCENT3)
    pdf.set_xy(x + 3, y + 2)
    pdf.cell(50, 5, r)

# Deployment options
pdf._card(155, 115, 130, 78, fill=(13, 17, 36))
pdf.set_fill_color(*C_GREEN)
pdf.rect(155, 115, 130, 2.5, style="F")
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_text_color(*C_WHITE)
pdf.set_xy(161, 120)
pdf.cell(118, 5, "Weitere Deployment-Optionen")

options = [
    (C_ACCENT1, "Docker", "Dockerfile erstellen, Container bauen\nund überall deployen (auch lokal)."),
    (C_ACCENT3, "Render / Railway", "Kostenloses Hosting mit GitHub-\nIntegration und Auto-Deploy."),
    (C_AMBER,   "Eigener Server", "Streamlit läuft auf jedem Linux-Server.\nNginx als Reverse Proxy vorschalten."),
]
for i, (color, title, desc) in enumerate(options):
    y = 130 + i * 19
    pdf._dot(162, y + 4.5, 2.5, color)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(167, y + 1)
    pdf.cell(111, 5, title)
    pdf.set_font("Helvetica", "", 7.3)
    pdf.set_text_color(*C_MUTED)
    pdf.set_xy(167, y + 7)
    pdf.multi_cell(111, 4.2, desc)

# ── Final footer on all pages ─────────────────────────────────────────────
# (already added per-slide as "Folie X/6")

pdf.output(OUTPUT)
print(f"\nPDF gespeichert: {OUTPUT}\n")
