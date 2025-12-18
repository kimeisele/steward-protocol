# OPUS-098: Analyzer Loader - VEDA-4 Auto-Discovery

> **Status**: ✅ IMPLEMENTED
> **Created**: 2025-12-18
> **Pattern**: VEDA-4 Fractal Loader
> **Critical**: STRICT MODE ENABLED

<!-- @HARNESS
files:
  - path: vibe_core/loaders/analyzer_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/intent_generator.py
    required: true
  - path: vibe_core/loaders/__init__.py
    required: true
tests:
  - tests/unit/loaders/test_analyzer_loader.py
  - tests/integration/test_manas_integration.py
wiring:
  - pattern: "class AnalyzerLoader"
    in: vibe_core/loaders/analyzer_loader.py
  - pattern: "AnalyzerLoader.discover_and_load"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
  - pattern: "from vibe_core.loaders import AnalyzerLoader"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
absent:
  - pattern: "_register_modular_analyzers"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
  - pattern: "ContractAnalyzer\\(workspace"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
  - pattern: "SemanticAnalyzer\\(workspace"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
config:
  - section: opus.analyzers
-->

---

## The Problem

Manual analyzer registration was **SPAGHETTI**:

```python
# OLD WAY (DELETED):
def _register_modular_analyzers(self):
    from .analyzers import (
        CIMonitorAnalyzer,
        ContractAnalyzer,
        DocHarnessAnalyzer,  # Added manually, often forgotten
        PratyayaAnalyzer,
        SemanticAnalyzer,
    )
    return [
        ContractAnalyzer(workspace=self._workspace),
        SemanticAnalyzer(workspace=self._workspace),
        # ... manual list breaks every time someone adds an analyzer
    ]
```

**Failure modes:**
1. Someone adds new analyzer → forgets to add to list → analyzer never runs
2. Someone renames analyzer → import breaks silently
3. CI passes but feature doesn't work
4. The system lobotomizes itself without anyone noticing

## The Solution: AnalyzerLoader

Following the **VEDA-4 Fractal Pattern** (same as PluginLoader, CircuitLoader):

```python
# NEW WAY:
def _load_analyzers_veda4(self):
    from vibe_core.loaders import AnalyzerLoader

    analyzers, metadata = AnalyzerLoader.discover_and_load(
        workspace=self._workspace,
        strict=True,  # CRASH on errors, no silent skip
    )
    return list(analyzers.values())
```

**To add a new analyzer:**
1. Create `my_analyzer.py` in `analyzers/`
2. Inherit from `BaseAnalyzer`
3. Done. AnalyzerLoader discovers it automatically.

## STRICT MODE (Critical Design Decision)

```python
class AnalyzerLoader:
    strict_mode = True  # CRASH on errors, no silent skip
```

**Why STRICT MODE:**
- Silent failures are the enemy
- If an analyzer fails to load, you KNOW immediately
- No more "it works on my machine" because CI catches it
- System cannot silently lobotomize itself

**What happens on failure:**
```
AnalyzerLoadError: STRICT MODE: 1 analyzer(s) failed to load:
  - Failed to load analyzer module broken_analyzer.py: SyntaxError

Fix these errors before continuing. No silent failures allowed.
```

## Architecture

```
vibe_core/loaders/
├── __init__.py              # Exports AnalyzerLoader
├── base_loader.py           # UnifiedLoader base class
├── analyzer_loader.py       # AnalyzerLoader (this doc)
├── circuit_loader.py        # Same pattern for circuits
└── plugin_loader.py         # Same pattern for plugins

vibe_core/plugins/opus_assistant/manas/analyzers/
├── __init__.py              # Exports (for manual import, still works)
├── base.py                  # BaseAnalyzer abstract class
├── ci_monitor_analyzer.py   # Auto-discovered
├── contract_analyzer.py     # Auto-discovered
├── doc_harness_analyzer.py  # Auto-discovered
├── pratyaya_analyzer.py     # Auto-discovered
└── semantic_analyzer.py     # Auto-discovered
```

## API

```python
from vibe_core.loaders import AnalyzerLoader

# Discover all analyzers
analyzers, metadata = AnalyzerLoader.discover_and_load(
    workspace=Path.cwd(),
    strict=True,  # Default: True
)

# Get list of analyzer names
names = AnalyzerLoader.list_analyzers()

# Get specific analyzer
ci_monitor = AnalyzerLoader.get_analyzer("ci_monitor")

# Clear cache (for testing)
AnalyzerLoader.clear_cache()
```

## Hard-Cut Verification

The `@HARNESS` section above includes `absent` patterns to verify the manual list was truly deleted:

```yaml
absent:
  - pattern: "_register_modular_analyzers"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
  - pattern: "ContractAnalyzer\\(workspace"
    in: vibe_core/plugins/opus_assistant/manas/intent_generator.py
```

This ensures:
1. No hybrid state (manual + auto coexisting)
2. Hard-cut was complete
3. Regression is impossible without breaking harness

## Related Docs

- [OPUS-032: MANAS Cognitive Kernel](032-MANAS-COGNITIVE-KERNEL.md)
- [OPUS-015: Container Format](015-CONTAINER-FORMAT.md)
- [OPUS-023: Fractal UI Architecture](023-FRACTAL-UI-ARCHITECTURE.md)
