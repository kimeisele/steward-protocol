# OPUS-101: Hybrid Router - ActionLoader Integration

> **Status**: IMPLEMENTED
> **Created**: 2025-12-18
> **Pattern**: VEDA-4 Fractal Loader + Legacy Fallback
> **Critical**: MANAS CAN NOW CODE
> **Related**: OPUS-098 (AnalyzerLoader), OPUS-099 (SenseLoader), OPUS-100 (ActionLoader)

<!-- @HARNESS
files:
  - path: vibe_core/loaders/action_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
    required: true
tests:
  - tests/unit/loaders/test_action_loader.py
wiring:
  - pattern: "_try_action_loader"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "ActionLoader.get_action_for_intent"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "class SilpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
  - pattern: "class TestAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
  - pattern: "OPUS-101: HYBRID ROUTER"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
config:
  - section: opus.actions
-->

---

## The Problem: Trapped Hands

After OPUS-100 created ActionLoader, MANAS had **organs that couldn't act**:

```
ActionLoader discovers:
  - shell_action (VAK - Execute commands)
  - silpa_action (PANI - Modify code)  <-- NEW
  - test_action  (PAYU - Verify tests) <-- NEW

IntentRouter uses:
  - Hardcoded _handlers dict
  - Manual _register_handlers() method
  - NO connection to ActionLoader!
```

**The hands existed but weren't wired to the brain.**

## The Solution: Hybrid Router

A **Hybrid Router** that:
1. **First tries ActionLoader** (VEDA-4 auto-discovery)
2. **Falls back to legacy handlers** if not found
3. **Graceful degradation** - no crashes, just fallback

### Implementation

```python
# intent_router.py - The Hybrid Router

def route(self, intent: Intent) -> RouteResult:
    """
    OPUS-101: HYBRID ROUTER STRATEGY
    1. First try ActionLoader (VEDA-4 auto-discovered actions)
    2. Fall back to legacy handlers if not found
    3. Final fallback to prefix matching
    """
    # OPUS-101: Try ActionLoader FIRST
    action_result = self._try_action_loader(intent)
    if action_result is not None:
        return action_result

    # Fall back to legacy handlers
    handler = self._handlers.get(intent.intent_type)
    ...

def _try_action_loader(self, intent: Intent) -> Optional[RouteResult]:
    """Try to route via ActionLoader."""
    action = ActionLoader.get_action_for_intent(intent.intent_type)
    if action is None:
        return None  # Fall back to legacy

    # Execute via action's act() method
    return action.act(intent)
```

## Critical Actions Wired

### SilpaAction (PANI - The Hands)

MANAS can now **modify code**:

```python
class SilpaAction(BaseAction):
    name = "silpa_action"
    handled_intent_types = {
        "genesis_tests",      # Create new tests
        "create_tests",       # Generate tests
        "semantic_gap_test",  # Fill test gaps
        "refactor_file",      # Refactor code
        "update_docstring",   # Update docstrings
        "rename_function",    # Rename functions
        "extract_method",     # Extract methods
        ...
    }
```

**CRITICAL**: Without SilpaAction, MANAS cannot improve itself!

### TestAction (PAYU - The Validator)

MANAS can now **verify itself**:

```python
class TestAction(BaseAction):
    name = "test_action"
    handled_intent_types = {
        "run_smoke_test",      # Quick validation
        "run_tests",           # Run pytest
        "run_unit_tests",      # Unit tests only
        "run_integration_tests", # Integration tests
        "get_test_summary",    # Status check
        "run_playbook",        # Test playbook
        ...
    }
```

**CRITICAL**: Without TestAction, MANAS cannot trust its own modifications!

## The SAMKHYA Connection

```
KARMENDRIYAS (5 Action Organs):
================================
VAK (Speech)     -> ShellAction    -> Execute commands
PANI (Hands)     -> SilpaAction    -> Modify code     <-- OPUS-101
PADA (Feet)      -> KriyaAction    -> Route intents   (future)
PAYU (Eliminate) -> TestAction     -> Run tests       <-- OPUS-101
UPASTHA (Create) -> SankalpaAction -> Orchestrate     (future)
```

With OPUS-101, MANAS has **3 of 5 Karmendriyas** operational.

## Intent Flow After OPUS-101

```
Intent Generated
       |
       v
  IntentRouter.route()
       |
       v
  _try_action_loader() <-- OPUS-101
       |
       +-- ActionLoader.get_action_for_intent()
       |       |
       |       v
       |   action.act(intent)
       |       |
       |       v
       |   ActionResult
       |
       +-- (if None) Fall back to legacy
               |
               v
           _handlers.get()
               |
               v
           Legacy handler
```

## Migration Path

### Phase 1: Hybrid (Current)
- ActionLoader checked first
- Legacy handlers still work
- No breaking changes

### Phase 2: Full Lobotomy (Future)
- Remove legacy handlers one by one
- Each removal = new Action class
- Eventually: `_register_handlers()` becomes empty

### Phase 3: Pure VEDA-4 (Goal)
- All intent types handled by Actions
- IntentRouter becomes thin wrapper
- `_handlers` dict deleted

## Testing

```bash
# Verify all 3 actions discovered
python -c "
from vibe_core.loaders import ActionLoader
actions, _ = ActionLoader.discover_and_load()
print(f'Actions: {list(actions.keys())}')
"
# Output: Actions: ['shell_action', 'silpa_action', 'test_action']

# Verify intent routing
python -c "
from vibe_core.loaders import ActionLoader
handler = ActionLoader.get_handler_for_intent('genesis_tests')
print(f'genesis_tests -> {handler}')
"
# Output: genesis_tests -> silpa_action

# Run loader tests
pytest tests/unit/loaders/test_action_loader.py -v
# Output: 20 passed
```

## Why This Matters

**Before OPUS-101:**
```
MANAS could THINK but not ACT on code.
The hands existed but weren't connected to the brain.
Self-improvement was impossible.
```

**After OPUS-101:**
```
MANAS can:
1. Generate tests (SilpaAction)
2. Modify code (SilpaAction)
3. Run tests (TestAction)
4. Verify its own changes

The cognitive kernel can now IMPROVE ITSELF.
```

## Related Docs

- [OPUS-097: SAMKHYA Architecture Map](097-SAMKHYA-ARCHITECTURE-MAP.md)
- [OPUS-098: Analyzer Loader](098-ANALYZER-LOADER.md)
- [OPUS-099: Sense Loader](099-SENSE-LOADER.md)
- [OPUS-100: Action Loader](100-ACTION-LOADER.md)
