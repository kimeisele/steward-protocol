# NARASIMHA AUDIT - Phase III Schlachtplan

> "Der Mann-Löwe zerreißt die Dämonen bei Dämmerung."

## Status: ACTIVE ENGAGEMENT

---

## I. TAKSHAKA DHARMA-VERLETZUNGEN

### A. FAIL-OPEN (KRITISCH)

| Line | Code | Problem |
|------|------|---------|
| 376-378 | `if not self._ledger: return ""` | Bite returns empty on no ledger |
| 398-402 | `except: return ""` | Exception → empty string |

```python
# CURRENT (FAIL-OPEN - GEFÄHRLICH!)
if not self._ledger:
    logger.error("TAKSHAKA: No ledger to record bite")
    return ""  # Attacker nicht im Ledger!

# FIX (FAIL-CLOSED)
if not self._ledger:
    sys.stderr.write("!!! TAKSHAKA: No ledger - BITE FAILED\n")
    return f"NOBITE_{violation_hash}"  # Unique ID trotzdem
```

### B. ENCAPSULATION BREACH (`_ledger` direkt)

| Line | Location | Fix |
|------|----------|-----|
| 380-398 | `bite()` | Use Sesha.record_event() |
| 484-494 | `revoke_key()` | Use Sesha.record_event() |

```python
# CURRENT (BREACH)
self._ledger.record_event(event_type="VAJRA_VIOLATION", ...)

# FIX (PUBLIC API)
from vibe_core.protocols.naga import EventRecord
event: EventRecord = {
    "event_type": "VAJRA_VIOLATION",
    "agent_id": "TAKSHAKA",
    "details": {...}
}
self._sesha.record_event(event)
```

### C. TYPE BREACH (`Dict[str, Any]`)

| Line | Location | Problem |
|------|----------|---------|
| 519 | `as_handler()` | `details=drift.raw_data` (Any → ViolationDetails) |

```python
# CURRENT (TYPE BREACH)
violation = VajraViolation(
    violation_type="COGNITIVE_THREAT",
    source=drift.component or "unknown",
    details=drift.raw_data,  # Dict[str, Any] → ViolationDetails!
)

# FIX (YAMARAJA)
from vibe_core.protocols.naga import ViolationDetails
violation = VajraViolation(
    violation_type="COGNITIVE_THREAT",
    source=drift.component or "unknown",
    details=ViolationDetails(
        event_type="COGNITIVE_DRIFT",
        error_message=drift.message[:500],
    ),
)
```

---

## II. VASUKI DHARMA-VERLETZUNGEN

### A. FAIL-OPEN SIGNING (KRITISCH)

| Line | Code | Problem |
|------|------|---------|
| 173-174 | `except: logger.warning(...)` | Sends message UNSIGNED! |

```python
# CURRENT (FAIL-OPEN - GIFT WIRD GESENDET!)
try:
    sig_str = sign_content(payload.hex(), self._private_key)
    signature = base64.b64decode(sig_str)
except Exception as e:
    logger.warning(f"VASUKI: Signing failed: {e}")
    # CONTINUES WITH signature = b"" !!!

# FIX (FAIL-CLOSED)
try:
    sig_str = sign_content(payload.hex(), self._private_key)
    signature = base64.b64decode(sig_str)
except Exception as e:
    sys.stderr.write(f"!!! VASUKI: Signing failed - REFUSING TO SEND: {e}\n")
    raise RuntimeError(f"VASUKI: Cannot send unsigned message: {e}")
```

### B. SILENT DROP (WARNING)

| Line | Code | Problem |
|------|------|---------|
| 314-317 | `return False` | Envelope dropped, attacker not informed |

```python
# CURRENT
if len(self._receive_queue) >= 1000:
    logger.warning("VASUKI: Receive queue full, dropping envelope")
    return False

# FIX
if len(self._receive_queue) >= 1000:
    sys.stderr.write("!!! VASUKI: Receive queue FULL - dropping envelope\n")
    return False
```

### C. MISSING TAKSHAKA GATE

**Problem**: `churn_in()` trusts envelope without verification!

```python
# CURRENT (BLIND TRUST)
def churn_in(self, envelope: SignedEnvelope) -> EventDict:
    """NOTE: Takshaka must verify BEFORE calling this!"""  # WHO ENFORCES?
    event = msgpack.unpackb(envelope.payload, raw=False)
    return event

# FIX (ENFORCED)
def churn_in(self, envelope: SignedEnvelope) -> EventDict:
    # YAMARAJA: Verify BEFORE deserialize
    if not self._takshaka_ref:
        sys.stderr.write("!!! VASUKI: No Takshaka - cannot verify\n")
        raise RuntimeError("VASUKI: Cannot churn_in without Takshaka")

    result = self._takshaka_ref.verify_envelope(envelope.to_bytes())
    if not result.is_valid:
        sys.stderr.write(f"!!! VASUKI: Takshaka REJECTED envelope: {result.reason}\n")
        raise ValueError(f"VASUKI: Envelope rejected: {result.status}")

    event = msgpack.unpackb(envelope.payload, raw=False)
    return event
```

---

## III. EXECUTION PLAN

### Phase 1: TAKSHAKA HARDENING

1. **bite() FAIL-CLOSED**: Generate synthetic ID on failure
2. **Sesha Encapsulation**: Replace `_ledger` with `sesha.record_event()`
3. **as_handler() Types**: ViolationDetails statt Dict[str, Any]

### Phase 2: VASUKI HARDENING

1. **REFUSE UNSIGNED**: Raise on signing failure
2. **TAKSHAKA GATE**: Verify before churn_in()
3. **sys.stderr on drop**: Queue full → visible error

### Phase 3: DEPENDENCY INJECTION

Both services access `_sesha` and `_takshaka` but don't verify they exist.

```python
# YAMARAJA: Fail at BOOT, not at USE
class VasukiService:
    def __init__(self, sesha, takshaka, ...):
        if sesha is None:
            sys.stderr.write("!!! VASUKI: sesha is REQUIRED\n")
            raise SystemExit(1)
        if takshaka is None:
            sys.stderr.write("!!! VASUKI: takshaka is REQUIRED\n")
            raise SystemExit(1)
```

---

## IV. NARASIMHA PRINCIPLES

1. **FAIL-CLOSED**: If in doubt, DENY
2. **VERIFY BEFORE PROCESS**: Takshaka BEFORE msgpack.unpackb()
3. **NO UNSIGNED TRANSIT**: If signing fails, DON'T SEND
4. **DEPENDENCY = CONTRACT**: Missing deps = SystemExit(1)
5. **sys.stderr for SECURITY**: All security failures visible

---

## V. FILES TO FIX

| File | Breaches | Priority |
|------|----------|----------|
| `services/takshaka.py` | 5 (2 CRIT) | HIGH |
| `services/vasuki.py` | 3 (2 CRIT) | HIGH |
| `orchestrator.py` | Wiring deps | MEDIUM |

---

## VI. MOHINI OUROBOROS - pytest RECURSION BUG

### Problem Gefunden (2026-01-06)

**MOHINI OUROBOROS**: `prahlad.verify_self_integrity()` rief `pytest.main()` während bootstrap!

```
Test aufrufen
  → bootstrap()
    → _run_boot_integrity_check()
      → prahlad.verify_self_integrity()
        → pytest.main([tests/naga/])  ← RUNS ALL TESTS!
          → Tests rufen bootstrap()...
            → INFINITE RECURSION!
```

### Fix (orchestrator.py:612-617)

```python
def _run_boot_integrity_check(self) -> None:
    # MOHINI OUROBOROS GUARD: Prevent pytest recursion!
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logger.debug("NAGA: Skipping boot integrity check (inside pytest)")
        return
    # ... rest of method
```

**Resultat**: 708 tests pass in ~50s (statt INFINITE HANG)

---

## VII. GARUDA - The Controller of Nagas

### Architektur (SAUBER ✅)

```
Level -1: AnantaShesha (Substrate)  ← Garuda kontrolliert NICHT
Level  0: NAGA Services             ← Garuda kontrolliert via @naga_governed
```

**GarudaProtocol** (`protocols/naga/garuda.py`):
- `is_flying` - prüft ob Recursion aktiv
- `fly()` - Context Manager für governance suppression

**Implementation** (`naga/garuda.py`):
- ContextVars für async-safe depth tracking
- Nested calls korrekt behandelt

**Usage in NagaBaseService** (`services/base.py:270-275`):
```python
@naga_governed
def some_method(self, ...):
    if garuda.is_flying:
        return func(self, ...)  # RAW execution, no governance
    with garuda.fly():
        # Governed execution
```

**Korrekt**: AnantaShesha nutzt Garuda NICHT - Substrate bleibt unabhängig!

---

## VIII. SUBSTRATE AUDIT - 1 ENTRY POINT

### Problem (Behoben 2026-01-06)

**MAYAVADA**: AnantaService hatte DUPLICATE gene storage!

```python
# AnantaService (VORHER - FALSCH!)
self._genes = {}
self._gene_statuses = {}
self._capability_providers = {}
self._event_listeners = {}

# AnantaShesha (THE Substrate)
self._genes = {}              # ← THE truth
```

### Fix (ananta.py)

```python
class AnantaService(NagaBaseService, AnantaProtocol):
    def __init__(self, ledger=None):
        # 1 ENTRY POINT: Delegate to THE substrate
        from vibe_core.ouroboros.ananta_shesha import get_system_anchor
        self._substrate = get_system_anchor()

        # NO LOCAL GENE STORAGE - that's MAYAVADA!
        # Only Splicer state:
        self._available_mixins: Dict[str, Type] = {}
        self._flood_history: List[VetoDecision] = []

    def get_gene(self, name: str) -> Optional[IGene]:
        return self._substrate.get_gene(name)  # DELEGATE!
```

**Resultat**: 1 ENTRY POINT, no MAYAVADA, clean architecture.

---

## IX. CURRENT STATUS

- [x] TakshakaProtocol audited - CLEAN
- [x] TakshakaService audited - 5 VIOLATIONS
- [x] VasukiProtocol audited - CLEAN
- [x] VasukiService audited - 3 VIOLATIONS
- [x] **MOHINI OUROBOROS FIX** - pytest recursion guard
- [x] **SUBSTRATE FIX** - AnantaService delegates to AnantaShesha
- [x] **GARUDA AUDIT** - Architecture correct
- [x] Takshaka FAIL-CLOSED fix
- [x] Takshaka Sesha encapsulation
- [x] Vasuki REFUSE UNSIGNED
- [x] Vasuki TAKSHAKA GATE
- [x] Dependency injection hardening

```