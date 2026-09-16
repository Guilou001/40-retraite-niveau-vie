"""Retraits annuels en pouvoir d'achat constant, payés en fin d'année."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike

RULES = {
    "fixed": "Montant constant",
    "percentage": "Pourcentage du solde",
    "dynamic": "Ajustement limité",
    "floor": "Ajustement avec budget minimal",
}


@dataclass(frozen=True)
class Policy:
    initial: float = 1_000_000
    rate: float = 0.04
    minimum_share: float = 0.75
    lower: float = -0.015
    upper: float = 0.05
    fee: float = 0.002

    def __post_init__(self):
        if not np.isfinite(
            [self.initial, self.rate, self.minimum_share, self.lower, self.upper, self.fee]
        ).all():
            raise ValueError("Paramètres finis requis")
        if not (self.initial > 0 and 0 < self.rate < 1 and 0 < self.minimum_share <= 1):
            raise ValueError("Capital, taux de retrait ou budget minimal invalide")
        if not (-1 < self.lower <= 0 <= self.upper and 0 <= self.fee < 1):
            raise ValueError("Limites de dépenses ou frais invalides")


def simulate(
    returns: ArrayLike, inflation: ArrayLike, rule: str, policy: Policy = Policy()
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Renvoie patrimoine et dépenses réels pour chaque trajectoire et année.

    La première dépense vaut rate * initial en monnaie de départ. Le taux
    de 4 % s'applique au solde avant retrait à partir de la deuxième année.
    Les limites annuelles portent sur les dépenses réelles effectivement payées.
    """
    r, pi = np.asarray(returns, dtype=float), np.asarray(inflation, dtype=float)
    if r.ndim == 1:
        r, pi = r[None, :], pi[None, :]
    if r.ndim != 2 or r.shape != pi.shape or r.shape[1] < 1:
        raise ValueError("Deux matrices de mêmes dimensions sont nécessaires")
    if not np.isfinite(r).all() or not np.isfinite(pi).all() or (r < -1).any() or (pi <= -1).any():
        raise ValueError("Rendement ou inflation impossible")
    if rule not in RULES:
        raise ValueError("Règle inconnue")
    wealth = np.full(r.shape[0], policy.initial, dtype=float)
    previous = np.full(r.shape[0], policy.initial * policy.rate)
    paid, balances, unfunded = np.zeros_like(r), np.zeros_like(r), np.zeros_like(r, dtype=bool)
    for t in range(r.shape[1]):
        available = wealth * (1 + r[:, t]) * (1 - policy.fee) / (1 + pi[:, t])
        if t == 0 or rule == "fixed":
            requested = np.full(r.shape[0], policy.initial * policy.rate)
        elif rule == "percentage":
            requested = policy.rate * available
        else:
            requested = np.clip(
                policy.rate * available, previous * (1 + policy.lower), previous * (1 + policy.upper)
            )
            if rule == "floor":
                requested = np.maximum(requested, policy.initial * policy.rate * policy.minimum_share)
        paid[:, t] = np.minimum(requested, available)
        unfunded[:, t] = paid[:, t] < requested - 1e-8
        wealth = available - paid[:, t]
        balances[:, t] = wealth
        previous = paid[:, t]
    return paid, balances, unfunded


def measure(paid: np.ndarray, balances: np.ndarray, unfunded: np.ndarray, policy: Policy) -> pd.DataFrame:
    """Mesure épuisement, dépenses insuffisantes et richesse finale par trajectoire."""
    minimum = policy.initial * policy.rate * policy.minimum_share
    below = paid < minimum - 1e-8
    run = np.zeros(paid.shape[0], dtype=int)
    longest = run.copy()
    for t in range(paid.shape[1]):
        run = np.where(below[:, t], run + 1, 0)
        longest = np.maximum(longest, run)
    return pd.DataFrame(
        {
            "ruined": np.any(balances <= 1e-8, axis=1),
            "unfunded_rule": np.any(unfunded, axis=1),
            "below_budget": below.any(axis=1),
            "years_below_budget": below.sum(axis=1),
            "longest_shortfall": longest,
            "shortfall_fraction": np.maximum(minimum - paid, 0).sum(axis=1) / (minimum * paid.shape[1]),
            "mean_spending": paid.mean(axis=1),
            "minimum_spending": paid.min(axis=1),
            "terminal_wealth": balances[:, -1],
        }
    )


def summary(frame: pd.DataFrame) -> dict:
    """Agrège les résultats des trajectoires sans les considérer indépendantes."""
    return {
        "paths": len(frame),
        "ruin_share": frame.ruined.mean(),
        "unfunded_share": frame.unfunded_rule.mean(),
        "below_budget_share": frame.below_budget.mean(),
        "years_below_mean": frame.years_below_budget.mean(),
        "longest_shortfall_p95": frame.longest_shortfall.quantile(0.95),
        "shortfall_fraction_mean": frame.shortfall_fraction.mean(),
        "mean_spending_median": frame.mean_spending.median(),
        "minimum_spending_p05": frame.minimum_spending.quantile(0.05),
        "terminal_wealth_median": frame.terminal_wealth.median(),
    }
