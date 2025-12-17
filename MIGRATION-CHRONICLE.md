# 🗡️ CHRONICLE MIGRATION ROADMAP

**Status:** Planning
**Goal:** Eliminate split-brain - keep only Cartridge, remove Plugin

---

## 🎯 Current State (SPLIT BRAIN)

### Plugin (`vibe_core/plugins/system_chronicle/`)
```python
# What it does:
- Hooks into PranaOrchestrator via on_pulse() method
- Runs during CLEANUP phase automatically
- Imports GitTools from Cartridge and calls seal_history()
- **HARDCODED sign=True** (line 84) ← THE PROBLEM!

# Files:
- plugin_main.py (thin wrapper)
- manifest.json
- tests/
```

### Cartridge (`vibe_core/cartridges/system/chronicle/`)
```python
# What it does:
- Full VibeAgent implementation
- GitTools with complete Git operations
- **Already supports configurable sign parameter!**
- Task-based execution (more modern)

# Files:
- cartridge_main.py (VibeAgent)
- tools/git_tools.py (the REAL implementation)
- cartridge.yaml
- STEWARD.md
```

**DIAGNOSIS:** Plugin is a 100-line wrapper that adds NO VALUE except auto-pulse hookup.

---

## 🚀 Migration Steps

### Step 1: Analyze Dependencies ✅
**Who uses Plugin?**
- `PranaOrchestrator` (discovers via `kernel.get_plugins()`)
- Heartbeat (via PranaOrchestrator.pulse())
- **THAT'S IT!** Only these two places.

**What does Plugin do that Cartridge doesn't?**
- Auto-registration in pulse cycle ← This we need to preserve
- Nothing else!

### Step 2: Add GPG Config to prana.yaml
```yaml
# config/prana.yaml
chronicle:
  # GPG signing for automatic commits
  gpg_sign_commits: true  # Set to true for production, false for dev/testing

  # Commit message prefix for heartbeat
  commit_prefix: "🫀 Heartbeat Pulse:"
```

### Step 3: Modify Heartbeat to Use GitTools Directly
Instead of relying on Plugin discovery, heartbeat calls GitTools directly:

```python
# scripts/heartbeat.py
from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools

# After PRANA pulse
if config.get("chronicle", {}).get("enabled", True):
    tools = GitTools()
    status = tools.get_status()

    if status.get("dirty"):
        sign = config.get("chronicle", {}).get("gpg_sign_commits", True)
        tools.seal_history(
            message="🫀 Heartbeat Pulse: System auto-save",
            sign=sign
        )
```

### Step 4: Remove Plugin from PranaOrchestrator Discovery
**Option A:** Plugin stays registered but becomes no-op
**Option B:** Remove plugin registration entirely

We go with **Option B** (clean cut).

### Step 5: Delete Plugin Directory
```bash
rm -rf vibe_core/plugins/system_chronicle/
```

Update ARCHITECTURE.md to remove references.

### Step 6: Fix MANAS Config Wiring (Bonus)
While we're here, fix the REAL problem:

```python
# vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py:565
prakriti_config = self._full_config.get("prakriti_sense", {})
self._prakriti_sense = PrakritiSense(
    workspace=self._workspace,
    config=prakriti_config  # ← ADD THIS!
)

# Line 663 for DharmaSense
dharma_config = self._full_config.get("dharma_sense", {})
self._dharma_sense = DharmaSense(
    workspace=self._workspace,
    agent_id="manas",
    config=dharma_config  # ← ADD THIS!
)
```

---

## 🎯 Success Criteria

1. ✅ Heartbeat creates commits via Cartridge GitTools
2. ✅ GPG signing is configurable (no hardcode)
3. ✅ Plugin directory deleted
4. ✅ No references to `system_chronicle` plugin
5. ✅ Prakriti/Dharma load config (show non-zero keys)
6. ✅ End-to-end test passes

---

## 🛡️ Risks & Mitigation

**Risk:** Breaking heartbeat commits
**Mitigation:** Test in dev first, commit message stays the same

**Risk:** Plugin used elsewhere
**Mitigation:** Already checked - only PranaOrchestrator uses it

**Risk:** Config not loaded
**Mitigation:** Test config loading before deletion

---

## 📋 Execution Order

```
1. ✅ Create this roadmap
2. 🔄 Add config to prana.yaml (GPG signing)
3. 🔄 Fix MANAS config wiring (Prakriti/Dharma)
4. 🔄 Modify heartbeat to use GitTools directly
5. 🔄 Test heartbeat creates commit
6. 🔄 Delete Plugin directory
7. 🔄 Test MANAS shows config loaded
8. ✅ Pull the plug (commit & push)
```

---

## 💡 Why This Works

1. **Cartridge has everything Plugin has** (and more)
2. **Plugin was just a wrapper** (thin delegation layer)
3. **Direct call is simpler** (fewer layers = fewer bugs)
4. **Config already in Cartridge** (sign parameter exists!)
5. **No functionality lost** (everything preserved)

**Philosophy:** "Delete code that doesn't add value."

---

## 🔗 Related Issues

- OPUS-092: Config wiring technical debt
- OPUS-091: Heartbeat purification
- Split-brain chronicle condition (this document)

---

## ✅ Ready to Execute

All analysis complete. No blockers. Let's go! 🚀
