# OPUS-070: VAJRA Wiring Map - The Neural Topology of VIBE

> "Everything must surrender to the Kernel. The Kernel is the Soul."

## Status: ⚡ ENFORCEMENT ACTIVE

| Category | Count | Status | Evidence |
|----------|-------|--------|----------|
| **Wired Components** | 18+ | ✅ | `inject_kernel()` verified |
| **VAJRA Module** | 1 | ✅ | `vibe_core/vajra/` |
| **Enforcement Tests** | 15 | ✅ | `tests/unit/test_vajra_wiring.py` |
| **Pre-commit Hook** | 1 | ✅ | `.pre-commit-config.yaml` |
| **Prompt Infrastructure** | 4 | ✅ | Runtime generation active |

### Victory Lap (Completed)

| Task | Status | Commit |
|------|--------|--------|
| **P0: Kill the Traitor** | ✅ DONE | Archivist duplicate ledger removed |
| **P1: Wire the Blind** | ✅ DONE | 6 Analyst tools wired |
| **P2: Enforce the Law** | ✅ DONE | VAJRA enforcement system created |

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

### 5.2 Archivist Tools (✅ FULLY WIRED)

| Tool | File | Status | Notes |
|------|------|--------|-------|
| **LedgerTool** | `archivist/tools/ledger_tool.py` | 🗑️ DELETED | Dead code - was duplicate ledger |
| **AuditLedger** | `archivist/tools/ledger.py` | ✅ REFACTORED | Now delegates to `kernel.ledger` |
| **AuditTool** | `archivist/tools/audit_tool.py` | ✅ WIRED | `inject_kernel()` + `_get_ledger()` |
| **ObserverTool** | `archivist/tools/observer_tool.py` | ✅ WIRED | `inject_kernel()` + `_get_ledger()` |
| **VerifierTool** | `archivist/tools/verifier_tool.py` | ✅ WIRED | `inject_kernel()` + `_get_ledger()` |

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
WIRED:          14 components    ███████████████░░░░░  56%
PARTIAL:         3 components    █░░░░░░░░░░░░░░░░░░░  12%
BLIND SPOTS:    11+ components   ░░░░░░░░░░░░░░░░░░░░  32%

GOAL: 100% kernel wiring = JET FUEL
```

**Recent Progress (2025-12-15):**
- ✅ AuditTool, ObserverTool, VerifierTool now wired

## 9. ⚡ VAJRA Enforcement System

### 9.1 The VAJRA Module (`vibe_core/vajra/`)

```
vibe_core/vajra/
├── __init__.py          # Public API
├── protocol.py          # WiringProtocol definition
├── enforcement.py       # @assert_wired, @require_wiring, WiringError
├── auto_wire.py         # auto_wire(), wire_all(), deep_wire()
├── scanner.py           # VAJRAScanner for static analysis
└── pytest_plugin.py     # wired_kernel fixture, markers
```

### 9.2 Usage Patterns

```python
# 1. Make a component wirable
class MyComponent:
    _vibe_kernel = None

    def inject_kernel(self, kernel):
        self._vibe_kernel = kernel

    def _get_ledger(self):
        if self._vibe_kernel is None:
            return None
        return self._vibe_kernel.ledger

# 2. Auto-wire in tests
from vibe_core.vajra import auto_wire, wire_all
auto_wire(kernel, component)
wire_all(kernel, c1, c2, c3)

# 3. Enforce wiring at runtime
from vibe_core.vajra import assert_wired, require_wiring

@assert_wired  # Warns in shadow mode
def execute(self): ...

@require_wiring(strict=True)  # Raises WiringError
def critical_operation(self): ...

# 4. Scan for orphans
from vibe_core.vajra import scan_for_orphans
result = scan_for_orphans(fail_on_orphans=True)
```

### 9.3 Pre-commit Hook

```bash
# Run VAJRA scanner manually
pre-commit run vajra-wiring-check --hook-stage manual

# Or directly
python -m vibe_core.vajra.scanner --strict
```

### 9.4 Test Fixtures

```python
# In tests, use wired_kernel fixture
@pytest.mark.require_wiring
def test_my_component(wired_kernel):
    component = MyComponent()
    component.inject_kernel(wired_kernel)
    assert component._get_ledger() is wired_kernel.ledger
```

## 10. Historical: Completed Action Items

### P0: Kill the Traitor ✅

1. **ARCHIVIST DUPLICATE LEDGER** - DELETED `ledger_tool.py`
   - `AuditLedger` now delegates to `kernel.ledger`
   - Commit: `c00faba`

### P1: Wire the Blind ✅

2. **Wire Analyst Tools** - Add `inject_kernel()` to all 6 tools
3. **Wire TaskManager** - Add kernel binding for event recording
4. **Fix PromptContext Late Binding** - Ensure null-checks in all resolvers

### P2: Medium (Enhancement)

5. **Wire DependencyManager** - Enable runtime import graph tracking
6. **Wire VFS** - Integrate with `kernel.io_service`
7. **Wire Librarian Tools** - Enable kernel registry access

## 11. OPUS-072 Tech Debt: MANAS Identity Proxy

### The Oppenheimer Moment 🔴

OPUS-072 gave MANAS the ability to act on behalf of the KERNEL for privileged syscalls.
This is architecturally **necessary** but creates tight coupling.

### The Coupling

```python
# vibe_core/circuit_executor.py:56
try:
    from vibe_core.cartridges.system.manas import ManasCartridge
    MANAS_AVAILABLE = True
except ImportError:
    MANAS_AVAILABLE = False
    ManasCartridge = None

# vibe_core/circuit_executor.py:808
if MANAS_AVAILABLE and ManasCartridge:
    effective_requester = ManasCartridge.get_syscall_identity(syscall_type_str)
```

### Why This Works (For Now)

1. **Soft Coupling**: `try/except ImportError` makes it optional
2. **Controlled Access**: Only circuits can reach this code
3. **Explicit Policy**: `PRIVILEGED_SYSCALLS = {"GRANT_MANDATE", "REVOKE_MANDATE"}`

### The Problem (Future Risk)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Layer Violation | 🟡 Medium | Runtime shouldn't know about Cartridges |
| Hardcoded Sudo | 🟠 Watchlist | No caller verification |
| Tight Coupling | 🟢 Acceptable | Documented, soft coupling |

### Future Refactoring: Abstract Identity Provider

```python
# PROPOSED: protocols/identity_provider.py
class IdentityProvider(Protocol):
    def get_syscall_identity(self, syscall_type: str) -> str:
        """Get effective identity for syscall execution."""
        ...

# circuit_executor.py would then use:
identity_provider: Optional[IdentityProvider] = None
# Set during boot by whoever provides identity (MANAS, KERNEL, etc.)
```

### Decision Record

- **Date**: 2025-12-14
- **Decision**: Accept coupling for OPUS-072 breakthrough
- **Rationale**: MANAS needs KERNEL identity to break Permission Denied deadlock
- **Review**: Refactor when abstracting identity layer (P3)

## 12. OPUS-073 Investigation - MANAS Triggering

**Discovery Date**: 2025-12-14
**Corrected**: 2025-12-15
**Status**: ✅ ANALYSIS COMPLETE

### What MANAS Actually Needs

The `manas_awakening.yaml` circuit explicitly states:
> "NOT triggered on every KERNEL_TICK"

MANAS triggers on:
| Event | Source | Status |
|-------|--------|--------|
| `KERNEL_BOOT` | kernel.boot() | ✅ Already exists |
| `HOURLY_PULSE` | heartbeat.py | ⏳ heartbeat.py needs to emit/call |
| `IDLE_DETECTED` | Activity monitor | Future |
| `MANAS_FORCE_THINK` | Manual/CLI | Available |

### What Was Wrong (Reverted)

An incorrect analysis suggested adding KERNEL_TICK emission to `kernel.tick()`.
This was **WRONG** because:
1. MANAS does NOT listen for KERNEL_TICK (by design - rate limiting)
2. It created a parallel event path (spaghetti)
3. The kernel architecture uses direct `on_tick_pre()` calls, not EventBus

**The kernel change was reverted.** Kernel is eternal.

### Correct Solution

The `heartbeat.py` script (runs every 15 mins via GitHub Actions) should:
1. Call `MANAS.think()` directly
2. Process safe auto-executable intents

```python
# scripts/heartbeat.py - correct approach
from vibe_core.plugins.opus_assistant.manas import CognitiveKernel

def beat():
    manas = CognitiveKernel(workspace=Path.cwd())
    intents = manas.think(force=True)
    # Process intents...
```

### Verification Harness

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-073-MANAS-TRIGGER
  version: 3.0.0
  status: ANALYSIS_COMPLETE

  checks:
    # KERNEL_BOOT - Already works
    - type: PATTERN
      path: vibe_core/kernel_impl.py
      pattern: "KERNEL_BOOT"
      status: PASS
      description: "KERNEL_BOOT already emitted during boot"

    # Heartbeat → MANAS
    - type: PATTERN
      path: scripts/heartbeat.py
      pattern: "manas|cognitive_kernel|think\\("
      required: true
      status: PENDING
      description: "heartbeat.py must import and use MANAS"

  tests:
    - path: tests/integration/test_event_emission.py
      description: "Verify MANAS triggering requirements"
```
<!-- HARNESS:END -->

### Key Insight

The kernel already emits KERNEL_BOOT during boot. MANAS awakening circuit
triggers on KERNEL_BOOT. The "missing" piece is:
1. HOURLY_PULSE should come from heartbeat.py (external cron)
2. OR heartbeat.py directly calls MANAS.think()

**Kernel is eternal. Don't touch it for event wiring.**

*"Architektur ohne Ausführung = Treibsand. Aber Spaghetti ist schlimmer."*

---

## 13. References

| Document | Purpose |
|----------|---------|
| `OPUS-057-VAJRA.md` | Kernel injection pattern spec |
| `OPUS-069-SRUTI-SMRITI.md` | Truth layer separation |
| `OPUS-050-VEDA.md` | Four-fold processing pipeline |
| `OPUS-072-MANAS-DEVATA.md` | MANAS identity proxy design |
| `vibe_core/kernel_impl.py` | The Soul implementation |
| `vibe_core/runtime/prompt_context.py` | Prompt infrastructure |
| `vibe_core/cartridges/system/manas/` | MANAS Devata cartridge |

---

*"The Kernel is the Soul. Everything surrenders to it. This is the TOTALER KRIEG."*

*"Code ohne Test = Tote Materie. Docu ohne Beweis = Spekulation."*

*"Der Geist hat Hände bekommen. Mal sehen, was er damit anfasst."* (OPUS-072)
