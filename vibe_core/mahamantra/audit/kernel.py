"""
AUDIT KERNEL - Dispatcher-Driven Audit Orchestration
=====================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo" (BG 15.15)
"I am seated in everyone's heart"

The AuditKernel is a thin facade over the AuditDispatcher.
It does NOT manually wire auditors — the Dispatcher auto-discovers
all modules with `class Auditor` + `__position__` in the audit/ folder.

Usage:
    from vibe_core.mahamantra.audit.kernel import AuditKernel

    kernel = AuditKernel()
    kernel.run_all()                    # Run all auditors
    findings = kernel.findings()        # Get all findings
    report = kernel.summary()           # Get summary dict
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

import logging
from typing import Dict, List, Optional

from vibe_core.mahamantra.protocols._seed import PARAMPARA
from vibe_core.mahamantra.audit.audit_registry import (
    AuditFinding,
    AuditRegistry,
    FindingSeverity,
    FindingStatus,
    get_registry,
)
from vibe_core.mahamantra.audit.audit_dispatcher import (
    AuditDispatcher,
    get_dispatcher,
)

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("AUDIT.KERNEL")


class AuditKernel:
    """
    Audit Kernel — thin facade over AuditDispatcher + AuditRegistry.

    Auto-discovers all auditors in the audit/ folder.
    No manual wiring. No monolith. Protocol-driven.
    """

    def __init__(
        self,
        dispatcher: Optional[AuditDispatcher] = None,
        registry: Optional[AuditRegistry] = None,
    ) -> None:
        self._dispatcher = dispatcher or get_dispatcher()
        self._registry = registry or get_registry()

    def run_all(self) -> int:
        """Run all discovered auditors. Returns total finding count."""
        self._registry.clear()
        self._dispatcher.run_all()
        count = self._registry.count
        logger.info("Audit complete: %d findings from %d auditors",
                     count, len(self._dispatcher.auditors))
        return count

    def run_by_position(self, position: int) -> int:
        """Run a single auditor by position. Returns finding count."""
        before = self._registry.count
        self._dispatcher.run_by_position(position)
        return self._registry.count - before

    def findings(
        self,
        severity: Optional[FindingSeverity] = None,
        status: Optional[FindingStatus] = None,
    ) -> List[AuditFinding]:
        """Get findings, optionally filtered."""
        return self._registry.list_by(status=status, severity=severity)

    def critical_findings(self) -> List[AuditFinding]:
        """Get only critical findings."""
        return self._registry.list_by(severity=FindingSeverity.CRITICAL)

    def summary(self) -> Dict[str, object]:
        """Get a summary of the last audit run."""
        all_findings = self._registry.list_all()
        critical = [f for f in all_findings if f.severity == FindingSeverity.CRITICAL]
        warnings = [f for f in all_findings if f.severity == FindingSeverity.WARNING]
        info = [f for f in all_findings if f.severity == FindingSeverity.INFO]

        # Group by source
        by_source: Dict[str, int] = {}
        for f in all_findings:
            by_source[f.source] = by_source.get(f.source, 0) + 1

        return {
            "total": len(all_findings),
            "critical": len(critical),
            "warnings": len(warnings),
            "info": len(info),
            "is_pristine": len(critical) == 0,
            "auditors_discovered": len(self._dispatcher.auditors),
            "by_source": by_source,
        }

    @property
    def is_pristine(self) -> bool:
        """True if no critical findings exist."""
        return len(self.critical_findings()) == 0


__all__ = ["AuditKernel"]

