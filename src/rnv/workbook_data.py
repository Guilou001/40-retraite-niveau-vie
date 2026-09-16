"""Prépare une sélection pédagogique de résultats pour le classeur."""

import json
from pathlib import Path

import pandas as pd

RULE = {
    "fixed": "Montant constant",
    "percentage": "Pourcentage du solde",
    "dynamic": "Ajustement limité",
    "floor": "Avec budget minimal",
}
PORT = {
    "reit": "Immobilier coté",
    "clone": "Remplacement estimé",
    "static_clone": "Mélange fixe 66 / 34",
    "base": "60 % actions et 40 % obligations",
    "with_reit": "Avec 10 % d’immobilier",
    "with_clone": "Avec 10 % de remplacement",
}


def table(name, subtitle, frame, columns):
    """Prépare le tableau de lecture en conservant les colonnes et leur ordre."""
    d = frame[[c[0] for c in columns]].copy()
    for col in d:
        if col == "rule":
            d[col] = d[col].map(RULE)
        if col == "portfolio":
            d[col] = d[col].map(PORT)
    return {
        "name": name,
        "subtitle": subtitle,
        "headers": [c[1] for c in columns],
        "formats": [c[2] for c in columns],
        "rows": json.loads(d.to_json(orient="values")),
    }


def example(title, note, cells, checks):
    """Décrit les entrées et formules de l’exemple arithmétique Excel."""
    return {"name": "Exemple", "title": title, "subtitle": note, "cells": cells, "checks": checks}


def val(row, label, value, fmt="0.00"):
    """Décrit une cellule d’entrée numérique et son format d’affichage."""
    return {"row": row, "label": label, "value": value, "format": fmt}


def formula(row, label, expression, fmt="0.00"):
    """Décrit une cellule calculée et sa formule Excel explicite."""
    return {"row": row, "label": label, "formula": expression, "format": fmt}


def build():
    """Prépare la sélection Excel depuis les tables calculées et l’exemple connu."""
    root = Path.cwd()
    p = json.loads(Path("config/project.json").read_text())

    def read(name):
        return pd.read_csv(root / "results/tables" / f"{name}.csv")

    a = table(
        "Résultats",
        "Départs américains de 40 ans, retraits en pouvoir d’achat constant",
        read("historical_summary").query("horizon == 40"),
        [
            ("rule", "Règle", "@"),
            ("paths", "Départs", "0"),
            ("ruin_share", "Capital épuisé", "0.0%"),
            ("below_budget_share", "Sous le budget au moins un an", "0.0%"),
            ("years_below_mean", "Années sous le budget en moyenne", "0.0"),
        ],
    )
    b = table(
        "Sensibilités",
        "Scénarios américains de 40 ans, 10 000 tirages par longueur de bloc",
        read("bootstrap_summary").query("horizon == 40"),
        [
            ("block_years", "Blocs en années", "0"),
            ("rule", "Règle", "@"),
            ("ruin_share", "Capital épuisé", "0.0%"),
            ("below_budget_share", "Sous le budget au moins un an", "0.0%"),
            ("shortfall_fraction_mean", "Manque cumulé relatif au budget", "0.0%"),
        ],
    )
    e = example(
        "Pourquoi l’ordre des rendements compte",
        "Modifier les rendements ou le retrait pour comparer les deux ordres.",
        [
            val(7, "Capital initial", 100),
            val(8, "Premier rendement", -0.2, "0.0%"),
            val(9, "Deuxième rendement", 0.25, "0.0%"),
            val(10, "Retrait en fin d’année", 10),
            formula(12, "Solde après la première année", "=B7*(1+B8)-B10"),
            formula(13, "Solde final", "=B12*(1+B9)-B10"),
            formula(15, "Solde intermédiaire, ordre inverse", "=B7*(1+B9)-B10"),
            formula(16, "Solde final, ordre inverse", "=B15*(1+B8)-B10"),
        ],
        {"B13": 77.5, "B16": 82},
    )
    e["mutation"] = {"input": "B7", "value": 110, "output": "B13", "expected": 87.5}
    source_urls = [m["url"] for m in json.loads((root / "config/data_manifest.json").read_text()).values()]
    payload = {
        "title": p["title"],
        "repository": "https://github.com/Guilou001/" + p["repo"],
        "tables": [a, b],
        "example": e,
        "sources": source_urls,
    }
    (root / "results/workbook_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
