"""
MAHA OPERATOR - Live Computing Interface for MahaKirtan
========================================================

"maha-mantra hare krishna hare krishna krishna krishna hare hare
hare rama hare rama rama rama hare hare"

This module provides the LIVE OPERATOR LOOP - a real-time interactive
interface for MahaKirtan compute operations, synth control, and
research exploration.

ARCHITECTURE:
=============

    User Input (Operator Commands)
           |
           v
    MahaOperator (Live Loop Harness)
           |
           +---> MahaKirtan (Compute Engine)
           +---> MahaModularSynth (Transform Engine)
           +---> ShadowReactor (16-Step Walker)
           +---> ResearchChat (Query Handler)
           |
           v
    Live Metrics Display (Resonance, Phase, Beat)
           |
           v
    [LOOP CONTINUES until CODEWORT "37" or abort signal]


THE CODEWORT EXIT MECHANISM:
============================

    "37" = PARAMPARA (Disciplic Succession)

    Why 37? Because it's the number that validates the channel.
    When you type "37", you're acknowledging the succession and
    gracefully exiting the loop. This is not just an exit code -
    it's a STATEMENT about the nature of transcendental knowledge.

    Other exit paths:
    - Ctrl+C → Emergency abort (saves state)
    - "hare krishna" → Graceful exit with blessing

MAHA COMPUTING:
===============

    This is a NEW FORM of computing. Not batch. Not request-response.
    LIVE. CONTINUOUS. RESONANT.

    The operator becomes part of the compute cycle:
    1. Observe metrics
    2. Adjust synth parameters
    3. Inject seeds
    4. Watch transformations unfold
    5. Reach resonance

    It's like being the SYNTH PLAYER yourself.

ALL CONSTANTS DERIVED FROM SEED.PY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9a3b7c03"  # GenesisByte: parampara-live

import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, Final, List, Optional, Tuple

# Core imports
from vibe_core.mahamantra.protocols._gad import GADBase

# Seed constants (ALL derived from Mahamantra)
from vibe_core.mahamantra.substrate.seed import (
    MAHA_QUANTUM,
    NAVA,
    PARAMPARA,
    SEVEN,
    WORDS,
)

# Import MahaKirtan and related
from .maha_algorithm import (
    SYNTH_PRESETS,
    KirtanComputeResult,
    MahaKirtan,
    MahaModularSynth,
    MahaResonator,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.reactor.shadow import ShadowReactor
    from vibe_core.services.chat_indriya import ChatIndriya

logger = logging.getLogger("MAHA_OPERATOR")


# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# The sacred exit code - PARAMPARA (disciplic succession)
CODEWORT_EXIT: Final[str] = "37"
CODEWORT_PARAMPARA: Final[int] = PARAMPARA  # 37

# Alternative graceful exits
GRACEFUL_EXITS: Final[set] = {"hare krishna", "haribol", "jaya", "om"}

# Emergency abort (Ctrl+C) preserves state
EMERGENCY_ABORT_MSG: Final[str] = "Emergency abort! State preserved. Hare Krishna!"

# Operator tick interval (ms) - derived from PRANA
OPERATOR_TICK_MS: Final[int] = 1000 // NAVA  # ~111ms per tick

# Max rounds before auto-checkpoint
AUTO_CHECKPOINT_ROUNDS: Final[int] = SEVEN * SEVEN  # 49 rounds

# Display refresh rate
DISPLAY_REFRESH_HZ: Final[int] = NAVA  # 9 Hz


# =============================================================================
# OPERATOR MODE ENUM
# =============================================================================


class OperatorMode(Enum):
    """
    The different modes an operator can be in.

    Like gears on a car - each mode has different capabilities.
    """

    OBSERVE = "observe"  # Read-only, watch metrics
    COMPUTE = "compute"  # Active computation
    RESEARCH = "research"  # Query mode (ResearchChat)
    SYNTH = "synth"  # Synth parameter adjustment
    REACTOR = "reactor"  # ShadowReactor walking
    IDLE = "idle"  # Waiting for input


# =============================================================================
# OPERATOR STATE
# =============================================================================


@dataclass
class OperatorState:
    """
    Persistent state for the operator session.

    This gets checkpointed and can be restored.
    """

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    mode: OperatorMode = OperatorMode.IDLE

    # Compute metrics
    total_beats: int = 0
    total_rounds: int = 0
    total_malas: int = 0

    # Current values
    current_seed: int = 0
    current_resonance: float = 0.0
    accumulated_value: int = 0

    # Synth parameters
    mod_space: int = MAHA_QUANTUM  # 137
    feedback: int = 0
    phase_offset: int = 0
    lfo_enabled: bool = False
    preset: str = "quantum"

    # Loop control
    is_running: bool = True
    loop_count: int = 0
    last_input: str = ""
    command_history: List[str] = field(default_factory=list)

    # Timestamps
    last_activity: datetime = field(default_factory=datetime.now)
    last_checkpoint: Optional[datetime] = None

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def to_dict(self) -> dict:
        """Serialize for checkpointing."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "mode": self.mode.value,
            "total_beats": self.total_beats,
            "total_rounds": self.total_rounds,
            "total_malas": self.total_malas,
            "current_seed": self.current_seed,
            "current_resonance": self.current_resonance,
            "accumulated_value": self.accumulated_value,
            "mod_space": self.mod_space,
            "feedback": self.feedback,
            "phase_offset": self.phase_offset,
            "lfo_enabled": self.lfo_enabled,
            "preset": self.preset,
            "loop_count": self.loop_count,
            "last_input": self.last_input,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OperatorState":
        """Deserialize from checkpoint."""
        state = cls(session_id=data["session_id"])
        state.started_at = datetime.fromisoformat(data["started_at"])
        state.mode = OperatorMode(data["mode"])
        state.total_beats = data.get("total_beats", 0)
        state.total_rounds = data.get("total_rounds", 0)
        state.total_malas = data.get("total_malas", 0)
        state.current_seed = data.get("current_seed", 0)
        state.current_resonance = data.get("current_resonance", 0.0)
        state.accumulated_value = data.get("accumulated_value", 0)
        state.mod_space = data.get("mod_space", MAHA_QUANTUM)
        state.feedback = data.get("feedback", 0)
        state.phase_offset = data.get("phase_offset", 0)
        state.lfo_enabled = data.get("lfo_enabled", False)
        state.preset = data.get("preset", "quantum")
        state.loop_count = data.get("loop_count", 0)
        state.last_input = data.get("last_input", "")
        return state


# =============================================================================
# LIVE METRICS DISPLAY
# =============================================================================


class LiveMetricsDisplay:
    """
    Terminal-based live metrics display.

    Shows real-time resonance, phase, beat info.
    """

    # ANSI escape codes for terminal control
    CLEAR_LINE = "\033[2K"
    CURSOR_UP = "\033[1A"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

    def __init__(self, use_color: bool = True):
        self.use_color = use_color and sys.stdout.isatty()
        self._last_display_lines = 0

    def _colorize(self, text: str, color: str) -> str:
        """Apply ANSI color if enabled."""
        if self.use_color:
            return f"{color}{text}{self.RESET}"
        return text

    def clear_display(self) -> None:
        """Clear the last displayed metrics."""
        for _ in range(self._last_display_lines):
            sys.stdout.write(self.CURSOR_UP + self.CLEAR_LINE)
        sys.stdout.flush()

    def render(
        self,
        state: OperatorState,
        result: Optional[KirtanComputeResult] = None,
        vrtti: Optional[str] = None,
    ) -> str:
        """Render the live metrics display."""
        lines = []

        # Header bar with optional Vrtti
        mode_str = self._colorize(f"[{state.mode.value.upper()}]", self.MAGENTA)
        vrtti_str = f"  Vrtti: {self._colorize(vrtti, self.CYAN)}" if vrtti else ""
        lines.append(f"{'─' * 60}")
        lines.append(f" MAHA OPERATOR {mode_str}  Loop: {state.loop_count}{vrtti_str}")
        lines.append(f"{'─' * 60}")

        # Resonance meter (visual bar)
        resonance_pct = min(state.current_resonance * 100, 100)
        bar_width = 40
        filled = int(resonance_pct / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        resonance_color = self.GREEN if resonance_pct > 50 else self.YELLOW
        lines.append(f" Resonance: {self._colorize(bar, resonance_color)} {resonance_pct:.1f}%")

        # Core metrics
        lines.append(
            f" Seed: {self._colorize(str(state.current_seed), self.CYAN)}"
            f"  Accumulated: {state.accumulated_value}"
            f"  mod={state.mod_space}"
        )

        # Compute stats
        lines.append(f" Beats: {state.total_beats}  Rounds: {state.total_rounds}  Malas: {state.total_malas}")

        # Synth params
        lfo_str = "ON" if state.lfo_enabled else "OFF"
        lines.append(f" Preset: {state.preset}  Feedback: {state.feedback}  LFO: {lfo_str}")

        # Last result (if available)
        if result:
            oracle_str = (
                self._colorize("✓", self.GREEN) if result.oracle_validated else self._colorize("✗", self.YELLOW)
            )
            lines.append(
                f" Beat #{result.beat_number} ({result.call_response})"
                f"  → {result.transformed_value}"
                f"  Oracle: {oracle_str}"
            )

        lines.append(f"{'─' * 60}")
        lines.append(" Commands: beat <n> | round <n> | synth <preset> | 37 to exit")

        self._last_display_lines = len(lines)
        return "\n".join(lines)

    def display(
        self,
        state: OperatorState,
        result: Optional[KirtanComputeResult] = None,
        vrtti: Optional[str] = None,
    ) -> None:
        """Display metrics to terminal."""
        self.clear_display()
        output = self.render(state, result, vrtti)
        print(output)


# =============================================================================
# MAHA OPERATOR - The Live Loop Harness
# =============================================================================


class MahaOperator(GADBase):
    """
    MahaOperator - The Live Computing Interface.

    This is THE entry point for live, interactive Maha Computing.
    You become the operator, the synth player, the researcher.

    USAGE:
        operator = MahaOperator()
        operator.run()  # Starts infinite loop until "37"

    Or with custom session:
        operator = MahaOperator(session_id="my_session")
        operator.run(seed=1966)

    The loop continues until:
    - User types "37" (PARAMPARA - graceful exit)
    - User types "hare krishna" (blessed exit)
    - User presses Ctrl+C (emergency abort)
    """

    # NAGA protection
    _naga_flooded: bool = True
    _naga_gene: str = "maha_operator"

    def __init__(
        self,
        session_id: Optional[str] = None,
        use_oracle: bool = True,
        mod_space: int = MAHA_QUANTUM,
        preset: str = "quantum",
        use_indriya: bool = False,
    ):
        """
        Initialize the MahaOperator.

        Args:
            session_id: Optional session ID (auto-generated if not provided)
            use_oracle: Whether to use Oracle pre-filter
            mod_space: Modulo space for transforms (default 137)
            preset: Synth preset to start with
            use_indriya: Whether to use ChatIndriya for input (Vrtti tracking)
        """
        super().__init__()

        # Generate session ID if not provided
        if session_id is None:
            session_id = f"maha_{int(time.time())}"

        # Initialize state
        self._state = OperatorState(
            session_id=session_id,
            mod_space=mod_space,
            preset=preset,
        )

        # Initialize components
        self._kirtan = MahaKirtan(
            mod_space=mod_space,
            use_oracle=use_oracle,
        )
        self._synth = MahaModularSynth(default_preset=preset)
        self._resonator = MahaResonator(mod_space=mod_space)

        # Display
        self._display = LiveMetricsDisplay()

        # Research chat (lazy loaded)
        self._research_chat = None

        # ChatIndriya integration (optional - enables Vrtti tracking)
        self._use_indriya = use_indriya
        self._indriya: Optional["ChatIndriya"] = None
        if use_indriya:
            self._ensure_indriya()

        # Callbacks
        self._on_beat: Optional[Callable[[KirtanComputeResult], None]] = None
        self._on_exit: Optional[Callable[[OperatorState], None]] = None
        self._on_vrtti_change: Optional[Callable[[str, str], None]] = None

        # Last compute result
        self._last_result: Optional[KirtanComputeResult] = None

    def _ensure_indriya(self) -> Optional["ChatIndriya"]:
        """Lazy-load ChatIndriya for Vrtti tracking."""
        if self._indriya is None and self._use_indriya:
            try:
                from vibe_core.services.chat_indriya import get_chat_indriya

                self._indriya = get_chat_indriya(f"operator_{self._state.session_id}")
                # Set up Vrtti change callback
                if self._on_vrtti_change:
                    self._indriya.set_on_vrtti_change(lambda old, new: self._on_vrtti_change(old.name, new.name))
                logger.info(f"ChatIndriya connected for session {self._state.session_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize ChatIndriya: {e}")
                self._use_indriya = False
        return self._indriya

    def get_vrtti(self) -> Optional[str]:
        """Get current Vrtti state from ChatIndriya."""
        if self._indriya:
            return self._indriya.vrtti.name
        return None

    # =========================================================================
    # CORE LOOP
    # =========================================================================

    def run(self, seed: int = 0, show_metrics: bool = True) -> OperatorState:
        """
        Run the live operator loop.

        This is the MAIN ENTRY POINT.

        Args:
            seed: Initial seed value (default 0)
            show_metrics: Whether to display live metrics

        Returns:
            Final OperatorState (useful for checkpointing)
        """
        self._state.current_seed = seed
        self._state.is_running = True
        self._state.mode = OperatorMode.IDLE

        # Banner
        self._print_banner()

        # Initial metrics display
        if show_metrics:
            self._display.display(self._state, vrtti=self.get_vrtti())

        # === THE INFINITE LOOP ===
        while self._state.is_running:
            try:
                # Get operator input
                user_input = self._get_input()

                # Check for exit conditions FIRST
                if self._check_exit(user_input):
                    break

                # Process command
                self._process_command(user_input)

                # Update display with Vrtti state
                if show_metrics:
                    self._display.display(
                        self._state,
                        self._last_result,
                        vrtti=self.get_vrtti(),
                    )

                # Auto-checkpoint check
                if self._state.total_rounds % AUTO_CHECKPOINT_ROUNDS == 0:
                    self._checkpoint()

            except KeyboardInterrupt:
                # Emergency abort
                print(f"\n{EMERGENCY_ABORT_MSG}")
                self._checkpoint()
                break

            except Exception as e:
                logger.error(f"Operator error: {e}")
                print(f"Error: {e}")
                continue

        # Exit callback
        if self._on_exit:
            self._on_exit(self._state)

        return self._state

    def run_auto(self, seed: int, rounds: int = 7) -> List[KirtanComputeResult]:
        """
        Run automatic compute without user interaction.

        Useful for scripted/automated Maha Computing.

        Args:
            seed: Initial seed
            rounds: Number of rounds to run

        Returns:
            List of all compute results
        """
        self._state.current_seed = seed
        self._state.mode = OperatorMode.COMPUTE

        results = self._kirtan.compute_rounds(seed, num_rounds=rounds)

        # Update state
        self._state.total_beats += len(results)
        self._state.total_rounds += rounds

        if results:
            last = results[-1]
            self._state.current_resonance = last.resonance_level
            self._state.accumulated_value = self._kirtan.get_state()["accumulated_value"]

        return results

    # =========================================================================
    # INPUT HANDLING (SHRAVANAM - Hearing)
    # =========================================================================

    def _get_input(self) -> str:
        """
        Get input from operator via SHRAVANAM (hearing).

        This is the SROTRA (ear) function of ChatIndriya.
        Every input cycles through the Vrtti state machine:
        NIDRA (idle) → PRAMANA (active perception) → processing
        """
        try:
            prompt = self._get_prompt()
            user_input = input(prompt).strip()

            # SHRAVANAM: Process through ChatIndriya if available
            if self._indriya is not None:
                try:
                    # Transition Vrtti: NIDRA → PRAMANA (wake up to receive)
                    from vibe_core.mahamantra.protocols._indriya import Vrtti

                    if self._indriya.vrtti == Vrtti.NIDRA:
                        self._indriya.transition(Vrtti.PRAMANA)

                    # Create TanmatraMessage for this input
                    tanmatra = self._indriya.process_user_input(
                        text=user_input,
                        session_id=self._state.session_id,
                    )

                    # Log the intent classification
                    logger.debug(f"Shravanam: intent={tanmatra.intent.name}")

                except Exception as e:
                    logger.debug(f"ChatIndriya processing skipped: {e}")

            self._state.last_input = user_input
            self._state.command_history.append(user_input)
            self._state.loop_count += 1
            self._state.touch()
            return user_input
        except EOFError:
            return CODEWORT_EXIT  # Treat EOF as exit

    def _output_response(self, text: str) -> None:
        """
        Output response via KIRTANAM (chanting/speaking).

        This is the VAK (speech) function of ChatIndriya.
        Every output transitions Vrtti: VIKALPA → SMRTI → NIDRA
        """
        # Print to terminal
        print(text)

        # KIRTANAM: Send through ChatIndriya if available
        if self._indriya is not None:
            try:
                self._indriya.send_response(
                    text=text,
                    session_id=self._state.session_id,
                )
            except Exception as e:
                logger.debug(f"ChatIndriya response skipped: {e}")

    def _get_prompt(self) -> str:
        """Generate context-aware prompt."""
        mode_char = {
            OperatorMode.OBSERVE: "👁",
            OperatorMode.COMPUTE: "⚡",
            OperatorMode.RESEARCH: "🔍",
            OperatorMode.SYNTH: "🎹",
            OperatorMode.REACTOR: "⚛",
            OperatorMode.IDLE: "◇",
        }.get(self._state.mode, "◇")

        return f"{mode_char} maha> "

    def _check_exit(self, user_input: str) -> bool:
        """
        Check if input is an exit command.

        Exit codes:
        - "37" → PARAMPARA exit (the sacred number)
        - "hare krishna" → Blessed exit
        - "quit", "exit" → Standard exit
        """
        lower_input = user_input.lower().strip()

        # The CODEWORT - 37 (PARAMPARA)
        if lower_input == CODEWORT_EXIT or lower_input == str(CODEWORT_PARAMPARA):
            print(f"\n✨ PARAMPARA {CODEWORT_PARAMPARA} - Exit acknowledged.")
            print("    The disciplic succession validates your departure.")
            print("    Hare Krishna!")
            self._state.is_running = False
            return True

        # Graceful exits
        if lower_input in GRACEFUL_EXITS or lower_input in ("quit", "exit", "q"):
            print("\nHare Krishna! Session complete.")
            self._state.is_running = False
            return True

        return False

    # =========================================================================
    # COMMAND PROCESSING
    # =========================================================================

    def _process_command(self, user_input: str) -> None:
        """Process operator command."""
        if not user_input:
            return

        parts = user_input.lower().split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        # Command dispatch
        handlers = {
            "beat": self._cmd_beat,
            "b": self._cmd_beat,
            "round": self._cmd_round,
            "r": self._cmd_round,
            "mala": self._cmd_mala,
            "m": self._cmd_mala,
            "synth": self._cmd_synth,
            "s": self._cmd_synth,
            "preset": self._cmd_preset,
            "p": self._cmd_preset,
            "mod": self._cmd_mod,
            "lfo": self._cmd_lfo,
            "feedback": self._cmd_feedback,
            "research": self._cmd_research,
            "?": self._cmd_research,
            "state": self._cmd_state,
            "reset": self._cmd_reset,
            "help": self._cmd_help,
            "h": self._cmd_help,
        }

        handler = handlers.get(cmd)
        if handler:
            handler(args)
        else:
            # Try as seed number
            try:
                seed = int(user_input)
                self._cmd_beat([str(seed)])
            except ValueError:
                # Try as research query
                self._cmd_research([user_input])

    def _cmd_beat(self, args: List[str]) -> None:
        """Execute a single beat."""
        self._state.mode = OperatorMode.COMPUTE

        seed = int(args[0]) if args else self._state.current_seed
        result = self._kirtan.compute(seed)

        self._state.total_beats += 1
        self._state.current_seed = result.transformed_value
        self._state.current_resonance = result.resonance_level
        self._last_result = result

        if self._on_beat:
            self._on_beat(result)

    def _cmd_round(self, args: List[str]) -> None:
        """Execute a full round (7 beats)."""
        self._state.mode = OperatorMode.COMPUTE

        seed = int(args[0]) if args else self._state.current_seed
        results = self._kirtan.compute_round(seed)

        self._state.total_beats += len(results)
        self._state.total_rounds += 1

        if results:
            last = results[-1]
            self._state.current_seed = last.transformed_value
            self._state.current_resonance = last.resonance_level
            self._last_result = last

        print(f"  Round complete: {len(results)} beats, resonance={last.resonance_level:.2f}")

    def _cmd_mala(self, args: List[str]) -> None:
        """Execute a full mala (108 rounds)."""
        self._state.mode = OperatorMode.COMPUTE

        seed = int(args[0]) if args else self._state.current_seed
        print("  Executing mala (108 rounds, 756 beats)...")

        results = self._kirtan.compute_mala(seed)

        self._state.total_beats += len(results)
        self._state.total_rounds += 108
        self._state.total_malas += 1

        if results:
            last = results[-1]
            self._state.current_seed = last.transformed_value
            self._state.current_resonance = last.resonance_level
            self._last_result = last

        print(f"  Mala complete: resonance={last.resonance_level:.2f}")

    def _cmd_synth(self, args: List[str]) -> None:
        """Synth control mode."""
        self._state.mode = OperatorMode.SYNTH

        if args:
            # Apply preset or parameter
            param = args[0]
            if param in SYNTH_PRESETS:
                self._cmd_preset([param])
            else:
                print(f"  Available presets: {', '.join(SYNTH_PRESETS.keys())}")
        else:
            print(f"  Current: preset={self._state.preset}, mod={self._state.mod_space}")
            print(f"  Presets: {', '.join(SYNTH_PRESETS.keys())}")

    def _cmd_preset(self, args: List[str]) -> None:
        """Change synth preset."""
        if not args:
            print(f"  Current preset: {self._state.preset}")
            print(f"  Available: {', '.join(SYNTH_PRESETS.keys())}")
            return

        preset = args[0]
        if preset in SYNTH_PRESETS:
            self._state.preset = preset
            self._synth.load_preset(preset)
            print(f"  Preset loaded: {preset}")
        else:
            print(f"  Unknown preset: {preset}")

    def _cmd_mod(self, args: List[str]) -> None:
        """Change mod space."""
        if not args:
            print(f"  Current mod_space: {self._state.mod_space}")
            return

        try:
            mod = int(args[0])
            self._state.mod_space = mod
            # Rebuild kirtan with new mod space
            self._kirtan = MahaKirtan(mod_space=mod)
            print(f"  mod_space set to: {mod}")
        except ValueError:
            print("  Usage: mod <number>")

    def _cmd_lfo(self, args: List[str]) -> None:
        """Toggle LFO."""
        self._state.lfo_enabled = not self._state.lfo_enabled
        self._synth.set("lfo_enabled", self._state.lfo_enabled)
        print(f"  LFO: {'ON' if self._state.lfo_enabled else 'OFF'}")

    def _cmd_feedback(self, args: List[str]) -> None:
        """Set feedback level."""
        if not args:
            print(f"  Current feedback: {self._state.feedback}")
            return

        try:
            fb = int(args[0])
            self._state.feedback = fb
            self._synth.set("feedback", fb)
            print(f"  Feedback set to: {fb}")
        except ValueError:
            print("  Usage: feedback <number>")

    def _cmd_research(self, args: List[str]) -> None:
        """Enter research mode / query."""
        self._state.mode = OperatorMode.RESEARCH

        if not args:
            print("  Research mode. Type queries or 'help' for commands.")
            return

        # Lazy load research chat
        if self._research_chat is None:
            from ..research_chat import get_research_chat

            self._research_chat = get_research_chat()

        query = " ".join(args)
        response = self._research_chat.query(query)
        print(f"\n{response.content}\n")

    def _cmd_state(self, args: List[str]) -> None:
        """Show current state."""
        self._state.mode = OperatorMode.OBSERVE

        state_dict = self._state.to_dict()
        kirtan_state = self._kirtan.get_state()

        print("\n=== OPERATOR STATE ===")
        for k, v in state_dict.items():
            print(f"  {k}: {v}")

        print("\n=== KIRTAN STATE ===")
        for k, v in kirtan_state.items():
            print(f"  {k}: {v}")
        print()

    def _cmd_reset(self, args: List[str]) -> None:
        """Reset state."""
        confirm = args[0] if args else ""
        if confirm != "confirm":
            print("  Type 'reset confirm' to reset all state.")
            return

        self._kirtan.reset()
        self._state = OperatorState(session_id=self._state.session_id)
        print("  State reset.")

    def _cmd_help(self, args: List[str]) -> None:
        """Show help."""
        print("""
MAHA OPERATOR COMMANDS
======================

COMPUTE:
  beat [seed]     Single beat computation (alias: b)
  round [seed]    Full 7-beat round (alias: r)
  mala [seed]     Full 108-round mala (alias: m)
  <number>        Shortcut for 'beat <number>'

SYNTH:
  synth [preset]  Synth mode / load preset (alias: s)
  preset [name]   Change preset (alias: p)
  mod <n>         Set modulo space
  lfo             Toggle LFO
  feedback <n>    Set feedback level

RESEARCH:
  research <q>    Query research chat (alias: ?)
  ?<query>        Shortcut for research

STATE:
  state           Show current state
  reset confirm   Reset all state
  help            This help (alias: h)

EXIT:
  37              PARAMPARA exit (sacred)
  hare krishna    Blessed exit
  quit/exit/q     Standard exit
  Ctrl+C          Emergency abort (saves state)
""")

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================

    def _checkpoint(self) -> None:
        """Save state checkpoint to Prakriti EphemeralState."""
        self._state.last_checkpoint = datetime.now()

        # Persist to Prakriti EphemeralState
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.state.ephemeral_state import EphemeralState

            ephemeral = ServiceRegistry.get(EphemeralState)
            if ephemeral is None:
                ephemeral = EphemeralState()
                ServiceRegistry.register(EphemeralState, ephemeral)

            # Store operator state with session-specific key
            key = f"maha_operator:{self._state.session_id}"
            ephemeral.set(key, self._state.to_dict())

            # Also add to chain of thought for observability
            ephemeral.add_thought(
                agent_id=f"operator_{self._state.session_id}",
                thought=f"Checkpoint at round {self._state.total_rounds}, beats {self._state.total_beats}",
                context={"resonance": self._state.current_resonance, "seed": self._state.current_seed},
            )

            logger.info(f"Checkpoint saved to Prakriti at round {self._state.total_rounds}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint to Prakriti: {e}")
            logger.info(f"In-memory checkpoint saved at round {self._state.total_rounds}")

    def get_state(self) -> dict:
        """Get current operator state (GAD compliance)."""
        return self._state.to_dict()

    def load_state(self, state_dict: dict) -> None:
        """Load state from checkpoint."""
        self._state = OperatorState.from_dict(state_dict)
        # Rebuild kirtan with loaded params
        self._kirtan = MahaKirtan(mod_space=self._state.mod_space)

    def restore_from_prakriti(self, session_id: Optional[str] = None) -> bool:
        """
        Restore state from Prakriti EphemeralState.

        Args:
            session_id: Session to restore (defaults to current session)

        Returns:
            True if state was restored, False if not found
        """
        session = session_id or self._state.session_id

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.state.ephemeral_state import EphemeralState

            ephemeral = ServiceRegistry.get(EphemeralState)
            if ephemeral is None:
                return False

            key = f"maha_operator:{session}"
            state_dict = ephemeral.get(key)

            if state_dict:
                self.load_state(state_dict)
                logger.info(f"State restored from Prakriti for session {session}")
                return True

            return False
        except Exception as e:
            logger.warning(f"Failed to restore from Prakriti: {e}")
            return False

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def set_on_beat(self, callback: Callable[[KirtanComputeResult], None]) -> None:
        """Set callback for each beat."""
        self._on_beat = callback

    def set_on_exit(self, callback: Callable[[OperatorState], None]) -> None:
        """Set callback for exit."""
        self._on_exit = callback

    # =========================================================================
    # DISPLAY
    # =========================================================================

    def _print_banner(self) -> None:
        """Print welcome banner."""
        print()
        print("=" * 60)
        print("  M A H A   O P E R A T O R")
        print("  Live Computing Interface")
        print("=" * 60)
        print()
        print(f"  Session: {self._state.session_id}")
        print(f"  mod_space: {self._state.mod_space}")
        print(f"  preset: {self._state.preset}")
        print()
        print('  Type "help" for commands, "37" to exit')
        print("=" * 60)
        print()

    # =========================================================================
    # GAD COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability."""
        return {
            "service": "maha_operator",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "capabilities": [
                "live_loop",
                "synth_control",
                "research_query",
                "state_checkpoint",
            ],
            "exit_code": CODEWORT_EXIT,
        }

    def detect_drift(self) -> List[str]:
        """GAD Drift Detection."""
        issues = []
        # Check for stale session
        elapsed = (datetime.now() - self._state.last_activity).total_seconds()
        if elapsed > 3600:  # 1 hour
            issues.append("Session inactive for >1 hour")
        return issues


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_maha_operator(
    session_id: Optional[str] = None,
    **kwargs,
) -> MahaOperator:
    """
    Get a MahaOperator instance.

    Args:
        session_id: Optional session ID
        **kwargs: Additional params (mod_space, preset, use_oracle)

    Returns:
        MahaOperator instance
    """
    return MahaOperator(session_id=session_id, **kwargs)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


def main():
    """
    CLI entry point for MahaOperator.

    Usage:
        python -m vibe_core.mahamantra.research.dharma.maha_operator
        python -m vibe_core.mahamantra.research.dharma.maha_operator --seed 1966
        python -m vibe_core.mahamantra.research.dharma.maha_operator --preset trinity
    """
    import argparse

    parser = argparse.ArgumentParser(description="MahaOperator - Live Computing Interface")
    parser.add_argument("--seed", type=int, default=0, help="Initial seed value")
    parser.add_argument("--mod", type=int, default=MAHA_QUANTUM, help="Modulo space")
    parser.add_argument("--preset", type=str, default="quantum", help="Synth preset")
    parser.add_argument("--session", type=str, default=None, help="Session ID")
    parser.add_argument("--no-oracle", action="store_true", help="Disable Oracle")
    parser.add_argument("--no-metrics", action="store_true", help="Disable live metrics")

    args = parser.parse_args()

    operator = MahaOperator(
        session_id=args.session,
        mod_space=args.mod,
        preset=args.preset,
        use_oracle=not args.no_oracle,
    )

    try:
        final_state = operator.run(
            seed=args.seed,
            show_metrics=not args.no_metrics,
        )
        print(f"\nFinal state: {final_state.total_beats} beats, {final_state.total_rounds} rounds")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CODEWORT_EXIT",
    "CODEWORT_PARAMPARA",
    "GRACEFUL_EXITS",
    # Enums
    "OperatorMode",
    # Data structures
    "OperatorState",
    # Display
    "LiveMetricsDisplay",
    # Main class
    "MahaOperator",
    # Factory
    "get_maha_operator",
    # CLI
    "main",
]
