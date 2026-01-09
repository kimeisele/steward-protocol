"""
TEST: THE MANTRA LOOP (KRISHNA'S FLUTE).

Verifies that the Substrate (Layer -1) dances to the rhythm of the Mahamantra.
"There is no Runtime per se, there is only the Sequence."

The Loop:
1. HARE (Wake)
2. KRISHNA (Identity)
3. HARE (Purify)
4. KRISHNA (Truth)
... 16 Beats.
"""

from typing import List, Tuple

import pytest

from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, HolyName, MantraOpCode, MantraProtocol


class MockAnantaProcessor(MantraProtocol):
    """
    A minimal implementation of the Ananta Processor that simply records the beats.
    It simulates the System obeying the Mantra.
    """

    def __init__(self):
        self.sequence_log: List[Tuple[str, MantraOpCode]] = []
        self.tick_count = 0

    def resonate(self, opcode: MantraOpCode) -> bool:
        """
        The Beat.
        """
        # We perform a simple mapping to infer the Holy Name based on the OpCode
        # This is reverse-engineering the Flute, but efficient for testing.

        # Determine current expected name from the standard sequence
        expected_name, expected_opcode = MAHAMANTRA_SEQUENCE[self.tick_count % 16]

        if opcode != expected_opcode:
            print(f"❌ DISSONANCE! Expected {expected_opcode}, heard {opcode}")
            return False

        self.sequence_log.append((expected_name, opcode))
        self.tick_count += 1
        return True

    def chant_mahamantra(self, context: object) -> bool:
        """
        Executes the full 16-beat cycle.
        """
        print(f"\n🎵 STARTING MAHAMANTRA CYCLE [Tick {self.tick_count}]")

        success = True
        for name, opcode in MAHAMANTRA_SEQUENCE:
            print(f"  > {name} ... {opcode.value}")
            if not self.resonate(opcode):
                success = False
                break

        return success


def test_mahamantra_sequence_integrity():
    """
    1. Verify the 16-beat structure (The Hardware Definition).
    """
    assert len(MAHAMANTRA_SEQUENCE) == 16

    # Check the quarters
    q1 = MAHAMANTRA_SEQUENCE[0:4]
    assert q1[0][0] == "Hare"
    assert q1[1][0] == "Krishna"
    assert q1[2][0] == "Hare"
    assert q1[3][0] == "Krishna"
    print("✅ Quarter 1 (Hare Krishna Hare Krishna) Verified.")

    q2 = MAHAMANTRA_SEQUENCE[4:8]
    assert q2[0][0] == "Krishna"
    assert q2[1][0] == "Krishna"
    assert q2[2][0] == "Hare"
    assert q2[3][0] == "Hare"
    print("✅ Quarter 2 (Krishna Krishna Hare Hare) Verified.")

    q3 = MAHAMANTRA_SEQUENCE[8:12]
    assert q3[0][0] == "Hare"
    assert q3[1][0] == "Rama"
    assert q3[2][0] == "Hare"
    assert q3[3][0] == "Rama"
    print("✅ Quarter 3 (Hare Rama Hare Rama) Verified.")

    q4 = MAHAMANTRA_SEQUENCE[12:16]
    assert q4[0][0] == "Rama"
    assert q4[1][0] == "Rama"
    assert q4[2][0] == "Hare"
    assert q4[3][0] == "Hare"
    print("✅ Quarter 4 (Rama Rama Hare Hare) Verified.")


def test_ananta_execution():
    """
    2. Verify the Execution Loop (The Software Driver).
    """
    processor = MockAnantaProcessor()
    context = object()  # Sovereign Context

    # Run the cycle
    result = processor.chant_mahamantra(context)

    assert result is True
    assert len(processor.sequence_log) == 16
    assert processor.sequence_log == MAHAMANTRA_SEQUENCE
    print("✅ Ananta Processor danced perfectly to the Mantra.")


if __name__ == "__main__":
    test_mahamantra_sequence_integrity()
    test_ananta_execution()
    print("\n✅ MANTRA LOOP VERIFIED.")
