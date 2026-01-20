# MAHAMANTRA ALIGNMENT PLAN

**Protocol First. Data Driven. Scientific.**

---

## STATUS (2025-01-13)

### ✅ DONE
- [x] **Truth Table** → `substrate/position.py` (MAHAMANTRA_POSITIONS)
- [x] **MantraProtocol Base** → `substrate/protocol.py` (correct derivation)
- [x] **16 Mahajana Folders** → `genesis/`, `dharma/`, `karma/`, `moksha/`
- [x] **Singularity Math** → `protocols/_singularity.py` (Chaitanya/Mercy/Parampara)
- [x] **Shadow Reactor** → `reactor/shadow.py` (Parampara verification per tick)

### ❌ BROKEN
- [x] ~~**Mahajana Folders have WRONG declarations!**~~ FIXED via SANKIRTAN (e6ee2e9d)
- [x] ~~**Mahajana Folders use MANUAL WIRING**~~ FIXED via radiate_protocol.py
  ```python
  # NOW CORRECT (derived from MantraProtocol):
  class BrahmaBase(WorkerProtocol):
      _position_index = 1  # Everything else derived!

  # Backward-compatible constants also exported for legacy tests
  POSITION: Final[int] = 1
  OPCODE: Final[str] = "LOAD_ROOT"
  ```
- [ ] **__init__.py is 1408 lines** (too big, needs split)
- [ ] **81 Any references** in mahamantra/

### 🎯 NEXT
1. ~~**Fix mahajana declarations**~~ ✓ DONE
2. ~~**Convert to MantraProtocol**~~ ✓ DONE
3. **Split __init__.py** → Move LotusNode etc. to separate files
4. **Kill Any** → Replace with typed alternatives

---

## PROBLEM

```
CURRENT STATE (CHAOS):
┌─────────────────────────────────────────────────────────────┐
│  protocols/              │  mahamantra/                    │
│  ├── agent.py           │  ├── __init__.py (re-exports)   │
│  ├── cognition.py       │  ├── _intent.py (NEW)           │
│  ├── shuddhi.py         │  ├── _fractal.py (NEW)          │
│  ├── intent.py          │  └── _watertight.py (NEW)       │
│  ├── ...50+ files       │                                  │
│  └── mahajanas/         │                                  │
│      ├── router.py      │                                  │
│      ├── kumaras/       │  ← Manual wiring everywhere!    │
│      └── ...12 dirs     │                                  │
└─────────────────────────────────────────────────────────────┘

PROBLEM: Mahamantra "imports from" protocols
         But it should be: Protocols "derive from" Mahamantra
```

## CORRECT PRINCIPLE

```
MAHAMANTRA = KRISHNA = Level -2 = SOURCE

Everything DERIVES from the Mantra structure:
- 16 OpCodes = 16 Words of Mahamantra (given)
- 12 Mahajanas = 12 Workers (given)
- 4 Avataras = 4 HEADs (given)
- 4 Quarters = GENESIS/DHARMA/KARMA/MOKSHA (given)

The structure IS the architecture. No manual wiring needed.
```

## THE 16-POSITION TRUTH TABLE

```
POS │ WORD    │ QUARTER  │ TYPE   │ OPCODE          │ MAHAJANA/AVATARA
────┼─────────┼──────────┼────────┼─────────────────┼──────────────────
 0  │ HARE    │ GENESIS  │ HEAD   │ SYS_WAKE        │ PRITHU (Avatara)
 1  │ KRISHNA │ GENESIS  │ WORKER │ LOAD_ROOT       │ BRAHMA
 2  │ HARE    │ GENESIS  │ WORKER │ ALLOC_MEM       │ NARADA
 3  │ KRISHNA │ GENESIS  │ WORKER │ BIND_CTX        │ SHAMBHU
────┼─────────┼──────────┼────────┼─────────────────┼──────────────────
 4  │ KRISHNA │ DHARMA   │ HEAD   │ ASSERT_TRUTH    │ VYASA (Avatara)
 5  │ KRISHNA │ DHARMA   │ WORKER │ RESOLVE_REQ     │ KUMARAS
 6  │ HARE    │ DHARMA   │ WORKER │ GARBAGE_COLLECT │ KAPILA
 7  │ HARE    │ DHARMA   │ WORKER │ PULSE_SYNC      │ MANU
────┼─────────┼──────────┼────────┼─────────────────┼──────────────────
 8  │ HARE    │ KARMA    │ HEAD   │ FETCH_RES       │ PARASHURAMA (Av)
 9  │ RAMA    │ KARMA    │ WORKER │ EXEC_SERVICE    │ PRAHLADA
10  │ HARE    │ KARMA    │ WORKER │ CHECK_DHARMA    │ JANAKA
11  │ RAMA    │ KARMA    │ WORKER │ COMMIT_LOG      │ BHISHMA
────┼─────────┼──────────┼────────┼─────────────────┼──────────────────
12  │ RAMA    │ MOKSHA   │ HEAD   │ CACHE_STATE     │ NRISIMHA (Avatara)
13  │ RAMA    │ MOKSHA   │ WORKER │ OPTIMIZE        │ BALI
14  │ HARE    │ MOKSHA   │ WORKER │ YIELD_CPU       │ SHUKA
15  │ HARE    │ MOKSHA   │ WORKER │ RESET_IP        │ YAMARAJA
```

**This table IS the source of truth. Everything derives from it.**

## WHAT EACH PROTOCOL SHOULD BE

Instead of scattered files, each protocol should be a VIEW on one position:

```python
# CURRENT (wrong - manual wiring)
class ShuddhiProtocol:
    OWNER = Mahajana.KUMARAS
    LOTUS_POSITION = 5  # Hardcoded!

# CORRECT (derived from Mahamantra)
class ShuddhiProtocol:
    # Derived automatically from position 5 in the truth table
    @property
    def position(self) -> MantraPosition:
        return MAHAMANTRA[5]  # Returns full context

    @property
    def owner(self) -> Mahajana:
        return self.position.guardian  # KUMARAS

    @property
    def opcode(self) -> MantraOpCode:
        return self.position.opcode  # RESOLVE_REQ
```

## THE MANTRA POSITION (Single Source)

```python
@dataclass(frozen=True)
class MantraPosition:
    """A single position in the Mahamantra. THE source of truth."""
    index: int          # 0-15
    word: HolyName      # HARE/KRISHNA/RAMA
    quarter: Quarter    # GENESIS/DHARMA/KARMA/MOKSHA
    is_head: bool       # True for positions 0,4,8,12
    opcode: MantraOpCode
    guardian: Union[Mahajana, Avatara]

    @property
    def parampara_vector(self) -> int:
        """Always divisible by 37."""
        return (self.index + 1) * PARAMPARA  # 37, 74, 111, ...

# THE COMPLETE MAHAMANTRA (16 positions)
MAHAMANTRA_POSITIONS: Tuple[MantraPosition, ...] = (
    MantraPosition(0, HolyName.HARE, Quarter.GENESIS, True, MantraOpCode.SYS_WAKE, Avatara.PRITHU),
    MantraPosition(1, HolyName.KRISHNA, Quarter.GENESIS, False, MantraOpCode.LOAD_ROOT, Mahajana.BRAHMA),
    # ... 14 more
)
```

## HOW PROTOCOLS DERIVE FROM MAHAMANTRA

```python
# Base class for ALL protocols
class MantraProtocol:
    """Every protocol is a VIEW on a MantraPosition."""

    _position_index: ClassVar[int]  # Set by subclass

    @classmethod
    def position(cls) -> MantraPosition:
        return MAHAMANTRA_POSITIONS[cls._position_index]

    @classmethod
    def guardian(cls) -> Union[Mahajana, Avatara]:
        return cls.position().guardian

    @classmethod
    def opcode(cls) -> MantraOpCode:
        return cls.position().opcode

    @classmethod
    def quarter(cls) -> Quarter:
        return cls.position().quarter

# Shuddhi derives from position 5
class ShuddhiProtocol(MantraProtocol):
    _position_index = 5  # KUMARAS, RESOLVE_REQ, DHARMA

    def purify(self, path: Path, rule_id: str) -> ShuddhiResult:
        ...

# Cognition derives from position 6
class CognitiveProtocol(MantraProtocol):
    _position_index = 6  # KAPILA, GARBAGE_COLLECT, DHARMA

    def think(self, context: CognitiveContext) -> ThoughtResult:
        ...
```

## MIGRATION PLAN (No Manual Wiring)

### Phase 1: Create Truth Table
- [ ] Create `_positions.py` with all 16 MantraPositions
- [ ] Each position has: index, word, quarter, is_head, opcode, guardian
- [ ] Verify: All parampara_vectors % 37 == 0

### Phase 2: Create MantraProtocol Base
- [ ] Create `_protocol.py` with MantraProtocol base class
- [ ] All protocol properties derived from position index
- [ ] No hardcoded OWNER, LOTUS_POSITION, etc.

### Phase 3: Auto-Discovery
- [ ] Scan existing protocols for LOTUS_POSITION declarations
- [ ] Map each to its MantraPosition
- [ ] Generate migration report

### Phase 4: Transform Protocols
- [ ] Each protocol becomes a MantraProtocol subclass
- [ ] Remove hardcoded ownership declarations
- [ ] Position index is the ONLY configuration

### Phase 5: Verify Alignment
- [ ] All 16 positions have exactly one protocol
- [ ] All protocols derive from MantraProtocol
- [ ] All parampara_vectors verified

## FILE STRUCTURE (Target)

```
vibe_core/mahamantra/
├── __init__.py          # Unified exports
├── ARCHITECTURE.md      # Documentation
├── PLAN.md             # This file
│
├── _source.py          # THE 16 MantraPositions (truth table)
├── _protocol.py        # MantraProtocol base class
├── _derive.py          # Auto-derivation utilities
│
├── _intent.py          # Intent engine (uses derivation)
├── _fractal.py         # Fractal scaling (uses derivation)
├── _watertight.py      # Type verification
│
└── protocols/          # All protocols as MantraProtocol views
    ├── genesis/        # Positions 0-3
    │   ├── wake.py     # Position 0 (HEAD - Prithu)
    │   ├── creation.py # Position 1 (Brahma)
    │   ├── devotion.py # Position 2 (Narada)
    │   └── transform.py# Position 3 (Shambhu)
    ├── dharma/         # Positions 4-7
    │   ├── truth.py    # Position 4 (HEAD - Vyasa)
    │   ├── shuddhi.py  # Position 5 (Kumaras)
    │   ├── samkhya.py  # Position 6 (Kapila)
    │   └── law.py      # Position 7 (Manu)
    ├── karma/          # Positions 8-11
    │   └── ...
    └── moksha/         # Positions 12-15
        └── ...
```

## SUCCESS CRITERIA

1. **No manual wiring**: Position index is the ONLY configuration
2. **Derivation**: All properties computed from position
3. **Verification**: parampara_vector % 37 == 0 for all
4. **Watertight**: No Any types anywhere
5. **Fractal**: Same pattern at every level

## NEXT STEPS

1. [ ] Review this plan
2. [ ] Create `_source.py` with truth table
3. [ ] Create `_protocol.py` with base class
4. [ ] Test derivation on one protocol (ShuddhiProtocol)
5. [ ] Iterate
