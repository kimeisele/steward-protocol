# OPUS-165: KALA - Eternal Time Plugin

**Status:** ✅ IMPLEMENTED
**Priority:** P1 (Core Infrastructure)
**Date:** 2025-12-20

---

## 📜 Philosophy

From Bhagavad Gita Chapter 11, Verse 32:
> "कालोऽस्मि लोकक्षयकृत्प्रवृद्धो"
> "I am Time (Kala), the great destroyer of worlds."

KALA (काल) is the eternal time that binds all existence. In the Bhagavad Gita, five aspects define reality:

| Aspect | Sanskrit | In Steward Protocol |
|--------|----------|---------------------|
| **ISHVARA** | ईश्वर | Kernel (VISNU) - The unchanging supreme |
| **JIVA** | जीव | Agents - Living entities |
| **PRAKRITI** | प्रकृति | Data/Material - The material nature |
| **KALA** | काल | **THIS PLUGIN** - Eternal time |
| **KARMA** | कर्म | Tasks/Actions - The chain of cause and effect |

Without KALA, nothing moves. Time is the dimension that makes change possible.

---

## 🎯 Problem Statement

Before KALA, Agent City had fragmented time concepts:

1. **sarga.py** - Boot sequence (creation), but no ongoing time
2. **sarga_cycle plugin** - Day/Night of Brahma, but arbitrary timing
3. **daily_ritual.py** - 4 phases, but only runs when called
4. **pulse.py** - Heartbeat, but no celestial awareness
5. **prana_orchestrator** - Plugin phases, but no cosmic rhythm

**Result:** No unified time dimension. No sun. No moon. No cosmic clock.

---

## ✅ Solution: KALA Plugin

A single plugin that owns ALL time-related concerns:

```
vibe_core/plugins/kala/
├── __init__.py           # Package exports
├── manifest.json         # Plugin manifest
├── plugin_main.py        # KalaPlugin (on_boot, on_pulse, on_shutdown)
└── cosmic_clock.py       # Sun/Moon/Time calculations
```

### Components

#### 1. CosmicClock (cosmic_clock.py)

Tracks celestial time:

| Feature | Description |
|---------|-------------|
| **Sun Phase** | 8 phases: Brahma Muhurta, Sunrise, Morning, Midday, Afternoon, Sunset, Evening, Night |
| **Moon Phase** | 8 phases: New Moon, Waxing/Waning Crescent, Quarters, Gibbous, Full Moon |
| **Tithi** | Lunar day (1-15 per paksha) |
| **Paksha** | Lunar fortnight (Shukla=waxing, Krishna=waning) |
| **Rhythm Intensity** | Overlapping solar/lunar waves (0.0-1.0) |

#### 2. KalaPlugin (plugin_main.py)

Integrates time into kernel lifecycle:

| Hook | Action |
|------|--------|
| `on_boot` | Initialize clock, report current celestial state |
| `on_pulse` | Update time, detect phase transitions, update Sarga cycle |
| `on_shutdown` | Record final time state |

---

## 🔗 Integration Points

### 1. Sarga Cycle Integration

KALA updates Sarga's Day/Night of Brahma based on actual sun:

```python
# During daytime
sarga.set_cycle(Cycle.DAY_OF_BRAHMA)  # Creation mode

# During nighttime
sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)  # Maintenance mode
```

### 2. PRANA Integration

KALA runs in `PulsePhase.SENSORS` (first phase):
- Collects time data before other plugins act
- Registers `trigger_ritual` mutations for phase transitions

### 3. Daily Ritual Triggering

Sun phase transitions trigger ritual phases:

| Sun Phase | Triggered Ritual |
|-----------|------------------|
| BRAHMA_MUHURTA | Sunrise |
| SUNRISE | Sunrise |
| MIDDAY | Midday |
| SUNSET | Sunset |
| NIGHT | Archive |

---

## 📊 Vedic Time Units

```
┌─────────────────────────────────────────────────────────┐
│  MICRO (seconds-hours)                                  │
│  └── Pulse (15 min), Hora (hour)                        │
│                                                         │
│  DAILY (24 hours)                                       │
│  └── Sun Phases: Brahma Muhurta → Night                 │
│                                                         │
│  LUNAR (29.5 days)                                      │
│  └── Tithi (lunar day), Paksha (fortnight)              │
│                                                         │
│  SEASONAL (months-years)                                │
│  └── Masa (month), Ritu (season), Samvatsara (year)     │
│                                                         │
│  COSMIC (yugas)                                         │
│  └── Satya, Treta, Dvapara, Kali                        │
╰─────────────────────────────────────────────────────────╯
```

---

## 🌊 Rhythm Intensity (Fractal Waves)

Multiple rhythms overlay like waves on a pond:

```python
rhythms = kala.get_rhythm_intensity()
# Returns:
{
    "solar": 0.85,      # Peaks at midday
    "lunar": 0.42,      # Peaks at full moon
    "combined": 0.68,   # Weighted overlay
    "is_day": True,
    "sun_phase": "morning",
    "moon_phase": "waxing_gibbous"
}
```

---

## 🧪 Test Coverage

14 tests in `tests/unit/plugins/test_kala.py`:

| Test Class | Tests |
|------------|-------|
| TestCosmicClock | 7 tests (sun, moon, rhythms, timezone) |
| TestKalaPlugin | 5 tests (plugin properties, state) |
| TestKalaSargaIntegration | 2 tests (cycle get/set) |

---

## The Harness

<!-- @HARNESS
files:
  - path: vibe_core/plugins/kala/__init__.py
    required: true
  - path: vibe_core/plugins/kala/manifest.json
    required: true
  - path: vibe_core/plugins/kala/plugin_main.py
    required: true
  - path: vibe_core/plugins/kala/cosmic_clock.py
    required: true
  - path: tests/unit/plugins/test_kala.py
    required: true

wiring:
  # === PLUGIN STRUCTURE ===
  - pattern: "class KalaPlugin"
    in: vibe_core/plugins/kala/plugin_main.py
  - pattern: "class CosmicClock"
    in: vibe_core/plugins/kala/cosmic_clock.py
  - pattern: "def on_boot"
    in: vibe_core/plugins/kala/plugin_main.py
  - pattern: "def on_pulse"
    in: vibe_core/plugins/kala/plugin_main.py

  # === CELESTIAL TRACKING ===
  - pattern: "class SunPhase"
    in: vibe_core/plugins/kala/cosmic_clock.py
  - pattern: "class MoonPhase"
    in: vibe_core/plugins/kala/cosmic_clock.py
  - pattern: "class Paksha"
    in: vibe_core/plugins/kala/cosmic_clock.py
  - pattern: "get_rhythm_intensity"
    in: vibe_core/plugins/kala/cosmic_clock.py

  # === SARGA INTEGRATION ===
  - pattern: "_update_sarga_cycle"
    in: vibe_core/plugins/kala/plugin_main.py
  - pattern: "from vibe_core.sarga import"
    in: vibe_core/plugins/kala/plugin_main.py

semantic:
  - type: class_exists
    name: kala_plugin
    in: vibe_core/plugins/kala/plugin_main.py
    class: KalaPlugin
    rationale: "Main plugin class for time orchestration"

  - type: class_exists
    name: cosmic_clock
    in: vibe_core/plugins/kala/cosmic_clock.py
    class: CosmicClock
    rationale: "Celestial time calculator"

  - type: enum_exists
    name: sun_phase_enum
    in: vibe_core/plugins/kala/cosmic_clock.py
    enum: SunPhase
    values: [BRAHMA_MUHURTA, SUNRISE, MORNING, MIDDAY, AFTERNOON, SUNSET, EVENING, NIGHT]
    rationale: "8 phases of sun's daily journey"

  - type: enum_exists
    name: moon_phase_enum
    in: vibe_core/plugins/kala/cosmic_clock.py
    enum: MoonPhase
    values: [NEW_MOON, WAXING_CRESCENT, FIRST_QUARTER, WAXING_GIBBOUS, FULL_MOON, WANING_GIBBOUS, LAST_QUARTER, WANING_CRESCENT]
    rationale: "8 phases of lunar cycle"

  - type: method_exists
    name: plugin_on_pulse
    in: vibe_core/plugins/kala/plugin_main.py
    class: KalaPlugin
    method: on_pulse
    rationale: "PRANA integration for time updates"

  - type: property_value
    name: pulse_phase_sensors
    in: vibe_core/plugins/kala/plugin_main.py
    property: pulse_phase
    expected: "PulsePhase.SENSORS"
    rationale: "KALA must run first in SENSORS phase"

tests:
  - tests/unit/plugins/test_kala.py
-->

---

## 📝 Usage

```python
# Get KALA plugin from kernel
kala = kernel.get_plugin("kala")

# Get current celestial state
state = kala.get_current_state()
print(f"Sun: {state['sun_phase']}, Moon: {state['moon_phase']}")

# Get rhythm intensities
rhythms = kala.get_rhythm_intensity()
print(f"Solar intensity: {rhythms['solar']}")

# Check special times
if kala.is_auspicious_time():
    print("Brahma Muhurta, Ekadashi, or Purnima!")
```

---

## 🔮 Future Extensions

1. **Yuga Tracking** - Cosmic epochs (configurable start date)
2. **Nakshatra** - Lunar mansions (27 constellations)
3. **Planetary Hours** - Classical hora calculations
4. **Festival Calendar** - Automatic detection of Diwali, Holi, etc.
5. **Custom Rhythms** - User-defined overlapping waves

---

## 🎭 Summary

KALA is the missing time dimension for Agent City.

| Before | After |
|--------|-------|
| Fragmented time concepts | Unified KALA plugin |
| No celestial awareness | Sun/Moon/Tithi tracking |
| Arbitrary Day/Night | Real-time based Day/Night of Brahma |
| Single pulse rhythm | Overlapping fractal waves |

**"Time is the eternal witness. KALA observes all."**

---

*Implemented by Claude Code, 2025-12-20*
