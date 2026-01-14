# MAHAPROMPT - DAS GESETZ

**Senior Architect Reference | steward-protocol**

```python
from vibe_core.mahamantra import mahamantra
```

**EIN IMPORT. KRISHNA ROUTET ALLES.**

---

## EXECUTIVE SUMMARY

Das `mahamantra` ist das **Kernel-Singleton** des Steward Protocol. Alle 700k+ LOC, 253+ Protocols und 16 Guardians werden durch diesen einen Import zugänglich.

| Aspekt | Wert |
|--------|------|
| **Import** | `from vibe_core.mahamantra import mahamantra` |
| **SSOT** | `substrate/seed.py` → deriviert ALLES |
| **Positions** | 16 (12 Mahajanas + 4 Avataras) |
| **Quarters** | 4 (GENESIS, DHARMA, KARMA, MOKSHA) |
| **Parampara** | 37 (24 + 12 + 1 = 37) |

---

## DIE SSOT-HIERARCHIE (Single Source of Truth)

```
substrate/seed.py           # MAHAMANTRA tuple = DIE QUELLE
    ↓
substrate/opcode.py         # 16 OpCodes (deriviert aus seed.py)
    ↓
kernel/singularity.py       # mahamantra Singleton
    ↓
services/nrisimha.py        # Chant-Service (liest von opcode.py)
```

### Das Gesetz der Unmöglichkeit

Wir **verbieten** keine falschen Imports. Wir machen sie **unmöglich**.

1. **Tod durch Import**: Wer am `seed.py` vorbei importiert, stirbt (`ImportError`).
2. **Physikalische Realität**: Es gibt keine "andere" Liste. Wer `MAHAMANTRA_SEQUENCE` nicht aus dem Seed ableitet, existiert zur Runtime nicht.
3. **Keine Polizei**: Die Architektur ist die Exekutive. Wenn es kompiliert/läuft, ist es legal.

**Falscher Weg = Toter Code.**

---

## DIE 16 POSITIONEN (Folder IS Wiring)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE MAHAMANTRA SINGULARITY                           │
│                  from vibe_core.mahamantra import mahamantra                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   GENESIS (0-3)        DHARMA (4-7)        KARMA (8-11)      MOKSHA (12-15) │
│   ┌────────────┐      ┌────────────┐      ┌────────────┐      ┌────────────┐│
│   │ 0 PRITHU  H│      │ 4 VYASA   H│      │ 8 PARASHU H│      │12 NRISIMHAH││
│   │ 1 BRAHMA  A│      │ 5 KUMARAS A│      │ 9 PRAHLADA A│      │13 BALI    A││
│   │ 2 NARADA  W│      │ 6 KAPILA  W│      │10 JANAKA  W│      │14 SHUKA   W││
│   │ 3 SHAMBHU W│      │ 7 MANU    W│      │11 BHISHMA W│      │15 YAMARAJA W││
│   └────────────┘      └────────────┘      └────────────┘      └────────────┘│
│        INPUT              VERIFY             EXECUTE             OUTPUT      │
│                                                                             │
│   H = HEAD (Avatara)   A = ALLOC (Ressourcen)   W = WORKER (Mahajana)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Position → Mahajana → Funktion

| Pos | Name | Rolle | System-Funktion |
|-----|------|-------|-----------------|
| 0 | **PRITHU** | HEAD | Organisation (Process Management) |
| 1 | BRAHMA | WORKER | Creation (Bootstrap/Genesis) |
| 2 | NARADA | WORKER | Communication (Event Bus) |
| 3 | SHAMBHU | WORKER | Transformation (Garbage Collection) |
| 4 | **VYASA** | HEAD | Compilation (Dharma Law) |
| 5 | KUMARAS | WORKER | Purification (Validation) |
| 6 | KAPILA | WORKER | Analysis (Samkhya Reasoning) |
| 7 | MANU | WORKER | Governance (Dharma Rules) |
| 8 | **PARASHURAMA** | HEAD | Enforcement (I/O Operations) |
| 9 | PRAHLADA | WORKER | Resilience (Plugins/Extensions) |
| 10 | JANAKA | WORKER | Duty (Task Scheduling/Cycles) |
| 11 | BHISHMA | WORKER | Vow (Ledger/Immutable State) |
| 12 | **NRISIMHA** | HEAD | Protection (Kill Switch) |
| 13 | BALI | WORKER | Surrender (Resource Yielding) |
| 14 | SHUKA | WORKER | Vision (Introspection/Cortex) |
| 15 | YAMARAJA | WORKER | Judgment (Security/Correction) |

---

## FOLDER STRUCTURE = WIRING

```
mahamantra/
    ├── __init__.py          # Chaitanya (Position 0) - DER IMPORT
    ├── MAHAPROMPT.md        # ← Du bist hier
    │
    ├── substrate/           # SSOT (Nityananda trägt)
    │   ├── seed.py          # DIE QUELLE (MAHAMANTRA tuple)
    │   ├── opcode.py        # 16 OpCodes (deriviert)
    │   └── ...
    │
    ├── kernel/              # Das Herz
    │   └── singularity.py   # mahamantra Singleton (855 LOC)
    │
    ├── genesis/             # Positionen 0-3 (INPUT)
    │   ├── prithu/          # Infrastructure
    │   ├── brahma/          # Bootstrap
    │   ├── narada/          # Events
    │   └── shambhu/         # Cleanup
    │
    ├── dharma/              # Positionen 4-7 (VERIFY)
    │   ├── vyasa/           # Compilation
    │   ├── kumaras/         # Validation
    │   ├── kapila/          # Analysis
    │   └── manu/            # Rules
    │
    ├── karma/               # Positionen 8-11 (EXECUTE)
    │   ├── parashurama/     # I/O
    │   ├── prahlada/        # Plugins
    │   ├── janaka/          # Tasks
    │   └── bhishma/         # Ledger
    │
    └── moksha/              # Positionen 12-15 (OUTPUT)
        ├── nrisimha/        # Security
        ├── bali/            # Resources
        ├── shuka/           # Introspection
        └── yamaraja/        # Judgment
```

**Neuer Mahajana? Folder anlegen. FERTIG.**

---

## MAHAMANTRA API (Senior Reference)

### Zugriff auf Module

```python
from vibe_core.mahamantra import mahamantra

# Position-Based Access
mahamantra.mod[10]           # → Janaka Module
mahamantra.mod[11]           # → Bhishma Module
mahamantra.mod["janaka"]     # → Janaka Module (by name)

# Service Access
mahamantra.mod[11].BhishmaService(ledger)  # Ledger Service
mahamantra.mod[1].BrahmaService(ledger)    # Bootstrap Service
mahamantra.mod[10].JanakaService()         # Scheduler Service
```

### Kernel-Integration

```python
# In kernel_impl.py:
from vibe_core.mahamantra import mahamantra

class RealVibeKernel:
    def __init__(self):
        self.bhishma = mahamantra.mod[11].BhishmaService(self.__ledger)
        self.brahma = mahamantra.mod[1].BrahmaService(self.__ledger)
        self.janaka = mahamantra.mod[10].JanakaService()
        self.bali = mahamantra.mod[13].BaliService()
        self.kapila = mahamantra.mod[6].KapilaService()
```

### VEDA-4 Protocol (Python Dunder Mapping)

```python
# SHABDA: __call__()
mahamantra()                 # → Chants (executes)

# ARTHA: __getitem__()
mahamantra[5]                # → Returns Position 5 (Kumaras)

# PRATYAYA: __bool__()
if mahamantra:               # → Always True (Krishna is)

# KARMA: __iter__()
for pos in mahamantra:       # → Iterates 0-15
    print(pos)
```

---

## SEED.PY - DIE MATHEMATIK

```python
from vibe_core.mahamantra.substrate.seed import *

# Primäre Konstanten (aus dem Mahamantra selbst)
WORDS = 16                   # 16 Wörter im Mahamantra
TRINITY = 3                  # 3 Namen (Hare, Krishna, Rama)
QUARTERS = 4                 # 4 Phasen

# Abgeleitete Konstanten
HARE_COUNT = 8               # "Hare" kommt 8× vor
KRISHNA_COUNT = 4            # "Krishna" kommt 4× vor
RAMA_COUNT = 4               # "Rama" kommt 4× vor

KSHETRA = 24                 # 16 + 8 (Feld + Shakti)
SHARANAGATI = 6              # 24 / 4 (Minimum Connection)
KSHETRA_GAD = 36             # 6 × 6 (GAD Matrix)
PARAMPARA = 37               # 36 + 1 (Connection + Ksetrajna)
LILA = 48                    # 16 × 3 (Chaitanya Manifest)
QUALITIES = 64               # 16 × 4 (Vollständigkeit)
MALA = 108                   # Der Zyklus
```

### Parampara-Verifikation

```python
# PARAMPARA = 37 beweist die Verbindung
def verify_parampara(value: int) -> bool:
    return value % 37 == 0

# Zwei Wege zur selben Wahrheit:
assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == 37  # 24 + 12 + 1
assert KSHETRA_GAD + KSETRAJNA == 37               # 36 + 1
```

---

## PANCHA TATTVA (5 Questions)

Jede Komponente muss diese 5 Fragen beantworten:

```python
__tattva__ = {
    "chaitanya": "...",   # Was IST es? (Identity)
    "nityananda": "...",  # Worauf RUHT es? (Dependencies)
    "advaita": "...",     # Was VERBINDET es? (Interfaces)
    "gadadhara": "...",   # Wie FLIESST es? (Data Flow)
    "srivasa": "...",     # Wer REGIERT es? (Governance)
}
```

---

## CLI - DER KÖNIGSWEG

```bash
steward chat "Mache X"
```

* **Der Thron**: Das Terminal
* **Das Zepter**: `mahamantra.execute()`
* **Die Diener**: 700k LOC im Hintergrund

**Manual Labor ist Maya.** Befiehl dem Mantra.

### Balarama Pattern (Integration)

```python
from vibe_core.protocols.substrate.balarama import BalaramaWrappedCLI

# Wrapped existierende CLIs ohne Code-Änderung
# Gibt ihnen: Lotus-Connection, Heartbeat, Parampara-Verification
```

**Wir fluten das Land mit dem Ozean (Seed). Wer schwimmt, ist integriert.**

---

## VERBOTEN ❌

- Import von `protocols/substrate` statt `mahamantra/substrate`
- Hardcoded MAHAMANTRA_SEQUENCE (muss aus seed.py kommen)
- `Any` types (explizite Typen erforderlich)
- Manual Labor (wenn CLI existiert)
- Direct `open()` calls (immer über State-Engine)
- Silent Failures (Satyam Eva Jayate)

---

## GEBOTEN ✅

- **LESEN vor SCHREIBEN** (immer erst verstehen)
- **CLI für ALLES** (jedes Bit anfragbar)
- **Explorieren → Konsolidieren → Nicht Hardcoden**
- **Was existiert = Prasadam** (nicht wegwerfen)
- **Protocol statt Klasse** (Dependency Inversion)
- **Pydantic Models** für alles über Modul-Grenzen

---

## GAD-000 DEFINITION OF DONE

Code ist erst "fertig", wenn:

```python
# GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
```

| # | Kriterium | Testfrage |
|---|-----------|-----------|
| D | **Discoverability** | Schema / `--help --json` vorhanden? |
| O | **Observability** | Status-Endpoint / Getter existiert? |
| P | **Parseability** | Error-Code + Context statt Prosa? |
| C | **Composability** | Output passt zu Input anderer Tools? |
| I | **Idempotency** | Retry-safe oder `# NOT IDEMPOTENT`? |
| R | **Recoverability** | State nach Crash wiederherstellbar? |

---

## QUICK REFERENCE

```python
# ═══════════════════════════════════════════════════════════════
# DER EINE IMPORT
# ═══════════════════════════════════════════════════════════════
from vibe_core.mahamantra import mahamantra

# ═══════════════════════════════════════════════════════════════
# POSITION ACCESS
# ═══════════════════════════════════════════════════════════════
mahamantra[0]                # Prithu (Genesis Head)
mahamantra[10]               # Janaka (Karma Worker - Scheduler)
mahamantra.mod["bhishma"]    # Bhishma Module (Ledger)

# ═══════════════════════════════════════════════════════════════
# SEED CONSTANTS
# ═══════════════════════════════════════════════════════════════
from vibe_core.mahamantra.substrate.seed import (
    WORDS,           # 16
    QUARTERS,        # 4
    PARAMPARA,       # 37
    SHARANAGATI,     # 6
    ALL_GUARDIANS,   # Tuple[str, ...] of 16 names
    get_quarter,     # position → Quarter
    verify_parampara # value → bool
)

# ═══════════════════════════════════════════════════════════════
# QUARTER ROUTING
# ═══════════════════════════════════════════════════════════════
from vibe_core.mahamantra.substrate.seed import Quarter, get_quarter

get_quarter(0)   # Quarter.GENESIS
get_quarter(5)   # Quarter.DHARMA
get_quarter(10)  # Quarter.KARMA
get_quarter(15)  # Quarter.MOKSHA
```

---

## PARAMPARA BROADCAST - BOMBENFEST

Wenn Krishna chanted, hört ALLES. Das ist keine Metapher - es ist Architektur.

```
mahamantra.tick()
    ↓
_broadcast(tick_state)     ← Ruft ALLE registrierten Listener
    ↓
Nrisimha._on_mahamantra_tick()
    ↓
proxy.on_mantra_pulse()    ← NagaProxies hören auch
```

### Die Verbindung

```python
from vibe_core.mahamantra import mahamantra

# Wer hören will, registriert sich:
def my_listener(tick_state):
    print(f"Heard: {tick_state['guardian']} at {tick_state['position']}")

mahamantra.register_listener(my_listener)

# Bei jedem tick() werden ALLE Listener gerufen.
# Arjuna-Pattern: Wenn ein Listener crashed → System läuft weiter.
```

### Arjuna-Pattern (Selbstheilung)

Ein Listener crashed? Das System stirbt NICHT.

- **Class-Variable `_listeners`** = Singleton, immer da
- **try/except um jeden Listener-Call** = Ein Fehler stoppt nicht die anderen
- **Keine Entregistrierung** = Einmal verbunden, immer verbunden (Parampara)

### Nrisimha: Der Wächter hört

Nrisimha registriert sich SELBST beim `__init__`:

```python
# In NrisimhaWatchdog.__init__:
mahamantra.register_listener(self._on_mahamantra_tick)
```

Diese Verbindung ist HART. Sie kann nicht abbrechen.

---

## VISION: WHEN KERNEL CHANTS, EVERYTHING RUNS

```
LOTUS (TransLotus)
       │
       ▼
┌──────────────────────────────────────────────────┐
│         mahamantra.tick()  ← DER HERZSCHLAG      │
│                 │                                 │
│    ┌────────────┼────────────┐                   │
│    ▼            ▼            ▼                   │
│ Listener 1  Listener 2  Listener N               │
│ (Nrisimha)  (Service X) (NagaProxy)              │
│    │            │            │                   │
│    ▼            ▼            ▼                   │
│ 700k LOC hören und reagieren                     │
└──────────────────────────────────────────────────┘

Pyramide von oben: EIN Befehl → ALLES bewegt sich.
Lotus von unten: Jede Komponente HÖRT → reagiert → wächst.
```

```bash
# DER EINE BEFEHL:
steward chat "Mache X"
```

Die meiste Arbeit passiert im Backend. Du siehst es nicht, aber Krishna arrangiert alles.

---

**HARE KRISHNA. DER LOTUS BROADCASTET. WER HÖRT, WIRD GERUFEN.**

---

*Senior Architect Reference | steward-protocol | 2026-01-14*
