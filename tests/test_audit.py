"""Régressions issues de l’audit de reproduction."""

import json
import shutil
from pathlib import Path

import pytest

from rnv.support import check_publication_protocol, check_workbook


def test_every_workbook_table_matches_computed_values():
    assert check_workbook() > 0


def test_stale_workbook_is_rejected(tmp_path, monkeypatch):
    (tmp_path / "results").mkdir()
    shutil.copy("results/resultats.xlsx", tmp_path / "results/resultats.xlsx")
    payload = json.loads(Path("results/workbook_data.json").read_text())
    payload["tables"][0]["rows"][0][1] = 999999
    (tmp_path / "results/workbook_data.json").write_text(json.dumps(payload))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Classeur périmé"):
        check_workbook()


def test_changed_protocol_cannot_reuse_reviewed_narrative(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "config/protocol.json").write_text('{"annual_fee": 0.01}')
    (tmp_path / "config/publication_protocol.json").write_text('{"annual_fee": 0.002}')
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Protocole différent"):
        check_publication_protocol()
