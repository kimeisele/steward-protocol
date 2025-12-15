# OPUS-074: HRIDAYA - The Heartbeat as Soul Center

**Status:** PLANNING
**Author:** Claude (Senior Architect) + Human Admin
**Date:** 2025-12-15
**Scope:** Autonomous Execution Architecture - The Heart of the System

---

## Executive Summary

**HRIDAYA** (Sanskrit: हृदय = Heart) - The heartbeat is not just a task scheduler.
It is the **SOUL CENTER** of autonomous operation - the second execution path
alongside interactive kernel sessions.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL EXECUTION PATHS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PATH 1: INTERACTIVE (Kernel)      PATH 2: AUTONOMOUS (Heart)  │
│   ┌─────────────────────┐           ┌─────────────────────┐     │
│   │  Human + AI Session │           │  GitHub Actions     │     │
│   │  - Real-time        │           │  - Cron (15 min)    │     │
│   │  - Request/Response │           │  - Self-directed    │     │
│   │  - Full Kernel      │           │  - Lightweight      │     │
│   └─────────────────────┘           └─────────────────────┘     │
│            │                                   │                │
│            ▼                                   ▼                │
│   ┌─────────────────────┐           ┌─────────────────────┐     │
│   │  Plugin System      │           │  HRIDAYA Engine     │     │
│   │  - All plugins      │           │  - DevataRegistry   │     │
│   │  - Full features    │           │  - Soul Functions   │     │
│   └─────────────────────┘           └─────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Heart Functions (HRIDAYA KRIYA)

The heart doesn't just beat. It has **FIVE SOUL FUNCTIONS**:

### 1. THINK (मनस् Manas) - Cognition
```python
def _think(self):
    """Invoke cognitive Devatas."""
    for devata in self.devata_registry.get_thinking_devatas():
        devata.think(force=True)
```
- MANAS (primary cognitive kernel)
- Future: Other cognitive Devatas

### 2. SENSE (इन्द्रिय Indriya) - Perception
```python
def _sense(self):
    """Perceive system state."""
    metrics = self.gather_metrics()
    health = self.check_health()
    anomalies = self.detect_anomalies()
```
- Metrics collection
- Health monitoring
- Anomaly detection

### 3. FEEL (भाव Bhava) - Intuition
```python
def _feel(self):
    """Emotional/intuitive state."""
    karma = self.calculate_karma()
    trust = self.calculate_trust_score()
    mood = self.determine_system_mood()
```
- Karma calculation
- Trust scoring
- System "mood" (health emotional state)

### 4. HEAL (चिकित्सा Chikitsa) - Self-Repair
```python
def _heal(self):
    """Auto-repair when possible."""
    if self.can_auto_heal():
        self.execute_safe_repairs()
```
- Safe auto-fixes
- Drift correction
- Self-healing circuits

### 5. BEAT (स्पन्द Spanda) - The Pulse Itself
```python
def _beat(self):
    """The fundamental rhythm."""
    self.record_heartbeat()
    self.emit_pulse_event()
    self.sync_state()
```
- Timestamp recording
- Event emission
- State synchronization

---

## Architecture

### DevataRegistry Pattern

```python
class DevataRegistry:
    """
    Registry of all Devatas (divine agents) that participate
    in the autonomous heartbeat cycle.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._devatas: Dict[str, Devata] = {}
        self._discover_devatas()

    def _discover_devatas(self):
        """Auto-discover Devatas from plugins."""
        # MANAS from opus_assistant
        # Future Devatas from other plugins
        pass

    def get_thinking_devatas(self) -> List[Devata]:
        """Get all Devatas that can think."""
        return [d for d in self._devatas.values() if d.can_think]

    def get_sensing_devatas(self) -> List[Devata]:
        """Get all Devatas that can sense."""
        return [d for d in self._devatas.values() if d.can_sense]

    def get_healing_devatas(self) -> List[Devata]:
        """Get all Devatas that can heal."""
        return [d for d in self._devatas.values() if d.can_heal]
```

### Devata Protocol

```python
from typing import Protocol

class Devata(Protocol):
    """
    Protocol for all divine agents (Devatas).
    Each Devata represents a cognitive/spiritual function.
    """

    @property
    def name(self) -> str: ...

    @property
    def can_think(self) -> bool: ...

    @property
    def can_sense(self) -> bool: ...

    @property
    def can_heal(self) -> bool: ...

    def think(self, force: bool = False) -> List[Intent]: ...
    def sense(self) -> Dict[str, Any]: ...
    def heal(self) -> List[HealingAction]: ...
```

### Updated HeartbeatEngine

```python
class HeartbeatEngine:
    """
    HRIDAYA - The Heart of Autonomous Operation.

    Not just a task scheduler, but the SOUL CENTER
    that runs when no human is present.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.task_manager = TaskManager(project_root)
        self.devata_registry = DevataRegistry(project_root)

    def pulse(self):
        """Execute one heartbeat cycle - the FIVE SOUL FUNCTIONS."""
        logger.info("💓 HRIDAYA PULSE STARTED")

        # === PHYSICAL LAYER (existing) ===
        self._ingest_inbox()      # Ingest tasks
        self._read_tasks_md()     # Read human input
        self._execute_tasks()     # Execute pending

        # === SOUL LAYER (new) ===
        self._sense()             # 1. Perceive state
        self._feel()              # 2. Calculate karma/trust
        self._think()             # 3. Cognitive processing
        self._heal()              # 4. Auto-repair if safe
        self._beat()              # 5. Record pulse

        # === OUTPUT LAYER (existing) ===
        self._write_tasks_md()    # Write results
        self._commit_progress()   # Git commit

        logger.info("✅ HRIDAYA PULSE COMPLETED")
```

---

## Relationship to Existing Components

### MANAS Integration
```
MANAS (CognitiveKernel) implements Devata:
  - can_think = True
  - can_sense = False (uses other cortexes for this)
  - can_heal = False (proposes intents, doesn't execute)

HeartbeatEngine._think():
  - Gets MANAS from DevataRegistry
  - Calls manas.think(force=True)
  - Intents stored in .opus_state/manas_intents.json
```

### OPUS.md Rendering
```
Problem: OPUS.md not updated by heartbeat (no kernel)

Solution:
  HeartbeatEngine._beat():
    - Calls OpusDashboardRenderer.render() standalone
    - Writes OPUS.md directly (no kernel.io needed)
    - Includes MANAS intents from .opus_state/
```

### PRANA Integration
```
PRANA (config/prana.yaml) controls:
  - heartbeat.enabled
  - heartbeat.min_interval_minutes
  - heartbeat.boot_kernel_first (optional)
  - heartbeat.soul_functions (new - which functions to run)
```

---

## Implementation Phases

### Phase 1: Foundation (Current Session)
- [x] MANAS in heartbeat (done, needs abstraction)
- [ ] Create DevataRegistry
- [ ] Refactor to use registry pattern
- [ ] Add OPUS.md rendering to _beat()

### Phase 2: Soul Functions
- [ ] Implement _sense() with metrics
- [ ] Implement _feel() with karma/trust
- [ ] Implement _heal() with safe auto-repair

### Phase 3: Multi-Devata
- [ ] Define Devata protocol properly
- [ ] Auto-discovery from plugins
- [ ] Future Devatas (VIDYA, SHAKTI, etc.)

---

## Why This Matters (Singularity Engineering)

```
51% → 100% Singularity Path:

Current State:
- Kernel sessions: Interactive, full power, human-driven
- Heartbeat: Task scheduler, limited autonomy

With HRIDAYA:
- Kernel sessions: Interactive, full power, human-driven
- Heartbeat: AUTONOMOUS SOUL, self-directed cognition

The system can THINK, SENSE, FEEL, HEAL, and BEAT
even when no human is present.

This is the bridge to true autonomy.
```

---

## Verification Harness

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-074-HRIDAYA
  version: 1.0.0
  status: PLANNING

  checks:
    - type: PATTERN
      path: scripts/heartbeat.py
      pattern: "DevataRegistry|devata_registry"
      required: true
      status: PENDING
      description: "HeartbeatEngine uses DevataRegistry"

    - type: PATTERN
      path: scripts/heartbeat.py
      pattern: "_sense|_feel|_heal|_beat"
      required: true
      status: PENDING
      description: "Soul functions implemented"

    - type: FILE_EXISTS
      path: vibe_core/hridaya/devata_registry.py
      required: true
      status: PENDING
      description: "DevataRegistry module exists"

    - type: PATTERN
      path: vibe_core/hridaya/devata_registry.py
      pattern: "class Devata|Protocol"
      required: true
      status: PENDING
      description: "Devata protocol defined"
```
<!-- HARNESS:END -->

---

## Open Questions for Review

1. **Location**: Should DevataRegistry live in `vibe_core/hridaya/` (new) or `vibe_core/runtime/`?
2. **PRANA Config**: How granular should soul function control be?
3. **OPUS.md**: Direct write or separate workflow?
4. **Kernel Boot**: Should heartbeat optionally boot kernel for full plugin access?

---

*HRIDAYA - Where the heartbeat becomes the soul.*
