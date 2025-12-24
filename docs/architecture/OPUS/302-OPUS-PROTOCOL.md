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

## CURRENT QUEUE

| OPUS | Status | Next Agent |
|------|--------|------------|
| 301 | Phase 1 ✅ | SONNET for Phase 2 |
| 302 | This doc | - |
| 303 | Pending | HAIKU prep needed |

---

## SONNET: OPUS-301 PHASE 2 TASKS

Execute these (from OPUS-301):

1. [ ] **Lazy jinja2** - `vibe_core/steward/loader.py`
   - Defer template loading until first use
   - Test: `python3 -X importtime` shows reduction
   - Commit when working

2. [ ] **Deferred SQLite** - `vibe_core/ledger.py` (⚠️ Ring 0)
   - Prepare code, call Senior for commit
   - Connection on first query, not init

3. [ ] **Split unified_execution** - `vibe_core/runtime/`
   - Core (routing) vs Full (execution)
   - Only load Core at boot

**When done**: Spawn Haiku to prep OPUS-303 (Runtime/Pulse optimization)

---

*Der Tanz der Modelle. Opus denkt. Sonnet handelt. Haiku bereitet vor.*
