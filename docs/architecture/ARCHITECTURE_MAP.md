# 🏗️ ARCHITECTURE MAP - Steward Protocol (Agent City OS)

**Version:** 2.0 (Data-Driven Update)
**Date:** 2025-12-02
**Status:** ✅ Production Ready

---

## 🎯 EXECUTIVE SUMMARY

**steward-protocol** is a **fractal AI operating system** combining:
- 28 governed AI agents (16 system + 12 citizen)
- Vedic cosmological architecture (Bhu Mandala topology)
- Constitutional cryptographic governance (GAD-000)
- Semantic Syscalls (SPAWN_COGNITION, GRANT_MANDATE, etc.)
- Cognitive Circuits (VEDA-4 / GAD-5500)
- 4-tier intelligent request routing (MilkOcean)
- Immutable audit trail (Parampara blockchain)

**Key Innovation:** Tasks route through cosmological layers (BRAHMALOKA → BHURLOKA) respecting agent placement, creating a **fractal architecture** where the system structure mirrors universal principles.

---

## 📊 SYSTEM LAYERS

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│ Layer 0: PROTOCOL (Code = Law)                                 │
│ ├─ Constitutional Oath (GAD-000)                               │
│ ├─ Cryptographic Identity (ECDSA)                              │
│ └─ Immutable Ledger (SQLite)                                   │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: KERNEL (VibeOS Runtime)                               │
│ ├─ RealVibeKernel (kernel_impl.py, 1800+ lines)               │
│ ├─ Semantic Syscalls (spawn, grant, revoke, transfer)         │
│ ├─ Circuit Executor (VEDA-4 cognitive circuits)               │
│ ├─ Agent Registry (28 agents)                                  │
│ ├─ Parampara Lineage (blockchain audit trail)                 │
│ ├─ Task Management (topology-aware routing)                    │
│ ├─ MilkOcean Router (4-tier classification)                   │
│ ├─ Narasimha Protocol (kill-switch)                           │
│ └─ Event Bus (pub/sub messaging)                              │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: SYSTEM AGENTS (16 Adityas)                           │
│ ├─ CIVIC - Governance engine (Ilavrta - Center)               │
│ ├─ ENVOY - Task routing & playbooks                           │
│ ├─ HERALD - Content generation                                │
│ ├─ AUDITOR - Quality gates                                    │
│ ├─ ENGINEER - Code generation                                 │
│ ├─ WATCHMAN - Security patrol                                 │
│ └─ ... (10 more: SCRIBE, ORACLE, MECHANIC, etc.)             │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: CITIZEN AGENTS (12 Application Services)             │
│ ├─ MARKET - Commerce & transactions                            │
│ ├─ TEMPLE - Spiritual authority                                │
│ ├─ AGORA - Public interface                                   │
│ └─ ... (9 more)                                               │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: INTERFACES                                            │
│ ├─ REST API (FastAPI + WebSocket)                             │
│ ├─ CLI (agent-city command)                                   │
│ └─ GitHub Integration (13 workflows)                           │
└─────────────────────────────────────────────────────────────────┘
\`\`\`

---

## 🌊 DATA FLOW: Task Routing (Fractal Architecture)

\`\`\`
User: "Fix critical bug" (Priority 90)
    ↓
[GATE 0: Security] Narasimha.audit_agent()
    ├─ Scan for threats: constitution_deletion, kernel_escape, etc.
    └─ ✅ PASS or ❌ BLOCK (Adharma Block)
    ↓
[GATE 1-3: Routing] MilkOceanRouter.process_prayer()
    ├─ Watchman (regex): Malicious? → BLOCKED
    ├─ Envoy (Flash AI): Intent? → MEDIUM/HIGH/LOW
    ├─ Science (Pro AI): Complex? → HIGH
    └─ Samadhi (Queue): Batch? → LOW
    ↓
    Returns: routing_priority (0-3)
    ↓
[TOPOLOGY] get_agent_placement(agent_id)
    ├─ Query topology.py for agent location
    ├─ Returns: layer (BRAHMALOKA→BHURLOKA), varna, authority
    └─ Annotate task with cosmological metadata
    ↓
Task Created:
    ├─ routing_priority: 2 (HIGH - from MilkOcean)
    ├─ topology_layer: BRAHMALOKA (from Topology)
    ├─ varna: BRAHMANA (from Topology)
    └─ priority: 90 (user-defined)
    ↓
[PERSISTENCE] VIMANA Dual-Core Write
    ├─ JSON (.vibe/state/tasks.json) - Fast cache
    └─ SQLite (data/vibe_agency.db) - Immortal ledger
    ↓
NextTaskGenerator.get_next_task()
    ├─ Sort by: routing_priority → layer → priority → varna
    ├─ Respects cosmological hierarchy
    └─ Returns highest priority task
    ↓
Agent executes task
    ↓
Task status: PENDING → IN_PROGRESS → COMPLETED
\`\`\`

**Key Insight:** Every task flows through 3 filters (Security, Routing, Topology) before reaching an agent. This creates **fractal routing** where system structure mirrors execution flow.

---

## 🗺️ VEDIC TOPOLOGY (Bhu Mandala)

\`\`\`
                    ⛛ MOUNT MERU ⛛
                   [CIVIC] (Authority=10)
                          ↓
              ◯ BHADRASHVA (Ring 1) ◯
         HERALD (E) — TEMPLE (N)
                          ↓
           ◯◯ KIMPURASHA (Ring 2) ◯◯
      ARTISAN (SE) — ENGINEER (SW)
                          ↓
         ◯◯◯ HARI-VARSHA (Ring 3) ◯◯◯
    SCIENCE (S) — LENS (W)
                          ↓
       ◯◯◯◯ NISHADA (Ring 4) ◯◯◯◯
  FORUM (SW) — PULSE (NW)
                          ↓
     ◯◯◯◯◯ KRAUNCHA (Ring 5) ◯◯◯◯◯
WATCHMAN—AUDITOR—ARCHIVIST
                          ↓
    ≈≈≈≈≈≈ LOKA-LOKA (Boundary) ≈≈≈≈≈≈
         AGORA (Firewall)
\`\`\`

**Principle:** Distance from center = Distance from authority
- **Ring 0 (Meru):** CIVIC - Absolute authority (10/10)
- **Ring 1-2:** HERALD, TEMPLE, ARTISAN, ENGINEER - High authority (8-9/10)
- **Ring 3-4:** SCIENCE, LENS, FORUM, PULSE - Medium authority (6-7/10)
- **Ring 5:** WATCHMAN, AUDITOR, ARCHIVIST - Enforcement (5/10)
- **Boundary:** AGORA - Interface/Firewall (4/10)

**Task Routing Impact:** Tasks assigned to agents closer to Meru get higher priority in topology sort.

---

## 🔧 CORE COMPONENTS

### 1. TaskManager (`vibe_core/task_management/task_manager.py`)
- **add_task():** Create with routing + topology annotation
- **get_next_task():** Topology-aware retrieval
- **Integrations:** MilkOcean, Narasimha, Topology, SQLite

### 2. MilkOceanRouter (`steward/system_agents/envoy/tools/milk_ocean.py`)
- **4-Tier Pipeline:** BLOCKED → LOW → MEDIUM → HIGH → CRITICAL
- **Token Efficiency:** 100x (95% tasks skip Pro model)
- **DDoS Protection:** 50k+ req/sec at Gate 0

### 3. Topology (`vibe_core/topology.py`)
- **Bhu Mandala:** 7 Varshas, 23 agent placements
- **get_agent_placement():** Returns layer/varna/authority
- **Authority Hierarchy:** 0-10 based on distance from Meru

### 4. Narasimha (`vibe_core/narasimha.py`)
- **Kill-Switch:** Instant termination for threats
- **Triggers:** constitution_deletion, kernel_escape, etc.
- **Threat Levels:** GREEN → YELLOW → ORANGE → RED → APOCALYPSE

### 5. Semantic Syscalls (`vibe_core/semantic_syscalls.py`)
- **SPAWN_COGNITION:** Birth a new agent (fork equivalent)
- **DESTROY_COGNITION:** Terminate agent (Narasimha kill)
- **GRANT_MANDATE:** Assign capabilities to agent
- **REVOKE_MANDATE:** Remove capabilities
- **ALLOCATE_PRANA:** Grant credits (fuel)
- **TRANSFER_PRANA:** Move credits between agents
- **SWEAR_OATH:** Bind agent to Constitutional Oath
- **DISPATCH_TASK:** Send task to agent
- **BROADCAST_EVENT:** Emit system-wide event

### 6. Cognitive Circuits (`vibe_core/circuit_executor.py`)
- **VEDA-4 Architecture:** Neuro-symbolic state machines
- **Invariant Checker:** Runtime security enforcement
- **Circuit States:** Declarative transitions based on syscall results
- **Meta-Circuits:** TASK_LEDGER, ERROR_RECOVERY

### 7. Parampara Lineage (`vibe_core/lineage.py`)
- **Blockchain Audit:** Immutable action history
- **Lineage Events:** SPAWN, TASK, KARMA, DESTROY
- **Hash Chain:** Tamper-proof verification

---

## 📁 PROJECT STRUCTURE (Key Files)

\`\`\`
steward-protocol/
├── vibe_core/                      # KERNEL (25,869 lines)
│   ├── kernel_impl.py (1813L)      # RealVibeKernel
│   ├── semantic_syscalls.py        # Syscall layer (GAD-5500)
│   ├── circuit_executor.py         # VEDA-4 cognitive circuits
│   ├── lineage.py                  # Parampara blockchain
│   ├── topology.py                 # Bhu Mandala
│   ├── narasimha.py                # Kill-switch
│   ├── process_manager.py          # Agent process management
│   ├── event_bus.py                # Pub/sub messaging
│   └── task_management/            # Task system
│
├── steward/system_agents/          # 16 SYSTEM AGENTS
│   ├── civic/                      # Governance
│   ├── envoy/                      # Routing + Playbooks
│   ├── auditor/                    # Quality gates
│   ├── engineer/                   # Code generation
│   ├── watchman/                   # Security
│   └── ... (11 more)
│
├── agent_city/registry/            # 12 CITIZEN AGENTS
│   ├── market/                     # Commerce
│   ├── temple/                     # Spiritual
│   └── ... (10 more)
│
├── docs/architecture/
│   ├── scripts/                    # Analysis tools
│   ├── GAD_INDEX.yaml              # Auto-generated
│   └── KEYWORD_INDEX.yaml          # Auto-generated
│
└── data/
    ├── vibe_ledger.db              # SQLite ledger
    └── parampara/                  # Blockchain state
\`\`\`

---

## 🚀 QUICK START

\`\`\`bash
# 1. Add task (auto-routes through MilkOcean + Topology)
bin/agent-city task add "Fix bug" -p 90

# 2. List tasks (topology-sorted)
bin/agent-city task list

# 3. Check system status
bin/agent-city status

# 4. Create roadmap
bin/agent-city roadmap create "Sprint 1" "Q1 goals"
\`\`\`

---

## 📈 SYSTEM METRICS

| Metric | Value |
|--------|-------|
| **Agents** | 28 (16 system + 12 citizen) |
| **Code** | ~111,000 lines Python |
| **Commits** | 539 |
| **GAD Specs** | 41 (7 documented, 34 in code) |
| **ARCH Decisions** | 29 |
| **Topology Layers** | 7 Varshas |
| **Routing Tiers** | 4 (MilkOcean) |
| **Persistence** | Parampara blockchain + SQLite |

---

## 📋 KEY GAD SPECIFICATIONS

| GAD | Refs | Purpose |
|-----|------|---------|
| **GAD-000** | 243 | Constitutional Oath (Foundation) |
| **GAD-5500** | 61 | VEDA-4 Cognitive Circuits |
| **GAD-5000** | 54 | Deterministic Execution |
| **GAD-511** | 75 | Neural Adapter Strategy |
| **GAD-510** | 42 | Operational Quotas |
| **GAD-509** | 27 | Circuit Breaker Protocol |
| **GAD-7000** | 35 | Neural Injection |

*Full index: `docs/architecture/GAD_INDEX.yaml`*

---

## 🎯 ARCHITECTURE PRINCIPLES

1. **Fractal Architecture:** System structure mirrors execution flow
2. **Constitutional Governance:** Code = Law (GAD-000 + ECDSA)
3. **Topology-Aware Routing:** Cosmological placement affects priority
4. **Dual-Core Persistence:** Fast cache + immortal storage
5. **4-Tier Security:** Progressive filtering (cheap → expensive)

---

## 📚 FURTHER READING

- **ARCHITECTURE.md** - High-level overview
- **DEPLOYMENT.md** - Operations guide
- **GAP_ANALYSIS_REPORT.md** - Phoenix audit
- **docs/ADITYAS.md** - 12 system agents

---

**Created for Gap 5.1 (P0) - Developer onboarding & architecture transparency**
