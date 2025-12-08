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
│  via      │  via      │  via                │
│  PRAKRITI │  Kernel   │  Circuits           │
└─────────────────────────────────────────────┘
```

---

## System Agent Registry

| Agent | Purpose | Status |
|-------|---------|--------|
| **ENGINEER** | Spawns new agents, creates code | **NEXT** |
| ENVOY | Circuit routing and execution | ✅ Exists |
| STEWARD | Protocol governance | ✅ Exists |
| AUDITOR | System verification | ✅ Exists |
| WATCHMAN | Monitoring and health | ✅ Exists |
| HERALD | Announcements and broadcasting | TODO |
| CURATOR | Knowledge curation | TODO |

---

## ENGINEER Specification

### Purpose
The ENGINEER creates new agents. It uses:
- `kernel.prakriti.personas` to create identity
- Plugin manifest system to register the agent
- Cartridge pattern for the code

### Capabilities
```yaml
capabilities:
  - spawn_agent        # Create new agent from spec
  - modify_cartridge   # Edit agent code
  - fork_agent         # Clone with modifications
  - retire_agent       # Mark agent deprecated
```

### Protocol (Circuits)

**AGENT_SPAWN_V1**:
```
INTAKE → DESIGN → IMPLEMENT → REGISTER → VERIFY → COMPLETE
```

1. **INTAKE**: Receive agent specification
2. **DESIGN**: Create persona + manifest
3. **IMPLEMENT**: Generate cartridge code
4. **REGISTER**: Wire into kernel
5. **VERIFY**: Test the new agent
6. **COMPLETE**: Record in lineage

### Integration Points

```python
# Engineer uses PRAKRITI for identity
persona = kernel.prakriti.personas.create_default(
    agent_id=spec.id,
    display_name=spec.name,
    dharma=spec.purpose,
)

# Engineer creates plugin manifest
manifest = {
    "id": spec.id,
    "version": "1.0.0",
    "persona": persona.agent_id,
    "cartridge": f"vibe_core/cartridges/{spec.id}",
}

# Engineer registers with kernel
kernel.register_agent(new_agent)
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
