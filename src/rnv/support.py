"""Téléchargement vérifié, tables de résultats et provenance des calculs."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd


def config() -> dict:
    return json.loads(Path("config/protocol.json").read_text())


def fingerprint(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch() -> None:
    manifest = json.loads(Path("config/data_manifest.json").read_text())
    raw = Path("data/raw")
    raw.mkdir(parents=True, exist_ok=True)
    for name, meta in manifest.items():
        path = raw / name
        if not path.exists():
            temporary = path.with_suffix(path.suffix + ".part")
            subprocess.run(
                [
                    "curl",
                    "--fail",
                    "--location",
                    "--silent",
                    "--show-error",
                    "--retry",
                    "2",
                    "--max-time",
                    "90",
                    meta["url"],
                    "-o",
                    str(temporary),
                ],
                check=True,
            )
            temporary.replace(path)
        if fingerprint(path) != meta["sha256"]:
            raise ValueError(
                f"Le millésime de {name} diffère du manifeste. Conserver le fichier séparément et créer un nouveau manifeste avant une nouvelle étude."
            )


def check_inputs() -> None:
    for name, meta in json.loads(Path("config/data_manifest.json").read_text()).items():
        path = Path("data/raw") / name
        if not path.exists() or fingerprint(path) != meta["sha256"]:
            raise ValueError(f"Source absente ou modifiée {path}. Exécuter la commande fetch.")


def save_table(frame: pd.DataFrame, name: str) -> None:
    p = Path("results/tables")
    p.mkdir(parents=True, exist_ok=True)
    frame.to_csv(p / f"{name}.csv", index=False, float_format="%.12g")


def block_indices(length: int, samples: int, horizon: int, block: int, rng) -> np.ndarray:
    """Blocs circulaires contigus, tronqués au nombre exact de périodes demandé."""
    if min(length, samples, horizon, block) < 1 or block > length:
        raise ValueError("Dimensions de rééchantillonnage invalides")
    starts = rng.integers(0, length, size=(samples, (horizon + block - 1) // block))
    return ((starts[..., None] + np.arange(block)) % length).reshape(samples, -1)[:, :horizon]


def finish_run(seconds: float) -> None:
    """Enregistre les tables et le programme exacts après réussite de l'analyse."""
    files = sorted(Path("results/tables").glob("*.csv"))
    outputs = {str(p): fingerprint(p) for p in files}
    sources = {str(p): fingerprint(p) for p in sorted(Path("src").rglob("*.py"))}
    Path("results/run_manifest.json").write_text(
        json.dumps(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "seconds": seconds,
                "python": sys.version,
                "platform": platform.platform(),
                "lock_sha256": fingerprint(Path("uv.lock")),
                "protocol_sha256": fingerprint(Path("config/protocol.json")),
                "data_manifest_sha256": fingerprint(Path("config/data_manifest.json")),
                "source_files": sources,
                "tables": outputs,
            },
            indent=2,
        )
        + "\n"
    )


def export_tables() -> None:
    """Entrepôt local depuis les tables effectivement calculées."""
    import duckdb

    path = Path("results")
    frames = {p.stem: pd.read_csv(p) for p in sorted((path / "tables").glob("*.csv"))}
    with duckdb.connect(str(path / "research.duckdb")) as con:
        for name, frame in frames.items():
            con.register("source_frame", frame)
            con.execute(f'CREATE OR REPLACE TABLE "{name}" AS SELECT * FROM source_frame')
            con.unregister("source_frame")


def check_results():
    """Contrôle le contrat du dernier calcul sans exiger les données brutes."""
    manifest = json.loads(Path("results/run_manifest.json").read_text())
    if fingerprint(Path("uv.lock")) != manifest["lock_sha256"]:
        raise ValueError("Le verrou des dépendances a changé")
    if fingerprint(Path("config/protocol.json")) != manifest["protocol_sha256"]:
        raise ValueError("Le protocole a changé depuis le calcul")
    if fingerprint(Path("config/data_manifest.json")) != manifest["data_manifest_sha256"]:
        raise ValueError("Le manifeste des données a changé depuis le calcul")
    current = {str(p) for p in Path("src").rglob("*.py")}
    if current != set(manifest["source_files"]):
        raise ValueError("La liste des fichiers du programme a changé")
    optional_path = Path("config/local_outputs.json")
    optional = json.loads(optional_path.read_text()) if optional_path.exists() else []
    for name, expected in {**manifest["source_files"], **manifest["tables"]}.items():
        path = Path(name)
        if not path.exists() and name in optional:
            continue
        if not path.exists() or fingerprint(path) != expected:
            raise ValueError(f"Fichier absent ou modifié depuis le calcul {name}")


def finish_publication():
    paths = [
        Path("README.md"),
        Path("ARTICLE.md"),
        Path("docs/templates/readme.md"),
        Path("docs/templates/article.md"),
        Path("rapport/rapport.pdf"),
        Path("rapport/rapport.typ"),
        *sorted(Path("results/figures").glob("*")),
    ]
    Path("results/publication_manifest.json").write_text(
        json.dumps({str(p): fingerprint(p) for p in paths}, indent=2) + "\n"
    )


def verify():
    check_results()
    for name, expected in json.loads(Path("results/publication_manifest.json").read_text()).items():
        if fingerprint(Path(name)) != expected:
            raise ValueError(f"Publication modifiée {name}")
    source = json.loads(Path("rapport/source_manifest.json").read_text())
    if fingerprint(Path("ARTICLE.md")) != source["sha256"]:
        raise ValueError("L'article et la source du PDF ne correspondent plus")
    print("Empreintes du code, des tables publiées, des figures et de l'article vérifiées.")
