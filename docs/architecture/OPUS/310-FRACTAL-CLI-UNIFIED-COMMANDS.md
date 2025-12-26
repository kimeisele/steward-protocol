# OPUS-310: Fractal CLI - Unified Command Protocol

**Status:** PHASE 1-3 COMPLETE, PHASE 4 IN PROGRESS
**Depends:** OPUS-309 (CognitiveProtocol)
**Author:** Claude Opus 4.5
**Date:** 2025-12-26
**Updated:** 2025-12-26

## Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | CommandProtocol + Registry | ✅ COMPLETE |
| 2 | Manifest Integration | ✅ COMPLETE |
| 3 | Unified Discovery (5 systems) | ✅ COMPLETE |
| 4 | MANAS Intent-to-Command | 🔄 IN PROGRESS |
| 5 | Holon Commands | ⏳ PENDING |

**Current Stats:** 159 commands from 5 execution systems

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

---

## Phase 4: Intent-to-Command (MANAS Awareness)

### The Problem

Currently `steward chat` returns generic responses even when a command exists:

```
User: "show me all agents"
MANAS: "I am an assistant that can help with..." (generic chat)

# But we HAVE the command:
agents.list → "List all registered agents"
```

### The Solution: IntentMatcherProtocol

PROMPT.md: "Protocol statt konkrete Klassen"

```python
# vibe_core/protocols/intent.py

@runtime_checkable
class IntentMatcherProtocol(Protocol):
    """
    GAD-000: AI operates the system on behalf of human.

    Matches natural language intent to available commands.
    No hardcoding. Everything via CommandRegistry.
    """

    def match(self, intent: str, commands: List[CommandInfo]) -> List[IntentMatch]:
        """
        Match intent to commands.

        Returns ranked list of matches with confidence scores.
        """
        ...

    def extract_params(self, intent: str, command: CommandInfo) -> Dict[str, Any]:
        """
        Extract parameters from natural language.

        E.g., "show agent status for worker-1" → {"agent_id": "worker-1"}
        """
        ...
```

### IntentMatch Result

```python
@dataclass
class IntentMatch:
    """Result of intent matching."""

    command: CommandInfo        # The matched command
    confidence: float           # 0.0 - 1.0
    extracted_params: Dict      # Parameters extracted from intent
    reasoning: str              # Why this match was chosen
```

### Matching Strategy (No LLM Required)

```python
class CommandAwareIntentMatcher:
    """
    Semantic matching using command metadata.

    No LLM calls - pure pattern matching on:
    - Command names (fuzzy match)
    - Command descriptions (keyword extraction)
    - Command tags (exact match)
    - Command parameters (slot filling)
    """

    def match(self, intent: str, commands: List[CommandInfo]) -> List[IntentMatch]:
        matches = []

        # Tokenize intent
        tokens = self._tokenize(intent)

        for cmd in commands:
            score = 0.0

            # Name matching (highest weight)
            name_score = self._fuzzy_match(tokens, cmd.name.split("."))
            score += name_score * 0.4

            # Description matching
            desc_score = self._keyword_match(tokens, cmd.description)
            score += desc_score * 0.3

            # Tag matching
            tag_score = self._tag_match(tokens, cmd.tags)
            score += tag_score * 0.3

            if score > 0.3:  # Threshold
                matches.append(IntentMatch(
                    command=cmd,
                    confidence=score,
                    extracted_params=self._extract_params(intent, cmd),
                    reasoning=self._explain_match(cmd, score),
                ))

        return sorted(matches, key=lambda m: m.confidence, reverse=True)
```

### Integration with MANASCognitive

```python
class MANASCognitive:
    """
    OPUS-309 + OPUS-310 Phase 4

    Now aware of CommandRegistry.
    """

    def __init__(self, ...):
        ...
        self._intent_matcher: IntentMatcherProtocol = None  # Injected

    async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
        # Phase 4: Try command matching FIRST
        if self._intent_matcher and self._command_registry:
            commands = self._command_registry.list_commands()
            matches = self._intent_matcher.match(intent, commands)

            if matches:
                best = matches[0]

                # High confidence → Execute
                if best.confidence >= 0.8:
                    return CognitiveResult(
                        intent_type=IntentType.EXECUTE,
                        syscall_type=best.command.name,
                        syscall_params=best.extracted_params,
                        confidence=best.confidence,
                        reasoning=best.reasoning,
                    )

                # Medium confidence → Suggest
                elif best.confidence >= 0.5:
                    suggestions = [m.command.name for m in matches[:3]]
                    return CognitiveResult(
                        intent_type=IntentType.QUERY,
                        response=f"Did you mean: {', '.join(suggestions)}?",
                        alternatives=suggestions,
                        confidence=best.confidence,
                    )

        # Fall back to JnanaHandler chat
        return await self._generate_jnana_response(intent, context)
```

### Execution Flow

```
User: "show all agents"
         │
         ▼
MANASCognitive.process_intent()
         │
         ├─→ IntentMatcher.match("show all agents", 159 commands)
         │   ├─→ "agents.list" (confidence: 0.85) ✓
         │   ├─→ "agents.status" (confidence: 0.60)
         │   └─→ "city.citizens" (confidence: 0.40)
         │
         ▼
High confidence (0.85) → EXECUTE
         │
         ▼
CognitiveResult(intent_type=EXECUTE, syscall="agents.list")
         │
         ▼
Kernel executes → CommandRegistry.execute("agents.list")
         │
         ▼
Output shown to user
```

### Success Criteria (Phase 4)

1. `steward chat "list agents"` → Executes `agents.list`
2. `steward chat "run tests"` → Executes `test.run`
3. `steward chat "what can herald do?"` → Suggests `herald.*` commands
4. No hardcoded command mappings
5. Works with all 159+ commands via CommandRegistry

### The Ouroboros Complete

With Phase 4:
- MANAS sees all commands (via CommandRegistry)
- MANAS matches intents to commands (via IntentMatcher)
- MANAS executes via unified protocol (via CognitiveResult)
- User speaks naturally, system acts precisely

```
YANTRA (Protocol) + MANTRA (Intent) + SHAKTI (Registry) = SIDDHI (Intelligent CLI)
```
