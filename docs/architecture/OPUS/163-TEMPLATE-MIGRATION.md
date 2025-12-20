# OPUS-163: Template Migration - Archiv Konsolidierung

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Pattern**: Deprecation & Migration
> **Depends**: OPUS-159 (Vibe Core Genesis), OPUS-160 (The Great Wiring)

---

## Preamble: Ein Archiv, nicht zwei

Nach OPUS-160 haben wir zwei Template-Quellen:

1. **TemplateRegistry** (`vibe_core/genesis/templates.py`) - Die neue Zentrale
2. **Engineer Templates** (`engineer/templates/agent/`) - Das alte System

Das ist Duplikation. OPUS-163 konsolidiert alles in die TemplateRegistry.

## The Problem

```
BEFORE:
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│  TemplateRegistry               │    │  Engineer Templates             │
│  (genesis/templates.py)         │    │  (templates/agent/)             │
│                                 │    │                                 │
│  Format: $id, ${class_name}     │    │  Format: YOUR_AGENT_ID          │
│  Style:  Python string.Template │    │  Style:  Manual string replace  │
│  Used:   OPUS-159+              │    │  Used:   Legacy (pre-OPUS-159)  │
└─────────────────────────────────┘    └─────────────────────────────────┘
```

```
AFTER:
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│  TemplateRegistry               │    │  Engineer Templates             │
│  (genesis/templates.py)         │    │  (templates/agent/)             │
│                                 │    │                                 │
│  Format: $id, ${class_name}     │    │  DEPRECATED                     │
│  Style:  Python string.Template │    │  Kept for reference only        │
│  Used:   ALL NEW SCAFFOLDING    │    │  NOT used in code paths         │
└─────────────────────────────────┘    └─────────────────────────────────┘
```

## Implementation

### 1. Deprecate Old Templates

Add deprecation notice to `templates/agent/` directory:

```markdown
# DEPRECATED - OPUS-163

These templates are deprecated as of OPUS-163.
New scaffolding uses `vibe_core.genesis.TemplateRegistry`.

These files are kept for:
- Historical reference
- Manual agent creation (copy & modify)

For programmatic scaffolding, use:
```python
from vibe_core.genesis import GenesisService, ModuleType

genesis = GenesisService.get_instance()
genesis.scaffold_new(path, ModuleType.CARTRIDGE, context={...})
```
```

### 2. Update Builder Tool

OPUS-160 already wired Engineer to use GenesisService.
Verify that the old template loading code is not reached.

### 3. Variable Mapping

| Old (Engineer)      | New (TemplateRegistry) |
|---------------------|------------------------|
| YOUR_AGENT_ID       | $id                    |
| YOUR_AGENT_NAME     | $name                  |
| YOUR_AGENT_DESCRIPTION | $description        |
| YOUR_DOMAIN         | $domain                |
| YOUR_NAME           | $author                |
| YourAgentCartridge  | ${class_name}Cartridge |

---

## HARNESS Verification

<!-- @HARNESS
files:
  - path: vibe_core/cartridges/system/engineer/templates/agent/DEPRECATED.md
    required: true
wiring:
  - pattern: "GenesisService"
    in: vibe_core/cartridges/system/engineer/tools/builder_tool.py
-->

---

## Related Documents

- [OPUS-159: Vibe Core Genesis](159-VIBE-CORE-GENESIS.md)
- [OPUS-160: The Great Wiring](160-THE-GREAT-WIRING.md)
