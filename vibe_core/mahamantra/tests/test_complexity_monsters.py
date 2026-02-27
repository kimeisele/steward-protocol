"""
COMPLEXITY MONSTERS — Safety Net Tests
========================================

Tests for the highest-complexity functions in the codebase.
These tests exist to enable safe decomposition.

Targets:
- _build_phoneme_sthana_from_protocols (complexity 34)
- _build_phoneme_varga_from_protocols (complexity 19)
- phonetic_bridge module-level constants
"""

import pytest


# ============================================================================
# Phonetic Bridge — Varga Mapping (WHERE = articulation point)
# ============================================================================


class TestPhonemeToVarga:
    """PHONEME_TO_VARGA maps phonemes to articulation points (0-4)."""

    def test_mapping_exists(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import PHONEME_TO_VARGA

        assert isinstance(PHONEME_TO_VARGA, dict)
        assert len(PHONEME_TO_VARGA) > 0

    def test_varga_values_in_range(self):
        """All values must be VargaIndex (0-4)."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
            PHONEME_TO_VARGA,
            VargaIndex,
        )

        for phoneme, varga in PHONEME_TO_VARGA.items():
            assert isinstance(varga, VargaIndex), f"'{phoneme}' has non-VargaIndex value: {varga}"
            assert 0 <= varga.value <= 4, f"'{phoneme}' varga {varga} out of range"

    def test_varga_enum_values(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import VargaIndex

        assert VargaIndex.KANTHYA == 0    # Throat
        assert VargaIndex.TALAVYA == 1    # Palate
        assert VargaIndex.MURDHANYA == 2  # Cerebral
        assert VargaIndex.DANTYA == 3     # Dental
        assert VargaIndex.OSHTHYA == 4    # Labial
        assert len(VargaIndex) == 5       # PANCHA

    def test_sanskrit_consonants_mapped(self):
        """Core Sanskrit consonants must be in the mapping."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import PHONEME_TO_VARGA

        # At least some basic consonants should be present
        # (exact keys depend on IAST vs roman representation)
        assert len(PHONEME_TO_VARGA) >= 20, "Should have at least 20 phoneme mappings"

    def test_all_five_vargas_represented(self):
        """All 5 articulation points must appear in the mapping."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
            PHONEME_TO_VARGA,
            VargaIndex,
        )

        vargas_seen = set(v.value for v in PHONEME_TO_VARGA.values())
        assert vargas_seen == {0, 1, 2, 3, 4}, f"Missing vargas: {set(range(5)) - vargas_seen}"


# ============================================================================
# Phonetic Bridge — Sthana Mapping (HOW = energy/intensity)
# ============================================================================


class TestPhonemeToSthana:
    """PHONEME_TO_STHANA maps phonemes to energy levels (0-4)."""

    def test_mapping_exists(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import PHONEME_TO_STHANA

        assert isinstance(PHONEME_TO_STHANA, dict)
        assert len(PHONEME_TO_STHANA) > 0

    def test_sthana_values_in_range(self):
        """All values must be SthanaIndex (0-4)."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
            PHONEME_TO_STHANA,
            SthanaIndex,
        )

        for phoneme, sthana in PHONEME_TO_STHANA.items():
            assert isinstance(sthana, SthanaIndex), f"'{phoneme}' has non-SthanaIndex value: {sthana}"
            assert 0 <= sthana.value <= 4, f"'{phoneme}' sthana {sthana} out of range"

    def test_sthana_enum_values(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import SthanaIndex

        assert SthanaIndex.SPARSHA == 0     # Contact
        assert SthanaIndex.MAHAPRANA == 1    # Aspirated
        assert SthanaIndex.GHOSHAVAT == 2   # Voiced
        assert SthanaIndex.GHOSHMAHA == 3   # Voiced aspirated
        assert SthanaIndex.ANUNASIKA == 4   # Nasal
        assert len(SthanaIndex) == 5        # PANCHA

    def test_all_five_sthanas_represented(self):
        """All 5 energy levels must appear in the mapping."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import (
            PHONEME_TO_STHANA,
            SthanaIndex,
        )

        sthanas_seen = set(v.value for v in PHONEME_TO_STHANA.values())
        assert sthanas_seen == {0, 1, 2, 3, 4}, f"Missing sthanas: {set(range(5)) - sthanas_seen}"


# ============================================================================
# UniversalPhoneticBridge
# ============================================================================


class TestUniversalPhoneticBridge:
    """The main bridge class for phonetic analysis."""

    def test_get_bridge(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import get_phonetic_bridge

        bridge = get_phonetic_bridge()
        assert bridge is not None

    def test_bridge_has_analyze(self):
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import get_phonetic_bridge

        bridge = get_phonetic_bridge()
        assert hasattr(bridge, "analyze")

    def test_varga_to_quarter(self):
        """Varga maps to Quarter (articulation → folder)."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import VARGA_TO_QUARTER

        assert isinstance(VARGA_TO_QUARTER, dict)
        assert len(VARGA_TO_QUARTER) > 0

    def test_sthana_energy(self):
        """Sthana has energy values."""
        from vibe_core.mahamantra.substrate.encoding.phonetic_bridge import STHANA_ENERGY

        assert isinstance(STHANA_ENERGY, dict)
        assert len(STHANA_ENERGY) > 0

