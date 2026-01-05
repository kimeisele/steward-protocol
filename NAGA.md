# NAGA.md - KURUKSHETRA BATTLEPLAN

> "Wie Wasser in jede Ritze" - ASHVAMEDHA

---

## CURRENT PHASE: ASHVAMEDHA

**Objective:** NAGAs infiltrate every byte. Living infrastructure.

**Status:** 7/11 Lords ACTIVE, 4 PLANNED

---

## INFRASTRUCTURE COVERAGE

### FLOODED (with NAGA protocols)

| Target | NAGA | Protocol | Status |
|--------|------|----------|--------|
| Ledger | SESHA | SeshaProtocol | ACTIVE |
| Security | TAKSHAKA | TakshakaProtocol | ACTIVE |
| Network | VASUKI | VasukiProtocol | ACTIVE |
| Quarantine | KALIYA | KaliyaProtocol | ACTIVE |
| Events | NARADA | NaradaProtocol | ACTIVE |
| Profiling | CHITRAGUPTA | ChitraguptaProtocol | ACTIVE |
| Resilience | PRAHLAD | PrahladProtocol | ACTIVE |

### NOT FLOODED (targets)

| Target | Needs | Priority |
|--------|-------|----------|
| ManifestationService | Narada observation | HIGH |
| CapabilityEnforcer | Takshaka validation | HIGH |
| LearningLoop | Chitragupta profiling | MEDIUM |
| LifecycleService | Prahlad resilience | MEDIUM |
| Manas | Cortex integration | HIGH |
| Genesis | Sesha ledger | LOW |

### PLANNED LORDS

| Lord | Purpose | Blocks |
|------|---------|--------|
| KARKOTAKA | Crypto/Secrets | - |
| PADMA | Cache/Treasury | - |
| SHANKHA | Broadcast/Pubsub | - |
| KULIKA | Schema (as service) | Has registry, needs service |

---

## BATTLE ORDERS

### Phase 1: Scanner Integration (DONE)
- [x] Kulika Schema Registry
- [x] @naga_service decorator
- [x] NaradaScanner auto-discovery
- [x] Orchestrator integration

### Phase 2: Flood Core Services
- [ ] Inject Narada into ManifestationService
- [ ] Inject Takshaka into CapabilityEnforcer
- [ ] Wire Cortex to Manas

### Phase 3: Complete Lords
- [ ] KULIKA as service (promote from registry)
- [ ] KARKOTAKA (secrets management)
- [ ] PADMA (caching layer)
- [ ] SHANKHA (event broadcast)

---

## PRINCIPLES

1. **No config in code** - Phoenix/YAML only
2. **Protocols first** - Define interface before implementation
3. **Fractal** - Small, composable, atomic
4. **Organic** - Water flows, doesn't force

---

*Last updated: Phase 1 complete*
