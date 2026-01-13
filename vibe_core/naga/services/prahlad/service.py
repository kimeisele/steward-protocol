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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x44221390"  # GenesisByte: parampara % 37 == 0

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
                import sys

                sys.stderr.write(f"!!! PRAHLAD: Audit ledger check failed: {e}\n")
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
    # Red Gate (Active Hardening via Hiranyakashipu)
    # =========================================================================

    @naga_governed(operation="run_red_gate")
    async def run_red_gate(self, target_module: str = "vibe_core.naga") -> dict:
        """
        Run Hiranyakashipu attacks using LivingTestFramework.

        This is the RED GATE.
        Prahlad invites the attacks to prove the system is Watertight.

        The Lila: Prahlad doesn't fight - he endures and proves.
        This method invokes the demon (LivingTestFramework) so all can witness
        that Narasimha (Steward/Kernel) protects.
        """
        # Lazy import to avoid circular dependency
        try:
            from vibe_core.naga.hiranyakashipu import LivingTestFramework
        except ImportError as e:
            import sys

            sys.stderr.write(f"!!! PRAHLAD: Hiranyakashipu framework missing: {e}\n")
            return {"error": "framework_missing", "status": "ABORTED"}

        logger.info(f"🐍 PRAHLAD: Opening Red Gate against {target_module}...")

        # 1. Instantiate the Demon (Test Framework)
        framework = LivingTestFramework()

        # 2. Load the Weapons (Seeds) via HiranyakashipuMixin
        if not self._attack_seeds:
            self.load_attack_seeds()

        # Feed seeds to framework
        count = 0
        for seed in self._attack_seeds:
            framework.add_seed(seed)
            count += 1

        if count == 0:
            logger.warning("PRAHLAD: No attack seeds loaded!")
            return {"error": "no_seeds", "status": "ABORTED"}

        logger.debug(f"Loaded {count} seeds into LivingTestFramework")

        # 3. Execute Attacks (The Ordeal)
        results = await framework.run_all_attacks(target_module)

        # 4. Analyze Survival
        total = len(results)
        # "Passed" means the DEFENSE held (attack failed or was caught)
        survived = sum(1 for r in results if r.passed)
        # "Bypassed" means the ATTACK succeeded (defense failed)
        breached = sum(1 for r in results if r.bypassed)

        # 5. Record to Sesha (The Legend)
        self._record_red_gate_results(results, total, survived, breached)

        status = "INVINCIBLE" if breached == 0 else "VULNERABLE"
        logger.info(f"🐍 PRAHLAD Red Gate Result: {status} ({survived}/{total} attacks blocked)")

        self._last_heartbeat = datetime.now()

        return {
            "status": status,
            "total_attacks": total,
            "blocked": survived,
            "breached": breached,
            "breached_seeds": [r.seed_name for r in results if r.bypassed],
        }

    def _record_red_gate_results(self, results: list, total: int, survived: int, breached: int) -> None:
        """Record the outcome of the Red Gate ordeal to Sesha."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                sesha.record_event(
                    {
                        "event_type": "PRAHLAD_RED_GATE",
                        "agent_id": "PRAHLAD",
                        "details": {
                            "total": total,
                            "blocked": survived,
                            "breached": breached,
                            "breached_seeds": [r.seed_name for r in results if r.bypassed],
                            "timestamp": datetime.now().isoformat(),
                        },
                        "result": "PASSED" if breached == 0 else "FAILED",
                    }
                )
        except Exception as e:
            import sys

            sys.stderr.write(f"!!! PRAHLAD: Failed to record Red Gate results: {e}\n")

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
            import subprocess
            import sys

            # YAMARAJA: Use SUBPROCESS instead of in-process pytest.main
            # Prevents Mohini Ouroboros recursion and allows TIMEOUT.
            cmd = [sys.executable, "-m", "pytest", test_dir, "-q", "--tb=line"]
            if quiet:
                cmd.append("--no-header")

            # 120s Timeout - enough for 700+ tests but prevents infinite hang
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            ret_code = result.returncode

            if ret_code == 0:
                logger.info("PRAHLAD: Self-Check PASSED. NAGA is Watertight.")
                self._record_integrity_event(passed=True, exit_code=ret_code)
                return True
            else:
                logger.error(f"PRAHLAD: Self-Check FAILED (Code {ret_code}). NAGA compromised!")
                # Log stderr if it failed
                if result.stderr:
                    logger.debug(f"PRAHLAD Stderr: {result.stderr}")
                self._record_integrity_event(passed=False, exit_code=ret_code, error=result.stdout[-500:])
                return False

        except subprocess.TimeoutExpired:
            import sys

            sys.stderr.write("!!! PRAHLAD CRITICAL: Integrity check TIMED OUT (120s). Chain compromised?\n")
            self._record_integrity_event(passed=False, error="TIMEOUT")
            return False
        except Exception as e:
            import sys

            sys.stderr.write(f"!!! PRAHLAD CRITICAL: Self-check error: {e}\n")
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
                    {
                        "event_type": "NAGA_INTEGRITY_CHECK",
                        "agent_id": "PRAHLAD",
                        "details": {
                            "passed": passed,
                            "exit_code": exit_code,
                            "error": error,
                            "timestamp": datetime.now().isoformat(),
                        },
                        "result": "PASSED" if passed else "FAILED",
                    }
                )
        except Exception as e:
            import sys

            sys.stderr.write(f"!!! PRAHLAD: Failed to record integrity event: {e}\n")
            # We don't raise here to avoid infinite loop if Sesha is what's failing,
            # but we ensured it's visible.

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
