"""
Risk Engine: Volatilität, Korrelation, Sharpe Ratio und Markowitz Efficient Frontier.

Verwendet EWMA (Exponentially Weighted Moving Average) für die Kovarianzmatrix,
um jüngere Daten stärker zu gewichten als ältere.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from utils.constants import EWMA_LAMBDA

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Risikokennzahlen des Portfolios."""
    annual_return: float          # Annualisierte Rendite
    annual_volatility: float      # Annualisierte Volatilität
    sharpe_ratio: float           # Sharpe Ratio (risikofreier Zins angenommen)
    max_drawdown: float           # Maximaler Drawdown
    var_95: float                 # Value at Risk (95%)
    var_99: float                 # Value at Risk (99%)
    cvar_95: float                # Conditional VaR / Expected Shortfall (95%)
    cvar_99: float                # Conditional VaR / Expected Shortfall (99%)
    risk_free_rate: float         # Verwendeter risikofreier Zinssatz


@dataclass
class FrontierPoint:
    """Ein Punkt auf der Efficient Frontier."""
    return_: float
    volatility: float
    sharpe: float
    weights: dict[str, float]     # Ticker → Gewicht


class RiskEngine:
    """Berechnet Risikokennzahlen und die Efficient Frontier."""

    def __init__(
        self,
        returns: pd.DataFrame,
        weights: dict[str, float],
        risk_free_rate: float = 0.03,  # 3% als Default
        ewma_lambda: float = EWMA_LAMBDA,
    ):
        """
        Args:
            returns: DataFrame mit täglichen Log-Renditen (Spalten = Ticker)
            weights: Dict {Ticker: Gewicht} (summiert zu 1.0)
            risk_free_rate: Annualisierter risikofreier Zinssatz
            ewma_lambda: Decay-Faktor für EWMA (0.94 = RiskMetrics Standard)
        """
        self.returns = returns.dropna()
        self.weights = weights
        self.risk_free_rate = risk_free_rate
        self.ewma_lambda = ewma_lambda

        # Nur Ticker verwenden, die sowohl in returns als auch in weights sind
        available = set(self.returns.columns) & set(self.weights.keys())
        if not available:
            raise ValueError(
                "Keine gemeinsamen Ticker zwischen Renditen und Gewichten. "
                f"Renditen: {list(self.returns.columns)}, "
                f"Gewichte: {list(self.weights.keys())}"
            )

        self.tickers = sorted(available)
        self.returns = self.returns[self.tickers]

        # Gewichte normalisieren auf verfügbare Ticker
        total = sum(self.weights[t] for t in self.tickers)
        self.w = np.array([self.weights[t] / total for t in self.tickers])

        self._cov_matrix: Optional[np.ndarray] = None
        self._mean_returns: Optional[np.ndarray] = None

    @property
    def cov_matrix(self) -> np.ndarray:
        """EWMA-Kovarianzmatrix (annualisiert)."""
        if self._cov_matrix is None:
            self._cov_matrix = self._compute_ewma_covariance()
        return self._cov_matrix

    @property
    def mean_returns(self) -> np.ndarray:
        """Annualisierte mittlere Renditen."""
        if self._mean_returns is None:
            # Geometrisches Mittel der täglichen Renditen, annualisiert
            daily_means = self.returns.mean().values
            self._mean_returns = daily_means * 252
        return self._mean_returns

    def _compute_ewma_covariance(self) -> np.ndarray:
        """
        EWMA-Kovarianzmatrix berechnen.
        Jüngere Beobachtungen erhalten exponentiell mehr Gewicht.
        """
        n = len(self.returns)
        n_assets = len(self.tickers)

        if n < 30:
            logger.warning(
                f"Nur {n} Beobachtungen vorhanden. EWMA-Schätzung könnte instabil sein."
            )

        # EWMA-Gewichte berechnen
        lam = self.ewma_lambda
        ewma_weights = np.array([(1 - lam) * lam ** i for i in range(n - 1, -1, -1)])
        ewma_weights /= ewma_weights.sum()

        # Demeaned Returns
        data = self.returns.values
        demeaned = data - data.mean(axis=0)

        # Gewichtete Kovarianzmatrix
        cov = np.zeros((n_assets, n_assets))
        for t in range(n):
            cov += ewma_weights[t] * np.outer(demeaned[t], demeaned[t])

        # Annualisieren
        cov *= 252

        return cov

    def compute_portfolio_metrics(self) -> RiskMetrics:
        """Risikokennzahlen des aktuellen Portfolios berechnen."""
        # Portfolio-Rendite
        port_return = float(self.w @ self.mean_returns)

        # Portfolio-Volatilität: sqrt(w' Σ w)
        port_vol = float(np.sqrt(self.w @ self.cov_matrix @ self.w))

        # Sharpe Ratio
        sharpe = (
            (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0
        )

        # Portfolio tägliche Renditen für Drawdown & VaR
        daily_portfolio_returns = (self.returns * self.w).sum(axis=1)

        # Maximum Drawdown
        cumulative = (1 + daily_portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdowns = (cumulative - running_max) / running_max
        max_dd = float(drawdowns.min())

        # Value at Risk (parametrisch, annualisiert → auf Tag umgerechnet)
        daily_vol = port_vol / np.sqrt(252)
        daily_mean = port_return / 252
        var_95 = -(daily_mean - 1.645 * daily_vol)
        var_99 = -(daily_mean - 2.326 * daily_vol)

        # CVaR (Expected Shortfall) via Monte Carlo
        cvar_95 = self._compute_cvar(daily_portfolio_returns, confidence=0.95)
        cvar_99 = self._compute_cvar(daily_portfolio_returns, confidence=0.99)

        return RiskMetrics(
            annual_return=round(port_return, 4),
            annual_volatility=round(port_vol, 4),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown=round(max_dd, 4),
            var_95=round(var_95, 4),
            var_99=round(var_99, 4),
            cvar_95=round(cvar_95, 4),
            cvar_99=round(cvar_99, 4),
            risk_free_rate=self.risk_free_rate,
        )

    def _compute_cvar(self, daily_returns: pd.Series, confidence: float = 0.95) -> float:
        """CVaR (Expected Shortfall): Durchschnittsverlust in den schlimmsten (1-c)% Szenarien."""
        cutoff = np.percentile(daily_returns, (1 - confidence) * 100)
        tail = daily_returns[daily_returns <= cutoff]
        return -float(tail.mean()) if len(tail) > 0 else 0.0

    def compute_efficient_frontier(
        self, n_points: int = 100, allow_short: bool = False
    ) -> list[FrontierPoint]:
        """
        Efficient Frontier via Optimierung berechnen.

        Für verschiedene Zielrenditen wird das Portfolio mit minimaler
        Varianz gesucht (quadratische Optimierung).
        """
        n_assets = len(self.tickers)

        # Rendite-Bereich festlegen
        # Mit long-only Constraints ist Portfolio-Rendite immer im Bereich [min, max] der Einzeltitel
        min_ret = float(self.mean_returns.min())
        max_ret = float(self.mean_returns.max())

        # Kein Puffer — Targets ausserhalb des feasible range führen zu Solver-Fehlern
        target_returns = np.linspace(min_ret, max_ret, n_points)

        # Constraints und Bounds
        if allow_short:
            bounds = [(-1.0, 1.0)] * n_assets
        else:
            bounds = [(0.0, 1.0)] * n_assets

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},  # Gewichte = 100%
        ]

        frontier = []
        for target_ret in target_returns:
            ret_constraint = {
                "type": "eq",
                "fun": lambda w, tr=target_ret: w @ self.mean_returns - tr,
            }

            result = minimize(
                fun=lambda w: w @ self.cov_matrix @ w,
                x0=np.ones(n_assets) / n_assets,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints + [ret_constraint],
                options={"ftol": 1e-12, "maxiter": 1000},
            )

            if result.success:
                vol = float(np.sqrt(result.fun))
                ret = float(result.x @ self.mean_returns)
                sharpe = (
                    (ret - self.risk_free_rate) / vol if vol > 0 else 0
                )
                frontier.append(FrontierPoint(
                    return_=round(ret, 6),
                    volatility=round(vol, 6),
                    sharpe=round(sharpe, 4),
                    weights={t: round(w, 4) for t, w in zip(self.tickers, result.x)},
                ))

        return frontier

    def find_minimum_variance_portfolio(self) -> Optional[FrontierPoint]:
        """Minimum-Varianz-Portfolio finden."""
        n_assets = len(self.tickers)

        result = minimize(
            fun=lambda w: w @ self.cov_matrix @ w,
            x0=np.ones(n_assets) / n_assets,
            method="SLSQP",
            bounds=[(0.0, 1.0)] * n_assets,
            constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}],
        )

        if not result.success:
            return None

        vol = float(np.sqrt(result.fun))
        ret = float(result.x @ self.mean_returns)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0

        return FrontierPoint(
            return_=round(ret, 6),
            volatility=round(vol, 6),
            sharpe=round(sharpe, 4),
            weights={t: round(w, 4) for t, w in zip(self.tickers, result.x)},
        )

    def find_max_sharpe_portfolio(self) -> Optional[FrontierPoint]:
        """Tangentialportfolio (Maximum Sharpe Ratio) finden."""
        n_assets = len(self.tickers)

        def neg_sharpe(w):
            ret = w @ self.mean_returns
            vol = np.sqrt(w @ self.cov_matrix @ w)
            if vol < 1e-10:
                return 0
            return -(ret - self.risk_free_rate) / vol

        result = minimize(
            fun=neg_sharpe,
            x0=np.ones(n_assets) / n_assets,
            method="SLSQP",
            bounds=[(0.0, 1.0)] * n_assets,
            constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}],
        )

        if not result.success:
            return None

        vol = float(np.sqrt(result.x @ self.cov_matrix @ result.x))
        ret = float(result.x @ self.mean_returns)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0

        return FrontierPoint(
            return_=round(ret, 6),
            volatility=round(vol, 6),
            sharpe=round(sharpe, 4),
            weights={t: round(w, 4) for t, w in zip(self.tickers, result.x)},
        )

    def compute_beta(self, benchmark_returns: pd.Series) -> float:
        """
        Portfolio-Beta gegenüber einem Benchmark berechnen.
        Beta = Cov(Portfolio, Benchmark) / Var(Benchmark)
        """
        port_returns = (self.returns * self.w).sum(axis=1)

        # Auf gemeinsamen Zeitraum einschränken
        common = port_returns.index.intersection(benchmark_returns.index)
        if len(common) < 30:
            return float("nan")

        p = port_returns.loc[common].values
        b = benchmark_returns.loc[common].values

        cov = float(np.cov(p, b)[0, 1])
        var_b = float(np.var(b, ddof=1))
        if var_b < 1e-12:
            return float("nan")

        return round(cov / var_b, 3)

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Korrelationsmatrix der Portfolio-Bestandteile."""
        # Aus der EWMA-Kovarianzmatrix die Korrelationsmatrix ableiten
        cov = self.cov_matrix
        stds = np.sqrt(np.diag(cov))
        # Avoid division by zero
        stds = np.where(stds == 0, 1e-10, stds)
        corr = cov / np.outer(stds, stds)
        # Diagonale auf exakt 1.0 setzen
        np.fill_diagonal(corr, 1.0)
        return pd.DataFrame(corr, index=self.tickers, columns=self.tickers).round(3)

    def compute_rate_sensitivity(
        self,
        sector_weights: dict[int, float],
        n_simulations: int = 10_000,
        max_shock_bps: float = 300,
    ) -> pd.DataFrame:
        """
        Zinssensitivität des Portfolios via Monte Carlo.

        Simuliert Zinsänderungen (±max_shock_bps Basispunkte) und berechnet
        den Portfolioeffekt anhand sektor-spezifischer Sensitivitäten.

        Returns: DataFrame mit Spalten [Zinsänderung_bps, Portfolio_Impact_pct]
        """
        # Sensitivität: wie viel verliert/gewinnt das Portfolio pro 100 bps Zinsanstieg
        # Quelle: empirische Schätzungen aus akademischer Literatur
        RATE_SENSITIVITY: dict[int, float] = {
            10:  0.03,   # Energie       — leicht positiv (Inflationsschutz)
            15: -0.02,   # Grundstoffe   — neutral
            20: -0.04,   # Industrie     — leicht negativ
            25: -0.06,   # Zykl. Konsum  — negativ (Kreditkosten)
            30: -0.03,   # Basiskonsumgüter — defensiv
            35: -0.04,   # Gesundheit    — leicht negativ
            40:  0.05,   # Finanzen      — positiv (Zinsmargen steigen)
            45: -0.08,   # IT            — sehr negativ (DCF-Bewertung)
            50: -0.06,   # Kommunikation — negativ (hohe Verschuldung)
            55: -0.12,   # Versorger     — sehr negativ (Bond-Proxy)
            60: -0.15,   # Immobilien    — extrem negativ (REIT-Bewertung)
            0:  -0.05,   # Unbekannt     — Durchschnitt Aktien
        }

        np.random.seed(42)
        # Zinsschocks in Basispunkten (Normal-Verteilung, leicht positiv verzerrt)
        shocks_bps = np.random.normal(0, max_shock_bps / 3, n_simulations)
        shocks_bps = np.clip(shocks_bps, -max_shock_bps, max_shock_bps)

        # Portfoliogewichtete Sensitivität berechnen
        total_weight = sum(sector_weights.values()) or 1.0
        portfolio_sensitivity = sum(
            (w / total_weight) * RATE_SENSITIVITY.get(gics, -0.05)
            for gics, w in sector_weights.items()
        )

        # Impact = sensitivity × Δrate (in %) + Volatilitäts-Rauschen
        delta_rate_pct = shocks_bps / 100
        vol_noise = np.random.normal(0, 0.005, n_simulations)
        impacts = portfolio_sensitivity * delta_rate_pct + vol_noise

        return pd.DataFrame({
            "Zinsänderung_bps": shocks_bps.round(0),
            "Portfolio_Impact_pct": (impacts * 100).round(3),
        })

    def compute_monte_carlo_frontier(
        self, n_simulations: int = 5000
    ) -> pd.DataFrame:
        """
        Monte-Carlo-Simulation: Zufällige Portfolio-Gewichtungen generieren
        und deren Return/Volatilität plotten.

        Nützlich als Ergänzung zur analytischen Frontier,
        um die gesamte Menge möglicher Portfolios zu zeigen.
        """
        n_assets = len(self.tickers)
        results = []

        for _ in range(n_simulations):
            # Zufällige Gewichte (Dirichlet-Verteilung → summieren zu 1)
            w = np.random.dirichlet(np.ones(n_assets))
            ret = float(w @ self.mean_returns)
            vol = float(np.sqrt(w @ self.cov_matrix @ w))
            sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0
            results.append({
                "Rendite": round(ret, 6),
                "Volatilität": round(vol, 6),
                "Sharpe": round(sharpe, 4),
            })

        return pd.DataFrame(results)
