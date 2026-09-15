"""Exécute le parcours pédagogique sans relancer la recherche."""

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

for name, folder in [("IPYTHONDIR", "ipython"), ("JUPYTER_RUNTIME_DIR", "jupyter")]:
    directory = Path.cwd() / ".cache" / folder
    directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault(name, str(directory))

path = Path("notebooks/01_comprendre.ipynb")
book = nbformat.read(path, as_version=4)
NotebookClient(
    book, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(Path.cwd())}}
).execute()
nbformat.write(book, path)
