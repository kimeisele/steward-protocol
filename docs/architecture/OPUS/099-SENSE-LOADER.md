# OPUS-099: Sense Loader - VEDA-4 Auto-Discovery for Cortex

> **Status**: ✅ IMPLEMENTED
> **Created**: 2025-12-18
> **Pattern**: VEDA-4 Fractal Loader
> **Critical**: STRICT MODE ENABLED
> **Related**: OPUS-098 (AnalyzerLoader), OPUS-097 (SAMKHYA)

<!-- @HARNESS
files:
  - path: vibe_core/loaders/sense_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
  - path: vibe_core/loaders/__init__.py
    required: true
tests:
  - tests/unit/loaders/test_sense_loader.py
wiring:
  - pattern: "class SenseLoader"
    in: vibe_core/loaders/sense_loader.py
  - pattern: "class BaseSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/base.py
  - pattern: "class PrakritiSense\\(BaseSense\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "class DharmaSense\\(BaseSense\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
  - pattern: "class SutraSense\\(BaseSense\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "def perceive\\("
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "def perceive\\("
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
  - pattern: "def perceive\\("
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
config:
  - section: opus.senses
-->

---

## The Problem

MANAS has perception organs (Jnanendriyas) in `cortex/`:
- `prakriti_sense.py` - System state perception
- `dharma_sense.py` - Ethical alignment
- `sutra_sense.py` - Doc/Code gap detection

But they were **standalone classes** - no common interface, no auto-discovery.
Adding a new sense required manual imports everywhere.

## The Solution: BaseSense + SenseLoader

Following the **SAMKHYA** architecture (OPUS-097):

```
JNANENDRIYAS (5 Perception Organs):
- TVAK (Touch)    → PrakritiSense  (System state)
- CHAKSHU (Sight) → SutraSense     (Doc/Code gaps)
- RASANA (Taste)  → DharmaSense    (Ethical check)
```

### BaseSense Abstract Class

```python
# vibe_core/plugins/opus_assistant/manas/cortex/base.py
class BaseSense(ABC):
    name: str = ""  # Unique identifier

    def __init__(self, workspace: Path, config: Optional[Dict] = None):
        self._workspace = workspace
        self._config = config or {}

    @abstractmethod
    def perceive(self, context: Optional[Dict] = None) -> Any:
        """Main perception method."""
        pass
```

### SenseLoader

```python
# vibe_core/loaders/sense_loader.py
class SenseLoader:
    item_type = "sense"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_sense.py"  # Only scan sense files
    strict_mode = True  # CRASH on errors

    @classmethod
    def discover_and_load(cls, workspace: Path) -> Tuple[SenseRegistry, SenseMetadata]:
        # Auto-discovers all *_sense.py files
        # Finds BaseSense subclasses
        # Instantiates with workspace
        ...
```

## STRICT MODE (Critical)

```python
class SenseLoader:
    strict_mode = True  # CRASH on errors, no silent skip
```

**Why STRICT MODE:**
- If a sense fails to load, MANAS is BLIND
- Silent failures = silent lobotomy
- CI catches broken senses immediately

**What happens on failure:**
```
SenseLoadError: STRICT MODE: 1 sense(s) failed to load:
  - Failed to load sense module broken_sense.py: SyntaxError

Fix these errors before continuing. MANAS cannot be blind.
```

## Usage

```python
from vibe_core.loaders import SenseLoader

# Discover all senses
senses, meta = SenseLoader.discover_and_load(workspace=Path.cwd())

# Get specific sense
prakriti = senses.get("prakriti_sense")
summary = prakriti.perceive()

# Or use utility method
dharma = SenseLoader.get_sense("dharma_sense")
```

## Architecture

```
vibe_core/loaders/
├── sense_loader.py          # SenseLoader (this doc)
├── analyzer_loader.py       # AnalyzerLoader (OPUS-098)
└── ...

vibe_core/plugins/opus_assistant/manas/cortex/
├── base.py                  # BaseSense abstract class
├── prakriti_sense.py        # Auto-discovered ✅
├── dharma_sense.py          # Auto-discovered ✅
├── sutra_sense.py           # Auto-discovered ✅
└── ...
```

## Adding New Senses

**To add a new sense:**
1. Create `my_sense.py` in `cortex/`
2. Inherit from `BaseSense`
3. Implement `perceive()` method
4. Done. SenseLoader discovers it automatically.

```python
# cortex/my_sense.py
from .base import BaseSense

class MySense(BaseSense):
    name = "my_sense"

    def perceive(self, context=None):
        return {"detected": True}
```

## API

```python
from vibe_core.loaders import SenseLoader

# Discover all senses (cached)
senses, metadata = SenseLoader.discover_and_load(workspace=Path.cwd())

# Force refresh
senses, metadata = SenseLoader.discover_and_load(force_refresh=True)

# List sense names
names = SenseLoader.list_senses()

# Get specific sense
sense = SenseLoader.get_sense("prakriti_sense")

# Clear cache
SenseLoader.clear_cache()
```

## Related Docs

- [OPUS-097: SAMKHYA Architecture Map](097-SAMKHYA-ARCHITECTURE-MAP.md)
- [OPUS-098: Analyzer Loader](098-ANALYZER-LOADER.md)
- [OPUS-009: Prakriti Sense](009-PRAKRITI-STATE-ENGINE.md)
