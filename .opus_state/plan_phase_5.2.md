# OPUS-171 Phase 5.2: CortexLoader (VEDA-4 Cortex Auto-Discovery)

## Ziel
Vervollständige die VEDA-4 Pyramide mit einem CortexLoader, der Cortex-Module
dynamisch lädt und Handlers von hardcoded Imports befreit.

## Ist-Zustand

### Cortex Module (14 Kandidaten)
```
vibe_core/plugins/opus_assistant/manas/cortex/
├── shell.py      → ShellCortex (CLI execution)
├── sutra.py      → SutraWeaver, SutraOrchestrator (Wiki docs)
├── silpa.py      → SilpaArchitect (Code refactoring)
├── test.py       → TestCortex (Test runner)
├── sankalpa.py   → Sankalpa (Strategy/Planning)
├── jnana.py      → JnanaHandler (Knowledge processing)
├── kriya.py      → KriyaExtractor (Intent extraction)
├── veda.py       → Veda (Language/Trust)
├── wiring_map.py → WiringMap (Architecture audit)
├── dharma.py     → DriftReport (Compliance)
├── akasha.py     → AkashaPort (Knowledge graph)
├── mandala.py    → FractalManifest (Config)
├── mukha.py      → MukhaGenerator (Identity)
└── samvada.py    → SamvadaListener (Communication)
```

### Problem: Hardcoded Imports in Handlers
```python
# shell_handler.py - HEUTE
from ..cortex.shell import ShellCortex
shell = ShellCortex(workspace=self._workspace)

# ZIEL
cortex = CortexLoader.get_cortex("shell", workspace=self._workspace)
```

## Soll-Zustand

### VEDA-4 Stack Complete
```
                    ┌─────────────────────────────────────┐
                    │  CognitiveKernel (Orchestrator)      │
                    └───────────────┬─────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
┌───────────┐               ┌───────────────┐               ┌─────────────┐
│SenseLoader│               │ HandlerLoader │               │CortexLoader │
│(VEDA-4)   │               │   (VEDA-4)    │               │  (VEDA-4)   │
└─────┬─────┘               └───────┬───────┘               └──────┬──────┘
      │                             │                              │
      ▼                             ▼                              ▼
┌─────────────┐             ┌───────────────┐               ┌─────────────┐
│BaseSense    │             │  BaseHandler  │               │ BaseCortex  │
│├─PrakritiS. │             │├─ShellHandler │               │├─ShellCortex│
│├─DharmaS.   │             │├─SutraHandler │               │├─SutraWeaver│
│└─...        │             │└─...          │               │└─...        │
└─────────────┘             └───────────────┘               └─────────────┘
```

## Implementierungsplan

### Phase 5.2.1: BaseCortex Interface
**Datei:** `vibe_core/plugins/opus_assistant/manas/cortex/base_cortex.py`

```python
class BaseCortex(ABC):
    """Base class for all MANAS cortex modules (execution engines)."""

    name: ClassVar[str] = ""  # Unique identifier (e.g., "shell")
    capabilities: ClassVar[List[str]] = []  # What this cortex can do

    def __init__(self, workspace: Path = None, kernel: Any = None):
        self._workspace = workspace or Path.cwd()
        self._kernel = kernel

    @abstractmethod
    def execute(self, intent: Intent) -> Dict[str, Any]:
        """Execute an intent and return result."""
        pass

    def inject_kernel(self, kernel: Any) -> None:
        """Inject kernel for ledger/state access."""
        self._kernel = kernel
```

### Phase 5.2.2: CortexLoader
**Datei:** `vibe_core/loaders/cortex_loader.py`

```python
class CortexLoader(CodeModuleLoader):
    """VEDA-4 auto-discovery for cortex modules."""

    item_type = "cortex"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*.py"  # or specific pattern
    base_class_name = "BaseCortex"

    @classmethod
    def get_cortex(cls, name: str, workspace: Path = None) -> Optional[BaseCortex]:
        """Get a cortex by name."""
        pass
```

### Phase 5.2.3: Cortex Adapter Pattern
Statt alle Cortex-Module umzuschreiben (zu invasiv), erstellen wir **Adapter**:

**Datei:** `vibe_core/plugins/opus_assistant/manas/cortex/adapters/shell_adapter.py`

```python
from ..shell import ShellCortex
from ..base_cortex import BaseCortex

class ShellCortexAdapter(BaseCortex):
    """Adapter for ShellCortex to BaseCortex interface."""

    name = "shell"
    capabilities = ["git_commit", "git_push", "git_pr", "cleanup"]

    def __init__(self, workspace: Path = None, kernel: Any = None):
        super().__init__(workspace, kernel)
        self._cortex = ShellCortex(workspace=workspace)

    def execute(self, intent: Intent) -> Dict[str, Any]:
        # Delegate to underlying ShellCortex based on intent type
        if intent.intent_type in ["commit_pending_changes", "commit_and_push"]:
            return self._handle_commit(intent)
        # ... etc
```

### Phase 5.2.4: Handler Refactoring
**Beispiel: shell_handler.py**

```python
# VORHER
from ..cortex.shell import ShellCortex

def handle(self, intent):
    cortex = ShellCortex(workspace=self._workspace)
    # ...

# NACHHER
from vibe_core.loaders import CortexLoader

def handle(self, intent):
    cortex = CortexLoader.get_cortex("shell", workspace=self._workspace)
    return cortex.execute(intent)
```

## Ausführungsreihenfolge

1. **base_cortex.py** - Interface definieren
2. **cortex_loader.py** - VEDA-4 Loader erstellen
3. **Adapters** - Für ShellCortex, SutraCortex, TestCortex, SilpaCortex
4. **Handler Update** - shell_handler.py, sutra_handler.py, test_handler.py
5. **Tests** - Verify routing works end-to-end

## Risiken

| Risiko | Mitigation |
|--------|------------|
| Breaking existing cortex | Adapter pattern, no changes to originals |
| Import cycles | Lazy loading in CortexLoader |
| Performance | Caching in CortexLoader (like HandlerLoader) |

## Erfolgsmetriken

- [ ] CortexLoader discovers 4+ cortex modules
- [ ] Handlers use CortexLoader statt hardcoded imports
- [ ] Tests pass
- [ ] No breaking changes to existing cortex modules
