# P0 FIX PLAN - SYSTEMATIC RECOVERY
## Generated: 2026-02-03
## Total Problems: 8 | Total Findings: 621

## 🔥 CRITICAL DISCOVERY: MahaKernel vs RealVibeKernel

**THE ROOT CAUSE:**
- `vibe_core/kernel_impl.py` (1211 lines) = **REAL KERNEL** (RealVibeKernel)
  - Process table, task scheduler, ledger, agent manifests
  - Implements VibeKernel protocol
  - Uses Balarama Pattern (MahamantraProxy)

- `vibe_core/mahamantra/kernel/maha_kernel.py` (216 lines) = **ROUTING CALCULATOR** (MahaKernel)
  - Input → Seed → Attractor → 16-Bit Address
  - Does NOT implement VibeKernel protocol
  - Used by mahamantra for resonance routing

**THESE ARE TWO DIFFERENT THINGS!** MahaKernel is NOT bypassing RealVibeKernel - they serve different purposes!

**HOWEVER:** The `hash()` fallback in MahaKernel line 127 is STILL WRONG and breaks determinism!

---

## PRIORITY ORDER (Most Critical First)

### 🔥 P0-1: Non-Deterministic hash() Usage (204 findings)
**SEVERITY:** CRITICAL - Breaks determinism guarantee
**ROOT CAUSE:** Commit `491172f9` introduced `hash()` in MahaKernel line 127
**FIX STRATEGY:**
1. Replace `hash(str(input_data))` with deterministic alternative
2. Use `hashlib.sha256()` or MahaCompression for fallback
3. Verify all 204 uses of `hash()` - replace where determinism required

**FILES TO FIX:**
- `vibe_core/mahamantra/kernel/maha_kernel.py:127` (PRIMARY)
- `vibe_core/mahamantra/adapters/compression.py:348` (SECONDARY)
- All ledger/chain hash functions (use hashlib)

**VERIFICATION:**
```python
# Before: hash('test') = random each run
# After: hashlib.sha256(b'test').digest() = deterministic
```

---

### 🔥 P0-2: Audit Trail Bypasses (163 findings)
**SEVERITY:** SECURITY - Ghost operations possible
**ROOT CAUSE:** Fail-open exception handling
**FIX STRATEGY:**
1. Replace `except Exception: pass` with proper error handling
2. Change CLI audit bypass to fail-close (block execution if audit fails)
3. Add logging to all exception handlers

**FILES TO FIX:**
- `vibe_core/mahamantra/cli/entry.py:146-147` (PRIMARY - Sankirtan bypass)
- All `except Exception: pass` patterns (163 total)

**VERIFICATION:**
```python
# Before: try: audit() except: pass  # Continues silently
# After: try: audit() except: raise AuditFailure()  # Blocks execution
```

---

### 🔥 P0-3: Assert-Based Security (4 findings)
**SEVERITY:** INTEGRITY - Checks removed in production
**ROOT CAUSE:** Using `assert` for critical integrity checks
**FIX STRATEGY:**
1. Replace all `assert` in orchestrator.py with runtime checks
2. Raise proper exceptions instead of AssertionError
3. Add tests to verify checks work in `python -O` mode

**FILES TO FIX:**
- `vibe_core/mahamantra/orchestrator.py:94,102,108,109,110,216,218,220`

**VERIFICATION:**
```python
# Before: assert xor == expected  # Removed in -O
# After: if xor != expected: raise IntegrityError()  # Always runs
```

---

### 🔥 P0-4: Circular Import Dependencies (199 findings)
**SEVERITY:** ARCHITECTURE - System fragile
**ROOT CAUSE:** Substrate imports from higher layers
**FIX STRATEGY:**
1. Break `wiring → prithu → lila → reactor → wiring` cycle
2. Move PrithuService out of substrate/wiring.py
3. Use dependency injection instead of direct imports

**FILES TO FIX:**
- `vibe_core/mahamantra/substrate/wiring.py:63-78` (PRIMARY)
- All lazy import patterns (199 total)

**VERIFICATION:**
```python
# Test: Import all modules in random order - should not crash
```

---

### ⚠️ P0-5: Duplicate State Systems (6 systems, 221 ServiceRegistry uses)
**SEVERITY:** ARCHITECTURE - No SSOT for state
**ROOT CAUSE:** Multiple parallel state management systems
**FIX STRATEGY:**
1. Make MahaState the SINGLE sovereign adapter
2. Route all state operations through MahaState
3. Deprecate direct access to StateService, Prakriti, etc.

**FILES TO FIX:**
- Consolidate all state access through `MahaState.get_instance()`
- Update 221 ServiceRegistry calls to use unified pattern

**VERIFICATION:**
```python
# All state operations go through ONE entry point
```

---

### ⚠️ P0-6: Research Code in Production (8 findings)
**SEVERITY:** STABILITY - Unstable dependencies
**ROOT CAUSE:** Production imports from research/
**FIX STRATEGY:**
1. Move stable research code to production paths
2. Add deprecation warnings to research imports
3. Remove research imports from production code

**FILES TO FIX:**
- `vibe_core/mahamantra/kernel/maha_kernel.py:27` (LotusArrayInt)
- `vibe_core/cli/kirtan_cli.py:127,321` (research_chat)
- 5 other files

---

### ⚠️ P0-7: Service Instantiation Bypasses (36 findings)
**SEVERITY:** ARCHITECTURE - Breaks routing
**ROOT CAUSE:** Direct `Service()` calls instead of mahamantra routing
**FIX STRATEGY:**
1. Replace all direct instantiation with ServiceRegistry.get()
2. Enforce Balarama pattern globally
3. Add linter rule to prevent direct instantiation

**FILES TO FIX:**
- `vibe_core/mahamantra/commands.py:523` (JanakaService)
- `vibe_core/mahamantra/cli/samskara.py:31` (SamskaraService)
- 34 other direct instantiations

---

### ⚠️ P0-8: Incomplete Balarama Pattern (43 direct vs 10 proxy)
**SEVERITY:** ARCHITECTURE - Inconsistent governance
**ROOT CAUSE:** Balarama pattern not enforced globally
**FIX STRATEGY:**
1. Wrap ALL service instantiations with MahamantraProxy
2. Update kernel to enforce proxy pattern
3. Add tests to verify all services are proxied

**FILES TO FIX:**
- All 43 direct Service() instantiations
- Enforce in ServiceRegistry

---

## EXECUTION PLAN

### Phase 1: CRITICAL FIXES (P0-1, P0-2, P0-3)
**Time Estimate:** 2-4 hours
**Risk:** LOW - Isolated changes
**Verification:** Run P0_AUDIT_VERIFICATION.py after each fix

### Phase 2: ARCHITECTURE FIXES (P0-4, P0-5)
**Time Estimate:** 4-8 hours
**Risk:** MEDIUM - Requires refactoring
**Verification:** Full test suite + import tests

### Phase 3: CLEANUP (P0-6, P0-7, P0-8)
**Time Estimate:** 2-4 hours
**Risk:** LOW - Mechanical changes
**Verification:** Linter + test suite

---

## ROLLBACK STRATEGY

If any fix breaks the system:
1. Git stash changes
2. Run P0_AUDIT_VERIFICATION.py to verify baseline
3. Apply fix incrementally
4. Test after each file change

---

## SUCCESS CRITERIA

- [ ] P0_AUDIT_VERIFICATION.py shows 0 CRITICAL findings
- [ ] All tests pass
- [ ] System boots without errors
- [ ] Determinism tests pass (same input = same output across runs)

