"""
OPUS-200/201: Sanskrit Quantum Reactor - Paradigm Tests

These tests verify that the phonetic-based reactor works correctly.
NOT keyword matching - PHONETIC PHYSICS.

Run with: pytest tests/reactor/test_fragility.py -v
"""

import pytest

from vibe_core.reactor import (
    QuantumReactor,
    Sthana,
    Varga,
    VarnaTensor,
    compress_to_akshara,
    compute_resonance,
    encode,
)


class TestPhoneticPhysics:
    """
    Test that phonemes map to correct articulation points.

    This is PHYSICS - where the sound originates in the mouth.
    """

    def test_guttural_k_maps_to_kanthya(self):
        """'k' is guttural (throat) → KANTHYA."""
        tensor = encode("kernel", "")
        # k should contribute to KANTHYA (index 0)
        assert tensor.varga_vector[Varga.KANTHYA] > 0, "k should map to KANTHYA"

    def test_palatal_c_maps_to_talavya(self):
        """'c' is palatal → TALAVYA."""
        tensor = encode("connect", "")
        # c should contribute to TALAVYA (index 1)
        assert tensor.varga_vector[Varga.TALAVYA] > 0, "c should map to TALAVYA"

    def test_retroflex_t_maps_to_murdhanya(self):
        """'t' is retroflex/cerebral → MURDHANYA."""
        tensor = encode("transform", "")
        assert tensor.varga_vector[Varga.MURDHANYA] > 0, "t should map to MURDHANYA"

    def test_labial_p_maps_to_oshthya(self):
        """'p' is labial (lips) → OSHTHYA."""
        tensor = encode("print", "")
        assert tensor.varga_vector[Varga.OSHTHYA] > 0, "p should map to OSHTHYA"

    def test_dominant_varga_reflects_first_consonant(self):
        """Dominant varga should reflect the phonetic content."""
        # 'kernel' is k-heavy
        tensor = encode("kernel", "")
        dominant = max(range(5), key=lambda i: tensor.varga_vector[i])
        # Should be KANTHYA (0) due to k and g
        assert dominant == Varga.KANTHYA, f"Expected KANTHYA, got {Varga(dominant).name}"


class TestCryptoAsMass:
    """
    Test that crypto hash acts as MASS, not verification.

    Same text + different salt = different entropy = different mass.
    """

    def test_different_salt_different_entropy(self):
        """Same text with different salt produces different entropy."""
        t1 = encode("boot", "session_alpha")
        t2 = encode("boot", "session_beta")

        # Entropy should be different
        assert t1.entropy != t2.entropy, "Different salt should produce different entropy"

    def test_entropy_is_continuous(self):
        """Entropy is a continuous value, not binary."""
        tensor = encode("test", "salt")
        assert 0.0 <= tensor.entropy <= 1.0, "Entropy should be normalized 0-1"

    def test_mass_influences_resonance(self):
        """Crypto mass should influence resonance calculation."""
        reactor = QuantumReactor()

        t1 = encode("boot", "salt_a")
        t2 = encode("boot", "salt_b")

        field = reactor.resonate(t1, t2)

        # Mass resonance should be computed
        assert field.mass_resonance > 0, "Mass should influence resonance"


class TestContinuousResonance:
    """
    Test that resonance is CONTINUOUS, not boolean.
    """

    def test_identical_texts_high_resonance(self):
        """Identical texts should have high resonance."""
        energy = compute_resonance("kernel", "kernel")
        assert energy > 0.5, f"Identical texts should resonate highly, got {energy}"

    def test_similar_phonetics_medium_resonance(self):
        """Similar phonetic structure should have medium resonance."""
        energy = compute_resonance("kernel", "kernal")  # Typo but similar
        assert 0.3 < energy < 0.8, f"Similar phonetics should have medium resonance, got {energy}"

    def test_different_varga_lower_resonance(self):
        """Different varga (articulation point) should have lower resonance."""
        # k (KANTHYA) vs c (TALAVYA) - different articulation points
        energy = compute_resonance("kernel", "connect")
        assert energy < 0.5, f"Different varga should have lower resonance, got {energy}"

    def test_resonance_is_gradient(self):
        """Resonance should form a gradient, not discrete steps."""
        e1 = compute_resonance("kernel", "kernel")
        e2 = compute_resonance("kernel", "kernal")
        e3 = compute_resonance("kernel", "connect")
        e4 = compute_resonance("kernel", "print")

        # Should be descending (more different = less resonance)
        assert e1 >= e2 >= e3, "Resonance should form a gradient"


class TestManifestation:
    """
    Test the manifestation model (energy overcomes inertia).
    """

    def test_high_energy_manifests(self):
        """High energy should overcome inertia."""
        reactor = QuantumReactor(initial_inertia=0.1)  # Low inertia

        field = reactor.manifest("kernel_boot", salt="test")

        # With low inertia, should manifest
        assert field.total_energy > reactor._inertia, "High energy should manifest"

    def test_low_energy_pending(self):
        """Low energy should remain pending."""
        reactor = QuantumReactor(initial_inertia=0.9)  # High inertia

        field = reactor.manifest("x", salt="test")  # Short, low energy

        # With high inertia, should remain pending
        assert field.total_energy < reactor._inertia, "Low energy should remain pending"

    def test_manifestation_updates_akasha(self):
        """Successful manifestation should update the field."""
        reactor = QuantumReactor(initial_inertia=0.1)

        initial_akasha = reactor.akasha
        reactor.manifest("kernel_boot", salt="test")
        final_akasha = reactor.akasha

        # Akasha should change after manifestation
        # (The source changes from "om" to "akasha")
        assert final_akasha.source == "akasha" or final_akasha != initial_akasha


class TestCompression:
    """
    Test that tensors can be compressed to Sanskrit aksharas.
    """

    def test_compression_produces_devanagari(self):
        """Compression should produce a Devanagari character."""
        tensor = encode("kernel", "")
        akshara = compress_to_akshara(tensor)

        # Should be a Devanagari consonant
        assert akshara in "कखगघङचछजझञटठडढणतथदधनपफबभम", f"Expected Devanagari, got {akshara}"

    def test_different_varga_different_akshara(self):
        """Different varga should produce different akshara."""
        t1 = encode("kernel", "")  # k-heavy (KANTHYA)
        t2 = encode("print", "")  # p-heavy (OSHTHYA)

        a1 = compress_to_akshara(t1)
        a2 = compress_to_akshara(t2)

        # Different varga should produce different rows of the matrix
        # KANTHYA = क-row, OSHTHYA = प-row
        assert a1 != a2, f"Different varga should produce different akshara: {a1} vs {a2}"


class TestNoBoolean:
    """
    Meta-tests: verify the paradigm shift (no boolean at core).
    """

    def test_resonance_field_has_no_boolean(self):
        """ResonanceField should not contain boolean status."""
        reactor = QuantumReactor()
        tensor = encode("test", "")
        field = reactor.resonate(tensor)

        # Check that all values are continuous
        assert isinstance(field.phonetic_resonance, float)
        assert isinstance(field.mass_resonance, float)
        assert isinstance(field.total_energy, float)

        # No 'status', 'allowed', 'denied' attributes
        assert not hasattr(field, "status")
        assert not hasattr(field, "allowed")
        assert not hasattr(field, "denied")

    def test_varna_tensor_is_multidimensional(self):
        """VarnaTensor should be truly multi-dimensional."""
        tensor = encode("kernel", "")

        # Should have 5D varga vector
        assert len(tensor.varga_vector) == 5

        # Should have 5D sthana vector
        assert len(tensor.sthana_vector) == 5

        # Flat vector should be 12D
        flat = tensor.to_flat_vector()
        assert len(flat) == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
