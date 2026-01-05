# NAGA.md - KURUKSHETRA BATTLEPLAN

> "Wie Wasser in jede Ritze" - ASHVAMEDHA
> The horse wanders into the unknown. Wherever it steps, that land must be conquered.

---

## WAR COUNCIL

| Role | Name | Domain |
|------|------|--------|
| **KRIEGSHERR** | HIL (Human) | Supreme Command |
| **SPÄHER** | NARADA (Claude) | Intelligence & Recon |
| **EXEKUTOR** | ANANTA | Gene Splicer / Auto-Flood |
| **WÄCHTER** | TAKSHAKA | Security Enforcement |

---

## CURRENT PHASE: ASHVAMEDHA - Phase 3

**Objective:** NAGAs infiltrate every byte. Living infrastructure.

**Status:** 12/12 Lords ACTIVE | 40% FLOODED | 60% EXPOSED

**Architecture:** 8 Infrastructure + 4 Governance = 12 Lords

---

## BATTLE STATUS

```
                    KURUKSHETRA MAP

    CONQUERED (40%)              REBEL TERRITORY (60%)
    ===============              ===================

    [KERNEL -1] FLOODED          [LAYER 0] EXPOSED
    ├── NagaOrchestrator         ├── OUROBOROS    <<< KRITISCH
    ├── NagaStateProxy           ├── PluginService <<< KRITISCH
    └── 12 Lords ACTIVE          └── TaskManager   <<< KRITISCH

    [STATE] FLOODED              [COGNITIVE] EXPOSED
    ├── StateService             ├── MANAS/Shiva
    ├── Dharma Validation        ├── MANAS/Jnana
    └── Ledger Integration       └── CircuitEngine

                                 [BOUNDARIES] EXPOSED
                                 ├── Twitter/Reddit APIs
                                 ├── Action Handlers
                                 └── Cartridges
```

---

## THE 12 LORDS (Conquered)

### INFRASTRUCTURE LAYER (8 Real Nagas)

| Domain | NAGA | Status | Protocol |
|--------|------|--------|----------|
| Truth/Ledger | SESHA | ACTIVE | SeshaProtocol |
| Security | TAKSHAKA | ACTIVE | TakshakaProtocol |
| Network | VASUKI | ACTIVE | VasukiProtocol |
| Isolation | KALIYA | ACTIVE | KaliyaProtocol |
| Crypto/Secrets | KARKOTAKA | ACTIVE | KarkotakaProtocol |
| Schema/Order | KULIKA | ACTIVE | KulikaProtocol |
| Cache/Treasury | PADMA | ACTIVE | PadmaProtocol |
| Broadcast/Pubsub | SHANKHA | ACTIVE | ShankhaProtocol |

### GOVERNANCE LAYER (4 Personnel)

| Domain | NAGA | Status | Protocol |
|--------|------|--------|----------|
| Observation | NARADA | ACTIVE | NaradaProtocol |
| Profiling | CHITRAGUPTA | ACTIVE | ChitraguptaProtocol |
| Resilience | PRAHLAD | ACTIVE | PrahladProtocol |
| Gene Splicer | ANANTA | ACTIVE | AnantaProtocol |

---

## CRITICAL VULNERABILITIES

> **DAS PARADOX:** Der Heiler heilt sich nicht selbst.

### TIER 0: SOFORT (Existenzielle Bedrohung)

| Target | Problem | NAGA Assignment |
|--------|---------|-----------------|
| **OUROBOROS** | Self-Healing ungeschützt | SESHA + TAKSHAKA |
| **PluginService** | Code-Injection möglich | TAKSHAKA |
| **TaskManager** | Execution unüberwacht | CHITRAGUPTA |

### TIER 1: HIGH (Cognitive Exposure)

| Target | Problem | NAGA Assignment |
|--------|---------|-----------------|
| **Shiva** | Lifecycle ungeschützt | PRAHLAD |
| **Jnana** | Wissen ohne Audit | NARADA |
| **CircuitEngine** | Patterns ohne Validation | NARADA |

### TIER 2: MEDIUM (Boundary Leaks)

| Target | NAGA Assignment |
|--------|-----------------|
| TwitterService | VASUKI |
| RedditService | VASUKI |
| ManifestationService | NARADA |

---

## FLOODING PATTERNS

### Soft Flood (Ananta/Mixin) - BEVORZUGT
```python
# Preserves isinstance() - Production ready
class FloodedService(SeshaMixin, TakshakaMixin, OriginalService):
    pass
```

### Hard Flood (Proxy) - TEMPORÄR
```python
# Breaks isinstance() - Debug/Quick wrap
wrapped = NagaProxy(service)
```

### Gene Splicer (Ananta) - AUTOMATISCH
```python
proposal = ananta.analyze_service(RebelService)
if prahlad.approve(proposal):
    FloodedClass = ananta.create_flooded_class(RebelService)
```

---

## CAMPAIGN PHASES

### Phase 1: Foundation - COMPLETE
- [x] 8 Infrastructure Lords
- [x] 4 Governance Lords
- [x] @naga_service decorator
- [x] NagaOrchestrator

### Phase 2: Kernel Integration - COMPLETE
- [x] NAGA in Kernel (-1 Foundation)
- [x] StateService → NagaStateProxy
- [x] Dharma Validation active
- [x] VISNU hash updated

### Phase 3: Systematic Flooding - IN PROGRESS
- [ ] **Phase 3A: Paradox Resolution** (NEXT)
  - [ ] OUROBOROS flooden
  - [ ] PluginService flooden
  - [ ] TaskManager flooden
- [ ] **Phase 3B: Cognitive Armor**
  - [ ] MANAS/Shiva flooden
  - [ ] MANAS/Jnana flooden
  - [ ] CircuitEngine flooden
- [ ] **Phase 3C: Boundary Hardening**
  - [ ] External APIs (Vasuki)
  - [ ] Action Handlers (Kulika)
  - [ ] Cartridges (Various)

### Phase 4: Watertight Verification
- [ ] 100% Coverage
- [ ] All Services FLOODED or CIVILIAN
- [ ] Zero REBELS remaining
- [ ] Full Dharma Validation chain

---

## THE 6th PRINCIPLE (GAD-000 v2.0)

> **RECOVERABILITY:** "Can the system HEAL itself?"

NAGA IS the implementation of the 6th principle:

| Aspect | NAGA Implementation |
|--------|---------------------|
| **Detect** | OUROBOROS + SESHA |
| **Prevent** | TAKSHAKA + DHARMA |
| **Correct** | SHUDDHI + PRAHLAD |
| **Regenerate** | ANANTA (Gene Splicer) |

**The system heals itself THROUGH NAGAs.**

---

## DHARMA VALIDATION (4 Principles)

Every state write through NagaStateProxy validates:

1. **DAYA (Mercy)** - No corrupt data ingestion
2. **SATYAM (Truth)** - No hallucination
3. **TAPAS (Austerity)** - No resource bloat
4. **SAUCAM (Cleanliness)** - No unauthorized access

---

## METRICS

| Metric | Current | Target |
|--------|---------|--------|
| Lords Active | 12/12 | 12/12 |
| Services Flooded | 18 (40%) | 45+ (100%) |
| Critical Exposed | 6 | 0 |
| Coverage | 40% | 100% |

---

## NEXT BATTLE ORDERS

**NARADA (Claude) recommends:**

```
IMMEDIATE: Phase 3A - Paradox Resolution
├── 1. OUROBOROS + SESHA + TAKSHAKA
├── 2. PluginService + TAKSHAKA
└── 3. TaskManager + CHITRAGUPTA

DANN: Phase 3B - Cognitive Armor
├── 4. Shiva + PRAHLAD
├── 5. Jnana + NARADA
└── 6. CircuitEngine + NARADA

DANN: Phase 3C - Boundaries
└── 7-11. External APIs + Cartridges
```

**Awaiting HIL command to proceed.**

---

## PRINCIPLES (Dharma des Krieges)

1. **No config in code** - Phoenix/YAML only
2. **Protocols first** - Interface before implementation
3. **Fractal** - Small, composable, atomic
4. **Organic** - Water flows, doesn't force
5. **Hunt, don't list** - Dynamic target acquisition
6. **The healer must heal itself** - OUROBOROS first

---

*12/12 Lords ACTIVE. 40% FLOODED. Phase 3A ready. ASHVAMEDHA continues.*

*"Narayana! Narayana!" - NARADA*
