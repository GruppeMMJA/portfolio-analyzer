"""
Konstanten für Portfolio-Analyse: GICS-Sektoren, Länder-Mappings, Währungen.
"""

# GICS Sektor-Codes → Deutsche Bezeichnung
GICS_SECTORS = {
    10: "Energie",
    15: "Grundstoffe",
    20: "Industrie",
    25: "Zyklischer Konsum",
    30: "Basiskonsumgüter",
    35: "Gesundheit",
    40: "Finanzen",
    45: "Informationstechnologie",
    50: "Kommunikation",
    55: "Versorger",
    60: "Immobilien",
}

# GICS Sektor-Codes → Englische Bloomberg-Bezeichnung
GICS_SECTORS_EN = {
    10: "Energy",
    15: "Materials",
    20: "Industrials",
    25: "Consumer Discretionary",
    30: "Consumer Staples",
    35: "Health Care",
    40: "Financials",
    45: "Information Technology",
    50: "Communication Services",
    55: "Utilities",
    60: "Real Estate",
}

# Sektorfarben für Visualisierung (konsistent über alle Charts)
SECTOR_COLORS = {
    "Energie": "#E74C3C",
    "Grundstoffe": "#E67E22",
    "Industrie": "#F1C40F",
    "Zyklischer Konsum": "#2ECC71",
    "Basiskonsumgüter": "#1ABC9C",
    "Gesundheit": "#3498DB",
    "Finanzen": "#9B59B6",
    "Informationstechnologie": "#34495E",
    "Kommunikation": "#E91E63",
    "Versorger": "#795548",
    "Immobilien": "#607D8B",
}

# ISO-3166 Alpha-2 → Land (Deutsch) + Alpha-3 für Plotly Choropleth
COUNTRY_MAPPING = {
    "US": {"name": "USA", "alpha3": "USA", "region": "Nordamerika"},
    "GB": {"name": "Großbritannien", "alpha3": "GBR", "region": "Europa"},
    "DE": {"name": "Deutschland", "alpha3": "DEU", "region": "Europa"},
    "FR": {"name": "Frankreich", "alpha3": "FRA", "region": "Europa"},
    "JP": {"name": "Japan", "alpha3": "JPN", "region": "Asien-Pazifik"},
    "CN": {"name": "China", "alpha3": "CHN", "region": "Asien-Pazifik"},
    "HK": {"name": "Hongkong", "alpha3": "HKG", "region": "Asien-Pazifik"},
    "KR": {"name": "Südkorea", "alpha3": "KOR", "region": "Asien-Pazifik"},
    "TW": {"name": "Taiwan", "alpha3": "TWN", "region": "Asien-Pazifik"},
    "IN": {"name": "Indien", "alpha3": "IND", "region": "Asien-Pazifik"},
    "AU": {"name": "Australien", "alpha3": "AUS", "region": "Asien-Pazifik"},
    "CH": {"name": "Schweiz", "alpha3": "CHE", "region": "Europa"},
    "NL": {"name": "Niederlande", "alpha3": "NLD", "region": "Europa"},
    "SE": {"name": "Schweden", "alpha3": "SWE", "region": "Europa"},
    "DK": {"name": "Dänemark", "alpha3": "DNK", "region": "Europa"},
    "NO": {"name": "Norwegen", "alpha3": "NOR", "region": "Europa"},
    "FI": {"name": "Finnland", "alpha3": "FIN", "region": "Europa"},
    "ES": {"name": "Spanien", "alpha3": "ESP", "region": "Europa"},
    "IT": {"name": "Italien", "alpha3": "ITA", "region": "Europa"},
    "PT": {"name": "Portugal", "alpha3": "PRT", "region": "Europa"},
    "BE": {"name": "Belgien", "alpha3": "BEL", "region": "Europa"},
    "AT": {"name": "Österreich", "alpha3": "AUT", "region": "Europa"},
    "IE": {"name": "Irland", "alpha3": "IRL", "region": "Europa"},
    "SG": {"name": "Singapur", "alpha3": "SGP", "region": "Asien-Pazifik"},
    "BR": {"name": "Brasilien", "alpha3": "BRA", "region": "Lateinamerika"},
    "MX": {"name": "Mexiko", "alpha3": "MEX", "region": "Lateinamerika"},
    "ZA": {"name": "Südafrika", "alpha3": "ZAF", "region": "Afrika"},
    "SA": {"name": "Saudi-Arabien", "alpha3": "SAU", "region": "Naher Osten"},
    "IL": {"name": "Israel", "alpha3": "ISR", "region": "Naher Osten"},
    "CA": {"name": "Kanada", "alpha3": "CAN", "region": "Nordamerika"},
    "NZ": {"name": "Neuseeland", "alpha3": "NZL", "region": "Asien-Pazifik"},
    "PL": {"name": "Polen", "alpha3": "POL", "region": "Europa"},
    "CZ": {"name": "Tschechien", "alpha3": "CZE", "region": "Europa"},
    "HU": {"name": "Ungarn", "alpha3": "HUN", "region": "Europa"},
    "RU": {"name": "Russland", "alpha3": "RUS", "region": "Europa"},
    "TR": {"name": "Türkei", "alpha3": "TUR", "region": "Europa"},
    "TH": {"name": "Thailand", "alpha3": "THA", "region": "Asien-Pazifik"},
    "ID": {"name": "Indonesien", "alpha3": "IDN", "region": "Asien-Pazifik"},
    "MY": {"name": "Malaysia", "alpha3": "MYS", "region": "Asien-Pazifik"},
    "PH": {"name": "Philippinen", "alpha3": "PHL", "region": "Asien-Pazifik"},
    "CL": {"name": "Chile", "alpha3": "CHL", "region": "Lateinamerika"},
    "CO": {"name": "Kolumbien", "alpha3": "COL", "region": "Lateinamerika"},
    "PE": {"name": "Peru", "alpha3": "PER", "region": "Lateinamerika"},
    "AR": {"name": "Argentinien", "alpha3": "ARG", "region": "Lateinamerika"},
}

# Währungs-Mapping: ISO-Code → Details
CURRENCY_MAPPING = {
    "USD": {"name": "US-Dollar", "symbol": "$", "region": "Nordamerika"},
    "EUR": {"name": "Euro", "symbol": "€", "region": "Europa"},
    "GBP": {"name": "Britisches Pfund", "symbol": "£", "region": "Europa"},
    "JPY": {"name": "Japanischer Yen", "symbol": "¥", "region": "Asien-Pazifik"},
    "CHF": {"name": "Schweizer Franken", "symbol": "CHF", "region": "Europa"},
    "CNY": {"name": "Chinesischer Yuan", "symbol": "¥", "region": "Asien-Pazifik"},
    "HKD": {"name": "Hongkong-Dollar", "symbol": "HK$", "region": "Asien-Pazifik"},
    "KRW": {"name": "Südkoreanischer Won", "symbol": "₩", "region": "Asien-Pazifik"},
    "TWD": {"name": "Neuer Taiwan-Dollar", "symbol": "NT$", "region": "Asien-Pazifik"},
    "INR": {"name": "Indische Rupie", "symbol": "₹", "region": "Asien-Pazifik"},
    "AUD": {"name": "Australischer Dollar", "symbol": "A$", "region": "Asien-Pazifik"},
    "CAD": {"name": "Kanadischer Dollar", "symbol": "C$", "region": "Nordamerika"},
    "SEK": {"name": "Schwedische Krone", "symbol": "kr", "region": "Europa"},
    "NOK": {"name": "Norwegische Krone", "symbol": "kr", "region": "Europa"},
    "DKK": {"name": "Dänische Krone", "symbol": "kr", "region": "Europa"},
    "BRL": {"name": "Brasilianischer Real", "symbol": "R$", "region": "Lateinamerika"},
    "MXN": {"name": "Mexikanischer Peso", "symbol": "$", "region": "Lateinamerika"},
    "ZAR": {"name": "Südafrikanischer Rand", "symbol": "R", "region": "Afrika"},
    "SGD": {"name": "Singapur-Dollar", "symbol": "S$", "region": "Asien-Pazifik"},
    "PLN": {"name": "Polnischer Zloty", "symbol": "zł", "region": "Europa"},
    "TRY": {"name": "Türkische Lira", "symbol": "₺", "region": "Europa"},
    "SAR": {"name": "Saudi-Rial", "symbol": "﷼", "region": "Naher Osten"},
    "ILS": {"name": "Israelischer Schekel", "symbol": "₪", "region": "Naher Osten"},
    "NZD": {"name": "Neuseeland-Dollar", "symbol": "NZ$", "region": "Asien-Pazifik"},
}

# Land → Primärwährung
COUNTRY_TO_CURRENCY = {
    "US": "USD", "GB": "GBP", "DE": "EUR", "FR": "EUR", "JP": "JPY",
    "CN": "CNY", "HK": "HKD", "KR": "KRW", "TW": "TWD", "IN": "INR",
    "AU": "AUD", "CH": "CHF", "NL": "EUR", "SE": "SEK", "DK": "DKK",
    "NO": "NOK", "FI": "EUR", "ES": "EUR", "IT": "EUR", "PT": "EUR",
    "BE": "EUR", "AT": "EUR", "IE": "EUR", "SG": "SGD", "BR": "BRL",
    "MX": "MXN", "ZA": "ZAR", "SA": "SAR", "IL": "ILS", "CA": "CAD",
    "NZ": "NZD", "PL": "PLN", "CZ": "EUR", "HU": "EUR", "RU": "RUB",
    "TR": "TRY",
}

# Bekannte Benchmark-Indizes
BENCHMARK_INDICES = {
    "MSCI World": {"ticker_yf": "URTH", "ticker_bbg": "MXWO Index"},
    "S&P 500": {"ticker_yf": "^GSPC", "ticker_bbg": "SPX Index"},
    "EURO STOXX 600": {"ticker_yf": "^STOXX", "ticker_bbg": "SXXP Index"},
    "DAX": {"ticker_yf": "^GDAXI", "ticker_bbg": "DAX Index"},
    "NASDAQ 100": {"ticker_yf": "^NDX", "ticker_bbg": "NDX Index"},
    "FTSE 100": {"ticker_yf": "^FTSE", "ticker_bbg": "UKX Index"},
    "Nikkei 225": {"ticker_yf": "^N225", "ticker_bbg": "NKY Index"},
    "MSCI Emerging Markets": {"ticker_yf": "EEM", "ticker_bbg": "MXEF Index"},
    "MSCI Europe": {"ticker_yf": "IEUR", "ticker_bbg": "MXEU Index"},
}

# Bekannte Aktien → (country, currency, gics_sector) für schnelle ETF-Holdings-Anreicherung
# ohne API-Calls. Deckt die häufigsten ETF-Bestandteile ab.
STOCK_METADATA: dict[str, dict] = {
    # US Tech / Growth
    "AAPL":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "MSFT":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "NVDA":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "AMZN":      {"country": "US", "currency": "USD", "gics_sector": 25},
    "GOOGL":     {"country": "US", "currency": "USD", "gics_sector": 50},
    "GOOG":      {"country": "US", "currency": "USD", "gics_sector": 50},
    "META":      {"country": "US", "currency": "USD", "gics_sector": 50},
    "TSLA":      {"country": "US", "currency": "USD", "gics_sector": 25},
    "AVGO":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "LLY":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "ORCL":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "AMD":       {"country": "US", "currency": "USD", "gics_sector": 45},
    "QCOM":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "INTC":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "TXN":       {"country": "US", "currency": "USD", "gics_sector": 45},
    "CRM":       {"country": "US", "currency": "USD", "gics_sector": 45},
    "ADBE":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "NOW":       {"country": "US", "currency": "USD", "gics_sector": 45},
    "INTU":      {"country": "US", "currency": "USD", "gics_sector": 45},
    "NFLX":      {"country": "US", "currency": "USD", "gics_sector": 50},
    "PLTR":      {"country": "US", "currency": "USD", "gics_sector": 45},
    # US Finance / Health / Consumer
    "JPM":       {"country": "US", "currency": "USD", "gics_sector": 40},
    "V":         {"country": "US", "currency": "USD", "gics_sector": 40},
    "MA":        {"country": "US", "currency": "USD", "gics_sector": 40},
    "BAC":       {"country": "US", "currency": "USD", "gics_sector": 40},
    "GS":        {"country": "US", "currency": "USD", "gics_sector": 40},
    "WFC":       {"country": "US", "currency": "USD", "gics_sector": 40},
    "UNH":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "JNJ":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "ABT":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "MRK":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "PFE":       {"country": "US", "currency": "USD", "gics_sector": 35},
    "WMT":       {"country": "US", "currency": "USD", "gics_sector": 30},
    "PG":        {"country": "US", "currency": "USD", "gics_sector": 30},
    "KO":        {"country": "US", "currency": "USD", "gics_sector": 30},
    "COST":      {"country": "US", "currency": "USD", "gics_sector": 30},
    "HD":        {"country": "US", "currency": "USD", "gics_sector": 25},
    "NKE":       {"country": "US", "currency": "USD", "gics_sector": 25},
    "MCD":       {"country": "US", "currency": "USD", "gics_sector": 25},
    "XOM":       {"country": "US", "currency": "USD", "gics_sector": 10},
    "CVX":       {"country": "US", "currency": "USD", "gics_sector": 10},
    "CAT":       {"country": "US", "currency": "USD", "gics_sector": 20},
    "DE":        {"country": "US", "currency": "USD", "gics_sector": 20},
    "RTX":       {"country": "US", "currency": "USD", "gics_sector": 20},
    "BA":        {"country": "US", "currency": "USD", "gics_sector": 20},
    "NEE":       {"country": "US", "currency": "USD", "gics_sector": 55},
    "AMT":       {"country": "US", "currency": "USD", "gics_sector": 60},
    "PLD":       {"country": "US", "currency": "USD", "gics_sector": 60},
    # Europa
    "SAP":       {"country": "DE", "currency": "EUR", "gics_sector": 45},
    "SAP.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 45},
    "ASML":      {"country": "NL", "currency": "EUR", "gics_sector": 45},
    "RHM.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 20},
    "SIE.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 20},
    "ALV.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 40},
    "DTE.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 50},
    "BMW.DE":    {"country": "DE", "currency": "EUR", "gics_sector": 25},
    "VOW3.DE":   {"country": "DE", "currency": "EUR", "gics_sector": 25},
    "MC.PA":     {"country": "FR", "currency": "EUR", "gics_sector": 25},
    "TTE.PA":    {"country": "FR", "currency": "EUR", "gics_sector": 10},
    "SAN.PA":    {"country": "FR", "currency": "EUR", "gics_sector": 35},
    "BNP.PA":    {"country": "FR", "currency": "EUR", "gics_sector": 40},
    "AIR.PA":    {"country": "FR", "currency": "EUR", "gics_sector": 20},
    "AZN":       {"country": "GB", "currency": "GBP", "gics_sector": 35},
    "SHEL":      {"country": "GB", "currency": "GBP", "gics_sector": 10},
    "HSBA.L":    {"country": "GB", "currency": "GBP", "gics_sector": 40},
    "BP.L":      {"country": "GB", "currency": "GBP", "gics_sector": 10},
    "ULVR.L":    {"country": "GB", "currency": "GBP", "gics_sector": 30},
    "NESN.SW":   {"country": "CH", "currency": "CHF", "gics_sector": 30},
    "ROG.SW":    {"country": "CH", "currency": "CHF", "gics_sector": 35},
    "NOVN.SW":   {"country": "CH", "currency": "CHF", "gics_sector": 35},
    "NOVO-B.CO": {"country": "DK", "currency": "DKK", "gics_sector": 35},
    "NESTE.HE":  {"country": "FI", "currency": "EUR", "gics_sector": 10},
    "ERICB.ST":  {"country": "SE", "currency": "SEK", "gics_sector": 45},
    "VOLV-B.ST": {"country": "SE", "currency": "SEK", "gics_sector": 20},
    # Asien-Pazifik
    "TSM":       {"country": "TW", "currency": "TWD", "gics_sector": 45},
    "2330.TW":   {"country": "TW", "currency": "TWD", "gics_sector": 45},
    "005930.KS": {"country": "KR", "currency": "KRW", "gics_sector": 45},
    "000660.KS": {"country": "KR", "currency": "KRW", "gics_sector": 45},
    "7203.T":    {"country": "JP", "currency": "JPY", "gics_sector": 25},
    "6758.T":    {"country": "JP", "currency": "JPY", "gics_sector": 45},
    "6861.T":    {"country": "JP", "currency": "JPY", "gics_sector": 45},
    "7974.T":    {"country": "JP", "currency": "JPY", "gics_sector": 25},
    "BHP.AX":    {"country": "AU", "currency": "AUD", "gics_sector": 15},
    "CBA.AX":    {"country": "AU", "currency": "AUD", "gics_sector": 40},
    "INFY":      {"country": "IN", "currency": "USD", "gics_sector": 45},
    "RELIANCE.NS": {"country": "IN", "currency": "INR", "gics_sector": 10},
    "ICICIBANK.NS": {"country": "IN", "currency": "INR", "gics_sector": 40},
    # Emerging Markets
    "TCEHY":     {"country": "CN", "currency": "HKD", "gics_sector": 50},
    "BABA":      {"country": "CN", "currency": "HKD", "gics_sector": 25},
    "PDD":       {"country": "CN", "currency": "USD", "gics_sector": 25},
    "BIDU":      {"country": "CN", "currency": "USD", "gics_sector": 50},
    "1398.HK":   {"country": "CN", "currency": "HKD", "gics_sector": 40},
    "0700.HK":   {"country": "CN", "currency": "HKD", "gics_sector": 50},
    "VALE":      {"country": "BR", "currency": "USD", "gics_sector": 15},
    "ITUB":      {"country": "BR", "currency": "USD", "gics_sector": 40},
    "AMX":       {"country": "MX", "currency": "USD", "gics_sector": 50},
    "BBCA.JK":   {"country": "ID", "currency": "IDR", "gics_sector": 40},
    "PTT.BK":    {"country": "TH", "currency": "THB", "gics_sector": 10},
}

# yfinance Sektor-Keys → GICS-Code
YFINANCE_SECTOR_TO_GICS: dict[str, int] = {
    "realestate":           60,
    "consumer_cyclical":    25,
    "basic_materials":      15,
    "consumer_defensive":   30,
    "technology":           45,
    "communication_services": 50,
    "financial_services":   40,
    "utilities":            55,
    "industrials":          20,
    "energy":               10,
    "healthcare":           35,
}

# Schwellwerte für Warnungen
CONCENTRATION_WARNING_THRESHOLD = 0.10  # 10% effektive Gewichtung → Warnung
SECTOR_OVERWEIGHT_THRESHOLD = 0.15      # 15pp über Benchmark → Warnung
COUNTRY_OVERWEIGHT_THRESHOLD = 0.20     # 20pp über Benchmark → Warnung
MIN_HISTORY_DAYS = 252                  # Mindestens ~1 Jahr für Vola-Berechnung
EWMA_LAMBDA = 0.94                      # RiskMetrics Standard Decay-Faktor

# =============================================================================
# Statische ETF-Länderdaten (Stand: Anfang 2025)
# Quelle: MSCI/FTSE Factsheets, ETF-Provider-Websites
# Werte werden intern auf Summe 1.0 normalisiert.
# =============================================================================

_ETF_DISTRIBUTIONS: dict[str, dict[str, float]] = {
    "msci_world": {
        "US": 0.682, "JP": 0.058, "GB": 0.039, "FR": 0.034, "CA": 0.034,
        "CH": 0.024, "DE": 0.024, "AU": 0.019, "NL": 0.015, "SE": 0.015,
        "DK": 0.010, "IT": 0.008, "ES": 0.008, "HK": 0.006, "NO": 0.004,
        "SG": 0.004, "FI": 0.004, "IE": 0.003, "BE": 0.003, "NZ": 0.002,
        "IL": 0.002, "AT": 0.001, "PT": 0.001,
    },
    "sp500": {"US": 1.000},
    "nasdaq100": {"US": 0.985, "NL": 0.010, "TW": 0.005},
    "msci_em": {
        "IN": 0.185, "TW": 0.175, "CN": 0.165, "KR": 0.120, "BR": 0.055,
        "SA": 0.040, "ZA": 0.035, "MX": 0.020, "TH": 0.018, "MY": 0.016,
        "ID": 0.015, "PL": 0.009, "PH": 0.008, "AR": 0.007, "AE": 0.006,
        "KW": 0.005, "CO": 0.004, "PE": 0.003, "CL": 0.003, "HU": 0.002,
        "CZ": 0.002, "QA": 0.003,
    },
    "msci_europe": {
        "GB": 0.225, "FR": 0.185, "CH": 0.170, "DE": 0.145, "NL": 0.070,
        "SE": 0.060, "DK": 0.050, "IT": 0.040, "ES": 0.030, "BE": 0.018,
        "FI": 0.015, "IE": 0.012, "NO": 0.012, "AT": 0.008, "PL": 0.005,
        "PT": 0.004, "LU": 0.003, "GR": 0.002,
    },
    "stoxx600": {
        "GB": 0.215, "FR": 0.170, "CH": 0.135, "DE": 0.130, "NL": 0.065,
        "SE": 0.055, "DK": 0.045, "IT": 0.040, "ES": 0.040, "BE": 0.020,
        "FI": 0.020, "IE": 0.015, "NO": 0.015, "AT": 0.012, "PL": 0.008,
        "PT": 0.005, "LU": 0.004, "GR": 0.003, "HU": 0.002, "CZ": 0.001,
    },
    "eurostoxx50": {
        "FR": 0.340, "DE": 0.255, "NL": 0.120, "ES": 0.085, "IT": 0.072,
        "BE": 0.040, "FI": 0.030, "IE": 0.025, "AT": 0.012, "LU": 0.010,
        "PT": 0.006, "GR": 0.005,
    },
    "dax": {"DE": 1.000},
    "all_world": {
        "US": 0.612, "JP": 0.060, "GB": 0.040, "CN": 0.030, "FR": 0.030,
        "CA": 0.030, "CH": 0.020, "DE": 0.020, "AU": 0.020, "IN": 0.020,
        "TW": 0.020, "KR": 0.015, "NL": 0.010, "SE": 0.010, "DK": 0.008,
        "IT": 0.007, "SA": 0.007, "BR": 0.006, "ZA": 0.005, "HK": 0.005,
        "SG": 0.005, "ES": 0.007, "MX": 0.003, "FI": 0.003, "NO": 0.003,
        "BE": 0.003, "IE": 0.003, "PL": 0.003, "AT": 0.001,
    },
    "msci_acwi": {
        "US": 0.640, "JP": 0.055, "GB": 0.038, "CN": 0.028, "FR": 0.032,
        "CA": 0.032, "CH": 0.022, "DE": 0.022, "AU": 0.018, "IN": 0.018,
        "TW": 0.018, "KR": 0.012, "NL": 0.014, "SE": 0.014, "DK": 0.010,
        "IT": 0.008, "SA": 0.004, "BR": 0.005, "ZA": 0.004, "HK": 0.006,
        "SG": 0.004, "FI": 0.004, "NO": 0.004, "BE": 0.003, "ES": 0.008,
        "IE": 0.003, "AT": 0.001,
    },
    "msci_world_sc": {
        "US": 0.570, "JP": 0.100, "GB": 0.065, "CA": 0.050, "AU": 0.040,
        "SE": 0.025, "DE": 0.020, "CH": 0.018, "FR": 0.018, "IT": 0.015,
        "DK": 0.012, "NL": 0.010, "NO": 0.008, "FI": 0.008, "ES": 0.008,
        "HK": 0.007, "SG": 0.006, "NZ": 0.005, "AT": 0.004, "BE": 0.004,
        "IE": 0.003, "PT": 0.002, "IL": 0.002,
    },
}

# Ticker (Großschreibung, mit und ohne Börsensuffix) → ETF-Kategorie
ETF_TICKER_TO_CANONICAL: dict[str, str] = {
    # ── MSCI World ───────────────────────────────────────────────────────────
    "EUNL": "msci_world", "EUNL.DE": "msci_world", "EUNL.AS": "msci_world",
    "IWDA": "msci_world", "IWDA.L": "msci_world",  "IWDA.AS": "msci_world",
    "XDWD": "msci_world", "XDWD.DE": "msci_world", "XDWD.AS": "msci_world",
    "LCUW": "msci_world", "LCUW.L": "msci_world",
    "SADM": "msci_world", "SADM.DE": "msci_world",
    "IQQW": "msci_world", "IQQW.DE": "msci_world",
    "SWRD": "msci_world", "SWRD.L": "msci_world",
    "MDWD": "msci_world", "MDWD.L": "msci_world",
    "URTH": "msci_world",
    "XWLD": "msci_world", "XWLD.DE": "msci_world",
    "HMWD": "msci_world", "HMWD.L": "msci_world",
    "IUWL": "msci_world", "IUWL.L": "msci_world",
    "DBXW": "msci_world", "DBXW.DE": "msci_world",
    "WDSP": "msci_world", "WDSP.L": "msci_world",
    "MWRD": "msci_world",
    # ── S&P 500 ──────────────────────────────────────────────────────────────
    "SPY": "sp500", "IVV": "sp500", "VOO": "sp500", "SPLG": "sp500",
    "CSPX": "sp500", "CSPX.L": "sp500",
    "VUSA": "sp500", "VUSA.L": "sp500", "VUSA.AS": "sp500",
    "SXR8": "sp500", "SXR8.DE": "sp500",
    "SPXS": "sp500", "SPXS.DE": "sp500",
    "SPX5": "sp500", "SPX5.DE": "sp500",
    "IUSA": "sp500", "IUSA.L": "sp500",
    "CSP1": "sp500", "CSP1.L": "sp500",
    "VUAA": "sp500", "VUAA.L": "sp500", "VUAA.AS": "sp500",
    "XSPU": "sp500", "XSPU.L": "sp500",
    "IUSP": "sp500",
    # ── NASDAQ 100 ───────────────────────────────────────────────────────────
    "QQQ": "nasdaq100", "QQQM": "nasdaq100",
    "CNDX": "nasdaq100", "CNDX.L": "nasdaq100",
    "EQQQ": "nasdaq100", "EQQQ.L": "nasdaq100",
    "XNAQ": "nasdaq100", "XNAQ.DE": "nasdaq100",
    "IQQQ": "nasdaq100", "IQQQ.DE": "nasdaq100",
    "NASD": "nasdaq100", "NASD.L": "nasdaq100",
    "CSNDX": "nasdaq100",
    # ── DAX ──────────────────────────────────────────────────────────────────
    "DAXEX": "dax", "DAXEX.DE": "dax",
    "EXS1": "dax",  "EXS1.DE": "dax",
    "1C22": "dax",
    "DBXD": "dax",  "DBXD.DE": "dax",
    "TDXP": "dax",  "TDXP.L": "dax",
    "XDDX": "dax",
    # ── STOXX Europe 600 ─────────────────────────────────────────────────────
    "EXSA": "stoxx600", "EXSA.DE": "stoxx600",
    "MEUD": "stoxx600", "MEUD.L": "stoxx600",
    "IQQY": "stoxx600", "IQQY.DE": "stoxx600",
    "XESC": "stoxx600", "STOXX": "stoxx600",
    # ── EURO STOXX 50 ────────────────────────────────────────────────────────
    "EUE":  "eurostoxx50", "EUE.L":  "eurostoxx50",
    "EXW1": "eurostoxx50", "EXW1.DE": "eurostoxx50",
    "DBBX": "eurostoxx50", "DBBX.DE": "eurostoxx50",
    "DBXE": "eurostoxx50", "DBXE.DE": "eurostoxx50",
    "EUN2": "eurostoxx50", "EUN2.DE": "eurostoxx50",
    "SX5EEX": "eurostoxx50",
    # ── MSCI Emerging Markets ────────────────────────────────────────────────
    "EEM":  "msci_em",
    "EIMI": "msci_em", "EIMI.L": "msci_em", "EIMI.AS": "msci_em",
    "IQQE": "msci_em", "IQQE.DE": "msci_em",
    "AEME": "msci_em", "AEME.L": "msci_em",
    "SEMA": "msci_em", "SEMA.L": "msci_em",
    "XMME": "msci_em", "XMME.DE": "msci_em",
    "VFEM": "msci_em", "VFEM.L": "msci_em",
    "AMEM": "msci_em",
    # ── MSCI Europe ──────────────────────────────────────────────────────────
    "IEUR": "msci_europe",
    "IMEU": "msci_europe", "IMEU.AS": "msci_europe", "IMEU.L": "msci_europe",
    "EXIB": "msci_europe",
    "IMEA": "msci_europe",
    "SMEA": "msci_europe",
    # ── Vanguard FTSE All-World ───────────────────────────────────────────────
    "VWRL": "all_world", "VWRL.L": "all_world", "VWRL.AS": "all_world",
    "VWRA": "all_world", "VWRA.L": "all_world",
    "VWCE": "all_world", "VWCE.DE": "all_world", "VWCE.AS": "all_world",
    "FWRA": "all_world", "FWRA.L": "all_world",
    "FWRG": "all_world", "FWRG.L": "all_world",
    # ── MSCI ACWI ────────────────────────────────────────────────────────────
    "ACWI": "msci_acwi",
    "SSAC": "msci_acwi", "SSAC.L": "msci_acwi",
    "ISAC": "msci_acwi", "ISAC.L": "msci_acwi",
    "SPYW": "msci_acwi",
    # ── MSCI World Small Cap ─────────────────────────────────────────────────
    "IUSN": "msci_world_sc", "IUSN.L": "msci_world_sc", "IUSN.DE": "msci_world_sc",
    "WSML": "msci_world_sc", "WSML.L": "msci_world_sc",
}


def get_etf_country_distribution(ticker: str) -> dict[str, float]:
    """
    Gibt die bekannte Länderverteilung für einen ETF-Ticker zurück.
    Normalisiert automatisch auf Summe = 1.0.
    Returns {} wenn der Ticker nicht bekannt ist.
    """
    canonical = ETF_TICKER_TO_CANONICAL.get(ticker.upper(), "")
    if not canonical:
        return {}
    raw = _ETF_DISTRIBUTIONS.get(canonical, {})
    if not raw:
        return {}
    total = sum(raw.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in raw.items()}
