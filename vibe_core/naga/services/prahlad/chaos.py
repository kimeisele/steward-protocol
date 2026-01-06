"""
PRAHLAD Chaos Probing - Mixin for chaos engineering.

Extracted to reduce service.py below 800 lines.
"""

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from vibe_core.naga.services.prahlad.types import (
    ChaosProbeResult,
    ChaosScenario,
    ChaosTarget,
    ErrorEvent,
    ProbeFailure,
    ProbeResult,
)

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.hiranyakashipu import AttackSeed

logger = logging.getLogger("PRAHLAD")


class ChaosProbingMixin:
    """
    Mixin for Prahlad chaos probing capabilities.

    Provides:
    - chaos_probe(): Standard chaos scenarios
    - chaos_probe_real(): Parasitic chaos injection
    - Hiranyakashipu attack seed integration
    """

    # These attributes are expected from PrahladService
    _components: Dict[str, ChaosTarget]
    _cortex: Optional["NagaCortex"]
    _chaos_probes: int
    _last_heartbeat: datetime

    def register_component(self, name: str, component: ChaosTarget) -> None:
        """Register a component for chaos testing."""
        self._components[name] = component

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

    def _execute_scenario(self, component: Optional[ChaosTarget], scenario: ChaosScenario) -> None:
        """Execute a chaos scenario against a component."""
        if component is None:
            return

        if scenario == ChaosScenario.NULL_INPUT:
            component.handle(None)
        elif scenario == ChaosScenario.MALFORMED_DATA:
            component.handle({"__invalid__": object()})
        elif scenario == ChaosScenario.TIMEOUT:
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

        Args:
            target: Target module/component to attack
            attack_seeds: List of AttackSeed objects

        Returns:
            ProbeResult with attack findings
        """
        from vibe_core.di import ServiceRegistry
        from vibe_core.naga.hiranyakashipu import LivingTestFramework
        from vibe_core.protocols.naga import NagaFederationProtocol

        result = ProbeResult(
            target=target,
            scenarios_tested=len(attack_seeds),
        )

        # Use WIRED framework from orchestrator if available
        fw = None
        federation = ServiceRegistry.get(NagaFederationProtocol)
        if federation and hasattr(federation, "living_framework"):
            fw = federation.living_framework

        if fw is None:
            fw = LivingTestFramework()

        # Run each attack seed
        for seed in attack_seeds:
            try:
                loop = asyncio.new_event_loop()
                try:
                    attack_result = loop.run_until_complete(fw.run_attack(seed, target))
                finally:
                    loop.close()

                if attack_result.bypassed:
                    failure = ProbeFailure(
                        scenario=f"hiranyakashipu:{seed.name}",
                        error_type="DEFENSE_BYPASSED",
                        message=f"Attack '{seed.name}' bypassed defenses. "
                        f"Type: {seed.attack_type}, Difficulty: {seed.difficulty}",
                    )
                    result.failures += 1
                    result.failure_details.append(failure)

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
                logger.debug(f"Attack {seed.name} blocked: {e}")

        self._chaos_probes += 1
        self._last_heartbeat = datetime.now()

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

    def chaos_probe_real(
        self,
        target_protocol: type,
        chaos_scenario: str = "unavailable",
        trigger_operation: Optional[Callable[[], None]] = None,
    ) -> ChaosProbeResult:
        """
        REAL parasitic chaos probe - injects into running system.

        This is NOT the phantom chaos_probe() that calls component.handle().
        This ACTUALLY poisons the ServiceRegistry and checks if Sesha detects it.

        Args:
            target_protocol: The protocol type to poison
            chaos_scenario: Type of chaos to inject
            trigger_operation: Callable that triggers the system

        Returns:
            ChaosProbeResult with resilience assessment
        """
        import uuid

        from vibe_core.di import ServiceRegistry

        chaos_id = uuid.uuid4().hex[:8]
        result: ChaosProbeResult = {
            "chaos_id": chaos_id,
            "target": target_protocol.__name__,
            "scenario": chaos_scenario,
            "detected": False,
            "system_resilient": False,
            "exception_raised": None,
            "ledger_events": [],
        }

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
                            time.sleep(0.5)
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
                    if chaos_scenario in ["timeout"]:
                        result["system_resilient"] = True

            # 3. CHECK SESHA LEDGER
            try:
                from vibe_core.protocols.naga import SeshaProtocol

                ServiceRegistry.disable_chaos()
                sesha = ServiceRegistry.get(SeshaProtocol)
                if sesha and hasattr(sesha, "_ledger"):
                    recent = sesha._ledger.get_recent_events(limit=20)
                    for event in recent:
                        e = event.to_dict() if hasattr(event, "to_dict") else event
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
            if result["detected"]:
                result["system_resilient"] = True
            elif result["exception_raised"] and chaos_scenario == "timeout":
                result["system_resilient"] = True
            elif trigger_operation is None:
                result["system_resilient"] = True

        finally:
            # 5. CLEANUP
            ServiceRegistry.clear_chaos()
            logger.info(f"🐍 PRAHLAD CHAOS[{chaos_id}]: Cleanup complete")

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


__all__ = ["ChaosProbingMixin"]
