"""Trajectoires historiques et rééchantillonnage conjoint des années."""

from pathlib import Path

import numpy as np
import pandas as pd

from .model import RULES, Policy, measure, simulate, summary
from .support import block_indices, config, save_table


def load_panel():
    """Charge les sources, aligne les dates et applique les unités documentées."""
    d = pd.read_stata("data/raw/jst.dta", convert_categoricals=False).sort_values(["iso", "year"])
    d["inflation"] = d.groupby("iso").cpi.pct_change(fill_method=None)
    d["portfolio"] = config()["equity_weight"] * d.eq_tr + (1 - config()["equity_weight"]) * d.bond_tr
    return d


def historical_windows(d, horizon):
    """Extrait des trajectoires annuelles complètes, sans relier une année manquante."""
    starts, r, pi = [], [], []
    for i in range(len(d) - horizon + 1):
        window = d.iloc[i : i + horizon]
        if window.year.iloc[-1] - window.year.iloc[0] != horizon - 1:
            continue
        if window[["portfolio", "inflation"]].isna().any().any():
            continue
        starts.append(int(window.year.iloc[0]))
        r.append(window.portfolio.to_numpy())
        pi.append(window.inflation.to_numpy())
    return starts, np.asarray(r), np.asarray(pi)


def run():
    """Exécute l’expérience et les sensibilités annoncées dans le protocole."""
    c = config()
    policy = Policy(
        initial=c["initial_wealth"],
        rate=c["withdrawal_rate"],
        minimum_share=c["minimum_budget_share"],
        fee=c["annual_fee"],
        lower=c["dynamic_lower"],
        upper=c["dynamic_upper"],
    )
    d = load_panel()
    coverage = (
        d.groupby(["iso", "country"])
        .agg(
            equity_years=("eq_tr", "count"),
            bond_years=("bond_tr", "count"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .reset_index()
    )
    save_table(coverage, "coverage")
    us = d[d.iso.eq(c["primary_country"])].copy()
    historical, aggregates, examples = [], [], []
    for horizon in c["horizons_years"]:
        starts, r, pi = historical_windows(us, horizon)
        for rule in RULES:
            paid, balances, unfunded = simulate(r, pi, rule, policy)
            m = measure(paid, balances, unfunded, policy)
            m["start_year"], m["horizon"], m["rule"] = starts, horizon, rule
            historical.append(m)
            aggregates.append({"horizon": horizon, "rule": rule, **summary(m)})
            if horizon == 40:
                # A calendar cohort chosen before inspecting outcomes, not the worst case.
                if 1966 in starts:
                    k = starts.index(1966)
                    examples.append(
                        pd.DataFrame(
                            {
                                "year": np.arange(1966, 2006),
                                "rule": rule,
                                "spending": paid[k],
                                "wealth": balances[k],
                            }
                        )
                    )
    hist = pd.concat(historical, ignore_index=True)
    save_table(hist, "historical_paths")
    save_table(pd.DataFrame(aggregates), "historical_summary")
    save_table(pd.concat(examples), "cohort_1966")
    # Compare horizons on exactly the same retirement start years as a separate table.
    shared = set.intersection(*(set(hist[hist.horizon.eq(h)].start_year) for h in c["horizons_years"]))
    common = hist[hist.start_year.isin(shared)]
    save_table(
        pd.DataFrame(
            [{"horizon": h, "rule": r, **summary(g)} for (h, r), g in common.groupby(["horizon", "rule"])]
        ),
        "common_origins",
    )
    international = []
    for (iso, country), group in d[d.year.ge(c["international_start"])].groupby(["iso", "country"]):
        starts, r, pi = historical_windows(group, 40)
        if not starts:
            continue
        for rule in RULES:
            m = measure(*simulate(r, pi, rule, policy), policy)
            international.append({"iso": iso, "country": country, "rule": rule, **summary(m)})
    save_table(pd.DataFrame(international), "international")
    complete = us.dropna(subset=["portfolio", "inflation"])
    if not np.all(np.diff(complete.year) == 1):
        raise ValueError("Le bootstrap exige une séquence annuelle complète")
    simulated, envelopes, comparisons = [], [], []
    rng = np.random.default_rng(c["seed"])
    for block in c["bootstrap_blocks_years"]:
        idx = block_indices(len(complete), c["bootstrap_paths"], max(c["horizons_years"]), block, rng)
        r, pi = complete.portfolio.to_numpy()[idx], complete.inflation.to_numpy()[idx]
        for horizon in c["horizons_years"]:
            paired = {}
            for rule in RULES:
                paid, balances, unfunded = simulate(r[:, :horizon], pi[:, :horizon], rule, policy)
                m = measure(paid, balances, unfunded, policy)
                paired[rule] = m
                simulated.append({"block_years": block, "horizon": horizon, "rule": rule, **summary(m)})
                if block == 5 and horizon == 40:
                    for t in range(horizon):
                        envelopes.append(
                            {
                                "year": t + 1,
                                "rule": rule,
                                **{
                                    f"spending_p{q:02}": np.quantile(paid[:, t], q / 100) for q in [5, 50, 95]
                                },
                            }
                        )
            for rule in ["percentage", "dynamic", "floor"]:
                delta = (
                    paired[rule].shortfall_fraction.to_numpy() - paired["fixed"].shortfall_fraction.to_numpy()
                )
                comparisons.append(
                    {
                        "block_years": block,
                        "horizon": horizon,
                        "rule": rule,
                        "mean_shortfall_difference": delta.mean(),
                        "monte_carlo_se": delta.std(ddof=1) / np.sqrt(len(delta)),
                        "share_lower_shortfall": np.mean(delta < -1e-12),
                    }
                )
    save_table(pd.DataFrame(simulated), "bootstrap_summary")
    save_table(pd.DataFrame(envelopes), "spending_distribution")
    save_table(pd.DataFrame(comparisons), "paired_comparisons")
    # A higher-fee sensitivity on observed, identical forty-year paths.
    fee_rows = []
    _, r, pi = historical_windows(us, 40)
    from dataclasses import replace

    for fee in [0, policy.fee, 0.01]:
        p = replace(policy, fee=fee)
        for rule in RULES:
            fee_rows.append({"fee": fee, "rule": rule, **summary(measure(*simulate(r, pi, rule, p), p))})
    save_table(pd.DataFrame(fee_rows), "fee_sensitivity")
    Path("data/processed").mkdir(exist_ok=True)
    d[["year", "iso", "country", "portfolio", "inflation"]].to_parquet(
        "data/processed/annual.parquet", index=False
    )
