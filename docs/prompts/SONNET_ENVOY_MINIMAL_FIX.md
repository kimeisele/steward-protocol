# SONNET TASK: ENVOY Minimal Fix

## Context

Read `docs/architecture/OPUS/OPUS_RUNTIME_SEPARATION.md` first. It explains the problem.

**TL;DR:** Template Context wird einmal gebaut, nicht pro Phase aktualisiert. Deswegen kann Phase 4 (render_output) die Ergebnisse von Phase 1-3 nicht sehen.

## Your Task

Fix BREAK 3: Template Context Stale Problem

## The Exact Fix

**File:** `vibe_core/cartridges/system/envoy/deterministic_executor.py`

**Location:** Method `_execute_phase_actions()`, around line 738-741

**Current Code (BROKEN):**
```python
async def _execute_phase_actions(
    self,
    phase: "PlaybookPhase",
    playbook: "PlaybookDefinition",
    execution: "PlaybookExecution",
    kernel: Any,
    emit_event: Optional[Callable],
    intent_vector: Any = None,
) -> bool:
    # ... validation code ...

    # Build template context for variable resolution (GAD-5000)
    template_context = self._build_template_context(playbook, execution, intent_vector)  # <-- BUILT ONCE!

    for action in phase.actions:
        # ... action processing uses template_context ...
```

**Fixed Code:**
```python
async def _execute_phase_actions(
    self,
    phase: "PlaybookPhase",
    playbook: "PlaybookDefinition",
    execution: "PlaybookExecution",
    kernel: Any,
    emit_event: Optional[Callable],
    intent_vector: Any = None,
) -> bool:
    # ... validation code ...

    for action in phase.actions:
        # CRITICAL FIX: Rebuild context EVERY action to get fresh phase_results
        # This ensures that render_output phase can see results from query_status, query_agents, query_tools
        template_context = self._build_template_context(playbook, execution, intent_vector)

        # ... action processing uses template_context ...
```

## How to Verify

Run this test:

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.WARNING)

from vibe_core.kernel_impl import RealVibeKernel

kernel = RealVibeKernel(ledger_path=':memory:')
kernel.boot()

result = kernel.envoy.execute_circuit('SYSTEM_STATUS_V2', params={'user_input': 'status'})

print('=== RESULT ===')
print(f'Status: {result.get(\"status\")}')

# Check rendered output
details = result.get('details', {})
rendered_phase = details.get('rendered', {})
rendered_text = rendered_phase.get('rendered', '') if isinstance(rendered_phase, dict) else ''

print(f'Rendered length: {len(rendered_text)}')

if 'Agent City' in rendered_text:
    print('SUCCESS: Template rendered correctly!')
    print()
    print(rendered_text)
else:
    print('FAILED: Template did not render')
    print(f'Phase data: {rendered_phase}')
"
```

**Expected Output:**
```
Status: COMPLETED
Rendered length: > 0
SUCCESS: Template rendered correctly!

## Agent City Status

**Kernel:** RUNNING
**Health:** OPERATIONAL
...
```

## Rules

1. **DO NOT** touch kernel_impl.py - DER KERNEL IST ETERNAL
2. **DO NOT** add new files - just fix the existing one
3. **DO NOT** change the circuit YAML files
4. **DO** run the verification test
5. **DO** commit if it works

## Commit Message

```
fix: Rebuild template context per action in DeterministicExecutor

BREAK 3 fix from OPUS_RUNTIME_SEPARATION analysis.
Template context was built once per phase, but phase_results are
updated AFTER each phase completes. This meant render_output phase
couldn't see results from previous phases.

Fix: Move template_context building inside the action loop so each
action gets fresh phase_results.

Refs: docs/architecture/OPUS/OPUS_RUNTIME_SEPARATION.md
```

## After Success

Tell the user: "Minimal fix applied. SYSTEM_STATUS_V2 circuit now renders output. Ready for Opus to do the refactoring."
