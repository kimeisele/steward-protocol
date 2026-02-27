"""
SSOT AUDITOR - Hardcoded Sacred Constants Detection
====================================================

Detects hardcoded sacred constants that should be imported from _seed.py.
SSOT = Single Source of Truth. Constants must flow from protocols/_seed.py,
never be redefined locally.

Implements AuditorProtocol: class Auditor + run_audit() → List[AuditFinding].
Auto-discovered by AuditDispatcher via __position__ + Auditor class.
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 1  # Second auditor to run
__genesis__ = "0x8000000f"

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity, get_source_cache
from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("AUDIT.SSOT")

# Sacred constants that MUST be imported, never hardcoded.
# Map: constant_name → value
SACRED_CONSTANTS: Dict[str, int] = {
    "PARAMPARA": 37,
    "WORDS": 16,
    "TRINITY": 3,
    "HARE_COUNT": 8,
    "KRISHNA_COUNT": 4,
    "RAMA_COUNT": 4,
    "PANCHA": 5,
    "HALVES": 2,
    "SHARANAGATI": 6,
    "NAVA": 9,
    "MAHAJANA_COUNT": 12,
    "GITA_CHAPTERS": 18,
    "KSHETRA": 24,
    "MALA": 108,
    "LILA": 48,
    "QUALITIES": 64,
    "MAHA_QUANTUM": 137,
}

# Files that ARE the SSOT — skip them
SSOT_FILES: Tuple[str, ...] = ("_axioms.py", "_seed.py", "_singularity.py")


class Auditor:
    """
    SSOT Auditor — detects hardcoded sacred constants.

    Single responsibility: find constants that should be imports.
    Does NOT heal (that's heal_mahamantra.py's job via CST).
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self._root = Path(root or "vibe_core/mahamantra")

    def run_audit(self) -> List[AuditFinding]:
        """AuditorProtocol: scan for hardcoded sacred constants."""
        findings: List[AuditFinding] = []
        cache = get_source_cache(self._root)

        for path, content in cache.scan():
            if any(ssot in path.name for ssot in SSOT_FILES):
                continue

            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and imports
                if stripped.startswith("#") or "import" in stripped:
                    continue
                # Skip assert lines (verification is fine)
                if stripped.startswith("assert"):
                    continue

                for const_name, const_val in SACRED_CONSTANTS.items():
                    # Match: CONST_NAME = value (redefinition)
                    pattern = rf"\b{const_name}\s*[:=]\s*{const_val}\b"
                    if re.search(pattern, line):
                        findings.append(
                            AuditFinding(
                                source="ssot_auditor",
                                position=__position__,
                                mahajana=__mahajana__,
                                description=(
                                    f"Hardcoded sacred constant: {const_name} = {const_val}. "
                                    f"Import from protocols._seed instead."
                                ),
                                file_path=str(path),
                                line_number=i,
                                severity=FindingSeverity.WARNING,
                            )
                        )

        logger.info(
            "SSOT audit: %d findings from %s",
            len(findings),
            self._root,
        )
        return findings


__all__ = ["Auditor"]
