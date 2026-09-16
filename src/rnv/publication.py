"""Figures et textes alimentés exclusivement par les tables calculées."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .model import RULES
from .rendering import (
    BLUE,
    GREY,
    ORANGE,
    RED,
    TEAL,
    compile_article,
    number,
    polish,
    save,
    style,
    table,
    templates,
)

COLORS = [BLUE, ORANGE, TEAL, RED]
LINESTYLES = {"fixed": "-", "percentage": "--", "dynamic": "-.", "floor": ":"}


def read(name):
    """Lit une table de résultats CSV depuis le dépôt courant."""
    return pd.read_csv(f"results/tables/{name}.csv")


def publish():
    """Produit les quatre figures et insère les résultats dans les textes relus."""
    style()
    h = read("historical_summary")
    primary = h[h.horizon.eq(40)].set_index("rule").loc[list(RULES)]
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    y = np.arange(4)
    ax.barh(y - 0.16, primary.ruin_share * 100, 0.3, label="Capital épuisé", color=BLUE)
    ax.barh(
        y + 0.16,
        primary.below_budget_share * 100,
        0.3,
        label="Dépenses sous 30 000 $ au moins un an",
        color=ORANGE,
    )
    ax.set_yticks(y, list(RULES.values()))
    ax.invert_yaxis()
    ax.set(
        xlabel="Part des départs historiques américains (%)",
        xlim=(0, 100),
        title=f"Deux façons différentes de manquer son objectif sur 40 ans\n{int(primary.paths.iloc[0])} départs historiques, portefeuille 50 % actions et 50 % obligations",
    )
    ax.legend(loc="lower right", fontsize=8)
    for k, row in enumerate(primary.itertuples()):
        ax.text(
            row.ruin_share * 100 + 1,
            k - 0.16,
            number(row.ruin_share, 1, True) + " %",
            va="center",
            fontsize=9,
        )
        ax.text(
            row.below_budget_share * 100 + 1,
            k + 0.16,
            number(row.below_budget_share, 1, True) + " %",
            va="center",
            fontsize=9,
        )
    save(fig, "budget_et_capital")
    cohort = read("cohort_1966")
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.6), sharex=True, layout="constrained")
    for color, (rule, label) in zip(COLORS, RULES.items(), strict=True):
        g = cohort[cohort.rule.eq(rule)]
        axes[0].plot(g.year, g.spending / 1000, label=label, color=color, linestyle=LINESTYLES[rule])
        axes[1].plot(g.year, g.wealth / 1000, color=color, linestyle=LINESTYLES[rule])
    axes[0].axhline(30, color=GREY, ls="--", label="Budget minimal")
    axes[0].set(
        title="Un départ en 1966, quatre règles de retrait",
        ylabel="Dépenses annuelles\n(milliers de dollars US de début 1966)",
    )
    axes[1].set(xlabel="Année", ylabel="Solde après retrait\n(milliers de dollars US de début 1966)")
    axes[0].legend(ncol=2, fontsize=8)
    for ax in axes:
        polish(ax)
    save(fig, "depart_1966")
    intl = read("international")
    pivot = intl.pivot(index="country", columns="rule", values="below_budget_share")[list(RULES)]
    names = {
        "Australia": "Australie",
        "Belgium": "Belgique",
        "Denmark": "Danemark",
        "Finland": "Finlande",
        "France": "France",
        "Germany": "Allemagne",
        "Italy": "Italie",
        "Japan": "Japon",
        "Netherlands": "Pays-Bas",
        "Norway": "Norvège",
        "Portugal": "Portugal",
        "Spain": "Espagne",
        "Sweden": "Suède",
        "Switzerland": "Suisse",
        "UK": "Royaume-Uni",
        "USA": "États-Unis",
    }
    fig, ax = plt.subplots(figsize=(9, 7.1), layout="constrained")
    im = ax.imshow(pivot.to_numpy() * 100, vmin=0, vmax=100, cmap="Oranges", aspect="auto")
    ax.set_yticks(range(len(pivot)), [names[n] for n in pivot.index])
    ax.set_xticks(
        range(4), ["Montant\nconstant", "Pourcentage\ndu solde", "Ajustement\nlimité", "Avec budget\nminimal"]
    )
    for i in range(len(pivot)):
        for j in range(4):
            v = pivot.iloc[i, j] * 100
            ax.text(
                j, i, f"{v:.0f}", ha="center", va="center", color="white" if v > 65 else "#303B46", fontsize=9
            )
    ax.set_title(
        "Les expériences américaines ne résument pas tous les pays\nDéparts depuis 1950, retraits pendant 40 ans, actifs domestiques"
    )
    fig.colorbar(im, ax=ax, label="Départs avec dépenses sous le budget minimal (%)", shrink=0.75)
    save(fig, "comparaison_pays")
    b = read("bootstrap_summary")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.7), sharey=True, layout="constrained")
    for color, (rule, label) in zip(COLORS, RULES.items(), strict=True):
        g = b[b.horizon.eq(40) & b.rule.eq(rule)]
        axes[0].plot(
            g.block_years,
            g.ruin_share * 100,
            marker="o",
            linestyle=LINESTYLES[rule],
            color=color,
            label=label,
        )
        axes[1].plot(
            g.block_years, g.below_budget_share * 100, marker="o", linestyle=LINESTYLES[rule], color=color
        )
    axes[0].set(title="Capital épuisé", ylabel="Part des scénarios (%)")
    axes[1].set_title("Dépenses sous le budget minimal")
    for ax in axes:
        ax.set(xlabel="Longueur des blocs (années)", xticks=[3, 5, 10], ylim=(-2, 100))
        polish(ax)
    fig.suptitle(
        "Le résultat dépend aussi de la façon de reconstruire les scénarios\n10 000 trajectoires américaines de 40 ans par longueur de bloc",
        fontsize=11,
    )
    fig.legend(
        *axes[0].get_legend_handles_labels(),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=2,
        fontsize=8,
    )
    save(fig, "sensibilite_blocs")
    bp = b[b.horizon.eq(40) & b.block_years.eq(5)].set_index("rule")
    rows = [
        [
            RULES[r],
            number(v.ruin_share, 1, True) + " %",
            number(v.below_budget_share, 1, True) + " %",
            number(v.years_below_mean, 1),
        ]
        for r, v in primary.iterrows()
    ]
    international_us = intl[intl.iso.eq("USA") & intl.rule.eq("floor")].iloc[0]
    values = {
        "historical_table": table(
            ["Règle", "Capital épuisé", "Au moins un an sous le budget", "Années sous le budget en moyenne"],
            rows,
        ),
        "bootstrap_table": table(
            ["Règle", "Capital épuisé", "Sous le budget", "Manque moyen au budget"],
            [
                [
                    RULES[r],
                    number(v.ruin_share, 1, True) + " %",
                    number(v.below_budget_share, 1, True) + " %",
                    number(v.shortfall_fraction_mean, 1, True) + " %",
                ]
                for r, v in bp.iterrows()
            ],
        ),
        "fixed_ruin": number(primary.loc["fixed", "ruin_share"], 1, True),
        "percentage_shortfall": number(primary.loc["percentage", "below_budget_share"], 1, True),
        "dynamic_shortfall": number(primary.loc["dynamic", "below_budget_share"], 1, True),
        "bootstrap_floor_ruin": number(bp.loc["floor", "ruin_share"], 1, True),
        "paths": int(primary.paths.iloc[0]),
        "countries": intl.iso.nunique(),
        "common_table": table(
            ["Durée", "Montant constant", "Ajustement limité", "Avec budget minimal"],
            [
                [
                    str(int(hh)) + " ans",
                    *[
                        number(g.set_index("rule").loc[r, "ruin_share"], 1, True) + " %"
                        for r in ["fixed", "dynamic", "floor"]
                    ],
                ]
                for hh, g in read("common_origins").groupby("horizon")
            ],
        ),
        "international_us_paths": int(international_us.paths),
    }
    templates(values)
    compile_article("40-retraite-niveau-vie")
