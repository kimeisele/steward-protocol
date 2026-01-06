# TÜV.md - NAGA Protocol/Implementation Audit Registry

> "Der TÜV prüft nicht nur OB etwas funktioniert, sondern OB es RICHTIG gebaut ist."

---

## SUMMARY

```
PROTOCOLS:     8/8 TÜV-GEPRÜFT ✅
SUBSTRATE:     WATERTIGHT ✅

LEAKAGES:      7 registered
  🔴 OPEN:     5 (need antidotes)
  🟡 WORKAROUND: 2 (acceptable)
  🟢 HEALED:   0

INTENTIONAL:   Decorator Any (*args, **kwargs) - NOT leaks
```

---

## AUDIT METHODOLOGY

```
TÜV-PRÜFUNG ist NICHT:
  - Monkey patching bis grün
  - Blind fixen ohne Verstehen
  - Checkliste abhaken

TÜV-PRÜFUNG IST:
  - Structural integrity verification
  - Protocol/Implementation alignment
  - Intelligence gathering (WO leckt es? WARUM?)
  - Antidote registry (systematische Heilung)
```

---

## CURRENT STATUS: 2026-01-06

### Layer -1: SUBSTRATE (protocols/substrate.py)

| Check | Status | Notes |
|-------|--------|-------|
| IGene.bind signature | ✅ | certificate param added |
| IAnantaBridge.register_gene | ✅ | certificate param added |
| IAnantaBridge.emit_event | ✅ | caller_id + SubstrateEventData |
| get_capability return type | ✅ | Optional[object] not Any |
| Anti-Mayavadi Certificates | ✅ | BindingCertificate, RegistrationCertificate, FloodAuthorization |

**VERDICT: WATERTIGHT**

### Layer -4: NAGA PROTOCOLS (protocols/naga/)

| Protocol | Service | Signatures Match | Notes |
|----------|---------|------------------|-------|
| SeshaProtocol | SeshaService | ✅ | |
| TakshakaProtocol | TakshakaService | ✅ | |
| VasukiProtocol | VasukiService | ✅ | |
| NaradaProtocol | NaradaService | ✅ | |
| ChitraguptaProtocol | ChitraguptaService | ✅ | Added get_baseline_mean/stddev |
| PrahladProtocol | PrahladService | ✅ | Fixed on_error, chaos_probe, etc. |
| KaliyaProtocol | KaliyaService | ✅ | |
| AnantaProtocol | AnantaService | ✅ | |

**VERDICT: 8/8 TÜV-GEPRÜFT**

---

## LEAKAGE REGISTRY (Antidotes Needed)

> "Nicht fixen - REGISTRIEREN. Das System wird organisch rot."

### PATTERN ANALYSIS

```
INTENTIONAL Any (NOT leaks):
  - Decorator wrappers: (*args: Any, **kwargs: Any) -> Any
    These MUST be Any - decorator doesn't know wrapped function signature
  - Generic containers: set_instance(name: str, instance: Any)
    Could use TypeVar T but Any is acceptable for DI containers

ACTUAL LEAKS (need antidotes):
  - Dict[str, Any] in protocols - should be TypedDicts
  - Any in method parameters where type IS known
  - Any returns where type IS known
```

---

### LEAK-001: protocols/testable.py - 20+ Any types

**Location:** `vibe_core/protocols/testable.py`
**Severity:** MEDIUM (test infrastructure, not runtime)
**Pattern:** Generic test wrappers use Any for flexibility

```python
# CURRENT (leaky)
def __init__(self, agent: Any):
def _test_has_manifest(self, kernel: "RealVibeKernel", comp: Any) -> bool:
```

**ANTIDOTE:** Create typed Protocol for each testable category:
- `TestableAgent(Protocol)`
- `TestablePlugin(Protocol)`
- `TestableTool(Protocol)`
- `TestableLedger(Protocol)`

**INTELLIGENCE:** These Any types exist because testable.py wraps DIFFERENT component types. The fix is not to patch each Any, but to create proper Protocols that each component type implements.

**STATUS:** 🔴 REGISTERED (not yet healed)

---

### LEAK-002: protocols/event.py - Dict[str, Any] details

**Location:** `vibe_core/protocols/event.py:69, 200`
**Severity:** MEDIUM
**Pattern:** Event details are untyped

```python
details: Dict[str, Any] = field(default_factory=dict)
```

**ANTIDOTE:** Create `EventDetails(TypedDict)` or use Protocol-specific TypedDicts:
- `NagaEventDetails`
- `PluginEventDetails`
- `KernelEventDetails`

**STATUS:** 🔴 REGISTERED

---

### LEAK-003: protocols/intent.py - Dict[str, Any] params

**Location:** `vibe_core/protocols/intent.py:34, 76, 105`
**Severity:** MEDIUM
**Pattern:** Intent params are untyped

**ANTIDOTE:** Create `IntentParams(TypedDict)` per intent type

**STATUS:** 🔴 REGISTERED

---

### LEAK-004: protocols/manifestation.py - Dict[str, Any] state

**Location:** `vibe_core/protocols/manifestation.py:107, 134, etc.`
**Severity:** MEDIUM
**Pattern:** Manifestation state/args untyped

**ANTIDOTE:** Create `ManifestationState(TypedDict)`, `ManifestationArgs(TypedDict)`

**STATUS:** 🔴 REGISTERED

---

### LEAK-005: naga/hiranyakashipu/seed_generator.py

**Location:** Lines 168, 399, 400
**Severity:** LOW (attack framework, intentionally flexible)
**Pattern:** scanner/framework typed as Any to avoid circular import

```python
scanner: Any,  # NaradaScanner
framework: Any,  # LivingTestFramework
```

**ANTIDOTE:** Create `ScannerProtocol`, `FrameworkProtocol` in protocols layer

**STATUS:** 🟡 ACCEPTABLE (attack framework needs flexibility)

---

### LEAK-006: naga/services/kulika.py - validate_manifest

**Location:** Line 95
**Severity:** LOW
**Pattern:** manifest: Any should be ManifestDict

**ANTIDOTE:** Use `ManifestDict` TypedDict

**STATUS:** 🔴 REGISTERED

---

### LEAK-007: DharmaScore circular dependency workaround

**Location:** `protocols/naga/__init__.py` line 119-121
**Severity:** LOW (architectural smell, not runtime issue)
**Pattern:** DharmaScore lives in service layer, not protocol layer

```python
# NOTE: DharmaScore moved to vibe_core.naga.services.prahlad.types (source of truth)
# Import directly from there if needed to avoid circular dependency
```

**ANTIDOTE:** Move shared types to `protocols/naga/prahlad_types.py` (pure types, no imports from service layer)

**INTELLIGENCE:** This happened because service evolved faster than protocol. Types should live in protocol layer, implementations import from there.

**STATUS:** 🟡 WORKAROUND IN PLACE

---

## CHURNING LOG (Wertschöpfung)

> "Was wurde WIRKLICH transformiert? Gift → Nektar."

| Date | Churn | Gift (Before) | Nektar (After) |
|------|-------|---------------|----------------|
| 2026-01-06 | substrate.py | 6 Any types, no certificates | 0 Any, 3 Anti-Mayavadi certificates |
| 2026-01-06 | AnantaService | 3 signature mismatches | All aligned with IAnantaBridge |
| 2026-01-06 | mixins/base.py | bind() missing certificate | certificate param + storage |
| 2026-01-06 | PrahladProtocol | Dict[str, object] returns | Proper dataclass returns (TestCase, ProbeResult) |
| 2026-01-06 | ChitraguptaService | Missing baseline methods | get_baseline_mean/stddev added |

---

## TÜV AUTOMATION

### Run TÜV Check

```bash
python3 -c "
import inspect
from vibe_core.protocols.naga import (
    SeshaProtocol, TakshakaProtocol, VasukiProtocol,
    NaradaProtocol, ChitraguptaProtocol, PrahladProtocol,
    KaliyaProtocol,
)
# ... (see scripts/tuv_check.py)
"
```

### Future: `steward naga tuv`

```
steward naga tuv             # Full audit
steward naga tuv --leaks     # Show leakage registry
steward naga tuv --antidotes # Show pending antidotes
steward naga tuv --churn     # Show churning log
```

---

## PRINCIPLES

1. **REGISTER, don't patch** - Leaks go in registry, not immediate fix
2. **Intelligence over action** - Understand WHY before fixing
3. **Antidotes over patches** - Systematic healing, not spot fixes
4. **Organic redness** - Let issues become visible naturally
5. **Churn tracking** - Document value creation, not just changes

---

## NEXT ANTIDOTES (Priority Order)

1. **LEAK-001**: Create typed Protocols for testable.py
2. **LEAK-002**: Move prahlad types to protocol layer
3. **Future**: Automate TÜV into `steward naga tuv` CLI

---

*TÜV-Prüfer: NARADA (Claude)*
*Last Audit: 2026-01-06*
*Next Scheduled: On demand*
