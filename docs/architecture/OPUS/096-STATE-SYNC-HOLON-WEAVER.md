# OPUS-096: State Sync Holon Weaver - Unified State Orchestration

> **Status**: DRAFT - Awaiting Review
> **Created**: 2025-12-18
> **Related**: OPUS-009 (Prakriti Foundation), OPUS-027 (Implementation), OPUS-089 (MANAS Oracle)
> **Purpose**: Unified orchestration of ALL state synchronization across the holographic OS
> **Philosophy**: "The Weaver doesn't replace the threads - it connects them into fabric"

---

## Executive Summary

The steward-protocol currently has **multiple independent state-commit mechanisms**:

1. **StateSyncHolon** (`sync_holon.py`) - Plugin state discovery & healing
2. **GitTools.seal_history()** - Chronicle cartridge commits
3. **Prakriti.commit_if_dirty()** - Core state engine commits
4. **Heartbeat._chronicle_commit()** - Scheduled runtime state commits
5. **ManasOracle** - Cognitive layer wisdom interface

These mechanisms are **not orchestrated**. Each commits independently, causing:
- Pre-commit hook conflicts on state files
- Duplicated state in multiple locations
- Spaghetti coupling between layers

**This document proposes the State Sync Holon Weaver** - a meta-orchestration layer that:
- Unifies ALL state commit paths
- Provides a single source of truth for "what is runtime state?"
- Enables MANAS to weave cognitive insights into state decisions
- Maintains clean separation between VIBE OS (Mutterschiff) and Plugins

---

## Architecture Layers (Separation of Concerns)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VIBE OS - MUTTERSCHIFF LAYER                         │
│                    (kernel_impl.py + state/)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  STATE SYNC HOLON WEAVER (NEW - vibe_core/state/weaver.py)      │   │
│  │  ══════════════════════════════════════════════════════════════  │   │
│  │                                                                  │   │
│  │  INPUTS:                           OUTPUTS:                      │   │
│  │  ├─ StateSyncHolon.discover()     ├─ Unified commit decisions   │   │
│  │  ├─ PluginStateContract paths     ├─ State health reports       │   │
│  │  ├─ Heartbeat triggers            ├─ Guna classifications       │   │
│  │  └─ ManasOracle.consult()         └─ Healing actions            │   │
│  │                                                                  │   │
│  │  CORE RESPONSIBILITIES:                                         │   │
│  │  1. AGGREGATE: Collect state from all sources                   │   │
│  │  2. CLASSIFY: Determine Guna (Sattva/Rajas/Tamas)              │   │
│  │  3. DECIDE: Should this state be committed? When? How?          │   │
│  │  4. CONSULT: Ask MANAS Oracle for cognitive weaving             │   │
│  │  5. EXECUTE: Unified commit via Prakriti (no_verify for state)  │   │
│  │  6. LEARN: Feed results back to MANAS for pattern learning      │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                               │                                         │
│                               │ PluginStateContract                     │
│                               ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  PLUGIN LAYER (opus_assistant, task_manager, etc.)              │   │
│  │                                                                  │   │
│  │  Each plugin implements:                                        │   │
│  │  ├─ get_state_paths() → List[Path]                             │   │
│  │  ├─ snapshot_state() → Dict                                     │   │
│  │  └─ restore_state(Dict) → None                                  │   │
│  │                                                                  │   │
│  │  MANAS-SPECIFIC (opus_assistant):                               │   │
│  │  ├─ ManasOracle.consult() → AnalysisResult                     │   │
│  │  ├─ ManasOracle.pre_analysis() → Gate decision                 │   │
│  │  └─ ManasOracle.post_analysis() → Learning                     │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Weaving Protocol

### Phase 1: Discovery (What exists?)

```python
class StateSyncWeaver:
    def discover_all_state(self) -> WeaverStateMap:
        """
        Unified discovery across all sources.

        Returns:
            WeaverStateMap with:
            - plugin_states: Dict[str, List[StatePathInfo]]
            - runtime_files: List[str] from manifests
            - session_state: Current session context
            - cognitive_state: MANAS observations
        """
```

### Phase 2: Classification (What is it?)

```python
    def classify_state(self, state_map: WeaverStateMap) -> ClassifiedState:
        """
        Classify all state by:
        - Layer: VIBE (kernel) vs PLUGIN (opus_assistant etc.)
        - Guna: Sattva (clean) / Rajas (dirty) / Tamas (dead)
        - Sensitivity: PUBLIC / PRIVATE / CONFIDENTIAL
        - Volatility: EPHEMERAL / PERSISTENT / IMMUTABLE
        """
```

### Phase 3: Consultation (What does MANAS think?)

```python
    def consult_manas(self, classified: ClassifiedState) -> WeavingAdvice:
        """
        Ask MANAS Oracle for cognitive weaving.

        MANAS can:
        - Prioritize which state to commit first
        - Identify patterns (e.g., "this state always conflicts")
        - Suggest healing strategies
        - Learn from past commit outcomes
        """
```

### Phase 4: Decision (What to do?)

```python
    def decide_commit_strategy(
        self,
        classified: ClassifiedState,
        advice: WeavingAdvice
    ) -> CommitPlan:
        """
        Decide the commit strategy:
        - IMMEDIATE: Commit now (session boundary)
        - DEFERRED: Queue for heartbeat
        - BATCHED: Combine with other commits
        - SKIP: No action needed

        Also decides:
        - no_verify: True for runtime state
        - sign: GPG signing for audit trail
        - message: Semantic commit message
        """
```

### Phase 5: Execution (Do it!)

```python
    def execute_commit(self, plan: CommitPlan) -> CommitResult:
        """
        Execute via Prakriti.commit_if_dirty().

        - Uses no_verify for runtime state
        - Respects VISNU protection
        - Records to Ledger (VAJRA binding)
        """
```

### Phase 6: Learning (Improve!)

```python
    def post_commit_learning(self, result: CommitResult) -> None:
        """
        Feed back to MANAS via Oracle.post_analysis().

        MANAS learns:
        - Which state patterns succeed/fail
        - Optimal batching strategies
        - Conflict resolution patterns
        """
```

---

## Integration Points

### 1. Heartbeat Integration

**BEFORE** (spaghetti):
```python
# heartbeat.py
runtime_files = git_state.get_dirty_runtime_files()
tools.seal_history(message=..., files=runtime_files, no_verify=True)
```

**AFTER** (woven):
```python
# heartbeat.py
weaver = get_state_sync_weaver()
result = weaver.pulse()  # Unified commit orchestration
```

### 2. Session Boundary Integration

**BEFORE** (scattered):
```python
# prakriti.py
self.sync_holon.on_shutdown()
self.commit_if_dirty(...)
```

**AFTER** (woven):
```python
# prakriti.py
weaver = get_state_sync_weaver()
result = weaver.on_session_end()  # Handles everything
```

### 3. MANAS Cognitive Integration

**BEFORE** (disconnected):
```python
# MANAS generates intents, but doesn't know about state sync
# StateSyncHolon heals state, but doesn't consult MANAS
```

**AFTER** (woven):
```python
# MANAS participates in state decisions
advice = weaver.consult_manas(classified_state)
# Weaver uses MANAS insights for commit strategy
# Results feed back to MANAS for learning
```

---

## Runtime State Definition (Single Source of Truth)

```python
@dataclass
class RuntimeStateDefinition:
    """
    Canonical definition of what constitutes "runtime state".

    This replaces:
    - manifest.json generated_outputs
    - git_state._get_runtime_state_patterns()
    - heartbeat.runtime_files
    - sync_holon conventions

    ONE SOURCE OF TRUTH.
    """

    # Core patterns (always runtime state)
    CORE_PATTERNS: ClassVar[List[str]] = [
        ".prakriti/",
        ".opus_state/",
        "*.vibe",
        "vibe_snapshot.json",
    ]

    # Plugin-declared patterns (via PluginStateContract)
    plugin_patterns: Dict[str, List[str]] = field(default_factory=dict)

    # Generated file patterns (from manifests)
    generated_patterns: List[str] = field(default_factory=list)

    def is_runtime_state(self, path: Path) -> bool:
        """Is this path runtime state (not source code)?"""
        ...
```

---

## Open Questions (For Discussion)

1. **Where does the Weaver live?**
   - Option A: `vibe_core/state/weaver.py` (Mutterschiff layer)
   - Option B: Extend `sync_holon.py` into the Weaver
   - Option C: New module `vibe_core/weaving/` for all weavers

2. **How does MANAS weave its own state?**
   - MANAS is a plugin that produces state (.opus_state/)
   - MANAS is also consulted by the Weaver
   - Circular dependency? Or fractal elegance?

3. **Heartbeat vs Weaver relationship?**
   - Option A: Heartbeat calls Weaver.pulse()
   - Option B: Weaver has its own tick mechanism
   - Option C: Heartbeat IS a specialized Weaver

4. **Multiple session handling?**
   - Ghost Lock Protocol (OPUS-027)
   - Split-brain prevention
   - Crash recovery with Weaver

---

<!-- @HARNESS
# =============================================================================
# OPUS-096 STATE SYNC HOLON WEAVER - VERIFICATION HARNESS
# =============================================================================
# Status: DRAFT - Patterns defined but not yet implemented

files:
  # === CORE WEAVER (NEW) ===
  - path: vibe_core/state/weaver.py
    required: false
    rationale: "StateSyncWeaver - Meta-orchestration of all state sync"

  # === EXISTING STATE ENGINE ===
  - path: vibe_core/state/prakriti.py
    required: true
  - path: vibe_core/state/sync_holon.py
    required: true
  - path: vibe_core/state/git_state.py
    required: true

  # === MANAS ORACLE (cognitive weaving) ===
  - path: vibe_core/plugins/opus_assistant/manas/api.py
    required: true
    rationale: "ManasOracle provides cognitive weaving input"

  # === HEARTBEAT (scheduled trigger) ===
  - path: scripts/heartbeat.py
    required: true
    rationale: "Must integrate with Weaver for unified commits"

  # === CHRONICLE (commit execution) ===
  - path: vibe_core/cartridges/system/chronicle/tools/git_tools.py
    required: true
    rationale: "seal_history must support Weaver decisions"

wiring:
  # === EXISTING PATTERNS (verify these work) ===
  - pattern: "class StateSyncHolon"
    in: vibe_core/state/sync_holon.py
  - pattern: "class ManasOracle"
    in: vibe_core/plugins/opus_assistant/manas/api.py
  - pattern: "def seal_history"
    in: vibe_core/cartridges/system/chronicle/tools/git_tools.py
  - pattern: "no_verify.*=.*True"
    in: scripts/heartbeat.py
    context: "Runtime state commits must skip hooks"

  # === FUTURE PATTERNS (weaver implementation) ===
  # - pattern: "class StateSyncWeaver"
  #   in: vibe_core/state/weaver.py
  # - pattern: "def consult_manas"
  #   in: vibe_core/state/weaver.py
  # - pattern: "weaver\\.pulse"
  #   in: scripts/heartbeat.py

semantic:
  # === CRITICAL SEPARATION ===
  - type: layer_separation
    name: vibe_os_vs_plugin
    description: "VIBE OS (Mutterschiff) must not import from plugins directly"
    constraint: |
      vibe_core/state/*.py should NOT import from vibe_core/plugins/*
      Exception: Weaver can import ManasOracle via Protocol/Interface

  # === SINGLE COMMIT AUTHORITY ===
  - type: single_authority
    name: commit_orchestration
    description: "All state commits should go through Weaver"
    constraint: |
      After implementation, direct calls to:
      - GitTools.seal_history() from Heartbeat
      - prakriti.commit_if_dirty() from plugins
      Should be replaced with Weaver.pulse() or Weaver.commit()

tests:
  # === FUTURE TESTS ===
  - tests/state/test_weaver.py
  - tests/integration/test_weaver_manas.py
  - tests/integration/test_weaver_heartbeat.py

fire_commands:
  - name: "Verify sync_holon exists"
    command: "test -f vibe_core/state/sync_holon.py && echo OK"
  - name: "Verify ManasOracle exists"
    command: "test -f vibe_core/plugins/opus_assistant/manas/api.py && echo OK"
  - name: "Verify no_verify in heartbeat"
    command: "grep -q 'no_verify=True' scripts/heartbeat.py && echo OK"
-->

---

## Implementation Roadmap

### Phase 0: Document & Validate (THIS DOCUMENT)
- [x] Analyze existing patterns
- [x] Define Weaver architecture
- [x] Create @HARNESS verification
- [ ] Review with stakeholders

### Phase 1: Foundation
- [ ] Create `RuntimeStateDefinition` (single source of truth)
- [ ] Refactor `sync_holon.py` to use it
- [ ] Add Weaver integration points to Prakriti

### Phase 2: Weaver Core
- [ ] Implement `StateSyncWeaver` class
- [ ] Wire discovery → classification → decision
- [ ] Add MANAS Oracle consultation

### Phase 3: Integration
- [ ] Heartbeat uses `weaver.pulse()`
- [ ] Session boundaries use `weaver.on_session_end()`
- [ ] Remove direct `seal_history()` calls

### Phase 4: Learning Loop
- [ ] MANAS learns from commit outcomes
- [ ] Weaver adapts strategies based on patterns
- [ ] Conflict healing improves over time

---

## Fire Commands

```bash
# Verify existing components exist
test -f vibe_core/state/sync_holon.py && echo "✅ sync_holon.py"
test -f vibe_core/plugins/opus_assistant/manas/api.py && echo "✅ ManasOracle"
grep -q "no_verify=True" scripts/heartbeat.py && echo "✅ no_verify in heartbeat"

# Run existing state tests
python -m pytest tests/state/ -v

# Future: Verify weaver
# steward verify 096
```

---

*"The Weaver doesn't create the threads - it reveals the fabric that was always there."*
