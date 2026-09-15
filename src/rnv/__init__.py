"""Faire durer son épargne sans trop réduire son niveau de vie"""

__version__ = "1.0.0"

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".cache" / "matplotlib"))
