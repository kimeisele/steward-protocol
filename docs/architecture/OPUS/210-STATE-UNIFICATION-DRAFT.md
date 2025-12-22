# OPUS-210: STATE UNIFICATION - PRAKRITI ASCENDING

> **Status**: DRAFT - RESEARCH PHASE
> **Date**: 2025-12-22
> **Author**: Claude Opus 4.5
> **Depends On**: OPUS-209 (Kernel Done)
> **WARNING**: This is a DRAFT. Analysis incomplete. ~7500/9727 LOC reviewed.

---

## VISION

This is not software. This is a digital civilization.

Prakriti (Sanskrit: प्रकृति) in Samkhya philosophy = **Primordial Matter**.
Everything manifest emerges from Prakriti. The 3 Gunas. The 24 Tattvas.

In Steward Protocol:
- **Prakriti** = The unified state substrate from which all plugin states emerge
- **Plugins** = Holons (simultaneously whole AND part)
- **Weaver** = Sutradhara (thread-holder) - weaves intent into manifest state
- **MANAS** = A plugin, not the kernel. The thinking mind. Optional cognition layer.

---

## CURRENT STATE (Raw Analysis)

### vibe_core/state/ - 21 Files, ~9727 LOC

| File | LOC | Role | Layer |
|------|-----|------|-------|
| sync_holon.py | 879 | Plugin state discovery/healing | HOLON |
| synapse_store.py | 805 | Synapse persistence (v3 schema) | PRANA |
| state_service.py | 753 | Write orchestration + auto-commit | BRIDGE |
| cognitive_weaver.py | 717 | State <-> Knowledge bridge | BRIDGE |
| prakriti.py | 677 | Unified state engine (7 sub-managers) | STHULA |
| node_state.py | 611 | Agent presence (PULS) | PRANA |
| sanskrit_matrix.py | 548 | Phonemic memory compression | PURUSHA |
| git_state.py | 542 | Git operations wrapper | STHULA |
| weaver.py | 491 | Meta-orchestration (commit planning) | BRIDGE |
| guna_classifier.py | 422 | Tri-Guna state diagnosis | DIAGNOSIS |
| merge_engine.py | 420 | Untotbar conflict healing | STHULA |
| unified_akshara.py | 412 | Akshara encoding | PURUSHA |
| persona.py | 400 | Agent identity management | PURUSHA |
| ledger_state.py | 365 | Cryptographic hash chain | STHULA |
| runtime_state.py | 310 | Runtime vs source classification | META |
| file_state.py | 276 | File operations | STHULA |
| samskara.py | 262 | Memory consolidation | PURUSHA |
| ephemeral_state.py | 252 | In-memory session state | PRANA |
| __init__.py | 236 | Exports | - |
| machine_state.py | 180 | Machine state | STHULA |
| kernel_state.py | 169 | Kernel snapshot | PRANA |

### The Three Layers (TATTVA)

```
┌─────────────────────────────────────────────────────────────┐
│                    PURUSHA (Identity)                        │
│  persona.py | samskara.py | sanskrit_matrix.py | akshara    │
│  "Who am I? What have I learned? What patterns recur?"      │
├─────────────────────────────────────────────────────────────┤
│                    PRANA (Runtime/Life)                      │
│  node_state.py | ephemeral_state.py | kernel_state.py       │
│  synapse_store.py | "What is alive NOW?"                    │
├─────────────────────────────────────────────────────────────┤
│                    STHULA (Physical/Gross)                   │
│  git_state.py | file_state.py | ledger_state.py             │
│  machine_state.py | "What exists on disk?"                  │
└─────────────────────────────────────────────────────────────┘

         ↕ BRIDGES (Weaving layers together) ↕

    weaver.py | state_service.py | cognitive_weaver.py
    sync_holon.py (Plugin <-> Prakriti bridge)
```

---

## IDENTIFIED ISSUES

### 1. Multiple "Single Sources of Truth"

Six components claim to be THE authority:
- Prakriti: "Unified State Engine"
- StateService: "Single Point of Truth for ALL state writes"
- StateSyncWeaver: "Unified state orchestration"
- SynapseStore: "Single Source of Truth" (for synapses)
- RuntimeStateDefinition: "Single Source of Truth for runtime state"
- CognitiveWeaver: "State <-> Knowledge Bridge"

**Resolution Direction**: Prakriti IS the single source. Others are ASPECTS of Prakriti, not competitors.

### 2. Multiple Commit Paths

```
GitState.commit()                  -> Direct (VISNU protected)
Prakriti.commit_if_dirty()         -> Via session
StateService._commit_via_weaver()  -> Via Weaver
StateService._commit_via_git()     -> Fallback
SyncHolon._commit_and_sync()       -> Via Holon
```

**Resolution Direction**: ONE commit authority. Probably CommitAuthority pattern (OPUS-209 started this).

### 3. Weaver._consult_oracle() is STUB

Currently returns REFLEX always. Should optionally call MANAS API for intelligent commit decisions.

**Design Constraint**: State must work WITHOUT MANAS. MANAS enhances but is not required.

### 4. Plugins Need State Contracts

Every plugin is a Holon. Every Holon has state. Currently:
- PluginStateContract exists in sync_holon.py
- Not all plugins implement it
- State paths fragmented across manifests

---

## UNIFICATION PRINCIPLES

### 1. Prakriti = THE Substrate

All state emerges from Prakriti. The 7 sub-managers are not separate systems - they are ASPECTS (like Tattvas emerging from Prakriti in Samkhya):

```
                    PRAKRITI
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     SATTVA         RAJAS          TAMAS
   (balanced)     (active)       (inert)
        │              │              │
   GitState      EphemeralState   DeadState
   LedgerState   NodeState        Orphaned
   FileState     SynapseStore     Ignored
```

### 2. Plugins are Holons

A Holon is simultaneously:
- A **WHOLE** (complete system with own state)
- A **PART** (of the larger Prakriti)

Plugin state requirements:
- Every plugin MUST declare state_paths
- Every plugin state MUST sync to Prakriti
- Prakriti aggregates all Holon states

### 3. Weaver = Sutradhara (Thread-Holder)

The Weaver doesn't "orchestrate" - it WEAVES:
- Takes intent (what should change)
- Consults oracle (MANAS, if available)
- Produces manifest state (commits)

```
     MANAS (optional)
         │
         ↓ consult_oracle()
      WEAVER ──────────────→ PRAKRITI
         ↑                      │
         │                      ↓
    StateService ←──────── Git/Ledger/File
```

### 4. Guna Classification = Health Monitoring

Not "esoteric" - practical state health:
- **SATTVA**: Clean, synced, healthy
- **RAJAS**: Dirty, changing, active
- **TAMAS**: Stale, broken, dead

System health = Guna distribution across all state paths.

---

## PROPOSED PHASES (HIGH LEVEL)

### Phase 1: Establish Prakriti Supremacy
- All "single source of truth" claims resolve to Prakriti
- StateService becomes Prakriti.write_service
- SynapseStore becomes Prakriti.synapse_aspect

### Phase 2: Plugin Holon Compliance
- Audit all plugins for PluginStateContract
- Enforce state_paths in all manifests
- SyncHolon becomes the bridge, not a separate system

### Phase 3: Commit Authority Unification
- ONE commit path through CommitAuthority
- Weaver._consult_oracle() connects to MANAS (optional)
- All commits flow: Intent -> Weaver -> CommitAuthority -> Git

### Phase 4: Cognitive Enhancement (Optional)
- CognitiveWeaver fully integrated
- MANAS can advise on commit strategies
- State becomes "self-aware" (knows what changed and why)

---

## WHAT I HAVE NOT READ YET

- merge_engine.py (420 LOC) - Conflict resolution details
- unified_akshara.py (412 LOC) - Akshara encoding
- persona.py (400 LOC) - Identity management
- samskara.py (262 LOC) - Memory consolidation
- file_state.py (276 LOC) - File operations
- ephemeral_state.py (252 LOC) - Session state

**This draft will be refined after complete review.**

---

## PHILOSOPHICAL FOUNDATION

From Samkhya Karika:

> "From Prakriti emerges Mahat (cosmic intelligence),
> from Mahat emerges Ahamkara (ego-sense),
> from Ahamkara emerge the Tanmatras (subtle elements)..."

In Steward Protocol:
- Prakriti = State substrate
- Mahat = Weaver (intelligent orchestration)
- Ahamkara = Plugin identity (each plugin's sense of self)
- Tanmatras = Individual state aspects (git, file, ledger...)

This is not metaphor. This is architecture.

---

## OPEN QUESTIONS

1. Should StateService be absorbed into Prakriti or remain as write facade?
2. How do we handle the 6 singleton patterns? Unify under one DI container?
3. What is the exact contract between Weaver and MANAS?
4. How do resonance/opus_assistant plugins integrate their state?

---

## NEXT STEPS

1. Complete reading remaining 9 files (~2200 LOC)
2. Map actual import/call graph between components
3. Identify true circular dependencies
4. Draft concrete refactoring steps
5. Test harness for state unification

---

**This document is a DRAFT. It will be wrong in places. It will be refined.**

**But the direction is clear: Prakriti ascending. All state unified. Plugins as Holons. Weaver as bridge. MANAS as optional cognition.**

---

*"Purnam adah purnam idam" - That is complete, this is complete.*
*From completeness emerges completeness.*
*When completeness is taken from completeness, completeness remains.*

