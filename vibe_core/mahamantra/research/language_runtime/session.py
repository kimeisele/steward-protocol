"""Research session that composes language generation with Venu runtime ticks."""

from __future__ import annotations

from typing import Callable, Optional, Protocol, Tuple

from .contracts import InputSignal, RuntimeEnvelope
from .incremental import FrameHistory, IncrementalBuffer, TickInputFrame
from .venu_bridge import VenuTickBridge


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

    This is intentionally thin: orchestration stays in VenuService/VenuOrchestrator.
    """

    __slots__ = ("_generate", "_bridge", "_buffer", "_history")

    def __init__(self, generate: Callable[[str], EngineLikeResult], bridge: Optional[VenuTickBridge] = None) -> None:
        self._generate = generate
        self._bridge = bridge or VenuTickBridge()
        self._buffer = IncrementalBuffer()
        self._history = FrameHistory()

    @property
    def bridge(self) -> VenuTickBridge:
        return self._bridge

    @property
    def buffer(self) -> IncrementalBuffer:
        return self._buffer

    @property
    def history(self) -> FrameHistory:
        return self._history

    def attach(self) -> None:
        self._bridge.attach()

    def detach(self) -> None:
        self._bridge.detach()

    def keystroke(self, char: str) -> TickInputFrame:
        """Feed a single character and return the current frame snapshot."""
        self._buffer.keystroke(char)
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
