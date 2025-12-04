# STEWARD PROTOCOL - Agent Meta-Layer Architecture

> **Status:** DRAFT - Architectural Design Document
> **Date:** 2024-12-04
> **Confidence:** HIGH

## Core Insight

**STEWARD is NOT an Agent. STEWARD is the PROTOCOL that enables Agents to exist.**

Like Telegram's BotFather is not a bot - it's the meta-instance that creates and manages bots.

```
WRONG (current state):
  Agents = [discoverer, chronicle, scribe, ...]
           ↑ discoverer calls itself "steward" - CONFUSION

CORRECT (target state):
  STEWARD PROTOCOL (Meta-Layer)
      │
      ├── defines   → Agent Manifest Schema
      ├── discovers → Agents in filesystem
      ├── validates → Against Constitution
      ├── registers → Into Kernel
      └── governs   → Constitutional Compliance

      └── manages → AGENTS (Citizens)
                    [discoverer, chronicle, scribe, ...]
```

## The Trinity (Fractal Architecture)

```
┌─────────────────┬─────────────────┬─────────────────┐
│     KERNEL      │     PHOENIX     │     STEWARD     │
│    (Vishnu)     │    (Config)     │   (Protocol)    │
│   Execution     │   Parameters    │   Agent Meta    │
├─────────────────┼─────────────────┼─────────────────┤
│ plugin_loader   │ section_loader  │ agent_loader    │
│ plugins/        │ sections/       │ system_agents/  │
│ KernelPlugin    │ ConfigSection   │ AgentManifest   │
│ plugin_protocol │ section_protocol│ agent_protocol  │
└─────────────────┴─────────────────┴─────────────────┘
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                    FRACTAL PATTERN
              (Same structure at every level)
```

## Directory Structure

### Current (Spaghetti)
```
steward/                          # Project root (confusing name)
├── system_agents/
│   ├── discoverer/               # agent_id="steward" (WRONG!)
│   │   ├── agent.py              # Discoverer class
│   │   └── steward.json          # identity.agent_id: "steward"
│   ├── steward/                  # ORPHAN - broken schema, no cartridge
│   │   └── steward.json          # Different schema!
│   └── ...
├── constitutional_oath.py        # Should be in protocol
└── oath_mixin.py                 # Should be in protocol
```

### Target (Fractal)
```
vibe_core/
├── kernel/                       # Execution layer
│   ├── kernel.py
│   └── plugin_loader.py
├── phoenix/                      # Configuration layer
│   ├── config.py
│   ├── section_loader.py
│   └── sections/
└── steward/                      # Agent Protocol layer (NEW)
    ├── __init__.py
    ├── protocol.py               # AgentManifest, AgentProtocol
    ├── loader.py                 # AgentLoader (like SectionLoader)
    ├── registry.py               # Agent Registry
    ├── constitution.py           # Constitutional Oath (moved)
    └── schema/
        └── manifest.schema.json  # JSON Schema for validation

steward/                          # RENAME to agent_city/ or citizens/
└── system_agents/                # Agent IMPLEMENTATIONS (not protocol)
    ├── discoverer/               # Service agent - discovers others
    │   ├── cartridge_main.py
    │   └── manifest.json         # RENAME from steward.json
    ├── chronicle/
    ├── scribe/
    └── ...
```

## Component Responsibilities

### vibe_core/steward/protocol.py
```python
@dataclass
class AgentManifest:
    """What an agent IS - identity, capabilities, governance."""
    agent_id: str
    name: str
    version: str
    domain: str
    capabilities: List[str]
    constitution_hash: str

@runtime_checkable
class AgentProtocol(Protocol):
    """Duck-typed protocol - any class with these is a valid agent."""
    agent_id: str
    def process(self, task: Task) -> Dict[str, Any]: ...
    def get_manifest(self) -> AgentManifest: ...
```

### vibe_core/steward/loader.py
```python
class AgentLoader:
    """
    Auto-discovery for agents (mirrors SectionLoader).

    Scans directories for manifest.json files,
    validates against schema, loads cartridges.
    """

    @classmethod
    def discover(cls,
                 agents_dir: Path = Path("steward/system_agents")
    ) -> Dict[str, AgentManifest]:
        """Discover all agent manifests."""
        ...

    @classmethod
    def load_cartridge(cls,
                       manifest_path: Path
    ) -> Optional[AgentProtocol]:
        """Dynamically load cartridge_main.py."""
        ...
```

### vibe_core/steward/constitution.py
```python
class ConstitutionalOath:
    """
    The binding contract between agents and the system.

    Moved from steward/constitutional_oath.py
    """

    @staticmethod
    def compute_hash() -> str: ...

    @staticmethod
    def create_oath_event(agent_id: str, ...) -> Dict: ...

    @staticmethod
    def verify(oath_event: Dict) -> Tuple[bool, str]: ...
```

## Manifest Schema (Unified)

All agents use ONE schema. No more `identity.agent_id` vs `agent.id` vs root-level `agent_id`.

```json
{
  "$schema": "https://steward-protocol.org/manifest.schema.json",
  "manifest_version": "2.0.0",

  "agent": {
    "id": "discoverer",
    "name": "The Discoverer",
    "version": "1.0.0",
    "domain": "GOVERNANCE",
    "description": "Discovers and registers agents"
  },

  "capabilities": [
    {
      "name": "discovery",
      "description": "Scan filesystem for new agents"
    },
    {
      "name": "registration",
      "description": "Register agents with kernel"
    }
  ],

  "governance": {
    "constitution_hash": "df4bf7b7...",
    "compliance_level": 2,
    "issuer": "passport_office",
    "issued_at": "2025-11-29T08:57:39Z"
  }
}
```

## Migration Path

### Phase 1: Create Protocol Layer
1. Create `vibe_core/steward/` directory
2. Move `constitutional_oath.py` → `vibe_core/steward/constitution.py`
3. Move `oath_mixin.py` → `vibe_core/steward/oath_mixin.py`
4. Create `protocol.py` with AgentManifest, AgentProtocol
5. Create `loader.py` mirroring SectionLoader

### Phase 2: Clean Up Naming
1. DELETE `steward/system_agents/steward/` (orphan)
2. FIX discoverer: `agent_id: "steward"` → `agent_id: "discoverer"`
3. Rename `steward.json` → `manifest.json` (optional, clearer)

### Phase 3: Unify Schema
1. Create JSON Schema at `vibe_core/steward/schema/manifest.schema.json`
2. Migrate legacy agents (envoy, ping, science) to standard schema
3. Add schema validation to AgentLoader

### Phase 4: Integration
1. Update Kernel to use AgentLoader
2. Update Discoverer to be a service agent using the protocol
3. Remove hardcoded agent loading logic

## Open Questions

1. **Project rename?** Should `steward/` directory become `citizens/` or `agents/`?
2. **Manifest filename?** Keep `steward.json` or rename to `manifest.json`?
3. **Backward compatibility?** How long to support legacy schemas?

## References

- `vibe_core/phoenix/section_loader.py` - The pattern to mirror
- `vibe_core/phoenix/config.py` - PhoenixConfig unified interface
- `vibe_core/protocols/agent.py` - Existing AgentManifest (to be moved)
