"""
GAPS - Atomic Gap Analysis (ADVAITA)
====================================

Returns gaps on-demand. No side effects.

Usage:
    from vibe_core.mahamantra.audit import gaps
    all_gaps = gaps.get()  # Returns List[Gap]
    critical = gaps.critical()  # Returns only critical gaps
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from pathlib import Path
from typing import List, Any

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


def get(root: Path = None) -> List[Any]:
    """
    Get all gaps using project_introspection.
    
    Returns:
        List of Gap objects with file_path, gap_type, description, severity
    """
    from vibe_core.mahamantra_research.project_introspection import scan_codebase, find_gaps
    files, _ = scan_codebase(root or Path.cwd())
    return find_gaps(files)


def critical(root: Path = None) -> List[Any]:
    """Get only critical gaps."""
    return [g for g in get(root) if g.severity == "critical"]


def by_type(gap_type: str, root: Path = None) -> List[Any]:
    """Get gaps of a specific type."""
    return [g for g in get(root) if g.gap_type == gap_type]


__all__ = ["get", "critical", "by_type"]

