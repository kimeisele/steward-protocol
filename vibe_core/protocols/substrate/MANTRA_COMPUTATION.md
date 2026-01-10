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
# From substrate/__init__.py

class MantraOpCode(str, Enum):
    # Quarter 1: GENESIS (Vasudeva)
    SYS_WAKE = "sys_wake"           # 0  HEAD
    LOAD_ROOT = "load_root"         # 1
    ALLOC_MEM = "alloc_mem"         # 2
    BIND_CTX = "bind_ctx"           # 3

    # Quarter 2: DHARMA (Sankarshana)
    ASSERT_TRUTH = "assert_truth"   # 4  HEAD
    RESOLVE_REQ = "resolve_req"     # 5
    FETCH_RES = "fetch_res"         # 6
    COMMIT_LOG = "commit_log"       # 7

    # Quarter 3: KARMA (Pradyumna)
    FETCH_RES = "fetch_res"         # 8  HEAD
    EXEC_KARMA = "exec_karma"       # 9
    SYNC_STATE = "sync_state"       # 10
    EMIT_SIGNAL = "emit_signal"     # 11

    # Quarter 4: MOKSHA (Aniruddha)
    CACHE_STATE = "cache_state"     # 12 HEAD
    OPTIMIZE = "optimize"           # 13
    GARBAGE_COLLECT = "garbage_collect"  # 14
    RESET_IP = "reset_ip"           # 15
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
