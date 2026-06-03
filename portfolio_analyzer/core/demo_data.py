"""
Demo-Daten: Simuliertes Portfolio mit realistischen Daten zum Testen.

Ermöglicht das Testen der gesamten App ohne Bloomberg oder Yahoo Finance.
Enthält ein Beispielportfolio mit Einzelaktien und ETFs, synthetische
historische Renditen und ETF-Holdings.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from core.portfolio import Portfolio, Position, AssetType, Holding
from core.data_provider import DataProvider
from utils.constants import GICS_SECTORS


# ─────────────────────────────────────────────────────
# Beispiel-Portfolio
# ─────────────────────────────────────────────────────

DEMO_POSITIONS = [
    # ETFs
    {
        "ticker": "IWDA",
        "name": "iShares Core MSCI World UCITS ETF",
        "isin": "IE00B4L5Y983",
        "market_value": 25000,
        "asset_type": "ETF",
        "country": "IE",
        "currency": "USD",
        "gics_sector": 0,
    },
    {
        "ticker": "CSPX",
        "name": "iShares Core S&P 500 UCITS ETF",
        "isin": "IE00B5BMR087",
        "market_value": 15000,
        "asset_type": "ETF",
        "country": "IE",
        "currency": "USD",
        "gics_sector": 0,
    },
    {
        "ticker": "EIMI",
        "name": "iShares Core MSCI EM IMI UCITS ETF",
        "isin": "IE00BKM4GZ66",
        "market_value": 5000,
        "asset_type": "ETF",
        "country": "IE",
        "currency": "USD",
        "gics_sector": 0,
    },
    # Rohstoff ETCs
    {
        "ticker": "PHAU",
        "name": "WisdomTree Physical Gold ETC",
        "isin": "JE00B1VS3770",
        "market_value": 4000,
        "asset_type": "ETF",
        "country": "IE",
        "currency": "USD",
        "gics_sector": 0,
    },
    {
        "ticker": "PHAG",
        "name": "WisdomTree Physical Silver ETC",
        "isin": "JE00B1VS3333",
        "market_value": 2000,
        "asset_type": "ETF",
        "country": "IE",
        "currency": "USD",
        "gics_sector": 0,
    },
    # Krypto ETP
    {
        "ticker": "BTCE",
        "name": "ETC Group Physical Bitcoin ETP",
        "isin": "DE000A27Z304",
        "market_value": 3000,
        "asset_type": "ETF",
        "country": "DE",
        "currency": "USD",
        "gics_sector": 0,
    },
    # Einzelaktien
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "isin": "US0378331005",
        "market_value": 8000,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 45,
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corp.",
        "isin": "US5949181045",
        "market_value": 7000,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 45,
    },
    {
        "ticker": "NVDA",
        "name": "NVIDIA Corp.",
        "isin": "US67066G1040",
        "market_value": 6000,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 45,
    },
    {
        "ticker": "PLTR",
        "name": "Palantir Technologies Inc.",
        "isin": "US69608A1088",
        "market_value": 4000,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 45,
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "isin": "US02079K3059",
        "market_value": 5000,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 50,
    },
    {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "isin": "US0231351067",
        "market_value": 4500,
        "asset_type": "STOCK",
        "country": "US",
        "currency": "USD",
        "gics_sector": 25,
    },
    {
        "ticker": "RHM.DE",
        "name": "Rheinmetall AG",
        "isin": "DE0007030009",
        "market_value": 3500,
        "asset_type": "STOCK",
        "country": "DE",
        "currency": "EUR",
        "gics_sector": 20,
    },
    {
        "ticker": "SAP",
        "name": "SAP SE",
        "isin": "DE0007164600",
        "market_value": 3000,
        "asset_type": "STOCK",
        "country": "DE",
        "currency": "EUR",
        "gics_sector": 45,
    },
    {
        "ticker": "NOVO-B.CO",
        "name": "Novo Nordisk A/S",
        "isin": "DK0062498333",
        "market_value": 2500,
        "asset_type": "STOCK",
        "country": "DK",
        "currency": "DKK",
        "gics_sector": 35,
    },
    {
        "ticker": "ASML",
        "name": "ASML Holding NV",
        "isin": "NL0010273215",
        "market_value": 3000,
        "asset_type": "STOCK",
        "country": "NL",
        "currency": "EUR",
        "gics_sector": 45,
    },
]


# ─────────────────────────────────────────────────────
# ETF-Holdings (vereinfacht, Top-20 pro ETF)
# ─────────────────────────────────────────────────────

DEMO_ETF_HOLDINGS = {
    "IWDA": [
        {"ticker": "AAPL", "name": "Apple Inc.", "weight": 0.048, "country": "US", "gics_sector": 45},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "weight": 0.043, "country": "US", "gics_sector": 45},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "weight": 0.040, "country": "US", "gics_sector": 45},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "weight": 0.032, "country": "US", "gics_sector": 25},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "weight": 0.025, "country": "US", "gics_sector": 50},
        {"ticker": "META", "name": "Meta Platforms Inc.", "weight": 0.020, "country": "US", "gics_sector": 50},
        {"ticker": "TSLA", "name": "Tesla Inc.", "weight": 0.015, "country": "US", "gics_sector": 25},
        {"ticker": "LLY", "name": "Eli Lilly and Co.", "weight": 0.014, "country": "US", "gics_sector": 35},
        {"ticker": "AVGO", "name": "Broadcom Inc.", "weight": 0.013, "country": "US", "gics_sector": 45},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "weight": 0.012, "country": "US", "gics_sector": 40},
        {"ticker": "UNH", "name": "UnitedHealth Group", "weight": 0.011, "country": "US", "gics_sector": 35},
        {"ticker": "V", "name": "Visa Inc.", "weight": 0.010, "country": "US", "gics_sector": 40},
        {"ticker": "NOVO-B.CO", "name": "Novo Nordisk A/S", "weight": 0.009, "country": "DK", "gics_sector": 35},
        {"ticker": "ASML", "name": "ASML Holding NV", "weight": 0.008, "country": "NL", "gics_sector": 45},
        {"ticker": "SAP", "name": "SAP SE", "weight": 0.006, "country": "DE", "gics_sector": 45},
        {"ticker": "NESN.SW", "name": "Nestlé SA", "weight": 0.006, "country": "CH", "gics_sector": 30},
        {"ticker": "ROG.SW", "name": "Roche Holding AG", "weight": 0.005, "country": "CH", "gics_sector": 35},
        {"ticker": "7203.T", "name": "Toyota Motor Corp.", "weight": 0.005, "country": "JP", "gics_sector": 25},
        {"ticker": "SHEL", "name": "Shell plc", "weight": 0.004, "country": "GB", "gics_sector": 10},
        {"ticker": "AZN", "name": "AstraZeneca plc", "weight": 0.004, "country": "GB", "gics_sector": 35},
    ],
    "CSPX": [
        {"ticker": "AAPL", "name": "Apple Inc.", "weight": 0.070, "country": "US", "gics_sector": 45},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "weight": 0.065, "country": "US", "gics_sector": 45},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "weight": 0.060, "country": "US", "gics_sector": 45},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "weight": 0.050, "country": "US", "gics_sector": 25},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "weight": 0.038, "country": "US", "gics_sector": 50},
        {"ticker": "META", "name": "Meta Platforms Inc.", "weight": 0.030, "country": "US", "gics_sector": 50},
        {"ticker": "TSLA", "name": "Tesla Inc.", "weight": 0.022, "country": "US", "gics_sector": 25},
        {"ticker": "LLY", "name": "Eli Lilly and Co.", "weight": 0.020, "country": "US", "gics_sector": 35},
        {"ticker": "AVGO", "name": "Broadcom Inc.", "weight": 0.019, "country": "US", "gics_sector": 45},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "weight": 0.018, "country": "US", "gics_sector": 40},
        {"ticker": "UNH", "name": "UnitedHealth Group", "weight": 0.016, "country": "US", "gics_sector": 35},
        {"ticker": "V", "name": "Visa Inc.", "weight": 0.015, "country": "US", "gics_sector": 40},
        {"ticker": "MA", "name": "Mastercard Inc.", "weight": 0.012, "country": "US", "gics_sector": 40},
        {"ticker": "COST", "name": "Costco Wholesale", "weight": 0.011, "country": "US", "gics_sector": 30},
        {"ticker": "HD", "name": "The Home Depot", "weight": 0.010, "country": "US", "gics_sector": 25},
        {"ticker": "NFLX", "name": "Netflix Inc.", "weight": 0.009, "country": "US", "gics_sector": 50},
        {"ticker": "CRM", "name": "Salesforce Inc.", "weight": 0.008, "country": "US", "gics_sector": 45},
        {"ticker": "ADBE", "name": "Adobe Inc.", "weight": 0.007, "country": "US", "gics_sector": 45},
        {"ticker": "PG", "name": "Procter & Gamble", "weight": 0.007, "country": "US", "gics_sector": 30},
        {"ticker": "KO", "name": "The Coca-Cola Co.", "weight": 0.006, "country": "US", "gics_sector": 30},
    ],
    "EIMI": [
        {"ticker": "TSM", "name": "Taiwan Semiconductor", "weight": 0.080, "country": "TW", "gics_sector": 45},
        {"ticker": "TCEHY", "name": "Tencent Holdings", "weight": 0.045, "country": "CN", "gics_sector": 50},
        {"ticker": "BABA", "name": "Alibaba Group", "weight": 0.030, "country": "CN", "gics_sector": 25},
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "weight": 0.020, "country": "IN", "gics_sector": 10},
        {"ticker": "005930.KS", "name": "Samsung Electronics", "weight": 0.040, "country": "KR", "gics_sector": 45},
        {"ticker": "VALE", "name": "Vale SA", "weight": 0.015, "country": "BR", "gics_sector": 15},
        {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd", "weight": 0.012, "country": "IN", "gics_sector": 40},
        {"ticker": "1398.HK", "name": "ICBC", "weight": 0.010, "country": "CN", "gics_sector": 40},
        {"ticker": "MEITUAN", "name": "Meituan", "weight": 0.015, "country": "CN", "gics_sector": 25},
        {"ticker": "2330.TW", "name": "TSMC (TW)", "weight": 0.010, "country": "TW", "gics_sector": 45},
        {"ticker": "INFY", "name": "Infosys Ltd", "weight": 0.010, "country": "IN", "gics_sector": 45},
        {"ticker": "PDD", "name": "PDD Holdings", "weight": 0.012, "country": "CN", "gics_sector": 25},
        {"ticker": "AMX", "name": "América Móvil", "weight": 0.008, "country": "MX", "gics_sector": 50},
        {"ticker": "BBCA.JK", "name": "Bank Central Asia", "weight": 0.008, "country": "ID", "gics_sector": 40},
        {"ticker": "PTT.BK", "name": "PTT PCL", "weight": 0.005, "country": "TH", "gics_sector": 10},
    ],
}


# ─────────────────────────────────────────────────────
# Synthetische Renditen generieren
# ─────────────────────────────────────────────────────

# Realistische annualisierte Parameter pro Aktie
DEMO_RETURN_PARAMS = {
    "IWDA":     {"mu": 0.10, "sigma": 0.14},
    "CSPX":     {"mu": 0.12, "sigma": 0.16},
    "EIMI":     {"mu": 0.06, "sigma": 0.20},
    "PHAU":     {"mu": 0.08, "sigma": 0.15},   # Gold — niedrige Vola, defensiv
    "PHAG":     {"mu": 0.06, "sigma": 0.25},   # Silber — höhere Vola als Gold
    "BTCE":     {"mu": 0.40, "sigma": 0.70},   # Bitcoin — sehr hohe Vola
    "AAPL":     {"mu": 0.15, "sigma": 0.28},
    "MSFT":     {"mu": 0.18, "sigma": 0.26},
    "NVDA":     {"mu": 0.35, "sigma": 0.50},
    "PLTR":     {"mu": 0.25, "sigma": 0.55},
    "GOOGL":    {"mu": 0.14, "sigma": 0.28},
    "AMZN":     {"mu": 0.16, "sigma": 0.32},
    "RHM.DE":   {"mu": 0.30, "sigma": 0.35},
    "SAP":      {"mu": 0.12, "sigma": 0.25},
    "NOVO-B.CO": {"mu": 0.08, "sigma": 0.30},
    "ASML":     {"mu": 0.15, "sigma": 0.35},
}

# Korrelationsstruktur (vereinfacht — Blöcke)
# US-Tech hoch korreliert, europäische Aktien weniger, EM eigene Dynamik
CORRELATION_BLOCKS = {
    "us_tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "PLTR"],
    "eu": ["RHM.DE", "SAP", "NOVO-B.CO", "ASML"],
    "etf_broad": ["IWDA", "CSPX"],
    "em": ["EIMI"],
    "commodities": ["PHAU", "PHAG"],   # Gold & Silber — niedrige Korrelation zu Aktien
    "crypto": ["BTCE"],                # Bitcoin — eigene Dynamik
}


def _generate_correlated_returns(
    tickers: list[str],
    n_days: int = 504,  # ~2 Jahre
    seed: int = 42,
) -> pd.DataFrame:
    """Synthetische korrelierte tägliche Renditen generieren."""
    np.random.seed(seed)
    n = len(tickers)

    # Korrelationsmatrix aufbauen
    corr = np.eye(n)

    def _get_block(ticker):
        for block_name, members in CORRELATION_BLOCKS.items():
            if ticker in members:
                return block_name
        return ticker  # Eigener Block

    for i in range(n):
        for j in range(i + 1, n):
            block_i = _get_block(tickers[i])
            block_j = _get_block(tickers[j])

            if block_i == block_j:
                corr[i, j] = corr[j, i] = np.random.uniform(0.6, 0.85)
            elif {block_i, block_j} & {"etf_broad"}:
                # ETFs korrelieren moderat mit allem
                corr[i, j] = corr[j, i] = np.random.uniform(0.5, 0.7)
            elif {block_i, block_j} == {"us_tech", "eu"}:
                corr[i, j] = corr[j, i] = np.random.uniform(0.3, 0.5)
            elif "em" in {block_i, block_j}:
                corr[i, j] = corr[j, i] = np.random.uniform(0.2, 0.4)
            else:
                corr[i, j] = corr[j, i] = np.random.uniform(0.2, 0.5)

    # Sicherstellen, dass die Matrix positiv-definit ist
    eigenvalues, eigenvectors = np.linalg.eigh(corr)
    eigenvalues = np.maximum(eigenvalues, 0.01)
    corr = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
    # Re-normalisieren
    d = np.sqrt(np.diag(corr))
    corr = corr / np.outer(d, d)
    np.fill_diagonal(corr, 1.0)

    # Cholesky-Zerlegung
    L = np.linalg.cholesky(corr)

    # Unkorrelierte Standardnormalverteilte Renditen
    Z = np.random.randn(n_days, n)

    # Korreliert machen
    correlated = Z @ L.T

    # Skalieren auf gewünschte Volatilität und Drift
    daily_returns = np.zeros_like(correlated)
    for i, ticker in enumerate(tickers):
        params = DEMO_RETURN_PARAMS.get(ticker, {"mu": 0.08, "sigma": 0.20})
        daily_mu = params["mu"] / 252
        daily_sigma = params["sigma"] / np.sqrt(252)
        daily_returns[:, i] = daily_mu + daily_sigma * correlated[:, i]

    # Datum-Index
    end_date = datetime.now()
    dates = pd.bdate_range(end=end_date, periods=n_days)

    return pd.DataFrame(daily_returns, index=dates, columns=tickers)


def _generate_prices_from_returns(returns_df: pd.DataFrame, base_price: float = 100.0) -> pd.DataFrame:
    """Aus Renditen synthetische Kurse generieren."""
    prices = base_price * np.exp(returns_df.cumsum())
    return prices


# ─────────────────────────────────────────────────────
# Demo Data Provider
# ─────────────────────────────────────────────────────

class DemoDataProvider(DataProvider):
    """
    Demo-Provider mit synthetischen Daten zum Testen ohne externe APIs.
    """

    def __init__(self):
        self._security_db = {p["ticker"]: p for p in DEMO_POSITIONS}
        self._returns_cache = None
        self._prices_cache = None

    def get_security_info(self, ticker: str) -> dict:
        ticker_upper = ticker.strip().upper()

        # Direkt in DB?
        if ticker_upper in self._security_db:
            info = self._security_db[ticker_upper]
            return {
                "name": info["name"],
                "isin": info["isin"],
                "country": info["country"],
                "currency": info["currency"],
                "gics_sector": info["gics_sector"],
                "asset_type": info["asset_type"],
            }

        # Fallback
        return {
            "name": ticker_upper,
            "isin": "",
            "country": "US",
            "currency": "USD",
            "gics_sector": 0,
            "asset_type": "STOCK",
        }

    def get_etf_holdings(self, ticker: str, top_n: int = 50) -> list[dict]:
        ticker_upper = ticker.strip().upper()
        holdings = DEMO_ETF_HOLDINGS.get(ticker_upper, [])
        return holdings[:top_n]

    def get_historical_prices(self, tickers: list[str], years: int = 2) -> pd.DataFrame:
        if self._prices_cache is None:
            all_tickers = list(DEMO_RETURN_PARAMS.keys())
            returns = _generate_correlated_returns(all_tickers, n_days=years * 252)
            self._returns_cache = returns
            self._prices_cache = _generate_prices_from_returns(returns)

        available = [t for t in tickers if t in self._prices_cache.columns]
        if not available:
            return pd.DataFrame()
        return self._prices_cache[available].copy()

    def get_benchmark_prices(self, benchmark_ticker: str, years: int = 2) -> pd.Series:
        # Synthetische Benchmark-Renditen
        np.random.seed(123)
        n_days = years * 252
        dates = pd.bdate_range(end=datetime.now(), periods=n_days)

        daily_mu = 0.09 / 252
        daily_sigma = 0.15 / np.sqrt(252)
        returns = daily_mu + daily_sigma * np.random.randn(n_days)
        prices = 100 * np.exp(np.cumsum(returns))

        return pd.Series(prices, index=dates, name=benchmark_ticker)

    def is_available(self) -> bool:
        return True


# ─────────────────────────────────────────────────────
# Demo-Portfolio erstellen
# ─────────────────────────────────────────────────────

def create_demo_portfolio() -> Portfolio:
    """Erstellt ein vollständig angereichertes Demo-Portfolio."""
    provider = DemoDataProvider()
    portfolio = Portfolio(name="Demo Portfolio")

    for pos_data in DEMO_POSITIONS:
        pos = Position(
            ticker=pos_data["ticker"],
            name=pos_data["name"],
            isin=pos_data["isin"],
            market_value=pos_data["market_value"],
            currency="EUR",
            asset_type=AssetType.ETF if pos_data["asset_type"] == "ETF" else AssetType.STOCK,
            country=pos_data["country"],
            trade_currency=pos_data["currency"],
            gics_sector=pos_data["gics_sector"],
            gics_sector_name=GICS_SECTORS.get(pos_data["gics_sector"], "Unbekannt"),
        )

        # ETF-Holdings laden
        if pos.is_etf:
            holdings_data = provider.get_etf_holdings(pos.ticker)
            pos.holdings = [
                Holding(
                    ticker=h["ticker"],
                    name=h["name"],
                    weight=h["weight"],
                    country=h["country"],
                    gics_sector=h["gics_sector"],
                )
                for h in holdings_data
            ]

        portfolio.add_position(pos)

    return portfolio
