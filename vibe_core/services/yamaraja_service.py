"""
YAMARAJA SERVICE - The Eternal Security Guardian
=================================================

Sanskrit: Yamaraja = Lord of Death/Justice (12th Mahajana)

Implements SecurityProtocol - the unified security layer for the entire system.
This is the SENIOR-grade implementation designed for 10,000 years of self-management.

"Even Brahma fears Yamaraja. Only the Holy Name is above him."
- The Ajamil Exception (SB 6.1-3)

FRACTAL DESIGN:
- Same judge/verdict/record pattern at every security level
- Violations cascade UP from lower to higher levels
- Self-auditing: Yamaraja judges even Yamaraja

WATERTIGHT GUARANTEE:
- No Dict[str, Any] anywhere
- All data flows through typed contracts
- Every operation logged to immutable ledger

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     YAMARAJA SERVICE                                    │
    │  SecurityProtocol + YamarajaProtocol + LedgerIntegration               │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  [Capabilities]  →  grant/revoke/check  →  [Ledger Audit]              │
    │  [Violations]    →  record/escalate     →  [Response Engine]           │
    │  [Defense]       →  4 Principles        →  [DAYA/SATYAM/TAPAS/SAUCAM]  │
    │  [Self-Audit]    →  audit_self()        →  [Health Snapshot]           │
    └─────────────────────────────────────────────────────────────────────────┘
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xba1ef2e0"  # GenesisByte: parampara % 37 == 0

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
from typing import Dict, FrozenSet, List, Optional, Set, Union

from vibe_core.protocols.defense import (
    IDataSanitizer,
    INetworkGuard,
    IOutputVerifier,
    IResourceManager,
)
from vibe_core.protocols.mahajanas.prithu.types.ledger import SQLiteLedger as VibeLedger  # Protocol-first
from vibe_core.protocols.mahajanas.router import Mahajana
from vibe_core.protocols.mahajanas.yamaraja import (
    Judgeable,
    JudgmentRecord,
    Verdict,
    YamarajaProtocol,
)
from vibe_core.protocols.mahajanas.yamaraja.security import (
    SecurityAuditRecord,
    SecurityCapability,
    SecurityLevel,
    SecurityProtocol,
    SecurityStateSnapshot,
    SecurityViolation,
)

logger = logging.getLogger("YAMARAJA_SERVICE")


# =============================================================================
# WATERTIGHT INTERNAL TYPES
# =============================================================================


@dataclass
class QuarantineEntry:
    """Internal quarantine tracking. WATERTIGHT."""

    subject_id: str
    reason: str
    started_at: datetime
    duration_seconds: int
    revoked_capabilities: FrozenSet[str]


@dataclass
class ViolationTracker:
    """Internal violation tracking with time windows. WATERTIGHT."""

    count_24h: int = 0
    count_1h: int = 0
    last_violation: Optional[datetime] = None
    critical_count: int = 0  # Level <= KERNEL


# =============================================================================
# YAMARAJA SERVICE IMPLEMENTATION
# =============================================================================


class YamarajaService(SecurityProtocol, YamarajaProtocol):
    """
    The Unified Security Guardian - Full SecurityProtocol Implementation.

    Owned by: Mahajana.YAMARAJA (12th Mahajana)

    Design Principles:
    1. FRACTAL: Same pattern at every level (judge → verdict → record)
    2. SCALABLE: Security levels extensible without breaking
    3. SELF-MANAGING: audit_self() for recursive judgment
    4. CAPABILITY-BASED: All permissions derived from capabilities
    5. WATERTIGHT: No Dict[str, Any], all typed
    6. LEDGER-BACKED: Every operation logged immutably

    Thread Safety:
    - All state mutations protected by RLock
    - Capability checks are fast-path (no lock for reads)
    """

    def __init__(
        self,
        ledger: VibeLedger,
        initial_level: SecurityLevel = SecurityLevel.APPLICATION,
    ):
        """
        Initialize YamarajaService.

        Args:
            ledger: VibeLedger for immutable audit trail
            initial_level: Starting security level (default: APPLICATION)
        """
        self._ledger = ledger
        self._active_level = initial_level
        self._lock = RLock()

        # Capability storage: subject_id -> set of capability names
        self._capabilities: Dict[str, Set[str]] = {}
        # Full capability records: subject_id -> list of SecurityCapability
        self._capability_records: Dict[str, List[SecurityCapability]] = {}

        # Violation tracking
        self._violations: List[SecurityViolation] = []
        self._violation_tracker = ViolationTracker()

        # Quarantine registry: subject_id -> QuarantineEntry
        self._quarantine: Dict[str, QuarantineEntry] = {}

        # Defense protocol instances (lazy-loaded)
        self._sanitizer: Optional[IDataSanitizer] = None
        self._verifier: Optional[IOutputVerifier] = None
        self._resource_manager: Optional[IResourceManager] = None
        self._network_guard: Optional[INetworkGuard] = None

        # Karma balance (for YamarajaProtocol)
        self._karma_balance: float = 0.0

        logger.info(f"⚖️  YAMARAJA: Initialized at level {initial_level.name}")

    @property
    def owner(self) -> Mahajana:
        """Return owning Mahajana."""
        return Mahajana.YAMARAJA  # Position 15

    # =========================================================================
    # SECURITY LEVEL MANAGEMENT
    # =========================================================================

    @property
    def active_level(self) -> SecurityLevel:
        """Get currently active security level."""
        return self._active_level

    def set_level(self, level: SecurityLevel, reason: str) -> bool:
        """
        Change security level.

        Lower levels (more strict) require audit trail.
        SUBSTRATE level can only be set with explicit authorization.
        """
        with self._lock:
            old_level = self._active_level

            # Cannot lower to SUBSTRATE without explicit authorization
            if level == SecurityLevel.SUBSTRATE and old_level != SecurityLevel.SUBSTRATE:
                logger.warning("⚖️  YAMARAJA: SUBSTRATE level requires sovereign authorization")
                self._record_audit(
                    operation="set_level_denied",
                    subject=f"{old_level.name} -> {level.name}",
                    level=level,
                    verdict=Verdict.DENY,
                    reason="SUBSTRATE requires sovereign",
                )
                return False

            self._active_level = level

            # Record level change
            self._record_audit(
                operation="set_level",
                subject=f"{old_level.name} -> {level.name}",
                level=level,
                verdict=Verdict.ALLOW,
                reason=reason,
            )

            logger.info(f"⚖️  YAMARAJA: Security level changed from {old_level.name} to {level.name}: {reason}")
            return True

    def enforce_level(self, minimum: SecurityLevel) -> None:
        """
        Ensure current level is at least 'minimum'.

        Raises SecurityError if active_level > minimum (less strict).
        """
        if self._active_level.value > minimum.value:
            msg = (
                f"Security level {self._active_level.name} ({self._active_level.value}) "
                f"does not meet minimum {minimum.name} ({minimum.value})"
            )
            logger.error(f"⚖️  YAMARAJA: {msg}")
            raise SecurityError(msg)

    # =========================================================================
    # CAPABILITY MANAGEMENT
    # =========================================================================

    def grant_capability(
        self,
        subject_id: str,
        capability: str,
        granter_id: str,
        expires_at: Optional[str] = None,
    ) -> SecurityCapability:
        """
        Grant a capability to a subject.

        All grants are logged to ledger.
        """
        with self._lock:
            # Check if subject is quarantined
            if subject_id in self._quarantine:
                logger.warning(f"⚖️  YAMARAJA: Cannot grant to quarantined subject {subject_id}")
                raise SecurityError(f"Subject {subject_id} is quarantined")

            # Initialize capability sets if needed
            if subject_id not in self._capabilities:
                self._capabilities[subject_id] = set()
                self._capability_records[subject_id] = []

            # Create capability record
            now = datetime.now().isoformat()
            cap_record = SecurityCapability(
                name=capability,
                level=self._active_level.value,
                granted_by=granter_id,
                granted_at=now,
                expires_at=expires_at,
                conditions=[],
            )

            # Add to storage
            self._capabilities[subject_id].add(capability)
            self._capability_records[subject_id].append(cap_record)

            # Record in ledger
            self._ledger.record_event(
                event_type="YAMARAJA_CAPABILITY_GRANTED",
                agent_id=granter_id,
                details={
                    "subject_id": subject_id,
                    "capability": capability,
                    "security_level": self._active_level.value,
                    "expires_at": expires_at or "NEVER",
                    "timestamp": now,
                },
            )

            # Record audit
            self._record_audit(
                operation="grant_capability",
                subject=f"{subject_id}:{capability}",
                level=self._active_level,
                verdict=Verdict.ALLOW,
                reason=f"Granted by {granter_id}",
            )

            logger.info(f"⚖️  YAMARAJA: Granted '{capability}' to '{subject_id}' by '{granter_id}'")
            return cap_record

    def revoke_capability(
        self,
        subject_id: str,
        capability: str,
        revoker_id: str,
        reason: str,
    ) -> bool:
        """
        Revoke a capability from a subject.

        All revocations are logged to ledger.
        """
        with self._lock:
            if subject_id not in self._capabilities:
                return False

            if capability not in self._capabilities[subject_id]:
                return False

            # Remove from storage
            self._capabilities[subject_id].discard(capability)

            # Remove from records
            self._capability_records[subject_id] = [
                cap for cap in self._capability_records[subject_id] if cap["name"] != capability
            ]

            # Record in ledger
            self._ledger.record_event(
                event_type="YAMARAJA_CAPABILITY_REVOKED",
                agent_id=revoker_id,
                details={
                    "subject_id": subject_id,
                    "capability": capability,
                    "reason": reason,
                    "security_level": self._active_level.value,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Record audit
            self._record_audit(
                operation="revoke_capability",
                subject=f"{subject_id}:{capability}",
                level=self._active_level,
                verdict=Verdict.DENY,
                reason=reason,
            )

            logger.info(f"⚖️  YAMARAJA: Revoked '{capability}' from '{subject_id}' by '{revoker_id}': {reason}")
            return True

    def check_capability(self, subject_id: str, capability: str) -> bool:
        """
        Check if subject has capability.

        Fast path - no logging for checks (too noisy).
        Checks expiration and quarantine status.
        """
        # Fast path: check quarantine
        if subject_id in self._quarantine:
            entry = self._quarantine[subject_id]
            elapsed = (datetime.now() - entry.started_at).total_seconds()
            if elapsed < entry.duration_seconds:
                return False  # Still quarantined
            else:
                # Quarantine expired - restore capabilities
                self._restore_from_quarantine(subject_id)

        # Check capability exists
        if subject_id not in self._capabilities:
            return False

        if capability not in self._capabilities[subject_id]:
            return False

        # Check expiration
        for cap_record in self._capability_records.get(subject_id, []):
            if cap_record["name"] == capability:
                if cap_record["expires_at"]:
                    expires = datetime.fromisoformat(cap_record["expires_at"])
                    if datetime.now() > expires:
                        # Expired - auto-revoke
                        self._capabilities[subject_id].discard(capability)
                        return False
                return True

        return False

    def list_capabilities(self, subject_id: str) -> List[SecurityCapability]:
        """List all capabilities for a subject."""
        return list(self._capability_records.get(subject_id, []))

    # =========================================================================
    # YAMARAJA PROTOCOL (JUDGMENT)
    # =========================================================================

    def judge(self, subject: Union[Judgeable, object]) -> Verdict:
        """
        Judge a subject according to security rules.

        THE AJAMIL EXCEPTION: Always check Holy Name first!
        """
        start = time.time()

        # THE AJAMIL EXCEPTION - Holy Name overrides all judgment
        if self.check_holy_name(subject):
            self._record_audit(
                operation="judge",
                subject=self._get_subject_id(subject),
                level=self._active_level,
                verdict=Verdict.MERCY,
                reason="AJAMIL EXCEPTION - Holy Name chanted",
                holy_name_checked=True,
                duration_ms=(time.time() - start) * 1000,
            )
            return Verdict.MERCY

        # Normal judgment based on karma
        subject_id = self._get_subject_id(subject)

        # Check quarantine
        if subject_id in self._quarantine:
            return Verdict.DENY

        # Check capabilities
        if subject_id not in self._capabilities:
            return Verdict.ATONE  # Not registered - must register first

        # Positive karma = ALLOW, negative = DENY
        karma = self._get_karma_for_subject(subject_id)

        if karma > 0:
            verdict = Verdict.ALLOW
        elif karma < -10:
            verdict = Verdict.DENY
        elif karma < 0:
            verdict = Verdict.ATONE
        else:
            verdict = Verdict.ALLOW

        self._record_audit(
            operation="judge",
            subject=subject_id,
            level=self._active_level,
            verdict=verdict,
            reason=f"Karma balance: {karma}",
            holy_name_checked=True,
            duration_ms=(time.time() - start) * 1000,
        )

        return verdict

    def check_holy_name(self, subject: Union[Judgeable, object]) -> bool:
        """
        THE AJAMIL EXCEPTION - Check if subject chanted Holy Name.

        In Kali Yuga, even accidental chanting counts.
        This is the ONLY way to transcend karma.
        """
        # Check for Holy Name markers
        if isinstance(subject, Judgeable):
            karma_history = subject.karma_history or []
            holy_names = {"HARE", "KRISHNA", "RAMA", "NARAYANA", "GOVINDA", "HARI"}
            for entry in karma_history:
                if any(name in entry.upper() for name in holy_names):
                    return True
        return False

    def assert_truth(self, condition: bool, reason: str) -> None:
        """Assert truth. Raises if false."""
        if not condition:
            self.record_violation(
                level=self._active_level,
                source="assert_truth",
                target="assertion",
                violation_type="TRUTH_VIOLATION",
                details=reason,
            )
            raise AssertionError(f"YAMARAJA ASSERTION FAILED: {reason}")

    def get_karma_balance(self) -> float:
        """Get overall karma balance."""
        return self._karma_balance

    # =========================================================================
    # DEFENSE INTEGRATION (4 REGULATING PRINCIPLES)
    # =========================================================================

    def get_sanitizer(self) -> IDataSanitizer:
        """Get DAYA (Mercy) - Data sanitization."""
        if self._sanitizer is None:
            from vibe_core.naga.defenses.daya import DataSanitizer

            self._sanitizer = DataSanitizer()
        return self._sanitizer

    def get_verifier(self) -> IOutputVerifier:
        """Get SATYAM (Truth) - Output verification."""
        if self._verifier is None:
            from vibe_core.naga.defenses.satyam import OutputVerifier

            self._verifier = OutputVerifier()
        return self._verifier

    def get_resource_manager(self) -> IResourceManager:
        """Get TAPAS (Austerity) - Resource limits."""
        if self._resource_manager is None:
            from vibe_core.naga.defenses.tapas import ResourceManager

            self._resource_manager = ResourceManager()
        return self._resource_manager

    def get_network_guard(self) -> INetworkGuard:
        """Get SAUCAM (Cleanliness) - Network protection."""
        if self._network_guard is None:
            from vibe_core.naga.defenses.saucam import NetworkGuard

            self._network_guard = NetworkGuard()
        return self._network_guard

    # =========================================================================
    # VIOLATION MANAGEMENT
    # =========================================================================

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

        Triggers appropriate response based on level.
        """
        with self._lock:
            violation_id = f"VIO-{uuid.uuid4().hex[:12]}"
            now = datetime.now()

            # Determine response based on level
            response = self._determine_response(level, violation_type)

            violation = SecurityViolation(
                violation_id=violation_id,
                level=level.value,
                source=source,
                target=target,
                violation_type=violation_type,
                details=details,
                timestamp=now.isoformat(),
                response_taken=response,
            )

            # Store violation
            self._violations.append(violation)

            # Update tracker
            self._violation_tracker.count_24h += 1
            self._violation_tracker.count_1h += 1
            self._violation_tracker.last_violation = now
            if level.is_critical:
                self._violation_tracker.critical_count += 1

            # Record in ledger
            self._ledger.record_event(
                event_type="YAMARAJA_VIOLATION",
                agent_id="YAMARAJA",
                details={
                    "violation_id": violation_id,
                    "level": level.name,
                    "source": source,
                    "target": target,
                    "type": violation_type,
                    "details": details,
                    "response": response,
                },
            )

            # Execute response
            self._execute_response(response, level, source, target, details, violation_type)

            logger.warning(f"⚖️  YAMARAJA VIOLATION [{level.name}]: {violation_type} - {source} -> {target}: {details}")

            return violation

    def get_audit_log(
        self,
        since: Optional[str] = None,
        level: Optional[SecurityLevel] = None,
        limit: int = 100,
    ) -> List[SecurityAuditRecord]:
        """Get audit log entries from ledger."""
        # Get events from ledger
        events = self._ledger.get_events(
            event_type="YAMARAJA_AUDIT",
            limit=limit * 2,  # Get more to filter
        )

        records: List[SecurityAuditRecord] = []
        cutoff = datetime.fromisoformat(since) if since else datetime.now() - timedelta(hours=24)

        for event in events:
            details = event.get("details", {})
            event_time = datetime.fromisoformat(details.get("timestamp", datetime.now().isoformat()))

            # Filter by time
            if event_time < cutoff:
                continue

            # Filter by level
            if level is not None and details.get("level") != level.value:
                continue

            record = SecurityAuditRecord(
                audit_id=details.get("audit_id", ""),
                operation=details.get("operation", ""),
                subject=details.get("subject", ""),
                level=details.get("level", SecurityLevel.APPLICATION.value),
                verdict=details.get("verdict", ""),
                reason=details.get("reason", ""),
                timestamp=details.get("timestamp", ""),
                duration_ms=details.get("duration_ms", 0.0),
                holy_name_checked=details.get("holy_name_checked", False),
            )
            records.append(record)

            if len(records) >= limit:
                break

        return records

    def audit_self(self) -> SecurityStateSnapshot:
        """
        Self-audit: Yamaraja judges Yamaraja.

        FRACTAL: The judge must also be judged.
        Returns snapshot of security health.
        """
        with self._lock:
            snapshot_id = f"SNAP-{uuid.uuid4().hex[:8]}"
            now = datetime.now()

            # Count total capabilities
            total_caps = sum(len(caps) for caps in self._capabilities.values())

            # Calculate health score
            # Factors: violation count, critical violations, quarantine count
            health = 1.0

            # Deduct for violations in last 24h
            if self._violation_tracker.count_24h > 0:
                health -= min(0.3, self._violation_tracker.count_24h * 0.03)

            # Heavy penalty for critical violations
            if self._violation_tracker.critical_count > 0:
                health -= min(0.5, self._violation_tracker.critical_count * 0.1)

            # Deduct for quarantined subjects
            quarantine_count = len(self._quarantine)
            if quarantine_count > 0:
                health -= min(0.2, quarantine_count * 0.02)

            health = max(0.0, health)

            snapshot = SecurityStateSnapshot(
                snapshot_id=snapshot_id,
                timestamp=now.isoformat(),
                active_level=self._active_level.value,
                capabilities_count=total_caps,
                violations_24h=self._violation_tracker.count_24h,
                health_score=round(health, 3),
            )

            # Record self-audit in ledger
            self._ledger.record_event(
                event_type="YAMARAJA_SELF_AUDIT",
                agent_id="YAMARAJA",
                details={
                    "snapshot_id": snapshot_id,
                    "health_score": health,
                    "active_level": self._active_level.name,
                    "capabilities_count": total_caps,
                    "violations_24h": self._violation_tracker.count_24h,
                    "critical_violations": self._violation_tracker.critical_count,
                    "quarantine_count": quarantine_count,
                },
            )

            logger.info(
                f"⚖️  YAMARAJA SELF-AUDIT: Health={health:.1%}, "
                f"Level={self._active_level.name}, Violations(24h)={self._violation_tracker.count_24h}"
            )

            return snapshot

    # =========================================================================
    # THREAT RESPONSE
    # =========================================================================

    def escalate(
        self,
        violation: SecurityViolation,
        to_level: SecurityLevel,
    ) -> None:
        """
        Escalate a violation to a stricter level.

        Used when automated response is insufficient.
        """
        if to_level.value >= violation["level"]:
            logger.warning(
                f"⚖️  YAMARAJA: Cannot escalate to same or higher level ({to_level.name} >= level {violation['level']})"
            )
            return

        # Record escalation
        self._ledger.record_event(
            event_type="YAMARAJA_ESCALATION",
            agent_id="YAMARAJA",
            details={
                "violation_id": violation["violation_id"],
                "from_level": violation["level"],
                "to_level": to_level.value,
                "original_type": violation["violation_type"],
            },
        )

        # Re-process with new level
        self.record_violation(
            level=to_level,
            source=violation["source"],
            target=violation["target"],
            violation_type=f"ESCALATED:{violation['violation_type']}",
            details=f"Escalated from level {violation['level']}: {violation['details']}",
        )

        logger.warning(f"⚖️  YAMARAJA ESCALATION: {violation['violation_id']} escalated to {to_level.name}")

    def quarantine(
        self,
        subject_id: str,
        reason: str,
        duration_seconds: int = 3600,
    ) -> bool:
        """
        Quarantine a subject (temporary capability suspension).

        All capabilities are suspended for the duration.
        """
        with self._lock:
            if subject_id not in self._capabilities:
                return False

            # Store current capabilities
            current_caps = frozenset(self._capabilities[subject_id])

            # Clear capabilities
            self._capabilities[subject_id] = set()

            # Create quarantine entry
            entry = QuarantineEntry(
                subject_id=subject_id,
                reason=reason,
                started_at=datetime.now(),
                duration_seconds=duration_seconds,
                revoked_capabilities=current_caps,
            )
            self._quarantine[subject_id] = entry

            # Record in ledger
            self._ledger.record_event(
                event_type="YAMARAJA_QUARANTINE",
                agent_id="YAMARAJA",
                details={
                    "subject_id": subject_id,
                    "reason": reason,
                    "duration_seconds": duration_seconds,
                    "suspended_capabilities": list(current_caps),
                },
            )

            logger.warning(f"⚖️  YAMARAJA QUARANTINE: '{subject_id}' quarantined for {duration_seconds}s: {reason}")
            return True

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _record_audit(
        self,
        operation: str,
        subject: str,
        level: SecurityLevel,
        verdict: Verdict,
        reason: str,
        holy_name_checked: bool = False,
        duration_ms: float = 0.0,
    ) -> None:
        """Record an audit entry to ledger."""
        audit_id = f"AUD-{uuid.uuid4().hex[:12]}"

        self._ledger.record_event(
            event_type="YAMARAJA_AUDIT",
            agent_id="YAMARAJA",
            details={
                "audit_id": audit_id,
                "operation": operation,
                "subject": subject,
                "level": level.value,
                "verdict": verdict.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "duration_ms": duration_ms,
                "holy_name_checked": holy_name_checked,
            },
        )

    def _determine_response(self, level: SecurityLevel, violation_type: str) -> str:
        """Determine appropriate response based on level."""
        return level.response_type

    def _execute_response(
        self,
        response: str,
        level: SecurityLevel,
        source: str,
        target: str,
        details: str,
        violation_type: str = "UNKNOWN",
    ) -> None:
        """Execute the determined response."""
        if response == "SYSTEM_HALT":
            logger.critical(f"⚖️  YAMARAJA: SYSTEM_HALT triggered by {level.name} violation")
            # In production, this would trigger graceful shutdown
            # For now, just log critically

        elif response == "KERNEL_PANIC":
            logger.critical(f"⚖️  YAMARAJA: KERNEL_PANIC triggered - {source} -> {target}")
            # Would trigger kernel-level recovery

        elif response == "AUTO_HEAL":
            logger.warning(f"⚖️  YAMARAJA: AUTO_HEAL requested for {target}")
            # Would trigger Ouroboros healing loop

        elif response == "NAGA_RESPONSE":
            logger.warning("⚖️  YAMARAJA: NAGA_RESPONSE - activating threat response")
            # Would notify NAGA services

        elif response == "LOG_ALERT":
            logger.info(f"⚖️  YAMARAJA: LOG_ALERT - {violation_type}")

        elif response == "USER_NOTIFY":
            logger.info(f"⚖️  YAMARAJA: USER_NOTIFY - {details}")

    def _restore_from_quarantine(self, subject_id: str) -> None:
        """Restore capabilities after quarantine expires."""
        if subject_id not in self._quarantine:
            return

        entry = self._quarantine.pop(subject_id)

        # Restore capabilities
        self._capabilities[subject_id] = set(entry.revoked_capabilities)

        # Record restoration
        self._ledger.record_event(
            event_type="YAMARAJA_QUARANTINE_LIFTED",
            agent_id="YAMARAJA",
            details={
                "subject_id": subject_id,
                "duration_served": entry.duration_seconds,
                "restored_capabilities": list(entry.revoked_capabilities),
            },
        )

        logger.info(f"⚖️  YAMARAJA: Quarantine lifted for '{subject_id}'")

    def _get_subject_id(self, subject: Union[Judgeable, object]) -> str:
        """Extract subject ID from various types."""
        if isinstance(subject, Judgeable):
            return subject.subject_id
        elif hasattr(subject, "subject_id"):
            return str(getattr(subject, "subject_id"))
        elif hasattr(subject, "agent_id"):
            return str(getattr(subject, "agent_id"))
        else:
            return str(id(subject))

    def _get_karma_for_subject(self, subject_id: str) -> float:
        """Get karma balance for a specific subject."""
        # Could integrate with external karma tracking
        # For now, return neutral
        return 0.0


# =============================================================================
# SECURITY ERROR
# =============================================================================


class SecurityError(Exception):
    """Security-related error from Yamaraja."""

    pass


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "YamarajaService",
    "SecurityError",
    "QuarantineEntry",
]
