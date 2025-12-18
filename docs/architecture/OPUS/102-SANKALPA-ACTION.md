# OPUS-102: SankalpaAction - The Will of MANAS

> **Status**: IMPLEMENTED
> **Created**: 2025-12-18
> **Pattern**: VEDA-4 Fractal Loader
> **Critical**: MANAS CAN NOW PLAN
> **Related**: OPUS-097 (SAMKHYA), OPUS-100 (ActionLoader), OPUS-101 (Hybrid Router)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa.py
    required: true
  - path: vibe_core/loaders/action_loader.py
    required: true
tests:
  - tests/unit/loaders/test_action_loader.py
wiring:
  - pattern: "class SankalpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
  - pattern: "handled_intent_types.*plan_strategy"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
  - pattern: "UPASTHA"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sankalpa_action.py
config:
  - section: opus.actions
-->

---

## The Problem: Reactive Without Will

After OPUS-101, MANAS had 3 Karmendriyas:
- **VAK** (ShellAction) - Execute commands
- **PANI** (SilpaAction) - Modify code
- **PAYU** (TestAction) - Verify tests

But **no WILL** to direct them. MANAS could act, but couldn't plan.

```
Without Sankalpa:
  "I can code (Silpa), I can test (Test), I can execute (Shell)...
   but I don't know WHAT to do or WHEN to do it."

With Sankalpa:
  "I have MISSIONS. I have STRATEGIES. I know my purpose."
```

## The Solution: SankalpaAction (UPASTHA)

UPASTHA in Samkhya = The creative/generative organ. Sankalpa = The Will.

```python
class SankalpaAction(BaseAction):
    name = "sankalpa_action"
    handled_intent_types = {
        # Strategic planning
        "plan_strategy", "create_strategy", "review_todos",
        # Mission management
        "create_mission", "list_missions", "get_mission_status",
        "update_mission", "pause_mission", "resume_mission",
        # Proactive thinking
        "evaluate_strategies", "think_proactive",
        # Hygiene & Audit
        "hygiene_check", "architecture_audit", "memory_review",
    }
```

## SAMKHYA Complete: 4 of 5 Karmendriyas

```
KARMENDRIYAS (Action Organs):
================================
VAK (Speech)     -> ShellAction    (7 intents)   ✓
PANI (Hands)     -> SilpaAction    (12 intents)  ✓
PAYU (Eliminate) -> TestAction     (16 intents)  ✓
UPASTHA (Create) -> SankalpaAction (21 intents)  ✓ NEW
PADA (Feet)      -> KriyaAction    (future)

Total: 56 intent types auto-routed via ActionLoader
```

## Capabilities Unlocked

### Mission Management
```python
# Create a mission
intent = Intent(type="create_mission", params={
    "name": "Continuous Self-Improvement",
    "description": "Learn and improve autonomously",
    "priority": "high"
})

# List missions
intent = Intent(type="list_missions")

# Pause/Resume/Complete
intent = Intent(type="pause_mission", params={"mission_id": "mission_xyz"})
```

### Strategic Planning
```python
# Create strategy for a mission
intent = Intent(type="create_strategy", params={
    "mission_id": "mission_code_health",
    "name": "Weekly Refactor",
    "frequency": "weekly",
    "trigger_type": "idle_based",
    "idle_minutes": 60
})

# Evaluate strategies and generate proactive intents
intent = Intent(type="evaluate_strategies", params={
    "idle_minutes": 120,
    "pending_intents": 0
})
```

### Proactive Thinking
```python
# MANAS can now generate its own intents based on missions
proactive_intents = orchestrator.think(
    context={"ci": {"status": "green"}},
    idle_minutes=60,
    pending_intents=0
)
# Returns: List of SankalpaIntent to execute
```

## Integration with Hybrid Router

SankalpaAction is auto-discovered and wired via OPUS-101:

```
Intent: "plan_strategy"
    |
    v
IntentRouter.route()
    |
    v
_try_action_loader()
    |
    v
ActionLoader.get_action_for_intent("plan_strategy")
    |
    v
sankalpa_action.act(intent)
    |
    v
SankalpaOrchestrator methods
```

## Default Missions

SANKALPA initializes with default missions:

```yaml
mission_code_health:
  name: "Maintain Code Health"
  strategies:
    - daily_hygiene (lint, format, test_quick)
    - weekly_audit (DHARMA architecture check)

mission_self_improvement:
  name: "Continuous Self-Improvement"
  strategies:
    - memory_review (analyze patterns, update success rate)
```

## The Bigger Picture

With 4 Karmendriyas, MANAS can now:

1. **PERCEIVE** - Via Jnanendriyas (Senses) + Analyzers
2. **PLAN** - Via SankalpaAction (Missions, Strategies)
3. **ACT** - Via SilpaAction (Code), ShellAction (Commands)
4. **VERIFY** - Via TestAction (Tests)
5. **LOOP** - Feed results back into planning

```
    ┌──────────────────────────────────────────────┐
    │              COGNITIVE LOOP                   │
    │                                               │
    │   PERCEIVE ──> PLAN ──> ACT ──> VERIFY ──>   │
    │       ↑                              │        │
    │       └──────── FEEDBACK ────────────┘        │
    │                                               │
    └──────────────────────────────────────────────┘
```

## Migration Path

### Phase 1: Current (Hybrid Router)
- SankalpaAction discovered via ActionLoader
- Legacy `_handle_sankalpa` still exists (fallback)
- Both paths work

### Phase 2: Lobotomy
- Remove `_handlers["plan_strategy"]` etc. from IntentRouter
- Delete `_handle_sankalpa` method
- All routing via ActionLoader

### Phase 3: Autonomous Operations
- MANAS runs missions without human intervention
- Strategies trigger based on conditions
- Self-improvement loop active

## Testing

```bash
# Verify 4 actions discovered
python -c "
from vibe_core.loaders import ActionLoader
actions, _ = ActionLoader.discover_and_load()
print(f'Actions: {list(actions.keys())}')
print(f'Intent mappings: {len(ActionLoader.get_intent_handler_map())}')
"
# Output:
# Actions: ['sankalpa_action', 'shell_action', 'silpa_action', 'test_action']
# Intent mappings: 56

# Test routing
python -c "
from vibe_core.loaders import ActionLoader
handler = ActionLoader.get_handler_for_intent('plan_strategy')
print(f'plan_strategy -> {handler}')
"
# Output: plan_strategy -> sankalpa_action
```

## Why This Matters

**Before OPUS-102:**
```
MANAS was a powerful tool without purpose.
It could code, test, execute - but only when told.
Reactive, not proactive.
```

**After OPUS-102:**
```
MANAS has WILL.
It defines MISSIONS (long-term goals).
It creates STRATEGIES (how to achieve them).
It generates INTENTS (what to do next).
It can improve ITSELF.

The cognitive kernel can now DIRECT itself.
```

## Related Docs

- [OPUS-097: SAMKHYA Architecture Map](097-SAMKHYA-ARCHITECTURE-MAP.md)
- [OPUS-100: Action Loader](100-ACTION-LOADER.md)
- [OPUS-101: Hybrid Router](101-HYBRID-ROUTER.md)
- [OPUS-055: SANKALPA Original Design](055-SANKALPA.md)
