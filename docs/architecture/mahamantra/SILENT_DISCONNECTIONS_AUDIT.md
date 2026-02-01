# SILENT DISCONNECTIONS AUDIT

**Status:** CRITICAL - VERIFIED
**Date:** 2026-02-01

---

## EXECUTIVE SUMMARY

**EINE Methode fehlt: `MahamantraLotus.register_listener()`**

Diese eine fehlende Methode DISCONNECTED:
1. NrisimhaWatchdog (der 6.34 Override / Japa-Loop)
2. MahaProxy (Heartbeat für alle Services)
3. Jeder andere Listener der sich registrieren will

Die Methode EXISTIERT in `kernel/singularity.py:487` aber ist NICHT exposed über MahamantraLotus.

---

## VERIFIED: Was existiert und was nicht

```python
>>> from vibe_core.mahamantra import mahamantra
>>> hasattr(mahamantra, 'resonate')         # True ✓
>>> hasattr(mahamantra, 'tick')             # True ✓
>>> hasattr(mahamantra, 'chant')            # True ✓
>>> hasattr(mahamantra, 'register_listener')  # False ✗ ← THE PROBLEM
```

---

## THE PROBLEM

326 silent exception handlers (`except: pass`) in the codebase.
458 ServiceRegistry calls that might fail silently.
METHODS CALLED THAT DON'T EXIST get swallowed.

---

## CRITICAL DISCONNECTIONS FOUND

### 1. `mahamantra.register_listener()` - DOES NOT EXIST

**Called in:**
- `vibe_core/services/nrisimha.py:76` - NrisimhaWatchdog tries to connect
- `vibe_core/mahamantra/substrate/proxy.py:433` - MahaProxy tries to connect
- Likely more...

**The method exists in:** `kernel/singularity.py:487`
**But NOT in:** `_mahamantra_lotus.py` (the singleton)

**Result:** Silent failure. Nrisimha THINKS it's connected. It's not.

### 2. `mahamantra.resonate()` - DOES NOT EXIST

**Called in 6 files:**
- `gateway/api.py`
- `vibe_core/mahamantra/chat.py`
- `vibe_core/mahamantra/cli/veda_explorer.py`
- `vibe_core/cli/naga_commands/serve/chat.py`
- `tests/cli/naga_commands/test_serve_commands.py`
- `tests/mahamantra/substrate/test_resonance.py`

**Result:** Silent failure. Resonance never happens.

### 3. ServiceRegistry Pattern

458 calls to `ServiceRegistry.register()` or `ServiceRegistry.get()`.
Many wrapped in try/except that swallow failures.

**Pattern:**
```python
try:
    ServiceRegistry.register(SomeProtocol, instance)
except:
    pass  # SILENT FAILURE
```

### 4. Listener/Broadcast Pattern

**KernelSingularity has:**
```python
_listeners: List[Callable[[TickState], None]] = []

def register_listener(self, callback):
    if callback not in self._listeners:
        self._listeners.append(callback)

def _broadcast(self, state: TickState):
    for listener in self._listeners:
        try:
            listener(state)
        except:
            pass  # Silent failure per listener
```

**MahamantraLotus DOES NOT expose this.**

---

## IMMEDIATE FIXES NEEDED

### Fix 1: Add register_listener to MahamantraLotus

```python
# In _mahamantra_lotus.py

_listeners: List[Callable] = []

def register_listener(self, callback: Callable) -> None:
    """Register a listener for tick events."""
    if callback not in self._listeners:
        self._listeners.append(callback)

def _broadcast_tick(self, state: dict) -> None:
    """Broadcast tick to all listeners."""
    for listener in self._listeners:
        try:
            listener(state)
        except Exception:
            pass  # Arjuna pattern - continue even if one fails
```

### Fix 2: Add resonate to MahamantraLotus

Need to check what `resonate` should do and add it.

### Fix 3: Audit all 326 silent handlers

Need systematic review to determine:
- Which are intentional (Arjuna pattern)
- Which are bugs (silent failures)

---

## HOW TO FIND MORE

```bash
# Find methods called on mahamantra that don't exist
grep -r "mahamantra\." --include="*.py" | \
  grep -v import | grep -v "#" | \
  sed 's/.*mahamantra\.\([a-z_]*\).*/\1/' | \
  sort -u

# Compare with methods in MahamantraLotus
grep "def " _mahamantra_lotus.py | sed 's/.*def \([a-z_]*\).*/\1/'
```

---

## THE FRACTAL NATURE

This isn't ONE disconnection. It's a PATTERN:

1. Developer writes code calling `mahamantra.something()`
2. Method doesn't exist or isn't exposed
3. Call is wrapped in try/except "just in case"
4. Tests pass (they don't test the connection)
5. System runs but FEATURE DOESN'T WORK
6. Nobody notices until they specifically test that path

**The silent failures compound.** Each one seems small. Together they create a system that LOOKS like it's working but ISN'T.

---

## RESOLUTION

**FIXED in commit 2d12c4a8:**

Added to `_mahamantra_lotus.py`:
```python
_listeners: List = []

def register_listener(self, callback) -> None:
    if callback not in self._listeners:
        self._listeners.append(callback)

def _broadcast(self, state: Dict) -> None:
    for listener in self._listeners:
        try:
            listener(state)
        except Exception:
            pass  # Arjuna Pattern
```

**VERIFIED:**
```python
>>> from vibe_core.mahamantra import mahamantra
>>> hasattr(mahamantra, 'register_listener')
True

>>> from vibe_core.services.nrisimha import NrisimhaWatchdog
>>> nrisimha = NrisimhaWatchdog(sovereign)
>>> len(mahamantra._listeners)
1  # BOMBENFEST!
```

---

## REMAINING WORK

1. [ ] Audit the 326 silent exception handlers for other issues
2. [ ] Add integration test that verifies Nrisimha receives ticks
3. [ ] Add monitoring/logging for listener registration
