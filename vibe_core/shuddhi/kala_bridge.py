"""
Shuddhi Kala Bridge - The Temporal Guardian.

This bridge connects the PulseManager (Time/Kala) with the Shuddhi LogMonitor.
It subscribes to the system pulse and scans logs at regular intervals.
"""

import logging
from pathlib import Path

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.task import TaskService
from vibe_core.pulse import PulsePacket, get_pulse_manager
from vibe_core.shuddhi.log_monitor import LogMonitor

logger = logging.getLogger("SHUDDHI.KALA")


class ShuddhiKalaBridge:
    def __init__(self, project_root: Path, interval_cycles: int = 10):
        self.project_root = project_root
        self.interval_cycles = interval_cycles
        self._pulse_manager = get_pulse_manager()
        self._subscription_id = None
        self._journal_path = project_root / "data" / "system_journal.jsonl"

    def start(self):
        """Subscribe to the system pulse."""
        if self._subscription_id:
            return

        self._subscription_id = self._pulse_manager.subscribe(self.on_pulse)
        logger.info(f"💓 Shuddhi Kala Bridge STARTED (Interval: {self.interval_cycles} cycles)")

    def stop(self):
        """Unsubscribe from the pulse."""
        if self._subscription_id:
            self._pulse_manager.unsubscribe(self.on_pulse)
            self._subscription_id = None
            logger.info("💀 Shuddhi Kala Bridge STOPPED")

    def on_pulse(self, packet: PulsePacket):
        """Callback for each heartbeat."""
        # Only run every N cycles to save resources
        if packet.cycle_id % self.interval_cycles == 0:
            self.run_checks()

    def run_pulse_sync(self, packet: PulsePacket):
        """Synchronous wrapper for pulse events."""
        self.on_pulse(packet)

    def run_checks(self):
        """Execute the log scan and task creation."""
        try:
            task_service = ServiceRegistry.get(TaskService)
            if not task_service:
                return

            monitor = LogMonitor(self._journal_path, task_service)
            tasks_created = monitor.scan_and_task()

            if tasks_created > 0:
                logger.info(f"🛡️ KalaBridge: Created {tasks_created} autonomous tasks from logs.")
        except Exception as e:
            logger.error(f"KalaBridge check failed: {e}")


def start_kala_bridge(project_root: Path) -> ShuddhiKalaBridge:
    """Factory function to start the bridge."""
    bridge = ShuddhiKalaBridge(project_root)
    bridge.start()
    return bridge
