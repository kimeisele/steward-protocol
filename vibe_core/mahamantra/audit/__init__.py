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

# Re-exports only - NO BUSINESS LOGIC
from vibe_core.mahamantra.audit.drift import DriftAuditor
from vibe_core.mahamantra.protocols._audit import (
    AuditProtocol,
    AuditReport,
    LineageViolation,
    SSOTViolation,
    ProtocolViolation,
)

__all__ = [
    "DriftAuditor",
    "AuditProtocol",
    "AuditReport",
    "LineageViolation",
    "SSOTViolation",
    "ProtocolViolation",
]

