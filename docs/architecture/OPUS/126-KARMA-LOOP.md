# OPUS-126: The Karma Loop (Samskara)

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-125 (Reflex Arc), OPUS-117 (Fractal Integration)

## Summary

"कर्मण्येवाधिकारस्ते" - "To action alone you have a right."

OPUS-126 connects the Reflex Arc (OPUS-125) to the Parampara lineage chain,
recording every autonomous healing action as an immutable karmic imprint (Samskara).

**This is the memory of the autonomic nervous system.**

## The Problem

OPUS-125 gave us autonomous self-healing:
- DisharmonyDetector detects pain
- TaskManager creates repair tasks
- UnifiedExecutor heals the wound

But there was no memory:

```
BEFORE:
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ DisharmonyDetector  │ → │   TaskManager       │ → │   UnifiedExecutor   │
│ (Pain Sensor)       │    │   (Creates Task)    │    │   (Heals)           │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                              ↓
                           NO RECORD
                    (Actions lost to time)
```

Without memory, we cannot:
1. Detect chronic pain (same file breaks repeatedly)
2. Analyze healing patterns (what works, what doesn't)
3. Prove the system healed itself (audit trail)

## The Solution: Samskara (Karmic Imprints)

```
AFTER (OPUS-126):
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPUS-126: THE KARMA LOOP (SAMSKARA)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. NOZIZEPTOR (Pain Receptor)                                             │
│     DisharmonyDetector.scan_all(min_severity="high")                        │
│         ↓ DisharmonyFinding                                                 │
│                                                                             │
│  2. REFLEX ARC (OPUS-125)                                                  │
│     TaskManagerPlugin._check_disharmony()                                   │
│         ↓ Creates StoredTask                                                │
│                                                                             │
│  3. KARMA RECORDING (OPUS-126) ← NEW!                                      │
│     LineageChain.add_block(REPAIR_TASK_CREATED)                            │
│         ↓ Immutable block in Parampara                                      │
│                                                                             │
│  4. SUMMARY EVENT                                                          │
│     LineageChain.add_block(REFLEX_ACTION)                                  │
│         ↓ Aggregate record of healing cycle                                 │
│                                                                             │
│  RESULT: Every reflex action is permanently recorded                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## New Event Types

Added to `LineageEventType` in `vibe_core/lineage.py`:

```python
class LineageEventType:
    # ... existing events ...

    # OPUS-126: Reflex Arc Events (Karma Loop)
    REFLEX_ACTION = "REFLEX_ACTION"           # Pain → Task → Action cycle summary
    DISHARMONY_DETECTED = "DISHARMONY_DETECTED"  # Pain sensor fired
    REPAIR_TASK_CREATED = "REPAIR_TASK_CREATED"  # Effector responded
```

## Event Data Structure

### REPAIR_TASK_CREATED

Recorded for each repair task created by the Reflex Arc:

```python
{
    "task_id": "a1b2c3d4",
    "task_title": "[HIGH] Repair disharmony: misplaced_file.py",
    "severity": "high",
    "path": "vibe_core/cli/kernel_ops.py",
    "location_varga": "OSHTHYA",  # OUTPUT layer
    "content_varga": "KANTHYA",   # KERNEL work
    "varga_distance": 4,          # Max disharmony
    "samskara": "reflex_arc"      # Karmic imprint type
}
```

### REFLEX_ACTION

Summary event for each Reflex Arc cycle:

```python
{
    "total_findings": 5,
    "tasks_created": 3,
    "min_severity": "high",
    "workspace": "/home/user/steward-protocol"
}
```

## Implementation

### Phase 1: Event Types

```python
# vibe_core/lineage.py
class LineageEventType:
    REFLEX_ACTION = "REFLEX_ACTION"
    DISHARMONY_DETECTED = "DISHARMONY_DETECTED"
    REPAIR_TASK_CREATED = "REPAIR_TASK_CREATED"
```

### Phase 2: Integration in Reflex Arc

```python
# vibe_core/plugins/task_manager/plugin_main.py

def _check_disharmony(self, project_root: Path) -> int:
    # ... detect disharmony ...

    # OPUS-126: Initialize lineage chain
    lineage = LineageChain() if LINEAGE_AVAILABLE else None

    for finding in report.findings:
        task = self.manager.add_task(...)

        # OPUS-126: Record in Parampara
        if lineage:
            lineage.add_block(
                event_type=LineageEventType.REPAIR_TASK_CREATED,
                agent_id="plugin.task_manager.reflex_arc",
                data={
                    "task_id": task.id,
                    "severity": finding.severity,
                    "path": finding.path,
                    "samskara": "reflex_arc",
                }
            )

    # OPUS-126: Record summary
    if created > 0 and lineage:
        lineage.add_block(
            event_type=LineageEventType.REFLEX_ACTION,
            agent_id="plugin.task_manager.reflex_arc",
            data={"total_findings": N, "tasks_created": created}
        )
```

## Philosophical Foundation

### Samskara (संस्कार)

In Vedic philosophy, Samskara are the karmic imprints left by our actions.
They form the basis of memory, habit, and character.

In our system:
- **Action**: Creating a repair task
- **Samskara**: The block in the Parampara chain
- **Memory**: The ability to query past actions
- **Wisdom**: Pattern detection across many Samskaras

### The Karma Loop

```
ACTION (Karma) → IMPRINT (Samskara) → MEMORY (Smriti) → WISDOM (Prajna)
     ↓                ↓                    ↓                ↓
Create task    →  Record block    →  Query history  →  Detect patterns
```

## Future Extensions (OPUS-127+)

### KarmaSense - Chronic Pain Detection

```python
class KarmaSense:
    """Detect chronic pain by analyzing Samskara patterns."""

    def find_chronic_pain(self, threshold: int = 3) -> List[ChronicPainReport]:
        """Find files that have been repaired more than threshold times."""
        blocks = self.lineage.get_blocks_by_type(LineageEventType.REPAIR_TASK_CREATED)

        # Group by path
        path_counts = Counter(b.data["path"] for b in blocks)

        return [
            ChronicPainReport(path=path, repair_count=count)
            for path, count in path_counts.items()
            if count >= threshold
        ]
```

### Integration with SutraSense

The Karma Loop enables SutraSense to:
1. Identify documentation gaps for frequently-repaired code
2. Track which OPUS docs led to healing actions
3. Measure the effectiveness of architectural decisions

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/lineage.py` | Added REFLEX_ACTION, DISHARMONY_DETECTED, REPAIR_TASK_CREATED event types |
| `vibe_core/plugins/task_manager/plugin_main.py` | Integrated LineageChain recording in _check_disharmony() |

## The Campaign Against Entropy: Memory

| OPUS | Problem | Solution |
|------|---------|----------|
| **117** | Blind system | DisharmonyDetector (pain sensors) |
| **124** | Phantom completions | Complete the circuit |
| **125** | Disconnected sensors | Reflex Arc |
| **126** | No memory | **Karma Loop (Samskara)** |

## Biological Analogy

```
HUMAN MEMORY FORMATION:
  Experience → Hippocampus encoding → Long-term storage
  (Repeated experiences strengthen memory traces)

STEWARD MEMORY FORMATION:
  Reflex Action → Parampara block → Lineage chain
  (Repeated repairs create queryable patterns)
```

## Related

- OPUS-125: Reflex Arc (the actions being recorded)
- OPUS-117: Fractal Integration (the pain sensors)
- Parampara: The lineage chain (the storage medium)
- Future: KarmaSense (pattern analysis on Samskaras)

**"What is recorded, can be learned from. What is learned from, can be improved."**
