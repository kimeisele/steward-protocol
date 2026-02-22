"""
Stable path anchors for substrate modules.

These paths are computed ONCE from this file's location (which is always
at substrate root) so that other modules can use them regardless of where
they've been moved to within the substrate tree.

Usage:
    from vibe_core.mahamantra.substrate._paths import SUBSTRATE_ROOT, MAHAMANTRA_ROOT, VIBE_CORE_ROOT
"""

from __future__ import annotations

from pathlib import Path

# substrate/ directory
SUBSTRATE_ROOT: Path = Path(__file__).resolve().parent

# mahamantra/ directory (substrate/..)
MAHAMANTRA_ROOT: Path = SUBSTRATE_ROOT.parent

# vibe_core/ directory (substrate/../..)
VIBE_CORE_ROOT: Path = MAHAMANTRA_ROOT.parent

# project root (vibe_core/..)
PROJECT_ROOT: Path = VIBE_CORE_ROOT.parent

# data/ directory (mahamantra/data)
DATA_DIR: Path = MAHAMANTRA_ROOT / "data"
