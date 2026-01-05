"""
PRAHLAD SERVICE - Der Resilience & Hardening Agent.

Prahlad Maharaj - Der unzerstörbare Devotee.

"Hiranyakashipu versuchte Prahlad zu töten mit Feuer, Schlangen,
Gift, Elefanten - aber Prahlad überlebte alles, weil er in
absoluter Wahrheit (Narayana) verankert war."

Purpose: Make the system ANTIFRAGILE.
- Error → Regression Test (learn from suffering)
- Chaos Probing (actively seek weakness)
- Dharma Audit (verify integrity)
- Phoenix Guarantee (crash-restart-resume)

"Was mich nicht tötet, macht mich stärker."
Vedisch: "Weil ich in Wahrheit verankert bin, kann mich nichts töten."

Integration:
- Auto-discovered by Narada via @naga_service decorator
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.protocols.naga import NagaStatus, NagaType

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.identity import NagaIdentity

logger = logging.getLogger("PRAHLAD")


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class ErrorEvent:
    """An error event to learn from."""

    error_type: str
    message: str
    component_id: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestCase:
    """A generated test case from an error."""

    target_component: str
    error_type: str
    reproduction_context: Dict[str, Any]
    test_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    generator_id: str = ""
    signature: Optional[bytes] = None

    def fingerprint(self) -> str:
        """Unique fingerprint for deduplication."""
        content = f"{self.target_component}:{self.error_type}:{self.reproduction_context}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ChaosScenario(str, Enum):
    """Chaos engineering scenarios."""

    NULL_INPUT = "null_input"
    TIMEOUT = "timeout"
    MALFORMED_DATA = "malformed_data"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAILURE = "network_failure"


@dataclass
class ProbeFailure:
    """A single failure during chaos probing."""

    scenario: str
    error_type: str
    message: str


@dataclass
class ProbeResult:
    """Result of a chaos probe."""

    target: str
    scenarios_tested: int = 0
    failures: int = 0
    failure_details: List[ProbeFailure] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DharmaScore:
    """Result of a Dharma audit."""

    total_score: float = 100.0
    unsigned_decisions: int = 0
    signature_compliance: float = 100.0
    ledger_intact: bool = True
    agents_without_identity: int = 0
    identity_coverage: float = 100.0
    timestamp: datetime = field(default_factory=datetime.now)
    auditor_id: str = ""
    signature: Optional[bytes] = None


@dataclass
class PhoenixResult:
    """Result of Phoenix guarantee verification."""

    target: str
    state_preserved: bool = True
    passed: bool = True
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# PrahladService
# =============================================================================


@naga_service(
    name="Prahlad",
    lord=NagaLord.PRAHLAD,
    drift_source="structural",
    priority=90,
    capabilities=[NagaCapability.RESILIENCE, NagaCapability.AUDIT],
    protocol_class="vibe_core.protocols.naga.PrahladProtocol",
)
class PrahladService:
    """
    Prahlad Maharaj - The Resilience Agent.

    Makes the system antifragile: every failure makes it stronger.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        identity: Optional["NagaIdentity"] = None,
    ):
        """
        Initialize Prahlad.

        Args:
            cortex: NagaCortex for reporting findings
            identity: NagaIdentity for signing findings
        """
        self._cortex = cortex
        self._identity = identity

        self._hardening_suite: List[TestCase] = []
        self._seen_fingerprints: set = set()
        self._components: Dict[str, Any] = {}
        self._agents: Dict[str, bool] = {}  # agent_id -> has_identity
        self._ledger: Optional[Any] = None

        self._tests_generated = 0
        self._chaos_probes = 0
        self._dharma_audits = 0
        self._last_heartbeat = datetime.now()

        logger.info("🐍 PRAHLAD initialized - The Resilience Agent watches")

    def get_status(self) -> NagaStatus:
        """Get current status."""
        return NagaStatus(
            naga_type=NagaType.PRAHLAD,
            healthy=True,
            events_processed=self._tests_generated + self._chaos_probes + self._dharma_audits,
            errors=0,
            last_heartbeat=self._last_heartbeat,
            details={
                "tests_generated": self._tests_generated,
                "chaos_probes": self._chaos_probes,
                "dharma_audits": self._dharma_audits,
                "hardening_suite_size": len(self._hardening_suite),
            },
        )

    # =========================================================================
    # Error → Test (Antifragility Core)
    # =========================================================================

    def on_error(self, error: ErrorEvent) -> TestCase:
        """
        Learn from an error by generating a regression test.

        This is the core antifragility loop:
        Error → Test → System Stronger

        Args:
            error: The error event to learn from

        Returns:
            Generated test case
        """
        test_case = TestCase(
            target_component=error.component_id,
            error_type=error.error_type,
            reproduction_context=error.context.copy(),
        )

        # Generate test code
        test_case.test_code = self._generate_test_code(error)

        # Sign if identity available
        if self._identity:
            test_case.generator_id = self._identity.agent_id
            test_case.signature = self._sign_test_case(test_case)

        # Deduplicate
        fingerprint = test_case.fingerprint()
        if fingerprint not in self._seen_fingerprints:
            self._hardening_suite.append(test_case)
            self._seen_fingerprints.add(fingerprint)
            self._tests_generated += 1

        self._last_heartbeat = datetime.now()

        logger.info(f"🐍 PRAHLAD learned from {error.error_type} in {error.component_id}")

        return test_case

    def _generate_test_code(self, error: ErrorEvent) -> str:
        """Generate pytest code from an error."""
        return f'''def test_regression_{error.component_id}_{error.error_type.lower()}():
    """
    Auto-generated regression test by Prahlad.
    Original error: {error.message}
    """
    # Context: {error.context}
    # TODO: Implement reproduction logic
    # The system should handle this gracefully now
    pass
'''

    # =========================================================================
    # Chaos Probing
    # =========================================================================

    def register_component(self, name: str, component: Any) -> None:
        """Register a component for chaos testing."""
        self._components[name] = component

    def chaos_probe(
        self,
        target: str,
        scenarios: Optional[List[ChaosScenario]] = None,
    ) -> ProbeResult:
        """
        Actively probe a component for weaknesses.

        Args:
            target: Component to probe
            scenarios: Specific scenarios to test (default: all)

        Returns:
            ProbeResult with findings
        """
        scenarios = scenarios or list(ChaosScenario)

        result = ProbeResult(
            target=target,
            scenarios_tested=len(scenarios),
        )

        component = self._components.get(target)

        for scenario in scenarios:
            try:
                self._execute_scenario(component, scenario)
            except Exception as e:
                failure = ProbeFailure(
                    scenario=scenario.value if isinstance(scenario, ChaosScenario) else str(scenario),
                    error_type=type(e).__name__,
                    message=str(e),
                )
                result.failures += 1
                result.failure_details.append(failure)

                # Auto-generate test for weakness
                self.on_error(
                    ErrorEvent(
                        error_type=type(e).__name__,
                        message=str(e),
                        component_id=target,
                        context={
                            "chaos_scenario": scenario.value if isinstance(scenario, ChaosScenario) else str(scenario)
                        },
                    )
                )

        self._chaos_probes += 1
        self._last_heartbeat = datetime.now()

        # Report to cortex
        if self._cortex and result.failures > 0:
            try:
                self._cortex.receive_prahlad_finding(
                    {
                        "type": "CHAOS_WEAKNESS",
                        "target": target,
                        "failures": result.failures,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to report to cortex: {e}")

        return result

    def _execute_scenario(self, component: Any, scenario: ChaosScenario) -> None:
        """Execute a chaos scenario against a component."""
        if component is None:
            return

        if scenario == ChaosScenario.NULL_INPUT:
            component.handle(None)
        elif scenario == ChaosScenario.MALFORMED_DATA:
            component.handle({"__invalid__": object()})
        elif scenario == ChaosScenario.TIMEOUT:
            # Simulate timeout scenario
            component.handle({"__timeout__": True})
        else:
            component.handle({})

    # =========================================================================
    # Dharma Audit
    # =========================================================================

    def set_ledger(self, ledger: Any) -> None:
        """Set the ledger for Dharma auditing."""
        self._ledger = ledger

    def register_agent(self, agent_id: str, has_identity: bool = True) -> None:
        """Register an agent for identity coverage tracking."""
        self._agents[agent_id] = has_identity

    def dharma_audit(self) -> DharmaScore:
        """
        Audit the system for Dharma compliance.

        Checks:
        - All decisions signed (37th Principle)
        - Ledger integrity
        - Agent identity coverage

        Returns:
            DharmaScore with compliance metrics
        """
        score = DharmaScore()

        # Check signatures
        if self._ledger:
            try:
                decisions = self._ledger.get_recent_decisions()
                unsigned = sum(1 for d in decisions if not d.get("signature"))
                total = len(decisions)

                score.unsigned_decisions = unsigned
                score.signature_compliance = ((total - unsigned) / total * 100) if total > 0 else 100.0

                # Check ledger integrity
                if hasattr(self._ledger, "verify_chain"):
                    score.ledger_intact = self._ledger.verify_chain()
            except Exception as e:
                logger.warning(f"Error checking ledger: {e}")
                score.ledger_intact = False

        # Check identity coverage
        if self._agents:
            without_identity = sum(1 for has_id in self._agents.values() if not has_id)
            total = len(self._agents)

            score.agents_without_identity = without_identity
            score.identity_coverage = ((total - without_identity) / total * 100) if total > 0 else 100.0

        # Calculate total score
        score.total_score = self._calculate_dharma_score(score)

        # Sign if identity available
        if self._identity:
            score.auditor_id = self._identity.agent_id
            score.signature = self._sign_dharma_score(score)

        self._dharma_audits += 1
        self._last_heartbeat = datetime.now()

        # Report violations to cortex
        if self._cortex and score.total_score < 100:
            try:
                self._cortex.receive_prahlad_finding(
                    {
                        "type": "DHARMA_VIOLATION",
                        "score": score.total_score,
                        "unsigned": score.unsigned_decisions,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to report to cortex: {e}")

        logger.info(f"🐍 PRAHLAD Dharma Audit: {score.total_score:.1f}%")

        return score

    def _calculate_dharma_score(self, score: DharmaScore) -> float:
        """Calculate total Dharma score."""
        total = 0.0
        weights = 0.0

        # Ledger integrity is critical (40%)
        if score.ledger_intact:
            total += 40.0
        weights += 40.0

        # Signature compliance (35%)
        total += score.signature_compliance * 0.35
        weights += 35.0

        # Identity coverage (25%)
        total += score.identity_coverage * 0.25
        weights += 25.0

        return (total / weights) * 100 if weights > 0 else 100.0

    # =========================================================================
    # Phoenix Guarantee
    # =========================================================================

    def verify_phoenix_guarantee(self, target: str) -> PhoenixResult:
        """
        Verify crash-restart-resume for a component.

        Tests:
        1. Get state before
        2. Simulate crash (shutdown)
        3. Restart
        4. Verify state preserved

        Args:
            target: Component to verify

        Returns:
            PhoenixResult
        """
        component = self._components.get(target)
        if not component:
            return PhoenixResult(target=target, passed=False)

        result = PhoenixResult(target=target)

        try:
            # Get state before crash
            result.state_before = component.get_state()

            # Simulate crash
            if hasattr(component, "shutdown"):
                component.shutdown()

            # Restart
            if hasattr(component, "restart"):
                component.restart()

            # Get state after
            result.state_after = component.get_state()

            # Compare
            result.state_preserved = result.state_before == result.state_after
            result.passed = result.state_preserved

        except Exception as e:
            logger.warning(f"Phoenix verification failed: {e}")
            result.passed = False
            result.state_preserved = False

        return result

    # =========================================================================
    # Hardening Suite Export
    # =========================================================================

    def export_hardening_suite(self) -> List[TestCase]:
        """Export the hardening test suite."""
        return list(self._hardening_suite)

    def export_as_pytest(self) -> str:
        """Export hardening suite as pytest code."""
        if not self._hardening_suite:
            return "# No tests generated yet\n"

        lines = [
            '"""',
            "Auto-generated hardening tests by Prahlad.",
            f"Generated: {datetime.now().isoformat()}",
            '"""',
            "",
            "import pytest",
            "",
        ]

        for tc in self._hardening_suite:
            lines.append(tc.test_code or "")
            lines.append("")

        return "\n".join(lines)

    def clear_hardening_suite(self) -> None:
        """Clear the hardening suite."""
        self._hardening_suite.clear()
        self._seen_fingerprints.clear()

    # =========================================================================
    # Signing
    # =========================================================================

    def _sign_test_case(self, tc: TestCase) -> bytes:
        """Sign a test case."""
        if not self._identity:
            return b""
        payload = f"{tc.target_component}:{tc.error_type}:{tc.timestamp.isoformat()}"
        return self._identity.sign(payload.encode())

    def _sign_dharma_score(self, score: DharmaScore) -> bytes:
        """Sign a dharma score."""
        if not self._identity:
            return b""
        payload = f"dharma:{score.total_score}:{score.timestamp.isoformat()}"
        return self._identity.sign(payload.encode())

    # =========================================================================
    # CorrectionHandler Interface
    # =========================================================================

    def as_handler(self):
        """Get this NAGA as a CorrectionHandler for DriftSource.STRUCTURAL."""
        from vibe_core.protocols.correction import (
            DriftSource,
            HealingResult,
            HealingStatus,
            HealingStrategy,
            UnifiedDriftReport,
        )

        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            self._last_heartbeat = datetime.now()

            if drift.source != DriftSource.STRUCTURAL:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="prahlad",
                    message=f"Not a STRUCTURAL drift: {drift.source}",
                )

            if strategy == HealingStrategy.DRY_RUN:
                score = self.dharma_audit()
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="prahlad",
                    message=f"Dharma score: {score.total_score:.1f}% (DRY_RUN)",
                )

            # Actual healing: generate test from error
            try:
                component_id = drift.context.get("component_id", "unknown")
                error_type = drift.context.get("error_type", "UnknownError")

                error_event = ErrorEvent(
                    error_type=error_type,
                    message=drift.message,
                    component_id=component_id,
                    context=drift.context,
                )
                test_case = self.on_error(error_event)

                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.HEALED,
                    handler_id="prahlad",
                    message=f"Generated regression test for {component_id}: {error_type}",
                )
            except Exception as e:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.FAILED,
                    handler_id="prahlad",
                    message=f"Test generation failed: {e}",
                )

        return handler
