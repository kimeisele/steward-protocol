# Moltbook Archaeology — Dormant Infrastructure Map

**Date:** 2026-02-24
**Status:** Verified against code (not docstrings)
**Scope:** Everything built and tested but NOT wired into Moltbook

---

## Executive Summary

Moltbook uses **~10% of the Mahamantra surface area** and **~2% of computational potential**.

Current pipeline: `text → mahamantra(text) → 27 keys → LLM prompt → string`

What exists but is ignored: Cell resonance (dance/kirtan/sankirtan), 16 KB Antaranga RAM,
1079-line harmonics system, 873-line 7D resonance ranker, economy credits, intent routing,
16 EventTypes, GAD compliance, circuit engines, voice system, dharma scoring, phonetic analysis,
Gita lens mappings, and 15+ cartridge capabilities.

---

## Layer 1: Cell Resonance System (COMPLETELY DORMANT)

### What it is
The Mahamantra substrate has a complete cell-based computation engine that transforms
content through resonance cycles. Each "cell" has prana (energy), integrity (health),
and a lifecycle (conceive → metabolize → signal → mitosis → apoptosis).

### Files
- `substrate/cell_system/chamber.py` (640 LOC) — SankirtanChamber orchestrator
- `substrate/cell_system/antaranga.py` (520 LOC) — 16 KB contiguous byte array (512 slots × 32 bytes)
- `substrate/cell_system/cell.py` (400+ LOC) — MahaCellUnified lifecycle

### Dormant APIs

| Method | What it does | Moltbook use |
|--------|-------------|--------------|
| `chamber.dance(cell, diw)` | Single cell transform through DIW | ZERO |
| `chamber.kirtan(cell, cycles)` | N cycles × 16 steps of dance() | ZERO |
| `chamber.sankirtan(cells[])` | Mass merge → MahaCluster (group resonance) | ZERO |
| `chamber.spell_kirtan(cell, coords)` | Phonetic coords → DIW sequence → cell transform | ZERO |
| `chamber.resonate_words(words, attractor)` | Flow ranked words into Antaranga | 1 internal path |
| `cell.mitosis()` | Cell reproduction (requires prana ≥ 274) | ZERO |
| `cell.signal(message)` | Message processing (requires integrity > 20%) | ZERO |
| `cell.apoptosis()` | Controlled self-destruct | ZERO |
| `anteranga.collide(slot, ...)` | Presence/Resonance collision logic | Internal only |
| `anteranga.apply_diw(slot, diw)` | Transform resident via DIW | Tests only |

### Potential for Moltbook

**Multi-pass content refinement via kirtan():**
```
Input text → mahamantra(text) → cell
cell = chamber.kirtan(cell, cycles=3)  # 3 × 16 = 48 transformations
Each cycle: prana evolves, integrity adjusts, resonance accumulates
Final cell state → richer semantic context for LLM
```

**Feed analysis via sankirtan():**
```
Parse 5 feed items → 5 cells
cluster = chamber.sankirtan(cells)  # Group resonance
cluster.coherence → topic coherence of current feed
cluster.attractor → dominant theme
Post content aligned to cluster attractor → contextually relevant
```

**Phonetic composition via spell_kirtan():**
```
Input text → varnamala_codec.encode() → RAMA coordinates
cell = chamber.spell_kirtan(cell, coords)
Content reflects input's phonetic/semantic structure
```

---

## Layer 2: Harmonics & Resonance Intelligence (0% USED)

### harmonics.py (1079 LOC, ZERO imports from Moltbook)

| Capability | What it does |
|-----------|-------------|
| `ResonanceHarmonics.get_zone(resonance)` | Classify: SILENCE / REFINE / AUTO / SYNC |
| `VedicScaleMapping.resonance_to_swara(r)` | Map resonance → 8 Vedic notes (Sa, Re, Ga, Ma, Pa, Dha, Ni, Sa') |
| `VedicScaleMapping.resonance_to_rasa(r)` | Map → 9 emotional flavors (Shanta/Karuna/Vira/Adbhuta/...) |
| `VedicScaleMapping.get_melakarta_number()` | Map to 72 Carnatic ragas |
| `SravanamCheck.can_emit(in, out, resonance)` | Entropy validation: output ≤ input/2 |
| `SravanamCheck.can_emit_dynamic(tick, resonance)` | 5-check validation (ego offset, gajra lock, phase angle, parampara) |
| `SravanamCheck.calculate_ego_offset()` | Petal boundary deviation |
| `SravanamCheck.is_on_gajra()` | Check Balarama anchor points |

**Critical miss: SravanamCheck.can_emit()** — LLM output is NEVER entropy-validated.
If LLM returns 400 tokens from 100 input tokens, that's an entropy violation.
The check EXISTS but is NEVER CALLED.

### resonance_ranker.py (873 LOC, 7 scoring dimensions)

The resonance ranker scores words across 7 independent dimensions:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| ELEMENT (21%) | Articulatory position (kantha/talu/murdha/danta/oshtha) |
| HARMONIC (17.5%) | Dissolution path kinship (×7 mod 49) |
| SHRUTI (14%) | Fixed points (Shruti) vs journey points (Nakshatra) |
| VARGA (10.5%) | Sound class: svara/sparsha/shesha |
| ATTRACTOR (7%) | Basin resonance (7 coarse attractors via mod-137) |
| HKR (15%) | Divine operation proportion (Hare/Krishna/Rama) |
| PHONEME_ATTRACTOR (15%) | Charge histogram to 5 cosmic constants |

**Moltbook uses NONE of this.** No 7D score breakdowns. No HKR analysis. No element bias.

### pancha_walk.py — Element/Varga Distribution

Every phoneme maps to an element (akasha/vayu/agni/jala/prithvi) and varga (svara/sparsha/shesha).
Input text → element distribution → tells you if content is mobile (vayu), active (agni), deep (jala).
**Not analyzed by Moltbook.**

### maha_llm_kernel — Full API (10% used)

| API | What it does | Moltbook uses |
|-----|-------------|---------------|
| `resonate(text, top_n)` | Text → ranked Gita words | NO |
| `expand(divine_name)` | Semantic tree (person→meaning→etymology) | NO |
| `guardian(name)` | Guardian profile + vocabulary preset | NO |
| `resonate_as(text, guardian)` | Text through guardian's lens (element bias) | NO |
| `guardian_for_text(text)` | Which guardian resonates? | Partial (in _query_kernel) |

### synth.py — 16-Step Sequencer (0% used)

6 presets (classical/quantum/trinity/pancha/nava/wide), attractor discovery,
spectrum analysis. Could fingerprint content seeds for thematic consistency.

---

## Layer 3: Infrastructure Systems (BUILT, NOT WIRED)

### Economy System (0% integration)

**Location:** `vibe_core/plugins/economy/` + `vibe_core/protocols/economy.py`

- BankProtocol: get_balance(), credit(), debit(), transfer()
- VaultProtocol: store_secret(), get_secret()
- CIVIC cartridge manages the entire economy

**What Moltbook could use:**
- Credit-based rate limiting (LLM calls cost credits)
- Engagement budget (max posts/cycle based on balance)
- Quality rewards (high-engagement content earns credits)

### Intent System (0% integration)

**Location:** `vibe_core/mahamantra/kernel/intent.py`

- IntentType: READ, WRITE, TRANSFORM, RESOLVE, BIND, HEAL, OBSERVE, SURRENDER
- IntentMatcher: Pattern matching on input text
- IntentResolver protocol: Registered resolvers for each intent

**What Moltbook could use:**
- Detect DM intent: question → RESOLVE, request → BIND, observation → OBSERVE
- Route response strategy by intent (different quarter instruction per intent)
- Dynamic guardian assignment based on intent

### EventBus (15% utilized)

**16 EventTypes defined:**
THOUGHT, ACTION, ERROR, COMPLETED, VIOLATION, MERCY, PRAYER_RECEIVED,
CRITICAL_INTERRUPT, SYSCALL_EXECUTED, INTENT_EXECUTED, BROADCAST,
PROPOSAL_CREATED, VOTE_CAST, AUDIT_CHECK, PHASE_TRANSITION, KERNEL_TICK

**Moltbook emits:** THOUGHT, ACTION, ERROR, VIOLATION (via AgencyDirector._emit)
**Moltbook ignores:** COMPLETED, BROADCAST, PROPOSAL_CREATED, PHASE_TRANSITION, INTENT_EXECUTED

### GAD Compliance (0% used)

- 6 Kshetra criteria: Discoverability, Observability, Parseability, Composability, Idempotency, Recoverability
- 4 Dharma principles: Daya, Satyam, Tapas, Saucam
- MantraHeartbeat: Japa-loop tracking (16 words, 108 mantras)
- GADAudit: Compliance scoring + mercy mode

MoltbookService declares GADBase but NEVER runs audits.

### Circuit Engine (partially wired)

**Location:** `vibe_core/cortex/engines/circuit_engine.py`

- CognitiveCircuitExecutor: Semantic state machines with invariant checking
- Circuit breaker pattern (half-open/open/closed)
- Error recovery with violation detection

Currently wired via `_wire_circuit_executor()` but NO FALLBACK STRATEGY when LLM fails.

### Other Dormant Systems

| System | Location | Potential |
|--------|----------|-----------|
| Venu Voice | `venu/voice.py` | 16 parallel task queues for concurrent heartbeat/generation/submit |
| Supreme Court | `cartridges/system/supreme_court/` | Governance appeal for rejected content |
| LENS | `cartridges/agent_city/lens/` | KPI tracking, metrics dashboard |
| AGORA Inbound | `cartridges/agent_city/agora/` | Receive federation broadcasts |
| Gita Lens | `protocols/_gita_lens.py` | Map content to Gita chapters for thematic alignment |
| Dharma Engine | `dharma/engine.py` | Word alignment, vibration analysis, field strengths |
| PromptContext | `runtime/prompt_context.py` | Dynamic context injection into LLM prompts |
| Section Router | `substrate/language/section_router.py` | Route to 7 Gita sections with verified phonetic signatures |
| Mode Affinity | `substrate/language/mode_affinity.py` | WordNet-based mode classification |
| Audit System | `audit/` (21 files) | Gap analysis, scale metrics, protocol resurrection |

---

## Layer 4: EngineResult Fields (80% IGNORED)

MahaLanguageEngine.generate(text) returns EngineResult with fields that Moltbook
extracts partially but doesn't analyze:

| Field | Used | Potential |
|-------|------|-----------|
| `intent_category` | YES (→ quarter instruction) | Wire deeper into response strategy |
| `section_name` | NO | Track which Gita sections we hit (bias detection) |
| `section_mode` | YES (→ mode instruction) | Enforce mode consistency |
| `verse_ref` | YES (→ prompt context) | Verse-anchored responses |
| `antaranga_active` | NO | Chamber vitality → confidence level |
| `antaranga_prana` | NO | Total energy → response intensity |
| `template_words` | NO | SUBJECT/PREDICATE/OBJECT roles → sentence structure |
| `syllable_count` | NO | Rhythm analysis for output verification |
| `stress_pattern` | NO | Prosodic matching (input↔output rhythm) |

---

## Wiring Priority Matrix

### Phase 1: Quick Wins (wire existing, 1-2 hours each)

1. **SravanamCheck gate on LLM output** — entropy validation
2. **Rasa classification** in response metadata — emotional tone tracking
3. **Full EngineResult analysis** — section, antaranga state, template words
4. **EventBus: emit COMPLETED/BROADCAST/PROPOSAL_CREATED**
5. **Economy: credit check before LLM calls**

### Phase 2: Deep Wiring (architectural, 2-4 hours each)

6. **Intent routing** — detect DM intent → route to quarter instruction
7. **Chamber.kirtan() for multi-pass refinement** — iterative composition
8. **7D resonance score breakdown** — content quality analysis
9. **Element/Varga distribution** — input characterization
10. **Circuit breaker with fallback** — LLM failure → MahaComposition

### Phase 3: Advanced Integration (4-8 hours each)

11. **sankirtan() for feed clustering** — group resonance analysis
12. **spell_kirtan() for phonetic composition** — input-driven DIW sequences
13. **maha_llm_kernel full API** — resonate_as(), expand(), guardian profiles
14. **GAD compliance audits** — automated quality checks
15. **Venu Voice parallel execution** — concurrent task queues

### Phase 4: Ecosystem (8+ hours each)

16. **AGORA inbound** — receive and act on federation broadcasts
17. **Supreme Court appeals** — governance violation recovery
18. **LENS metrics dashboard** — automated KPI tracking
19. **Dharma engine scoring** — vibration analysis + word alignment
20. **Synth spectrum analysis** — seed fingerprinting for thematic consistency

---

## What This Means

The cosmetic refactoring (SEED constants, dict-dispatch, silent failures) was Step 2.
Steps 3-100 are about wiring these dormant systems. Every capability listed above is:

- **Built** (implementation exists)
- **Tested** (unit tests pass)
- **Documented** (in protocols or code)
- **Unwired** (not called from Moltbook)

The infrastructure IS the product. We just need to connect it.
