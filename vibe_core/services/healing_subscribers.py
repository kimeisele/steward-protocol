"""
HEALING BEAT SUBSCRIBERS - The Organism's Immune System
=======================================================

These subscribers implement BeatSubscriberProtocol to receive
periodic heartbeat callbacks from VenuService.

NO MANUAL WIRING. They register themselves via ServiceRegistry.
VenuService discovers them at boot. Yasoda's rope.

Subscribers:
    OuroborosSubscriber — Violation ingestion every NADI (72 ticks = 18s)
    ShuddhiSubscriber   — CST healing every FIELD (144 ticks = 36s)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x7a2c1e09"

import logging
from pathlib import Path
from typing import Optional

from vibe_core.mahamantra import (
    VENU_FIELD_TICKS,
    VENU_NADI_TICKS,
)

logger = logging.getLogger("HEALING.BEAT")


class OuroborosSubscriber:
    """
    Ingests violations from CI artifacts, reports, audit files,
    AND runtime I/O Sentinel detections.

    Runs every NADI interval (72 ticks = 18 seconds).
    Feeds the Knowledge Graph so ShuddhiEngine knows what to heal.

    The Sentinel→Ouroboros→KG→Shuddhi loop:
        1. Sentinel sees rogue json.dump calls at runtime
        2. drain_violations() harvests them (clears buffer)
        3. ViolationIngester pushes them into KG
        4. ShuddhiSubscriber reads KG and applies CST remedies

    Zero-arg constructor: workspace resolved lazily from ServiceRegistry.
    """

    def __init__(self) -> None:
        self._orchestrator = None  # Lazy

    @property
    def beat_name(self) -> str:
        return "ouroboros_ingestion"

    @property
    def beat_interval(self) -> int:
        return VENU_NADI_TICKS  # 72 ticks = 18 seconds

    def _resolve_workspace(self) -> Optional[Path]:
        """Lazy workspace resolution from ServiceRegistry."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.kernel_protocol import KernelProtocol

            kernel = ServiceRegistry.get(KernelProtocol)
            if kernel and hasattr(kernel, "_workspace"):
                return kernel._workspace
        except Exception:
            pass
        return None

    def _get_orchestrator(self):
        if self._orchestrator is None:
            try:
                from vibe_core.ouroboros.loop_orchestrator import OuroborosLoopOrchestrator

                workspace = self._resolve_workspace()
                self._orchestrator = OuroborosLoopOrchestrator(workspace=workspace)
            except Exception as e:
                logger.debug(f"[OUROBOROS] Could not create orchestrator: {e}")
        return self._orchestrator

    def _ingest_sentinel_violations(self) -> int:
        """Drain I/O Sentinel violations and push into KG."""
        try:
            from vibe_core.mahamantra.substrate.io_sentinel import drain_violations
            from vibe_core.ouroboros.ingestion import ViolationRecord, ViolationSource

            drained = drain_violations()
            if not drained:
                return 0

            records = []
            for v in drained:
                records.append(
                    ViolationRecord(
                        source=ViolationSource.SENTINEL,
                        rule_id="unsafe_io_write",
                        file_path=v["caller_file"],
                        line=v["caller_line"],
                        message=f"Rogue {v['call_type']} in {v['caller_func']}() — bypasses StateService",
                        severity="MEDIUM",
                        has_remedy=True,
                        verification_status="verified",
                        origin="live_scan",
                    )
                )

            orchestrator = self._get_orchestrator()
            if orchestrator is None:
                return 0

            return orchestrator.ingester.ingest(records)
        except Exception as e:
            logger.debug("[OUROBOROS] Sentinel ingestion failed: %s", e)
            return 0

    def on_beat_tick(self, tick_count: int, position: int) -> None:
        # Step 1: Drain runtime Sentinel violations into KG
        sentinel_count = self._ingest_sentinel_violations()
        if sentinel_count > 0:
            logger.info(
                "[OUROBOROS] Sentinel: %d rogue I/O violations ingested (tick %d)",
                sentinel_count,
                tick_count,
            )

        # Step 2: Ingest from CI artifacts / reports (existing path)
        orchestrator = self._get_orchestrator()
        if orchestrator is None:
            return

        try:
            result = orchestrator.ingest_all_sources()
            if result.ingested_count > 0:
                logger.info(
                    f"[OUROBOROS] Ingested {result.ingested_count} violations "
                    f"from {result.sources_parsed} sources (tick {tick_count})"
                )
        except Exception as e:
            logger.debug(f"[OUROBOROS] Ingestion tick failed: {e}")


class ShuddhiSubscriber:
    """
    Heals violations using CST surgery.

    Runs every FIELD interval (144 ticks = 36 seconds).
    Reads unhealed violations from Knowledge Graph, applies remedies.

    Zero-arg constructor: dry_run defaults to True (safe mode).
    """

    def __init__(self) -> None:
        self._dry_run = True  # Safe default — no mutations without explicit opt-in
        self._engine = None  # Lazy

    @property
    def beat_name(self) -> str:
        return "shuddhi_healing"

    @property
    def beat_interval(self) -> int:
        return VENU_FIELD_TICKS  # 144 ticks = 36 seconds

    def _get_engine(self):
        if self._engine is None:
            try:
                from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine

                self._engine = ShuddhiEngine()
            except Exception as e:
                logger.debug(f"[SHUDDHI] Could not create engine: {e}")
        return self._engine

    def on_beat_tick(self, tick_count: int, position: int) -> None:
        engine = self._get_engine()
        if engine is None:
            return

        try:
            results = engine.heal_all_violations(dry_run=self._dry_run)
            healed = sum(1 for r in results if r.status.value == "purified")
            if results:
                logger.info(
                    f"[SHUDDHI] Healing tick: {healed}/{len(results)} healed "
                    f"(dry_run={self._dry_run}, tick {tick_count})"
                )
        except Exception as e:
            logger.debug(f"[SHUDDHI] Healing tick failed: {e}")


__all__ = ["OuroborosSubscriber", "ShuddhiSubscriber"]
