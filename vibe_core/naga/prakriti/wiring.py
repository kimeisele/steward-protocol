"""
PRAKRITI WIRING - Connect Living Tests to Protocol Truth.

"Don't implement what's already defined. WIRE IT."

This module connects Prakriti (Living Test Framework) to:
1. CorrectionDispatcher (HealingStrategy.RESONANCE)
2. ReactorProtocol (DriftEvent tracking)
3. Sesha (Ledger persistence)

The adapters convert:
- TestResult → UnifiedDriftReport
- AttackSeed → DriftDetector
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import uuid4

from vibe_core.protocols.correction import (
    CorrectionHandler,
    DriftRegistryProtocol,
    DriftSeverity,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.reactor import (
    BasicReactor,
    DriftEvent,
    DriftMetrics,
    DriftType,
    ReactorProtocol,
)

from .living_tests import LivingTestFramework, TestResult
from .seed_loader import AttackSeed

if TYPE_CHECKING:
    from vibe_core.protocols.naga import SeshaProtocol

logger = logging.getLogger("NAGA.Prakriti.Wiring")


# =============================================================================
# ADAPTERS: Prakriti → Protocols
# =============================================================================


def adapt_test_result_to_drift(
    result: TestResult,
    seed: AttackSeed,
    target_module: str,
) -> UnifiedDriftReport:
    """
    Adapt Prakriti TestResult → UnifiedDriftReport.

    This allows Prakriti results to flow into CorrectionDispatcher.
    """
    # Determine severity based on attack difficulty and outcome
    if result.bypassed:
        # Attack succeeded - severity based on difficulty
        if seed.difficulty >= 6:
            severity = DriftSeverity.CRITICAL
        elif seed.difficulty >= 4:
            severity = DriftSeverity.ERROR
        else:
            severity = DriftSeverity.WARNING
    else:
        severity = DriftSeverity.INFO

    # Build message
    if result.bypassed:
        message = f"Attack '{seed.name}' bypassed defense for {target_module}"
    else:
        message = f"Defense held against '{seed.name}' for {target_module}"

    return UnifiedDriftReport(
        id=f"prakriti_{seed.name}_{uuid4().hex[:8]}",
        source=DriftSource.STRUCTURAL,  # Security/test structure
        severity=severity,
        message=message,
        detected_at=result.timestamp,
        component=target_module,
        detector_id="prakriti_living_tests",
        rule_id=seed.attack_type,
        auto_healable=False,  # Security tests need review
        requires_approval=result.bypassed,  # Bypassed attacks need attention
        raw_data={
            "seed_name": seed.name,
            "attack_type": seed.attack_type,
            "difficulty": seed.difficulty,
            "bypassed": result.bypassed,
            "exit_code": result.exit_code,
            "execution_time_ms": result.execution_time_ms,
            "analysis": result.analysis,
        },
    )


def adapt_test_result_to_reactor(
    result: TestResult,
    seed: AttackSeed,
) -> DriftEvent:
    """
    Adapt Prakriti TestResult → ReactorProtocol DriftEvent.

    This allows Prakriti to feed into drift detection.
    """
    from vibe_core.protocols.reactor import DriftSeverity as ReactorSeverity

    # Map severity
    if result.bypassed and seed.difficulty >= 5:
        severity = ReactorSeverity.ERROR
    elif result.bypassed:
        severity = ReactorSeverity.WARNING
    else:
        severity = ReactorSeverity.INFO

    return DriftEvent(
        id=f"prakriti_{seed.name}_{uuid4().hex[:8]}",
        type=DriftType.RELIABILITY,  # Test reliability
        severity=severity,
        message=f"Prakriti attack '{seed.name}': {'BYPASSED' if result.bypassed else 'BLOCKED'}",
        source="prakriti",
        data={
            "seed_name": seed.name,
            "attack_type": seed.attack_type,
            "bypassed": result.bypassed,
            "exit_code": result.exit_code,
        },
    )


# =============================================================================
# PRAKRITI DRIFT DETECTOR (for DriftRegistry)
# =============================================================================


class PrakritiDriftDetector:
    """
    Prakriti as a DriftDetector for DriftRegistry.

    Runs all attack seeds and reports bypassed attacks as drift.
    """

    def __init__(
        self,
        framework: LivingTestFramework,
        target_module: str = "test_module",
    ):
        self._framework = framework
        self._target_module = target_module
        self._last_results: List[TestResult] = []

    async def detect(self) -> List[UnifiedDriftReport]:
        """
        Run all attacks and return drifts for bypassed ones.

        This is called by DriftRegistry.detect_all()
        """
        drifts = []

        # Run all attacks
        seeds = self._framework.get_seeds()
        for seed in seeds:
            result = await self._framework.run_attack(seed, self._target_module)
            self._last_results.append(result)

            # Only report bypassed attacks as drift
            if result.bypassed:
                drift = adapt_test_result_to_drift(result, seed, self._target_module)
                drifts.append(drift)

        logger.info(f"🔬 Prakriti detected {len(drifts)} bypassed attacks out of {len(seeds)} total")
        return drifts

    def __call__(self) -> List[UnifiedDriftReport]:
        """Sync wrapper for async detect."""
        import asyncio

        return asyncio.run(self.detect())


# =============================================================================
# PRAKRITI CORRECTION HANDLER (for CorrectionDispatcher)
# =============================================================================


class PrakritiCorrectionHandler:
    """
    Handler for Prakriti-detected drifts.

    When an attack bypasses defense, this handler:
    1. Records to Sesha ledger
    2. Suggests defense improvements
    3. Optionally triggers Diamond Protocol
    """

    def __init__(self, workspace: Path = None):
        self._workspace = workspace or Path.cwd()

    def handle(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy,
    ) -> HealingResult:
        """
        Handle a Prakriti drift report.

        For RESONANCE strategy, we compute the appropriate action.
        """
        # Extract Prakriti data
        raw = drift.raw_data
        seed_name = raw.get("seed_name", "unknown")
        attack_type = raw.get("attack_type", "unknown")
        difficulty = raw.get("difficulty", 1)

        # Record to Sesha if available
        self._record_to_sesha(drift)

        # Determine action based on strategy
        if strategy == HealingStrategy.RESONANCE:
            # Use difficulty as resonance proxy
            # High difficulty (6+) = needs human review
            # Low difficulty (1-3) = can suggest auto-fix
            if difficulty >= 6:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.MANUAL_REQUIRED,
                    handler_id="prakriti",
                    message=f"High-difficulty attack '{seed_name}' requires human review",
                )
            else:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="prakriti",
                    message=f"Attack '{seed_name}' queued for defense improvement",
                )

        elif strategy == HealingStrategy.DRY_RUN:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="prakriti",
                message=f"DRY_RUN: Would improve defense against '{seed_name}'",
            )

        else:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="prakriti",
                message=f"Strategy {strategy} not implemented for Prakriti",
            )

    def _record_to_sesha(self, drift: UnifiedDriftReport) -> None:
        """Record drift to Sesha ledger."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                sesha.record_event(
                    event_type="PRAKRITI_ATTACK_BYPASS",
                    source="prakriti",
                    details=drift.to_dict(),
                )
                logger.info(f"📜 Recorded to Sesha: {drift.id}")
        except Exception as e:
            logger.debug(f"Sesha not available: {e}")

    def __call__(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy,
    ) -> HealingResult:
        """Make handler callable."""
        return self.handle(drift, strategy)


# =============================================================================
# REACTOR INTEGRATION
# =============================================================================


class PrakritiReactorIntegration:
    """
    Integrates Prakriti with ReactorProtocol for drift tracking.

    Updates reactor metrics based on attack results.
    """

    def __init__(self, reactor: ReactorProtocol = None):
        self._reactor = reactor or BasicReactor()

    def record_attack_result(self, result: TestResult, seed: AttackSeed) -> None:
        """Record attack result to reactor metrics."""
        # Update metrics for this attack type
        command = f"prakriti_attack_{seed.attack_type}"
        success = not result.bypassed  # Defense success = attack blocked

        self._reactor.update_metrics(
            command=command,
            duration_ms=result.execution_time_ms,
            success=success,
        )

    def detect_defense_drift(self) -> List[DriftEvent]:
        """Detect if defense effectiveness is drifting."""
        return self._reactor.detect_drift()


# =============================================================================
# WIRING HELPER
# =============================================================================


def wire_prakriti_to_protocols(
    framework: LivingTestFramework,
    target_module: str = "test_module",
) -> Dict[str, Any]:
    """
    Wire Prakriti to all relevant protocols.

    Returns dict of wired components for inspection.

    Usage:
        framework = LivingTestFramework()
        framework.add_seed_dir(Path("seeds/"))

        wiring = wire_prakriti_to_protocols(framework, "my_module")

        # Now Prakriti is connected to:
        # - DriftRegistry (as detector)
        # - CorrectionDispatcher (as handler)
        # - Reactor (for metrics)
    """
    wiring = {}

    # 1. Create detector
    detector = PrakritiDriftDetector(framework, target_module)
    wiring["detector"] = detector

    # 2. Create handler
    handler = PrakritiCorrectionHandler()
    wiring["handler"] = handler

    # 3. Create reactor integration
    reactor_integration = PrakritiReactorIntegration()
    wiring["reactor"] = reactor_integration

    # 4. Wire callbacks
    def on_attack_complete(seed: AttackSeed, result: TestResult):
        reactor_integration.record_attack_result(result, seed)

    framework.on_attack_bypassed(on_attack_complete)
    framework.on_defense_held(on_attack_complete)

    # 5. Try to register with DriftRegistry if available
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.correction import DriftRegistryProtocol

        registry = ServiceRegistry.get(DriftRegistryProtocol)
        if registry:
            registry.register_detector(
                source=DriftSource.STRUCTURAL,
                detector=detector,
                detector_id="prakriti_living_tests",
            )
            logger.info("✅ Prakriti registered with DriftRegistry")
            wiring["registry_registered"] = True
    except Exception as e:
        logger.debug(f"DriftRegistry not available: {e}")
        wiring["registry_registered"] = False

    # 6. Try to register handler with CorrectionDispatcher
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.correction import CorrectionDispatcherProtocol

        dispatcher = ServiceRegistry.get(CorrectionDispatcherProtocol)
        if dispatcher:
            dispatcher.register_handler(
                source=DriftSource.STRUCTURAL,
                handler=handler,
                handler_id="prakriti_handler",
                priority=10,  # Higher priority for security
            )
            logger.info("✅ Prakriti handler registered with CorrectionDispatcher")
            wiring["dispatcher_registered"] = True
    except Exception as e:
        logger.debug(f"CorrectionDispatcher not available: {e}")
        wiring["dispatcher_registered"] = False

    logger.info(f"🔌 Prakriti wiring complete: {wiring}")
    return wiring


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Adapters
    "adapt_test_result_to_drift",
    "adapt_test_result_to_reactor",
    # Components
    "PrakritiDriftDetector",
    "PrakritiCorrectionHandler",
    "PrakritiReactorIntegration",
    # Helper
    "wire_prakriti_to_protocols",
]
