# PHOENIX VIMANA UNIFIED BOOT PLAN

**Version:** 1.1
**Date:** 2025-11-29
**Status:** APPROVED - IMPLEMENTATION IN PROGRESS
**Author:** Senior Engineer Session
**Approved By:** Founder (with Gemini review)
**Precedence:** This plan connects GAD-000, Sarga, Knowledge Graph, and the Universal Operator concept.

**CRITICAL REQUIREMENT:** Strict typing with Pydantic models. No `dict[str, Any]`.

---

## EXECUTIVE SUMMARY

This document describes the **PHOENIX VIMANA UNIFIED BOOT** - a plan to connect all existing components of Steward Protocol into a cohesive, operator-agnostic system.

**Key Insight:** We are not building a chatbot. We are building an **Operating System** where the intelligence (operator) is interchangeable - like TCP/IP doesn't care if data travels over copper, fiber, or carrier pigeon.

**The Revolution:** The system runs regardless of WHO operates it (Human, Claude Code, LLM, Local Model). The protocol stays the same.

---

## TABLE OF CONTENTS

1. [The Problem](#1-the-problem)
2. [The Vision](#2-the-vision)
3. [Architecture Overview](#3-architecture-overview)
4. [Strict Typing Protocol](#4-strict-typing-protocol) **(NEW - CRITICAL)**
5. [The Universal Operator Adapter](#5-the-universal-operator-adapter)
6. [Sarga Boot Sequence](#6-sarga-boot-sequence)
7. [Component Wiring](#7-component-wiring)
8. [Implementation Phases](#8-implementation-phases)
9. [Success Criteria](#9-success-criteria)

---

## 1. THE PROBLEM

### Current State (Disconnected Components)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ boot_orchestrator│     │     sarga.py    │     │  boot_sequence  │
│   (Kernel)      │     │ (Cosmic Boot)   │     │ (Dynamic Prompt)│
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │    NOT CONNECTED      │    NOT CONNECTED      │
         │                       │                       │
         ▼                       ▼                       ▼
    [Orphaned]              [Orphaned]              [Orphaned]
```

### What Exists But Isn't Wired:

| Component | File | Status |
|-----------|------|--------|
| Sarga Boot | `vibe_core/sarga.py` | Exists, not connected to boot |
| Boot Orchestrator | `vibe_core/boot_orchestrator.py` | Boots kernel, ignores Sarga |
| Boot Sequence | `vibe_core/runtime/boot_sequence.py` | Dynamic prompts, no kernel |
| PromptContext | `vibe_core/runtime/prompt_context.py` | Resolvers exist |
| KernelOracle | `vibe_core/runtime/oracle.py` | Capabilities exposed |
| Varnas | `steward/varna.py` | Classification exists |
| Ashramas | `steward/ashrama.py` | Lifecycle exists |
| Knowledge Graph | `vibe_core/knowledge/` | 4D system exists |
| UniversalProvider | `provider/universal_provider.py` | Routing exists |

### The Gap:
- Sarga phases don't trigger real components
- Knowledge Graph isn't used in agent discovery
- Varnas/Ashramas aren't assigned at registration
- Dynamic prompts aren't connected to the booted kernel
- No unified "operator socket" for interchangeable intelligence

---

## 2. THE VISION

### TCP/IP for Agents

```
TCP/IP:
  - Protocol doesn't care about transport (copper, fiber, wireless)
  - Data packets flow regardless of physical medium
  - Standardized interface, interchangeable implementation

STEWARD PROTOCOL:
  - Protocol doesn't care about operator (Human, Claude, LLM, Local)
  - Intent flows regardless of intelligence source
  - Standardized socket, interchangeable operator
```

### The Universal Operator Principle (GAD-000 Realized)

```
TRADITIONAL:
  Human → System → Response

AI-NATIVE (GAD-000):
  [Any Operator] → Universal Socket → System → Response

  Where [Any Operator] can be:
    - Human typing in terminal
    - Claude Code executing CLI
    - LLM via API gateway
    - Local model (offline)
    - Hot-swappable at runtime
```

### The Goal

**One Boot. Any Operator. Always Works.**

---

## 3. ARCHITECTURE OVERVIEW

### The Four Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    PHOENIX VIMANA ARCHITECTURE               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 0: OPERATOR (INTERCHANGEABLE)                        │
│           ┌─────────────────────────────────────────┐       │
│           │     UNIVERSAL OPERATOR ADAPTER          │       │
│           │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐  │       │
│           │  │Human│ │Claude│ │ LLM │ │LocalLLM │  │       │
│           │  └──┬──┘ └──┬──┘ └──┬──┘ └────┬────┘  │       │
│           │     └───────┴───────┴─────────┘        │       │
│           │              │ (INTENT)                 │       │
│           └──────────────┼──────────────────────────┘       │
│                          ▼                                   │
│  LAYER 1: UNIVERSAL PROVIDER (Central Nervous System)       │
│           ├── SemanticRouter (intent understanding)         │
│           ├── ReflexEngine (instant responses)              │
│           ├── PlaybookEngine (deterministic execution)      │
│           ├── LLMEngineAdapter (intelligent fallback)       │
│           └── DegradationChain (offline-first)              │
│                          │                                   │
│                          ▼ (ROUTE)                          │
│                                                              │
│  LAYER 2: ENVOY (Universal Operator Interface)              │
│           ├── Translates Intent → Kernel Tasks              │
│           ├── HILAssistant (simplifies for humans)          │
│           └── CityControlTool (Golden Straw)                │
│                          │                                   │
│                          ▼ (TASKS)                          │
│                                                              │
│  LAYER 3: KERNEL + AGENTS                                   │
│           ├── VibeKernel (Sarga-aware scheduler)            │
│           ├── Agents (with Varnas/Ashramas)                 │
│           ├── Knowledge Graph (4D routing)                  │
│           └── Ledger + Lineage (persistence)                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. STRICT TYPING PROTOCOL

> **CRITICAL CONDITION FOR IMPLEMENTATION** (Gemini Review, Founder Approved)

### The Rule: No Loose JSON Blobs

The Universal Operator Adapter MUST use strictly typed models. No `dict[str, Any]`.
This is **TCP/IP for Agents** - the protocol must be hard-defined.

### Pydantic Models

```python
# vibe_core/protocols/operator_protocol.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum
from datetime import datetime


class IntentType(str, Enum):
    """Types of operator intents"""
    COMMAND = "command"       # Direct command execution
    QUERY = "query"           # Information retrieval
    DELEGATION = "delegation" # Delegate to agent
    CONTROL = "control"       # System control (shutdown, status, etc.)
    REFLEX = "reflex"         # Automatic response (no operator needed)


class OperatorType(str, Enum):
    """Types of operators in the system"""
    HUMAN = "human"
    CLAUDE_CODE = "claude_code"
    LLM_API = "llm_api"
    LOCAL_LLM = "local_llm"
    DEGRADED = "degraded"


class SystemContext(BaseModel):
    """
    The complete system state passed to operators.

    This is what the operator SEES before making a decision.
    Strictly typed - no loose dictionaries.
    """

    # Core Identity
    boot_id: str = Field(..., description="Unique boot session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # System State
    kernel_status: Literal["booting", "ready", "degraded", "shutdown"] = "booting"
    agents_registered: int = 0
    agents_healthy: int = 0

    # Git State (for code-aware operators)
    git_branch: Optional[str] = None
    git_uncommitted: int = 0
    git_behind: int = 0

    # Current Task State
    current_task: Optional[str] = None
    task_progress: Optional[float] = None  # 0.0 - 1.0

    # Operator Awareness
    operator_type: OperatorType = OperatorType.HUMAN
    degradation_level: int = 0  # 0 = full, higher = more degraded

    # Message History (last N for context)
    recent_messages: list[str] = Field(default_factory=list, max_length=10)

    # Capabilities (from KernelOracle)
    available_tools: list[str] = Field(default_factory=list)
    available_agents: list[str] = Field(default_factory=list)

    class Config:
        frozen = False  # Allow updates during boot


class Intent(BaseModel):
    """
    The decision from an operator.

    This is what the operator WANTS to happen.
    Strictly typed - parseable, verifiable, composable.
    """

    # Core Intent
    intent_type: IntentType
    raw_input: str = Field(..., description="Original input from operator")

    # Parsed Intent
    target_agent: Optional[str] = Field(None, description="Agent to handle this")
    target_tool: Optional[str] = Field(None, description="Tool to invoke")
    parameters: dict[str, str] = Field(default_factory=dict)  # String params only

    # Metadata
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_operator: OperatorType = OperatorType.HUMAN
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Control Flags
    requires_confirmation: bool = False
    is_destructive: bool = False
    priority: Literal["low", "normal", "high", "critical"] = "normal"

    class Config:
        frozen = True  # Intents are immutable once created


class OperatorResponse(BaseModel):
    """
    Response back to the operator after processing intent.
    """

    success: bool
    message: str
    data: Optional[dict[str, str]] = None  # Typed string values only
    next_context: Optional[SystemContext] = None
    suggested_actions: list[str] = Field(default_factory=list)
```

### Why Strict Typing Matters

```
WITHOUT STRICT TYPING:
  context = {"status": "ok", "agents": 23, ...}  # What fields exist? Unknown.
  intent = {"action": "do something", ...}        # Is this valid? Who knows.

WITH STRICT TYPING (Pydantic):
  context = SystemContext(...)  # IDE knows every field
  intent = Intent(...)          # Validation at creation time

  context.kernel_status  # ✅ Autocomplete works
  context.nonexistent    # ❌ Type error at compile time
```

### Integration Points

1. **OperatorSocket.receive_context()** → Takes `SystemContext` (not dict)
2. **OperatorSocket.provide_intent()** → Returns `Intent` (not dict)
3. **UniversalProvider routing** → Uses `Intent.intent_type` for deterministic routing
4. **KernelOracle** → Populates `SystemContext.available_tools/agents`
5. **All logging** → Uses `.model_dump()` for JSON serialization

---

## 5. THE UNIVERSAL OPERATOR ADAPTER

### The Socket Interface

The **Universal Operator Adapter** is the key abstraction. It defines a **single interface** that all operators must implement.

```python
# CONCEPTUAL INTERFACE (not actual code yet)

class OperatorSocket(Protocol):
    """
    The Universal Socket for Operator Intelligence.

    Any entity that can provide decisions implements this.
    The system doesn't know or care WHO is deciding.
    """

    async def receive_context(self, context: SystemContext) -> None:
        """
        Receive the current system state.

        For Human: Render as markdown in terminal/web
        For Claude: Inject as system prompt
        For LLM: Send as API context
        For Local: Pass as string
        """
        ...

    async def provide_intent(self) -> Intent:
        """
        Provide the next action/decision.

        For Human: Read from stdin/form
        For Claude: Parse response
        For LLM: Parse API response
        For Local: Parse output
        """
        ...

    def is_available(self) -> bool:
        """Check if this operator is currently available."""
        ...


class UniversalOperatorAdapter:
    """
    Manages multiple operator backends.
    Provides graceful degradation and hot-swap capability.
    """

    def __init__(self):
        self.operators: list[OperatorSocket] = []
        self.current_operator: OperatorSocket | None = None

    def register_operator(self, operator: OperatorSocket, priority: int) -> None:
        """Register an operator backend with priority."""
        ...

    async def get_decision(self, context: SystemContext) -> Intent:
        """
        Get a decision from the current best available operator.
        Falls back through priority chain if current fails.
        """
        ...

    def hot_swap(self, new_operator: OperatorSocket) -> None:
        """Hot-swap the current operator without system restart."""
        ...
```

### Operator Implementations

```
┌────────────────────────────────────────────────────────────┐
│                    OPERATOR IMPLEMENTATIONS                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  HumanOperator:                                           │
│    receive_context() → print(render_markdown(context))    │
│    provide_intent() → input("Your command: ")             │
│                                                            │
│  ClaudeCodeOperator:                                      │
│    receive_context() → inject_system_prompt(context)      │
│    provide_intent() → parse_claude_response()             │
│                                                            │
│  LLMOperator:                                             │
│    receive_context() → api.send_context(context)          │
│    provide_intent() → api.get_completion()                │
│                                                            │
│  LocalLLMOperator:                                        │
│    receive_context() → local_model.set_context(context)   │
│    provide_intent() → local_model.generate()              │
│                                                            │
│  DegradedOperator (Fallback):                             │
│    receive_context() → log(context)                       │
│    provide_intent() → return DEFAULT_SAFE_ACTION          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Graceful Degradation Chain

```
Priority 1: Claude/OpenAI API (if available, if API key valid)
    │
    ▼ (fails?)
Priority 2: Local LLM (if installed, if model loaded)
    │
    ▼ (fails?)
Priority 3: Human (always available if terminal)
    │
    ▼ (fails? - headless mode)
Priority 4: DegradedOperator (safe defaults, log everything)
```

**The system NEVER crashes.** It always has a fallback.

---

## 6. SARGA BOOT SEQUENCE

### The Cosmic Boot (Connected to Reality)

The Sarga boot sequence will be wired to REAL system components:

```
SARGA PHASE 1: SHABDA (Sound/Command)
├── Trigger: User/System initiates boot
├── Component: Entry point (CLI, API, or auto-boot)
├── Handler: Log boot initiation, set boot_start_time
└── Success: Boot process started

SARGA PHASE 2: AKASHA (Space/Memory)
├── Trigger: Phase 1 complete
├── Component: VibeKernel.__init__()
├── Handler:
│   ├── Allocate process space (ProcessManager)
│   ├── Initialize ResourceManager with quotas
│   └── Create in-memory scheduler
└── Success: Kernel space allocated

SARGA PHASE 3: VAYU (Air/Communication)
├── Trigger: Phase 2 complete
├── Component: Message bus + PromptContext
├── Handler:
│   ├── Initialize PromptContext with resolvers
│   ├── Register all context resolvers
│   └── Enable inter-agent communication
└── Success: Communication channels open

SARGA PHASE 4: AGNI (Fire/Form)
├── Trigger: Phase 3 complete
├── Component: KernelOracle + UI
├── Handler:
│   ├── KernelOracle.get_cortex_text() generates capabilities
│   ├── System prompt compiled with live state
│   └── Dashboard/HUD ready for rendering
└── Success: System is visible/observable

SARGA PHASE 5: JALA (Water/Data Streams)
├── Trigger: Phase 4 complete
├── Component: Knowledge Graph + Discoverer
├── Handler:
│   ├── Load Knowledge Graph (get_knowledge_graph())
│   ├── Discoverer scans for agents
│   ├── Context resolvers execute (git, agenda, inbox)
│   └── Data starts flowing through the system
└── Success: Data streams active

SARGA PHASE 6: PRITHVI (Earth/Persistence)
├── Trigger: Phase 5 complete
├── Component: Ledger + CivicBank + Lineage
├── Handler:
│   ├── SQLite ledger mounts
│   ├── CivicBank initializes (graceful if crypto fails)
│   ├── Lineage chain connects
│   └── All agents registered with Varnas/Ashramas
└── Success: Persistent reality established

POST-BOOT: UNIVERSE IS ALIVE
├── All 6 elements manifested
├── UniversalOperatorAdapter ready
├── System waiting for ANY operator
└── "Agent City is ALIVE"
```

### Sarga Integration Code Location

The wiring will happen in `vibe_core/boot_orchestrator.py`:

```python
# CONCEPTUAL - What boot() will look like after wiring

def boot(self) -> RealVibeKernel:
    sarga = get_sarga()
    sarga.begin_boot()

    # Phase 1: SHABDA - already happened (this function was called)
    sarga.execute_phase(Element.SHABDA)

    # Phase 2: AKASHA - Create kernel
    sarga.register_phase_handler(Element.AKASHA, self._boot_akasha)
    sarga.execute_phase(Element.AKASHA)

    # Phase 3: VAYU - Communication
    sarga.register_phase_handler(Element.VAYU, self._boot_vayu)
    sarga.execute_phase(Element.VAYU)

    # Phase 4: AGNI - Form/UI
    sarga.register_phase_handler(Element.AGNI, self._boot_agni)
    sarga.execute_phase(Element.AGNI)

    # Phase 5: JALA - Data streams
    sarga.register_phase_handler(Element.JALA, self._boot_jala)
    sarga.execute_phase(Element.JALA)

    # Phase 6: PRITHVI - Persistence
    sarga.register_phase_handler(Element.PRITHVI, self._boot_prithvi)
    sarga.execute_phase(Element.PRITHVI)

    sarga.complete_boot()
    return self.kernel
```

---

## 7. COMPONENT WIRING

### What Gets Connected

| From | To | Connection |
|------|-----|------------|
| `sarga.py` | `boot_orchestrator.py` | Phase handlers call real boot steps |
| `boot_orchestrator.py` | `prompt_context.py` | `set_kernel()` after boot |
| `prompt_context.py` | `oracle.py` | `kernel_capabilities` resolver |
| `discoverer/agent.py` | `knowledge/graph.py` | Use graph for agent discovery |
| `kernel_impl.py` | `varna.py` | Assign Varna at agent registration |
| `kernel_impl.py` | `ashrama.py` | Initialize Ashrama lifecycle |
| `universal_provider.py` | `UniversalOperatorAdapter` | NEW - operator abstraction |

### Files to Modify

1. **`vibe_core/boot_orchestrator.py`**
   - Import and use Sarga
   - Register phase handlers
   - Wire PromptContext after boot

2. **`vibe_core/kernel_impl.py`**
   - Add Varna assignment in `register_agent()`
   - Add Ashrama initialization
   - Make scheduler Sarga-cycle aware

3. **`steward/system_agents/discoverer/agent.py`**
   - Use Knowledge Graph for routing decisions
   - Support both `agent.id` and `identity.agent_id` schemas

4. **NEW: `vibe_core/operator_adapter.py`**
   - UniversalOperatorAdapter class
   - OperatorSocket protocol
   - Operator implementations (Human, Claude, LLM, Local)

---

## 8. IMPLEMENTATION PHASES

### Phase A: WIRING (No new architecture)

**Goal:** Connect existing components without creating new abstractions.

```
[ ] 1. boot_orchestrator.py imports and uses Sarga phases
[ ] 2. Sarga phase handlers call real boot steps
[ ] 3. PromptContext.set_kernel() called after boot
[ ] 4. Oracle connected to PromptContext resolvers
[ ] 5. Discoverer supports both manifest schemas
```

**Estimated Effort:** Small (mostly imports and function calls)

### Phase B: ENRICHMENT (Varnas/Ashramas)

**Goal:** Add the Vedic lifecycle to agent registration.

```
[ ] 1. kernel_impl.register_agent() assigns Varna
[ ] 2. kernel_impl.register_agent() initializes Ashrama
[ ] 3. Scheduler respects Brahma cycle (Day/Night)
[ ] 4. Knowledge Graph used in Discoverer routing
```

**Estimated Effort:** Medium (logic changes in kernel)

### Phase C: UNIVERSAL OPERATOR (The Socket)

**Goal:** Create the operator-agnostic interface.

```
[ ] 1. Define OperatorSocket protocol
[ ] 2. Implement HumanOperator
[ ] 3. Implement ClaudeCodeOperator
[ ] 4. Implement LLMOperator
[ ] 5. Implement LocalLLMOperator
[ ] 6. Implement DegradedOperator (fallback)
[ ] 7. Create UniversalOperatorAdapter
[ ] 8. Wire into UniversalProvider
```

**Estimated Effort:** Medium-Large (new abstraction, multiple implementations)

### Phase D: INTEGRATION TESTING

**Goal:** Prove it works end-to-end.

```
[ ] 1. Boot with Human operator
[ ] 2. Boot with Claude Code operator
[ ] 3. Boot with LLM operator (mocked)
[ ] 4. Boot with Local LLM (if available)
[ ] 5. Test graceful degradation chain
[ ] 6. Test hot-swap capability
[ ] 7. Full Sarga boot with all phases logging
```

---

## 9. SUCCESS CRITERIA

### The System Is Complete When:

1. **Sarga Boot Works**
   - All 6 phases execute in order
   - Each phase triggers real components
   - Boot report shows timing for each phase
   - "Agent City is ALIVE" prints at the end

2. **Operator Agnostic**
   - Same boot sequence for any operator
   - Human can operate via terminal
   - Claude Code can operate via CLI
   - LLM can operate via API
   - Local model can operate offline

3. **Graceful Degradation**
   - System never crashes
   - Falls back through priority chain
   - Always has a response (even if degraded)
   - DegradedOperator handles worst case

4. **Hot-Swap Works**
   - Can switch operators at runtime
   - No restart required
   - State preserved during swap

5. **GAD-000 Compliant**
   - All tools discoverable by AI
   - All state observable
   - All errors parseable
   - All operations composable

---

## APPENDIX: KEY FILES REFERENCE

```
BOOT:
  vibe_core/boot_orchestrator.py    # Main boot logic
  vibe_core/sarga.py                # Cosmic boot phases
  vibe_core/kernel_impl.py          # VibeKernel implementation

OPERATORS:
  provider/universal_provider.py    # Central nervous system
  vibe_core/operator_adapter.py     # NEW - Universal Operator Adapter

PROMPTS:
  vibe_core/runtime/prompt_context.py   # Dynamic context
  vibe_core/runtime/oracle.py           # Kernel capabilities

AGENTS:
  steward/system_agents/envoy/          # Universal Operator Interface
  steward/system_agents/discoverer/     # Agent discovery

PHILOSOPHY:
  steward/varna.py                  # Agent classification
  steward/ashrama.py                # Agent lifecycle
  vibe_core/knowledge/graph.py      # Knowledge Graph

DOCUMENTATION:
  GAD-000.md                        # Operator Inversion Principle
  GAD-1000.md                       # Identity Fusion
```

---

## APPROVAL

**STATUS: ✅ APPROVED FOR IMPLEMENTATION**

- [x] Technical Review (Gemini)
- [x] Architecture Alignment (Strict Typing Protocol added)
- [x] Founder Approval (2025-11-29)

**Condition:** Strict typing with Pydantic models. No loose `dict[str, Any]`.

---

**END OF PLAN**

*"Sound became form. Abstraction became reality. The operator is interchangeable. Agent City is ALIVE."*
