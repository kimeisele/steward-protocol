# OPUS-026: Semantic Verification Protocol

> **Status**: 🚧 PLANNED (NOT YET IMPLEMENTED)
> **Created**: 2025-12-12
> **Scope**: Extend @HARNESS from syntactic (grep) to semantic (code execution) verification
> **Honesty Note**: This doc describes FUTURE functionality. `_verify_semantic()` does not exist yet.

<!-- @HARNESS
# NOTE: This doc describes PLANNED functionality.
# The harness validates prerequisites only, not the implementation.
files:
  - path: vibe_core/plugins/interface/renderers/opus/panels/verification.py
    required: true
  - path: config/opus.yaml
    required: true
config:
  - section: opus.verification.weights.semantic_passes
wiring:
  - pattern: "semantic_passes"
    in: config/opus.yaml
# PLANNED: These checks will pass once implemented
# wiring:
#   - pattern: "_verify_semantic"
#     in: vibe_core/plugins/interface/renderers/opus/panels/verification.py
-->

---

## Problem

@HARNESS was purely **syntactic** - it only checked:
- File EXISTS? (not: does code work?)
- Pattern FOUND? (regex grep, not execution)
- Config key EXISTS? (not: is value correct?)

**Result:** 90% trust scores on docs where code was BROKEN.

Example: OPUS-012 showed 90% but:
- Gate 5 (Herald) had `Event.__init__()` API mismatch
- LifecyclePlugin was claimed missing but actually loaded
- Doc said "❌ TODO" but code was implemented

---

## Solution

Add `semantic:` check type to @HARNESS that **actually executes code**.

### New @HARNESS Syntax

```yaml
<!-- @HARNESS
files:
  - path: vibe_core/plugins/lifecycle/plugin_main.py
semantic:
  # Type 1: Verify plugin loads in kernel
  - type: plugin_loaded
    name: "lifecycle_loads"
    plugin: lifecycle

  # Type 2: Verify method exists and is callable
  - type: method_exists
    name: "spawn_method"
    class: LifecyclePlugin
    method: spawn_agent
    in: vibe_core/plugins/lifecycle/plugin_main.py

  # Type 3: Run specific pytest
  - type: pytest_passes
    name: "spawn_test"
    test: tests/integration/test_lifecycle.py::test_spawn
-->
```

---

## Implementation

### Location

`vibe_core/plugins/interface/renderers/opus/panels/verification.py`

### Method: `_verify_semantic()`

```python
def _verify_semantic(self, semantics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    OPUS-026: Semantic verification - actually EXECUTE code.

    Safety guarantees:
    - 2s timeout per check (no UI freeze)
    - Full try/except panzerung (never crashes)
    - Uses in-memory kernel (no side effects)
    """
```

### Check Types

| Type | What it does | Timeout |
|------|--------------|---------|
| `plugin_loaded` | Boot kernel, check `_plugins_map` | 2s |
| `method_exists` | Import module, check `callable()` | 2s |
| `pytest_passes` | Run subprocess pytest | 2s |

### Safety Features

1. **Timeout**: 2 seconds per check via `signal.SIGALRM`
2. **Panzerung**: All checks wrapped in try/except
3. **Isolation**: Uses in-memory ledger (`ledger_path=":memory:"`)
4. **Caching**: Kernel booted once per verification run

---

## Config Changes

`config/opus.yaml`:

```yaml
weights:
  files_exist: 20        # was 30
  tests_exist: 15        # was 25
  wiring_verified: 20    # was 25
  semantic_passes: 25    # NEW - code execution
  config_exists: 10
  doc_complete: 10
```

---

## OPUS.md Table Update

New column added:

```
| Doc | Score | Files | Tests | Wiring | Absent | Config | Semantic |
|-----|-------|-------|-------|--------|--------|--------|----------|
```

Legend:
- ✅ = All semantic checks pass
- ❌ = One or more semantic checks failed
- ⏭️ = Checks skipped (timeout)
- ⚪ = No semantic checks defined

---

## Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| `_verify_semantic()` | ❌ PLANNED | Not yet implemented |
| Timeout (2s) | ❌ PLANNED | Requires `_verify_semantic()` |
| Panzerung | ❌ PLANNED | Requires `_verify_semantic()` |
| Config weights | ✅ | opus.yaml:215 (`semantic_passes: 25`) |
| Table column | ⚪ | Semantic column shown but always ⚪ |

---

## Usage Example

Add to any OPUS doc:

```yaml
<!-- @HARNESS
semantic:
  - type: plugin_loaded
    name: "my_plugin_loads"
    plugin: my_plugin
-->
```

If plugin doesn't load → ❌ in Semantic column → Trust Score drops.

---

## Next Steps

1. [ ] Add semantic checks to OPUS-012 (System Agents)
2. [ ] Add semantic checks to all OPUS docs with code claims
3. [ ] Consider adding `assertion` type for custom code
