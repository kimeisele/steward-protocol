"""
SCALE - Atomic Scale Metrics (NITYANANDA)
=========================================

Returns scale metrics on-demand. No side effects.

Usage:
    from vibe_core.mahamantra.audit import scale
    metrics = scale.get()  # Returns Dict[str, int]
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from pathlib import Path
from typing import Dict, Any

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


def get(root: Path = None) -> Dict[str, Any]:
    """
    Get scale metrics using project_introspection.

    Returns:
        Dict with: total_files, total_lines, coverage_percent, broken_lineage
    """
    from vibe_core.mahamantra_research.project_introspection import measure_scale

    return measure_scale(root or Path.cwd())


__all__ = ["get"]
