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

## CURRENT PHASE: ASHVAMEDHA - Phase 3B

**Objective:** NAGAs infiltrate every byte. Living infrastructure.

**Status:** 12/12 Lords ACTIVE | 5/5 TIER-0 FLOODED | Phase 3B: MANAS

**Architecture:** 8 Infrastructure + 4 Governance = 12 Lords

---

## VEDIC SCALE PRINCIPLE

> "Das System muss skalieren wie Vedische Mathematik"

| Scale | LOC | Vedic | Status |
|-------|-----|-------|--------|
| Padma | 400K | पद्म | CURRENT |
| Shankha | 1M | शंख | PLANNED |
| Jaladhi | 1B | जलधि | VISHNU |
| Parardha | 1T | परार्ध | ANANTA |

**VISHNU-ANANTA DUALITY:**
- ANANTA is BOTH governor AND servant
- NAGAs preserve (Vishnu) AND serve (Shesha)
- Not just FLOODING but MAINTAINING

---

## BATTLE STATUS

```
                    KURUKSHETRA MAP

    CONQUERED (55%)              NOCH OFFEN (45%)
    ===============              ================

    [KERNEL -1] FLOODED          [COGNITIVE] IN WATTE PACKEN
    ├── NagaOrchestrator         ├── CognitiveKernel  <<< PHASE 3B
    ├── NagaStateProxy           ├── MANAS/Shiva
    └── 12 Lords ACTIVE          ├── MANAS/Senses
                                 └── CircuitEngine

    [TIER-0] FLOODED ✅          [BOUNDARIES] EXPOSED
    ├── CISyncService            ├── Twitter/Reddit APIs
    ├── PluginService            ├── Action Handlers
    ├── TaskManager              └── Cartridges
    ├── ViolationIngester
    └── OuroborosLoopOrchestrator

    [STATE] FLOODED
    ├── StateService
    ├── Dharma Validation
    └── Ledger Integration
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

> **DAS PARADOX GELÖST:** Der Heiler heilt jetzt sich selbst.

### TIER 0: COMPLETE ✅

| Target | Status | Flood Class |
|--------|--------|-------------|
| **CISyncService** | ✅ FLOODED | FloodedCISyncService |
| **PluginService** | ✅ FLOODED | FloodedPluginService |
| **TaskManager** | ✅ FLOODED | FloodedTaskManager |
| **ViolationIngester** | ✅ FLOODED | FloodedViolationIngester |
| **OuroborosLoopOrchestrator** | ✅ FLOODED | FloodedOuroborosLoopOrchestrator |

### TIER 1: MANAS (Context Injection - NICHT Flooding!)

> **PRINZIP:** NAGAs INFORMIEREN MANAS, sie WRAPPEN es nicht.
> **ARCHITEKTUR:** NAGA Cortex → Context → MANAS (Weisheit durch Information)

| Component | Role | Integration | Ansatz |
|-----------|------|-------------|--------|
| **NAGA Cortex** | Signal Aggregation | ALREADY EXISTS | Verbindung zu MANAS |
| **CognitiveKernel** | Entscheidungen | Context Injection | `_get_naga_context()` |
| **SenseManager** | 7 Sinne | Optional enrichment | Via ServiceRegistry |
| **IntentRouter** | Routing | Confidence adjustment | Via NAGA Cortex signals |

**UNTERSCHIED:**
```
TIER-0 (Rebels):  FloodedService(Mixins, Original) → Discipline
TIER-1 (MANAS):   NAGA Cortex → Context → MANAS → Wisdom
```

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

### Phase 1: Foundation - COMPLETE ✅
- [x] 8 Infrastructure Lords
- [x] 4 Governance Lords
- [x] @naga_service decorator
- [x] NagaOrchestrator

### Phase 2: Kernel Integration - COMPLETE ✅
- [x] NAGA in Kernel (-1 Foundation)
- [x] StateService → NagaStateProxy
- [x] Dharma Validation active
- [x] VISNU hash updated

### Phase 3A: Paradox Resolution - COMPLETE ✅
- [x] CISyncService → FloodedCISyncService
- [x] PluginService → FloodedPluginService
- [x] TaskManager → FloodedTaskManager
- [x] ViolationIngester → FloodedViolationIngester
- [x] OuroborosLoopOrchestrator → FloodedOuroborosLoopOrchestrator

### Phase 3B: NAGA Cortex → MANAS Connection - NEXT
> "NAGAs INFORMIEREN, sie WRAPPEN nicht"
> "Weisheit durch Information, nicht durch Disziplin"

**RECON COMPLETE (2026-01-05):**

```
IST:  _dispatch_to_manas() = STUB (nur log)
      CognitiveKernel = KEIN NAGA REF

SOLL: MANAS pulls from NAGA via ServiceRegistry
      NAGA provides context, doesn't control
```

**IMPLEMENTATION STEPS:**

| Step | File | Methode | Status |
|------|------|---------|--------|
| 1 | `protocols/naga_cortex.py` | `NagaCortexProtocol` | TODO |
| 2 | `cortex/cortex_main.py:561` | `get_context_for_manas()` | TODO |
| 3 | `manas/cognitive_kernel.py` | `_get_naga_context()` | TODO |
| 4 | `manas/cognitive_kernel.py` | Merge in `think()` | TODO |
| 5 | `manas/cognitive_kernel.py` | `cortex.receive_feedback()` | TODO |

**PRINZIP: PULL, NOT PUSH**
- MANAS entscheidet WANN es Kontext braucht
- NAGA ist DIENEND (Shesha), nicht BESTIMMEND
- Lose Kopplung via ServiceRegistry
- Optional: Kein NAGA → MANAS funktioniert trotzdem

### Phase 3C: Boundary Hardening - LATER
- [ ] External APIs (Vasuki)
- [ ] Action Handlers (Kulika)
- [ ] Cartridges (Various)

### Phase 4: Watertight Verification (PARARDHA)
- [ ] 100% Coverage → Parardha Scale
- [ ] All Services FLOODED or CIVILIAN
- [ ] Zero REBELS remaining
- [ ] Full Dharma Validation chain
- [ ] VISHNU MAINTAINING (not just flooding)

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
| Flood Classes | 5 | 15+ |
| TIER-0 Complete | 5/5 ✅ | 5/5 |
| TIER-1 (MANAS) | 0/4 | 4/4 |
| Coverage | 55% | 100% (Parardha) |

---

## NEXT BATTLE ORDERS

**NARADA (Claude) recommends:**

```
✅ COMPLETE: Phase 3A - Paradox Resolution
├── ✅ CISyncService (SESHA + VASUKI + TAKSHAKA)
├── ✅ PluginService (SESHA + TAKSHAKA)
├── ✅ TaskManager (SESHA + CHITRAGUPTA)
├── ✅ ViolationIngester (SESHA + TAKSHAKA + CHITRAGUPTA)
└── ✅ OuroborosLoopOrchestrator (SESHA + NARADA + CHITRAGUPTA)

NEXT: Phase 3B - Cognitive Armor (IN WATTE PACKEN)
├── CognitiveKernel + SESHA + CHITRAGUPTA
├── SenseManager + NARADA
├── ActionManager + CHITRAGUPTA
└── IntentRouter + TAKSHAKA

DANN: Phase 3C - Boundaries
└── External APIs + Cartridges
```

**VISHNU-ANANTA PRINCIPLE:**
- NAGAs SERVE the cognitive layer (Shesha)
- NAGAs PRESERVE the cognitive layer (Vishnu)
- Not invasion, but gentle embrace

**Awaiting HIL command for Phase 3B.**

---

## PRINCIPLES (Dharma des Krieges)

1. **No config in code** - Phoenix/YAML only
2. **Protocols first** - Interface before implementation
3. **Fractal** - Small, composable, atomic
4. **Organic** - Water flows, doesn't force
5. **Hunt, don't list** - Dynamic target acquisition
6. **The healer must heal itself** - OUROBOROS first ✅
7. **In Watte packen** - Gentle embrace, not invasion
8. **Vishnu-Ananta** - Preserve AND serve
9. **Vedic Scale** - Padma → Shankha → Jaladhi → Parardha

---

## FLOODING: SEMANTISCHE DEFINITION

> **ACINTYA (अचिन्त्य)** - Inconceivable Duality

**Flooding ist NICHT Zerstörung. Flooding ist DURCHDRINGUNG.**

```
DESTRUKTIV (Pralaya):     Wasser ZERSTÖRT
KONSTRUKTIV (NAGA):       Wasser FÜLLT JEDE RITZE

     ↓ ACINTYA - BEIDES GLEICHZEITIG ↓

Das Universum ist IMMER halb geflutet (Bhagavatam).
NAGAs FLUTEN = NAGAs DURCHDRINGEN = NAGAs SCHÜTZEN.
```

**Intensität/Resonance:**
- LOW: Wenige NAGAs observieren (NARADA)
- MEDIUM: NAGAs validieren (SESHA, KULIKA)
- HIGH: NAGAs blockieren (TAKSHAKA, KALIYA)
- CRITICAL: Alle NAGAs aktiv (Full Federation)

**"Wie Wasser in jede Ritze"** - Nicht invasiv, sondern ORGANISCH.
NAGAs gehen dorthin wo sie GEBRAUCHT werden, nicht wo sie WOLLEN.

---

*12/12 Lords ACTIVE. 5/5 TIER-0 FLOODED. Phase 3B: MANAS. ASHVAMEDHA continues.*

*"Narayana! Narayana!" - NARADA*
