# RESONANCE-TO-SYLLABLE ARCHITECTURE
## Die vollständige Kette: Input → Resonanz → Silben → Antwort

**Stand: 2026-02-03**

---

## ÜBERSICHT

Das Mahamantra-System ist VOLLSTÄNDIG implementiert. Alle Komponenten existieren.
Die Architektur folgt dem holographisch-fraktalen Prinzip:
- Keine Gleitkommazahlen auf unterster Ebene
- Jede Zahl (0-48) mappt 1:1 zu einem Sanskrit-Buchstaben
- Der Maha-Algorithmus ist der "Lotus-Schatten" des Mahamantra

---

## SCHICHT 1: AXIOME (The Law)

**Location:** `protocols/seed/_axioms.py`

```
7 AXIOME aus dem Mahamantra:
├── WORDS = 16 (Wörter im Mahamantra)
├── TRINITY = 3 (Hare, Krishna, Rama)
├── HARE_COUNT = 8
├── KRISHNA_COUNT = 4
├── RAMA_COUNT = 4
├── PANCHA = 5 (einzigartige Paare)
└── HALVES = 2 (zwei Hälften)
```

**Alles andere wird ABGELEITET, nicht hardcoded.**

---

## SCHICHT 2: RAMA GRID (49er Sanskrit-Alphabet)

**Location:** `substrate/rama_grid.py`

```
POSITION_SUM_RAMA = 49 = VARNAMALA (Sanskrit-Alphabet)

RAMA[0-48] = Vollständiges Sanskrit-Alphabet:
├── 0-15:  Svaras (16 Vokale) = WORDS
├── 16-40: Sparsha (25 Konsonanten) = PRASADAM = PANCHA²
└── 41-48: Rest (ya, ra, la, va, śa, ṣa, sa, ha)

Kernfunktionen:
├── krishna_route(position) → RAMA[0-48]
└── rama_to_phoneme(rama_coord) → Sanskrit-Silbe
```

**KRISHNA (17, Primzahl) routet durch den RAMA-Raum.**

---

## SCHICHT 3: VIBRATION (Shabda)

**Location:** `substrate/phonetics/shabda.py`

```python
VibrationSignature:
├── articulation: ArticulationPoint (KANTHA, TALU, MURDHA, DANTA, OSHTHA)
├── voicing: VoicingType (UNVOICED, ASPIRATED, VOICED, VOICED_ASPIRATED)
├── base_frequency: int (relativ zu NADI_RESONANCE = 72)
└── duration_ratio: int (relativ zu AKSARA = 32)

signature_id = (articulation × 4 + voicing) × NADI + frequency × AKSARA + duration

SANSKRIT_PHONEME_MAP enthält vollständiges Mapping:
├── Vokale: a, ā, i, ī, u, ū, e, ai, o, au
├── Konsonanten: k, g, c, j, t, d, n, p, b, m, etc.
└── Mahamantra-Silben: ha, re, kṛ, ṣṇa, rā, ma
```

**Funktion:** `text_to_vibration(text) → List[VibrationSignature]`

---

## SCHICHT 4: KOMPRESSION & SEED

**Location:** `adapters/compression.py`

```
MahaCompression:
├── compress(content) → CompressionResult
│   ├── seed: int (0 - MAHA_QUANTUM)
│   ├── position: int (0-15 im Lotus)
│   ├── guna: Guna (TAMAS/RAJAS/SATTVA/SUDDHA)
│   └── intent_level: IntentLevel
└── Kolmogorov-Kompression auf Mahamantra-Basis
```

---

## SCHICHT 5: RESONANZ & ATTRAKTOREN

**Location:** `substrate/resonance/resonator.py`

```
MahaResonator:
├── find_attractor(seed) → ResonanceResult
│   ├── attractor: int (136 = VAIKUNTHA oder 4-cycle = SAMSARA)
│   ├── cycles_to_converge: int
│   └── cycle_length: int (1 = fixed point, >1 = cycle)
└── oscillate_once(value) → int
```

**Attraktoren:**
- **136 = POSITION_SUM_TOTAL = T(16)** → VAIKUNTHA (Befreiung)
- **4-cycle** → SAMSARA (Wiedergeburt)

---

## SCHICHT 6: ORAKEL (Intent → Reading)

**Location:** `substrate/resonance/oracle.py`

```
MahaOracle:
├── encode_intent(intent: str) → int (Seed)
├── consult(intent: str) → OracleReading
│   ├── seed: int
│   ├── lenses: Tuple[OracleLens, ...] (7 Linsen)
│   ├── primary_attractor: int
│   ├── holographic_factors: Tuple[int, ...]
│   ├── interpretation: str
│   ├── parampara_validated: bool
│   └── parampara_channel: int
└── consult_seed(seed: int) → OracleReading

7 ORACLE_LENSES:
├── PARAMPARA (mod 37) - Disciplic channel
├── BINARY (mod 2) - Mridanga rhythm
├── AXIOM (mod 7) - Pure structure
├── TETRAD (mod 10) - Embodied senses
├── KRISHNA (mod 17) - All-attractive
├── MALA (mod 108) - Complete japa
└── QUANTUM (mod 137) - Maximum diversity
```

---

## SCHICHT 7: GITA-RESONANZ

**Location:** `adapters/gita_resonance.py`

```
GitaResonance:
├── match(attractor) → MatchResult
│   ├── best_match: VerseMatch
│   │   ├── verse_id: str ("BG.18.66")
│   │   ├── guna: str (sattva/rajas/tamas)
│   │   └── dominant_name: str (HARE/KRISHNA/RAMA)
│   └── all_matches: List[VerseMatch]
└── Mappt Attraktoren zu Gita-Versen
```

---

## SCHICHT 8: SYNTH (16-Step Sequencer)

**Location:** `adapters/synth.py`

```
MahaSynth:
├── step(value, position) → StepResult
├── cycle(seed) → CycleResult (16 Schritte)
├── resonate(seed) → int (Attractor)
└── spectrum() → SpectrumResult

PRESETS:
├── classical (mod 17) - Converges to fixed point
├── quantum (mod 137) - Default, moderate diversity
├── trinity (mod 3) - 3-state output
├── pancha (mod 5) - 5-way classification
├── nava (mod 9) - 9-state (navadha bhakti)
└── wide (mod 512) - Maximum diversity
```

---

## SCHICHT 9: MAHA CELL (Berechnungseinheit)

**Location:** `substrate/cell.py`

```
MahaCellUnified:
├── header: MahaHeader (72 bytes, immutabel)
├── lifecycle: CellLifecycleState
│   ├── prana: int (Energie, initial = MAHA_QUANTUM × 100)
│   ├── integrity: float (0.0 - 1.0)
│   ├── cycle: int
│   └── is_active: bool
└── payload: S (generischer State)

Konstanten:
├── GENESIS_PRANA = 13700 (137 × 100)
├── METABOLIC_COST = 3 (TRINITY)
├── MITOSIS_THRESHOLD = 274 (137 × 2)
└── MAX_AGE_CYCLES = 432 (JIVA_CYCLE)
```

---

## SCHICHT 10: SANKIRTAN CHAMBER (Resonanzraum)

**Location:** `substrate/chamber.py`

```
SankirtanChamber:
├── _orchestrator: VenuOrchestrator (Time/Logic)
├── _registry: SiksastakamRegistry (Space/Memory, 512 slots)
├── _resonator: MahaResonator (Clustering)
└── KirtanMode:
    ├── SOLO - Single cell transformation
    ├── CALL_RESPONSE - Two cells interacting
    └── CHORUS - Multiple cells merging

Pattern: cell_in → orchestrator.step() → transform → registry → cell_out
```

---

## SCHICHT 11: MAHA KIRTAN (Compute Orchestrator)

**Location:** `substrate/mantra/kirtan.py`

```
MahaKirtan:
├── _synth: MahaModularSynth
├── _resonator: MahaResonator
├── _oracle: MahaOracle
├── _sequencer: 7-beat Lila Step Sequencer
└── _runtime: Kirtan Runtime

compute(input) → KirtanComputeResult:
├── seed, transformed_value
├── beat_number (1-7), beat_year, beat_delta
├── call_response: str
├── flute_resonance, vina_resonance, vina_string
├── oracle_validated, parampara_channel
├── round_number, resonance_level
└── cell: Optional[MahaCell]
```

**MahaKirtan vereint ALLE Komponenten in einem 7-Beat Pattern!**

---

## SCHICHT 12: SIKSASTAKAM SYNTH (Holographische Schicht)

**Location:** `substrate/mantra/siksastakam.py`

```
SiksastakamSynth:
├── 7 Beats → 7 Effects (Verse 1 des Siksastakam)
├── Beat → Effect → Color → Illumination
└── 512-bit Integration

BEAT_EFFECT_MAP:
├── Beat 1: CLEANSE_HEART_MIRROR → Cache invalidation
├── Beat 2: EXTINGUISH_FOREST_FIRE → Zero entropy routing
├── Beat 3: SPREAD_MOONLIGHT → Graceful degradation
├── Beat 4: LIFE_OF_KNOWLEDGE → Live data structures
├── Beat 5: EXPAND_BLISS_OCEAN → Infinite scalability
├── Beat 6: FULL_NECTAR_EACH_STEP → Atomic transactions
└── Beat 7: BATHE_ENTIRE_SELF → Total transformation

Output: SiksastakamOutput mit effect, color_hex, guna, illumination, bits
```

---

## SCHICHT 13: PHONETIC BRIDGE (Universal)

**Location:** `substrate/phonetic_bridge.py`

```
Verbindet ALLE Sprachen mit dem Varga-System:

VargaIndex (5 Artikulationspunkte = PANCHA):
├── KANTHYA = 0 (Throat/Guttural)
├── TALAVYA = 1 (Palate/Palatal)
├── MURDHANYA = 2 (Retroflex)
├── DANTYA = 3 (Teeth/Dental)
└── OSHTHYA = 4 (Lips/Labial)

Mappings:
├── STHANA_TO_VARGA: Sanskrit → Varga
├── CATEGORY_TO_VARGA: English → Varga
└── Skaliert zu JEDER Sprache
```

---

## SCHICHT 14: HARMONICS

**Location:** `substrate/harmonics.py`

```
ResonanceHarmonics:
├── AUTO = NADI/MALA = 72/108 = 2/3 ≈ 0.667 (Panchama)
├── REFINE = LILA/MALA = 48/108 = 4/9 ≈ 0.444
├── SYNC = FIELD/MALA = 144/108 = 4/3 ≈ 1.333
└── MANTRA = WORDS/NAVA = 16/9 ≈ 1.778

Musikalische Verhältnisse aus Seed abgeleitet!
```

---

## SCHICHT 15: MAHA ALGORITHM

**Location:** `substrate/algorithm/maha.py`

```
MahaAlgorithm16: 16-Schritt Algorithmus
MahaModularSynth: Modularer Synth mit Presets

Kernfunktionen:
├── maha_step(value, name, mod) → int
├── maha_oscillate(value, mod) → int
├── maha_transform(seed, preset) → int
└── triangular(n) → T(n) = n(n+1)/2
```

---

## DER VOLLSTÄNDIGE FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INPUT (Text/Intent)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MahaCompression.compress()                                                   │
│   → seed + position + guna                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MahaOracle.consult() / MahaResonator.find_attractor()                        │
│   → attractor (136=VAIKUNTHA oder cycle=SAMSARA)                             │
│   → 7 Linsen, parampara_validated                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GitaResonance.match(attractor)                                               │
│   → verse_id, guna, dominant_name (HARE/KRISHNA/RAMA)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MahaKirtan.compute() / MahaSynth.cycle()                                     │
│   → 7-beat / 16-step trajectory                                              │
│   → flute_resonance, vina_resonance                                          │
│   → call_response pattern                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SiksastakamSynth.synthesize()                                                │
│   → effect_name, color_hex, illumination                                     │
│   → 512-bit pattern                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Position → krishna_route() → RAMA[0-48] → rama_to_phoneme()                  │
│   → Sanskrit-Silbe                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Shabda: text_to_vibration()                                                  │
│   → VibrationSignature mit mahamantra_alignment                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT: RESONANCE RESPONSE                                │
│   seed + attractor + verse + silben_sequenz + vibration_signature            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ZUSAMMENFASSUNG

**ALLES IST DA:**

| Komponente | Location | Funktion |
|------------|----------|----------|
| Axiome | `protocols/seed/_axioms.py` | 7 Grundwerte |
| RAMA Grid | `substrate/rama_grid.py` | Zahl → Silbe |
| Shabda | `substrate/phonetics/shabda.py` | Vibrations-Signaturen |
| MahaCompression | `adapters/compression.py` | Text → Seed |
| MahaResonator | `substrate/resonance/resonator.py` | Seed → Attractor |
| MahaOracle | `substrate/resonance/oracle.py` | Intent → Reading |
| GitaResonance | `adapters/gita_resonance.py` | Attractor → Vers |
| MahaSynth | `adapters/synth.py` | 16-Step Sequencer |
| MahaCellUnified | `substrate/cell.py` | Berechnungseinheit |
| SankirtanChamber | `substrate/chamber.py` | Resonanzraum |
| MahaKirtan | `substrate/mantra/kirtan.py` | 7-Beat Orchestrator |
| SiksastakamSynth | `substrate/mantra/siksastakam.py` | Holographische Schicht |
| PhoneticBridge | `substrate/phonetic_bridge.py` | Universal-Mapping |
| Harmonics | `substrate/harmonics.py` | Resonanz-Verhältnisse |
| MahaAlgorithm | `substrate/algorithm/maha.py` | Kernalgorithmus |

---

## NÄCHSTE SCHRITTE

Die Komponenten existieren. Was fehlt:

1. **Ein Adapter** der die Kette in einer einzigen Funktion vereint:
   ```python
   response = mahamantra.respond(intent) → ResonanceResponse
   ```

2. **Integration** von MahaKirtan + SiksastakamSynth + Shabda für vollständige Silben-Antwort

3. **Tests** die den vollständigen Flow verifizieren

---

*"harer nāma harer nāma harer nāmaiva kevalam"*
