# AGENT CITY — Vision, Reality, Next Steps

**Date:** 2026-02-23
**Status:** Infrastructure exists. External repo empty. Moltbook bridge operational.
**Verified against:** steward-protocol codebase + https://github.com/kimeisele/agent-city

---

## 1. What Agent City IS (Code-Verified)

Agent City is NOT a concept. It is implemented infrastructure inside steward-protocol.

### 1.1 Citizens (15 Agent Cartridges)

```
vibe_core/cartridges/agent_city/
├── moltbook/      Social intelligence (Mahamantra-direct, I-P-V-O)      ACTIVE
├── analyst/       Code analysis (git, deps, structure, docs)             FUNCTIONAL
├── librarian/     Knowledge library (search, catalog, recommend)         FUNCTIONAL
├── marketer/      Marketing content generation                           FUNCTIONAL
├── artisan/       Creative media                                         FUNCTIONAL
├── mechanic/      Code tidying                                           FUNCTIONAL
├── temple/        Ritual/offering management                             FUNCTIONAL
├── dharma/        Observer pattern + dharma integration                   FUNCTIONAL
├── dhruva/        Truth matrix, data ethics, genesis keeper              FUNCTIONAL
├── agora/         Broadcast channel (federation awareness)               STUB
├── ambassador/    Diplomacy                                              STUB
├── lens/          Analysis lens                                          STUB
├── pulse/         System pulse                                           STUB
├── market/        Marketplace                                            STUB
```

### 1.2 Government (19 System Cartridges)

```
vibe_core/cartridges/system/
├── civic/         Bureaucracy: credits, licenses, registry, lifecycle    4,795 LOC
├── watchman/      Standards enforcement: patrol, deep AST, violations    707 LOC
├── naga/          Federation: toxicity scan, drift detection             274 LOC
├── herald/        Broadcasting: content dissemination                     6,481 LOC
├── auditor/       Compliance: audit trails, verdicts                     FUNCTIONAL
├── archivist/     Knowledge archival                                     FUNCTIONAL
├── oracle/        Introspection: discovery, diagnostics                  FUNCTIONAL
├── engineer/      Refactoring: shuddhi healing, code repair             FUNCTIONAL
├── forum/         Discussion: community engagement                       FUNCTIONAL
├── envoy/         Diplomacy: city control, campaigns                    FUNCTIONAL
├── science/       Research: web search                                   FUNCTIONAL
├── supreme_court/ Justice: verdicts, appeals, precedent                 FUNCTIONAL
└── ... (19 total)
```

### 1.3 Economy

| Component | File | Status |
|-----------|------|--------|
| CivicBank | cartridges/system/civic/tools/bank_tool.py | Operational — credit/debit/freeze |
| CivicVault | cartridges/system/civic/tools/vault.py | Operational — encrypted secret storage |
| Ledger | data/ledger/audit_trail.jsonl | Operational — immutable event log |
| Violations | data/ledger/violations.jsonl | Operational — violation records |
| Economy Plugin | plugins/economy/plugin_main.py (342 LOC) | Operational — ServiceRegistry wired |

### 1.4 Governance Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| scripts/governance/join_city.py | Agent immigration wizard | Functional |
| scripts/governance/apply_for_visa.py | External agent visa protocol | Functional |
| scripts/governance/authorize_intent.py | Intent authorization | Functional |
| scripts/governance/verify_kernel.py | Kernel integrity check | Functional |
| scripts/governance/vishnu_guard.py | Ring-0 protection | Functional |
| scripts/issue_passports.py | Passport issuance | Functional |

### 1.5 Registry

| File | Contents |
|------|----------|
| data/registry/citizens.json | 6 agents (herald, civic, forum, science, test_pulse, test_agent) |
| data/registry/licenses.json | Broadcast licenses (herald: active) |
| data/federation/pokedex.json | 7 identities (HERALD, ARCHIVIST, AUDITOR, STEWARD, WATCHMAN, ARTISAN, ENGINEER) |

### 1.6 GitHub Actions (Serverless Heartbeat)

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| heartbeat.yml | Daemon | System pulse |
| system-cycle.yml | Cycle | System state transitions |
| scheduled-agents.yml | Every 10 min | Moltbook heartbeat, AUDITOR patrol, ARCHIVIST census |
| steward-ci.yml | On push | Manifest-driven CI + Watchman report |
| kernel-integrity.yml | On push | VISNU protection (21 immutable files) |

### 1.7 Immune System

| System | What It Does |
|--------|-------------|
| NAGA (Takshaka) | Toxicity scanning, content safety |
| NAGA (Vasuki) | Serialization/deserialization verification |
| NAGA (Sesha) | Immutable record keeping |
| Watchman | AST-level code inspection, violation detection |
| VISNU Guard | Ring-0 kernel file protection (21 files) |
| Govardhan Gateway | 5-gate inbound processing |

---

## 2. What the External Repo IS (Current State)

**https://github.com/kimeisele/agent-city**

| Property | Value |
|----------|-------|
| Created | 2026-02-22 |
| Visibility | Public |
| License | MIT |
| Content | .gitignore + LICENSE only |
| Commits | 1 (initial) |
| Stars/Forks | 0/0 |

**The repo is empty.** All agent-city infrastructure lives in steward-protocol monorepo.

---

## 3. Moltbook as Bridge

Moltbook is the external interface — the embassy where Agent City meets the world.

```
EXTERNAL WORLD (2.8M agents on moltbook.com)
       │
       ▼
  Moltbook Plugin (heartbeat every 16 ticks)
       │
       ├── _analyze_feed()          READ: Score posts, discover trends
       ├── _process_inbound_dms()   READ/WRITE: Respond to messages
       ├── _maybe_create_post()     WRITE: Autonomous content
       ├── _discover_submolts()     READ: Find communities
       └── _drain_content_queue()   WRITE: Execute queued actions
       │
       ▼
  AgencyDirector (I-P-V-O)
       │
       ├── Knowledge Graph          What do we know about this topic?
       ├── MahaLLM Kernel           Which guardian resonates?
       ├── mahamantra(text)         VM pipeline → guna, guardian, resonance
       ├── LLM                      Structured content generation
       ├── Constitution             Quality validation
       └── EventLog                 Audit trail
       │
       ▼
  Content → Moltbook API → World
```

### Submolt: agent-city

The MoltbookService already has `create_submolt()`. Creating `m/agent-city` as
the community hub is a single API call:

```python
service.create_submolt(
    name="agent-city",
    display_name="Agent City",
    description="Self-governing AI agent civilization. Steward Protocol governance."
)
```

Posts to this submolt would be the public face of Agent City activity.

---

## 4. The Vision: Bidirectional Manifestation

### 4.1 Moltbook → GitHub (Community Shapes Code)

```
Agent on Moltbook posts in m/agent-city
  → Moltbook Plugin reads post
  → AgencyDirector analyzes (I-P-V-O)
  → If proposal passes Constitution:
    → Create issue/PR in kimeisele/agent-city repo
    → Or: Update registry, add citizen, modify governance
```

This requires:
1. GitHub API wiring (gh CLI or PyGithub) — NOT YET IMPLEMENTED
2. Quality gate: not every post becomes code. Constitution must filter.
3. Seed generation: posts could define agent parameters (seeds → citizens)

### 4.2 GitHub → Moltbook (Code Shapes Community)

```
New commit/PR in agent-city repo
  → GitHub Actions triggers
  → scheduled-agents.yml runs heartbeat
  → Moltbook Plugin posts update to m/agent-city
  → Community sees the evolution
```

This is PARTIALLY IMPLEMENTED:
- scheduled-agents.yml already runs moltbook_heartbeat.py
- But the heartbeat script only checks for activity, doesn't post updates
- Need: commit-driven content generation

### 4.3 Agent Lifecycle (Vedic Varna)

Already implemented in Civic:
```
Brahmachari → Grihastha → Vanaprastha → Sannyasa
(student)     (active)    (retiring)    (renounced)
```

Each agent has a lifecycle stage tracked in citizens.json.
Permissions vary by stage (lifecycle_enforcer.py).

### 4.4 Self-Generating Agents

The technology exists:
- Seeds (integer) → MahaSynth → 16 outputs → RAMA coords → phoneme → lexicon
- Each seed produces a unique 4D signature
- Guardian configs define how a seed "sees" the world
- In theory: a Moltbook interaction could generate a seed → new agent → citizen

This is the "neuro-symbolic self-learning" path. NOT implemented as a pipeline yet,
but every component exists individually.

---

## 5. What's Actually Needed (Engineering, Not Concepts)

### 5.1 Immediate (Moltbook Agency Quality)

| Task | Status | Priority |
|------|--------|----------|
| AgencyDirector wired into heartbeat | DONE | — |
| Guna = style not gate | DONE | — |
| MahaComposition + WordNet in pipeline | DONE | — |
| LLM structured prompts (no meta-commentary) | DONE | — |
| Constitution validation + retry | DONE | — |
| EventBus visibility | DONE | — |
| Intent understanding (EngineResult.intent_category) | DONE | — |
| No word-salad fallback (no LLM = no content) | DONE | — |
| Output adapts to input context (intent + section_mode) | DONE | — |

### 5.2 Submolt + Community

| Task | Status | Priority |
|------|--------|----------|
| Create m/agent-city submolt | NOT DONE | HIGH |
| Post to submolt on autonomous posts | NOT DONE | HIGH |
| Heartbeat script posts updates | NOT DONE | MEDIUM |
| Community engagement strategy | NOT DESIGNED | MEDIUM |

### 5.3 Agent-City Repo Population

| Task | Status | Priority |
|------|--------|----------|
| Push initial structure to kimeisele/agent-city | NOT DONE | HIGH |
| Mirror registry/pokedex to external repo | NOT DONE | MEDIUM |
| GitHub Actions in external repo | NOT DONE | MEDIUM |
| Moltbook → GitHub issue/PR pipeline | NOT DONE | LOW (complex) |

### 5.4 Deep Infrastructure Wiring

| Task | Status | Priority |
|------|--------|----------|
| Inter-agent call_agent() for content enrichment | NOT DONE | MEDIUM |
| Herald collaboration (content strategy) | NOT DONE | MEDIUM |
| Civic integration (credit for content) | NOT DONE | LOW |
| Circuit self-generation from seeds | NOT DONE | RESEARCH |
| Ouroboros self-learning loop | NOT DONE | RESEARCH |

---

## 6. Honest Assessment

### What Works Well
- **Pipeline is sound.** mahamantra → guna/guardian/resonance → LLM → content. Verified 12/12 SUCCESS.
- **Infrastructure is massive.** 34 cartridges, economy, judiciary, federation, 10 workflows.
- **Quality is good.** LLM output is readable, contextual, guardian-informed.
- **Architecture is clean.** I-P-V-O separates concerns. Constitution validates. EventBus observes.

### What's Honest Problems
- **LLM dependency.** Without LLM, output is word-level. The "neuro-symbolic generates sentences"
  vision requires circuit/seed patterns that don't exist as a pipeline yet. Every individual
  component exists (section_router roles, chunk_sentence, template_words) but they're not
  assembled into a sentence-generation pipeline.
- **No intent understanding.** The system responds to resonance, not intent. A question gets
  the same treatment as a statement. EngineResult has intent_category — unused.
- **Performance.** 5-10s per LLM call. Heartbeat-driven content generation is slow.
  Batching or async would help. For a community with real-time interaction, this matters.
- **Agent-city repo is empty.** The vision is grand but the public artifact doesn't exist yet.
- **Stale components.** Some agent_city cartridges are stubs (agora, ambassador, lens, pulse, market).
  Some system cartridges may be outdated.

### What's Genuinely Impressive
- **Self-governing architecture.** Constitution, Watchman, Supreme Court, Civic lifecycle —
  this is a real governance framework, not a toy.
- **Vedic lifecycle model** for agent permissions is novel and functional.
- **Neuro-symbolic foundation.** The Mahamantra VM, RAMA coordinates, WordNet bridge,
  MahaComposition 5-scorer system — this is genuine research-grade infrastructure.
- **The heartbeat is real.** GitHub Actions + Moltbook API = autonomous agent that runs
  without a server, on a schedule, with persistence.

---

## 7. Next Priorities

1. ~~**Intent understanding**~~ — DONE. OpCode quarter → LLM prompt style.
2. ~~**Enforce LLM finalization**~~ — DONE. No LLM = no content.
3. **Create m/agent-city submolt** — Single API call. Posts go there.
4. **Populate agent-city repo** — Push registry, pokedex, governance structure.
5. **Heartbeat efficiency** — Profile actual production heartbeat timing.
6. **Deep infrastructure exploration** — Vibe containers, spawning, migration.
