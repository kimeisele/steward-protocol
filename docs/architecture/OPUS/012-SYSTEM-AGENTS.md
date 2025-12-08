# OPUS-012: System Agents (BRAHMIN Architecture)

> **Status**: PLANNING
> **Created**: 2025-12-08
> **Scope**: Define System Agents as first-class kernel plugins with persona + state + protocol

---

## Philosophy

System Agents are the **BRAHMIN** class - they don't just process tasks, they **shape the system itself**.

The fractal insight: A System Agent IS a Plugin IS a Persona IS a Protocol.

```
┌─────────────────────────────────────────────┐
│           SYSTEM AGENT = PLUGIN             │
├─────────────────────────────────────────────┤
│  PERSONA  │  STATE    │  PROTOCOL           │
│  (Who)    │  (What)   │  (How)              │
│           │           │                     │
│  Identity │  Runtime  │  Syscalls           │
│  via      │  via      │  Circuits           │
│  PRAKRITI │  Kernel   │                     │
└─────────────────────────────────────────────┘
```

---

## Current System Agents (16 Cartridges)

Location: `vibe_core/cartridges/system/`

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

## Implementation Priority

1. **Phase 1**: ENGINEER (creates agents)
2. **Phase 2**: HERALD (broadcasting)  
3. **Phase 3**: CURATOR (knowledge)

---

## GAD-000 Compliance

System Agents MUST be:
- **Discoverable**: `kernel.get_capabilities()` lists them
- **Observable**: `kernel.get_system_status()` shows their state
- **Parseable**: All outputs are structured
- **Composable**: Can be chained via circuits

---

## Open Questions

1. Should ENGINEER have constitutional limits on what agents it can spawn?
2. Should spawned agents require AUDITOR approval before activation?
3. How to handle agent versioning and upgrades?

---

## Next Steps

- [ ] Implement ENGINEER as plugin in `vibe_core/plugins/engineer/`
- [ ] Create AGENT_SPAWN_V1 circuit
- [ ] Wire into existing AGENT_BIRTH_V1 playbook
- [ ] Integration tests
