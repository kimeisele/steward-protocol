"""
DRIFT - Atomic Drift Detection (GADADHARA)
==========================================

Returns drift items on-demand. No side effects.

Usage:
    from vibe_core.mahamantra.audit import drift
    items = drift.get()  # Returns List[DriftItem]
    broken = drift.broken_lineage()  # Returns files with bad genesis
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


@dataclass
class DriftItem:
    """A single drift finding."""
    drift_type: str
    file_path: str
    description: str
    severity: str = "critical"


def get(root: Path = None) -> List[DriftItem]:
    """
    Get all drift items (broken lineage, ssot violations).
    
    Returns:
        List of DriftItem objects
    """
    items = []
    items.extend(broken_lineage(root))
    return items


def broken_lineage(root: Path = None) -> List[DriftItem]:
    """
    Find files with broken lineage (genesis % 37 != 0).
    Uses project_introspection.
    """
    from vibe_core.mahamantra.research.project_introspection import scan_codebase, find_gaps
    files, _ = scan_codebase(root or Path.cwd())
    gaps = find_gaps(files)
    
    items = []
    for g in gaps:
        if g.gap_type == "BROKEN_LINEAGE":
            items.append(DriftItem(
                drift_type="BROKEN_LINEAGE",
                file_path=str(g.file_path),
                description=g.description,
                severity="critical"
            ))
    return items


def count(root: Path = None) -> Dict[str, int]:
    """Get drift counts by type."""
    items = get(root)
    counts: Dict[str, int] = {}
    for item in items:
        counts[item.drift_type] = counts.get(item.drift_type, 0) + 1
    return counts


__all__ = ["DriftItem", "get", "broken_lineage", "count"]

