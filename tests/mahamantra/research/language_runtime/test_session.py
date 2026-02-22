from __future__ import annotations

from typing import NamedTuple, cast

from vibe_core.mahamantra.protocols._venu import DIWEvent
from vibe_core.mahamantra.research.language_runtime.session import LanguageRuntimeSession
from vibe_core.mahamantra.research.language_runtime.venu_bridge import VenuTickBridge


class FakeResult(NamedTuple):
    seed: int
    attractor: int
    output: str
    derivation: str
    stress_pattern: tuple[int, ...]
    sequencer_steps: tuple[int, ...]


def _event() -> DIWEvent:
    return cast(
        DIWEvent,
        {
            "diw": 456,
            "tick": 9,
            "position": 5,
            "phase": 1,
            "venu": 15,
            "vamsi": 99,
            "murali": 1,
            "mode": 2,
        },
    )


def test_process_text_returns_runtime_envelope_with_tick_context() -> None:
    bridge = VenuTickBridge()
    bridge.on_diw(_event())

    session = LanguageRuntimeSession(
        generate=lambda text: FakeResult(
            seed=111,
            attractor=22,
            output=f"OUT:{text}",
            derivation="seed=111",
            stress_pattern=(1, 0, 1),
            sequencer_steps=(0, 2, 3),
        ),
        bridge=bridge,
    )

    envelope = session.process_text("devotion")
    assert envelope.input_signal.text == "devotion"
    assert envelope.tick is not None
    assert envelope.tick.tick == 9
    assert envelope.seed == 111
    assert envelope.attractor == 22
    assert envelope.rhythm_signature == "101"
    assert envelope.output == "OUT:devotion"
    assert envelope.derivation == "seed=111"
    assert envelope.stress_pattern == (1, 0, 1)
    assert envelope.sequencer_steps == (0, 2, 3)


def test_process_text_without_stress_uses_dash_signature() -> None:
    session = LanguageRuntimeSession(
        generate=lambda text: FakeResult(
            seed=1, attractor=2, output=text, derivation="", stress_pattern=(), sequencer_steps=()
        ),
        bridge=VenuTickBridge(),
    )

    envelope = session.process_text("house")
    assert envelope.rhythm_signature == "-"
