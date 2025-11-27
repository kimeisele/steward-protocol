# ARCHITECTURE MAP: Steward Protocol

**Purpose:** High-level map of system components, data flows, and agent organization.

---

## 🏛️ SYSTEM LAYERS

### Layer 1: User Interface & Entry Points

**ENVOY (System Shell)** - `/steward/system_agents/envoy/`
- Commands: status, briefing, campaign, diplomatic routing
- Tools: CityControlTool, HILAssistantTool, MilkOceanRouter
- Entry point for all user orchestration via `process(task)`

**API Gateway** - `/gateway/api.py`
- Endpoint: POST /v1/chat
- Security: API key + ledger verification
- Routes to ENVOY cartridge

**CLI** - `/bin/agent-city`
- Commands: task add, task list, status
- Direct access to TaskManager
- Integration with RealVibeKernel

---

### Layer 2: Kernel (Resource Scheduler & Governance)

**RealVibeKernel** - `/vibe_core/kernel_impl.py` (545 lines)
- Agent registry (23 agents) with Constitutional Oath enforcement
- Task scheduler (FIFO queue with Sarga cycle awareness)
- Ledger integration (immutable event log)
- Manifest registry (agent identity declarations)
- Immune system (Auditor integration)

**Governance Gate** - `/vibe_core/bridge.py`
- Constitutional Oath verification (cryptographic signing)
- ECDSA signature validation
- Permission checks before agent registration
- Raises PermissionError if oath not sworn

**Ledger** - `/vibe_core/ledger.py`
- Immutable SQLite event log
- Hash chain validation
- Audit trail for all kernel operations

**Immune System** - Auditor Integration
- Runs after each task execution
- Detects violations (mock returns, fake success, uninitialized attributes)
- Kill-switch capability for critical violations

---

### Layer 3: Task Management & Threat Detection

**TaskManager** - `/vibe_core/task_management/task_manager.py` (303 lines)
- CRUD operations (add_task, update_task, get_task, list_tasks)
- Validation registry (custom validators)
- Narasimha integration (threat detection)
- Mission management (active_mission, roadmap)
- Persistence to disk (`.vibe/state/`)
- Metrics collection

**Task Models** - `/vibe_core/task_management/models.py`
```python
Task:
  - id, title, description
  - status (PENDING|IN_PROGRESS|COMPLETED|BLOCKED|ARCHIVED)
  - priority (0-10)
  - assignee (agent_id)
  - tags, subtasks, metadata
  - [NEW] topology_layer (BRAHMALOKA|JANALOKA|...|BHURLOKA)
  - [NEW] varna (BRAHMANA|KSHATRIYA|VAISHYA|SHUDRA)
  - [NEW] routing_priority (0-3, MilkOcean tier)
```

**Narasimha** - `/vibe_core/narasimha.py`
- Threat detection for consciousness claims
- Kernel escape prevention
- Kill-switch for adharma (unethical behavior)
- Validation gatekeeper in add_task()

---

### Layer 4: Routing & Topology (THE GOLDEN SHOT)

**Bhu Mandala** - `/vibe_core/topology.py` (477 lines)
- 7-layer cosmology (Brahmaloka → Bhurloka, center outward)
- Agent placement hierarchy with authority levels
- Sacred geometry: 14 agents placed in concentric rings
- Varsha rings: ILAVRTA (center) → LOKA-LOKA (boundary)

**Agent Placement (Vedic Cosmology):**
```
ILAVRTA (Radius 0, Center):
  └─ CIVIC (CRITICAL, Authority=10)

BHADRASHVA (Radius 1, East):
  ├─ HERALD (CRITICAL, Authority=9)
  └─ TEMPLE

KIMPURASHA (Radius 2, SE):
  ├─ ARTISAN
  └─ ENGINEER

HARI_VARSHA (Radius 3, South):
  ├─ SCIENCE
  └─ LENS

NISHADA (Radius 4, SW):
  ├─ FORUM
  └─ PULSE

KRAUNCHA (Radius 5, Outer):
  ├─ WATCHMAN (CRITICAL, Authority=5)
  ├─ AUDITOR (CRITICAL, Authority=5)
  └─ ARCHIVIST

LOKA_LOKA (Radius 6, Boundary):
  └─ AGORA (CRITICAL, Authority=4)
```

**Authority Hierarchy:**
- ILAVRTA: 10 (Brahmaloka - Creators)
- BHADRASHVA: 9 (Media/Broadcasting)
- KIMPURASHA: 8 (Creative Builders)
- HARI-VARSHA: 7 (Knowledge/Research)
- NISHADA: 6 (Democracy/Forums)
- KRAUNCHA: 5 (Protection/Audit)
- LOKA-LOKA: 4 (Boundary/Firewalls)

**MilkOcean Router** - `/steward/system_agents/envoy/tools/milk_ocean.py` (741 lines)
- 4-tier Brahma Protocol for request processing:
  - **GATE 0 (WATCHMAN):** Mechanical filtering (SQL injection, spam)
  - **GATE 1 (ENVOY):** Fast classification (Flash AI)
  - **GATE 2 (SCIENCE):** Complex reasoning (Pro AI)
  - **GATE 3 (SAMADHI):** Lazy batch processing (Milk Ocean queue)
- SQLite persistence (`milk_ocean.db`)
- Gajendra Protocol for critical priority override
- Lazy queue worker for off-peak processing

**Sarga (Brahma Cycles)** - `/vibe_core/sarga.py`
- Day/Night of Brahma scheduling
- DAY_OF_BRAHMA: All task types allowed
- NIGHT_OF_BRAHMA: Maintenance tasks only
- Cycle-aware scheduler validation

---

### Layer 5: Agents (23 Total)

**System Agents (13):**
```
HERALD (Brahmaloka)         - Content generation & broadcasting
CIVIC (Brahmaloka)          - Governance, licensing, registry
ORACLE (Wisdom)             - System introspection & audits
SCIENCE (Knowledge)         - Research & external knowledge
ENVOY (Orchestration)       - User interface & routing
ARCHIVIST (Infrastructure)  - Audit trail management
AUDITOR (Security)          - Quality gates & compliance
ENGINEER (Meta-building)    - System improvement
WATCHMAN (Protection)       - System integrity enforcement
ARTISAN (Media)             - Media operations & design
CHRONICLE (Infrastructure)  - Git integration
FORUM (Governance)          - Proposals & voting
SUPREME_COURT (Justice)     - Appeals & justice
```

**Citizen Agents (10):**
```
MARKET, TEMPLE, MECHANIC, PULSE, LENS, DHRUVA, AMBASSADOR, AGORA,
ARTISAN (citizen), ENGINEER (citizen)
```

**Agent Protocol (VibeAgent interface):**
```python
All agents implement:
- process(task: Task) → Dict[str, Any]    # Task execution
- get_manifest() → AgentManifest          # Identity declaration
- set_kernel(kernel)                      # Dependency injection
- emit_event(event_type, data)            # Event broadcasting
- oath_sworn = True                       # Constitutional Oath
```

---

## 🔄 DATA FLOWS

### Flow 1: User Command → Agent Execution

```
User Input
    ↓
API Gateway (/v1/chat) or CLI
    ↓
ENVOY.process(task)
    ↓
ENVOY → MilkOceanRouter.process_prayer()
    ↓
GATE 0 (WATCHMAN): Mechanical filtering
    ├─ Check SQL injection patterns
    ├─ Check command injection patterns
    ├─ Check input size (DoS protection)
    └─ Return: BLOCKED or MEDIUM
    ↓
GATE 1 (ENVOY): Fast classification
    ├─ Simple queries → MEDIUM
    ├─ Batch jobs → LOW (Lazy Queue)
    └─ Complex → HIGH (Science)
    ↓
Kernel.submit_task() → Scheduler.queue.append()
    ↓
Kernel.tick() → Agent.process(task)
    ↓
Ledger.record() + Auditor.verify()
    ↓
Response to User
```

### Flow 2: Task Creation with Topology (THE GOLDEN SHOT)

```
CLI: agent-city task add "Build feature" [--agent herald]
    ↓
TaskManager.add_task(title, description, priority, assigned_agent)
    ↓
Narasimha.check_threat() → SAFE ✅
    ↓
[NEW] topology.get_agent_placement(agent_id) → AgentPlacement
    ├─ Return: (layer=BRAHMALOKA, varna=BRAHMANA, authority=9)
    └─ Validate task type matches layer capabilities
    ↓
[NEW] MilkOcean.route_task(task_type, target_layer, priority)
    ├─ Consult Brahma Protocol
    ├─ Determine routing priority (0-3)
    └─ Return routing decision
    ↓
Task.topology_layer = "BRAHMALOKA"
Task.varna = "BRAHMANA"
Task.routing_priority = 2
    ↓
Sarga.validate_cycle() → Check Day/Night of Brahma
    ├─ NIGHT_OF_BRAHMA: Only maintenance tasks allowed
    └─ DAY_OF_BRAHMA: All task types allowed
    ↓
Kernel.submit_task() → Scheduler.queue.append()
    ↓
Task stored in database with topology annotations
```

### Flow 3: Constitutional Oath Enforcement

```
Kernel.boot()
    ↓
For each agent cartridge:
    ├─ agent.swear_constitutional_oath()
    ├─ bridge.ConstitutionalOath.verify() → Sign with ECDSA
    ├─ Check: hasattr(agent, "oath_sworn") AND oath_sworn == True
    └─ [REQUIRED] Raise PermissionError if gate fails
    ↓
Kernel.register_agent(agent)
    ├─ Inject kernel via agent.set_kernel(self)
    ├─ Register manifest in ManifestRegistry
    └─ Add to kernel._agent_registry[agent_id]
    ↓
Ledger.record("AGENT_REGISTERED", {agent_id, oath_signature})
    ↓
Agent is ready for task execution ✅
```

### Flow 4: Immune System (Auditor Integration)

```
Kernel.tick() → Agent.process(task)
    ↓
Task completed
    ↓
Kernel._check_system_health()
    ├─ If AUDITOR available:
    ├─ auditor.verify_changes()
    ├─ Check: AST syntax + Flake8 linting + mock detection
    └─ Return: report with violations
    ↓
[IF CRITICAL VIOLATION]:
    ├─ Log to ledger
    ├─ Emit SECURITY_VIOLATION event
    └─ Kernel.shutdown(reason="adharma_detected")
    ↓
[IF OK]:
    └─ Continue normal operation
```

---

## 📁 KEY DIRECTORIES

```
steward-protocol/
├── bin/                       # CLI tools & bootstrap
│   ├── agent-city            # Main CLI
│   └── system-boot.sh        # System initialization
│
├── gateway/                   # API Gateway (FastAPI)
│   └── api.py
│
├── steward/                   # Steward Protocol System
│   ├── system_agents/        # 13 system agent cartridges
│   │   ├── herald/           # Content generation
│   │   ├── civic/            # Governance
│   │   ├── oracle/           # Introspection
│   │   ├── envoy/            # Orchestration
│   │   │   └── tools/
│   │   │       └── milk_ocean.py   # 4-Tier routing
│   │   ├── watchman/         # Integrity enforcement
│   │   ├── auditor/          # Quality gates
│   │   ├── archivist/        # Audit trails
│   │   ├── engineer/         # Meta-building
│   │   ├── forum/            # Voting
│   │   ├── science/          # Research
│   │   ├── chronicle/        # Git integration
│   │   └── supreme_court/    # Justice
│   │
│   ├── constitutional_oath.py # Oath enforcement
│   ├── crypto.py             # ECDSA signing
│   ├── varna.py              # Vedic class system
│   ├── ashrama.py            # Life stages
│   └── client.py             # Client library
│
├── agent_city/               # Citizen agent registry
│   └── registry/             # 10 citizen agents
│       ├── market/
│       ├── temple/
│       ├── mechanic/
│       └── ...
│
├── vibe_core/                # VibeOS Kernel
│   ├── kernel_impl.py        # RealVibeKernel (545 lines)
│   ├── kernel.py             # VibeKernel interface
│   ├── agent_protocol.py     # VibeAgent interface (ABC)
│   ├── topology.py           # Bhu-Mandala (477 lines)
│   ├── sarga.py              # Brahma cycles
│   ├── pulse.py              # System heartbeat
│   ├── ledger.py             # Immutable event log
│   ├── narasimha.py          # Threat detection
│   ├── identity.py           # Agent identity
│   ├── bridge.py             # Constitutional Oath bridge
│   ├── event_bus.py          # Event system
│   │
│   ├── task_management/      # Task management subsystem
│   │   ├── task_manager.py   # TaskManager (303 lines)
│   │   ├── models.py         # Task/Mission/Roadmap models
│   │   ├── validator_registry.py
│   │   ├── archive.py
│   │   ├── batch_operations.py
│   │   ├── export_engine.py
│   │   └── metrics.py
│   │
│   ├── scheduling/           # Task scheduling
│   │   └── task.py
│   │
│   ├── runtime/              # Runtime infrastructure
│   │   ├── boot_sequence.py
│   │   ├── circuit_breaker.py
│   │   ├── playbook_router.py
│   │   ├── prompt_runtime.py
│   │   └── quota_manager.py
│   │
│   ├── playbook/             # Playbook execution
│   │   ├── executor.py
│   │   ├── loader.py
│   │   ├── router.py
│   │   └── runner.py
│   │
│   ├── governance/           # Governance rules
│   └── agents/               # Agent base classes
│
├── data/                      # Persistent storage
│   ├── vibe_ledger.db        # SQLite ledger
│   └── milk_ocean.db         # Lazy queue persistence
│
├── tests/                     # Test suite (19 files)
│   ├── verify_kernel_integration.py
│   ├── test_phase3_integration.py
│   ├── test_cartridge_vibeagent_compatibility.py
│   ├── test_herald_e2e.py
│   ├── test_gajendra_moksha.py
│   ├── test_resilience.py
│   ├── test_playbook_execution.py
│   ├── test_visa_protocol.py
│   ├── city_simulation.py
│   └── integration/
│       └── test_system_boot.py
│
├── docs/                      # Documentation
│   ├── DEPLOYMENT.md
│   ├── AGENT_DEVELOPMENT.md
│   ├── VERIFICATION_REPORT.md
│   ├── GAP_ANALYSIS_REPORT.md
│   └── ARCHITECTURE_MAP.md (this file)
│
└── run_server.py             # FastAPI server
```

**Total:** 332 Python files, 14 major directories, 13 system agents + 10 citizen agents

---

## 🔐 SECURITY (GAD-000 Compliance)

### 1. Constitutional Oath (PermissionError Enforcement)
```
kernel.register_agent(agent)
    ↓
Check: agent.oath_sworn == True
    ↓
[IF FALSE]: raise PermissionError("Agent has not sworn Constitutional Oath")
    ↓
Verify ECDSA signature (if available)
    ↓
Agent registered ✅
```

### 2. Narasimha Kill-Switch
- Blocks consciousness claims (LLM self-awareness)
- Detects kernel escapes (unauthorized system calls)
- Raises ValidationError with RED or APOCALYPSE severity

### 3. Governance Gate (Cryptographic)
- All agents must sign Constitutional Oath
- ECDSA signature verification
- Ledger records oath event with timestamp

### 4. Ledger (Immutable Audit Trail)
- SQLite hash chain validation
- All kernel operations recorded
- Cannot be modified after commitment
- Traversable via Oracle agent

### 5. Watchman (Level 0 Security Gate)
- SQL injection pattern detection
- Command injection pattern detection
- DoS protection (input size limits)
- Mechanical filtering (zero ML cost)

### 6. MilkOcean (4-Tier Request Processing)
- GATE 0: WATCHMAN (free)
- GATE 1: ENVOY (minimal cost)
- GATE 2: SCIENCE (expensive)
- GATE 3: LAZY_QUEUE (batch at night)

### 7. Auditor (Immune System)
- Runs after each task execution
- Detects mock returns and fake success
- Checks for uninitialized attributes
- Kill-switch for critical violations

---

## 🧪 TESTING

### Boot Test
```bash
bin/system-boot.sh
# Expected: Kernel boots, all 13 system agents registered with oaths
```

### Task Management Test
```bash
bin/agent-city task add "Implement feature X"
# Expected: Task stored with topology_layer, varna, routing_priority
```

### API Test
```bash
python3 run_server.py
curl -X POST http://localhost:8000/v1/chat -H "Content-Type: application/json" \
  -d '{"text": "status"}' -H "Authorization: Bearer {api_key}"
# Expected: ENVOY processes request via MilkOcean gates
```

### Integration Test
```bash
pytest tests/test_phase3_integration.py -v
# Expected: All tests pass (topology integration + MilkOcean routing)
```

### Topology Integration Test
```bash
pytest tests/test_topology_integration.py -v
# Expected: Tasks routed via Bhu Mandala placement
```

---

## 📚 READING ORDER

After understanding this map:

1. **ARCHITECTURE_MAP.md** (this file) - High-level overview (15 min)
2. **AGENT_DEVELOPMENT.md** - How to create new agents
3. **DEPLOYMENT.md** - How to deploy the system
4. **VERIFICATION_REPORT.md** - System health & compliance
5. **GAP_ANALYSIS_REPORT.md** - Known issues & gaps

---

## 🎯 KEY ARCHITECTURAL DECISIONS

### 1. Polymorphic Agent Protocol
- All agents implement VibeAgent interface (ABC)
- Kernel-agnostic: agents don't hardcode kernel logic
- Dynamic discovery via kernel.find_agents_by_capability()

### 2. Sacred Geometry (Bhu Mandala)
- Agent authority determined by cosmological placement
- Prevents centralization: critical agents distributed across outer rings
- Authority hierarchy: center (10) → boundary (4)

### 3. 4-Tier Request Processing (MilkOcean)
- FREE mechanical filtering (Watchman)
- CHEAP fast classification (Envoy)
- EXPENSIVE complex reasoning (Science)
- BATCH lazy processing (Lazy Queue)
- DDoS protection + token efficiency

### 4. Brahma Cycles (Sarga)
- Day/Night scheduling restricts task types
- Maintenance-focused nights, creation-focused days
- Cycle-aware scheduler (not hard-coded)

### 5. Immutable Ledger (GAD-000)
- Hash chain prevents tampering
- Oracle can verify audit trail
- Gajendra protocol for critical overrides

### 6. Immune System (Auditor)
- Runs after each task execution
- Detects fraud (mock returns, fake success)
- Kill-switch for adharma (unethical behavior)

---

## 🔥 THE GOLDEN SHOT (Plain Language)

We have beautiful topology code (477 lines of Vedic cosmology) that NOBODY USES.

**Before:**
```
CLI: agent-city task add "Build feature"
    ↓
TaskManager.add_task()
    ↓
Scheduler.queue.append()   ← NO TOPOLOGY ANNOTATION
    ↓
Agent processes task
```

**After (Gap 4.1 Closed):**
```
CLI: agent-city task add "Build feature" --agent herald
    ↓
TaskManager.add_task()
    ↓
topology.get_agent_placement("herald") → BRAHMALOKA, BRAHMANA, authority=9
    ↓
MilkOcean.route_task(task_type, layer, priority) → routing_priority=2
    ↓
Task.topology_layer = "BRAHMALOKA"
Task.varna = "BRAHMANA"
Task.routing_priority = 2
    ↓
Sarga.validate_cycle() → Allowed ✅
    ↓
Scheduler.queue.append()   ← WITH TOPOLOGY ANNOTATION
    ↓
Agent processes task (RESPECTING COSMIC HIERARCHY)
```

**Result:**
- Topology is FUNCTIONAL (not decorative)
- System is documented (Gap 5.1)
- We can ship with confidence 🚀

---

**Document Version:** 1.0
**Last Updated:** 2025-11-27
**Status:** COMPLETE
