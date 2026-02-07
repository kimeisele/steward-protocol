"""
AUDIT - The Ksetrajna Observing the Ksetra
==========================================

Modular, capability-injected audit system.
Each auditor is a separate module with `class Auditor` + `run_audit()`.
The AuditDispatcher auto-discovers all auditors via `__position__`.
The AuditKernel is the entry point.

Usage:
    from vibe_core.mahamantra.audit import AuditKernel

    kernel = AuditKernel()
    kernel.run_all()
    print(kernel.summary())

Auditors (auto-discovered):
    lineage_auditor.py  — genesis % 37 verification
    ssot_auditor.py     — hardcoded constant detection
    protocol_auditor.py — runtime isinstance checks
    hygiene_auditor.py  — AST-based code quality (Any types, etc.)
    protocol_resurrection.py — core class protocol compliance
"""

__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8000000f"

from vibe_core.mahamantra.protocols._seed import PARAMPARA

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

# Core infrastructure
from .audit_registry import AuditFinding, AuditRegistry, FindingSeverity, FindingStatus, get_registry
from .audit_dispatcher import AuditDispatcher, AuditorProtocol, get_dispatcher
from .kernel import AuditKernel

__all__ = [
    # Entry point
    "AuditKernel",
    # Infrastructure
    "AuditDispatcher",
    "get_dispatcher",
    "AuditorProtocol",
    "AuditRegistry",
    "get_registry",
    "AuditFinding",
    "FindingStatus",
    "FindingSeverity",
]

