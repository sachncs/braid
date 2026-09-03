"""Shared test fixtures."""

import sys
from pathlib import Path

# Make sure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
