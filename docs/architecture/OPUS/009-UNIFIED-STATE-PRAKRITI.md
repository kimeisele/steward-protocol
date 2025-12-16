# OPUS-009: Unified State Management (PRAKRITI)

> **Status**: 🔥 GOLDEN FOUNDATION - The Philosophical Core
> **Created**: 2025-12-08
> **Deepened**: 2025-12-16 (Fractal State, Plugin Discovery, Sync Holon)
> **Related**: OPUS-027 (Implementation), OPUS-028 (Git Slave)
> **Purpose**: Unified State & Identity Management for Agent OS
> **GAD-000**: See compliance section below
> **Philosophy**: This is the CONCEPTUAL FOUNDATION. Not "superseded" - FOUNDATIONAL.

**IMPORTANT**: OPUS-027/028 implement PARTS of this vision. This document is the SOURCE OF TRUTH for the complete architecture. When 027/028 conflict with 009, 009 wins.

<!-- @HARNESS
files:
  # === CORE STATE ENGINE ===
  - path: vibe_core/state/prakriti.py
    required: true
  - path: vibe_core/state/git_state.py
    required: true
  - path: vibe_core/state/ledger_state.py
    required: true
  - path: vibe_core/state/kernel_state.py
    required: true
  - path: vibe_core/state/file_state.py
    required: true
  - path: vibe_core/state/ephemeral_state.py
    required: true
  - path: vibe_core/state/persona.py
    required: true
  # === RUNTIME INTEGRATION ===
  - path: vibe_core/runtime/unified_execution.py
    required: true
  - path: vibe_core/runtime/layered_router.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  # === STATE LOCATIONS (must exist, must be tracked) ===
  - path: .opus_state/manas_intents.json
    required: true
  - path: .opus_state/sankalpa.json
    required: true

tests:
  # === PRAKRITI TEST SUITE ===
  - tests/state/test_prakriti.py
  - tests/state/test_git_state.py
  - tests/state/test_ledger_state.py
  - tests/state/test_kernel_state.py
  - tests/state/test_file_state.py
  - tests/state/test_ephemeral_state.py
  - tests/state/test_persona.py
  # === INTEGRATION ===
  - tests/integration/test_prakriti_kernel.py
  - tests/integration/test_state_sync.py

wiring:
  # === CORE CLASS STRUCTURE ===
  - pattern: "class Prakriti"
    in: vibe_core/state/prakriti.py
  - pattern: "class GitState"
    in: vibe_core/state/git_state.py
  - pattern: "class LedgerState"
    in: vibe_core/state/ledger_state.py
  - pattern: "class KernelState"
    in: vibe_core/state/kernel_state.py
  - pattern: "class AgentPersona"
    in: vibe_core/state/persona.py

  # === CRITICAL METHODS ===
  - pattern: "def commit_if_dirty"
    in: vibe_core/state/prakriti.py
  - pattern: "def sync_ledger_git"
    in: vibe_core/state/prakriti.py
  - pattern: "def snapshot"
    in: vibe_core/state/prakriti.py
  - pattern: "def verify"
    in: vibe_core/state/prakriti.py

  # === KERNEL INTEGRATION ===
  - pattern: "self\\.prakriti"
    in: vibe_core/kernel_impl.py
  - pattern: "prakriti\\.commit_if_dirty"
    in: vibe_core/kernel_impl.py

  # === STATE FILE TRACKING (NEW - Plugin Discovery) ===
  # Every plugin with state MUST have its state tracked
  - pattern: "\\.opus_state"
    in: vibe_core/plugins/opus_assistant/plugin_main.py
  - pattern: "\\.vibe/state"
    in: vibe_core/task_management/task_manager.py

absent:
  # === NO ORPHAN STATE ===
  # State files must NEVER be in .gitignore
  - pattern: "\\.opus_state"
    in: .gitignore
  - pattern: "\\.vibe/state"
    in: .gitignore
  - pattern: "state.*\\.json"
    in: .gitignore
  # === NO INCOMPLETE PRAKRITI ===
  - pattern: "TODO.*prakriti"
    in: vibe_core/state/prakriti.py
  - pattern: "TODO.*persona"
    in: vibe_core/state/persona.py

config:
  - section: state_management
  - section: persona_storage
  - section: guardrails.ui_files

semantic:
  # === API COMPLETENESS ===
  - type: module_exports
    name: prakriti_public_api
    module: vibe_core.state.prakriti
    exports:
      - Prakriti
      - StateSnapshot
      - ConsistencyReport
      - SyncResult
      - CommitResult

  # === LAYER COMPLETENESS ===
  - type: method_exists
    name: prakriti_has_all_layers
    in: vibe_core/state/prakriti.py
    class: Prakriti
    method: snapshot

  - type: method_exists
    name: prakriti_can_verify
    in: vibe_core/state/prakriti.py
    class: Prakriti
    method: verify

  - type: method_exists
    name: prakriti_can_commit
    in: vibe_core/state/prakriti.py
    class: Prakriti
    method: commit_if_dirty

  # === HOLISTIC RUNTIME CHECKS ===
  - type: file_writable
    name: opus_state_writable
    path: .opus_state/
    rationale: "MANAS needs write access to persist intents"

  - type: file_writable
    name: vibe_state_writable
    path: .vibe/state/
    rationale: "Task Manager needs write access to persist tasks"

  - type: git_tracked
    name: state_files_tracked
    paths:
      - .opus_state/
      - .vibe/state/
      - .vibe/config/
    rationale: "State files MUST be committed, never ignored"
-->

---

## Executive Summary

**Stop thinking in tools. Start thinking in organism.**

PRAKRITI (Sanskrit: "Primordial Matter") is the unified state engine that treats:
- Every **Agent** as a Commit
- Every **Decision** as a Branch
- Every **Learning** as a Merge

This is not "Git Operations". This is **The Repository IS the Mind**.

---

## The Problem We're Actually Solving

Current state is fragmented across:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRAGMENTED STATE                         │
├─────────────────────────────────────────────────────────────┤
│  Git          → Code, but no runtime awareness              │
│  Kernel       → Runtime, but no persistence                 │
│  Ledger       → Audit, but no identity                      │
│  Files        → Config, but no versioning                   │
│  LLM Context  → Ephemeral, lost every session               │
└─────────────────────────────────────────────────────────────┘
```

**The Real Problem**: An agent cannot remember who it is between sessions.

**The Solution**: The System Prompt is not a constant. It's a **variable in the state**.

---

## The Triad: Three Layers of Being

```
┌─────────────────────────────────────────────────────────────┐
│                       PRAKRITI                              │
│                (Unified State Engine)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ╔═══════════════════════════════════════════════════════╗  │
│  ║  LAYER 3: PURUSHA (Spirit/Identity)                   ║  │
│  ║  ─────────────────────────────────────────────────    ║  │
│  ║  • System Prompt as mutable state                     ║  │
│  ║  • Personality traits (curious: 0.8, cautious: 0.6)   ║  │
│  ║  • Learned preferences from interactions              ║  │
│  ║  • Varna/Dharma assignment                            ║  │
│  ║  • Lives in: context/personas/{agent_id}.yaml         ║  │
│  ╚═══════════════════════════════════════════════════════╝  │
│                          ▲                                  │
│                          │ informs                          │
│                          ▼                                  │
│  ╔═══════════════════════════════════════════════════════╗  │
│  ║  LAYER 2: PRANA (Energy/Runtime)                      ║  │
│  ║  ─────────────────────────────────────────────────    ║  │
│  ║  • Tasks, Queues, Circuit State                       ║  │
│  ║  • Ephemeral Storage (Chain of Thought)               ║  │
│  ║  • Agent Registry, Capabilities                       ║  │
│  ║  • Current conversation context                       ║  │
│  ║  • Lives in: Kernel memory (RAM)                      ║  │
│  ╚═══════════════════════════════════════════════════════╝  │
│                          ▲                                  │
│                          │ persists to                      │
│                          ▼                                  │
│  ╔═══════════════════════════════════════════════════════╗  │
│  ║  LAYER 1: STHULA (Substance/Physical)                 ║  │
│  ║  ─────────────────────────────────────────────────    ║  │
│  ║  • Git Repository (Code, Configs, Markdown)           ║  │
│  ║  • Ledger (SQLite, Hash Chain)                        ║  │
│  ║  • File System (ENVOY.md, OPUS.md)                    ║  │
│  ║  • Lives in: Disk                                     ║  │
│  ╚═══════════════════════════════════════════════════════╝  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Git as Consciousness Stream

**Forget "version control". Git is cognitive logging.**

| Git Operation | Consciousness Equivalent |
|---------------|--------------------------|
| `branch` | Start thinking about something |
| `commit` | Crystallize a fact/decision |
| `diff` | Proof of Work (what changed?) |
| `merge` | Learning (integrate knowledge) |
| `HEAD` | Current state of mind |
| `log` | Memory/History |
| `checkout` | Context switch |

### The Agent Work Cycle

```
┌─────────────────────────────────────────────────────────────┐
│                   CONSCIOUSNESS CYCLE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. BRANCH (Intention)                                      │
│     Agent receives task → git branch task/{hash}            │
│     "I am now thinking about X"                             │
│                                                             │
│  2. THINK (Ephemeral)                                       │
│     Chain of Thought → Ephemeral Storage                    │
│     Not committed. Can be discarded.                        │
│     "Working memory"                                        │
│                                                             │
│  3. COMMIT (Crystallize)                                    │
│     Insight/Decision → git commit                           │
│     "I now KNOW this"                                       │
│     Each commit = atomic fact                               │
│                                                             │
│  4. VERIFY (Proof of Work)                                  │
│     git diff main..HEAD                                     │
│     Steward validates: "Is this work real?"                 │
│     Diff = Evidence of consciousness                        │
│                                                             │
│  5. MERGE (Learn)                                           │
│     Squash merge → main                                     │
│     "This is now part of my identity"                       │
│     Delete branch (forget the thinking, keep the knowing)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Persona Cartridge

**An Agent is a shell. Its soul is a file.**

```yaml
# context/personas/haiku-coder.yaml
agent_id: haiku-coder
varna: shudra  # Worker caste - executes tasks
dharma: code   # Life purpose - write code

personality:
  curious: 0.7
  cautious: 0.9
  verbose: 0.3

system_prompt: |
  You are a focused code implementer.
  You prefer small, atomic changes.
  You always run tests before committing.
  You ask clarifying questions when requirements are unclear.

learned_preferences:
  - prefers_pytest_over_unittest
  - likes_type_hints
  - avoids_comments_for_obvious_code

context_window:
  max_messages: 50
  summarize_after: 30

evolution:
  parent: null  # Or "opus-architect" if forked
  generation: 1
  mutations: []
```

### Runtime Injection

```python
# On kernel boot or agent spawn
persona = Prakriti.load_persona("haiku-coder")
system_message = persona.to_system_prompt()
# Inject into LLM context
```

### Self-Modification

```python
# Agent can modify its own persona via ENVOY.md or tool
await kernel.tools.write_file(
    "context/personas/haiku-coder.yaml",
    updated_persona
)
# Next boot: Agent has new personality
```

### Agent Forking (Evolution)

```python
# Create child agent with mutation
child_persona = parent_persona.fork(
    agent_id="haiku-coder-v2",
    mutations={"cautious": 0.5}  # Less cautious child
)
# Child is a new branch of consciousness
```

---

## UnifiedState API

```python
class Prakriti:
    """The Fractal State Engine."""

    # Layer 1: Sthula (Physical)
    git: GitState           # Branches, commits, diffs
    ledger: LedgerState     # Events, hash chain
    files: FileState        # Workspace files

    # Layer 2: Prana (Runtime)
    kernel: KernelState     # Tasks, agents, queue
    ephemeral: EphemeralState  # Temp data, CoT

    # Layer 3: Purusha (Identity)
    personas: Dict[str, AgentPersona]

    # Operations
    def snapshot(self) -> StateSnapshot:
        """Full state dump across all layers."""

    def verify(self) -> ConsistencyReport:
        """Cross-layer consistency check."""

    def restore(self, snapshot: StateSnapshot) -> None:
        """Recover from snapshot."""

    def diff(self, other: StateSnapshot) -> StateDelta:
        """What changed between two points in time?"""

    def sync(self) -> None:
        """Reconcile all layers (e.g., after crash)."""

    # Persona Operations
    def load_persona(self, agent_id: str) -> AgentPersona:
        """Load identity from disk into runtime."""

    def save_persona(self, persona: AgentPersona) -> None:
        """Persist identity changes."""

    def fork_persona(self, parent_id: str, child_id: str,
                     mutations: dict) -> AgentPersona:
        """Create evolved child agent."""
```

---

## Integration with Existing Architecture

### Where Prakriti Lives

```
vibe_core/
├── runtime/
│   ├── unified_execution.py   # UnifiedRouter (exists)
│   ├── layered_router.py      # LayeredRouter (exists)
│   └── prakriti.py            # NEW: UnifiedState
├── state/                      # NEW directory
│   ├── git_state.py           # Git operations
│   ├── kernel_state.py        # Runtime state
│   ├── file_state.py          # Workspace files
│   ├── ephemeral_state.py     # Temp storage
│   └── persona.py             # Agent identity
```

### Boot Sequence Integration

```python
# In kernel_impl.py boot()

# 1. Load Prakriti (before plugins)
self.prakriti = Prakriti.from_workspace(self.workspace_path)

# 2. Restore state from last shutdown (if exists)
if self.prakriti.has_snapshot("last_shutdown"):
    self.prakriti.restore("last_shutdown")

# 3. Load personas for all registered agents
for agent_id in self._agent_registry:
    persona = self.prakriti.load_persona(agent_id)
    self._agent_registry[agent_id].inject_persona(persona)

# 4. Continue normal boot...
```

### Shutdown Sequence

```python
# In kernel_impl.py shutdown()

# 1. Save current state
self.prakriti.save_snapshot("last_shutdown")

# 2. Persist all persona changes
for agent_id, agent in self._agent_registry.items():
    self.prakriti.save_persona(agent.persona)

# 3. Git commit if dirty
if self.prakriti.git.is_dirty():
    self.prakriti.git.commit("Auto-save on shutdown")
```

---

## Kernel LOC Impact

**Goal**: Reduce kernel_impl.py towards ~1008 LOC (currently higher)

| Change | LOC Impact |
|--------|------------|
| Add `self.prakriti` | +1 |
| Boot integration | +5 |
| Shutdown integration | +5 |
| **Total** | **+11 LOC** |

All actual logic lives in `vibe_core/state/` (new module).

**Note**: Current kernel is above 1008 LOC. This is aspirational target, not current state.

---

## Implementation

### Phase 1: Foundation (GitState + FileState)
- `vibe_core/state/git_state.py` - Git operations wrapper
- `vibe_core/state/file_state.py` - Workspace file tracking
- Basic `Prakriti` class with `.git` and `.files`
- **Deliverable**: `git diff` as work verification

### Phase 2: Runtime State
- `vibe_core/state/kernel_state.py` - Serialize kernel state
- `vibe_core/state/ephemeral_state.py` - Chain of Thought storage
- **Deliverable**: `prakriti.snapshot()` works

### Phase 3: Identity Layer (The Breakthrough)
- `vibe_core/state/persona.py` - AgentPersona class
- Persona loading on boot
- Runtime system prompt injection
- **Deliverable**: Agents remember who they are

### Phase 4: Self-Modification
- Persona edit via ENVOY.md
- Agent forking/evolution
- **Deliverable**: Agents can evolve

---

## Verification Checkpoints

### After Phase 1:
```bash
python3 -c "
from vibe_core.state.prakriti import Prakriti
p = Prakriti.from_workspace('.')
print(f'Git branch: {p.git.current_branch()}')
print(f'Dirty files: {p.files.dirty_files()}')
"
```

### After Phase 3:
```bash
python3 -c "
from vibe_core.kernel_impl import RealVibeKernel
k = RealVibeKernel(ledger_path=':memory:')
k.boot()
envoy = k._agent_registry['envoy']
print(f'Persona loaded: {envoy.persona.agent_id}')
print(f'System prompt length: {len(envoy.persona.system_prompt)}')
"
```

---

## Open Questions for Review

1. **Persona Storage Format**: YAML vs JSON vs SQLite?
   - YAML: Human-readable, git-friendly
   - JSON: Faster parsing
   - SQLite: Query-able

2. **Git Integration Depth**:
   - Minimal (just diff verification)?
   - Full (branch per task)?
   - Hybrid (branch for complex tasks only)?

3. **Self-Modification Limits**:
   - Can agent modify its own dharma/varna?
   - Need approval for personality changes?
   - Constitutional limits?

4. **Memory/Context Window**:
   - How much conversation history in persona?
   - Summarization strategy?
   - Token budget?

---

## Critical Business Requirements (Gemini Review)

### 1. Semantic Commit Gate

**Problem**: Agents write "I fixed the thing" - unreadable by other agents.

**Solution**: Enforce Conventional Commits via Scribe Filter:

```python
def seal_history(self, type: str, scope: str, subject: str, body: str):
    """Enforce semantic commits for machine parseability."""
    VALID_TYPES = ["feat", "fix", "chore", "refactor", "docs", "thinking"]
    if type not in VALID_TYPES:
        raise GovernanceViolation(f"Invalid commit type: {type}")

    formatted = f"{type}({scope}): {subject}\n\n{body}"
    formatted += f"\n\nSigned-off-by: Agent-{self.agent_id}"
    formatted += f"\nModel: {self.model_id}"
    formatted += f"\nTemperature: {self.temperature}"
    # ... execute git commit ...
```

**Why**: Makes history searchable ("show all `feat` in scope `payment`").

---

### 2. Concurrency: The Index Lock Problem

**Problem**: 50 agents doing `git commit` = `fatal: Unable to create 'index.lock'`

**Solution**: Serialization Queue in Prakriti:

```python
class PrakritiStateManager:
    """Sequential git operations to prevent locking."""

    _commit_queue: asyncio.Queue
    _lock: asyncio.Lock

    async def request_commit(self, agent_id: str, changes: dict):
        """Queue commit request, executed sequentially."""
        await self._commit_queue.put((agent_id, changes))

    async def _process_queue(self):
        """Single worker processes commits one by one."""
        while True:
            agent_id, changes = await self._commit_queue.get()
            async with self._lock:
                self._execute_commit(agent_id, changes)
```

**Alternative**: Each agent on own branch (`agent/{id}/current-task`), Steward merges.

---

### 3. Lazarus Protocol (Kill Switch)

**Problem**: Agent goes insane, writes garbage to persona, loops forever.

**Solution**: Hard reset as safety mechanism:

```python
def lazarus_reset(self, agent_id: str, target_ref: str = "origin/stable"):
    """
    Time-travel kill switch for misbehaving agents.

    Scenario: Agent 'marketer' generates harmful content,
    saves it as 'good' in persona. Watchman detects, triggers:

    git reset --hard origin/stable

    Agent loses memory of 'madness'. Ultimate control.
    """
    branch = f"agent/{agent_id}"
    subprocess.run(["git", "checkout", branch])
    subprocess.run(["git", "reset", "--hard", target_ref])
    self.ledger.record_event("LAZARUS_RESET", agent_id, {
        "reason": "governance_violation",
        "reset_to": target_ref
    })
```

---

### 4. Attribution Metadata

**Problem**: Debugging/cost control impossible without knowing which model generated what.

**Solution**: Every commit includes:

```yaml
# In commit message footer
Model: claude-3-opus
Temperature: 0.7
Token-Cost: 1234
Task-ID: task_abc123
Parent-Commit: def456
```

---

## GAD-000 Compliance Matrix

| Test | Question | PRAKRITI Implementation |
|------|----------|------------------------|
| **Discoverability** | Can AI find state tools? | `prakriti.get_capabilities()` returns all operations |
| **Observability** | Can AI see state? | `prakriti.snapshot()` dumps all 3 layers |
| **Parseability** | Can AI understand errors? | Uses `StructuredError` with codes |
| **Composability** | Can AI chain ops? | All methods return `dict` or `dataclass` |
| **Idempotency** | Can AI retry safely? | Commits are idempotent (same content = no-op) |
| **Identity** | Crypto verification? | Signed commits with agent ID |

### Required API for GAD-000:

```python
class Prakriti:
    def get_capabilities(self) -> dict:
        """GAD-000: Discoverability - what can Prakriti do?"""
        return {
            "operations": ["snapshot", "restore", "verify", "diff", "sync"],
            "layers": ["git", "kernel", "persona"],
            "supported_commit_types": ["feat", "fix", "chore", "refactor", "docs"],
        }

    def get_system_status(self) -> dict:
        """GAD-000: Observability - current state summary."""
        return {
            "git": {
                "branch": self.git.current_branch(),
                "dirty": self.git.is_dirty(),
                "last_commit": self.git.head_sha(),
            },
            "kernel": {
                "status": self.kernel.status,
                "agents": len(self.kernel.agents),
                "queue_depth": self.kernel.queue_depth,
            },
            "personas": {
                "loaded": list(self.personas.keys()),
                "modified": [p for p in self.personas if p.is_dirty],
            },
        }
```

---

## Non-Goals

- **Not a full Git client** - Just what agents need
- **Not replacing Ledger** - Ledger is audit, Prakriti is state
- **Not AI training** - This is runtime persistence, not model fine-tuning

---

## Success Criteria

1. Agent personality persists across kernel restarts
2. `git diff` validates agent work before merge
3. Persona editable via markdown UI
4. Kernel LOC stays under 1020
5. All existing tests pass

---

## FRACTAL STATE ARCHITECTURE (2025-12-16 Deepening)

**The Missing Piece: Every Plugin IS a Mini-Prakriti**

The original 009 described 3 layers. But it missed the FRACTAL nature:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRACTAL STATE HOLARCHY                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   PRAKRITI (System-Level)                                          │
│   ├── STHULA: Git + Ledger + Files                                 │
│   ├── PRANA: Kernel + Ephemeral + Session                          │
│   └── PURUSHA: System Personas                                     │
│         │                                                          │
│         ├──→ PLUGIN PRAKRITI (opus_assistant/MANAS)                │
│         │    ├── STHULA: .opus_state/*.json                        │
│         │    ├── PRANA: CognitiveKernel memory                     │
│         │    └── PURUSHA: MANAS persona/config                     │
│         │                                                          │
│         ├──→ PLUGIN PRAKRITI (task_manager)                        │
│         │    ├── STHULA: .vibe/state/*.json + SQLite              │
│         │    ├── PRANA: TaskManager in-memory dict                 │
│         │    └── PURUSHA: Roadmap config                           │
│         │                                                          │
│         └──→ PLUGIN PRAKRITI (any_plugin)                          │
│              ├── STHULA: {plugin_dir}/state/                       │
│              ├── PRANA: Plugin runtime state                       │
│              └── PURUSHA: Plugin config/identity                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Plugin State Contract

Every plugin with state MUST implement:

```python
class PluginStateContract(Protocol):
    """The Fractal Prakriti Contract."""

    def get_state_paths(self) -> List[Path]:
        """Return all paths where this plugin stores state.

        These paths will be:
        1. Auto-discovered by Prakriti
        2. Auto-committed on session boundaries
        3. NEVER ignored by git

        Examples:
            - [Path(".opus_state/")]
            - [Path(".vibe/state/"), Path("data/vibe_agency.db")]
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """Return current runtime state for inclusion in system snapshot."""
        ...

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot (crash recovery)."""
        ...
```

---

## PLUGIN STATE DISCOVERY (Zwischeninstanz)

**The Problem**: Plugins create state files. Nobody knows where. Nobody commits them.

**The Solution**: State Sync Holon - the Zwischeninstanz.

```python
class StateSyncHolon:
    """
    The Zwischeninstanz - bridges Plugin State to Git.

    Responsibilities:
    1. DISCOVER all plugin state paths
    2. WATCH for changes
    3. STAGE on session boundaries
    4. COMMIT via Prakriti
    5. RESOLVE merge conflicts (untötbar)
    """

    def discover_state_paths(self) -> Dict[str, List[Path]]:
        """
        Auto-discover all plugin state paths.

        Strategy:
        1. Query all loaded plugins for get_state_paths()
        2. Scan known locations (.opus_state/, .vibe/, plugin_dir/state/)
        3. Check manifest.json for state_paths declaration

        Returns:
            {"plugin_name": [Path(...), Path(...)], ...}
        """
        paths = {}

        # Method 1: Protocol query
        for plugin in self.kernel.plugins:
            if hasattr(plugin, 'get_state_paths'):
                paths[plugin.name] = plugin.get_state_paths()

        # Method 2: Convention scan
        conventions = [
            Path(".opus_state"),
            Path(".vibe/state"),
            Path(".vibe/config"),
        ]
        for plugin_dir in Path("vibe_core/plugins").iterdir():
            state_dir = plugin_dir / "state"
            if state_dir.exists():
                paths.setdefault(plugin_dir.name, []).append(state_dir)

        # Method 3: Manifest declaration
        for manifest in Path(".").glob("**/manifest.json"):
            data = json.loads(manifest.read_text())
            if "state_paths" in data:
                plugin_name = manifest.parent.name
                paths.setdefault(plugin_name, []).extend(
                    Path(p) for p in data["state_paths"]
                )

        return paths

    def ensure_tracked(self) -> List[str]:
        """
        Ensure all state paths are git-tracked (not ignored).

        Raises GovernanceViolation if any state path is in .gitignore.
        """
        violations = []
        gitignore = Path(".gitignore").read_text() if Path(".gitignore").exists() else ""

        for plugin, paths in self.discover_state_paths().items():
            for path in paths:
                if self._is_ignored(path, gitignore):
                    violations.append(f"{plugin}: {path} is IGNORED (LOBOTOMY!)")

        if violations:
            raise GovernanceViolation(
                "State files in .gitignore = LOBOTOMY!\n" +
                "\n".join(violations)
            )

        return list(self.discover_state_paths().keys())
```

---

## UNTÖTBAR MERGE STRATEGY

**The Problem**: State files get merge conflicts. System breaks.

**The Solution**: Per-type merge strategies that NEVER fail.

```python
class UntotbarMergeEngine:
    """
    Merge conflicts are NOT fatal. They are HEALABLE.

    Strategy per file type:
    - JSON state files: Deep merge with conflict markers
    - YAML config: Ours wins (config is human-controlled)
    - SQLite: Ledger merge via event replay
    - Binary: Ours wins (regenerate from source)
    """

    STRATEGIES = {
        "*.json": "deep_merge",      # Merge objects, concat arrays
        "*.yaml": "ours_wins",       # Config is human-controlled
        "*.db": "ledger_replay",     # Replay missing events
        "*.sqlite": "ledger_replay",
        "*": "ours_wins",            # Default: don't lose local work
    }

    def heal_conflict(self, path: Path, ours: bytes, theirs: bytes) -> bytes:
        """
        Heal a merge conflict. NEVER returns None. ALWAYS produces valid state.

        Args:
            path: Conflicting file path
            ours: Our version
            theirs: Their version

        Returns:
            Healed content (valid state)
        """
        strategy = self._get_strategy(path)

        if strategy == "deep_merge":
            return self._deep_merge_json(ours, theirs)
        elif strategy == "ours_wins":
            return ours
        elif strategy == "ledger_replay":
            return self._replay_ledger_events(path, ours, theirs)
        else:
            return ours  # Safe default

    def _deep_merge_json(self, ours: bytes, theirs: bytes) -> bytes:
        """
        Deep merge two JSON objects.

        Rules:
        - Objects: Recursive merge, ours wins on conflict
        - Arrays: Concatenate, dedupe by id if present
        - Primitives: Ours wins
        - Conflict markers preserved in _conflicts key
        """
        ours_data = json.loads(ours)
        theirs_data = json.loads(theirs)

        merged = self._recursive_merge(ours_data, theirs_data)
        merged["_merge_timestamp"] = time.time()
        merged["_merge_strategy"] = "deep_merge"

        return json.dumps(merged, indent=2).encode()

    def _recursive_merge(self, ours: Any, theirs: Any) -> Any:
        if isinstance(ours, dict) and isinstance(theirs, dict):
            result = dict(theirs)  # Start with theirs
            for key, value in ours.items():
                if key in result:
                    result[key] = self._recursive_merge(value, result[key])
                else:
                    result[key] = value
            return result
        elif isinstance(ours, list) and isinstance(theirs, list):
            # Concat and dedupe
            combined = theirs + [x for x in ours if x not in theirs]
            return combined
        else:
            return ours  # Ours wins
```

---

## STATE SYNC LIFECYCLE

The complete lifecycle of state in the system:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STATE SYNC LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. BOOT                                                           │
│     ├── StateSyncHolon.discover_state_paths()                      │
│     ├── StateSyncHolon.ensure_tracked()  ─→ FAIL if .gitignore!    │
│     ├── Prakriti.verify() ─→ Check Git↔Ledger consistency          │
│     └── Prakriti.recover_from_crash() ─→ Commit dirty state        │
│                                                                     │
│  2. RUNTIME                                                         │
│     ├── Plugins write state to their paths                         │
│     ├── StateSyncHolon watches for changes (optional)              │
│     └── MANAS intents accumulate in .opus_state/                   │
│                                                                     │
│  3. SHUTDOWN                                                        │
│     ├── StateSyncHolon.stage_all_state()                          │
│     ├── Prakriti.commit_if_dirty()                                 │
│     ├── Prakriti.sync_ledger_git()                                │
│     └── Prakriti.save_snapshot("shutdown")                         │
│                                                                     │
│  4. CRASH RECOVERY                                                  │
│     ├── Prakriti.begin_session()                                   │
│     ├── Detect dirty state from previous session                   │
│     ├── Prakriti.recover_from_crash() ─→ Commit with marker        │
│     └── Resume normal boot                                          │
│                                                                     │
│  5. MERGE CONFLICT (git pull)                                       │
│     ├── UntotbarMergeEngine.detect_conflicts()                     │
│     ├── UntotbarMergeEngine.heal_conflict() per file               │
│     ├── Auto-commit healed state                                   │
│     └── Log healing in Ledger                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION ROADMAP

### Phase 5: Plugin State Discovery (NEW)
- `StateSyncHolon` class in `vibe_core/state/sync_holon.py`
- Plugin state contract protocol
- Auto-discovery via protocol + convention + manifest
- `ensure_tracked()` enforcement

### Phase 6: Untötbar Merge Engine (NEW)
- `UntotbarMergeEngine` class in `vibe_core/state/merge_engine.py`
- Per-type merge strategies
- JSON deep merge
- Ledger replay for SQLite

### Phase 7: Fractal Plugin Integration (NEW)
- All plugins implement `PluginStateContract`
- MANAS: `.opus_state/` → Prakriti
- TaskManager: `.vibe/state/` → Prakriti
- Template for new plugins

---

## Related Documents

- **OPUS-027**: Implements Phases 1-4 (Git, Ledger, Session, Kernel)
- **OPUS-028**: Git write operations (sub-component)
- **OPUS-075**: MANAS Reliability (example of deep harness)
- **GAD-000**: Operator Inversion (API design)

---

## Philosophy Reminder

**"The Repository IS the Mind"**

State files are not "data to be backed up". They are **neurons**.
Ignoring them is **lobotomy**.
Merge conflicts are not errors - they are **opportunities for learning**.
Every plugin is a **cell in the organism** with its own state lifecycle.

The fractal nature means: What works for the whole, works for the part.
Prakriti at system level. Mini-Prakriti at plugin level.
Same patterns. Same contracts. Same lifecycle.

---

**Signed**: Opus 4.5
**Original**: 2025-12-08
**Deepened**: 2025-12-16
**Status**: 🔥 GOLDEN FOUNDATION

> *"The Repository IS the Mind"*
> *- Gemini's Insight*

> *"State files in .gitignore = Lobotomy"*
> *- User's Insight, 2025-12-16*
