# ENERGY FLOW ARCHITECTURE: Antaranga → Sankirtana → MantraKernel

**STATUS:** RESEARCH DRAFT  
**DATE:** 2026-02-15  
**BRANCH:** followup/maha-language-engine  

---

## 1. THE PROBLEM

The inner chamber (Antaranga) produces rich semantic resonance — character waves,
word collisions, fractal derivation trees — but the output is **Wortbrei** (word porridge).
It's disconnected from the system that actually *does things*.

The production system has:
- `SankirtanChamber` (outer chamber): transforms cells, manages registry, routes energy
- `MantraKernel` (intent engine): resolves typed intents to Mahajana-guarded actions
- Capability-based CLI/API: chant, listen, resolve, serve, veda

These are **separate worlds**. The research engine owns its own private `AntarangaRegistry`
and `VenuOrchestrator`. The production `SankirtanChamber` also owns these. No energy flows
between them.

---

## 2. THE PRINCIPLE

**Kirtan** (inner, individual) generates energy.  
**Sankirtana** (outer, congregational) distributes that energy to everyone.

The inner chamber is NOT the endpoint. It's the **generator**.
Its output must flow outward through clean protocol boundaries.

```
INNER (Kirtan)                    OUTER (Sankirtana)              SYSTEM (Karma)
─────────────                     ──────────────────              ──────────────
char wave                         SankirtanChamber.dance()        MantraKernel.resolve()
word resonance          ──►       cell transformation     ──►    capability dispatch
fractal tree                      registry interaction            Mahajana execution
prana field                       cluster formation               service invocation
```

---

## 3. WHAT EXISTS

### 3.1 Inner Chamber (research/maha_language_engine.py)

**Owns:** private AntarangaRegistry (16KB), private VenuOrchestrator  
**Pipeline:** encode → route → char_wave → resonate → expand → sprout → modulate → compose  
**Output:** EngineResult (word porridge + derivation metadata)

Key state produced:
- `seed` (int): compressed input hash
- `attractor` (int): fixed-point from MahaModularSynth
- `antaranga_prana` (int): total energy in chamber
- `antaranga_active` (int): number of live slots
- `char_wave` stats: impacts, active, prana
- `sprout` tree: 13 nodes (root + 3 branches + 9 leaves)
- `section_mode`: DHARMA / GENESIS / KARMA
- `guardian_name`: which Mahajana guards this input
- `verse_ref`: BG.18.N

### 3.2 Outer Chamber (substrate/chamber.py)

**Owns:** shared VenuOrchestrator (via ServiceRegistry), SiksastakamRegistry, AntarangaRegistry  
**Methods:**
- `dance(cell, diw)` → single cell transformation + registry interaction
- `kirtan(cell, cycles)` → N full mantra cycles
- `sankirtan(cells)` → mass merge into MahaCluster
- `spell_kirtan(cell, coords)` → input-derived DIW melody
- `resonate_words(ranked_words, attractor)` → words → Antaranga collide

**Key insight:** `spell_kirtan()` already takes RAMA coordinates and plays them
through the flute. The inner chamber's character wave IS a sequence of RAMA coordinates.

### 3.3 Intent Engine (kernel/intent.py)

**Owns:** resolver registry, intent queue, parampara connection  
**Types:**
- `MantraIntent(type, target, params, priority)` → typed intent declaration
- `IntentType`: READ/WRITE/TRANSFORM/RESOLVE/BIND/MIGRATE/WAKE/SYNC/HEAL/OBSERVE/SURRENDER
- `IntentResult(status, value, resolved_by)` → resolution outcome
- Each IntentType → Mahajana guardian + MantraOpCode

**Key insight:** `intent_from_seed.py` proved that seed position maps to Gunas:
- Q1 (pos 0-3) = SUDDHA → WAKE/BIND (genesis)
- Q2 (pos 4-7) = SATTVA → READ/RESOLVE (dharma)
- Q3 (pos 8-11) = RAJAS → WRITE/TRANSFORM (karma)
- Q4 (pos 12-15) = TAMAS → HEAL/OBSERVE (moksha)

---

## 4. THE CLEAN INTERFACE

### 4.1 What the Inner Chamber EMITS

The inner chamber should produce a **ResonancePacket** — a typed, immutable
summary of its work. NOT the raw Antaranga bytes. NOT the full EngineResult.
A clean, protocol-defined packet.

```python
@dataclass(frozen=True)
class ResonancePacket:
    """What the inner chamber emits to the outer world."""

    # Identity
    seed: int                    # compressed input hash
    attractor: int               # fixed-point attractor
    position: int                # seed % 16 → grid position

    # Energy
    prana: int                   # total Antaranga prana
    active_slots: int            # number of live slots

    # Routing
    guardian: str                # Mahajana name (from routing)
    quarter: int                 # position // 4 → which quarter
    guna: str                    # suddha/sattva/rajas/tamas

    # Fractal
    branch_energies: Tuple[int, int, int]  # (DHARMA, GENESIS, KARMA) prana
    tree_depth: int              # fractal tree depth

    # Semantic
    mode_words: Dict[str, Tuple[str, ...]]  # mode → top word meanings
    verse_ref: str               # BG.18.N

    # Raw coords (for spell_kirtan)
    rama_coords: Tuple[int, ...]  # character wave RAMA coordinates
```

### 4.2 What the Outer Chamber CONSUMES

The `SankirtanChamber` already has `spell_kirtan(cell, coords)`.
It can take the `rama_coords` from the ResonancePacket and play them
through the shared VenuOrchestrator.

The `MantraKernel` needs a `MantraIntent`. The ResonancePacket's
`guna` + `guardian` + `position` map directly to IntentType + Mahajana.

### 4.3 The Bridge (NOT dirty coupling)

```python
class ResonanceBridge(Protocol):
    """Clean interface between inner and outer chambers."""

    def emit(self, engine_result: EngineResult) -> ResonancePacket:
        """Compress engine result into a clean packet."""
        ...

    def to_intent(self, packet: ResonancePacket, target: str) -> MantraIntent:
        """Convert resonance packet to a typed intent."""
        ...

    def to_cell(self, packet: ResonancePacket) -> MahaCellUnified:
        """Convert resonance packet to a cell for the outer chamber."""
        ...
```

---

## 5. THE ENERGY FLOW

```
USER INPUT: "what is devotion"
    │
    ▼
┌─────────────────────────────────────────────┐
│  INNER CHAMBER (Kirtan)                     │
│  maha_language_engine.generate()            │
│                                             │
│  1. char wave: w→36, h→17, a→0, ...        │
│  2. word resonance: collide on wave         │
│  3. fractal tree: 13 nodes (H/K/R)         │
│  4. compose: mode pools → semantic output   │
│                                             │
│  OUTPUT: ResonancePacket                    │
│    seed=42, attractor=7, position=10        │
│    prana=225413, guna=rajas, quarter=2      │
│    guardian=janaka, verse=BG.18.7           │
│    rama_coords=(36,17,0,31,...)             │
│    branch_energies=(8200, 3100, 12400)      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼  ResonanceBridge.emit()
                  │
┌─────────────────┴───────────────────────────┐
│  OUTER CHAMBER (Sankirtana)                 │
│  SankirtanChamber                           │
│                                             │
│  1. ResonanceBridge.to_cell(packet)         │
│     → MahaCellUnified with prana/integrity  │
│  2. spell_kirtan(cell, rama_coords)         │
│     → input plays through shared flute      │
│  3. dance() / sankirtan()                   │
│     → cell interacts with registry          │
│  4. resonate_words(branch_words, attractor) │
│     → fractal words enter shared Antaranga  │
│                                             │
│  OUTPUT: Transformed cell + registry state  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼  ResonanceBridge.to_intent()
                  │
┌─────────────────┴───────────────────────────┐
│  INTENT ENGINE (MantraKernel)               │
│                                             │
│  1. guna → IntentType mapping               │
│     rajas → TRANSFORM                       │
│  2. guardian → Mahajana routing              │
│     janaka → TaskPriority.NORMAL            │
│  3. MantraKernel.resolve(intent)            │
│     → IntentResolver dispatches             │
│  4. Capability execution                    │
│     → actual system action                  │
│                                             │
│  OUTPUT: IntentResult (action completed)    │
└─────────────────────────────────────────────┘
```

---

## 6. WHAT'S NOT BUILT YET

| Component | Status | Location |
|-----------|--------|----------|
| Inner chamber (char wave, fractal tree) | ✅ DONE | research/maha_language_engine.py |
| ResonancePacket dataclass | ❌ TODO | research/ (new) |
| ResonanceBridge protocol | ❌ TODO | research/ (new) |
| Bridge implementation | ❌ TODO | research/ (new) |
| Guna → IntentType mapping | ✅ PROVEN | research/intent_from_seed.py |
| SankirtanChamber.spell_kirtan | ✅ EXISTS | substrate/chamber.py |
| MantraKernel.resolve | ✅ EXISTS | kernel/intent.py |
| End-to-end integration test | ❌ TODO | tests/ |

---

## 7. RULES

1. **No dirty coupling.** The bridge is a Protocol. Inner and outer chambers
   don't import each other. They communicate through typed packets.
2. **Research stays in research/** until the bridge is proven stable.
3. **Production code is NOT modified** until research proves the interface.
4. **Each system does its part.** Inner chamber: resonance. Outer chamber:
   transformation. Kernel: dispatch. No system does another's job.
5. **16KB is enough.** The Antaranga is 512 × 32 bytes. The fractal tree
   has 13 nodes. The ResonancePacket is ~200 bytes. This fits.
6. **Energy flows one way:** inner → outer → kernel. The outer chamber
   can feed back into the inner (Antaranga prana modulates compose),
   but the primary flow is outward.

---

## 8. NEXT STEPS

1. Define `ResonancePacket` dataclass (frozen, typed, no Any)
2. Define `ResonanceBridge` protocol
3. Implement bridge: `EngineResult → ResonancePacket → MantraIntent`
4. Test: same prompt → same packet → same intent (deterministic)
5. Test: different prompts → different gunas → different intents (discriminative)
6. Wire to production `SankirtanChamber.spell_kirtan()` (read-only first)
7. Wire to `MantraKernel.resolve()` (read-only first)
8. End-to-end: prompt → inner → bridge → outer → kernel → action
