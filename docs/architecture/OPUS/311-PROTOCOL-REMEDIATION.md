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
