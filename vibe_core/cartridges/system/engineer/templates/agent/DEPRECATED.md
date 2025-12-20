# DEPRECATED - OPUS-163

> **Status**: DEPRECATED
> **Superseded By**: `vibe_core.genesis.TemplateRegistry`
> **Since**: OPUS-159/160

---

## Why Deprecated?

These templates were the original scaffolding mechanism for new agents.
As of OPUS-159, all scaffolding is centralized in the `vibe_core.genesis` module.

## What To Use Instead

For **programmatic scaffolding** (from code):

```python
from vibe_core.genesis import GenesisService, ModuleType

genesis = GenesisService.get_instance()
result = genesis.scaffold_new(
    path=target_directory,
    module_type=ModuleType.CARTRIDGE,
    context={
        "id": "my_agent",
        "name": "My Agent",
        "domain": "research",
        "description": "An agent that does research",
    }
)
```

For **manual creation** (human developer):

1. Copy one of these deprecated templates
2. Replace `YOUR_*` placeholders manually
3. This is fine for one-off manual work

## Variable Mapping

If you need to understand the old format:

| Old Placeholder       | New Template Variable |
|-----------------------|-----------------------|
| `YOUR_AGENT_ID`       | `$id`                 |
| `YOUR_AGENT_NAME`     | `$name`               |
| `YOUR_AGENT_DESCRIPTION` | `$description`     |
| `YOUR_DOMAIN`         | `$domain`             |
| `YOUR_NAME`           | `$author`             |
| `YourAgentCartridge`  | `${class_name}Cartridge` |

## Files Kept

These files are kept for reference:

- `cartridge.yaml` - Agent configuration template
- `cartridge_main.py` - Main entry point template
- `steward.json` - Steward passport template
- `tools/__init__.py` - Tools directory template

---

**Do not modify these files.** They are frozen for historical reference.
All active template development happens in `vibe_core/genesis/templates.py`.
