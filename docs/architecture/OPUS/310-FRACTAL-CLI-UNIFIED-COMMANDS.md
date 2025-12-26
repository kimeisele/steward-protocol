# OPUS-310: Fractal CLI - Unified Command Protocol

**Status:** PROPOSED
**Depends:** OPUS-309 (CognitiveProtocol)
**Author:** Claude Opus 4.5
**Date:** 2025-12-26

## The Vision

> "Ein Agent der sich als Byte durch den Raum frei bewegen kann"

The CLI is not just a human interface. It is the **Universal Execution Layer**.
- Human types: `steward chat "hello"`
- Agent calls: `kernel.execute("chat", "hello")`
- Same power. Same interface. Same capabilities.

## The Problem

### Current State: 5 Parallel Command Systems

```
unified_cli.py
├── CORE_COMMANDS (hardcoded dict, ~15 commands)
├── CartridgeBridge (lazy-loaded, separate namespace)
├── PluginCLI (per-plugin, inconsistent)
├── StewardCLI (deprecated, still used)
└── Direct kernel methods (not exposed to CLI)
```

**Result:**
- MANAS cannot see all capabilities
- Agents cannot discover what's possible
- New plugins must wire commands manually
- No single source of truth

### What We Need: Unified Command Protocol

```
CommandRegistry (Manifest-based, Protocol-driven)
├── Core Commands (declared in manifest)
├── Plugin Commands (declared in manifest)
├── Cartridge Commands (declared in manifest)
├── Holon Commands (declared in manifest)
└── ALL discoverable via: steward commands
```

## The Architecture

### 1. CommandProtocol (The Interface)

```python
# vibe_core/protocols/command.py

@runtime_checkable
class CommandProtocol(Protocol):
    """Every command implements this. No exceptions."""

    @property
    def name(self) -> str:
        """Unique command name (e.g., 'chat', 'boot', 'civic.bank')"""
        ...

    @property
    def description(self) -> str:
        """Human-readable description"""
        ...

    @property
    def parameters(self) -> Dict[str, ParameterSpec]:
        """Parameter schema for validation"""
        ...

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute the command"""
        ...

    def validate(self, args: List[str]) -> List[str]:
        """Validate args, return errors"""
        ...
```

### 2. CommandRegistry (The Aggregator)

```python
# vibe_core/cli/registry.py

class CommandRegistry:
    """
    Single source of truth for ALL commands.

    Scans:
    - vibe_core/plugins/*/manifest.yaml → commands section
    - vibe_core/cartridges/*/manifest.yaml → commands section
    - ~/.vibe/containers/*/manifest.yaml → commands section (Holons!)

    Provides:
    - get_command(name) → CommandProtocol
    - list_commands() → List[CommandInfo]
    - search_commands(query) → List[CommandInfo]
    """
```

### 3. Manifest Declaration (The Contract)

```yaml
# Any manifest.yaml can declare commands
name: opus_assistant
type: plugin

commands:
  - name: chat
    protocol: OperatorCognitiveProtocol
    method: process_intent
    description: "Chat with the cognitive layer"
    parameters:
      message:
        type: string
        required: true

  - name: spawn
    protocol: AgentLifecycleProtocol
    method: spawn_agent
    description: "Spawn a new agent"
    parameters:
      agent_type:
        type: string
        required: true
      config:
        type: object
        required: false
```

### 4. The Universal Execution Flow

```
steward <command> [args...]
         │
         ▼
┌─────────────────────────┐
│   CommandRegistry       │
│   (finds command)       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   CommandProtocol       │
│   (validates args)      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Protocol Method       │
│   (actual execution)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   CommandResult         │
│   (structured output)   │
└─────────────────────────┘
```

## The Fractal Property

**Key Insight:** Every Holon is a potential CLI.

```
steward commands                    # Root level
steward civic commands              # Civic cartridge
steward civic.bank commands         # Bank sub-cartridge
~/.vibe/my-agent/steward commands   # Agent's own CLI
```

When a Holon (container) is downloaded:
1. ManifestRegistry scans its manifest
2. CommandRegistry registers its commands
3. Immediately available in CLI
4. MANAS can discover and use it

## MANAS Integration (Ouroboros)

With CommandRegistry, MANAS can:

```python
# In MANASCognitive
async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
    # Get ALL available commands
    commands = self._kernel.command_registry.list_commands()

    # Match intent to command
    matched = self._match_intent_to_command(intent, commands)

    if matched:
        return CognitiveResult(
            intent_type=IntentType.EXECUTE,
            syscall_type=matched.name,
            syscall_params=matched.extracted_params,
        )

    # No match? MANAS can now:
    # 1. Suggest creating a new command
    # 2. Route to Envoy for complex tasks
    # 3. Learn from the gap (Ouroboros)
```

## Implementation Plan

### Phase 1: CommandProtocol + Registry
- [ ] Create `vibe_core/protocols/command.py`
- [ ] Create `vibe_core/cli/command_registry.py`
- [ ] Migrate 3-5 core commands as proof of concept

### Phase 2: Manifest Integration
- [ ] Add `commands` section to manifest schema
- [ ] ManifestRegistry extracts commands during scan
- [ ] CommandRegistry consumes from ManifestRegistry

### Phase 3: Full Migration
- [ ] Migrate all core commands to Protocol
- [ ] Migrate CartridgeBridge commands
- [ ] Deprecate CORE_COMMANDS dict

### Phase 4: MANAS Awareness
- [ ] CommandRegistry exposed to CognitiveProtocol
- [ ] MANAS can query available commands
- [ ] Intent matching uses command metadata

### Phase 5: Holon Commands
- [ ] Scan `~/.vibe/containers/*/manifest.yaml`
- [ ] Dynamic command registration
- [ ] "Agent Virus" complete

## Success Criteria

1. `steward commands` shows ALL capabilities (plugins, cartridges, holons)
2. `steward run <any-command>` works uniformly
3. MANAS can discover and suggest commands
4. New plugins need ZERO code changes in unified_cli.py
5. Downloaded Holons immediately appear in CLI

## The Mantra

```
YANTRA (CommandProtocol) + MANTRA (CLI) = SIDDHI (Universal Execution)
```

Every command is a spell.
Every manifest is a grimoire.
The registry is the summoning circle.
MANAS is the wizard.

---

## Appendix: Why Not "Discovery Service"?

Gemini suggested building a "Discovery Service". But:

1. **ManifestRegistry already scans everything** (77 manifests)
2. The problem is not discovery, it's **exposition**
3. We don't need another scanner, we need a **unified interface**

The CommandRegistry doesn't replace ManifestRegistry - it **consumes** it:

```
ManifestRegistry (scanning) → CommandRegistry (exposing) → CLI (executing)
```

This is the missing link.
