# MOLTBOOK AGENCY — Target Architecture

**Status: DESIGN (2026-02-24). Not yet implemented.**
**Depends on:** ARCHITECTURE.md, ARCHAEOLOGY.md, CLAUDE.md

---

## Problem

AgencyDirector (889 LOC) is a monolith doing 12 jobs:
context gathering, pipeline execution, engine analysis, MahaComposition,
LLM prompting, truncation, engagement, event sourcing, feedback, quota,
constitution validation, retry loop.

The agency has no workers. The "director" IS the whole agency.

---

## Principle

The Moltbook Agency must be THE example of how the repo's infrastructure is used.
Everything is already built. Nothing needs to be invented.

---

## Existing Infrastructure (ALL BUILT, MOST UNUSED)

### Orchestration
- **MOLTBOOK_CONTENT_V1 Circuit** (`playbook/circuits/moltbook_content.yaml`, 294 LOC)
  - SHABDA → ARTHA → PRATYAYA → KARMA → REVIEW → SUCCESS
  - Wired in plugin_main.py (`_wire_circuit_executor()`), never called by heartbeat
  - Has InvariantChecker, MetaCircuitManager, TASK_LEDGER, ERROR_RECOVERY
- **Shadow Reactor** (`reactor/shadow.py`, 1454 LOC)
  - Non-linear: BHOGA (dispatch) → SWITCH → PRASADAM (fold) → RETURN
  - TaskKernel dispatch via SamanaBridge + Nadi
  - JivaShadow qualification per dispatch
  - API: `mahamantra.shadow.spawn()`, `queue_task()`, `get_fold_results()`
- **Playbook Loader** (`loaders/playbook_loader.py`)
  - DAG with topological sort + loop support (`back_to`)

### Workers (Capabilities + Tools)
- **ContentCapability** (`capabilities/content.py`) — analyze, should_engage, analyze_feed
- **EngagementCapability** (`capabilities/engagement.py`) — follow_back, subscribe, upvote + state
- **ResearchCapability** (`capabilities/research.py`) — feed analysis, topic extraction
- **MoltbookContentTool** (`tools/content_tool.py`) — Tool protocol (moltbook.content)
  - Actions: analyze, compose_comment, compose_post, compose_dm_reply
  - Ready for `execute_tool("moltbook.content", params)` pattern

### Content Intelligence
- **MahaComposition** — 5 scorers (Prana, Rhythm, Semantic/WordNet, Mode, State)
  - Output: resonant Gita vocabulary ranked for input → LLM context, NOT standalone English
- **ResonanceProposer** — scoring + analysis (L3, no content generation responsibility)
- **MahaLanguageEngine** — EngineResult (resonant words, template words, section, verse)
- **context_builders.py** — format_resonant_words, section_data, guardian_vocabulary_short

### Governance
- **Constitution** — validate(content, type) → violations/warnings
- **SravanamCheck** — entropy advisory (observability)
- **ResonanceHarmonics** — zone classification
- **VedicScaleMapping** — rasa emotional tone

### Communication
- **EventBus** — THOUGHT, ACTION, ERROR, VIOLATION, COMPLETED
- **FeedbackProtocol** — signal_success/failure/partial
- **EventLog** — JSONL ledger, event sourcing

---

## Target: Non-Linear Agency

Not 1→2→3→4. Like Shadow Reactor: 1→2→(research)→back to 1→reframe→2→3.

### Circuit as State Machine + Reactor as Executor

The circuit defines WHAT states exist and WHAT transitions are valid.
The reactor provides non-linear execution with fold-back.

```
SHABDA (parse)
  → ContentCapability.analyze() via MoltbookContentTool
  → Pipeline + Engine + MahaComposition = raw context

ARTHA (validate)
  → Deterministic gates (guna, cell, integrity)
  → Constitution pre-check

PRATYAYA (compose)
  → Context refinement (MahaComposition output = vocabulary hints for LLM)
  → LLM call with v10 YAML template (~120 tokens context)
  → IF quality insufficient → fold back to SHABDA with feedback

KARMA (record)
  → EventLog.record_content_generated()
  → FeedbackProtocol.signal_success()
  → EventBus.emit(COMPLETED)
```

### Key: MahaComposition in the Pipeline

MahaComposition output is NOT English. It's ranked Gita vocabulary:
"perfection unattached unmanifested — tranquility duty mortal"

This flows to the LLM as "Themes:" in the YAML template.
The LLM's job: weave these resonant concepts into natural language.
The 5 scorers already encode guna, quarter, prana, rhythm, semantics.

---

## What the Director Becomes

THIN orchestrator. 3 responsibilities:
1. Route content requests to circuit executor
2. Route engagement to EngagementCapability
3. Signal events (EventBus, FeedbackProtocol, EventLog)

Everything else delegated to existing capabilities/tools.

---

## Migration Path

1. Make `execute_content_circuit()` the PRIMARY content path (it's already wired!)
2. AgencyDirector._process() already tries circuit first — debug why it fails
3. Once circuit works, the inline pipeline code in _process() becomes dead code
4. Remove dead code → director shrinks from 889 → ~200 LOC
