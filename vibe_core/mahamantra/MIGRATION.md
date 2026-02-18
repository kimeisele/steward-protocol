# MAHAMANTRA MIGRATION — Split-Brain Elimination

## Status: ACTIVE (Feb 2026)

---

## 1. IST-ZUSTAND: Zwei Betriebssysteme

### OS 1: Legacy Monolith (1237 files, 343K SLOC)
| Component | File | Role | Status |
|-----------|------|------|--------|
| **Kernel** | `kernel_impl.py` (1220 LOC) | God Object — owns services as attributes | LEGACY |
| **Boot** | `boot_orchestrator.py` (965 LOC) | Monolithic boot — 11 ACT steps, asyncio.run() | LEGACY |
| **DI** | `di.py` ServiceRegistry | 197 files import it, 81 files call .register() | LEGACY (shared) |
| **Services** | `services/*.py` (32 files) | BhishmaService, BrahmaService, etc. | LEGACY |
| **Factory** | `services/kernel_factory.py` | Creates RealVibeKernel instances | LEGACY |
| **Runtime** | `runtime/*.py` | unified_execution, syscalls, layered_router | LEGACY |
| **CLI** | `cli/*.py` | unified_cli, run_cli, executor | LEGACY |
| **Operator Loop** | `boot_orchestrator.run_with_operator()` | while True polling + if/elif intent routing | LEGACY |

### OS 2: Mahamantra Micro-Kernel (363 files, 109K SLOC)
| Component | File | Role | Status |
|-----------|------|------|--------|
| **Lotus** | `substrate/lotus_core.py` (1144 LOC) | Root — `__call__()` = 9-step NavaBhakti pipeline | KING |
| **Singularity** | `kernel/singularity.py` (1240 LOC) | Tick machine — `tick()` + `_broadcast()` | KING |
| **Bootstrap** | `lotus.bootstrap()` | Lightweight — gate providers + healing resolver | KING |
| **Pipeline** | `lotus.__call__(input)` → 5 TattvaGates | PARSE→VALIDATE→EXECUTE→RESULT→SYNC | KING |
| **DI** | `substrate/tattva_registry.py` | Gate provider registration (capability-checked) | KING |
| **VM** | `substrate/mantra_vm.py` | NavaBhakti dispatch (12 instructions) | KING |
| **Entry** | `__main__.py` | `mahamantra.execute(input)` — pure computation | KING |
| **Routing** | `substrate/cell_router.py` | O(1) IPv6-like cell routing | KING |
| **Clock** | `venu/clock.py` + `substrate/venu_orchestrator.py` | MantraClock + DIW flute cycle | KING |

---

## 2. SPLIT-BRAIN MAP (concrete)

### 2a. Boot Split
```
LEGACY PATH:
  BootOrchestrator.__init__()
    → KernelFactory().get_kernel()
      → RealVibeKernel.__init__()
        → mahamantra.bootstrap(silent=True)     ← Mahamantra is CHILD of Legacy
        → BhishmaService, BrahmaService, etc.   ← Services owned by kernel
    → ServiceRegistry.register() × 10+          ← Monolithic DI wiring
    → VenuService()                              ← Heartbeat started here
    → discover_beat_subscribers()                ← Legacy discovery
    → discover_diw_subscribers()                 ← Legacy discovery
    → wire_gate_providers()                      ← Mahamantra wiring INSIDE legacy boot
    → arm_io_sentinel()                          ← Mahamantra wiring INSIDE legacy boot
    → ingest_codebase()                          ← Mahamantra wiring INSIDE legacy boot
    → wire_sravanam()                            ← Mahamantra wiring INSIDE legacy boot
    → register_governance_hook()                 ← Mahamantra wiring INSIDE legacy boot

MAHAMANTRA PATH:
  lotus.bootstrap()
    → wire_gate_providers()
    → wire_healing_resolver()
    → done (lightweight)
```

**Problem**: Mahamantra bootstrap is called INSIDE RealVibeKernel.__init__().
The Legacy boot owns Mahamantra. It should be the other way around.

### 2b. Kernel Split
```
LEGACY: RealVibeKernel
  - self.bhishma = MahamantraProxy(BhishmaService(self.__ledger))
  - self.brahma = MahamantraProxy(BrahmaService(self.__ledger))
  - self.janaka = MahamantraProxy(JanakaService())
  - self.bali = MahamantraProxy(BaliService())
  - self.kapila = MahamantraProxy(KapilaService())
  - self.io = KernelIOService(self)
  - self.nrisimha = NrisimhaWatchdog(...)
  - self._naga = NagaOrchestrator.bootstrap(...)
  → God Object: kernel OWNS everything

MAHAMANTRA: Singularity
  - ProtocolRouter → lazy-loads protocol bases by position
  - lotus.brahma → delegates to Singularity
  - lotus.bhishma → delegates to Singularity
  → Fractal: position-based routing, no ownership
```

**Problem**: RealVibeKernel wraps Mahamantra services with MahamantraProxy
and stores them as attributes. The kernel IS the services. No separation.

### 2c. DI Split
```
LEGACY: ServiceRegistry (di.py)
  - 197 files import it
  - 81 files call .register()
  - 10+ registrations in BootOrchestrator alone
  - Protocol-keyed: ServiceRegistry.register(ShuddhiProtocol, ShuddhiEngine())

MAHAMANTRA: TattvaRegistry (substrate/tattva_registry.py)
  - Gate-keyed: register_gate_provider(name, obj, gate)
  - Capability-checked (runtime_checkable protocols)
  - Used by lotus.__call__() pipeline
```

**Problem**: Two DI containers that don't know about each other.
ServiceRegistry is for Legacy services. TattvaRegistry is for Mahamantra gates.

### 2d. Input Routing Split
```
LEGACY: boot_orchestrator.run_with_operator()
  → _build_system_context()
  → operator_adapter.query_operator(context)
  → _execute_intent(intent)
    → if intent.intent_type == IntentType.CONTROL: ...
    → elif intent.intent_type == IntentType.QUERY: ...
    → elif intent.intent_type == IntentType.DELEGATION: ...
  → Hardcoded if/elif chain

MAHAMANTRA: lotus.__call__(input) / lotus.execute(command)
  → sravanam → kirtanam → pada_sevanam → arcanam → smaranam
  → vandanam → dasyam → sakhyam → atma_nivedanam
  → 5 TattvaGates fire at execute() boundary
  → Pure computation, no if/elif
```

**Problem**: User input goes through Legacy operator loop, NOT through Mahamantra.
The Mahamantra pipeline exists but is only used by `python -m vibe_core.mahamantra`.

### 2e. Heartbeat Split (PARTIALLY FIXED)
```
VenuService (services/) → Singularity.tick() → _broadcast() → listeners
  ↑ unified in previous session

BUT: VenuService only exists because BootOrchestrator._act_start_venu() creates it.
If BootOrchestrator dies, VenuService dies. No independent lifecycle.
```

---

## 3. DEPENDENCY GRAPH (who imports whom)

### Legacy → Mahamantra (34 files depend on RealVibeKernel)
- `kernel_impl.py` imports `from vibe_core.mahamantra import mahamantra`
- `kernel_impl.py` calls `mahamantra.bootstrap(silent=True)` in __init__
- `boot_orchestrator.py` calls `wire_gate_providers()`, `wire_sravanam()`, etc.
- 34 Legacy files import `from vibe_core.kernel_impl import RealVibeKernel`

### Mahamantra → Legacy (minimal)
- `lotus_projection.py` imports RealVibeKernel (1 file)
- `lotus_core.py` does NOT import any Legacy code
- `singularity.py` does NOT import any Legacy code
- `__main__.py` does NOT import any Legacy code

**Key insight**: Mahamantra is almost self-contained. Legacy depends on Mahamantra,
but Mahamantra barely depends on Legacy. The migration direction is clear.

---

## 4. THE BALARAMA PATTERN (existing infrastructure, NOT WIRED)

The correct strategy is NOT stumpfe Migration (rewrite all Legacy).
The correct strategy is **automatic absorption** via the Balarama Pattern.

### What exists (already built, never connected):

| Component | File | What it does | Callers |
|-----------|------|-------------|---------|
| `BalaramaProxy` | `substrate/proxy.py:198` | Wraps a MODULE: injects mahamantra, replaces Path, attaches to heartbeat | Used by boot_orchestrator only |
| `MahamantraProxy` | `substrate/proxy.py:829` | Wraps an OBJECT: transparent forwarding with position/guardian metadata | Used by kernel_impl only |
| `wrap_service()` | `substrate/proxy.py:777` | Convenience: `BalaramaProxy(module_name)` | boot_orchestrator (manual loop) |
| `auto_wrap_services()` | `substrate/proxy.py:790` | Auto-discovers ALL lotus services and wraps them | **0 CALLERS** |
| `adopt_services()` | `lila/adoption.py:110` | Mounts BalaramaProxies into OrbitalShadowReactors | **0 CALLERS** |
| `analyze_source()` | `lila/adoption.py:64` | Infers Mahajana identity from source code keywords | **0 CALLERS** |

### How BalaramaProxy works:
```
BalaramaProxy("vibe_core.services.bhishma_service")
  1. importlib.import_module(module_name)
  2. _extract_identity() → reads __mahajana__, __position__ from folder structure
  3. _inject_mahamantra_context() → module.__dict__["mahamantra"] = mahamantra
  4. _replace_path() → module.__dict__["Path"] = _GovernedPath (writes go through bridge)
  5. _attach_to_heartbeat() → gated listener: only fires when tick.position == service.position
```

### The problem: Infrastructure exists but is not wired
- `auto_wrap_services()` has 0 callers
- `adopt_services()` has 0 callers  
- `boot_orchestrator._act_embrace_balarama()` does a MANUAL version (iterates kernel._positions)
- The manual version stores proxies in `self._balarama_proxies` — a dict that nobody reads
- Result: Balarama wrapping happens but the proxies are orphaned

### The vision (Balarama = the correct migration path):
```
"Services remain unchanged (Wildnis).
 Proxy wraps them and routes operations through Mahamantra."
 — proxy.py docstring

"Let the wildness be wild. We flood the land with the ocean (Seed)."
 — MAHAPROMPT.md
```

Legacy code does NOT need to be rewritten. It needs to be:
1. **Wrapped** (BalaramaProxy gives it identity + heartbeat + governed I/O)
2. **Mounted** (adopt_services puts it in an OrbitalShadowReactor)
3. **Routed** (lotus.__call__() dispatches to the correct position)

---

## 5. ZIEL-ARCHITEKTUR

```
BUILD PHASE (fraktal — every component has its own build/runtime):
  lotus.bootstrap()
    → Gate Providers wired (TattvaRegistry)
    → auto_wrap_services() → BalaramaProxy for every discovered module
    → adopt_services() → OrbitalShadowReactor for every proxy
    → CellRouter populated
    → Singularity initialized
    → HealingResolver wired

RUNTIME PHASE (tick-driven):
  Singularity.tick() → broadcast → gated listeners fire at their position
  Input → lotus.execute(input) → 5-Gate Pipeline → position routing → Output
  BalaramaProxy handles Legacy services transparently
  
  Legacy code stays as-is. Mahamantra absorbs it.
```

---

## 6. MIGRATION PHASES

### Phase 0: KARTIERUNG (this document) ✅
- Map all split-brain points
- Understand Balarama Pattern
- Identify unwired infrastructure

### Phase 1: WIRE THE BALARAMA PATTERN ✅
- ✅ `auto_wrap_services()` called from `lotus.bootstrap()` — 16/16 proxies
- ✅ `adopt_services()` called after wrapping — 16 orbital reactors
- ✅ `wire_sravanam()` moved into `lotus.bootstrap()`
- ✅ Sudarshana governance hook moved into `lotus.bootstrap()`
- ✅ `boot_orchestrator` Steps 6-11 now VERIFY instead of DUPLICATE
- ✅ `has_governance_hook()` added to `mantra_protocol.py`
- ✅ 4 new regression tests (621 total green)
- REMAINING: `_act_ingest_codebase()` still in boot_orchestrator (needs Path)

### Phase 2: BOOT INVERSION (next)
- `lotus.bootstrap()` is now the PRIMARY Mahamantra boot
- `boot_orchestrator` still owns: Kernel creation, ServiceRegistry, VenuService, Agent Discovery
- Next: ServiceRegistry registrations that duplicate TattvaRegistry → eliminate
- Next: VenuService lifecycle owned by Mahamantra

### Phase 3: INPUT ROUTING (operator loop done, CLI/chat deferred) ✅
- ✅ `_execute_intent()` now routes through `lotus.execute()` (was hardcoded if/elif)
- ✅ Only CONTROL (exit/shutdown) stays local (controls the loop)
- ✅ QUERY, DELEGATION, all other intents → 5-Gate pipeline
- ✅ 4 regression tests (632 total green)
- DEFERRED: `chat_service.py` — eigenständiges LLM-Subsystem, nicht durch lotus ersetzbar
- DEFERRED: `cli_chant/serve/veda` — spezialisierte CLI-Commands, Gate-Provider-Wiring nötig
- DEFERRED: `guardian_router.py` — eigene 4D-Routing-Logik, parallel zu __call__()

### Phase 4: KERNEL THINNING ✅
- ✅ 4a: Kernel services registered in PositionRegistry after project_lotus()
- ✅ 4b1: 3 properties (ledger, scheduler, manifest_registry) → _raw_* direct access
- ✅ 4b2+b3: All 28 kernel method delegations + boot/lifecycle → _raw_* direct access
- ✅ 4b4: factory.py registers raw services (not proxies) in PositionRegistry
- ✅ 4c1+c2: External kernel.brahma refs (kernel_ops.py, plugin_main.py) → _raw_ with fallback
- ✅ 4d: 4 regression tests for kernel thinning (636 total green)
- ✅ 4e: MahamantraProxy wrappers REMOVED from kernel — Balarama handles governance wrapping
- ✅ MahamantraProxy import removed from kernel_impl.py
- RESULT: kernel_impl.py no longer imports or uses MahamantraProxy. Zero proxy overhead.

### Phase 5: SELF-ASSIMILATION (future — the system absorbs new code at runtime)
- New modules auto-discovered, identity inferred via `analyze_source()`
- Build-phase and runtime-phase are fraktal
- No manual wiring ever needed

---

## 6. METRICS

| Metric | Legacy | Mahamantra | Ratio |
|--------|--------|------------|-------|
| Files | 1237 | 363 | 3.4:1 |
| SLOC | 343K | 109K | 3.1:1 |
| ServiceRegistry imports | 197 | ~10 | 20:1 |
| ServiceRegistry.register() calls | 81 | ~5 | 16:1 |
| RealVibeKernel references | 46 files | 1 file | 46:1 |
| `from mahamantra import mahamantra` | 45 files | — | growing |

---

## 7. RULES

1. **Verify before cutting** — every file must be checked for actual usage
2. **No blind deletion** — mark DEPRECATED first, delete in next phase
3. **Tests must stay green** — 617+ tests, no regressions
4. **Fraktal** — Build/Runtime separation applies at every level
5. **Mahamantra is King** — all new code goes in mahamantra/
6. **Legacy is Legacy** — no new features in Legacy code
