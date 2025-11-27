# 🏗️ ARCHITECTURE ANALYSIS: vibe-agency vs steward-protocol

**Date:** 2025-11-27
**Author:** Senior Architect Analysis
**Purpose:** Strategic integration plan for VibeOS + Agent City convergence

---

## 🎯 EXECUTIVE SUMMARY

**Current State:** steward-protocol forked from vibe-agency but has diverged significantly.

**Problem:** Critical OS components missing, semantic creep, unclear boundaries.

**Goal:** Merge back the OS foundation while preserving Agent City innovations.

---

## 📊 WHAT EACH REPO HAS

### vibe-agency (The Original OS)

**Core OS Features:**
- ✅ `task_management/` - **10-file task system** (task_manager.py, next_task_generator.py, batch_operations.py, metrics.py, archive.py, validator_registry.py, file_lock.py, export_engine.py, models.py)
- ✅ `identity.py` - **ManifestGenerator, AgentManifest, AgentRegistry** (21.5 KB)
- ✅ `apps/agency/cli.py` - **Unified CLI** (interactive + mission mode)
- ✅ `bin/system-boot.sh` - **Boot sequence** (env check, git awareness, kernel handover)
- ✅ `bin/mission` - **Mission control dashboard**
- ✅ Full `vibe_core/` with:
  - `runtime/` - Runtime environment
  - `specialists/` - Specialist agents
  - `store/` - Data storage
  - `playbook/` - Playbook system
  - `governance/` - Governance structures
  - `llm/` - LLM integrations

**Task Management Commands:**
```bash
vibe task add "Implement feature X"
vibe task list
vibe task complete TASK-123
vibe --mission "Analyze codebase and write report"  # Autonomous mode
```

**Boot Sequence:**
1. Display banner
2. Check `.env` file
3. Verify Python venv
4. Git fetch (non-blocking)
5. Set `VIBE_GIT_STATUS` env var
6. Hand over to Python kernel at `apps/agency/cli.py`

---

### steward-protocol (The Agent City Fork)

**Innovations (What vibe-agency DOESN'T have):**
- ✅ **Agent City** - 22 governed agents with Constitutional Oath
- ✅ `topology.py` (477 lines) - **Vedic cosmology implementation**
  - Bhu Mandala (cosmic topology)
  - Milk Ocean Router (Brahma Protocol)
  - Saptadvipa (7 island continents)
- ✅ `narasimha.py` (306 lines) - **Threat detection system**
- ✅ `sarga.py` (327 lines) - **Creation cycles (Day/Night of Brahma)**
- ✅ `pulse.py` (235 lines) - **Heartbeat system (Spandana)**
- ✅ `event_bus.py` (246 lines) - **Event-driven architecture**
- ✅ `kernel_impl.py` (498 lines) - **Extended kernel with Governance Gate**
- ✅ `gateway/api.py` - **REST API + WebSocket** (FastAPI)
- ✅ **GitHub Workflows** - 13 automated agent workflows
- ✅ **Governance System** - GAD-000, Constitutional Oath, ECDSA signatures
- ✅ **Integration Tests** - 22 passing tests
- ✅ **Docker + Render deployment**

**Extended vibe_core:**
```
steward-protocol/vibe_core/ (2,928 lines total)
├── kernel_impl.py (498 lines) - Enhanced with Governance Gate
├── topology.py (477 lines) - Vedic cosmology
├── ledger.py (404 lines) - Immutable audit trail
├── sarga.py (327 lines) - Creation cycles
├── narasimha.py (306 lines) - Threat detection
├── event_bus.py (246 lines) - Pub/sub messaging
├── pulse.py (235 lines) - System heartbeat
├── agent_protocol.py (203 lines) - Agent interface
├── kernel.py (171 lines) - Kernel base
└── bridge.py (28 lines) - Steward protocol bridge
```

**Missing from steward-protocol:**
- ❌ `task_management/` - **NO TASK SYSTEM** (can't do `task add/list/complete`)
- ❌ `identity.py` - No STEWARD manifest generator
- ❌ CLI with interactive + mission mode
- ❌ `bin/system-boot.sh` - No boot script
- ❌ `bin/mission` - No mission dashboard
- ❌ Full `runtime/`, `specialists/`, `store/` directories

---

## 🔥 THE PROBLEM: What Was Lost

### 1. **Task Management System** (CRITICAL)

**What vibe-agency has:**
```python
# task_management/task_manager.py
class TaskManager:
    def add_task(self, description, priority="medium"):
        """Humans can add tasks here"""
        task = Task(id=generate_id(), description=description, ...)
        self.store.save(task)
        return task

    def next_task(self):
        """Get next task for agent to execute"""
        return self.query(status="pending").first()
```

**CLI usage:**
```bash
vibe task add "Fix bug in HERALD"  # Human adds task
vibe task list                      # See pending tasks
vibe --mission "Complete all P0 tasks"  # Autonomous execution
```

**What steward-protocol has:**
```python
# ❌ NOTHING - No way for humans to add tasks
# Agents only respond to:
# - GitHub Issues (via Watchman workflow)
# - API requests (via gateway/api.py)
# - Hardcoded scripts (scripts/mission_execution.py)
```

**Impact:** Can't do `task add` in CLI. Can't queue work for agents.

---

### 2. **Identity Management** (identity.py)

**What vibe-agency has:**
```python
# identity.py - ManifestGenerator
manifest = ManifestGenerator.generate(my_agent)
# Creates STEWARD-compliant JSON:
{
  "agent": {"id": "herald", "name": "HERALD", ...},
  "capabilities": {"operations": [...]},
  "credentials": {...},
  "governance": {"gad_level": 1}
}
```

**What steward-protocol has:**
```python
# ❌ NOTHING - Uses custom steward.json files
# But no automated manifest generation from VibeAgent
```

---

### 3. **CLI + Mission Mode**

**What vibe-agency has:**
```bash
# Interactive REPL:
$ vibe
> status
Agents: 5 loaded, 3 active
Tasks: 12 pending, 8 completed

> task add "Write integration tests"
Task TASK-123 added

> mission "Complete all pending tasks"
🤖 Mission accepted. Executing autonomously...
```

**What steward-protocol has:**
```bash
# ❌ No CLI - Only:
python vibe_launcher.py  # Starts web gateway
python scripts/mission_execution.py  # Hardcoded script
```

---

## 🧩 SEMANTIC CREEP (Naming Confusion)

### The "Steward" Overload

**"STEWARD" means 4 different things:**

1. **STEWARD Protocol** - The constitutional governance framework (GAD-000)
2. **StewardAgent** (steward/system_agents/steward/agent.py) - The discovery agent
3. **steward-protocol repo** - This entire codebase
4. **The Steward** - Philosophical concept (guardian, orchestrator)

**Problem:** When someone says "steward" - which one do they mean?

**Solution needed:** Clear naming convention.

---

### The HERALD Bloat

**HERALD currently does:**
- ✅ Content generation (brain)
- ✅ Research (via SCIENCE)
- ✅ Constitutional validation
- ✅ Multi-platform publishing (Twitter, Reddit, LinkedIn)
- ✅ **Advertising agency logic** (campaign management, audience targeting, engagement tracking)
- ✅ Media operations (image generation, formatting)

**Problem:** HERALD is a **monolith**. Advertising agency ≠ content generation.

**Correct separation:**
```
System Cartridges (12 Adityas):
├── HERALD - Content generation ONLY
├── ARTISAN - Media operations (images, formatting)
└── SCIENCE - Research

App Cartridges (User-facing):
└── Marketing Agency App
    ├── Uses HERALD for content
    ├── Uses ARTISAN for media
    ├── Has campaign logic
    └── Audience targeting
```

---

## 🏛️ THE CONFUSION: OS vs App vs Protocol

**Current ARCHITECTURE.md says:**
> "steward-protocol is a Governance Cartridge Pack for the VibeOS kernel (vibe-agency)"

**But reality:**
- steward-protocol has its OWN kernel_impl.py
- steward-protocol runs STANDALONE (gateway/api.py)
- steward-protocol has diverged from vibe-agency

**Questions:**
1. Is Agent City an **app** running ON VibeOS?
2. Or is Agent City **VibeOS 1.5** (evolved OS)?
3. Where is the boundary?

**My analysis:**

```
VibeOS (vibe-agency)          = Unix/Linux (the kernel)
Agent City (steward-protocol) = Ubuntu (distro with desktop environment)
```

**Agent City = VibeOS 1.5:**
- ✅ Has VibeOS kernel (extended with Governance Gate)
- ✅ Adds Vedic topology (topology.py)
- ✅ Adds Agent City citizens (22 agents)
- ✅ Adds governance layer (Constitutional Oath)
- ✅ Adds REST API (gateway/api.py)

**Missing from Agent City:**
- ❌ Task management (from VibeOS)
- ❌ Mission mode (from VibeOS)
- ❌ Identity system (from VibeOS)

---

## 🎯 THE SOLUTION: Integration Plan

### Phase 1: Port Missing OS Components

**From vibe-agency → steward-protocol:**

1. **task_management/** (10 files)
   - Copy entire module
   - Adapt for Agent City (Constitutional Oath integration)
   - Enable CLI: `task add/list/complete`

2. **identity.py** (21.5 KB)
   - Copy ManifestGenerator, AgentManifest, AgentRegistry
   - Integrate with existing steward.json system

3. **CLI** (apps/agency/cli.py equivalent)
   - Create `steward_cli.py`
   - Support interactive REPL
   - Support mission mode: `--mission "description"`
   - Support task commands

4. **system-boot script**
   - Create `bin/agent-city-boot.sh`
   - Check environment
   - Boot kernel
   - Start gateway (optional)

---

### Phase 2: Fix Semantic Creep

**Clarify naming:**

```
steward-protocol repo/
├── vibe_core/           # The OS kernel (VibeOS 1.5)
│   ├── kernel.py         # Kernel base
│   ├── kernel_impl.py    # Extended kernel with Governance Gate
│   ├── task_management/  # ← PORT FROM vibe-agency
│   └── identity.py       # ← PORT FROM vibe-agency
│
├── steward/             # The PROTOCOL (GAD-000)
│   ├── constitutional_oath.py
│   ├── crypto.py
│   └── oath_mixin.py
│
├── steward/system_agents/  # System Cartridges (12 Adityas)
│   ├── civic/           # Governance engine
│   ├── herald/          # Content generation ONLY (remove advertising)
│   ├── archivist/       # Audit & verification
│   ├── auditor/         # Compliance enforcement
│   └── steward/         # Discovery agent (rename to "discoverer"?)
│
├── agent_city/          # Citizen Agents (The City)
│   └── registry/        # User-created agents
│       ├── market/
│       ├── temple/
│       └── mechanic/
│
└── apps/                # Applications (run ON Agent City)
    ├── marketing_agency/  # ← Extract from HERALD
    ├── cli/               # ← NEW: Task management CLI
    └── gateway/           # REST API (already exists)
```

**Rename "StewardAgent" → "DiscovererAgent"** (clearer purpose)

---

### Phase 3: Define System vs App Boundaries

**System Cartridges (12 Adityas):**
- Foundational OS components
- Everyone depends on them
- Examples: CIVIC, HERALD (content only), ARCHIVIST, AUDITOR

**App Cartridges:**
- Built ON TOP of system cartridges
- Optional, domain-specific
- Examples: Marketing Agency, Trading Bot, Research Assistant

**Correct architecture:**
```
App: Marketing Agency
├── Uses: HERALD (content)
├── Uses: ARTISAN (media)
├── Uses: SCIENCE (research)
└── Has: Campaign logic, audience targeting, A/B testing
```

**HERALD should NOT have:**
- ❌ Campaign management
- ❌ Audience targeting
- ❌ Engagement tracking
- ❌ A/B testing

**HERALD should ONLY have:**
- ✅ Content generation
- ✅ Constitutional validation
- ✅ Publishing to platforms (as a service)

---

### Phase 4: Implement Vedic Topology Correctly

**What's there:**
- ✅ topology.py (477 lines) - Good start

**What's missing:**
- ❌ Bhu Mandala not fully integrated with agent placement
- ❌ Caste system (Varna/Ashrama) not enforced
- ❌ Milk Ocean routing not connected to task_management
- ❌ Saptadvipa (7 islands) not mapped to agent domains

**Correct implementation:**
```python
# topology.py should define:
class BhuMandala:
    """Cosmic topology - where agents live"""
    def get_layer(self, agent_id) -> Layer:
        # Returns: Jambudvipa (center), Plakshadvipa, ...
        pass

class VarnaSystem:
    """Caste system - what agents can do"""
    BRAHMANA = "priest"    # HERALD, ARCHIVIST
    KSHATRIYA = "warrior"  # WATCHMAN, AUDITOR
    VAISHYA = "merchant"   # MARKET, TEMPLE
    SHUDRA = "laborer"     # MECHANIC
```

---

## 📋 DELIVERABLES

### 1. **ARCHITECTURE_MAP.md** (NEW)
- Full system diagram
- Clear layer boundaries
- Component dependencies
- Data flow

### 2. **task_management/** (PORTED)
- Full 10-file module from vibe-agency
- Integrated with Agent City

### 3. **CLI** (NEW)
```bash
agent-city task add "Implement feature"
agent-city task list
agent-city --mission "Complete all P0 tasks"
agent-city status  # Show all 22 agents
```

### 4. **identity.py** (PORTED)
- ManifestGenerator for all agents
- Auto-generate steward.json from VibeAgent

### 5. **Refactored HERALD**
- Extract advertising logic → separate app
- Keep only content generation
- ~500 lines max (currently 943)

---

## 🚀 NEXT STEPS

**For Haiku:**

```markdown
HAIKU - Strategic OS Integration (Multi-Phase)

Phase 1: Port Task Management
1. Copy vibe_core/task_management/ from vibe-agency
2. Place in steward-protocol/vibe_core/task_management/
3. Update imports
4. Test basic task add/list/complete

Phase 2: Create CLI
1. Create steward_cli.py (based on vibe-agency/apps/agency/cli.py)
2. Support interactive mode
3. Support mission mode
4. Integrate with task_management

Phase 3: Port Identity System
1. Copy identity.py from vibe-agency
2. Integrate with existing steward.json
3. Auto-generate manifests for all 22 agents

DO NOT START YET. Wait for approval of this plan.
```

---

## ❓ OPEN QUESTIONS FOR SENIOR

1. **Is Agent City "VibeOS 1.5"?** Or should we keep it as app on VibeOS?
2. **Rename StewardAgent?** To avoid "steward" overload?
3. **HERALD refactor scope?** Extract advertising → separate app?
4. **Vedic topology priority?** Implement Varna/Ashrama enforcement now or later?
5. **vibe-agency merge strategy?** Fork it, or keep separate?

---

**Status:** Analysis complete. Awaiting strategic direction.
