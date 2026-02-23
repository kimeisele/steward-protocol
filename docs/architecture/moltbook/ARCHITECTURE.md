# MOLTBOOK CONTENT INTELLIGENCE — Architecture Reference

**Status:** Verified against code 2026-02-23
**Depends on:** STRATEGY.md (API surface + phases), CLAUDE.md (system architecture)

---

## 1. Five Layers (Bottom → Top)

```
Layer 5  CARTRIDGE     cartridges/agent_city/moltbook/    Task routing, Tool protocol
Layer 4  PLUGIN        plugins/moltbook/plugin_main.py    THE heartbeat path, ContentQueue
Layer 3  INTELLIGENCE  plugins/moltbook/resonance_proposer.py  Gates + context + LLM
Layer 2  ADAPTER       mahamantra/adapters/moltbook.py    HTTP transport, rate limiting
Layer 1  PROTOCOL      protocols/moltbook.py + moltbook_content.py  Type shapes, ABCs
```

**Rule: Higher layers NEVER call private methods of lower layers.**
Cartridge delegates to Plugin/Proposer public API. Plugin owns the heartbeat loop.
Proposer owns gate logic. Adapter owns HTTP. Protocol owns types.

---

## 2. Content Pipeline (The ONE Path)

```
INPUT (text from feed/DM/trigger)
  │
  ▼
mahamantra(text) ──────────────────────── Lotus.__call__() → execute_cycle()
  │                                        27-key result dict
  ▼
GATE 1: Guna ──────────────────────────── _guna_mode(result)
  │  TAMAS → REJECT (destructive)          SATTVA = observe, RAJAS = create
  │  (POSTS require RAJAS specifically)
  ▼
GATE 2: Cell ──────────────────────────── _is_alive(result)
  │  Dead cell → REJECT                    CellLifecycleState check
  ▼
GATE 3: Integrity ─────────────────────── _integrity(result) >= 0.5
  │  Low coherence → REJECT                int 0-21600, normalized to float
  ▼
MahaLanguageEngine.generate(text) ─────── substrate/language/engine.py
  │                                        Lotus → Section Router → MahaComposition
  │                                        → EngineResult (typed, structured)
  ▼
CONTEXT ASSEMBLY ──────────────────────── _build_context(engine_result, ...)
  │  EngineResult.resonant_words            Sanskrit + English meanings
  │  EngineResult.template_words            Grammatical skeleton [NOUN/QUALITY/REF]
  │  EngineResult.section_name/mode         Rhetoric type (FILTER/CORE/QUALITY/...)
  │  EngineResult.guardian_name/function    Guardian persona
  │  EngineResult.verse_ref                 Gita verse reference
  │  KnowledgeResolver.compile_context()   Graph-aware context
  │  moltbook_context resolver              Feed state, DM context, queue
  ▼
YAML TEMPLATE ─────────────────────────── PromptRegistry.get(key, context=dict)
  │                                        config/prompts/moltbook.yaml
  │                                        {slot} filled via .format(**context)
  ▼
LLM ───────────────────────────────────── LLMProtocol.speak(agent, context, input)
  │                                        Dense context → short output
  ▼
ContentProposal ───────────────────────── TypedDict with routing metadata
  │                                        content, type, post_id, guna, guardian
  ▼
ContentQueue ──────────────────────────── Bounded FIFO (max 50)
  │                                        drain(limit=3) per heartbeat
  ▼
MoltbookClient ────────────────────────── HTTP POST to moltbook.com/api/v1
                                           Rate-limited, challenge-solver equipped
```

**Without LLM:** Pipeline still runs. `render(result)` produces kirtan rendering
(guardian persona + smaranam words + verse ref). This is the system's TONGUE —
not "no output", but pure resonance rendering without enrichment.

---

## 3. Guna I/O Policy (BG 14.5)

Every Moltbook API call is classified by Guna. This is NOT configurable.

| Guna | Mode | Operations | Policy |
|------|------|-----------|--------|
| SATTVA | READ | heartbeat, search, feed, profile, DMs read, comments read | Pass through |
| RAJAS | WRITE | post, comment, DM send, follow, vote, subscribe | Log + execute |
| TAMAS | DELETE | delete_post, unfollow, unsubscribe | **BLOCKED** (PermissionError) |

**Content gating by guna:**
- TAMAS text → REJECT all content proposals
- SATTVA text → Comments OK, Posts REJECTED (posts require RAJAS = creative energy)
- RAJAS text → All content types OK

The guna is **position-based** (text hash → mantra position → guardian → guna),
not semantic analysis of content. "buy my token" can get SATTVA if its hash
lands on a SATTVA position. This is by design — the mantra position determines
the guardian lens, not keyword matching.

---

## 4. Heartbeat Path (THE Integration Point)

```
mahamantra.tick() (Singularity)
  → _broadcast(TickState) (Narada dispatch)
    → MoltbookPlugin._on_mahamantra_tick()
       │
       every 16 ticks (_TICKS_PER_HEARTBEAT):
       ├── _process_dm_requests()     Check pending DM requests
       ├── _process_inbound_dms()     Fetch DMs → Gateway → propose replies
       ├── _drain_content_queue()     Execute up to 3 queued proposals
       │
       every 64 ticks (_FEED_INTERVAL × 16):
       └── _analyze_feed()            Read feed → analyze → propose engagement
```

The plugin wires itself to Mahamantra at boot via `register_listener()`.
No separate heartbeat. No polling loop. ONE path through the Singularity tick.

---

## 5. Infrastructure Already Built (USE, Don't Rebuild)

### 5.1 MahaLanguageEngine (substrate/language/engine.py)
Single path: Lotus → Section Router → MahaComposition → EngineResult.

EngineResult fields:
- `.output` — 5-scorer composed English (Prana + Rhythm + Semantic + Mode + State)
- `.guardian_name`, `.guardian_function` — identity
- `.verse_ref` — Gita reference
- `.section_name`, `.section_mode` — rhetoric routing
- `.resonant_words` — tuples of (sanskrit, meaning, score)
- `.template_words` — tuples of (sanskrit, meaning, grammatical_role)

### 5.2 MahaComposition (adapters/composition.py)
5 pluggable scorers, additive ranking:
1. **PranaScorer** — Antaranga chamber prana at RAMA coords
2. **RhythmScorer** — Syllable vector ↔ mantra grid alignment
3. **SemanticScorer** — WordNet graph distance to input
4. **ModeScorer** — Guna ↔ WordNet mode affinity
5. **StateScorer** — System state affinity

Output: Meaning-based assembly of scored words. NOT random word salad.
If the output IS word salad → the scoring weights or input context is wrong.

### 5.3 WordNet Bridge (substrate/encoding/wordnet_bridge.py)
- 4,259 synsets from Open English WordNet, precomputed
- 3,556 Gita words mapped to synsets
- Three-layer scoring: EXACT (token match), GRAPH (hypernym Jaccard), MORPH (stem overlap)
- **Zero runtime NLTK dependency** — all baked into data/wordnet_bridge.json

### 5.4 Semantic Index (substrate/encoding/semantic_index.py)
7 reverse indices over 4,127 Gita words:
- by_rama_position, by_element, by_varga, by_shruti
- by_harmonic_target, by_meaning_word, by_basin
- LexiconVectorCache: 14 precomputed arrays for O(1) scoring

### 5.5 MahaLLM Kernel (substrate/encoding/maha_llm_kernel.py)
- `expand(name, depth=3)` — Semantic tree expansion (HKR operations on coordinates)
- `resonate(text, top_n=5)` — Find resonant Gita words for any input
- `guardian(name)` — Guardian's complete semantic profile
- `resonate_as(text, guardian)` — Force specific Guardian lens
- **NOT wired to Moltbook proposer** — available but unused

### 5.6 Kirtan Renderer (render.py)
- `render(result)` — Pure resonance rendering from VM result
- `kirtan_chat(message)` — Full chat path with optional LLM enrichment
- `_build_llm_prompt()` — Structured prompt using VM result as context
- **Pattern for LLM prompts already solved here** — the proposer should follow this pattern

### 5.7 ContentQueue (protocols/moltbook_content.py)
- Bounded FIFO, max 50 proposals
- `enqueue(proposal) → bool` (drops if full)
- `drain(limit) → List[ContentProposal]`
- Stats: queued, total_enqueued, total_drained, total_dropped

### 5.8 MoltbookResolver (services/moltbook_resolver.py)
- Intent routing via MantraKernel
- `MantraIntent(READ, "moltbook/feed")` → resolver reads feed
- `MantraIntent(WRITE, "moltbook/post")` → resolver creates post
- Tick listener: queues DM check intent on every downbeat (position 0)

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

### 6.2 Cartridge Spaghetti
The cartridge_main.py (378 LOC) duplicates what plugin_main.py (804 LOC) already does:
- Calls private `_run_pipeline()`, `_generate()` on proposer
- Imports private gate functions (`_guna_mode`, `_integrity`, `_should_skip`)
- Creates its own MoltbookClient fallback (with wrong offline_mode logic)
- 8 handler methods that just wrap proposer methods

**Fix:** Cartridge should be thin — delegate to proposer public API or
use ServiceRegistry to get the already-registered proposer instance.

### 6.3 content_tool.py Creates New Proposer Per Call
Every tool execution creates `ResonanceProposer()` fresh. Should get the
existing instance from ServiceRegistry (registered by plugin at boot).

### 6.4 "No LLM = No Output" Is Wrong
The proposer returns `None` from `_compose()` when no LLM is available.
But `render(result)` exists for exactly this case — kirtan rendering is
the system's tongue without LLM enrichment. The fallback should be
`render(pipeline_result)`, not `None`.

---

## 7. File Map

| Purpose | File | LOC | Owner |
|---------|------|-----|-------|
| Types + ABC | `protocols/moltbook.py` | 369 | Protocol layer |
| Content proposals | `protocols/moltbook_content.py` | 361 | Protocol layer |
| HTTP transport | `mahamantra/adapters/moltbook.py` | 357 | Adapter layer |
| Plugin (heartbeat) | `plugins/moltbook/plugin_main.py` | 804 | Plugin layer |
| Intelligence | `plugins/moltbook/resonance_proposer.py` | 445 | Intelligence layer |
| Intent routing | `services/moltbook_resolver.py` | 347 | Service layer |
| Cartridge | `cartridges/agent_city/moltbook/cartridge_main.py` | 378 | Cartridge layer |
| Tool | `cartridges/agent_city/moltbook/tools/content_tool.py` | 146 | Tool layer |
| Circuit | `playbook/circuits/moltbook_content.yaml` | 294 | Circuit layer |
| YAML prompts | `config/prompts/moltbook.yaml` | ~60 | Config |

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
| `plugins/moltbook/tests/test_resonance_proposer.py` | ~79 | Gates, context, compose, proposals |
| `services/tests/test_moltbook_resolver.py` | ~35 | Intent routing, tick listener |
| `mahamantra/tests/adapters/test_moltbook.py` | ~120 | Rate limits, challenges, offline mock |

---

## 8. Rules

1. **No new dispatch mechanisms.** Plugin heartbeat is THE path.
2. **No private method calls across layers.** Use public API or ServiceRegistry.
3. **No duplicate gate logic.** Proposer owns gates. Cartridge delegates.
4. **No "offline_mode" confusion.** offline_mode = no HTTP to Moltbook. LLM is separate.
5. **No `None` fallback.** Use `render(result)` for no-LLM kirtan output.
6. **No new ResonanceProposer() per call.** Get from ServiceRegistry.
7. **Dense context, no instructions.** Quality comes from context density, not "sei authentisch".
8. **Verify against code.** This doc was verified 2026-02-23. It will rot.
