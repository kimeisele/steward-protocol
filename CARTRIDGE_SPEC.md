# Cartridge Specification (Golden Template)

> This document defines the **canonical structure** for all Steward Protocol cartridges.
> Every agent MUST conform to this specification to be loaded by the Discoverer.

## Required Files

```
{agent_id}/
├── steward.json        # REQUIRED - Identity & Governance
├── cartridge.yaml      # REQUIRED - Configuration & Dependencies
├── cartridge_main.py   # REQUIRED - Python Implementation
├── STEWARD.md          # OPTIONAL - Agent Constitution
└── tools/              # OPTIONAL - Agent Tools
    ├── __init__.py
    └── {tool_name}.py
```

---

## 1. steward.json (Identity & Governance)

The passport. Declares who this agent is and what it can do.

```json
{
  "identity": {
    "agent_id": "{agent_id}",
    "name": "{AGENT_NAME}"
  },
  "specs": {
    "version": "1.0.0",
    "description": "{Brief description of what this agent does}",
    "domain": "{DOMAIN}"
  },
  "capabilities": {
    "operations": [
      {
        "name": "{operation_name}",
        "description": "{What this operation does}"
      }
    ]
  },
  "governance": {
    "compliance_level": 2,
    "constitution_hash": "{sha256_hash}",
    "issued_at": "{ISO8601_timestamp}",
    "issuer": "passport_office"
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `identity.agent_id` | YES | Unique identifier (lowercase, no spaces) |
| `identity.name` | YES | Display name (usually UPPERCASE) |
| `specs.version` | YES | Semantic version (e.g., "1.0.0") |
| `specs.description` | YES | One-line description |
| `specs.domain` | YES | Domain category (see below) |
| `capabilities.operations` | YES | List of operations this agent can perform |
| `governance.compliance_level` | YES | 1-3 (1=minimal, 2=standard, 3=strict) |
| `governance.constitution_hash` | YES | SHA256 of CONSTITUTION.md |
| `governance.issued_at` | YES | ISO8601 timestamp |
| `governance.issuer` | YES | Always "passport_office" |

### Valid Domains

- `GOVERNANCE` - System administration, rules enforcement
- `INFRASTRUCTURE` - Documentation, monitoring, tooling
- `MEDIA` - Content generation, broadcasting
- `RESEARCH` - Analysis, data processing
- `ENGINEERING` - Code generation, builds
- `TESTING` - Test agents, validation
- `SYSTEM` - Core system agents

---

## 2. cartridge.yaml (Configuration & Dependencies)

The brain configuration. Declares how this agent thinks.

```yaml
meta:
  id: "agent.steward.{agent_id}"
  name: "{Agent Name}"
  version: "1.0.0"
  author: "Steward Protocol"
  description: "{Detailed description}"

agent:
  domain: "{DOMAIN}"
  capabilities:
    - "{capability_1}"
    - "{capability_2}"

dependencies:
  - "pyyaml"
  - "python-dotenv"

config:
  # Agent-specific configuration
  governance:
    level: "standard"
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta.id` | YES | Full identifier (agent.steward.{agent_id}) |
| `meta.name` | YES | Human-readable name |
| `meta.version` | YES | Must match steward.json |
| `meta.author` | YES | Author/team name |
| `meta.description` | YES | Detailed description |
| `agent.domain` | YES | Must match steward.json |
| `agent.capabilities` | YES | List of capability strings |
| `dependencies` | NO | Python package dependencies |
| `config` | NO | Agent-specific configuration |

---

## 3. cartridge_main.py (Python Implementation)

The body. The actual Python code that makes the agent work.

```python
#!/usr/bin/env python3
"""
{AGENT_NAME} Cartridge - {Brief Description}

{Detailed description of what this agent does}
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.steward.oath_mixin import OathMixin
from vibe_core import Task, VibeAgent
from vibe_core.protocols import AgentManifest

logger = logging.getLogger("{AGENT_NAME}")


class {AgentName}Cartridge(VibeAgent, OathMixin):
    """
    The {AGENT_NAME} Agent Cartridge.

    {Detailed docstring}
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize {AGENT_NAME} as a VibeAgent."""
        self.config = config

        super().__init__(
            agent_id="{agent_id}",
            name="{AGENT_NAME}",
            version="1.0.0",
            author="Steward Protocol",
            description="{Description}",
            domain="{DOMAIN}",
            capabilities=["{cap1}", "{cap2}"],
        )

        # Swear Constitutional Oath
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True

        logger.info("✅ {AGENT_NAME} initialized")

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest for kernel registry."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """Process a task from the kernel scheduler."""
        action = task.payload.get("action")
        logger.info(f"Processing action: {action}")

        if action == "{action_name}":
            return self._handle_action(task.payload)

        return {"status": "error", "error": f"Unknown action: {action}"}

    def _handle_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specific action."""
        # Implementation here
        return {"status": "success"}

    def report_status(self) -> Dict[str, Any]:
        """Report agent status for kernel heartbeat."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
        }


# REQUIRED: Export for dynamic loading
__all__ = ["{AgentName}Cartridge"]
```

### Requirements

1. **Class Name**: Must end with `Cartridge` (e.g., `PingCartridge`, `HeraldCartridge`)
2. **Inheritance**: Must inherit from `VibeAgent` AND `OathMixin`
3. **Oath**: Must call `self.oath_mixin_init()` and set `self.oath_sworn = True`
4. **Methods**: Must implement `__init__`, `get_manifest`, `process`, `report_status`
5. **Export**: Must have `__all__` with the class name

---

## 4. tools/ Directory (Optional)

If the agent has tools, they go here.

```
tools/
├── __init__.py
└── {tool_name}.py
```

Each tool must implement the `Tool` protocol:

```python
from vibe_core.tools.tool_protocol import Tool

class MyTool(Tool):
    name = "{agent_id}.{tool_name}"
    description = "{What this tool does}"

    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {...}}

    def validate(self, params: dict) -> tuple[bool, str]:
        return True, ""

    def execute(self, params: dict, context: dict) -> Any:
        # Implementation
        pass
```

---

## Validation Checklist

Before an agent is considered compliant:

- [ ] `steward.json` exists and has valid JSON
- [ ] `steward.json` has `identity.agent_id` field
- [ ] `cartridge.yaml` exists and has valid YAML
- [ ] `cartridge.yaml` has `meta.id` field
- [ ] `cartridge_main.py` exists
- [ ] `cartridge_main.py` has a class ending with `Cartridge`
- [ ] Class inherits from `VibeAgent` and `OathMixin`
- [ ] Class has `oath_sworn = True` set in `__init__`
- [ ] Class has `__all__` export

---

## Discovery Process

The Discoverer loads agents as follows:

1. Scan `steward/system_agents/` and `agent_city/registry/` for `steward.json`
2. For each `steward.json` found:
   - Read `identity.agent_id`
   - Check if `cartridge_main.py` exists in same directory
   - If YES: Dynamically import and find `*Cartridge` class
   - If NO: Log warning, skip agent
3. Instantiate cartridge class with optional config
4. Register with kernel

**No CARTRIDGE_MAP required.** Discovery is fully dynamic.
