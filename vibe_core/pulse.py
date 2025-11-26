"""
CANTO 10: THE PULSE (Spandana - Primordial Vibration)

This module implements the heartbeat of the VibeOS system.
Every agent's dance is choreographed by this rhythmic vibration.

The Pulse emits a JSON packet at regular intervals containing:
- System state (HEALTHY, DEGRADED, EMERGENCY)
- Active agent list
- Queue depth
- Cycle counter

Frequencies:
- IDLE (0.5Hz): Deep sleep state (Samadhi)
- ACTIVE (1Hz): Normal operations
- STRESS (5Hz): Emergency/High load (Gajendra Protocol)
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import uuid4

logger = logging.getLogger("PULSE")


class SystemState(str, Enum):
    """System health states"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    EMERGENCY = "EMERGENCY"


class PulseFrequency(float, Enum):
    """Heartbeat frequencies in Hz"""
    IDLE = 0.5  # Deep sleep (2 seconds)
    ACTIVE = 1.0  # Normal (1 second)
    STRESS = 5.0  # Emergency (200ms)


@dataclass
class PulsePacket:
    """The heartbeat payload - minimal and efficient (<1KB)"""
    timestamp: str  # ISO 8601
    cycle_id: int  # Monotonic counter
    system_state: str  # HEALTHY, DEGRADED, EMERGENCY
    active_agents: List[str]  # Currently processing
    queue_depth: int  # Tasks in queue
    frequency: float  # Current heartbeat frequency (Hz)

    def to_json(self) -> str:
        """Serialize to JSON (<1KB requirement)"""
        return json.dumps(asdict(self), separators=(',', ':'))


class PulseManager:
    """
    Singleton heartbeat manager for the VibeOS system.

    Non-blocking: Runs on separate asyncio task
    Fault-tolerant: Continues even if subscribers fail
    Efficient: Small payloads, minimal overhead
    """

    _instance: Optional['PulseManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._cycle_id = 0
        self._frequency = PulseFrequency.ACTIVE
        self._system_state = SystemState.HEALTHY
        self._active_agents: List[str] = []
        self._queue_depth = 0
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._subscribers: List[callable] = []
        self._last_packet: Optional[PulsePacket] = None

        logger.info("🫀 PulseManager initialized (Singleton)")

    async def start(self):
        """Start the heartbeat loop"""
        if self._running:
            logger.warning("⚠️  Pulse already running")
            return

        self._running = True
        logger.info("💓 Pulse STARTED - Heart begins to beat...")
        self._task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self):
        """Stop the heartbeat loop gracefully"""
        self._running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️  Heartbeat loop timeout on shutdown")
                self._task.cancel()

        logger.info("💀 Pulse STOPPED - Heart falls silent")

    async def _heartbeat_loop(self):
        """
        Main heartbeat loop - runs continuously in background
        Emits pulse packets at configured frequency
        """
        try:
            while self._running:
                # Create packet
                packet = self._create_packet()
                self._last_packet = packet

                # Emit to all subscribers (non-blocking)
                await self._emit_packet(packet)

                # Calculate sleep duration
                sleep_duration = 1.0 / self._frequency.value  # Convert Hz to seconds

                # Sleep until next beat
                await asyncio.sleep(sleep_duration)

        except asyncio.CancelledError:
            logger.info("💗 Heartbeat loop cancelled (expected during shutdown)")
        except Exception as e:
            logger.error(f"❌ Heartbeat loop error: {e}", exc_info=True)
            self._running = False

    def _create_packet(self) -> PulsePacket:
        """Create a heartbeat packet"""
        self._cycle_id += 1

        return PulsePacket(
            timestamp=datetime.utcnow().isoformat() + "Z",
            cycle_id=self._cycle_id,
            system_state=self._system_state.value,
            active_agents=self._active_agents.copy(),
            queue_depth=self._queue_depth,
            frequency=self._frequency.value
        )

    async def _emit_packet(self, packet: PulsePacket):
        """
        Emit packet to all subscribers
        Fault-tolerant: Errors in one subscriber don't affect others
        """
        failed_subscribers = []

        for subscriber in self._subscribers:
            try:
                # Handle both async and sync subscribers
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(packet)
                else:
                    subscriber(packet)
            except Exception as e:
                logger.warning(f"⚠️  Subscriber error: {e}")
                failed_subscribers.append(subscriber)

        # Remove failed subscribers (cleanup)
        for sub in failed_subscribers:
            self._subscribers.remove(sub)

    def subscribe(self, callback: callable) -> str:
        """
        Subscribe to heartbeat events
        Returns subscription ID for unsubscribe
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"📡 New subscriber registered (total: {len(self._subscribers)})")

        return str(uuid4())

    def unsubscribe(self, callback: callable):
        """Unsubscribe from heartbeat events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"📡 Subscriber removed (total: {len(self._subscribers)})")

    def set_frequency(self, frequency: PulseFrequency):
        """Change heartbeat frequency (IDLE/ACTIVE/STRESS)"""
        self._frequency = frequency
        logger.info(f"⚡ Pulse frequency changed to {frequency.value}Hz ({frequency.name})")

    def set_system_state(self, state: SystemState):
        """Update system health state"""
        self._system_state = state
        logger.warning(f"🔴 System state: {state.value}")

    def update_active_agents(self, agents: List[str]):
        """Update list of currently active agents"""
        self._active_agents = agents

    def update_queue_depth(self, depth: int):
        """Update task queue depth"""
        self._queue_depth = depth

    def get_status(self) -> Dict[str, Any]:
        """Get current pulse status"""
        return {
            "running": self._running,
            "cycle_id": self._cycle_id,
            "frequency": self._frequency.value,
            "system_state": self._system_state.value,
            "active_agents": len(self._active_agents),
            "queue_depth": self._queue_depth,
            "subscribers": len(self._subscribers),
            "last_packet": asdict(self._last_packet) if self._last_packet else None
        }

    def get_last_packet(self) -> Optional[PulsePacket]:
        """Get the most recent pulse packet (for new WebSocket connections)"""
        return self._last_packet


# Module-level convenience function
def get_pulse_manager() -> PulseManager:
    """Get the global pulse manager singleton"""
    return PulseManager()
