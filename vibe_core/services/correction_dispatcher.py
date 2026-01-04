"""
OPUS-LZ2: CorrectionDispatcher Service - Unified Drift Detection & Healing.

Implementation of the CorrectionDispatcher protocols.

Architecture:
    ┌─────────────────────────────────────────────────┐
    │  BasicDriftRegistry                             │
    │  ├── Wraps existing detectors                   │
    │  ├── ReactorProtocol → performance/reliability  │
    │  ├── VajraEnforcer → config                     │
    │  ├── ShuddhiEngine → structural                 │
    │  └── DriftDetector → code_doc                   │
    │                                                 │
    │  BasicCorrectionDispatcher                      │
    │  ├── Routes by DriftSource                      │
    │  ├── Priority-ordered handlers                  │
    │  └── Feeds results to Knowledge Graph           │
    │                                                 │
    │  BasicCorrectionOrchestrator                    │
    │  ├── High-level API for callers                 │
    │  └── What biorhythm.py should use               │
    └─────────────────────────────────────────────────┘

Usage:
    # Register with ServiceRegistry at boot
    from vibe_core.services.correction_dispatcher import BasicCorrectionOrchestrator

    orchestrator = BasicCorrectionOrchestrator()
    ServiceRegistry.register(CorrectionOrchestratorProtocol, orchestrator)

    # In biorhythm.py (observation only):
    orchestrator = ServiceRegistry.get(CorrectionOrchestratorProtocol)
    drifts = orchestrator.detect_and_report()
    healable = [d for d in drifts if d.auto_healable]

    # In healing circuit (actual healing):
    results = orchestrator.detect_and_heal(strategy=HealingStrategy.AUTO)
"""

import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from vibe_core.protocols.correction import (
    CorrectionDispatcherProtocol,
    CorrectionHandler,
    CorrectionOrchestratorProtocol,
    CorrectionStats,
    DriftDetector,
    DriftRegistryProtocol,
    DriftSeverity,
    DriftSource,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    HealingStrategyResolverProtocol,
    UnifiedDriftReport,
    adapt_reactor_drift,
    adapt_shuddhi_result,
)

logger = logging.getLogger("CORRECTION_DISPATCHER")


# =============================================================================
# Basic Implementations
# =============================================================================


class BasicDriftRegistry:
    """
    In-memory drift registry.

    Manages detector registration and runs detection passes.
    """

    def __init__(self):
        # source -> [(detector_id, detector_fn)]
        self._detectors: Dict[DriftSource, List[Tuple[str, DriftDetector]]] = defaultdict(list)
        self._detector_ids: Set[str] = set()
        self._last_results: List[UnifiedDriftReport] = []

    def register_detector(
        self,
        source: DriftSource,
        detector: DriftDetector,
        detector_id: str = "",
    ) -> None:
        """Register a drift detector."""
        if not detector_id:
            detector_id = f"{source.value}_{uuid.uuid4().hex[:8]}"

        if detector_id in self._detector_ids:
            logger.warning(f"Detector {detector_id} already registered, skipping")
            return

        self._detectors[source].append((detector_id, detector))
        self._detector_ids.add(detector_id)
        logger.info(f"Registered detector: {detector_id} for source {source.value}")

    def unregister_detector(self, detector_id: str) -> bool:
        """Remove a detector by ID."""
        if detector_id not in self._detector_ids:
            return False

        for source, detectors in self._detectors.items():
            self._detectors[source] = [(did, d) for did, d in detectors if did != detector_id]

        self._detector_ids.discard(detector_id)
        logger.info(f"Unregistered detector: {detector_id}")
        return True

    def detect(self, source: Optional[DriftSource] = None) -> List[UnifiedDriftReport]:
        """Run detection for a specific source."""
        results: List[UnifiedDriftReport] = []

        sources = [source] if source else list(self._detectors.keys())

        for src in sources:
            for detector_id, detector in self._detectors.get(src, []):
                try:
                    drifts = detector()
                    for drift in drifts:
                        drift.detector_id = detector_id
                    results.extend(drifts)
                except Exception as e:
                    logger.warning(f"Detector {detector_id} failed: {e}")

        self._last_results = results
        return results

    def detect_all(self) -> List[UnifiedDriftReport]:
        """Run all registered detectors."""
        return self.detect(source=None)

    def get_detector_ids(self) -> List[str]:
        """List all registered detector IDs."""
        return list(self._detector_ids)


class BasicCorrectionDispatcher:
    """
    In-memory correction dispatcher.

    Routes drifts to appropriate handlers based on source.
    Handlers are called in priority order (highest first).
    """

    def __init__(self):
        # source -> [(priority, handler_id, handler_fn)]
        self._handlers: Dict[DriftSource, List[Tuple[int, str, CorrectionHandler]]] = defaultdict(list)
        self._handler_ids: Set[str] = set()
        self._stats = CorrectionStats()

    def register_handler(
        self,
        source: DriftSource,
        handler: CorrectionHandler,
        handler_id: str = "",
        priority: int = 0,
    ) -> None:
        """Register a correction handler."""
        if not handler_id:
            handler_id = f"{source.value}_handler_{uuid.uuid4().hex[:8]}"

        if handler_id in self._handler_ids:
            logger.warning(f"Handler {handler_id} already registered, skipping")
            return

        self._handlers[source].append((priority, handler_id, handler))
        # Sort by priority descending
        self._handlers[source].sort(key=lambda x: -x[0])
        self._handler_ids.add(handler_id)
        self._stats.handlers_registered = len(self._handler_ids)
        logger.info(f"Registered handler: {handler_id} for source {source.value} (priority={priority})")

    def unregister_handler(self, handler_id: str) -> bool:
        """Remove a handler by ID."""
        if handler_id not in self._handler_ids:
            return False

        for source, handlers in self._handlers.items():
            self._handlers[source] = [(p, hid, h) for p, hid, h in handlers if hid != handler_id]

        self._handler_ids.discard(handler_id)
        self._stats.handlers_registered = len(self._handler_ids)
        logger.info(f"Unregistered handler: {handler_id}")
        return True

    def dispatch(
        self,
        drift: UnifiedDriftReport,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> HealingResult:
        """Dispatch a drift to appropriate handler(s)."""
        start_time = time.time()
        self._stats.healings_attempted += 1

        # Get handlers for this drift source
        handlers = self._handlers.get(drift.source, [])

        if not handlers:
            logger.debug(f"No handlers for drift source {drift.source.value}")
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="none",
                message=f"No handler registered for source {drift.source.value}",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Try handlers in priority order
        for priority, handler_id, handler in handlers:
            try:
                result = handler(drift, strategy)
                result.duration_ms = (time.time() - start_time) * 1000

                if result.healed:
                    self._stats.healings_succeeded += 1
                    logger.info(f"Drift {drift.id} healed by {handler_id}")
                    return result
                elif result.status == HealingStatus.FAILED:
                    self._stats.healings_failed += 1
                    # Try next handler
                    continue
                else:
                    # SKIPPED, DEFERRED, MANUAL_REQUIRED - return as-is
                    return result

            except Exception as e:
                logger.warning(f"Handler {handler_id} failed for drift {drift.id}: {e}")
                self._stats.healings_failed += 1
                continue

        # All handlers failed or skipped
        return HealingResult(
            drift_id=drift.id,
            status=HealingStatus.FAILED,
            handler_id="all",
            message="All handlers failed or skipped",
            duration_ms=(time.time() - start_time) * 1000,
        )

    def dispatch_all(
        self,
        drifts: List[UnifiedDriftReport],
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
    ) -> List[HealingResult]:
        """Dispatch multiple drifts."""
        self._stats.last_healing_run = datetime.now()
        return [self.dispatch(drift, strategy) for drift in drifts]

    def can_heal(self, drift: UnifiedDriftReport) -> bool:
        """Check if a handler exists for this drift source."""
        return len(self._handlers.get(drift.source, [])) > 0

    def get_handler_ids(self) -> List[str]:
        """List all registered handler IDs."""
        return list(self._handler_ids)

    def get_stats(self) -> CorrectionStats:
        """Get dispatcher statistics."""
        return self._stats


class BasicCorrectionOrchestrator:
    """
    High-level orchestrator combining detection and dispatch.

    This is what callers (biorhythm, CLI, etc.) should use.
    """

    def __init__(
        self,
        registry: Optional[DriftRegistryProtocol] = None,
        dispatcher: Optional[CorrectionDispatcherProtocol] = None,
        resolver: Optional["HealingStrategyResolverProtocol"] = None,
        skip_default_init: bool = False,
    ):
        self._registry = registry or BasicDriftRegistry()
        self._dispatcher = dispatcher or BasicCorrectionDispatcher()
        self._resolver = resolver  # Lazy-loaded if None
        self._initialized = skip_default_init  # Skip if explicitly set

    @property
    def resolver(self) -> Optional["HealingStrategyResolverProtocol"]:
        """Access the healing strategy resolver (lazy-loaded)."""
        if self._resolver is None:
            try:
                from vibe_core.services.healing_resolver import get_healing_resolver

                self._resolver = get_healing_resolver()
            except ImportError:
                pass
        return self._resolver

    @property
    def registry(self) -> DriftRegistryProtocol:
        """Access the drift registry."""
        return self._registry

    @property
    def dispatcher(self) -> CorrectionDispatcherProtocol:
        """Access the correction dispatcher."""
        return self._dispatcher

    def initialize_default_detectors(self) -> None:
        """
        Wire up default detectors from ServiceRegistry.

        Call this after ServiceRegistry is populated.
        """
        if self._initialized:
            return

        try:
            from vibe_core.di import ServiceRegistry

            # Wire ReactorProtocol → performance/reliability
            self._wire_reactor_detector(ServiceRegistry)

            # Wire ShuddhiProtocol → structural
            self._wire_shuddhi_detector(ServiceRegistry)

            # Wire VajraEnforcer → config (if available)
            self._wire_vajra_detector()

            self._initialized = True
            logger.info("CorrectionOrchestrator initialized with default detectors")

        except ImportError as e:
            logger.warning(f"Could not initialize default detectors: {e}")

    def _wire_reactor_detector(self, service_registry) -> None:
        """Wire ReactorProtocol as a detector."""
        from vibe_core.protocols.reactor import ReactorProtocol

        reactor = service_registry.get(ReactorProtocol)
        if reactor is None:
            logger.debug("ReactorProtocol not registered, skipping")
            return

        def reactor_detector() -> List[UnifiedDriftReport]:
            events = reactor.detect_drift()
            return [adapt_reactor_drift(e) for e in events]

        self._registry.register_detector(
            DriftSource.PERFORMANCE,
            reactor_detector,
            "reactor_performance",
        )

    def _wire_shuddhi_detector(self, service_registry) -> None:
        """Wire ShuddhiProtocol as a detector."""
        from vibe_core.protocols.shuddhi import ShuddhiProtocol

        shuddhi = service_registry.get(ShuddhiProtocol)
        if shuddhi is None:
            logger.debug("ShuddhiProtocol not registered, skipping")
            return

        def shuddhi_detector() -> List[UnifiedDriftReport]:
            # Shuddhi doesn't detect - it heals.
            # We need to get violations from Knowledge Graph instead.
            # For now, return empty - violations come from other sources.
            return []

        # Register Shuddhi as a HANDLER, not detector
        def shuddhi_handler(
            drift: UnifiedDriftReport,
            strategy: HealingStrategy,
        ) -> HealingResult:
            if drift.source != DriftSource.STRUCTURAL:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="shuddhi",
                    message="Not a structural drift",
                )

            if not drift.file_path or not drift.rule_id:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.SKIPPED,
                    handler_id="shuddhi",
                    message="Missing file_path or rule_id",
                )

            if not shuddhi.can_heal(drift.rule_id):
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.MANUAL_REQUIRED,
                    handler_id="shuddhi",
                    message=f"No remedy for rule {drift.rule_id}",
                )

            if strategy == HealingStrategy.DRY_RUN:
                return HealingResult(
                    drift_id=drift.id,
                    status=HealingStatus.DEFERRED,
                    handler_id="shuddhi",
                    message="Dry run - healing available but not applied",
                )

            # Actually heal
            result = shuddhi.purify(drift.file_path, drift.rule_id)
            return adapt_shuddhi_result(result, drift.id)

        self._dispatcher.register_handler(
            DriftSource.STRUCTURAL,
            shuddhi_handler,
            "shuddhi_structural",
            priority=100,  # High priority
        )

    def _wire_vajra_detector(self) -> None:
        """Wire VajraEnforcer as a config drift detector."""
        try:
            from vibe_core.vajra.enforcement import VajraEnforcer

            enforcer = VajraEnforcer()

            def vajra_detector() -> List[UnifiedDriftReport]:
                # VajraEnforcer.detect_drift needs runtime state
                # For now, return empty - would need kernel context
                return []

            self._registry.register_detector(
                DriftSource.CONFIG,
                vajra_detector,
                "vajra_config",
            )

        except ImportError:
            logger.debug("VajraEnforcer not available, skipping")

    def detect_and_report(
        self,
        source: Optional[DriftSource] = None,
    ) -> List[UnifiedDriftReport]:
        """
        Run detection and return reports (no healing).

        Use this for observation/reporting.
        """
        if not self._initialized:
            self.initialize_default_detectors()

        drifts = self._registry.detect(source)
        self._dispatcher._stats.drifts_detected += len(drifts)
        self._dispatcher._stats.last_detection_run = datetime.now()

        logger.info(f"Detection complete: {len(drifts)} drifts found")
        return drifts

    def detect_and_heal(
        self,
        source: Optional[DriftSource] = None,
        strategy: HealingStrategy = HealingStrategy.DRY_RUN,
        agent_id: Optional[str] = None,
        auto_only: bool = True,
    ) -> List[HealingResult]:
        """
        Run detection and dispatch corrections.

        Args:
            source: Filter to specific source, or None for all
            strategy: How to apply corrections (or RESONANCE to use resolver)
            agent_id: Agent requesting healing (required for RESONANCE strategy)
            auto_only: Only heal drifts marked auto_healable

        Returns:
            List of healing results
        """
        drifts = self.detect_and_report(source)

        if auto_only:
            drifts = [d for d in drifts if d.auto_healable]

        if not drifts:
            logger.info("No healable drifts found")
            return []

        results = []
        for drift in drifts:
            # Resolve strategy per-drift if using RESONANCE
            effective_strategy = strategy
            if strategy == HealingStrategy.RESONANCE:
                if agent_id and self.resolver:
                    effective_strategy = self.resolver.resolve(agent_id, drift)
                    logger.debug(f"Resolved strategy for {agent_id}: {effective_strategy.value}")
                else:
                    logger.warning("RESONANCE strategy requires agent_id and resolver, falling back to DRY_RUN")
                    effective_strategy = HealingStrategy.DRY_RUN

            result = self._dispatcher.dispatch(drift, effective_strategy)
            results.append(result)

        healed = sum(1 for r in results if r.healed)
        logger.info(f"Healing complete: {healed}/{len(drifts)} drifts healed")

        return results

    def get_healable_count(self) -> Dict[DriftSource, int]:
        """Get count of healable drifts by source."""
        drifts = self.detect_and_report()
        counts: Dict[DriftSource, int] = defaultdict(int)

        for drift in drifts:
            if self._dispatcher.can_heal(drift):
                counts[drift.source] += 1

        return dict(counts)


# =============================================================================
# Detector/Handler Factories
# =============================================================================


def create_structural_detector(
    workspace: Path,
    knowledge_graph: Optional[Any] = None,
) -> DriftDetector:
    """
    Create a detector for structural violations.

    Reads violations from Knowledge Graph or scans with Vajra.
    """

    def detector() -> List[UnifiedDriftReport]:
        reports: List[UnifiedDriftReport] = []

        # Try Knowledge Graph first
        if knowledge_graph is not None:
            try:
                violations = knowledge_graph.get_violations(healed=False)
                for v in violations:
                    reports.append(
                        UnifiedDriftReport(
                            id=f"structural_{uuid.uuid4().hex[:8]}",
                            source=DriftSource.STRUCTURAL,
                            severity=DriftSeverity.WARNING,
                            message=v.get("message", "Structural violation"),
                            file_path=Path(v["file_path"]) if v.get("file_path") else None,
                            line_number=v.get("line"),
                            rule_id=v.get("rule_id"),
                            auto_healable=v.get("has_remedy", False),
                            detector_id="knowledge_graph",
                        )
                    )
            except Exception as e:
                logger.debug(f"Knowledge graph query failed: {e}")

        # Fallback: scan with Vajra
        if not reports:
            try:
                from vibe_core.vajra.scanner import VajraScanner

                scanner = VajraScanner(workspace)
                violations = scanner.scan()

                for v in violations:
                    reports.append(
                        UnifiedDriftReport(
                            id=f"structural_{uuid.uuid4().hex[:8]}",
                            source=DriftSource.STRUCTURAL,
                            severity=DriftSeverity.WARNING,
                            message=v.message,
                            file_path=v.file_path,
                            line_number=v.line,
                            rule_id=v.rule_id,
                            auto_healable=v.has_remedy,
                            detector_id="vajra_scanner",
                        )
                    )
            except Exception as e:
                logger.debug(f"Vajra scan failed: {e}")

        return reports

    return detector


def create_code_doc_detector(workspace: Path) -> DriftDetector:
    """
    Create a detector for code-documentation drift.

    Uses opus_assistant's DriftDetector.
    """

    def detector() -> List[UnifiedDriftReport]:
        reports: List[UnifiedDriftReport] = []

        try:
            from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

            dd = DriftDetector(workspace)
            result = dd.detect()

            if result.get("has_drift"):
                for item in result.get("drift_items", []):
                    reports.append(
                        UnifiedDriftReport(
                            id=f"code_doc_{uuid.uuid4().hex[:8]}",
                            source=DriftSource.CODE_DOC,
                            severity=DriftSeverity.INFO,
                            message=item.get("description", "Code-doc drift"),
                            file_path=Path(item["file"]) if item.get("file") else None,
                            component=item.get("component"),
                            auto_healable=False,  # Code-doc drift needs human review
                            detector_id="opus_drift_detector",
                            raw_data=item,
                        )
                    )
        except Exception as e:
            logger.debug(f"Code-doc drift detection failed: {e}")

        return reports

    return detector


# =============================================================================
# ServiceRegistry Integration Helper
# =============================================================================


def get_correction_orchestrator() -> CorrectionOrchestratorProtocol:
    """
    Get CorrectionOrchestrator from ServiceRegistry with fallback.

    Usage:
        orchestrator = get_correction_orchestrator()
        drifts = orchestrator.detect_and_report()
    """
    try:
        from vibe_core.di import ServiceRegistry

        orchestrator = ServiceRegistry.get(CorrectionOrchestratorProtocol)
        if orchestrator is not None:
            return orchestrator
    except ImportError:
        pass

    # Fallback to new instance
    return BasicCorrectionOrchestrator()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BasicDriftRegistry",
    "BasicCorrectionDispatcher",
    "BasicCorrectionOrchestrator",
    "create_structural_detector",
    "create_code_doc_detector",
    "get_correction_orchestrator",
]
