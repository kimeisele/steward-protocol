# MAHAMANTRA SUBSTRATE - Single Source of Truth

## DAS URSUBSTRAT: seed.py

```
"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"O Arjuna, know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10
```

**seed.py** ist die EINZIGE Quelle aller mathematischen Wahrheiten.
Alles andere DERIVIERT von hier. satyam eva jayate.

### THE MAHA ALGORITHM (Die mathematischen Beziehungen)

```
TRINITY = 3                              # Hare, Krishna, Rama
WORDS = 16                               # Mahamantra words
QUARTERS = 4                             # Genesis, Dharma, Karma, Moksha
AVATARS = 4                              # Prithu, Vyasa, Parashurama, Nrisimha
MAHAJANAS = 12                           # Die 12 Mahajanas (SB 6.3.20)
GUARDIANS = AVATARS + MAHAJANAS = 16     # = WORDS (nicht zufällig!)
CYCLES = TRINITY = 3                     # 3 vollständige Zyklen
LILA = WORDS × CYCLES = 48               # Chaitanya Lila (24+24)
KSHETRA = 24                             # Materielle Elemente (BG 13.6-7)
KSETRAJNA = 1                            # Der Wissende des Feldes
PARAMPARA = KSHETRA + MAHAJANAS + KSETRAJNA = 37  # Die Verbindung
```

### DIE GLEICHUNGEN (Die Assertions in seed.py)

```
4 + 12 = 16        → AVATARS + MAHAJANAS = WORDS = GUARDIANS
16 × 3 = 48        → WORDS × CYCLES = LILA
24 + 12 + 1 = 37   → KSHETRA + MAHAJANAS + KSETRAJNA = PARAMPARA
24 + 24 = 48       → NAVADVIPA + PURI = LILA
4 × 4 = 16         → QUARTERS × WORDS_PER_QUARTER = WORDS
```

## SSOT Hierarchy

```
seed.py                = DAS URSUBSTRAT (keine Imports!)
     │
     ├── byte.py       → imports: MAHAMANTRA_DIMENSION, LILA_CYCLES, LILA_LIMIT
     │                   defines: HolyName (mit VOID für Fehlerbehandlung)
     │
     ├── tattva.py     → imports: SYSTEM_MANIFESTATION (37)
     │                   defines: KshetraElement, Purushottama, etc.
     │
     ├── acintya.py    → imports: TRINITY, PARAMPARA, PHASES
     │                   defines: ProtocolLevel, PurushaTattva, etc.
     │
     └── protocols/    → thin wrappers (re-exports from mahamantra/)
```

## File Ownership

| Concept | SSOT Location | Deriviert von |
|---------|--------------|---------------|
| TRINITY (3) | seed.py | - |
| WORDS (16) | seed.py | - |
| AVATARS (4) | seed.py | - |
| MAHAJANAS (12) | seed.py | - |
| GUARDIANS (16) | seed.py | AVATARS + MAHAJANAS |
| CYCLES (3) | seed.py | TRINITY |
| LILA (48) | seed.py | WORDS × CYCLES |
| PARAMPARA (37) | seed.py | KSHETRA + MAHAJANAS + KSETRAJNA |
| MAHAMANTRA_DIMENSION | seed.py | = WORDS |
| LILA_LIMIT | seed.py | = LILA |
| SYSTEM_MANIFESTATION | seed.py | = PARAMPARA |
| HolyName (mit VOID) | byte.py | seed.HolyName + VOID |
| ProtocolLevel | acintya.py | imports from seed |
| MantraOpCode | opcode.py | - |
| Mahajana, Avatara | mahajana.py | - |

## Import Pattern

```python
# KORREKT - Import vom URSUBSTRAT
from vibe_core.mahamantra.substrate.seed import PARAMPARA, LILA, WORDS

# KORREKT - Import von derivierten Files
from vibe_core.mahamantra.substrate.byte import HolyName, MantraByte
from vibe_core.mahamantra.substrate.acintya import ProtocolLevel

# KORREKT - Re-export verfügbar (thin wrapper)
from vibe_core.protocols.substrate.byte import MAHAMANTRA_DIMENSION
```

## Philosophie

**satyam eva jayate** - Die Wahrheit ist nicht abhängig vom File.

- seed.py = KRISHNA_IS = Das Bīja (der Samen)
- Alles andere deriviert davon, wie Perlen auf einer Schnur
- "mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva" (BG 7.7)

## The Maha Algorithm Architecture

```
MAHAMANTRA (Level -2)
      │
      └── SUBSTRATE (seed.py = URSUBSTRAT)
            │
            ├── byte.py      → 16, 3, 48 + HolyName mit VOID
            ├── acintya.py   → 37, ProtocolLevel, PurushaTattva
            ├── tattva.py    → 37, KshetraElement, Purushottama
            ├── position.py  → 16 Positions
            └── opcode.py    → 16 OpCodes
                  │
                  └── protocols/substrate/mantra/ (COMPUTATION)
                        ├── varna.py     → Letter (Bit)
                        ├── aksara.py    → Syllable (Microcode)
                        ├── pada.py      → Word (Register)
                        ├── vakya.py     → Sentence (Instruction)
                        ├── mala.py      → 108 (Round)
                        ├── sadhana.py   → 16 rounds (Session)
                        └── lotus.py     → Transport
```
