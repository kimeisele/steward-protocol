# GEMINI TASK: Migrate 33 Test Files to PANOPTICON+ Fixtures

**Priority**: Medium (Tech Debt Cleanup)
**Effort**: ~2-3 hours
**Type**: Repetitive refactoring (no design decisions needed)

---

## Objective

Migrate 33 test files from direct `RealVibeKernel` usage to standardized `TestKernel` fixtures. This improves test isolation and consistency.

---

## Pre-Requisites

```bash
# Verify you're on main and up to date
git checkout main && git pull

# Create feature branch
git checkout -b feat/test-fixture-migration

# Verify current state (should show 33 WARNED)
python3 -c "
from pathlib import Path
from vibe_core.plugins.test_orchestration import validate_test_files
results = validate_test_files([str(f) for f in Path('tests').glob('**/*.py')])
warned = [r for r in results if r['verdict'] == 'warn']
print(f'Files to migrate: {len(warned)}')
"
```

---

## Migration Pattern

### Pattern 1: Kernel Instantiation

```python
# BEFORE
from vibe_core.kernel_impl import RealVibeKernel
kernel = RealVibeKernel(ledger_path=":memory:")

# AFTER
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.plugins.test_orchestration import TestAgents
kernel = RealVibeKernel(ledger_path=":memory:")
# Note: TestKernel.minimal() is preferred but RealVibeKernel is acceptable
# The key fix is using TestAgents instead of custom agent classes
```

### Pattern 2: Agent Creation (CRITICAL)

```python
# BEFORE - FORBIDDEN
class MyTestAgent(VibeAgent):
    def __init__(self):
        super().__init__(agent_id="test", ...)
        self.oath_sworn = True  # FORBIDDEN!

agent = MyTestAgent()

# AFTER - CORRECT
from vibe_core.plugins.test_orchestration import TestAgents

agent = TestAgents.compliant("test-agent")           # Normal compliant agent
agent = TestAgents.without_oath("bad-agent")         # For governance rejection tests
agent = TestAgents.with_false_oath("liar-agent")     # For false oath tests
```

### Pattern 3: Add Required Import

```python
# If file uses RealVibeKernel or creates agents, add this import:
from vibe_core.plugins.test_orchestration import TestAgents
```

---

## Files to Migrate

Run this command to get the current list:

```bash
python3 -c "
from pathlib import Path
from vibe_core.plugins.test_orchestration import validate_test_files
results = validate_test_files([str(f) for f in Path('tests').glob('**/*.py')])
for r in results:
    if r['verdict'] == 'warn':
        print(r['file_path'])
"
```

---

## DO NOT TOUCH These Files

These are intentionally excluded from validation rules:

- `tests/hardening/*` - Security tests need custom agents
- `tests/archive/*` - Deprecated code
- Files containing `test_governance` - Need custom oath handling
- Files containing `test_red_team` - Security testing
- Files containing `test_capability` - Capability testing
- Files containing `test_event_bus` - Event system testing

---

## Validation After Each File

```bash
# 1. Run the specific test file
python -m pytest <file_path> -v --tb=short

# 2. Check PANOPTICON+ validation (should not be BLOCKED)
python3 -c "
from vibe_core.plugins.test_orchestration import validate_test_file
result = validate_test_file('<file_path>')
print(f\"Verdict: {result['verdict']}\")
print(f\"Blocked: {result['blocked']}\")
"
```

---

## Commit Strategy

Commit in batches of ~5-10 files:

```bash
git add tests/path/to/migrated_files...
git commit -m "refactor: Migrate test files to TestAgents fixtures (batch N)

Files migrated:
- tests/file1.py
- tests/file2.py
...

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"
```

---

## Final Validation

After all migrations:

```bash
# 1. Full PANOPTICON+ validation (should show 0 WARNED for migrated files)
python3 -c "
from pathlib import Path
from vibe_core.plugins.test_orchestration import validate_test_files
results = validate_test_files([str(f) for f in Path('tests').glob('**/*.py')])
blocked = len([r for r in results if r['blocked']])
warned = len([r for r in results if r['verdict'] == 'warn'])
passed = len([r for r in results if r['verdict'] == 'passed'])
print(f'BLOCKED: {blocked} | WARNED: {warned} | PASSED: {passed}')
"

# 2. Run full test suite
python -m pytest tests/ -v --tb=short

# 3. Push and create PR
git push origin feat/test-fixture-migration
gh pr create --title "refactor: Migrate test files to PANOPTICON+ fixtures" --body "Migrates 33 test files to use TestAgents fixtures instead of custom agent classes."
```

---

## Success Criteria

- [ ] All 33 WARNED files migrated (or documented why excluded)
- [ ] Zero BLOCKED files
- [ ] All tests pass (`pytest tests/`)
- [ ] CI passes on PR

---

## Reference

- Fixtures source: `vibe_core/plugins/test_orchestration/fixtures.py`
- Validation rules: `knowledge/circuits/test_validation.yaml`
- Example migration: `tests/verify_immune_system.py` (done in previous session)
