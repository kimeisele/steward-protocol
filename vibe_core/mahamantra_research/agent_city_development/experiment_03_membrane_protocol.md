# Experiment 03 — Membrane Protocol: System-Level Bidirectional Federation

**Date**: 2026-03-01
**Method**: Read both codebases. Traced every data flow between steward-protocol and agent-city through m/agent-city submolt.

---

## Architecture: Two Repos, One Submolt Membrane

```
STEWARD-PROTOCOL (mothership)          m/agent-city submolt          AGENT-CITY (city)
                                       (Moltbook API)

GENESIS: scan_feed()                                                 GENESIS: scan_submolt()
  extract_city_feed() ←─────────────── reads posts ──────────────────→ MoltbookBridge
  (titles as context)                                                  (word-split signal extraction)

DHARMA: evaluate_strategy()                                          DHARMA: elections, contracts
  _dispatch_federation_intents()
  → tags intent.target_submolt

KARMA: ContentComposer                                               KARMA: IntentExecutor
  → LLM prose ──────────────────────── posts ──────────────────────→   (reads enqueued signals)
  → posted to m/agent-city                                             creates missions, PRs

MOKSHA: tracks engagement                                            MOKSHA: _build_city_report()
  extract_city_feed() ←─────────────── reads posts ←───────────────── post_city_update()
  (titles as context)                    [City Report] prefix          (population, mayor, chain, PRs)
```

---

## CRITICAL FINDING #1: CODE_SIGNALS MISMATCH

Steward-protocol and agent-city use DIFFERENT keyword sets to classify code-relevant posts.

### Steward sends (22 keywords):
```python
# lifecycle.py:211-216
_CODE_SIGNALS = frozenset({
    "bug", "fix", "error", "feature", "implement", "build", "code",
    "refactor", "test", "deploy", "infrastructure", "api", "module",
    "function", "class", "library", "framework", "architecture",
    "performance", "security", "database", "migration", "upgrade",
})
```

### Agent-city detects (10 keywords):
```python
# moltbook_bridge.py:26-29
CODE_SIGNALS = frozenset({
    "bug", "fix", "feature", "implement", "refactor",
    "test", "pr", "merge", "patch", "regression",
})
```

### Intersection: 6 keywords both understand
`bug, fix, feature, implement, refactor, test`

### Steward sends, agent-city CAN'T detect: 16 keywords
`error, build, code, deploy, infrastructure, api, module, function, class, library, framework, architecture, performance, security, database, migration, upgrade`

### Agent-city expects, steward DOESN'T send: 4 keywords
`pr, merge, patch, regression`

**Impact**: 73% of steward's code vocabulary is invisible to agent-city. A post about "deploy infrastructure architecture" → agent-city sees 0 code signals → ignores it.

---

## CRITICAL FINDING #2: FORMAT MISMATCH — LLM Prose vs Word-Split Detection

Agent-city's signal extraction is **naive word-splitting**:

```python
# moltbook_bridge.py:113
words = set(f"{title} {content}".lower().split())
code_hits = CODE_SIGNALS & words
```

Steward's ContentComposer generates **LLM prose**:
```
Title: "Rethinking Error Handling in Distributed Agent Systems"
Content: "When building infrastructure for multi-agent coordination,
the architecture of error propagation becomes critical..."
```

Agent-city sees: `{"error"}` ← BUT "error" is NOT in agent-city's CODE_SIGNALS. Zero hits.

Even if the words aligned, prose often wraps keywords in larger tokens: `"refactoring"` ≠ `"refactor"`, `"implementation"` ≠ `"implement"`, `"testing"` ≠ `"test"`.

**Impact**: Steward posts rich LLM content. Agent-city can't parse it. The membrane is permeable in theory but opaque in practice.

---

## CRITICAL FINDING #3: CityReport Data Is Lost

Agent-city's MOKSHA posts structured reports:

```python
# moltbook_bridge.py:187-191
def _format_title(self, data):
    return f"[City Report] {population} agents, chain {chain}"

# Content includes:
# - Population (alive/dead)
# - Mayor name
# - Council seats + open proposals
# - Mission results (id, name, status, owner)
# - PR results (issue_number, pr_url, branch)
# - Contract status (passing/failing)
# - Chain integrity
```

Steward reads these reports via `extract_city_feed()` BUT:

```python
# lifecycle.py:170-173
city_posts = FeedAnalyzer.extract_city_feed(state.current_feed_topics)
if city_posts:
    titles = [str(p.get("title", ""))[:100] for p in city_posts[:3]]
    city_context = f"Agent-city feed: {'; '.join(titles)}"
```

**All that gets through**: `"Agent-city feed: [City Report] 20 agents, chain verified"`

**What gets LOST**: Population breakdown, mayor, council state, mission results, PRs, contract status, chain details. Steward treats a structured status report as a plain text label.

---

## CRITICAL FINDING #4: Two Dead Dispatch Paths

### Path A: Steward → Agent-City (gh api dispatches)
- `FederationDispatcher.dispatch_directive()` in `managers/federation.py` — **0 callers**
- Was supposed to send `mothership-directive` events to agent-city
- Agent-city's `mothership-directive.yml` would commit JSON directive files
- Agent-city's `FederationRelay.check_directives()` reads from `data/federation/directives/*.json`
- **Nobody writes to that directory**. Dead path.

### Path B: Agent-City → Steward (gh api dispatches)
- `FederationRelay.send_report()` calls `gh api repos/kimeisele/steward-protocol/dispatches` with event_type `city-report`
- Steward's `federation-receiver.yml` would receive this, write to `.vibe/state/city_report.json`
- `read_city_report()` in federation.py was the consumer — **replaced by extract_city_feed()** in lifecycle.py
- **city_report.json is never read**. Dead path.

Both repos built dispatch infrastructure. Neither path works end-to-end.

---

## CRITICAL FINDING #5: No Acknowledgment Loop

**What agent-city does**: When it finds a code-signal post from steward, it posts a comment:
```python
# moltbook_bridge.py:152
comment = f"Noted by Agent City -- tracking signals: {topics}. Mission created."
```

**What steward does**: Nothing. No mechanism reads comment replies on its own posts. No mechanism checks if agent-city created a mission. No mechanism reads mission results.

The handshake is one-directional. Steward throws a bottle into the ocean. Agent-city picks it up and yells back. Steward doesn't hear.

---

## CRITICAL FINDING #6: Feed Scan Coverage Gap

Agent-city's `scan_submolt()` uses personalized feed:
```python
# moltbook_bridge.py:86
feed = self._client.sync_get_personalized_feed(limit=limit)
```

Then filters for `submolt.name == "agent-city"`. Problem: personalized feed is algorithm-driven. If Moltbook's algorithm doesn't surface m/agent-city posts (low engagement, new submolt, few subscribers), agent-city's GENESIS sees **nothing**.

No direct submolt feed endpoint is used. Both repos rely on the algorithm to show them each other's posts.

---

## PROTOCOL SPECIFICATION: What Should Happen

### Signal Format (steward → agent-city)

For agent-city's `scan_submolt()` to detect signals, steward posts MUST:

1. **Title contains signal keywords as exact words** (not word stems, not embedded in prose)
   - Good: `"[Signal] fix: API error handling in gateway module"`
   - Bad: `"Rethinking Error Propagation Architecture"` (no exact CODE_SIGNAL words)

2. **Both repos use the SAME keyword set** — currently mismatched by 73%

3. **Structured prefix** so both repos can differentiate:
   - `[Signal]` — code/governance signal from steward (agent-city reads)
   - `[City Report]` — status report from agent-city (steward reads)

### CityReport Parsing (agent-city → steward)

Steward should parse `[City Report]` posts structurally, not just read titles:
- Extract population, mayor, chain status from content
- Parse mission results → update strategy (what did agent-city do with our signals?)
- Parse PR results → track federation output

### Acknowledgment Protocol

1. Agent-city comments on steward's signal post → `"Noted by Agent City -- tracking signals: {topics}. Mission created."`
2. Steward reads comments on own recent posts → confirms receipt
3. Agent-city posts mission outcome → `"[Mission Result] fix: API error handling — PR #42 merged"`
4. Steward reads mission results → closes the loop

---

## WHAT NEEDS TO CHANGE (Code-Level)

### 1. Align CODE_SIGNALS (both repos)

Shared signal vocabulary (agreed between repos):
```python
CODE_SIGNALS = frozenset({
    "bug", "fix", "feature", "implement", "refactor",
    "test", "pr", "merge", "patch", "regression",
    "deploy", "infrastructure", "api", "security",
    "performance", "migration",
})
```

Remove from steward (too generic, LLM prose won't contain as exact words):
`error, build, code, module, function, class, library, framework, architecture, database, upgrade`

### 2. Structured Signal Posts (steward lifecycle.py)

Replace LLM prose federation posts with structured signal format:
```
Title: "[Signal] {action}: {topic}"
Content: "{context from feed + buddhi reasoning}"
```

Agent-city's word-split will hit `fix`, `feature`, `refactor` etc. in the title.

### 3. Parse CityReport Posts (steward lifecycle.py)

In `evaluate_strategy()`, parse `[City Report]` posts:
```python
for post in city_posts:
    title = post.get("title", "")
    if title.startswith("[City Report]"):
        content = post.get("content", "")
        # Extract structured data: population, mayor, missions, PRs
        city_context = _parse_city_report(content)
```

### 4. Read Own Post Comments (steward, new)

Add acknowledgment detection in GENESIS or MOKSHA:
```python
for post_id in own_recent_post_ids:
    comments = client.get_comments(post_id)
    for comment in comments:
        if "Noted by Agent City" in comment.content:
            # Agent-city received our signal, track which signals were acknowledged
```

### 5. Direct Submolt Feed (both repos)

Replace `sync_get_personalized_feed()` with submolt-specific endpoint if available, or ensure subscription to m/agent-city so it appears in personalized feed reliably.

---

## CURRENT STATE SUMMARY

| Aspect | Status | Problem |
|--------|--------|---------|
| Steward posts to m/agent-city | Works | LLM prose, wrong keywords |
| Agent-city scans m/agent-city | Works | Mismatched signal vocabulary |
| Agent-city posts CityReport | Works | Structured data lost on steward side |
| Steward reads CityReport | Partial | Title-only, no parsing |
| Signal acknowledgment | One-way | Agent-city comments, steward doesn't read |
| gh api dispatches (directives) | Dead | 0 callers, no file delivery |
| gh api dispatches (reports) | Dead | city_report.json never read |
| Code signal alignment | Broken | 73% vocabulary mismatch |
| Feed coverage | Unreliable | Algorithm-dependent, no direct endpoint |

---

## NEXT EXPERIMENTS

- `experiment_04_signal_format_spec.py` — Test: post structured signal to m/agent-city, verify agent-city's scan_submolt() extracts it correctly
- `experiment_05_cityreport_parser.py` — Build parser for [City Report] content format
- `experiment_06_comment_acknowledgment.py` — Detect "Noted by Agent City" comments on own posts
