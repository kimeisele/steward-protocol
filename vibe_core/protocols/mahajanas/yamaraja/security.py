"""
YAMARAJA SECURITY PROTOCOL - The Eternal Guardian
==================================================

Sanskrit: Yamaraja = Lord of Death/Justice
         Kala = Time (Yamaraja is also called Kala)

"Even Brahma fears Yamaraja. Only the Holy Name is above him."

This is THE SecurityProtocol that unifies ALL security layers:
- Level -1: Substrate (Protocols themselves)
- Level 0: Kernel (Vishnu protection)
- Level 1: Defense (4 Regulating Principles)
- Level 2: NAGA (Active threat detection)
- Level 3: Plugins (Event interception)

DESIGN FOR 10,000 YEARS:
========================
1. FRACTAL: Same pattern at every level (judge → verdict → record)
2. SCALABLE: SecurityLevel can be extended without breaking
3. SELF-MANAGING: Yamaraja judges even himself (recursive audit)
4. CAPABILITY-BASED: No hardcoded permissions, all derived from capabilities
5. WATERTIGHT: No Dict[str, Any], all typed

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────────────┐
    │                    YAMARAJA (SecurityProtocol)               │
    │  "The Final Judge - Even He Bows to the Holy Name"          │
    ├─────────────────────────────────────────────────────────────┤
    │  SecurityLevel.SUBSTRATE (-1)  │  Protocol integrity        │
    │  SecurityLevel.KERNEL (0)      │  Vishnu/Vajra protection   │
    │  SecurityLevel.DEFENSE (1)     │  4 Regulating Principles   │
    │  SecurityLevel.NAGA (2)        │  Active threat detection   │
    │  SecurityLevel.PLUGIN (3)      │  Event interception        │
    └─────────────────────────────────────────────────────────────┘

GAD-000 Compliance:
    ✓D Discoverability - All capabilities listed
    ✓O Observability - SecurityAuditRecord logs all
    ✓P Parseability - Typed errors with codes
    ✓C Composability - Can be combined with any Protocol
    ✓I Idempotency - judge() is deterministic
    ✓R Recoverability - State persists in ledger
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x2ffe7d18"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, auto
from typing import (
    TYPE_CHECKING,
    Callable,
    Final,
    FrozenSet,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

if TYPE_CHECKING:
    from vibe_core.protocols.defense import (
        IDataSanitizer,
        INetworkGuard,
        IOutputVerifier,
        IResourceManager,
    )

from . import Judgeable, JudgmentRecord, Verdict, YamarajaProtocol


# =============================================================================
# SECURITY LEVELS - Fractal Protection Hierarchy
# =============================================================================


class SecurityLevel(IntEnum):
    """
    Protection levels from substrate (-1) to application (3+).

    LOWER = STRICTER (more fundamental)
    Violations at lower levels cascade UP.

    Level -1 violations → System halt (Dharma broken)
    Level 0 violations → Kernel panic (Vishnu protection)
    Level 1 violations → Automatic healing attempted
    Level 2 violations → NAGA response (bite/quarantine)
    Level 3 violations → Plugin handles (log/alert)
    """

    SUBSTRATE = -1  # Protocol integrity (Level -1, the foundation)
    KERNEL = 0  # Vishnu/Vajra protection (Level 0)
    DEFENSE = 1  # 4 Regulating Principles (DAYA, SATYAM, TAPAS, SAUCAM)
    NAGA = 2  # Active threat detection (Takshaka, Kaliya)
    PLUGIN = 3  # Event interception (naga_guard, integrity_guard)
    APPLICATION = 4  # User-level security (agent permissions)

    @property
    def is_critical(self) -> bool:
        """Levels below DEFENSE are critical - violations may halt system."""
        return self.value <= SecurityLevel.KERNEL.value

    @property
    def response_type(self) -> str:
        """What happens when this level is violated."""
        responses = {
            SecurityLevel.SUBSTRATE: "SYSTEM_HALT",
            SecurityLevel.KERNEL: "KERNEL_PANIC",
            SecurityLevel.DEFENSE: "AUTO_HEAL",
            SecurityLevel.NAGA: "NAGA_RESPONSE",
            SecurityLevel.PLUGIN: "LOG_ALERT",
            SecurityLevel.APPLICATION: "USER_NOTIFY",
        }
        return responses.get(self, "UNKNOWN")


# =============================================================================
# WATERTIGHT TYPEDDICTS - Security Data Contracts
# =============================================================================


class SecurityCapability(TypedDict):
    """A single security capability. WATERTIGHT."""

    name: str  # e.g., "read_file", "network_access"
    level: int  # SecurityLevel value
    granted_by: str  # Who granted this
    granted_at: str  # ISO timestamp
    expires_at: Optional[str]  # None = never expires
    conditions: List[str]  # Conditions that must hold


class SecurityViolation(TypedDict):
    """A security violation record. WATERTIGHT."""

    violation_id: str
    level: int  # SecurityLevel value
    source: str  # What caused this
    target: str  # What was targeted
    violation_type: str  # "unauthorized_access", "injection", etc.
    details: str
    timestamp: str
    response_taken: str  # What action was taken


class SecurityAuditRecord(TypedDict):
    """Complete audit record for security operations. WATERTIGHT."""

    audit_id: str
    operation: str  # "judge", "grant", "revoke", "check"
    subject: str
    level: int
    verdict: str  # Verdict value
    reason: str
    timestamp: str
    duration_ms: float
    holy_name_checked: bool  # Ajamil exception


class SecurityStateSnapshot(TypedDict):
    """Snapshot of security state. WATERTIGHT."""

    snapshot_id: str
    timestamp: str
    active_level: int
    capabilities_count: int
    violations_24h: int
    health_score: float  # 0.0 to 1.0


# =============================================================================
# SECURITY SUBJECT - What Can Be Secured
# =============================================================================


@dataclass(frozen=True)
class SecuredSubject(Judgeable):
    """
    Extension of Judgeable specifically for security operations.

    Adds capability tracking and security-specific metadata.
    """

    capabilities: FrozenSet[str] = frozenset()
    security_level: SecurityLevel = SecurityLevel.APPLICATION
    last_audit: Optional[str] = None  # ISO timestamp

    def has_capability(self, capability: str) -> bool:
        """Check if subject has a specific capability."""
        return capability in self.capabilities

    def to_judgeable(self) -> Judgeable:
        """Convert to base Judgeable for Yamaraja."""
        return Judgeable(
            subject_type=self.subject_type,
            subject_id=self.subject_id,
            karma_history=list(self.karma_history) if self.karma_history else [],
        )


# =============================================================================
# SECURITY PROTOCOL - The Unified Interface
# =============================================================================


@runtime_checkable
class SecurityProtocol(YamarajaProtocol, Protocol):
    """
    The Unified Security Protocol - Owned by Yamaraja.

    Extends YamarajaProtocol with:
    - Capability management (grant/revoke/check)
    - Security levels (substrate to application)
    - Defense integration (4 Regulating Principles)
    - Audit trail (all operations logged)

    FRACTAL DESIGN:
    This same protocol works at EVERY level:
    - Substrate: Protocols checking protocols
    - Kernel: Vishnu checking kernel operations
    - Defense: 4 Principles checking data/output/resources/network
    - NAGA: NAGAs checking threats
    - Plugin: Plugins checking events

    10,000 YEAR DESIGN:
    - All methods return typed results (no Dict[str, Any])
    - All state changes are logged to ledger
    - Self-auditing: audit_self() checks the security system itself
    """

    # === LEVEL MANAGEMENT ===

    @property
    def active_level(self) -> SecurityLevel:
        """Get the currently active security level."""
        ...

    def set_level(self, level: SecurityLevel, reason: str) -> bool:
        """
        Change security level. Returns True if successful.

        Lower levels require higher authority.
        Level -1 (SUBSTRATE) can only be set by sovereign.
        """
        ...

    def enforce_level(self, minimum: SecurityLevel) -> None:
        """
        Ensure current level is at least 'minimum'.

        Raises SecurityError if active_level > minimum.
        (Lower number = stricter security)
        """
        ...

    # === CAPABILITY MANAGEMENT ===

    def grant_capability(
        self,
        subject_id: str,
        capability: str,
        granter_id: str,
        expires_at: Optional[str] = None,
    ) -> SecurityCapability:
        """
        Grant a capability to a subject.

        Returns the granted capability record.
        All grants are logged to ledger.
        """
        ...

    def revoke_capability(
        self,
        subject_id: str,
        capability: str,
        revoker_id: str,
        reason: str,
    ) -> bool:
        """
        Revoke a capability from a subject.

        Returns True if revoked, False if not found.
        All revocations are logged to ledger.
        """
        ...

    def check_capability(
        self,
        subject_id: str,
        capability: str,
    ) -> bool:
        """
        Check if subject has capability.

        Fast path - no logging for checks (too noisy).
        """
        ...

    def list_capabilities(self, subject_id: str) -> List[SecurityCapability]:
        """List all capabilities for a subject."""
        ...

    # === DEFENSE INTEGRATION (4 Regulating Principles) ===

    def get_sanitizer(self) -> "IDataSanitizer":
        """Get DAYA (Mercy) - Data sanitization."""
        ...

    def get_verifier(self) -> "IOutputVerifier":
        """Get SATYAM (Truth) - Output verification."""
        ...

    def get_resource_manager(self) -> "IResourceManager":
        """Get TAPAS (Austerity) - Resource limits."""
        ...

    def get_network_guard(self) -> "INetworkGuard":
        """Get SAUCAM (Cleanliness) - Network protection."""
        ...

    # === AUDIT & OBSERVABILITY ===

    def record_violation(
        self,
        level: SecurityLevel,
        source: str,
        target: str,
        violation_type: str,
        details: str,
    ) -> SecurityViolation:
        """
        Record a security violation.

        Returns the violation record.
        Triggers appropriate response based on level.
        """
        ...

    def get_audit_log(
        self,
        since: Optional[str] = None,
        level: Optional[SecurityLevel] = None,
        limit: int = 100,
    ) -> List[SecurityAuditRecord]:
        """
        Get audit log entries.

        Args:
            since: ISO timestamp (default: last 24h)
            level: Filter by level (default: all)
            limit: Max entries (default: 100)
        """
        ...

    def audit_self(self) -> SecurityStateSnapshot:
        """
        Self-audit: Check the security system itself.

        FRACTAL: Yamaraja judges Yamaraja.
        Returns snapshot of security health.
        """
        ...

    # === THREAT RESPONSE ===

    def escalate(
        self,
        violation: SecurityViolation,
        to_level: SecurityLevel,
    ) -> None:
        """
        Escalate a violation to a higher (stricter) level.

        Used when automated response is insufficient.
        """
        ...

    def quarantine(
        self,
        subject_id: str,
        reason: str,
        duration_seconds: int = 3600,
    ) -> bool:
        """
        Quarantine a subject (temporary capability revocation).

        Returns True if quarantined.
        All quarantines are logged.
        """
        ...


# =============================================================================
# NULL IMPLEMENTATION - For Testing
# =============================================================================


class NullSecurityProtocol:
    """
    Maximum mercy implementation (for testing).

    All operations succeed. No real security.
    Like NullYamaraja, grants mercy to all.
    """

    _active_level: SecurityLevel = SecurityLevel.APPLICATION
    _capabilities: dict = field(default_factory=dict)  # type: ignore

    @property
    def active_level(self) -> SecurityLevel:
        return self._active_level

    def set_level(self, level: SecurityLevel = None, reason: str = "") -> bool:
        self._active_level = level
        return True

    def enforce_level(self, minimum: SecurityLevel = None) -> None:
        pass  # Always passes

    def grant_capability(
        self,
        subject_id: str = "",
        capability: str = "",
        granter_id: str = "",
        expires_at: Optional[str] = None,
    ) -> SecurityCapability:
        return SecurityCapability(
            name=capability,
            level=SecurityLevel.APPLICATION.value,
            granted_by=granter_id,
            granted_at=datetime.now().isoformat(),
            expires_at=expires_at,
            conditions=[],
        )

    def revoke_capability(
        self,
        subject_id: str = "",
        capability: str = "",
        revoker_id: str = "",
        reason: str = "",
    ) -> bool:
        return True

    def check_capability(self, subject_id: str = "", capability: str = "") -> bool:
        return True  # Maximum mercy

    def list_capabilities(self, subject_id: str = "") -> List[SecurityCapability]:
        return []

    def judge(self, subject: Union[Judgeable, object] = None) -> Verdict:
        return Verdict.MERCY  # Ajamil exception always

    def check_holy_name(self, subject: Union[Judgeable, object] = None) -> bool:
        return True  # Always grant mercy

    def assert_truth(self, condition: bool = False, reason: str = "") -> None:
        pass  # No assertion

    def get_karma_balance(self) -> float:
        return 0.0

    def get_sanitizer(self) -> "IDataSanitizer":
        from vibe_core.naga.defenses.daya import DataSanitizer

        return DataSanitizer()

    def get_verifier(self) -> "IOutputVerifier":
        from vibe_core.naga.defenses.satyam import OutputVerifier

        return OutputVerifier()

    def get_resource_manager(self) -> "IResourceManager":
        from vibe_core.naga.defenses.tapas import ResourceManager

        return ResourceManager()

    def get_network_guard(self) -> "INetworkGuard":
        from vibe_core.naga.defenses.saucam import NetworkGuard

        return NetworkGuard()

    def record_violation(
        self,
        level: SecurityLevel = None,
        source: str = "",
        target: str = "",
        violation_type: str = "",
        details: str = "",
    ) -> SecurityViolation:
        return SecurityViolation(
            violation_id="null",
            level=level.value,
            source=source,
            target=target,
            violation_type=violation_type,
            details=details,
            timestamp=datetime.now().isoformat(),
            response_taken="LOGGED",
        )

    def get_audit_log(
        self,
        since: Optional[str] = None,
        level: Optional[SecurityLevel] = None,
        limit: int = 100,
    ) -> List[SecurityAuditRecord]:
        return []

    def audit_self(self) -> SecurityStateSnapshot:
        return SecurityStateSnapshot(
            snapshot_id="null",
            timestamp=datetime.now().isoformat(),
            active_level=self._active_level.value,
            capabilities_count=0,
            violations_24h=0,
            health_score=1.0,
        )

    def escalate(self, violation: SecurityViolation = None, to_level: SecurityLevel = None) -> None:
        pass

    def quarantine(
        self,
        subject_id: str = "",
        reason: str = "",
        duration_seconds: int = 3600,
    ) -> bool:
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol
    "SecurityProtocol",
    "NullSecurityProtocol",
    # Levels
    "SecurityLevel",
    # Types
    "SecurityCapability",
    "SecurityViolation",
    "SecurityAuditRecord",
    "SecurityStateSnapshot",
    "SecuredSubject",
]
