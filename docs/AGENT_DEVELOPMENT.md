# AGENT DEVELOPMENT GUIDE

**Purpose:** Complete guide for creating new agents in Steward Protocol.

---

## 🏛️ AGENT ARCHITECTURE

### Agent Types

**System Agents** (`/steward/system_agents/`)
- OS-level cartridges (12 Adityas)
- Direct kernel access
- Constitutional Oath required
- Examples: HERALD, CIVIC, ENVOY

**Citizen Agents** (`/agent_city/registry/`)
- Application-level services
- Limited kernel access via CIVIC
- Constitutional Oath required
- Examples: MARKET, TEMPLE, MECHANIC

---

## 🔧 CREATING A SYSTEM AGENT

### Step 1: Directory Structure

```bash
mkdir -p steward/system_agents/your_agent
cd steward/system_agents/your_agent
touch __init__.py cartridge_main.py
mkdir tools
touch tools/__init__.py
```

### Step 2: Implement VibeAgent Protocol

```python
# cartridge_main.py
from vibe_core.agent_protocol import VibeAgent, AgentManifest
from vibe_core.bridge import OathMixin
from vibe_core.scheduling import Task
from typing import Dict

class YourAgentCartridge(VibeAgent, OathMixin):
    def __init__(self):
        super().__init__()
        self.agent_id = "your_agent"
        self.name = "YOUR_AGENT"
        self.version = "1.0.0"

        # Constitutional Oath (GAD-000)
        import asyncio
        try:
            asyncio.run(self.swear_constitutional_oath())
        except Exception as e:
            print(f"⚠️ Oath ceremony failed: {e}")

        # Load tools
        self.tools = {}  # Add your tools here

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest for kernel registration."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author="Steward Protocol",
            description="[What does this agent do?]",
            domain="[DOMAIN]",  # e.g., GOVERNANCE, MEDIA, SCIENCE
            capabilities=['capability_1', 'capability_2']
        )

    def process(self, task: Task) -> Dict:
        """Main entry point for task processing."""
        # 1. Extract task payload
        payload = task.payload

        # 2. Route to appropriate tool/handler
        result = self._handle_task(payload)

        # 3. Return result
        return {
            "status": "success",
            "result": result
        }

    def _handle_task(self, payload: Dict) -> Dict:
        """Internal task handler."""
        # Your logic here
        pass
```

### Step 3: Register in Kernel

```python
# In run_server.py or kernel boot script
from steward.system_agents.your_agent.cartridge_main import YourAgentCartridge

your_agent = YourAgentCartridge()
kernel.register_agent(your_agent)
```

### Step 4: Add to Bhu Mandala (Topology)

```python
# In vibe_core/topology.py
AGENT_PLACEMENTS = {
    # ... existing agents ...
    "your_agent": AgentPlacement(
        layer="MAHARLOKA",  # Choose appropriate layer
        varna="BRAHMANA",   # Choose appropriate varna
        authority_level=7,
        radius=3,
        angle=45
    ),
}
```

---

## 🧰 CREATING TOOLS

### Tool Structure

```python
# tools/example_tool.py
from typing import Dict, Any

class ExampleTool:
    def __init__(self, kernel=None):
        self.kernel = kernel  # Optional kernel reference

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Result dictionary with 'status' and data
        """
        # Your tool logic
        return {
            "status": "success",
            "data": {}
        }
```

---

## 🔐 CONSTITUTIONAL OATH (GAD-000)

All agents MUST swear the Constitutional Oath.

### Why:

- Cryptographic identity binding
- Governance compliance
- Immutable ledger accountability

### Implementation:

```python
from vibe_core.bridge import OathMixin

class YourAgent(VibeAgent, OathMixin):
    def __init__(self):
        super().__init__()
        # Swear oath during initialization
        import asyncio
        asyncio.run(self.swear_constitutional_oath())
```

### Verification:

- Check logs: "🎖️ Constitutional Oath sworn by [agent_id]"
- Check ledger: oath event recorded

---

## 🧪 TESTING YOUR AGENT

### Unit Tests

```python
# tests/test_your_agent.py
import pytest
from steward.system_agents.your_agent.cartridge_main import YourAgentCartridge

def test_agent_initialization():
    agent = YourAgentCartridge()
    assert agent.agent_id == "your_agent"
    assert agent.version == "1.0.0"

def test_agent_manifest():
    agent = YourAgentCartridge()
    manifest = agent.get_manifest()
    assert manifest.agent_id == "your_agent"
    assert manifest.author == "Steward Protocol"

def test_agent_process():
    agent = YourAgentCartridge()
    task = Task(agent_id="your_agent", payload={"action": "test"})
    result = agent.process(task)
    assert result["status"] == "success"
```

### Integration Tests

```python
def test_agent_registration():
    kernel = RealVibeKernel()
    agent = YourAgentCartridge()
    kernel.register_agent(agent)

    assert "your_agent" in kernel.agent_registry
    assert kernel.agent_registry["your_agent"] == agent
```

---

## 📏 BEST PRACTICES

- Keep agents < 500 lines (single responsibility)
- Swear Constitutional Oath (GAD-000 compliance)
- Provide complete manifest (author, description, capabilities)
- Map to Bhu Mandala (topology integration)
- Write tests (unit + integration)
- Document tools (clear docstrings)
- Handle errors gracefully (no crashes)
- Log important events (use logger)

---

## 🚫 COMMON MISTAKES

- ❌ Forgetting to swear Constitutional Oath
- ❌ Missing manifest fields (author, description)
- ❌ Not registering in kernel
- ❌ Creating monoliths > 1000 lines
- ❌ Hardcoding paths (use project_root)
- ❌ Not handling async oath ceremony
- ❌ Skipping topology placement

---

## 📚 REFERENCE AGENTS

### Good Examples:

- `steward/system_agents/watchman/` - Simple, clean (< 300 lines)
- `steward/system_agents/oracle/` - Tool-based architecture
- `steward/system_agents/envoy/` - Well-documented

### Complex Examples:

- `steward/system_agents/herald/` - Multiple tools, 940 lines
- `steward/system_agents/civic/` - Governance, 1003 lines

---

## 🎯 CHECKLIST

Before submitting your agent:

- [ ] Agent extends VibeAgent + OathMixin
- [ ] Constitutional Oath sworn in init
- [ ] get_manifest() returns complete AgentManifest
- [ ] process() method implements task handling
- [ ] Agent registered in kernel boot
- [ ] Topology placement defined
- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Documentation added
- [ ] Code < 500 lines (or justified if larger)

**Ready to build?** Start with the template above and reference existing agents.
