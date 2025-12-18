# OPUS-110: BIG BUG HUNT

> **Status:** ACTIVE INVESTIGATION
> **Created:** 2024-12-18
> **Mission:** Verify MANAS is truly alive, not a zombie

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

## Known Gaps (To Hunt)

| ID | Area | Issue | Severity | Status |
|----|------|-------|----------|--------|
| GAP-001 | Events | KernelTickHandler not wired in headless | CRITICAL | FIXED (OPUS-091) |
| GAP-002 | Provider | OpenRouter key misdetected | CRITICAL | FIXED (86d971d) |
| GAP-003 | Manifest | Ghost files in state_files | HIGH | FIXED (OPUS-096) |
| GAP-004 | ? | ? | ? | HUNTING |

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
