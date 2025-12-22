"""
MANAS Biorhythm Processor - The Pulse of Consciousness.

OPUS-176: Extracted from cognitive_kernel.py (2570 → ~2300 lines)

The Biorhythm is NOT polling. It's a continuous consciousness spectrum:
- Tamas (0.0-0.2): Hibernate - heartbeat only
- Rajas (0.2-0.5): React - quick perception, respond to triggers
- Sattva (0.5-0.8): Reflect - organize buffer, reinforce synapses
- Turiya (0.8-1.0): Deep think - full OODA loop

This module computes consciousness level from three inputs:
- Synaptic urgency (0.5 weight) - learned patterns firing
- Prakriti health (0.3 weight) - system guna state
- Kala rhythm (0.2 weight) - cosmic time (optional)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .cognitive_kernel import CognitiveKernel

logger = logging.getLogger("MANAS.Biorhythm")


@dataclass
class BiorhythmState:
    """Current state of the biorhythm processor."""

    tick_count: int = 0
    ticks_since_turiya: int = 0
    consciousness_level: float = 0.5
    consciousness_state: str = "rajas"
    last_tick_time: Optional[datetime] = None

    # Cached input values (recomputed periodically)
    cached_urgency: float = 0.0
    cached_health: float = 0.5
    cached_rhythm: float = 0.5


class BiorhythmProcessor:
    """
    Processes MANAS consciousness ticks.

    Extracted from CognitiveKernel to reduce complexity.
    Uses delegate pattern - receives kernel reference for state access.
    """

    def __init__(self, kernel: "CognitiveKernel"):
        """
        Initialize with kernel reference.

        Args:
            kernel: The CognitiveKernel instance to delegate to
        """
        self._kernel = kernel
        self._state = BiorhythmState()

    @property
    def consciousness_level(self) -> float:
        """Current consciousness level (0.0-1.0)."""
        return self._state.consciousness_level

    @property
    def consciousness_state(self) -> str:
        """Current consciousness state name."""
        return self._state.consciousness_state

    @property
    def tick_count(self) -> int:
        """Number of ticks processed."""
        return self._state.tick_count

    def tick(self) -> Dict[str, Any]:
        """
        MANAS Biorhythm tick - runs every KERNEL_TICK (~3s).

        OPUS-174: NOT binary. A SPECTRUM of consciousness.

        Returns:
            Dict with state, consciousness_level, and should_think
        """
        now = datetime.utcnow()
        self._state.tick_count += 1
        self._state.last_tick_time = now

        # Compute consciousness level
        level = self._compute_consciousness_level()
        self._state.consciousness_level = level

        # Dispatch to appropriate behavior based on level
        if level >= 0.8:
            result = self._turiya_tick()
        elif level >= 0.5:
            result = self._sattva_tick()
        elif level >= 0.2:
            result = self._rajas_tick()
        else:
            result = self._tamas_tick()

        # Update awareness (in-memory, for transparency)
        pending_count = len(self._kernel._buffer.get_pending())
        awareness = {
            "tick": self._state.tick_count,
            "consciousness_level": round(level, 3),
            "state": result.get("state", "unknown"),
            "inputs": {
                "synaptic_urgency": round(self._state.cached_urgency, 3),
                "prakriti_health": round(self._state.cached_health, 3),
                "kala_rhythm": round(self._state.cached_rhythm, 3),
            },
            "last_tick": now.isoformat(),
            "pending_intents": pending_count,
            "ticks_since_turiya": self._state.ticks_since_turiya,
            "last_thought": (self._kernel._last_thought_time.isoformat() if self._kernel._last_thought_time else None),
        }
        self._kernel._awareness = awareness

        # Periodic persistence (every 20 ticks = ~60s)
        if self._state.tick_count % 20 == 0:
            self._persist_awareness()

        return result

    def _compute_consciousness_level(self) -> float:
        """
        Compute consciousness level (0.0 - 1.0) from multiple signals.

        Inputs:
        - Synaptic urgency (0.5 weight) - learned patterns firing
        - Prakriti health (0.3 weight) - system guna state
        - Kala rhythm (0.2 weight) - cosmic time (optional)
        """
        tick = self._state.tick_count

        # 1. Synaptic urgency (REQUIRED - 0.5 weight)
        if tick % 10 == 0:
            self._state.cached_urgency = self._kernel._get_synaptic_urgency()

        # 2. Prakriti health (REQUIRED - 0.3 weight)
        if tick % 10 == 0:
            try:
                prakriti = self._kernel._prakriti_sense
                if prakriti:
                    guna = prakriti.perceive_state()
                    self._state.cached_health = guna.health_ratio if guna else 0.5
                else:
                    self._state.cached_health = 0.5
            except Exception:
                self._state.cached_health = 0.5

        # 3. Kala rhythm (OPTIONAL - 0.2 weight)
        if tick % 20 == 0:
            try:
                kernel_ref = self._kernel._kernel
                if kernel_ref:
                    kala = kernel_ref.get_service("kala")
                    if kala and hasattr(kala, "get_rhythm_intensity"):
                        rhythms = kala.get_rhythm_intensity()
                        self._state.cached_rhythm = rhythms.get("combined", 0.5)
                    else:
                        self._state.cached_rhythm = 0.5
                else:
                    self._state.cached_rhythm = 0.5
            except Exception:
                self._state.cached_rhythm = 0.5

        # Combine with weights
        level = (
            (self._state.cached_urgency * 0.5) + (self._state.cached_health * 0.3) + (self._state.cached_rhythm * 0.2)
        )
        return min(1.0, max(0.0, level))

    def _tamas_tick(self) -> Dict[str, Any]:
        """Tamas state (0.0-0.2): Hibernate. Minimal activity."""
        self._state.consciousness_state = "tamas"
        self._state.ticks_since_turiya += 1

        return {
            "state": "tamas",
            "action": "heartbeat",
            "should_think": False,
            "consciousness_level": self._state.consciousness_level,
        }

    def _rajas_tick(self) -> Dict[str, Any]:
        """Rajas state (0.2-0.5): React. Quick perception."""
        self._state.consciousness_state = "rajas"
        self._state.ticks_since_turiya += 1

        urgency = self._state.cached_urgency
        pending = len(self._kernel._buffer.get_pending())

        # If urgency spikes, consider escalating
        escalate = urgency >= 0.8 or pending >= 5

        return {
            "state": "rajas",
            "action": "escalate" if escalate else "monitor",
            "should_think": escalate,
            "consciousness_level": self._state.consciousness_level,
            "pending": pending,
        }

    def _sattva_tick(self) -> Dict[str, Any]:
        """Sattva state (0.5-0.8): Reflect. Organize buffer."""
        self._state.consciousness_state = "sattva"
        self._state.ticks_since_turiya += 1

        tick = self._state.tick_count

        # Periodic buffer organization (every 5 ticks in Sattva)
        if tick % 5 == 0:
            self._organize_buffer_light()

        # Periodic synapse reinforcement (every 10 ticks in Sattva)
        if tick % 10 == 0:
            self._reinforce_recent_patterns()

        return {
            "state": "sattva",
            "action": "reflect",
            "should_think": False,
            "consciousness_level": self._state.consciousness_level,
        }

    def _turiya_tick(self) -> Dict[str, Any]:
        """Turiya state (0.8-1.0): Deep Think. Full OODA loop."""
        self._state.consciousness_state = "turiya"
        self._state.ticks_since_turiya = 0  # Reset counter

        return {
            "state": "turiya",
            "action": "deep_think",
            "should_think": True,
            "consciousness_level": self._state.consciousness_level,
        }

    def _organize_buffer_light(self) -> None:
        """Light buffer organization during Sattva state."""
        try:
            buffer = self._kernel._buffer
            expired = [
                e for e in buffer.get_all() if e.status == "pending" and self._kernel._is_intent_expired(e.intent)
            ]
            for entry in expired[:3]:  # Max 3 per tick to stay light
                entry.status = "expired"
            if expired:
                buffer.save()
        except Exception as e:
            logger.debug(f"Light buffer organization failed: {e}")

    def _reinforce_recent_patterns(self) -> None:
        """Reinforce recent successful patterns during Sattva state."""
        try:
            buffer = self._kernel._buffer
            recent = [
                e
                for e in buffer.get_all()
                if e.status == "executed" and e.execution_result and e.execution_result.get("success")
            ]
            # Light reinforcement - VivekaAction handles this at execution time
            _ = recent[:2]  # Just acknowledge we checked
        except Exception as e:
            logger.debug(f"Pattern reinforcement failed: {e}")

    def _persist_awareness(self) -> None:
        """Persist awareness state for transparency."""
        try:
            from vibe_core.state.state_service import get_state_service

            state_service = get_state_service(self._kernel._workspace, plugin_id="opus_assistant")
            awareness = getattr(self._kernel, "_awareness", {})
            result = state_service.save("manas_awareness.json", awareness, create_backup=False)

            if result.success:
                logger.debug(f"🧠 MANAS awareness persisted: {awareness.get('state', 'unknown')}")
            else:
                logger.warning(f"Failed to persist awareness: {result.error}")
        except Exception as e:
            logger.warning(f"Failed to persist awareness: {e}")

    def get_awareness(self) -> Dict[str, Any]:
        """Get current awareness state (for dashboard/templates)."""
        return getattr(self._kernel, "_awareness", {})
