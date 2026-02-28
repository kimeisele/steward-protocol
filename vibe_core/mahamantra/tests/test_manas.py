"""
Tests for MahaManas — Cognitive Mind Substrate (Tattva #6)
==========================================================

24 tests covering:
- Protocol compliance (ManasProtocol, DharmaGateProtocol, SynapticProtocol)
- Frozen dataclasses (PerceptionEntry, ManaVerdict)
- Chitta dedup
- Viveka scoring
- Hebbian learning (success/failure/persistence)
- Perceive/decide/learn cycle
- DharmaGate blocking
- Singleton
- MANAS_TATTVA constant
- No Any types
"""

import ast
import tempfile
from pathlib import Path
from typing import Tuple
from unittest.mock import patch

import pytest

from vibe_core.mahamantra.protocols._manas import (
    DharmaGateProtocol,
    ManaVerdict,
    ManasProtocol,
    PerceptionEntry,
    SynapticProtocol,
)
from vibe_core.mahamantra.substrate.core.seed import SHARANAGATI
from vibe_core.mahamantra.substrate.manas.chitta import Chitta
from vibe_core.mahamantra.substrate.manas.manas_core import MANAS_TATTVA, MahaManas
from vibe_core.mahamantra.substrate.manas.synaptic import HebbianSynaptic
from vibe_core.mahamantra.substrate.manas.viveka import is_viable, score_priority


# =========================================================================
# FIXTURES
# =========================================================================


def _make_entry(
    content: str = "test perception",
    source: str = "feed_scan",
    category: str = "sthula",
    priority: int = 50,
    **ctx: str,
) -> PerceptionEntry:
    return PerceptionEntry(
        content=content,
        source=source,
        category=category,
        priority=priority,
        context=ctx,
    )


def _mock_buddhi_result(**overrides):
    """Create a mock BuddhiResult for testing."""
    from vibe_core.mahamantra.protocols._buddhi import BuddhiResult

    defaults = {
        "perspective": "Karma Yoga - Action",
        "focus": "field",
        "approach": "DHARMA",
        "mode": "RAJAS",
        "function": "VISHNU",
        "chapter": 3,
        "verse_concepts": (),
        "resonant_words": (),
        "prana": 10800,
        "integrity": 0.8,
        "is_alive": True,
        "composed": "dharma action truth",
        "vm_result": {},
    }
    defaults.update(overrides)
    return BuddhiResult(**defaults)


class MockDharmaGate:
    """Mock DharmaGate that blocks perceptions with 'blocked' in content."""

    def check(self, perception: PerceptionEntry) -> Tuple[bool, str]:
        if "blocked" in perception.content.lower():
            return False, "content blocked by dharma"
        return True, "ok"


# =========================================================================
# PROTOCOL COMPLIANCE
# =========================================================================


class TestProtocolCompliance:
    def test_perception_entry_is_frozen(self):
        entry = _make_entry()
        with pytest.raises(AttributeError):
            entry.content = "mutated"  # type: ignore[misc]

    def test_mana_verdict_is_frozen(self):
        entry = _make_entry()
        verdict = ManaVerdict(
            perception=entry,
            approved=True,
            priority_score=50.0,
            confidence=0.5,
            dharma_ok=True,
            dharma_reason="ok",
            reason="approved",
        )
        with pytest.raises(AttributeError):
            verdict.approved = False  # type: ignore[misc]

    def test_perception_entry_default_context(self):
        entry = PerceptionEntry(content="x", source="y", category="sthula")
        assert entry.context == {}
        assert entry.priority == 50

    def test_mana_verdict_default_buddhi(self):
        entry = _make_entry()
        verdict = ManaVerdict(
            perception=entry,
            approved=True,
            priority_score=50.0,
            confidence=0.5,
            dharma_ok=True,
            dharma_reason="ok",
            reason="approved",
        )
        assert verdict.buddhi is None

    def test_dharma_gate_protocol_structural(self):
        gate = MockDharmaGate()
        assert isinstance(gate, DharmaGateProtocol)

    def test_synaptic_protocol_structural(self):
        syn = HebbianSynaptic()
        assert isinstance(syn, SynapticProtocol)

    def test_manas_protocol_structural(self):
        manas = MahaManas()
        assert isinstance(manas, ManasProtocol)


# =========================================================================
# CHITTA
# =========================================================================


class TestChitta:
    def test_receive_and_process(self):
        chitta = Chitta()
        entries = [_make_entry(content=f"topic {i}") for i in range(5)]
        chitta.receive_batch(entries)
        result = chitta.process()
        assert len(result) == 5

    def test_dedup_same_source_same_content(self):
        chitta = Chitta()
        chitta.receive(_make_entry(content="same topic", source="feed"))
        chitta.receive(_make_entry(content="same topic", source="feed"))
        chitta.receive(_make_entry(content="same topic", source="feed"))
        result = chitta.process()
        assert len(result) == 1

    def test_dedup_preserves_different_sources(self):
        chitta = Chitta()
        chitta.receive(_make_entry(content="same topic", source="feed"))
        chitta.receive(_make_entry(content="same topic", source="dm"))
        result = chitta.process()
        assert len(result) == 2

    def test_process_clears_pool(self):
        chitta = Chitta()
        chitta.receive(_make_entry())
        assert chitta.pool_size == 1
        chitta.process()
        assert chitta.pool_size == 0

    def test_dedup_uses_first_60_chars(self):
        chitta = Chitta()
        base = "x" * 60
        chitta.receive(_make_entry(content=base + "AAA"))
        chitta.receive(_make_entry(content=base + "BBB"))
        result = chitta.process()
        # Same first 60 chars → deduped
        assert len(result) == 1


# =========================================================================
# VIVEKA
# =========================================================================


class TestViveka:
    def test_score_high_prana_high_integrity(self):
        cognition = _mock_buddhi_result(prana=21600, integrity=1.0, function="BRAHMA")
        score = score_priority(cognition)
        # 60 (full prana) + 20 (full integrity) + 20 (BRAHMA) = 100
        assert score == 100.0

    def test_score_zero_prana(self):
        cognition = _mock_buddhi_result(prana=0, integrity=0.0, function="SHIVA")
        score = score_priority(cognition)
        # 0 + 0 + 5 (SHIVA) = 5
        assert score == 5.0

    def test_score_mid_range(self):
        cognition = _mock_buddhi_result(prana=10800, integrity=0.5, function="VISHNU")
        score = score_priority(cognition)
        # 30 (half prana) + 10 (half integrity) + 10 (VISHNU) = 50
        assert score == 50.0

    def test_is_viable_alive(self):
        cognition = _mock_buddhi_result(is_alive=True)
        assert is_viable(cognition) is True

    def test_is_viable_dead(self):
        cognition = _mock_buddhi_result(is_alive=False)
        assert is_viable(cognition) is False


# =========================================================================
# HEBBIAN SYNAPTIC
# =========================================================================


class TestHebbianSynaptic:
    def test_default_weight(self):
        syn = HebbianSynaptic()
        assert syn.get_weight("x", "y") == 0.5

    def test_success_increases_weight(self):
        syn = HebbianSynaptic()
        w = syn.update("x", "y", success=True)
        assert w > 0.5

    def test_failure_decreases_weight(self):
        syn = HebbianSynaptic()
        w = syn.update("x", "y", success=False)
        assert w < 0.5

    def test_success_asymptotic_to_one(self):
        syn = HebbianSynaptic()
        for _ in range(100):
            syn.update("x", "y", success=True)
        assert syn.get_weight("x", "y") > 0.99

    def test_failure_asymptotic_to_zero(self):
        syn = HebbianSynaptic()
        for _ in range(100):
            syn.update("x", "y", success=False)
        assert syn.get_weight("x", "y") < 0.01

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            syn1 = HebbianSynaptic(state_dir=path)
            syn1.update("a", "b", success=True)
            syn1.flush()
            w1 = syn1.get_weight("a", "b")

            syn2 = HebbianSynaptic(state_dir=path)
            w2 = syn2.get_weight("a", "b")
            assert w1 == w2

    def test_snapshot(self):
        syn = HebbianSynaptic()
        syn.update("a", "b", success=True)
        snap = syn.snapshot()
        assert "a→b" in snap
        assert isinstance(snap["a→b"], float)


# =========================================================================
# MAHA MANAS (INTEGRATION)
# =========================================================================


class TestMahaManas:
    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_perceive_decide_learn_cycle(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entries = [
            _make_entry(content="topic A"),
            _make_entry(content="topic B"),
        ]

        clean = manas.perceive(entries)
        assert len(clean) == 2

        verdicts = manas.decide(clean, max_verdicts=5)
        assert len(verdicts) == 2
        assert all(v.approved for v in verdicts)

        manas.learn(verdicts[0], success=True)
        assert manas.learn_count == 1

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_dead_cell_not_approved(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result(is_alive=False)

        manas = MahaManas()
        clean = manas.perceive([_make_entry()])
        verdicts = manas.decide(clean)
        assert len(verdicts) == 0  # Dead cell → not approved

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_dharma_gate_blocks(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        manas.set_dharma_gate(MockDharmaGate())

        entries = [
            _make_entry(content="good topic"),
            _make_entry(content="blocked topic"),
        ]

        clean = manas.perceive(entries)
        verdicts = manas.decide(clean, max_verdicts=5)
        # Only "good topic" approved
        assert len(verdicts) == 1
        assert verdicts[0].perception.content == "good topic"

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_max_verdicts_limit(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entries = [_make_entry(content=f"topic {i}") for i in range(10)]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean, max_verdicts=3)
        assert len(verdicts) <= 3

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_verdicts_sorted_by_priority(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value

        # Different prana levels → different priorities
        results = [
            _mock_buddhi_result(prana=21600, function="BRAHMA"),
            _mock_buddhi_result(prana=5400, function="SHIVA"),
            _mock_buddhi_result(prana=10800, function="VISHNU"),
        ]
        mock_buddhi.think.side_effect = results

        manas = MahaManas()
        entries = [_make_entry(content=f"topic {i}") for i in range(3)]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean, max_verdicts=3)

        assert verdicts[0].priority_score >= verdicts[1].priority_score
        assert verdicts[1].priority_score >= verdicts[2].priority_score

    def test_snapshot(self):
        manas = MahaManas()
        snap = manas.snapshot()
        assert "perceive_count" in snap
        assert "decide_count" in snap
        assert "learn_count" in snap
        assert "synaptic_weights" in snap


# =========================================================================
# SINGLETON + CONSTANTS
# =========================================================================


class TestSingleton:
    def test_get_manas_singleton(self):
        from vibe_core.mahamantra.substrate.manas import get_manas

        # Reset singleton for test
        import vibe_core.mahamantra.substrate.manas as manas_mod

        manas_mod._manas_instance = None

        a = get_manas()
        b = get_manas()
        assert a is b

    def test_manas_tattva_equals_sharanagati(self):
        assert MANAS_TATTVA == SHARANAGATI
        assert MANAS_TATTVA == 6


# =========================================================================
# MEDITATION MODE (COOLDOWN + SHOULD_ACT)
# =========================================================================


class TestMeditationMode:
    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_record_outcome_success_clears_cooldown(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entry = _make_entry(content="test", source="feed_scan")
        clean = manas.perceive([entry])
        verdicts = manas.decide(clean)
        assert len(verdicts) == 1

        # Record 3 failures → cooldown
        for _ in range(3):
            manas.record_outcome(verdicts[0], success=False)
        assert manas.is_in_cooldown("feed_scan")

        # Success clears cooldown
        manas.record_outcome(verdicts[0], success=True)
        assert not manas.is_in_cooldown("feed_scan")

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_cooldown_after_max_failures(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entry = _make_entry(content="test", source="feed_scan")
        clean = manas.perceive([entry])
        verdicts = manas.decide(clean)

        # 2 failures = not yet in cooldown
        manas.record_outcome(verdicts[0], success=False)
        manas.record_outcome(verdicts[0], success=False)
        assert not manas.is_in_cooldown("feed_scan")

        # 3rd failure → cooldown
        manas.record_outcome(verdicts[0], success=False)
        assert manas.is_in_cooldown("feed_scan")

    def test_should_act_true_before_first_decide(self):
        manas = MahaManas()
        assert manas.should_act() is True

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_should_act_false_when_zero_approved(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result(is_alive=False)

        manas = MahaManas()
        entries = [_make_entry()]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean)
        assert len(verdicts) == 0
        assert manas.should_act() is False

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_should_act_false_when_all_sources_cooled(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entry = _make_entry(source="only_source")
        clean = manas.perceive([entry])
        verdicts = manas.decide(clean)

        # Cooldown the only source
        for _ in range(3):
            manas.record_outcome(verdicts[0], success=False)

        assert manas.should_act() is False

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_should_act_true_when_some_sources_active(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entries = [
            _make_entry(source="source_a"),
            _make_entry(source="source_b"),
        ]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean)

        # Cool down only source_a
        v_a = [v for v in verdicts if v.perception.source == "source_a"][0]
        for _ in range(3):
            manas.record_outcome(v_a, success=False)

        # source_b still active → should_act = True
        assert manas.should_act() is True

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_perceive_filters_cooled_sources(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        # First pass to register and cool down
        entries = [_make_entry(source="hot"), _make_entry(source="cold")]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean)

        v_cold = [v for v in verdicts if v.perception.source == "cold"][0]
        for _ in range(3):
            manas.record_outcome(v_cold, success=False)

        # Second pass: cold source filtered out
        entries2 = [
            _make_entry(content="new hot", source="hot"),
            _make_entry(content="new cold", source="cold"),
        ]
        clean2 = manas.perceive(entries2)
        assert len(clean2) == 1
        assert clean2[0].source == "hot"

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_snapshot_includes_cooldown_state(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entries = [_make_entry(source="test_source")]
        clean = manas.perceive(entries)
        verdicts = manas.decide(clean)
        for _ in range(3):
            manas.record_outcome(verdicts[0], success=False)

        snap = manas.snapshot()
        assert "cooldowns" in snap
        assert "failure_counts" in snap
        assert "known_sources" in snap
        assert "last_approved_count" in snap
        assert "test_source" in snap["known_sources"]

    @patch("vibe_core.mahamantra.substrate.buddhi.get_buddhi")
    def test_record_outcome_integrates_with_learn(self, mock_get_buddhi):
        mock_buddhi = mock_get_buddhi.return_value
        mock_buddhi.think.return_value = _mock_buddhi_result()

        manas = MahaManas()
        entry = _make_entry()
        clean = manas.perceive([entry])
        verdicts = manas.decide(clean)

        manas.record_outcome(verdicts[0], success=True)
        # record_outcome calls learn internally
        assert manas.learn_count == 1

    def test_is_in_cooldown_false_for_unknown_source(self):
        manas = MahaManas()
        assert not manas.is_in_cooldown("nonexistent")

    def test_protocol_compliance_new_methods(self):
        from vibe_core.mahamantra.protocols._manas import ManasProtocol

        assert hasattr(ManasProtocol, "record_outcome")
        assert hasattr(ManasProtocol, "should_act")
        assert hasattr(ManasProtocol, "is_in_cooldown")


# =========================================================================
# CODE QUALITY
# =========================================================================


class TestCodeQuality:
    """Verify no Any types in MahaManas protocol and substrate."""

    @pytest.mark.parametrize(
        "filepath",
        [
            "vibe_core/mahamantra/protocols/_manas.py",
            "vibe_core/mahamantra/substrate/manas/manas_core.py",
            "vibe_core/mahamantra/substrate/manas/chitta.py",
            "vibe_core/mahamantra/substrate/manas/viveka.py",
            "vibe_core/mahamantra/substrate/manas/synaptic.py",
        ],
    )
    def test_no_any_type(self, filepath):
        source = Path(filepath).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "Any":
                pytest.fail(f"Any type found in {filepath}")
