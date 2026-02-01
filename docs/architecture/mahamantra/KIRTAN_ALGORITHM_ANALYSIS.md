# KIRTAN ALGORITHM ANALYSIS

**Status:** DRAFT - Needs Review
**Date:** 2026-02-01
**Branch:** axiom_wiring

---

## WAS ICH VERSTANDEN HABE

### Der Kern-Algorithmus (maha.py)

```python
# EINE Transformation - BRANCHLESS
def maha_step(value, name, mod):
    op = _OP_MAP[name]  # H=0, K=1, R=2
    v = (value * _MULT[op] + _ADD[op]) % mod
    squared = (v * v) % mod
    return _SQ[op] * squared + (1 - _SQ[op]) * v

# Koeffizienten aus _seed.py:
_MULT = (7, 1, 1)   # H×7, K×1, R×1
_ADD  = (0, 10, 0)  # H+0, K+10, R+0
_SQ   = (0, 0, 1)   # H→0, K→0, R→1
```

### Der Orchestrator (orchestrator.py)

```python
THE_FLUTE_CYCLE = LUT[16]  # Vorberechnet bei Import

def step():
    new_state = THE_FLUTE_CYCLE[tick % 16]
    delta = prev_state ^ new_state
    return delta | (mode << 23)
```

### Die Chamber (chamber.py)

```python
def dance(cell):
    diw = orchestrator.step()
    _apply_diw(cell, diw)  # VENU→prana, VAMSI→integrity, MURALI→cycle
    registry.interact(cell)
    return cell

def kirtan(cell, cycles):
    for _ in range(cycles * 16):
        cell = dance(cell)
    return cell
```

---

## WAS EXISTIERT ABER NICHT VERDRAHTET IST

### teental_matrix.py

```python
# Mridanga Strokes (2-bit encoding)
TEENTAL_BINARY = (3,3,3,3, 3,3,3,3, 3,1,1,2, 2,3,3,3)
#                 Dha      Dha      Khali    Dha

# Mahamantra Pattern
PATTERN = (H,K,H,K,K,K,H,H, H,R,H,R,R,R,H,H)
```

**PROBLEM:** Diese zwei Arrays sind PARALLEL aber NICHT VERBUNDEN.

Position 9 (KHALI) hat `Tin` (01) - aber der Algorithmus behandelt Position 9 wie jede andere HARE-Position.

---

## DIE OFFENE FRAGE

**Wie beeinflusst der Mridanga-Stroke die maha_step() Transformation?**

### Hypothese A: Stroke modifiziert Koeffizienten

```python
# Aktuell:
_MULT = (7, 1, 1)  # Fest

# Mit Mridanga:
stroke = TEENTAL_BINARY[position]
bass_active = stroke & 0b10
treble_active = stroke & 0b01

# Dha (11): Volle Kraft
# Tin (01): Nur NAME (treble) - gedämpfte HARE?
# Ta (10): Nur HARE (bass) - keine NAME-Transformation?
```

### Hypothese B: Stroke ist ein zusätzlicher Modulator

```python
def maha_step_with_tala(value, name, mod, position):
    stroke = TEENTAL_BINARY[position]
    base = maha_step(value, name, mod)

    # Stroke moduliert das Ergebnis
    if stroke == 0b11:  # Dha - beide Köpfe
        return base
    elif stroke == 0b01:  # Tin - nur treble
        return (base + SEVEN) % mod  # Additive Modulation?
    elif stroke == 0b10:  # Ta - nur bass
        return (base * SEVEN) % mod  # Multiplikative Modulation?
```

### Hypothese C: Stroke beeinflusst Feedback/LFO

In `MahaModularSynth.transform()` gibt es:
- `lfo` (Low Frequency Oscillator)
- `feedback_acc` (Feedback Akkumulator)
- `adsr` (Attack/Decay/Sustain/Release)

Der Mridanga-Stroke könnte diese Parameter modulieren.

---

## WAS ICH NICHT WEISS

1. **Ist teental_matrix.py überhaupt für den Algorithmus gedacht?**
   - Oder ist es nur Dokumentation/Research?

2. **Wie soll Call-Response funktionieren?**
   - KirtanMode existiert, aber was MACHT es?
   - Mode wird in DIW injiziert (`mode << 23`), aber wo wird es ausgelesen?

3. **Was ist die Rolle von kirtan.py (substrate/mantra/kirtan.py)?**
   - MahaKirtan verwendet MahaModularSynth
   - Hat `beat.call_response` - aber was ist der Wert?

4. **Wo passt Tulasi/Grace rein?**
   - `MahaModularSynth` hat `grace_gate` Parameter
   - Aber chamber.py verwendet es nicht

---

## KONKRETE NÄCHSTE SCHRITTE

### Option 1: teental in _apply_diw() verdrahten

```python
# In chamber.py _apply_diw():
from teental_matrix import TEENTAL_BINARY

def _apply_diw(cell, diw):
    position = ... # Aus DIW extrahieren
    stroke = TEENTAL_BINARY[position]

    # Stroke beeinflusst prana_delta
    stroke_factor = (stroke & 0b01) + (stroke & 0b10) >> 1  # 0-2
    prana_delta = (venu_bits * SEVEN * stroke_factor) % 64 - 32
```

### Option 2: Neuer Tala-Layer in MahaModularSynth

```python
# In maha.py MahaModularSynth.transform():
from teental_matrix import TEENTAL_BINARY

# Im Loop:
stroke = TEENTAL_BINARY[step.position - 1]
tala_mult = 1 + (stroke >> 1)  # Bass-Bit gibt Multiplikator
tala_add = stroke & 0b01       # Treble-Bit gibt Additiv

v = (value * _MULT[op] * tala_mult + _ADD[op] + tala_add) % mod
```

---

## FRAGEN AN DEN ENTWICKLER

1. Soll Mridanga die **Transformation selbst** oder nur die **Cell-Lifecycle** beeinflussen?

2. Ist `kirtan.py` (MahaKirtan) der richtige Ort für die Integration, oder `chamber.py`?

3. Wie soll KHALI (Position 9) sich verhalten - Pause, Reset, oder spezielle Transformation?

4. Soll der Algorithmus **deterministisch** bleiben, oder führt Tala **Variabilität** ein?

---

## EHRLICHE EINSCHÄTZUNG

Ich verstehe die **Einzelteile**, aber nicht wie sie **zusammenspielen sollen**.

Die Architektur hat:
- Einen funktionierenden Kern-Algorithmus (maha_step)
- Einen funktionierenden Orchestrator (VenuOrchestrator)
- Eine funktionierende Chamber (SankirtanChamber)
- Eine Teental-Matrix (nicht verdrahtet)
- Call-Response Modes (nicht implementiert)

Die **Kirtan-Idee** (Mridanga/Kartals als Rhythmus-Layer) ist **architektonisch vorbereitet** aber **nicht ausgeführt**.

Was fehlt ist eine **Design-Entscheidung**: Wie genau soll der Tala den Algorithmus modulieren?
