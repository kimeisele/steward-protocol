# KERNEL STABILIZATION PLAN

> **Ziel:** kernel_impl.py wird NIE WIEDER angefasst
> **Für:** Nächster Senior Agent
> **Priorität:** P0 (ABSOLUT vor allem anderen)

---

## Philosophie: "Zu Ende Gedacht"

**Problem mit Interface-Extraktion allein:**
```python
# Kernel muss trotzdem bei jedem neuen Interface angefasst werden:
self._ui_manager.sync_all()      # Hardcoded
self._playbook_bridge.execute()  # Hardcoded
# Neues Interface? → Kernel anfassen → Churn!
```

**Lösung: Plugin/Hook-System**
```python
# Kernel lädt Plugins AUTOMATISCH - keine Hardcoded Calls:
self._plugins = PluginLoader.discover("vibe_core/plugins/")

# Neues Plugin? → Datei erstellen → Kernel NICHT anfassen!
```

---

## Phase 1: Plugin-System (ZUERST)

### 1.1 Plugin Protocol definieren
```python
# vibe_core/plugin_protocol.py (NEU)
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

class KernelPlugin(ABC):
    """Base class for all kernel plugins."""

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""
        pass

    @property
    def priority(self) -> int:
        """Execution order (lower = earlier). Default: 100."""
        return 100

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called once when kernel boots."""
        pass

    def on_tick(self, kernel: "RealVibeKernel") -> None:
        """Called every kernel tick."""
        pass

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel shuts down."""
        pass
```

### 1.2 Plugin Loader erstellen
```python
# vibe_core/plugin_loader.py (NEU)
import importlib
import pkgutil
from pathlib import Path
from typing import List
from .plugin_protocol import KernelPlugin

class PluginLoader:
    @staticmethod
    def discover(plugin_dir: str = "vibe_core/plugins") -> List[KernelPlugin]:
        """Auto-discover and load all plugins from directory."""
        plugins = []
        plugin_path = Path(plugin_dir)

        if not plugin_path.exists():
            return plugins

        for module_info in pkgutil.iter_modules([str(plugin_path)]):
            module = importlib.import_module(f"vibe_core.plugins.{module_info.name}")

            # Find KernelPlugin subclasses
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type)
                    and issubclass(attr, KernelPlugin)
                    and attr is not KernelPlugin):
                    plugins.append(attr())

        # Sort by priority
        return sorted(plugins, key=lambda p: p.priority)
```

### 1.3 Kernel EINMAL anpassen (letzte Änderung!)
```python
# vibe_core/kernel_impl.py - FINALE VERSION:

from .plugin_loader import PluginLoader

class RealVibeKernel:
    def __init__(self):
        # ... existing init ...

        # PLUGIN SYSTEM (einziger extensibility point)
        self._plugins = PluginLoader.discover()
        for plugin in self._plugins:
            plugin.on_boot(self)

    def tick(self):
        # ... existing tick logic ...

        # ALLE PLUGINS (keine hardcoded calls mehr!)
        for plugin in self._plugins:
            plugin.on_tick(self)

    def shutdown(self):
        for plugin in self._plugins:
            plugin.on_shutdown(self)
```

---

## Phase 2: Existierende UI als Plugins migrieren

### 2.1 Settings Plugin
```python
# vibe_core/plugins/settings_ui.py (NEU)
from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.settings_sync import SettingsSync

class SettingsUIPlugin(KernelPlugin):
    plugin_id = "settings_ui"
    priority = 50  # Early in tick

    def __init__(self):
        self.sync = SettingsSync()
        self.last_modified = 0.0

    def on_tick(self, kernel):
        self.sync.sync(kernel)
```

### 2.2 Envoy Plugin
```python
# vibe_core/plugins/envoy_ui.py (NEU)
from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.envoy_sync import EnvoySync

class EnvoyUIPlugin(KernelPlugin):
    plugin_id = "envoy_ui"
    priority = 60

    def __init__(self):
        self.sync = EnvoySync()
        self.pending_tasks = {}

    def on_tick(self, kernel):
        self.sync.sync(kernel, self.pending_tasks)
```

### 2.3 Kernel State-Variablen ENTFERNEN
```python
# kernel_impl.py - LÖSCHEN:
# self._settings_last_modified    → jetzt in SettingsUIPlugin
# self._envoy_pending_tasks       → jetzt in EnvoyUIPlugin
# self._paused_agents             → jetzt in SettingsUIPlugin
```

---

## Phase 3: Hash-Verification (NACHDEM Plugin-System steht)

### 3.1 Kernel Hash generieren
```python
# scripts/governance/verify_kernel.py (NEU)
import hashlib
from pathlib import Path

PROTECTED_FILES = [
    "vibe_core/kernel_impl.py",
    "vibe_core/plugin_protocol.py",
    "vibe_core/plugin_loader.py",
]

def generate_hashes():
    hashes = {}
    for file in PROTECTED_FILES:
        content = Path(file).read_bytes()
        hashes[file] = hashlib.sha256(content).hexdigest()
    return hashes

def verify_hashes(expected: dict) -> bool:
    current = generate_hashes()
    for file, expected_hash in expected.items():
        if current.get(file) != expected_hash:
            print(f"❌ INTEGRITY VIOLATION: {file}")
            return False
    print("✅ Kernel integrity verified")
    return True
```

### 3.2 CI Integration
```yaml
# .github/workflows/kernel-integrity.yml
- name: Verify Kernel Integrity
  run: python scripts/governance/verify_kernel.py --verify

- name: Block Kernel Changes
  if: contains(github.event.pull_request.changed_files, 'kernel_impl.py')
  run: |
    echo "⚠️ kernel_impl.py was modified!"
    echo "This requires SENIOR REVIEW approval."
    exit 1  # Or require specific label
```

---

## Status Quo (was bereits existiert)

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
