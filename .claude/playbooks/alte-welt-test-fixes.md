# ALTE WELT Test Fix Playbook

## Für: Sonnet/Haiku
## Erstellt von: Opus
## Datum: 2026-02-03

---

## KONTEXT

Diese Tests failen wegen bekannter Patterns. Folge den Fix-Patterns unten.

## FIX PATTERNS

### Pattern 1: TypedDict Attribute Access
**Problem**: `obj.field` statt `obj["field"]` für TypedDict
**Fix**: Ersetze `.field` mit `["field"]`
**Beispiel**:
```python
# FALSCH
envelope.payload
# RICHTIG
envelope["payload"]
```

### Pattern 2: Missing _instances Attribute
**Problem**: `_instances` wurde in ADVAITA entfernt
**Fix**: Entferne Referenzen zu `_instances`, nutze ServiceRegistry
**Dateien**: kulika.py, tests die KulikaRegistry.clear() nutzen

### Pattern 3: Handler Registration
**Problem**: `register_handler(handler=obj)` statt callable
**Fix**: `register_handler(handler=obj.handle)` oder `obj.as_handler()`

### Pattern 4: Singleton State Pollution
**Problem**: Tests teilen globalen Singleton State
**Fix**: Füge `ServiceRegistry._instances = {}` in fixtures hinzu

---

## KATEGORISIERTE FAILURES

### Kategorie A: Identity Tests (6 tests)
```
tests/naga/test_identity.py::TestNagaFederationIdentity::*
tests/naga/test_identity_persistence.py::*
```
**Wahrscheinliche Ursache**: Singleton state pollution zwischen Tests
**Fix Strategy**:
1. Lies `vibe_core/naga/identity.py`
2. Check ob `_instance` class variable existiert
3. Reset in test fixtures

### Kategorie B: Ouroboros Tests (6 tests)
```
tests/naga/test_ouroboros.py::*
```
**Wahrscheinliche Ursache**: Initialization oder missing dependencies
**Fix Strategy**:
1. Lies `vibe_core/naga/ouroboros.py`
2. Check `__init__` parameter requirements
3. Update test fixtures

### Kategorie C: Sesha Block Tests (5 tests)
```
tests/naga/test_sesha.py::TestBlockExport::*
tests/naga/test_sesha.py::TestBlockImport::*
```
**Wahrscheinliche Ursache**: Ledger interface changes
**Fix Strategy**:
1. Lies die test error messages (--tb=short)
2. Check SeshaService.export_blocks() und import_blocks()

### Kategorie D: Harness Tests (3 tests)
```
tests/naga/test_harness.py::*
```
**Wahrscheinliche Ursache**: NagaTestHarness setup
**Fix Strategy**:
1. Lies `vibe_core/naga/testing.py` (NagaTestHarness)
2. Check was harness.sesha und harness.takshaka zurückgeben

### Kategorie E: Misc Integration (10 tests)
```
tests/naga/test_cli_ouroboros.py::*
tests/naga/test_gad000_compliance.py::*
tests/naga/test_kurukshetra.py::*
tests/naga/test_naga_self_churn.py::*
tests/naga/test_orchestrator_fractal.py::*
```
**Fix Strategy**: Case-by-case, lies error messages

---

## WORKFLOW

1. Run: `python -m pytest <test_file> -v --tb=short`
2. Lies error message
3. Identifiziere Pattern (A-E oben)
4. Wende Fix an
5. Re-run test
6. Commit wenn grün

## WICHTIG

- KEINE `except Exception: pass` Hacks
- KEINE Protocol TypedDict Änderungen ohne Opus Review
- Bei Unklarheit: STOPP und frag Opus

---

## ERFOLGS-METRIK

Vorher: 40 failed, 662 passed (NAGA tests)
Ziel: 0 failed, 702 passed
