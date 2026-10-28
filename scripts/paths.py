"""Canonical project-root paths for all pipeline scripts.

Importing this module resolves the project root from the script location,
creates the output directories if missing, and anchors every `../`-relative
literal used by the pipeline scripts at the repository root regardless of
the caller's working directory.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
DATA_PROCESSED = DATA / "processed"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"
MANUSCRIPT = ROOT / "manuscript"

for _d in (DATA_PROCESSED, TABLES, FIGURES, MANUSCRIPT):
    _d.mkdir(parents=True, exist_ok=True)

# Keep legacy '../output/...' literals valid no matter the caller's cwd.
os.chdir(SCRIPTS)
