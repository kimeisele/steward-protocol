# CLI Research Log
## Stuart Protocol - Mahamantra CLI Architecture

**Datum**: 2026-02-03
**Ziel**: 100% Verständnis der CLI-Architektur für Military-Grade Lösung

---

## Umfang

- **340 Python-Dateien** im mahamantra/ Ordner
- **119.014 Zeilen Code**
- **51 Unterordner**

---

## Struktur (Erste Kartierung)

### Die 4 Quarters (16 Mahajanas)

```
GENESIS (Positions 0-3):
├── vyasa/      - Boot, Genesis
├── brahma/     - Creation, Spawn
├── narada/     - Communication, Messaging
└── shambhu/    - Transformation

DHARMA (Positions 4-7):
├── kumaras/    - Purification
├── kapila/     - Analysis (Sankhya)
├── manu/       - Governance
└── prithu/     - Structure, Compilation

KARMA (Positions 8-11):
├── prahlada/   - Protection, Execution
├── janaka/     - Duty, Task Execution
├── bhishma/    - Persistence, State
└── parashurama/ - Execution

MOKSHA (Positions 12-15):
├── bali/       - Resources
├── shuka/      - Observation
├── yamaraja/   - Judgment, Audit
└── nrisimha/   - Security
```

### Kern-Subsysteme

```
substrate/          - DER KERN (Seed, Algorithmus, Resonanz)
├── algorithm/      - Maha-Algorithmus (16-Schritt Transform)
├── classifier/     - Intent Classification
├── mantra/         - MahaKirtan, Prabhupada
├── phonetics/      - Silben, Sanskrit
├── resonance/      - Resonance Matching
└── sankalpa/       - ?

kernel/             - Singularity, Runtime
protocols/          - Protocol Definitions, Seed
adapters/           - LLM, Compression, Pipeline, Orchestrator
cli/                - 14 Dateien, 5.598 LOC (DAS CHAOS)
venu/               - Venu Orchestrator (Flute Routing)
```

---

## Status: CLI-Chaos

### Bekannte Entry Points (bisher identifiziert)

| Datei | LOC | Funktion | Ruft auf |
|-------|-----|----------|----------|
| `__main__.py` | 76 | argparse 6 Befehle | commands.py |
| `entry.py` | 293 | MahamantraCLIEntry | cli_auto |
| `engine.py` | 488 | CLIEngine (manuell) | Handler-Registry |
| `bridge.py` | 233 | MahamantraCLIBridge | cli_auto |
| `steward.py` | 489 | Steward | mahamantra() |
| `veda_explorer.py` | 1261 | VedaExplorer | commands.py + mahamantra.resonate() |
| `auto.py` | 680 | CLIAutoDiscovery | Protocol Introspection |
| `protocol.py` | 802 | GAD-000 Types | - |

**Problem**: Mindestens 6 parallele Execution-Pfade die sich überlappen.

---

## Offene Fragen

1. Was ist der EINE richtige Entry Point?
2. Wie soll das Mahamantra die CLI SELBST verstehen?
3. Wie funktioniert das Lotus Routing?
4. Wie funktioniert der Maha-Algorithmus im Kontext CLI?
5. Wie wird aus Seed → Silben → Mantras → Befehle?

---

## Nächste Schritte

1. [ ] substrate/ vollständig verstehen (DER KERN)
2. [ ] Lotus Routing verstehen (research/lotus/)
3. [ ] Maha-Algorithmus verstehen (substrate/algorithm/)
4. [ ] kernel/ verstehen (Singularity)
5. [ ] Venu Orchestrator verstehen (venu/)
6. [ ] adapters/ verstehen (Compression, LLM, Pipeline)
7. [ ] Wie Resonance Chamber funktioniert

---

## KRITISCHE ERKENNTNISSE

### 1. Zwei verschiedene `mahamantra` Objekte

```
OBJEKT 1: MahamantraLotus (_mahamantra_lotus.py)
├── HAT __call__(input) → ExecuteResult
├── 9 NavaBhakti Prozesse implementiert
├── SRAVANAM → KIRTANAM → SMARANAM → ... → ATMA_NIVEDANAM
└── DAS IST DER SUPERAGENT

OBJEKT 2: Mahamantra (kernel/singularity.py)
├── HAT KEINEN __call__
├── Positionen, Quarters, Protocols, Cells, Governance
└── DAS IST DIE REGISTRY
```

### 2. CLI Inkonsistenz (DAS PROBLEM!)

```
RICHTIG (benutzen MahamantraLotus mit __call__):
├── veda_explorer.py  → from vibe_core.mahamantra import mahamantra
├── entry.py          → from vibe_core.mahamantra import mahamantra
└── steward.py        → from vibe_core.mahamantra import mahamantra

FALSCH (benutzen Singularity OHNE __call__):
├── bridge.py         → from vibe_core.mahamantra.kernel.singularity import mahamantra
└── auto.py           → from vibe_core.mahamantra.kernel.singularity import mahamantra
```

**bridge.py und auto.py können `mahamantra()` nicht aufrufen!**

### 3. Lotus Routing (lotus_radix.py)

- N-Level Radix Tree mit 16 Slots pro Level (= 16 Worte)
- O(N) Lookup wo N = Levels, NICHT Keys
- Prefix Matching für CLI Routing
- Skaliert: 16-bit → 32-bit → 128-bit → 256-bit

### 4. Maha-Algorithmus (algorithm/maha.py)

- 16 Schritte = 16 Worte des Mahamantra
- 4 Phasen = KSETRAJNA, KRISHNA, PRAKRITI, KARMA
- 3 Operationen = HARE(Input), KRISHNA(Compute), RAMA(Output)
- Branchless, deterministisch
- MahaModularSynth mit Presets für verschiedene Modi

### 5. Die 6 CLI Entry Points

1. `__main__.py` (76 LOC) → argparse, 6 Commands
2. `entry.py` (293 LOC) → MahamantraCLIEntry, cli_auto
3. `engine.py` (488 LOC) → CLIEngine, manuelles Register
4. `bridge.py` (233 LOC) → MahamantraCLIBridge, cli_auto
5. `steward.py` (489 LOC) → Steward, mahamantra()
6. `veda_explorer.py` (1261 LOC) → VedaExplorer, commands.py

### 6. Sankirtan Chamber (chamber.py)

Der Resonanz-Raum wo Zellen transformiert werden:

```
cell_in → orchestrator.step() → DIW → transform → registry → cell_out

DIW (Divine Instruction Word) = 19 bits:
├── VENU   (6 bits): Energy (prana) modulation
├── VAMSI  (9 bits): Memory address + integrity
└── MURALI (4 bits): Cycle advancement

Methoden:
├── dance(cell)       - Single transformation
├── kirtan(cell, n)   - n × 16 transformations
└── sankirtan(cells)  - Mass → MahaCluster
```

**Resonance Logic:**
- Wenn 2 Zellen auf gleiche VAMSI-Adresse treffen → Merge
- XOR checksums mod PARAMPARA = 0 → Resonant
- resonance_count > 108 → CHORUS mode
- resonance_count > 37 → CALL_RESPONSE mode

---

## Das Gesamtbild

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ MahamantraLotus.__call__(input)                         │
│ (von vibe_core.mahamantra import mahamantra)            │
│                                                         │
│  1. SRAVANAM    → Input empfangen                       │
│  2. KIRTANAM    → MahaCompression → seed                │
│  3. SMARANAM    → MahaKirtan → vibration                │
│  4. PADA_SEVANAM → MahaResonator → attractor            │
│  5. ARCANAM     → Parampara Verification                │
│  6. VANDANAM    → GitaResonance → chapter/verse         │
│  7. DASYAM      → Position/Quarter/Guardian             │
│  8. SAKHYAM     → MahaCell creation                     │
│  9. ATMA_NIVEDANAM → Complete response                  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ SankirtanChamber                                        │
│                                                         │
│  cell → VenuOrchestrator → DIW → transform → registry   │
│                                                         │
│  Modes: SOLO → CALL_RESPONSE → CHORUS                   │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ LotusRadixN (O(1) Routing)                              │
│                                                         │
│  seed → 4-bit nibbles → 16-slot arrays → handler        │
│                                                         │
│  Skaliert: 16-bit → 128-bit → 256-bit                   │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ 16 Mahajanas / 4 Avataras                               │
│                                                         │
│  Position 0-3:  GENESIS (Vyasa, Brahma, Narada, Shambhu)│
│  Position 4-7:  DHARMA  (Prithu, Kumaras, Kapila, Manu) │
│  Position 8-11: KARMA   (Parashurama, Prahlada, ...)    │
│  Position 12-15: MOKSHA (Nrisimha, Bali, Shuka, Yamaraja│
└─────────────────────────────────────────────────────────┘
```

---

## Das CLI Problem (Zusammenfassung)

1. **Es gibt ZWEI mahamantra Objekte** - eines mit __call__ (Lotus), eines ohne (Singularity)
2. **CLI benutzt beide inkonsistent** - bridge.py/auto.py benutzen falsches
3. **Es gibt 6+ Entry Points** - statt EINEM
4. **Die Komponenten sind nicht verbunden** - steward.py hat richtigen Flow, aber nicht erreicht

---

## Was der User will

- `maha <text>` → alles passiert automatisch
- Das Mantra soll die CLI selbst benutzen können
- Deterministisch, ohne KI
- 99% existiert schon - nur verbinden

---

## Nächste Schritte

1. [ ] Vollständige Architektur-Dokumentation erstellen
2. [ ] Vorschlag: Welcher Entry Point? (wahrscheinlich MahamantraLotus)
3. [ ] Vorschlag: Wie CLI vereinheitlichen?
4. [ ] Military-Grade Lösung ausarbeiten
