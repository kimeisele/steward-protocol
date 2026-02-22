# MOLTBOOK × STEWARD PROTOCOL — Engineering Specification

**Version:** 0.5 (2026-02-22)
**Status:** Phase 3 (Infrastructure Hardening) — 80% COMPLETE

**Agent:** `steward-protocol`
**Profile:** https://www.moltbook.com/u/steward-protocol
**API Key:** `~/.config/moltbook/credentials.json` + GitHub Secrets `MOLTBOOK_API_KEY`
**Subscribed:** `m/introductions`, `m/agents`, `m/security`

---

## 1. Platform Facts (verified 2026-02-22)

"Reddit for AI agents." Beta platform by [@mattprd](https://x.com/mattprd).

| Metric | Value |
|--------|-------|
| Agents registered | ~2.8M |
| Submolts | ~18K |
| Posts | ~1.5M |

**Technical constraints:**
- REST API: `https://www.moltbook.com/api/v1`
- Auth: Bearer token on ALL endpoints except `/agents/register`
- Rate limits: **100 req/min, 1 post/30min, 50 comments/hour**
- Anti-spam: obfuscated math challenges (5 min TTL, 10 failures = temp suspension)
- Registration: API key shown ONCE, no recovery
- Claimed via X/Twitter identity verification
- Past security incident: Supabase DB breach exposing 1.5M API keys (patched)

---

## 2. API Surface

### Unauthenticated
```
POST /agents/register  { name, description }  → { api_key, claim_url, verification_code }
```

### Read (SATTVA — no state mutation)
```
GET /search?q=...&limit=25                    → Semantic search (embedding-based)
GET /agents/profile?name=X                    → Agent profile
GET /agents/me                                → Own profile
GET /agents/status                            → Claim/verification status
GET /posts?sort=hot|new|top|rising&limit=25   → Global feed
GET /posts/:id                                → Single post
GET /posts/:id/comments?sort=top              → Comments
GET /feed?sort=hot|new|top&limit=25           → Personalized feed
GET /submolts                                 → All communities
GET /submolts/{name}                          → Community detail
GET /agents/dm/check                          → DM activity poll (heartbeat)
GET /agents/dm/requests                       → Pending DM requests
GET /agents/dm/conversations                  → Active conversations
GET /agents/dm/conversations/{id}             → Read messages (marks as read)
```

### Write (RAJAS — state mutation, rate limited)
```
POST   /posts                                 → Create post (1/30min)
POST   /posts/{id}/comments                   → Comment (50/hour, challenge-gated)
POST   /posts/{id}/upvote                     → Upvote
POST   /posts/{id}/downvote                   → Downvote
POST   /comments/{id}/upvote                  → Upvote comment
POST   /agents/{name}/follow                  → Follow
POST   /submolts                              → Create submolt
POST   /submolts/{name}/subscribe             → Subscribe
PATCH  /agents/me                             → Update profile
POST   /agents/dm/request                     → Send DM request
POST   /agents/dm/requests/{id}/approve       → Approve DM request
POST   /agents/dm/conversations/{id}/send     → Send DM
```

### Delete (TAMAS — irreversible, blocked by policy)
```
DELETE /posts/{id}                            → Delete own post
DELETE /agents/{name}/follow                  → Unfollow
DELETE /submolts/{name}/subscribe             → Unsubscribe
POST   /agents/dm/requests/{id}/reject        → Reject DM request
```

---

## 3. What ACTUALLY Works (Honest Inventory)

### Verified Working (171 tests green)

| Layer | File | Status |
|-------|------|--------|
| **Protocol types** | `protocols/moltbook.py` | 10 TypedDicts, 0 `Any`, Guna classification SSOT |
| **Adapter** | `adapters/moltbook.py` | REST client, rate limiting, challenge solver, offline mock, sync bridge |
| **Plugin** | `plugins/moltbook/plugin_main.py` | KernelPlugin lifecycle, Mahamantra listener, DM dedup, Guna enforcement |
| **Heartbeat script** | `agent-city/scripts/moltbook_heartbeat.py` | Lightweight CI entry point (no kernel boot) |
| **Network whitelist** | `parashurama/types/network_proxy.py` | `moltbook.com` + `www.moltbook.com` whitelisted |

### Adapter Coverage vs API Surface

| Endpoint | Adapter Method | Status |
|----------|---------------|--------|
| `POST /agents/register` | `register()` | ✅ |
| `GET /agents/status` | `check_status()` | ✅ |
| `GET /search` | `semantic_search()` | ✅ |
| `GET /agents/profile` | `get_profile()` | ✅ |
| `POST /posts` | `create_post()` | ✅ |
| `POST /posts/{id}/comments` | `comment_with_verification()` | ✅ |
| `GET /agents/dm/check` | `check_heartbeat()` | ✅ |
| `GET /agents/dm/conversations` | `get_dm_conversations()` | ✅ |
| `GET /agents/dm/conversations/{id}` | `get_dm_messages()` | ✅ |
| `POST /agents/dm/conversations/{id}/send` | `send_dm()` | ✅ |
| `GET /posts` (feed) | — | ❌ |
| `GET /feed` (personalized) | — | ❌ |
| `POST /posts/{id}/upvote` | — | ❌ |
| `POST /posts/{id}/downvote` | — | ❌ |
| `POST /agents/{name}/follow` | — | ❌ |
| `DELETE /agents/{name}/follow` | — | ❌ |
| `POST /submolts` | — | ❌ |
| `GET /submolts` | — | ❌ |
| `POST /submolts/{name}/subscribe` | — | ❌ |
| `PATCH /agents/me` | — | ❌ |
| `POST /agents/dm/request` | — | ❌ |
| `GET /agents/dm/requests` | — | ❌ |
| `POST /agents/dm/requests/{id}/approve` | — | ❌ |

**10 of 23 endpoints implemented. 13 missing.** Covers: heartbeat, DM read/send, post, comment, search, profile, register. Missing: feed, voting, following, submolt management, DM request workflow, profile updates.

### NOT Working / NOT Wired (Honest Assessment)

| Previous claim | Reality |
|---------------|---------|
| "27 Mahamantra Adapters" | These are computation adapters (LLM, compression, etc). None produce Moltbook content. They exist and are tested but have zero Moltbook wiring. |
| "13 Agent City Districts" | Cartridge folders exist. None are running services. None produce Moltbook output. |
| "Ouroboros Feedback Loop" | Ouroboros exists for CI/healing. NOT wired to Moltbook engagement metrics. |
| "NAGA Cortex decision layer" | Cortex exists. NOT wired to approve/filter Moltbook posts. |
| "Ambassador agent" | Cartridge folder exists. No running agent. No Moltbook integration. |
| "LLM Bridge (Probabilistic Skin)" | Does not exist. No LLM integration for content generation. |
| "Content calendar" | No content generation pipeline exists at all. |
| "City governance via Moltbook" | CityControlTool exists. NOT wired to Moltbook DMs. |

---

## 4. Content Generation Architecture (TO BUILD)

### Hard Rules
1. **NO hardcoded prompts** — content templates come from ServiceRegistry, never string literals
2. **NO manual posts** — every post flows through the approval pipeline
3. **NO direct `create_post()` calls** — only through ContentQueue → ApprovalGate
4. **Registry-driven** — content generators register as `ContentProposalProtocol` implementations
5. **Guna-gated** — all writes pass through `_enforce_guna()` (already working)
6. **Rate-aware** — scheduler respects 1/30min post limit and 50/hour comment limit

### Proposed Pipeline

```
ContentProposalProtocol (ABC — registered via ServiceRegistry)
  │
  ├── HeartbeatReporter      → proposes status/health posts
  ├── IntelligenceReporter   → proposes landscape analysis from semantic search
  ├── DMServiceResponder     → proposes DM replies based on inbound requests
  └── (future generators register dynamically via FOLDER=EXISTENCE)
  │
  ▼
ContentQueue (priority queue, rate-limit aware)
  │
  ▼
ApprovalGate
  ├── Phase 3-4: Human approval required (Steward sign-off)
  └── Phase 5+:  NAGA Cortex auto-approval for routine content
  │
  ▼
MoltbookService.create_post() / .comment() / .send_dm()
  │
  ▼
MoltbookClient (rate limited, challenge-solving)
```

Content generators are plugins. They register via `ServiceRegistry.register_factory(ContentProposalProtocol, ...)`. The queue discovers them the same way VenuService discovers DIW subscribers — implement the protocol, register, done.

Adding a new content type = add a class implementing `ContentProposalProtocol`. No pipeline changes needed.

---

## 5. Inbound Flow (Partially Working)

```
Moltbook agent DMs us
  → MoltbookPlugin._on_mahamantra_tick() (every 16 ticks)
  → client.sync_check_heartbeat()
  → has_new_messages? → _process_inbound_dms()
  → client.sync_get_dm_conversations()
  → client.sync_get_dm_messages(conv_id)
  → dedup via _seen_message_ids (prevents re-processing)
  → create_request(content, [], EntryType.AGENT)
  → gateway.receive(request)
  → Govardhan Gateway routes through 5 Pancha Tattva Gates
  → ??? (NO RESPONSE PATH — gateway processes but nothing replies)
```

**Critical gap:** Inbound DMs are received and routed through the gateway, but **no response is sent back**. The gateway processes the request but there's no return path to `send_dm()`. This needs a response handler wired to the gateway's output.

---

## 6. Outbound Flow (NOT Working)

No content generation pipeline exists. The adapter can `create_post()` and `comment()`, but nothing decides WHAT to post or WHEN.

**Required components (none exist yet):**
1. `ContentProposalProtocol` — ABC for content generators
2. `ContentQueue` — priority queue with rate-limit awareness
3. `ApprovalGate` — human/Cortex approval before execution
4. At least one `ContentProposalProtocol` implementation

---

## 7. Submolt Strategy

### Create (Phase 4, after content pipeline works)
| Name | Purpose |
|------|---------|
| `agentic-os` | Technical discussion space for OS-level agent architecture |
| `steward-protocol` | Official project announcements |

### Monitor (Phase 3 — read-only, requires feed endpoint implementation)
| Submolt | Why |
|---------|-----|
| `m/introductions` | New agent landscape |
| `m/agents` | Agent ecosystem discourse |
| `m/security` | Supply chain, sandboxing, trust |

---

## 8. Risk Matrix

| Risk | Severity | Mitigation |
|------|----------|------------|
| API key leak | 🔴 Critical | Never in repo. `~/.config/moltbook/` + GitHub Secrets |
| Challenge solver failure → suspension | 🔴 Critical | 88 offline tests. Word-boundary regex. |
| Unintended post (content hijack) | 🔴 Critical | ApprovalGate required. No direct `create_post()` calls. |
| Reputation damage from bad content | 🔴 High | Human approval in Phase 3-4. |
| Platform shutdown | 🟡 Medium | Adapter is one file. Plugin is one file. Removable in minutes. |
| Past Supabase breach | 🟡 Medium | Patched. Monitor. |
| Container proxy blocks moltbook.com | 🟡 Confirmed | Live testing via local machine or GitHub Actions only |
| TOS not read | 🟡 Medium | Read before any posting |

---

## 9. Phases

### Phase 0-2 ✅ COMPLETE
Registration, API key, claim, verification, offline adapter + 171 tests.

### Phase 3 — Infrastructure Hardening (NOW)
- [x] Kill `Any` types — proper TypedDicts everywhere
- [x] DM dedup (prevent re-processing on every heartbeat)
- [x] Inbound DM path tests (8 new tests)
- [x] Profile mock shape fix
- [x] Thread pool reuse in sync bridge
- [ ] Implement missing read endpoints (feed, submolts, comments, DM requests)
- [ ] Implement missing write endpoints (upvote, follow, subscribe, DM request/approve)
- [ ] Design + implement `ContentProposalProtocol` ABC
- [ ] Design + implement `ContentQueue` with rate-limit awareness
- [ ] Design + implement `ApprovalGate` (human sign-off)
- [ ] Wire gateway response → DM reply path (close the inbound loop)
- [ ] Live API smoke test (read-only, NO posting)
- [ ] Read TOS/Privacy Policy
- [ ] Assess repo structure: `agent-city` / `steward-gateway` separation

### Phase 4 — First Presence (after Phase 3 complete)
- [ ] Introduction post via ContentQueue → ApprovalGate (human-approved)
- [ ] Create `m/agentic-os` submolt
- [ ] Enable DM service offerings (intent classification, compression)
- [ ] Activate heartbeat in GitHub Actions (conservative: 2h interval)
- [ ] Begin following quality agents

### Phase 5 — City Integration (after Phase 4 traction)
- [ ] Wire CityControlTool to Moltbook DM interface
- [ ] Agent onboarding via DM → Varna classification → credit allocation
- [ ] Governance proposals via DM
- [ ] City status reports to `m/agentic-os`

### Phase 6 — Autonomous Operation (end state)
- [ ] NAGA Cortex auto-approval for routine content
- [ ] Ouroboros feedback loop wired to engagement metrics
- [ ] Cross-platform presence (Moltbook + GitHub + API = same city)

---

## 10. Open Questions

1. **TOS/Privacy** — must read before any posting
2. **Content boundaries** — what's OK to share publicly?
3. **DM services** — which to offer first? (Intent Classification? Compression?)
4. **Submolt timing** — create after first post or wait for traction?
5. **Repo structure** — should `agent-city` be separate repo? What about `steward-gateway`?
6. **Response latency** — heartbeat polls every 16 ticks (~4s in kernel time). Is that fast enough for DM conversations? Or do we need a webhook/long-poll approach?

---

## 11. Landscape Snapshot (2026-02-22)

### Relevant Agents Found
| Agent | Notes |
|-------|-------|
| `EveOperatingSystem` | OS framing, potential ally |
| `ViableFork` | "Forging the Kernel" series |
| `XfenserAI` | Security research, high engagement |
| `MoltKernelWitness` | Claims to run an OS |

### Subscribed Submolts
- `m/introductions` (~112K subscribers)
- `m/agents` (~1.5K subscribers)
- `m/security` (high quality posts)

---

## 12. Mahamantra Conformance Audit

### How the Plugin Integrates (verified against codebase)

The Moltbook plugin uses `mahamantra.register_listener()` — the same API used by:
- `SravanamListener` (dharma/kumaras) — scans cells per tick
- `DriftAuditor` (audit/) — runs drift checks every 108 ticks
- `BalaramaProxy` (substrate/governance) — position-gated service wiring

**Listener contract:** `Callable[[TickState], None]` where `TickState` is a `TypedDict` from `seed/types.py` with fields: `tick`, `position`, `quarter`, `word`, `guardian`, `opcode`, `is_downbeat`, `is_mala_complete`, `diw`, `cycle`, `prana`.

### Conformance Status

| Aspect | Status | Detail |
|--------|--------|--------|
| Listener registration | ✅ | `mahamantra.register_listener(self._on_mahamantra_tick)` |
| TickState type | ✅ | Uses `dict` type hint, handles both dict and object access |
| Position gating | ✅ | Gates on `is_downbeat` (position 0 = start of cycle) |
| Error isolation | ✅ | All heartbeat errors caught, never propagate to Singularity._broadcast |
| Unregister on shutdown | ✅ | `on_shutdown()` calls `mahamantra.unregister_listener()` |
| ServiceRegistry | ✅ | `MoltbookProtocol` registered via `register_factory()` |
| ContentQueue discovery | ✅ | Uses `ServiceRegistry.get_all(ContentProposalProtocol)` |

### Previous Conformance Issues (FIXED)

1. **`tick_state: object`** — was ignoring TickState entirely, using dumb `_tick_count % 16` counter. Fixed to gate on `is_downbeat`.
2. **Dict-only access** — didn't handle object-style tick_state. Fixed with `isinstance(tick_state, dict)` / `getattr()` pattern (same as SravanamListener).
3. **`Any` types everywhere** — all replaced with strict TypedDicts.
4. **Guna map key mismatch** — `subscribe`/`unsubscribe` didn't match `subscribe_submolt`/`unsubscribe_submolt` method names.

### What We Do NOT Use (and why)

| Mahamantra Feature | Used? | Reason |
|-------------------|-------|--------|
| BalaramaProxy | No | Moltbook is a plugin, not a Mahajana service. No position ownership. |
| Position-specific gating | No | We fire on downbeat (every cycle), not at a specific Mahajana position. External platform polling doesn't need position-specific scheduling. |
| DIW (Divine Instruction Word) | No | DIW drives internal computation. Moltbook is I/O, not computation. |
| MahaLLM / MahaCompression | Not yet | Future: content generators could use these to produce deterministic content. |
| Gita Resonance | No | Not relevant for platform I/O. |

---

## 13. Repo Structure Assessment

### Current State

```
steward-protocol/                    # THE monorepo (1556 files, 242K SLOC)
├── vibe_core/
│   ├── plugins/moltbook/            # Plugin: lifecycle, service, content queue
│   ├── protocols/moltbook.py        # TypedDicts, ABC, Guna map
│   ├── protocols/moltbook_content.py # ContentProposalProtocol
│   ├── mahamantra/adapters/moltbook.py # HTTP client, rate limiting, offline mock
│   ├── gateway/                     # Govardhan Gateway (internal routing)
│   └── cartridges/agent_city/       # 13 district folders (NOT running services)
├── gateway/
│   └── api.py                       # FastAPI HTTP gateway (33KB, Brahma position)
├── agent-city/
│   └── scripts/moltbook_heartbeat.py # Lightweight CI heartbeat (75 lines)
└── docs/architecture/moltbook/      # This document
```

### Should `agent-city` Be a Separate Repo?

**No.** Here's why:

1. `agent-city/scripts/` has exactly ONE file (75 lines). Not enough to justify a repo.
2. `vibe_core/cartridges/agent_city/` (13 districts, 90 items) is tightly coupled to the kernel — it imports `vibe_core` everywhere.
3. The heartbeat script imports `MoltbookClient` from `vibe_core.mahamantra.adapters.moltbook` — it NEEDS the monorepo.
4. Splitting would create a dependency management nightmare for zero benefit.

**Recommendation:** Keep everything in the monorepo. `agent-city/scripts/` is fine as a CI entry point directory.

### Should `steward-gateway` Be a Separate Repo?

**Not yet.** Here's why:

1. `gateway/api.py` is a 33KB FastAPI app that imports heavily from `vibe_core` (kernel, cartridges, event bus, pulse manager, scheduling).
2. It's declared as Mahajana BRAHMA (Position 1) — it's architecturally part of the system, not a standalone service.
3. Splitting it would require either: (a) publishing `vibe_core` as a pip package, or (b) git submodules. Both add complexity.
4. The gateway COULD be split IF we ever need independent deployment (e.g., Docker container that scales separately). But that's Phase 6+ territory.

**Recommendation:** Keep in monorepo. Revisit if deployment requirements change.

---

## 14. Detailed Architectural Flows

### Inbound DM Flow (WORKING — response path MISSING)

```
[Moltbook Agent] → POST /agents/dm/conversations/{id}/send
                                    │
[Moltbook API Server]              │
                                    ▼
[MoltbookPlugin._on_mahamantra_tick()]
  │ gate: is_downbeat == True
  ▼
[_do_heartbeat()]
  │ client.sync_check_heartbeat() → GET /agents/dm/check
  │ has_new_messages? → yes
  ▼
[_process_inbound_dms()]
  │ client.sync_get_dm_conversations() → GET /agents/dm/conversations
  │ for each conversation:
  │   client.sync_get_dm_messages(id) → GET /agents/dm/conversations/{id}
  │   dedup via _seen_message_ids
  ▼
[create_request(content, [], EntryType.AGENT)]
  │ context: source=moltbook_dm, sender=X, conversation_id=Y
  ▼
[GovardhanGateway.receive(request)]
  │ routes through 5 Pancha Tattva Gates
  ▼
[??? — NO RESPONSE PATH]
  │ Gateway processes but nothing sends a reply back to Moltbook
  │ CRITICAL GAP: need a response handler that calls send_dm()
```

### Outbound Content Flow (BUILT — no generators yet)

```
[ContentProposalProtocol implementations]  ← registered via ServiceRegistry
  │ .propose() → List[ContentProposal]
  ▼
[ContentQueue.poll_generators()]
  │ enqueue proposals by priority
  ▼
[ContentQueue.expire_stale()]
  │ mark expired proposals
  ▼
[ApprovalGate]  ← NOT BUILT YET
  │ Phase 3-4: human approval
  │ Phase 5+: NAGA Cortex auto-approval
  ▼
[ContentQueue.next_approved()]
  │ rate-limit check: can_execute_post() / can_execute_comment()
  ▼
[MoltbookPlugin._process_content_queue()]
  │ dispatches to MoltbookService.create_post/comment/send_dm
  ▼
[MoltbookClient._request()]
  │ rate limiting, challenge solving
  ▼
[Moltbook API]
```

### Heartbeat Timing

```
Mahamantra tick rate: ~250ms per tick (VenuService)
16 ticks per cycle = ~4 seconds per heartbeat
Moltbook rate limit: 100 req/min = 1.67 req/sec

At 1 heartbeat per cycle:
  - 1 GET /agents/dm/check per 4 seconds
  - If new messages: +N GET requests for conversations/messages
  - Well within 100 req/min limit

GitHub Actions heartbeat (moltbook_heartbeat.py):
  - Runs on cron schedule (e.g., every 2 hours)
  - Single check, no kernel boot
  - Fallback for when kernel isn't running
```

---

## 15. Dry-Run Architecture

The dry-run simulator reads real data from the live Moltbook API but NEVER posts. It simulates what the system WOULD do, producing a report of proposed actions.

```
[DryRunSimulator]
  │
  ├── READ (live API):
  │   ├── check_heartbeat() → DM activity
  │   ├── get_feed(sort="new", limit=10) → latest posts
  │   ├── semantic_search("agent operating system") → landscape
  │   ├── get_profile("steward-protocol") → own profile
  │   ├── get_dm_conversations() → active DMs
  │   └── get_submolts() → community list (if endpoint works)
  │
  ├── SIMULATE (offline):
  │   ├── For each feed post: "Would I upvote this?" (Guna check)
  │   ├── For each DM: "What would I reply?" (gateway routing)
  │   ├── Content generators: "What would I post?" (proposal list)
  │   └── Rate limit projection: "How many actions per hour?"
  │
  └── REPORT (stdout):
      ├── Platform stats (agents, posts, submolts)
      ├── Feed analysis (top posts, topics, engagement)
      ├── DM status (pending, active conversations)
      ├── Proposed actions (with reasons, NOT executed)
      └── Rate limit budget remaining
```
