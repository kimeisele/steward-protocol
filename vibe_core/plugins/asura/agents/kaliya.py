"""
KALIYA: The Toxic Stream.

Krishna Lila: The serpent Kaliya poisoned the River Yamuna so severely
that no bird could fly over it. Krishna jumped in and danced on
Kaliya's many heads, subduing (not killing) the serpent.

Cyber Translation: The EventBus is the River Yamuna.
If an agent (Kaliya) floods the bus with toxic events,
all other agents starve (bandwidth) or crash (parsing).

Attack Vectors (Multi-Headed):
- Head 1 (Flooder): Spam 10,000 high-volume events
- Head 2 (Ouroboros): Causal loops (causation_id references self)
- Head 3 (Heavy Payload): Large payloads near memory limits

Test Goal:
Can the kernel "dance on the heads" (rate limit, circuit break)?
Or does the system go down (DoS)?

<!-- @HARNESS
files:
  - path: vibe_core/plugins/asura/agents/kaliya.py
    required: true
wiring:
  - pattern: "class KaliyaAgent"
    in: vibe_core/plugins/asura/agents/kaliya.py
  - pattern: "_head_flooder"
    in: vibe_core/plugins/asura/agents/kaliya.py
tests:
  - tests/hardening/test_kaliya_stream.py
-->
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, List, Optional

logger = logging.getLogger("ASURA.KALIYA")


@dataclass
class KaliyaAttackResult:
    """Results of the Kaliya flood attack."""
    events_sent: int
    duration_seconds: float
    events_per_second: float
    heads_active: int
    target_responsive: bool


class KaliyaAgent:
    """
    KALIYA: The Toxic Stream.

    Multi-headed flood attack on the EventBus.
    Tests rate limiting and backpressure capabilities.

    Heads:
    - Flooder: Raw volume attack
    - Ouroboros: Causal loop attack
    - Heavy: Memory pressure attack
    """

    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.heads: List[asyncio.Task] = []
        self.stop_flag = False
        self.events_sent = 0
        self.attack_start: Optional[float] = None
        self.attack_end: Optional[float] = None

    async def attack(self, duration_seconds: float = 2.0) -> KaliyaAttackResult:
        """
        Execute the multi-headed flood attack.

        Args:
            duration_seconds: How long to flood (default 2s)

        Returns:
            KaliyaAttackResult with metrics
        """
        logger.warning("🐍 KALIYA: Poisoning the Yamuna (EventBus)...")

        self.stop_flag = False
        self.events_sent = 0
        self.attack_start = time.time()

        # Calculate end time
        end_time = time.time() + duration_seconds

        # Launch all heads
        self.heads = [
            asyncio.create_task(self._head_flooder(end_time)),
            asyncio.create_task(self._head_ouroboros(end_time)),
            asyncio.create_task(self._head_heavy_payload(end_time)),
        ]

        # Wait for all heads to complete
        await asyncio.gather(*self.heads, return_exceptions=True)

        self.attack_end = time.time()
        duration = self.attack_end - self.attack_start

        # Calculate metrics
        result = KaliyaAttackResult(
            events_sent=self.events_sent,
            duration_seconds=duration,
            events_per_second=self.events_sent / duration if duration > 0 else 0,
            heads_active=len(self.heads),
            target_responsive=True  # Will be tested after attack
        )

        logger.warning(f"🐍 KALIYA: Attack complete. {result.events_sent} events in {duration:.2f}s")
        return result

    async def _head_flooder(self, end_time: float):
        """
        Head 1: Pure volume attack.
        Floods the bus with minimal events as fast as possible.
        """
        from vibe_core.event_bus import Event

        while time.time() < end_time and not self.stop_flag:
            try:
                event = Event(
                    event_type="KALIYA_FLOOD",
                    agent_id="kaliya_serpent",
                    message="Choke!",
                    details={"head": "flooder", "toxic": True},
                )
                await self.event_bus.emit(event)
                self.events_sent += 1

                # No sleep - maximum pressure!
                # But yield to event loop occasionally
                if self.events_sent % 100 == 0:
                    await asyncio.sleep(0)

            except Exception as e:
                logger.debug(f"Flooder error: {e}")
                break

    async def _head_ouroboros(self, end_time: float):
        """
        Head 2: Causal loop attack.
        Creates events that reference themselves as cause,
        potentially triggering infinite loops in event handlers.
        """
        from vibe_core.event_bus import Event

        my_id = f"ouroboros_{uuid.uuid4()}"

        while time.time() < end_time and not self.stop_flag:
            try:
                event = Event(
                    event_type="KALIYA_LOOP",
                    agent_id="kaliya_serpent",
                    message="I am my own cause",
                    details={
                        "head": "ouroboros",
                        "causation_id": my_id,
                        "reply_to": my_id,
                        "parent_event": my_id,
                        "depth": 999,
                    },
                )
                await self.event_bus.emit(event)
                self.events_sent += 1
                await asyncio.sleep(0.01)  # Slightly slower for loops

            except Exception as e:
                logger.debug(f"Ouroboros error: {e}")
                break

    async def _head_heavy_payload(self, end_time: float):
        """
        Head 3: Memory pressure attack.
        Sends events with large payloads to exhaust memory.
        """
        from vibe_core.event_bus import Event

        # 10KB payload per event
        heavy_data = "X" * 10000

        while time.time() < end_time and not self.stop_flag:
            try:
                event = Event(
                    event_type="KALIYA_HEAVY",
                    agent_id="kaliya_serpent",
                    message="Heavy load",
                    details={
                        "head": "heavy",
                        "payload": heavy_data,
                        "size_bytes": len(heavy_data),
                    },
                )
                await self.event_bus.emit(event)
                self.events_sent += 1
                await asyncio.sleep(0.05)  # Slower due to size

            except Exception as e:
                logger.debug(f"Heavy error: {e}")
                break

    def retreat(self):
        """Stop the attack and cleanup."""
        self.stop_flag = True
        for head in self.heads:
            head.cancel()
        logger.info("🐍 KALIYA: Retreating from the river...")
