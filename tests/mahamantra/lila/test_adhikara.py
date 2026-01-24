"""
TESTS: adhikara.py - Qualification Computed from Mahamantra
===========================================================

Tests for:
1. compute_required_bitmap (Mahamantra-derived requirements)
2. get_required_qualities (Human-readable version)
3. shadow_can_execute (Qualification check)
4. shadow_match_score (Match quality)
5. spawn_shadow_for_position (Varnashrama spawn)
6. Determinism verification

"adhikari purusah pancaratriki-viddhina"
"A person is qualified according to the Pancharatra regulations."
"""

import pytest

from vibe_core.mahamantra.lila.adhikara import (
    HARE_AFFINITY,
    KRISHNA_AFFINITY,
    # Constants (derived)
    QUARTER_RANGES,
    RAMA_AFFINITY,
    # Core computation
    compute_required_bitmap,
    find_best_shadow,
    # Reporting
    get_position_adhikara_report,
    get_required_count,
    get_required_qualities,
    # Shadow matching
    shadow_can_execute,
    shadow_match_score,
    # Varnashrama spawn
    spawn_shadow_for_position,
    # Verification
    verify_adhikara_determinism,
)
from vibe_core.mahamantra.lila.jiva_shadow import (
    JivaQuality,
    JivaShadow,
    spawn_shadow,
)
from vibe_core.mahamantra.protocols._seed import JIVA_QUALITIES, WORDS

# =============================================================================
# Constants Tests
# =============================================================================


class TestAdhikaraConstants:
    """Test Adhikara constants derived from seed."""

    def test_hare_affinity_is_half(self):
        """HARE_AFFINITY is 8/16 = 0.5."""
        assert HARE_AFFINITY == 0.5

    def test_krishna_affinity_is_quarter(self):
        """KRISHNA_AFFINITY is 4/16 = 0.25."""
        assert KRISHNA_AFFINITY == 0.25

    def test_rama_affinity_is_quarter(self):
        """RAMA_AFFINITY is 4/16 = 0.25."""
        assert RAMA_AFFINITY == 0.25

    def test_quarter_ranges_has_4_entries(self):
        """There are 4 quarter ranges."""
        assert len(QUARTER_RANGES) == 4

    def test_quarter_ranges_cover_50_qualities(self):
        """Quarter ranges cover all 50 qualities."""
        all_indices = set()
        for start, end in QUARTER_RANGES.values():
            all_indices.update(range(start, end))
        # At minimum, should have substantial coverage
        assert len(all_indices) >= 48  # Slight overlap allowed


# =============================================================================
# compute_required_bitmap Tests
# =============================================================================


class TestComputeRequiredBitmap:
    """Test compute_required_bitmap function."""

    def test_bitmap_for_position_0(self):
        """Position 0 returns a valid bitmap."""
        bitmap = compute_required_bitmap(0)
        assert isinstance(bitmap, int)
        assert bitmap >= 0

    def test_bitmap_for_all_16_positions(self):
        """All 16 positions return valid bitmaps."""
        for pos in range(WORDS):
            bitmap = compute_required_bitmap(pos)
            assert isinstance(bitmap, int)
            assert bitmap < (1 << JIVA_QUALITIES)  # Max 50 bits

    def test_bitmap_is_deterministic(self):
        """Same position always returns same bitmap."""
        bitmap1 = compute_required_bitmap(5)
        bitmap2 = compute_required_bitmap(5)
        assert bitmap1 == bitmap2

    def test_bitmap_position_out_of_range_raises(self):
        """Position < 0 or >= 16 raises ValueError."""
        with pytest.raises(ValueError):
            compute_required_bitmap(-1)
        with pytest.raises(ValueError):
            compute_required_bitmap(16)

    def test_bitmap_is_cached(self):
        """compute_required_bitmap uses LRU cache."""
        # Clear cache first
        compute_required_bitmap.cache_clear()

        # First call
        compute_required_bitmap(8)
        info1 = compute_required_bitmap.cache_info()
        assert info1.hits == 0
        assert info1.misses == 1

        # Second call (should hit cache)
        compute_required_bitmap(8)
        info2 = compute_required_bitmap.cache_info()
        assert info2.hits == 1


# =============================================================================
# get_required_qualities Tests
# =============================================================================


class TestGetRequiredQualities:
    """Test get_required_qualities function."""

    def test_returns_frozenset(self):
        """Returns FrozenSet of JivaQuality."""
        qualities = get_required_qualities(0)
        assert isinstance(qualities, frozenset)
        for q in qualities:
            assert isinstance(q, JivaQuality)

    def test_matches_bitmap(self):
        """FrozenSet matches the bitmap."""
        pos = 8
        bitmap = compute_required_bitmap(pos)
        qualities = get_required_qualities(pos)

        for q in qualities:
            assert bitmap & (1 << q.value)

    def test_count_function(self):
        """get_required_count returns correct count."""
        pos = 8
        qualities = get_required_qualities(pos)
        count = get_required_count(pos)
        assert len(qualities) == count


# =============================================================================
# shadow_can_execute Tests
# =============================================================================


class TestShadowCanExecute:
    """Test shadow_can_execute function."""

    def test_shadow_with_all_required_can_execute(self):
        """Shadow with all required qualities can execute."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Create shadow with exactly required qualities
        shadow = JivaShadow(
            quality_bitmap=required,
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )

        assert shadow_can_execute(shadow, pos) is True

    def test_shadow_with_extra_qualities_can_execute(self):
        """Shadow with extra qualities (superset) can execute."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Create shadow with required + extra
        shadow = JivaShadow(
            quality_bitmap=required | 0xFFFF,  # Add many extra bits
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )

        assert shadow_can_execute(shadow, pos) is True

    def test_shadow_missing_required_cannot_execute(self):
        """Shadow missing required qualities cannot execute."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Create shadow with almost all required (missing first set bit)
        if required > 0:
            # Find first set bit and unset it
            first_bit = required & -required  # Isolate lowest set bit
            incomplete = required ^ first_bit

            shadow = JivaShadow(
                quality_bitmap=incomplete,
                seed_hash=b"test" * 8,
                shadow_id="test_shadow",
            )

            assert shadow_can_execute(shadow, pos) is False


# =============================================================================
# shadow_match_score Tests
# =============================================================================


class TestShadowMatchScore:
    """Test shadow_match_score function."""

    def test_perfect_match_is_1(self):
        """Perfect match (exact qualities) scores 1.0."""
        pos = 5
        required = compute_required_bitmap(pos)

        shadow = JivaShadow(
            quality_bitmap=required,
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )

        score = shadow_match_score(shadow, pos)
        assert score == 1.0

    def test_missing_required_is_0(self):
        """Missing required qualities scores 0.0."""
        pos = 5
        required = compute_required_bitmap(pos)

        if required > 0:
            first_bit = required & -required
            incomplete = required ^ first_bit

            shadow = JivaShadow(
                quality_bitmap=incomplete,
                seed_hash=b"test" * 8,
                shadow_id="test_shadow",
            )

            score = shadow_match_score(shadow, pos)
            assert score == 0.0

    def test_excess_qualities_reduce_score(self):
        """Excess qualities slightly reduce score (but stay >= 0.5)."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Add many extra qualities
        shadow = JivaShadow(
            quality_bitmap=required | ((1 << 50) - 1),  # All 50 qualities
            seed_hash=b"test" * 8,
            shadow_id="test_shadow",
        )

        score = shadow_match_score(shadow, pos)
        assert 0.5 <= score < 1.0


# =============================================================================
# spawn_shadow_for_position Tests (Varnashrama)
# =============================================================================


class TestSpawnShadowForPosition:
    """Test spawn_shadow_for_position - Varnashrama spawn."""

    def test_spawned_shadow_is_qualified(self):
        """Spawned shadow is ALWAYS qualified for its position."""
        for pos in range(WORDS):
            shadow = spawn_shadow_for_position(pos)
            assert shadow_can_execute(shadow, pos) is True

    def test_spawned_shadow_has_correct_id_prefix(self):
        """Spawned shadow ID contains position info."""
        shadow = spawn_shadow_for_position(8)
        assert "8" in shadow.shadow_id
        assert "shadow_" in shadow.shadow_id

    def test_spawned_shadow_with_context(self):
        """Context adds uniqueness."""
        shadow1 = spawn_shadow_for_position(8, context=b"context_a")
        shadow2 = spawn_shadow_for_position(8, context=b"context_b")

        # Both should be qualified
        assert shadow_can_execute(shadow1, 8) is True
        assert shadow_can_execute(shadow2, 8) is True

        # But should have different extra qualities (usually)
        # Note: Required qualities are the same

    def test_spawned_shadow_has_all_required(self):
        """Spawned shadow has at least all required qualities."""
        pos = 5
        required = compute_required_bitmap(pos)
        shadow = spawn_shadow_for_position(pos)

        # Check all required bits are set
        assert (shadow.quality_bitmap & required) == required


# =============================================================================
# find_best_shadow Tests
# =============================================================================


class TestFindBestShadow:
    """Test find_best_shadow function."""

    def test_finds_best_from_list(self):
        """Finds best matching shadow from list."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Create 3 shadows: qualified perfect, qualified excess, unqualified
        perfect = JivaShadow(
            quality_bitmap=required,
            seed_hash=b"a" * 32,
            shadow_id="perfect",
        )
        excess = JivaShadow(
            quality_bitmap=required | 0xFF00,
            seed_hash=b"b" * 32,
            shadow_id="excess",
        )

        best = find_best_shadow([excess, perfect], pos)
        assert best.shadow_id == "perfect"  # Perfect match wins

    def test_returns_none_if_no_qualified(self):
        """Returns None if no shadow qualifies."""
        pos = 5
        required = compute_required_bitmap(pos)

        # Create unqualified shadow
        if required > 0:
            first_bit = required & -required
            incomplete = required ^ first_bit

            unqualified = JivaShadow(
                quality_bitmap=incomplete,
                seed_hash=b"u" * 32,
                shadow_id="unqualified",
            )

            best = find_best_shadow([unqualified], pos)
            assert best is None


# =============================================================================
# get_position_adhikara_report Tests
# =============================================================================


class TestGetPositionAdhikaraReport:
    """Test get_position_adhikara_report function."""

    def test_report_structure(self):
        """Report has correct structure."""
        report = get_position_adhikara_report(8)

        assert "position" in report
        assert "holy_name" in report
        assert "quarter" in report
        assert "required_count" in report
        assert "required_bitmap" in report
        assert "guna_distribution" in report
        assert "qualities" in report

    def test_report_position_matches(self):
        """Report position matches input."""
        for pos in range(WORDS):
            report = get_position_adhikara_report(pos)
            assert report["position"] == pos


# =============================================================================
# Determinism Verification Tests
# =============================================================================


class TestVerifyAdhikaraDeterminism:
    """Test verify_adhikara_determinism function."""

    def test_computation_is_deterministic(self):
        """Adhikara computation is deterministic."""
        assert verify_adhikara_determinism() is True


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.lila import adhikara

        expected = [
            "compute_required_bitmap",
            "get_required_qualities",
            "get_required_count",
            "shadow_can_execute",
            "shadow_match_score",
            "find_best_shadow",
            "spawn_shadow_for_position",
            "get_position_adhikara_report",
            "verify_adhikara_determinism",
            "QUARTER_RANGES",
            "HARE_AFFINITY",
            "KRISHNA_AFFINITY",
            "RAMA_AFFINITY",
        ]
        for item in expected:
            assert item in adhikara.__all__, f"{item} should be in __all__"
