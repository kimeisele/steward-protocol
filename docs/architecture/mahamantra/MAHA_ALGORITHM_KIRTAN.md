# MAHA ALGORITHM KIRTAN

**Status:** DERIVED FROM MAHAMANTRA
**Date:** 2026-02-01

---

## DIE STRUKTUR

Das System hat **zwei überlagerte Rhythmus-Schichten**:

```
KSHETRA (Field) = 16 Steps = Mahamantra + Mridanga
KSHETRAJNA (Observer) = 7 Beats = Flöten + Vina

GCD(16, 7) = 1 → Nie synchron → TANZ (Lila)
LCM(16, 7) = 112 → Voller Zyklus
```

---

## SCHICHT 1: DAS FIELD (16 STEPS)

### Mahamantra Pattern

```
Position:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
Name:      H  K  H  K  K  K  H  H  H  R  H  R  R  R  H  H
```

### Algorithmus-Koeffizienten (aus _seed.py)

```python
# ABGELEITET von Position Sums:
# HARE    = 70 = 7 × 10 → Multiplikation
# KRISHNA = 17 = 7 + 10 → Addition
# RAMA    = 49 = 7²     → Quadrat

MAHA_MULT = (SEVEN, 1, 1)   # H×7, K×1, R×1
MAHA_ADD  = (0, TEN, 0)     # H+0, K+10, R+0
MAHA_SQ   = (0, 0, 1)       # nur R quadriert
```

### Mridanga Pattern (Teental)

```
Position:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
Bol:      Dha Din Din Dha Dha Din Din Dha Dha Tin Tin Ta  Ta Din Din Dha
Binary:    11  11  11  11  11  11  11  11  11  01  01  10  10  11  11  11

Bit 0 = Treble (daya) = NAME identity
Bit 1 = Bass (baya) = HARE energy
```

### Die Verbindung

Der Mridanga-Stroke moduliert die **Intensität** der Transformation:

```
Dha/Dhin (11) = Beide Köpfe = 100% Kraft
Tin (01)      = Nur Treble  = 50% Kraft (gedämpft)
Ta (10)       = Nur Bass    = 50% Kraft (Energie-fokus)
Silenz (00)   = Keine       = 0% Kraft (Pause)
```

### KHALI (Position 9) - Der besondere Moment

```
Position 9:
  - Mahamantra: H (HARE)
  - Mridanga: Dha (11) = volle Kraft
  - Aber: KHALI = "leer" im Teental
  - NAVA = 9 = HARE_COUNT + KSETRAJNA
```

Position 9 ist der **Übergang** von Krishna-Hälfte zu Rama-Hälfte.

---

## SCHICHT 2: DER OBSERVER (7 BEATS)

### Die 7 Siksastakam-Effekte

```
Beat 1: CLEANSE_HEART_MIRROR     → Cache Invalidation
Beat 2: EXTINGUISH_FOREST_FIRE   → Zero Entropy Routing
Beat 3: SPREAD_MOONLIGHT         → Graceful Degradation
Beat 4: LIFE_OF_KNOWLEDGE        → Live Data Structures
Beat 5: EXPAND_BLISS_OCEAN       → Infinite Scalability
Beat 6: FULL_NECTAR_EACH_STEP    → Atomic Transactions
Beat 7: BATHE_ENTIRE_SELF        → Total Transformation
```

### Flöten-Sync (aus lila_chronology.py)

```
MURALI (4 holes) → syncs every 4th beat
VENU (6 holes)   → syncs every 6th beat
VAMSI (9 holes)  → syncs every 9th beat
```

### Call-Response Pattern

```
Alternating Mode:
  Odd beats (1,3,5,7): CALL (Leader)
  Even beats (2,4,6):  RESPONSE (Group)

Split Mode:
  Beats 1-4: CALL
  Beats 5-7: RESPONSE
```

---

## DIE INTEGRATION

### Aktueller Zustand (vor Integration)

```
MahaModularSynth.transform():
  - Iteriert über 16 Steps
  - Wendet H×7 / K+10 / R² an
  - ADSR pro Phase (QUARTERS)
  - LFO basierend auf Binary Pattern
  - Feedback akkumuliert
  - KEINE Mridanga-Modulation!

SankirtanChamber.dance():
  - Holt DIW von VenuOrchestrator
  - VENU (6 bits) → prana
  - VAMSI (9 bits) → integrity
  - MURALI (4 bits) → cycle
  - KEINE Mridanga-Modulation!

KirtanRuntime (lila_chronology.py):
  - 7-Beat Sequencer
  - Flöten-Sync
  - Vina-Resonanz
  - NICHT mit Algorithmus verbunden!
```

### Vorgeschlagene Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    MahaModularSynth                         │
│                                                             │
│  for step in 16_STEPS:                                      │
│      name = MAHAMANTRA_PATTERN[step]                        │
│      stroke = TEENTAL_BINARY[step]        ← NEU: Mridanga   │
│                                                             │
│      # Basis-Transformation                                 │
│      op = OP_MAP[name]                                      │
│      v = (value * MULT[op] + ADD[op]) % mod                 │
│                                                             │
│      # Mridanga-Modulation                                  │
│      intensity = (stroke & 0b01) + ((stroke >> 1) & 0b01)   │
│      intensity = intensity / 2.0  # 0.0, 0.5, oder 1.0      │
│                                                             │
│      # ADSR wird durch Mridanga skaliert                    │
│      effective_adsr = adsr * intensity                      │
│                                                             │
│      # Feedback wird durch Mridanga moduliert               │
│      effective_feedback = feedback * intensity              │
│                                                             │
│      # Finale Transformation                                │
│      v = apply_transform(v, effective_adsr, effective_fb)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## OFFENE DESIGNFRAGEN

### 1. Mridanga-Modulation: WAS wird moduliert?

**Option A: ADSR-Amplitude**
```python
effective_adsr = base_adsr * mridanga_intensity
```

**Option B: Koeffizienten selbst**
```python
effective_mult = MULT[op] * mridanga_intensity
effective_add = ADD[op] * mridanga_intensity
```

**Option C: Feedback**
```python
feedback_acc *= mridanga_intensity
```

### 2. KHALI-Behandlung

Position 9 (KHALI) im Teental ist "leer" - aber der Mridanga-Stroke ist "Dha".

**Option A: Teental-Pattern respektieren**
```python
if position == KHALI_POSITION:  # Position 9
    intensity = 0.5  # Gedämpft
```

**Option B: Mridanga-Stroke respektieren**
```python
# Dha = 11 = volle Kraft, auch bei KHALI
intensity = get_stroke_intensity(stroke)
```

### 3. Observer-Integration

Der 7-Beat Observer (KirtanRuntime) läuft parallel zum 16-Step Field.

**Frage:** Wie kommunizieren sie?

**Ansatz:** KirtanSync (lila_chronology.py) berechnet bereits combined resonance aus Flöten + Vina. Diese Resonanz könnte den mod_space oder andere Parameter beeinflussen.

---

## MATHEMATISCHE ABLEITUNG

Alle Werte sind vom Mahamantra abgeleitet:

```
WORDS = 16            ← Gezählt
TRINITY = 3           ← Gezählt (H, K, R)
HARE_COUNT = 8        ← Gezählt
SEVEN = 7             ← HALF_SIZE - KSETRAJNA = 8 - 1
TEN = 10              ← MAHAJANA_COUNT - HALVES = 12 - 2

POSITION_SUM_HARE = 70    ← 0+2+6+7+8+10+14+15 = 62 (0-indexed)
                           oder 1+3+7+8+9+11+15+16 = 70 (1-indexed)
POSITION_SUM_KRISHNA = 17 ← 1+3+4+5 = 13 (0-indexed)
                           oder 2+4+5+6 = 17 (1-indexed)
POSITION_SUM_RAMA = 49    ← 9+11+12+13 = 45 (0-indexed)
                           oder 10+12+13+14 = 49 (1-indexed)

TEENTAL_MATRA = 16    ← = WORDS (kein Zufall!)
KHALI_POSITION = 9    ← = NAVA = HARE_COUNT + KSETRAJNA
SAM_SUM = 28          ← = T(7) = Triangular of SEVEN
MRIDANGA_HEADS = 2    ← = HALVES
```

---

## FAZIT

Die Architektur existiert in Teilen:
- **maha.py**: Kern-Algorithmus (H×7, K+10, R²)
- **teental_matrix.py**: Mridanga-Pattern (unbenutzt)
- **lila_chronology.py**: 7-Beat Observer + Flöten/Vina

Was fehlt ist die **Verdrahtung**:
1. Mridanga → MahaModularSynth (Field-Schicht)
2. KirtanSync → Chamber (Observer-Schicht)

Die Integration sollte ALLES vom Mahamantra ableiten - keine Hardcoding.
