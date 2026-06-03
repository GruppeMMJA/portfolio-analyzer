# Portfolio Analyzer

Interaktive Portfolio-Analyse mit Streamlit: Exposure-Analyse (Länder, Währungen, Branchen), Overlap-Erkennung und Markowitz-Optimierung.

## Features

- **Portfolio Eingabe**: Manuell, per Screenshot (Claude Vision OCR) oder CSV-Import
- **Exposure Dashboard**: Weltkarte, Treemap, Balkendiagramme für Länder/Währungen/Sektoren
- **Overlap-Analyse**: Erkennt Überschneidungen zwischen ETFs und Einzelaktien, Sankey-Diagramm
- **Risiko & Markowitz**: EWMA-Volatilität, Efficient Frontier, Sharpe Ratio, Korrelationsmatrix

## Setup

### 1. Voraussetzungen

- Python 3.10+
- Bloomberg Terminal (optional, empfohlen)
- Anthropic API Key (für Screenshot-OCR)

### 2. Installation

```bash
# Repository klonen / Dateien kopieren
cd portfolio_analyzer

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### 3. Bloomberg (optional)

Falls Bloomberg Terminal vorhanden:

```bash
# Bloomberg C++ SDK muss installiert sein
# Siehe: https://www.bloomberg.com/professional/support/api-library/
pip install blpapi
```

### 4. Anthropic API Key (für Screenshot-OCR)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Oder in .env Datei setzen
```

### 5. Starten

```bash
streamlit run app.py
```

Die App öffnet sich im Browser unter `http://localhost:8501`.

## Nutzung

1. **Datenquelle verbinden** — Sidebar → "Bloomberg Terminal" oder "Yahoo Finance" → "Verbinden"
2. **Portfolio eingeben** — Seite "Portfolio Eingabe" → Manuell oder Screenshot
3. **Exposure analysieren** — Seite "Exposure Dashboard"
4. **Überschneidungen prüfen** — Seite "Overlap-Analyse"
5. **Risiko berechnen** — Seite "Risiko & Markowitz"

## Projektstruktur

```
portfolio_analyzer/
├── app.py                          # Hauptseite
├── requirements.txt                # Dependencies
├── core/
│   ├── portfolio.py                # Portfolio-Datenmodell
│   ├── data_provider.py            # Bloomberg + yfinance Provider
│   ├── exposure_engine.py          # Länder/Währung/Sektor-Analyse
│   ├── overlap_engine.py           # Überschneidungserkennung
│   ├── risk_engine.py              # Volatilität, Markowitz
│   └── ocr_engine.py               # Claude Vision OCR
├── pages/
│   ├── 1_📝_Portfolio_Eingabe.py   # Manuelle Eingabe + Screenshot
│   ├── 2_🌍_Exposure_Dashboard.py  # Weltkarte, Treemap, Charts
│   ├── 3_🔗_Overlap_Analyse.py     # Sankey, Overlap-Matrix
│   └── 4_📈_Risiko_Markowitz.py    # Efficient Frontier, KPIs
└── utils/
    ├── constants.py                # GICS, Länder, Währungen
    └── ticker_matcher.py           # Fuzzy-Matching für OCR
```

## Datenquellen

| Quelle | Vorteile | Nachteile |
|--------|----------|-----------|
| Bloomberg Terminal | Goldstandard, ETF-Holdings | Lizenz nötig |
| Yahoo Finance | Kostenlos | Keine ETF-Holdings, Rate Limits |

## Nächste Schritte

- [ ] Bloomberg-Felder für ETF-Holdings testen und kalibrieren
- [ ] Benchmark-Vergleich erweitern (Über-/Untergewichtung vs. Index)
- [ ] Export-Funktion (PDF-Report)
- [ ] Historisches Portfolio-Tracking über Zeit
- [ ] Multi-Currency-Unterstützung (Portfolio in CHF, GBP, etc.)
