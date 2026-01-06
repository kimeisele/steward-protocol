"""
KALIYA SERVICE - Die Quarantäne.

Kaliya - Von Krishna gebändigt, nicht getötet.

"Krishna verbannte Kaliya in den Ozean - isoliert aber lebendig."
Die Fußabdrücke auf Kaliyas Hauben schützen ihn vor Garuda.

Responsibilities:
- Isolate misbehaving components WITHOUT killing them
- Track violations per component
- Auto-quarantine on threshold
- Escalate to sovereign (37th) after repeated quarantines

Integration:
- Auto-discovered by Narada via @naga_service decorator
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import NagaStatus, NagaType
from vibe_core.protocols.naga.groups import SecurityProtocol, Subject, Verdict

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.identity import NagaIdentity

logger = logging.getLogger("KALIYA")


@dataclass
class QuarantineRecord:
    """Record of a component quarantine."""

    component_id: str
    reason: str
    started_at: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 300.0
    violation_count: int = 0
    signer_id: str = ""
    signature: Optional[bytes] = None

    def is_expired(self) -> bool:
        """Check if quarantine has expired."""
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed >= self.duration_seconds


@naga_service(
    name="Kaliya",
    lord=NagaLord.KALIYA,
    drift_source="reliability",
    priority=80,
    capabilities=[NagaCapability.ISOLATION],
    protocol_class="vibe_core.protocols.naga.KaliyaProtocol",
)
class KaliyaService(NagaBaseService, SecurityProtocol):
    """
    Kaliya - The Quarantine Agent.

    Isolates misbehaving components without killing them.
    Tracks violations and escalates after threshold.

    INTERFACE GROUP: SecurityProtocol (intercept, bite, is_quarantined)
    SEVA: Kaliya ISOLIERT FÜR Prahlad - Krishna verbannte ihn, tötete ihn nicht!
    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        identity: Optional["NagaIdentity"] = None,
        default_duration_seconds: float = 300.0,
        violation_threshold: int = 3,
        escalation_threshold: int = 3,
    ):
        """
        Initialize Kaliya.

        Args:
            cortex: NagaCortex for event reporting
            identity: NagaIdentity for signing records
            default_duration_seconds: Default quarantine duration
            violation_threshold: Violations before auto-quarantine
            escalation_threshold: Quarantine cycles before escalation
        """
        super().__init__(service_name="Kaliya")

        self._cortex = cortex
        self._identity = identity
        self._default_duration = default_duration_seconds
        self._violation_threshold = violation_threshold
        self._escalation_threshold = escalation_threshold

        self._quarantine_registry: Dict[str, QuarantineRecord] = {}
        self._violation_counts: Dict[str, int] = {}
        self._quarantine_cycles: Dict[str, int] = {}
        self._escalated: set = set()

        self._quarantined_count = 0
        self._errors = 0
        self._last_heartbeat = datetime.now()

        logger.info("🐍 KALIYA initialized - The Quarantine watches")

    def get_status(self) -> NagaStatus:
        """Get current status."""
        return NagaStatus(
            naga_type=NagaType.KALIYA,
            healthy=True,
            events_processed=self._quarantined_count,
            errors=self._errors,
            last_heartbeat=self._last_heartbeat,
            details={
                "active_quarantines": len(self._quarantine_registry),
                "escalated_components": len(self._escalated),
            },
        )

    def quarantine(
        self,
        component_id: str,
        reason: str,
        duration_seconds: Optional[float] = None,
    ) -> QuarantineRecord:
        """
        Put a component in quarantine.

        Args:
            component_id: ID of component to quarantine
            reason: Reason for quarantine
            duration_seconds: Override default duration

        Returns:
            QuarantineRecord
        """
        duration = duration_seconds or self._default_duration

        record = QuarantineRecord(
            component_id=component_id,
            reason=reason,
            duration_seconds=duration,
            violation_count=self._violation_counts.get(component_id, 0),
        )

        # Sign if identity available
        if self._identity:
            record.signer_id = self._identity.agent_id
            record.signature = self._sign_record(record)

        self._quarantine_registry[component_id] = record
        self._quarantined_count += 1
        self._last_heartbeat = datetime.now()

        # Track quarantine cycles for escalation
        self._quarantine_cycles[component_id] = self._quarantine_cycles.get(component_id, 0) + 1

        # Check for escalation
        if self._quarantine_cycles[component_id] >= self._escalation_threshold:
            self._escalate(component_id)

        # Notify cortex
        if self._cortex:
            try:
                self._cortex.receive_kaliya_event(
                    {
                        "type": "QUARANTINE",
                        "component_id": component_id,
                        "reason": reason,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to notify cortex: {e}")
                self._errors += 1

        logger.info(f"🐍 KALIYA quarantined {component_id}: {reason}")
        return record

    def is_quarantined(self, component_id: str) -> bool:
        """Check if component is currently quarantined."""
        if component_id not in self._quarantine_registry:
            return False

        record = self._quarantine_registry[component_id]
        if record.is_expired():
            del self._quarantine_registry[component_id]
            return False

        return True

    @naga_governed(operation="release")
    def release(self, component_id: str) -> None:
        """
        Release component from quarantine.

        Raises:
            Exception: If component is escalated (cannot be released)
        """
        if component_id in self._escalated:
            raise Exception(f"Component {component_id} is escalated - cannot be released without sovereign approval")

        if component_id in self._quarantine_registry:
            del self._quarantine_registry[component_id]

        # Reset violation count on release
        self._violation_counts[component_id] = 0

        logger.info(f"🐍 KALIYA released {component_id}")

    @naga_governed(operation="record_violation", log_args=True)
    def record_violation(self, component_id: str) -> None:
        """
        Record a violation for a component.

        Auto-quarantines if threshold reached.
        """
        self._violation_counts[component_id] = self._violation_counts.get(component_id, 0) + 1
        self._last_heartbeat = datetime.now()

        if self._violation_counts[component_id] >= self._violation_threshold:
            self.quarantine(
                component_id,
                f"Auto-quarantine: {self._violation_counts[component_id]} violations",
            )

    def get_violation_count(self, component_id: str) -> int:
        """Get current violation count for component."""
        return self._violation_counts.get(component_id, 0)

    def is_escalated(self, component_id: str) -> bool:
        """Check if component has been escalated to sovereign."""
        return component_id in self._escalated

    def _escalate(self, component_id: str) -> None:
        """Escalate component to sovereign (37th)."""
        self._escalated.add(component_id)

        logger.warning(f"🐍 KALIYA ESCALATED {component_id} to sovereign!")

        if self._cortex:
            try:
                self._cortex.receive_kaliya_event(
                    {
                        "type": "ESCALATION",
                        "component_id": component_id,
                        "quarantine_cycles": self._quarantine_cycles[component_id],
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to notify cortex of escalation: {e}")
                self._errors += 1

    def _sign_record(self, record: QuarantineRecord) -> bytes:
        """Sign a quarantine record."""
        if not self._identity:
            return b""

        payload = f"{record.component_id}:{record.reason}:{record.started_at.isoformat()}"
        return self._identity.sign(payload.encode())

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self):
        """Get this NAGA as a CorrectionHandler for DriftSource.RELIABILITY."""
        from typing import Callable

        from vibe_core.protocols.correction import (
            DriftSource,
            HealingResult,
            HealingStatus,
            HealingStrategy,
            UnifiedDriftReport,
        )

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.RELIABILITY:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="kaliya",
                    message=f"Not a RELIABILITY drift: {drift.source}",
                )

            # Extract component from drift context
            component_id = drift.context.get("component_id", drift.id)

            if strategy == HealingStrategy.DRY_RUN:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="kaliya",
                    message=f"Would quarantine {component_id} (DRY_RUN)",
                )

            # Actual quarantine
            try:
                self.quarantine(component_id, f"RELIABILITY drift: {drift.message}")
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.HEALED,
                    handler_id="kaliya",
                    message=f"Quarantined {component_id}",
                )
            except Exception as e:
                self._errors += 1
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.FAILED,
                    handler_id="kaliya",
                    message=f"Quarantine failed: {e}",
                )

        return handler

    # =========================================================================
    # SecurityProtocol Implementation (Interface Group - Seva for Prahlad)
    # =========================================================================

    def intercept(self, subject: Subject) -> Verdict:
        """
        Judge a subject (SecurityProtocol).

        SEVA: Kaliya intercepts FÜR Prahlad - isolation not death.
        Krishna didn't kill Kaliya, he banished him to the ocean.

        Args:
            subject: The subject to judge

        Returns:
            Verdict: QUARANTINE if isolated, ALLOW otherwise
        """
        if self.is_quarantined(subject.identifier):
            return Verdict.QUARANTINE

        if self.is_escalated(subject.identifier):
            return Verdict.DENY  # Escalated = blocked until sovereign approval

        # Check violation count
        violations = self.get_violation_count(subject.identifier)
        if violations >= self._violation_threshold:
            return Verdict.QUARANTINE

        return Verdict.ALLOW

    def bite(self, subject: Subject, reason: str) -> None:
        """
        Record a violation (SecurityProtocol).

        SEVA: Kaliya "bites" by recording violation FÜR Prahlad.
        Unlike Takshaka's lethal bite, Kaliya's bite leads to isolation.

        Args:
            subject: The subject that violated
            reason: Why they violated
        """
        self.record_violation(subject.identifier)

        # If threshold reached, quarantine happens automatically in record_violation
        # But we also want to record the reason
        if self.is_quarantined(subject.identifier):
            record = self._quarantine_registry.get(subject.identifier)
            if record and not record.reason.startswith("Auto-quarantine"):
                # Update reason if it was auto-quarantined
                pass  # Already has reason from quarantine() call
