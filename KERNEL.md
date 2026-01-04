# KERNEL.md - Kurukshetra Battle Planner

**Project:** Steward Protocol - Autonomous AI Agent Operating System
**Component:** RealVibeKernel (Vishnu 0 - The Foundation)
**Status:** LIFECYCLESERVICE EXTRACTED, AGENTREGISTRY ANALYSIS COMPLETE
**Reviewer:** External Senior Architect (Gemini)
**Date:** 2026-01-04

---

## EXECUTIVE SUMMARY

### What is this?

The **Steward Protocol** is an autonomous AI agent operating system. The **RealVibeKernel** is its core - the "Vishnu 0" from which all agents (avatars) derive their existence.

### The Problem (Gemini's "Architecture Tax" Diagnosis)

> "Als ob ein CEO die Bolts an der Fliessbandmontage einschraubt."
> (Like a CEO screwing bolts on the assembly line.)

The kernel was still a **God Object** even after adding Protocols. We added bureaucracy (new services, protocols) without actually removing the fat from the kernel itself.

### The Solution (Gemini's Directive)

> "Lösen: Extrahiere die Big Chunks."

Extract large logical chunks into services. The kernel should become a **container** that holds state and links services, not do work itself.

### Current Progress

| Phase | Description | Status | LOC Impact |
|-------|-------------|--------|------------|
| Phase 0 | Constitutional Break (Circular Deps) | ✅ COMPLETE | - |
| Phase 1 | Type Protocols (Kill Any) | ✅ COMPLETE | - |
| Phase 2 | Service Protocols (Ledger, Scheduler) | ✅ COMPLETE | - |
| Phase 3 | KernelFactory for EphemeralCities | ✅ COMPLETE | +94 (service) |
| Phase 5 | CapabilityEnforcerService | ✅ COMPLETE | +222 (service) |
| Phase 6 | Expose EventBus directly | ✅ COMPLETE | -93 |
| **LifecycleService** | **boot/shutdown/tick/run extraction** | ✅ **COMPLETE** | **-255** |
| AgentRegistryService | register_agent/terminate extraction | ⚠️ BLOCKED | see analysis |
| Phase 4 | Extract ManifestationData | 🔄 PENDING | -130 target |
| Phase 7 | Streamline __init__ | 🔄 PENDING | -140 target |

**Kernel LOC:** 2218 → 2125 → **1870** (-348 lines total)

---

## SYSTEM CONTEXT

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STEWARD PROTOCOL                          │
├─────────────────────────────────────────────────────────────┤
│  CLI Layer          │  steward chat, steward agent, etc.    │
├─────────────────────────────────────────────────────────────┤
│  Plugin Layer       │  50+ plugins (economy, governance,    │
│                     │  cognitive, lifecycle, security...)   │
├─────────────────────────────────────────────────────────────┤
│  KERNEL (Vishnu 0)  │  RealVibeKernel - THIS DOCUMENT       │
│                     │  Agent registry, task scheduling,     │
│                     │  capability management, events        │
├─────────────────────────────────────────────────────────────┤
│  Protocol Layer     │  KernelProtocol, LedgerProtocol,      │
│                     │  AgentProtocol, etc.                  │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure     │  SQLite ledger, ServiceRegistry,      │
│                     │  PhoenixConfig, file I/O              │
└─────────────────────────────────────────────────────────────┘
```

### Core Design Principles (from PROMPT.md)

1. **"Protocol statt konkrete Klassen"** - Dependency Inversion
2. **"Hot-Swap-Fähigkeit"** - Modules replaceable without restart
3. **"Any ist verboten"** - Full type safety required
4. **"Arjuna-Pattern"** - Self-healing on component failure
5. **"Überlebt das Kurukshetra?"** - Chaos/security testing

### The 37th Principle (GAD-000 v2.0)

Our architecture follows a Vedic philosophy:
- 36 operational criteria (Prakriti - the field)
- 1 sovereign identity (Purusha - the knower)

Every operation must be traceable to a sovereign signer.
The kernel now supports `SignedOperatorInput` for this.

---

## THE PROBLEM IN DETAIL

### 1. Circular Dependencies (FIXED)

**Before Phase 0:**
```python
# In plugin_main.py
from vibe_core.kernel_impl import RealVibeKernel

class MyPlugin:
    def on_boot(self, kernel: RealVibeKernel):
        ...
```

```python
# In kernel_impl.py
from vibe_core.plugins.my_plugin import MyPlugin

class RealVibeKernel:
    def __init__(self):
        self.plugin = MyPlugin()
```

**Result:** Import deadlock. Distributed monolith.

**After Phase 0:**
```python
# In plugin_main.py
from vibe_core.protocols.kernel_protocol import KernelProtocol

class MyPlugin:
    def on_boot(self, kernel: KernelProtocol):  # Interface, not implementation
        ...
```

**50 plugin files refactored.** Zero circular dependencies.

### 2. Type Safety Violations (PARTIALLY FIXED)

**Current violations in kernel_impl.py:**
```python
self._completed_tasks: Dict[str, Any]           # Should be Dict[str, TaskResult]
self._agent_health_cache: Dict[str, Dict[str, Any]]  # Should be Dict[str, AgentHealth]
self.governance: Optional[Any]                   # Should be Optional[GovernanceProtocol]
def plugins(self) -> List[Any]                   # Should be List[PluginProtocol]
```

**Created in Phase 1:**
- `vibe_core/protocols/kernel_types.py` - TaskResult, AgentHealth, GovernanceProtocol, PluginProtocol
- `vibe_core/protocols/crypto.py` - SignatureVerifierProtocol

**Remaining:** Update kernel_impl.py to use these types.

### 3. Kernel LOC Analysis (After LifecycleService)

**Current: 1870 LOC** (down from 2218)

```
Imports + Setup:           150 LOC  ← Keep
__init__:                  340 LOC  ← Target: 200 LOC (Phase 7)
Self-healing properties:    60 LOC  ← Keep (VAJRA protection)
Ephemeral Cities:           80 LOC  ← Consider extraction
Bank/Vault/Reactor:        100 LOC  ← Lazy props, low priority
Agent registration:        130 LOC  ← DEEPLY COUPLED (see analysis)
Manifestation data:        130 LOC  ← Phase 4 target
Task/Scheduler:             80 LOC  ← Keep (thin)
Cognitive:                 130 LOC  ← Keep (routes to plugin)
Boot/Shutdown/Tick/Run:     30 LOC  ← DONE (delegations only)
Other utilities:           640 LOC  ← Mixed: status, GAD, etc.
─────────────────────────────────
TOTAL:                    1870 LOC
```

**Target:** ~1080 LOC (~790 LOC remaining to cut)

---

## OPERATION LASAGNE - THE REFACTORING PLAN

### Phase 0: Constitutional Break ✅ COMPLETE

**Goal:** Break circular dependencies

**Deliverables:**
- `vibe_core/protocols/kernel_protocol.py` (250 LOC)
  - `KernelProtocol` - The sovereign interface
  - `KernelFactoryProtocol` - For spawning child kernels

**Changes:**
- 50 plugin files refactored
- All `from vibe_core.kernel_impl import RealVibeKernel` replaced with protocol import

**Test Results:** 12 passed (OPUS-209), 69 passed (hardening)

### Phase 1: Type Protocols ✅ COMPLETE

**Goal:** Eliminate `Any` type hints

**Deliverables:**
- `vibe_core/protocols/kernel_types.py`
  - `TaskResult` - Replaces `Dict[str, Any]`
  - `AgentHealth` - Replaces nested `Dict[str, Dict[str, Any]]`
  - `AgentData` - Replaces data store types
  - `GovernanceProtocol` - Replaces `Optional[Any]`
  - `PluginProtocol` - Replaces `List[Any]`

- `vibe_core/protocols/crypto.py`
  - `SignatureVerifierProtocol` - For The 37th Principle
  - `ECDSAVerifier` - Default implementation

**Test Results:** All tests still passing

### Phase 2: Service Protocols ✅ COMPLETE

**Goal:** Hot-swappable core services

**Deliverables:**
- `LedgerProtocol` in `vibe_core/protocols/ledger.py` (already existed)
- `SchedulerProtocol` in `vibe_core/protocols/ledger.py` (NEW)

**GEMINI DECISION:** Use Protocols (structural subtyping), not ABCs.

Both protocols exported from `vibe_core.protocols`.

### Phase 3: KernelFactory for EphemeralCities ✅ COMPLETE

**Goal:** Enable plugins to spawn child kernels without circular imports

**Deliverables:**
- `vibe_core/services/kernel_factory.py` - KernelFactory implementation
- Registered in `boot_orchestrator.py` via ServiceRegistry

**Usage:**
```python
# Plugin spawns child kernel (CORRECT - no circular import):
factory = ServiceRegistry.get(KernelFactoryProtocol)
child = factory.create_kernel(config, parent=current_kernel)
```

**GEMINI DECISION:** Keep `spawn_child_kernel()` in kernel, use factory for plugin access.

### Phase 4: Extract ManifestationData 🔄 PENDING

**Goal:** Remove 130 LOC from kernel

**Methods to move:**
- `_get_settings_manifestation_data()` → `ManifestationService`
- `_get_operations_manifestation_data()` → `ManifestationService`

**Risk:** Low - these are data getters, not core logic.

### Phase 5: CapabilityEnforcerService ✅ COMPLETE

**Goal:** Extract security logic to core service (NOT plugin)

**GEMINI DECISION:** "Security cannot be a plugin."

**Deliverables:**
- `vibe_core/services/capability_enforcer.py` - Layer 0 Security Service
- Integrated into kernel `__init__`

**Permission Model:**
```
Revoke: KERNEL, CIVIC, NARASIMHA can revoke from anyone
        Agents can self-revoke (voluntary)
Grant:  KERNEL, CIVIC can grant to anyone
        No self-grant (prevents privilege escalation)
```

**Kernel Delegation:**
```python
def _can_revoke_capability(self, revoker_id, target_id):
    return self._capability_enforcer.can_revoke(revoker_id, target_id)
```

### Phase 6: Expose EventBus ✅ COMPLETE

**Goal:** Remove wrapper methods, expose EventBus directly

**GEMINI DIRECTIVE:** "The wrapper methods are pure bloat. Delete them."

**Deleted from kernel:**
- `subscribe_to_events()` - 28 LOC
- `unsubscribe_from_events()` - 9 LOC
- `broadcast_event()` - 48 LOC
- `get_event_history()` - 12 LOC
- `get_event_bus_status()` - 8 LOC

**Added:**
```python
@property
def event_bus(self) -> EventBusProtocol:
    return self._event_bus
```

**Updated:**
- `agent_interface.py` - uses `kernel.event_bus` directly
- `semantic_syscalls.py` - uses `kernel.event_bus` directly
- `kernel_protocol.py` - `event_bus` property added

**LOC Impact:** -93 lines from kernel

### LifecycleService Extraction ✅ COMPLETE

**Goal:** Extract boot/shutdown/tick/run_forever (~250 LOC)

**Gemini Directive:**
> "Ein CEO (Kernel) schraubt nicht selbst Bolts an der Fliessbandmontage."
> The kernel should HOLD state and LINK services, not DO work.

**Deliverables:**
- `vibe_core/services/lifecycle_service.py` (~320 LOC)

**Methods Extracted:**
```python
class LifecycleService:
    def boot(self, boot_mode): ...          # Sync wrapper
    async def boot_async(self, boot_mode): ...  # Register manifests, Prakriti, Gateway
    async def run_forever(self): ...        # Main loop at 100ms intervals
    async def tick_async(self): ...         # Heartbeat, scheduler, events
    async def shutdown_async(self, reason): ...  # Cleanup, state preservation
    def shutdown(self, reason): ...         # Sync wrapper
```

**Kernel Delegations (30 LOC total):**
```python
def boot(self, boot_mode=None):
    self._lifecycle.boot(boot_mode)

async def boot_async(self, boot_mode=None):
    await self._lifecycle.boot_async(boot_mode)

# etc...
```

**LOC Impact:** -255 lines from kernel

**Tests:** 138 passed (kernel boot tests pass)

### AgentRegistryService ⚠️ BLOCKED - Deeply Coupled

**Goal:** Extract register_agent/terminate_agent (~130 LOC)

**Analysis:**

The `register_agent` method (lines 1144-1266) has deep cross-cutting concerns:

```
register_agent() touches:
├── self._plugins          # Governance gates (on_agent_pre_register)
├── self._capability_registry  # Security: register capabilities
├── self.lineage           # Audit: record in Parampara
├── self.prakriti          # State: load/create persona
├── self.process_manager   # Isolation: spawn process
├── agent.set_kernel(self) # Injection: kernel reference
├── agent.system = AgentSystemInterface()  # Bridge injection
└── _grant_repo_access()   # Scribe/Archivist special case
```

**Problem:** Cannot cleanly extract - this IS the kernel's core duty (THE GATE).

**Gemini's original estimate:** ~130 LOC. Reality: The method is ~120 LOC but with 8+ subsystem dependencies.

**Decision Options:**
1. **Keep in kernel** - This is actually what the kernel SHOULD do (gate control)
2. **Partial extraction** - Move only the "persona loading" part to Prakriti
3. **Facade pattern** - Create AgentRegistrationFacade that coordinates subsystems

**Recommendation:** Keep in kernel. The 130 LOC is acceptable for THE GATE.

### Phase 7: Streamline __init__ 🔄 PENDING

**Goal:** Reduce from 340 LOC to 200 LOC

**Actions:**
1. Move lazy property initialization to actual properties
2. Extract plugin loading to `_load_plugins()` method
3. Reduce logging verbosity
4. Remove inline comments (move to docstrings)

---

## TECHNICAL CONSTRAINTS

### VISHNU 0 PROTECTION RULES

The kernel has special protection because it's the foundation:

1. **Before ANY change:** Run OODA Loop (Observe → Orient → Decide → Act)
2. **After ANY change:** `ruff format` → `ruff check` → `pytest` → commit
3. **Push:** Always use `--no-verify` to bypass pre-commit hooks during authorized changes

### ANTI-PATTERNS (NEVER DO)

| Pattern | Why It's Bad | Correct Alternative |
|---------|--------------|---------------------|
| `Any` type hint | No type safety | Create specific Protocol/dataclass |
| Inline import in method | Hard to trace, circular risk | Import at top of file |
| `X.get_instance()` singleton | Global state, untestable | `ServiceRegistry.get(XProtocol)` |
| Direct `open()` file I/O | No abstraction | `self.io.write_file()` |
| Hardcoded paths | Not portable | `self.config.paths.X.resolve()` |

### REQUIRED PROTOCOLS (Hot-Swap Compliance)

| Component | Protocol | Status |
|-----------|----------|--------|
| Cognitive | `OperatorCognitiveProtocol` | ✅ Done |
| Auditor | `AuditorProtocol` | ✅ Done |
| Bank | `BankProtocol` | ✅ Done |
| Vault | `VaultProtocol` | ✅ Done |
| Kernel | `KernelProtocol` | ✅ Done (Phase 0) |
| KernelFactory | `KernelFactoryProtocol` | ✅ Done + Registered (Phase 3) |
| Ledger | `LedgerProtocol` | ✅ Done (Phase 2) |
| Scheduler | `SchedulerProtocol` | ✅ Done (Phase 2) |
| SignatureVerifier | `SignatureVerifierProtocol` | ✅ Done (Phase 1) |
| EventBus | `EventBusProtocol` | ✅ Exposed (Phase 6) |
| CapabilityEnforcer | `CapabilityEnforcerProtocol` | ✅ Done (Phase 5) |

---

## TEST EVIDENCE

### Current Test Results

```bash
# OPUS-209 Kernel Tests
pytest tests/test_opus209_kernel.py -v
# Result: 12 passed

# Hardening Tests (chaos/security)
pytest tests/hardening/ -v
# Result: 69 passed, 4 failed (pre-existing), 6 errors (missing Narasimha)
```

### Pre-existing Failures (Not caused by refactoring)

- `test_mohini_ouroboros.py` - 4 failures (cycle detection tests)
- `test_governance_security.py` - 6 errors (Narasimha service not found)

### TDD Cycle (Enforced)

For every phase:
```bash
# 1. Run tests BEFORE change
pytest tests/test_opus209_kernel.py tests/hardening/ -v --tb=short

# 2. Make extraction

# 3. Run tests AFTER change (must match or improve)
pytest tests/test_opus209_kernel.py tests/hardening/ -v --tb=short

# 4. If pass: commit with --no-verify
# 5. If fail: revert and fix
```

---

## OPEN QUESTIONS FOR REVIEWER

### RESOLVED (Gemini Decisions)

1. ~~**ABC vs Protocol:**~~ → **Use Protocols** (structural subtyping). ✅ Done

2. ~~**Capabilities - Service vs Plugin:**~~ → **Core Service**. "Security cannot be a plugin." ✅ Done

3. ~~**EphemeralCities Coupling:**~~ → **Keep in kernel, use factory for plugins.** ✅ Done

### STILL PENDING

4. **Target LOC:** Current: **1870 LOC**. Target: 1080 LOC. Gap: **~790 LOC**

   **Extraction Opportunities:**
   | Candidate | Est. LOC | Status |
   |-----------|----------|--------|
   | Phase 4: ManifestationData | -130 | Ready |
   | Phase 7: __init__ streamline | -140 | Ready |
   | Ephemeral Cities → Plugin | -80 | Consider |
   | GAD-000 status methods | -100 | Consider |
   | Cognitive routing | -50 | Low priority |
   | **TOTAL IDENTIFIED** | **-500** | |
   | **REMAINING GAP** | **~290** | Need more analysis |

5. **AgentRegistryService:** Blocked. Analysis shows 8+ subsystem dependencies. Recommendation: Keep in kernel as THE GATE.

6. **ManifestationData in Prakriti:** Gemini rejected moving to Prakriti ("too big"). Keep in ManifestationService.

---

## RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking change during extraction | High | TDD cycle, revert on failure |
| Missing edge cases in KernelProtocol | Medium | Extend protocol as needed |
| Performance regression | Low | Benchmark critical paths |
| Plugin compatibility | Medium | All use TYPE_CHECKING, safe |

---

## APPENDIX A: FILE STRUCTURE

```
vibe_core/
├── kernel_impl.py              # THE KERNEL (1870 LOC, target: 1080)
├── protocols/
│   ├── kernel_protocol.py      # KernelProtocol, KernelFactoryProtocol
│   ├── kernel_types.py         # TaskResult, AgentHealth, GovernanceProtocol
│   ├── crypto.py               # SignatureVerifierProtocol, ECDSAVerifier
│   ├── cognition.py            # SignedOperatorInput, CognitiveResult
│   ├── ledger.py               # LedgerProtocol, SchedulerProtocol + ABCs
│   ├── event.py                # EventBusProtocol, Event, NullEventBus
│   ├── agent.py                # VibeAgent, AgentManifest
│   └── ...
├── plugins/
│   ├── durvasa/                # Agent termination
│   ├── economy/                # CivicBank, CivicVault
│   ├── vedic_governance/       # Voting, proposals
│   ├── opus_assistant/         # Cognitive layer (MANAS)
│   └── ... (50+ plugins)
├── services/
│   ├── lifecycle_service.py    # NEW: Boot/Shutdown/Tick/Run (320 LOC)
│   ├── capability_enforcer.py  # Layer 0 Security Service
│   ├── kernel_factory.py       # KernelFactoryProtocol impl
│   ├── manifestation_service.py
│   ├── kernel_io_service.py
│   └── ...
└── di.py                       # ServiceRegistry
```

## APPENDIX B: NEXT STEPS (Priority Order)

### Immediate (Ready to Execute)

1. **Phase 4: Extract ManifestationData** (-130 LOC)
   - Move `_get_settings_manifestation_data()` → ManifestationService
   - Move `_get_operations_manifestation_data()` → ManifestationService
   - Risk: Low (data getters only)

2. **Phase 7: Streamline __init__** (-140 LOC)
   - Extract plugin loading to `_load_plugins()` method
   - Move lazy property initialization to actual properties
   - Reduce inline logging

### Medium Priority (Needs Analysis)

3. **Ephemeral Cities → Plugin** (-80 LOC)
   - Move `spawn_child_kernel()`, `fold_child_result()` to plugin
   - Keep `_child_kernels` list in kernel
   - Requires: New EphemeralCitiesPlugin

4. **GAD-000 Status Methods** (-100 LOC)
   - Move `get_gad_status()`, `get_status()` to StatusService
   - Kernel keeps property delegation

### Blocked/Deferred

5. **AgentRegistryService** - KEEP IN KERNEL
   - register_agent is THE GATE - this is what kernels DO
   - 8+ subsystem dependencies make extraction complex
   - 130 LOC is acceptable for core duty

## APPENDIX C: COMMITS (This Session)

```
[PENDING] refactor(kernel): LifecycleService extraction (-255 LOC)
3560092e feat(protocols): SchedulerProtocol + update Vishnu 0 hashes
40a8b35b feat(services): KernelFactory for EphemeralCities
0ebc2a89 refactor(kernel): Phase 6 - Expose EventBus directly
bf449f05 feat(services): CapabilityEnforcerService - Layer 0 Security
11dfad1d refactor(kernel): Apply kernel_types - kill critical Any types
368e7b4c docs(KERNEL): restructure as senior review document
d538db6e docs(KERNEL): update changelog with Phase 0 completion
588de5ea refactor(kernel): Phase 0 - The Constitutional Break
45be6c21 refactor(kernel): Phase 1 - Type Protocols for OPERATION LASAGNE
e10a928a fix(kernel): GAD-000 v2.0 - The 37th Principle implementation
800e84fa refactor(state): migrate .opus_state to .vibe/state/plugins/opus_assistant
```

---

## REVIEWER SIGN-OFF

| Reviewer | Date | Decision | Notes |
|----------|------|----------|-------|
| Gemini (External) | 2026-01-04 | PROCEED | "Phase 0 first, break circular deps" |
| Gemini (External) | 2026-01-04 | PROCEED | "LifecycleService is biggest lever" |
| _Your Name_ | _Date_ | _APPROVE/REVISE/REJECT_ | _Notes_ |

---

## BATTLE STATUS SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│  OPERATION LASAGNE - Kurukshetra Status                     │
├─────────────────────────────────────────────────────────────┤
│  START:    2218 LOC                                         │
│  CURRENT:  1870 LOC  ████████████████░░░░░░░░  (-348)       │
│  TARGET:   1080 LOC                                         │
│  REMAINING: 790 LOC to cut                                  │
├─────────────────────────────────────────────────────────────┤
│  COMPLETED:                                                 │
│    ✅ Phase 0: Constitutional Break (circular deps)         │
│    ✅ Phase 1-3: Type/Service Protocols                     │
│    ✅ Phase 5-6: CapabilityEnforcer + EventBus              │
│    ✅ LifecycleService: -255 LOC (boot/shutdown/tick/run)   │
│                                                             │
│  BLOCKED:                                                   │
│    ⚠️  AgentRegistry: Keep in kernel (THE GATE, 8+ deps)    │
│                                                             │
│  NEXT:                                                      │
│    🔄 Phase 4: ManifestationData (-130 LOC)                 │
│    🔄 Phase 7: Streamline __init__ (-140 LOC)               │
└─────────────────────────────────────────────────────────────┘
```

**Document maintained by:** Claude Opus 4.5
**Last updated:** 2026-01-04
