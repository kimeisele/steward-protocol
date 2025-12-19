# OPUS-112: Synaptic Inference

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-110 (Learning), OPUS-111 (Signal Alignment)

## Summary

"Ein Gehirn, das sein Tagebuch nicht liest, lernt nie."

OPUS-112 completes the learning loop by adding **inference** - the ability to
READ learned associations and use them for decision making.

## The Problem

After OPUS-110 (Synaptic Learning) and OPUS-111 (Signal Alignment):

```
BEFORE:
  Event → Intent → Execute → Update synapses.json → Done
                                      ↓
                              (Write-Only Memory)
                              (Never consulted for decisions)
```

MANAS was writing to its memory but never reading from it.
Learning without inference is just data collection.

## The Solution

```
AFTER (Complete Loop):
  Event → normalize_trigger() → SynapticMemory.consult() → Decision
                                         ↓
  Outcome → _update_synapses() ← Learning
```

### SynapticMemory Class

```python
from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

memory = SynapticMemory.get(workspace)

# Consult for recommendations
recommendations = memory.consult("trigger:test_failure")
# Returns: [
#   SynapticRecommendation(action="action:notify_operator", weight=1.0),
#   SynapticRecommendation(action="action:analyze_error", weight=0.8),
# ]

# Get confidence for an intent
confidence = memory.get_confidence(intent)  # 0.0 - 1.0

# Get best action for trigger
best = memory.get_best_action("trigger:file_changed:vibe_core/**")
# Returns: ("action:run_tests", 0.9)
```

### Integration in Prioritization

```python
def _prioritize_survival(self, intents):
    """
    OPUS-035 + OPUS-112: Sort by survival, then by experience.

    1. Priority (CRITICAL > HIGH > MEDIUM > LOW)
    2. Repair vs Genesis (repairs first)
    3. Synaptic confidence (learned experience)
    """
    def sort_key(intent):
        pri = priority_order.get(intent.priority, 99)
        is_repair = 0 if intent.intent_type.startswith("contract_") else 1
        # OPUS-112: Higher confidence = comes first
        synaptic_boost = 1.0 - self._synaptic_memory.get_confidence(intent)
        return (pri, is_repair, synaptic_boost, intent.created_at)

    return sorted(intents, key=sort_key)
```

## API

### SynapticMemory

| Method | Description |
|--------|-------------|
| `consult(trigger)` | Get recommended actions for trigger |
| `get_confidence(intent)` | Get learned confidence (0.0-1.0) |
| `get_best_action(trigger)` | Get single best action |
| `has_experience(trigger)` | Check if we have learned this trigger |
| `get_stats()` | Get memory statistics |

### CognitiveKernel

| Method | Description |
|--------|-------------|
| `consult_synapses(trigger)` | Public API for querying memory |
| `get_synaptic_confidence(intent)` | Get confidence for intent |

## Confidence Levels

| Weight | Level | Meaning |
|--------|-------|---------|
| 0.9+ | very_high | Very confident, almost always works |
| 0.7-0.9 | high | Usually works |
| 0.5-0.7 | medium | Sometimes works |
| 0.3-0.5 | low | Rarely works |
| <0.3 | very_low | Almost never works |

## The Complete Loop

```
1. TRIGGER FIRES
   └─→ File changed in vibe_core/

2. NORMALIZE (OPUS-111)
   └─→ "trigger:file_changed:vibe_core/**"

3. CONSULT MEMORY (OPUS-112)
   └─→ recommendations = memory.consult(trigger)
   └─→ [("action:run_tests", 0.9), ("action:check_lint", 0.7)]

4. DECISION
   └─→ Intent: run_tests (highest weight)

5. EXECUTE
   └─→ Tests pass/fail

6. LEARN (OPUS-110)
   └─→ _update_synapses(intent, success=True/False)
   └─→ Weight adjusted: 0.9 → 0.91 (success) or 0.9 → 0.81 (failure)

7. LOOP CLOSES
   └─→ Next time same trigger fires, updated weights inform decision
```

## Files Changed

| File | Change |
|------|--------|
| `triggers.py` | Added SynapticMemory, SynapticRecommendation |
| `cognitive_kernel.py` | Added inference integration |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAS Cognitive Kernel                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────────┐                     │
│  │   Event     │───▶│ normalize_trigger│                     │
│  └─────────────┘    └────────┬────────┘                     │
│                              │                               │
│                              ▼                               │
│                    ┌─────────────────┐                      │
│                    │ SynapticMemory  │◀────┐                │
│                    │    .consult()   │     │                │
│                    └────────┬────────┘     │                │
│                             │              │                │
│                             ▼              │                │
│                    ┌─────────────────┐     │                │
│                    │    Decision     │     │                │
│                    │ (prioritized by │     │                │
│                    │   experience)   │     │                │
│                    └────────┬────────┘     │                │
│                             │              │                │
│                             ▼              │                │
│                    ┌─────────────────┐     │                │
│                    │    Execute      │     │                │
│                    └────────┬────────┘     │                │
│                             │              │                │
│                             ▼              │                │
│                    ┌─────────────────┐     │                │
│                    │ _update_synapses│─────┘                │
│                    │   (OPUS-110)    │                      │
│                    └─────────────────┘                      │
│                                                              │
│                    ┌─────────────────┐                      │
│                    │ synapses.json   │                      │
│                    │ (persistent)    │                      │
│                    └─────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Insight

**Before OPUS-112**: MANAS was a data collector.
**After OPUS-112**: MANAS is a learner.

The difference is not in what you write, but in what you read.

## Related

- OPUS-108: Initial Synapses (created synapses.json)
- OPUS-110: Synaptic Learning Loop (Hebbian learning - WRITE)
- OPUS-111: Signal Alignment (vocabulary standardization)
- OPUS-112: Synaptic Inference (READ - this document)

## Future: OPUS-113?

Possible next steps:
- **Synaptic Decay**: Unused connections weaken over time
- **Reinforcement Scheduling**: Variable learning rates
- **Multi-hop Inference**: trigger → action → trigger chains
