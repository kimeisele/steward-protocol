# STEWARD PROTOCOL — INCOMPLETE INFRASTRUCTURE AUDIT

**Generated:** 2026-02-26
**Scope:** All "wired but never called" components causing silent failures
**GitHub Issue:** #835

---

## CRITICAL FINDINGS

### 1. SECURITY — identity_tool Parameter (CRITICAL)
**File:** `docs/architecture/archive/SOLID_HARDENING_PLAN.md`
**Finding:** `identity_tool` parameter is accepted but NEVER CALLED
**Impact:** Signatures in oath events are completely ignored
**Risk:** Anyone can forge an oath — authentication is THEATER
**Status:** UNFIXED

### 2. KERNEL PROTECTION — Verification Theater (CRITICAL)
**File:** `docs/architecture/OPUS/024-KERNEL-PROTECTION-AUDIT.md`
**Finding:**
- `verify_kernel.py` exists but NEVER CALLED
- Pre-commit only guards 1 of 3 files
- CI runs verification but result ignored
**Impact:** Kernel modifications not actually protected
**Status:** UNFIXED

### 3. CIRCUIT EXECUTOR — Wired but Dead (HIGH)
**File:** `vibe_core/plugins/moltbook/plugin_main.py`
**Timeline:**
- Feb 23: Circuit wired (commit f876b3640)
- Feb 24: Circuit failed → kernel._agent_registry crash
- Feb 24: Fallback created, circuit abandoned (commit 89f5feec3)
- Now: Circuit is dead code, GOVARDHAN GATES bypassed
**Impact:** No governance, no PANCHA TATTVA validation
**Status:** UNFIXED (requires kernel._agent_registry fix)

### 4. LOGGING LIFECYCLE — shutdown_async_logging() (MEDIUM)
**File:** `docs/architecture/OPUS/305-TEST-SUITE-HEALTH.md`
**Finding:** `shutdown_async_logging()` exists but NEVER CALLED
**Impact:** Async logging may not flush on shutdown → lost logs
**Status:** UNFIXED

### 5. INTENT INFRASTRUCTURE — IntentBridge Dead (MEDIUM)
**File:** `docs/architecture/OPUS/173-INTENT-BACKLOG-BRIDGE.md`
**Finding:** IntentBridge created but NEVER CALLED
**Impact:** Intent backlog system non-functional
**Status:** UNFIXED

### 6. PRANA ORCHESTRATION — on_pulse() Never Called (MEDIUM)
**File:** `docs/architecture/moltbook/REVIEW_2026-02-23.md`
**Finding:** `on_pulse()` exists but never called by PranaOrchestrator
**Impact:** Prana signaling incomplete
**Status:** UNFIXED

---

## DESIGN PHASE (Not Yet Implemented)

| Status | File | Component | Impact |
|--------|------|-----------|--------|
| DESIGN | moltbook/AGENCY.md | MOLTBOOK_CONTENT_V1 Full Circuit | No governance gates |
| DESIGN | OPUS/009 | prakriti.guna_thresholds | Incomplete harmonics |
| DESIGN | OPUS/150 | Interface layer "Skin" | No UI protocol |
| DESIGN | OPUS/308 | FILESYSTEM-UI-PROTOCOL | Design only |
| DESIGN | OPUS/032 | Semantic Verification | Not implemented |
| DESIGN | OPUS/309 | FRACTAL-CLI-COGNITIVE-HOOK | Design only |
| DESIGN | architecture/ | MARKDOWN_UI_ENHANCEMENT | Design only |
| DESIGN | WIRING_ROADMAP_V3 | Playbook execution in kernel | Not in kernel |

---

## ROOT CAUSE PATTERN

### The "Wire → Crash → Fallback → Abandon" Pattern

```
1. Feature DESIGNED (doc + design doc written)
2. Feature WIRED (integrated into bootstrap/init)
3. Feature ATTEMPTED (first use attempt)
4. Feature CRASHES (error handling/fallback activates)
5. Feature ABANDONED (fallback becomes permanent)
6. Feature DEAD CODE (wired but never called again)
```

This happens because:
- ✅ Code compiles (no syntax errors)
- ✅ Tests pass (tests often test wrong thing or test isolation)
- ✅ Fallbacks hide errors (silent failures)
- ❌ No verification that ACTUAL execution path uses feature
- ❌ No monitoring for "feature was wired but path never taken"

### Why This Happens

1. **Fallback tolerance:** System has safe fallbacks, so failures are hidden
2. **Test isolation:** Unit tests work, integration fails silently
3. **No execution tracing:** No logging of "feature was/was not called"
4. **Incomplete migrations:** Features wired mid-refactor then abandoned
5. **Gradual decay:** Working code around failures, never return to fix

---

## SYSTEMATIC FIXES REQUIRED

### Phase 1: Surface the Problems (1-2 days)
- [ ] Add logging: every wired component logs "activated" on first call
- [ ] Add metrics: track "wired but never called" patterns
- [ ] Audit test coverage: verify integration tests actually exercise new paths

### Phase 2: Fix Critical Issues (3-5 days)
- [ ] Identity tool: wire signature verification into oath system
- [ ] Kernel protection: make verify_kernel.py part of actual CI
- [ ] Circuit executor: fix kernel._agent_registry crash, activate circuit path

### Phase 3: Complete Abandoned Features (1-2 weeks)
- [ ] Prana signaling: activate on_pulse() in orchestrator
- [ ] Intent system: verify IntentBridge is called
- [ ] Logging: call shutdown_async_logging() on exit

### Phase 4: Complete Design Phase Features (2-4 weeks)
- [ ] Classify each DESIGN doc: implement or deprecate
- [ ] For implemented ones: activate in execution path
- [ ] For deprecated: delete code + doc

---

## VERIFICATION CHECKLIST

For each "wired" component:
1. ✅ Does it exist in code?
2. ✅ Is it initialized/wired at boot?
3. **❌ Is it CALLED in the actual execution path?** ← THIS IS WHERE WE FAIL
4. ✅ Does it have tests?
5. ❌ Do those tests actually exercise the REAL path? ← TESTING ILLUSION

---

## PRIORITY ORDER (Severity × Impact)

1. **CRITICAL** — Identity tool (security breach)
2. **CRITICAL** — Kernel protection (security theater)
3. **HIGH** — Circuit executor (governance missing)
4. **MEDIUM** — Async logging (data loss)
5. **MEDIUM** — Prana orchestration (incomplete architecture)
6. **LOW** — Design phase features (not yet critical)

---

## OWNER: Opus

All of these need Opus's attention because they require:
- Kernel-level fixes (circuit executor)
- Architecture decisions (which features to complete vs. deprecate)
- Systematic verification (code → execution path tracing)

This is NOT a task for incrementalists. This is CTO-level work.
