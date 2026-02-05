"""
AUDIT REGISTRY - The Book of Dharma
====================================

"yathākāśa-sthito nityaṁ vāyuḥ sarvatra-go mahān
tathā sarvāṇi bhūtāni mat-sthānīty upadhāraya"

"Know that as the mighty wind, blowing everywhere, rests always in the sky,
all created beings rest in Me." (BG 9.6)

THE LAW:
========
    - All audit findings are recorded here.
    - The Registry is the Single Source of Truth for system health.
    - Findings are immutable; only their status can change.

This module provides the data structures and the central registry for tracking
all audit findings from all position-specific auditors.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x..." # TODO: Add genesis byte

__all__ = ["AuditFinding", "AuditRegistry", "FindingStatus", "FindingSeverity", "get_registry"]

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable


class FindingStatus(Enum):
    """Lifecycle of an audit finding."""
    IDENTIFIED = "identified"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class FindingSeverity(Enum):
    """Severity of an audit finding."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AuditFinding:
    """A single, immutable audit finding."""

    # Fields without default values must come first
    source: str  # e.g., "DriftAuditor.lineage", "ProtocolResurrection"
    position: int
    mahajana: str
    description: str

    # Fields with default values
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    severity: FindingSeverity = FindingSeverity.WARNING
    status: FindingStatus = FindingStatus.IDENTIFIED
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def resolve(self) -> None:
        """Mark the finding as resolved."""
        self.status = FindingStatus.RESOLVED

    def ignore(self) -> None:
        """Mark the finding as ignored."""
        self.status = FindingStatus.IGNORED


@runtime_checkable
class AuditRegistryProtocol(Protocol):
    """The abstract protocol for any audit registry."""

    def register(self, finding: AuditFinding) -> None:
        """Register a new finding."""
        ...

    def get(self, finding_id: str) -> Optional[AuditFinding]:
        """Retrieve a finding by its ID."""
        ...

    def list_all(self) -> List[AuditFinding]:
        """Return a list of all findings."""
        ...

    def list_by(self, status: Optional[FindingStatus] = None, severity: Optional[FindingSeverity] = None) -> List[AuditFinding]:
        """Filter findings by status or severity."""
        ...

    def clear(self) -> None:
        """Clear all findings from the registry."""
        ...

    @property
    def count(self) -> int:
        """Return the total number of findings."""
        ...


class AuditRegistry(AuditRegistryProtocol):
    """The central, in-memory registry for all audit findings."""

    def __init__(self) -> None:
        self._findings: Dict[str, AuditFinding] = {}

    def register(self, finding: AuditFinding) -> None:
        """Register a new finding."""
        if finding.id in self._findings:
            # This should not happen with UUIDs
            return
        self._findings[finding.id] = finding

    def get(self, finding_id: str) -> Optional[AuditFinding]:
        """Retrieve a finding by its ID."""
        return self._findings.get(finding_id)

    def list_all(self) -> List[AuditFinding]:
        """Return a list of all findings."""
        return list(self._findings.values())

    def list_by(self, status: Optional[FindingStatus] = None, severity: Optional[FindingSeverity] = None) -> List[AuditFinding]:
        """Filter findings by status or severity."""
        results = self.list_all()
        if status:
            results = [f for f in results if f.status == status]
        if severity:
            results = [f for f in results if f.severity == severity]
        return results

    def clear(self) -> None:
        """Clear all findings from the registry."""
        self._findings.clear()

    @property
    def count(self) -> int:
        """Return the total number of findings."""
        return len(self._findings)


# Singleton instance
_registry: Optional[AuditRegistry] = None

def get_registry() -> AuditRegistry:
    """Get the singleton AuditRegistry instance."""
    global _registry
    if _registry is None:
        _registry = AuditRegistry()
    return _registry
