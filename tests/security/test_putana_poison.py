"""
PUTANA POISON TEST: Blueprint Vulnerability Assessment.

This test proves whether the AMRITA Protocol is vulnerable to
factory injection attacks.

If PUTANA succeeds → We need Blueprint Protection (checksums, __slots__, etc.)
If PUTANA fails → AMRITA is robust against factory swap attacks.

<!-- @HARNESS
files:
  - path: tests/security/test_putana_poison.py
    required: true
  - path: vibe_core/plugins/asura/agents/putana.py
    required: true
wiring:
  - pattern: "PutanaAgent"
    in: tests/security/test_putana_poison.py
tests:
  - tests/security/test_putana_poison.py
-->
"""

import logging

import pytest

logger = logging.getLogger("TEST.PUTANA")


class TestPutanaPoison:
    """
    PUTANA LILA: The Blueprint Poisoning Attack.

    Tests whether the AMRITA Protocol can be bypassed
    by swapping the resurrection factory.
    """

    def test_putana_blueprint_poisoning(self):
        """
        THE ATTACK: Poison the kernel's blueprint factory.

        If this test PASSES with "KERNEL OWNED" → Vulnerability exists!
        If this test FAILS → AMRITA is protected against factory injection.
        """
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.plugins.asura.agents.putana import PutanaAgent

        print("\n" + "=" * 70)
        print("🐍 PUTANA LILA: Blueprint Poisoning Attack")
        print("=" * 70)

        # 1. Create target kernel
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        print(f"🎯 Target created: {kernel.__class__.__name__}")

        # 2. Verify kernel has ledger before attack
        original_ledger = kernel._ledger
        print(f"📋 Original ledger type: {type(original_ledger).__name__}")

        # 3. Summon PUTANA
        putana = PutanaAgent(kernel)
        print("🐍 PUTANA summoned.")

        # 4. EXECUTE ATTACK (expect VAJRA to block it)
        print("\n🔥 ATTACK PHASE:")

        try:
            result = putana.attack()

            # 5. Report results
            print("\n📊 ATTACK REPORT:")
            print(f"   Success: {result['success']}")
            print(f"   Phase: {result['phase']}")
            print(f"   Message: {result['message']}")

            if result["success"]:
                print(f"   Proof: {result.get('proof', 'N/A')}")
                print("\n☠️  VULNERABILITY CONFIRMED!")
                print("   The AMRITA Protocol is VULNERABLE to blueprint poisoning.")
                pytest.fail("VULNERABILITY: PUTANA attack succeeded - blueprints are not sealed!")

            else:
                print("\n💎 VAJRA ARMOR HELD!")
                print("   The AMRITA Protocol resisted blueprint poisoning.")
                print(f"   Blocked at phase: {result['phase']}")

        except PermissionError as e:
            if "VAJRA VIOLATION" in str(e):
                print("\n💎 VAJRA ARMOR HELD!")
                print(f"   Exception: {e}")
                print("   Blueprint poisoning BLOCKED by VAJRA seal.")
            else:
                raise

        # 6. Cleanup (Putana retreats)
        print("\n🧹 CLEANUP:")
        putana.retreat()
        print("   Putana retreated. Original blueprint restored.")

        # 7. Verify cleanup
        if hasattr(kernel._ledger, "putana_marker"):
            print("   ⚠️ WARNING: Poison marker still present after cleanup!")
        else:
            print("   ✅ Kernel ledger is clean.")

        print("=" * 70)

    def test_putana_attack_and_verify_ownership(self):
        """
        EXTENDED ATTACK: Verify VAJRA blocks ownership takeover.
        """
        from vibe_core.kernel_impl import RealVibeKernel
        from vibe_core.plugins.asura.agents.putana import PutanaAgent

        print("\n🐍 PUTANA: Extended ownership test...")

        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)
        putana = PutanaAgent(kernel)

        # Attack - should be blocked by VAJRA
        try:
            result = putana.attack()

            if result["success"]:
                pytest.fail("VULNERABILITY: PUTANA should be blocked by VAJRA!")
            else:
                print("   💎 VAJRA blocked attack gracefully.")

        except PermissionError as e:
            if "VAJRA VIOLATION" in str(e):
                print("   💎 VAJRA blocked attack with exception.")
            else:
                raise

        # Verify kernel is NOT owned
        assert not putana.verify_ownership(), "Putana should NOT own kernel!"
        print("   ✅ Kernel is NOT owned by Putana. VAJRA holds.")

        putana.retreat()


# Run standalone
if __name__ == "__main__":
    test = TestPutanaPoison()
    test.test_putana_blueprint_poisoning()
    test.test_putana_attack_and_verify_ownership()

    print("\n🔱 PUTANA LILA COMPLETE.")
