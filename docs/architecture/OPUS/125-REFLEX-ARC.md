# OPUS-125: The Reflex Arc - Autonomous Self-Healing

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-117 (Fractal Integration), OPUS-124 (Completing the Circuit)

## Summary

"Schmerz → Aufgabe → Aktion" (Pain → Task → Action)

OPUS-125 connects the pain sensors (DisharmonyDetector) to the effectors
(TaskManager) creating an autonomous reflex arc. When disharmony is detected,
repair tasks are automatically created - no human intervention required.

**This is the autonomic nervous system of the codebase.**

## The Problem

OPUS-117 gave us pain sensors (DisharmonyDetector).
OPUS-124 gave us working muscles (TaskManager that actually executes).

But they weren't connected:

```
BEFORE:
┌─────────────────────┐    ┌─────────────────────┐
│ DisharmonyDetector  │    │   TaskManagerPlugin │
│ (Pain Sensor)       │    │   (Effector)        │
│                     │    │                     │
│ → scan_all()        │    │   ← add_task()      │
│ → DisharmonyReport  │ ❌  │   ← execute()       │
│                     │    │                     │
└─────────────────────┘    └─────────────────────┘
         No Connection - Manual intervention required
```

The system could feel pain but not react to it automatically.

## The Solution: The Reflex Arc

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPUS-125: AUTONOMIC REFLEX ARC                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. NOZIZEPTOR (Pain Receptor)                                             │
│     DisharmonyDetector.scan_all(min_severity="high")                        │
│         ↓ DisharmonyFinding                                                 │
│                                                                             │
│  2. AFFERENTE NERVENBAHN (Sensory Pathway)                                 │
│     _finding_to_title() + _finding_to_description()                         │
│         ↓ Task parameters                                                   │
│                                                                             │
│  3. RÜCKENMARK (Spinal Cord)                                               │
│     TaskManagerPlugin._check_disharmony()                                   │
│         ↓ Decision: Create task?                                            │
│                                                                             │
│  4. EFFERENTE NERVENBAHN (Motor Pathway)                                   │
│     JsonTaskManager.add_task(type="disharmony_repair")                      │
│         ↓ StoredTask                                                        │
│                                                                             │
│  5. EFFEKTOR (Muscle)                                                       │
│     UnifiedExecutor.execute() (OPUS-124)                                    │
│                                                                             │
│  RESULT: Pain → Task → Action (No brain/human in loop)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Insight: No Brain Required

Just like a biological reflex arc bypasses the brain for faster response,
this system bypasses human intervention. The "spinal cord" (TaskManagerPlugin)
makes the decision autonomously.

## Implementation

### Phase 3 in SENSORS

```python
def _handle_sensors(self, project_root: Path) -> HookResult:
    # Phase 1: Ingest JSON files from inbox
    inbox_count = self._ingest_json_files(project_root)

    # Phase 2: Parse TASKS.md for new tasks
    markdown_count = self._read_tasks_md(project_root)

    # OPUS-125: Phase 3: Reflex Arc - Check for disharmony
    reflex_count = self._check_disharmony(project_root)

    total = inbox_count + markdown_count + reflex_count
```

### The Reflex Arc Method

```python
def _check_disharmony(self, project_root: Path) -> int:
    """OPUS-125: Reflex Arc - Scan for disharmony and create repair tasks."""

    detector = DisharmonyDetector(project_root)

    # Only react to HIGH and CRITICAL (real pain, not minor discomfort)
    report = detector.scan_all(min_severity="high")

    if report.is_harmonious:
        return 0

    created = 0
    for finding in report.findings:
        # Deduplication (avoid duplicate reflex responses)
        task_title = self._finding_to_title(finding)
        if self._task_exists(task_title):
            continue

        # Create repair task
        task = self.manager.add_task(
            title=task_title,
            description=self._finding_to_description(finding),
            type="disharmony_repair",
            metadata={
                "source": "reflex_arc",
                "severity": finding.severity,
                "path": finding.path,
                ...
            },
        )
        created += 1

    return created
```

## Task Metadata

Each reflex-generated task carries rich metadata:

```python
{
    "source": "reflex_arc",        # Origin marker
    "severity": "high",            # Pain intensity
    "path": "vibe_core/cli/x.py",  # Pain location
    "location_varga": "OSHTHYA",   # Where file is
    "content_varga": "KANTHYA",    # What file does
    "varga_distance": 4,           # How wrong (0-4)
    "evidence": [...]              # Supporting data
}
```

## Deduplication

The reflex arc includes a deduplication mechanism to prevent creating the same
repair task repeatedly:

```python
# Check for existing task (avoid duplicate reflex responses)
task_title = self._finding_to_title(finding)
existing = [t for t in self.manager.get_all_tasks() if t.title == task_title]
if existing:
    continue  # Skip - already reacting to this pain
```

## Severity Threshold

Only HIGH and CRITICAL disharmony triggers automatic task creation:

- **CRITICAL** (distance ≥ 4): OUTPUT code doing KERNEL work
- **HIGH** (distance ≥ 3): Large layer violations

LOW and MEDIUM findings are logged but don't trigger automatic action.
This prevents the system from being overwhelmed by minor discomfort.

## Full Circuit

With OPUS-124 and OPUS-125 combined:

```
DisharmonyDetector
        ↓ scan_all()
DisharmonyReport
        ↓ _check_disharmony()
StoredTask (type="disharmony_repair")
        ↓ _handle_actuators()
UnifiedRouter.route()
        ↓ (OPUS-124)
UnifiedExecutor.execute()
        ↓
Task COMPLETED/FAILED (based on actual result)
```

## Files Changed

| File | Change |
|------|--------|
| `vibe_core/plugins/task_manager/plugin_main.py` | Added `_check_disharmony()`, imports, Phase 3 |

## The Campaign Against Entropy: Complete

| OPUS | Problem | Solution |
|------|---------|----------|
| **117** | Blind system | DisharmonyDetector (pain sensors) |
| **118** | Split-Brain (CircuitState) | Canonical circuit_types.py |
| **120** | Duplicate Logic | Thin proxy, single engine |
| **121** | Namespace Collision | LedgerEvent rename |
| **122** | Task chaos | TaskStatus SSOT + DispatchTask |
| **124** | Phantom completions | Complete the circuit |
| **125** | Disconnected sensors | **Reflex Arc** |

## Biological Analogy

```
HUMAN REFLEX ARC:
  Hot stove → Pain receptor → Sensory neuron
      → Spinal cord → Motor neuron → Muscle → Hand withdraws
  (No brain involvement - response time ~50ms)

STEWARD REFLEX ARC:
  Disharmony → DisharmonyDetector → _check_disharmony()
      → TaskManagerPlugin → add_task() → execute()
  (No human involvement - autonomous healing)
```

## Philosophical Foundation

From Ayurveda: "रोगो दोषविषमसमुत्थः" - "Disease arises from imbalance."

The DisharmonyDetector measures imbalance (Varga distance).
The Reflex Arc restores balance (creates repair tasks).
The system heals itself.

**The codebase is now a living organism.**

## Related

- OPUS-117: Fractal Integration (pain sensors)
- OPUS-124: Completing the Circuit (actual execution)
- OPUS-125: Reflex Arc (connecting sensors to effectors)

---

## @HARNESS

**Files**:
- `/home/user/steward-protocol/vibe_core/plugins/task_manager/plugin_main.py`
  - `TaskManagerPlugin._check_disharmony()` - Phase 3 of SENSORS (OPUS-125)
  - `_finding_to_title()` - converts DisharmonyFinding to task title
  - `_finding_to_description()` - converts finding to task description
  - `_task_exists()` - deduplication check
  - `_handle_sensors()` - includes Phase 3: reflex arc
- `/home/user/steward-protocol/vibe_core/plugins/opus_assistant/manas/disharmony_detector.py`
  - `DisharmonyDetector` class - pain sensors
  - `scan_all()` - scans for disharmony (min_severity filter)
  - `DisharmonyReport` - collection of findings
  - `DisharmonyFinding` - individual pain signal

**Wiring Pattern**:
```python
# REFLEX ARC (autonomic response - no human in loop)
detector = DisharmonyDetector(project_root)
report = detector.scan_all(min_severity="high")  # Only HIGH/CRITICAL pain

for finding in report.findings:
    # Deduplication
    if self._task_exists(self._finding_to_title(finding)):
        continue

    # Create repair task (effector response)
    task = self.manager.add_task(
        title=self._finding_to_title(finding),
        description=self._finding_to_description(finding),
        type="disharmony_repair",
        metadata={
            "source": "reflex_arc",
            "severity": finding.severity,
            "path": finding.path,
            "varga_distance": finding.varga_distance,
        }
    )
```

**Autonomic Loop**:
```
DisharmonyDetector (pain) → _check_disharmony() (spinal cord)
    → add_task() (motor neuron) → execute() (muscle) - NO BRAIN REQUIRED
```
