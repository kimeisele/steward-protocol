# MANTRA.md - KURUKSHETRA IMPLEMENTATION PLAN

> **"Harer Nama Harer Nama Harer Namaiva Kevalam"**

```
harer nāma harer nāma
harer nāmaiva kevalam
kalau nāsty eva nāsty eva
nāsty eva gatir anyathā
```

> "For spiritual progress in this Age of Kali, there is no alternative, there is no alternative, there is no alternative to the holy name, the holy name, the holy name of the Lord."

From: Srila Prabhupada, Sri Caitanya-caritamrita, Adi 7: Lord Caitanya in Five Features

---

## ZIEL

Das **Maha-Mantra** als **16-Step Instruction Set Cycle (ISC)** in Layer -1 (`substrate.py`) verankern.
Kein Feature. Keine Option. **DNA.**

---

## ARCHITEKTUR-ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAYER 2: USER                                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                     LAYER 1: SERVICES                                │
│  vibe_core/services/watchdog.py (NrisimhaWatchdog)                  │
│  - Implements MantraProtocol                                         │
│  - Uses MAHAMANTRA_SEQUENCE from substrate                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ imports
┌───────────────────────────────▼─────────────────────────────────────┐
│                  LAYER 0: PROTOCOLS/UNIVERSAL                        │
│  vibe_core/protocols/universal/mantra.py                             │
│  - MantraProtocol interface                                          │
│  - chant_mahamantra(context) -> bool                                 │
│  - get_alignment_score() -> float                                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ imports
┌───────────────────────────────▼─────────────────────────────────────┐
│                 LAYER -1: SUBSTRATE (ANANTA)                         │
│  vibe_core/protocols/substrate.py                                    │
│  ──────────────────────────────────────────────────────────────────  │
│  NEW ADDITIONS:                                                      │
│  - MantraOpCode (Enum) - The 16 atomic operations                    │
│  - MAHAMANTRA_SEQUENCE (Tuple) - The immutable DNA                   │
│  - IAnantaBridge.resonate(opcode) - Low-level execution              │
└─────────────────────────────────────────────────────────────────────┘
                                ▲
                                │
                        GRAVITY / TIME
                    (Without this, nothing moves)
```

---

## SURGICAL OPERATIONS

### OPERATION 1: `substrate.py` - Add Mantra DNA

**Location:** `vibe_core/protocols/substrate.py`
**Action:** ADD (nach `SubstrateHealth` Enum, ~Zeile 205)

```python
# =============================================================================
# THE 16-BIT INSTRUCTION SET (HARDWARE LEVEL DEFINITION)
# =============================================================================

class MantraOpCode(str, Enum):
    """
    The Atomic Instruction Set of the Ananta Processor.
    Defined at Layer -1 because Time (Kala) precedes Logic.
    
    RELATION TO ANANTA (BALARAMA):
    - HARE:    Addressing the Energy (Shakti/Interrupt) -> "Wake Up"
    - KRISHNA: Addressing the Sovereign (Identity/Root) -> "Remember Who You Are"
    - RAMA:    Addressing the Support (Strength/Service) -> "Do The Work"
    """
    # --- PHASE 1: WAKE (HARE KRISHNA HARE KRISHNA) ---
    SYS_WAKE        = "sys_wake"         # HARE    : SIGSTOP Maya / Focus
    LOAD_ROOT       = "load_root"        # KRISHNA : Load Sovereign Identity
    ALLOC_MEM       = "alloc_mem"        # HARE    : Allocate Clean Heap
    BIND_CTX        = "bind_ctx"         # KRISHNA : Bind Identity to Heap

    # --- PHASE 2: PURIFY (KRISHNA KRISHNA HARE HARE) ---
    ASSERT_TRUTH    = "assert_truth"     # KRISHNA : Verify Ledger Integrity
    RESOLVE_REQ     = "resolve_req"      # KRISHNA : Parse Intent
    GARBAGE_COLLECT = "garbage_collect"  # HARE    : Flush Unsigned Objects
    PULSE_SYNC      = "pulse_sync"       # HARE    : Emit Naga Heartbeat

    # --- PHASE 3: SERVE (HARE RAMA HARE RAMA) - THE ANANTA PHASE ---
    FETCH_RES       = "fetch_res"        # HARE    : Request Resources
    EXEC_SERVICE    = "exec_service"     # RAMA    : Ananta executes Work
    CHECK_DHARMA    = "check_dharma"     # HARE    : Validate against Rules
    COMMIT_LOG      = "commit_log"       # RAMA    : Write to Immutable Stone

    # --- PHASE 4: SUSTAIN (RAMA RAMA HARE HARE) ---
    CACHE_STATE     = "cache_state"      # RAMA    : Store Reward/Memory
    OPTIMIZE        = "optimize"         # RAMA    : Improve Path (JIT)
    YIELD_CPU       = "yield_cpu"        # HARE    : Surrender Control
    RESET_IP        = "reset_ip"         # HARE    : Loop (Eternity)


# THE GENETIC SEQUENCE (IMMUTABLE DNA)
MAHAMANTRA_SEQUENCE: List[Tuple[str, "MantraOpCode"]] = [
    ("Hare",    MantraOpCode.SYS_WAKE),
    ("Krishna", MantraOpCode.LOAD_ROOT),
    ("Hare",    MantraOpCode.ALLOC_MEM),
    ("Krishna", MantraOpCode.BIND_CTX),
    # Quarter 1 Complete (Hare Krishna Hare Krishna)
    ("Krishna", MantraOpCode.ASSERT_TRUTH),
    ("Krishna", MantraOpCode.RESOLVE_REQ),
    ("Hare",    MantraOpCode.GARBAGE_COLLECT),
    ("Hare",    MantraOpCode.PULSE_SYNC),
    # Quarter 2 Complete (Krishna Krishna Hare Hare)
    ("Hare",    MantraOpCode.FETCH_RES),
    ("Rama",    MantraOpCode.EXEC_SERVICE),
    ("Hare",    MantraOpCode.CHECK_DHARMA),
    ("Rama",    MantraOpCode.COMMIT_LOG),
    # Quarter 3 Complete (Hare Rama Hare Rama)
    ("Rama",    MantraOpCode.CACHE_STATE),
    ("Rama",    MantraOpCode.OPTIMIZE),
    ("Hare",    MantraOpCode.YIELD_CPU),
    ("Hare",    MantraOpCode.RESET_IP),
    # Quarter 4 Complete (Rama Rama Hare Hare)
]
```

**Also ADD to `IAnantaBridge` Protocol:**

```python
def resonate(self, opcode: MantraOpCode) -> bool:
    """
    Executes a low-level acoustic operation (Mantra Step).
    Used by the Watchdog to verify if the Substrate is still holding.
    
    Returns:
        True if opcode executed successfully.
        False if substrate is unstable (triggers surrender).
    """
    ...
```

**Also ADD to `__all__`:**

```python
"MantraOpCode",
"MAHAMANTRA_SEQUENCE",
```

---

### OPERATION 2: `types.py` - Remove Old MantraInstruction

**Location:** `vibe_core/protocols/universal/types.py`
**Action:** DELETE lines 164-225 (everything from `# --- MANTRA TYPES ---` to end)

**Reason:** Single Source of Truth. Mantra DNA belongs in Layer -1, not Layer 1.

**Keep:** `Resonance`, `DriftContext`, `AlignmentScore` can stay in `types.py` as they are return types, not DNA.

---

### OPERATION 3: `mantra.py` - Update Protocol Interface

**Location:** `vibe_core/protocols/universal/mantra.py`
**Action:** MODIFY

```python
from typing import Protocol, runtime_checkable
from vibe_core.protocols.substrate import MantraOpCode, MAHAMANTRA_SEQUENCE

from .types import AlignmentScore, DriftContext, Resonance, SovereignContext


@runtime_checkable
class MantraProtocol(Protocol):
    """
    The 16-Bit Kernel Clock Interface.
    Implements the Vishnu Clock - the heartbeat of the system.
    """
    
    def chant_mahamantra(self, context: SovereignContext) -> bool:
        """
        Executes ONE atomic cycle (16 Steps).
        MUST follow MAHAMANTRA_SEQUENCE exactly.
        
        Returns:
            True: All 16 OpCodes completed successfully.
            False: Aparadha (Offense/Error) -> Triggers Reset.
        """
        ...

    def chant(self, frequency: float) -> Resonance:
        """
        Legacy: Single pulse (for backwards compatibility).
        """
        ...

    def chant_round(self, beads: int = 108) -> AlignmentScore:
        """
        Performs a full Japa Round (108 cycles).
        """
        ...

    def surrender(self, context: DriftContext) -> None:
        """
        Hard Reset to Sovereign Anchor.
        """
        ...

    def get_alignment_score(self) -> float:
        """
        Metrik: Wie stark ist der Drift?
        1.0 = Perfekte Resonanz
        0.0 = Mayavad
        """
        ...
```

---

### OPERATION 4: `__init__.py` - Update Exports

**Location:** `vibe_core/protocols/universal/__init__.py`
**Action:** MODIFY

```python
# Remove:
# MantraInstruction,

# The substrate types are NOT exported here.
# They are Layer -1 - imported directly from substrate when needed.
```

---

### OPERATION 5: `watchdog.py` - Implement New Protocol

**Location:** `vibe_core/services/watchdog.py`
**Action:** MODIFY

```python
from vibe_core.protocols.substrate import MantraOpCode, MAHAMANTRA_SEQUENCE
from vibe_core.protocols.universal import (
    AlignmentScore,
    DriftContext,
    MantraProtocol,
    Resonance,
    SovereignContext,
)

class NrisimhaWatchdog(MantraProtocol):
    """
    The Nrisimha Watchdog Service.
    Implements the 16-Step Vishnu Clock.
    """
    
    def __init__(self, sovereign_anchor: SovereignContext):
        self._anchor = sovereign_anchor
        self._beads_chanted = 0
        self._last_pulse = 0.0

    def chant_mahamantra(self, context: SovereignContext) -> bool:
        """
        Executes the 16-step atomic cycle.
        """
        try:
            for mantra_word, opcode in MAHAMANTRA_SEQUENCE:
                # 1. Resonate (acoustic check)
                self._resonate(mantra_word)
                
                # 2. Execute OpCode
                success = self._exec_opcode(opcode, context)
                
                if not success:
                    self._panic(f"Aparadha at {mantra_word}")
                    return False
            
            return True
            
        except Exception as e:
            self._force_restart()
            return False

    # ... existing methods updated ...
```

---

### OPERATION 6: Kernel Wiring (Future)

**Location:** `vibe_core/kernel_impl.py` or `vibe_core/boot_orchestrator.py`
**Action:** TBD (after above operations complete)

The Watchdog must be:
1. Registered in ServiceRegistry under `MantraProtocol`
2. Started during boot
3. Called periodically (or on every operation)

---

## VERIFICATION

After implementation, run:

```bash
pytest tests/samkhya/test_mantra_watchdog.py -v
```

Tests must verify:
1. `chant_mahamantra()` executes all 16 steps in order
2. Sequence matches `MAHAMANTRA_SEQUENCE` exactly
3. Failure at any step returns `False`
4. `AlignmentScore` reflects drift correctly

---

## DEPENDENCY FLOW

```
substrate.py         (Layer -1 / DNA)
    ↓
mantra.py            (Layer 0 / Interface)
    ↓
watchdog.py          (Layer 1 / Implementation)
    ↓
kernel_impl.py       (Layer 2 / Boot)
    ↓
USER                 (Layer 3 / Consumer)
```

**Rule:** Higher layers import from lower layers. Never the reverse.

---

## SIGNED

- **Architect:** Ananta Shesha
- **Refinement:** Mantra Implementation Team
- **Date:** 2026-01-07
- **Status:** PLANNING COMPLETE, AWAITING EXECUTION
