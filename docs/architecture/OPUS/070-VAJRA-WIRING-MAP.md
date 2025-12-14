# OPUS-070: VAJRA Wiring Map - The Neural Topology of VIBE

> "Everything must surrender to the Kernel. The Kernel is the Soul."

## Status: ACTIVE HARNESS

| Category | Count | Status | Evidence |
|----------|-------|--------|----------|
| **Wired Components** | 11 | ✅ | `inject_kernel()` verified |
| **Partially Wired** | 3 | ⚠️ | Late binding patterns |
| **Blind Spots** | 14+ | ❌ | Tools orphaned from kernel |
| **Prompt Infrastructure** | 4 | ✅ | Runtime generation active |
| **Duplicate Ledgers** | 1 | 🚨 | ARCHIVIST violation |

## 1. The Core Axiom: TOTALER KRIEG

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE THREE LAWS OF EXISTENCE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. CODE ohne TEST = TOTE MATERIE                                          │
│      (Code without test = dead matter)                                      │
│                                                                             │
│   2. DOCU ohne BEWEIS = SPEKULATION                                         │
│      (Documentation without evidence = speculation)                         │
│                                                                             │
│   3. COMPONENT ohne KERNEL = ORPHAN                                         │
│      (Component without kernel = orphaned soul)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. The Kernel as Soul

```
                              ┌─────────────────┐
                              │   VIBE KERNEL   │
                              │   (The Soul)    │
                              │                 │
                              │  ┌───────────┐  │
                              │  │  LEDGER   │  │  ← SRUTI (Immutable Truth)
                              │  └───────────┘  │
                              │  ┌───────────┐  │
                              │  │  EVENTS   │  │  ← All actions recorded
                              │  └───────────┘  │
                              │  ┌───────────┐  │
                              │  │ REGISTRY  │  │  ← All agents known
                              │  └───────────┘  │
                              │  ┌───────────┐  │
                              │  │  PROMPTS  │  │  ← Runtime generation!
                              │  └───────────┘  │
                              └────────┬────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
      ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
      │   PRAKRITI    │       │    MANAS      │       │   PLUGINS     │
      │  (5 Layers)   │       │ (Cognitive)   │       │  (Extensions) │
      └───────────────┘       └───────────────┘       └───────────────┘
```

## 3. WIRED COMPONENTS (✅ Connected to Kernel)

### 3.1 Core Infrastructure

| Component | File | Method | Access |
|-----------|------|--------|--------|
| **Prakriti** | `vibe_core/state/prakriti.py:247` | `inject_kernel()` | Full kernel, cascades to Layer 2 |
| **KernelState** | `vibe_core/state/kernel_state.py:71` | `inject_kernel()` | Full kernel reference |
| **KernelIOService** | `vibe_core/io_service.py:72` | Constructor | `kernel.ledger` direct |

### 3.2 Runtime Routing

| Component | File | Method | Access |
|-----------|------|--------|--------|
| **LayeredRouter** | `vibe_core/runtime/layered_router.py:72` | `inject_kernel()` | Registries, circuits |
| **UnifiedExecution** | `vibe_core/runtime/unified_execution.py:223` | `inject_kernel()` | Circuit execution |

### 3.3 Plugin System

| Component | File | Method | Cascades To |
|-----------|------|--------|-------------|
| **OpusAssistantPlugin** | `plugin_main.py:113` | `on_boot()` | PromptContext, MANAS |
| **InterfacePlugin** | `plugin_main.py:57` | `on_boot()` | 14 renderers |

### 3.4 Cognitive Components (MANAS)

| Component | File | Method | Ledger Access |
|-----------|------|--------|---------------|
| **SrutiValidator** | `manas/validator.py:167` | `inject_kernel()` | `kernel.ledger.get_all_events()` |
| **IntentRouter** | `manas/intent_router.py:78` | `inject_kernel()` | Propagates to validator |
| **CognitiveKernel** | `manas/cognitive_kernel.py:228` | `inject_kernel()` | `kernel.ledger.record_event()` |
| **ShellCortex** | `manas/cortex/shell.py:134` | `inject_kernel()` | `kernel.ledger.record_event()` |
| **TestCortex** | `manas/cortex/test.py:139` | `inject_kernel()` | `kernel.ledger.record_event()` |

### 3.5 All Interface Renderers (14 total)

All renderers inherit from `BaseRenderer` and receive kernel in constructor:
- ArchitectureRenderer, EnvoyRenderer, GitRenderer, MatrixRenderer
- OperationsRenderer, TasksRenderer, AgentRenderer, etc.

## 4. PARTIALLY WIRED (⚠️ Late Binding)

| Component | File | Issue | Risk |
|-----------|------|-------|------|
| **EnvoyPlugin** | `envoy/plugin_main.py:549` | Lazy kernel injection on first call | Init order dependency |
| **KernelTickHandler** | `events/kernel_tick.py:264` | Conditional late-binding | MANAS might be wired differently |
| **PromptContext** | `runtime/prompt_context.py:66` | `set_kernel()` called AFTER init | Resolvers may fail early |

### Pattern Problem

```python
# ANTI-PATTERN: Late binding
class PromptContext:
    def __init__(self):
        self._kernel = None  # ← NOT SET!

    def set_kernel(self, kernel):  # ← Called later
        self._kernel = kernel

# CORRECT PATTERN: Constructor injection
class SrutiValidator:
    def inject_kernel(self, kernel):
        self._vibe_kernel = kernel
        logger.info("⚡ SRUTI: Kernel injected")
```

## 5. BLIND SPOTS STATUS

### 5.1 Analyst Tools (6 tools - ✅ WIRED)

| Tool | File | Status | Pattern |
|------|------|--------|---------|
| **ArchitectureAnalysisTool** | `analyst/tools/architecture_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |
| **CodeAnalysisTool** | `analyst/tools/code_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |
| **DependencyAnalysisTool** | `analyst/tools/deps_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |
| **DocsAnalysisTool** | `analyst/tools/docs_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |
| **GitAnalysisTool** | `analyst/tools/git_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |
| **StructureAnalysisTool** | `analyst/tools/structure_tool.py` | ✅ | `inject_kernel()` + `_get_ledger()` |

### 5.2 Archivist Tools (✅ FIXED)

| Tool | File | Status | Notes |
|------|------|--------|-------|
| **LedgerTool** | `archivist/tools/ledger_tool.py` | 🗑️ DELETED | Dead code - was duplicate ledger |
| **AuditLedger** | `archivist/tools/ledger.py` | ✅ REFACTORED | Now delegates to `kernel.ledger` |
| **AuditTool** | `archivist/tools/audit_tool.py` | ⏳ | Needs `inject_kernel()` |
| **ObserverTool** | `archivist/tools/observer_tool.py` | ⏳ | Needs kernel wiring |
| **VerifierTool** | `archivist/tools/verifier_tool.py` | ⏳ | Needs kernel wiring |

### 5.3 Other Orphaned Components

| Component | File | Issue |
|-----------|------|-------|
| **TaskManager** | `task_management/task_manager.py:35` | Optional IO service, not kernel |
| **DependencyManager** | Various | File-based only |
| **VFS** | `vibe_core/vfs.py` | Should integrate with `kernel.io_service` |
| **Librarian Tools (3)** | `librarian/tools/` | No kernel registry access |
| **MediaTool (Artisan)** | `artisan/tools/media_tool.py` | No metadata ledger |

## 6. PROMPT AS INFRASTRUCTURE (Runtime Generation)

> "Prompts generiert das System zu Runtime!" - This is the JET FUEL!

### 6.1 The Prompt Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PromptContext  │────▶│  KernelOracle   │────▶│  PromptComposer │
│  (16+ resolvers)│     │  (capabilities) │     │  (templates)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐            ┌─────────┐            ┌─────────┐
    │git_status│           │cartridges│           │ FINAL   │
    │system_time│          │tools     │           │ PROMPT  │
    │kernel_   │           │agents    │           │         │
    │capabilities│         │meta_cmds │           │ (LIVE!) │
    └─────────┘            └─────────┘            └─────────┘
```

### 6.2 PromptContext Resolvers (16+ built-in)

```python
# vibe_core/runtime/prompt_context.py

RESOLVERS = {
    # Git/Repo (LIVE at call time)
    "git_status":        lambda: subprocess.run(["git", "status"]),
    "project_structure": lambda: walk_directory_tree(),
    "current_branch":    lambda: git_current_branch(),
    "recent_commits":    lambda: git_log_recent(),

    # System State (LIVE)
    "system_time":       lambda: datetime.utcnow().isoformat(),
    "inbox_count":       lambda: count_inbox_items(),
    "agenda_summary":    lambda: summarize_agenda(),

    # Kernel State (via kernel.*)
    "kernel_status":     lambda: kernel.status,
    "kernel_agents":     lambda: kernel.manifest_registry.list(),
    "kernel_ledger_events": lambda: kernel.ledger.get_all_events()[-10:],
    "kernel_capabilities":  lambda: kernel_oracle.get_system_capabilities(),
}
```

### 6.3 Plugin-Driven Resolution

Plugins can register their own resolvers:

```python
# In opus_assistant/plugin_main.py:326

def on_boot(self, kernel):
    # Register OPUS-specific resolver
    prompt_context = get_prompt_context()
    prompt_context.register("opus_context", self._opus_context_provider)

def _opus_context_provider(self) -> str:
    """Dynamic OPUS state injection."""
    return {
        "trust_score": self._calculate_trust(),
        "karma": self._get_karma_level(),
        "active_intents": self._get_pending_intents(),
    }
```

### 6.4 KernelOracle (ARCH-064)

```python
# vibe_core/runtime/oracle.py

class KernelOracle:
    """Single source of truth for system capabilities."""

    def get_cartridges(self) -> List[Dict]:
        return self.kernel.manifest_registry.list_cartridges()

    def get_tools(self) -> List[str]:
        return self.kernel.tool_discovery.list_all()

    def get_meta_commands(self) -> List[Dict]:
        return self.kernel.command_registry.list()

    def get_system_capabilities(self) -> Dict:
        """Injected into Steward's system prompt."""
        return {
            "cartridges": self.get_cartridges(),
            "tools": self.get_tools(),
            "meta_commands": self.get_meta_commands(),
        }
```

## 7. THE VISION: opus_assistant as Operator

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OPUS_ASSISTANT: THE MILLION DOLLAR APP                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           ┌───────────────────┐                             │
│                           │   VIBE KERNEL     │                             │
│                           │   (The Soul)      │                             │
│                           └─────────┬─────────┘                             │
│                                     │                                       │
│                     ┌───────────────┼───────────────┐                       │
│                     │               │               │                       │
│                     ▼               ▼               ▼                       │
│            ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│            │   MANAS     │  │  PRAKRITI   │  │  PROMPTS    │                │
│            │ (Cognition) │  │  (5 Layers) │  │ (Runtime)   │                │
│            └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│                   │                │                │                       │
│         ┌─────────┴─────────┬──────┴──────┬────────┴────────┐               │
│         │                   │             │                 │               │
│         ▼                   ▼             ▼                 ▼               │
│   ┌──────────┐       ┌──────────┐   ┌──────────┐     ┌──────────┐          │
│   │  JNANA   │       │  DHARMA  │   │ SANKALPA │     │   VEDA   │          │
│   │ (Wisdom) │       │  (Law)   │   │ (Will)   │     │(Pipeline)│          │
│   └──────────┘       └──────────┘   └──────────┘     └──────────┘          │
│         │                   │             │                 │               │
│         └───────────────────┴─────────────┴─────────────────┘               │
│                                     │                                       │
│                                     ▼                                       │
│                        ┌────────────────────────┐                           │
│                        │   SRUTI VALIDATOR      │                           │
│                        │   (Truth Guardian)     │                           │
│                        │                        │                           │
│                        │ Facts require EVT-ref  │                           │
│                        │ Speculation = BLOCKED  │                           │
│                        └────────────────────────┘                           │
│                                                                             │
│   "A universe inside a universe. Self-maintaining. Self-healing."           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 8. THE WIRING CHECKLIST (Harness)

### Verified Wiring (for @HARNESS)

```yaml
harness:
  wiring:
    # Core - Must pass
    - test: "prakriti_has_kernel"
      check: "hasattr(prakriti, '_kernel') and prakriti._kernel is not None"

    - test: "manas_has_ledger_access"
      check: "cognitive_kernel._vibe_kernel.ledger is not None"

    - test: "sruti_validator_bound"
      check: "intent_router._validator._vibe_kernel is not None"

    - test: "prompt_context_kernel_set"
      check: "prompt_context._kernel is not None"

    # Blind Spots - Must fix
    - test: "analyst_tools_wired"
      check: "all(hasattr(t, 'inject_kernel') for t in analyst_tools)"
      status: "FAILING"  # TODO: Wire these

    - test: "archivist_single_ledger"
      check: "archivist_ledger_tool.uses_kernel_ledger()"
      status: "FAILING"  # TODO: Remove duplicate ledger
```

### Wiring Coverage Score

```
WIRED:          11 components    ████████████░░░░░░░░  44%
PARTIAL:         3 components    █░░░░░░░░░░░░░░░░░░░  12%
BLIND SPOTS:    14+ components   ░░░░░░░░░░░░░░░░░░░░  44%

GOAL: 100% kernel wiring = JET FUEL
```

## 9. Action Items (Priority Order)

### P0: Critical (Architectural Violations)

1. **ARCHIVIST DUPLICATE LEDGER** - Remove `ledger_tool.py`'s separate JSON file
   - File: `vibe_core/cartridges/system/archivist/tools/ledger_tool.py`
   - Fix: Use `kernel.ledger` wrapper instead

### P1: High (Blind Spots)

2. **Wire Analyst Tools** - Add `inject_kernel()` to all 6 tools
3. **Wire TaskManager** - Add kernel binding for event recording
4. **Fix PromptContext Late Binding** - Ensure null-checks in all resolvers

### P2: Medium (Enhancement)

5. **Wire DependencyManager** - Enable runtime import graph tracking
6. **Wire VFS** - Integrate with `kernel.io_service`
7. **Wire Librarian Tools** - Enable kernel registry access

## 10. References

| Document | Purpose |
|----------|---------|
| `OPUS-057-VAJRA.md` | Kernel injection pattern spec |
| `OPUS-069-SRUTI-SMRITI.md` | Truth layer separation |
| `OPUS-050-VEDA.md` | Four-fold processing pipeline |
| `vibe_core/kernel_impl.py` | The Soul implementation |
| `vibe_core/runtime/prompt_context.py` | Prompt infrastructure |

---

*"The Kernel is the Soul. Everything surrenders to it. This is the TOTALER KRIEG."*

*"Code ohne Test = Tote Materie. Docu ohne Beweis = Spekulation."*
