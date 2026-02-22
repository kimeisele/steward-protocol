"""
Shuddhi Kala Bridge - The Temporal Guardian (BeatSubscriber)
============================================================

Subscribes to VenuService heartbeat via BeatSubscriberProtocol.
Auto-discovered at boot — no manual wiring.

Two cycles, both derived from SSOT:
1. Log scan every NADI (72 ticks = 18s) — detects runtime errors
2. Watchman patrol every NADI × SHARANAGATI (432 ticks = 108s) — code violations

MIGRATION (Feb 2026):
    Was: PulseManager subscriber (1s legacy heartbeat)
    Now: BeatSubscriberProtocol (250ms VenuService heartbeat)
    Why: One heartbeat, not two. VenuService is the drummer.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x39f0252d"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import Optional

from vibe_core.mahamantra import SHARANAGATI, VENU_NADI_TICKS

logger = logging.getLogger("SHUDDHI.KALA")

# Patrol interval: NADI × SHARANAGATI = 72 × 6 = 432 ticks = 108s
# This is exactly MALA (108) seconds — harmonically derived.
_PATROL_EVERY_N_NADIS: int = SHARANAGATI  # 6


class KalaBridgeSubscriber:
    """
    Temporal guardian for log scanning and watchman patrol.

    Implements BeatSubscriberProtocol. VenuService discovers this
    at boot via ServiceRegistry.get_all(BeatSubscriberProtocol).

    Beat interval: NADI (72 ticks = 18s) for log scan.
    Patrol: every 6th NADI (432 ticks = 108s) for watchman.

    Zero-arg constructor: project_root resolved lazily from ServiceRegistry.
    """

    def __init__(self) -> None:
        self._project_root: Optional[Path] = None
        self._nadi_count: int = 0

    @property
    def beat_name(self) -> str:
        return "kala_bridge"

    @property
    def beat_interval(self) -> int:
        return VENU_NADI_TICKS  # 72 ticks = 18 seconds

    def on_beat_tick(self, tick_count: int, position: int) -> None:
        """Called by VenuService every NADI interval."""
        self._nadi_count += 1

        # Log scan — every NADI
        self._run_log_scan()

        # Watchman patrol — every SHARANAGATI NADIs (108s)
        if self._nadi_count % _PATROL_EVERY_N_NADIS == 0:
            self._run_watchman_patrol()

    def _resolve_project_root(self) -> Optional[Path]:
        if self._project_root is not None:
            return self._project_root
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols import VibeKernel

            kernel = ServiceRegistry.get(VibeKernel)
            if kernel and hasattr(kernel, "project_root"):
                return kernel.project_root
        except Exception:
            pass
        return None

    def _run_log_scan(self) -> None:
        """Execute log scan and create tasks for detected errors."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.task import TaskProtocol

            task_service = ServiceRegistry.get(TaskProtocol)
            if not task_service:
                return

            project_root = self._resolve_project_root()
            if not project_root:
                return

            journal_path = project_root / "data" / "system_journal.jsonl"
            from vibe_core.shuddhi.log_monitor import LogMonitor

            monitor = LogMonitor(journal_path, task_service)
            tasks_created = monitor.scan_and_task()

            if tasks_created > 0:
                logger.info(
                    "[KALA] Log scan: %d tasks created (nadi %d)",
                    tasks_created,
                    self._nadi_count,
                )
        except Exception as e:
            logger.debug("[KALA] Log scan failed: %s", e)

    def _run_watchman_patrol(self) -> None:
        """Trigger watchman deep inspection via task dispatch."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.task import TaskProtocol

            task_service = ServiceRegistry.get(TaskProtocol)
            if not task_service:
                return

            existing = [t for t in task_service.list_tasks() if t.title == "PATROL: Watchman Deep Inspection"]
            if existing:
                return

            task_service.add_task(
                title="PATROL: Watchman Deep Inspection",
                description=(
                    "Periodic code quality patrol triggered by Kala Bridge.\n"
                    "Runs StandardsInspectionTool on system agents.\n"
                    "Creates healing tasks for violations with remedies."
                ),
                priority=70,
                assigned_agent="watchman",
            )
            logger.info("[KALA] Watchman patrol dispatched (nadi %d)", self._nadi_count)
        except Exception as e:
            logger.debug("[KALA] Patrol dispatch failed: %s", e)


__all__ = ["KalaBridgeSubscriber"]
