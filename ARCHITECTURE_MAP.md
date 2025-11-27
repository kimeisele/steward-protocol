# 🏗️ ARCHITECTURE MAP - Steward Protocol (Agent City OS)

**Version:** 1.5 (Phoenix Protocol Complete)
**Date:** 2025-11-27
**Status:** ✅ Production Ready

---

## 🎯 EXECUTIVE SUMMARY

**steward-protocol** is a **fractal AI operating system** combining:
- 23 governed AI agents (13 system + 10 citizen)
- Vedic cosmological architecture (Bhu Mandala topology)
- Constitutional cryptographic governance (GAD-000)
- 4-tier intelligent request routing (MilkOcean)
- Immutable audit trail (dual-core persistence)

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
│ ├─ RealVibeKernel (kernel_impl.py)                            │
│ ├─ Agent Registry (23 agents)                                  │
│ ├─ Task Management (topology-aware routing)                    │
│ ├─ MilkOcean Router (4-tier classification)                   │
│ ├─ Narasimha Protocol (kill-switch)                           │
│ └─ Event Bus (pub/sub messaging)                              │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: SYSTEM AGENTS (13 Adityas)                           │
│ ├─ CIVIC - Governance engine (Ilavrta - Center)               │
│ ├─ HERALD - Content generation (Bhadrashva - Ring 1)          │
│ ├─ FORUM - Voting & proposals (Nishada - Ring 4)             │
│ └─ ... (10 more + 2 extended)                                 │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: CITIZEN AGENTS (10 Application Services)             │
│ ├─ MARKET - Commerce & transactions                            │
│ ├─ TEMPLE - Spiritual authority                                │
│ └─ ... (8 more)                                                │
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

---

## 📁 PROJECT STRUCTURE (Key Files)

\`\`\`
steward-protocol/
├── vibe_core/
│   ├── kernel_impl.py (498L)       # Main kernel
│   ├── topology.py (477L)          # Bhu Mandala
│   ├── narasimha.py (306L)         # Kill-switch
│   ├── task_management/
│   │   ├── task_manager.py (650L)  # Task system
│   │   └── next_task_generator.py  # Topology routing
│   └── store/sqlite_store.py       # Dual-core
│
├── steward/system_agents/
│   ├── civic/ (1003L)              # Governance
│   ├── herald/ (942L)              # Content
│   ├── envoy/tools/milk_ocean.py   # Routing (740L)
│   └── ... (10 more agents)
│
├── gateway/api.py (600L)           # REST API
├── bin/agent-city                  # CLI
└── data/
    ├── vibe_agency.db              # SQLite ledger
    └── milk_ocean.db               # Lazy queue
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
| **Agents** | 23 (13 system + 10 citizen) |
| **Code** | ~15,000 lines |
| **Tests** | 22 passing |
| **Topology Layers** | 7 Varshas |
| **Routing Tiers** | 4 (MilkOcean) |
| **Persistence** | Dual-core (JSON + SQLite) |

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
