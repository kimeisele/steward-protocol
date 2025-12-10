# OPUS-009: Unified State Management (PRAKRITI)

> **Status**: ✅ IMPLEMENTED
> **Created**: 2025-12-08
> **Implemented**: 2025-12-08d)
> **Purpose**: Unified State & Identity Management for Agent OS
> **GAD-000**: See compliance section below

<!-- @HARNESS
files:
  - path: vibe_core/runtime/unified_execution.py
    required: true
  - path: vibe_core/runtime/layered_router.py
    required: true
  - path: vibe_core/state/git_state.py
    required: true
  - path: vibe_core/state/kernel_state.py
    required: true
  - path: vibe_core/state/file_state.py
    required: true
  - path: vibe_core/state/ephemeral_state.py
    required: true
  - path: vibe_core/state/persona.py
    required: true
  - path: vibe_core/kernel_impl.py
    required: true
  - path: vibe_core/state/prakriti.py
    required: true
tests: []
wiring:
  - pattern: "Prakriti"
    in: vibe_core/state/prakriti.py
  - pattern: "AgentPersona"
    in: vibe_core/state/persona.py
  - pattern: "GitState"
    in: vibe_core/state/git_state.py
  - pattern: "KernelState"
    in: vibe_core/state/kernel_state.py
absent:
  - pattern: "TODO.*persona"
    in: vibe_core/state/persona.py
  - pattern: "TODO.*prakriti"
    in: vibe_core/state/prakriti.py
config:
  - section: state_management
  - section: persona_storage
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

## Related Documents

- **OPUS-001-008**: Foundation (superseded context)
- **GAD-000**: Operator Inversion (Prakriti must be AI-operable)
- **Gemini Review**: Requested for this document

---

**Signed**: Opus 4.5
**Date**: 2025-12-08
**Status**: AWAITING REVIEW (No implementation until approved)

> *"The Repository IS the Mind"*
> *- Gemini's Insight*
