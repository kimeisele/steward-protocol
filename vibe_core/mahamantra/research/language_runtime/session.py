"""Research session that composes language generation with Venu runtime ticks."""

from __future__ import annotations

from typing import Callable, Optional, Protocol, Tuple

from .contracts import InputSignal, RuntimeEnvelope
from .incremental import FrameHistory, IncrementalBuffer, TickInputFrame
from .venu_bridge import VenuTickBridge
from .antaranga_bridge import ImpactResult, impact_keystroke, modulate_with_diw


class EngineLikeResult(Protocol):
    """Minimum shape needed from language generation output."""

    seed: int
    attractor: int
    output: str
    derivation: str
    stress_pattern: Tuple[int, ...]
    sequencer_steps: Tuple[int, ...]


class LanguageRuntimeSession:
    """Venu-aware session wrapper for research experiments.

    Now owns an AntarangaRegistry: each keystroke fires a collide() event
    into the 16KB contiguous RAM. VenuOrchestrator ticks modulate the
    standing wave via apply_diw().
    """

    __slots__ = ("_generate", "_bridge", "_buffer", "_history", "_antaranga", "_venu", "_last_impact")

    def __init__(self, generate: Callable[[str], EngineLikeResult], bridge: Optional[VenuTickBridge] = None) -> None:
        from vibe_core.mahamantra.substrate.antaranga import AntarangaRegistry
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

        self._generate = generate
        self._bridge = bridge or VenuTickBridge()
        self._buffer = IncrementalBuffer()
        self._history = FrameHistory()
        self._antaranga = AntarangaRegistry()
        self._venu = VenuOrchestrator()
        self._last_impact: Optional[ImpactResult] = None

    @property
    def bridge(self) -> VenuTickBridge:
        return self._bridge

    @property
    def buffer(self) -> IncrementalBuffer:
        return self._buffer

    @property
    def history(self) -> FrameHistory:
        return self._history

    @property
    def antaranga(self):
        """Direct access to the 16KB Antaranga chamber."""
        return self._antaranga

    @property
    def last_impact(self) -> Optional[ImpactResult]:
        """Result of the most recent keystroke impact."""
        return self._last_impact

    def attach(self) -> None:
        self._bridge.attach()

    def detach(self) -> None:
        self._bridge.detach()

    def keystroke(self, char: str) -> TickInputFrame:
        """Feed a single character, fire it into Antaranga, and return frame.

        Pipeline:
            1. char → IncrementalBuffer (text accumulation)
            2. char → antaranga_bridge.impact_keystroke() (physical impact)
            3. VenuOrchestrator.step() → apply_diw() (standing wave modulation)
        """
        self._buffer.keystroke(char)

        # Fire keystroke into the Antaranga chamber
        self._last_impact = impact_keystroke(self._antaranga, char)

        # Venu tick modulates the standing wave
        diw = self._venu.step()
        modulate_with_diw(self._antaranga, diw)

        frame = self._buffer.snapshot(self._bridge.latest())
        self._history.push(frame)
        return frame

    def backspace(self) -> TickInputFrame:
        """Remove last character and return updated frame."""
        self._buffer.backspace()
        frame = self._buffer.snapshot(self._bridge.latest())
        self._history.push(frame)
        return frame

    def generate_live(self, source: str = "live") -> RuntimeEnvelope:
        """Run engine on current buffer contents and return envelope."""
        text = self._buffer.text
        if not text:
            return RuntimeEnvelope(
                input_signal=InputSignal(text="", source=source),
                tick=self._bridge.latest(),
                rhythm_signature="-",
                seed=0,
                attractor=0,
                output="",
            )
        return self.process_text(text, source=source)

    def process_text(self, text: str, source: str = "text") -> RuntimeEnvelope:
        result = self._generate(text)
        signature = "".join(str(s) for s in result.stress_pattern) if result.stress_pattern else "-"
        return RuntimeEnvelope(
            input_signal=InputSignal(text=text, source=source),
            tick=self._bridge.latest(),
            rhythm_signature=signature,
            seed=result.seed,
            attractor=result.attractor,
            output=result.output,
            derivation=getattr(result, "derivation", ""),
            stress_pattern=result.stress_pattern,
            sequencer_steps=getattr(result, "sequencer_steps", ()),
        )
