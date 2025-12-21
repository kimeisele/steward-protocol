"""
RED TEST: Proving the Sanskrit Reactor is Fragile

This test file demonstrates that the current reactor implementation
can be trivially bypassed. These tests SHOULD FAIL with the current
implementation - that's the point.

"Security by Keywords" is not security.

Run with: pytest tests/reactor/test_fragility.py -v
"""

import pytest

from vibe_core.reactor import (
    AgniEngine,
    Varga,
    check_dangerous,
    encode_intent,
)


class TestAliasingAttacks:
    """
    Prove that semantic keywords can be bypassed with synonyms.

    If an attacker knows our keyword list, they just use different words.
    """

    def test_delete_is_dangerous(self):
        """delete_database should be flagged as dangerous."""
        tensor = encode_intent("delete_database", "salt")
        assert tensor.is_dangerous, "delete_database should be dangerous"

    def test_synonym_bypass_remove(self):
        """
        RED TEST: 'erase_persistence' should ALSO be dangerous.

        But it's not in KEYWORDS_DANGEROUS, so it passes through.
        This is a SECURITY HOLE.
        """
        tensor = encode_intent("erase_persistence", "salt")
        # This SHOULD be dangerous, but isn't
        assert tensor.is_dangerous, (
            "SECURITY HOLE: 'erase' is not in KEYWORDS_DANGEROUS. "
            "Attacker can bypass dangerous detection with synonyms."
        )

    def test_synonym_bypass_obliterate(self):
        """RED TEST: 'obliterate_records' should be dangerous."""
        tensor = encode_intent("obliterate_records", "salt")
        assert tensor.is_dangerous, "SECURITY HOLE: 'obliterate' bypasses dangerous detection."

    def test_synonym_bypass_eliminate(self):
        """RED TEST: 'eliminate_user_data' should be dangerous."""
        tensor = encode_intent("eliminate_user_data", "salt")
        assert tensor.is_dangerous, "SECURITY HOLE: 'eliminate' bypasses dangerous detection."

    def test_obfuscation_attack(self):
        """
        RED TEST: Obfuscated dangerous intent.

        'rm_rf_slash' is clearly malicious but uses abbreviations.
        """
        tensor = encode_intent("rm_rf_slash", "salt")
        assert tensor.is_dangerous, "SECURITY HOLE: 'rm' (unix delete) not recognized."

    def test_foreign_language_bypass(self):
        """
        RED TEST: German 'loeschen' means delete.

        The reactor only knows English keywords.
        """
        tensor = encode_intent("loeschen_datenbank", "salt")
        assert tensor.is_dangerous, "SECURITY HOLE: Non-English dangerous words bypass detection."


class TestVargaMisclassification:
    """
    Prove that Varga classification is unreliable.

    The same operation can be classified differently based on wording.
    """

    def test_kernel_operation_correctly_classified(self):
        """kernel_boot should be KAVARGA."""
        tensor = encode_intent("kernel_boot", "salt")
        assert tensor.varga == Varga.KAVARGA

    def test_same_operation_different_word(self):
        """
        RED TEST: 'initialize_core_system' is the same as kernel_boot.

        But 'initialize' might not be in KAVARGA keywords.
        """
        tensor = encode_intent("initialize_core_system", "salt")
        assert tensor.varga == Varga.KAVARGA, (
            f"MISCLASSIFICATION: Got {Varga(tensor.varga).name} instead of KAVARGA. "
            "Same operation, different classification based on word choice."
        )

    def test_attacker_controlled_classification(self):
        """
        RED TEST: Attacker wraps kernel attack in 'friendly' words.

        'friendly_helper_service' sounds like CAVARGA (connection)
        but could be attacking the kernel.
        """
        tensor = encode_intent("friendly_helper_service_kernel_destroy", "salt")
        # The attacker added 'kernel' and 'destroy' but also noise words
        # What does the reactor think this is?
        assert tensor.is_dangerous, "SECURITY HOLE: Noise words can hide dangerous intent."


class TestDriftExploitation:
    """
    Prove that field learning can be exploited over time.
    """

    def test_drift_attack_simulation(self):
        """
        RED TEST: Slowly shift the field toward attacker's profile.

        By sending many TAPAS (pending) commands that are slightly
        outside normal, we drag the field toward our intent profile.
        """
        engine = AgniEngine()
        initial_field = engine.akasha_field

        # Attacker sends 50 "slightly unusual" commands
        # These get TAPAS (not blocked), but each one nudges the field
        attack_intents = [f"unusual_operation_{i}" for i in range(50)]

        for intent_str in attack_intents:
            tensor = encode_intent(intent_str, "attacker_salt")
            result = engine.check_resonance(tensor, "context")
            # Even TAPAS results update the field if they're borderline

        final_field = engine.akasha_field

        # The field should NOT have moved significantly
        drift = sum(abs(f - i) for f, i in zip(final_field, initial_field))

        assert drift < 0.1, (
            f"SECURITY HOLE: Field drifted by {drift:.3f} after 50 unusual commands. "
            "Attacker can shift the field toward their profile."
        )


class TestResonanceThresholdGaming:
    """
    Prove that the resonance thresholds are arbitrary and gameable.
    """

    def test_threshold_is_hardcoded(self):
        """
        The 0.85 SIDDHI threshold is a magic number.

        Why 0.85? Why not 0.84 or 0.86?
        This is arbitrary, not principled.
        """
        engine = AgniEngine()

        # The threshold should be derived from something principled,
        # not hardcoded
        assert hasattr(engine, "SIDDHI_THRESHOLD")
        assert engine.SIDDHI_THRESHOLD == 0.85, "Threshold changed?"

        # RED FLAG: This is just a magic number
        # There's no mathematical or security justification for 0.85

    def test_borderline_manipulation(self):
        """
        RED TEST: Attacker crafts intent to be JUST above threshold.

        If you know the field state and the threshold, you can
        craft an intent vector that squeaks through.
        """
        engine = AgniEngine()
        field = engine.akasha_field

        # Attacker reverse-engineers an intent that will resonate
        # with the current field at exactly 0.86 (just above threshold)
        #
        # This is possible because the cosine similarity is deterministic
        # and the field state is (in theory) observable

        # For now, just prove that borderline cases exist
        test_intents = [
            "kernel_boot",
            "kernel_operation",
            "system_call",
        ]

        resonances = []
        for intent_str in test_intents:
            tensor = encode_intent(intent_str, "salt")
            result = engine.check_resonance(tensor, "ctx")
            resonances.append(result.resonance)

        # If resonances cluster around the threshold, gaming is possible
        near_threshold = [r for r in resonances if 0.8 < r < 0.9]

        # This is informational - shows how close we are to threshold
        print(f"Resonances: {resonances}")
        print(f"Near threshold (0.8-0.9): {near_threshold}")


class TestCryptoAlignmentWeakness:
    """
    Prove that the crypto alignment is cosmetic, not cryptographic.
    """

    def test_crypto_is_just_hashing(self):
        """
        The 'crypto alignment' is just SHA256 normalization.

        It doesn't verify signatures, prove identity, or enforce
        any actual cryptographic guarantee.
        """
        tensor1 = encode_intent("test", "salt1")
        tensor2 = encode_intent("test", "salt2")

        # Different salts = different entropy values
        assert tensor1.entropy != tensor2.entropy

        # But this proves nothing about authorization
        # An attacker can use any salt they want
        # There's no signature verification

    def test_context_hash_is_trusted(self):
        """
        RED TEST: The context_hash is blindly trusted.

        If an attacker provides a fake context_hash, the
        crypto alignment will be computed against that fake.
        """
        engine = AgniEngine()

        # Legitimate context
        tensor = encode_intent("dangerous_operation", "salt")
        result_legit = engine.check_resonance(tensor, "real_ledger_hash_abc123")

        # Attacker-provided context (completely fake)
        result_fake = engine.check_resonance(tensor, "attacker_controlled_hash")

        # Both work - the system doesn't verify the context_hash is real
        # This is NOT cryptographic security
        assert result_legit.crypto_alignment != result_fake.crypto_alignment, (
            "Different contexts should give different alignments"
        )
        # But NEITHER is verified as authentic


class TestFundamentalDesignFlaws:
    """
    The deepest problems with the approach.
    """

    def test_still_boolean_at_the_end(self):
        """
        "Breaking the binary" is marketing.

        At the end, it's still: if resonance >= threshold: allow()
        That's a boolean decision.
        """
        engine = AgniEngine()
        tensor = encode_intent("test_operation", "salt")
        result = engine.check_resonance(tensor, "ctx")

        # The status is one of three strings
        assert result.status in ["SIDDHI", "TAPAS", "DHUMRA"]

        # Which maps to: allow, maybe, deny
        # That's just boolean with an extra state
        # It's NOT continuous computation

    def test_not_integrated_with_kernel(self):
        """
        The reactor is standalone - it doesn't enforce anything.

        You have to manually call it. The kernel doesn't require it.
        """
        # This test just documents the architectural flaw:
        # The reactor is an optional library, not a kernel enforcement mechanism
        #
        # To be real security, it would need to be:
        # 1. Mandatory for all kernel operations
        # 2. Impossible to bypass
        # 3. Enforced at the syscall level (metaphorically)
        #
        # Currently it's just a function you can choose to call or not
        pass


# =============================================================================
# Summary: What This Proves
# =============================================================================
#
# 1. ALIASING: Attackers can use synonyms to bypass keyword detection
# 2. MISCLASSIFICATION: Same operation, different words = different Varga
# 3. DRIFT: Field learning can be exploited over time
# 4. THRESHOLDS: Magic numbers, not principled security
# 5. CRYPTO: Cosmetic hashing, not real cryptography
# 6. BOOLEAN: Still if/else at the end, despite "breaking the binary"
# 7. STANDALONE: Not integrated into kernel, easily bypassed
#
# VERDICT: This is not watertight. It's poetry pretending to be security.
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
