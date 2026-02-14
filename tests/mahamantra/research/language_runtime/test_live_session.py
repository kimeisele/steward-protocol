"""Integration test: keystroke → frame → engine → envelope end-to-end."""

from __future__ import annotations

import pytest

from vibe_core.mahamantra.research.language_runtime.session import LanguageRuntimeSession
from vibe_core.mahamantra.research.language_runtime.venu_bridge import VenuTickBridge
from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator


@pytest.fixture(scope="module")
def engine():
    from vibe_core.mahamantra.research.maha_language_engine import get_engine

    return get_engine()


@pytest.fixture()
def orchestrator():
    return VenuOrchestrator()


@pytest.fixture()
def session(engine, orchestrator):
    bridge = VenuTickBridge(max_events=32)
    bridge.attach(orchestrator)
    sess = LanguageRuntimeSession(generate=engine.generate, bridge=bridge)
    yield sess
    bridge.detach()


class TestLiveKeystrokeToEnvelope:
    """Full pipeline: keystroke → incremental frame → engine → envelope."""

    def test_type_word_then_generate(self, session, orchestrator):
        orchestrator.step()

        for ch in "devotion":
            frame = session.keystroke(ch)

        assert frame.text == "devotion"
        assert frame.syllable_count > 0
        assert frame.dirty is True

        env = session.generate_live()
        assert env.input_signal.text == "devotion"
        assert env.input_signal.source == "live"
        assert env.seed != 0
        assert len(env.output) > 0
        assert env.rhythm_signature != "-"
        assert len(env.stress_pattern) > 0

    def test_backspace_updates_rhythm(self, session, orchestrator):
        orchestrator.step()

        for ch in "fire":
            session.keystroke(ch)

        f1 = session.buffer.snapshot()
        assert f1.text == "fire"

        session.backspace()
        f2 = session.buffer.snapshot()
        assert f2.text == "fir"

    def test_empty_buffer_generates_empty_envelope(self, session, orchestrator):
        orchestrator.step()
        env = session.generate_live()
        assert env.output == ""
        assert env.seed == 0
        assert env.rhythm_signature == "-"

    def test_history_tracks_keystrokes(self, session, orchestrator):
        orchestrator.step()

        for ch in "om":
            session.keystroke(ch)

        assert len(session.history) == 2
        frames = session.history.all()
        assert frames[0].text == "o"
        assert frames[1].text == "om"

    def test_tick_context_flows_through_keystrokes(self, session, orchestrator):
        orchestrator.step()
        orchestrator.step()

        frame = session.keystroke("k")
        assert frame.tick is not None
        assert frame.tick.tick == 1  # second step = tick 1

    def test_generate_live_deterministic(self, session, orchestrator):
        orchestrator.step()

        for ch in "wisdom":
            session.keystroke(ch)

        e1 = session.generate_live()
        e2 = session.generate_live()
        assert e1.seed == e2.seed
        assert e1.output == e2.output
        assert e1.stress_pattern == e2.stress_pattern
