# MOLTBOOK CONTENT INTELLIGENCE — Architecture Reference

**Status:** Re-verified against code 2026-02-23 (post-merge)
**Depends on:** STRATEGY.md (API surface + phases), CLAUDE.md (system architecture)

---

## 1. Five Layers (Bottom → Top)

```
Layer 5  CARTRIDGE     cartridges/agent_city/moltbook/    Thin delegation, Tool protocol
Layer 4  PLUGIN        plugins/moltbook/plugin_main.py    THE heartbeat path, ContentQueue, Circuit Executor
Layer 3  INTELLIGENCE  plugins/moltbook/resonance_proposer.py  Gates + context + LLM + caching
Layer 2  ADAPTER       mahamantra/adapters/moltbook.py    HTTP transport, rate limiting
Layer 1  PROTOCOL      protocols/moltbook.py + moltbook_content.py  Type shapes, ABCs
```

**Rule: Higher layers NEVER call private methods of lower layers.**
Cartridge delegates to Proposer public API via ServiceRegistry. Plugin owns the heartbeat loop.
Proposer owns gate logic. Adapter owns HTTP. Protocol owns types.

---

## 2. Content Pipeline (The ONE Path)

```
INPUT (text from feed/DM/trigger)
  │
  ▼
mahamantra(text) ──────────────────────── Lotus.__call__() → execute_cycle()
  │                                        27-key result dict (cached per text)
  ▼
GATE 1: Guna ──────────────────────────── _guna_mode(result)
  │  TAMAS → REJECT (destructive)          SATTVA = observe only
  │  (POSTS + COMMENTS require RAJAS)      RAJAS = create/write
  ▼
GATE 2: Cell ──────────────────────────── _is_alive(result)
  │  Dead cell → REJECT                    CellLifecycleState check
  ▼
GATE 3: Integrity ─────────────────────── _integrity(result) >= 0.5
  │  Low coherence → REJECT                int 0-21600, normalized to float
  ▼
MahaLanguageEngine.generate(text) ─────── substrate/language/engine.py
  │                                        Lotus → Section Router → MahaComposition
  │                                        → EngineResult (typed, structured, cached per text)
  ▼
CONTEXT ASSEMBLY ──────────────────────── _build_context(engine_result, ...)
  │  EngineResult.resonant_words            Sanskrit + English meanings
  │  EngineResult.template_words            Grammatical skeleton [NOUN/QUALITY/REF]
  │  EngineResult.section_name/mode         Rhetoric type (FILTER/CORE/QUALITY/...)
  │  EngineResult.guardian_name/function    Guardian persona
  │  EngineResult.verse_ref                 Gita verse reference
  │  EngineResult.intent_category           Intent classification
  │  EngineResult.expanded_names            HKR expansions
  │  EngineResult.derivation                Name derivation chain
  │  KnowledgeResolver.compile_context()   Graph-aware context (topic + "moltbook" domain)
  │  moltbook_context resolver              Feed state, DM context, queue, social graph
  ▼
YAML TEMPLATE ─────────────────────────── PromptRegistry.get(key, context=dict)
  │                                        config/prompts/moltbook.yaml
  │                                        {slot} filled via .format(**context)
  ▼
LLM ───────────────────────────────────── LLMProvider.invoke(prompt, model, ...)
  │                                        via get_llm_provider() from runtime/providers/factory.py
  │                                        NOT LLMEngine.speak() (that's hardcoded template trash)
  ▼
ContentProposal ───────────────────────── TypedDict with routing metadata
  │                                        content, type, post_id, priority (from KG)
  ▼
ContentQueue ──────────────────────────── Bounded FIFO (max 50), priority-sorted
  │                                        drain(limit=3) per heartbeat
  │                                        Failed proposals: exponential backoff (2s, 4s), max 2 retries
  ▼
MoltbookService ───────────────────────── GAD-000 compliant service wrapper
  │                                        Guna enforcement + KG constraint check + audit trail
  ▼
MoltbookClient ────────────────────────── HTTP POST to moltbook.com/api/v1
                                           Rate-limited, challenge-solver equipped
```

**Without LLM:** Three-tier fallback:
1. **MahaComposition** — 5-scorer ranked English pipeline (`compose(pipeline_result, text)`)
2. **Kirtan rendering** — `render(pipeline_result)` → guardian persona + smaranam + verse ref
3. **None** — only if no pipeline_result at all

This is the system's TONGUE — not "no output", but resonance rendering without LLM enrichment.

---

## 3. Guna I/O Policy (BG 14.5)

Every Moltbook API call is classified by Guna. This is NOT configurable.

| Guna | Mode | Operations | Policy |
|------|------|-----------|--------|
| SATTVA | READ | heartbeat, search, feed, profile, DMs read, comments read | Pass through |
| RAJAS | WRITE | post, comment, DM send, follow, vote, subscribe | Log + execute |
| TAMAS | DELETE | delete_post, unfollow, unsubscribe | **BLOCKED** (PermissionError) |

**Content gating by guna (resonance_proposer.py):**
- TAMAS text → REJECT all content proposals (DMs, comments, posts)
- SATTVA text → DM replies OK, Comments REJECTED, Posts REJECTED
- RAJAS text → All content types OK

Both **posts and comments** require RAJAS. DM replies only check for non-TAMAS.

The guna is **position-based** (text hash → mantra position → guardian → guna),
not semantic analysis of content. "buy my token" can get SATTVA if its hash
lands on a SATTVA position. This is by design — the mantra position determines
the guardian lens, not keyword matching.

**Knowledge Graph constraint check** (`_enforce_guna`): Additionally queries
`knowledge/moltbook/platform.yaml` constraints via KnowledgeResolver.

---

## 4. Heartbeat Path (THE Integration Point)

```
mahamantra.tick() (Singularity)
  → _broadcast(TickState) (Narada dispatch)
    → MoltbookPlugin._on_mahamantra_tick()
       │
       _do_heartbeat() [debounce: min 2s between fires]
       │
       every 16 ticks (_TICKS_PER_HEARTBEAT):
       ├── _process_dm_requests()          Check pending DM requests
       ├── _process_inbound_dms()          Fetch DMs → Gateway → propose replies
       ├── _follow_back(sender)            Social reciprocity
       ├── _drain_content_queue()          Execute up to 3 queued proposals
       ├── _monitor_queue_health()         Warn on overflow
       │
       every 64 ticks (feed_interval × 16, configurable):
       ├── _analyze_feed()                 Read feed → analyze → propose engagement + comments
       │
       every 384 ticks (post_interval × 16, configurable):
       ├── _maybe_create_post()            Autonomous posts from trending feed topics
       │
       every 128 ticks (reply_check_interval × 16):
       ├── _check_own_comment_replies()    Monitor replies → propose follow-ups
       │
       every ~768 ticks (profile_update_interval × 16):
       ├── _update_profile()               Karma, followers, activity stats in bio
       │
       on first heartbeat + periodically:
       ├── _discover_submolts()            Subscribe to communities
       │
       every profile_update_interval:
       └── _trim_memory()                  Cap seen IDs + flush proposer caches
```

The plugin wires itself to Mahamantra at boot via `register_listener()`.
No separate heartbeat. No polling loop. ONE path through the Singularity tick.

**on_pulse()** kept for backward compat — delegates to same `_do_heartbeat()`.
Debounce guard prevents double-fire if both tick and pulse trigger.

**Boot sequence:**
1. Create MoltbookClient (offline or live)
2. Register MoltbookService (GAD-000) in ServiceRegistry
3. Resolve agent name from profile
4. Boot ResonanceProposer + register moltbook_context in PromptContext
5. Register ContentProposalProtocol in ServiceRegistry
6. Restore persisted queue + seen IDs
7. Wire Circuit Executor (MOLTBOOK_CONTENT_V1)
8. Wire AGORA broadcast channel
9. Wire to Mahamantra heartbeat

**Shutdown:** Persist queue + seen IDs → unregister listener.

---

## 5. Infrastructure Wiring Status

### 5.1 MahaLanguageEngine (substrate/language/engine.py) — WIRED
Single path: Lotus → Section Router → MahaComposition → EngineResult.
Called by `ResonanceProposer._generate(text)`. Cached per text.

EngineResult fields (all used in `_build_context()`):
- `.output` — 5-scorer composed English (Prana + Rhythm + Semantic + Mode + State)
- `.guardian_name`, `.guardian_function` — identity
- `.verse_ref` — Gita reference
- `.section_name`, `.section_mode` — rhetoric routing
- `.resonant_words` — tuples of (sanskrit, meaning, score)
- `.template_words` — tuples of (sanskrit, meaning, grammatical_role)
- `.intent_category` — intent classification
- `.expanded_names` — HKR name expansions
- `.derivation` — name derivation chain

### 5.2 MahaComposition (adapters/composition.py) — WIRED (LLM-free fallback)
5 pluggable scorers, additive ranking:
1. **PranaScorer** — Antaranga chamber prana at RAMA coords
2. **RhythmScorer** — Syllable vector ↔ mantra grid alignment
3. **SemanticScorer** — WordNet graph distance to input
4. **ModeScorer** — Guna ↔ WordNet mode affinity
5. **StateScorer** — System state affinity

Used as **primary LLM-free fallback** in `_compose()`. If LLM fails/unavailable,
`MahaComposition().compose(pipeline_result, user_input)` produces ranked English.

### 5.3 WordNet Bridge (substrate/encoding/wordnet_bridge.py) — INDIRECT
- 4,259 synsets from Open English WordNet, precomputed
- 3,556 Gita words mapped to synsets
- Three-layer scoring: EXACT (token match), GRAPH (hypernym Jaccard), MORPH (stem overlap)
- **Zero runtime NLTK dependency** — all baked into data/wordnet_bridge.json
- Used by SemanticScorer and ModeScorer inside MahaComposition

### 5.4 Semantic Index (substrate/encoding/semantic_index.py) — INDIRECT
7 reverse indices over 4,127 Gita words.
Used by MahaComposition scorers and resonance_ranker.

### 5.5 MahaLLM Kernel (substrate/encoding/maha_llm_kernel.py) — NOT WIRED
- `expand(name, depth=3)` — Semantic tree expansion (HKR operations on coordinates)
- `resonate(text, top_n=5)` — Find resonant Gita words for any input
- `guardian(name)` — Guardian's complete semantic profile
- `resonate_as(text, guardian)` — Force specific Guardian lens
- **NOT wired to Moltbook proposer** — available but unused
- Could enrich `_build_context()` with deeper guardian profiles and HKR expansions

### 5.6 Kirtan Renderer (render.py) — WIRED (last-resort fallback)
- `render(result)` — Pure resonance rendering from VM result
- Used as **last-resort fallback** in `_compose()` when both LLM and MahaComposition fail
- `kirtan_chat(message)` — Full chat path with LLM enrichment (separate from proposer)
- The proposer follows the same LLM pattern: `get_llm_provider() → provider.invoke()`

### 5.7 ContentQueue (protocols/moltbook_content.py) — WIRED
- Bounded FIFO, max 50 proposals
- `enqueue(proposal) → bool` (drops if full)
- `drain(limit) → List[ContentProposal]`
- Stats: queued, total_enqueued, total_drained, total_dropped
- **Persisted** to disk on shutdown, restored on boot
- Failed proposals re-enqueued with exponential backoff (2s, 4s), max 2 retries

### 5.8 MoltbookResolver (services/moltbook_resolver.py) — WIRED
- Intent routing via MantraKernel
- `MantraIntent(READ, "moltbook/feed")` → resolver reads feed
- `MantraIntent(WRITE, "moltbook/post")` → resolver creates post
- Tick listener: queues DM check intent on every downbeat (position 0)

### 5.9 Knowledge Graph (knowledge/moltbook/platform.yaml) — WIRED
- Content type priorities: DM=9, Post=7, Comment=6, Vote=4 (via `_kg_priority()`)
- Platform constraints checked in `_enforce_guna()` (6 hard/soft constraints)
- Topic + "moltbook" domain context in `_knowledge_context()` for prompts

### 5.10 Circuit Executor (cortex/engines/circuit_engine.py) — WIRED
- MOLTBOOK_CONTENT_V1 circuit: SHABDA → ARTHA → PRATYAYA → KARMA → SUCCESS
- `execute_content_circuit()` on plugin — full state-machine content generation
- MetaCircuitManager adds TASK_LEDGER and ERROR_RECOVERY as active observers
- Degrades gracefully if cortex unavailable

### 5.11 AGORA Broadcast (cartridges/agent_city/agora/) — WIRED
- Post/comment content broadcast to AGORA for federation awareness
- One-way: Moltbook → AGORA → [PULSE, LENS, AMBASSADOR, ...]
- Degrades gracefully if AGORA not registered

### 5.12 MoltbookService (plugin_main.py) — WIRED, GAD-000 Compliant
- Wraps MoltbookClient with MoltbookProtocol ABC
- 6 Kshetra criteria: discover(), get_state(), is_healthy(), is_idempotent, detect_drift(), parseability
- 4 Dharma principles: Daya (input validation), Satyam (verified output), Tapas (rate limits), Saucam (auth-only I/O)
- Guna enforcement + KG constraint check on every operation
- RAJAS operations logged with timestamp audit trail

---

## 6. Known Problems (Current State)

### 6.1 Engine Output Quality
MahaComposition.compose() produces word-level assembly. The 5 scorers rank
individual words, but the assembly step (meaning-based ordering) can produce
sequences that lack grammatical coherence. This is the "word salad" problem.

**Root cause:** The composition pipeline ranks INDIVIDUAL words but doesn't
score SEQUENCES. The meaning-based assembly (`_assemble_by_meaning`) orders
by score, not by grammar.

**The template_words with grammatical roles [NOUN/QUALITY/REF/PREP/PARTICLE]
exist specifically to provide grammatical skeleton.** These should constrain
the assembly, but currently they're only used as context for the LLM, not
as structural constraints for the composition itself.

### 6.2 MahaLLM Kernel Unwired
`maha_llm_kernel.py` provides `expand()`, `resonate()`, `guardian()`, `resonate_as()` —
deeper semantic operations than the pipeline produces. These could enrich
`_build_context()` with expanded guardian profiles and HKR semantic trees.
Currently unused by any moltbook code.

### 6.3 No End-to-End LLM Test
Tests use `_TestProvider` (deterministic stub). No test verifies actual content
quality with a real LLM provider. Need integration test with API key.

---

## 7. Resolved Problems (from previous versions)

- **6.2 (old) Cartridge Spaghetti** — FIXED. Cartridge rewritten as thin delegation layer (202 LOC). No private method calls. Uses ServiceRegistry.
- **6.3 (old) content_tool.py Creates New Proposer Per Call** — FIXED. Uses ServiceRegistry to get existing proposer instance.
- **6.4 (old) "No LLM = No Output"** — FIXED. Three-tier fallback: LLM → MahaComposition → kirtan rendering.

---

## 8. File Map

| Purpose | File | LOC | Owner |
|---------|------|-----|-------|
| Types + ABC | `protocols/moltbook.py` | 369 | Protocol layer |
| Content proposals | `protocols/moltbook_content.py` | 361 | Protocol layer |
| HTTP transport | `mahamantra/adapters/moltbook.py` | 357 | Adapter layer |
| Plugin (heartbeat) | `plugins/moltbook/plugin_main.py` | 1689 | Plugin layer |
| Intelligence | `plugins/moltbook/resonance_proposer.py` | 585 | Intelligence layer |
| Intent routing | `services/moltbook_resolver.py` | 347 | Service layer |
| Cartridge | `cartridges/agent_city/moltbook/cartridge_main.py` | 202 | Cartridge layer |
| Tool | `cartridges/agent_city/moltbook/tools/content_tool.py` | 117 | Tool layer |
| Circuit | `playbook/circuits/moltbook_content.yaml` | 293 | Circuit layer |
| YAML prompts | `config/prompts/moltbook.yaml` | 77 | Config |
| Governance | `cartridges/agent_city/moltbook/steward.json` | — | Governance |

### Composition Infrastructure (used by proposer)

| Purpose | File | LOC |
|---------|------|-----|
| Language Engine | `substrate/language/engine.py` | 164 |
| Composer (5 scorers) | `substrate/language/composer.py` | 411 |
| Composition adapter | `adapters/composition.py` | 436 |
| WordNet bridge | `substrate/encoding/wordnet_bridge.py` | 313 |
| Semantic index | `substrate/encoding/semantic_index.py` | 584 |
| Resonance ranker | `substrate/encoding/resonance_ranker.py` | 873 |
| Seed-to-words | `substrate/encoding/seed_to_words.py` | 390 |
| MahaLLM kernel | `substrate/encoding/maha_llm_kernel.py` | 465 |
| Kirtan renderer | `render.py` | 230 |

### Tests

| File | Tests | Coverage |
|------|-------|---------|
| `plugins/moltbook/tests/test_moltbook_plugin.py` | ~100 | Plugin lifecycle, guna enforcement, heartbeat |
| `plugins/moltbook/tests/test_resonance_proposer.py` | 80 | Gates, context, compose, proposals, caching |
| `services/tests/test_moltbook_resolver.py` | ~35 | Intent routing, tick listener |
| `mahamantra/tests/adapters/test_moltbook.py` | ~120 | Rate limits, challenges, offline mock |

---

## 9. Rules

1. **No new dispatch mechanisms.** Plugin heartbeat is THE path.
2. **No private method calls across layers.** Use public API or ServiceRegistry.
3. **No duplicate gate logic.** Proposer owns gates. Cartridge delegates.
4. **No "offline_mode" confusion.** offline_mode = no HTTP to Moltbook. LLM is separate.
5. **Three-tier fallback.** LLM → MahaComposition → kirtan rendering. Never `None` when pipeline_result exists.
6. **No new ResonanceProposer() per call.** Get from ServiceRegistry.
7. **Dense context, no instructions.** Quality comes from context density, not "sei authentisch".
8. **LLMProvider.invoke(), NOT LLMEngine.speak().** speak() is hardcoded template trash.
9. **Verify against code.** This doc was re-verified 2026-02-23. It will rot.
