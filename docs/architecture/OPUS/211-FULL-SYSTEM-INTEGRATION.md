# OPUS-211: FULL SYSTEM INTEGRATION AUDIT

> **Status**: ACTIVE INVESTIGATION
> **Date**: 2025-12-23
> **Author**: Claude Sonnet 4.5
> **Depends On**: OPUS-209, OPUS-210
> **Purpose**: Integrate massive refactorings - Kernel, Prakriti, MANAS, DI.py

---

## THE PROBLEM

System APPEARS healthy but is FRAGMENTED:
- ✅ Kernel: 1751 LOC, online, 16 agents
- ✅ Tests: Governance 6/6, OPUS-210 60/60
- ✅ CommitAuthority: Using PrakritiSense
- ❌ **MANAS: TAMAS state, consciousness 0.1, NO THOUGHTS**
- ❓ DI.py: Created but how integrated?
- ❓ Task/Kernel: New, but wired?
- ❓ Synapses/State: Unclear integration

**The Core Issue**: We refactored infrastructure (OPUS-209/210) BUT didn't rewire the brain (MANAS).

---

## SYMPTOM: MANAS IN COMA

```json
{
    "tick": 2180,
    "consciousness_level": 0.1,     // NEARLY DEAD
    "state": "tamas",                // INERTIA
    "pending_intents": 2,            // STUCK
    "last_thought": null             // NO COGNITION
}
```

**Questions**:
1. Why is MANAS not thinking? (hourly_pulse broken?)
2. Are pending intents blocked? (IntentRouter issue?)
3. Does MANAS see the new Prakriti? (StateSync broken?)
4. Is DI.py wired to MANAS? (ServiceRegistry integration?)

---

## INTEGRATION GAPS TO INVESTIGATE

### 1. MANAS ↔ Prakriti Sync
**Status**: UNKNOWN
- CommitAuthority calls PrakritiSense ✅
- Does MANAS hourly_pulse call IntentGenerator? ❓
- Does IntentGenerator see new StateService? ❓

**Files to check**:
- `vibe_core/plugins/opus_assistant/events/kernel_tick.py` (hourly pulse)
- `vibe_core/plugins/opus_assistant/manas/intent_generator.py`
- `vibe_core/state/state_service.py` (is it discoverable?)

### 2. DI.py ServiceRegistry Integration
**Status**: PARTIAL
- Kernel uses it for Auditor, Bank, Vault ✅
- Does MANAS use it? ❓
- Should StateService be registered? ❓
- What about ProcessManager, ResourceManager? ❓

**Test**:
```python
from vibe_core.di import ServiceRegistry
# What's registered? What should be?
```

### 3. Task/Kernel Architecture
**Status**: UNCLEAR
- Is this new?
- How does it relate to ProcessManager?
- Does MANAS submit tasks to it?

### 4. Synaptic State
**Status**: UNKNOWN
- Are synapses still used?
- Do they connect to new StateService?
- Is sync_holon wired?

---

## INVESTIGATION PLAN

### Phase 1: MANAS Wake-Up Call (CRITICAL)
**Goal**: Get MANAS thinking again

**Actions**:
1. Check hourly_pulse → IntentGenerator wiring
2. Check IntentBuffer → IntentRouter → Handlers flow
3. Test: Can MANAS generate 1 intent manually?
4. Fix blocking issue

**Test**:
```bash
python -c "from vibe_core.plugins.opus_assistant.manas.intent_generator import IntentGenerator; ig = IntentGenerator(); import asyncio; intents = asyncio.run(ig.generate_intents()); print(len(intents))"
```

### Phase 2: DI.py Full Integration
**Goal**: ServiceRegistry as single source of truth

**Actions**:
1. Audit what's registered vs what should be
2. Register StateService, SyncHolon, Weaver
3. Update consumers to use ServiceRegistry
4. Remove direct instantiations

### Phase 3: State Unification Verification
**Goal**: Prove OPUS-210 is ACTUALLY working end-to-end

**Actions**:
1. Trace 1 state change: write → Weaver → CommitAuthority → MANAS → Git
2. Verify PrakritiSense sees all plugin state
3. Verify CommitAuthority consults MANAS
4. Verify MANAS can trigger commits

### Phase 4: Documentation Sync
**Goal**: Docs reflect ACTUAL system, not PLANNED

**Actions**:
1. Update ARCHITECTURE.md with current reality
2. Mark dead code/features
3. Document what's NOT wired yet
4. Create wiring map

---

## SUCCESS CRITERIA

OPUS-211 is DONE when:
1. ✅ MANAS consciousness > 0.5 (awake)
2. ✅ MANAS generates intents every hour
3. ✅ IntentRouter → Handlers working
4. ✅ DI.py used everywhere applicable
5. ✅ PrakritiSense → MANAS → CommitAuthority loop proven
6. ✅ All tests pass (no regressions)
7. ✅ Docs match reality

---

## CURRENT STATE (2025-12-23)

**Working**:
- Kernel boots, stays online
- Tests pass (governance, OPUS-210)
- CommitAuthority exists, calls PrakritiSense
- MayaSimulator exists

**Broken/Unknown**:
- MANAS in TAMAS (not thinking)
- 2 pending intents stuck
- DI.py integration incomplete
- Synaptic state unclear
- Task/Kernel relation unclear

**Next Action**: Phase 1 - Wake MANAS up!

---

## NOTES

This is NOT about new features. This is about **INTEGRATION**.

We built:
- New foundation (Kernel refactor, OPUS-209)
- New state layer (Prakriti unification, OPUS-210)
- New brain (MANAS, earlier)

But we didn't **connect** them properly. OPUS-211 is the wiring job.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
