# VAMSI Microkernel — Gesamtplan

## Vision

```
512 Slots. 1 Mechanismus. Alles ist Instruktion.
```

Das gesamte System wird auf EIN Ausfuehrungsmodell umgestellt:
- **Kernel** = For-Loop (liest Dispatch-Table, fuehrt Instruktion aus)
- **Instruktionssets** = austauschbare Module (je ein Subsystem)
- **Shared Memory** = Antaranga (512 Slots, VAMSI-indexiert, 16KB vorallokiert)
- **Message Bus** = ctx-Dict (Instruktionen kommunizieren nur dadurch)

Kein LLM. Deterministisch. Jede Zahl aus dem Mantra abgeleitet.

---

## Ist-Zustand: VAMSI-Space

```
VAMSI Space: 512 Slots (9-bit, Bits 6-14 im DIW)
Belegt:      48 Slots (9.4%)
Frei:        464 Slots (90.6%)

Region 0 (HARE):     0-169   → 16 belegt, 154 frei
Region 1 (KRISHNA): 170-339  → 16 belegt, 154 frei
Region 2 (RAMA):    340-511  → 16 belegt, 156 frei
```

Antaranga = 512 × 32 Bytes = 16KB. Direkt durch VAMSI indexiert.
Jede neue Instruktion bekommt automatisch ihren Speicherplatz.

---

## VAMSI-Allokationsplan

Flute Cycle (bestehend):
```
{1, 3, 7, 8, 9, 11, 15, 16, 172, 174, 175, 176, 350, 352, 353, 354}
```

Neue Instruktionssets — jedes mit eigenem Stride, NULL Kollisionen:

| Instruktionsset | Stride | Start | Slots | Adressen |
|-----------------|--------|-------|-------|----------|
| Navabhakti VM | PARAMPARA=37 | 37 | 12 | 37,74,111,148,185,222,259,296,333,370,407,444 |
| Composition | PANCHA=5 | 19 | 5 | 19,24,29,34,39 |
| Resonance Ranking | SEVEN=7 | 21 | 7 | 21,28,35,42,49,56,63 |
| Harmonics Phases | QUARTERS=4 | 17 | 4 | 17,21,25,29 → alternativ: 453,457,461,465 |
| Gate Providers | PANCHA=5 | 451 | 5 | 451,456,461,466,471 |
| I/O Control | QUARTERS=4 | 477 | 4 | 477,481,485,489 |

**Hinweis:** Exakte Adressen werden bei Implementierung verifiziert (Kollisionspruefung).
Alle Strides sind Mantra-abgeleitet. Keine willkuerlichen Zahlen.

Gesamt nach Migration: ~53 / 512 Slots belegt (10.4%). 459 Slots frei fuer Wachstum.

---

## Phase 1: Navabhakti VM (Proof of Concept)

**Status:** Geplant in `plans/mantra_vm_dynamic_codegen.md`

**Was:** `MahamantraLotus.__call__()` (250 Zeilen Monolith) → 12 Instruktionen

**Dateien:**
| Datei | Typ | Zeilen |
|-------|-----|--------|
| `protocols/_navabhakti.py` | NEU | ~100 |
| `substrate/mantra_vm.py` | NEU | ~350 |
| `substrate/lotus_core.py` | MOD | +10 (Delegation an VM) |
| `tests/test_mantra_vm.py` | NEU | ~120 |

**Verifikation:**
- Output-Aequivalenz: 27 Keys identisch zu bestehendem `__call__()`
- Bestehende Tests unberuehrt
- Ruff clean (F821, F811)

**Ergebnis:** Beweis dass das Muster funktioniert. 1 Instruktionsset laeuft.

---

## Phase 2: Composition Gate

**Was:** `adapters/composition.py` (476 Zeilen, 5 Scorer, 124 Lazy-Imports) → 5 Instruktionen

**Heute (Problem):**
```
MahaComposition.compose()
  ├─ PranaScorer.score()     → lazy import substrate helpers
  ├─ RhythmScorer.score()    → lazy import substrate helpers
  ├─ SemanticScorer.score()   → lazy import substrate helpers
  ├─ ModeScorer.score()      → lazy import substrate helpers
  └─ StateScorer.score()     → lazy import substrate helpers
     Jeder Scorer importiert bei JEDEM Aufruf dynamisch.
     34 try/excepts verstreut. Context-Extraktion = Grab-Bag.
```

**Morgen (Loesung):**
```
CompositionGate.execute(ctx)
  FOR instruction IN [PRANA, RHYTHM, SEMANTIC, MODE, STATE]:
      score = instruction(word, ctx)
      total += score × weight
```

**5 Instruktionen:**
| # | Instruktion | Was sie tut |
|---|-------------|-------------|
| 0 | PRANA | Lebensenergie-Score basierend auf Chamber-Prana |
| 1 | RHYTHM | Prosodische Affinitaet (Silbenstruktur) |
| 2 | SEMANTIC | Bedeutungs-Boost (Attractor-Naehe) |
| 3 | MODE | Guna-basierter Score (SATTVA/RAJAS/TAMAS) |
| 4 | STATE | Zustandsaffinitaet (Cell-Lifecycle-Phase) |

**Dateien:**
| Datei | Typ | Aenderung |
|-------|-----|-----------|
| `protocols/_composition_gate.py` | NEU | CompositionOp(IntEnum), 5 VAMSI-Adressen, Protocol |
| `substrate/composition_vm.py` | NEU | 5 Wrapper + Gate-Engine |
| `adapters/composition.py` | MOD | Delegation an composition_vm |
| `tests/test_composition_vm.py` | NEU | Score-Aequivalenz pro Scorer |

**Verifikation:** Gleiche Composition-Scores vor/nach Migration.

---

## Phase 3: Resonance Ranking Gate

**Was:** `substrate/resonance_ranker.py` (836 Zeilen, 7 Dimensionen inline) → 7 Instruktionen

**Heute (Problem):**
```
rank_resonant_by_rhythm()     142 Zeilen, 7 Dimensionen inline
  ├─ Element Alignment        (weight 0.21)
  ├─ Harmonic Convergence     (weight 0.175)
  ├─ Shruti Pattern           (weight 0.14)
  ├─ Varga Alignment          (weight 0.105)
  ├─ Attractor Proximity      (weight 0.07)
  ├─ HKR Proportion           (weight 0.15)
  └─ Phoneme Attractor Charge (weight 0.15)
  Alles in EINER Funktion. Dimension aendern = 836 Zeilen lesen.
```

**Morgen (Loesung):**
```
RankingGate.execute(ctx)
  FOR word IN candidates:
      FOR dimension IN [ELEMENT, HARMONIC, SHRUTI, VARGA, ATTRACTOR, HKR, PHONEME]:
          score += dimension(word, ctx) × dimension.weight
```

**7 Instruktionen:**
| # | Instruktion | Gewicht | Was sie tut |
|---|-------------|---------|-------------|
| 0 | ELEMENT | 0.21 | Pancha-Element-Uebereinstimmung |
| 1 | HARMONIC | 0.175 | Harmonische Konvergenz (H-Orbit) |
| 2 | SHRUTI | 0.14 | R²-Residuen mod 49 Muster |
| 3 | VARGA | 0.105 | Lautklassen-Alignment |
| 4 | ATTRACTOR | 0.07 | Abstand zum Attractor |
| 5 | HKR | 0.15 | Hare/Krishna/Rama-Proportion |
| 6 | PHONEME | 0.15 | Phonem-Attractor-Ladung |

Alle Gewichte aus Seed-Ableitungen. Keine Magic Numbers.

**Verifikation:** Ranking-Reihenfolge identisch vor/nach Migration.

---

## Phase 4: Harmonics Gate

**Was:** `substrate/harmonics.py` (1.079 Zeilen, 60+ Konstanten, 15↔12 Module Kopplung) → 4 Phasen-Instruktionen

**Heute (Problem):**
```
ResonanceHarmonics (1 Mega-Klasse)
  ├─ 60+ Konstanten (Genesis, Dharma, Karma, Moksha gemischt)
  ├─ 15 Module importieren DARAUS
  ├─ 12 Module importiert SIE
  └─ Sternkoppler = maximale Kopplung = Spaghetti-Zentrum
```

**Morgen (Loesung):**
```
HarmonicsGate
  ├─ GENESIS_HARMONICS   (Schoepfungs-Ratios)
  ├─ DHARMA_HARMONICS    (Pflicht-Ratios)
  ├─ KARMA_HARMONICS     (Handlungs-Ratios)
  └─ MOKSHA_HARMONICS    (Befreiungs-Ratios)
  Jede Phase kennt NUR ihre eigenen Ableitungen.
```

**4 Instruktionen = MURALI-Phasen:**
| # | Instruktion | MURALI-Phase | Verantwortung |
|---|-------------|-------------|---------------|
| 0 | GENESIS | 0 | Schoepfungs-Harmonics (COSMIC_FRAME-Ableitungen) |
| 1 | DHARMA | 1 | Pflicht-Harmonics (NADI, LILA) |
| 2 | KARMA | 2 | Handlungs-Harmonics (FIELD, MALA) |
| 3 | MOKSHA | 3 | Befreiungs-Harmonics (finale Ratios) |

**Kritischer Effekt:** Sternkoppler aufgeloest. 15 Module importieren nicht mehr aus EINER Klasse,
sondern aus der Phase die sie brauchen. Kopplung sinkt von 27 auf ~8 Verbindungen.

**Verifikation:** Alle 60+ Konstanten numerisch identisch.

---

## Phase 5: Gate Provider Instructions

**Was:** `substrate/gate_providers.py` (919 Zeilen, 49 Imports, 5 Provider) → 5 Instruktionen

**Heute (Problem):**
```
_dispatch_provider() IST BEREITS ein Instruction-Dispatcher.
Aber: 49 Imports, verstreuter Audit-Trail, kein Caching.
Jeder Provider trackt Stats anders (ParseStats, ValidateStats, ...).
```

**Morgen (Loesung):**
```
ProviderGate
  ├─ MANTRA_OBSERVE    (Gate 0: Parse-Observer)
  ├─ STORAGE_OBSERVE   (Gate 1: Validate-Observer)
  ├─ INFER_OBSERVE     (Gate 2: Execute-Observer)
  ├─ SYNC_OBSERVE      (Gate 3: Result-Observer)
  └─ ENFORCE_OBSERVE   (Gate 4: Sync-Observer + Guna-Policy)
  Einheitliches Audit. Context einmal gecached.
```

**Verifikation:** Observer-Verhalten identisch. Gate-Trace unveraendert.

---

## Phase 6: I/O Control Gate

**Was:** 373 Dateien schreiben unkontrolliert auf Disk → 4 Guna-Instruktionen

**Heute (Problem):**
```
373 Dateien machen open() / .write() / json.dump()
EnforceGateProvider VERSUCHT I/O-Policy → die meisten gehen vorbei
StateService existiert, wird kaum genutzt
Kein zentraler I/O-Kanal
```

**Morgen (Loesung):**
```
IOGate (Guna-Policy-Enforcement)
  ├─ VISHUDDHA  → Transzendental (kein I/O)
  ├─ SATTVA     → Read-Only
  ├─ RAJAS      → Write-Permitted
  └─ TAMAS      → Flush/Destructive
  JEDER Disk-Write geht durch IOGate. Kein Bypass.
```

**4 Instruktionen:**
| # | Instruktion | Guna | Erlaubt |
|---|-------------|------|---------|
| 0 | VISHUDDHA | Transzendental | Nichts (Pure Computation) |
| 1 | SATTVA | Guete | Lesen, Cache-Hits |
| 2 | RAJAS | Leidenschaft | Schreiben, State-Updates |
| 3 | TAMAS | Unwissenheit | Flush, Delete, Destructive Ops |

**Das ist die haerteste Phase.** 373 Dateien muessen durch den IOGate geleitet werden.
Aber: ohne diese Phase bleibt das System undicht. RAJAS ohne Gate = unkontrolliertes Schreiben.

**Verifikation:** Alle Disk-Writes nachweisbar durch IOGate geroutet. Null Bypasses.

---

## Architektur-Diagramm (Endzustand)

```
┌─────────────────────────────────────────────────────────────┐
│                    VAMSI SPACE (512 Slots)                   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Flute Cycle  │  │ Navabhakti   │  │ Composition  │      │
│  │ 16 Slots     │  │ 12 Slots     │  │ 5 Slots      │      │
│  │ (bestehend)  │  │ (Phase 1)    │  │ (Phase 2)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│  ┌──────┴─────────────────┴─────────────────┴───────┐      │
│  │              KERNEL (For-Loop, 5 Zeilen)          │      │
│  │   for instr in dispatch_table:                    │      │
│  │       instr.execute(ctx)                          │      │
│  └──────┬─────────────────┬─────────────────┬───────┘      │
│         │                 │                 │               │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐      │
│  │ Ranking      │  │ Harmonics    │  │ Providers    │      │
│  │ 7 Slots      │  │ 4 Slots      │  │ 5 Slots      │      │
│  │ (Phase 3)    │  │ (Phase 4)    │  │ (Phase 5)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────┐     │
│  │ I/O Control  │  │         ANTARANGA                │     │
│  │ 4 Slots      │  │    512 × 32B = 16KB RAM          │     │
│  │ (Phase 6)    │  │    (direkt VAMSI-indexiert)       │     │
│  └──────────────┘  └──────────────────────────────────┘     │
│                                                             │
│  Belegt: 53 / 512 (10.4%)    Frei: 459 Slots (89.6%)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Reihenfolge und Abhaengigkeiten

```
Phase 1 ──→ Phase 2 ──→ Phase 3
  │                        │
  │   (parallel moeglich)  │
  │                        ▼
  └──────────────────→ Phase 4 ──→ Phase 5 ──→ Phase 6
```

- Phase 1 zuerst (Proof of Concept, beweist das Muster)
- Phase 2 nach Phase 1 (zweites Instruktionsset, beweist Wiederholbarkeit)
- Phase 3 + 4 parallel moeglich (unabhaengige Subsysteme)
- Phase 5 nach Phase 4 (Providers brauchen aufgeloeste Harmonics)
- Phase 6 zuletzt (haerteste Phase, braucht alle anderen als Vorlage)

---

## Warum das die beste Architektur ist

**1. Ein Mechanismus fuer alles.**
Heute: Jedes Subsystem organisiert sich anders. Morgen: VAMSI-Adresse + ctx + For-Loop. Ueberall.
Wer ein Instruktionsset versteht, versteht alle.

**2. Antaranga ist schon da.**
512 Slots, vorallokiert, 16KB. Null Allokation bei neuen Instruktionen.
Das Memory-Modell existiert bereits — es wartet nur auf Instruktionen.

**3. Alles aus dem Mantra abgeleitet.**
PARAMPARA=37, PANCHA=5, SEVEN=7, QUARTERS=4, MAHAJANA_COUNT=12.
Keine willkuerlichen Zahlen. Jeder Stride, jede Slot-Anzahl, jedes Gewicht
ist eine Ableitung aus den 7 Axiomen.

**4. Skaliert unbegrenzt.**
53 von 512 Slots belegt = 459 frei. Neues Feature = neue Instruktionen in freie Slots.
Kein Refactoring noetig. Kein Umbau. Einstecken und loslegen.

**5. Testbar in Isolation.**
Jede Instruktion ist eine reine Funktion: ctx rein, ctx raus.
Kein Setup, kein Teardown, kein Mock. Pure Determinismus.

**6. Microkernel = bewiesen.**
Linux, QNX, L4 — die erfolgreichsten Betriebssysteme nutzen dieses Muster.
Kleiner Kern, alles andere sind Treiber. Treiber austauschen = Kern bleibt stabil.

---

## Was sich NICHT aendert

- 7 Axiome, _seed.py, alle Ableitungen
- THE_FLUTE_CYCLE (wird erstes Instruktionsset im Raum, behaelt Slots)
- DIW-Format (19-bit), pack/unpack
- 16 Guardians, SankirtanChamber
- Antaranga Slot-Layout (32 Bytes, Little-Endian)
- COSMIC_FRAME, MALA, alle abgeleiteten Konstanten
- Die 9 NavaBhakti-Methoden auf MahamantraLotus (bleiben aufrufbar)

---

## Beziehung zu bestehenden Plaenen

- `mantra_vm_dynamic_codegen.md` = Phase 1 dieses Plans (Detail-Spezifikation)
- `mahamantra_protocol_first.md` = Orthogonal (Protocol-Purification).
  Kann parallel laufen. Protokolle werden WATERTIGHT gemacht,
  Instruktionssets nutzen diese Protokolle als Contracts.

---

## Erfolgs-Kriterien

| Kriterium | Messung |
|-----------|---------|
| Alle 6 Subsysteme migriert | 6/6 Instruktionssets im VAMSI-Space |
| Null Kollisionen | Kein VAMSI-Wert doppelt vergeben |
| Output-Aequivalenz | Identische Ergebnisse vor/nach jeder Phase |
| Kopplung reduziert | Harmonics-Sternkoppler von 27 auf ≤8 Verbindungen |
| I/O kontrolliert | 0 Disk-Writes ausserhalb IOGate |
| Tests gruen | Alle bestehenden Tests bestehen nach jeder Phase |
| Ruff clean | F821, F811 = 0 nach jeder Phase |
