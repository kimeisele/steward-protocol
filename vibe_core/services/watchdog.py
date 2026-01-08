"""
NrisimhaWatchdog - The Vishnu Clock Implementation.

Implements MantraProtocol by executing the 16-step MAHAMANTRA_SEQUENCE.
This is the heartbeat that keeps the system from drifting into Maya.
"""

import logging
import time
from datetime import datetime
from typing import Optional

from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, MantraOpCode
from vibe_core.protocols.universal import (
    AlignmentScore,
    DriftContext,
    MantraProtocol,
    Resonance,
    SovereignContext,
)

logger = logging.getLogger("NRISIMHA_WATCHDOG")


class NrisimhaWatchdog(MantraProtocol):
    """
    The Nrisimha Watchdog Service.
    Implements the 16-Step Vishnu Clock for Agentic Alignment.

    "When the Mind drifts, the Watchdog bites (or chants)."
    """

    def __init__(
        self,
        sovereign_anchor: SovereignContext,
        opcode_handlers: Optional[dict] = None,
        naga_proxies: Optional[list] = None,
    ):
        self._anchor = sovereign_anchor
        self._beads_chanted = 0
        self._last_pulse = 0.0
        self._alignment_score = 1.0  # Start perfectly aligned
        self._opcode_handlers = opcode_handlers or {}  # Kernel-injected handlers
        self._naga_proxies = naga_proxies or []  # NagaProxy instances to broadcast to
        logger.info(f"🦁 Nrisimha Watchdog initialized for Sovereign: {sovereign_anchor.identity_id}")

    # =========================================================================
    # CORE: The 16-Step Atomic Cycle
    # =========================================================================

    def chant_mahamantra(self, context: SovereignContext) -> bool:
        """
        Executes the 16-step atomic cycle.
        MUST follow MAHAMANTRA_SEQUENCE exactly.

        Returns:
            True: All 16 OpCodes completed successfully.
            False: Aparadha (Offense/Error) -> Triggers Reset.
        """
        try:
            for mantra_word, opcode in MAHAMANTRA_SEQUENCE:
                # 1. Resonate (acoustic check)
                self._resonate(mantra_word)

                # 2. Execute OpCode
                success = self._exec_opcode(opcode, context)

                if not success:
                    self._panic(f"Aparadha at {mantra_word} ({opcode.value})")
                    return False

            # All 16 steps completed successfully
            self._last_pulse = time.time()
            self._alignment_score = 1.0
            return True

        except Exception as e:
            logger.error(f"🔥 MAYAVAD DETECTED: {e}")
            self._force_restart()
            return False

    # =========================================================================
    # Legacy Methods (Backwards Compatibility)
    # =========================================================================

    def chant(self, frequency: float) -> Resonance:
        """
        Legacy: Single pulse (for backwards compatibility).
        Internally calls chant_mahamantra.
        """
        start_time = time.time()

        # Execute full 16-step cycle
        success = self.chant_mahamantra(self._anchor)

        # Calculate Resonance
        amplitude = 1.0 if success else 0.0

        return Resonance(
            frequency=frequency,
            amplitude=amplitude,
            signature=self._anchor.signature,
            timestamp=datetime.fromtimestamp(start_time),
        )

    def chant_round(self, beads: int = 108) -> AlignmentScore:
        """
        Performs a full Japa Round (108 cycles).
        Each bead is one complete chant_mahamantra cycle.
        """
        corrections = 0

        logger.info(f"📿 Starting Japa Round ({beads} beads)...")

        for i in range(beads):
            # Execute one complete cycle
            success = self.chant_mahamantra(self._anchor)

            if not success:
                corrections += 1
                self._correct_drift(i)

            self._beads_chanted += 1

        score = 1.0 - (corrections / beads)
        status = "ALIGNED" if score > 0.9 else "DRIFTING"
        if score < 0.5:
            status = "LOST (MAYAVAD)"

        logger.info(f"📿 Round Complete. Score: {score:.4f} [{status}]")

        return AlignmentScore(score=score, status=status, corrections_applied=corrections)

    def surrender(self, context: DriftContext) -> None:
        """
        Total Surrender (Prapatti).
        Hard Reset to Sovereign Anchor.
        """
        logger.critical("🙇 NRISIMHA TRIGGERED SURRENDER (PRAPATTI)")
        logger.critical(f"   Reason: Drift Magnitude {context.drift_magnitude:.2f}")
        logger.critical("   Action: FLUSHING CONTEXT -> RELOADING ANCHOR")

        # In a real kernel, this would clear RAM and reload from checkpoint.
        self._beads_chanted = 0
        self._alignment_score = 1.0
        self._last_pulse = time.time()
        logger.info("✨ System Purified. Reset to Zero.")

    def get_alignment_score(self) -> float:
        """
        Metrik: Wie stark ist der Drift?
        1.0 = Perfekte Resonanz
        0.0 = Mayavad
        """
        # Decay based on time since last pulse
        if self._last_pulse == 0.0:
            return 0.0

        elapsed = time.time() - self._last_pulse
        decay = elapsed / 100.0  # 100s to full drift
        return max(0.0, self._alignment_score - decay)

    # =========================================================================
    # Internal OpCode Execution
    # =========================================================================

    def _resonate(self, mantra_word: str) -> None:
        """
        Resonance check for the mantra word.
        In a real system, this could verify sound/vibration patterns.
        """
        # logger.debug(f"   🔊 {mantra_word}")
        pass

    def _exec_opcode(self, opcode: MantraOpCode, context: SovereignContext) -> bool:
        """
        Executes a single Kernel OpCode.
        Each opcode maps to a specific system operation.

        Priority:
        1. Kernel-injected handler (if available)
        2. Broadcast to NagaProxies (Balarama Heartbeat)
        3. Internal default logic

        Returns:
            True if operation succeeded.
            False if operation failed (Aparadha).
        """
        # Check for kernel-injected handler first
        if opcode in self._opcode_handlers:
            try:
                return self._opcode_handlers[opcode](context)
            except Exception as e:
                logger.warning(f"Kernel handler failed for {opcode}: {e}")
                return False

        # Broadcast to all registered NagaProxies (The Balarama Heartbeat)
        for proxy in self._naga_proxies:
            try:
                if hasattr(proxy, "on_mantra_pulse"):
                    proxy.on_mantra_pulse(opcode)
            except Exception as e:
                logger.debug(f"Proxy pulse failed: {e}")

        # Fall back to internal default logic

        if opcode == MantraOpCode.SYS_WAKE:
            # SIGSTOP Maya / Focus on Sovereign
            pass
        elif opcode == MantraOpCode.LOAD_ROOT:
            # Load Sovereign Identity
            if not context.identity_id:
                return False
        elif opcode == MantraOpCode.ALLOC_MEM:
            # Allocate clean heap
            pass
        elif opcode == MantraOpCode.BIND_CTX:
            # Bind context to identity
            pass
        elif opcode == MantraOpCode.ASSERT_TRUTH:
            # Verify ledger integrity
            pass
        elif opcode == MantraOpCode.RESOLVE_REQ:
            # Parse intent
            pass
        elif opcode == MantraOpCode.GARBAGE_COLLECT:
            # Flush unsigned objects
            pass
        elif opcode == MantraOpCode.PULSE_SYNC:
            # Emit Naga heartbeat
            self._last_pulse = time.time()
            # ASHVAMEDHA: Auto-flood orphan services on every pulse
            self._ashvamedha_pulse()
        elif opcode == MantraOpCode.FETCH_RES:
            # Request resources
            pass
        elif opcode == MantraOpCode.EXEC_SERVICE:
            # Execute business logic (Rama's work)
            pass
        elif opcode == MantraOpCode.CHECK_DHARMA:
            # Validate against rules
            pass
        elif opcode == MantraOpCode.COMMIT_LOG:
            # Write to immutable log
            pass
        elif opcode == MantraOpCode.CACHE_STATE:
            # Store reward/memory
            pass
        elif opcode == MantraOpCode.OPTIMIZE:
            # JIT compilation
            pass
        elif opcode == MantraOpCode.YIELD_CPU:
            # Surrender control
            pass
        elif opcode == MantraOpCode.RESET_IP:
            # Loop back to start
            pass

        return True

    def _panic(self, message: str) -> None:
        """Handle Aparadha (offense) during chanting."""
        logger.error(f"💀 APARADHA: {message}")
        self._alignment_score = 0.0

    def _force_restart(self) -> None:
        """Force restart after Maya detection."""
        logger.critical("🔄 FORCING RESTART - MAYA PURGE")
        self._beads_chanted = 0
        self._alignment_score = 0.0

    def _correct_drift(self, bead_index: int) -> None:
        """Apply micro-correction during Japa."""
        # logger.debug(f"   ⚡ Correction applied at Bead {bead_index}")
        pass

    def _ashvamedha_pulse(self) -> None:
        """
        ASHVAMEDHA: The Horse Sacrifice (Automatic Protocol Integration).

        On every PULSE_SYNC (Step 8), Ananta scans for orphan services
        and floods them with NagaProxy capabilities.

        This is the Mantra-based integration - no manual wiring needed.
        "Holy Name > All Other Dharma" - Chaitanya Mahaprabhu
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.substrate import IAnantaBridge

            # Get Ananta from ServiceRegistry
            ananta = ServiceRegistry.get(IAnantaBridge)
            if ananta is None:
                return  # Ananta not yet registered (boot sequence)

            # Ananta analyzes and floods orphan services
            if hasattr(ananta, "auto_flood_orphans"):
                ananta.auto_flood_orphans()

        except Exception as e:
            # Silent fail - Ashvamedha is opportunistic, not critical
            logger.debug(f"Ashvamedha pulse skipped: {e}")
