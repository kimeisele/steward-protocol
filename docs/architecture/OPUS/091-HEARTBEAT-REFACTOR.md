# OPUS-091: HEARTBEAT PURIFICATION (Prana Purification Operation)

**Status:** 🎯 RESEARCH & PLANNING  
**Priority:** P1 (REFACTOR - Mental Circle 0 Security Violation)  
**Date:** 2025-12-16  

---

## 🎭 THE PROBLEM: "Monolith-Logik im Pulsschlag"

`scripts/heartbeat.py` is **overstuffed with business logic**. It currently handles:

1. **Sync `TASKS.md`** ↔ TaskManager (bi-directional)
2. **Ingest tasks** from `data/inbox/*.json`
3. **Execute pending tasks** with Unified Router + MANAS gates
4. **Commit to Git** (TASKS.md + vibe_agency.db)

**Plus orchestration overhead:**
- MANAS Cognitive Kernel initialization
- MANAS Oracle pre/post-analysis gates
- SQLiteLedger (VAJRA) binding
- Plugin pulse orchestration (PRANA)
- LLM provider detection (JNANA)

**Problem Statement:**
- **Violates SoC** (Separation of Concerns) → heartbeat should be "dumb taktgeber"
- **Monolithic failure mode** → if Heartbeat crashes, unclear if it's a kernel bug or script bug
- **Security risk** (Mental Circle 0) → too many moving parts in one process
- **Untestable** → business logic intertwined with scheduling logic
- **Unmaintainable** → 785 lines of mixed concerns

---

## ✅ THE SOLUTION: "Dumb Pulse Architecture"

The heartbeat **must be reduced to:**

```python
def run():
    kernel = boot_kernel()
    while True:
        kernel.pulse()  # Alles passiert HIER DRIN
        sleep(60)
```

**This means:**
- Heartbeat = **scheduler only** (no business logic)
- Kernel.pulse() = **delegation point** (all logic lives here)
- Cartridges/Plugins = **execution units** (PRANA orchestration)

---

## 🎯 REFACTORING ROADMAP

### PHASE 1: MOVE CORE ORCHESTRATION → `vibe_core/pulse.py`

**Current:** `PulseManager` in `vibe_core/pulse.py` only emits heartbeat packets.

**Future:** `PulseManager` becomes the **unified pulse orchestrator**:

| Function | Current Location | Move To | Notes |
|----------|------------------|---------|-------|
| `_run_prana_pulse()` | Heartbeat | PulseManager | Plugin orchestration (keep as-is) |
| `_ingest_inbox()` | Heartbeat | Plugin: TaskIngest | Or: PulseManager.run_ingest_phase() |
| `_read_tasks_md()` | Heartbeat | Plugin: TaskSync | Or: PulseManager.run_sync_phase() |
| `_execute_tasks()` | Heartbeat | Plugin: TaskExecutor | Unified Router routing logic |
| `_write_tasks_md()` | Heartbeat | Plugin: TaskSync | Bi-directional sync |
| `_commit_progress()` | Heartbeat | Plugin: Chronicle | Git commit logic |
| `_manas_think()` | Heartbeat | Plugin: MANAS Pulse | MANAS invocation |

---

### PHASE 2: CARTRIDGE-BASED TASK MANAGEMENT

Create cartridges for each major concern:

#### Cartridge: `TaskIngest`
```python
# vibe_core/plugins/task_ingest.py (or cartridges/task_ingest/)
class TaskIngestPlugin(VibePlugin):
    def on_pulse(self, phase: PulsePhase):
        """Ingest JSON files from data/inbox/ into TaskManager"""
        if phase != PulsePhase.SENSORS:
            return
        
        inbox_dir = self.workspace / "data" / "inbox"
        for json_file in inbox_dir.glob("*.json"):
            task_data = json.load(open(json_file))
            self.task_manager.add_task(...)
            json_file.unlink()
```

**Benefits:**
- Testable independently
- Pluggable (can disable/replace)
- Clear ownership (TaskIngest cartridge)
- Participates in PRANA phase ordering

---

#### Cartridge: `TaskSync`
```python
# vibe_core/plugins/task_sync.py
class TaskSyncPlugin(VibePlugin):
    def on_pulse(self, phase: PulsePhase):
        if phase == PulsePhase.SENSORS:
            self._read_tasks_md()  # Parse TASKS.md → TaskManager
        elif phase == PulsePhase.CLEANUP:
            self._write_tasks_md()  # TaskManager → TASKS.md
```

**Current heartbeat logic:**
- `_read_tasks_md()` → 48 lines of regex parsing
- `_write_tasks_md()` → 88 lines of markdown generation

---

#### Cartridge: `TaskExecutor`
```python
# vibe_core/plugins/task_executor.py
class TaskExecutorPlugin(VibePlugin):
    def on_pulse(self, phase: PulsePhase):
        if phase != PulsePhase.ACTUATORS:
            return
        
        # Get next pending task
        task = self.task_manager.get_next_task()
        if not task:
            return
        
        # All routing/execution logic from _execute_tasks()
        self._execute_task(task)
```

**Current heartbeat logic:**
- `_execute_tasks()` → 199 lines (largest method)
- Handles: Router gate checking, MANAS Oracle gates, status updates
- Should be **extracted to plugin**

---

#### Cartridge: `Chronicle` (Git Integration)
```python
# vibe_core/plugins/chronicle.py
class ChroniclePlugin(VibePlugin):
    def on_pulse(self, phase: PulsePhase):
        if phase != PulsePhase.CLEANUP:
            return
        
        # Git commit logic from _commit_progress()
        self._commit_changes()
```

**Current heartbeat logic:**
- `_commit_progress()` → 27 lines
- Handles: git add, git diff, git commit
- Should be **cartridge** for auditability

---

### PHASE 3: REDUCE `scripts/heartbeat.py` TO 50 LINES

**Target structure:**

```python
#!/usr/bin/env python3
"""🫀 HEARTBEAT ENGINE - The Autonomous Task Orchestrator (Dumb Pulse)

This is ONLY a scheduler. All business logic is in Kernel.pulse().
"""

import logging
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.prana import load_config, record_heartbeat, ensure_kernel_running
from vibe_core.kernel_impl import VibeKernel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEARTBEAT")

def main():
    """Main entry point - PRANA-driven scheduler"""
    config = load_config()
    
    if not config.heartbeat.enabled:
        logger.info("💓 Heartbeat disabled in config")
        return
    
    # Boot kernel if configured
    if config.heartbeat.boot_kernel_first:
        ensure_kernel_running(config)
    
    # Record heartbeat timing
    record_heartbeat()
    
    # RUN THE PULSE (all magic happens here)
    kernel = VibeKernel(project_root)
    kernel.pulse()
    
    logger.info("✅ Heartbeat pulse complete")

if __name__ == "__main__":
    main()
```

**Changes:**
- **Remove:** 
  - HeartbeatEngine class (299 lines)
  - All business logic methods
  - MANAS initialization
  - Ledger initialization
  - Plugin orchestration code
  
- **Keep:**
  - PRANA config loading
  - Kernel initialization
  - Simple error handling

**Result: ~50 lines instead of 785** ✂️

---

### PHASE 4: KERNEL.PULSE() IMPLEMENTATION

Move orchestration to `vibe_core/kernel_impl.py`:

```python
def pulse(self):
    """Main heartbeat cycle - delegates to PulseManager"""
    logger.info("💓 HEARTBEAT PULSE STARTED")
    
    try:
        # Initialize components (lazy-load)
        self._ensure_components()
        
        # Run PRANA pulse cycle (orchestrates all plugins)
        result = self.pulse_manager.run_pulse_cycle()
        
        # Log results
        plugins_run = result.get("plugins_executed", 0)
        mutations = result.get("mutations_committed", 0)
        failures = result.get("failures", 0)
        
        logger.info(f"✅ Pulse cycle: {plugins_run} plugins, {mutations} mutations")
        
    except Exception as e:
        logger.error(f"❌ Heartbeat failed: {e}")
        raise
```

---

## 📊 IMPACT ANALYSIS

### Code Reduction

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| heartbeat.py | 785 lines | ~50 lines | **94% reduction** |
| pulse.py | 253 lines | +100 lines | +39% (new orchestration) |
| New plugins | N/A | ~600 lines | Distributed, testable |

**Total code:** ~1050 → ~750 lines (**28% reduction** + **100% testability**)

---

### Security Benefits

| Issue | Before | After |
|-------|--------|-------|
| **Monolithic failure** | Entire system blamed | Plugin isolated failure |
| **Mental Circle 0 violation** | 785 lines in taktgeber | <50 lines, SoC enforced |
| **Undefined behavior** | Business logic in scheduler | Clear separation: Kernel owns business logic |
| **Testing** | 1 massive integration test | Individual cartridge unit tests |

---

### Maintainability

| Aspect | Before | After |
|--------|--------|-------|
| **Debugging** | "Where did it crash?" | "Which plugin failed?" |
| **Feature addition** | Modify heartbeat (risky) | Add new cartridge (isolated) |
| **Dependency injection** | Hardcoded in HeartbeatEngine | Config-driven via PRANA |
| **Pluggability** | Can't disable features | Toggle via config/prana.yaml |

---

## 🎯 EXECUTION PLAN

### Sprint 1: Research & Design ✅ (THIS DOCUMENT)

- [x] Analyze current heartbeat bloat
- [x] Identify extraction boundaries
- [x] Design cartridge architecture
- [x] Estimate impact

### Sprint 2: CREATE CARTRIDGES

**Tasks:**
1. Create `TaskIngestPlugin` (move `_ingest_inbox`)
2. Create `TaskSyncPlugin` (move `_read_tasks_md`, `_write_tasks_md`)
3. Create `TaskExecutorPlugin` (move `_execute_tasks`)
4. Create `ChroniclePlugin` (move `_commit_progress`)

**Testing:** Unit tests for each cartridge

---

### Sprint 3: MOVE ORCHESTRATION TO KERNEL

1. Enhance `PulseManager` with phase orchestration
2. Create `kernel.pulse()` method
3. Integrate PRANA phase ordering
4. Wire up HeartbeatEngine → Kernel delegation

---

### Sprint 4: SIMPLIFY HEARTBEAT SCRIPT

1. Remove all business logic from heartbeat.py
2. Replace with simple Kernel.pulse() call
3. Keep PRANA config loading
4. Validate no loss of functionality

---

### Sprint 5: TESTING & VALIDATION

1. Test cartridge phase ordering
2. Test fallback when cartridges unavailable
3. Integration test: heartbeat → kernel → cartridges
4. Performance: measure pulse latency

---

## 🔗 RELATED ISSUES

- **OPUS-087:** PRANA Plugin Pulse Architecture (plugin phase ordering)
- **OPUS-074:** VAJRA Ledger Integration (immutable event log)
- **OPUS-073:** MANAS Cognitive Kernel (proactive system intelligence)

---

## 📝 NOTES

### Why This Matters: Mental Circle 0

**Mental Circle 0** = "The outermost ring of security"

If the **heartbeat is compromised**, everything else is compromised. Currently:
- Heartbeat runs 785 lines of unsandboxed Python
- No clear failure boundaries
- No rollback mechanism

**By purifying the heartbeat:**
- Reduce attack surface
- Make failures diagnostic (not fatal)
- Enable feature toggles without code changes
- Improve observability

### Alternative: Don't Refactor?

**Risks of not doing this:**
1. Heartbeat becomes impossible to debug
2. Every new feature requires heartbeat changes
3. Monolithic test suite (too slow)
4. Security audits will flag as high-risk

**Opportunity cost:** ~2 sprints now vs. 5+ sprints debugging later

---

## 🎭 CONCLUSION

The heartbeat is the **heart** of the steward-protocol. It must be **simple, reliable, and auditable**.

**OPUS-091 transforms heartbeat from:**
- 🔴 Monolithic scheduler with embedded business logic
- 🟢 **Dumb pulse that delegates to Kernel**

This enables the **Dumb Pulse Architecture**:
- **Kernel owns logic** (not scheduler)
- **Cartridges own features** (not heartbeat)
- **PRANA orchestrates phases** (not ad-hoc)

**Result:** A heartbeat you can understand in 5 minutes. ❤️

---

*Generated by Senior System Architect, 2025-12-16*
*Implementation Lead: @codebase-agent (custom agent)*
