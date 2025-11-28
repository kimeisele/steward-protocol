# 🏗️ STEWARD PROTOCOL ARCHITECTURE (VibeOS Native)

## 🎯 EXECUTIVE SUMMARY

**steward-protocol** is a **Governance Cartridge Pack** for the VibeOS kernel (`vibe-agency`).

It is **NOT** a standalone application. It is a **set of native VibeAgent implementations** that run within the VibeOS runtime.

### The Paradigm Shift

```
OLD ARCHITECTURE (❌ Abandoned):
├─ Standalone agents
├─ Filesystem-based registry
├─ Self-managed event loops
├─ Git hooks for discovery
└─ No kernel coordination

NEW ARCHITECTURE (✅ Active):
├─ VibeAgent native implementations
├─ Kernel-managed registry (manifest_registry)
├─ Task-driven via kernel scheduler
├─ Runtime discovery via kernel API
└─ Full kernel coordination
```

---

## 🏛️ ARCHITECTURE LAYERS

### Layer 0: THE PROTOCOL (CODE IS LAW)

**Constitution** - Immutable governance rules as code

```python
# Example: herald/governance/constitution.py
class HeraldConstitution:
    """Immutable rules for content generation and broadcasting"""

    def validate(self, content: str) -> ValidationResult:
        # Rules engine (no clichés, fact-based, etc.)
        pass
```

**Scope**: Defines constraints. Applied by agents.

---

### Layer 1: THE OS (VibeOS Kernel)

**Location**: `vibe-agency/vibe_core/kernel.py`

The **runtime host** for all cartridges. Provides:

| Component | Purpose |
|-----------|---------|
| `VibeKernel` | Main orchestrator |
| `agent_registry` | Maps agent_id → VibeAgent instance |
| `scheduler` | FIFO task queue |
| `manifest_registry` | Agent identity + capabilities |
| `ledger` | Immutable task history (SQLite @ `data/vibe_ledger.db`) |
| `identities` | Cryptographic keys per agent (in `data/identities/`) |

**Responsibility**:
- Load cartridges at boot
- Inject kernel reference via `set_kernel()`
- Coordinate task execution
- Maintain manifest registry
- Restore state from persistent ledger on boot
- Load agent identity keys from `data/identities/`

---

### Layer 2: THE SYSTEM AGENTS (VibeAgent Implementations)

**Location**: `steward-protocol/` (this repo)

Four core agents that implement governance:

#### 🏛️ **CIVIC** - Authority & Registry

**Agent ID**: `civic`
**Domain**: `GOVERNANCE`
**Capabilities**: `registry`, `licensing`, `ledger`, `governance`

**Old Design**: Scanned filesystem for cartridges
**New Design**: Queries kernel for authoritative agent list

```python
# NEW: Kernel-aware registry query
manifests = self.kernel.manifest_registry.list_all()
for manifest in manifests:
    print(f"{manifest.agent_id}: {manifest.name}")

# OLD: Filesystem scan (DELETED)
# cartridges = glob("*/cartridge_main.py")
```

**Key Methods**:
- `check_broadcast_license(agent_id)` - Verify permission
- `deduct_credits(agent_id)` - Charge for action
- `refill_credits(agent_id)` - Admin refill

---

#### 🦅 **HERALD** - Media & Content

**Agent ID**: `herald`
**Domain**: `MEDIA`
**Capabilities**: `content_generation`, `broadcasting`, `research`, `strategy`

**Workflow**:
1. Research (via SCIENCE agent)
2. Create (LLM-based content)
3. Validate (against Constitution)
4. Publish (multi-platform)

**Governance Integration**:
```python
# In process() method:
if action == "run_campaign":
    # Checks license via CIVIC
    license = civic.process(Task(
        agent_id="civic",
        payload={"action": "check_license", "agent_id": "herald"}
    ))
```

---

#### 🗳️ **FORUM** - Democracy & Voting

**Agent ID**: `forum`
**Domain**: `GOVERNANCE`
**Capabilities**: `governance`, `voting`, `proposal_management`

**Workflow**:
1. Create proposal (from agent)
2. Collect votes (from citizens)
3. Check threshold (50% + 1)
4. Execute action (via CIVIC)

**Data Model**:
```
data/governance/
├── proposals/        # PROP-001.json, PROP-002.json, ...
├── votes/           # votes.jsonl (append-only ledger)
└── executed/        # Archive of executed proposals
```

---

#### 🔬 **SCIENCE** - Research & Intelligence

**Agent ID**: `science`
**Domain**: `SCIENCE`
**Capabilities**: `research`, `web_search`, `fact_synthesis`

**Purpose**: Supplies ground truth to HERALD

**Usage**:
```python
briefing = science.process(Task(
    agent_id="science",
    payload={"action": "research", "query": "AI governance trends"}
))
```

---

### Layer 3: SUPPORTING AGENTS (Future)

Additional agents in the cartridge pack:

- **ARCHIVIST** - Knowledge & documentation
- **AUDITOR** - Compliance & verification
- **ARTISAN** - Media operations
- **ENGINEER** - Meta-builder & automation
- **WATCHMAN** - Monitoring & alerts

---

## 🔄 TASK FLOW (VibeOS Coordination)

```
┌─────────────────────────────────────────────────────────────┐
│ VibeOS Kernel                                               │
│                                                              │
│  ┌───────────────┐                                          │
│  │ Scheduler     │ FIFO Task Queue                          │
│  └───────┬───────┘                                          │
│          │                                                   │
│    task = {                                                 │
│      agent_id: "herald",                                    │
│      payload: {action: "run_campaign"},                     │
│      task_id: "uuid..."                                     │
│    }                                                         │
│          │                                                   │
│    ┌─────▼──────────────────────────────┐                 │
│    │ Herald.process(task)               │                 │
│    │ ├─ Check license (ask CIVIC)       │                 │
│    │ ├─ Research (ask SCIENCE)          │                 │
│    │ ├─ Generate content                │                 │
│    │ ├─ Validate (Constitution)         │                 │
│    │ └─ Publish                         │                 │
│    └─────┬──────────────────────────────┘                 │
│          │                                                   │
│    ┌─────▼──────────────┐                                  │
│    │ Ledger.record()    │ SQLite (immutable)              │
│    └────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 REGISTRY & STATE MANAGEMENT

### Source of Truth: VibeOS Kernel

```python
# The kernel's manifest registry is authoritative
manifests = kernel.manifest_registry.list_all()

# Returns:
[
    AgentManifest(agent_id="civic", name="CIVIC", ...),
    AgentManifest(agent_id="herald", name="HERALD", ...),
    AgentManifest(agent_id="forum", name="FORUM", ...),
    AgentManifest(agent_id="science", name="SCIENCE", ...),
]
```

### CITYMAP: Real-Time Agent Map

**Generated by CIVIC** from kernel registry:

```markdown
# 🏙️ AGENT CITY MAP

Generated: 2025-11-24T12:00:00Z
Kernel Status: RUNNING
Total Agents: 4

## GOVERNANCE

### CIVIC (`civic`)
- Version: 2.0.0
- Capabilities: registry, licensing, ledger, governance
- Status: 🟢 RUNNING

### FORUM (`forum`)
- Version: 1.0.0
- Capabilities: governance, voting, proposal_management
- Status: 🟢 RUNNING

## MEDIA

### HERALD (`herald`)
- Version: 3.0.0
- Capabilities: content_generation, broadcasting, research, strategy
- Status: 🟢 RUNNING

## SCIENCE

### SCIENCE (`science`)
- Version: 1.0.0
- Capabilities: research, web_search, fact_synthesis
- Status: 🟢 RUNNING
```

---

## 🔌 INTEGRATION POINTS

### How Cartridges Interact

```python
# 1. Dependency Injection (VibeAgent pattern)
herald = HeraldCartridge()
herald.set_kernel(kernel)  # Called by kernel.boot()

# 2. Agent Registry Query
civic = kernel.agent_registry["civic"]

# 3. Direct Inter-Agent Communication
license = civic.check_broadcast_license("herald")

# 4. Task Submission (via scheduler)
kernel.scheduler.submit_task(Task(
    agent_id="science",
    payload={"action": "research", "query": "..."}
))
```

### Governance Workflow

```
HERALD wants to publish
    ↓
Check license: HERALD → CIVIC.check_broadcast_license()
    ↓
✅ Licensed? → Deduct credits: HERALD → CIVIC.deduct_credits()
    ↓
Credits available? → Publish
    ✗ No credits? → Create proposal: HERALD → FORUM.create_proposal()
    ↓
FORUM collects votes
    ↓
✅ Approved? → Execute: FORUM → CIVIC.refill_credits("herald")
    ↓
HERALD resumes publishing
```

---

## 📁 FILE STRUCTURE

```
steward-protocol/
├── vibe_core/                          # VibeAgent Protocol Stubs
│   ├── __init__.py
│   ├── agent_protocol.py               # VibeAgent interface
│   ├── kernel.py                       # VibeKernel interface
│   └── scheduling/
│       ├── __init__.py
│       └── task.py                     # Task data class
│
├── civic/                              # CIVIC Cartridge
│   ├── cartridge_main.py               # CivicCartridge(VibeAgent)
│   └── tools/
│       ├── ledger_tool.py              # Credit management
│       ├── license_tool.py             # Broadcasting permissions
│       ├── registry_tool.py            # Agent registry queries
│       └── map_tool.py                 # CityMap generation (kernel-aware)
│
├── herald/                             # HERALD Cartridge
│   ├── cartridge_main.py               # HeraldCartridge(VibeAgent)
│   ├── tools/                          # Content generation tools
│   ├── governance/
│   │   └── constitution.py             # Immutable rules
│   └── core/
│       └── memory.py                   # Event sourcing
│
├── forum/                              # FORUM Cartridge
│   ├── cartridge_main.py               # ForumCartridge(VibeAgent)
│   └── tools/                          # Proposal & voting tools
│
├── science/                            # SCIENCE Cartridge
│   ├── cartridge_main.py               # ScientistCartridge(VibeAgent)
│   └── tools/
│       └── web_search_tool.py          # Tavily search integration
│
├── data/                               # Persistent State
│   ├── vibe_ledger.db                  # ⭐ SQLite - ALL ledger entries, crash-recovery, immutable
│   ├── identities/                     # ⭐ Cryptographic keys
│   │   ├── civic.pem                   # CIVIC's ECDSA private key
│   │   ├── herald.pem                  # HERALD's ECDSA private key
│   │   ├── forum.pem                   # FORUM's ECDSA private key
│   │   └── science.pem                 # SCIENCE's ECDSA private key
│   ├── registry/
│   │   ├── citizens.json               # Local cache (fallback)
│   │   ├── ledger.jsonl                # Credit transactions (legacy, also in SQLite)
│   │   └── licenses.json               # License database
│   ├── governance/
│   │   ├── proposals/                  # PROP-001.json, ...
│   │   ├── votes/
│   │   │   └── votes.jsonl             # Vote ledger (append-only)
│   │   └── executed/                   # Executed proposals
│   ├── events/
│   │   └── herald.jsonl                # HERALD event log
│   └── science/
│       ├── cache/                      # Search results cache
│       └── results/                    # Research findings
│
├── config/                             # Configuration
│   └── matrix.yaml                     # THE MATRIX (central config)
│
├── ARCHITECTURE.md                     # This file
├── ARCHITECTURE_PLAN.md                # Old build plan (reference)
├── STEWARD.md                          # STEWARD Protocol specification
└── AGENTS.md                           # Auto-generated agent registry
```

---

## 🚀 DEPLOYMENT MODEL

### Development (Standalone)

Cartridges can be tested standalone (for development):

```bash
# Not recommended in production
herald = HeraldCartridge()
result = herald.run_campaign()  # Old API (for backward compatibility)
```

### Production (VibeOS Native) — ⭐ RECOMMENDED

```python
# This is the correct deployment model
kernel = VibeKernel()
kernel.boot()  # Loads all cartridges from vibe_core/cartridges/

# Kernel automatically:
# 1. Discovers cartridges
# 2. Calls set_kernel() on each
# 3. Registers manifests
# 4. Initializes scheduler & ledger (SQLite @ data/vibe_ledger.db)
# 5. Restores all historical state from persistent ledger
# 6. Loads agent identity keys from data/identities/

# Use kernel API to submit tasks
kernel.scheduler.submit_task(Task(
    agent_id="herald",
    payload={"action": "run_campaign"}
))

# Kernel executes the task
while kernel.status == KernelStatus.RUNNING:
    kernel.tick()  # Process one task
```

**Persistence Guarantee:**
- ✅ Ledger stored in SQLite (`data/vibe_ledger.db`)
- ✅ Auto-recovery on kernel restart
- ✅ Cryptographically signed entries (unforgeable)
- ✅ All governance state persists (proposals, votes, credits)

---

## ⚡ KEY ARCHITECTURAL DECISIONS

### 1. **Single Source of Truth (Kernel)**

OLD: Cartridges scanned filesystem independently
NEW: Kernel registry is authoritative

✅ **Benefit**: Real-time accuracy, no stale caches, dynamic agent support

### 2. **Task-Driven (vs. Event-Driven)**

OLD: Agents had own event loops
NEW: Agents respond to kernel tasks

✅ **Benefit**: Coordinated execution, scheduler control, easier testing

### 3. **Kernel Injection (vs. Global Singleton)**

OLD: Agents imported civic globally
NEW: Kernel injects itself via `set_kernel()`

✅ **Benefit**: Testability, loose coupling, dependency clarity

### 4. **Git Hook ELIMINATION**

OLD: `.githooks/pre-commit` scanned and regenerated registry
NEW: Deleted - kernel discovery handles this

✅ **Benefit**: Real-time discovery, works with Docker, no Build-Time dependency

### 5. **Immutable SQLite Ledger (Event Sourcing + Persistence)**

ALL state changes → SQLite database (`data/vibe_ledger.db`)

✅ **Benefit**: Crash recovery, audit trail, temporal queries, **PERSISTENCE ACROSS RESTARTS**

**This is not a simulation.** The ledger survives process death, power outages, container restarts. All 2000+ entries restored on boot.

### 6. **Cryptographic Identity (Real Crypto, Not Mock)**

Each agent gets an ECDSA private key stored in `data/identities/`.

✅ **Benefit**: Unforgeable action signatures, provable accountability, multi-agent coordination

---

## 🔮 FUTURE EXTENSIONS

### Cartridge Isolation

When vibe-agency supports **process isolation**, cartridges can run in separate processes:

```
Kernel (Process 1)
├─ Scheduler
├─ Manifest Registry
└─ Ledger (IPC)

Agents (Processes 2-5)
├─ CIVIC (Process 2)
├─ HERALD (Process 3)
├─ FORUM (Process 4)
└─ SCIENCE (Process 5)
```

### Distributed Ledger

Future: Replace SQLite with distributed ledger (blockchain-like):

```python
kernel.ledger.record_completion(task, result)
# Automatically syncs across federation nodes
```

### Federation

Multiple VibeOS instances coordinate:

```
City 1 (vibe-agency-1)      City 2 (vibe-agency-2)
├─ CIVIC                     ├─ CIVIC
├─ HERALD                    ├─ HERALD
└─ FORUM ──── IPC ──────────── FORUM
```

---

## 📚 REFERENCES

- **VibeOS Kernel**: `vibe-agency/vibe_core/kernel.py`
- **Protocol Spec**: `STEWARD.md`
- **Build Plan**: `ARCHITECTURE_PLAN.md` (historical reference)

---

**Last Updated**: 2025-11-24
**Architecture Version**: 2.0 (VibeOS Native)
**Status**: ✅ ALIGNED WITH VIBE-AGENCY KERNEL

