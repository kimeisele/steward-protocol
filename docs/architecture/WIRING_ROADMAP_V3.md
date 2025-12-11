# WIRING ROADMAP V3 - Playbook Execution & Audit Refinement

> **Created:** 2025-12-04 by Opus (Senior Verification Sprint #3)
> **Previous:** WIRING_ROADMAP_V2.md (P3-P6 fixes implemented by Sonnet)
> **Status:** P3-P6 VERIFIED DONE → Now P7+ (Final Wiring)

---

## Verification Summary (Opus Audit)

### VERIFIED FIXES (Sonnet's Work)

| ID | Issue | Status | Evidence |
|----|-------|--------|----------|
| P3.1 | agent.set_kernel(self) missing | ✅ FIXED | `kernel_impl.py:730` |
| P4.1 | Critical/Gajendra path missing | ✅ FIXED | `envoy/cartridge_main.py:200-208` |
| P4.2 | Lazy path missing | ✅ FIXED | `envoy/cartridge_main.py:230` |
| P5.1 | Action handlers stubs | ✅ FIXED | `action_handlers.py` - all 5 handlers implemented |
| P6.1 | Async process() mismatch | ✅ NOT A BUG | Kernel handles both (lines 961-964) |

### Kernel Dispatch Pattern (WORKING)
```python
# kernel_impl.py:961-964 - Handles both sync and async
if asyncio.iscoroutinefunction(agent.process):
    result = asyncio.run(agent.process(task))
else:
    result = agent.process(task)
```

---

## P7: REMAINING ISSUES (Real, Not False Positives)

### P7.1 CallPlaybookHandler is STUB (HIGH)

**Problem:** The `CALL_PLAYBOOK` action type cannot execute nested playbooks.

**Evidence:**
```python
# steward/system_agents/envoy/action_handlers.py:521-530
logger.warning("⚠️ Playbook execution stub - implement kernel.execute_playbook()")

return ActionResult.ok({
    "playbook": target,
    "status": "stub",  # ← PROBLEM
    "message": "Playbook execution not yet implemented in kernel",
})
```

**Root Cause:** Kernel has no `execute_playbook()` method.

**Fix Required:**
```python
# vibe_core/kernel_impl.py - ADD METHOD
async def execute_playbook(
    self,
    playbook_path: str,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a playbook through the DeterministicExecutor."""
    from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

    executor = DeterministicExecutor(kernel=self)
    return await executor.execute_playbook(playbook_path, input_data)
```

**Then update action_handlers.py:516-530:**
```python
# Replace stub with real call
result = await context.kernel.execute_playbook(playbook_path, input_data)
return ActionResult.ok({
    "playbook": target,
    "path": playbook_path,
    "status": "executed",
    "result": result,
})
```

**Files to modify:**
1. `vibe_core/kernel_impl.py` - Add `execute_playbook()` method
2. `steward/system_agents/envoy/action_handlers.py` - Replace stub call
3. `steward/system_agents/envoy/deterministic_executor.py` - Ensure `execute_playbook()` exists

---

### P7.2 WIRING_AUDIT False Positives (MEDIUM)

**Problem:** The audit reports 38 "stubs" but most are false positives:
- Deprecated classes with helpful error messages (intentional)
- Abstract base classes (NotImplementedError is correct pattern)
- Templates (TODOs expected)
- Example agents (not core system)

**Fix Required:** Update audit script to exclude known false positives.

**File:** `steward/system_agents/envoy/tools/wiring_audit_scripts.py`

**Add exclusion list:**
```python
# Line ~230 - Add after exclude_files
EXCLUDE_PATTERNS = [
    # Intentional deprecation stubs
    "vibe_core/specialists/__init__.py",
    # Abstract base classes (NotImplementedError is correct)
    "vibe_core/specialists/base_specialist.py",
    "vibe_core/playbook/executor.py",
    # Templates (TODOs expected)
    "starter-packs/",
    "engineer/templates/",
    # Example agents (not core)
    "agent_city/registry/",
    # Audit tool itself
    "wiring_audit_scripts.py",
]
```

---

## P8: STRETCH GOALS (Nice to Have)

### P8.1 DeterministicExecutor.execute_playbook() Validation

Verify the executor can actually load and run YAML playbooks end-to-end.

**Test:** Create integration test that:
1. Loads `vibe_core/playbook/circuits/wiring_audit.yaml`
2. Executes through kernel.execute_playbook()
3. Verifies output contains audit results

### P8.2 Action Handler Coverage

Add missing script handlers to ExecuteScriptHandler:
```python
# action_handlers.py - _scripts registry
self._scripts = {
    "scaffold.create_folders": self._create_folders,
    "scaffold.init_git": self._init_git,
    "file.write": self._write_file,
    "file.read": self._read_file,
    # ADD THESE:
    "git.commit": self._git_commit,
    "git.push": self._git_push,
    "shell.run": self._shell_run,
}
```

---

## Implementation Order

### Phase 1: Core Fix (P7.1)
1. Add `kernel.execute_playbook()` method
2. Update CallPlaybookHandler to use real call
3. Verify DeterministicExecutor.execute_playbook() works

### Phase 2: Tooling Fix (P7.2)
1. Update WIRING_AUDIT with exclusion patterns
2. Re-run audit to verify false positive reduction
3. Target: <5 issues remaining

### Phase 3: Integration Test
1. Create end-to-end playbook execution test
2. Verify CALL_PLAYBOOK action works in real circuit

---

## Execution Commands

```bash
# After fixes, run audit to verify
python steward/system_agents/envoy/tools/wiring_audit_scripts.py --scope full

# Expected result: <10 issues (mostly LOW/INFO)
```

---

## Success Criteria

1. [ ] `kernel.execute_playbook()` exists and works
2. [ ] CallPlaybookHandler returns real results, not "stub"
3. [ ] WIRING_AUDIT shows <10 issues after exclusion fixes
4. [ ] Integration test for CALL_PLAYBOOK passes

---

*"The last mile is always the hardest. But we're almost there."*
— Opus, Senior Sprint #3
