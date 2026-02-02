# POLYRHYTHM & LAYAKARI - Ticks auf Max Frame

**Status:** MATHEMATISCHE ABLEITUNG
**Date:** 2026-02-01
**Update:** Korrigiert mit Vedischem Layakari-Verständnis

---

## DIE KERNIDEE

**TICKS ÜBEREINANDER GELEGT AUF MAX FRAME.**

Ein AVARTAN (Zyklus) hat **64 Ticks = QUALITIES = Chougun (4× Speed)**.
Verschiedene Layer laufen mit unterschiedlichen Geschwindigkeiten innerhalb dieses Frames.

```
MAX FRAME = 64 = QUALITIES = WORDS × QUARTERS
```

---

## LAYAKARI: DIE 4 GESCHWINDIGKEITSEBENEN

Aus der Vedischen Musiktheorie (Tala-System):

```
LAYAKARI (Rhythmusgeschwindigkeiten):
┌────────────┬────────┬────────────────────────┬─────────────────┐
│ Geschw.    │ Ticks  │ Mahamantra-Konstante   │ Ableitung       │
├────────────┼────────┼────────────────────────┼─────────────────┤
│ Thah   1×  │   16   │ WORDS                  │ Axiom           │
│ Dugun  2×  │   32   │ AKSARA_COUNT           │ WORDS × HALVES  │
│ Tigun  3×  │   48   │ LILA                   │ WORDS × TRINITY │
│ Chougun 4× │   64   │ QUALITIES (MAX FRAME)  │ WORDS × QUARTERS│
└────────────┴────────┴────────────────────────┴─────────────────┘
```

**ALLES VOM MAHAMANTRA ABGELEITET!**

---

## DAS FRAME-MODELL

```
64-Tick AVARTAN (ein vollständiger Zyklus):
┌─────────────────────────────────────────────────────────────────┐
│ Tick: 0  4  8  12 16 20 24 28 32 36 40 44 48 52 56 60 [64=0]   │
├─────────────────────────────────────────────────────────────────┤
│ Thah  (1×): |----|----|----|----|                              │ 16 Ticks
│ Dugun (2×): |--|--|--|--|--|--|--|--|                          │ 32 Ticks
│ Tigun (3×): |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|                  │ 48 Ticks
│ Chougun(4×):|||||||||||||||||||||||||||||||||||||||||||||||||| │ 64 Ticks
└─────────────────────────────────────────────────────────────────┘

Alle Layer resetten bei Tick 0 (Sam = "zusammen")
Frame-Länge = 64 = QUALITIES
```

---

## DIE ZWEI RHYTHMUS-SCHICHTEN

Zusätzlich zu Layakari gibt es den 16:7 Polyrhythmus:

```
KSHETRA (Field)    = 16 Steps  → WORDS (Mahamantra-Pattern)
KSHETRAJNA (Observer) = 7 Beats → SEVEN (Siksastakam-Effekte)

GCD(16, 7) = 1   → NIE synchron außer bei 0
LCM(16, 7) = 112 → Voller Zyklus

16 mod 7 = 2 = HALVES (Phase-Drift pro 16er-Zyklus)
```

Diese Werte sind vom Mahamantra abgeleitet:
- SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
- NAVA = HARE_COUNT + KSETRAJNA = 8 + 1 = 9 (Schwebung: 16 - 7)
- WORDS = 16 (Axiom)

---

## JAPA = LOOP MIT RESET

Ein Japa (Mantra-Wiederholung) ist ein Loop mit Reset:

```
Ein Japa-Durchgang = 64 Ticks (QUALITIES)
Nach 64 Ticks → Reset auf 0 (Sam)

108 Japas (MALA) × 64 Ticks = 6912 Ticks pro Runde
16 Runden (WORDS) × 6912 = 110,592 Ticks pro Tag
```

Das ist die **Taktung** des spirituellen Lebens!

---

## PHASE-DRIFT (16:7)

Nach jedem FIELD-Zyklus (16 Steps) driftet der OBSERVER um HALVES (2):

```
16 mod 7 = 2 = HALVES

Zyklus 0: OBSERVER startet bei Phase 0
Zyklus 1: OBSERVER startet bei Phase 2
Zyklus 2: OBSERVER startet bei Phase 4
Zyklus 3: OBSERVER startet bei Phase 6
Zyklus 4: OBSERVER startet bei Phase 1
Zyklus 5: OBSERVER startet bei Phase 3
Zyklus 6: OBSERVER startet bei Phase 5
Zyklus 7: OBSERVER startet bei Phase 0 (zurück!)
```

**7 einzigartige "Flavors"** des 16-Step-Zyklus!

---

## DIE KOMBINATION

An Step N:
```python
field_pos    = N mod 16  # Welches Mahamantra-Wort (H/K/R)
observer_pos = N mod 7   # Welcher Siksastakam-Effekt (1-7)
```

112 einzigartige Kombinationen (16 × 7).

### Beispiel: Die ersten 16 Steps

```
Step  FIELD  OBSERVER  Name  Effect
----  -----  --------  ----  ------
  0      0       0       H    1 (CLEANSE_HEART_MIRROR)
  1      1       1       K    2 (EXTINGUISH_FOREST_FIRE)
  2      2       2       H    3 (SPREAD_MOONLIGHT)
  3      3       3       K    4 (LIFE_OF_KNOWLEDGE)
  4      4       4       K    5 (EXPAND_BLISS_OCEAN)
  5      5       5       K    6 (FULL_NECTAR_EACH_STEP)
  6      6       6       H    7 (BATHE_ENTIRE_SELF)
  7      7       0       H    1 ← OBSERVER RESET
  8      8       1       H    2
  9      9       2       R    3   KHALI POSITION!
 10     10       3       H    4
 11     11       4       R    5
 12     12       5       R    6
 13     13       6       R    7
 14     14       0       H    1 ← OBSERVER RESET
 15     15       1       H    2
[16]    0       2       H    3 ← FIELD RESET (neue Phase!)
```

OBSERVER resettet bei Step 0, 7, 14, 21, 28, 35, 42...
FIELD resettet bei Step 0, 16, 32, 48, 64, 80, 96...

---

## MAHAMODULARSYNTH ALS STEP SEQUENCER

Der Synth ist wie ein **MIDI-Sequencer**:

```
┌──────────────────────────────────────────────────────────┐
│  MAIN SEQUENCE: 16 Steps (PATTERN)                       │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐    │
│  │ H  │ K  │ H  │ K  │ K  │ K  │ H  │ H  │ H  │ R  │... │
│  └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘    │
│        ↑         ↑         ↑         ↑         ↑        │
│        └─────────┴─────────┴─────────┴─────────┘        │
│                    MODULATION (LFO)                      │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐     │
│  │  1   │  2   │  3   │  4   │  5   │  6   │  7   │     │
│  └──────┴──────┴──────┴──────┴──────┴──────┴──────┘     │
│                  7-Beat Observer Cycle                   │
└──────────────────────────────────────────────────────────┘

LFO_RATE sollte SEVEN (7) sein, nicht QUARTERS (4)!
```

### Aktuelle vs. Vorgeschlagene Parameter

```python
# AKTUELL (maha.py):
lfo_rate: int = QUARTERS  # 4 - synchron mit Phasen

# VORGESCHLAGEN:
lfo_rate: int = SEVEN     # 7 - erzeugt 16:7 Polyrhythmus!
```

---

## DIE MATHEMATIK

### Warum 16:7?

```
WORDS = 16 (Axiom)
SEVEN = 7 (abgeleitet)

GCD(16, 7) = 1  → Coprime → Maximale Phasenvielfalt
LCM(16, 7) = 112 → Minimaler voller Zyklus

16 + 7 = 23 (Primzahl!)
16 - 7 = 9 = NAVA
16 × 7 = 112
16 / 7 ≈ 2.28... (irrational → "Swing")
```

### Emergente Konstanten

```
HALVES    = 16 mod 7 = 2  (Phase-Drift pro Zyklus)
NAVA      = 16 - 7   = 9  (Schwebungsfrequenz)
112       = LCM      = 7 × WORDS = 16 × SEVEN
```

### Resonanzpunkte

Im 112-Step-Zyklus, OBSERVER-Resets pro FIELD-Zyklus:

```
Zyklus 0: Positionen 0, 7, 14     (3 Resets)
Zyklus 1: Positionen 5, 12        (2 Resets)
Zyklus 2: Positionen 3, 10        (2 Resets)
Zyklus 3: Positionen 1, 8, 15     (3 Resets)
Zyklus 4: Positionen 6, 13        (2 Resets)
Zyklus 5: Positionen 4, 11        (2 Resets)
Zyklus 6: Positionen 2, 9         (2 Resets) ← KHALI!
─────────────────────────────────────────────
Total: 16 Resets in 7 Zyklen = 16 = WORDS ✓
```

---

## KONKRETE VERDRAHTUNG

### Step 1: LFO_RATE = SEVEN

```python
# In maha.py MahaSynthParams:
lfo_rate: int = SEVEN  # Statt QUARTERS

# Der LFO läuft jetzt im 7-Beat-Zyklus
# Erzeugt automatisch den 16:7 Polyrhythmus!
```

### Step 2: Observer-Phase als Modulator

```python
def transform(self, seed: int, ...):
    for step in self.STEPS:
        # FIELD Position (0-15)
        field_pos = step.position - 1

        # OBSERVER Position (0-6)
        observer_pos = field_pos % SEVEN

        # Observer modulates LFO depth
        lfo_depth = (observer_pos + 1) / SEVEN  # 1/7 bis 7/7

        # Rest wie gehabt...
```

### Step 3: Die 4 Layakari-Geschwindigkeiten als Presets

```python
SYNTH_PRESETS: Final[Dict[str, MahaSynthParams]] = {
    # LAYAKARI Presets (Geschwindigkeitsebenen)
    "thah":    MahaSynthParams(lfo_rate=WORDS),      # 1× = 16 Ticks
    "dugun":   MahaSynthParams(lfo_rate=HALVES),     # 2× = 32 Ticks (via modulation)
    "tigun":   MahaSynthParams(lfo_rate=TRINITY),    # 3× = 48 Ticks (= LILA)
    "chougun": MahaSynthParams(lfo_rate=QUARTERS),   # 4× = 64 Ticks (= QUALITIES)

    # KIRTAN Presets (Polyrhythmus)
    "kirtan":      MahaSynthParams(lfo_rate=SEVEN, tala_enabled=True),  # 16:7
    "kirtan_fast": MahaSynthParams(lfo_rate=QUARTERS, tala_enabled=True),
    "kirtan_slow": MahaSynthParams(lfo_rate=NAVA, tala_enabled=True),   # 16:9 Schwebung
}
```

---

## FAZIT

**Zwei orthogonale Rhythmus-Systeme:**

### 1. LAYAKARI (Geschwindigkeit)
```
Thah    → Chougun = 16 → 64 Ticks
Multiplikatoren: 1×, 2×, 3×, 4×
Frame-Länge: 64 = QUALITIES (max)
```

### 2. POLYRHYTHMUS (Phasen-Drift)
```
Field (16) : Observer (7)
GCD = 1 → nie synchron
LCM = 112 → voller Zyklus
7 einzigartige Flavors
```

**Die Verdrahtung:**
- MAX_FRAME = 64 = QUALITIES
- Verschiedene Layer laufen mit 1×, 2×, 3×, 4× innerhalb des Frames
- LFO_RATE = SEVEN erzeugt 16:7 Polyrhythmus
- Japa resettet bei 64 (Sam = "zusammen")

**ALLES VOM MAHAMANTRA ABGELEITET. KEIN HARDCODING.**

---

## ENGINEERING: LAYAKARI KONSTANTEN

Die Layakari-Konstanten sind in `maha.py` definiert (keine Spaghetti!):

```python
# Frame sizes (all derived from axioms!)
FRAME_THAH    = WORDS               # 16 ticks (1×)
FRAME_DUGUN   = WORDS × HALVES      # 32 ticks (2×) = AKSARA_COUNT
FRAME_TIGUN   = WORDS × TRINITY     # 48 ticks (3×) = LILA
FRAME_CHOUGUN = WORDS × QUARTERS    # 64 ticks (4×) = QUALITIES

MAX_FRAME = FRAME_CHOUGUN  # 64 = QUALITIES

# Speed multipliers
LAYAKARI_THAH    = KSETRAJNA  # 1× (TRINITY - HALVES = 1)
LAYAKARI_DUGUN   = HALVES     # 2× (Axiom)
LAYAKARI_TIGUN   = TRINITY    # 3× (Axiom)
LAYAKARI_CHOUGUN = QUARTERS   # 4× (= KRISHNA_COUNT)
```

**Verwendung mit MantraTick (venu/tick.py):**
```python
from vibe_core.mahamantra.venu.tick import MantraTick
from vibe_core.mahamantra.substrate.algorithm.maha import (
    FRAME_CHOUGUN, LAYAKARI_DUGUN, WORDS, SEVEN
)

tick = MantraTick()
for _ in range(64):
    pos = tick.position                    # 0-15 (Mahamantra)
    frame_pos = tick.tick_count % 64       # 0-63 (Chougun frame)
    observer_pos = tick.tick_count % 7     # 0-6 (Siksastakam)
    tick.advance()
```

**MantraTick = CLOCK (stateful), Layakari-Konstanten = FRAME SIZES (derived).**
