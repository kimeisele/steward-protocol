# OPUS-173: Intent-Backlog Bridge (Sankalpa-Karma Link)

**Status:** PLANNING
**Author:** OPUS (Claude)
**Created:** 2025-12-21
**Sanskrit:** संकल्प-कर्म सेतु (Sankalpa-Karma Setu) = Will-Action Bridge

---

## Executive Summary

MANAS generates intents via senses (Prakriti, Dharma, Karma, etc.) and stores them in `.opus_state/manas_intents.json`. Meanwhile, the user-facing backlog lives in `workspace/BACKLOG.md`. **These two systems are completely disconnected.**

The result: MANAS thinks, but nobody sees what it thinks.

This document proposes the **Intent-Backlog Bridge** to:
1. Sync IntentBuffer → BACKLOG.md (visibility)
2. Enable MANAS to perceive BACKLOG.md (BacklogSense)
3. Create bidirectional flow for human-AI collaboration

---

## Problem Statement

### The Disconnect

```
┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
│   MANAS COGNITIVE LAYER             │     │   USER-FACING LAYER                 │
│                                     │     │                                     │
│   .opus_state/manas_intents.json    │     │   workspace/BACKLOG.md              │
│   ┌───────────────────────────────┐ │     │   ┌───────────────────────────────┐ │
│   │ • pending intents (invisible) │ │  X  │   │ ## Outstanding Tasks          │ │
│   │ • executed history            │ │◄───►│   │ - [ ] [PRIORITY] description  │ │
│   │ • reasoning, params, risk     │ │     │   └───────────────────────────────┘ │
│   └───────────────────────────────┘ │     │                                     │
│                                     │     │   agenda_tools (AddTask, ListTask)  │
│   IntentBuffer (cognitive)          │     │   (user/agent facing)               │
└─────────────────────────────────────┘     └─────────────────────────────────────┘
```

### Evidence of Staleness

```json
// .opus_state/manas_intents.json
{
  "intents": [
    {"id": "opus109_meru_test", "status": "pending", "added_at": "2025-12-18T19:39:39"},
    {"id": "manas_0001", "status": "pending", "added_at": "2025-12-18T21:58:32"}
  ],
  "updated_at": "2025-12-18T21:58:33"  // 3 DAYS OLD
}
```

MANAS hasn't ticked since Dec 18. No new intents generated.

### Root Causes

1. **No Bridge**: IntentBuffer and agenda_tools are separate systems
2. **No Tick**: MANAS only generates intents when `tick()` is called
3. **No Visibility**: User cannot see what MANAS is thinking
4. **No Feedback Loop**: User tasks in BACKLOG don't inform MANAS

---

## Proposed Solution

### Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          INTENT-BACKLOG BRIDGE                                │
│                                                                              │
│  ┌─────────────────┐         ┌─────────────────┐         ┌────────────────┐ │
│  │  IntentBuffer   │────────►│  IntentBridge   │────────►│  BACKLOG.md    │ │
│  │  (cognitive)    │         │  (translator)   │         │  (user-facing) │ │
│  └─────────────────┘         └─────────────────┘         └────────────────┘ │
│         ▲                           │                           │           │
│         │                           │                           │           │
│         │                    ┌──────┴──────┐                    │           │
│         │                    │             │                    │           │
│         │              sync_to_backlog()   │             sync_from_backlog()│
│         │                    │             │                    │           │
│         │                    ▼             ▼                    ▼           │
│  ┌─────────────────┐   ┌─────────────┐ ┌─────────────┐  ┌────────────────┐ │
│  │  BacklogSense   │◄──│  Formatter  │ │   Parser    │──│  agenda_tools  │ │
│  │  (perception)   │   │  (Int→Task) │ │  (Task→Int) │  │  (manual add)  │ │
│  └─────────────────┘   └─────────────┘ └─────────────┘  └────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. IntentBridge (New)

**Location:** `vibe_core/plugins/opus_assistant/manas/intent_bridge.py`

**Responsibilities:**
- Sync IntentBuffer entries to BACKLOG.md
- Parse BACKLOG.md tasks back to Intent format
- Handle bidirectional conflict resolution
- Maintain source tracking (MANAS vs User)

#### 2. BacklogSense (New)

**Location:** `vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py`

**Responsibilities:**
- Perceive BACKLOG.md state
- Detect new user-added tasks
- Generate intents for untracked tasks
- Monitor task completion patterns

#### 3. IntentFormatter (Utility)

**Responsibilities:**
- Convert Intent → BACKLOG.md task line
- Map priority/risk → [HIGH/MEDIUM/LOW]
- Preserve MANAS metadata in task line (optional)

#### 4. BacklogParser (Utility)

**Responsibilities:**
- Parse BACKLOG.md task lines → Intent objects
- Extract priority, description, status
- Detect source (MANAS vs User)

---

## Data Flow

### Flow A: MANAS Intent → BACKLOG.md

```
1. Sense generates Intent
2. Intent → Chitta → Buddhi → IntentBuffer.add()
3. IntentBridge.sync_to_backlog() triggered
4. Formatter converts: Intent → "- [ ] [PRIORITY] Title (MANAS: id)"
5. Append to BACKLOG.md Outstanding section
```

### Flow B: User Task → MANAS Awareness

```
1. User adds task via agenda_tools or manual edit
2. BacklogSense.perceive() detects new task
3. Parser converts: task line → Intent-like object
4. BacklogSense.generate_intents() creates tracking intent
5. MANAS now aware of user's priorities
```

### Flow C: Task Completion Sync

```
1. User completes task in BACKLOG.md
2. BacklogSense detects completed task
3. If task was MANAS-generated:
   - IntentBridge updates IntentBuffer status → "executed"
   - Karma recorded (Bhakti +5)
4. If task was User-generated:
   - BacklogSense logs completion pattern
```

---

## Implementation Plan

### Phase 1: IntentBridge Core

```python
class IntentBridge:
    """Bridge between IntentBuffer and BACKLOG.md."""

    def __init__(self, workspace: Path, buffer: IntentBuffer):
        self._workspace = workspace
        self._buffer = buffer
        self._backlog_path = workspace / "workspace" / "BACKLOG.md"

    def sync_to_backlog(self) -> int:
        """Sync pending intents to BACKLOG.md. Returns count synced."""
        pending = self._buffer.get_pending()
        synced = 0
        for intent in pending:
            if not self._is_in_backlog(intent):
                self._append_to_backlog(intent)
                synced += 1
        return synced

    def sync_from_backlog(self) -> List[Intent]:
        """Parse BACKLOG.md and return untracked tasks as intents."""
        tasks = self._parse_backlog()
        untracked = [t for t in tasks if not self._is_manas_task(t)]
        return [self._task_to_intent(t) for t in untracked]
```

### Phase 2: BacklogSense

```python
class BacklogSense(BaseSense):
    """Perceive BACKLOG.md state."""

    name = "backlog_sense"

    def perceive(self, context: Optional[Dict] = None) -> BacklogPerception:
        """Perceive backlog state."""
        tasks = self._parse_backlog()
        return BacklogPerception(
            outstanding_count=len([t for t in tasks if not t.completed]),
            completed_count=len([t for t in tasks if t.completed]),
            manas_tasks=[t for t in tasks if t.source == "manas"],
            user_tasks=[t for t in tasks if t.source == "user"],
        )

    def generate_intents(self, context: Optional[Dict] = None) -> List[Intent]:
        """Generate intents for new user tasks."""
        perception = self.perceive()
        intents = []
        for task in perception.user_tasks:
            if not self._is_tracked(task):
                intents.append(self._create_tracking_intent(task))
        return intents
```

### Phase 3: Integration with CognitiveKernel

```python
# In cognitive_kernel.py _persist phase:
async def _persist(self, context: CycleContext) -> Dict[str, str]:
    # Existing buffer save
    self._buffer.save()

    # NEW: Sync to BACKLOG.md
    if self._intent_bridge:
        synced = self._intent_bridge.sync_to_backlog()
        if synced > 0:
            logger.info(f"📋 INTENT BRIDGE: Synced {synced} intents to BACKLOG.md")

    return {}
```

---

## BACKLOG.md Format Extension

### Current Format
```markdown
## Outstanding Tasks
- [ ] [HIGH] Fix authentication bug
- [ ] [MEDIUM] Update documentation

## Completed Tasks
- [x] [HIGH] Deploy v2.0
```

### Extended Format (MANAS Metadata)
```markdown
## Outstanding Tasks
- [ ] [HIGH] Fix authentication bug
- [ ] [MEDIUM] Commit 20 pending changes <!-- manas:manas_0001 -->
- [ ] [CRITICAL] Persistence test intent <!-- manas:opus109_meru_test -->

## Completed Tasks
- [x] [HIGH] Deploy v2.0
- [x] [MEDIUM] Heal Tamas state in config/ <!-- manas:healing_001 executed:2025-12-21 -->
```

The `<!-- manas:id -->` comment preserves MANAS tracking without cluttering the UI.

---

## Success Criteria

1. **Visibility**: User can see MANAS intents in BACKLOG.md
2. **Bidirectional**: User tasks visible to MANAS via BacklogSense
3. **No Data Loss**: IntentBuffer remains source of truth for cognitive data
4. **Human-Readable**: BACKLOG.md stays clean, metadata in HTML comments
5. **Idempotent**: Multiple syncs don't create duplicates

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Sync conflicts | IntentBuffer is source of truth; BACKLOG.md is view |
| Performance | Lazy sync only on buffer.save() |
| Format corruption | Validate BACKLOG.md before write |
| User confusion | Clear prefix for MANAS tasks |

---

## @HARNESS

```yaml
<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    required: true
    rationale: "Core bridge between IntentBuffer and BACKLOG.md"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    required: true
    rationale: "VEDA-4 sense for perceiving BACKLOG.md state"
  - path: vibe_core/plugins/opus_assistant/manas/intent_buffer.py
    required: true
    rationale: "Source of truth for cognitive intents"
  - path: vibe_core/tools/agenda_tools.py
    required: true
    rationale: "User-facing backlog tools (AddTask, ListTask, CompleteTask)"

wiring:
  - pattern: "class IntentBridge"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
  - pattern: "def sync_to_backlog"
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
  - pattern: "class BacklogSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
  - pattern: "self._intent_bridge"
    in: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py

semantic:
  - type: method_exists
    name: bridge_sync_to_backlog
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    class: IntentBridge
    method: sync_to_backlog
  - type: method_exists
    name: bridge_sync_from_backlog
    in: vibe_core/plugins/opus_assistant/manas/intent_bridge.py
    class: IntentBridge
    method: sync_from_backlog
  - type: class_inherits
    name: backlog_sense_is_sense
    in: vibe_core/plugins/opus_assistant/manas/cortex/backlog_sense.py
    class: BacklogSense
    parent: BaseSense

tests:
  - tests/manas/test_intent_bridge.py
  - tests/manas/cortex/test_backlog_sense.py
-->
```

---

## Dependencies

- **OPUS-167**: IntentBuffer extraction (DONE)
- **OPUS-168**: OODA Loop / Chitta integration (DONE)
- **OPUS-172**: VEDA-4 Knowledge Integration (DONE - this session)

---

## Open Questions

1. Should MANAS auto-complete tasks when intents are executed?
2. How to handle conflicting priorities (User says HIGH, MANAS says LOW)?
3. Should BacklogSense run on every tick or only on file change?

---

## Next Steps

1. [ ] Review and approve this design
2. [ ] Implement IntentBridge core
3. [ ] Implement BacklogSense
4. [ ] Wire into CognitiveKernel._persist()
5. [ ] Test bidirectional sync
6. [ ] Document in MANAS master doc
