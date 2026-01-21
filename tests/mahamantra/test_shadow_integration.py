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


if __name__ == "__main__":
    pytest.main([__file__])
