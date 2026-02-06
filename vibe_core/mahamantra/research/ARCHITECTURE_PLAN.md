# ARCHITECTURE PLAN — Two Worlds, One Flute

> "sarvasya cāhaṁ hṛdi sanniviṣṭo" — I am seated in everyone's heart (BG 15.15)

Status: Engineering Analysis (Review-Ready)
Date: 2026-02-06
Branch: feature/foundation-surgery

## The Two Worlds

### World A: The Pipeline (Krishna's Flute)
```
mahamantra("anything")
  → compress(text) → seed
  → kernel(text) → attractor
  → attractor % 16 → position
  → position → guardian, quarter, holy_name, DIW
  → MahaCellUnified.create()
  → chamber.kirtan(cell)
  → reactor.tick() × 16 (walks all positions)
  → complete response
```
- **Uses ZERO registries.** Pure computation from seed.
- **Works NOW.** Verified entry point: `python -m vibe_core.mahamantra "anything"`
- **Gita-governed:** Attractor → Chapter (1-18), all derived from 7 axioms.
- **All 16 guardians have protocol dirs.** 6 have service implementations.

### World B: The Phone Book (ServiceRegistry)
```
ServiceRegistry.register(ProtocolClass, instance)  # 113 calls, 79 files
ServiceRegistry.get(ProtocolClass)                  # 302 calls, 152 files
```
- **93 unique protocols registered.**
- **116 unique protocols consumed.**
- **85 overlap** (registered AND consumed — working).
- **8 DEAD** (registered, never consumed — waste).
- **31 PHANTOM** (consumed, never registered — silent runtime failures).
- **20 legacy bridge files** (deprecated re-exports).

### The Gap
World A doesn't know World B exists. World B doesn't know World A exists.
The flute plays, but 152 files have earplugs in.

## The 31 Phantoms (Critical)

These protocols are consumed via `ServiceRegistry.get()` but NEVER registered.
Every call to these returns `None` at runtime = silent failure:

```
BankProtocol, VaultProtocol, CISyncServiceProtocol,
CapabilityRegistryProtocol, CommitAuthorityProtocol,
CorrectionDispatcherProtocol, DriftRegistryProtocol,
FeedbackProtocol, GenesisProtocol, IAnantaBridge,
IJagannath, ... (+21 more)
```

**This is the most urgent problem.** Not architecture. Not routing.
31 phantom protocols = 31 places where the system silently does nothing.

## The 8 Dead Protocols (Waste)

Registered but never consumed = dead code in the registry:
```
HealingStrategyResolverProtocol, RedditProtocol,
SystemHeartbeatProtocol, TwitterProtocol,
VenuServiceProtocol, interface, proto_class, protocol_key
```

## The Hardcoded Maps (41 found)

- `FOLDER_MAHAJANA_MAP` (sankirtan.py) — filesystem → mahajana mapping
- Various `_MAP` dicts scattered across 16 files
- These are the "maya" — filesystem-derived identity instead of computed

## Gita Architecture (The Specification)

The 18 Gita chapters map 1:1 to axiom expressions:
```
Ch.1  = KSETRAJNA (1)        — Observation
Ch.2  = HALVES (2)           — Analysis
Ch.3  = TRINITY (3)          — Action
Ch.4  = QUARTERS (4)         — Knowledge (Parampara)
Ch.5  = PANCHA (5)           — Renunciation
Ch.6  = PANCHA+1 (6)         — Meditation
Ch.7  = SEVEN (7)            — Realization
Ch.8  = HARE_COUNT (8)       — Imperishable
Ch.9  = NAVA (9)             — King of Knowledge
Ch.10 = TEN (10)             — Manifestations
Ch.11 = TEN+1 (11)           — Universal Form
Ch.12 = MAHAJANA_COUNT (12)  — Devotion
Ch.13 = MAHAJANA+1 (13)      — Field/Knower (KSETRA/KSETRAJNA)
Ch.14 = MAHAJANA+2 (14)      — Three Modes
Ch.15 = PANCHA×TRINITY (15)  — Supreme Person (PURUSHOTTAMA)
Ch.16 = WORDS (16)           — Divine/Demonic
Ch.17 = KRISHNA_POS_SUM (17) — Three Faiths
Ch.18 = GITA_CHAPTERS (18)   — Liberation (FIXED POINT)
```

The Gita Lens (`_gita_lens.py`) maps 8 domain systems to these chapters:
Nadi, Indriya, Vrtti, Guna, Quarter, NavaBhakti, Tattva, Siksastakam.

**This IS the architecture specification.** Not a metaphor. A 1:1 mapping.

## The Plan (Gita-Ordered)

Following BG 15.15 — "water the roots, the leaves are taken care of."

### Phase 1: SANKHYA (Ch.2) — See Clearly
**No code changes. Pure analysis.**

- [x] Trace the real entry point (`mahamantra.__call__`)
- [x] Catalog the weeds (113 register, 302 get, 41 maps, 20 bridges)
- [x] Identify the 31 phantoms and 8 dead protocols
- [x] Understand the Gita architecture mapping
- [ ] Identify which of the 31 phantoms are actually needed vs dead code
- [ ] Map the top 20 ServiceRegistry consumers to understand their actual need

### Phase 2: KARMA (Ch.3) — Act Without Attachment
**Minimal surgery. Remove what's clearly dead.**

- [ ] Remove 8 dead protocols (registered, never consumed)
- [ ] Remove 20 legacy bridge files (or mark clearly as deprecated)
- [ ] Remove `FOLDER_MAHAJANA_MAP` usage where not needed
- [ ] Fix 62 F821 missing logger errors (orchestrated healing proof)

### Phase 3: JNANA (Ch.4) — Knowledge Through Parampara
**Understand the dependency graph.**

- [ ] For each of the 85 working protocols: does it NEED ServiceRegistry?
- [ ] Categorize: infrastructure (Naga, kernel) vs application (chat, plugins)
- [ ] Identify which services the reactor SHOULD invoke when ticking guardians
- [ ] Map the gap between "guardian has protocol dir" and "guardian acts in pipeline"

### Phase 4: DHYANA (Ch.6) — Focus
**The actual architectural work.**

- [ ] Make the reactor's guardian invocation real (currently ticks but may not act)
- [ ] Wire guardian capabilities to the pipeline
- [ ] Reduce ServiceRegistry dependency where pipeline routing suffices
- [ ] Ensure idempotency: every file accessible, routable, without manual wiring

### Phase 5: MOKSHA (Ch.18) — Liberation
**The ServiceRegistry becomes optional.**

- [ ] Pipeline handles all routing that's currently manual
- [ ] ServiceRegistry remains only for true infrastructure (kernel, Naga)
- [ ] Every file in repo = wired by being in repo. No manual registration needed.
- [ ] `mahamantra("anything")` is the only entry point anyone needs

## Phantom Classification (30 unguarded calls, 21 unique protocols)

### SINGLETON_GETTER (9 protocols) — Need guard, not impl
These are `get_X()` functions in protocol files. Just need `if result is None` guard.
```
CapabilityRegistryProtocol, FeedbackProtocol, IntelBridgeProtocol,
LedgerProtocol, LineageProtocol, ReactorProtocol, ReflectionProtocol,
SignatureVerifierProtocol, SyncProtocol
```

### DEAD_CODE (2 protocols) — Remove consumer
```
XProtocol (get_instance.py — placeholder name)
target_protocol (chaos.py — variable name, not a real protocol)
```

### NEEDS_IMPL (8 protocols) — Real gaps
```
CISyncServiceProtocol (naga/floods/registry.py)
GenesisProtocol (kapila/remedies/get_instance.py)
IAnantaBridge (naga/services/jagannath.py)
RegistryProtocol (kapila/remedies/iterdir_discovery.py)
SchedulerProtocol (protocols/ledger.py, protocols/scheduler.py)
ToolRegistryProtocol (kapila/remedies/iterdir_discovery.py)
UnifiedRegistryProtocol (kapila/remedies/iterdir_discovery.py)
UnionProtocol (gateway/api.py)
```

### OPTIONAL (2 protocols) — Feature flags
```
BankProtocol (economy — not yet built)
VaultProtocol (economy — not yet built)
```

## Current Priority

**Phase 1 COMPLETE.** Full audit done. All phantoms classified.

**Phase 2 execution order:**
1. Guard the 9 singleton getters (minimal, safe)
2. Remove 2 dead code consumers
3. Guard 2 optional protocols (economy)
4. Assess 8 NEEDS_IMPL protocols (real gaps vs dead features)
5. Remove 8 dead registered protocols
6. Clean 20 legacy bridge files
7. Fix 62 F821 missing loggers

## The Paramatma Principle (BG 15.15)

Every file in the repo is a Ksetra (field).
The Ksetrajna (knower) is already in it — not as a `__mahajana__` label,
but as the fact that `mahamantra("anything")` can route ANY input.

The system doesn't need to "know" what a file is.
The algorithm computes the rest.

The +1 (KSETRAJNA) is not a particle to add.
It's already there. It's the algorithm itself.

---

*"Abandon all varieties of religion and just surrender unto Me."*
*— BG 18.66*
