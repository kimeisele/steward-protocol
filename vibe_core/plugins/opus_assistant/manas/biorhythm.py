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

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import CognitiveKernelProtocol

if TYPE_CHECKING:
    pass

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
    # OPUS-211: Default cached_health to 0.7 (development-friendly)
    # MANAS should start in a healthy state, not penalized for missing data
    cached_urgency: float = 0.0
    cached_health: float = 0.7  # Changed from 0.5 - assume healthy until proven otherwise
    cached_rhythm: float = 0.5


class BiorhythmProcessor:
    """
    Processes MANAS consciousness ticks.

    Extracted from CognitiveKernel to reduce complexity.
    Uses delegate pattern - receives kernel reference for state access.

    OPUS-211 SENIOR FIX: Uses ServiceRegistry to break circular import.
    """

    def __init__(self, kernel: Optional[CognitiveKernelProtocol] = None):
        """
        Initialize with kernel reference.

        Args:
            kernel: Optional CognitiveKernel instance to delegate to.
                    If None, uses ServiceRegistry to find it.
        """
        self._kernel = kernel
        self._state = BiorhythmState()
        self._in_tick = False

    @property
    def kernel(self) -> Optional[CognitiveKernelProtocol]:
        """Lazy-discover kernel via DI if not provided."""
        if self._kernel is None:
            self._kernel = ServiceRegistry.get(CognitiveKernelProtocol)
        return self._kernel

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
        if self._in_tick:
            return {"state": "locked", "consciousness_level": 0.0, "should_think": False}

        self._in_tick = True
        try:
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
            pending_count = len(self.kernel._buffer.get_pending())
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
                "last_thought": (
                    self.kernel._last_thought_time.isoformat() if self.kernel._last_thought_time else None
                ),
            }
            self.kernel._awareness = awareness

            # Periodic persistence (every 20 ticks = ~60s)
            if self._state.tick_count % 20 == 0:
                self._persist_awareness()

            return result
        finally:
            self._in_tick = False

    def _compute_consciousness_level(self) -> float:
        """
        Compute consciousness level (0.0 - 1.0) from multiple signals.

        Inputs:
        - Synaptic urgency
        - Prakriti health
        - Kala rhythm

        Uses weights from config/manas.yaml (biorhythm.weights).
        """
        tick = self._state.tick_count

        # Get weights from config (or defaults)
        # Assuming CognitiveKernel exposes full config or biorhythm section
        weights = {"synaptic_urgency": 0.5, "prakriti_health": 0.3, "kala_rhythm": 0.2}
        try:
            full_config = getattr(self.kernel, "_full_config", {})
            if full_config and "biorhythm" in full_config:
                weights = full_config["biorhythm"].get("weights", weights)
        except Exception:
            pass

        # 1. Synaptic urgency
        if tick % 10 == 0:
            self._state.cached_urgency = self.kernel._get_synaptic_urgency()

        # 2. Prakriti health
        # OPUS-211: Improved error handling with logging
        if tick % 10 == 0:
            try:
                prakriti = self.kernel._prakriti_sense
                if prakriti:
                    guna = prakriti.perceive_state()
                    if guna:
                        self._state.cached_health = guna.health_ratio
                        logger.debug(
                            f"🫀 Biorhythm: prakriti_health={guna.health_ratio:.2f} "
                            f"(S:{guna.sattva_count} R:{guna.rajas_count} T:{guna.tamas_count})"
                        )
                    else:
                        # No guna returned - use development-friendly default
                        self._state.cached_health = 0.7
                        logger.warning("🫀 Biorhythm: prakriti.perceive_state() returned None, using 0.7")
                else:
                    # No prakriti sense - development mode
                    self._state.cached_health = 0.7
                    logger.debug("🫀 Biorhythm: No prakriti_sense, using default 0.7")
            except Exception as e:
                # Log the actual error so we can debug
                self._state.cached_health = 0.7
                logger.warning(f"🫀 Biorhythm: prakriti_health failed: {e}, using 0.7")

        # 3. Kala rhythm
        if tick % 20 == 0:
            try:
                kernel_ref = self.kernel._kernel
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

        # OPUS-211 ARCHITECTURE FIX by Opus 4.5:
        #
        # Philosophy: MANAS serves by being RESILIENT, not by collapsing under
        # the mistakes of others. Prabhupada Patch says "serve, not suffer."
        #
        # OLD (fragile): level = urgency*0.5 + health*0.3 + rhythm*0.2
        #   Problem: health=0 → MANAS dies. Too dependent on external state.
        #
        # NEW (resilient):
        #   base = 0.4 (MANAS starts healthy, assumes good faith)
        #   + urgency boost when there's work
        #   + rhythm boost from Kala
        #   - health penalty ONLY if truly sick (Tamas dominant)
        #
        # Key: Rajas (development) should BOOST, not lower consciousness.
        # Development IS work. Work IS good. MANAS wakes up for activity.

        base = 0.4  # MANAS is healthy by default ("innocent until proven guilty")

        # Urgency BOOSTS consciousness (work to do = wake up)
        urgency_boost = self._state.cached_urgency * weights.get("synaptic_urgency", 0.3)

        # Rhythm from Kala (cosmic time)
        rhythm_boost = self._state.cached_rhythm * weights.get("kala_rhythm", 0.2)

        # Health penalty ONLY when truly sick (health < 0.3 = Tamas dominant)
        health_penalty = 0.0
        if self._state.cached_health < 0.3:
            health_penalty = (0.3 - self._state.cached_health) * 0.5  # Max -0.15

        level = base + urgency_boost + rhythm_boost - health_penalty

        logger.debug(
            f"🫀 Consciousness: base=0.4 + urgency={urgency_boost:.2f} "
            f"+ rhythm={rhythm_boost:.2f} - health_penalty={health_penalty:.2f} = {level:.2f}"
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
        pending = len(self.kernel._buffer.get_pending())

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
            buffer = self.kernel._buffer
            expired = [
                e for e in buffer.get_all() if e.status == "pending" and self.kernel._is_intent_expired(e.intent)
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
            buffer = self.kernel._buffer
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

            state_service = get_state_service(self.kernel._workspace, plugin_id="opus_assistant")
            awareness = getattr(self.kernel, "_awareness", {})
            result = state_service.save("manas_awareness.json", awareness, create_backup=False)

            if result.success:
                logger.debug(f"🧠 MANAS awareness persisted: {awareness.get('state', 'unknown')}")
            else:
                logger.warning(f"Failed to persist awareness: {result.error}")
        except Exception as e:
            logger.warning(f"Failed to persist awareness: {e}")

    def get_awareness(self) -> Dict[str, Any]:
        """Get current awareness state (for dashboard/templates)."""
        return getattr(self.kernel, "_awareness", {})
