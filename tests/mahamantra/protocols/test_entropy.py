"""
TESTS: _entropy.py - The Entropy Protocol
==========================================

REAL TESTS for:
1. Entropy constants
2. EntropyLevel enum
3. EntropyReading dataclass
4. AggregateEntropy dataclass
5. EntropySensor/EntropyAggregator protocols
6. EntropyProtocolDef
"""

import pytest
from datetime import datetime
from vibe_core.mahamantra.protocols._entropy import (
    # Shastra constants
    SB_GAJENDRA_CHAPTER,
    PAIN_SAMADHI,
    PAIN_SADHANA,
    HEALTH_SAMADHI,
    HEALTH_SADHANA,
    # Enums
    EntropyLevel,
    # Data classes
    EntropyReading,
    AggregateEntropy,
    # Protocols
    EntropySensor,
    EntropyAggregator,
    # Protocol definition
    EntropyProtocolDef,
    # Convenience functions
    pain_to_frequency,
    health_to_frequency,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestEntropyConstants:
    """Test entropy constants."""

    def test_sb_gajendra_chapter(self):
        """SB_GAJENDRA_CHAPTER is 8.2-4."""
        assert SB_GAJENDRA_CHAPTER == "8.2-4"

    def test_pain_samadhi(self):
        """PAIN_SAMADHI is 0.05."""
        assert PAIN_SAMADHI == 0.05

    def test_pain_sadhana(self):
        """PAIN_SADHANA is 0.20."""
        assert PAIN_SADHANA == 0.20

    def test_health_samadhi(self):
        """HEALTH_SAMADHI is 0.95."""
        assert HEALTH_SAMADHI == 0.95

    def test_health_sadhana(self):
        """HEALTH_SADHANA is 0.80."""
        assert HEALTH_SADHANA == 0.80

    def test_health_pain_inverse(self):
        """Health and pain thresholds are inverse."""
        assert HEALTH_SAMADHI == 1.0 - PAIN_SAMADHI
        assert HEALTH_SADHANA == 1.0 - PAIN_SADHANA


# =============================================================================
# EntropyLevel Enum Tests
# =============================================================================


class TestEntropyLevel:
    """Test EntropyLevel enum."""

    def test_entropy_level_samadhi(self):
        """EntropyLevel has SAMADHI."""
        assert EntropyLevel.SAMADHI.value == "samadhi"

    def test_entropy_level_sadhana(self):
        """EntropyLevel has SADHANA."""
        assert EntropyLevel.SADHANA.value == "sadhana"

    def test_entropy_level_gajendra(self):
        """EntropyLevel has GAJENDRA."""
        assert EntropyLevel.GAJENDRA.value == "gajendra"

    def test_entropy_level_count(self):
        """There are 3 entropy levels."""
        assert len(EntropyLevel) == 3

    def test_from_pain_samadhi(self):
        """from_pain returns SAMADHI for low pain."""
        assert EntropyLevel.from_pain(0.0) == EntropyLevel.SAMADHI
        assert EntropyLevel.from_pain(0.05) == EntropyLevel.SAMADHI

    def test_from_pain_sadhana(self):
        """from_pain returns SADHANA for medium pain."""
        assert EntropyLevel.from_pain(0.10) == EntropyLevel.SADHANA
        assert EntropyLevel.from_pain(0.20) == EntropyLevel.SADHANA

    def test_from_pain_gajendra(self):
        """from_pain returns GAJENDRA for high pain."""
        assert EntropyLevel.from_pain(0.30) == EntropyLevel.GAJENDRA
        assert EntropyLevel.from_pain(1.0) == EntropyLevel.GAJENDRA

    def test_from_health_samadhi(self):
        """from_health returns SAMADHI for high health."""
        assert EntropyLevel.from_health(1.0) == EntropyLevel.SAMADHI
        assert EntropyLevel.from_health(0.95) == EntropyLevel.SAMADHI

    def test_from_health_sadhana(self):
        """from_health returns SADHANA for medium health."""
        assert EntropyLevel.from_health(0.90) == EntropyLevel.SADHANA
        assert EntropyLevel.from_health(0.80) == EntropyLevel.SADHANA

    def test_from_health_gajendra(self):
        """from_health returns GAJENDRA for low health."""
        assert EntropyLevel.from_health(0.70) == EntropyLevel.GAJENDRA
        assert EntropyLevel.from_health(0.0) == EntropyLevel.GAJENDRA

    def test_frequency_hz_samadhi(self):
        """SAMADHI frequency is 0.5 Hz."""
        assert EntropyLevel.SAMADHI.frequency_hz == 0.5

    def test_frequency_hz_sadhana(self):
        """SADHANA frequency is 1.0 Hz."""
        assert EntropyLevel.SADHANA.frequency_hz == 1.0

    def test_frequency_hz_gajendra(self):
        """GAJENDRA frequency is 5.0 Hz."""
        assert EntropyLevel.GAJENDRA.frequency_hz == 5.0

    def test_frequency_ordering(self):
        """Frequencies increase with urgency."""
        assert EntropyLevel.SAMADHI.frequency_hz < EntropyLevel.SADHANA.frequency_hz
        assert EntropyLevel.SADHANA.frequency_hz < EntropyLevel.GAJENDRA.frequency_hz

    def test_cycle_time(self):
        """cycle_time is 16 / frequency_hz."""
        for level in EntropyLevel:
            assert level.cycle_time == 16.0 / level.frequency_hz

    def test_word_interval(self):
        """word_interval is 1 / frequency_hz."""
        for level in EntropyLevel:
            assert level.word_interval == 1.0 / level.frequency_hz


# =============================================================================
# EntropyReading Tests
# =============================================================================


class TestEntropyReading:
    """Test EntropyReading dataclass."""

    def test_entropy_reading_creation(self):
        """EntropyReading can be created."""
        reading = EntropyReading(source="test", pain=0.5)
        assert reading.source == "test"
        assert reading.pain == 0.5

    def test_entropy_reading_health(self):
        """health is inverse of pain."""
        reading = EntropyReading(source="test", pain=0.3)
        assert reading.health == 0.7

    def test_entropy_reading_entropy_level(self):
        """entropy_level derives from pain."""
        reading = EntropyReading(source="test", pain=0.01)
        assert reading.entropy_level == EntropyLevel.SAMADHI

    def test_entropy_reading_clamps_pain(self):
        """Pain is clamped to 0.0-1.0."""
        reading_high = EntropyReading(source="test", pain=1.5)
        assert reading_high.pain == 1.0

        reading_low = EntropyReading(source="test", pain=-0.5)
        assert reading_low.pain == 0.0


# =============================================================================
# AggregateEntropy Tests
# =============================================================================


class TestAggregateEntropy:
    """Test AggregateEntropy dataclass."""

    def test_aggregate_entropy_creation(self):
        """AggregateEntropy can be created."""
        agg = AggregateEntropy()
        assert agg.readings == []

    def test_aggregate_entropy_total_pain_empty(self):
        """total_pain returns 0.0 for empty readings."""
        agg = AggregateEntropy()
        assert agg.total_pain == 0.0

    def test_aggregate_entropy_total_pain_max(self):
        """total_pain returns max pain."""
        agg = AggregateEntropy(readings=[
            EntropyReading(source="a", pain=0.3),
            EntropyReading(source="b", pain=0.7),
            EntropyReading(source="c", pain=0.5),
        ])
        assert agg.total_pain == 0.7

    def test_aggregate_entropy_average_pain(self):
        """average_pain returns average."""
        agg = AggregateEntropy(readings=[
            EntropyReading(source="a", pain=0.3),
            EntropyReading(source="b", pain=0.6),
        ])
        assert agg.average_pain == pytest.approx(0.45)

    def test_aggregate_entropy_health(self):
        """health is inverse of total_pain."""
        agg = AggregateEntropy(readings=[
            EntropyReading(source="a", pain=0.4),
        ])
        assert agg.health == 0.6

    def test_aggregate_entropy_entropy_level(self):
        """entropy_level derives from total_pain."""
        agg = AggregateEntropy(readings=[
            EntropyReading(source="a", pain=0.02),
        ])
        assert agg.entropy_level == EntropyLevel.SAMADHI

    def test_aggregate_entropy_dominant_source(self):
        """dominant_source returns source with max pain."""
        agg = AggregateEntropy(readings=[
            EntropyReading(source="a", pain=0.3),
            EntropyReading(source="b", pain=0.7),
            EntropyReading(source="c", pain=0.5),
        ])
        assert agg.dominant_source == "b"

    def test_aggregate_entropy_add_reading(self):
        """add_reading appends reading."""
        agg = AggregateEntropy()
        agg.add_reading(EntropyReading(source="test", pain=0.5))
        assert len(agg.readings) == 1


# =============================================================================
# Convenience Functions Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_pain_to_frequency_samadhi(self):
        """pain_to_frequency returns 0.5 for low pain."""
        assert pain_to_frequency(0.01) == 0.5

    def test_pain_to_frequency_sadhana(self):
        """pain_to_frequency returns 1.0 for medium pain."""
        assert pain_to_frequency(0.10) == 1.0

    def test_pain_to_frequency_gajendra(self):
        """pain_to_frequency returns 5.0 for high pain."""
        assert pain_to_frequency(0.50) == 5.0

    def test_health_to_frequency_samadhi(self):
        """health_to_frequency returns 0.5 for high health."""
        assert health_to_frequency(0.99) == 0.5

    def test_health_to_frequency_sadhana(self):
        """health_to_frequency returns 1.0 for medium health."""
        assert health_to_frequency(0.85) == 1.0

    def test_health_to_frequency_gajendra(self):
        """health_to_frequency returns 5.0 for low health."""
        assert health_to_frequency(0.50) == 5.0


# =============================================================================
# EntropyProtocolDef Tests
# =============================================================================


class TestEntropyProtocolDef:
    """Test EntropyProtocolDef."""

    def test_entropy_protocol_validates(self):
        """EntropyProtocolDef validates."""
        valid, violations = EntropyProtocolDef.validate()
        assert valid is True

    def test_entropy_protocol_identity(self):
        """EntropyProtocolDef has correct identity."""
        identity = EntropyProtocolDef.get_identity()
        assert identity.name == "EntropyProtocol"
        assert identity.mahajana == "parashurama"
        assert identity.position == 8

    def test_entropy_protocol_provides(self):
        """EntropyProtocolDef provides entropy capabilities."""
        cap = EntropyProtocolDef.get_capability()
        assert "entropy_level" in cap.provides
        assert "pain_measurement" in cap.provides
        assert "health_score" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _entropy
        expected = [
            "EntropyLevel",
            "EntropyReading",
            "AggregateEntropy",
            "EntropySensor",
            "EntropyAggregator",
            "EntropyProtocolDef",
            "pain_to_frequency",
            "health_to_frequency",
        ]
        for item in expected:
            assert item in _entropy.__all__, f"{item} should be in __all__"
