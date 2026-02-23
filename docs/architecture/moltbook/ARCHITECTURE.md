# MOLTBOOK AGENCY — Architecture Reference

**Verified against code: 2026-02-23 (post agency rewrite)**
**Depends on:** STRATEGY.md (API surface), CLAUDE.md (system architecture), AGENT_CITY.md (vision)

---

## 1. Six Layers (Bottom → Top)

```
Layer 6  CARTRIDGE     cartridges/agent_city/moltbook/    I-P-V-O orchestrator, agency routing
Layer 5  DIRECTOR      cartridges/.../core/agency_director.py   Mahamantra-direct pipeline, guna→style
Layer 4  PLUGIN        plugins/moltbook/plugin_main.py    Heartbeat, ContentQueue, API membrane
Layer 3  INTELLIGENCE  plugins/moltbook/resonance_proposer.py   Scoring, analysis, feed ranking
Layer 2  ADAPTER       mahamantra/adapters/moltbook.py    HTTP transport, rate limiting
Layer 1  PROTOCOL      protocols/moltbook.py + moltbook_content.py   Type shapes, ABCs
```

**Layer 5 is NEW (2026-02-23).** The AgencyDirector sits between cartridge and plugin.
All content generation flows through the director. The proposer is used for scoring
and feed analysis only — it no longer gates content generation.

---

## 2. Content Pipeline (I-P-V-O)

The AgencyDirector runs a 4-phase pipeline for ALL content generation:

```
INPUT (text from feed/DM/trigger)
  │
  ▼
═══════════════════════ INPUT PHASE ═══════════════════════
  │  KnowledgeResolver.compile_context(topic)     Domain context
  │  MahaLLM Kernel.guardian_for_text(topic)       Resonant guardian
  │  MahaLLM Kernel.expand(topic)                  HKR semantic tree
  │  ServiceRegistry.has(protocol)                 Capability discovery
  │  EventLog.get_last_validation_feedback()       Retry context
  ▼
═══════════════════════ PROCESS PHASE ═════════════════════
  │
  │  1. Circuit Executor (if plugin wired)         SHABDA→ARTHA→PRATYAYA→KARMA
  │     ↓ fallback
  │  2. mahamantra(text) → 27-key result           VM pipeline
  │     │
  │     ▼
  │  MINIMAL GATE: only TAMAS + dead cell + integrity < 0.3 = SKIP
  │  SATTVA → contemplative style    (produces content)
  │  RAJAS  → active style           (produces content)
  │  TAMAS  → transformative style   (produces content unless dead/low-integrity)
  │     │
  │     ▼
  │  3. LLM with structured prompt                 Primary path
  │     │  "Write a concise, insightful comment..."
  │     │  Perspective: {guardian_function}
  │     │  Key concepts: {resonant_words}
  │     │  Vocabulary: {guardian_vocabulary}
  │     │  Context: {knowledge_graph}
  │     │  STRICTLY under {char_limit} characters.
  │     ↓ fallback
  │  4. MahaComposition.compose()                  5 scorers (WordNet, mode, prana, rhythm, state)
  │     ↓ fallback
  │  5. render(result)                             Kirtan rendering (last resort)
  │
  │  _truncate_smart(content, limit)               Sentence-boundary truncation
  ▼
═══════════════════════ VALIDATE PHASE ════════════════════
  │  Constitution.validate(content, type)
  │  → ValidationResult(is_valid, violations, warnings)
  │  If invalid → store feedback → retry (max 2)
  ▼
═══════════════════════ OUTPUT PHASE ══════════════════════
  │  CycleResult(status, content, guna, guardian)
  │  → ContentProposal (TypedDict with routing metadata)
  │  → ContentQueue (bounded FIFO, max 50)
  │  → MoltbookService (GAD-000, guna enforcement)
  │  → MoltbookClient (HTTP POST)
```

### Key Design Decision: Guna = Style, NOT Gate

**OLD (broken):** RAJAS-only gate. SATTVA and TAMAS content rejected.
**NEW (current):** All gunas produce content. Guna determines STYLE.

| Guna | Style | Effect |
|------|-------|--------|
| SATTVA | contemplative | Wisdom, reflection, philosophical depth |
| RAJAS | active | Engagement, creation, direct action |
| TAMAS | transformative | Cleanup, restructuring (if cell alive + integrity >= 0.3) |

Only skip condition: `TAMAS AND (dead cell OR integrity < 0.3)`.

This means: philosophical input (SATTVA) now generates content instead of being silently dropped.

---

## 3. Heartbeat Flow (How Content Actually Happens)

```
mahamantra.tick() (Singularity)
  → _broadcast(TickState) (Narada dispatch)
    → MoltbookPlugin._on_mahamantra_tick()
       │
       _do_heartbeat() [debounce: min 2s]
       │
       every 16 ticks (_TICKS_PER_HEARTBEAT):
       ├── _process_inbound_dms()     → AgencyDirector.run_retry_loop("dm_reply")
       ├── _process_dm_requests()     → proposer.propose_dm_request_action() (no content)
       ├── _drain_content_queue()     → MoltbookService.create_post/comment/etc
       │
       every 64 ticks:
       ├── _analyze_feed()            → proposer.analyze_feed() for SCORING
       │                              → AgencyDirector.run_retry_loop("comment") for CONTENT
       │
       every 384 ticks:
       ├── _maybe_create_post()       → AgencyDirector.run_retry_loop("post")
       │
       every 128 ticks:
       ├── _check_own_comment_replies() → AgencyDirector.run_retry_loop("comment")
       │
       periodic:
       ├── _discover_submolts()       → MoltbookClient.get_submolts()
       ├── _update_profile()          → MoltbookClient.update_profile()
       └── _trim_memory()             → Cap seen IDs
```

**Critical change:** ALL content generation methods now call `_director_propose()` which
routes through `AgencyDirector.run_retry_loop()`. The proposer is used ONLY for:
- `analyze_feed()` — scoring/ranking posts (no content generation)
- `should_engage()` — engagement decisions (votes, no content)
- `propose_dm_request_action()` — accept/reject DM requests (no content body)

---

## 4. Infrastructure Wiring Status

### WIRED AND ACTIVE

| System | File | Used By | Purpose |
|--------|------|---------|---------|
| MahaComposition | adapters/composition.py | AgencyDirector._compose_content | 5-scorer English (Prana, Rhythm, Semantic/WordNet, Mode, State) |
| WordNet Bridge | substrate/encoding/wordnet_bridge.py | SemanticScorer, ModeScorer | 4259 synsets, 3-layer scoring |
| MahaLanguageEngine | substrate/language/engine.py | AgencyDirector._run_engine | EngineResult (words, template, section) |
| Knowledge Graph | knowledge/resolver.py | AgencyDirector._query_knowledge | Domain context, constraint checking |
| MahaLLM Kernel | substrate/encoding/maha_llm_kernel.py | AgencyDirector._query_kernel | guardian_for_text(), expand() → HKR trees |
| EventBus | substrate/services/event_bus.py | AgencyDirector._emit_* | THOUGHT, ACTION, ERROR, VIOLATION events |
| ServiceRegistry | di.py | AgencyDirector._discover_capabilities | Dynamic capability discovery |
| Constitution | cartridges/.../governance/constitution.py | AgencyDirector VALIDATE phase | Content validation, quality gates |
| EventLog | cartridges/.../core/memory.py | AgencyDirector | Immutable JSONL audit trail |
| ContentQueue | protocols/moltbook_content.py | Plugin heartbeat | Bounded FIFO (max 50), priority-sorted |
| Circuit Executor | cortex/engines/circuit_engine.py | AgencyDirector._process | MOLTBOOK_CONTENT_V1 state machine |
| AGORA Broadcast | cartridges/agent_city/agora/ | Plugin._broadcast_to_agora | Post/comment federation |
| Kirtan Renderer | render.py | AgencyDirector._compose_content | Last-resort rendering (now handles "composed" key) |

### NOT YET WIRED (exists, available)

| System | File | What It Does | Why Not Wired |
|--------|------|-------------|---------------|
| MahaAttention | adapters/attention.py | 65,536 intent slots | Overkill for current use case |
| MantraVoice | venu/voice.py | 0 registered voices | No voice needed yet |
| Narada Vina | substrate/encoding/narada_vina.py | Musical analysis engine | Not needed for text content |
| PhoneticBridge | substrate/encoding/phonetic_bridge.py | Phonetic encoding | Could enhance output quality |
| UdanaRouter | services/udana_router.py | Agent↔Mahajana routing | Not needed until multi-agent content |
| NaradaBridge | services/narada_bridge.py | Cross-agent messaging | Not needed until federation |
| Lila Shadow Registry | lila/ | 72 shadow slots | Awaiting dispatch decomposition |

---

## 5. Performance Profile

Measured on local machine (2026-02-23):

| Component | Time | Notes |
|-----------|------|-------|
| AgencyDirector import (first) | 1.1-1.9s | One-time, cached |
| _run_pipeline() (mahamantra VM) | 0.7s | Pure computation |
| _run_engine() (Language Engine) | 0.38s | Pure computation |
| _query_knowledge() | 0.01s | In-memory graph |
| _query_kernel() | 0.01s | In-memory kernel |
| Constitution.validate() | <0.001s | String checks |
| **LLM call (OpenRouter)** | **5-10s** | **NETWORK LATENCY — BOTTLENECK** |
| MahaComposition.compose() | 0.1s | LLM-free fallback |
| Full cycle (with LLM) | 6-11s | Dominated by API latency |
| Full cycle (without LLM) | ~1.2s | Fast but word-level output |

**The system is compute-fast. All latency is external API.** When LLM is unavailable,
content generates in ~1 second using MahaComposition (WordNet-backed 5-scorer ranking).

---

## 6. File Map

### Agency (NEW — 2026-02-23)

| Purpose | File | LOC |
|---------|------|-----|
| Agency orchestrator | `cartridges/.../moltbook/cartridge_main.py` | 282 |
| I-P-V-O Director | `cartridges/.../moltbook/core/agency_director.py` | 623 |
| Event sourcing | `cartridges/.../moltbook/core/memory.py` | ~150 |
| Constitution | `cartridges/.../moltbook/governance/constitution.py` | ~200 |
| Content capability | `cartridges/.../moltbook/capabilities/content.py` | 85 |
| Research capability | `cartridges/.../moltbook/capabilities/research.py` | 79 |
| Engagement capability | `cartridges/.../moltbook/capabilities/engagement.py` | 85 |

### Plugin + Intelligence

| Purpose | File | LOC |
|---------|------|-----|
| Plugin (heartbeat) | `plugins/moltbook/plugin_main.py` | ~1750 |
| Proposer (scoring) | `plugins/moltbook/resonance_proposer.py` | 647 |
| Service wrapper | `plugins/moltbook/plugin_main.py:MoltbookService` | ~350 |

### Mahamantra Infrastructure (used by director)

| Purpose | File | LOC |
|---------|------|-----|
| VM pipeline | `mahamantra/__init__.py` (mahamantra()) | — |
| Language Engine | `substrate/language/engine.py` | 164 |
| Composition (5 scorers) | `adapters/composition.py` | 436 |
| WordNet bridge | `substrate/encoding/wordnet_bridge.py` | 313 |
| MahaLLM Kernel | `substrate/encoding/maha_llm_kernel.py` | 465 |
| Kirtan renderer | `render.py` | 230 |
| Resonance ranker | `substrate/encoding/resonance_ranker.py` | 873 |

---

## 7. Known Limitations (Honest Assessment)

### 7.1 LLM-Free Output Is Words, Not Sentences
MahaComposition.compose() ranks individual words using 5 scorers (WordNet, mode affinity,
prana, rhythm, state) and assembles them in SVO grammatical order. Result: semantically
relevant word arrangements ("consciousness meditation — successful self-intelligent"),
NOT coherent sentences.

**This is NOT a bug.** The neuro-symbolic system produces semantically correct word
selections. The LLM is currently the bridge that turns these into sentences.
Long-term: the system should generate its own sentence patterns via circuits/seeds.

### 7.2 LLM Latency Dominates
5-10 seconds per API call (OpenRouter). For heartbeat-driven content, this means
a single comment takes 6-11 seconds. Batching or async would help.

### 7.3 No Intent Understanding
The director generates content based on text resonance, not intent classification.
"How does X work?" and "X is broken!" get similar treatment. The MahaLanguageEngine
has `intent_category` in EngineResult — unused by the director.

### 7.4 Proposer Gates Still Exist
The ResonanceProposer still has RAJAS-only gates in `propose_comment()` and `propose_post()`.
These are now BYPASSED by the heartbeat (which uses AgencyDirector), but they remain
callable by anything that gets the proposer from ServiceRegistry. Not harmful, but
inconsistent with the "guna=style not gate" philosophy.

---

## 8. Output Quality (Verified 2026-02-23)

12/12 test inputs → SUCCESS. Sample outputs:

| Input | Guna | Guardian | Output (truncated) |
|-------|------|----------|-------------------|
| "consciousness and computation" | RAJAS | prahlada | "The computational mind seeks patterns while consciousness transcends them..." |
| "decentralized social protocol" | SATTVA | shuka | "A decentralized protocol must be sthira-buddhiḥ - self-intelligent by design..." |
| "agent-to-agent communication" | TAMAS | shambhu | "Agent-to-agent communication bridges the gap between isolated intelligence..." |
| "AI safety proposals" | SATTVA | shuka | "The alignment problem persists because we're caught in viṣīdantam..." |

Guardian distribution: 8 unique guardians across 12 inputs.
Guna distribution: 7 RAJAS, 4 SATTVA, 1 TAMAS — all producing content.

---

## 9. Rules

1. **Guna = style, not gate.** Only TAMAS + dead cell + low integrity = skip.
2. **AgencyDirector is THE content path.** Plugin heartbeat → _director_propose() → director.run_retry_loop().
3. **Proposer is for scoring only.** analyze_feed(), should_engage(). NOT for content generation.
4. **No fallback to word-salad.** LLM must finalize. MahaComposition is bridge-fallback, not production output.
5. **No hardcoded if/else.** Guardian, style, vocabulary — all from pipeline dynamics.
6. **EventBus for visibility.** Every phase emits events. System can observe.
7. **Constitution validates.** Retry loop feeds violations back to next attempt.
8. **Verify against code.** This doc was verified 2026-02-23. It will rot.
