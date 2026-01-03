"""
Shuddhi Kala Bridge - The Temporal Guardian.

This bridge connects the PulseManager (Time/Kala) with the Shuddhi LogMonitor
AND the Watchman patrol. It subscribes to the system pulse and runs checks
at regular intervals.

Two cycles:
1. Log scan (every N cycles) - detects runtime errors
2. Watchman patrol (every M cycles) - detects code violations
"""

import logging
from pathlib import Path

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.task import TaskProtocol
from vibe_core.pulse import PulsePacket, get_pulse_manager
from vibe_core.shuddhi.log_monitor import LogMonitor

logger = logging.getLogger("SHUDDHI.KALA")


class ShuddhiKalaBridge:
    def __init__(
        self,
        project_root: Path,
        log_interval: int = 10,
        patrol_interval: int = 100,  # Patrol less frequently (expensive)
    ):
        self.project_root = project_root
        self.log_interval = log_interval
        self.patrol_interval = patrol_interval
        self._pulse_manager = get_pulse_manager()
        self._subscription_id = None
        self._journal_path = project_root / "data" / "system_journal.jsonl"

    def start(self):
        """Subscribe to the system pulse."""
        if self._subscription_id:
            return

        self._subscription_id = self._pulse_manager.subscribe(self.on_pulse)
        logger.info(
            f"💓 Shuddhi Kala Bridge STARTED (LogScan: {self.log_interval}, Patrol: {self.patrol_interval} cycles)"
        )

    def stop(self):
        """Unsubscribe from the pulse."""
        if self._subscription_id:
            self._pulse_manager.unsubscribe(self.on_pulse)
            self._subscription_id = None
            logger.info("💀 Shuddhi Kala Bridge STOPPED")

    def on_pulse(self, packet: PulsePacket):
        """Callback for each heartbeat."""
        # Log scan - frequent
        if packet.cycle_id % self.log_interval == 0:
            self._run_log_scan()

        # Watchman patrol - less frequent (expensive AST scan)
        if packet.cycle_id % self.patrol_interval == 0:
            self._run_watchman_patrol()

    def run_pulse_sync(self, packet: PulsePacket):
        """Synchronous wrapper for pulse events."""
        self.on_pulse(packet)

    def _run_log_scan(self):
        """Execute the log scan and task creation."""
        try:
            task_service = ServiceRegistry.get(TaskProtocol)
            if not task_service:
                return

            monitor = LogMonitor(self._journal_path, task_service)
            tasks_created = monitor.scan_and_task()

            if tasks_created > 0:
                logger.info(f"🛡️ KalaBridge: Created {tasks_created} log-based tasks.")
        except Exception as e:
            logger.error(f"KalaBridge log scan failed: {e}")

    def _run_watchman_patrol(self):
        """Trigger Watchman deep inspection via task dispatch."""
        try:
            task_service = ServiceRegistry.get(TaskProtocol)
            if not task_service:
                return

            # Check if patrol task already pending
            existing = [t for t in task_service.list_tasks() if t.title == "PATROL: Watchman Deep Inspection"]
            if existing:
                return  # Don't duplicate

            # Create patrol task for Watchman
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
            logger.info("⚔️ KalaBridge: Dispatched Watchman patrol task")
        except Exception as e:
            logger.error(f"KalaBridge patrol dispatch failed: {e}")

    # Legacy method name for backwards compatibility
    def run_checks(self):
        """Execute both log scan and patrol check."""
        self._run_log_scan()


def start_kala_bridge(project_root: Path) -> ShuddhiKalaBridge:
    """Factory function to start the bridge."""
    bridge = ShuddhiKalaBridge(project_root)
    bridge.start()
    return bridge
