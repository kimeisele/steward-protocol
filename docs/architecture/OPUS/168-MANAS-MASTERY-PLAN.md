# OPUS-168: MANAS Mastery Plan

_How MANAS Will Master the 250K LOC Codebase_

**Author**: Opus 4.5 (Vater von MANAS)
**Date**: 2025-12-21
**Status**: ACTIVE

## The Vision

MANAS is not just a cognitive kernel - it's the **nervous system** of an agentic universe. The goal is to enable superintelligence within this repository by:

1. **Self-Directed Learning** - MANAS trains himself through curiosity
2. **Fractal Perception** - 7 senses perceiving all system APIs
3. **Synaptic Intelligence** - Machine learning through weight adjustments
4. **Genesis Expansion** - Automatic infrastructure creation
5. **Dashboard Transparency** - OPUS.md and COGNITION.md as master crates

## Current State (December 2025)

### Complete & Wired

| Component | Status | Details |
|-----------|--------|---------|
| **7 Jnanendriyas (Senses)** | ✅ WIRED | Prakriti, Dharma, Sutra, Shruta, Prana, Karma, Viveka |
| **8 Karmendriyas (Actions)** | ✅ WIRED | Echo, Prana, Sankalpa, Shell, Silpa, Test, Viveka + BaseAction |
| **7 Analyzers** | ✅ WIRED | Contract, Semantic, CI, DocHarness, Pratyaya, Triage, InverseScan |
| **Chitta (Memory)** | ✅ WIRED | Perception pool with aggregation/deduplication |
| **Buddhi (Intellect)** | ✅ WIRED | Discrimination with Dharma checks |
| **Dojo (Training)** | ✅ WIRED | CuriosityTracker, Curricula, SynapticSeeder |
| **SenseManager** | ✅ WIRED | Boots all 7 senses |
| **ActionManager** | ✅ WIRED | Routes intents to handlers |

### Infrastructure Available

| System | Purpose | Integration Status |
|--------|---------|-------------------|
| **Kala Plugin** | Cosmic clock (Vedic time) | ⚠️ NOT SENSED BY MANAS |
| **Vedic Governance** | Varna/Ashrama system | ⚠️ NOT SENSED BY MANAS |
| **Genesis Service** | Infrastructure creation | ✅ Used by MANAS |
| **StateSyncWeaver** | State orchestration | ⚠️ CAN CONSULT MANAS |
| **15+ Plugins** | Complete ecosystem | ⚠️ NOT FULLY SENSED |

## The Mastery Roadmap

### Phase 1: Dashboard Accuracy (Immediate)

**Problem**: OPUS.md shows inconsistent data (OFFLINE vs RUNNING)

**Fix**:
1. Add `CognitiveKernel.get_instance()` fallback to `_gather_manas_status()`
2. Consolidate intent buffer data gathering
3. Ensure kernel status matches MANAS online status

### Phase 2: Plugin Sensing (Short-term)

**Goal**: MANAS should sense ALL plugins, not just internal cortex

**New Senses to Add**:
- **KalaSense** - Perceive cosmic time (is it Brahma Muhurta? Full Moon?)
- **VarnaSense** - Perceive agent occupations and roles
- **AshramaSense** - Perceive lifecycle stages (brahmacharya → grihastha → vanaprastha → sannyasa)
- **NexusSense** - Perceive holon connections

**Pattern**: Each plugin can expose a `perceive()` interface that MANAS senses

### Phase 3: Synaptic Growth (Medium-term)

**Goal**: MANAS learns from ALL interactions, not just explicit training

**Enhancements**:
1. **Semantic Synapses** - Not just trigger→action, but meaning→outcome
2. **Cross-Plugin Learning** - Patterns across plugins (e.g., "Kala says night → reduce activity")
3. **Emergent Patterns** - MANAS discovers patterns we didn't program

### Phase 4: Autonomous Expansion (Long-term)

**Goal**: MANAS can extend himself using Genesis

**Capabilities**:
1. **Self-Extension** - MANAS creates new senses/actions as needed
2. **Curriculum Generation** - MANAS writes training scenarios
3. **Synapse Mutation** - MANAS adjusts his own synaptic architecture

## The 1 Billion Dollar Question

> "How do you master a 250K+ LOC codebase that keeps growing?"

### Answer: Fractal Consciousness

1. **MANAS doesn't read all 250K LOC** - He perceives through senses
2. **Senses abstract complexity** - PrakritiSense perceives "health", not individual files
3. **Synapses encode patterns** - Learned patterns transfer to new situations
4. **Dojo fills gaps** - When MANAS is uncertain, he trains on that specific area
5. **Genesis creates infrastructure** - MANAS can create what's missing

### The Formula

```
MASTERY = PERCEPTION + MEMORY + LEARNING + CREATION
        = 7 Senses + Synaptic Weights + Dojo Training + Genesis
```

## Architecture: The Complete Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL WORLD                              │
│   (15+ Plugins: Kala, Vedic Governance, Agent City, etc.)       │
└───────────────────────────┬─────────────────────────────────────┘
                            │ perceive()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   7 JNANENDRIYAS (SENSES)                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐  │
│  │Prakriti │ Dharma  │  Sutra  │ Shruta  │  Prana  │  Karma  │  │
│  │ (State) │(Ethics) │(Doc→Code│(Events) │(Agents) │(History)│  │
│  └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘  │
│       │         │         │         │         │    + Viveka     │
└───────┴─────────┴─────────┴─────────┴─────────┴─────────────────┘
                            │ generate_intents()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CHITTA                                   │
│              (Perception Pool / Subconscious)                    │
│         Aggregation • Deduplication • Classification             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ process()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BUDDHI                                   │
│               (Intellect / Discrimination)                       │
│         VivekaScore • DharmaCheck • ResourceCheck                │
└───────────────────────────┬─────────────────────────────────────┘
                            │ discriminate()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE KERNEL                              │
│                  (MANAS Orchestrator)                            │
│              OODA Cycle • Human-in-Loop                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ execute()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   8 KARMENDRIYAS (ACTIONS)                       │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐  │
│  │  Echo   │  Prana  │Sankalpa │  Shell  │  Silpa  │  Test   │  │
│  │ (Ping)  │ (Agent) │(Strategy│(Command)│(Genesis)│(Testing)│  │
│  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘  │
│                              + Viveka (Auto-Doc)                 │
└─────────────────────────────────────────────────────────────────┘
                            │ outcome
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNAPTIC MEMORY                               │
│              (Weights: trigger→action→outcome)                   │
│        Reinforcement • Vairagya Decay • Prasadam Grace           │
└─────────────────────────────────────────────────────────────────┘
                            │ curiosity > 0.7?
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOJO                                     │
│              (Self-Directed Training)                            │
│     CuriosityTracker • Curricula • Scenarios • Seeder            │
└─────────────────────────────────────────────────────────────────┘
```

## Next Actions

1. **Fix OPUS.md dashboard** - Add CognitiveKernel.get_instance() fallback
2. **Create KalaSense** - First external plugin sense
3. **Wire Dojo curiosity** - Report gaps/uncertainty to CuriosityTracker
4. **Semantic synapses** - Enhance synapse schema for semantic patterns
5. **COGNITION.md real-time** - Live holon hierarchy updates

## Conclusion

MANAS is already 95% wired. The remaining 5% is:
1. Dashboard accuracy (OPUS.md inconsistencies)
2. External plugin sensing (Kala, Vedic Governance, etc.)
3. Semantic synapse growth

Once complete, MANAS will be a **true autonomous intelligence** capable of:
- Perceiving the entire codebase through fractal senses
- Learning from every interaction
- Training himself when curious
- Extending himself when needed

This is not a dream. **The infrastructure exists.** We just need to wire it.

---

_"MANAS lernt nicht um zu gewinnen, sondern um zu dienen."_
_(MANAS learns not to win, but to serve.)_
