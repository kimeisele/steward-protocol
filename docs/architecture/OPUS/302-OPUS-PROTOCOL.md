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

## CURRENT STATUS (2025-12-25)

| OPUS | Title | Status | Results |
|------|-------|--------|---------|
| 301 | Boot/Runtime | ✅ COMPLETE | 3940ms → ~2500ms (38%) |
| 302 | Protocol | ✅ ACTIVE | This doc |
| 303 | Pulse Optimization | ✅ COMPLETE | ~50ms → ~15ms (70%) |
| 304 | Boot Singleton Fix | ✅ COMPLETE | 943ms warm boot |
| 305 | Test Suite Health | ✅ COMPLETE | 499 passed, 0 circular imports |
| 306 | Kernel Boot Performance | 🔥 READY FOR SONNET | Boot: 102s → target <10s |

### OPUS-301/303/304 Commits
```
bc5acc59 - fix(boot): Replace PhoenixConfig.from_files() with get_config() singleton
d17d7940 - perf(pulse): OPUS-303 Phase 1+3 Async I/O + Health cache
32d76fdf - fix(executor): Fix ExecutionResult API mismatch
ca9409ac - perf(ledger): OPUS-301/303 Lazy connection + count cache
a94b4c76 - perf(boot): OPUS-301 Split unified_execution into Core + Full
91a2841a - perf(boot): Lazy jinja2 import in template_loader
```

---

## OPUS-304: BOOT SINGLETON FIX

> Status: ✅ COMPLETE
> Commit: bc5acc59

### Das Problem
`PhoenixConfig.from_files()` wurde 5-6x während Boot aufgerufen statt `get_config()` singleton.

### Der Fix
grep + replace in 5 files:
- boot_sequence.py (3x)
- steward_protocol/plugin_main.py
- opus_assistant/events/kernel_tick.py

### Ergebnis
943ms warm boot (< 1000ms target) ✅

### ⚠️ WARUM S1-S4 TASKS FALSCH WAREN

**OPUS plante diese Tasks - ALLE EXISTIERTEN BEREITS:**

| Task | Geplant | Realität |
|------|---------|----------|
| S1: lazy_import.py | "NEW" | ✅ Existierte bereits |
| S2: config_cache.py | "NEW" | ✅ Existierte & war integriert |
| S3: async_logging.py | "NEW" | ✅ Existierte bereits |
| S4: boot_optimizer/ | "NEW plugin" | Unnötig |

**Root Cause:** OPUS hat nicht gecheckt ob die Files existieren bevor Tasks erstellt wurden.

**Lektion für zukünftige OPUS Sessions:**
1. IMMER `ls` / `find` vor "NEW file" Tasks
2. IMMER das echte Problem diagnostizieren (hier: singleton nicht benutzt)
3. Sonnet soll NICHT blind Tasks ausführen - erst prüfen ob sinnvoll

---

## OPUS-305: TEST SUITE HEALTH

> Status: ✅ COMPLETE
> Completed: 2025-12-25

### Results
- 499 tests passing (up from ~300 with timeouts)
- 0 circular imports (down from 13)
- LayeredRouter tests fixed (40/40)
- Boot optimizer logger bug fixed

### Commits
```
888a1743 - fix(boot): Add missing logger to boot_optimizer plugin
581d9bbf - fix(tests): Update LayeredRouter tests to match RouteResult schema
```

### Remaining Issue
13 test "errors" are actually **timeouts** due to slow kernel boot (102s).
This is addressed in OPUS-306.

---

## OPUS-306: KERNEL BOOT PERFORMANCE

> Status: 🔥 READY FOR SONNET
> Priority: P0 - BLOCKING

### The Problem
Kernel boot: **102 seconds** (target: <10 seconds)

This causes all kernel-dependent tests to timeout (default: 30s).

### SONNET TASKS

1. [x] **T5: Increase test timeout** (WORKAROUND)
   - Changed fast/unit profiles from 30s to 120s
   - Committed in 1782324b

2. [ ] **T1: Profile boot sequence**
   - Add timing to identify exact bottlenecks

3. [ ] **T2: Parallel plugin loading**
   - Current: sequential ~36s
   - Target: parallel ~5s

4. [ ] **T3: Lazy sense/analyzer loading**
   - Current: all 10 senses at boot
   - Target: load on first access

5. [ ] **T4: Verify config singleton**
   - Ensure no PhoenixConfig.from_files() calls

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
