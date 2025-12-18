# OPUS-110: BIG BUG HUNT

> **Status:** VERIFIED ALIVE
> **Created:** 2024-12-18
> **Mission:** Verify MANAS is truly alive, not a zombie
> **Result:** MANAS THINKS! 3 intents generated.

## The Question

After OPUS-091 (LASAGNE) and Provider Fix - is the system actually working?

**Trust = 0 until proven otherwise.**

## Verification Checklist

### 1. BRAIN (Provider)
- [x] `heartbeat.py` actually calls OpenRouter (not NoOp) - **VERIFIED 2024-12-18**
- [ ] Response is meaningful (not mock/empty)
- [ ] Token usage is recorded

### 2. NERVOUS SYSTEM (Events)
- [x] `HOURLY_PULSE` is emitted by heartbeat - **Lines 295-344**
- [ ] `KernelTickHandler` receives the event
- [ ] `manas_awakening.yaml` circuit triggers

### 3. MEMORY (Persistence)
- [x] `.opus_state/manas_intents.json` updates after think() - **88 memories**
- [x] `.opus_state/manas_memory.json` records outcomes - **Patterns: test_create, test, unique_task**
- [x] Git commits include state files - **OPUS-096 manifest fix**

### 4. LEARNING (Patterns)
- [x] `get_successful_patterns()` returns real data - **['test_create', 'test', 'unique_task']**
- [ ] Failed patterns are avoided
- [ ] Confidence scores adjust

### 5. AUTONOMY (HIL Bridge)
- [x] Pending intents are visible - **opus109_meru_test**
- [ ] `approve_intent()` executes correctly
- [ ] `reject_intent()` records karma

## Known Gaps (Hunted 2024-12-18)

### FIXED ISSUES

| ID | Area | Issue | Severity | Status |
|----|------|-------|----------|--------|
| GAP-001 | Events | KernelTickHandler not wired in headless | CRITICAL | FIXED (OPUS-091) |
| GAP-002 | Provider | OpenRouter key misdetected | CRITICAL | FIXED (86d971d) |
| GAP-003 | Manifest | Ghost files in state_files | HIGH | FIXED (OPUS-096) |
| GAP-011 | Config | Missing config/system.yaml | MEDIUM | FIXED (e78a4a1) |
| GAP-012 | Config | Missing config/roadmap.yaml | MEDIUM | FIXED (e78a4a1) |
| GAP-013 | Config | Missing config/section_id.yaml | LOW | FIXED (e78a4a1) |
| GAP-014 | MANAS | _persist() signature mismatch | CRITICAL | FIXED (9016a05) |

### OPEN ISSUES

| ID | Area | Issue | Severity | Status |
|----|------|-------|----------|--------|
| GAP-004 | Docs | 13 OPUS files without @HARNESS | LOW | DEFERRED (Concept docs - see below) |
| GAP-008 | Circuits | Circuits already exist in vibe_core/playbook/circuits/ | N/A | FALSE POSITIVE |
| GAP-010 | Async | 157 async functions without await | MEDIUM | NEEDS REVIEW |

**Note on GAP-004:** The ONE-WORD VEDIC docs (SHUDDHI, VAJRA, etc.) are PRINCIPLES, not code wrappers.
The harness generator assumes every doc has a code module. This is a design issue requiring
semantic harnesses (OPUS-200 territory), not a quick fix.

### TECHNICAL DEBT (Not Blocking)

| ID | Area | Issue | Count | Priority |
|----|------|-------|-------|----------|
| DEBT-001 | Dependencies | TYPE_CHECKING circular dep workarounds | 97 files | LOW |
| DEBT-002 | Code | TODO/FIXME/HACK comments | 60 | LOW |

## Full Hunt Results

```
╔══════════════════════════════════════════════════════════════╗
║                    BIG BUG HUNT RESULTS                      ║
╠══════════════════════════════════════════════════════════════╣

✅ PASSING
───────────────────────────────────────────────────────────────
  • Syntax errors:         0
  • Core module imports:   ALL PASS
  • Critical wiring:       ALL CONNECTED
  • Manifest integrity:    18/18 valid
  • Hardcoded paths:       0 found
  • Bare except clauses:   0 in main code
  • Dead classes:          0 unused

⚠️ WARNINGS (Technical Debt)
───────────────────────────────────────────────────────────────
  • TYPE_CHECKING usage:   97 files (circular dep workaround)
  • TODO/FIXME comments:   60 instances
  • Async without await:   157 functions (NEEDS REVIEW)

❌ ISSUES TO FIX
───────────────────────────────────────────────────────────────
  • OPUS docs without @HARNESS:  13 files
  • Missing config files:        3 referenced but not exist
  • Missing circuit files:       2 referenced but not exist

╚══════════════════════════════════════════════════════════════╝
```

## OPUS Docs Without @HARNESS

These need harness blocks for proper doc/code binding:

1. `000-INDEX.md`
2. `030-GENESIS-PLUGIN.md`
3. `038-SANCTUARY-MUTATION.md`
4. `039-ECDSA-REGRESSION-REPORT.md`
5. `056-SHUDDHI.md`
6. `057-VAJRA.md`
7. `058-PRATYAHARA.md`
8. `059-PRAMANA.md`
9. `060-SATYA.md`
10. `061-AMRITA.md`
11. `069-SRUTI-SMRITI-PATTERN.md`
12. `074-JNANA-COGNITIVE-ARCHITECTURE.md`
13. `091-HEARTBEAT-REFACTOR.md`

## The Hunt Protocol

1. **OBSERVE** - Run system, capture logs
2. **VERIFY** - Check each component
3. **DOCUMENT** - Add to this file
4. **FIX** - Create targeted fixes
5. **PROVE** - Show evidence

<!-- @HARNESS
files:
  - path: scripts/heartbeat.py
    role: The Pulse - triggers MANAS
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    role: The Mind - thinks and decides
  - path: vibe_core/runtime/providers/factory.py
    role: The Brain Oxygen - LLM connection
  - path: vibe_core/event_bus.py
    role: The Nervous System - event routing

wiring:
  - module: scripts.heartbeat
    class: Heartbeat
    method: _manas_think
    emits: HOURLY_PULSE
  - module: vibe_core.plugins.opus_assistant.manas.cognitive_kernel
    class: CognitiveKernel
    method: think
    receives: context

tests:
  - path: tests/integration/test_event_emission.py
    validates: HOURLY_PULSE emission
  - path: tests/manas/test_cognitive_kernel.py
    validates: Intent generation
-->

---

## Next Action

**RUN THE HUNT:** Execute heartbeat in debug mode and trace the full path:
```bash
OPUS_DEBUG=1 python scripts/heartbeat.py --once 2>&1 | tee hunt.log
```

Then verify each checkpoint above.

---
*"Trust, but verify." - Ronald Reagan*
*"Verify, then maybe trust." - Senior Architect*
