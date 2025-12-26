# OPUS-309: Fractal CLI + Cognitive Hook Architecture

**Status**: DESIGN
**Date**: 2025-12-26
**Author**: Opus 4.5 (Head Opus)
**Prereqs**: GAD-000, PROMPT.md, OPUS-307, OPUS-308

---

## 1. EXECUTIVE SUMMARY

Zwei architektonische Probleme wurden identifiziert:

1. **CLI ist fragmentiert** - 5 parallele Registrierungssysteme
2. **Cognition ist falsch verdrahtet** - MANAS (Plugin) direkt im Code statt via Protocol

Beide verletzen PROMPT.md: "Protocol statt konkrete Klassen"

---

## 2. PROBLEM A: CLI FRAGMENTIERUNG

### Ist-Zustand

```
UnifiedCLI enthält:
├── _legacy_map      → 13 hardcoded commands
├── _prakriti_cmds   → 8 hardcoded commands
├── _conductor_cmds  → 1 hardcoded command
├── CLIRegistry      → @register_cli decorator (16 modules)
├── CLILoader        → manifest.json discovery (25+ commands)
└── CartridgeBridge  → 29 cartridges, 64 tools

= 5 Systeme, keine Einheit
```

### Soll-Zustand

```
Ein System. On Boot = All Set Up.

ManifestRegistry.scan_all()
    ↓ Findet ALLE manifests (plugins, cartridges, containers, hollows)
    ↓
CLIService.build_from_manifests()
    ↓ Baut unified registry
    ↓
ServiceRegistry.register(CLIProtocol, cli_service)
    ↓
UnifiedCLI = Pure Router
    cli = ServiceRegistry.require(CLIProtocol)
    return cli.dispatch(args)
```

### GAD-000 Compliance

```bash
steward --discover --json
# Returns ALL commands from ALL sources
# No exceptions. No hidden registrations.
```

---

## 3. PROBLEM B: COGNITIVE HOOK FEHLT

### Ist-Zustand (FALSCH)

```python
# In unified_cli.py - HARDCODED!
from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

def cmd_chat(self, args):
    handler = JnanaHandler(workspace=Path.cwd())  # Plugin direkt instantiiert!
    ...
```

MANAS ist ein Plugin. Der Kernel/CLI darf es NICHT direkt importieren.

### Soll-Zustand (RICHTIG)

```python
# In protocols/cognition.py
@runtime_checkable
class CognitiveProtocol(Protocol):
    """
    Hook for cognitive plugins.

    PROMPT.md: "Protocol statt konkrete Klassen"
    PROMPT.md: "Hot-Swap-Fähigkeit – Module austauschbar ohne Neustart"
    """

    async def process_intent(self, intent: str, context: Dict) -> CognitiveResult:
        """Process natural language intent → structured action."""
        ...

    async def generate_response(self, context: Dict) -> str:
        """Generate intelligent response."""
        ...

    def get_capabilities(self) -> List[str]:
        """GAD-000: Discoverability."""
        ...


@dataclass
class CognitiveResult:
    """Result from cognitive processing."""
    intent_type: str  # "chat" | "execute" | "query"
    confidence: float

    # For execution intents
    syscall_request: Optional[SyscallRequest] = None

    # For chat intents
    response: Optional[str] = None

    # For routing
    target: Optional[str] = None  # "envoy" | "herald" | specific agent
```

```python
# In kernel_impl.py
class RealVibeKernel:
    def __init__(self):
        ...
        self._cognitive: Optional[CognitiveProtocol] = None

    def register_cognitive(self, cognitive: CognitiveProtocol) -> None:
        """
        Register cognitive plugin.

        PROMPT.md: Hot-Swap-Fähigkeit
        Can be called multiple times to swap implementations.
        """
        self._cognitive = cognitive
        logger.info(f"Cognitive hook registered: {type(cognitive).__name__}")

    async def process_operator_input(self, input: str) -> Any:
        """
        Main entry point for operator (human/AI) input.

        Routes through cognitive plugin if registered,
        otherwise falls back to direct routing.
        """
        if self._cognitive:
            result = await self._cognitive.process_intent(input, self.get_context())

            if result.intent_type == "execute" and result.syscall_request:
                return self.execute_syscall(result.syscall_request)
            elif result.intent_type == "chat":
                return result.response
            elif result.target:
                return self.dispatch_to(result.target, input)

        # Fallback: Direct Envoy routing
        return self.envoy.route(input)
```

```python
# In plugins/opus_assistant/plugin_main.py
class OpusAssistantPlugin:
    def on_kernel_ready(self, kernel):
        """Called when kernel is ready."""
        # Register MANAS as cognitive hook
        cognitive = MANASCognitive(workspace=kernel.workspace)
        kernel.register_cognitive(cognitive)


class MANASCognitive:
    """
    Implements CognitiveProtocol.

    Bridges:
    - JnanaHandler (intelligent responses)
    - BlueprintGenerator (intent → syscall)
    - IntentRouter (action routing)
    """

    async def process_intent(self, intent: str, context: Dict) -> CognitiveResult:
        # 1. VEDA Pipeline: SHABDA → ARTHA → PRATYAYA
        veda_result = await self.veda_pipeline.process(intent)

        # 2. If execution intent, generate blueprint
        if veda_result.intent_type == "execute":
            blueprint = await self.blueprint_generator.generate(intent)
            return CognitiveResult(
                intent_type="execute",
                confidence=blueprint.confidence,
                syscall_request=blueprint.syscall_request
            )

        # 3. If chat intent, generate response
        response = await self.jnana_handler.handle(intent, context)
        return CognitiveResult(
            intent_type="chat",
            confidence=1.0,
            response=response
        )
```

---

## 4. FRACTAL CLI ROUTING

### The Inception Model

```
steward chat "create a monitoring agent"
    ↓
UnifiedCLI.dispatch(["chat", "create a monitoring agent"])
    ↓
CLIService.route("chat", args)
    ↓
kernel.process_operator_input("create a monitoring agent")
    ↓
CognitiveProtocol.process_intent(...)  # MANAS
    ↓
BlueprintGenerator: SPAWN_COGNITION syscall
    ↓
kernel.execute_syscall()
    ↓
New Agent spawned → Has its own CLI!
    ↓
steward agent:monitoring:status  # Holon CLI!
```

### Holon CLI = Recursive

Jedes Holon kann CLI deklarieren in manifest.json:

```json
{
  "id": "monitoring-agent",
  "cli": {
    "namespace": "monitoring",
    "commands": [
      {"name": "status", "handler": "cmd_status"},
      {"name": "alerts", "handler": "cmd_alerts"}
    ]
  }
}
```

Auf Boot werden ALLE Holons gescannt (rekursiv, inkl. Hollows).
Alle CLI Commands landen in einer unified Registry.
Addressing: `steward {namespace}:{command}`

---

## 5. IMPLEMENTATION PHASES

### Phase 1: CognitiveProtocol (Foundation)

**Files:**
- `vibe_core/protocols/cognition.py` - NEW
- `vibe_core/kernel_impl.py` - Add hook

**Tasks:**
1. Create CognitiveProtocol with process_intent(), generate_response()
2. Add register_cognitive() to kernel
3. Add process_operator_input() entry point

### Phase 2: MANAS Migration

**Files:**
- `vibe_core/plugins/opus_assistant/cognitive.py` - NEW
- `vibe_core/plugins/opus_assistant/plugin_main.py` - Register hook

**Tasks:**
1. Create MANASCognitive implementing CognitiveProtocol
2. Bridge JnanaHandler + BlueprintGenerator
3. Register on kernel_ready

### Phase 3: CLI Unification

**Files:**
- `vibe_core/cli/service.py` - NEW (replaces loader.py expansion)
- `vibe_core/cli/unified_cli.py` - Simplify to pure router

**Tasks:**
1. CLIService that builds from ManifestRegistry
2. Recursive holon scanning (incl. hollows)
3. UnifiedCLI becomes 10 lines

### Phase 4: cmd_chat Migration

**Files:**
- `vibe_core/cli/unified_cli.py` - Remove hardcoded JnanaHandler

**Tasks:**
1. cmd_chat routes to kernel.process_operator_input()
2. No direct plugin imports
3. CognitiveProtocol handles everything

---

## 6. SUCCESS CRITERIA

### GAD-000 Turing Test

- [ ] `steward --discover --json` returns ALL commands
- [ ] `steward chat "list all tools"` returns structured tool list
- [ ] `steward chat "run the health check"` executes tool
- [ ] Hot-swap: Different cognitive plugin works without code change

### PROMPT.md Compliance

- [ ] No `Any` types in new code
- [ ] All protocols are @runtime_checkable
- [ ] No plugin imports in kernel/cli
- [ ] Phoenix guarantee: Cognitive can crash without killing kernel

### Dharma Gates

- [ ] Kernel doesn't know MANAS exists
- [ ] CLI doesn't know MANAS exists
- [ ] Only Protocol flows through system

---

## 7. RISKS

1. **BlueprintGenerator + JnanaHandler integration complexity**
   - Mitigation: Clear CognitiveResult type separates concerns

2. **Recursive holon scanning performance**
   - Mitigation: Lazy loading + TTL cache (already in CLILoader)

3. **Namespace collisions with deep hollows**
   - Mitigation: Qualified names with warning on ambiguity

---

## 8. RELATED DOCUMENTS

- **GAD-000**: Operator Inversion Principle
- **PROMPT.md**: Dharma + Yantra
- **OPUS-307**: CLI Consolidation (predecessor)
- **OPUS-308**: Markdown Manifestation Protocol
- **OPUS-015**: Container Format (hollows)

---

*"Der einzige Weg nach draußen ist der Kernel-Bus (Nachrichten), nicht das Filesystem."*
*— PROMPT.md*
