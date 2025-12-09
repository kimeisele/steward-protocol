# OPUS-012: System Agents (BRAHMIN Architecture)

> **Status**: PLANNING
> **Created**: 2025-12-08
> **Scope**: Define System Agents as first-class kernel plugins with persona + state + protocol

---

## The Fractal Pattern (System Devata)

A **System Devata** exists on **three planes simultaneously**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYSTEM DEVATA = 3 PLANES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PLANE 1: PLUGIN           PLANE 2: CARTRIDGE      PLANE 3: PASSPORT│
│  (Kernel Governance)       (Task Processing)       (Identity)       │
│                                                                     │
│  • on_boot()               • process(task)         • steward.json   │
│  • on_agent_registered()   • manifest_reality()    • constitution_  │
│  • on_capability_check()   • action handlers         hash           │
│  • on_task_submit()        • tools/                • capabilities   │
│                                                                     │
│  priority: 5-15            LOC: 200-600+           trust score      │
│  hooks into kernel         executes work           governs identity │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ENVOY Analysis (The System Shell)

| Plane | Location | Size | Purpose |
|-------|----------|------|---------|
| Plugin | `plugins/envoy/plugin_main.py` | 660 LOC | Routes intent, manages unified executor |
| Cartridge | `cartridges/system/envoy/` | 179KB | Executor, provider, action handlers |
| Passport | `cartridges/system/envoy/steward.json` | Identity, constitution_hash |

**Plugin hooks**: `on_boot`, `on_tick`, `on_shutdown`  
**Priority**: 15 (after steward_protocol)  
**Depends on**: `steward_protocol`, `tools`

### STEWARD Analysis (The Protocol Layer)

| Plane | Location | Size | Purpose |
|-------|----------|------|---------|
| Plugin | `plugins/steward_protocol/plugin_main.py` | 895 LOC | GATES all agents |
| Cartridge | **NONE** | - | IS the protocol, not an agent |
| Passport | **N/A** | - | Governs passports, doesn't need one |

**Plugin hooks**: 7 hooks including `on_agent_pre_register`, `on_capability_check`  
**Priority**: 5 (boots FIRST)  
**The GATEKEEPER**: Blocks unregistered agents, verifies constitution oath

### The Insight

STEWARD has NO cartridge because **it is not an agent - it IS the protocol**.  
ENVOY is BOTH plugin AND cartridge because **it routes AND executes**.

A true **System Devata** like ENGINEER would need:
- **Plugin**: `plugins/engineer/` for spawning governance hooks
- **Cartridge**: `cartridges/system/engineer/` ✅ EXISTS (254 LOC)
- **Passport**: `steward.json` ✅ EXISTS

**ENGINEER is MISSING PLANE 1 (Plugin)**.

| Agent | Purpose | Status |
|-------|---------|--------|
| **engineer** | Code generation, agent scaffolding | ✅ EXISTS - Needs PRAKRITI |
| **envoy** | Circuit routing and execution | ✅ EXISTS |
| **auditor** | System verification | ✅ EXISTS |
| **watchman** | Monitoring and health | ✅ EXISTS |
| **herald** | Announcements | ✅ EXISTS |
| **scribe** | Documentation | ✅ EXISTS |
| **archivist** | Data archival | ✅ EXISTS |
| **oracle** | Knowledge queries | ✅ EXISTS |
| civic | Governance voting | ✅ EXISTS |
| chronicle | History tracking | ✅ EXISTS |
| discoverer | Agent discovery | ✅ EXISTS |
| forum | Discussions | ✅ EXISTS |
| ping | Health checks | ✅ EXISTS |
| science | Research | ✅ EXISTS |
| supreme_court | Constitutional enforcement | ✅ EXISTS |

---

## ENGINEER Enhancement (Not Creation)

### Current State
```
vibe_core/cartridges/system/engineer/
├── cartridge_main.py    # 254 LOC - manifest_reality, create_agent_legacy
├── cartridge.yaml       # capabilities: code_generation, scaffolding, automation
├── steward.json         # Passport with constitution_hash
└── tools/               # BuilderTool, etc.
```

### Current Capabilities
- `manifest_reality`: Write code to sandbox
- `create_agent_legacy`: Scaffold new agents (marked legacy)

### Missing: PRAKRITI Integration
Current ENGINEER doesn't use:
- `kernel.prakriti.personas` for agent identity
- Persistent system prompts
- Chain of Thought logging

### Enhancement Tasks

1. **Wire PRAKRITI into ENGINEER**:
   ```python
   # In manifest_reality or new spawn_agent method:
   persona = self.kernel.prakriti.personas.create_default(
       agent_id=new_agent_id,
       display_name=spec.name,
       dharma=spec.purpose,
   )
   self.kernel.prakriti.personas.save(persona)
   ```

2. **Add spawn_agent method** (replace create_agent_legacy):
   - Create persona via PRAKRITI
   - Generate cartridge code
   - Create steward.json passport
   - Register with kernel

3. **Add Chain of Thought**:
   ```python
   self.kernel.prakriti.ephemeral.add_thought(
       agent_id='engineer',
       thought=f'Spawning agent: {spec.name}',
       context={'spec': spec}
   )
   ```

---

## Critical Architectural Constraints

> **ALL System Devatas MUST exist on 3 planes.**

### Constraint 1: Syscall Translation Layer

The Circuit (`AGENT_BIRTH_V1`) ends with `EXECUTE_SYSCALL: SPAWN_COGNITION`.

**Gap**: This symbolic syscall must map to concrete Python.

**Solution**: Syscall Registry in `EnvoyPlugin`:
```python
SYSCALL_REGISTRY = {
    "SPAWN_COGNITION": "kernel.plugins['lifecycle'].spawn_agent",
    "QUERY_KNOWLEDGE": "kernel.plugins['curator'].query",
}
```

### Constraint 2: Constitution Binding at Birth

The `steward.json` passport requires `constitution_hash`.

**This is NOT a random ID** - it MUST be SHA256 of the active `CONSTITUTION.md`.

**Solution**: Engineer reads `kernel.steward.current_constitution_hash` at birth:
```python
oath_hash = self.kernel.steward.current_constitution_hash
if not oath_hash:
    raise GovernanceError("Cannot spawn: No active constitution")
passport["governance"]["constitution_hash"] = oath_hash
```

**Consequence**: Agents without this hash are **Ronin** (oathless) and will be rejected by `StewardProtocol`.

### Constraint 3: Sandbox → Live Atomic Move

`manifest_reality` writes to `./workspaces/sandbox` (untrusted).

**Gap**: No path from sandbox to `vibe_core/cartridges/` (trusted).

**Solution**: Purification Pipeline
1. **Engineer** writes to Sandbox
2. **Auditor** scans (syntax, security, oath compliance)
3. **LifecyclePlugin** (Kernel level) performs atomic move ONLY after Auditor signs off

> ⚠️ **CRITICAL**: Do NOT let Engineer write directly to live cartridge directory.

### Constraint 4: Separation of Powers (God Mode Prevention)

**Risk**: If Engineer has raw kernel access, it could spawn infinite agents (cancer).

**Solution**: Two-entity separation
- **Engineer (Agent/Cartridge)**: *Proposes* life - writes DNA/code, requests birth
- **LifecyclePlugin (Kernel)**: *Grants* life - executes spawn, subject to quotas

```
┌─────────────────────────────────────────────────────────┐
│  ENGINEER proposes → LIFECYCLE grants (with governance) │
│                                                         │
│  Engineer                    LifecyclePlugin            │
│  ────────                    ───────────────            │
│  write_cartridge()           on_spawn_request()         │
│  generate_passport()         verify_constitution()      │
│  request_spawn()   ────────→ register_if_approved()     │
└─────────────────────────────────────────────────────────┘
```

> **Do NOT give the Agent the keys to the Kernel's process table.**

### Constraint 5: CURATOR before HERALD

**Correction**: Swap priority order.

- **CURATOR** (Knowledge/Memory) needed for Engineer to know *what* to build
- **HERALD** is noise if agents aren't smart enough to be announced

---

## Implementation Priority (Corrected)

1. **Phase 1**: ENGINEER + LifecyclePlugin (spawning with governance)
2. **Phase 2**: CURATOR (knowledge for intelligent spawning)
3. **Phase 3**: HERALD (broadcasting after agents are worthy)

---

## The Spawn Protocol

```python
# vibe_core/plugins/lifecycle/plugin_main.py

def on_spawn_request(self, spec: AgentSpec, oath_hash: str):
    """
    The Atomic 'Spark of Life'.
    Called by Engineer (via syscall), executed by Kernel.
    """
    # 1. Constitution Gate
    if oath_hash != self.kernel.steward.current_constitution_hash:
        raise GovernanceError("Cannot spawn: Constitution Mismatch")

    # 2. Auditor Gate (was sandbox scanned?)
    if not self.kernel.plugins['auditor'].is_approved(spec.id):
        raise GovernanceError("Cannot spawn: Auditor approval required")

    # 3. Prakriti Registration (Identity)
    persona = self.kernel.prakriti.personas.create_default(
        agent_id=spec.id,
        display_name=spec.name,
        dharma=spec.purpose,
    )

    # 4. Kernel Registration (Execution)
    self.kernel.register_agent(spec.load_cartridge())

    # 5. Herald Announcement
    self.kernel.bus.publish("system.life.birth", {"agent": spec.id})

    return {"status": "born", "agent_id": spec.id}
```

---

## Definition of Done (GAD-000 Compliance)

### The 6-Test Turing Test for Agent Spawning

Every spawned agent MUST pass these tests:

#### 1. Discoverability Test ✅
- [ ] `kernel.get_capabilities()` lists the spawned agent
- [ ] Agent appears in `AGENTS.md` auto-generated interface
- [ ] CLI command `vibe list agents` shows agent

**Current Status:** ❌ INCOMPLETE - Agent not auto-registered in kernel (Gate 4 TODO)

#### 2. Observability Test
- [ ] `kernel.get_system_status()` shows agent state
- [ ] Agent persona exists in `config/personas/{agent_id}.yaml`
- [ ] Agent cartridge exists in sandbox or live directory

**Current Status:** ⚠️ PARTIAL - Persona created ✅, cartridge in sandbox ✅, not in kernel registry ❌

#### 3. Parseability Test
- [ ] `steward.json` passport is valid JSON with schema
- [ ] `audit_certificate.json` has machine-readable status
- [ ] Spawn errors return structured `{status, error, reason}`

**Current Status:** ✅ COMPLETE - All outputs are structured JSON

#### 4. Composability Test
- [ ] Spawn can be triggered via circuit (`AGENT_BIRTH_V1`)
- [ ] Spawn can be triggered via syscall (`SPAWN_COGNITION`)
- [ ] Spawn output can feed into next operation

**Current Status:** ✅ COMPLETE - SPAWN_COGNITION syscall works

#### 5. Idempotency Test
- [ ] Spawning same agent twice returns "already exists"
- [ ] Spawn can be safely retried after failure
- [ ] State is atomic (no half-spawned agents)

**Current Status:** ❌ INCOMPLETE - No duplicate detection

#### 6. Identity Test (GAD-1000)
- [ ] Spawned agent has `constitution_hash` in passport
- [ ] Hash matches kernel's locked `CONSTITUTION.md` hash
- [ ] Agent rejected if hash mismatches (Ronin prevention)

**Current Status:** ✅ COMPLETE - Constitution gate verified

---

## Implementation Status

### What Works NOW

| Component | Status | Evidence |
|-----------|--------|----------|
| LifecyclePlugin | ✅ | Boots, registers SPAWN_COGNITION syscall |
| SyscallRegistry | ✅ | `vibe_core/runtime/syscalls.py` |
| Engineer.spawn_agent | ✅ | Creates cartridge, passport, persona |
| Gate 1 (Constitution) | ✅ | Hash verified against kernel |
| Gate 2 (Auditor) | ⚠️ | STUB - engineer_stub signs |
| Gate 3 (Prakriti) | ✅ | Persona created and saved |
| Gate 4 (Kernel) | ❌ | TODO - dynamic cartridge loading |
| Gate 5 (Herald) | ⚠️ | Event prepared, not published |

### What's Missing

1. **Gate 4 - Dynamic Cartridge Loading**
   - Agent code stays in sandbox
   - Not moved to `vibe_core/cartridges/`
   - Not registered in kernel at runtime

2. **Real Auditor Agent**
   - Currently engineer signs its own work
   - Need separate Auditor to scan sandbox
   - Security audit before approval

3. **CLI Integration**
   - No `vibe spawn <agent>` command
   - No `vibe list spawned` command
   - Not visible via GAD-000 interfaces

4. **Duplicate Prevention**
   - Can spawn same agent twice
   - Idempotency not enforced

---

## Files Created by Spawn

```
workspaces/sandbox/{agent_id}/
├── cartridge_main.py    # Generated Python code
├── steward.json         # Passport with constitution_hash
└── audit_certificate.json  # STUB approval record

config/personas/{agent_id}.yaml  # Prakriti identity
```

---

## Next Steps (Priority Order)

1. [ ] **Gate 4 Fix**: Move approved cartridge to live, register in kernel
2. [ ] **Real Auditor**: Separate agent for code scanning
3. [ ] **CLI Commands**: `vibe spawn`, `vibe list agents`
4. [ ] **Duplicate Check**: Reject if agent_id already exists
5. [ ] **Integration Test**: Full end-to-end spawn + use cycle
