# 🫀 KERNEL PULSE - POST-BUILD STATE SYNC

**Problem:** Builder Agent modifies code while Kernel is offline → snapshot becomes stale.

**Solution:** Pulse script keeps Kernel heartbeat synchronized with git repo.

---

## Quick Start

After making code changes:

```bash
python3 scripts/pulse.py
```

This:
1. ✅ Boots RealVibeKernel
2. ✅ Executes one `_pulse()` tick
3. ✅ Updates `vibe_snapshot.json` (live system state)
4. ✅ Updates `OPERATIONS.md` (operational status)
5. ✅ Ensures git repo state = live kernel state

---

## What Gets Updated

### vibe_snapshot.json
- Live kernel state captured
- Agent registry snapshot
- Current heartbeat count
- Ledger statistics

### OPERATIONS.md
- Current timestamp
- Agent count
- Ledger entries
- Operational status

---

## Integration Points

### For Builder Agent

After every code modification:
```python
import subprocess
subprocess.run(["python3", "scripts/pulse.py"], check=True)
```

### For Git Workflow

Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
python3 scripts/pulse.py
```

This automatically updates artifacts after every commit.

### For CI/CD

Before pushing to origin:
```bash
python3 scripts/pulse.py  # Ensure repo state is fresh
git add OPERATIONS.md
git commit --amend --no-edit
```

---

## The Philosophy

**Before Pulse:**
```
Builder writes code → Kernel offline → Snapshot stale → Next Builder sees lies
```

**After Pulse:**
```
Builder writes code → Builder runs pulse → Kernel ticks once → Snapshot fresh → Truth preserved
```

This ensures the repo is always the **single source of truth** about system state.

---

## Advanced Usage

### Manual Snapshot

```bash
python3 scripts/pulse.py
# Outputs: Kernel state, updated files, status report
```

### What Happens Inside

1. **Kernel Initialization**
   ```
   💾 SQLite ledger initialized at data/vibe_ledger.db
   🚀 Vibe Kernel initialized (persistent ledger)
   ```

2. **Single Pulse Tick**
   ```
   💓 Pulse written: vibe_snapshot.json
   📋 Operations dashboard rendered
   ```

3. **State Captured**
   ```
   ✅ Snapshot loaded
   📝 OPERATIONS.md updated
   ✅ PULSE COMPLETE
   ```

---

## Failure Handling

If kernel fails to pulse:
- Pulse script will exit with error code 1
- Git artifacts remain unchanged
- No stale data is committed

This is intentional: it's safer to fail than to capture invalid state.

---

## References

- **Implementation:** `scripts/pulse.py`
- **Invoked by:** Builder Agent after code changes
- **Updates:** `vibe_snapshot.json`, `OPERATIONS.md`
- **Philosophy:** Kernel Transcendence (always-on state awareness)

---

**Status:** ✅ Operational

The heart beats. The repo breathes. Truth persists. 🫀
