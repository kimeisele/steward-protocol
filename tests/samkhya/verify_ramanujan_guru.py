import sys
import unittest
from decimal import Decimal, getcontext

# Set match context
getcontext().prec = 108

# Import Ramanujan
from vibe_core.protocols.universal.ramanujan import RamanujanProtocol


class TestGuruLogic(unittest.TestCase):
    def test_guru_closure(self):
        """Invoke the _test_guru_closure method directly."""
        rp = RamanujanProtocol()

        # Test 12 is Entropy, Test 13 is Guru (Index 12 in list if 0-indexed? No, explicit method call)

        print("\n--- INVOKING GURU CLOSURE ---")
        result = rp._test_guru_closure(None, None)
        print(f"Guru Closure Result: {result}")

        self.assertTrue(result)

    def test_samsara_loop_explicit(self):
        """Explicitly re-verify the 36/37 loop."""
        samsara = Decimal(36) / Decimal(37)
        s_str = str(samsara)
        print(f"\nSamsara (36/37): {s_str[:50]}...")

        # Check recurring pattern "972" (36*27 = 972)
        repeating = s_str.split(".")[1][:9]
        self.assertEqual(repeating, "972972972")


if __name__ == "__main__":
    unittest.main()
