# OPUS-302: THE OPUS PROTOCOL

> **Status**: ACTIVE
> **Date**: 2025-12-24
> **Purpose**: Cost-efficient AI agent cascade

---

## THE DANCE

```
┌─────────────────────────────────────────────────────┐
│  OPUS (Senior) - $$$                                │
│  └─ Plans, Documents, Ring 0 changes                │
│     └─ Creates OPUS-XXX with clear tasks            │
│        └─ Hands off to SONNET                       │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  SONNET (Mid) - $$                                  │
│  └─ Executes OPUS-XXX tasks                         │
│     └─ When DONE:                                   │
│        └─ Spawns HAIKU for next problem analysis    │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  HAIKU (Junior) - $                                 │
│  └─ Pre-analyzes next OPUS-XXX                      │
│     └─ Gathers context, identifies blockers         │
│        └─ Writes PREP section in next OPUS doc      │
│           └─ OPUS starts next session ready to go   │
└─────────────────────────────────────────────────────┘
```

---

## PROTOCOL RULES

### 1. OPUS Creates
```markdown
## OPUS-XXX: [Title]
> Status: READY FOR SONNET
> Next: OPUS-YYY

### SONNET TASKS
- [ ] Task 1 (file, test, commit)
- [ ] Task 2 (file, test, commit)

### WHEN DONE
Spawn Haiku to pre-analyze OPUS-YYY:
- What files to read
- What blockers exist
- What questions to answer
```

### 2. SONNET Executes
```bash
# For each task:
1. Read the task
2. Implement
3. Test
4. Commit
5. Mark done

# When all done:
# Spawn Haiku with prompt:
"Pre-analyze OPUS-YYY. Read [files]. Identify blockers.
Write findings to docs/architecture/OPUS/YYY-PREP.md"
```

### 3. HAIKU Pre-Analyzes
```markdown
## OPUS-YYY-PREP: Pre-Analysis

### Files Read
- file1.py: [summary]
- file2.py: [summary]

### Blockers Identified
1. X depends on Y
2. Z needs refactoring

### Questions for OPUS
1. Should we do A or B?
2. What about C?

### Suggested Approach
[Brief recommendation]
```

### 4. OPUS Continues
Next session, OPUS reads PREP file and jumps straight in.

---

## COST MODEL

| Agent | Cost/1M tokens | Role |
|-------|----------------|------|
| Opus | $15/$75 | Strategic planning, Ring 0 |
| Sonnet | $3/$15 | Execution, testing |
| Haiku | $0.25/$1.25 | Pre-analysis, context gathering |

**Optimal ratio**: 1 Opus : 5 Sonnet : 10 Haiku

---

## CURRENT STATUS (2025-12-24)

| OPUS | Title | Status | Results |
|------|-------|--------|---------|
| 301 | Boot/Runtime | ✅ COMPLETE | 3940ms → ~2500ms (38%) |
| 302 | Protocol | ✅ ACTIVE | This doc |
| 303 | Pulse Optimization | ✅ COMPLETE | ~50ms → ~15ms (70%) |
| 304 | Deep Lazy Loading | 📋 PLANNED | See below |

### OPUS-301/303 Commits (2025-12-24)
```
d17d7940 - perf(pulse): OPUS-303 Phase 1+3 Async I/O + Health cache
32d76fdf - fix(executor): Fix ExecutionResult API mismatch
ca9409ac - perf(ledger): OPUS-301/303 Lazy connection + count cache
a94b4c76 - perf(boot): OPUS-301 Split unified_execution into Core + Full
91a2841a - perf(boot): Lazy jinja2 import in template_loader
```

---

## OPUS-304: DEEP LAZY LOADING

> Status: READY FOR SONNET
> Next: OPUS-305

### Target
Boot: 2500ms → <1000ms

### SONNET TASKS

1. [ ] **S1: Lazy Import Wrapper** - `vibe_core/utils/lazy_import.py` (NEW)
   - Create utility for deferred imports
   - Test with ledger import
   - Commit

2. [ ] **S2: Config Cache** - `vibe_core/phoenix/config_cache.py` (NEW)
   - Pickle parsed config
   - Hash-based invalidation
   - Integrate into phoenix/config.py
   - Commit

3. [ ] **S3: Async Logging** - `vibe_core/utils/async_logging.py` (NEW)
   - QueueHandler + QueueListener pattern
   - Non-blocking file writes
   - Commit

4. [ ] **S4: Boot Optimizer Plugin** - `vibe_core/plugins/boot_optimizer/` (NEW)
   - Plugin to patch heavy properties lazy
   - Not Ring 0 (safe for Sonnet)
   - Commit

### WHEN DONE
Spawn Haiku to pre-analyze OPUS-305:
- Read vibe_core/cli/ for CLI optimization opportunities
- Read vibe_core/runtime/interface.py for interface latency
- Identify remaining boot blockers with `python3 -X importtime`

---

## HANDOFF TEMPLATES

### OPUS → SONNET
```markdown
## SONNET: Execute OPUS-XXX

Tasks:
1. [ ] ...
2. [ ] ...

Rules:
- One task, one commit
- Test before commit
- Call Senior for Ring 0

When done: Spawn Haiku for OPUS-YYY prep
```

### SONNET → HAIKU
```markdown
## HAIKU: Pre-analyze OPUS-YYY

Read these files:
- path/to/file1.py
- path/to/file2.py

Answer:
1. What are the main blockers?
2. What dependencies exist?
3. What's the suggested approach?

Write to: docs/architecture/OPUS/YYY-PREP.md
```

---

*Der Tanz der Modelle. Opus denkt. Sonnet handelt. Haiku bereitet vor.*
