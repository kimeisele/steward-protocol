"""
ORBITAL VERIFICATION - PRITHU'S DANCE
======================================

Verifies that two Shadow Reactors can walk the path with different PHASE OFFSETS (Lagna).
This proves the "Flat Earth" problem is solved.

Scenario:
    - Reactor A (ID="A_SUN")
    - Reactor B (ID="B_MOON")

    They should have different Lagna.
    At Tick 0, they should see different positions.
"""

from vibe_core.mahamantra.reactor.shadow import shadow_reactor_factory
from vibe_core.mahamantra.substrate.orbit import OrbitCalculator
from vibe_core.mahamantra.reactor.shadow_protocol import TickStateInput


def verify_orbit():
    print("=== ORBITAL REACTOR VERIFICATION ===")

    # 1. Create two reactors manually to force IDs (mocking factory behavior or just checking lagna)
    # Since we can't easily force ID in __init__ (it generates UUID),
    # we will rely on random UUIDs having different Lagna.

    r1 = shadow_reactor_factory.spawn(auto_discover=False)
    r2 = shadow_reactor_factory.spawn(auto_discover=False)

    print(f"Reactor 1: {r1}")
    print(f"Reactor 2: {r2}")

    # Check Lagna
    l1 = r1.lagna
    l2 = r2.lagna

    if l1 == l2:
        print("WARNING: Random collision or fixed offset? Trying again...")
        r2 = shadow_reactor_factory.spawn(auto_discover=False)
        l2 = r2.lagna

    print(f"Lagna 1: {l1}")
    print(f"Lagna 2: {l2}")

    # 2. Drive Tick 0 (Global)
    # Construct input state
    global_tick = 0
    input_state: TickStateInput = {
        "tick": global_tick,
        "position": global_tick % 16,
        "quarter": "genesis",  # dummy
        "guardian": "brahma",  # dummy
        "word": "hare",
        "opcode": None,
    }

    # Process
    s1 = r1.tick(input_state)
    s2 = r2.tick(input_state)

    print("\n--- TICK 0 SIMULATION ---")
    print(f"R1 sees Position: {s1['position']} (Expected {(0 - l1) % 16})")
    print(f"R2 sees Position: {s2['position']} (Expected {(0 - l2) % 16})")

    assert s1["position"] == (0 - l1) % 16
    assert s2["position"] == (0 - l2) % 16

    if l1 != l2:
        assert s1["position"] != s2["position"]
        print("✅ SUCCESS: Reactors are in different orbits!")
    else:
        print("⚠️ SKIPPED: Lagna collision (unlikely but possible)")


if __name__ == "__main__":
    verify_orbit()
