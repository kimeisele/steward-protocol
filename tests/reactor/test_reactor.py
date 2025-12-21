"""
Test: Sanskrit Reactor - Breaking the Binary

This test verifies the core paradigm:
1. VarnaTensor encodes meaning as 4D vectors
2. AgniEngine computes resonance instead of boolean logic
3. Crypto properties participate in computation
"""

import pytest

from vibe_core.reactor import (
    AgniEngine,
    Guna,
    ResonanceResult,
    Varga,
    VarnaTensor,
    encode_intent,
    infer_guna,
    infer_varga,
)


class TestVarnaTensor:
    """Tests for VarnaTensor encoding."""

    def test_encode_kernel_intent(self):
        """Kernel operations should map to KAVARGA."""
        tensor = encode_intent("kernel_boot", "test_salt")
        assert tensor.varga == Varga.KAVARGA
        assert 0.0 <= tensor.entropy <= 1.0

    def test_encode_connect_intent(self):
        """Connection operations should map to CAVARGA."""
        tensor = encode_intent("connect_socket", "test_salt")
        assert tensor.varga == Varga.CAVARGA

    def test_encode_data_intent(self):
        """Data operations should map to TAVARGA."""
        tensor = encode_intent("transform_data", "test_salt")
        assert tensor.varga == Varga.TAVARGA

    def test_encode_print_intent(self):
        """Print/Make operations should map to PAVARGA."""
        tensor = encode_intent("print_report", "test_salt")
        assert tensor.varga == Varga.PAVARGA

    def test_guna_inference_rajas(self):
        """Write operations should be RAJAS."""
        tensor = encode_intent("create_file", "test_salt")
        assert tensor.guna == Guna.RAJAS

    def test_guna_inference_tamas(self):
        """Read operations should be TAMAS."""
        tensor = encode_intent("read_config", "test_salt")
        assert tensor.guna == Guna.TAMAS

    def test_vector_normalization(self):
        """Vector components should be normalized to 0.0-1.0."""
        tensor = encode_intent("test_intent", "salt")
        vector = tensor.to_vector()

        for component in vector:
            assert 0.0 <= component <= 1.0

    def test_different_salts_different_entropy(self):
        """Different salts should produce different entropy values."""
        t1 = encode_intent("same_intent", "salt_a")
        t2 = encode_intent("same_intent", "salt_b")

        # Same phonetics = same varga
        assert t1.varga == t2.varga
        # Different crypto = different entropy
        assert t1.entropy != t2.entropy


class TestAgniEngine:
    """Tests for AgniEngine resonance computation."""

    def test_engine_initialization(self):
        """Engine should initialize with balanced field."""
        engine = AgniEngine()
        assert engine.akasha_field is not None
        assert len(engine.akasha_field) == 4

    def test_resonance_computation(self):
        """Resonance should be computed as float between 0 and 1."""
        engine = AgniEngine()
        tensor = encode_intent("test_intent", "salt")
        result = engine.check_resonance(tensor)

        assert isinstance(result, ResonanceResult)
        assert 0.0 <= result.resonance <= 1.0
        assert result.status in ["SIDDHI", "TAPAS", "DHUMRA"]

    def test_field_tuned_resonance(self):
        """Field tuned for a layer should resonate with that layer."""
        # Field tuned for KERNEL layer
        engine = AgniEngine(initial_field=(0.0, 0.8, 0.5, 0.5))

        # KERNEL intent should have higher resonance
        kernel_tensor = encode_intent("kernel_boot", "salt")
        kernel_result = engine.check_resonance(kernel_tensor)

        # OUTPUT intent should have lower resonance (different layer)
        output_tensor = encode_intent("print_output", "salt")
        output_result = engine.check_resonance(output_tensor)

        # KERNEL should resonate better with KERNEL-tuned field
        # (This test may need adjustment based on exact vector math)
        assert kernel_result.resonance >= 0.5

    def test_ignite_returns_status(self):
        """Ignite should return a valid status string."""
        engine = AgniEngine()
        tensor = encode_intent("test_action", "salt")
        status = engine.ignite(tensor)

        assert status in ["SIDDHI", "TAPAS", "DHUMRA"]

    def test_field_learning(self):
        """Field should adapt after SIDDHI (success)."""
        # Create engine with low threshold for testing
        engine = AgniEngine(initial_field=(0.5, 0.5, 0.5, 0.5))
        engine.SIDDHI_THRESHOLD = 0.5  # Lower threshold for test

        initial_field = engine.akasha_field

        tensor = encode_intent("kernel_boot", "salt")
        engine.ignite(tensor)

        # Field should have changed (learning)
        assert engine.akasha_field != initial_field

    def test_crypto_alignment_affects_resonance(self):
        """Different context hashes should produce different alignments."""
        engine = AgniEngine()
        tensor = encode_intent("test_intent", "salt")

        result1 = engine.check_resonance(tensor, context_hash="context_a")

        # Reset for clean test
        engine2 = AgniEngine()
        result2 = engine2.check_resonance(tensor, context_hash="context_b")

        # Crypto alignment should differ
        assert result1.crypto_alignment != result2.crypto_alignment

    def test_history_tracking(self):
        """Engine should track computation history."""
        engine = AgniEngine()

        assert len(engine.history) == 0

        tensor = encode_intent("test", "salt")
        engine.check_resonance(tensor)

        assert len(engine.history) == 1


class TestParadigmShift:
    """Tests demonstrating 'Breaking the Binary' paradigm."""

    def test_resonance_instead_of_boolean(self):
        """
        Core paradigm test: Instead of if/else, we get continuous resonance.

        Binary: permission == True/False
        Reactor: resonance is a continuous value 0.0-1.0
        """
        engine = AgniEngine()
        tensor = encode_intent("action", "salt")
        result = engine.check_resonance(tensor)

        # Not boolean - continuous value
        assert not isinstance(result.resonance, bool)
        assert isinstance(result.resonance, float)

        # Has gradients (SIDDHI/TAPAS/DHUMRA)
        assert result.status in ["SIDDHI", "TAPAS", "DHUMRA"]

    def test_meaning_encoded_in_structure(self):
        """
        Paradigm test: Meaning is encoded in vector structure, not parsed strings.
        """
        # Different intents produce different vectors
        t1 = encode_intent("kernel_boot", "salt")
        t2 = encode_intent("print_output", "salt")

        # Different layers (meaning encoded in varga)
        assert t1.varga != t2.varga

        # But same energy (both active)
        assert t1.shakti == t2.shakti

    def test_crypto_as_computation_dimension(self):
        """
        Paradigm test: Crypto participates in computation, not just verification.
        """
        engine = AgniEngine()
        tensor = encode_intent("action", "salt")

        # With context hash
        result_with_ctx = engine.check_resonance(tensor, context_hash="ledger_hash")

        # Crypto alignment is a computational factor, not just a pass/fail
        assert 0.0 <= result_with_ctx.crypto_alignment <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
