# CLI Plugin Golden Template

Copy this folder to create a new plugin with CLI commands.

## Quick Start

```bash
# 1. Copy to plugins directory
cp -r docs/templates/cli_plugin vibe_core/plugins/my_plugin

# 2. Edit manifest.json
#    - Change "id" to "my_plugin"
#    - Change "namespace" to "my"
#    - Update commands as needed

# 3. Edit plugin_main.py
#    - Rename MyPlugin class
#    - Implement your cmd_* handlers

# 4. Test it
steward --help              # See your commands
steward my-hello            # Run offline command
steward my-hello --name Kim # With argument
steward --json my-hello     # JSON output
steward my-status           # Run boot command
```

## File Structure

```
my_plugin/
├── __init__.py       # Package exports
├── manifest.json     # Plugin config + CLI commands
├── plugin_main.py    # Plugin class + cmd_* handlers
└── README.md         # This file (optional)
```

## Key Rules

1. **Handlers return DATA, not print()** - GAD-000 compliance
2. **Commands in manifest.json, logic in plugin_main.py**
3. **execution_mode**: `offline` (no kernel), `boot` (needs kernel), `hybrid` (tries both)
4. **Namespace**: Commands become `steward <namespace>-<command>`

## See Also

- [CLI Implementation Guide](../../architecture/CLI_IMPLEMENTATION.md)
- [Plugin Protocol](../../../vibe_core/plugin_protocol.py)
