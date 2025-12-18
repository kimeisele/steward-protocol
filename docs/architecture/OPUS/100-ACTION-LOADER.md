# OPUS-100: Action Loader - VEDA-4 Auto-Discovery for Karmendriyas

> **Status**: ✅ IMPLEMENTED
> **Created**: 2025-12-18
> **Pattern**: VEDA-4 Fractal Loader
> **Critical**: STRICT MODE ENABLED
> **Related**: OPUS-098 (AnalyzerLoader), OPUS-099 (SenseLoader), OPUS-097 (SAMKHYA)

<!-- @HARNESS
files:
  - path: vibe_core/loaders/action_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
    required: true
  - path: vibe_core/loaders/__init__.py
    required: true
tests:
  - tests/unit/loaders/test_action_loader.py
wiring:
  - pattern: "class ActionLoader"
    in: vibe_core/loaders/action_loader.py
  - pattern: "class BaseAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/base_action.py
  - pattern: "class ShellAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
  - pattern: "handled_intent_types"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
  - pattern: "def act\\("
    in: vibe_core/plugins/opus_assistant/manas/cortex/shell_action.py
config:
  - section: opus.actions
-->

---

## The Problem

IntentRouter has **hardcoded intent_type -> handler mappings**:

```python
# OLD WAY (hardcoded in intent_router.py):
def route(intent):
    if intent.type == "git_commit":
        from .cortex.shell import ShellCortex
        shell = ShellCortex(workspace=self._workspace)
        # ... manual handling
    elif intent.type == "refactor_file":
        from .cortex.silpa import SilpaArchitect
        # ... more spaghetti
```

**Problems:**
1. Adding new action requires editing router
2. Intent types scattered across router code
3. No single source of truth for "who handles what"

## The Solution: BaseAction + ActionLoader

Following the **SAMKHYA** architecture (OPUS-097):

```
KARMENDRIYAS (5 Action Organs):
- VAK (Speech)      → ShellAction      (Execute commands)
- PANI (Hands)      → SilpaAction      (Refactor code)
- PADA (Feet)       → KriyaAction      (Route intents)
- PAYU (Eliminate)  → TestAction       (Run tests)
- UPASTHA (Create)  → SankalpaAction   (Orchestrate missions)
```

### BaseAction Abstract Class

```python
# vibe_core/plugins/opus_assistant/manas/cortex/base_action.py
class BaseAction(ABC):
    name: str = ""
    handled_intent_types: Set[str] = set()  # KEY FEATURE

    def __init__(self, workspace: Path, config: Optional[Dict] = None):
        self._workspace = workspace
        self._config = config or {}

    def can_handle(self, intent_type: str) -> bool:
        return intent_type in self.handled_intent_types

    @abstractmethod
    def act(self, intent: Intent) -> ActionResult:
        """Execute an intent."""
        pass
```

### ActionLoader

```python
# vibe_core/loaders/action_loader.py
class ActionLoader:
    item_type = "action"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_action.py"
    strict_mode = True  # CRASH on errors

    @classmethod
    def discover_and_load(cls, workspace: Path):
        # Auto-discovers all *_action.py files
        # Finds BaseAction subclasses
        # Builds intent_type -> action_name mapping
        ...

    @classmethod
    def get_action_for_intent(cls, intent_type: str):
        # Returns the action that handles this intent
        ...
```

## KEY FEATURE: Intent Mapping

Each action declares its `handled_intent_types`. ActionLoader builds the mapping:

```python
class ShellAction(BaseAction):
    name = "shell_action"
    handled_intent_types = {
        "shell_execute",
        "git_status",
        "git_commit",
        "git_push",
        "run_tests",
    }
```

ActionLoader output:
```
git_status    -> shell_action
git_commit    -> shell_action
git_push      -> shell_action
run_tests     -> shell_action
shell_execute -> shell_action
```

**No more hardcoded router mappings!**

## STRICT MODE

```python
class ActionLoader:
    strict_mode = True
```

**Why STRICT MODE:**
- If an action fails to load, MANAS can't act
- Silent failures = silent impotence
- CI catches broken actions immediately

## Usage

```python
from vibe_core.loaders import ActionLoader

# Discover all actions
actions, meta = ActionLoader.discover_and_load(workspace=Path.cwd())

# Get action for an intent type
action = ActionLoader.get_action_for_intent("git_commit")
if action:
    result = action.act(intent)

# Get full intent mapping
intent_map = ActionLoader.get_intent_handler_map()
# {"git_commit": "shell_action", "git_push": "shell_action", ...}
```

## Architecture

```
vibe_core/loaders/
├── action_loader.py         # ActionLoader (this doc)
├── analyzer_loader.py       # AnalyzerLoader (OPUS-098)
├── sense_loader.py          # SenseLoader (OPUS-099)
└── ...

vibe_core/plugins/opus_assistant/manas/cortex/
├── base_action.py           # BaseAction abstract class
├── shell_action.py          # ShellAction ✅ Auto-discovered
├── (future) silpa_action.py # SilpaAction (refactoring)
├── (future) test_action.py  # TestAction (testing)
└── ...
```

## Adding New Actions

**To add a new action:**
1. Create `my_action.py` in `cortex/`
2. Inherit from `BaseAction`
3. Define `handled_intent_types`
4. Implement `act()` method
5. Done. ActionLoader discovers it automatically.

```python
# cortex/my_action.py
from .base_action import ActionResult, BaseAction

class MyAction(BaseAction):
    name = "my_action"
    handled_intent_types = {"do_something", "do_other_thing"}

    def act(self, intent):
        if intent.type == "do_something":
            return self._handle_something(intent)
        return ActionResult(
            success=False,
            action_name=self.name,
            intent_type=intent.type,
            error="Unknown intent"
        )
```

## Migration Path

Currently only `ShellAction` is converted. Future work:
1. Convert `SilpaArchitect` → `SilpaAction`
2. Convert `TestCortex` → `TestAction`
3. Convert `SankalpaOrchestrator` → `SankalpaAction`
4. Update IntentRouter to use `ActionLoader.get_action_for_intent()`

## API

```python
from vibe_core.loaders import ActionLoader

# Discover all actions (cached)
actions, metadata = ActionLoader.discover_and_load(workspace=Path.cwd())

# Get action by name
action = ActionLoader.get_action("shell_action")

# Get action for intent type
action = ActionLoader.get_action_for_intent("git_commit")

# Get handler name for intent
handler_name = ActionLoader.get_handler_for_intent("git_commit")

# Get full mapping
intent_map = ActionLoader.get_intent_handler_map()

# List all actions
names = ActionLoader.list_actions()

# Clear cache
ActionLoader.clear_cache()
```

## Related Docs

- [OPUS-097: SAMKHYA Architecture Map](097-SAMKHYA-ARCHITECTURE-MAP.md)
- [OPUS-098: Analyzer Loader](098-ANALYZER-LOADER.md)
- [OPUS-099: Sense Loader](099-SENSE-LOADER.md)
