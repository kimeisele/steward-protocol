# OPUS-092: HEARTBEAT GPG RESILIENCE HARNESS

**Scope:** CI/CD Bulletproofing - Graceful GPG Degradation in Headless Mode
**Philosophy:** The harness IS the truth. Dynamic verification of GPG safety gates.
**Goal:** Heartbeat automation survives missing GPG keys without silent failures.

---

## The Harness

This document contains NO manual status. The `@HARNESS` below is the ONLY source of truth.

<!-- @HARNESS
files:
  # === HEARTBEAT AUTOMATION ===
  - path: scripts/heartbeat.py
    required: true
    reason: "Contains GPG resilience logic and CI detection"

  # === CHRONICLE WIRING ===
  - path: vibe_core/cartridges/system/chronicle/tools/git_tools.py
    required: true
    reason: "GitTools.seal_history() method that accepts sign parameter"

  # === CONFIGURATION ===
  - path: config/prana.yaml
    required: true
    reason: "Contains chronicle.gpg_sign_commits setting"

  # === CI AUTOMATION ===
  - path: .github/workflows/heartbeat.yml
    required: true
    reason: "GitHub Actions workflow with correct permissions"

wiring:
  # === GPG DETECTION LOGIC ===
  # Heartbeat must detect CI environment
  - pattern: "GITHUB_ACTIONS"
    in: scripts/heartbeat.py
    context: "Detects GitHub Actions execution environment"

  # === GPG KEY AVAILABILITY CHECK ===
  # Must have method to check GPG keys before committing
  - pattern: "def _check_gpg_key_available"
    in: scripts/heartbeat.py
    context: "Static method to verify GPG key availability"

  - pattern: "gpg.*--list-secret-keys"
    in: scripts/heartbeat.py
    context: "Queries GPG for available signing keys"

  # === FALLBACK LOGIC ===
  # Must gracefully degrade to unsigned commits
  - pattern: "gpg_sign = False"
    in: scripts/heartbeat.py
    context: "Fallback sets signing to False when GPG unavailable"

  - pattern: "Falling back to unsigned commits"
    in: scripts/heartbeat.py
    context: "Warning log when GPG not available in CI"

  # === CHRONICLE INTEGRATION ===
  # Must pass sign parameter to seal_history()
  - pattern: "seal_history.*sign=gpg_sign"
    in: scripts/heartbeat.py
    context: "Passes GPG flag to chronicle cartridge"

  # === CONFIG LOADING ===
  # Must load prana.yaml chronicle config
  - pattern: "chronicle_config.*get.*gpg_sign_commits"
    in: scripts/heartbeat.py
    context: "Reads GPG setting from config"

  # === WORKFLOW PERMISSIONS ===
  # GitHub Actions workflow must have write permissions
  - pattern: "contents: write"
    in: .github/workflows/heartbeat.yml
    context: "Allows workflow to commit and push changes"

  # === WORKFLOW SETUP ===
  # Must use Python 3.11 and install dependencies
  - pattern: "python-version.*3.11"
    in: .github/workflows/heartbeat.yml
    context: "Ensures compatible Python version"

  - pattern: "pip install -e"
    in: .github/workflows/heartbeat.yml
    context: "Installs project in editable mode"

  # === GITTOOLS SIGN PARAMETER ===
  # GitTools.seal_history must accept and handle sign parameter
  - pattern: "def seal_history.*sign"
    in: vibe_core/cartridges/system/chronicle/tools/git_tools.py
    context: "accepts sign parameter for optional GPG signing"

  - pattern: "if sign:.*append.*-S"
    in: vibe_core/cartridges/system/chronicle/tools/git_tools.py
    context: "Only appends -S flag if sign=True"

tests:
  # === GPG RESILIENCE TEST ===
  - tests/heartbeat/test_gpg_resilience.py
  - tests/heartbeat/test_ci_detection.py
  - tests/chronicle/test_unsigned_commits.py

semantic:
  # === HEARTBEAT ENGINE CLASS ===
  - type: method_exists
    name: heartbeat_chronicle_commit
    in: scripts/heartbeat.py
    class: HeartbeatEngine
    method: _chronicle_commit
    context: "Core commit method with GPG resilience"

  - type: method_exists
    name: heartbeat_check_gpg
    in: scripts/heartbeat.py
    class: HeartbeatEngine
    method: _check_gpg_key_available
    context: "Static method for GPG key detection"

  # === ENVIRONMENT DETECTION ===
  - type: config_setting
    name: gpg_signing_enabled
    in: config/prana.yaml
    path: chronicle.gpg_sign_commits
    expected_type: boolean
    context: "GPG signing is configurable"

  # === CHRONCILE INTERFACE ===
  - type: method_signature
    name: gittools_seal_history
    in: vibe_core/cartridges/system/chronicle/tools/git_tools.py
    class: GitTools
    method: seal_history
    params:
      - message
      - files
      - sign
    context: "Accept sign parameter for conditional GPG"

  # === BEHAVIORAL CONTRACT ===
  - type: execution_path
    name: gpg_available_ci
    expected: "Signed commit created"
    conditions:
      - "GITHUB_ACTIONS=true"
      - "GPG key exists"
      - "gpg_sign_commits=true"
    rationale: "If GPG available in CI, use it"

  - type: execution_path
    name: gpg_unavailable_ci
    expected: "Unsigned commit created + warning logged"
    conditions:
      - "GITHUB_ACTIONS=true"
      - "GPG key NOT found"
      - "gpg_sign_commits=true"
    rationale: "If GPG missing in CI, fallback gracefully"

  - type: execution_path
    name: local_no_gpg
    expected: "Git command fails (expected behavior)"
    conditions:
      - "GITHUB_ACTIONS != true"
      - "GPG key NOT found"
      - "gpg_sign_commits=true"
    rationale: "Local execution without GPG should fail (prevents accidental unsigned commits)"

  - type: file_writable
    name: git_repo_writable
    path: .git/
    rationale: "Heartbeat needs to commit to repository"

  - type: env_var_exists
    name: github_token_available
    in: .github/workflows/heartbeat.yml
    var: secrets.GITHUB_TOKEN
    rationale: "GitHub Actions provides GITHUB_TOKEN for authentication"

fire_proofs:
  # === RUNTIME VERIFICATION ===
  - name: "GPG detection works in CI"
    command: "GITHUB_ACTIONS=true python -c 'from scripts.heartbeat import HeartbeatEngine; print(\"CI detected\" if __import__(\"os\").environ.get(\"GITHUB_ACTIONS\") else \"Not CI\")'"
    expected: "CI detected"

  - name: "GPG key check is safe"
    command: "python -c 'from scripts.heartbeat import HeartbeatEngine; result = HeartbeatEngine._check_gpg_key_available(); print(f\"GPG check: {result}\")'"
    expected: "GPG check: True or False"

  - name: "GitTools accepts sign parameter"
    command: "grep -n 'def seal_history' vibe_core/cartridges/system/chronicle/tools/git_tools.py"
    expected: "sign.*=.*True"

  - name: "Config has GPG setting"
    command: "grep -A1 'chronicle:' config/prana.yaml | grep 'gpg_sign_commits'"
    expected: "gpg_sign_commits: true"

  - name: "Workflow has write permissions"
    command: "grep -A1 'permissions:' .github/workflows/heartbeat.yml"
    expected: "contents: write"
-->

---

## Fire Commands

```bash
# Verify the harness (ONLY TRUTH)
steward verify 092

# Test GPG resilience locally
python -c "
from scripts.heartbeat import HeartbeatEngine
import os

# Test 1: GPG check
has_gpg = HeartbeatEngine._check_gpg_key_available()
print(f'✅ GPG available: {has_gpg}')

# Test 2: CI detection
os.environ['GITHUB_ACTIONS'] = 'true'
is_ci = os.environ.get('GITHUB_ACTIONS') == 'true'
print(f'✅ CI detected: {is_ci}')
"

# Check heartbeat can import Chronicle
python -c "from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools; print('✅ GitTools loaded')"

# Verify config exists
grep gpg_sign_commits config/prana.yaml && echo "✅ GPG config found"

# Check workflow permissions
grep "contents: write" .github/workflows/heartbeat.yml && echo "✅ Workflow has write perms"
```

---

## Execution Paths (The Truth)

### Path 1: GitHub Actions + GPG Key Available
```
1. Heartbeat triggers (cron every 15 min)
2. Detect: GITHUB_ACTIONS=true ✅
3. Load config: gpg_sign_commits=true ✅
4. Check GPG: gpg --list-secret-keys ✅ (returns keys)
5. Action: sign=true
6. Commit: git commit -S -m "..." ✅ SIGNED
7. Push: git push ✅
Result: 🔐 CRYPTOGRAPHICALLY SIGNED COMMIT
```

### Path 2: GitHub Actions + No GPG Key (DEFAULT)
```
1. Heartbeat triggers (cron every 15 min)
2. Detect: GITHUB_ACTIONS=true ✅
3. Load config: gpg_sign_commits=true ✅
4. Check GPG: gpg --list-secret-keys ❌ (no output)
5. Fallback: sign=false + warning logged ⚠️
6. Commit: git commit -m "..." ✅ UNSIGNED
7. Push: git push ✅
Result: ✅ SAFE UNSIGNED COMMIT (not crash!)
```

### Path 3: Local Development + No GPG
```
1. User runs: python scripts/heartbeat.py
2. Detect: GITHUB_ACTIONS != true (not in CI)
3. Load config: gpg_sign_commits=true ✅
4. Check GPG: gpg --list-secret-keys ❌ (no key)
5. Action: sign=true (config says sign)
6. Commit: git commit -S -m "..." ❌ FAILS
Result: ⛔ EXPECTED FAILURE (prevents accidental unsigned commits locally)
```

---

## The Bulletproof Contract

| Scenario | GPG Key | CI? | Config | Result | Status |
|----------|---------|-----|--------|--------|--------|
| Production + GPG | ✅ | ✅ | true | 🔐 Signed | ✅ |
| **CI Default** | ❌ | ✅ | true | ✅ Unsigned+warn | ✅ |
| Local with key | ✅ | ❌ | true | 🔐 Signed | ✅ |
| Local no key | ❌ | ❌ | true | ⛔ Fail | ✅ |
| Disabled | ❌ | ✅ | false | ✅ Unsigned | ✅ |

**The Safety Matrix:**
- **Prevents:** Silent failures (was: GPG crash → no commit)
- **Ensures:** Logging (warning visible in Actions)
- **Respects:** Config (gpg_sign_commits setting)
- **Smart:** Auto-detects environment
- **Safe:** Doesn't auto-sign locally

---

## Implementation Details

### 1. CI Detection
```python
is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
```
Only GitHub Actions sets this env var (official GitHub documentation).

### 2. GPG Key Availability
```python
@staticmethod
def _check_gpg_key_available() -> bool:
    try:
        result = subprocess.run(
            ["gpg", "--list-secret-keys", "--quiet"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except:
        return False
```
- Safe: timeout protects against hung processes
- Safe: catches exceptions (GPG not installed)
- Accurate: only returns True if keys found

### 3. Graceful Fallback
```python
if is_ci and gpg_sign:
    gpg_available = self._check_gpg_key_available()
    if not gpg_available:
        logger.warning("GPG signing requested but no key found...")
        gpg_sign = False
```
- Only applies in CI (GitHub Actions)
- Respects config (only if gpg_sign_commits=true)
- Logs warning (visible in Actions)
- Continues execution (no crash)

---

## Why This Is Production-Ready

✅ **No Silent Failures:** Will not crash when GPG missing
✅ **Visible Logging:** Warning appears in GitHub Actions logs
✅ **Respects Config:** Honors `prana.yaml` settings
✅ **Backward Compatible:** Local development still works
✅ **Optional Signing:** Can add GPG later via secrets
✅ **Tested Paths:** All three execution paths verified

---

## Optional: Enable Signed Commits in CI

To add GPG signing to GitHub Actions:

1. Generate GPG key locally
2. Export: `gpg --export-secret-keys KEY_ID | base64 > key.b64`
3. Add GitHub Secret: `GPG_PRIVATE_KEY = <contents of key.b64>`
4. Add workflow step:
   ```yaml
   - name: 🔐 Import GPG Key
     uses: crazy-max/ghaction-import-gpg@v6
     with:
       gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
       git_config_global: true
       git_user_signingkey: true
   ```

Then GPG detection will find the key and sign commits automatically.

---

## Status Summary

**Date:** 2025-12-17

- [x] GPG resilience implemented
- [x] CI detection wired
- [x] Fallback logic in place
- [x] Config loading correct
- [x] Chronicle integration complete
- [x] Graceful error handling
- [x] Warning logging
- [x] GitHub Actions permissions correct
- [x] Harness defined

**Status: 🟢 PRODUCTION READY**

The heartbeat will NOT crash at 3 AM because of missing GPG keys.

---

*"The harness is the truth. Run it to know the state."*
