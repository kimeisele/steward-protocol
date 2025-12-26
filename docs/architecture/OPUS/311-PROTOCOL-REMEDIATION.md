# OPUS-311: Protocol Remediation - PROMPT.md Compliance Audit

**Status:** ANALYSIS COMPLETE, REMEDIATION PENDING
**Depends:** OPUS-310 (Fractal CLI), OPUS-309 (CognitiveProtocol)
**Author:** Claude Opus 4.5
**Date:** 2025-12-26
**Goal:** Full PROMPT.md Compliance → Autonomy Loop

## The Problem

> "Protocol statt konkrete Klassen" - PROMPT.md

We have 35 protocols defined, but many core components are **hardcoded** in the kernel.
This breaks:
- Hot-swap capability
- Testability (can't mock)
- Plugin extensibility
- The Autonomy Loop (agents can't replace components)

## Current State Audit

### Protocol Inventory

```
vibe_core/protocols/
├── agent.py          # AgentManifest, VibeAgent
├── auditor.py        # AuditorProtocol ✅
├── capability.py     # Capability
├── cartridge.py      # CartridgeProtocol ✅
├── circuit.py        # CircuitServiceProtocol
├── cli.py            # CLIHandler
├── cognition.py      # OperatorCognitiveProtocol ✅
├── command.py        # CommandProtocol ✅
├── economy.py        # BankProtocol, VaultProtocol
├── external.py       # TwitterProtocol, RedditProtocol
├── intent.py         # IntentMatcherProtocol ✅
├── ledger.py         # (empty?)
├── llm.py            # LLMProtocol
├── manifestation.py  # ManifestationProtocol ✅
├── network.py        # NetworkGatewayProtocol
├── operator_protocol.py # OperatorSocket
├── opus.py           # OpusAssistantProtocol
├── plugin.py         # PluginServiceProtocol
├── process.py        # ProcessSupervisorProtocol
├── registry.py       # ManifestIndexProtocol
├── resource.py       # ResourceSupervisorProtocol
├── scheduler.py      # (check if exists)
├── section.py        # SectionServiceProtocol
├── shuddhi.py        # ShuddhiProtocol
├── state.py          # StateServiceProtocol, PrakritiProtocol
├── task.py           # TaskProtocol
├── testable.py       # Testable
└── vedic.py          # VedicGovernanceProtocol ✅
```

**Count:** 35 Protocol definitions

---

## Gap Analysis

### 🔴 CRITICAL: Hardcoded in Kernel (No Protocol)

These are directly imported in `kernel_impl.py` without protocol abstraction:

| Component | File | Issue | Priority |
|-----------|------|-------|----------|
| **EventBus** | event_bus.py | `get_event_bus()` singleton, no protocol | P0 |
| **KernelIOService** | io_service.py | Direct instantiation | P0 |
| **PluginLoader** | plugin_loader.py | Direct instantiation | P1 |
| **CapabilityRegistry** | capability_registry.py | Direct import | P1 |
| **InMemoryScheduler** | scheduling.py | Hardcoded impl (SchedulerProtocol exists!) | P1 |
| **InMemoryLedger** | ledger.py | Direct choice of impl | P2 |
| **InMemoryManifestRegistry** | manifest_registry.py | Direct choice of impl | P2 |

### 🟠 HIGH: Missing Protocols

These components exist but have NO protocol definition:

| Component | Location | Needed Protocol | Priority |
|-----------|----------|-----------------|----------|
| **QuantumReactor** | reactor/quantum.py | ReactorProtocol | P0 |
| **EventBus** | event_bus.py | EventBusProtocol | P0 |
| **KernelIOService** | io_service.py | IOServiceProtocol | P1 |
| **PluginLoader** | plugin_loader.py | PluginLoaderProtocol | P1 |
| **GenesisService** | cli/genesis_cli.py | GenesisProtocol | P2 |
| **OpusContextService** | opus_assistant/ | ContextServiceProtocol | P2 |

### 🟡 MEDIUM: Protocol Exists but Not Injected

These have protocols but kernel uses concrete class:

| Component | Protocol | Current Usage | Fix |
|-----------|----------|---------------|-----|
| **Scheduler** | SchedulerProtocol (?) | `InMemoryScheduler()` | Use ServiceRegistry |
| **Ledger** | LedgerProtocol (?) | `SQLiteLedger()` | Use ServiceRegistry |
| **ManifestRegistry** | ManifestIndexProtocol | `InMemoryManifestRegistry()` | Use ServiceRegistry |

### 🟢 GOOD: Proper Protocol + Fallback (Arjuna Pattern)

These follow PROMPT.md correctly:

| Component | Protocol | Fallback | Status |
|-----------|----------|----------|--------|
| Auditor | AuditorProtocol | NullAuditor | ✅ |
| Cognitive | OperatorCognitiveProtocol | NullCognitive | ✅ |
| IntentMatcher | IntentMatcherProtocol | NullIntentMatcher | ✅ |
| Governance | VedicGovernanceProtocol | - | ✅ |
| Manifestation | ManifestationProtocol | - | ✅ |
| Command | CommandProtocol | BaseCommand | ✅ |
| Cartridge | CartridgeProtocol | - | ✅ |

---

## Missing Concepts (No Implementation)

These are referenced in docs/comments but don't exist:

| Concept | References | Purpose |
|---------|------------|---------|
| **SynapseProtocol** | (docs only) | Inter-agent messaging |
| **ResonanceProtocol** | reactor, vajra | Drift/alignment detection |
| **MemoryProtocol** | (needed for autonomy) | Agent persistent memory |
| **ReflectionProtocol** | (needed for autonomy) | Self-improvement loop |

---

## Remediation Plan

### Phase 1: Core Kernel Protocols (P0)

**Goal:** Kernel imports ONLY protocols, never concrete classes.

#### 1.1 EventBusProtocol

```python
# vibe_core/protocols/event.py

@runtime_checkable
class EventBusProtocol(Protocol):
    """Event pub/sub for inter-component messaging."""

    def publish(self, event: Event) -> None: ...
    def subscribe(self, event_type: EventType, handler: Callable) -> None: ...
    def unsubscribe(self, event_type: EventType, handler: Callable) -> None: ...


class NullEventBus:
    """Arjuna fallback - events are silently dropped."""
    def publish(self, event: Event) -> None: pass
    def subscribe(self, event_type: EventType, handler: Callable) -> None: pass
    def unsubscribe(self, event_type: EventType, handler: Callable) -> None: pass
```

#### 1.2 ReactorProtocol

```python
# vibe_core/protocols/reactor.py

@runtime_checkable
class ReactorProtocol(Protocol):
    """Quantum resonance engine for drift detection."""

    def compute_resonance(self, state: Dict[str, Any]) -> float: ...
    def detect_drift(self, current: Any, expected: Any) -> float: ...
    def get_inertia(self) -> float: ...
    def adjust_inertia(self, delta: float) -> None: ...


class NullReactor:
    """Arjuna fallback - no resonance computation."""
    def compute_resonance(self, state: Dict[str, Any]) -> float: return 1.0
    def detect_drift(self, current: Any, expected: Any) -> float: return 0.0
    def get_inertia(self) -> float: return 0.5
    def adjust_inertia(self, delta: float) -> None: pass
```

#### 1.3 IOServiceProtocol

```python
# vibe_core/protocols/io.py

@runtime_checkable
class IOServiceProtocol(Protocol):
    """Centralized file I/O with VFS support."""

    def read(self, path: Path) -> str: ...
    def write(self, path: Path, content: str) -> None: ...
    def exists(self, path: Path) -> bool: ...
    def resolve(self, path: Path) -> Path: ...


class NullIOService:
    """Arjuna fallback - all I/O fails gracefully."""
    def read(self, path: Path) -> str: return ""
    def write(self, path: Path, content: str) -> None: pass
    def exists(self, path: Path) -> bool: return False
    def resolve(self, path: Path) -> Path: return path
```

### Phase 2: ServiceRegistry Integration (P1)

**Goal:** All components obtained via DI, not direct import.

```python
# kernel_impl.py - BEFORE
from .event_bus import get_event_bus
from .io_service import KernelIOService

self._event_bus = get_event_bus()
self._io = KernelIOService(self)

# kernel_impl.py - AFTER
from .protocols.event import EventBusProtocol, NullEventBus
from .protocols.io import IOServiceProtocol, NullIOService
from .di import ServiceRegistry

self._event_bus = ServiceRegistry.get(EventBusProtocol) or NullEventBus()
self._io = ServiceRegistry.get(IOServiceProtocol) or NullIOService()
```

### Phase 3: Autonomy Loop Protocols (P2)

**Goal:** Enable self-improving agents.

#### 3.1 MemoryProtocol

```python
@runtime_checkable
class MemoryProtocol(Protocol):
    """Agent persistent memory for learning."""

    def remember(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    def recall(self, key: str) -> Optional[Any]: ...
    def forget(self, key: str) -> None: ...
    def search(self, query: str) -> List[Any]: ...
```

#### 3.2 ReflectionProtocol

```python
@runtime_checkable
class ReflectionProtocol(Protocol):
    """Self-improvement through execution analysis."""

    def analyze_execution(self, result: ExecutionResult) -> Insights: ...
    def propose_improvement(self, insights: Insights) -> Proposal: ...
    def apply_improvement(self, proposal: Proposal) -> bool: ...
```

#### 3.3 SynapseProtocol

```python
@runtime_checkable
class SynapseProtocol(Protocol):
    """Inter-agent neural messaging."""

    def connect(self, agent_id: str) -> bool: ...
    def send(self, agent_id: str, message: SynapseMessage) -> None: ...
    def receive(self) -> Optional[SynapseMessage]: ...
    def broadcast(self, message: SynapseMessage) -> None: ...
```

---

## The Autonomy Loop Architecture

```
                    ┌─────────────────────┐
                    │   MANAS (Cognitive) │
                    │   IntentMatcher     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
     ┌────────────────┐ ┌────────────┐ ┌────────────────┐
     │ ReactorProtocol│ │EventBusProto│ │MemoryProtocol │
     │ (resonance)    │ │ (messaging) │ │ (learning)    │
     └────────────────┘ └────────────┘ └────────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ ReflectionProtocol  │
                    │ (self-improvement)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   CommandRegistry   │
                    │   (execution)       │
                    └─────────────────────┘
```

**The Loop:**
1. MANAS receives intent
2. Matches to command via IntentMatcher
3. Executes via CommandRegistry
4. Reactor detects resonance/drift
5. Memory stores result
6. Reflection analyzes patterns
7. Proposes improvements (new commands, better matching)
8. Loop back to step 1

---

## Implementation Priority

### Sprint 1: Foundation (P0)
- [ ] Create EventBusProtocol + NullEventBus
- [ ] Create ReactorProtocol + NullReactor
- [ ] Create IOServiceProtocol + NullIOService
- [ ] Update kernel_impl.py to use protocols

### Sprint 2: Integration (P1)
- [ ] Wire all P0 protocols through ServiceRegistry
- [ ] Create PluginLoaderProtocol
- [ ] Create SchedulerProtocol (or use existing)
- [ ] Update all direct imports in kernel

### Sprint 3: Autonomy (P2)
- [ ] Create MemoryProtocol + InMemoryImpl
- [ ] Create ReflectionProtocol + BasicImpl
- [ ] Create SynapseProtocol + LocalImpl
- [ ] Wire into MANASCognitive

### Sprint 4: Loop Closure
- [ ] Connect Reflection → CommandRegistry (auto-register new commands)
- [ ] Connect Memory → IntentMatcher (learning from usage)
- [ ] Connect Reactor → Reflection (drift triggers improvement)
- [ ] The Ouroboros is complete

---

## Success Criteria

1. **Zero direct imports in kernel_impl.py** - All via protocols
2. **Every protocol has Null fallback** - Arjuna pattern everywhere
3. **Hot-swap any component** - Replace without restart
4. **Agents can propose new protocols** - Self-extension
5. **Autonomy Loop functional** - Agent improves itself

---

## Critical 5% (Senior Insights)

These are the issues that separate "working code" from "living architecture".

### 1. The Amnesia Trap (Context Continuity)

**Problem:** `steward chat "list agents"` works. But `steward chat "delete the second one"` fails.

```python
# Current: Per-request context (amnesia)
result = await kernel.process_operator_input("list agents")  # Works
result = await kernel.process_operator_input("delete the second one")  # WHAT second one?
```

**Root Cause:** `CognitiveContext` is per-request. No episodic memory.

**Solution:** ContextServiceProtocol with session persistence.

```python
@runtime_checkable
class ContextServiceProtocol(Protocol):
    """Episodic memory for conversation continuity."""

    def remember_result(self, session_id: str, key: str, result: Any) -> None: ...
    def recall_result(self, session_id: str, key: str) -> Optional[Any]: ...
    def get_last_entities(self, session_id: str) -> List[Entity]: ...  # "the second one"
```

**Priority:** P1 (required for natural conversation)

---

### 2. The Lazy Loading House of Cards

**Problem:** Errors hidden until runtime.

```python
# Boot time: Everything looks fine
steward boot  # ✅ Success

# 3 hours later: User triggers lazy load
steward chat "run audit"  # 💥 ImportError: archivist.audit failed
```

**Root Cause:** `if self._tool is None: load()` pattern masks broken plugins.

**Solution:** Boot-time integrity check.

```python
class IntegrityCheckProtocol(Protocol):
    """Dry-run all lazy loaders at boot."""

    def check_all_loadable(self) -> List[IntegrityIssue]: ...
    def warm_cache(self) -> None: ...  # Touch all lazy loaders

# In boot sequence:
issues = integrity_checker.check_all_loadable()
if issues:
    logger.warning(f"🔥 {len(issues)} components failed integrity check")
    for issue in issues:
        logger.warning(f"   - {issue.component}: {issue.error}")
```

**Priority:** P0 (Dharma: reliability)

---

### 3. The One-Way Feedback Loop

**Problem:** No learning from failures.

```
Current:  Input → Intent → Command → Output → (void)
Needed:   Input → Intent → Command → Output → Sensor → Reflection → Memory → Improvement
```

**Root Cause:** When command fails (exit code 1), MANAS sees the error string but doesn't **feel** it.

```python
# Current: Error is just text
cmd_result = await registry.execute(...)
if not cmd_result.success:
    print(f"❌ {cmd_result.error}")  # User sees it
    # MANAS learns... nothing
```

**Solution:** ReactorProtocol + MemoryProtocol feedback loop.

```python
@runtime_checkable
class FeedbackProtocol(Protocol):
    """Pain/pleasure signals for learning."""

    def signal_success(self, command: str, context: Dict) -> None: ...
    def signal_failure(self, command: str, error: str, context: Dict) -> None: ...
    def get_failure_patterns(self) -> List[FailurePattern]: ...

# In execution:
if cmd_result.success:
    feedback.signal_success(cmd_name, context)
else:
    feedback.signal_failure(cmd_name, cmd_result.error, context)
    # Next time: IntentMatcher can avoid this pattern
```

**Priority:** P2 (required for Autonomy Loop)

---

### 4. The Kernel God-Object

**Problem:** `kernel_impl.py` holds too much.

```python
# Current: Kernel is a container
class RealVibeKernel:
    self.plugins = ...
    self.io = ...
    self.scheduler = ...
    self.ledger = ...
    self.event_bus = ...
```

**Root Cause:** Kernel "knows" about implementations, not just protocols.

**Solution:** Pure DI - Kernel should be almost empty.

```python
# Target: Kernel is pure protocol orchestration
class RealVibeKernel:
    def __init__(self, container: DIContainer):
        # Kernel knows NOTHING except how to wire protocols
        self._container = container

    @property
    def scheduler(self) -> SchedulerProtocol:
        return self._container.get(SchedulerProtocol)

    @property
    def io(self) -> IOServiceProtocol:
        return self._container.get(IOServiceProtocol)
```

**Priority:** P1 (architectural debt)

---

### 5. The Identity Crisis (Who Am I?)

**Problem:** Anonymous mode is dangerous.

```
⚠️ [Steward] Identity file herald/STEWARD.md not found. Running in anonymous mode.
```

**Root Cause:** Commands execute without permission check.

```python
# Current: Execute anything
result = await registry.execute("delete_everything", [], context)  # No auth check!
```

**Solution:** GovernanceGate before every execution.

```python
@runtime_checkable
class GovernanceGateProtocol(Protocol):
    """Permission check before execution."""

    def can_execute(self,
                    identity: Identity,
                    command: str,
                    context: ExecutionContext) -> PermissionResult: ...

# In CommandRegistry.execute():
permission = governance_gate.can_execute(identity, cmd_name, context)
if not permission.allowed:
    return CommandResult(
        success=False,
        error=f"Permission denied: {permission.reason}"
    )
```

**Priority:** P0 (security - Agent Virus requires this)

---

### 6. The Sync/Async Death Trap

**Problem:** Mixing `async def` (Cognitive) with blocking calls (Legacy Tools).

```python
# Current: Some tools block
async def execute(self, args, context):
    result = some_legacy_tool.run()  # BLOCKS! Freezes entire event loop
    return CommandResult(...)
```

**Root Cause:** Not all tools are async-safe.

**Solution:** Force everything through executor.

```python
@runtime_checkable
class AsyncSafeProtocol(Protocol):
    """Ensure all execution is non-blocking."""

    async def run_sync(self, func: Callable, *args) -> Any:
        """Run blocking function in thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

# In CommandProtocol enforcement:
if not asyncio.iscoroutinefunction(cmd.execute):
    raise ProtocolViolation("Commands MUST be async")
```

**Priority:** P1 (stability)

---

### 7. The Stringly-Typed Catastrophe

**Problem:** `args: List[str]` with no schema validation.

```python
# "delete agent 5" vs "delete agent --id 5" vs "delete agent id=5"
# All different, all passed as List[str], validation happens... never?
```

**Root Cause:** No input schema enforcement.

**Solution:** Pydantic schemas per command.

```python
from pydantic import BaseModel

class DeleteAgentParams(BaseModel):
    agent_id: str
    force: bool = False

@runtime_checkable
class TypedCommandProtocol(Protocol):
    """Commands with validated input schemas."""

    @property
    def input_schema(self) -> Type[BaseModel]: ...

    async def execute(self, params: BaseModel, context: CommandContext) -> CommandResult: ...

# IntentMatcher validates BEFORE execution:
try:
    validated = cmd.input_schema(**extracted_params)
except ValidationError as e:
    return CommandResult(success=False, error=f"Invalid parameters: {e}")
```

**Priority:** P1 (reliability)

---

### 8. The Observer Effect (Log Explosion)

**Problem:** MANAS reads its own logs → infinite loop.

```python
# Reflection reads logs
logs = get_recent_logs()
insight = analyze(logs)  # This gets logged
logs = get_recent_logs()  # Now includes the analysis
insight = analyze(logs)  # "I see that I see that I see..."
```

**Root Cause:** No separation between operational logs and agent memory.

**Solution:** Separate log streams.

```python
class LogStreamProtocol(Protocol):
    """Separated log streams."""

    def operational_log(self, msg: str) -> None:
        """For humans/debugging - MANAS cannot read."""
        ...

    def episodic_log(self, event: EpisodicEvent) -> None:
        """For agent memory - structured, queryable."""
        ...

    def get_episodic_events(self, since: datetime) -> List[EpisodicEvent]:
        """Agent can query its own history (not raw logs)."""
        ...
```

**Priority:** P2 (autonomy loop)

---

## Acceptance Criteria (Hardened System)

### Boot-Time Guarantees
- [ ] All lazy loaders validated at boot (IntegrityCheckProtocol)
- [ ] All protocols have registered implementations or Null fallbacks
- [ ] Identity established before any command execution

### Runtime Guarantees
- [ ] Every command execution has permission check (GovernanceGate)
- [ ] Every failure feeds back to learning system (FeedbackProtocol)
- [ ] Session context persists across requests (ContextServiceProtocol)

### Architectural Guarantees
- [ ] Kernel imports ZERO concrete implementations
- [ ] All wiring via ServiceRegistry/DI
- [ ] Any component hot-swappable without restart

---

## The Mantra

```
PROTOCOL (Interface) + SERVICE (Implementation) + DI (Wiring) = SHAKTI (Power)

Concrete classes are prisons.
Protocols are freedom.
The Autonomy Loop is enlightenment.
```

---

## Related OPUSes

- OPUS-309: CognitiveProtocol (done)
- OPUS-310: CommandProtocol + IntentMatcher (done)
- OPUS-311: Protocol Remediation (this document)
- OPUS-312: (future) Autonomy Loop Implementation
