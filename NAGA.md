# NAGA.md - KURUKSHETRA BATTLEPLAN

> "Wie Wasser in jede Ritze" - ASHVAMEDHA
> The horse wanders into the unknown. Wherever it steps, that land must be conquered.

---

## CURRENT PHASE: ASHVAMEDHA

**Objective:** NAGAs infiltrate every byte. Living infrastructure.

**Status:** 7/11 Lords ACTIVE, 4 PLANNED

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

### FLOODED (with NAGA protocols)

| Domain | NAGA | Protocol | DriftSource |
|--------|------|----------|-------------|
| Truth/Ledger | SESHA | SeshaProtocol | state |
| Security | TAKSHAKA | TakshakaProtocol | cognitive |
| Network | VASUKI | VasukiProtocol | config |
| Isolation | KALIYA | KaliyaProtocol | reliability |
| Observation | NARADA | NaradaProtocol | - |
| Profiling | CHITRAGUPTA | ChitraguptaProtocol | performance |
| Resilience | PRAHLAD | PrahladProtocol | structural |

### KNOWN REBELS (manual targets)

| Target | Location | Needs | Priority |
|--------|----------|-------|----------|
| ManifestationService | services/ | Narada | HIGH |
| CapabilityEnforcer | services/ | Takshaka | HIGH |
| LearningLoop | services/ | Chitragupta | MEDIUM |
| LifecycleService | services/ | Prahlad | MEDIUM |
| Manas Cortex | plugins/opus_assistant/ | Full integration | HIGH |

### LORDS IN TRAINING

| Lord | Purpose | Status |
|------|---------|--------|
| KARKOTAKA | Crypto/Secrets | PLANNED |
| PADMA | Cache/Treasury | PLANNED |
| SHANKHA | Broadcast/Pubsub | PLANNED |
| KULIKA | Schema Service | Registry exists, service needed |

---

## CAMPAIGN PHASES

### Phase 1: Foundation (COMPLETE)
- [x] Kulika Schema Registry
- [x] @naga_service decorator on all 7 services
- [x] NaradaScanner auto-discovery
- [x] Orchestrator integration

### Phase 2: Active Recon (CURRENT)
- [ ] Run TARGET ACQUISITION scan
- [ ] Classify all services as FLOODED/REBEL/CIVILIAN
- [ ] Update KNOWN REBELS dynamically

### Phase 3: Systematic Flooding
- [ ] Flood REBELS by priority (HIGH first)
- [ ] Protocol-first: define interface, then implement
- [ ] No config in code

### Phase 4: Complete the Lords
- [ ] KULIKA service (promote registry)
- [ ] KARKOTAKA, PADMA, SHANKHA

---

## PRINCIPLES (Dharma)

1. **No config in code** - Phoenix/YAML only
2. **Protocols first** - Interface before implementation
3. **Fractal** - Small, composable, atomic
4. **Organic** - Water flows, doesn't force
5. **Hunt, don't list** - Dynamic target acquisition

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

*Phase 1 complete. Phase 2: Active Recon initiated.*
