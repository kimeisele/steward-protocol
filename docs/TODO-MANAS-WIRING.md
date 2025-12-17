# MANAS CONFIG WIRING - REMAINING WORK

**Session:** 2025-12-17
**Status:** PARTIAL - Config infrastructure done, features need wiring
**Priority:** P0 - Critical for MANAS functionality
**Principle:** NO HALF-BAKED SHIT - Complete this properly!

---

## ✅ COMPLETED (This Session)

### 1. Config Loading Infrastructure
- `CognitiveKernel._load_full_config()` - Loads config/manas.yaml
- Stores as `self._full_config` with all 10 sections
- Graceful fallback if file missing

### 2. Sankalpa Config Injection
- `SankalpaOrchestrator.__init__` accepts `config` param
- `cognitive_kernel._init_sankalpa()` passes config section
- Backwards compatible (optional param)

### 3. Config Files Complete
- `config/manas.yaml` - 230 lines with all feature sections
- `config/opus.yaml` - 461 lines with MANAS section
- `.opus_state/sankalpa.json` - Trigger requirements fixed

---

## ❌ REMAINING WORK

### 3. Shiva Config Injection (30 min)

**Files:**
- `vibe_core/plugins/opus_assistant/manas/shiva.py`
- `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

**Changes:**
```python
# shiva.py
def __init__(self, workspace: Path, config: Optional[Dict[str, Any]] = None):
    self._workspace = workspace
    self._config = config or {}
    self._sweep_interval = self._config.get("sweep_interval_minutes", 30)
    # ... use config values

# cognitive_kernel.py
def __init__(self):
    # ...
    shiva_config = self._full_config.get("shiva", {})
    self._shiva = ShivaLifecycleManager(
        workspace=self._workspace,
        config=shiva_config
    )
```

**Config Available:**
```yaml
shiva:
  enabled: true
  sweep_interval_minutes: 30
  fulfillment_checks:
    - "commit_pending_changes: git status --short"
  archive_fulfilled: true
  archive_path: ".opus_state/archived_intents.json"
```

---

### 4. ObservationLogger Config Injection (45 min)

**Files:**
- Find/create `vibe_core/plugins/opus_assistant/manas/cortex/observation_logger.py`
- `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

**Current State:**
```python
# cognitive_kernel.py:262
self._observation_logger = None
self._init_observation_logger()
```

**Action:**
1. Check if ObservationLogger class exists
2. If not, create it based on config requirements
3. Wire config injection similar to Sankalpa

**Config Available:**
```yaml
observation_logger:
  enabled: true
  log_to_opus: true
  log_to_file: true
  log_file: ".opus_state/observations.json"
  log_events:
    - think_cycle_start
    - think_cycle_complete
    - intent_generated
    - intent_auto_executed
    - intent_blocked
    - sensor_perception
  max_observations: 100
  retention_days: 7
```

---

### 5. Sensors Config Injection (1 hour)

**Files:**
- `vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py`
- `vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py`
- `vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py`
- `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

**Pattern:** Same as Sankalpa - add config param, wire in cognitive_kernel

**Config Available:**
```yaml
sutra_sense:
  enabled: true
  scan_interval_minutes: 60
  severity:
    missing_code: "high"
    missing_test: "medium"
  auto_fix_enabled: true

prakriti_sense:
  enabled: true
  scan_interval_minutes: 15
  thresholds:
    git_uncommitted_changes: 10
    test_failure_rate: 0.1
  guna_weights:
    sattva: 1.0
    rajas: 0.5
    tamas: 0.0

dharma_sense:
  enabled: true
  state_file: ".vibe/state/vedic_dharma.json"
  bhakti:
    success_reward: 5
    failure_penalty: -10
  ashrama_rules:
    grihastha: ["code_modify", "git_commit"]
```

---

### 6. @HARNESS Blocks Missing (2 hours)

**Critical Gap:** 16 docs without @HARNESS (80% coverage)

**High Priority Docs:**
- `009-UNIFIED-STATE-PRAKRITI.md` - **0% trust score** (ALL FAILED)
- `054-SUTRA.md` - 35% (files/tests missing)
- `056-SHUDDHI.md` through `060-SATYA.md` - No harness at all

**Template:**
```markdown
<!-- @HARNESS
files:
  - path: vibe_core/path/to/implementation.py
    required: true
tests:
  - tests/unit/test_feature.py
wiring:
  - pattern: "from.*import Feature"
    in: vibe_core/kernel_impl.py
  - pattern: "class Feature"
    in: vibe_core/path/to/implementation.py
absent:
  - pattern: "TODO.*implement"
    in: vibe_core/path/to/implementation.py
  - pattern: "raise NotImplementedError"
    in: vibe_core/path/to/implementation.py
config:
  - section: manas.feature_name
-->
```

**Action:** For each doc:
1. Read the doc to understand what it claims
2. Grep for file paths mentioned
3. Verify files exist and have real implementations
4. Add @HARNESS with verified paths
5. Run verification to confirm trust score improves

---

### 7. Heartbeat Auto-Push Broken (30 min)

**Problem:**
- Local OPUS.md: 2025-12-17 14:45 UTC
- GitHub main: 2025-12-17 12:44 UTC
- **3 hour drift!**

**Root Cause:**
- `.github/workflows/heartbeat.yml` exists (cron */15 min)
- But workflow not running OR not pushing

**Debug Steps:**
```bash
# Check GitHub Actions status
gh workflow list
gh run list --workflow=heartbeat.yml --limit 10

# Check if workflow file valid
cat .github/workflows/heartbeat.yml

# Try manual run
python scripts/heartbeat.py
git status  # Did it create commits?
git push    # Does push work?
```

**Likely Fixes:**
1. GitHub Actions permissions issue
2. Workflow disabled
3. Cron not triggering
4. Git push failing (credentials?)

**Fallback:** Add local cron
```bash
crontab -e
# Add:
*/15 * * * * cd /home/user/steward-protocol && python scripts/heartbeat.py && git push
```

---

### 8. Tests for Config Loading (1 hour)

**Create:**
- `tests/unit/plugins/opus_assistant/manas/test_config_loading.py`

**Test Cases:**
```python
def test_load_full_config():
    """Config loader reads all sections from manas.yaml"""
    kernel = CognitiveKernel()
    assert "sankalpa" in kernel._full_config
    assert "shiva" in kernel._full_config
    assert len(kernel._full_config) == 10

def test_sankalpa_config_injection():
    """Sankalpa receives config from kernel"""
    kernel = CognitiveKernel()
    assert kernel._sankalpa._config is not None
    assert "enabled" in kernel._sankalpa._config

def test_config_fallback_graceful():
    """Kernel works even if manas.yaml missing"""
    # Temporarily rename config file
    # Init kernel
    # Verify it uses defaults
    pass

def test_backwards_compatibility():
    """Old code without config param still works"""
    orch = SankalpaOrchestrator(workspace=Path.cwd())
    assert orch._config == {}
```

---

### 9. End-to-End Verification (30 min)

**Checklist:**
```bash
# 1. Boot kernel
python -m vibe_core.cli boot --mode full_power

# 2. Verify config loaded
# Check logs for:
# "🔌 Loaded full config with 10 sections"
# "🌙 SANKALPA: Strategic Will initialized (config: X keys)"

# 3. Trigger MANAS think cycle
# Should use configured intervals (15 min not 60 min)

# 4. Check intent generation
# Should include Sankalpa strategic intents

# 5. Verify Heartbeat
# OPUS.md should update every 15 min
# Should auto-push to GitHub

# 6. Check @HARNESS coverage
# Run verification, trust score should be >85%
```

---

## 🎯 CRITICAL PATH (Order of Execution)

**Priority 1 (Core Functionality):**
1. Shiva config injection (30 min)
2. ObservationLogger config injection (45 min)
3. Sensors config injection (1 hour)

**Priority 2 (Verification):**
4. Tests for config loading (1 hour)
5. End-to-end verification (30 min)

**Priority 3 (Documentation):**
6. @HARNESS blocks (2 hours)
7. Heartbeat fix (30 min)

**Total Estimated Time:** ~6 hours

---

## 🔥 GUIDING PRINCIPLES

1. **NO HALF-BAKED SHIT**
   - Every feature must be fully wired, not just "partially working"
   - Config must flow end-to-end
   - Tests must exist

2. **CODE WITHOUT TESTS = DEAD MATTER**
   - Every config loading path needs a test
   - Every feature injection needs a test
   - No "I'll add tests later"

3. **DOCS WITHOUT @HARNESS = JUST WORDS**
   - Every OPUS doc must have @HARNESS
   - Every @HARNESS must verify actual files
   - Trust scores must be >85%

4. **CONFIG DYNAMIC NOT HARDCODED**
   - Features load from config/manas.yaml
   - Phoenix loads from structured sections
   - No magic numbers in code

5. **NOTHING LEFT HALF-DONE**
   - Finish what you start
   - Document what's remaining clearly
   - Next session picks up seamlessly

---

## 📚 REFERENCES

- **Config File:** `config/manas.yaml` (230 lines, 10 sections)
- **Phoenix Section:** `vibe_core/phoenix/sections/manas/section_main.py`
- **Cognitive Kernel:** `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`
- **Feature Modules:** `vibe_core/plugins/opus_assistant/manas/cortex/`
- **Verification:** OPUS.md verification section (trust scores)

---

## 💾 SESSION CONTEXT (Resume Here)

**What Was Done:**
- Config infrastructure built ✅
- Sankalpa wired ✅
- Remaining features identified

**What's Next:**
- Continue with Shiva (line 254 in cognitive_kernel.py)
- Then ObservationLogger (line 262)
- Then sensors (lines 247, 251, 247)

**Key Insight:**
All components exist, almost everything is declared, but **KABEL FEHLEN** (cables missing). This is pure wiring work - systematic but straightforward.

**Commit History:**
```
b9069d7 feat(manas): Wire config loading - Sankalpa integrated (OPUS-092)
340a800 fix(config): Complete manas.yaml with all OPUS-089/088/054/009 features
5226484 fix(manas): Complete config integration - all OPUS-089/088 features
```

---

**END OF TODO**

Next developer: Pick up at "3. Shiva Config Injection" and work through systematically.
Remember: This is about MANAS being the cognitive core. Get it right!
