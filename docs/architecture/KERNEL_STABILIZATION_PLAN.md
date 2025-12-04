# KERNEL STABILIZATION PLAN

> **Ziel:** kernel_impl.py wird NICHT mehr angefasst für UI-Features
> **Für:** Nächster Senior Agent
> **Priorität:** P0 (vor allen anderen Features)

---

## Status Quo

**Bereits extrahiert:**
```
vibe_core/
├── settings_sync.py    # SettingsSync Klasse existiert
├── envoy_sync.py       # EnvoySync Klasse existiert
├── doc_renderer.py     # DocRenderer existiert
├── settings_executor.py # Command execution
```

**PROBLEM:** Kernel hat noch State-Variablen die in Sync-Module gehören:
```python
# kernel_impl.py - DIESE MÜSSEN RAUS:
self._settings_last_modified = 0.0
self._settings_writing = False
self._settings_execution_history = deque(maxlen=10)
self._paused_agents = set()
self._envoy_last_modified = 0.0
self._envoy_pending_tasks = {}
```

**Tests erwarten Methoden die NICHT im Kernel sein sollten:**
- `_render_settings_file()` → gehört in SettingsSync
- `_parse_settings_commands()` → gehört in SettingsSync
- `_render_envoy_file()` → gehört in EnvoySync
- `_dispatch_envoy_request()` → gehört in EnvoySync

---

## Architektur-Ziel

```
┌─────────────────────────────────────────────────────────┐
│                    kernel_impl.py                        │
│  - Agent Registry                                        │
│  - Task Scheduling                                       │
│  - Tick Loop                                             │
│  - KEINE UI/Markdown Logik!                              │
└─────────────────────────────────────────────────────────┘
           │
           │ kernel.tick() ruft auf:
           ▼
┌─────────────────────────────────────────────────────────┐
│              MarkdownUIManager (NEU)                     │
│  - Koordiniert alle Sync-Module                          │
│  - Hat ALLEN State (last_modified, pending_tasks, etc)   │
└─────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┬─────────────┐
     ▼           ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────────┐
│Settings │ │ Envoy   │ │ DocRenderer │
│  Sync   │ │  Sync   │ │             │
└─────────┘ └─────────┘ └─────────────┘
```

---

## Implementation Steps

### Step 1: MarkdownUIManager erstellen
```python
# vibe_core/markdown_ui_manager.py (NEU)

class MarkdownUIManager:
    """Zentrale Koordination aller Markdown-Interfaces."""

    def __init__(self, kernel_ref):
        self.kernel = kernel_ref  # Weak reference zum Kernel
        self.settings_sync = SettingsSync()
        self.envoy_sync = EnvoySync()
        self.doc_renderer = DocRenderer()

        # STATE HIERHIN VERSCHOBEN:
        self.settings_last_modified = 0.0
        self.envoy_last_modified = 0.0
        self.envoy_pending_tasks = {}
        self.paused_agents = set()

    def sync_all(self):
        """Called by kernel.tick() - einziger Einstiegspunkt."""
        self.settings_sync.sync(self)
        self.envoy_sync.sync(self)
```

### Step 2: Kernel State entfernen
```python
# kernel_impl.py - ÄNDERUNGEN:

# LÖSCHEN:
# self._settings_last_modified = 0.0
# self._envoy_pending_tasks = {}
# etc.

# HINZUFÜGEN:
from .markdown_ui_manager import MarkdownUIManager

def __init__(self):
    # ... existing code ...
    self._ui_manager = MarkdownUIManager(self)

def tick(self):
    # ... existing code ...
    self._ui_manager.sync_all()  # EINZIGER UI-Call
```

### Step 3: Tests anpassen
```python
# Tests sollten MarkdownUIManager testen, NICHT Kernel:

def test_render_settings():
    manager = MarkdownUIManager(mock_kernel)
    manager.settings_sync.render()
    # ...
```

---

## Dateien die geändert werden

| Datei | Aktion |
|-------|--------|
| `vibe_core/markdown_ui_manager.py` | NEU erstellen |
| `vibe_core/kernel_impl.py` | State-Variablen entfernen, UI-Manager nutzen |
| `vibe_core/settings_sync.py` | An Manager anpassen |
| `vibe_core/envoy_sync.py` | An Manager anpassen |
| `tests/integration/test_kernel_markdown_interfaces.py` | Auf Manager umstellen |

---

## Prioritäten danach

1. **P1: Stub-Fixes** (WIRING_ROADMAP_V3.md P7.1)
   - `kernel.execute_playbook()` → aber in PlaybookBridge, NICHT in Kernel!

2. **P2: UI Verbesserungen**
   - Einheitlicher Header für alle .md Files
   - Settings.md: Provider-Auswahl, Live-Fire Toggle
   - Matrix.md: 3D-Visualisierung

3. **P3: Hash-Verification**
   - Core-Files (kernel_impl.py, protocols/) bekommen Hash
   - CI prüft: "Wurde Kernel modifiziert? → Extra Review required"

---

## Erfolgs-Kriterien

- [ ] kernel_impl.py hat KEINE `_render_`, `_parse_`, `_sync_` Methoden
- [ ] kernel_impl.py hat KEINE UI-State-Variablen
- [ ] Kernel ruft nur `self._ui_manager.sync_all()` im Tick
- [ ] Alle 33 failing Tests passen oder sind korrekt geskipped
- [ ] Churn auf kernel_impl.py sinkt auf ~0

---

*"Der Kernel ist der Motor. UI ist das Dashboard. Beides getrennt halten."*
