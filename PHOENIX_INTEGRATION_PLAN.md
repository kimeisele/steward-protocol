# 🔥 PHOENIX PROTOCOL: Integration Plan

**Date:** 2025-11-27
**Mission:** Merge best of vibe-agency + steward-protocol
**Code Name:** REBIRTH

---

## 📊 THE AUDIT (What We Have)

### vibe-agency (The Original VibeOS)

**File Count:**
- `vibe_core/`: **88 Python files** (2,419 lines)
- `bin/`: **40 executables**
- `tests/`: **16 test directories**
- `docs/`: **29 doc directories**
- `workspaces/`: **8 active workspaces**

**Core Components:**
```
vibe-agency/
├── vibe_core/                # THE KERNEL (88 files)
│   ├── kernel.py             # 716 lines - Main kernel
│   ├── identity.py           # 625 lines - Manifest generator
│   ├── task_management/      # 10 files - Mission control
│   ├── runtime/              # Providers, safety guards
│   ├── llm/                  # LLM adapters
│   ├── playbook/             # Workflow engine
│   ├── specialists/          # Specialist agents
│   ├── store/                # Data persistence
│   ├── governance/           # Soul governance
│   └── tools/                # Tool registry
│
├── bin/                      # SYSTEM UTILITIES (40 files)
│   ├── system-boot.sh        # Boot sequence
│   ├── vibe                  # Main CLI wrapper
│   ├── mission               # Mission control dashboard
│   ├── vibe-shell            # Runtime execution
│   ├── vibe-knowledge        # Knowledge retrieval
│   ├── next-task.py          # Task generator
│   ├── vibe-test             # Test runner
│   └── vibe-check            # Code quality
│
├── apps/                     # CORE APPLICATIONS
│   ├── agency/               # The main CLI app
│   │   ├── cli.py            # Entry point (interactive + mission mode)
│   │   ├── prompts/          # System prompts
│   │   └── specialists/      # Planning, Coding, Testing agents
│   └── vibe-monitor/         # System monitor
│
├── workspaces/               # USER APPLICATIONS (8 workspaces)
│   ├── .workspace_index.yaml # Workspace registry
│   ├── prabhupad_os/         # CLI app (external client)
│   ├── temple_companion/     # Web app (external client)
│   ├── vibe_coding_framework/# Framework (internal)
│   ├── vibe_research_framework/# Research (internal)
│   └── agency_toolkit/       # Toolkit (internal)
│
└── docs/                     # DOCUMENTATION (29 directories)
    ├── architecture/
    ├── gad/                  # GAD protocols
    └── guides/
```

**Key Features:**
1. ✅ **Task Management System** (10-file module)
   - TaskManager, ActiveMission, Roadmap, Task models
   - `task add`, `task list`, `task complete` commands
   - Next task generator
   - Validation registry
   - Metrics & monitoring

2. ✅ **Workspace System**
   - Applications live in `workspaces/`
   - Each workspace has `project_manifest.json` + `artifacts/`
   - Registry: `.workspace_index.yaml`
   - Can be internal (agency) or external (client) projects

3. ✅ **CLI with Mission Mode**
   - Interactive REPL
   - Autonomous mission mode: `--mission "description"`
   - Tool registry (AddTaskTool, ListTasksTool, CompleteTaskTool)

4. ✅ **System Boot**
   - `system-boot.sh` - Environment check, git awareness, kernel handover
   - Idempotent, fail-fast
   - Hands over to Python kernel

5. ✅ **Identity System**
   - ManifestGenerator (625 lines)
   - AgentManifest, AgentRegistry
   - STEWARD Protocol Level 1 compliance

6. ✅ **Runtime System**
   - Providers (Google, Local, Chain)
   - Tool safety guards
   - Oracle (kernel introspection)

---

### steward-protocol (Agent City)

**File Count:**
- `vibe_core/`: **16 Python files** (2,928 lines)
- `steward/system_agents/`: **15 agents**
- `agent_city/registry/`: **7 citizen agents**
- `gateway/`: **1 file (FastAPI)**
- `tests/`: **19 test files**

**Core Components:**
```
steward-protocol/
├── vibe_core/                # EXTENDED KERNEL (16 files)
│   ├── kernel_impl.py        # 498 lines - Governance Gate
│   ├── topology.py           # 477 lines - Vedic cosmology
│   ├── ledger.py             # 404 lines - Immutable audit trail
│   ├── sarga.py              # 327 lines - Creation cycles
│   ├── narasimha.py          # 306 lines - Threat detection
│   ├── pulse.py              # 235 lines - System heartbeat
│   ├── event_bus.py          # 246 lines - Pub/sub messaging
│   └── agent_protocol.py     # 203 lines - Agent interface
│
├── steward/                  # THE PROTOCOL + SYSTEM AGENTS
│   ├── constitutional_oath.py# GAD-000 enforcement
│   ├── crypto.py             # ECDSA signatures
│   └── system_agents/        # 15 system agents (22 total with citizens)
│       ├── civic/            # 989 lines - Governance engine
│       ├── herald/           # 943 lines - Content + advertising (BLOAT!)
│       ├── archivist/        # Audit & verification
│       ├── auditor/          # Compliance enforcement
│       ├── steward/          # Discovery agent
│       ├── forum/            # 648 lines - Governance proposals
│       ├── envoy/            # Diplomatic interface
│       └── ...               # 8 more
│
├── agent_city/               # CITIZEN AGENTS (The City)
│   └── registry/
│       ├── market/
│       ├── temple/
│       ├── mechanic/
│       └── ...               # 7 total
│
├── gateway/                  # REST API
│   ├── api.py                # FastAPI + WebSocket
│   └── static/               # Frontend (optional)
│
├── .github/workflows/        # CI/CD (13 workflows)
│   ├── herald-approval.yml   # Human-in-the-loop
│   ├── watchman-patrol.yml   # GitHub issue triage
│   ├── multi-agent-federation.yml
│   └── ...
│
└── tests/                    # INTEGRATION TESTS
    ├── integration/          # 22 tests passing
    └── city_simulation.py    # Full city simulation
```

**Key Features:**
1. ✅ **Agent City** (22 governed agents)
   - Constitutional Oath (100% compliant)
   - ECDSA signatures
   - Governance Gate in kernel

2. ✅ **Vedic Topology**
   - topology.py (477 lines) - Bhu Mandala, Milk Ocean Router, Saptadvipa
   - narasimha.py (306 lines) - Threat detection
   - sarga.py (327 lines) - Day/Night of Brahma cycles

3. ✅ **Event-Driven Architecture**
   - pulse.py - System heartbeat (Spandana)
   - event_bus.py - Pub/sub messaging

4. ✅ **REST API Gateway**
   - FastAPI + WebSocket
   - Multi-platform support
   - Milk Ocean Router integration

5. ✅ **GitHub Integration**
   - 13 automated workflows
   - Issue triage (Watchman)
   - PR reviews (Auditor)
   - Multi-agent federation

6. ✅ **Integration Tests**
   - 22 tests passing
   - System boot verification
   - Agent discovery tests
   - Governance gate tests

---

## 🔥 THE GAP ANALYSIS

### Missing in steward-protocol (from vibe-agency):

| Component | Lines | Impact | Priority |
|-----------|-------|--------|----------|
| **task_management/** | ~5,000 | ❌ No way to add tasks via CLI | **P0** |
| **identity.py** | 625 | ❌ No manifest generator | **P0** |
| **CLI + Mission Mode** | ~1,500 | ❌ No interactive REPL | **P0** |
| **bin/system-boot.sh** | ~100 | ❌ No boot script | **P1** |
| **workspaces/** | N/A | ❌ No app isolation pattern | **P1** |
| **runtime/providers/** | ~2,000 | ⚠️ Has basic provider, missing advanced | **P2** |
| **llm/** adapters | ~1,500 | ⚠️ Has basic LLM, missing adapters | **P2** |
| **playbook/** engine | ~3,000 | ⚠️ Has basic playbook, missing full engine | **P2** |
| **specialists/** | ~2,000 | ❌ No specialist agent pattern | **P2** |
| **store/** | ~1,000 | ❌ No data persistence layer | **P2** |
| **governance/** (soul) | ~800 | ⚠️ Has Constitutional Oath, missing InvariantChecker | **P2** |
| **tools/** (40+ tools) | ~5,000 | ⚠️ Has some tools, missing most | **P3** |

**Total missing:** ~22,000 lines of code (~75% of vibe-agency functionality)

### Missing in vibe-agency (from steward-protocol):

| Component | Lines | Impact | Priority |
|-----------|-------|--------|----------|
| **topology.py** | 477 | ❌ No Vedic cosmology | **P1** |
| **Agent City (22 agents)** | ~8,000 | ❌ No governed agent society | **P0** |
| **Constitutional Oath** | ~500 | ❌ No cryptographic governance | **P0** |
| **gateway/api.py** | ~600 | ❌ No REST API | **P1** |
| **pulse.py** | 235 | ❌ No heartbeat system | **P2** |
| **event_bus.py** | 246 | ❌ No pub/sub | **P2** |
| **narasimha.py** | 306 | ❌ No threat detection | **P2** |
| **sarga.py** | 327 | ❌ No creation cycles | **P2** |
| **GitHub workflows** | N/A | ❌ No CI/CD | **P2** |
| **Integration tests** | ~2,000 | ❌ No system-level tests | **P1** |

**Total missing:** ~12,500 lines of code (~30% of steward-protocol innovations)

---

## 🎯 THE INTEGRATION STRATEGY

### Phase 0: Preparation (DONE ✅)
- [x] Clone vibe-agency locally
- [x] Analyze both codebases
- [x] Document gaps
- [x] Create integration plan

### Phase 1: Foundation (CRITICAL - Week 1)

**Goal:** Get task management working in steward-protocol

**Tasks:**
1. **Port task_management/ module**
   ```bash
   cp -r vibe-agency/vibe_core/task_management/ steward-protocol/vibe_core/
   ```
   - Adapt imports
   - Test with pytest
   - Integrate with kernel

2. **Port identity.py**
   ```bash
   cp vibe-agency/vibe_core/identity.py steward-protocol/vibe_core/
   ```
   - Integrate with existing steward.json system
   - Generate manifests for all 22 agents

3. **Create CLI**
   ```bash
   cp vibe-agency/apps/agency/cli.py steward-protocol/apps/cli/
   ```
   - Adapt for Agent City
   - Add task commands
   - Support mission mode

4. **Port system-boot.sh**
   ```bash
   cp vibe-agency/bin/system-boot.sh steward-protocol/bin/
   ```
   - Adapt paths
   - Boot gateway (optional)

**Success Criteria:**
```bash
# User can do:
agent-city task add "Implement feature X"
agent-city task list
agent-city --mission "Complete all P0 tasks"
agent-city status  # Shows 22 agents
```

**Files Changed:** ~20
**Lines Added:** ~7,000
**Risk:** Medium (task_management has dependencies on store/)

---

### Phase 2: Unification (Week 2-3)

**Goal:** Merge remaining OS components

**Tasks:**
1. **Port runtime/ system**
   - Providers (Google, Chain, Local)
   - Tool safety guards
   - Oracle

2. **Port playbook/ engine**
   - Workflow definitions
   - Task templates
   - Execution engine

3. **Port specialists/**
   - Planning, Coding, Testing agents
   - Integrate with Agent City

4. **Port store/ layer**
   - Data persistence
   - SQLite shadow mode

5. **Merge governance/**
   - InvariantChecker from vibe-agency
   - Constitutional Oath from steward-protocol
   - Create unified governance system

**Success Criteria:**
- All vibe-agency features work in steward-protocol
- All steward-protocol features preserved
- No regressions in tests

**Files Changed:** ~50
**Lines Added:** ~15,000
**Risk:** High (many dependencies)

---

### Phase 3: Separation of Concerns (Week 4)

**Goal:** Fix semantic creep & bloat

**Tasks:**
1. **Refactor HERALD**
   - Extract advertising → `apps/marketing_agency/`
   - Keep only content generation
   - Reduce from 943 → ~400 lines

2. **Rename StewardAgent → DiscovererAgent**
   - Avoid "steward" overload
   - Update all references

3. **Define 12 Adityas (System Cartridges)**
   ```
   System Cartridges (OS-level):
   ├── CIVIC - Governance engine
   ├── HERALD - Content generation (ONLY)
   ├── ARCHIVIST - Audit & verification
   ├── AUDITOR - Compliance enforcement
   ├── DISCOVERER - Agent discovery (renamed from STEWARD)
   ├── WATCHMAN - Security patrol
   ├── ENVOY - Diplomatic interface
   ├── FORUM - Governance proposals
   ├── ENGINEER - Code operations
   ├── ORACLE - Knowledge retrieval
   ├── SCIENCE - Research operations
   └── ARTISAN - Media operations
   ```

4. **Move apps to workspaces/**
   ```bash
   mkdir -p steward-protocol/workspaces/
   mv apps/marketing_agency/ workspaces/
   ```

**Success Criteria:**
- Clear boundary: System vs App
- No monoliths (all agents < 500 lines)
- Semantic clarity (no naming conflicts)

**Files Changed:** ~30
**Lines Changed:** ~5,000
**Risk:** Medium (refactoring is always risky)

---

### Phase 4: Vedic Topology Integration (Week 5)

**Goal:** Implement fractal architecture

**Tasks:**
1. **Integrate topology.py with task_management**
   - Map agents to Bhu Mandala layers
   - Route tasks via Milk Ocean

2. **Implement Varna/Ashrama system**
   ```python
   class VarnaSystem:
       BRAHMANA = ["HERALD", "ARCHIVIST"]  # Priests
       KSHATRIYA = ["WATCHMAN", "AUDITOR"]  # Warriors
       VAISHYA = ["MARKET", "TEMPLE"]      # Merchants
       SHUDRA = ["MECHANIC"]                # Laborers
   ```

3. **Map workspaces to Saptadvipa**
   - Jambudvipa (center) = Core OS
   - Plakshadvipa = Internal apps
   - Shalmalidvipa = External clients
   - etc.

4. **Integrate sarga.py with task scheduling**
   - Day of Brahma = High activity
   - Night of Brahma = Maintenance mode

**Success Criteria:**
- Topology is functional, not decorative
- Task routing uses Milk Ocean
- Agent placement reflects Bhu Mandala

**Files Changed:** ~15
**Lines Added:** ~2,000
**Risk:** Low (mostly integration glue)

---

### Phase 5: Documentation & Polish (Week 6)

**Goal:** Make it production-ready

**Tasks:**
1. **Create ARCHITECTURE_MAP.md**
   - Full system diagram
   - Component dependencies
   - Data flow
   - Clear layer boundaries

2. **Update README.md**
   - Quick start guide
   - Architecture overview
   - CLI examples

3. **Write DEPLOYMENT.md**
   - Local setup
   - Docker deployment
   - Render deployment

4. **Create WORKSPACE_GUIDE.md**
   - How to create workspaces
   - Project manifest structure
   - Artifact conventions

5. **Write AGENT_DEVELOPMENT.md**
   - How to create agents
   - System vs App cartridges
   - Testing guidelines

**Success Criteria:**
- New developers can understand system in < 1 hour
- All major patterns documented
- Examples for common tasks

**Files Changed:** ~10 (all docs)
**Lines Added:** ~5,000
**Risk:** None

---

## 📋 DECISION MATRIX

### What Gets Merged?

| Component | Source | Decision | Reason |
|-----------|--------|----------|--------|
| **task_management/** | vibe-agency | ✅ MERGE | Critical missing feature |
| **identity.py** | vibe-agency | ✅ MERGE | Needed for manifest generation |
| **CLI** | vibe-agency | ✅ MERGE (adapt) | Interactive + mission mode essential |
| **system-boot.sh** | vibe-agency | ✅ MERGE | Clean boot sequence |
| **workspaces/** | vibe-agency | ✅ MERGE | App isolation pattern |
| **runtime/** | vibe-agency | ✅ MERGE | Advanced providers needed |
| **playbook/** | vibe-agency | ✅ MERGE | Workflow engine useful |
| **specialists/** | vibe-agency | ✅ MERGE | Planning/Coding/Testing agents |
| **store/** | vibe-agency | ✅ MERGE | Data persistence needed |
| **tools/** | vibe-agency | ✅ MERGE (selective) | Many useful tools |
| **topology.py** | steward-protocol | ✅ KEEP | Unique to Agent City |
| **Agent City (22 agents)** | steward-protocol | ✅ KEEP | Core innovation |
| **Constitutional Oath** | steward-protocol | ✅ KEEP | Governance framework |
| **gateway/api.py** | steward-protocol | ✅ KEEP | REST API essential |
| **pulse.py** | steward-protocol | ✅ KEEP | Heartbeat system |
| **event_bus.py** | steward-protocol | ✅ KEEP | Pub/sub essential |
| **GitHub workflows** | steward-protocol | ✅ KEEP | CI/CD automation |

### What Gets Refactored?

| Component | Current | Target | Reason |
|-----------|---------|--------|--------|
| **HERALD** | 943 lines (content + advertising) | ~400 lines (content only) | Separation of concerns |
| **CIVIC** | 989 lines (registry + economy + lifecycle) | 3 agents (~300 each) | Single responsibility |
| **FORUM** | 648 lines (proposals + voting) | 2 agents (~300 each) | Single responsibility |
| **StewardAgent** | "steward" (ambiguous) | "DiscovererAgent" | Naming clarity |

---

## 🚀 ROLLOUT PLAN

### Week 1: Foundation (P0)
**Owner:** Haiku
**Output:** CLI with task management
**Validation:** `agent-city task add` works

### Week 2-3: Unification (P1)
**Owner:** Haiku + Sonnet
**Output:** Full OS merged
**Validation:** All tests pass

### Week 4: Cleanup (P2)
**Owner:** Sonnet
**Output:** Refactored agents
**Validation:** No monoliths

### Week 5: Topology (P2)
**Owner:** Sonnet
**Output:** Vedic integration
**Validation:** Routing via Milk Ocean

### Week 6: Docs (P3)
**Owner:** Sonnet
**Output:** Complete documentation
**Validation:** New dev onboarding < 1hr

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Dependency Hell
**Problem:** task_management/ depends on store/, which depends on runtime/, etc.
**Mitigation:** Port in order (store → runtime → task_management)

### Risk 2: Import Conflicts
**Problem:** Both repos have vibe_core/ with different structures
**Mitigation:** Merge carefully, test after each component

### Risk 3: Regression
**Problem:** Breaking existing steward-protocol features
**Mitigation:** Run full test suite after each phase

### Risk 4: Scope Creep
**Problem:** Trying to merge everything at once
**Mitigation:** Strict phase boundaries, focus on P0 first

### Risk 5: Naming Collisions
**Problem:** Functions/classes with same names in both repos
**Mitigation:** Prefix with source (e.g., vibe_store, city_store)

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Complete:
```bash
✅ agent-city task add "Implement feature"
✅ agent-city task list
✅ agent-city --mission "Complete all P0 tasks"
✅ agent-city status
```

### Phase 2 Complete:
```bash
✅ All vibe-agency features work
✅ All steward-protocol features preserved
✅ Integration tests pass (22/22)
```

### Phase 3 Complete:
```bash
✅ No agent > 500 lines
✅ Clear system/app boundaries
✅ No semantic conflicts
```

### Phase 4 Complete:
```bash
✅ Tasks route via Milk Ocean
✅ Agents mapped to Bhu Mandala
✅ Varna system enforced
```

### Phase 5 Complete:
```bash
✅ ARCHITECTURE_MAP.md exists
✅ All major patterns documented
✅ New dev onboarding < 1 hour
```

---

## 🔥 THE PHOENIX VISION

**Before:**
- vibe-agency = OS without society
- steward-protocol = Society without full OS

**After:**
- steward-protocol = **VibeOS 1.5: Agent City Edition**
  - Full OS (task management, CLI, boot, workspaces)
  - Agent City (22 governed agents)
  - Vedic topology (Bhu Mandala, Milk Ocean, Sarga)
  - REST API + GitHub integration
  - Clean separation: System vs App
  - Fractal architecture (as above, so below)

**Result:**
- First fully governed AI operating system
- Agents can self-organize
- Humans can add tasks via CLI
- System scales fractally
- Code = Constitution
- The shady era is OVER

---

**Status:** Plan complete. Ready for Phase 1 execution.
**Next:** Get approval, then start porting task_management/
