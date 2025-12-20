# OPUS-158: Infrastructure Genesis - The Stadtamt Service

> **Status**: DESIGNING
> **Created**: 2025-12-20
> **Pattern**: Agent Virus (Self-Replicating Infrastructure)
> **Depends**: OPUS-156 (ShrutaSense), GAD-000 (Operator Inversion)

---

## Preamble: The Hen-and-Egg Problem

```
Problem: AI needs infrastructure to operate
         But infrastructure must be created first
         Who creates the infrastructure that AI needs?

Traditional: Human creates files manually
Agent Virus: System auto-generates GAD-000 compliant files
```

**"Wir brauchen Straßenarbeiter die alles vorbereiten - diese `__init__.py` und manifest files."**

## The Stadtamt Metaphor

In every German city, the **Stadtamt** (city office) ensures:
- Every house has a mailbox (addressable)
- Every street has a sign (discoverable)
- Every building has utilities connected (operable)

**InfrastructureGenesis IS the Stadtamt for STEWARD:**
- Every module gets `__init__.py` (importable)
- Every plugin gets `manifest.json` (discoverable)
- Every component gets base class inheritance (operable)

---

## Architecture

### The Agent Virus Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT VIRUS LOOP                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. DETECT (ShrutaSense - OPUS-156)                                 │
│     └─ Perceive filesystem vibrations                               │
│     └─ Filter: directory_created, file_created                      │
│                                                                      │
│  2. CLASSIFY (InfrastructureClassifier)                             │
│     └─ Determine module type from path patterns                      │
│     └─ Types: plugin, analyzer, sense, action, circuit, section     │
│                                                                      │
│  3. GENERATE (InfrastructureGenesis)                                │
│     └─ Create required files based on type                          │
│     └─ __init__.py, manifest.json, base_*.py                        │
│                                                                      │
│  4. WIRE (LoaderRegistry)                                            │
│     └─ Register with appropriate loader                             │
│     └─ Trigger cache refresh                                         │
│                                                                      │
│  5. REPLICATE                                                        │
│     └─ Pattern spreads to every new module                          │
│     └─ System becomes self-organizing                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
vibe_core/plugins/opus_assistant/manas/
├── cortex/
│   ├── shruta_sense.py          # DETECT  - Already exists (OPUS-156)
│   └── genesis/                  # NEW - InfrastructureGenesis
│       ├── __init__.py
│       ├── classifier.py        # CLASSIFY - Determine module type
│       ├── generator.py         # GENERATE - Create infrastructure
│       └── templates/           # Templates for each module type
│           ├── plugin/
│           │   ├── __init__.py.template
│           │   ├── manifest.json.template
│           │   └── plugin_main.py.template
│           ├── analyzer/
│           │   └── analyzer.py.template
│           ├── sense/
│           │   └── sense.py.template
│           ├── action/
│           │   └── action.py.template
│           └── section/
│               └── manifest.json.template
```

---

## GAD-000 Compliance Checklist (Per Module Type)

### Plugin Infrastructure

| File | GAD-000 Purpose | Required |
|------|-----------------|----------|
| `__init__.py` | Discoverability (Python import) | YES |
| `manifest.json` | Discoverability (capabilities, version) | YES |
| `plugin_main.py` | Entry point (entry_point in manifest) | YES |

### Analyzer Infrastructure

| File | GAD-000 Purpose | Required |
|------|-----------------|----------|
| `*_analyzer.py` | Naming convention (loader pattern match) | YES |
| Inherit `BaseAnalyzer` | Composability (interface contract) | YES |

### Sense Infrastructure

| File | GAD-000 Purpose | Required |
|------|-----------------|----------|
| `*_sense.py` | Naming convention (loader pattern match) | YES |
| Inherit `BaseSense` | Composability (interface contract) | YES |
| `name` attribute | Discoverability (unique identifier) | YES |
| `perceive()` method | Composability (standard interface) | YES |

### Action Infrastructure

| File | GAD-000 Purpose | Required |
|------|-----------------|----------|
| `*_action.py` | Naming convention (loader pattern match) | YES |
| Inherit `BaseAction` | Composability (interface contract) | YES |
| `handled_intent_types` | Discoverability (intent routing) | YES |
| `act()` method | Composability (standard interface) | YES |

### Phoenix Section Infrastructure

| File | GAD-000 Purpose | Required |
|------|-----------------|----------|
| `manifest.json` | Discoverability (schema, version) | YES |
| `validate()` function | Idempotency (validation before apply) | YES |

---

## Implementation

### InfrastructureClassifier

```python
# vibe_core/plugins/opus_assistant/manas/cortex/genesis/classifier.py

from enum import Enum, auto
from pathlib import Path
from typing import Optional

class ModuleType(Enum):
    PLUGIN = auto()          # vibe_core/plugins/*
    ANALYZER = auto()        # */analyzers/*.py
    SENSE = auto()           # */cortex/*_sense.py
    ACTION = auto()          # */cortex/*_action.py
    CIRCUIT = auto()         # */circuits/*.yaml
    SECTION = auto()         # phoenix/sections/*
    KNOWLEDGE = auto()       # knowledge/*
    UNKNOWN = auto()         # Cannot classify

class InfrastructureClassifier:
    """
    Classify new directories/files by their purpose.

    Uses path patterns to determine what infrastructure is needed.
    """

    PATTERNS = {
        ModuleType.PLUGIN: [
            "vibe_core/plugins/*",
        ],
        ModuleType.ANALYZER: [
            "*/manas/analyzers/*",
        ],
        ModuleType.SENSE: [
            "*/manas/cortex/*",  # Only if *_sense.py
        ],
        ModuleType.ACTION: [
            "*/manas/cortex/*",  # Only if *_action.py
        ],
        ModuleType.CIRCUIT: [
            "*/circuits/*",
            "*/playbook/circuits/*",
        ],
        ModuleType.SECTION: [
            "vibe_core/phoenix/sections/*",
        ],
        ModuleType.KNOWLEDGE: [
            "knowledge/*",
        ],
    }

    def classify(self, path: Path, is_directory: bool) -> ModuleType:
        """
        Classify a path to determine required infrastructure.

        Args:
            path: Absolute or relative path to new file/directory
            is_directory: True if this is a directory

        Returns:
            ModuleType indicating what infrastructure to generate
        """
        path_str = str(path)

        # Check each pattern
        for module_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if self._matches_pattern(path_str, pattern):
                    return module_type

        return ModuleType.UNKNOWN

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Match path against glob-like pattern."""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
```

### InfrastructureGenerator

```python
# vibe_core/plugins/opus_assistant/manas/cortex/genesis/generator.py

import json
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Dict, Optional

from .classifier import ModuleType

class InfrastructureGenerator:
    """
    Generate GAD-000 compliant infrastructure files.

    The Stadtamt - creates mailboxes for every house.
    """

    def __init__(self, workspace: Path, templates_dir: Optional[Path] = None):
        self._workspace = workspace
        self._templates_dir = templates_dir or self._get_default_templates()

    def generate(self, path: Path, module_type: ModuleType) -> Dict[str, Path]:
        """
        Generate infrastructure files for a module.

        Args:
            path: Path to the new module directory
            module_type: Type of module (from classifier)

        Returns:
            Dict mapping file type to created path
        """
        if module_type == ModuleType.UNKNOWN:
            return {}

        generators = {
            ModuleType.PLUGIN: self._generate_plugin,
            ModuleType.ANALYZER: self._generate_analyzer,
            ModuleType.SENSE: self._generate_sense,
            ModuleType.ACTION: self._generate_action,
            ModuleType.SECTION: self._generate_section,
        }

        generator = generators.get(module_type)
        if generator:
            return generator(path)
        return {}

    def _generate_plugin(self, path: Path) -> Dict[str, Path]:
        """Generate plugin infrastructure."""
        created = {}

        # __init__.py
        init_path = path / "__init__.py"
        if not init_path.exists():
            init_content = self._load_template("plugin/__init__.py.template", {
                "name": path.name,
                "date": datetime.now().isoformat(),
            })
            init_path.write_text(init_content)
            created["__init__.py"] = init_path

        # manifest.json
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            manifest = {
                "type": "plugin",
                "id": path.name,
                "name": path.name.replace("_", " ").title(),
                "version": "0.1.0",
                "description": f"Auto-generated plugin: {path.name}",
                "entry_point": "plugin_main.py",
                "entry_class": f"{path.name.title().replace('_', '')}Plugin",
                "enabled": True,
                "hooks": [],
                "capabilities": [],
                "dependencies": [],
            }
            manifest_path.write_text(json.dumps(manifest, indent=2))
            created["manifest.json"] = manifest_path

        return created

    def _generate_analyzer(self, path: Path) -> Dict[str, Path]:
        """Generate analyzer stub inheriting BaseAnalyzer."""
        # Only for .py files that don't exist
        created = {}

        # Create stub file with proper inheritance
        stub = '''"""
Auto-generated analyzer stub.

TODO: Implement analyze() method.
"""

from .base import BaseAnalyzer


class {class_name}(BaseAnalyzer):
    """
    {name} Analyzer.

    TODO: Add description.
    """

    name = "{name_lower}"

    def analyze(self, context=None):
        """
        Analyze and generate intents.

        TODO: Implement analysis logic.
        """
        return []
'''
        return created

    def _generate_sense(self, path: Path) -> Dict[str, Path]:
        """Generate sense stub inheriting BaseSense."""
        return {}  # Similar to analyzer

    def _generate_action(self, path: Path) -> Dict[str, Path]:
        """Generate action stub inheriting BaseAction."""
        return {}  # Similar to analyzer

    def _generate_section(self, path: Path) -> Dict[str, Path]:
        """Generate phoenix section manifest."""
        created = {}

        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            manifest = {
                "type": "phoenix_section",
                "id": path.name,
                "name": path.name.replace("_", " ").title(),
                "version": "0.1.0",
                "schema_file": "schema.json",
                "default_file": "defaults.yaml",
            }
            manifest_path.write_text(json.dumps(manifest, indent=2))
            created["manifest.json"] = manifest_path

        return created

    def _load_template(self, template_path: str, context: Dict) -> str:
        """Load and render a template."""
        full_path = self._templates_dir / template_path
        if full_path.exists():
            template = Template(full_path.read_text())
            return template.safe_substitute(context)
        return ""

    def _get_default_templates(self) -> Path:
        """Get default templates directory."""
        return Path(__file__).parent / "templates"
```

### Integration with CognitiveKernel

```python
# In cognitive_kernel.py, add to _perceive_filesystem_vibrations():

def _perceive_filesystem_vibrations(self) -> Optional["ShrutaPerception"]:
    """Perceive filesystem vibrations since last check."""
    if not self._shruta_sense:
        return None

    perception = self._shruta_sense.perceive()

    # AGENT VIRUS: Auto-generate infrastructure for new modules
    if self._infrastructure_genesis:
        for vibration in perception.vibrations:
            if vibration.event_type == "created" and vibration.is_directory:
                module_type = self._classifier.classify(
                    vibration.path,
                    is_directory=True
                )
                if module_type != ModuleType.UNKNOWN:
                    created = self._infrastructure_genesis.generate(
                        vibration.path,
                        module_type
                    )
                    if created:
                        self._log_genesis(vibration.path, created)

    return perception
```

---

## The "Virus" Behavior

### Trigger: Directory Creation

When ShrutaSense detects a new directory:

1. **Classify**: What type of module is this?
2. **Check**: Does it have required infrastructure?
3. **Generate**: Create missing files from templates
4. **Announce**: Log what was created

### Example: New Plugin Created

```bash
# Developer creates new plugin directory
mkdir vibe_core/plugins/my_new_plugin

# ShrutaSense detects vibration: directory_created
# InfrastructureClassifier: ModuleType.PLUGIN
# InfrastructureGenesis: Create missing files

# Auto-generated:
# vibe_core/plugins/my_new_plugin/__init__.py
# vibe_core/plugins/my_new_plugin/manifest.json
```

### Example: New Analyzer Created

```bash
# Developer creates new analyzer
touch vibe_core/plugins/opus_assistant/manas/analyzers/my_analyzer.py

# ShrutaSense detects vibration: file_created
# InfrastructureClassifier: ModuleType.ANALYZER
# InfrastructureGenesis:
#   - Verify file follows naming convention (*_analyzer.py)
#   - If empty, populate with BaseAnalyzer stub
```

---

## Configuration

```yaml
# phoenix.yaml
manas:
  genesis:
    enabled: true
    auto_generate: true
    templates_dir: "vibe_core/plugins/opus_assistant/manas/cortex/genesis/templates"

    # Which module types to auto-generate for
    enabled_types:
      - plugin
      - analyzer
      - sense
      - action
      - section

    # Skip these directories
    ignore_patterns:
      - "**/test*"
      - "**/__pycache__"
      - "**/node_modules"
```

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/genesis/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/genesis/classifier.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/genesis/generator.py
    required: true
tests:
  - tests/manas/cortex/test_infrastructure_genesis.py
wiring:
  - pattern: "class InfrastructureClassifier"
    in: vibe_core/plugins/opus_assistant/manas/cortex/genesis/classifier.py
  - pattern: "class InfrastructureGenerator"
    in: vibe_core/plugins/opus_assistant/manas/cortex/genesis/generator.py
  - pattern: "class ModuleType"
    in: vibe_core/plugins/opus_assistant/manas/cortex/genesis/classifier.py
config:
  - section: manas.genesis
-->

---

## Related Documents

- [GAD-000: Operator Inversion Principle](../../GAD-0XX/GAD-000.md)
- [OPUS-156: ShrutaSense - The Listening System](156-SHRUTA-SENSE.md)
- [OPUS-098: Analyzer Loader](098-ANALYZER-LOADER.md)
- [OPUS-099: Sense Loader](099-SENSE-LOADER.md)
- [OPUS-100: Action Loader](100-ACTION-LOADER.md)

---

## Summary

**GAD-000 says:** "Can an AI operate this system?"

**OPUS-158 answers:** "Yes - because every new module automatically gets GAD-000 compliant infrastructure."

The Agent Virus spreads GAD-000 compliance throughout the codebase. No manual work required.

**"Jedes Haus bekommt einen Briefkasten. Jede Straße ein Schild. So funktioniert eine Stadt."**

*Every house gets a mailbox. Every street a sign. That's how a city works.*
