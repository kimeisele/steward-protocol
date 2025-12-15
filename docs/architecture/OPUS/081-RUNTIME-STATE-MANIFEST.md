# OPUS-081: RUNTIME STATE MANIFEST

**Scope:** GitState unterscheidet SOURCE CODE von RUNTIME STATE
**Status:** ✅ IMPLEMENTED

---

## Das Problem

```
KERNEL TICK → renders OPUS.md
STOP HOOK → is_dirty() = true → blocks exit
INFINITE LOOP
```

**Root Cause:** `GitState.is_dirty()` unterscheidet nicht zwischen:
- **SOURCE CODE** (menschlich geschrieben, muss committed werden)
- **RUNTIME STATE** (kernel-generiert, ändert sich ständig)

---

## Die Lösung

```
┌─────────────────────────────────────────────────────┐
│  scripts/git_gatekeeper.py                          │
│  → Exit 0 if clean, Exit 1 if source dirty          │
├─────────────────────────────────────────────────────┤
│  GitState.is_source_dirty()                         │
│  → Excludes runtime state from dirty check          │
├─────────────────────────────────────────────────────┤
│  GitState._get_runtime_state_patterns()             │
│  → Scans plugin manifests for generated_outputs     │
├─────────────────────────────────────────────────────┤
│  Plugin Manifests                                   │
│  → "generated_outputs": { "files": [...] }          │
└─────────────────────────────────────────────────────┘
```

---

## The Harness

<!-- @HARNESS
files:
  - path: vibe_core/plugins/interface/manifest.json
    required: true
  - path: vibe_core/plugins/opus_assistant/manifest.json
    required: true
  - path: vibe_core/state/git_state.py
    required: true
  - path: scripts/git_gatekeeper.py
    required: true

wiring:
  # === PHASE 1: Plugin Declarations ===
  - pattern: "generated_outputs"
    in: vibe_core/plugins/interface/manifest.json
  - pattern: "generated_outputs"
    in: vibe_core/plugins/opus_assistant/manifest.json

  # === PHASE 2: GitState Aggregation ===
  - pattern: "_get_runtime_state_patterns"
    in: vibe_core/state/git_state.py
  - pattern: "def is_source_dirty"
    in: vibe_core/state/git_state.py
  - pattern: "get_dirty_source_files"
    in: vibe_core/state/git_state.py

  # === PHASE 3: Gatekeeper ===
  - pattern: "is_source_dirty"
    in: scripts/git_gatekeeper.py
  - pattern: "get_dirty_source_files"
    in: scripts/git_gatekeeper.py

  # === FOUNDATIONS ===
  - pattern: "VISNU_PROTECTED"
    in: vibe_core/state/git_state.py
  - pattern: "cognitive logging"
    in: vibe_core/state/git_state.py

tests:
  - tests/state/test_git_state.py

-->

---

## Usage

```bash
# Test gatekeeper directly
python scripts/git_gatekeeper.py

# Stop hook delegation (in ~/.claude/stop-hook-git-check.sh)
GATEKEEPER="$REPO_ROOT/scripts/git_gatekeeper.py"
if [[ -f "$GATEKEEPER" ]]; then
    python3 "$GATEKEEPER"
    exit $?
fi
```

---

*"Git ist kognitives Logging. Runtime state ist Gedächtnis, Source code ist DNA."*
