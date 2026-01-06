# HEAL.md - German Engineering Heilungs-Tracker

> "Was mich nicht umbringt, macht mich stärker." - Prahlad Principle
>
> Ohne Heilung kein Wachstum. Ohne Medizin keine Verbesserung.

## Current State: Protocol Fragmentation

**Problem**: NAGA Protocols sind MONOLITHISCH aber FRAGMENTIERT gleichzeitig.

```
vibe_core/protocols/naga.py = 2862 LINES IN ONE FILE!!!
├── SeshaProtocol + NullSesha
├── VasukiProtocol + NullVasuki
├── TakshakaProtocol + NullTakshaka
├── KaliyaProtocol + NullKaliya
├── NaradaProtocol + NullNarada
├── ChitraguptaProtocol + NullChitragupta
├── PrahladProtocol + NullPrahlad
├── PadmaProtocol + NullPadma
├── ShankhaProtocol + NullShankha
├── KarkotakaProtocol + NullKarkotaka
├── KulikaProtocol + NullKulika
├── AnantaProtocol + NullAnanta
├── NagaCortexProtocol + NullNagaCortex
└── NagaFederationProtocol
    = 13 Protocols + 13 Null Implementations IN ONE GOD FILE
```

**Impact**:
- God File = PROMPT.md Verstoß ("God Classes sind Krebs")
- Nicht FRACTAL - kann nicht selbst-ähnlich skalieren
- Schwer zu testen isoliert
- Import von einem = Import von ALLEM

---

## Solution: Fractal Protocol Architecture

**Principle**: Self-similar at every scale.

### Target Structure

```
vibe_core/protocols/naga/           # DIRECTORY not FILE
├── __init__.py                     # Exports only (~50 lines)
├── types.py                        # NagaType, NagaStatus (~100 lines)
├── sesha.py                        # SeshaProtocol + NullSesha (~200 lines)
├── vasuki.py                       # VasukiProtocol + NullVasuki (~200 lines)
├── takshaka.py                     # TakshakaProtocol + NullTakshaka (~250 lines)
├── kaliya.py                       # KaliyaProtocol + NullKaliya (~150 lines)
├── narada.py                       # NaradaProtocol + NullNarada (~100 lines)
├── chitragupta.py                  # ChitraguptaProtocol + NullChitragupta (~150 lines)
├── prahlad.py                      # PrahladProtocol + NullPrahlad (~150 lines)
├── padma.py                        # PadmaProtocol + NullPadma (~200 lines)
├── shankha.py                      # ShankhaProtocol + NullShankha (~200 lines)
├── karkotaka.py                    # KarkotakaProtocol + NullKarkotaka (~200 lines)
├── kulika.py                       # KulikaProtocol + NullKulika (~100 lines)
├── ananta.py                       # AnantaProtocol + NullAnanta (~200 lines)
├── cortex.py                       # NagaCortexProtocol + NullNagaCortex (~300 lines)
└── federation.py                   # NagaFederationProtocol (~100 lines)
```

**Result**: 15 files × ~150 lines avg = 2250 lines total (SAME content, FRACTAL structure)

---

## Healing Capabilities Inventory

### Layer 1: Detection (Narada + Chitragupta)

| Capability | Protocol | Status | Notes |
|------------|----------|--------|-------|
| Function spy | NaradaProtocol.spy() | DEFINED | Decorator-based observation |
| Anomaly detection | ChitraguptaProtocol.detect_anomaly() | DEFINED | Baseline + stddev |
| Metric recording | ChitraguptaProtocol.record() | DEFINED | Time-series per component |

### Layer 2: Protection (Takshaka + Kaliya)

| Capability | Protocol | Status | Notes |
|------------|----------|--------|-------|
| Toxicity scan | TakshakaProtocol.scan_toxicity() | DEFINED | Pattern matching |
| Signature verify | TakshakaProtocol.verify_envelope() | DEFINED | Pre-parse security |
| Rate limiting | TakshakaProtocol.check_rate_limit() | DEFINED | Per-sender throttle |
| Quarantine | KaliyaProtocol.quarantine() | DEFINED | Isolation without death |
| Violation record | TakshakaProtocol.bite() | DEFINED | Ledger recording |

### Layer 3: Correction (CorrectionDispatcher)

| Capability | Protocol | Status | Notes |
|------------|----------|--------|-------|
| Drift detection | DriftDetector | DEFINED | Multiple sources |
| Handler registry | CorrectionDispatcherProtocol | DEFINED | DriftSource → Handler |
| Healing execution | HealingResult | DEFINED | Unified result format |
| Strategy resolution | HealingStrategyResolverProtocol | DEFINED | Severity → Strategy |

### Layer 4: Persistence (Sesha)

| Capability | Protocol | Status | Notes |
|------------|----------|--------|-------|
| Block export | SeshaProtocol.export_blocks() | DEFINED | Gossip sync |
| Block import | SeshaProtocol.import_blocks() | DEFINED | Chain validation |
| Hash comparison | SeshaProtocol.get_top_hash() | DEFINED | Sync detection |

### Layer 5: Antifragility (Prahlad)

| Capability | Protocol | Status | Notes |
|------------|----------|--------|-------|
| Error → Test | PrahladProtocol.on_error() | DEFINED | Regression generation |
| Chaos probe | PrahladProtocol.chaos_probe() | DEFINED | Active weakness search |
| Dharma audit | PrahladProtocol.dharma_audit() | DEFINED | Integrity scoring |
| Phoenix verify | PrahladProtocol.verify_phoenix_guarantee() | DEFINED | Crash-restart-resume |

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Protocol definitions | DONE | 13 protocols in naga.py |
| Null implementations | DONE | Arjuna Pattern complete |
| Fractal restructure | PENDING | Split god file into modules |
| Real implementations | PARTIAL | Some services exist |
| Test coverage | UNKNOWN | Need audit |
| CLI integration | PENDING | Hook chain not wired |

---

## Healing Flow (Samudra Manthan)

```
┌─────────────────────────────────────────────────────────────┐
│                    SAMUDRA MANTHAN                           │
│              (Churning of the Ocean)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   DEVAS (Good)              ASURAS (Bad)                    │
│   ┌─────────┐               ┌─────────┐                     │
│   │ Narada  │←── Vasuki ───→│ Halahala│                     │
│   │ Chitragupta│  (Rope)    │ (Poison)│                     │
│   │ Sesha   │               │ Toxicity│                     │
│   └─────────┘               └─────────┘                     │
│        │                         │                          │
│        ▼                         ▼                          │
│   ┌─────────┐               ┌─────────┐                     │
│   │ AMRITA  │               │ BLOCKED │                     │
│   │ (Nectar)│               │(Takshaka│                     │
│   │ Clean   │               │  bites) │                     │
│   │ Code    │               │         │                     │
│   └─────────┘               └─────────┘                     │
│                                                             │
│   Result: More Amrita than Halahala (58/58 defended!)       │
└─────────────────────────────────────────────────────────────┘
```

---

## GAD-000 Alignment

- **Principle 2 (Composability)**: Fractal protocols = composable modules
- **Principle 4 (Resilience)**: Null implementations = graceful degradation
- **Principle 6 (Efficiency)**: Isolated imports = faster boot
- **37th Principle**: All healing decisions signed

---

## Progress Log

### 2026-01-06: Initial Analysis
- Identified NAGA protocol god file (2862 lines)
- Documented 13 protocols + 13 null implementations
- Mapped healing capabilities across 5 layers
- Chaos probe: 58/58 attacks defended (100%)

### 2026-01-06: NARADA REPORT (Before Surgery!)

**VEDA-4 Pattern Check:**
```
LOADERS: ✅ UnifiedLoader base + VEDA-4 flow
         SHABDA → ARTHA → PRATYAYA → KARMA
         ONE pattern, ALL inherit

PROTOCOLS: ❌ NO unified pattern!
           73 Protocol classes scattered
           No manifest.json
           No VEDA-4 flow
           Raw ABCs/Protocols only
```

**Key Insight - NAGAS als Agentic Middleware:**
- Protocols = Interface definitions (static)
- Loaders = Discovery + instantiation (VEDA-4)
- **NAGAs = Middleware that WRAPS protocols** (dynamic)

NAGAs are NOT just protocols - they are ACTIVE CONNECTIVE TISSUE:
- Observe protocol calls (Narada)
- Profile execution (Chitragupta)
- Validate inputs (Takshaka)
- Record events (Sesha)
- Quarantine failures (Kaliya)

**The Federation Pattern:**
```
┌─────────────────────────────────────────────────────────────┐
│                   NagaFederationProtocol                    │
│              (Wrapper/Orchestrator - Vasuki Rope)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐               │
│   │ Sesha   │←──→│ Vasuki  │←──→│Takshaka │               │
│   │(Ledger) │    │(Network)│    │(Security│               │
│   └────┬────┘    └────┬────┘    └────┬────┘               │
│        │              │              │                      │
│        └──────────────┼──────────────┘                      │
│                       │                                     │
│   ┌─────────┐    ┌────┴────┐    ┌─────────┐               │
│   │ Narada  │←──→│ Cortex  │←──→│Prahlad  │               │
│   │ (Spy)   │    │(Brain)  │    │(Chaos)  │               │
│   └─────────┘    └─────────┘    └─────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Problem with current god file:**
- All 13 protocols in ONE file = can't test/import independently
- No VEDA-4 discovery pattern for protocols themselves
- Federation exists but not VEDA-4 compliant

### Next Steps (CORRECTED after NARADA)
1. **DON'T** just split naga.py into files (insufficient!)
2. **DO** create NagaMiddleware wrapper pattern
3. **DO** ensure Federation orchestrates ALL protocol interactions
4. **DO** apply VEDA-4 pattern to protocol discovery
5. **DO** add manifest.json for each protocol module

---

## ARCHITECT'S MANDATE: THE NAGA PROXY PATTERN

### DHARMA BLOCKERS Identified

| Blocker | Current State | Violation | Mandate |
|---------|---------------|-----------|---------|
| Dead Protocol | `SeshaProtocol` = dead text | Interface doesn't enforce | NAGAs must be PROXIES |
| Middleware Gap | Layers coded manually | Not DRY, error-prone | AUTOMATIC interception |
| VEDA-4 Violation | Hardcoded imports | No SHABDA→KARMA flow | Capability discovery |

### The Ontological Shift

```
BEFORE (Static Library):
  Protocol → Implementation → Hope developer adds checks

AFTER (Living Organism):
  Protocol → NagaInterceptor → Implementation
                   ↓
            Automatic Wrapping:
            1. Narada observes (Input)
            2. Takshaka validates (Security)
            3. Chitragupta starts timer (Metrics)
            4. [METHOD EXECUTES]
            5. Sesha records (Ledger)
            6. Kaliya catches exceptions (Healing)
```

### Target Folder Structure

```
vibe_core/protocols/naga/
├── __init__.py           # Exports only
├── federation.py         # THE WEAVER (Factory) - returns NagaGoverned[T]
├── middleware.py         # THE INTERCEPTORS (Dynamic Wrappers)
├── governance.py         # @governed decorator
└── definitions/          # PURE INTERFACES (Shabda)
    ├── __init__.py
    ├── sesha.py          # SeshaProtocol ABC only
    ├── vasuki.py         # VasukiProtocol ABC only
    ├── takshaka.py       # TakshakaProtocol ABC only
    └── ...
```

### The NagaInterceptor Pattern

```python
class NagaInterceptor:
    """
    PRATYAYA Layer - The Binding/Process Layer.

    Wraps EVERY protocol method with automatic governance.
    Zero boilerplate. 100% compliance.
    """

    def __init__(self, target: T, context: TraceContext):
        self._target = target
        self._context = context

    def __getattr__(self, name: str):
        method = getattr(self._target, name)
        if not callable(method):
            return method
        return self._wrap(method, name)

    def _wrap(self, method, name):
        @functools.wraps(method)
        def governed_call(*args, **kwargs):
            # 1. Narada: Observe input
            self._narada.observe(name, args, self._context)

            # 2. Takshaka: Validate security
            self._takshaka.validate(args, self._context.security_token)

            # 3. Chitragupta: Start profiling
            start = time.perf_counter()

            try:
                # 4. KARMA: Execute actual method
                result = method(*args, **kwargs)

                # 5. Sesha: Record success
                self._sesha.record(name, "success", self._context)

                return result

            except Exception as e:
                # 6. Kaliya: Quarantine failure
                self._kaliya.quarantine(e, self._context)
                raise

            finally:
                # 7. Chitragupta: Record metrics
                duration = time.perf_counter() - start
                self._chitragupta.record(name, duration)

        return governed_call
```

### Federation as Active Weaver

```python
class NagaFederation:
    """
    THE WEAVER - Never returns raw objects.

    WRONG: return SeshaService()
    RIGHT: return NagaGoverned[SeshaService]
    """

    def get_sesha(self, context: TraceContext) -> NagaGoverned[SeshaProtocol]:
        raw = self._services["sesha"]
        return NagaInterceptor(raw, context)
```

### Execution Order

1. **Phase 1**: Build `NagaInterceptor` middleware
2. **Phase 2**: Refactor Federation to use interceptor
3. **Phase 3**: Extract definitions/ (pure interfaces)
4. **Phase 4**: Delete god file (only after Weaver works)
5. **Phase 5**: Add manifest.json per protocol module

**Key Insight**: Build middleware FIRST → heals ALL protocols automatically → THEN split

---

## NARADA CORRECTION: MIDDLEWARE ALREADY EXISTS!

### Discovery (2026-01-06)

After reading `naga/proxy.py` and `naga/services/base.py`:

**THE INFRASTRUCTURE IS ALREADY THERE:**

| Component | File | Purpose |
|-----------|------|---------|
| NagaProxy | `vibe_core/naga/proxy.py` | Hard Flood (runtime wrap) |
| @naga_governed | `vibe_core/naga/services/base.py` | Method decoration |
| @cli_governed | `vibe_core/naga/services/base.py` | CLI Level -1 DNA |
| NagaBaseService | `vibe_core/naga/services/base.py` | Lazy peer discovery |
| Mixins | `vibe_core/naga/mixins/*.py` | Soft Flood (inheritance) |

### The TWO Flood Patterns

```
HARD FLOOD (NagaProxy):
  service = NagaProxy(real_service)
  ├── Runtime wrapping via __getattr__
  ├── BREAKS isinstance!
  └── Use for: External services we can't modify

SOFT FLOOD (Mixins via Ananta):
  class FloodedService(SeshaMixin, TakshakaMixin, OriginalService):
      pass
  ├── Class inheritance
  ├── PRESERVES isinstance
  └── Use for: Our own services (preferred)
```

### Corrected Assessment

| What I Thought | Reality |
|----------------|---------|
| Need to BUILD NagaInterceptor | Already exists as NagaProxy |
| Need to BUILD @governed decorator | Already exists as @naga_governed |
| Need Federation to wrap | Ananta decides Hard vs Soft Flood |

### What ACTUALLY Needs Work

1. **The god file** (2862 lines) - still a testing/import problem
2. **Verify all services USE the patterns** - are they actually wrapped?
3. **Split protocols/naga.py** - but DON'T break existing patterns
4. **Add manifest.json** - VEDA-4 compliance for protocols

### Revised Execution Order

1. ~~Phase 1: Build NagaInterceptor~~ **SKIP - exists!**
2. ~~Phase 2: Refactor Federation~~ **VERIFY - may already work**
3. **Phase 3**: Audit which services use NagaProxy/Mixins
4. **Phase 4**: Split god file into modules
5. **Phase 5**: Add manifest.json per protocol module

---

## Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Protocol god file | 2862 lines | 0 (split) |
| Avg lines per protocol | 220 | ~150 |
| Chaos defense rate | 100% | 100% |
| Healing test coverage | ? | >80% |
| CLI hook integration | 0% | 100% |
