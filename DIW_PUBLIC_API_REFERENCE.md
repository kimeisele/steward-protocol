# DIW (Divine Instruction Word) - Complete Public API Reference

## Overview
The DIW is a 19-bit protocol encoding three flute components:
- **VENU** (6 bits, 0-63): Quality/Mood (Sharanagati)
- **VAMSI** (9 bits, 0-511): Process/Action (Nava Bhakti)
- **MURALI** (4 bits, 0-15): Phase/Quarter (Quarters)

Total: 19 bits = 0x7FFFF

---

## Module: `vibe_core.mahamantra.protocols.diw`

### Constants (Bit Shifts)
```python
VENU_SHIFT: Final[int] = 0          # bits 0-5
VAMSI_SHIFT: Final[int] = 6         # bits 6-14
MURALI_SHIFT: Final[int] = 15       # bits 15-18
VELOCITY_SHIFT: Final[int] = 19     # bits 19-22 (32-bit transport)
CLUSTER_SHIFT: Final[int] = 23      # bits 23-26 (32-bit transport)
CONDITION_SHIFT: Final[int] = 27    # bits 27-30 (32-bit transport)
CONDITION_MASK: Final[int] = 0xF    # 4 bits
```

### Constants (Bit Masks)
```python
VENU_MASK: Final[int] = 0x3F        # 6 bits
VAMSI_MASK: Final[int] = 0x1FF      # 9 bits
MURALI_MASK: Final[int] = 0xF       # 4 bits
DIW_MASK: Final[int] = 0x7FFFF      # 19 bits (core)
SUNYA_MASK: Final[int] = 0x80000000 # bit 31 (silence flag)
```

### Type: DIW (NamedTuple)
```python
class DIW(NamedTuple):
    venu: int      # 6 bits: Quality/Mood
    vamsi: int     # 9 bits: Process/Action
    murali: int    # 4 bits: Phase/Quarter
```

### Functions

#### `pack(venu: int, vamsi: int, murali: int) -> int`
Pack three components into a 19-bit DIW.
- **Args**: venu (0-63), vamsi (0-511), murali (0-15)
- **Returns**: 19-bit integer
- **Masking**: Automatically masks overflow values

#### `unpack(word: int) -> DIW`
Unpack a 19-bit DIW into components.
- **Args**: word (19-bit or wider, only low 19 bits used)
- **Returns**: DIW(venu, vamsi, murali)

#### `pack_full(venu: int, vamsi: int, murali: int, velocity: int = 0, cluster: int = 0, sunya: bool = False) -> int`
Pack into a full 32-bit transport word.
- **Args**: 
  - venu (6-bit), vamsi (9-bit), murali (4-bit)
  - velocity (4-bit, 0-15): intensity
  - cluster (4-bit, 0-15): routing
  - sunya (bool): silence flag
- **Returns**: 32-bit integer
- **Note**: Only 1 production caller (venu_orchestrator.py)

#### `is_sunya(word: int) -> bool`
Check if word is silence (no-op).
- **Returns**: True if bit 31 is set

#### `extract_core(word: int) -> int`
Extract the 19-bit DIW core from a 32-bit transport word.
- **Returns**: word & DIW_MASK

---

## Module: `vibe_core.mahamantra.substrate.vm.venu_orchestrator`

### Constant: THE_FLUTE_CYCLE
```python
THE_FLUTE_CYCLE: Final[Tuple[int, ...]]  # 16 pre-computed DIW entries
```
- Pre-computed at module load (O(1) access)
- Derived from MAHAMANTRA_WORD_PATTERN (SSOT)
- Each entry is a native 19-bit DIW in canonical 6-9-4 format
- Verified at load time: all entries fit in 19 bits, no zeros, all quarters represented

### Class: VenuOrchestrator

#### Constructor
```python
def __init__(self) -> None
```

#### Properties
```python
@property
def tick(self) -> int              # Current tick position
@property
def mode(self) -> int              # Current Kirtan Mode (0/1/2)
@property
def subscriber_count(self) -> int  # Number of active DIW subscribers
```

#### Core Methods

##### `step() -> int`
One step through the Mahamantra.
- **Returns**: 19-bit DIW | Mode bits (23-26) | Position bits (27-30)
- **O(1)**: Just a LUT lookup
- **Side effect**: Emits DIWEvent to all subscribers

##### `cycle() -> int`
Complete 16-step cycle.
- **Returns**: XOR of all 19-bit DIW entries (full cycle resonance)

##### `verify_divinity() -> bool`
Verify LUT structural properties (non-mutating).
- Checks: no zeros, all quarters, all names, unique VENU, cycle XOR non-zero
- **Raises**: ValueError if any check fails

#### Routing & Harmonization

##### `route(seed: int) -> Tuple[int, int, int]`
Route seed through orchestra → (venu, vamsi, murali).
- Uses SSOT constants (SEVEN, TEN) for full coverage

##### `harmonize(venu: int, vamsi: int, murali: int, velocity: int = 15, cluster_route: int = 0, sunya: bool = False) -> int`
Combine three flute states into 32-bit word.
- Delegates to `pack_full()`

##### `spell(coords: Tuple[int, ...], cycle: int = 0) -> Tuple[int, ...]`
Spell a Sanskrit word through the flute.
- Each RAMA coordinate becomes VENU field
- VAMSI encodes name-region, MURALI encodes quarter
- Emits DIWEvent for each phoneme

#### Subscriber Management

##### `subscribe(subscriber: DIWSubscriberProtocol) -> None`
Register a DIW subscriber.
- **Raises**: TypeError if doesn't implement protocol

##### `unsubscribe(subscriber: DIWSubscriberProtocol) -> None`
Remove a DIW subscriber (idempotent).

#### State Management

##### `reset() -> None`
Reset to initial state (tick=0, prev_state=0, mode=0).
- Subscribers preserved (they are wiring, not state)

##### `set_mode(mode: int) -> None`
Set Kirtan Mode (0=Solo, 1=CallResponse, 2=Chorus).
- **Raises**: TypeError/ValueError if invalid

##### `to_bytes() -> bytes`
Serialize state (tick, prev_state, mode) as 24 bytes.

##### `from_bytes(data: bytes) -> None`
Restore state from serialized bytes.
- Validates against SSOT bounds
- Backwards compatible with 16-byte snapshots

#### Static Methods

##### `is_sunya(word: int) -> bool`
Check if instruction is silence.

##### `extract_diw(full_word: int) -> int`
Extract 19-bit DIW from 32-bit word.

---

## Module: `vibe_core.mahamantra.protocols._venu`

### Type: DIWEvent (TypedDict)
```python
class DIWEvent(TypedDict):
    diw: int       # 19-bit Divine Instruction Word
    tick: int      # Absolute tick count (0..COSMIC_FRAME-1)
    position: int  # Position in 16-beat cycle (0..WORDS-1)
    phase: int     # Quarter/phase (0..QUARTERS-1) = MURALI
    venu: int      # Quality/Mood (6 bits)
    vamsi: int     # Process/Action (9 bits)
    murali: int    # Phase/Quarter (4 bits)
    mode: int      # Kirtan mode (0/1/2)
```

### Protocol: DIWSubscriberProtocol
```python
@runtime_checkable
class DIWSubscriberProtocol(Protocol):
    @property
    def subscriber_name(self) -> str:
        """Human-readable name for logging/telemetry."""
        ...
    
    def on_diw(self, event: DIWEvent) -> None:
        """Called on every tick with current DIW."""
        ...
```

---

## Import Paths

### From diw.py
```python
from vibe_core.mahamantra.protocols.diw import (
    # Shifts
    VENU_SHIFT, VAMSI_SHIFT, MURALI_SHIFT,
    VELOCITY_SHIFT, CLUSTER_SHIFT, CONDITION_SHIFT, CONDITION_MASK,
    # Masks
    VENU_MASK, VAMSI_MASK, MURALI_MASK, DIW_MASK, SUNYA_MASK,
    # Type
    DIW,
    # Functions
    pack, unpack, pack_full, is_sunya, extract_core,
)
```

### From venu_orchestrator.py
```python
from vibe_core.mahamantra.substrate.vm.venu_orchestrator import (
    THE_FLUTE_CYCLE,
    VenuOrchestrator,
    DIWEvent,
    DIWSubscriberProtocol,
)
```

### From _venu.py
```python
from vibe_core.mahamantra.protocols._venu import (
    DIWEvent,
    DIWSubscriberProtocol,
)
```

---

## Key Rules

1. **ALWAYS use `unpack()` for DIW consumers** — never manual bit-shifts
2. **`pack_full()` has 1 production caller** — venu_orchestrator.py only
3. **THE_FLUTE_CYCLE is static** — 16 entries, pre-computed at module load
4. **DIW is 19 bits** — 0x7FFFF is the canonical mask
5. **VAMSI has two separate uses**:
   - chamber._apply_diw(): VAMSI → 3 name-regions (H/K/R) via `vamsi // 170`
   - mantra_vm.py: VAMSI as dispatch keys for pipeline instructions

