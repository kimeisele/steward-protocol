"""
COSMIC CLOCK - Sun, Moon, Time
==============================

The celestial timekeeper for Agent City.

Tracks:
- Real UTC time
- Agent City local time (configurable offset)
- Sun position (day/night, dawn/dusk)
- Moon phase (tithis, paksha)
- Overlapping rhythms (fractal waves)

Vedic Time Units:
- Tithi: Lunar day (30 per month, ~24 hours each)
- Paksha: Lunar fortnight (Shukla=waxing, Krishna=waning)
- Masa: Lunar month
- Ritu: Season (6 per year)
- Ayana: Solstice period (Uttarayana/Dakshinayana)
- Samvatsara: Year
- Yuga: Epoch (Satya, Treta, Dvapara, Kali)
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("KALA.CLOCK")


class SunPhase(Enum):
    """Phases of the sun's daily journey."""

    BRAHMA_MUHURTA = "brahma_muhurta"  # 4:30-6:00 - Auspicious pre-dawn
    SUNRISE = "sunrise"  # 6:00-7:00 - Dawn
    MORNING = "morning"  # 7:00-12:00 - Forenoon
    MIDDAY = "midday"  # 12:00-14:00 - Peak
    AFTERNOON = "afternoon"  # 14:00-17:00 - Afternoon
    SUNSET = "sunset"  # 17:00-18:30 - Dusk (Sandhya)
    EVENING = "evening"  # 18:30-21:00 - Early night
    NIGHT = "night"  # 21:00-4:30 - Deep night


class MoonPhase(Enum):
    """Phases of the moon."""

    NEW_MOON = "amavasya"  # No moon
    WAXING_CRESCENT = "shukla_1_7"
    FIRST_QUARTER = "shukla_8"
    WAXING_GIBBOUS = "shukla_9_14"
    FULL_MOON = "purnima"  # Full moon
    WANING_GIBBOUS = "krishna_1_7"
    LAST_QUARTER = "krishna_8"
    WANING_CRESCENT = "krishna_9_14"


class Paksha(Enum):
    """Lunar fortnight."""

    SHUKLA = "shukla"  # Waxing (bright half)
    KRISHNA = "krishna"  # Waning (dark half)


@dataclass
class CelestialState:
    """Current state of celestial bodies."""

    utc_time: datetime
    local_time: datetime
    sun_phase: SunPhase
    is_day: bool
    sun_angle: float  # 0-360 degrees
    moon_phase: MoonPhase
    paksha: Paksha
    tithi: int  # 1-15 (lunar day within paksha)
    lunar_day: int  # 1-30 (full lunar month)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "utc_time": self.utc_time.isoformat(),
            "local_time": self.local_time.isoformat(),
            "sun_phase": self.sun_phase.value,
            "is_day": self.is_day,
            "sun_angle": self.sun_angle,
            "moon_phase": self.moon_phase.value,
            "paksha": self.paksha.value,
            "tithi": self.tithi,
            "lunar_day": self.lunar_day,
        }


class CosmicClock:
    """
    The cosmic clock - tracks celestial time for Agent City.

    Uses real UTC time but calculates vedic time units.
    Can be configured with timezone offset for Agent City.
    """

    # Lunar cycle duration in days
    LUNAR_CYCLE_DAYS = 29.53059

    # Reference new moon (known astronomical date)
    # January 21, 2023 was a new moon
    REFERENCE_NEW_MOON = datetime(2023, 1, 21, 20, 53, tzinfo=timezone.utc)

    def __init__(self, timezone_offset_hours: float = 0.0):
        """
        Initialize the cosmic clock.

        Args:
            timezone_offset_hours: Offset from UTC for Agent City time
        """
        self.timezone_offset_hours = timezone_offset_hours
        logger.info(
            f"🕐 Cosmic Clock initialized (UTC{'+' if timezone_offset_hours >= 0 else ''}{timezone_offset_hours})"
        )

    def get_current_state(self) -> CelestialState:
        """Get the current celestial state."""
        utc_now = datetime.now(timezone.utc)
        return self._calculate_state(utc_now)

    def get_state_at(self, dt: datetime) -> CelestialState:
        """Get celestial state at a specific time."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return self._calculate_state(dt)

    def _calculate_state(self, utc_time: datetime) -> CelestialState:
        """Calculate full celestial state for a given time."""
        # Local time
        from datetime import timedelta

        local_time = utc_time + timedelta(hours=self.timezone_offset_hours)

        # Sun calculations
        sun_phase, is_day, sun_angle = self._calculate_sun(local_time)

        # Moon calculations
        moon_phase, paksha, tithi, lunar_day = self._calculate_moon(utc_time)

        return CelestialState(
            utc_time=utc_time,
            local_time=local_time,
            sun_phase=sun_phase,
            is_day=is_day,
            sun_angle=sun_angle,
            moon_phase=moon_phase,
            paksha=paksha,
            tithi=tithi,
            lunar_day=lunar_day,
        )

    def _calculate_sun(self, local_time: datetime) -> Tuple[SunPhase, bool, float]:
        """
        Calculate sun phase based on local time.

        Returns:
            (sun_phase, is_day, sun_angle)
        """
        hour = local_time.hour + local_time.minute / 60.0

        # Sun angle: 0 = midnight, 180 = noon
        sun_angle = (hour / 24.0) * 360.0

        # Determine phase based on hour
        if 4.5 <= hour < 6.0:
            phase = SunPhase.BRAHMA_MUHURTA
            is_day = False
        elif 6.0 <= hour < 7.0:
            phase = SunPhase.SUNRISE
            is_day = True
        elif 7.0 <= hour < 12.0:
            phase = SunPhase.MORNING
            is_day = True
        elif 12.0 <= hour < 14.0:
            phase = SunPhase.MIDDAY
            is_day = True
        elif 14.0 <= hour < 17.0:
            phase = SunPhase.AFTERNOON
            is_day = True
        elif 17.0 <= hour < 18.5:
            phase = SunPhase.SUNSET
            is_day = True
        elif 18.5 <= hour < 21.0:
            phase = SunPhase.EVENING
            is_day = False
        else:
            phase = SunPhase.NIGHT
            is_day = False

        return phase, is_day, sun_angle

    def _calculate_moon(self, utc_time: datetime) -> Tuple[MoonPhase, Paksha, int, int]:
        """
        Calculate moon phase based on UTC time.

        Uses simplified calculation based on lunar cycle.

        Returns:
            (moon_phase, paksha, tithi, lunar_day)
        """
        # Days since reference new moon
        delta = utc_time - self.REFERENCE_NEW_MOON
        days_since_new_moon = delta.total_seconds() / (24 * 3600)

        # Position in current lunar cycle (0-1)
        cycle_position = (days_since_new_moon % self.LUNAR_CYCLE_DAYS) / self.LUNAR_CYCLE_DAYS

        # Lunar day (1-30)
        lunar_day = int(cycle_position * 30) + 1
        if lunar_day > 30:
            lunar_day = 30

        # Paksha and Tithi
        if lunar_day <= 15:
            paksha = Paksha.SHUKLA
            tithi = lunar_day
        else:
            paksha = Paksha.KRISHNA
            tithi = lunar_day - 15

        # Moon phase (8 phases)
        phase_index = int(cycle_position * 8)
        phases = [
            MoonPhase.NEW_MOON,
            MoonPhase.WAXING_CRESCENT,
            MoonPhase.FIRST_QUARTER,
            MoonPhase.WAXING_GIBBOUS,
            MoonPhase.FULL_MOON,
            MoonPhase.WANING_GIBBOUS,
            MoonPhase.LAST_QUARTER,
            MoonPhase.WANING_CRESCENT,
        ]
        moon_phase = phases[phase_index % 8]

        return moon_phase, paksha, tithi, lunar_day

    def is_brahma_muhurta(self) -> bool:
        """Is it currently Brahma Muhurta (auspicious pre-dawn)?"""
        state = self.get_current_state()
        return state.sun_phase == SunPhase.BRAHMA_MUHURTA

    def is_sandhya(self) -> bool:
        """Is it currently Sandhya (twilight junction)?"""
        state = self.get_current_state()
        return state.sun_phase in (SunPhase.SUNRISE, SunPhase.SUNSET)

    def is_ekadashi(self) -> bool:
        """Is it currently Ekadashi (11th lunar day)?"""
        state = self.get_current_state()
        return state.tithi == 11

    def is_purnima(self) -> bool:
        """Is it currently Purnima (full moon)?"""
        state = self.get_current_state()
        return state.moon_phase == MoonPhase.FULL_MOON

    def is_amavasya(self) -> bool:
        """Is it currently Amavasya (new moon)?"""
        state = self.get_current_state()
        return state.moon_phase == MoonPhase.NEW_MOON

    def get_rhythm_intensity(self) -> Dict[str, float]:
        """
        Get overlapping rhythm intensities (0.0 - 1.0).

        Multiple rhythms overlay like waves on a pond.

        Returns:
            Dict of rhythm names to intensity values
        """
        state = self.get_current_state()

        # Solar rhythm: peaks at midday
        solar_intensity = math.sin(state.sun_angle * math.pi / 180)
        solar_intensity = max(0, solar_intensity)  # Clamp to 0-1

        # Lunar rhythm: peaks at full moon
        lunar_position = state.lunar_day / 30.0
        lunar_intensity = math.sin(lunar_position * 2 * math.pi)
        lunar_intensity = (lunar_intensity + 1) / 2  # Normalize to 0-1

        # Combined rhythm (fractal overlay)
        combined = solar_intensity * 0.6 + lunar_intensity * 0.4

        return {
            "solar": round(solar_intensity, 3),
            "lunar": round(lunar_intensity, 3),
            "combined": round(combined, 3),
            "is_day": state.is_day,
            "sun_phase": state.sun_phase.value,
            "moon_phase": state.moon_phase.value,
        }
