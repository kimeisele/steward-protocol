"""
QuantumHealingResolver - Graduated Healing Strategy via Quantum Resonance

Replaces binary dry_run=True with karma-based trust calculation.
Uses:
- VedicGovernanceProtocol for Bhakti/Ashrama state
- QuantumReactor for resonance computation
- Agent history for trust calibration

Philosophy: Agents EARN write privileges through devotional practice.
No hardcoded thresholds - resonance determines manifestation.
"""

import logging
from typing import TYPE_CHECKING, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import (
    AsharamaStage,
    HealingStrategy,
    HealingStrategyResolverProtocol,
    UnifiedDriftReport,
    VedicGovernanceProtocol,
)

if TYPE_CHECKING:
    from vibe_core.reactor.quantum import QuantumReactor

logger = logging.getLogger("HEALING_RESOLVER")

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
        bhakti_override_threshold: int = DEFAULT_BHAKTI_OVERRIDE_THRESHOLD,
        bhakti_max: int = DEFAULT_BHAKTI_MAX,
    ):
        """
        Initialize resolver with dependencies.

        Args:
            governance: VedicGovernance for trust state (DI if None)
            reactor: QuantumReactor for resonance (DI if None)
            bhakti_override_threshold: Bhakti needed for MANUAL (default 50)
            bhakti_max: Maximum bhakti for normalization (default 200)
        """
        self._governance = governance
        self._reactor = reactor
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
            if ashrama == AsharamaStage.BRAHMACHARI:
                logger.debug(f"🎓 Agent {agent_id} is BRAHMACHARI - DRY_RUN only")
                return HealingStrategy.DRY_RUN

            if ashrama == AsharamaStage.SANNYASA:
                logger.debug(f"🕉️ Agent {agent_id} is SANNYASA - system functions only")
                return HealingStrategy.DRY_RUN

            # Step 2: Get Bhakti balance
            bhakti = self._get_bhakti_safe(agent_id)
            normalized_bhakti = min(bhakti / self._bhakti_max, 1.0)

            # Step 3: Compute resonance via Quantum Reactor
            intent = f"heal:{drift.source.value}:{drift.severity.value}"
            field = self.reactor.manifest(intent, salt=agent_id)

            # Step 4: Check if resonance manifests
            if field.total_energy > self.reactor._inertia:
                logger.info(
                    f"✨ RESONANCE MANIFEST: Agent {agent_id} (bhakti={bhakti}, energy={field.total_energy:.3f}) → AUTO"
                )
                return HealingStrategy.AUTO

            # Step 5: High trust but no manifest → MANUAL
            if bhakti >= self._bhakti_override_threshold:
                logger.info(f"🙏 HIGH BHAKTI: Agent {agent_id} (bhakti={bhakti}) → MANUAL review")
                return HealingStrategy.MANUAL

            # Step 6: Default → DRY_RUN (still learning)
            logger.debug(f"📚 Agent {agent_id} (bhakti={bhakti}, energy={field.total_energy:.3f}) → DRY_RUN (learning)")
            return HealingStrategy.DRY_RUN

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
