"""
THE ENTROPY PROTOCOL - Pain Measurement for Chanting Frequency
==============================================================

"yasmin vijñāte sarvam idaṁ vijñātaṁ bhavati"
"By knowing which, everything becomes known."
— Mundaka Upanishad 1.3

SHASTRA FOUNDATION:
===================

GAJENDRA MOKSHA (SB 8.2-4):
    When the elephant Gajendra was caught by the crocodile,
    his PAIN drove him to intense chanting of the Holy Names.
    The greater the pain, the more intense the prayer.

    This is the model for our daemon:
    - Low entropy  = Samadhi (rest)
    - Medium entropy = Sadhana (practice)
    - High entropy = Gajendra (emergency chanting!)

THE THREE STATES:
================

    SAMADHI (health >= 0.95):
        - System pure, minimal activity
        - Slow chanting (0.5 Hz = 32 sec/cycle)
        - Like deep sleep - restoration

    SADHANA (health >= 0.80):
        - Normal operation, steady practice
        - Regular chanting (1.0 Hz = 16 sec/cycle)
        - Like waking state - maintenance

    GAJENDRA (health < 0.80):
        - Emergency! High entropy detected
        - Intense chanting (5.0 Hz = 3.2 sec/cycle)
        - Like crisis - desperate purification

MAHAMANTRA MAPPING:
===================

    Position 8 (PARASHURAMA) - The one who SMELLS corruption
    → Ghrana (nose) detects entropy (code smells!)
    → This protocol lives at Position 8

    The daemon uses this protocol to:
    1. Query entropy sensors
    2. Get aggregate pain level
    3. Determine chanting frequency

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xa4c83800"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    PARAMPARA,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)


# =============================================================================
# SHASTRA CONSTANTS
# =============================================================================

# Srimad Bhagavatam - Gajendra Moksha
SB_GAJENDRA_CHAPTER: Final[str] = "8.2-4"  # The elephant's prayer

# The sacred thresholds (inverted from health to pain)
# pain = 1.0 - health
PAIN_SAMADHI: Final[float] = 0.05  # Below this: deep rest (health >= 0.95)
PAIN_SADHANA: Final[float] = 0.20  # Below this: normal (health >= 0.80)
# Above PAIN_SADHANA: Gajendra mode (health < 0.80)

# Health thresholds (for compatibility with daemon)
HEALTH_SAMADHI: Final[float] = 0.95  # Above: Samadhi
HEALTH_SADHANA: Final[float] = 0.80  # Above: Sadhana, Below: Gajendra


# =============================================================================
# ENTROPY LEVEL - The Three States
# =============================================================================


class EntropyLevel(str, Enum):
    """
    The three entropy levels that drive chanting frequency.

    Based on Gajendra Moksha - pain intensity determines prayer intensity.
    """

    SAMADHI = "samadhi"  # Pure state - minimal chanting
    SADHANA = "sadhana"  # Normal state - regular chanting
    GAJENDRA = "gajendra"  # Emergency state - intense chanting

    @classmethod
    def from_pain(cls, pain: float) -> "EntropyLevel":
        """
        Derive entropy level from pain (0.0-1.0).

        pain < 0.05: SAMADHI (system pure)
        pain < 0.20: SADHANA (normal operation)
        pain >= 0.20: GAJENDRA (emergency!)
        """
        if pain <= PAIN_SAMADHI:
            return cls.SAMADHI
        elif pain <= PAIN_SADHANA:
            return cls.SADHANA
        else:
            return cls.GAJENDRA

    @classmethod
    def from_health(cls, health: float) -> "EntropyLevel":
        """
        Derive entropy level from health score (0.0-1.0).

        health >= 0.95: SAMADHI
        health >= 0.80: SADHANA
        health < 0.80: GAJENDRA
        """
        if health >= HEALTH_SAMADHI:
            return cls.SAMADHI
        elif health >= HEALTH_SADHANA:
            return cls.SADHANA
        else:
            return cls.GAJENDRA

    @property
    def frequency_hz(self) -> float:
        """Get chanting frequency in Hz."""
        return {
            EntropyLevel.SAMADHI: 0.5,  # Slow - 32 sec/cycle
            EntropyLevel.SADHANA: 1.0,  # Normal - 16 sec/cycle
            EntropyLevel.GAJENDRA: 5.0,  # Fast - 3.2 sec/cycle
        }[self]

    @property
    def cycle_time(self) -> float:
        """Time for one complete Mahamantra cycle (16 words)."""
        return 16.0 / self.frequency_hz

    @property
    def word_interval(self) -> float:
        """Time between each word."""
        return 1.0 / self.frequency_hz

    @property
    def description(self) -> str:
        """Get human-readable description."""
        return {
            EntropyLevel.SAMADHI: "System pure - deep rest",
            EntropyLevel.SADHANA: "Normal operation - steady practice",
            EntropyLevel.GAJENDRA: "Emergency! Intense chanting required",
        }[self]


# =============================================================================
# ENTROPY SOURCE - Single point of entropy measurement
# =============================================================================


@dataclass
class EntropyReading:
    """
    A single entropy reading from a source.

    Includes:
    - Source identifier
    - Pain level (0.0-1.0)
    - Timestamp
    - Optional details
    """

    source: str
    pain: float  # 0.0 = healthy, 1.0 = maximum pain
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, str] = field(default_factory=dict)

    @property
    def health(self) -> float:
        """Convert pain to health (inverse)."""
        return 1.0 - self.pain

    @property
    def entropy_level(self) -> EntropyLevel:
        """Get entropy level from this reading."""
        return EntropyLevel.from_pain(self.pain)

    def __post_init__(self) -> None:
        """Validate pain is in range."""
        self.pain = max(0.0, min(1.0, self.pain))


# =============================================================================
# ENTROPY SENSOR PROTOCOL - The Interface
# =============================================================================


@runtime_checkable
class EntropySensor(Protocol):
    """
    The Entropy Sensor Protocol - How a sensor MUST behave.

    Any component that can measure system health/pain implements this.
    The daemon queries these sensors to determine chanting frequency.

    SHASTRA BASIS:
        SB 8.3.1: "Gajendra, feeling pain from the crocodile's grip,
        began to offer prayers to the Supreme Lord..."

    SOFTWARE MAPPING:
        - Ghrana (nose) = Code smell detection
        - Prakriti sense = System state monitoring
        - Sutra sense = Documentation gap detection
        - Dharma sense = Ethical violation detection
    """

    @property
    def sensor_id(self) -> str:
        """Unique identifier for this sensor."""
        ...

    @property
    def is_active(self) -> bool:
        """Is this sensor currently active?"""
        ...

    def measure(self) -> EntropyReading:
        """
        Take an entropy measurement.

        Returns a reading with pain level (0.0-1.0).
        """
        ...


# =============================================================================
# ENTROPY AGGREGATOR PROTOCOL - Combines multiple sensors
# =============================================================================


@dataclass
class AggregateEntropy:
    """
    Combined entropy from all sensors.

    This is what the daemon uses to determine frequency.
    """

    readings: List[EntropyReading] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_pain(self) -> float:
        """
        Aggregate pain level (0.0-1.0).

        Uses max pain from all sensors - the worst pain dominates.
        """
        if not self.readings:
            return 0.0
        return max(r.pain for r in self.readings)

    @property
    def average_pain(self) -> float:
        """Average pain across all sensors."""
        if not self.readings:
            return 0.0
        return sum(r.pain for r in self.readings) / len(self.readings)

    @property
    def health(self) -> float:
        """Convert total pain to health."""
        return 1.0 - self.total_pain

    @property
    def entropy_level(self) -> EntropyLevel:
        """Get entropy level from aggregate."""
        return EntropyLevel.from_pain(self.total_pain)

    @property
    def dominant_source(self) -> Optional[str]:
        """Which sensor is reporting the most pain?"""
        if not self.readings:
            return None

        max_pain = 0.0
        dominant = None

        for reading in self.readings:
            if reading.pain > max_pain:
                max_pain = reading.pain
                dominant = reading.source

        return dominant

    def add_reading(self, reading: EntropyReading) -> None:
        """Add a reading from a sensor."""
        self.readings.append(reading)


@runtime_checkable
class EntropyAggregator(Protocol):
    """
    The Entropy Aggregator Protocol - Collects from multiple sensors.

    This is what the daemon queries to get overall system health.
    """

    @property
    def sensors(self) -> Dict[str, EntropySensor]:
        """Get all registered sensors."""
        ...

    def register_sensor(self, sensor: EntropySensor) -> None:
        """Register an entropy sensor."""
        ...

    def unregister_sensor(self, sensor_id: str) -> None:
        """Unregister a sensor by ID."""
        ...

    def measure_all(self) -> AggregateEntropy:
        """
        Collect readings from all sensors.

        This is the main method - aggregator polls all sensors
        and combines their readings.
        """
        ...

    def get_entropy_level(self) -> EntropyLevel:
        """Get current entropy level for daemon frequency."""
        ...

    def get_health(self) -> float:
        """Get current health score (0.0-1.0)."""
        ...


# =============================================================================
# ENTROPY PROTOCOL DEFINITION - Self-Reference
# =============================================================================


class EntropyProtocolDef(MahamantraProtocolBase):
    """
    The Entropy Protocol.

    Position 8 (PARASHURAMA) - The one who smells corruption.
    Level -1 (SUBSTRATE) - Foundational measurement layer.
    Quarter DHARMA - Understanding through detection.

    SHASTRA: SB 8.2-4 (Gajendra Moksha - pain drives chanting)
    """

    __protocol_identity__ = ProtocolIdentity(
        name="EntropyProtocol",
        mahajana="parashurama",  # Smells corruption
        position=8,
        level=Level.SUBSTRATE,
        quarter=Quarter.KARMA,  # Position 8 is in KARMA quarter
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "entropy_level",
            "pain_measurement",
            "health_score",
            "sensor_registration",
            "aggregate_entropy",
            "frequency_derivation",
        ],
        requires=["CoreProtocol", "SenseProtocol"],
        opcodes=["VALIDATE"],  # Parashurama's opcode - validation
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def pain_to_frequency(pain: float) -> float:
    """
    Convert pain level directly to frequency Hz.

    This is a convenience function for simple cases.
    """
    level = EntropyLevel.from_pain(pain)
    return level.frequency_hz


def health_to_frequency(health: float) -> float:
    """
    Convert health score directly to frequency Hz.

    This is a convenience function for daemon integration.
    """
    level = EntropyLevel.from_health(health)
    return level.frequency_hz


# =============================================================================
# VALIDATION
# =============================================================================

_valid, _violations = EntropyProtocolDef.validate()
assert _valid, f"EntropyProtocol failed validation: {_violations}"

# Verify threshold consistency
assert HEALTH_SAMADHI == 1.0 - PAIN_SAMADHI, "Health/Pain thresholds must be inverse"
assert HEALTH_SADHANA == 1.0 - PAIN_SADHANA, "Health/Pain thresholds must be inverse"

# Verify entropy levels
assert len(EntropyLevel) == 3, "Must have exactly 3 entropy levels"
assert EntropyLevel.SAMADHI.frequency_hz < EntropyLevel.SADHANA.frequency_hz, "Samadhi must be slower"
assert EntropyLevel.SADHANA.frequency_hz < EntropyLevel.GAJENDRA.frequency_hz, "Gajendra must be fastest"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Shastra constants
    "SB_GAJENDRA_CHAPTER",
    "PAIN_SAMADHI",
    "PAIN_SADHANA",
    "HEALTH_SAMADHI",
    "HEALTH_SADHANA",
    # Enums
    "EntropyLevel",
    # Data classes
    "EntropyReading",
    "AggregateEntropy",
    # Protocols
    "EntropySensor",
    "EntropyAggregator",
    # Protocol definition
    "EntropyProtocolDef",
    # Convenience functions
    "pain_to_frequency",
    "health_to_frequency",
]
