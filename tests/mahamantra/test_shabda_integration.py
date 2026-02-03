"""
Test Shabda/Phoneme Integration in mahamantra()
================================================

Verifies that phoneme and vibration extraction works in production.
"""

import pytest

from vibe_core.mahamantra import mahamantra


def test_mahamantra_includes_phoneme():
    """mahamantra() response includes phoneme from RAMA grid."""
    result = mahamantra("test")

    assert "vibration" in result
    assert "phoneme" in result["vibration"]
    assert "rama_index" in result["vibration"]

    # Phoneme should be a string
    phoneme = result["vibration"]["phoneme"]
    assert isinstance(phoneme, str)
    assert len(phoneme) > 0


def test_shabda_signature_structure():
    """Vibration signature has correct structure."""
    result = mahamantra("analyze")

    sig = result["vibration"]["signature"]
    assert "varga" in sig
    assert "sthana" in sig
    assert "frequency" in sig


def test_rama_index_range():
    """RAMA index is in valid range [0-48]."""
    result = mahamantra("test")

    rama_idx = result["vibration"]["rama_index"]
    assert isinstance(rama_idx, int)
    assert 0 <= rama_idx < 49  # RAMA grid is 0-48


def test_phoneme_varies_by_position():
    """Different positions produce different phonemes."""
    results = [mahamantra(f"test{i}") for i in range(5)]
    phonemes = [r["vibration"]["phoneme"] for r in results]

    # At least some should be different (not all same)
    assert len(set(phonemes)) > 1
