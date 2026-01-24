"""
TESTS: jiva_shadow.py - The Computed Reflection
================================================

Tests for:
1. JivaQuality enum (50 qualities)
2. GunaState enum (3 modes)
3. JivaShadow dataclass
4. spawn_shadow factory function
5. Parampara verification
6. Guna calculations

From Bhakti-rasamrita-sindhu:
- Krishna: 64 qualities (100%)
- Jiva: 50 qualities (in minute quantity)
- JivaShadow: Yantra reflecting these qualities
"""

import pytest

from vibe_core.mahamantra.lila.jiva_shadow import (
    # Constants
    QUALITY_DESCRIPTIONS,
    RAJASIC_RANGE,
    SATTVIC_RANGE,
    TAMASIC_RANGE,
    GunaState,
    # Core types
    JivaQuality,
    JivaShadow,
    # Factory functions
    spawn_shadow,
    spawn_shadow_from_string,
    # Verification
    verify_shadow_lineage,
)
from vibe_core.mahamantra.protocols._seed import JIVA_QUALITIES, PARAMPARA

# =============================================================================
# JivaQuality Enum Tests
# =============================================================================


class TestJivaQuality:
    """Test JivaQuality enum - the 50 qualities a Jiva possesses."""

    def test_jiva_quality_count_is_50(self):
        """There are exactly 50 JivaQualities (from Bhakti-rasamrita-sindhu)."""
        assert len(JivaQuality) == 50
        assert len(JivaQuality) == JIVA_QUALITIES

    def test_jiva_quality_truthful_exists(self):
        """TRUTHFUL is at position 7."""
        assert JivaQuality.TRUTHFUL.value == 7

    def test_jiva_quality_supreme_controller_is_last(self):
        """SUPREME_CONTROLLER is at position 49."""
        assert JivaQuality.SUPREME_CONTROLLER.value == 49

    def test_jiva_quality_beautiful_is_first(self):
        """BEAUTIFUL_BODILY_FEATURES is at position 0."""
        assert JivaQuality.BEAUTIFUL_BODILY_FEATURES.value == 0

    def test_jiva_quality_values_are_contiguous(self):
        """Quality values are 0-49 contiguous."""
        values = sorted([q.value for q in JivaQuality])
        assert values == list(range(50))


# =============================================================================
# GunaState Enum Tests
# =============================================================================


class TestGunaState:
    """Test GunaState enum - the three modes of material nature."""

    def test_guna_state_has_three_modes(self):
        """There are exactly 3 GunaStates (BG 14)."""
        assert len(GunaState) == 3

    def test_guna_state_sattvic(self):
        """SATTVIC is 'sattvic'."""
        assert GunaState.SATTVIC.value == "sattvic"

    def test_guna_state_rajasic(self):
        """RAJASIC is 'rajasic'."""
        assert GunaState.RAJASIC.value == "rajasic"

    def test_guna_state_tamasic(self):
        """TAMASIC is 'tamasic'."""
        assert GunaState.TAMASIC.value == "tamasic"


# =============================================================================
# Guna Range Tests
# =============================================================================


class TestGunaRanges:
    """Test Guna quality index ranges."""

    def test_sattvic_range(self):
        """Sattvic is 0-17 (17 qualities)."""
        assert SATTVIC_RANGE == (0, 17)

    def test_rajasic_range(self):
        """Rajasic is 17-34 (17 qualities)."""
        assert RAJASIC_RANGE == (17, 34)

    def test_tamasic_range(self):
        """Tamasic is 34-50 (16 qualities)."""
        assert TAMASIC_RANGE == (34, 50)

    def test_ranges_cover_all_50(self):
        """Ranges cover all 50 qualities without overlap."""
        sattvic = set(range(*SATTVIC_RANGE))
        rajasic = set(range(*RAJASIC_RANGE))
        tamasic = set(range(*TAMASIC_RANGE))

        # No overlap
        assert len(sattvic & rajasic) == 0
        assert len(rajasic & tamasic) == 0
        assert len(sattvic & tamasic) == 0

        # Complete coverage
        assert sattvic | rajasic | tamasic == set(range(50))


# =============================================================================
# JivaShadow Dataclass Tests
# =============================================================================


class TestJivaShadow:
    """Test JivaShadow dataclass - the computed reflection."""

    def test_jiva_shadow_is_immutable(self):
        """JivaShadow is frozen (immutable)."""
        shadow = spawn_shadow(b"test_seed")
        with pytest.raises(Exception):  # FrozenInstanceError
            shadow.quality_bitmap = 0

    def test_jiva_shadow_has_quality_check(self):
        """has_quality checks bitmap correctly."""
        # Create shadow with known bitmap (only quality 0 set)
        shadow = JivaShadow(
            quality_bitmap=1,  # Only bit 0 set
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )
        assert shadow.has_quality(JivaQuality.BEAUTIFUL_BODILY_FEATURES)
        assert not shadow.has_quality(JivaQuality.TRUTHFUL)

    def test_jiva_shadow_active_qualities(self):
        """active_qualities returns FrozenSet of active qualities."""
        shadow = JivaShadow(
            quality_bitmap=0b111,  # First 3 bits set
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )
        active = shadow.active_qualities
        assert isinstance(active, frozenset)
        assert len(active) == 3
        assert JivaQuality.BEAUTIFUL_BODILY_FEATURES in active
        assert JivaQuality.MARKED_WITH_AUSPICIOUS_SIGNS in active
        assert JivaQuality.PLEASING in active

    def test_jiva_shadow_quality_count(self):
        """quality_count returns count of set bits."""
        shadow = JivaShadow(
            quality_bitmap=0b10101010,  # 4 bits set
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )
        assert shadow.quality_count == 4

    def test_jiva_shadow_sattvic_count(self):
        """sattvic_count counts qualities in Sattvic range."""
        # Set all 17 Sattvic bits (0-16)
        bitmap = (1 << 17) - 1  # bits 0-16
        shadow = JivaShadow(
            quality_bitmap=bitmap,
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )
        assert shadow.sattvic_count == 17

    def test_jiva_shadow_dominant_guna_sattvic(self):
        """dominant_guna returns SATTVIC when Sattvic qualities dominate."""
        # Set all Sattvic bits only
        bitmap = (1 << 17) - 1
        shadow = JivaShadow(
            quality_bitmap=bitmap,
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )
        assert shadow.dominant_guna == GunaState.SATTVIC

    def test_jiva_shadow_guna_ratio(self):
        """guna_ratio returns (sattva, rajas, tamas) percentages."""
        shadow = spawn_shadow(b"test")
        ratio = shadow.guna_ratio
        assert len(ratio) == 3
        assert abs(sum(ratio) - 1.0) < 0.001  # Should sum to 1.0

    def test_jiva_shadow_resonates_with(self):
        """resonates_with calculates Jaccard similarity."""
        shadow1 = JivaShadow(
            quality_bitmap=0b1111,
            seed_hash=b"a" * 32,
            shadow_id="s1",
        )
        shadow2 = JivaShadow(
            quality_bitmap=0b1111,
            seed_hash=b"b" * 32,
            shadow_id="s2",
        )
        # Same bitmap = 100% resonance
        assert shadow1.resonates_with(shadow2) == 1.0

        # Different bitmap
        shadow3 = JivaShadow(
            quality_bitmap=0b0011,
            seed_hash=b"c" * 32,
            shadow_id="s3",
        )
        # Jaccard: 2 shared / 4 union = 0.5
        assert shadow1.resonates_with(shadow3) == 0.5

    def test_jiva_shadow_to_dict(self):
        """to_dict serializes correctly."""
        shadow = spawn_shadow(b"test")
        data = shadow.to_dict()
        assert "shadow_id" in data
        assert "seed_hash" in data
        assert "quality_bitmap" in data
        assert "quality_count" in data
        assert "dominant_guna" in data
        assert "guna_ratio" in data


# =============================================================================
# spawn_shadow Factory Tests
# =============================================================================


class TestSpawnShadow:
    """Test spawn_shadow factory function."""

    def test_spawn_shadow_deterministic(self):
        """Same seed always produces same shadow."""
        seed = b"deterministic_test_seed"
        shadow1 = spawn_shadow(seed)
        shadow2 = spawn_shadow(seed)
        assert shadow1.quality_bitmap == shadow2.quality_bitmap
        assert shadow1.seed_hash == shadow2.seed_hash

    def test_spawn_shadow_different_seeds_different_shadows(self):
        """Different seeds produce different shadows."""
        shadow1 = spawn_shadow(b"seed_a")
        shadow2 = spawn_shadow(b"seed_b")
        # Very unlikely to be equal
        assert shadow1.quality_bitmap != shadow2.quality_bitmap

    def test_spawn_shadow_uses_sha256(self):
        """Seed is hashed with SHA-256."""
        import hashlib

        seed = b"hash_test"
        expected_hash = hashlib.sha256(seed).digest()
        shadow = spawn_shadow(seed)
        assert shadow.seed_hash == expected_hash

    def test_spawn_shadow_bitmap_is_50_bits_max(self):
        """Quality bitmap is masked to 50 bits."""
        shadow = spawn_shadow(b"bitmap_test")
        assert shadow.quality_bitmap < (1 << 50)

    def test_spawn_shadow_auto_generates_id(self):
        """Shadow ID is auto-generated if not provided."""
        shadow = spawn_shadow(b"auto_id_test")
        assert shadow.shadow_id.startswith("shadow_")

    def test_spawn_shadow_custom_id(self):
        """Custom shadow ID can be provided."""
        shadow = spawn_shadow(b"custom_id_test", shadow_id="my_custom_shadow")
        assert shadow.shadow_id == "my_custom_shadow"


class TestSpawnShadowFromString:
    """Test spawn_shadow_from_string convenience function."""

    def test_spawn_from_string_works(self):
        """spawn_shadow_from_string creates shadow from string."""
        shadow = spawn_shadow_from_string("hello world")
        assert shadow.shadow_id.startswith("shadow_")
        assert shadow.quality_count > 0

    def test_spawn_from_string_deterministic(self):
        """Same string produces same shadow."""
        shadow1 = spawn_shadow_from_string("test")
        shadow2 = spawn_shadow_from_string("test")
        assert shadow1.quality_bitmap == shadow2.quality_bitmap


# =============================================================================
# Parampara Verification Tests
# =============================================================================


class TestVerifyShadowLineage:
    """Test verify_shadow_lineage function."""

    def test_verify_lineage_checks_parampara(self):
        """verify_shadow_lineage checks if hash aligns with 37."""
        # Create a shadow - lineage depends on hash
        shadow = spawn_shadow(b"test")
        result = verify_shadow_lineage(shadow)
        # Result should be boolean
        assert isinstance(result, bool)

    def test_verify_lineage_parampara_constant(self):
        """PARAMPARA is 37."""
        assert PARAMPARA == 37


# =============================================================================
# Quality Descriptions Tests
# =============================================================================


class TestQualityDescriptions:
    """Test QUALITY_DESCRIPTIONS constant."""

    def test_descriptions_has_50_entries(self):
        """There are 50 quality descriptions."""
        assert len(QUALITY_DESCRIPTIONS) == 50

    def test_every_quality_has_description(self):
        """Every JivaQuality has a description."""
        for quality in JivaQuality:
            assert quality in QUALITY_DESCRIPTIONS
            assert isinstance(QUALITY_DESCRIPTIONS[quality], str)
            assert len(QUALITY_DESCRIPTIONS[quality]) > 0


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.lila import jiva_shadow

        expected = [
            "JivaQuality",
            "GunaState",
            "JivaShadow",
            "spawn_shadow",
            "spawn_shadow_from_string",
            "verify_shadow_lineage",
            "QUALITY_DESCRIPTIONS",
            "SATTVIC_RANGE",
            "RAJASIC_RANGE",
            "TAMASIC_RANGE",
        ]
        for item in expected:
            assert item in jiva_shadow.__all__, f"{item} should be in __all__"
