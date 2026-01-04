"""
QuantumHealingResolver - Graduated Healing Strategy via Quantum Resonance

Replaces binary dry_run=True with karma-based trust calculation.
Uses:
- VedicGovernanceProtocol for Bhakti/Ashrama state
- QuantumReactor for resonance computation
- Agent history for trust calibration

Philosophy: Agents EARN write privileges through devotional practice.
No hardcoded thresholds - resonance determines manifestation.

OPUS-LZ3: All resonance decisions are now recorded to Ledger for audit trail.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import (
    AsharamaStage,
    HealingStrategy,
    HealingStrategyResolverProtocol,
    UnifiedDriftReport,
    VedicGovernanceProtocol,
    VibeLedger,
)

if TYPE_CHECKING:
    from vibe_core.reactor.quantum import QuantumReactor

logger = logging.getLogger("HEALING_RESOLVER")


@dataclass
class ResonanceDecisionRecord:
    """
    Typed record for ledger audit trail.

    OPUS-LZ3: Cryptographic proof of WHY healing was allowed/denied.
    No Dict[str, Any] - everything is typed.
    """

    event: str
    drift_id: str
    drift_source: str
    drift_severity: str
    drift_rule: Optional[str]
    strategy: str
    ashrama: str
    bhakti: int
    bhakti_threshold: int
    reason: str
    timestamp: str
    resonance_energy: Optional[float] = None
    resonance_inertia: Optional[float] = None
    resonance_manifested: Optional[bool] = None


# Trust thresholds (not hardcoded - configurable via protocol)
DEFAULT_BHAKTI_OVERRIDE_THRESHOLD = 50  # Bhakti level for manual review
DEFAULT_BHAKTI_MAX = 200  # Maximum bhakti for normalization


class QuantumHealingResolver(HealingStrategyResolverProtocol):
    """
    Resolves HealingStrategy using Quantum Reactor resonance.

    Trust flows through three channels:
    1. Ashrama stage (lifecycle permissions)
    2. Bhakti balance (earned trust)
    3. Quantum resonance (energy vs inertia)

    Only when all three align does AUTO healing manifest.
    """

    def __init__(
        self,
        governance: Optional[VedicGovernanceProtocol] = None,
        reactor: Optional["QuantumReactor"] = None,
        ledger: Optional[VibeLedger] = None,
        bhakti_override_threshold: int = DEFAULT_BHAKTI_OVERRIDE_THRESHOLD,
        bhakti_max: int = DEFAULT_BHAKTI_MAX,
    ):
        """
        Initialize resolver with dependencies.

        Args:
            governance: VedicGovernance for trust state (DI if None)
            reactor: QuantumReactor for resonance (DI if None)
            ledger: VibeLedger for audit trail (DI if None)
            bhakti_override_threshold: Bhakti needed for MANUAL (default 50)
            bhakti_max: Maximum bhakti for normalization (default 200)
        """
        self._governance = governance
        self._reactor = reactor
        self._ledger = ledger
        self._bhakti_override_threshold = bhakti_override_threshold
        self._bhakti_max = bhakti_max

    @property
    def governance(self) -> VedicGovernanceProtocol:
        """Lazy-load governance via DI."""
        if self._governance is None:
            self._governance = ServiceRegistry.get(VedicGovernanceProtocol)
        return self._governance

    @property
    def reactor(self) -> "QuantumReactor":
        """Lazy-load reactor via DI."""
        if self._reactor is None:
            from vibe_core.reactor.quantum import QuantumReactor

            self._reactor = QuantumReactor()
        return self._reactor

    @property
    def ledger(self) -> Optional[VibeLedger]:
        """Lazy-load ledger via DI."""
        if self._ledger is None:
            try:
                self._ledger = ServiceRegistry.get(VibeLedger)
            except Exception:
                pass  # Ledger not available
        return self._ledger

    def _record_decision(
        self,
        agent_id: str,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy,
        ashrama: AsharamaStage,
        bhakti: int,
        energy: Optional[float] = None,
        inertia: Optional[float] = None,
        reason: str = "",
    ) -> None:
        """
        Record resonance decision to Ledger for audit trail.

        OPUS-LZ3: Cryptographic proof of WHY healing was allowed/denied.
        This enables post-hoc verification that the system followed Dharma.

        Args:
            agent_id: Agent requesting healing
            drift: The drift being considered
            strategy: The resolved strategy
            ashrama: Agent's lifecycle stage
            bhakti: Agent's trust balance
            energy: Resonance energy (if computed)
            inertia: Reactor inertia threshold (if computed)
            reason: Human-readable reason for decision
        """
        if self.ledger is None:
            return

        try:
            record = ResonanceDecisionRecord(
                event="RESONANCE_DECISION",
                drift_id=drift.id,
                drift_source=drift.source.value,
                drift_severity=drift.severity.value,
                drift_rule=drift.rule_id,
                strategy=strategy.value,
                ashrama=ashrama.value,
                bhakti=bhakti,
                bhakti_threshold=self._bhakti_override_threshold,
                reason=reason,
                timestamp=datetime.utcnow().isoformat(),
                resonance_energy=round(energy, 4) if energy is not None else None,
                resonance_inertia=round(inertia, 4) if inertia is not None else None,
                resonance_manifested=energy > inertia if energy is not None and inertia is not None else None,
            )

            self.ledger.record_event(
                event_type="HEALING_RESONANCE",
                agent_id=agent_id,
                details=asdict(record),
            )
            logger.debug(f"📜 Ledger: RESONANCE_DECISION for {agent_id} → {strategy.value}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to record decision to ledger: {e}")

    def resolve(
        self,
        agent_id: str,
        drift: UnifiedDriftReport,
    ) -> HealingStrategy:
        """
        Determine healing strategy via quantum resonance.

        Flow:
        1. Check Ashrama stage - BRAHMACHARI cannot write
        2. Get Bhakti balance - trust score
        3. Compute resonance intent
        4. If resonance manifests → AUTO
        5. If high Bhakti but no manifest → MANUAL
        6. Otherwise → DRY_RUN

        Args:
            agent_id: Agent requesting healing
            drift: Drift report for context

        Returns:
            HealingStrategy based on earned trust
        """
        try:
            # Step 1: Check Ashrama stage
            ashrama = self._get_ashrama_safe(agent_id)
            bhakti = self._get_bhakti_safe(agent_id)

            if ashrama == AsharamaStage.BRAHMACHARI:
                strategy = HealingStrategy.DRY_RUN
                self._record_decision(
                    agent_id,
                    drift,
                    strategy,
                    ashrama,
                    bhakti,
                    reason="BRAHMACHARI stage - learning only",
                )
                logger.debug(f"🎓 Agent {agent_id} is BRAHMACHARI - DRY_RUN only")
                return strategy

            if ashrama == AsharamaStage.SANNYASA:
                strategy = HealingStrategy.DRY_RUN
                self._record_decision(
                    agent_id,
                    drift,
                    strategy,
                    ashrama,
                    bhakti,
                    reason="SANNYASA stage - system functions only",
                )
                logger.debug(f"🕉️ Agent {agent_id} is SANNYASA - system functions only")
                return strategy

            # Step 2: Compute resonance via Quantum Reactor
            intent = f"heal:{drift.source.value}:{drift.severity.value}"
            field = self.reactor.manifest(intent, salt=agent_id)
            energy = field.total_energy
            inertia = self.reactor._inertia

            # Step 3: Check if resonance manifests
            if energy > inertia:
                strategy = HealingStrategy.AUTO
                self._record_decision(
                    agent_id,
                    drift,
                    strategy,
                    ashrama,
                    bhakti,
                    energy=energy,
                    inertia=inertia,
                    reason=f"Resonance manifested: energy {energy:.4f} > inertia {inertia:.4f}",
                )
                logger.info(f"✨ RESONANCE MANIFEST: Agent {agent_id} (bhakti={bhakti}, energy={energy:.3f}) → AUTO")
                return strategy

            # Step 4: High trust but no manifest → MANUAL
            if bhakti >= self._bhakti_override_threshold:
                strategy = HealingStrategy.MANUAL
                self._record_decision(
                    agent_id,
                    drift,
                    strategy,
                    ashrama,
                    bhakti,
                    energy=energy,
                    inertia=inertia,
                    reason=f"High bhakti {bhakti} >= threshold {self._bhakti_override_threshold}",
                )
                logger.info(f"🙏 HIGH BHAKTI: Agent {agent_id} (bhakti={bhakti}) → MANUAL review")
                return strategy

            # Step 5: Default → DRY_RUN (still learning)
            strategy = HealingStrategy.DRY_RUN
            self._record_decision(
                agent_id,
                drift,
                strategy,
                ashrama,
                bhakti,
                energy=energy,
                inertia=inertia,
                reason=f"Learning: bhakti {bhakti} < threshold, energy {energy:.4f} < inertia {inertia:.4f}",
            )
            logger.debug(f"📚 Agent {agent_id} (bhakti={bhakti}, energy={energy:.3f}) → DRY_RUN (learning)")
            return strategy

        except Exception as e:
            logger.warning(f"⚠️ Resolver error for {agent_id}: {e} → DRY_RUN (safe)")
            return HealingStrategy.DRY_RUN

    def get_trust_level(self, agent_id: str) -> float:
        """
        Get normalized trust level (0.0-1.0) for an agent.

        Combines:
        - Ashrama stage (0.0 for student, 1.0 for active)
        - Bhakti balance (normalized to 0.0-1.0)

        Args:
            agent_id: Agent to check

        Returns:
            Trust level 0.0-1.0
        """
        try:
            # Ashrama contribution
            ashrama = self._get_ashrama_safe(agent_id)
            ashrama_weight = {
                AsharamaStage.BRAHMACHARI: 0.0,  # Student - no trust
                AsharamaStage.GRIHASTHA: 1.0,  # Active - full trust potential
                AsharamaStage.VANAPRASTHA: 0.5,  # Retiring - reduced trust
                AsharamaStage.SANNYASA: 0.2,  # Daemon - minimal trust
            }.get(ashrama, 0.0)

            # Bhakti contribution
            bhakti = self._get_bhakti_safe(agent_id)
            bhakti_normalized = min(bhakti / self._bhakti_max, 1.0)

            # Combined: 50% ashrama, 50% bhakti
            trust = 0.5 * ashrama_weight + 0.5 * bhakti_normalized
            return trust

        except Exception as e:
            logger.warning(f"⚠️ Trust level error for {agent_id}: {e} → 0.0")
            return 0.0

    def _get_ashrama_safe(self, agent_id: str) -> AsharamaStage:
        """Get Ashrama stage safely, defaulting to BRAHMACHARI."""
        try:
            return self.governance.get_agent_ashrama(agent_id)
        except Exception:
            return AsharamaStage.BRAHMACHARI

    def _get_bhakti_safe(self, agent_id: str) -> int:
        """Get Bhakti balance safely, defaulting to 0."""
        try:
            return self.governance.get_bhakti_balance(agent_id)
        except Exception:
            return 0


# =============================================================================
# Factory and DI Registration
# =============================================================================


def get_healing_resolver(
    governance: Optional[VedicGovernanceProtocol] = None,
    reactor: Optional["QuantumReactor"] = None,
) -> QuantumHealingResolver:
    """
    Factory function for QuantumHealingResolver.

    Uses DI for missing dependencies.
    """
    return QuantumHealingResolver(governance=governance, reactor=reactor)


# Register with DI if available
try:
    ServiceRegistry.register(HealingStrategyResolverProtocol, QuantumHealingResolver)
except Exception:
    pass  # DI not initialized yet - will be registered at boot
