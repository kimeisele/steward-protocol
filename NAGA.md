# NAGA.md - KURUKSHETRA BATTLEPLAN

> "Wie Wasser in jede Ritze" - ASHVAMEDHA
> The horse wanders into the unknown. Wherever it steps, that land must be conquered.

---

## CURRENT PHASE: ASHVAMEDHA

**Objective:** NAGAs infiltrate every byte. Living infrastructure.

**Status:** 12/12 Lords ACTIVE

**Architecture:** 8 Infrastructure + 4 Governance = 12 Lords

---

## TARGET ACQUISITION (The Horse)

> The Agent doesn't attack a list. It **hunts**.

### Detection Criteria (Rebel Kingdom Indicators)

Code is "atheist" (running without God/Infrastructure) if:

| Signal | Indicates | Needs |
|--------|-----------|-------|
| Class contains `Service`, `Manager`, `Handler` | Service candidate | @naga_service audit |
| Has `__init__` with injected dependencies | Stateful | Sesha observation |
| Makes HTTP/network calls | Boundary crossing | Vasuki protocol |
| Has auth/permission logic | Security surface | Takshaka validation |
| Writes to files/DB directly | State mutation | Sesha ledger |
| Has retry/fallback logic | Resilience | Prahlad/Kaliya |
| Logs metrics/events | Observable | Chitragupta profiling |
| Missing `@naga_service` decorator | UNFLOODED | Immediate target |

### Scan Locations (Where the Horse Wanders)

```
vibe_core/services/**/*.py      # Core services (HIGH priority)
vibe_core/plugins/**/plugin_main.py   # Plugin entry points
vibe_core/cartridges/**/*.py    # Cartridge tools
vibe_core/state/**/*.py         # State handlers
vibe_core/**/manas/**/*.py      # Cognitive components
```

### Classification Output

For each discovered target, classify:

1. **FLOODED** - Has @naga_service or uses NAGA protocols
2. **REBEL** - Service-like but no NAGA integration
3. **CIVILIAN** - Pure utility, no infrastructure needed

---

## CONQUERED TERRITORY

### INFRASTRUCTURE LAYER (8 Real Nagas) - ACTIVE

| Domain | NAGA | Protocol | DriftSource |
|--------|------|----------|-------------|
| Truth/Ledger | SESHA | SeshaProtocol | state |
| Security | TAKSHAKA | TakshakaProtocol | cognitive |
| Network | VASUKI | VasukiProtocol | config |
| Isolation | KALIYA | KaliyaProtocol | reliability |
| Crypto/Secrets | KARKOTAKA | KarkotakaProtocol | - |
| Schema/Order | KULIKA | KulikaProtocol | - |
| Cache/Treasury | PADMA | PadmaProtocol | - |
| Broadcast/Pubsub | SHANKHA | ShankhaProtocol | - |

### GOVERNANCE LAYER (4 Personnel) - ACTIVE

| Domain | NAGA | Protocol | Status |
|--------|------|----------|--------|
| Observation | NARADA | NaradaProtocol | ACTIVE |
| Profiling | CHITRAGUPTA | ChitraguptaProtocol | ACTIVE |
| Resilience | PRAHLAD | PrahladProtocol | ACTIVE |
| Gene Splicer | ANANTA | AnantaProtocol | ACTIVE |

### KNOWN REBELS (25+ identified)

> Full list: [NAGA_RECON.md](NAGA_RECON.md)

**TIER 1 - Immediate:**
| Target | Location | Needs |
|--------|----------|-------|
| StateService | state/ | Sesha |
| ManifestationService | services/ | Narada |
| CapabilityEnforcer | services/ | Takshaka |

**TIER 2 - Short-term:**
| Target | Location | Needs |
|--------|----------|-------|
| OpusStateManager | plugins/opus_assistant/ | Sesha |
| ActionManager | plugins/opus_assistant/ | Chitragupta |
| SenseManager | plugins/opus_assistant/ | Takshaka |

---

## CAMPAIGN PHASES

### Phase 1: Foundation (COMPLETE)
- [x] Kulika Schema Registry
- [x] @naga_service decorator on all 7 services
- [x] NaradaScanner auto-discovery
- [x] Orchestrator integration

### Phase 2: Active Recon (COMPLETE)
- [x] Run TARGET ACQUISITION scan
- [x] Classify all services as FLOODED/REBEL/CIVILIAN
- [x] Update KNOWN REBELS dynamically
- **See:** [NAGA_RECON.md](NAGA_RECON.md) for full intel

### Phase 3: Systematic Flooding
- [ ] Flood REBELS by priority (HIGH first)
- [ ] Protocol-first: define interface, then implement
- [ ] No config in code

### Phase 4: Complete Infrastructure Lords (COMPLETE)
- [x] KULIKA service (Schema Registry)
- [x] KARKOTAKA (Crypto/Secrets)
- [x] PADMA (Cache/Treasury)
- [x] SHANKHA (Broadcast/Pubsub)

### Phase 5: Ananta - The Gene Splicer (COMPLETE)
- [x] Define AnantaProtocol (interface first)
- [x] Define FloodProposal and VetoDecision types
- [x] Integrate with PrahladProtocol (Veto mechanism)
- [x] Write RED tests (TDD)
- [x] Implement AnantaService (make tests GREEN)
- [ ] Wire into NagaOrchestrator

---

## FLOODING PATTERNS

### Hard Flood (Balarama/Proxy) - BREAKS isinstance

```python
from vibe_core.naga import NagaProxy

# PROBLEM: Wraps at runtime with __getattr__ intercept
wrapped = NagaProxy(real_service)

# BREAKS:
isinstance(wrapped, OriginalService)  # FALSE!
pickle.dumps(wrapped)  # May fail
wrapped._internal_state  # Intercepted
```

Use cases: Quick observation, debugging, temporary wrapping

### Soft Flood (Ananta/Mixin) - PRESERVES isinstance

```python
# SOLUTION: DNA injection via Mixin inheritance
class FloodedService(SeshaMixin, TakshakaMixin, OriginalService):
    pass

# PRESERVES:
isinstance(instance, OriginalService)  # TRUE!
pickle.dumps(instance)  # Works
instance._internal_state  # Direct access
```

Use cases: Production flooding, permanent NAGA integration

### The Gene Splicer (Ananta)

Ananta creates flooded classes automatically:

```python
from vibe_core.naga import AnantaService

ananta = AnantaService()

# 1. Analyze service
proposal = ananta.analyze_service(MyRebelService)

# 2. Get Prahlad's approval (Check and Balance)
decision = ananta.request_approval(proposal)

# 3. Create flooded class (if approved)
if decision.approved:
    FloodedClass = ananta.create_flooded_class(MyRebelService, decision)
```

**Critical:** Ananta cannot flood without Prahlad's consent.

---

## PRINCIPLES (Dharma)

1. **No config in code** - Phoenix/YAML only
2. **Protocols first** - Interface before implementation
3. **Fractal** - Small, composable, atomic
4. **Organic** - Water flows, doesn't force
5. **Hunt, don't list** - Dynamic target acquisition
6. **Balarama wraps, doesn't modify** - Proxy pattern

---

## AGENT DIRECTIVE

```
ASHVAMEDHA PROTOCOL:
1. Scan locations using Detection Criteria
2. Classify each target
3. Report REBELS to battleplan
4. Await orders before flooding
5. After flooding: verify with @naga_service
```

---

*12/12 Lords ACTIVE. Ananta (Gene Splicer) implements Soft Flood with Prahlad's Veto. ASHVAMEDHA continues.*
