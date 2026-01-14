# MAHAMANTRA SUBSTRATE - Single Source of Truth

## SSOT Hierarchy

```
mahamantra/substrate/     = SSOT (Konstanten, Definitionen)
protocols/substrate/      = Re-exports + Computation
protocols/substrate/mantra/ = Fraktale Berechnung
```

## File Ownership

| Concept | SSOT Location | Re-exported by |
|---------|--------------|----------------|
| MAHAMANTRA_DIMENSION (16) | mahamantra/substrate/byte.py | protocols/substrate/byte.py |
| LILA_CYCLES (3) | mahamantra/substrate/byte.py | protocols/substrate/byte.py |
| LILA_LIMIT (48) | mahamantra/substrate/byte.py | protocols/substrate/byte.py |
| PARAMPARA (37) | mahamantra/substrate/acintya.py | (todo) |
| ProtocolLevel | mahamantra/substrate/acintya.py | (todo) |
| MAHAMANTRA_POSITIONS | mahamantra/substrate/position.py | - |
| MantraOpCode | mahamantra/substrate/opcode.py | - |
| Mahajana, Avatara | mahamantra/substrate/mahajana.py | - |

## Duplicate Files (Need Consolidation)

| File | mahamantra/substrate | protocols/substrate | Action |
|------|---------------------|--------------------|----|
| byte.py | SSOT | re-exports | DONE |
| acintya.py | SSOT (662L) | mantra/ (662L) | TODO |
| tattva.py | SSOT (433L) | (422L) | TODO |
| scanner.py | SSOT | duplicate | TODO |

## The Maha Algorithm

```
MAHAMANTRA (Level -2)
      │
      ├── SUBSTRATE (Constants, SSOT)
      │     ├── byte.py      → 16, 3, 48
      │     ├── acintya.py   → 37, ProtocolLevel
      │     ├── position.py  → 16 Positions
      │     └── opcode.py    → 16 OpCodes
      │
      └── COMPUTATION (protocols/substrate/mantra/)
            ├── varna.py     → Letter (Bit)
            ├── aksara.py    → Syllable (Microcode)
            ├── pada.py      → Word (Register)
            ├── vakya.py     → Sentence (Instruction)
            ├── mala.py      → 108 (Round)
            ├── sadhana.py   → 16 rounds (Session)
            └── lotus.py     → Transport
```

## Import Pattern

```python
# CORRECT - import from SSOT
from vibe_core.mahamantra.substrate.byte import MAHAMANTRA_DIMENSION

# ALSO OK - re-export available
from vibe_core.protocols.substrate.byte import MAHAMANTRA_DIMENSION

# COMPUTATION - use protocols/substrate/mantra/
from vibe_core.protocols.substrate.mantra.lotus import LotusNode
from vibe_core.protocols.substrate.mantra.routing import FractalLevel
```
