"""Commandes pour télécharger, calculer et publier les résultats."""

import time
from pathlib import Path

import typer

from . import support

app = typer.Typer(no_args_is_help=True, help="Étude reproductible avec sources figées.")


@app.command()
def fetch():
    """Télécharger et vérifier les empreintes des données."""
    support.fetch()


@app.command()
def run():
    """Calculer les analyses et leurs contrôles de sensibilité."""
    from .experiment import run as analyze

    support.check_inputs()
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    analyze()
    support.export_tables()
    from .workbook_data import build

    build()
    support.finish_run(time.perf_counter() - started)


@app.command()
def publish():
    """Recréer les figures et le rapport depuis les résultats locaux."""
    from .publication import publish as render

    support.check_results()
    support.check_publication_protocol()
    support.check_workbook()
    render()
    support.finish_publication()


@app.command()
def verify():
    """Vérifier la provenance du calcul et les publications locales."""
    support.verify()
