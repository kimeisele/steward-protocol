# P0: State Writer Audit

**Date:** 2025-12-20
**Status:** CRITICAL - 22+ Direct Writers Found
**Author:** Claude Opus (GURUKULA Session)

---

## Executive Summary

**FINDING:** 22 Methoden schreiben direkt in State-Dateien, ALLE bypassen den Weaver.

Das ist die Root Cause der Git-Chaos-Probleme.

---

## Direct State Writers (opus_assistant Plugin)

### CORE Module (`opus_assistant/core/`)

| File | Method | Target | Line |
|------|--------|--------|------|
| `treasury.py` | `_save()` | `.opus_state/treasury.json` | 134 |
| `state_manager.py` | `_log_observation()` | `.opus_state/observations.jsonl` | 272 |
| `state_manager.py` | `_log_karma()` | `.opus_state/karma_history.jsonl` | 353 |
| `state_manager.py` | `_log_syscall()` | `.opus_state/syscalls.jsonl` | 427 |
| `state_manager.py` | `save_session()` | `plugin/.opus_state/session.json` | 572 |

### MANAS Module (`opus_assistant/manas/`)

| File | Method | Target | Line |
|------|--------|--------|------|
| `akshara.py` | `save()` | `.opus_state/akshara_graph.json` | 887 |
| `intent_router.py` | `_save_pending_intents()` | `.opus_state/pending_intents.json` | 323 |
| `intent_router.py` | `_log_karma()` | `.opus_state/karma_log.json` | 528 |
| `intent_router.py` | `_log_system_act()` | `.opus_state/system_acts.jsonl` | 725 |
| `memory_store.py` | `_save()` | `.opus_state/manas_memory.json` | 141 |
| `cognitive_kernel.py` | `_update_synapses()` | `.opus_state/synapses.json` | 2228 |
| `cognitive_kernel.py` | `_save_intent_buffer()` | `.opus_state/manas_intents.json` | 2320 |

### CORTEX Module (`opus_assistant/manas/cortex/`)

| File | Method | Target | Line |
|------|--------|--------|------|
| `sankalpa.py` | `_save()` | `.opus_state/sankalpa.json` | 400 |
| `viveka_action.py` | `_save_entries()` | `.opus_state/viveka_decisions.json` | 317 |
| `viveka_action.py` | `_save_synapses()` | `.opus_state/synapses.json` + backups | 1340 |
| `viveka_action.py` | `_save_karma_log()` | `.opus_state/karma_log.json` | 1550 |
| `sutra_sense.py` | `_save_intent_history()` | `.opus_state/sutra_intent_history.json` | 1037 |

### DOJO Module (`opus_assistant/manas/dojo/`)

| File | Method | Target | Line |
|------|--------|--------|------|
| `runner.py` | `_save_metrics()` | `.opus_state/dojo_sessions/*.json` | 452 |
| `synaptic_seeder.py` | `_save_synapses()` | `.opus_state/synapses.json` | 453 |
| `agency.py` | `_save_state()` | `.opus_state/curiosity.json` | 159 |
| `mirror.py` | `_save_inspection()` | `.opus_state/mirror/*.json` | 455 |
| `library.py` | `_save_knowledge()` | `.opus_state/library/*.json` | 276 |

---

## Pattern Analysis

### 1. Duplicate Writers (CRITICAL)

**synapses.json wird von 3 verschiedenen Stellen geschrieben:**
- `cognitive_kernel.py:2228`
- `viveka_action.py:1340`
- `synaptic_seeder.py:453`

→ **Race Condition Risiko!**

### 2. Double State Directories

```
/.opus_state/                    ← ROOT (22 files)
/vibe_core/plugins/opus_assistant/.opus_state/  ← PLUGIN (4 files)
```

Der `state_manager.py` schreibt in PLUGIN-lokales Verzeichnis,
alle anderen schreiben nach ROOT.

### 3. Unbounded Growth

| File | Current Size | Cleanup |
|------|--------------|---------|
| `viveka_decisions.json` | 156KB | ❌ NONE |
| `session.json` | 7MB | ❌ NONE |
| `synapses_backup/` | 40+ files | ❌ NONE |
| `dojo_sessions/` | Growing | ❌ NONE |

---

## Solution Architecture

### Option A: Central State Service (Recommended)

```python
# NEW: vibe_core/state/state_service.py
class StateService:
    """Single point of truth for ALL state writes."""

    def write(self, path: Path, data: Any, category: str) -> None:
        """
        All state writes go through here.
        - Validates path is in allowed list
        - Batches writes
        - Notifies Weaver for commit
        """
        ...

    def schedule_commit(self) -> None:
        """Request Weaver to commit pending changes."""
        weaver = get_state_sync_weaver()
        weaver.pulse()
```

Migration:
1. Create `StateService`
2. Replace all 22 direct writers with `StateService.write()`
3. Weaver subscribes to StateService for commit scheduling

### Option B: Notify Pattern (Incremental)

```python
# Each existing _save() method adds:
def _save(self):
    # ... existing save logic ...

    # NEW: Notify Weaver
    from vibe_core.state.weaver import get_state_sync_weaver
    weaver = get_state_sync_weaver()
    if weaver:
        weaver.mark_dirty(self._file_path)
```

Problem: Still 22 places to modify, easy to miss.

### Option C: File System Observer (Non-Intrusive)

```python
# Weaver watches .opus_state/ for changes
from watchdog.observers import Observer

class StateWatcher:
    def on_modified(self, event):
        weaver.mark_dirty(event.src_path)
```

Problem: Adds external dependency, doesn't solve double-directory issue.

---

## Recommended Action Plan

1. **IMMEDIATE:** Consolidate double `.opus_state/` to single ROOT location
2. **SHORT-TERM:** Implement Option A (StateService)
3. **MEDIUM-TERM:** Add cleanup policies for unbounded files
4. **LONG-TERM:** Elevate MANAS from plugin to kernel subsystem

---

## Files to Modify

### Phase 1: Consolidate State Directory

```
MOVE: vibe_core/plugins/opus_assistant/.opus_state/*
  TO: /.opus_state/

UPDATE: state_manager.py to use root .opus_state/
```

### Phase 2: Introduce StateService

```
CREATE: vibe_core/state/state_service.py
UPDATE: All 22 files listed above
```

### Phase 3: Wire Weaver

```
UPDATE: StateService calls weaver.mark_dirty()
UPDATE: Heartbeat calls weaver.pulse() (already done)
REMOVE: Legacy fallback in heartbeat.py
```

---

## Verification Checklist

After fix, verify:
- [ ] Only ONE `.opus_state/` directory exists
- [ ] All writes go through StateService
- [ ] Weaver.pulse() commits all dirty files
- [ ] No legacy direct commit paths remain
- [ ] Cleanup policies prevent unbounded growth

---

*This audit is P0 priority. No new features until resolved.*
