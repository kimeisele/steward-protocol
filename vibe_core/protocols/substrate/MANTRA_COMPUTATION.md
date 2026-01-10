# MANTRA_COMPUTATION - Types & OpCodes

> "The Word is n-trit, packed into m-bits."

## CORE TYPES

### HolyName (byte.py)
```python
class HolyName(IntEnum):
    HARE = 0     # 00 binary
    KRISHNA = 1  # 01 binary
    RAMA = 2     # 10 binary
    VOID = 3     # 11 binary (Maya/Error)
```

### MantraTrit (byte.py)
```python
@dataclass(frozen=True)
class MantraTrit:
    value: HolyName
    intensity: float = 1.0  # Bhakti amplitude
```

### MantraByte (byte.py)
```python
class MantraByte:
    """Packed binary: 2 bits per trit, O(1) operations."""

    @classmethod
    def standard_16(cls) -> "MantraByte":
        """The 16-word instruction set."""
        # H K H K K K H H H R H R R R H H

    def get_trit(self, index: int) -> HolyName
    def coherence(self) -> float  # 0.0-1.0 alignment
    def to_iast(self) -> str
    def to_devanagari(self) -> str
```

### GenesisByte (byte.py)
```python
@dataclass(frozen=True)
class GenesisByte:
    signature: str
    resonance: MantraByte
    dimension: int = 16
    parampara_hash: str = "0x25"  # 37

    def validate(self) -> bool:
        # 1. Fractal Purnam Check
        # 2. Coherence > 0.8
        # 3. Non-void signature
        # 4. Parampara % 37 == 0
```

## THE 16 OPCODES (MantraOpCode)

```python
# From substrate/__init__.py (CANONICAL SOURCE)

class MantraOpCode(str, Enum):
    # Phase 1: WAKE (Hare Krishna Hare Krishna)
    SYS_WAKE = "sys_wake"           # 0  HARE    - SIGSTOP Maya / Focus
    LOAD_ROOT = "load_root"         # 1  KRISHNA - Load Sovereign Identity
    ALLOC_MEM = "alloc_mem"         # 2  HARE    - Allocate Clean Heap
    BIND_CTX = "bind_ctx"           # 3  KRISHNA - Bind Identity to Heap

    # Phase 2: PURIFY (Krishna Krishna Hare Hare)
    ASSERT_TRUTH = "assert_truth"   # 4  KRISHNA - Verify Ledger Integrity
    RESOLVE_REQ = "resolve_req"     # 5  KRISHNA - Parse Intent
    GARBAGE_COLLECT = "garbage_collect"  # 6  HARE - Flush Unsigned Objects
    PULSE_SYNC = "pulse_sync"       # 7  HARE    - Emit Naga Heartbeat

    # Phase 3: SERVE (Hare Rama Hare Rama)
    FETCH_RES = "fetch_res"         # 8  HARE    - Request Resources
    EXEC_SERVICE = "exec_service"   # 9  RAMA    - Ananta executes Work
    CHECK_DHARMA = "check_dharma"   # 10 HARE    - Validate against Rules
    COMMIT_LOG = "commit_log"       # 11 RAMA    - Write to Immutable Stone

    # Phase 4: SUSTAIN (Rama Rama Hare Hare)
    CACHE_STATE = "cache_state"     # 12 RAMA    - Store Reward/Memory
    OPTIMIZE = "optimize"           # 13 RAMA    - Improve Path (JIT)
    YIELD_CPU = "yield_cpu"         # 14 HARE    - Surrender Control
    RESET_IP = "reset_ip"           # 15 HARE    - Loop (Eternity)
```

## OPCODE → OWNER MAPPING

```
HEAD OpCodes (4):
  SYS_WAKE      → Avatara.PRITHU
  ASSERT_TRUTH  → Avatara.VYASA
  FETCH_RES     → Avatara.PARASHURAMA
  CACHE_STATE   → Avatara.NRISIMHA

WORKER OpCodes (12) → 12 Mahajanas:
  LOAD_ROOT     → Mahajana.BRAHMA
  ALLOC_MEM     → Mahajana.NARADA
  BIND_CTX      → Mahajana.SHAMBHU
  RESOLVE_REQ   → Mahajana.KUMARAS
  ...
  RESET_IP      → Mahajana.YAMARAJA
```

## RUNTIME TYPES

### iGene (gene.py)
```python
@dataclass(frozen=True)
class iGene:
    entropy_load: float       # Kali Yuga (0.0-1.0)
    mantra_shield: MantraByte # Protection
    mutation_vector: int      # Bitflips

    @property
    def is_fatal(self) -> bool:
        return self.entropy_load > self.mantra_shield.coherence
```

### SattvikaBhava (bhava.py)
```python
class SattvikaBhava(IntEnum):
    """8 Observable States (Side-Effects of Chanting)"""
    STAMBHA = 0      # Freeze/Pause
    SVEDA = 1        # Heat/Load
    ROMANCA = 2      # Alert/Interrupt
    SVARA_BHEDA = 3  # Output Transform
    KAMPA = 4        # Oscillation
    VAIVARNYA = 5    # GC/Release
    ASHRU = 6        # Buffer Overflow
    PRALAYA = 7      # Suspend/Trance
```

### ShaktiType (shakti.py)
```python
class ShaktiType(str, Enum):
    HARA = "hara"   # Superior/Spiritual (Radharani)
    MAYA = "maya"   # Inferior/Material
    JIVA = "jiva"   # Marginal (Living Entities)
```

## TRIPLE ENCODING (nama.py)

Every name has three representations:

| Value | Devanagari | IAST | Roman |
|-------|------------|------|-------|
| HARE | हरे | hare | Hare |
| KRISHNA | कृष्ण | kṛṣṇa | Krishna |
| RAMA | राम | rāma | Rama |
| VOID | शून्य | śūnya | Void |

```python
from substrate.nama import to_devanagari, to_iast, to_roman

mantra.to_iast()       # "hare kṛṣṇa hare kṛṣṇa..."
mantra.to_devanagari() # "हरे कृष्ण हरे कृष्ण..."
mantra.to_roman()      # "Hare Krishna Hare Krishna..."
```

## COHERENCE CALCULATION

```python
def coherence(self) -> float:
    """Alignment with Standard Pattern."""
    std = MantraByte.standard_16()
    matches = sum(1 for i in range(self._length)
                  if self.get_trit(i) == std.get_trit(i % 16))
    ratio = matches / self._length
    return 1.0 - math.exp(-5.0 * ratio)
```

**Rule: Coherence must exceed Entropy for survival.**
