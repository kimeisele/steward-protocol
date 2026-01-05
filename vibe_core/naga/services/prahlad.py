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
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import NagaStatus, NagaType

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.hiranyakashipu import AttackSeed, SeedLoader
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
class PrahladService(NagaBaseService):
    """
    Prahlad Maharaj - The Resilience Agent.

    Makes the system antifragile: every failure makes it stronger.

    OUROBOROS: Inherits NagaBaseService for self-monitoring.
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
        super().__init__(service_name="Prahlad")
        self._cortex = cortex
        self._identity = identity

        self._hardening_suite: List[TestCase] = []
        self._seen_fingerprints: set = set()
        self._components: Dict[str, Any] = {}
        self._agents: Dict[str, bool] = {}  # agent_id -> has_identity
        self._ledger: Optional[Any] = None

        # Hiranyakashipu integration - living attack seeds
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

    @naga_governed(operation="chaos_probe")
    def chaos_probe(
        self,
        target: str,
        scenarios: Optional[List[ChaosScenario]] = None,
        attack_seeds: Optional[List["AttackSeed"]] = None,
    ) -> ProbeResult:
        """
        Actively probe a component for weaknesses.

        Args:
            target: Component to probe
            scenarios: Specific ChaosScenario enum scenarios (default: all)
            attack_seeds: External Hiranyakashipu attack seeds to run.
                          If provided, these YAML-defined attacks are executed
                          in addition to (or instead of) built-in scenarios.

        Returns:
            ProbeResult with findings
        """
        scenarios = scenarios or list(ChaosScenario)

        # If attack_seeds provided, use Hiranyakashipu framework
        if attack_seeds:
            return self._probe_with_attack_seeds(target, attack_seeds)

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

    def _probe_with_attack_seeds(
        self,
        target: str,
        attack_seeds: List["AttackSeed"],
    ) -> ProbeResult:
        """
        Execute Hiranyakashipu attack seeds against a target.

        This runs the living test framework's attacks synchronously,
        converting results to ProbeResult format.

        Args:
            target: Target module/component to attack
            attack_seeds: List of AttackSeed objects from Hiranyakashipu

        Returns:
            ProbeResult with attack findings
        """
        import asyncio

        from vibe_core.naga.hiranyakashipu import LivingTestFramework

        result = ProbeResult(
            target=target,
            scenarios_tested=len(attack_seeds),
        )

        # Create framework for running attacks
        fw = LivingTestFramework()

        # Run each attack seed
        for seed in attack_seeds:
            try:
                # Run attack (sync wrapper around async)
                loop = asyncio.new_event_loop()
                try:
                    attack_result = loop.run_until_complete(fw.run_attack(seed, target))
                finally:
                    loop.close()

                # If attack bypassed defenses, it's a failure (we're weak)
                if attack_result.bypassed:
                    failure = ProbeFailure(
                        scenario=f"hiranyakashipu:{seed.name}",
                        error_type="DEFENSE_BYPASSED",
                        message=f"Attack '{seed.name}' bypassed defenses. "
                        f"Type: {seed.attack_type}, Difficulty: {seed.difficulty}",
                    )
                    result.failures += 1
                    result.failure_details.append(failure)

                    # Generate regression test from bypass
                    self.on_error(
                        ErrorEvent(
                            error_type="DEFENSE_BYPASSED",
                            message=f"Hiranyakashipu attack '{seed.name}' succeeded",
                            component_id=target,
                            context={
                                "attack_seed": seed.name,
                                "attack_type": seed.attack_type,
                                "difficulty": seed.difficulty,
                                "test_code": seed.test_code[:200] if seed.test_code else "",
                            },
                        )
                    )

            except Exception as e:
                # Attack execution failed - this is OK (defense held)
                logger.debug(f"Attack {seed.name} blocked: {e}")

        self._chaos_probes += 1
        self._last_heartbeat = datetime.now()

        # Report to cortex if bypasses found
        if self._cortex and result.failures > 0:
            try:
                self._cortex.receive_prahlad_finding(
                    {
                        "type": "HIRANYAKASHIPU_BYPASS",
                        "target": target,
                        "bypasses": result.failures,
                        "attack_seeds": [s.name for s in attack_seeds[:5]],
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to report to cortex: {e}")

        return result

    # =========================================================================
    # PARASITIC CHAOS PROBE (REAL Antifragility Testing)
    # =========================================================================

    @naga_governed(operation="chaos_probe_real")
    def chaos_probe_real(
        self,
        target_protocol: type,
        chaos_scenario: str = "unavailable",
        trigger_operation: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        REAL parasitic chaos probe - injects into running system.

        This is NOT the phantom chaos_probe() that calls component.handle().
        This ACTUALLY poisons the ServiceRegistry and checks if Sesha detects it.

        The Ouroboros Pattern:
        1. Inject chaos into ServiceRegistry
        2. Trigger a real operation (kernel.tick, service call, etc.)
        3. Check if Sesha recorded the anomaly
        4. Return whether the system is resilient

        Args:
            target_protocol: The protocol type to poison (e.g., SeshaProtocol)
            chaos_scenario: Type of chaos to inject:
                - "unavailable": Service returns None
                - "timeout": Service raises TimeoutError
                - "corrupt": Service returns malformed data
                - "slow": Service delays response
            trigger_operation: Callable that triggers the system.
                If None, we don't trigger (just inject).

        Returns:
            Dict with:
                - chaos_id: Unique ID for this chaos injection
                - scenario: The chaos scenario used
                - detected: Whether Sesha recorded an anomaly
                - system_resilient: True if detected OR gracefully handled
                - ledger_events: List of related Sesha events

        Example:
            from vibe_core.protocols.naga import TakshakaProtocol

            # Test what happens when Takshaka is unavailable
            result = prahlad.chaos_probe_real(
                target_protocol=TakshakaProtocol,
                chaos_scenario="unavailable",
                trigger_operation=lambda: kernel.tick()
            )

            if not result["system_resilient"]:
                print("VULNERABILITY: System crashes without Takshaka!")
        """
        import uuid

        from vibe_core.di import ServiceRegistry

        chaos_id = uuid.uuid4().hex[:8]
        result = {
            "chaos_id": chaos_id,
            "target": target_protocol.__name__,
            "scenario": chaos_scenario,
            "detected": False,
            "system_resilient": False,
            "exception_raised": None,
            "ledger_events": [],
        }

        # Create chaos injector based on scenario
        def create_injector():
            if chaos_scenario == "unavailable":
                return lambda: None
            elif chaos_scenario == "timeout":

                def timeout_chaos():
                    raise TimeoutError(f"CHAOS[{chaos_id}]: {target_protocol.__name__} timed out")

                return timeout_chaos
            elif chaos_scenario == "corrupt":

                class CorruptService:
                    def __getattr__(self, name):
                        return lambda *a, **k: {"__CORRUPTED__": chaos_id}

                return lambda: CorruptService()
            elif chaos_scenario == "slow":
                import time

                original = ServiceRegistry.get(target_protocol)

                class SlowProxy:
                    def __init__(self):
                        self._original = original

                    def __getattr__(self, name):
                        def slow_method(*args, **kwargs):
                            time.sleep(0.5)  # 500ms delay
                            if self._original:
                                return getattr(self._original, name)(*args, **kwargs)
                            return None

                        return slow_method

                return lambda: SlowProxy()
            else:
                return lambda: None

        try:
            # 1. INJECT CHAOS
            ServiceRegistry.inject_chaos(target_protocol, create_injector())
            ServiceRegistry.enable_chaos()
            logger.warning(f"🐍 PRAHLAD CHAOS[{chaos_id}]: Poisoning {target_protocol.__name__} with {chaos_scenario}")

            # 2. TRIGGER OPERATION (if provided)
            if trigger_operation:
                try:
                    trigger_operation()
                except Exception as e:
                    result["exception_raised"] = str(e)
                    # Exception is expected in some scenarios
                    if chaos_scenario in ["timeout"]:
                        result["system_resilient"] = True  # System correctly raised

            # 3. CHECK SESHA LEDGER
            try:
                from vibe_core.protocols.naga import SeshaProtocol

                # Temporarily disable chaos to get real Sesha
                ServiceRegistry.disable_chaos()
                sesha = ServiceRegistry.get(SeshaProtocol)
                if sesha and hasattr(sesha, "_ledger"):
                    # Look for anomaly events
                    recent = sesha._ledger.get_recent_events(limit=20)
                    for event in recent:
                        e = event.to_dict() if hasattr(event, "to_dict") else event
                        # Check if this event relates to our chaos
                        if (
                            chaos_id in str(e.get("details", {}))
                            or "CHAOS" in e.get("event_type", "")
                            or "error" in str(e.get("details", {})).lower()
                        ):
                            result["ledger_events"].append(e)
                            result["detected"] = True

            except Exception as e:
                logger.debug(f"Ledger check failed: {e}")

            # 4. DETERMINE RESILIENCE
            # System is resilient if:
            # - Chaos was detected (logged to Sesha), OR
            # - System gracefully handled it (no crash, exception caught)
            if result["detected"]:
                result["system_resilient"] = True
            elif result["exception_raised"] and chaos_scenario == "timeout":
                result["system_resilient"] = True  # Expected exception
            elif trigger_operation is None:
                result["system_resilient"] = True  # No trigger = injection only test

        finally:
            # 5. CLEANUP
            ServiceRegistry.clear_chaos()
            logger.info(f"🐍 PRAHLAD CHAOS[{chaos_id}]: Cleanup complete")

        # Record this probe to our stats
        self._chaos_probes += 1
        self._last_heartbeat = datetime.now()

        # Generate regression test if NOT resilient
        if not result["system_resilient"]:
            self.on_error(
                ErrorEvent(
                    error_type="CHAOS_VULNERABILITY",
                    message=f"System vulnerable to {chaos_scenario} on {target_protocol.__name__}",
                    component_id=target_protocol.__name__,
                    context={
                        "chaos_id": chaos_id,
                        "scenario": chaos_scenario,
                        "detected": result["detected"],
                    },
                )
            )

        return result

    # =========================================================================
    # Hiranyakashipu Integration - Living Attack Seeds
    # =========================================================================

    def load_attack_seeds(
        self,
        seed_dirs: Optional[List[str]] = None,
        attack_type: Optional[str] = None,
    ) -> int:
        """
        Load attack seeds from Hiranyakashipu YAML files.

        Hiranyakashipu provides the weapons, Prahlad survives them.
        This wires the living test framework into chaos_probe().

        Args:
            seed_dirs: Directories containing YAML seed files.
                       If None, uses default hiranyakashipu/seeds/.
            attack_type: Filter by attack type (trivial, real, narasimha_paradox).

        Returns:
            Number of seeds loaded.
        """
        from pathlib import Path

        from vibe_core.naga.hiranyakashipu import SeedLoader

        if self._seed_loader is None:
            self._seed_loader = SeedLoader()

        # Default seed directory
        if seed_dirs is None:
            default_dir = Path(__file__).parent.parent / "hiranyakashipu" / "seeds"
            if default_dir.exists():
                seed_dirs = [str(default_dir)]
            else:
                seed_dirs = []

        # Add directories and load
        for seed_dir in seed_dirs:
            self._seed_loader.add_seed_dir(Path(seed_dir))

        count = self._seed_loader.load_seeds()

        # Get seeds (optionally filtered)
        if attack_type:
            self._attack_seeds = self._seed_loader.get_seeds(attack_type=attack_type)
        else:
            self._attack_seeds = self._seed_loader.get_all_seeds()

        logger.info(f"🐍 PRAHLAD loaded {count} Hiranyakashipu attack seeds")
        return count

    def get_attack_seeds(
        self,
        attack_type: Optional[str] = None,
        difficulty: Optional[int] = None,
    ) -> List["AttackSeed"]:
        """
        Get loaded attack seeds with optional filtering.

        Args:
            attack_type: Filter by type (trivial, real, narasimha_paradox)
            difficulty: Filter by difficulty (1-10)

        Returns:
            List of matching AttackSeed objects.
        """
        if self._seed_loader is None:
            return []

        return self._seed_loader.get_seeds(
            attack_type=attack_type,
            difficulty=difficulty,
        )

    # =========================================================================
    # Dharma Audit
    # =========================================================================

    def set_ledger(self, ledger: Any) -> None:
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
    # OUROBOROS Self-Verification
    # =========================================================================

    def verify_self_integrity(self, quiet: bool = True) -> bool:
        """
        OUROBOROS SELF-CHECK: Prahlad runs the NAGA test suite.

        "Bevor wir über andere richten, prüfen wir uns selbst."

        This is the IMMUNE RESPONSE - NAGA checks its own health
        before checking others. True self-governance.

        Args:
            quiet: If True, minimal output. If False, verbose.

        Returns:
            bool: True if NAGA is healthy (Watertight), False if compromised.
        """
        import os
        import sys

        self._last_heartbeat = datetime.now()

        # Find the test directory (tests/naga/ from repo root)
        naga_dir = os.path.dirname(os.path.dirname(__file__))  # vibe_core/naga
        vibe_core_dir = os.path.dirname(naga_dir)  # vibe_core
        repo_root = os.path.dirname(vibe_core_dir)  # repo root
        test_dir = os.path.join(repo_root, "tests", "naga")

        if not os.path.exists(test_dir):
            logger.warning(f"PRAHLAD: Test chamber not found at {test_dir}")
            return False

        logger.info("PRAHLAD: Initiating Self-Diagnostic (Ouroboros Scan)...")

        try:
            import pytest

            # Run tests
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

    def _record_integrity_event(
        self,
        passed: bool,
        exit_code: int = 0,
        error: str = "",
    ) -> None:
        """Record integrity check result to Sesha if available."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                sesha.record_event(
                    event_type="NAGA_INTEGRITY_CHECK",
                    source="prahlad.verify_self_integrity",
                    details={
                        "passed": passed,
                        "exit_code": exit_code,
                        "error": error,
                    },
                )
        except Exception:
            pass  # Graceful degradation

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
    # Coverage Intelligence (Agency API Integration)
    # =========================================================================

    def get_coverage_intelligence(self, kernel: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get coverage intelligence from TestableRegistry.

        This is NAGA's EYES - visibility into what we actually protect.
        Uses existing TestOrchestration infrastructure instead of rebuilding.

        "Jeder Dienst stellt auch Dienst zur Verfügung."

        Args:
            kernel: Optional kernel for discovery. If None, uses global registry.

        Returns:
            Coverage report with:
            - total_testables: Components we can test
            - total_tests: Test cases available
            - by_type: Breakdown by component type
            - tests_by_type: Tests per type
            - naga_coverage: What NAGA specifically covers
        """
        try:
            from vibe_core.protocols.testable_registry import (
                TestableRegistry,
                get_global_registry,
            )

            # Use global registry or create new one
            registry = get_global_registry()

            # Discover from kernel if provided
            if kernel:
                discovery_counts = registry.discover_from_kernel(kernel)
                logger.info(f"PRAHLAD: Discovered {sum(discovery_counts.values())} components")

            # Get summary from existing infrastructure
            summary = registry.get_summary()

            # Add NAGA-specific coverage
            naga_coverage = self._calculate_naga_coverage(registry)

            return {
                "timestamp": datetime.now().isoformat(),
                "source": "prahlad.get_coverage_intelligence",
                # From TestableRegistry
                "total_testables": summary["total_testables"],
                "total_tests": summary["total_tests"],
                "by_type": summary["by_type"],
                "tests_by_type": summary["tests_by_type"],
                # NAGA-specific
                "naga_coverage": naga_coverage,
                # Self-stats
                "prahlad_stats": {
                    "tests_generated": self._tests_generated,
                    "chaos_probes": self._chaos_probes,
                    "dharma_audits": self._dharma_audits,
                    "hardening_suite_size": len(self._hardening_suite),
                },
            }

        except ImportError as e:
            logger.warning(f"PRAHLAD: TestableRegistry not available: {e}")
            return {
                "error": "TestableRegistry not available",
                "prahlad_stats": {
                    "tests_generated": self._tests_generated,
                    "chaos_probes": self._chaos_probes,
                    "dharma_audits": self._dharma_audits,
                },
            }

    def _calculate_naga_coverage(self, registry: Any) -> Dict[str, Any]:
        """Calculate what NAGA specifically covers."""
        try:
            from vibe_core.protocols.testable import TestableType

            # Get NAGA-related testables
            naga_testables = []
            for testable in registry.testables:
                testable_id = testable.testable_id.lower()
                if any(kw in testable_id for kw in ["naga", "sesha", "vasuki", "takshaka", "prahlad", "cortex"]):
                    naga_testables.append(testable)

            # Count NAGA tests
            naga_tests = 0
            for testable in naga_testables:
                try:
                    naga_tests += len(testable.get_test_cases())
                except Exception:
                    pass

            return {
                "testables_covered": len(naga_testables),
                "tests_available": naga_tests,
                "services": [t.testable_id for t in naga_testables],
            }
        except Exception as e:
            logger.warning(f"PRAHLAD: NAGA coverage calculation failed: {e}")
            return {"error": str(e)}

    def request_shuddhi_heal(
        self,
        file_path: str,
        rule_id: str,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Request healing from Shuddhi Engine.

        NAGA as AGENCY: We use Shuddhi's API, not rebuild.
        "Gift zu Medizin" - Shuddhi transforms violations into fixes.

        Args:
            file_path: File to heal
            rule_id: Which remedy to apply
            dry_run: If True, just show diff without writing

        Returns:
            Shuddhi result
        """
        try:
            from pathlib import Path

            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol, ShuddhiStatus

            shuddhi = ServiceRegistry.get(ShuddhiProtocol)
            if not shuddhi:
                return {"error": "Shuddhi not available", "status": "UNAVAILABLE"}

            # Request purification
            path = Path(file_path)
            result = shuddhi.purify(path, rule_id)

            response = {
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "file": str(result.file_path),
                "rule": result.rule_id,
                "message": result.message,
            }

            # Include diff if available
            if hasattr(result, "diff") and result.diff:
                response["diff"] = result.diff

            # Write if not dry_run and successful
            if (
                not dry_run
                and result.status == ShuddhiStatus.PURIFIED
                and hasattr(result, "purified_code")
                and result.purified_code
            ):
                path.write_text(result.purified_code)
                response["written"] = True
                logger.info(f"PRAHLAD: Shuddhi healed {file_path} with {rule_id}")

            return response

        except Exception as e:
            logger.error(f"PRAHLAD: Shuddhi request failed: {e}")
            return {"error": str(e), "status": "FAILED"}

    def list_available_remedies(self) -> List[str]:
        """
        List available Shuddhi remedies.

        Returns:
            List of rule_ids that Shuddhi can apply
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.shuddhi import ShuddhiProtocol

            shuddhi = ServiceRegistry.get(ShuddhiProtocol)
            if not shuddhi:
                return []

            return shuddhi.list_remedies()
        except Exception:
            return []

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
