"""Contrôles des artefacts livrés, sans téléchargement de données."""

import re
from pathlib import Path

from rnv.support import verify


def test_published_artifacts_match_manifests():
    verify()


def test_documentation_has_no_unresolved_fields_and_local_links_exist():
    for path in [Path("README.md"), Path("ARTICLE.md"), *Path("docs").glob("*.md")]:
        content = path.read_text()
        assert "{{" not in content
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
            if target.startswith(("http:", "https:", "#", "mailto:")):
                continue
            assert (path.parent / target.split("#")[0]).exists(), (str(path), target)


def test_executed_notebook_has_no_error_output():
    import json

    book = json.loads(Path("notebooks/01_comprendre.ipynb").read_text())
    cells = [c for c in book["cells"] if c["cell_type"] == "code"]
    assert cells and all(c["execution_count"] is not None for c in cells)
    assert not any(o["output_type"] == "error" for c in cells for o in c["outputs"])


def test_excel_examples_have_correct_cached_results():
    import json

    import openpyxl
    import pytest

    expected = json.loads(Path("results/workbook_data.json").read_text())["example"]["checks"]
    book = openpyxl.load_workbook("results/resultats.xlsx", data_only=True, read_only=True)
    for cell, value in expected.items():
        assert book["Exemple"][cell].value == pytest.approx(value, abs=1e-9)
    book.close()
