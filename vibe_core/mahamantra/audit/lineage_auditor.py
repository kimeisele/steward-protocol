"""
LINEAGE AUDITOR - Genesis Byte Verification
============================================

Verifies that every __genesis__ byte in the codebase is divisible by PARAMPARA (37).
Broken lineage = broken parampara chain = system integrity violation.

Implements AuditorProtocol: class Auditor + run_audit() → List[AuditFinding].
Auto-discovered by AuditDispatcher via __position__ + Auditor class.
"""

from __future__ import annotations

__mahajana__ = "yamaraja"
__position__ = 0  # First auditor to run
__genesis__ = "0x8000000f"

import hashlib
import logging
import re
from pathlib import Path
from typing import List, Optional

from vibe_core.mahamantra.audit.audit_registry import AuditFinding, FindingSeverity, get_source_cache
from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("AUDIT.LINEAGE")


class Auditor:
    """
    Lineage Auditor — verifies genesis % PARAMPARA == 0 for all modules.

    Single responsibility: lineage verification only.
    Healing capability: can compute and fix correct genesis bytes.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self._root = Path(root or "vibe_core/mahamantra")

    def run_audit(self) -> List[AuditFinding]:
        """AuditorProtocol: scan all .py files for broken lineage."""
        findings: List[AuditFinding] = []
        cache = get_source_cache(self._root)

        for path, content in cache.scan():
            gen_match = re.search(r'__genesis__\s*[=:]\s*["\']?(0x[0-9a-fA-F]+)', content)
            if not gen_match:
                continue

            genesis_str = gen_match.group(1)
            try:
                genesis_val = int(genesis_str, 16)
            except ValueError:
                findings.append(
                    AuditFinding(
                        source="lineage_auditor",
                        position=__position__,
                        mahajana=__mahajana__,
                        description=f"Invalid genesis format: {genesis_str}",
                        file_path=str(path),
                        severity=FindingSeverity.CRITICAL,
                    )
                )
                continue

            remainder = genesis_val % PARAMPARA
            if remainder != 0:
                mj = re.search(r'__mahajana__\s*[=:]\s*["\'](\w+)["\']', content)
                pos = re.search(r"__position__\s*[=:]\s*(\d+)", content)
                mahajana = mj.group(1) if mj else "unknown"
                position = int(pos.group(1)) if pos else -1

                correct = self._compute_genesis(mahajana, position)
                findings.append(
                    AuditFinding(
                        source="lineage_auditor",
                        position=__position__,
                        mahajana=__mahajana__,
                        description=(f"Broken lineage: {genesis_str} % {PARAMPARA} = {remainder}. Correct: {correct}"),
                        file_path=str(path),
                        severity=FindingSeverity.CRITICAL,
                    )
                )

        logger.info(
            "Lineage audit: %d findings from %s",
            len(findings),
            self._root,
        )
        return findings

    def heal(self, dry_run: bool = True) -> List[str]:
        """Fix all broken lineages. Returns list of fixed paths."""
        findings = self.run_audit()
        fixed: List[str] = []

        for finding in findings:
            if not finding.file_path:
                continue
            path = Path(finding.file_path)
            content = path.read_text()

            mj = re.search(r'__mahajana__\s*[=:]\s*["\'](\w+)["\']', content)
            pos = re.search(r"__position__\s*[=:]\s*(\d+)", content)
            if not mj or not pos:
                continue

            correct = self._compute_genesis(mj.group(1), int(pos.group(1)))
            new_content = re.sub(
                r'(__genesis__\s*[=:]\s*["\']?)0x[0-9a-fA-F]+(["\']?)',
                rf"\g<1>{correct}\g<2>",
                content,
            )
            if not dry_run:
                path.write_text(new_content)
            fixed.append(str(path))

        return fixed

    @staticmethod
    def _compute_genesis(mahajana: str, position: int) -> str:
        """Compute correct genesis byte from identity."""
        identity = f"{mahajana}:{position}"
        raw = hashlib.sha256(identity.encode()).hexdigest()[:8]
        base = int(raw, 16)
        return f"0x{base - (base % PARAMPARA):08x}"


__all__ = ["Auditor"]
