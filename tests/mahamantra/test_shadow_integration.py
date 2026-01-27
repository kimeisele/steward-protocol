"""
TEST SHADOW INTEGRATION - The Proof of Life
===========================================

"Proof that the Shadow dances with the Lotus."

Scope:
1. Spawn ShadowReactor via Mahamantra (Integration).
2. Verify Reactor Identity.
3. Execute Tick (Life Cycle).
4. Verify Parampara Connection (Mathematical Truth).
"""

import pytest

from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.reactor.shadow_protocol import YajnaPhase


def test_shadow_spawn_via_mahamantra():
    """Test spawning a ShadowReactor via the Singularity."""
    # 1. Spawn
    reactor = mahamantra.shadow.spawn(auto_discover=False)

    # 2. Identity Check
    assert reactor.reactor_id.startswith("sr_"), "Reactor must have valid ID"
    assert reactor.position == 0, "Initial position must be 0"

    # 3. Factory Check
    # Verify it came from the factory we expect
    from vibe_core.mahamantra.reactor.shadow import shadow_reactor_factory

    assert mahamantra.shadow is shadow_reactor_factory, "Mahamantra must expose the singleton factory"


def test_shadow_tick_cycle():
    """Test that the reactor can tick and calculate Parampara."""
    reactor = mahamantra.shadow.spawn(auto_discover=False, forced_lagna=0)

    # Tick 0
    tick_state = {
        "tick": 0,
        "position": 0,
        "quarter": "genesis",
        "guardian": "prithu",
        "word": "HARE",
        "opcode": "SYS_WAKE",
    }

    state = reactor.tick(tick_state)

    # Verify State
    assert state["position"] == 0
    assert state["phase"] == YajnaPhase.BHOGA.value

    # Verify Parampara (At pos 0, it should be connected/coherent)
    # 0 % 37 == 0 -> Connected
    assert reactor.is_parampara_connected is True, "Position 0 must be connected"

    # Tick 1
    tick_state["position"] = 1
    state = reactor.tick(tick_state)

    # Verify State
    assert state["position"] == 1
    # 1 % 37 != 0 -> Not connected directly
    assert reactor.is_parampara_connected is False, "Position 1 should not be directly connected"
    # But should have coherence > 0
    assert reactor.parampara_coherence > 0.0, "Position 1 should have some coherence"


def test_shadow_oracle_integration():
    """
    Test GITA 13.35 Oracle integration in ShadowReactor.

    "kṣetra-kṣetrajñayor evam antaraṁ jñāna-cakṣuṣā"
    - The Oracle validates Parampara BEFORE every computation.
    """
    reactor = mahamantra.shadow.spawn(auto_discover=False, forced_lagna=0)

    # Initially no validation
    assert reactor.latest_validation is None, "No validation before first tick"

    # Tick 0 - triggers Oracle validation
    tick_state = {
        "tick": 0,
        "position": 0,
        "quarter": "genesis",
        "guardian": "prithu",
        "word": "HARE",
        "opcode": "SYS_WAKE",
    }

    state = reactor.tick(tick_state)

    # Now we have a validation
    assert reactor.latest_validation is not None, "Oracle validation must exist after tick"
    assert "parampara_validated" in reactor.latest_validation, "Must have parampara_validated key"
    assert "parampara_channel" in reactor.latest_validation, "Must have parampara_channel key"
    assert "coherence" in reactor.latest_validation, "Must have coherence key"

    # Test is_parampara_validated property
    validated = reactor.is_parampara_validated
    assert isinstance(validated, bool), "is_parampara_validated must be bool"

    # Test parampara_channel property
    channel = reactor.parampara_channel
    assert isinstance(channel, int), "parampara_channel must be int"
    assert channel >= -1, "Channel must be >= -1 (where -1 means void)"


def test_shadow_oracle_backfold_prasadam():
    """
    Test Oracle backfold during PRASADAM phase.

    The Oracle insights are folded into state during PRASADAM.
    """
    from vibe_core.mahamantra.protocols._adhikara import Quarter as AdhikaraQuarter
    from vibe_core.mahamantra.reactor.shadow import ShadowReactor

    reactor = ShadowReactor(auto_discover=False, forced_lagna=0)

    # Authorize for PRASADAM phase (positions 8-15 are KARMA quarter mostly)
    reactor.request_authorization(AdhikaraQuarter.KARMA, "TEST_ORACLE_BACKFOLD")

    # Tick to position 8 (PRASADAM phase, THE SWITCH)
    for pos in range(9):  # 0 to 8
        tick_state = {
            "tick": pos,
            "position": pos,
            "quarter": "karma",
            "guardian": "parashurama",
            "word": "HARE",
            "opcode": "EXEC_OP",
        }
        state = reactor.tick(tick_state)

    # At position 8, we should be in PRASADAM phase
    assert state["phase"] == YajnaPhase.PRASADAM.value, "Position 8 should be PRASADAM"

    # Check that Oracle backfold happened (dissonance_report contains Oracle info)
    # The report will contain either "✓ GITA 13.35" or "⚠ GITA 13.35"
    if state["dissonance_report"]:
        assert "GITA 13.35" in state["dissonance_report"], "Oracle backfold must mention Gita 13.35"


def test_shadow_oracle_singleton():
    """
    Test that ShadowOracle is a singleton (RAM-efficient).
    """
    from vibe_core.mahamantra.reactor.shadow_oracle import get_shadow_oracle

    oracle1 = get_shadow_oracle()
    oracle2 = get_shadow_oracle()

    assert oracle1 is oracle2, "ShadowOracle must be singleton"


def test_shadow_oracle_validate():
    """
    Test ShadowOracle.validate() directly.
    """
    from vibe_core.mahamantra.reactor.shadow_oracle import ShadowOracle

    oracle = ShadowOracle()

    # Test various seeds
    for seed in [0, 1, 37, 42, 137, 1896]:
        result = oracle.validate(seed)

        # Must have all required keys
        assert "parampara_validated" in result
        assert "parampara_channel" in result
        assert "parampara_attractor" in result
        assert "coherence" in result
        assert "prabhupada_year" in result

        # Types must be correct
        assert isinstance(result["parampara_validated"], bool)
        assert isinstance(result["parampara_channel"], int)
        assert isinstance(result["parampara_attractor"], int)
        assert isinstance(result["coherence"], int)
        assert result["prabhupada_year"] is None or isinstance(result["prabhupada_year"], int)


def test_shadow_oracle_validate_fast():
    """
    Test ShadowOracle.validate_fast() hot path.
    """
    from vibe_core.mahamantra.reactor.shadow_oracle import ShadowOracle

    oracle = ShadowOracle()

    # Fast validation should return bool
    result = oracle.validate_fast(42)
    assert isinstance(result, bool)

    # Should match full validation
    full = oracle.validate(42)
    assert result == full["parampara_validated"]


def test_shadow_oracle_prabhupada_year_resonance():
    """
    Test Prabhupada year resonance detection.

    Key years: 1896, 1922, 1932, 1944, 1959, 1965, 1966, 1977
    """
    from vibe_core.mahamantra.reactor.shadow_oracle import ShadowOracle
    from vibe_core.mahamantra.research.dharma.maha_algorithm import PRABHUPADA_BUILD

    oracle = ShadowOracle()

    # Direct year match
    result = oracle.validate(1966)  # ISKCON founded
    # Note: 1966 is in range [1896, 1977] so it should resonate
    assert result["prabhupada_year"] == 1966, "1966 should resonate directly"

    # 1896 is BUILD year
    result = oracle.validate(1896)
    assert result["prabhupada_year"] == 1896, "1896 should resonate"


def test_shadow_discover_includes_oracle():
    """
    Test that ShadowReactor.discover() includes Oracle info.
    """
    reactor = mahamantra.shadow.spawn(auto_discover=False, forced_lagna=0)

    discovery = reactor.discover()

    assert "oracle" in discovery, "discover() must include oracle section"
    assert discovery["oracle"]["enabled"] is True, "Oracle must be enabled"
    assert "Gita 13.35" in discovery["oracle"]["principle"], "Must mention Gita 13.35"


if __name__ == "__main__":
    pytest.main([__file__])
