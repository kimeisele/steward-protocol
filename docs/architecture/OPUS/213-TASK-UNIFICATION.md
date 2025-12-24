# OPUS-213: ADVAITA - Unified Task Sovereignty
> "Der Geist darf nicht gegen sich selbst arbeiten."

**Status:** APPROVED
**Author:** Senior Steward
**Date:** 2025-12-24
**Scope:** Architecture / Task Management / Persistence

---

## 1. DAS PROBLEM (Die Schizophrenie)

Das System hat ZWEI parallele Task-Systeme:

| Komponente | Speicherort | Status |
|------------|-------------|--------|
| **Core TaskManager** | `.vibe/state/tasks.json` + `vibe_agency.db` | Der Veteran |
| **Plugin TaskManager** | `plugins/task_manager/.state/tasks.json` | Der Rebell |

**Symptome:**
- Plugin-Tasks werden nicht in Core gesehen
- `vibe_agency.db` ist redundant zum Ledger
- Keine Single Source of Truth

---

## 2. DIE LÖSUNG

### Phase 0: ATOMIC WRITE (PFLICHT VOR ALLEM)
**Datei:** `vibe_core/utils/atomic_io.py`

```python
import os
import tempfile
import json
from pathlib import Path

def atomic_write_json(path: Path, data: dict) -> None:
    """Dharma: State ist entweder ALT oder NEU, niemals KORRUPT."""
    content = json.dumps(data, indent=2)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        os.write(fd, content.encode())
        os.fsync(fd)
        os.close(fd)
        os.rename(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
```

---

### Phase 1: CORE TASK MANAGER → LEDGER BACKEND

**Änderungen in:** `vibe_core/task_management/task_manager.py`

1. Entferne SQLite-Dependency (`vibe_agency.db`)
2. Nutze `VibeLedger.record_event()` für kritische Events
3. Behalte JSON-Snapshot für schnellen Boot
4. Nutze `atomic_write_json()` für Snapshots

---

### Phase 2: PLUGIN → SERVICEREGISTRY

**Änderungen in:** `vibe_core/plugins/task_manager/plugin_main.py`

1. Entferne `from .state_store import JsonTaskManager`
2. Hole Manager via `ServiceRegistry.get(TaskProtocol)`
3. Behalte Ingestion-Logik (TASKS.md, inbox/*.json)

**WICHTIG:** `state_store.py` wird NICHT gelöscht bis Phase 1 getestet!

---

### Phase 3: SERVICEREGISTRY WIRING

**Änderungen in:** `vibe_core/kernel_impl.py`

```python
from vibe_core.task_management.task_manager import TaskManager
from vibe_core.protocols.task import TaskProtocol
from vibe_core.di import ServiceRegistry

manager = TaskManager(project_root, io_service=self.io)
ServiceRegistry.register(TaskProtocol, manager)
```

---

### Phase 4: MIGRATION + CLEANUP

1. Backup `vibe_agency.db`
2. Migriere offene Tasks
3. Lösche alte Dateien

---

## 3. COMMIT-REIHENFOLGE

```
1. [feat] Add atomic_write_json utility
2. [feat] Core TaskManager uses Ledger for events
3. [feat] Register TaskManager in ServiceRegistry
4. [refactor] Plugin uses ServiceRegistry
5. [chore] Migration + cleanup
```

---

## 4. MANAS IST GETRENNT

- `kernel.think()` existiert NICHT im Kernel
- MANAS bleibt Plugin (`CognitiveKernel`)
- Tasks = MECHANISCH, MANAS = KOGNITIV
- Keine Vermischung!

---

## 5. GEMINI HANDOVER CHECKLIST

Für Junior-Entwickler (Gemini):

- [ ] Phase 0 testen: `pytest tests/unit/test_atomic_io.py`
- [ ] Phase 1 testen: `pytest tests/task_management/`
- [ ] Phase 2 testen: `pytest tests/plugins/test_task_manager.py`
- [ ] NIEMALS mehrere Phasen gleichzeitig
- [ ] NIEMALS Dateien löschen bevor Tests grün
- [ ] NIEMALS Signaturen ändern ohne existierende Tests zu prüfen
