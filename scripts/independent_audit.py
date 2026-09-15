"""Contre-calcul séparé de résultats choisis, sans import du moteur scientifique."""

import json
from pathlib import Path

import pandas as pd

root = Path.cwd()
checks = []


def record(name, actual, reference, tolerance=1e-8):
    error = float(abs(actual - reference))
    assert error <= tolerance, (name, actual, reference, error)
    checks.append(
        {
            "check": name,
            "calculated": float(actual),
            "independent_reference": float(reference),
            "absolute_difference": error,
            "tolerance": tolerance,
        }
    )


raw = pd.read_stata(root / "data/raw/jst.dta").query('iso == "USA"').set_index("year")
published = pd.read_csv(root / "results/tables/historical_paths.csv").query("horizon == 40")
counts = {}
for row in published.itertuples():
    wealth = 1e6
    previous = 40000.0
    payments = []
    for year in range(row.start_year, row.start_year + 40):
        a = raw.loc[year]
        cpi = a.cpi / raw.loc[row.start_year - 1].cpi
        available = wealth * (1 + (float(a.eq_tr) + float(a.bond_tr)) / 2) * 0.998
        real = available / cpi
        if year == row.start_year or row.rule == "fixed":
            wanted = 40000.0
        elif row.rule == "percentage":
            wanted = 0.04 * real
        else:
            wanted = max(previous * 0.985, min(previous * 1.05, 0.04 * real))
            if row.rule == "floor":
                wanted = max(30000, wanted)
        spent = min(available, wanted * cpi)
        payments.append(spent / cpi)
        wealth = available - spent
        previous = spent / cpi
    record(f"{row.rule}_{row.start_year}_terminal", row.terminal_wealth, wealth / cpi, 1e-4)
    record(f"{row.rule}_{row.start_year}_mean_spending", row.mean_spending, sum(payments) / 40, 1e-6)
    record(
        f"{row.rule}_{row.start_year}_years_below",
        row.years_below_budget,
        sum(v < 30000 - 1e-8 for v in payments),
        0,
    )

output = {
    "date": "2026-09-15",
    "method": "Contre-calcul séparé, sans import des fonctions scientifiques du projet",
    "checks": checks,
    "passed": len(checks),
}
(root / "results/verification.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
print(len(checks), "comparaisons numériques réussies")
