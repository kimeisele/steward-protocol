# Fractal CLI System - Implementation Guide

> **Status:** IMPLEMENTED v1.0
> **Date:** 2025-12-06

---

## Quick Start

```bash
# Show all commands
steward --help

# Built-in commands
steward observe              # List system monitors (Glass Box)
steward status               # System status

# Plugin commands (auto-discovered)
steward test-summary         # From test_orchestration plugin
steward test-guardian        # From test_orchestration plugin

# Output formats (GAD-000 compliant)
steward --json observe       # Machine-readable JSON
steward --yaml status        # YAML output
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRACTAL CLI ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   steward <command> [args]                                      │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                          │
│   │   main.py       │  Entry point                             │
│   │                 │  - Built-in: observe, status             │
│   │                 │  - Plugin: auto-discovered               │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐      ┌─────────────────┐                │
│   │   CLILoader     │ ──── │  MonitorLoader  │                │
│   │                 │      │                 │                 │
│   │  Discovers from │      │  Discovers from │                │
│   │  manifest.json  │      │  get_monitors() │                │
│   └────────┬────────┘      └─────────────────┘                │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐      ┌─────────────────┐                │
│   │   CLIExecutor   │      │   CLIRenderer   │                │
│   │                 │      │                 │                 │
│   │  OFFLINE/BOOT/  │      │  JSON/YAML/     │                │
│   │  RPC/HYBRID     │      │  Human (Rich)   │                │
│   └─────────────────┘      └─────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
vibe_core/cli/
├── __init__.py          # Package exports
├── protocol.py          # CLICommand, CLIArg, CLIResponse, ExecutionMode
├── loader.py            # CLILoader - discovers from manifest.json
├── executor.py          # CLIExecutor - handles execution modes
├── renderer.py          # CLIRenderer - JSON/YAML/human output
├── monitors.py          # SystemMonitor protocol for introspection
├── monitor_loader.py    # MonitorLoader - discovers from plugins
└── main.py              # Entry point with built-in commands

vibe_core/phoenix/sections/cli/
├── manifest.json        # Phoenix section manifest
└── section_main.py      # CLIConfig dataclass

config/cli.yaml          # CLI configuration (output format, etc.)
```

---

## Adding Commands to Your Plugin

### Step 1: Add CLI section to manifest.json

```json
{
  "type": "plugin",
  "id": "my_plugin",
  "name": "My Plugin",
  ...
  "cli": {
    "namespace": "myns",
    "commands": [
      {
        "name": "hello",
        "handler": "cmd_hello",
        "execution_mode": "offline",
        "help": "Say hello",
        "args": [
          {
            "name": "name",
            "type": "str",
            "help": "Name to greet",
            "required": false,
            "default": "World"
          }
        ]
      }
    ]
  }
}
```

### Step 2: Implement handler in plugin_main.py

```python
class MyPlugin(KernelPlugin):
    @property
    def plugin_id(self) -> str:
        return "my_plugin"

    # CLI handler - returns DATA, not print()!
    def cmd_hello(self, name: str = "World") -> dict:
        """Say hello. Returns structured data (GAD-000 compliant)."""
        return {
            "greeting": f"Hello, {name}!",
            "timestamp": datetime.now().isoformat(),
        }
```

### Step 3: Use it

```bash
steward myns-hello              # Human output
steward myns-hello --name Kim   # With argument
steward --json myns-hello       # JSON output
```

---

## Execution Modes

| Mode | Description | Use When |
|------|-------------|----------|
| `offline` | No kernel, file operations only | Config, logs, static data |
| `boot` | Spin up kernel with persistent DB | Need kernel state |
| `rpc` | Talk to running kernel | Daemon mode (FUTURE) |
| `hybrid` | Try RPC, fallback to boot | Default |

### Important: No Ghost Kernels!

Built-in commands (`observe`, `status`) use **persistent DB** by default:

```python
# CORRECT - Uses real DB
db_path = _get_default_db_path()  # data/vibe_ledger.db
kernel = RealVibeKernel(db_path)

# WRONG - Ghost kernel sees nothing!
kernel = RealVibeKernel(":memory:")  # DON'T DO THIS
```

The CLI auto-discovers the DB path in this order:
1. `data/vibe_ledger.db` (project default)
2. `.vibe/state/vibe_agency.db` (agent state)
3. `/tmp/vibe_os/kernel/lineage.db` (lineage DB)

**Note:** RPC mode requires a running Gateway daemon.

### TODO: Graceful Degradation (Future Enhancement)

Current implementation uses DB-read only. For production-grade CLI:

```
IDEAL Graceful Degradation:
1. Try RPC to Gateway (localhost:8000) → Live State
2. Fallback: DB-read → Persistent Snapshot State
3. Fallback: Clear error message

CURRENT:
1. DB-read only → Works but no live state from running daemon
```

**Required for RPC-First:**
- [ ] Implement `CLIClient` that talks to `gateway/api.py`
- [ ] Add `/v1/system/monitors` endpoint to Gateway
- [ ] `--offline` flag to force DB-only mode
- [ ] Clear distinction: Live State vs Snapshot State in output

**Priority:** Enhancement (not blocking - current implementation is functional)

```json
{
  "name": "status",
  "handler": "cmd_status",
  "execution_mode": "hybrid"
}
```

---

## Argument Types

| Type | JSON | Example |
|------|------|---------|
| `str` | `"string"` | `--name "Kim"` |
| `int` | `"int"` | `--count 5` |
| `bool` | `"bool"` | `--verbose` (flag) |
| `float` | `"float"` | `--threshold 0.8` |
| `path` | `"path"` | `--config ./config.yaml` |

---

## Adding System Monitors (Glass Box)

Plugins can expose monitors for `steward observe`:

```python
from vibe_core.cli.monitors import (
    SystemMonitor,
    MonitorType,
    MonitorSnapshot,
    MonitorValue,
)
from datetime import datetime

class MyPlugin(KernelPlugin):
    def get_monitors(self) -> list:
        """Return monitors for introspection."""
        return [QueueMonitor(self)]

class QueueMonitor(SystemMonitor):
    def __init__(self, plugin):
        self._plugin = plugin

    @property
    def monitor_id(self) -> str:
        return "my_plugin:queue"

    @property
    def monitor_type(self) -> MonitorType:
        return MonitorType.QUEUE

    @property
    def description(self) -> str:
        return "Task queue depth"

    def snapshot(self) -> MonitorSnapshot:
        return MonitorSnapshot(
            monitor_id=self.monitor_id,
            timestamp=datetime.now().isoformat(),
            values=[
                MonitorValue(name="depth", value=42, unit="tasks"),
                MonitorValue(name="status", value="healthy"),
            ],
        )
```

---

## Configuration

Edit `config/cli.yaml`:

```yaml
# CLI Configuration
enabled: true
debug: false

output:
  default_format: "human"  # human, json, yaml
  json_indent: 2
  rich_enabled: true

observe:
  enabled: true
  auto_discover: true

namespaces:
  enabled: []    # Empty = all enabled
  disabled: []   # Blacklist
```

Access in code:

```python
from vibe_core.phoenix import get_config

config = get_config()
cli_config = config.get_section("cli")
print(cli_config.output.default_format)  # "human"
```

---

## GAD-000 Compliance

**Rule:** Handlers return DATA, CLI renders.

```python
# WRONG - prints output
def cmd_status(self) -> int:
    print("Status: OK")
    return 0

# RIGHT - returns data
def cmd_status(self) -> dict:
    return {"status": "OK", "uptime": 3600}
```

CLI automatically handles:
- `steward status` → Human-readable output
- `steward --json status` → `{"status": "OK", "uptime": 3600}`
- `steward --yaml status` → YAML format

---

## Streaming Commands (Long-running)

For commands that take time:

```python
from vibe_core.cli.protocol import ProgressUpdate

def cmd_run(self, target: str = "all") -> dict:
    """Generator for progress updates."""
    yield ProgressUpdate(status="starting", message="Discovering...")

    # Do work...
    results = self._run_tests()

    yield ProgressUpdate(status="done", message="Complete", percent=100)

    # Final return
    return {"total": len(results), "passed": sum(r.passed for r in results)}
```

Mark as streaming in manifest:

```json
{
  "name": "run",
  "handler": "cmd_run",
  "streaming": true
}
```

---

## Golden Template: New Plugin with CLI

**Location:** `docs/templates/cli_plugin/`

```bash
# Copy the template to create a new plugin
cp -r docs/templates/cli_plugin vibe_core/plugins/my_plugin

# Edit manifest.json and plugin_main.py
# Then test:
steward my-hello                    # Hello, World!
steward my-hello --name Kim         # Hello, Kim!
steward --json my-hello             # {"greeting": "Hello, World!", ...}
steward my-status                   # Boots kernel, shows status
```

See `docs/templates/cli_plugin/README.md` for full instructions.

---

## Testing Your CLI Commands

```python
# tests/test_my_plugin_cli.py
from vibe_core.cli import CLILoader

def test_commands_discovered():
    """Verify CLI commands are discovered from manifest."""
    commands = CLILoader.discover_commands(force_refresh=True)

    assert "my:greet" in commands
    assert "my:count" in commands

    greet = commands["my:greet"]
    assert greet.handler == "cmd_greet"
    assert greet.namespace == "my"

def test_greet_handler():
    """Test handler returns structured data."""
    from vibe_core.plugins.my_plugin.plugin_main import MyPlugin

    plugin = MyPlugin()
    result = plugin.cmd_greet(name="Test")

    assert "greeting" in result
    assert "Test" in result["greeting"]
```

---

## Troubleshooting

### Command not showing up

1. Check `manifest.json` has valid JSON
2. Check `cli.namespace` matches expected pattern
3. Run `steward --debug --help` for discovery logs

### Handler not found

1. Check `handler` in manifest matches method name
2. Method must be on plugin class, not nested

### Kernel not available in handler

1. Check `execution_mode` is `boot` or `hybrid`, not `offline`
2. Handler receives kernel via `on_boot()` - store it in `self._kernel`

---

## Summary

| What | Where | How |
|------|-------|-----|
| Declare commands | `manifest.json` | `cli.commands[]` |
| Implement handlers | `plugin_main.py` | Methods returning data |
| Configure CLI | `config/cli.yaml` | Output format, namespaces |
| Add monitors | `get_monitors()` | For `steward observe` |
| Config dataclass | `vibe_core/phoenix/sections/cli/` | Auto-discovered |

**Key Principles:**
1. Handlers return DATA, not print()
2. Commands in manifest, logic in plugin
3. Config separate from code
4. Auto-discovery everywhere
