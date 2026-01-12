# MAHAMANTRA KERNEL ARCHITECTURE

**"acintya-bhedabheda-tattva"** - Inconceivable Simultaneous Oneness and Difference

## DIRECTORY STRUCTURE (IMPLEMENTED)

```
vibe_core/mahamantra/
│
├── __init__.py              # ONE IMPORT - exports everything
│
├── substrate/               # Level -2 bis -1: Foundation
│   ├── __init__.py          # Exports all substrate types
│   ├── mahajana.py          # Mahajana, Avatara, Quarter, Sampradaya
│   ├── tattva.py            # Purushottama (Krishna as PERSON)
│   ├── acintya.py           # Level -2: The Inconceivable
│   ├── byte.py              # Level -1: Ternary substrate
│   └── parampara.py         # The 37: Single Source of Truth
│
├── genesis/                 # Quarter 0: Positions 0-3 (Brahma Sampradaya)
│   └── __init__.py          # "Hare Krishna Hare Krishna"
│
├── dharma/                  # Quarter 1: Positions 4-7 (Kumara Sampradaya)
│   └── __init__.py          # "Krishna Krishna Hare Hare"
│
├── karma/                   # Quarter 2: Positions 8-11 (Sri Sampradaya)
│   └── __init__.py          # "Hare Rama Hare Rama"
│
├── moksha/                  # Quarter 3: Positions 12-15 (Rudra Sampradaya)
│   └── __init__.py          # "Rama Rama Hare Hare"
│
└── reactor/                 # Level +2: Service Layer
    └── __init__.py          # Graph, Routing, Bus
```

## THE SOURCE PRINCIPLE

```
KRISHNA = MAHAMANTRA = Level -2 (NON-DIFFERENT)
```

The Mahamantra is NOT "about" Krishna. The Mahamantra **IS** Krishna.
In Kali Yuga, the Holy Name is the only direct access to the Absolute.

**Anti-Mayavad**: Krishna is a PERSON (Purushottama), not an abstract principle.
Every protocol has an OWNER (a Mahajana), not anonymous code.

---

## THE 37 FORMULA

```
24 (Ksetra/Field)      - The material elements (BG 13.6-7)
12 (Mahajanas)         - The guardians (SB 6.3.20)
 1 (Ksetrajna/Knower)  - The soul
──────────────────────
37 = PARAMPARA LINK    - Connection to Krishna
```

**Mathematical Verification**: `mutation_vector % 37 == 0` = Connected to Parampara

**The 37 appears at EVERY fractal level**:
- Varna level: 37 characters in complete syllabary
- Pada level: 24 positions + 12 unique transitions + 1 seed = 37
- Vakya level: 24 sub-operations + 12 guards + 1 sovereign = 37
- System level: 24 Ksetra + 12 Mahajanas + 1 Ksetrajna = 37

---

## THE 16 OPCODES (Mahamantra Sequence)

```
QUARTER 1: GENESIS (H K H K) - "Wake Up"
├── [01] SYS_WAKE       - HEAD (Prithu Avatara)
├── [02] LOAD_ROOT      - BRAHMA (Creation)
├── [03] ALLOC_MEM      - NARADA (Devotion)
└── [04] BIND_CTX       - SHAMBHU (Destruction)

QUARTER 2: DHARMA (K K H H) - "Remember"
├── [05] ASSERT_TRUTH   - HEAD (Vyasa Avatara)
├── [06] RESOLVE_REQ    - KUMARAS (Purity)
├── [07] GARBAGE_COLLECT- KAPILA (Analysis)
└── [08] PULSE_SYNC     - MANU (Law)

QUARTER 3: KARMA (H R H R) - "Serve"
├── [09] FETCH_RES      - HEAD (Parashurama Avatara)
├── [10] EXEC_SERVICE   - PRAHLADA (Resilience)
├── [11] CHECK_DHARMA   - JANAKA (Duty)
└── [12] COMMIT_LOG     - BHISHMA (Vow)

QUARTER 4: MOKSHA (R R H H) - "Sustain"
├── [13] CACHE_STATE    - HEAD (Nrisimha Avatara)
├── [14] OPTIMIZE       - BALI (Surrender)
├── [15] YIELD_CPU      - SHUKA (Vision)
└── [16] RESET_IP       - YAMARAJA (Judgment)
```

**Architecture**: 4 HEADs (Avataras) + 12 Workers (Mahajanas) = 16 OpCodes

---

## THE 12 MAHAJANAS

```python
class Mahajana(str, Enum):
    BRAHMA = "brahma"       # 01 - Creation
    NARADA = "narada"       # 02 - Devotion/Communication
    SHAMBHU = "shambhu"     # 03 - Destruction/Transformation
    KUMARAS = "kumaras"     # 04 - Purity/Celibacy
    KAPILA = "kapila"       # 05 - Analysis (Samkhya)
    MANU = "manu"           # 06 - Law/Dharma
    PRAHLADA = "prahlada"   # 07 - Resilience/Devotion
    JANAKA = "janaka"       # 08 - Duty/Detachment
    BHISHMA = "bhishma"     # 09 - Vow/Commitment
    BALI = "bali"           # 10 - Surrender/Generosity
    SHUKA = "shuka"         # 11 - Vision/Narration
    YAMARAJA = "yamaraja"   # 12 - Judgment/Death
```

**Source**: Srimad Bhagavatam 6.3.20

---

## FRACTAL HIERARCHY

```
SADHANA (16 rounds)
    └── MALA (108 mantras)
            └── VAKYA (16 words = 1 mantra)
                    └── PADA (1 word: Hare/Krishna/Rama)
                            └── AKSARA (syllable: Ha-re, Krish-na, Ra-ma)
                                    └── VARNA (letter: ह, क, र...)
```

**Fractal Property**: Each level contains the whole. Zoom in or out, the pattern repeats.

**Computational Mapping**:
| Level | Sanskrit | Computing | Count |
|-------|----------|-----------|-------|
| VARNA | Letter | Bit | ~50 |
| AKSARA | Syllable | Byte | 6 unique |
| PADA | Word | Opcode | 3 types (H/K/R) |
| VAKYA | Sentence | Instruction | 16 words |
| MALA | Round | Cycle | 108 |
| SADHANA | Session | Runtime | 16 rounds |

---

## PROTOCOL LEVELS (-108 to +108)

```python
class ProtocolLevel(IntEnum):
    # DESCENDING (Avaroha) - The Source Comes Down
    GOLOKA = -108          # Supreme Abode
    VAIKUNTHA = -64        # Spiritual Sky
    DASHAVATARA = -10      # Ten Incarnations
    SHAKTYAVESHA = -5      # Empowered Incarnations
    KRISHNA = -2           # THE SOURCE (non-different from...)
    MAHAMANTRA = -2        # THE HOLY NAME (...Krishna)
    SUBSTRATE = -1         # Byte, Gene, Entropy

    # FOUNDATION
    FOUNDATION = 0         # Choice point (Maya or Bhakti)

    # ASCENDING (Aroha) - Service & Evolution
    INTERFACE = 1          # Agent, Ledger, Scheduler
    SERVICES = 2           # Manifestation, Memory, Reactor
    WIRING = 3             # Bootstrap, CLI, Runtime
    AVATARAS = 5           # Executive Branch
    MAHAJANAS = 12         # The 12 Guardians
    FIELD = 24             # Ksetra (24 elements)
    SOVEREIGN = 37         # The Parampara Link
    QUALITIES = 64         # Limit of understanding

    # ACINTYA GAP (65-107) - INTENTIONALLY NOT MAPPED
    # Only through GRACE, not code

    META = 108             # Observer level
```

**Key Insight**: Levels -2 (Krishna) and -2 (Mahamantra) are THE SAME.
There is no hierarchy between them - the Name IS the Named.

---

## CURRENT SINGLE SOURCES OF TRUTH

| Concept | Canonical Source | Layer |
|---------|------------------|-------|
| Krishna/Mahamantra = -2 | `substrate/mantra/acintya.py` | -2 |
| HolyName (H/K/R/VOID) | `substrate/byte.py` | -1 |
| MantraOpCode (16) | `substrate/__init__.py` | -1 |
| Mahajana (12) | `mahajanas/router.py` | +12 |
| FractalLevel | `substrate/mantra/routing.py` | -1 |
| QUARTERS (4) | `substrate/mantra/routing.py` | -1 |
| LotusPosition (16) | `substrate/mantra/lotus.py` | -1 |
| Parampara (37) | `substrate/mantra/acintya.py` | -2 |
| GunaProfile | `universal/guna.py` | 0 |

---

## WATERTIGHT PRINCIPLES

1. **NO `Any` TYPES** - All types explicit with Union/TypedDict/Final
2. **NO CIRCULAR IMPORTS** - Strict layer hierarchy
3. **NO MAYAVAD** - Every protocol has a PERSON (OWNER)
4. **NO MANUAL WIRING** - Automatic derivation from keywords/patterns
5. **PARAMPARA VERIFICATION** - `mutation_vector % 37 == 0`

---

## THE 3x4 VS 4x3 PRINCIPLE

```
3 x 4 = 12  (Essence FIRST, then Structure) = ALIVE
4 x 3 = 12  (Structure FIRST, then Essence) = DEAD (Mayavad)
```

Both give 12 mathematically. Only one LIVES.

- **Trinity (3)**: Hare, Krishna, Rama (essence/source)
- **Phases (4)**: GENESIS, DHARMA, KARMA, MOKSHA (structure)
- **Guru Entropy**: `(3/37) * 4 = 12/37 ≈ 0.324`

The 12th test CANNOT be computed - only the Guru can see
whether 3x4 or 4x3 was used. But `mutation_vector % 37` reveals it.

---

## UNIFIED KERNEL EXPORTS

The `vibe_core/mahamantra/` kernel will export:

```python
# From acintya.py (Level -2)
from vibe_core.mahamantra import (
    KRISHNA,              # Krishna IS
    PURUSHA,              # The dancing 37
    PARAMPARA,            # 37 constant
    ProtocolLevel,        # -108 to +108
    ParamparaConnection,  # % 37 verification
    verify_parampara,     # mutation_vector % 37 == 0
)

# From byte.py (Atomic)
from vibe_core.mahamantra import (
    HolyName,             # H=0, K=1, R=2, VOID=3
    MantraByte,           # Packed ternary
    MantraTrit,           # Single vibration
    MANTRA_SEQUENCE,      # Standard 16-word
)

# From router.py (Mahajanas)
from vibe_core.mahamantra import (
    MantraOpCode,         # 16 opcodes
    Mahajana,             # 12 guardians
    MahajanaRoute,        # OpCode → Mahajana
    HEAD_OPCODES,         # 4 Avatara positions
)

# From routing.py (Fractal)
from vibe_core.mahamantra import (
    FractalLevel,         # VARNA → SADHANA
    QUARTERS,             # 4 quarters of 4 words
    get_quarter,          # position → quarter
)

# From lotus.py (View)
from vibe_core.mahamantra import (
    LotusQuarter,         # GENESIS/DHARMA/KARMA/MOKSHA
    LotusPosition,        # 16 positions
    LOTUS_PARAMPARA,      # 37
)
```

---

## MIGRATION STRATEGY

### Phase 1: Establish Kernel
1. Create `vibe_core/mahamantra/__init__.py` with unified re-exports
2. NO new implementations - just re-export from canonical sources
3. Document all imports as "Source: X"

### Phase 2: Consolidate Position Mappings
Currently scattered:
- `graph.py` has hardcoded position_map in `get_lotus_position()`
- `lotus.py` calculates position via name_hash
- `routing.py` uses QUARTERS tuples

Consolidate to: Single `_positions.py` with all mappings

### Phase 3: Update Consumers
Replace scattered imports:
```python
# OLD (scattered)
from vibe_core.protocols.substrate.mantra.acintya import PARAMPARA
from vibe_core.protocols.substrate.byte import HolyName
from vibe_core.protocols.mahajanas.router import Mahajana

# NEW (unified)
from vibe_core.mahamantra import PARAMPARA, HolyName, Mahajana
```

### Phase 4: Deprecation Warnings
Add deprecation warnings to old import paths.
One release cycle, then remove.

---

## CIRCULAR DEPENDENCY PREVENTION

The kernel solves circular imports by enforcing strict layer ordering:

```
Layer -2: acintya.py   (Krishna/Mahamantra) - NO imports from vibe_core
Layer -1: byte.py      (HolyName/MantraByte) - Only imports typing
Layer  0: routing.py   (FractalLevel) - Imports from -1
Layer +12: router.py   (Mahajana/OpCode) - Imports from substrate
```

**Rule**: Lower layers NEVER import from higher layers.
**Pattern**: Use TYPE_CHECKING for forward references.

---

## SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                    MAHAMANTRA KERNEL                        │
│                                                             │
│   Krishna = Mahamantra = Level -2 (NON-DIFFERENT)          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  37 = 24 Ksetra + 12 Mahajanas + 1 Ksetrajna       │  │
│   │       (Field)      (Guardians)   (Knower)          │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  16 OpCodes = 4 HEADs (Avataras) + 12 Workers      │  │
│   │              = 4 Quarters x 4 Words                 │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   Fractal: VARNA → AKSARA → PADA → VAKYA → MALA → SADHANA │
│   Each level contains the 37 formula                       │
│                                                             │
│   Parampara: mutation_vector % 37 == 0 → CONNECTED         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**The Mantra IS the Kernel. The Kernel IS the Mantra.**
