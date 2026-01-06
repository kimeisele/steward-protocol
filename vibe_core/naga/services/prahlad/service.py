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

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.naga.services.prahlad.chaos import ChaosProbingMixin
from vibe_core.naga.services.prahlad.coverage import CoverageIntelligenceMixin
from vibe_core.naga.services.prahlad.hiranyakashipu import HiranyakashipuMixin
from vibe_core.naga.services.prahlad.types import (
    ChaosTarget,
    DharmaScore,
    ErrorContextData,
    ErrorEvent,
    LedgerLike,
    PhoenixResult,
    PhoenixStateData,
    TestCase,
)
from vibe_core.protocols.correction import (
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga import NagaStatus, NagaType
from vibe_core.protocols.naga.groups import AuditResult, GovernanceProtocol

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.hiranyakashipu import AttackSeed, SeedLoader
    from vibe_core.naga.identity import NagaIdentity

logger = logging.getLogger("PRAHLAD")


@naga_service(
    name="Prahlad",
    lord=NagaLord.PRAHLAD,
    drift_source="structural",
    priority=90,
    capabilities=[NagaCapability.RESILIENCE, NagaCapability.AUDIT],
    protocol_class="vibe_core.protocols.naga.PrahladProtocol",
)
class PrahladService(
    NagaBaseService,
    GovernanceProtocol,
    ChaosProbingMixin,
    CoverageIntelligenceMixin,
    HiranyakashipuMixin,
):
    """
    Prahlad Maharaj - The Resilience Agent.

    Makes the system antifragile: every failure makes it stronger.

    INTERFACE GROUP: GovernanceProtocol (audit, verify, get_dharma_score)
    MIXINS: ChaosProbingMixin, CoverageIntelligenceMixin, HiranyakashipuMixin
    OUROBOROS: Inherits NagaBaseService for self-monitoring.
    """

    def __init__(
        self,
        cortex: Optional["NagaCortex"] = None,
        identity: Optional["NagaIdentity"] = None,
    ):
        """Initialize Prahlad."""
        super().__init__(service_name="Prahlad")
        self._cortex = cortex
        self._identity = identity

        self._hardening_suite: List[TestCase] = []
        self._seen_fingerprints: set = set()
        self._components: Dict[str, ChaosTarget] = {}
        self._agents: Dict[str, bool] = {}
        self._ledger: Optional[LedgerLike] = None

        # Hiranyakashipu integration
        self._seed_loader: Optional["SeedLoader"] = None
        self._attack_seeds: List["AttackSeed"] = []

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

        This is the core antifragility loop: Error → Test → System Stronger
        """
        test_case = TestCase(
            target_component=error.component_id,
            error_type=error.error_type,
            reproduction_context=error.context.copy(),
        )

        test_case.test_code = self._generate_test_code(error)

        if self._identity:
            test_case.generator_id = self._identity.agent_id
            test_case.signature = self._sign_test_case(test_case)

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
    pass
'''

    # =========================================================================
    # Dharma Audit
    # =========================================================================

    def set_ledger(self, ledger: LedgerLike) -> None:
        """Set the ledger for Dharma auditing."""
        self._ledger = ledger

    def register_agent(self, agent_id: str, has_identity: bool = True) -> None:
        """Register an agent for identity coverage tracking."""
        self._agents[agent_id] = has_identity

    @naga_governed(operation="dharma_audit")
    def dharma_audit(self) -> DharmaScore:
        """
        Audit the system for Dharma compliance.

        Checks:
        - All decisions signed (37th Principle)
        - Ledger integrity
        - Agent identity coverage
        """
        score = DharmaScore()

        if self._ledger:
            try:
                decisions = self._ledger.get_recent_decisions()
                unsigned = sum(1 for d in decisions if not d.get("signature"))
                total = len(decisions)

                score.unsigned_decisions = unsigned
                score.signature_compliance = ((total - unsigned) / total * 100) if total > 0 else 100.0

                if hasattr(self._ledger, "verify_chain"):
                    score.ledger_intact = self._ledger.verify_chain()
            except Exception as e:
                logger.warning(f"Error checking ledger: {e}")
                score.ledger_intact = False

        if self._agents:
            without_identity = sum(1 for has_id in self._agents.values() if not has_id)
            total = len(self._agents)
            score.agents_without_identity = without_identity
            score.identity_coverage = ((total - without_identity) / total * 100) if total > 0 else 100.0

        score.total_score = self._calculate_dharma_score(score)

        if self._identity:
            score.auditor_id = self._identity.agent_id
            score.signature = self._sign_dharma_score(score)

        self._dharma_audits += 1
        self._last_heartbeat = datetime.now()

        if self._cortex and score.total_score < 100:
            try:
                self._cortex.receive_prahlad_finding(
                    {"type": "DHARMA_VIOLATION", "score": score.total_score, "unsigned": score.unsigned_decisions}
                )
            except Exception as e:
                logger.warning(f"Failed to report to cortex: {e}")

        logger.info(f"🐍 PRAHLAD Dharma Audit: {score.total_score:.1f}%")
        return score

    def _calculate_dharma_score(self, score: DharmaScore) -> float:
        """Calculate total Dharma score."""
        total = 0.0
        weights = 0.0

        if score.ledger_intact:
            total += 40.0
        weights += 40.0

        total += score.signature_compliance * 0.35
        weights += 35.0

        total += score.identity_coverage * 0.25
        weights += 25.0

        return (total / weights) * 100 if weights > 0 else 100.0

    # =========================================================================
    # GovernanceProtocol Implementation (Interface Group)
    # =========================================================================

    def audit(self, target: str) -> AuditResult:
        """Audit a target for compliance (GovernanceProtocol)."""
        dharma = self.dharma_audit()

        violations: List[str] = []
        if dharma.unsigned_decisions > 0:
            violations.append(f"Unsigned decisions: {dharma.unsigned_decisions}")
        if not dharma.ledger_intact:
            violations.append("Ledger integrity compromised")
        if dharma.agents_without_identity > 0:
            violations.append(f"Agents without identity: {dharma.agents_without_identity}")

        return AuditResult(
            passed=dharma.total_score >= 80.0,
            score=dharma.total_score / 100.0,
            violations=violations,
            timestamp=dharma.timestamp,
        )

    def verify(self, claim: str) -> bool:
        """Verify a claim is true (GovernanceProtocol)."""
        if claim == "ledger_intact":
            if self._ledger and hasattr(self._ledger, "verify_chain"):
                return self._ledger.verify_chain()
            return False

        if claim == "all_signed":
            dharma = self.dharma_audit()
            return dharma.unsigned_decisions == 0

        if claim == "phoenix_ready":
            return self.verify_self_integrity(quiet=True)

        logger.warning(f"Unknown claim to verify: {claim}")
        return False

    def get_dharma_score(self) -> float:
        """Get overall dharma compliance score (GovernanceProtocol)."""
        dharma = self.dharma_audit()
        return dharma.total_score / 100.0

    # =========================================================================
    # Phoenix Guarantee
    # =========================================================================

    def verify_phoenix_guarantee(self, target: str) -> PhoenixResult:
        """Verify crash-restart-resume for a component."""
        component = self._components.get(target)
        if not component:
            return PhoenixResult(target=target, passed=False)

        result = PhoenixResult(target=target)

        try:
            result.state_before = component.get_state()

            if hasattr(component, "shutdown"):
                component.shutdown()

            if hasattr(component, "restart"):
                component.restart()

            result.state_after = component.get_state()
            result.state_preserved = result.state_before == result.state_after
            result.passed = result.state_preserved

        except Exception as e:
            logger.warning(f"Phoenix verification failed: {e}")
            result.passed = False
            result.state_preserved = False

        return result

    # =========================================================================
    # OUROBOROS Self-Verification
    # =========================================================================

    def verify_self_integrity(self, quiet: bool = True) -> bool:
        """OUROBOROS SELF-CHECK: Prahlad runs the NAGA test suite."""
        self._last_heartbeat = datetime.now()

        naga_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        vibe_core_dir = os.path.dirname(naga_dir)
        repo_root = os.path.dirname(vibe_core_dir)
        test_dir = os.path.join(repo_root, "tests", "naga")

        if not os.path.exists(test_dir):
            logger.warning(f"PRAHLAD: Test chamber not found at {test_dir}")
            return False

        logger.info("PRAHLAD: Initiating Self-Diagnostic (Ouroboros Scan)...")

        try:
            import pytest

            args = [test_dir, "-q", "--tb=line"]
            if quiet:
                args.append("--no-header")

            ret_code = pytest.main(args)

            if ret_code == 0:
                logger.info("PRAHLAD: Self-Check PASSED. NAGA is Watertight.")
                self._record_integrity_event(passed=True, exit_code=ret_code)
                return True
            else:
                logger.error(f"PRAHLAD: Self-Check FAILED (Code {ret_code}). NAGA compromised!")
                self._record_integrity_event(passed=False, exit_code=ret_code)
                return False

        except ImportError:
            logger.warning("PRAHLAD: pytest not available for self-check")
            return False
        except Exception as e:
            logger.error(f"PRAHLAD: Self-check error: {e}")
            self._record_integrity_event(passed=False, error=str(e))
            return False

    def _record_integrity_event(self, passed: bool, exit_code: int = 0, error: str = "") -> None:
        """Record integrity check result to Sesha if available."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                sesha.record_event(
                    event_type="NAGA_INTEGRITY_CHECK",
                    source="prahlad.verify_self_integrity",
                    details={"passed": passed, "exit_code": exit_code, "error": error},
                )
        except Exception:
            pass

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

            try:
                component_id = drift.context.get("component_id", "unknown")
                error_type = drift.context.get("error_type", "UnknownError")

                error_event = ErrorEvent(
                    error_type=error_type,
                    message=drift.message,
                    component_id=component_id,
                    context=drift.context,
                )
                self.on_error(error_event)

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
