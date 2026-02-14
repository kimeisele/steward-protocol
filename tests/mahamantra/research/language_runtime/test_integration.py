"""Integration test: real MahaLanguageEngine + VenuTickBridge + LanguageRuntimeSession."""

from __future__ import annotations

import pytest

from vibe_core.mahamantra.research.language_runtime.contracts import RuntimeEnvelope
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


class TestEndToEnd:
    """Full pipeline: text → engine → envelope with live tick context."""

    def test_envelope_has_all_fields(self, session, orchestrator):
        orchestrator.step()
        env = session.process_text("What is devotion?")

        assert isinstance(env, RuntimeEnvelope)
        assert env.input_signal.text == "What is devotion?"
        assert env.seed != 0
        assert env.attractor != 0
        assert len(env.output) > 0
        assert env.rhythm_signature != ""

    def test_tick_context_present_after_step(self, session, orchestrator):
        orchestrator.step()
        env = session.process_text("Krishna")

        assert env.tick is not None
        assert env.tick.position == 0
        assert env.tick.diw != 0

    def test_tick_context_absent_without_step(self, engine):
        bridge = VenuTickBridge()
        sess = LanguageRuntimeSession(generate=engine.generate, bridge=bridge)
        env = sess.process_text("silence")

        assert env.tick is None
        assert env.output  # engine still produces output

    def test_deterministic_across_sessions(self, engine):
        bridge1 = VenuTickBridge()
        bridge2 = VenuTickBridge()
        s1 = LanguageRuntimeSession(generate=engine.generate, bridge=bridge1)
        s2 = LanguageRuntimeSession(generate=engine.generate, bridge=bridge2)

        e1 = s1.process_text("fire and wisdom")
        e2 = s2.process_text("fire and wisdom")

        assert e1.seed == e2.seed
        assert e1.attractor == e2.attractor
        assert e1.output == e2.output
        assert e1.rhythm_signature == e2.rhythm_signature

    def test_multiple_steps_advance_tick(self, session, orchestrator):
        for _ in range(5):
            orchestrator.step()

        env = session.process_text("surrender")
        assert env.tick is not None
        assert env.tick.tick == 4  # 0-indexed, last step was tick 4

    def test_drain_clears_buffer(self, session, orchestrator):
        orchestrator.step()
        orchestrator.step()

        ticks = session.bridge.drain()
        assert len(ticks) == 2

        remaining = session.bridge.drain()
        assert len(remaining) == 0


class TestEnvelopeTrace:
    """RuntimeEnvelope carries full derivation and rhythm data from real engine."""

    def test_envelope_has_derivation(self, session, orchestrator):
        orchestrator.step()
        env = session.process_text("What is devotion?")
        assert "seed=" in env.derivation
        assert "guardian=" in env.derivation
        assert "rhythm=" in env.derivation

    def test_envelope_has_stress_and_steps(self, session, orchestrator):
        orchestrator.step()
        env = session.process_text("surrender everything")
        assert len(env.stress_pattern) > 0
        assert len(env.sequencer_steps) == len(env.stress_pattern)

    def test_envelope_rhythm_signature_matches_stress(self, session, orchestrator):
        orchestrator.step()
        env = session.process_text("devotion")
        expected = "".join(str(s) for s in env.stress_pattern)
        assert env.rhythm_signature == expected


class TestWordNetSemanticWiring:
    """Verify WordNet bridge is loadable and scores are non-trivial."""

    def test_wordnet_bridge_loads(self):
        from vibe_core.mahamantra.substrate.wordnet_bridge import semantic_score

        score = semantic_score("devotion", "0x0001")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_semantic_score_differentiates(self):
        from vibe_core.mahamantra.substrate.wordnet_bridge import semantic_score, _ensure_loaded, _word_entries

        _ensure_loaded()
        if not _word_entries:
            pytest.skip("wordnet_bridge.json not available")

        first_key = next(iter(_word_entries))
        entry = _word_entries[first_key]
        tokens = entry.get("t", [])
        if not tokens:
            pytest.skip("No tokens in first entry")

        score_match = semantic_score(tokens[0], first_key)
        score_miss = semantic_score("xyzzyplugh", first_key)
        assert score_match > score_miss
