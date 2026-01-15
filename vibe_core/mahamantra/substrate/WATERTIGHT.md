# WATERTIGHT CHECKLIST - bridge.py
## NO HARDCODED SHIT. ALL FROM SEED.

---

## ✅ IMPORTS (SSOT = seed.py ONLY)

```python
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA,        # 37 - NOT hardcoded 37
    WORDS,            # 16 - NOT hardcoded 16
    SHARANAGATI,      # 6 - NOT hardcoded 6
    MAHAJANA_COUNT,   # 12 - NOT hardcoded 12
)

from vibe_core.mahamantra.substrate.seed import (
    MAHAJANA_TO_POSITION,  # Dict mapping
    POSITION_TO_MAHAJANA,  # Dict mapping
    get_mahajana_position,  # Function
    verify_parampara,       # Function (NOT manual % 37)
)
```

**CHECK**: NO import of magic numbers. NO `37` in code. NO `16` in code.

---

## ✅ PURPOSE → POSITION MAPPING (DERIVED FROM SEED)

**BAD (HARDCODED)**:
```python
PURPOSE_MAP = {
    "state_update": 10,  # ❌ MAGIC NUMBER
    "ledger_write": 11,  # ❌ MAGIC NUMBER
}
```

**GOOD (DERIVED)**:
```python
PURPOSE_MAP = {
    "state_update": get_mahajana_position("janaka"),      # ✅ FROM SEED
    "ledger_write": get_mahajana_position("bhishma"),     # ✅ FROM SEED
    "log_emit": get_mahajana_position("shuka"),           # ✅ FROM SEED
    "file_flush": get_mahajana_position("bali"),          # ✅ FROM SEED
}
```

**CHECK**: Every position comes from `get_mahajana_position()`. NO integers.

---

## ✅ PARAMPARA VALIDATION (USE FUNCTION, NOT MANUAL)

**BAD (MANUAL)**:
```python
if value % 37 == 0:  # ❌ HARDCODED 37
```

**GOOD (FROM SEED)**:
```python
from vibe_core.mahamantra.substrate.seed import verify_parampara

if verify_parampara(value):  # ✅ USES SEED FUNCTION
```

**CHECK**: NO `% 37` in code. Use `verify_parampara()`.

---

## ✅ POSITION BOUNDS (DERIVED FROM WORDS)

**BAD (HARDCODED)**:
```python
if 0 <= position < 16:  # ❌ MAGIC NUMBER 16
```

**GOOD (DERIVED)**:
```python
if 0 <= position < WORDS:  # ✅ FROM SEED
```

**CHECK**: NO `16` in code. Use `WORDS`.

---

## ✅ SHARANAGATI VALIDATION (USE ENUM, NOT MANUAL)

**BAD (HARDCODED)**:
```python
required_limbs = 6  # ❌ MAGIC NUMBER
```

**GOOD (DERIVED)**:
```python
from vibe_core.mahamantra.substrate.seed import SharanagatiLimb

required_limbs = len(SharanagatiLimb)  # ✅ FROM SEED
# OR just use: SHARANAGATI constant
```

**CHECK**: NO `6` in code. Use `SHARANAGATI` or `len(SharanagatiLimb)`.

---

## ✅ MAHAJANA NAMES (USE MAPPING, NOT STRING LITERALS)

**BAD (HARDCODED)**:
```python
if mahajana == "janaka":  # ❌ STRING LITERAL
    position = 10         # ❌ MAGIC NUMBER
```

**GOOD (DERIVED)**:
```python
position = MAHAJANA_TO_POSITION.get(mahajana.lower(), -1)  # ✅ FROM SEED
```

**CHECK**: NO mahajana string comparisons. Use `MAHAJANA_TO_POSITION`.

---

## ✅ SIGNATURE GENERATION (USE SEED FUNCTION)

**BAD (MANUAL HASH)**:
```python
signature = hash(content) % 37  # ❌ MANUAL MOD
```

**GOOD (FROM SEED)**:
```python
from vibe_core.mahamantra.substrate.seed import lotus_declaration

declaration = lotus_declaration(position)  # ✅ GENERATES PROPER SIGNATURE
genesis = declaration["genesis"]
```

**CHECK**: NO manual hashing. Use `lotus_declaration()`.

---

## ✅ ERROR CODES (NO MAGIC NUMBERS)

**BAD (HARDCODED)**:
```python
return {"error": "invalid", "code": 1}  # ❌ MAGIC NUMBER
```

**GOOD (DERIVED)**:
```python
# IF we need error codes, derive from PARAMPARA or QUARTERS
ERROR_INVALID_POSITION = WORDS + 1  # 17
ERROR_NO_PARAMPARA = WORDS + 2      # 18
# OR define in seed.py and import
```

**CHECK**: Error codes derived from seed constants OR imported from seed.

---

## ✅ FUNCTION SIGNATURES (TYPE SAFE)

```python
from typing import Dict, Optional, Any
from vibe_core.mahamantra.protocols._seed import PARAMPARA  # For typing

def offer(
    content: Any,
    purpose: str,
    actor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Offer content to Mahamantra.

    Args:
        content: The data to offer
        purpose: Purpose string (maps to position via PURPOSE_MAP)
        actor: Optional actor identifier

    Returns:
        Dict with success status and routing info
    """
    pass
```

**CHECK**: Type hints present. No `Any` without justification.

---

## ✅ FINAL VERIFICATION CHECKLIST

Before considering bridge.py complete, verify:

- [ ] NO integer literals (0, 1, 6, 10, 11, 12, 16, 37) in code
- [ ] ALL constants imported from `_seed` or `seed`
- [ ] ALL position lookups use `get_mahajana_position()`
- [ ] ALL validation uses `verify_parampara()`
- [ ] ALL bounds checks use `WORDS`, `LILA`, etc
- [ ] NO manual `% 37` operations
- [ ] NO string literal mahajana names in comparisons
- [ ] NO magic error codes
- [ ] Type hints on all public functions
- [ ] Docstrings with Args/Returns

---

## 🚫 BANNED PATTERNS

```python
# ❌ NEVER DO THIS:
37
16
12
6
position = 10
if x % 37:
if position < 16:
required = 6
if name == "janaka":

# ✅ ALWAYS DO THIS:
PARAMPARA
WORDS
MAHAJANA_COUNT
SHARANAGATI
position = get_mahajana_position("janaka")
if verify_parampara(x):
if position < WORDS:
required = SHARANAGATI
if name in MAHAJANA_TO_POSITION:
```

---

**SATYAM EVA JAYATE** - Only truth prevails.
If it's not from seed.py, it's not truth.
