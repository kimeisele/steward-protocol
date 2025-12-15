# OPUS-081: RUNTIME STATE MANIFEST

**Scope:** GitState unterscheidet SOURCE CODE von RUNTIME STATE
**Philosophy:** Git ist kognitives Logging. Runtime state ist Gedächtnis, nicht Code.

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

GitState bekommt neue Methoden:
- `is_source_dirty()` - nur source code changes
- `is_runtime_dirty()` - nur runtime state changes
- `get_runtime_state_files()` - aus plugin manifests aggregiert

```
┌─────────────────────────────────────────────────────┐
│  STOP HOOK / TOOLS                                  │
│  → git_state.is_source_dirty()                      │
├─────────────────────────────────────────────────────┤
│  GitState (vibe_core/state/git_state.py)            │
│  → get_runtime_state_files() aggregiert manifests   │
├─────────────────────────────────────────────────────┤
│  Plugin Manifests                                   │
│  → "generated_outputs": [...]                       │
└─────────────────────────────────────────────────────┘
```

---

## The Harness

<!-- @HARNESS
files:
  # === PLUGIN MANIFESTS ===
  - path: vibe_core/plugins/interface/manifest.json
    required: true
  - path: vibe_core/plugins/opus_assistant/manifest.json
    required: true

  # === GIT STATE ===
  - path: vibe_core/state/git_state.py
    required: true

wiring:
  # === PHASE 1: Plugin Declarations (DONE) ===
  - pattern: "generated_outputs"
    in: vibe_core/plugins/interface/manifest.json
  - pattern: "generated_outputs"
    in: vibe_core/plugins/opus_assistant/manifest.json

  # === PHASE 2: GitState Aggregation (TODO) ===
  # Uncomment when implemented:
  # - pattern: "def get_runtime_state_files"
  #   in: vibe_core/state/git_state.py
  # - pattern: "def is_source_dirty"
  #   in: vibe_core/state/git_state.py
  # - pattern: "def is_runtime_dirty"
  #   in: vibe_core/state/git_state.py

  # === EXISTING FOUNDATIONS ===
  - pattern: "VISNU_PROTECTED"
    in: vibe_core/state/git_state.py
  - pattern: "def is_dirty"
    in: vibe_core/state/git_state.py
  - pattern: "cognitive logging"
    in: vibe_core/state/git_state.py

tests:
  - tests/state/test_git_state.py

-->

---

## Implementation

### Phase 1: Plugin Manifests ✅ DONE

```json
// vibe_core/plugins/interface/manifest.json
{
  "generated_outputs": {
    "dashboard_files": ["OPUS.md", "ENVOY.md", ...]
  }
}
```

### Phase 2: GitState Extension (TODO)

```python
# vibe_core/state/git_state.py

# Nach VISNU_PROTECTED hinzufügen:
def get_runtime_state_files(self) -> List[str]:
    """Aggregate generated_outputs from all plugin manifests."""
    ...

def is_source_dirty(self) -> bool:
    """Check if SOURCE CODE changed (excludes runtime state)."""
    ...

def is_runtime_dirty(self) -> bool:
    """Check if only RUNTIME STATE changed."""
    ...
```

### Phase 3: Tool Integration (TODO)

Stop hooks und CI nutzen `is_source_dirty()` statt `is_dirty()`.

---

## Fire Commands

```bash
steward verify 081
```

---

*"Git ist kognitives Logging. Runtime state ist Gedächtnis, Source code ist DNA."*
