# OPUS-209: STATE & KERNEL UNIFICATION (Das Große Aufräumen)

> **Status**: DRAFT
> **Date**: 2025-12-22
> **Author**: Claude Opus 4.5 (Senior Architecture Review)
> **Depends On**: OPUS-203, OPUS-206, OPUS-024
> **Blocks**: All new feature work until Priority 1 complete

---

## Executive Summary

The kernel is a **2062 LOC monolith** with:
- **21 direct instantiations** in `__init__`
- **68 methods**
- **Concrete class imports** instead of interfaces
- **Imports from cartridges** (circular dependency!)

The state layer (Prakriti/StateService/Weaver) has:
- **Circular dependencies**
- **3+ git commit paths**
- **Dead code**
- **God object anti-pattern**

This ADR defines the surgical extraction plan to make both:
1. **Kernel**: Minimal, interface-only, never touched again
2. **State**: Single authority, no circular deps, clean

---

## Part A: KERNEL EXTRACTION

### Current State (The Problem)

```python
# kernel_impl.py:__init__ - 21 DIRECT INSTANTIATIONS!

self._scheduler = InMemoryScheduler()           # 1. Concrete!
self.__ledger = InMemoryLedger()                # 2. Concrete!
self.__ledger = SQLiteLedger(ledger_path)       # 3. Concrete!
self._manifest_registry = InMemoryManifestRegistry()  # 4. Concrete!
self._auditor = get_judge()                     # 5. FROM CARTRIDGE!
self.process_manager = ProcessManager()        # 6. Should be plugin
self.resource_manager = ResourceManager()      # 7. Should be plugin
self.network = KernelNetworkProxy(kernel=self) # 8. Should be plugin
self.lineage = LineageChain(db_path=...)       # 9. Should be plugin
self.trace = UnifiedTrace()                    # 10. Should be plugin
self.prakriti = Prakriti(db_path=...)          # 11. GOD OBJECT!
self.__capability_registry = CapabilityRegistry(...)  # 12. Core, keep
self.io = KernelIOService(self)                # 13. Should be plugin
self._narasimha = get_narasimha()              # 14. Singleton
self._event_bus = get_event_bus()              # 15. Singleton
self._unified_router, self._unified_executor = create_unified_runtime(self)  # 16,17
self._plugins_map, ... = PluginLoader.discover_and_load(...)  # 18
self.gateway = NetworkGateway(self.prakriti)   # 19. SHOULD BE PLUGIN!
self._bank = CivicBank(...)                    # 20. FROM CARTRIDGE!
self._vault = CivicVault(...)                  # 21. FROM CARTRIDGE!
```

### Target State (The Goal)

**VISHNU KERNEL: 1008 LOC Maximum** (Symbolic: Vishnu's 1008 Names)

```python
class VisnuKernel:
    """
    The Eternal Kernel. Never touched again after stabilization.

    ONLY responsibilities:
    1. Event Loop (tick, run_forever)
    2. Agent Registry (register, lookup)
    3. Task Queue (submit, next)
    4. Plugin Lifecycle (boot, shutdown)
    5. Event Bus (subscribe, emit)

    EVERYTHING ELSE is a Plugin or Injected.
    """

    def __init__(
        self,
        # ALL DEPENDENCIES INJECTED
        ledger: VibeLedger,              # Interface, not concrete
        scheduler: VibeScheduler,         # Interface, not concrete
        event_bus: EventBus,              # Interface, not concrete
        plugin_loader: PluginLoaderProtocol,
    ):
        # NO direct instantiations!
        self._ledger = ledger
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._plugin_loader = plugin_loader

        # Core state only
        self._agent_registry: Dict[str, VibeAgent] = {}
        self._plugins: List[KernelPlugin] = []
        self._status = KernelStatus.STOPPED
```

### Extraction Plan

| Current Component | Target Location | Priority |
|-------------------|-----------------|----------|
| `ProcessManager` | Plugin: `process_isolation` | P1 |
| `ResourceManager` | Plugin: `resource_limits` | P1 |
| `LineageChain` | Plugin: `parampara` | P2 |
| `NetworkGateway` | Plugin: `sangha_network` | P1 |
| `KernelIOService` | Plugin: `io_service` | P2 |
| `UnifiedTrace` | Plugin: `telemetry` | P2 |
| `Prakriti` | **Injected** (not plugin) | P0 |
| `get_judge()` | Plugin: `auditor` | P1 |
| `CivicBank/Vault` | Plugin: `economy` | P2 |
| `QuantumReactor` | Plugin: `resonance` | P3 |

### New Interface Contracts

```python
# vibe_core/protocols/ledger.py (exists, extend)
class VibeLedger(Protocol):
    def record_event(self, event_type: str, agent_id: str, details: dict) -> str: ...
    def count_events(self) -> int: ...
    def get_top_hash(self) -> str: ...
    # NEW: Factory method for DI
    @classmethod
    def create(cls, path: str) -> "VibeLedger": ...

# vibe_core/protocols/scheduler.py (NEW)
class VibeScheduler(Protocol):
    def submit_task(self, task: Task) -> str: ...
    def next_task(self) -> Optional[Task]: ...
    def get_queue_status(self) -> Dict[str, int]: ...

# vibe_core/protocols/event_bus.py (NEW)
class EventBusProtocol(Protocol):
    def subscribe(self, callback: Callable, event_type: Optional[str] = None) -> str: ...
    def emit(self, event: Event) -> Awaitable[None]: ...
    def unsubscribe(self, callback: Callable) -> None: ...
```

### `register_agent` Decomposition

Current: 143 lines, 12 responsibilities

Target: 20 lines, 2 responsibilities (register + notify)

```python
def register_agent(self, agent: VibeAgent) -> None:
    """Register agent. Everything else via Plugin hooks."""

    # 1. GOVERNANCE GATE (plugins decide)
    for plugin in self._plugins:
        if not plugin.on_agent_pre_register(self, agent):
            raise PermissionError(f"Registration denied by {plugin.plugin_id}")

    # 2. CORE REGISTRATION (the only thing kernel does)
    self._agent_registry[agent.agent_id] = agent
    agent.set_kernel(self)

    # 3. NOTIFY PLUGINS (they do the rest)
    for plugin in self._plugins:
        plugin.on_agent_registered(self, agent)

    # That's it. 20 lines. Everything else is plugin responsibility:
    # - Process spawning: ProcessIsolationPlugin
    # - Resource quotas: ResourceLimitsPlugin
    # - Lineage recording: ParamparaPlugin
    # - Persona creation: PrakritiPlugin
    # - Capability registration: CapabilityPlugin
```

---

## Part B: STATE UNIFICATION

### Current State (OPUS-206 Findings)

```
Prakriti                    ← God Object (7 sub-managers)
  ├── GitState
  ├── FileState
  ├── LedgerState
  ├── MachineState
  ├── KernelState
  ├── EphemeralState
  └── PersonaManager

StateService                ← Circular Dependencies
  ├── _commit_via_git()     ← --no-verify bypass!
  ├── _commit_via_weaver()  ← creates new Prakriti()!
  └── 3+ commit paths       ← CHAOS

Weaver                      ← Dead Oracle Code
  └── _consult_oracle()     ← Never called (manas_oracle=None)
```

### Target State

```
CommitAuthority (NEW)       ← SINGLE way to commit
  └── commit()              ← One path, always hooks

Prakriti (FACADE)           ← Delegates to managers
  ├── git: GitManager       ← Only git ops
  ├── files: FileManager    ← Only file ops
  ├── ledger: LedgerManager ← Only ledger ops
  └── session: SessionManager ← Only session ops

StateService                ← Uses CommitAuthority
  └── _commit()             ← Calls CommitAuthority.commit()

Weaver                      ← Oracle code REMOVED
```

### Priority 1 Fixes (Do First)

#### Fix 1: StateService Circular Dependency

```python
# BEFORE (state_service.py:651-663)
def _commit_via_weaver(self) -> bool:
    from .prakriti import Prakriti          # Creates new!
    prakriti = Prakriti(self.workspace)     # Every time!
    weaver = get_state_sync_weaver(prakriti)
    return weaver.pulse()

# AFTER
def _commit_via_weaver(self) -> bool:
    weaver = get_state_sync_weaver()  # Use existing singleton
    if weaver is None:
        return False
    return weaver.pulse()
```

#### Fix 2: Remove Dead Oracle Code

```python
# DELETE entirely (weaver.py:229-260)
def _consult_oracle(self, classified: ClassifiedState) -> WeavingAdvice:
    # manas_oracle is NEVER set - this code never runs
    ...
```

#### Fix 3: Single Commit Authority

```python
# NEW FILE: vibe_core/commit_authority.py
import threading
import os
import subprocess
from pathlib import Path
from typing import List, Optional

class CommitAuthority:
    """
    THE ONLY WAY TO COMMIT. Period.

    All git commits in the entire codebase MUST go through here.
    This ensures:
    1. Single locking mechanism
    2. Consistent hook behavior
    3. Audit trail
    4. Environment variable respect
    """

    _lock = threading.Lock()

    @classmethod
    def commit(
        cls,
        files: List[Path],
        message: str,
        author: str = "kernel",
        no_verify: bool = False,  # DANGEROUS - requires explicit opt-in
    ) -> bool:
        """
        Commit files atomically.

        Args:
            files: Files to stage and commit
            message: Commit message
            author: Who is committing (for audit)
            no_verify: Skip hooks (DANGEROUS - logged!)

        Returns:
            True if committed, False if skipped/failed
        """
        with cls._lock:
            # Check environment
            if os.environ.get("VIBE_NO_GIT_COMMIT") == "1":
                logger.info(f"[COMMIT_AUTHORITY] Skipped (VIBE_NO_GIT_COMMIT=1)")
                return False

            # Log dangerous operations
            if no_verify:
                logger.warning(f"[COMMIT_AUTHORITY] --no-verify used by {author}!")

            # Stage files
            for f in files:
                subprocess.run(["git", "add", str(f)], check=True)

            # Commit
            cmd = ["git", "commit", "-m", message]
            if no_verify:
                cmd.append("--no-verify")

            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                logger.info(f"[COMMIT_AUTHORITY] Committed by {author}: {message[:50]}")
                return True
            else:
                logger.error(f"[COMMIT_AUTHORITY] Failed: {result.stderr.decode()}")
                return False
```

---

## Part C: DEPENDENCY INJECTION CONTAINER

### The Problem

Multiple singleton patterns, each different:
- `StateService`: Dict registry `_instances`
- `Weaver`: Global variable `_global_weaver`
- `EventBus`: Multiple patterns
- `CycleRegistry`: Global variable

### The Solution

```python
# NEW FILE: vibe_core/di.py
from typing import TypeVar, Type, Dict, Any, Optional
import threading

T = TypeVar('T')

class ServiceRegistry:
    """
    Centralized Dependency Injection Container.

    Replaces all ad-hoc singleton patterns with one consistent mechanism.

    Usage:
        # Register
        ServiceRegistry.register(VibeLedger, SQLiteLedger(path))

        # Resolve
        ledger = ServiceRegistry.get(VibeLedger)

        # Testing - reset all
        ServiceRegistry.reset()
    """

    _services: Dict[str, Any] = {}
    _factories: Dict[str, callable] = {}
    _lock = threading.Lock()

    @classmethod
    def register(cls, interface: Type[T], instance: T) -> None:
        """Register a service instance."""
        with cls._lock:
            cls._services[interface.__name__] = instance

    @classmethod
    def register_factory(cls, interface: Type[T], factory: callable) -> None:
        """Register a factory for lazy instantiation."""
        with cls._lock:
            cls._factories[interface.__name__] = factory

    @classmethod
    def get(cls, interface: Type[T]) -> Optional[T]:
        """Get a service by interface type."""
        with cls._lock:
            name = interface.__name__

            # Try instance first
            if name in cls._services:
                return cls._services[name]

            # Try factory
            if name in cls._factories:
                instance = cls._factories[name]()
                cls._services[name] = instance
                return instance

            return None

    @classmethod
    def reset(cls) -> None:
        """Reset all services. FOR TESTING ONLY."""
        with cls._lock:
            cls._services.clear()
            # Keep factories - they can recreate

    @classmethod
    def get_or_raise(cls, interface: Type[T]) -> T:
        """Get service or raise if not registered."""
        service = cls.get(interface)
        if service is None:
            raise RuntimeError(f"Service not registered: {interface.__name__}")
        return service
```

---

## Implementation Phases

### Phase 0: Foundation (Week 1)
- [ ] Create `vibe_core/di.py` (ServiceRegistry)
- [ ] Create `vibe_core/commit_authority.py`
- [ ] Create protocol interfaces in `vibe_core/protocols/`

### Phase 1: State Fixes (Week 2)
- [ ] Fix StateService circular dependency (OPUS-206 #1)
- [ ] Remove dead Oracle code (OPUS-206 #3)
- [ ] Migrate all commit paths to CommitAuthority
- [ ] Remove `--no-verify` from StateService

### Phase 2: Kernel Extraction (Week 3-4)
- [ ] Extract `ProcessManager` to plugin
- [ ] Extract `ResourceManager` to plugin
- [ ] Extract `NetworkGateway` to plugin
- [ ] Extract `get_judge()` to plugin
- [ ] Remove cartridge imports from kernel

### Phase 3: Kernel Slimming (Week 5)
- [ ] Refactor `register_agent` to 20 lines
- [ ] Inject Prakriti instead of instantiate
- [ ] Inject Ledger via interface
- [ ] Inject Scheduler via interface
- [ ] Inject EventBus via interface

### Phase 4: Stabilization (Week 6)
- [ ] Update kernel hashes (OPUS-024)
- [ ] Full test suite pass
- [ ] Documentation update
- [ ] VISNU Protection verification

---

## Success Criteria

### Kernel Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Lines of Code | 2062 | ≤1008 |
| Direct Instantiations | 21 | 0 |
| Methods | 68 | ≤25 |
| Concrete Imports | 15+ | 0 |
| Cartridge Imports | 3 | 0 |

### State Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Git Commit Paths | 3+ | 1 |
| Circular Dependencies | 1 | 0 |
| Dead Code Lines | ~50 | 0 |
| Singleton Patterns | 5 | 1 (ServiceRegistry) |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing plugins | Keep backward compat aliases for 1 release |
| VISNU Protection blocks changes | Coordinate with Senior for hash updates |
| Test suite breaks | Run incrementally, fix as we go |
| Performance regression | Benchmark before/after each phase |

---

## Appendix: Files to Modify

### Kernel (VISNU Protected)
- `vibe_core/kernel_impl.py` - Major refactor
- `vibe_core/kernel_ops.py` - Move to plugins

### State (Not Protected)
- `vibe_core/state/state_service.py` - Fix circular dep
- `vibe_core/state/weaver.py` - Remove dead code
- `vibe_core/state/prakriti.py` - Decompose god object

### New Files
- `vibe_core/di.py` - ServiceRegistry
- `vibe_core/commit_authority.py` - Single commit path
- `vibe_core/protocols/scheduler.py` - Scheduler interface
- `vibe_core/protocols/event_bus.py` - EventBus interface
- `vibe_core/plugins/process_isolation/` - Extracted plugin
- `vibe_core/plugins/resource_limits/` - Extracted plugin
- `vibe_core/plugins/sangha_network/` - Extracted plugin

---

## Approval Checklist

- [x] Problem clearly identified
- [x] Solution designed with interfaces
- [x] Implementation phases defined
- [x] Success metrics established
- [x] Risks documented
- [ ] Human Senior Review
- [ ] Implementation started
- [ ] All phases complete

**Status: READY FOR REVIEW**
