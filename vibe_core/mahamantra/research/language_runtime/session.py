"""Research session that composes language generation with Venu runtime ticks."""

from __future__ import annotations

from typing import Callable, Optional, Protocol, Tuple

from .contracts import InputSignal, RuntimeEnvelope
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

    __slots__ = ("_generate", "_bridge")

    def __init__(self, generate: Callable[[str], EngineLikeResult], bridge: Optional[VenuTickBridge] = None) -> None:
        self._generate = generate
        self._bridge = bridge or VenuTickBridge()

    @property
    def bridge(self) -> VenuTickBridge:
        return self._bridge

    def attach(self) -> None:
        self._bridge.attach()

    def detach(self) -> None:
        self._bridge.detach()

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
