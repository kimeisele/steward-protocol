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

__all__ = [
    "AuditFinding", "AuditRegistry", "FindingStatus", "FindingSeverity",
    "SourceCache", "get_registry", "get_source_cache",
]

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple, runtime_checkable

_audit_logger = logging.getLogger("AUDIT.CACHE")


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


# =============================================================================
# SOURCE CACHE — One rglob to rule them all
# =============================================================================


class SourceCache:
    """
    Shared file-content cache for all auditors.

    Problem: lineage_auditor, ssot_auditor, hygiene_auditor, drift.py all do
    independent rglob("*.py") + read_text() over the same root. That's 4-5×
    the same FS scan + file reads.

    Solution: Scan once, cache (path, content) tuples. All auditors consume
    from the same cache. Cache is invalidated explicitly or on root change.
    """

    __slots__ = ("_root", "_files")

    def __init__(self, root: Optional[Path] = None) -> None:
        self._root = Path(root or "vibe_core/mahamantra")
        self._files: Optional[Tuple[Tuple[Path, str], ...]] = None

    @property
    def root(self) -> Path:
        return self._root

    def scan(self) -> Tuple[Tuple[Path, str], ...]:
        """Return cached (path, content) pairs. Scans FS on first call only."""
        if self._files is not None:
            return self._files

        result: List[Tuple[Path, str]] = []
        for path in self._root.rglob("*.py"):
            if "__pycache__" in str(path):
                continue
            try:
                content = path.read_text()
            except Exception:
                continue
            result.append((path, content))

        self._files = tuple(result)
        _audit_logger.debug(
            "SourceCache: scanned %d files from %s", len(self._files), self._root
        )
        return self._files

    def invalidate(self) -> None:
        """Force rescan on next access."""
        self._files = None


_source_cache: Optional[SourceCache] = None


def get_source_cache(root: Optional[Path] = None) -> SourceCache:
    """Get the singleton SourceCache instance."""
    global _source_cache
    if _source_cache is None or (root and _source_cache.root != Path(root)):
        _source_cache = SourceCache(root)
    return _source_cache
