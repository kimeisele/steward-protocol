"""
INTEGRATION TEST: TULASI GATE (Production)
==========================================

"ye yathā māṁ prapadyante..." (BG 4.11)

Verifies the production integration of TulasiGate into MahaModularSynth.
"""

import pytest
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.adapters.tulasi_gate import TulasiGate
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, POSITION_SUM_TOTAL, HARE_COUNT


def test_production_integration():
    """
    Verify that the Synth happily accepts the Tulasi Gate
    and changes behavior based on the HasTulasi flag.
    """

    # 1. Setup with Gate
    gate = TulasiGate()
    synth = MahaModularSynth(default_preset="quantum", grace_gate=gate)

    # 2. Test Loop WITHOUT Tulasi (Bhoga / Material Field)
    # Seed 136 (POSITION_SUM_TOTAL) represents the Classical Field (No Observer).
    # It enters the loop as 136.

    res_standard = synth.transform(seed=POSITION_SUM_TOTAL, has_tulasi=False)

    # 3. Test Loop WITH Tulasi (Transcendental Expansion)
    # Seed 136 becomes 137 via purify_offering.
    # Mod Space becomes 137 * 8 = 1096 via expand_field.
    # The loop runs in the Expanded Field.

    res_tulasi = synth.transform(seed=POSITION_SUM_TOTAL, has_tulasi=True)

    print(f"\n[INTEGRATION] Standard Result (seed=136): {res_standard}")
    print(f"[INTEGRATION] Tulasi Result (seed=136->137, mod=1096): {res_tulasi}")

    # Assert they are DIFFERENT (Grace changes the outcome)
    assert res_standard != res_tulasi, "Tulasi had no effect!"

    # Assert Calculation Logic match
    # With field expansion, output can exceed 137 but must be within 1096

    val_tulasi = synth.transform(seed=108, has_tulasi=True)
    val_standard = synth.transform(seed=108, has_tulasi=False)

    print(f"[PROOF] Standard: {val_standard}, Tulasi: {val_tulasi}")

    assert val_tulasi != val_standard, "Tulasi must have an effect"
    assert val_tulasi < MAHA_QUANTUM * HARE_COUNT, "Tulasi should stay within Transcendental Field (1096)"

    # We found a qualitative difference (Expansion)
    print("[CONCLUSION] Tulasi Gate is operational. Field is expanded.")


if __name__ == "__main__":
    test_production_integration()
