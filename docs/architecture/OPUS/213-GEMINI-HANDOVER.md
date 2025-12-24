# OPUS-213: GEMINI HANDOVER

**Von:** Senior Steward (Opus)
**An:** Junior Partner (Gemini)
**Datum:** 2025-12-24

---

## STATUS

Phase 0 ist ABGESCHLOSSEN. Du kannst Phase 1-4 ausführen.

### Was ich gebaut habe:
- `vibe_core/utils/atomic_io.py` - Crash-sichere Schreiboperationen
- `tests/unit/test_atomic_io.py` - 13 Tests, alle grün

### Was du tun sollst:
- Phase 1-4 gemäß `213-TASK-UNIFICATION.md`

---

## REGELN (NICHT VERHANDELBAR)

### 1. EIN SCHRITT, EIN TEST, EIN COMMIT
```
FALSCH: Drei Dateien auf einmal ändern
RICHTIG: Eine Datei ändern → testen → committen → nächste
```

### 2. NIEMALS LÖSCHEN BEVOR ERSATZ FUNKTIONIERT
```
FALSCH: state_store.py löschen, dann Plugin umbauen
RICHTIG: Plugin umbauen → testen → DANN state_store.py löschen
```

### 3. SIGNATUREN PRÜFEN
```
FALSCH: def think(context: str) hinzufügen ohne Tests zu prüfen
RICHTIG: grep "kernel.think(" um existierende Aufrufe zu finden
```

### 4. ATOMIC IO NUTZEN
```python
# FALSCH:
with open(path, "w") as f:
    json.dump(data, f)

# RICHTIG:
from vibe_core.utils import atomic_write_json
atomic_write_json(path, data)
```

---

## PHASE 1: CORE TASKMANAGER → LEDGER

**Datei:** `vibe_core/task_management/task_manager.py`

**Änderungen:**

1. Import hinzufügen:
```python
from vibe_core.utils import atomic_write_json
```

2. `_save_tasks()` ändern:
```python
def _save_tasks(self):
    tasks_file = self.tasks_dir / "tasks.json"
    tasks_data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
    atomic_write_json(tasks_file, tasks_data)
```

3. SQLite-Writes BEHALTEN (noch nicht löschen!)

**Test:**
```bash
pytest tests/task_management/ -v
```

---

## PHASE 2: PLUGIN → SERVICEREGISTRY

**Datei:** `vibe_core/plugins/task_manager/plugin_main.py`

**Änderungen:**

1. Neuer Import:
```python
from vibe_core.di import ServiceRegistry
from vibe_core.protocols.task import TaskProtocol
```

2. In `on_pulse()`:
```python
manager = ServiceRegistry.get(TaskProtocol)
if not manager:
    logger.warning("TaskProtocol not registered")
    return HookResult.ok()
```

3. `state_store.py` Import ENTFERNEN
4. `self.manager` ENTFERNEN

**Test:**
```bash
pytest tests/plugins/test_task_manager.py -v
```

---

## PHASE 3: SERVICEREGISTRY WIRING

**Datei:** `vibe_core/kernel_impl.py`

**Stelle:** Nach Plugin-Boot, vor Status=RUNNING

```python
# OPUS-213: Register Core TaskManager
from vibe_core.task_management.task_manager import TaskManager
from vibe_core.protocols.task import TaskProtocol
from vibe_core.di import ServiceRegistry

if not ServiceRegistry.get(TaskProtocol):
    manager = TaskManager(Path(self.workspace))
    ServiceRegistry.register(TaskProtocol, manager)
```

**Test:**
```bash
python -c "from vibe_core.di import ServiceRegistry; from vibe_core.protocols.task import TaskProtocol; print(ServiceRegistry.get(TaskProtocol))"
```

---

## PHASE 4: MIGRATION + CLEANUP

NUR NACH PHASE 1-3 GRÜN!

1. Backup erstellen:
```bash
cp data/vibe_agency.db data/vibe_agency.db.backup
cp -r vibe_core/plugins/task_manager/.state vibe_core/plugins/task_manager/.state.backup
```

2. `state_store.py` löschen
3. `.state/` Verzeichnis löschen
4. SQLite-Code aus task_manager.py entfernen

---

## VERBOTENE AKTIONEN

1. ❌ `kernel.think()` zum RealVibeKernel hinzufügen
2. ❌ `cognition.py` überschreiben
3. ❌ Mehrere Dateien gleichzeitig ändern
4. ❌ Dateien löschen bevor Tests grün sind
5. ❌ Signaturen ändern ohne grep nach Aufrufstellen

---

## BEI PROBLEMEN

```bash
# Rollback auf sauberen Zustand:
git checkout HEAD -- vibe_core/

# Kernel-Boot testen:
python -c "from vibe_core.kernel_impl import RealVibeKernel; RealVibeKernel(ledger_path=':memory:', load_plugins=False)"

# Alle Task-Tests:
pytest tests/task_management/ -v
```

---

## ERFOLGSKRITERIEN

Phase 1-4 ist FERTIG wenn:

- [ ] `pytest tests/task_management/` - GRÜN
- [ ] `pytest tests/plugins/test_task_manager.py` - GRÜN
- [ ] Kernel bootet ohne Fehler
- [ ] `vibe_agency.db` ist gelöscht
- [ ] `state_store.py` ist gelöscht
- [ ] Ein TaskManager, ein Speicherort, ein Ledger
