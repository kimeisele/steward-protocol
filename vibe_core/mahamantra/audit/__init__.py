"""
AUDIT - The Ksetrajna Observing the Ksetra
==========================================

Usage:
    from vibe_core.mahamantra.audit.drift import DriftAuditor

    auditor = DriftAuditor()
    report = auditor.audit()
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

# Re-exports for the new audit system
from .audit_registry import AuditFinding, AuditRegistry, FindingSeverity, FindingStatus, get_registry
from .audit_dispatcher import AuditDispatcher, AuditorProtocol, get_dispatcher

__all__ = [
    "AuditDispatcher",
    "get_dispatcher",
    "AuditorProtocol",
    "AuditRegistry",
    "get_registry",
    "AuditFinding",
    "FindingStatus",
    "FindingSeverity",
]

