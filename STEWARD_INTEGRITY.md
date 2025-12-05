# STEWARD INTEGRITY PLAN

> "Half-finished wiring kills the system" - The Reality

**Created**: 2025-12-05
**Status**: 🔴 CRITICAL - System works but wiring is spaghetti

---

## THE REAL PROBLEMS

### 1. Auto-Generated Files Chaos
**Problem**: MD files (OPERATIONS.md, SETTINGS.md, etc.) change every tick
- ✅ They MUST be in git (they're the UI!)
- ❌ They cause merge conflicts constantly
- ❌ No strategy for conflict-free updates

**What's Missing**:
- Auto-commit strategy for generated files
- Atomic updates (read-modify-write with file locks)
- Conflict resolution rules

### 2. No Integration Checks
**Problem**: System reports "healthy" but logs show errors
- Agents report errors but kernel says OK
- Plugins hook into tick but nobody checks if they work
- No regression detection

**What's Missing**:
- Boot-time integrity checks (MUST pass or HALT)
- Plugin health monitoring
- Integration test suite that runs on every deploy

### 3. Half-Finished Plugin Extraction
**Problem**: Opus extracted plugins but left broken wiring
- ✅ FIXED: VedicGovernancePlugin API (pause/resume/registries)
- ✅ FIXED: SettingsSync parser (markdown separators)
- ❌ TODO: OPERATIONS.md error handling
- ❌ TODO: Agent report_status() audit

---

## ROADMAP: Next 2-3 Hours

### Phase 1: AUDIT (30 min)
**Goal**: Know EXACTLY what's broken

- [ ] Boot system, capture ALL errors/warnings
- [ ] List all auto-generated MD files
- [ ] Check which plugins actually fire hooks
- [ ] Find all agents with broken report_status()
- [ ] Document in this file

### Phase 2: INTEGRITY PLUGIN (1 hour)
**Goal**: System KNOWS when it's broken

Create `vibe_core/plugins/integrity.py`:
```python
class IntegrityPlugin(KernelPlugin):
    """
    Checks system integrity on every tick.

    Boot-time checks (HALT on failure):
    - All agents can report_status()
    - All plugins have valid hooks
    - Auto-generated files are writable
    - Git state is clean (or known dirty)

    Runtime checks (LOG warnings):
    - Plugins that should fire but don't
    - Agents reporting errors
    - Tick rate degradation
    """
```

**Hooks**:
- `on_boot()`: Run critical checks, HALT if fail
- `on_tick_post()`: Monitor runtime health
- `on_shutdown()`: Report final state

### Phase 3: AUTO-GENERATED FILE STRATEGY (1 hour)
**Goal**: No more merge conflicts

**Option A: Atomic Updates**
- Use file locks (already have `vibe_core/task_management/file_lock.py`)
- Read-modify-write pattern
- Timestamp-based conflict detection

**Option B: Git Auto-Commit**
- Plugin commits auto-gen files after render
- Commit message: `chore(auto): Update OPERATIONS.md [skip ci]`
- Pull before push (rebase strategy)

**Option C: Separate Branch**
- Auto-gen files live on `auto-gen` branch
- Main branch has stubs only
- Merge strategy handles conflicts

**DECISION NEEDED**: Which option?

### Phase 4: FIX REMAINING P0 (30 min)
**Goal**: Clean logs, no hidden errors

- [ ] Fix OPERATIONS.md error handling (P0.3)
- [ ] Audit all agent report_status()
- [ ] Test with full boot cycle
- [ ] Verify logs are clean

---

## INTEGRATION CHECKLIST

**BEFORE building more features**, these MUST work:

### Boot Integrity ✅/❌
- [ ] All 27 agents boot without errors
- [ ] All 8 plugins load and hook correctly
- [ ] No warnings in first 10 seconds of boot
- [ ] SETTINGS.md renders without errors
- [ ] OPERATIONS.md renders without errors

### Plugin Health ✅/❌
- [ ] VedicGovernancePlugin: pause/resume work
- [ ] SargaCyclePlugin: DAY/NIGHT_OF_BRAHMA transitions
- [ ] SettingsUIPlugin: Commands parse correctly
- [ ] EnvoyUIPlugin: Renders without errors
- [ ] GitHistoryPlugin: GIT.md generates correctly
- [ ] TestOrchestrationPlugin: All tests discoverable

### Auto-Generated Files ✅/❌
- [ ] OPERATIONS.md: No errors, updates every tick
- [ ] SETTINGS.md: No errors, commands work
- [ ] AGENTS.md: All agents listed
- [ ] ENVOY.md: Routes correct
- [ ] GIT.md: Stats accurate
- [ ] EPHEMERAL.md: Updates correctly

### Git Hygiene ✅/❌
- [ ] No untracked critical files
- [ ] Auto-gen files have strategy
- [ ] Commits are atomic (all or nothing)
- [ ] No merge conflicts on auto-gen files

---

## METRICS FOR SUCCESS

**After this work, system should**:
1. Boot with ZERO warnings in first 10 seconds
2. All agents report "healthy" (and mean it)
3. Auto-gen files update without conflicts
4. Integration checks run on every boot
5. Logs are clean (no error spam)

**How to measure**:
```bash
# Boot and check logs
python boot.py 2>&1 | grep -E "(ERROR|CRITICAL|⚠️)" | head -20

# Should be empty or only expected warnings (credentials, etc.)
```

---

## NEXT AGENT TO BUILD

**ONLY AFTER integrity is solid**:
- RoadmapPlugin: Tracks progress, checks regressions
- Or: AuditorPlugin: Enforces quality on boot
- Or: Whatever you need - but foundation must be solid first

---

## PHILOSOPHY

> "Das System muss sich selbst überprüfen können."

We're building an Agent Operating System. Like any OS:
- **Boot checks are mandatory** (POST, BIOS checks)
- **Runtime monitoring is continuous** (watchdog, health checks)
- **Failures are visible** (kernel panic, not silent errors)

No more half-finished wiring. No more "works but logs show errors."

**STEWARD means taking responsibility for system integrity.**

---

*This is the plan. Execute it. Don't build more features until this is done.*
