# OPUS CLI FRACTAL DESIGN

> **Status:** DRAFT v0.2 - Gemini Review Integrated
> **Author:** Opus
> **Date:** 2025-12-06
> **Reviewers:** Gemini (Senior Architect)

---

## 1. PROBLEM STATEMENT

### Current State: Hardcoded Monolith

`vibe_core/cli.py` = 1100 lines of hardcoded commands

```python
# Current pattern - EVERY command manually registered
def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(...)

    # Manual registration for EACH command
    subparsers.add_parser("status", ...)
    subparsers.add_parser("verify", ...)
    subparsers.add_parser("boot", ...)
    # ... 15+ more

    # Manual dispatch
    if args.command == "status":
        return cli.cmd_status()
    elif args.command == "verify":
        return cli.cmd_verify(args.agent_id)
    # ... 15+ more elif
```

### Problems

| Problem | Impact |
|---------|--------|
| New command = edit cli.py | Violates Open/Closed Principle |
| Commands not co-located with logic | steward_protocol logic in cli.py, not in plugin |
| No command discovery | Can't list what commands a plugin provides |
| No command namespacing | `verify` vs `test verify` vs `steward verify` |
| Hardcoded paths | `MANIFESTS_DIR = PROJECT_ROOT / "vibe_core/cartridges/system"` |
| No plugin CLI integration | Plugins can't expose commands |

---

## 2. THE VISION: Fractal CLI

**Principle:** CLI follows same pattern as everything else - auto-discoverable, plugin-based, VEDA-4.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   steward <command> [args]                                  │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────┐                                          │
│   │  CLILoader  │  ← Discovers commands from plugins       │
│   └─────────────┘                                          │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────┐          │
│   │              Plugin Commands                 │          │
│   ├─────────────────────────────────────────────┤          │
│   │ steward_protocol:                           │          │
│   │   - verify <agent_id>                       │          │
│   │   - attest <agent_id> <capability>          │          │
│   │   - trust <agent_id>                        │          │
│   ├─────────────────────────────────────────────┤          │
│   │ test_orchestration:                         │          │
│   │   - test [pattern]                          │          │
│   │   - validate                                │          │
│   ├─────────────────────────────────────────────┤          │
│   │ interface:                                  │          │
│   │   - render [view]                           │          │
│   │   - refresh                                 │          │
│   ├─────────────────────────────────────────────┤          │
│   │ kernel (core):                              │          │
│   │   - boot                                    │          │
│   │   - stop                                    │          │
│   │   - status                                  │          │
│   │   - ps                                      │          │
│   └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. DESIGN OPTIONS

### Option A: Plugin Method

Each plugin implements `get_cli_commands()`:

```python
class KernelPlugin:
    def get_cli_commands(self) -> List[CLICommand]:
        """Override to expose CLI commands."""
        return []

class StewardProtocolPlugin(KernelPlugin):
    def get_cli_commands(self):
        return [
            CLICommand(
                name="verify",
                handler=self.cmd_verify,
                args=[Arg("agent_id", str, "Agent to verify")],
                help="Verify agent passport against Parampara"
            ),
        ]
```

**Pros:**
- Commands co-located with plugin logic
- Type-safe arguments
- Plugin can access its own state

**Cons:**
- Requires kernel boot to discover commands
- Commands tightly coupled to plugin instance

### Option B: Manifest Declaration

Commands declared in plugin manifest.json:

```json
{
  "plugin_id": "steward_protocol",
  "cli_commands": [
    {
      "name": "verify",
      "handler": "cmd_verify",
      "args": [{"name": "agent_id", "type": "str", "help": "Agent to verify"}],
      "help": "Verify agent passport"
    }
  ]
}
```

**Pros:**
- Can discover commands without booting kernel
- Declarative, easy to audit
- Can validate schema

**Cons:**
- Handler string needs resolution
- Duplication if handler signature changes

### Option C: Decorator Pattern

Commands marked with decorator, discovered via inspection:

```python
class StewardProtocolPlugin(KernelPlugin):

    @cli_command("verify", help="Verify agent passport")
    @cli_arg("agent_id", type=str, help="Agent to verify")
    def cmd_verify(self, agent_id: str) -> int:
        ...
```

**Pros:**
- Clean, Pythonic
- Self-documenting
- Can introspect at import time

**Cons:**
- Magic (decorators)
- Needs import to discover

### Option D: Hybrid (RECOMMENDED)

Manifest declares commands exist, plugin provides handlers:

```yaml
# In plugin manifest.yaml
cli:
  namespace: "steward"  # Optional prefix
  commands:
    - name: verify
      handler: cmd_verify
      help: Verify agent passport
      args:
        - name: agent_id
          type: str
          required: true
```

```python
# In plugin code
class StewardProtocolPlugin(KernelPlugin):
    def cmd_verify(self, agent_id: str) -> int:
        """Handler implementation."""
        ...
```

**Pros:**
- Manifest is source of truth for CLI structure
- Code is source of truth for implementation
- Can discover commands from manifest (no kernel boot needed)
- Can validate handler exists at load time

---

## 4. NAMESPACING QUESTION

### Flat vs Namespaced

**Flat (current):**
```bash
steward verify herald
steward test --pattern "test_*.py"
steward render agents
```

**Namespaced:**
```bash
steward steward:verify herald
steward test:run --pattern "test_*.py"
steward interface:render agents
```

**Hybrid (RECOMMENDED):**
```bash
# Core commands stay flat
steward boot
steward stop
steward status

# Plugin commands can be flat OR namespaced
steward verify herald           # Common command, flat
steward test:validate           # Less common, namespaced
```

### Collision Resolution

What if two plugins define `verify`?

| Strategy | Example |
|----------|---------|
| First wins | Bad - load order dependent |
| Last wins | Bad - silent override |
| Error | `steward verify` → "Ambiguous: steward_protocol:verify or other:verify" |
| Require namespace | Only namespaced commands allowed |
| Priority | Plugin with higher priority wins |

**Recommendation:** Error on collision, require namespace to disambiguate.

---

## 5. DISCOVERY MECHANISM

### When to Discover?

| Trigger | Pros | Cons |
|---------|------|------|
| On CLI invocation | Always fresh | Slow startup |
| On install/boot | Fast CLI | Stale if plugins change |
| Cached + invalidate | Fast + fresh | Complexity |

### Discovery Flow

```
steward <command>
    │
    ├─► Check cache (data/cli_commands.json)
    │       │
    │       ├─► Cache valid? → Use cached commands
    │       │
    │       └─► Cache stale? → Rediscover
    │
    └─► No cache → Discover from plugins
            │
            ├─► Scan plugin manifests
            │
            ├─► Extract CLI declarations
            │
            ├─► Build command registry
            │
            └─► Cache for next invocation
```

### Cache Invalidation

Cache invalidated when:
- Plugin added/removed
- Plugin manifest.yaml changed
- Manual: `steward --refresh-commands`

---

## 6. IMPLEMENTATION PLAN

### Phase 1: Contract Definition

```python
# vibe_core/cli/protocol.py

@dataclass
class CLIArg:
    name: str
    type: type  # str, int, bool, Path
    help: str
    required: bool = True
    default: Any = None

@dataclass
class CLICommand:
    name: str
    handler: str  # Method name on plugin
    help: str
    args: List[CLIArg] = field(default_factory=list)
    namespace: Optional[str] = None  # Plugin namespace

class CLIProvider(Protocol):
    """Protocol for plugins that provide CLI commands."""

    def get_cli_commands(self) -> List[CLICommand]:
        """Return CLI commands this plugin exposes."""
        ...
```

### Phase 2: CLILoader

```python
# vibe_core/loaders/cli_loader.py

class CLILoader(UnifiedLoader):
    """Discovers CLI commands from plugins."""

    @classmethod
    def discover_commands(cls) -> Dict[str, CLICommand]:
        """Scan all plugin manifests for CLI commands."""
        commands = {}

        for manifest_path in Path("vibe_core/plugins").glob("*/manifest.yaml"):
            manifest = yaml.safe_load(manifest_path.read_text())

            if "cli" not in manifest:
                continue

            namespace = manifest["cli"].get("namespace")

            for cmd_def in manifest["cli"].get("commands", []):
                cmd = CLICommand(
                    name=cmd_def["name"],
                    handler=cmd_def["handler"],
                    help=cmd_def.get("help", ""),
                    args=[CLIArg(**a) for a in cmd_def.get("args", [])],
                    namespace=namespace,
                )

                full_name = f"{namespace}:{cmd.name}" if namespace else cmd.name

                if full_name in commands:
                    raise CLICollisionError(f"Command '{full_name}' already registered")

                commands[full_name] = cmd

        return commands
```

### Phase 3: CLI Entry Point (Minimal)

```python
# vibe_core/cli.py (NEW - minimal)

def main():
    # 1. Discover commands
    commands = CLILoader.discover_commands()

    # 2. Build argparse dynamically
    parser = build_parser_from_commands(commands)

    # 3. Parse args
    args = parser.parse_args()

    # 4. Find command
    cmd = commands.get(args.command)
    if not cmd:
        parser.print_help()
        return 1

    # 5. Boot kernel (lazy - only if command needs it)
    kernel = None
    if cmd.requires_kernel:
        kernel = boot_kernel()

    # 6. Get plugin instance
    plugin = get_plugin(kernel, cmd.namespace) if kernel else None

    # 7. Execute handler
    handler = getattr(plugin, cmd.handler) if plugin else globals()[cmd.handler]
    return handler(**vars(args))
```

### Phase 4: Migrate Existing Commands

| Current | New Location | Namespace |
|---------|--------------|-----------|
| status | kernel_core plugin | (flat) |
| boot | kernel_core plugin | (flat) |
| stop | kernel_core plugin | (flat) |
| ps | kernel_core plugin | (flat) |
| verify | steward_protocol plugin | steward: |
| lineage | steward_protocol plugin | steward: |
| discover | steward_protocol plugin | steward: |
| introspect | kernel_core plugin | (flat) |
| delegate | kernel_core plugin | (flat) |
| do | semantic_router plugin | (flat) |
| test | test_orchestration plugin | test: |
| install-llm | llm plugin | llm: |

---

## 7. OPEN QUESTIONS

### Q1: Kernel Boot Latency

Current CLI commands that don't need kernel:
- `steward status` - reads files directly
- `steward lineage` - reads SQLite directly
- `steward logs` - reads log files

If we boot kernel for every command → slow.

**Options:**
1. Mark commands as `requires_kernel: false`
2. Lazy kernel boot (only when handler needs it)
3. Separate "light" commands from "heavy" commands

### Q2: Backward Compatibility

Users have scripts using current CLI. Breaking changes?

**Options:**
1. Keep old commands as aliases
2. Deprecation warnings for 1 version
3. Hard break (major version bump)

### Q3: Help Text Source

Where does help text come from?
- Manifest yaml?
- Docstring on handler?
- Both (manifest overrides docstring)?

### Q4: Argument Types

How to handle complex types?
- `--config path/to/config.yaml` → Path
- `--agents a,b,c` → List[str]
- `--json '{"key": "value"}'` → Dict

### Q5: Plugin Load Order

If plugins depend on each other, does CLI discovery order matter?

---

## 8. CRITICAL ARCHITECTURE GAPS (Gemini Review)

### 8.1 The Client-Daemon Problem

**The Flaw:** Design assumes commands either run "offline" or "boot a new kernel".

**The Reality:**
- Kernel already running (Docker, background process, systemd)
- `steward ps` should talk to RUNNING kernel, not boot new one
- New kernel would crash (DB locked) or show stale data

**Solution: Execution Topology**

```python
class ExecutionMode(Enum):
    OFFLINE = "offline"   # File manipulation only (verify, config, logs)
    RPC = "rpc"           # Forward to running kernel via API
    BOOT = "boot"         # Spin up ephemeral kernel for command
    HYBRID = "hybrid"     # Try RPC, fallback to BOOT

@dataclass
class CLICommand:
    name: str
    handler: str
    help: str
    args: List[CLIArg]
    execution_mode: ExecutionMode = ExecutionMode.HYBRID
    response_model: Optional[Type] = None  # Pydantic model for output
```

**CLI Flow with Topology:**

```
steward ps
    │
    ├─► Check execution_mode
    │       │
    │       ├─► OFFLINE → Execute locally (read files)
    │       │
    │       ├─► RPC → Check if kernel running
    │       │         │
    │       │         ├─► Running → POST to gateway/api.py
    │       │         │
    │       │         └─► Not running → Error or fallback
    │       │
    │       └─► BOOT → Start ephemeral kernel, execute, shutdown
    │
    └─► Return structured response
```

**Gateway Integration:**

```python
# gateway/api.py already exists - CLI becomes a client
class CLIClient:
    def __init__(self, endpoint: str = "http://localhost:8000"):
        self.endpoint = endpoint

    def execute(self, command: str, args: Dict) -> CLIResponse:
        """Forward command to running kernel."""
        resp = requests.post(
            f"{self.endpoint}/v1/cli/{command}",
            json=args
        )
        return CLIResponse(**resp.json())

    def is_kernel_running(self) -> bool:
        """Check if kernel is accepting connections."""
        try:
            requests.get(f"{self.endpoint}/health", timeout=1)
            return True
        except:
            return False
```

### 8.2 GAD-000 Compliance: Structured Output

**The Flaw:** Handlers use `print()` - not machine readable.

**The Fix:** Strict separation of DATA and RENDERING.

```python
# WRONG - Current pattern
def cmd_status(self) -> int:
    print("=" * 70)
    print("🎛️  STEWARD PROTOCOL - SYSTEM STATUS")
    kernel_running = self._check_kernel_pulse()
    print(f"Kernel: {'✅ ONLINE' if kernel_running else '❌ OFFLINE'}")
    return 0

# RIGHT - GAD-000 Compliant
@dataclass
class StatusResponse:
    kernel_running: bool
    pulse_age_seconds: float
    chain_blocks: int
    chain_verified: bool
    certified_agents: int

def cmd_status(self) -> StatusResponse:
    """Handler returns DATA, not presentation."""
    return StatusResponse(
        kernel_running=self._check_kernel_pulse(),
        pulse_age_seconds=self._get_pulse_age(),
        chain_blocks=self._count_blocks(),
        chain_verified=self._verify_chain(),
        certified_agents=self._count_agents(),
    )
```

**CLI Rendering Layer:**

```python
# cli.py main loop
def main():
    ...
    result = execute_command(cmd, args)

    # Output format based on flag
    if args.json:
        # Machine output - for scripts/agents
        print(json.dumps(asdict(result), indent=2))
    elif args.yaml:
        print(yaml.dump(asdict(result)))
    else:
        # Human output - Rich rendering
        render_human(cmd.name, result)

def render_human(command: str, result: Any):
    """Rich rendering for humans."""
    renderer = get_renderer(command)  # Plugin can provide custom renderer
    if renderer:
        renderer.render(result)
    else:
        # Default table/pretty print
        console.print(Pretty(result))
```

**Updated CLICommand Contract:**

```python
@dataclass
class CLICommand:
    name: str
    handler: str
    help: str
    args: List[CLIArg] = field(default_factory=list)
    namespace: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.HYBRID
    response_model: Type = Dict  # Pydantic model or dataclass
    renderer: Optional[str] = None  # Custom renderer method name
```

### 8.3 Streaming/Lifecycle Feedback

**The Problem:** Agent commands take 30+ seconds. CLI freezes.

**The Solution:** Generator support for progress streaming.

```python
# Handler can be sync, async, or generator
def cmd_run_agent(self, agent_id: str) -> Generator[ProgressUpdate, None, AgentResult]:
    """Long-running command with progress updates."""
    yield ProgressUpdate(status="starting", message=f"Booting agent {agent_id}...")

    agent = self.kernel.get_agent(agent_id)
    yield ProgressUpdate(status="running", message="Agent processing task...")

    for i, step in enumerate(agent.execute()):
        yield ProgressUpdate(
            status="progress",
            message=step.message,
            percent=step.progress
        )

    return AgentResult(success=True, output=agent.result)
```

**CLI Streaming Renderer:**

```python
def execute_streaming(handler, args) -> Any:
    """Execute handler with streaming support."""
    gen = handler(**args)

    if not inspect.isgenerator(gen):
        # Simple return
        return gen

    # Stream progress updates
    final_result = None
    with Live(Spinner("dots"), console=console) as live:
        for update in gen:
            if isinstance(update, ProgressUpdate):
                live.update(f"[cyan]{update.message}[/] {update.percent or ''}%")
            else:
                final_result = update

    return final_result
```

**Progress Protocol:**

```python
@dataclass
class ProgressUpdate:
    status: Literal["starting", "running", "progress", "done", "error"]
    message: str
    percent: Optional[int] = None
    data: Optional[Dict] = None
```

---

## 8.4 Summary: The Complete Contract

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Type, Dict, Any, Generator

class ExecutionMode(Enum):
    OFFLINE = "offline"   # No kernel needed
    RPC = "rpc"           # Talk to running kernel
    BOOT = "boot"         # Start ephemeral kernel
    HYBRID = "hybrid"     # Try RPC, fallback BOOT

@dataclass
class CLIArg:
    name: str
    type: type
    help: str
    required: bool = True
    default: Any = None

@dataclass
class CLICommand:
    # Identity
    name: str
    namespace: Optional[str] = None

    # Handler
    handler: str  # Method name on plugin
    execution_mode: ExecutionMode = ExecutionMode.HYBRID

    # Documentation
    help: str = ""
    args: List[CLIArg] = field(default_factory=list)

    # GAD-000 Compliance
    response_model: Type = Dict  # What handler returns
    renderer: Optional[str] = None  # Custom human renderer

    # Streaming
    supports_streaming: bool = False  # Handler is generator?

@dataclass
class CLIResponse:
    """Standard response wrapper."""
    success: bool
    data: Any  # The actual response_model instance
    error: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.OFFLINE

@dataclass
class ProgressUpdate:
    """For streaming commands."""
    status: str
    message: str
    percent: Optional[int] = None
```

---

## 9. RISKS

| Risk | Mitigation |
|------|------------|
| Breaking existing scripts | Compatibility layer / aliases |
| Slow discovery | Caching |
| Complex debugging | Clear error messages, --verbose |
| Over-engineering | Start minimal, iterate |
| RPC complexity | Start with OFFLINE/BOOT, add RPC later |
| Streaming complexity | Optional, start with sync handlers |

---

## 10. SUCCESS CRITERIA

1. `vibe_core/cli.py` < 100 lines (entry point only)
2. New plugin = automatic CLI commands (no cli.py edit)
3. `steward --help` shows all discovered commands dynamically
4. No hardcoded command list anywhere
5. Commands co-located with plugin logic
6. `steward <cmd> --json` works for ALL commands (GAD-000)
7. RPC mode works when kernel running
8. Tests pass

---

## 11. IMPLEMENTATION PHASES

### Phase 1: Contract + CLILoader (Foundation)
- [ ] Define `CLICommand`, `CLIArg`, `ExecutionMode` in `vibe_core/cli/protocol.py`
- [ ] Implement `CLILoader` that reads from plugin manifests
- [ ] Create minimal `cli.py` that uses CLILoader

### Phase 2: Migrate One Plugin (POC)
- [ ] Add `cli:` section to `test_orchestration/manifest.yaml`
- [ ] Refactor handler to return data (not print)
- [ ] Test: `steward test:validate --json`

### Phase 3: GAD-000 Output Layer
- [ ] Implement `--json` / `--yaml` global flags
- [ ] Implement default Rich renderer
- [ ] Plugin can provide custom renderer

### Phase 4: RPC Mode
- [ ] Implement `CLIClient` for daemon communication
- [ ] Add `/v1/cli/<command>` endpoint to gateway
- [ ] Auto-detect running kernel

### Phase 5: Streaming
- [ ] Generator support in execution layer
- [ ] Progress spinner/log streaming
- [ ] Test with long-running agent command

### Phase 6: Full Migration
- [ ] Migrate all commands from old cli.py
- [ ] Deprecation warnings for old patterns
- [ ] Remove old cli.py

---

## 12. COMMAND MIGRATION MAP

| Current Command | New Plugin | Namespace | ExecutionMode |
|----------------|------------|-----------|---------------|
| status | kernel_core | (flat) | HYBRID |
| boot | kernel_core | (flat) | OFFLINE |
| stop | kernel_core | (flat) | OFFLINE |
| ps | kernel_core | (flat) | RPC |
| logs | kernel_core | (flat) | OFFLINE |
| introspect | kernel_core | (flat) | RPC |
| verify | steward_protocol | steward: | OFFLINE |
| lineage | steward_protocol | steward: | OFFLINE |
| discover | steward_protocol | steward: | HYBRID |
| delegate | kernel_core | (flat) | RPC |
| do | semantic_router | (flat) | BOOT |
| init | steward_protocol | steward: | OFFLINE |
| install-llm | llm | llm: | OFFLINE |
| test | test_orchestration | test: | BOOT |
| validate | test_orchestration | test: | OFFLINE |

---

## 13. OPEN DECISIONS

| Decision | Options | Recommendation | Status |
|----------|---------|----------------|--------|
| Option A/B/C/D | See Section 3 | **D (Hybrid)** | DECIDED |
| Namespacing | Flat vs Namespaced | **Hybrid** (core flat, plugins namespaced) | DECIDED |
| Cache location | File vs Memory | **File** (data/cli_cache.json) | DECIDED |
| RPC Protocol | HTTP vs Unix Socket | **HTTP** (gateway already exists) | DECIDED |
| Breaking changes | Hard break vs Compat | **Compat layer** for v1 | OPEN |

---

*Draft v0.2 - Gemini Review Integrated*
*Next: User review, then Phase 1 implementation*
