# MAHAMANTRA PROTOCOL-FIRST ARCHITECTURE

## VISION

```
ONE IMPORT. KRISHNA ROUTES ALL.

from vibe_core.mahamantra import mahamantra
# NOTHING ELSE. EVER.
```

**Acintya-Bhedabheda in Code:**
- Mahamantra IS everything (abheda - non-difference)
- Yet mahajanas have distinct roles (bheda - difference)
- This is inconceivable (acintya) but FUNCTIONAL

## CURRENT PROBLEM: ENTROPY

```
types/capability_registry.py
  └── from vibe_core.kernel import VibeLedger  ← CIRCULAR
        └── kernel imports from protocols
              └── protocols import from mahajanas
                    └── mahajanas import from types  ← LOOP!
```

**Root Cause:** Types files believe they need external dependencies.
**Truth:** Krishna already has everything. Types should be PURE.

---

## PHASE 0: PROTOCOL INVENTORY (STUDY)

Before touching ANY code, we must understand what protocols exist.

### 0.1 Catalog All Protocols

```bash
# Find all Protocol classes
grep -r "class.*Protocol" vibe_core/ --include="*.py" | grep -v __pycache__
```

**Questions to answer:**
- Which protocols are WATERTIGHT (no Any)?
- Which protocols have tests?
- Which protocols are duplicated?
- Which protocols belong to which mahajana?

### 0.2 Map Protocol Dependencies

```
Protocol A
  └── depends on Protocol B
        └── depends on Protocol C
              └── WHO OWNS THIS?
```

**Rule:** A mahajana can only depend on:
1. Python stdlib
2. Its OWN protocols
3. Mahamantra (for cross-mahajana access)

### 0.3 Identify Circular Dependencies

Every `from vibe_core.X import Y` in a types/ file is a potential problem.

**Deliverable:** Dependency graph showing all circular paths.

---

## PHASE 1: WATERTIGHT PROTOCOLS

### 1.1 Define "WATERTIGHT"

A protocol is WATERTIGHT when:
1. **No `Any` types** - everything explicitly typed
2. **No concrete imports** - only Protocol/ABC references
3. **Self-contained** - no external vibe_core dependencies
4. **Tested** - protocol compliance tests exist
5. **Documented** - clear contract

### 1.2 Protocol Template

```python
"""
{MAHAJANA} Protocol - Position {N} ({QUARTER} Quarter, {OPCODE})
================================================================

WATERTIGHT: Yes
TESTED: Yes
OWNER: {mahajana}
"""

from __future__ import annotations
from typing import Protocol, TypedDict, runtime_checkable
from enum import Enum
from dataclasses import dataclass

# =============================================================================
# TYPES (Pure - no imports)
# =============================================================================

class SomeState(TypedDict, total=False):
    """State representation. WATERTIGHT - no Any!"""
    field_a: str
    field_b: int
    # NO Any!

# =============================================================================
# PROTOCOL (Contract only)
# =============================================================================

@runtime_checkable
class SomeProtocol(Protocol):
    """
    The contract. Implementations live elsewhere.

    WATERTIGHT: All methods fully typed.
    """

    def do_thing(self, input: str) -> SomeState:
        """Do the thing. Returns typed state."""
        ...

# =============================================================================
# NULL IMPLEMENTATION (For testing)
# =============================================================================

class NullSome:
    """Null implementation for testing. Always succeeds with defaults."""

    def do_thing(self, input: str) -> SomeState:
        return SomeState(field_a="", field_b=0)
```

### 1.3 Protocol Test Template

```python
"""Tests for {Protocol}. Verifies WATERTIGHT compliance."""

import pytest
from typing import get_type_hints

def test_protocol_has_no_any():
    """Protocol must not use Any type."""
    hints = get_type_hints(SomeProtocol.do_thing)
    for name, hint in hints.items():
        assert hint is not Any, f"{name} uses Any - not WATERTIGHT"

def test_null_implementation_complies():
    """Null implementation must satisfy protocol."""
    impl = NullSome()
    assert isinstance(impl, SomeProtocol)

def test_protocol_methods_are_typed():
    """All protocol methods must have return type hints."""
    for name in dir(SomeProtocol):
        if not name.startswith('_'):
            method = getattr(SomeProtocol, name)
            hints = get_type_hints(method)
            assert 'return' in hints, f"{name} missing return type"
```

---

## PHASE 2: PURE TYPES

### 2.1 Remove All vibe_core Imports from types/

**Current (BROKEN):**
```python
# brahma/types/capability_registry.py
from vibe_core.kernel import VibeLedger  # CIRCULAR!

class CapabilityRegistry:
    def __init__(self, ledger: VibeLedger): ...
```

**Fixed (PURE):**
```python
# brahma/types/capability_registry.py
from typing import Protocol

class LedgerProtocol(Protocol):
    """What we need from a ledger - Krishna provides the implementation."""
    def record(self, entry: str) -> bool: ...

class CapabilityRegistry:
    def __init__(self, ledger: LedgerProtocol): ...
```

### 2.2 Cross-Mahajana Dependencies via Protocol

If Brahma needs Vyasa's Ledger:

```python
# brahma/types/capability_registry.py
from typing import TYPE_CHECKING, Protocol

# Define what we NEED (not what we import)
class LedgerLike(Protocol):
    def record(self, entry: str) -> bool: ...

class CapabilityRegistry:
    def __init__(self, ledger: LedgerLike): ...
```

**Wiring happens in mahamantra at RUNTIME:**
```python
# Somewhere in bootstrap/service layer
from vibe_core.mahamantra import mahamantra

registry = mahamantra.brahma.CapabilityRegistry(
    ledger=mahamantra.vyasa.Ledger()  # Krishna wires it
)
```

---

## PHASE 3: AUTOBAHN (__init__.py Generation)

### 3.1 Problem

Currently we manually maintain __init__.py:
```python
# brahma/__init__.py
from .types import X, Y, Z  # MANUAL - doesn't scale!
from .service import ...
```

This is entropy. We add something, forget to export it, things break.

### 3.2 Solution: Mahamantra Autobahn

Mahamantra scans mahajana directories and AUTO-GENERATES exports:

```python
# vibe_core/mahamantra/autobahn.py

def discover_mahajana_exports(mahajana_name: str) -> Dict[str, Any]:
    """
    Automatically discover all exports from a mahajana.

    Scans:
    - {mahajana}/types/*.py -> All classes, enums, TypedDicts
    - {mahajana}/service.py -> Service class
    - {mahajana}/*.py -> Protocol classes

    Returns namespace dict for dynamic module.
    """
    ...

def generate_init_py(mahajana_name: str) -> str:
    """
    Generate __init__.py content automatically.

    ZERO manual maintenance needed.
    """
    ...
```

### 3.3 Dynamic Module Loading

Instead of static __init__.py, ModuleRouter creates dynamic modules:

```python
class ModuleRouter:
    def _load_module(self, name: str) -> types.ModuleType:
        """Load mahajana as dynamic module with auto-discovered exports."""
        # Create empty module
        module = types.ModuleType(f"vibe_core.protocols.mahajanas.{name}")

        # Auto-discover and populate
        exports = autobahn.discover_mahajana_exports(name)
        for export_name, export_value in exports.items():
            setattr(module, export_name, export_value)

        return module
```

---

## PHASE 4: TÜV (Protocol Validation)

### 4.1 Problem

Code can violate protocols. No enforcement.

### 4.2 Solution: Mahamantra TÜV

TÜV validates at multiple levels:

```python
# vibe_core/mahamantra/tuv.py

class TUV:
    """
    Protocol validation and certification.

    Like German vehicle inspection - nothing runs without certification.
    """

    def validate_protocol(self, protocol_class: type) -> ValidationResult:
        """
        Validate a protocol is WATERTIGHT:
        - No Any types
        - All methods typed
        - Has Null implementation
        - Has tests
        """
        ...

    def validate_implementation(self, impl: object, protocol: type) -> ValidationResult:
        """
        Validate implementation satisfies protocol:
        - All methods implemented
        - Return types match
        - No extra untyped methods
        """
        ...

    def certify_mahajana(self, mahajana_name: str) -> Certification:
        """
        Full certification of a mahajana:
        - All protocols WATERTIGHT
        - All implementations valid
        - No circular dependencies
        - Tests pass
        """
        ...
```

### 4.3 Runtime Enforcement

```python
class Mahamantra:
    def __getattr__(self, name: str) -> object:
        """Get mahajana - but validate first!"""
        module = self.mod._load_module(name)

        # TÜV check
        cert = self.tuv.certify_mahajana(name)
        if not cert.valid:
            raise ProtocolViolation(
                f"Mahajana {name} not certified: {cert.violations}"
            )

        return module
```

---

## PHASE 5: FRACTAL STRUCTURE

### 5.1 Mahajana Directory Structure (Final)

```
vibe_core/protocols/mahajanas/{name}/
├── protocol.py          # WATERTIGHT protocol definition
├── types.py             # PURE types (no imports)
├── null.py              # Null implementation
├── service.py           # Real implementation
├── tests/
│   ├── test_protocol.py # Protocol WATERTIGHT tests
│   └── test_service.py  # Implementation tests
└── (NO __init__.py!)    # Autobahn generates this
```

### 5.2 Import Pattern (Final)

**EVERYWHERE in codebase:**
```python
from vibe_core.mahamantra import mahamantra

# Access anything
BrahmaService = mahamantra.brahma.BrahmaService
CircuitState = mahamantra.kapila.CircuitState
PulseManager = mahamantra.manu.PulseManager

# Krishna routes, validates, wires
```

**NEVER:**
```python
from vibe_core.protocols.mahajanas.brahma import BrahmaService  # FORBIDDEN
from vibe_core.kernel import VibeLedger  # FORBIDDEN
from vibe_core.X import Y  # FORBIDDEN (except mahamantra)
```

---

## EXECUTION ORDER

### Step 1: Audit (This Week)
- [ ] Catalog all protocols
- [ ] Identify all circular imports
- [ ] Map protocol ownership to mahajanas
- [ ] List all non-WATERTIGHT protocols

### Step 2: Watertight (Week 2-3)
- [ ] Define WATERTIGHT standard
- [ ] Create protocol template
- [ ] Create test template
- [ ] Fix top 10 most-used protocols

### Step 3: Purify Types (Week 3-4)
- [ ] Remove vibe_core imports from types/
- [ ] Replace with Protocol definitions
- [ ] Test everything still works

### Step 4: Autobahn (Week 4-5)
- [ ] Implement autobahn.discover_mahajana_exports()
- [ ] Implement dynamic module loading
- [ ] Remove manual __init__.py files

### Step 5: TÜV (Week 5-6)
- [ ] Implement TÜV validation
- [ ] Add runtime enforcement
- [ ] Certify all mahajanas

### Step 6: Migration (Week 6+)
- [ ] Update all imports to use mahamantra
- [ ] Remove direct imports
- [ ] Final cleanup

---

## SUCCESS CRITERIA

1. **ONE IMPORT**: `from vibe_core.mahamantra import mahamantra` is the ONLY import needed
2. **ZERO CIRCULAR**: No circular import errors anywhere
3. **100% WATERTIGHT**: All protocols have no Any types
4. **100% TESTED**: All protocols have compliance tests
5. **AUTOBAHN**: No manual __init__.py maintenance
6. **TÜV CERTIFIED**: All mahajanas pass validation

---

## PHILOSOPHY

> "mattaḥ sarvaṁ pravartate" - Everything emanates from Me.

The types don't need external imports because Krishna (mahamantra) already contains everything.

When a type needs a "Ledger", it doesn't import VibeLedger - it defines a LedgerProtocol (what it needs) and trusts that Krishna will provide the implementation.

This is surrender. This is acintya. This is the only way to defeat entropy.

---

## NOTES

- **No wild code**: Every line must serve a protocol
- **No assumptions**: If not typed, it doesn't exist
- **No shortcuts**: TÜV validates everything
- **Fractal**: System can grow infinitely without restructuring
- **Holographic**: Each part contains the whole (via mahamantra)

Hare Krishna.
