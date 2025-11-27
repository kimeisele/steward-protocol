# Steward Protocol Development Guidelines

## Architecture Overview

This project uses a **clean 3-layer architecture** to eliminate circular dependencies and provide clear separation of concerns.

**See:** `docs/ADR-002-three-layer-architecture.md` for detailed rationale.

---

## Layer Architecture Rules

### ✅ DO

#### Layer 1: Protocols (vibe_core/protocols/)
- ✅ Define **ONLY abstract base classes and interfaces**
- ✅ Import from: `stdlib`, `abc`, `typing`, `dataclasses`, `enum`
- ✅ Use `@abstractmethod` decorators
- ✅ Write clear docstrings for each abstract method
- ✅ Export via `__init__.py` for centralized imports

**Example:**
```python
# vibe_core/protocols/agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class VibeAgent(ABC):
    """Abstract protocol for all agents."""

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return result."""
        pass
```

#### Layer 2: Implementations
- ✅ Import **ONLY from Layer 1** (vibe_core.protocols)
- ✅ Implement business logic
- ✅ Create concrete classes inheriting from protocols
- ✅ Place in appropriate subdirectories (agents/, runtime/, etc.)
- ✅ Use dependency injection for dependencies

**Example:**
```python
# vibe_core/agents/llm_agent.py
from vibe_core.protocols import VibeAgent

class SimpleLLMAgent(VibeAgent):
    """Concrete LLM agent implementation."""

    async def process(self, task):
        # Implementation here
        pass
```

#### Layer 3: Wiring & Configuration
- ✅ Import from **Layers 1 AND 2**
- ✅ Use `config/phoenix.yaml` for dynamic configuration
- ✅ Implement dependency injection
- ✅ Provide initialization hooks
- ✅ Handle optional/missing components gracefully

**Example:**
```python
# vibe_core/phoenix_config.py
from vibe_core.protocols import VibeAgent
from vibe_core.agents.llm_agent import SimpleLLMAgent

class PhoenixConfigEngine:
    def wire_agent(self, agent_config):
        # Dynamically wire based on config
        pass
```

---

### ❌ DON'T

#### Layer 1: Protocols
- ❌ NO concrete implementations in Layer 1
- ❌ NO imports from Layer 2 (agent implementations, services)
- ❌ NO imports from Layer 3 (wiring, config)
- ❌ NO try/except ImportError blocks (except for truly optional stdlib)
- ❌ NO business logic

#### Layer 2: Implementations
- ❌ NO sibling imports (MyAgent importing AnotherAgent)
- ❌ NO imports from Layer 1 ABCs for anything except inheritance
- ❌ NO wiring or orchestration logic
- ❌ NO try/except ImportError for internal modules
- ❌ NO circular dependencies (A → B → A)

#### Layer 3: Wiring
- ❌ NO implementations (business logic) in Layer 3
- ❌ NO hardcoded class instantiation (use config)
- ❌ NO direct agent instantiation without configuration

#### All Layers
- ❌ **NEVER use try/except ImportError for internal modules**
  - Exception: External libraries (openai, tavily, etc.) can use try/except
  - Exception: Optional features that gracefully degrade
- ❌ **If you're adding try/except ImportError, you're doing it wrong**

---

## Common Patterns

### Pattern 1: Adding a New Protocol

**Step 1:** Define in Layer 1
```python
# vibe_core/protocols/my_protocol.py
from abc import ABC, abstractmethod

class MyProtocol(ABC):
    @abstractmethod
    def do_something(self) -> str:
        """Do something."""
        pass
```

**Step 2:** Export from Layer 1
```python
# vibe_core/protocols/__init__.py
from .my_protocol import MyProtocol

__all__ = [..., "MyProtocol"]
```

**Step 3:** Implement in Layer 2
```python
# vibe_core/services/my_implementation.py
from vibe_core.protocols import MyProtocol

class MyImplementation(MyProtocol):
    def do_something(self) -> str:
        return "something"
```

---

### Pattern 2: Adding a New Agent

**Step 1:** Check protocol exists
```python
from vibe_core.protocols import VibeAgent  # Layer 1
```

**Step 2:** Create implementation
```python
# steward/system_agents/my_agent/cartridge_main.py
from vibe_core.protocols import VibeAgent, AgentManifest

class MyAgent(VibeAgent):
    def __init__(self, ...):
        super().__init__(
            agent_id="my_agent",
            name="My Agent",
            # ...
        )

    async def process(self, task):
        # Implementation
        pass
```

**Step 3:** Register in phoenix.yaml
```yaml
agents:
  system_agents:
    - name: "MyAgent"
      class: "steward.system_agents.my_agent.cartridge_main:MyAgent"
      protocol: "VibeAgent"
      enabled: true
```

---

### Pattern 3: Using Phoenix for Wiring

**Don't do this (hardcoded):**
```python
# ❌ WRONG - Hardcoded import
from steward.system_agents.discoverer.agent import Discoverer

discoverer = Discoverer()
```

**Do this instead (configured):**
```python
# ✅ RIGHT - Phoenix wired
from vibe_core.phoenix_config import get_phoenix_engine

phoenix = get_phoenix_engine()
agents = phoenix.wire_agents()
discoverer = agents['DiscoveryAgent']()  # Class, not instance
```

---

## Testing Guidelines

### Unit Testing
- Test implementations **in isolation** from other layers
- Mock Layer 1 protocols using `unittest.mock`
- Don't test Layer 1 (it's just interfaces)

```python
from unittest.mock import Mock
from vibe_core.protocols import VibeAgent
from vibe_core.agents.my_agent import MyAgent

def test_my_agent():
    agent = MyAgent()
    assert isinstance(agent, VibeAgent)
```

### Integration Testing
- Test Layer 2 ↔ Layer 1 compatibility
- Test Layer 3 wiring
- Use Phoenix engine in tests

```python
def test_phoenix_wiring():
    from vibe_core.phoenix_config import get_phoenix_engine
    phoenix = get_phoenix_engine()
    agents = phoenix.wire_agents()
    assert len(agents) == 12
```

### Import Testing
- Verify no circular imports
- Verify Layer 1 imports cleanly
- Verify Phoenix initializes

```python
def test_no_circular_imports():
    from vibe_core.protocols import VibeAgent
    from steward.system_agents.discoverer.agent import Discoverer
    assert issubclass(Discoverer, VibeAgent)
```

---

## Code Review Checklist

When reviewing PRs, check:

### Layer 1 Changes
- [ ] Only ABCs and dataclasses?
- [ ] Only stdlib/abc imports?
- [ ] Clear docstrings?
- [ ] Exported in `__init__.py`?

### Layer 2 Changes
- [ ] Implements Layer 1 protocol?
- [ ] Only imports Layer 1?
- [ ] No sibling imports?
- [ ] No try/except ImportError for internal modules?

### Layer 3 Changes
- [ ] Uses config, not hardcoded?
- [ ] Gracefully handles missing components?
- [ ] Updated `config/phoenix.yaml`?

### Any Layer
- [ ] No new try/except ImportError for internal modules?
- [ ] No circular imports introduced?
- [ ] Tests pass?

---

## FAQ

**Q: Can I import Agent A from Agent B?**
A: No. If you need shared logic, extract it to a utility in Layer 2, or access via Phoenix's registry.

**Q: Can I put business logic in Layer 1?**
A: No. Layer 1 is pure interface. Put logic in Layer 2 implementations.

**Q: Can I hardcode agent instantiation?**
A: No. Use Phoenix config engine for dynamic wiring.

**Q: What if I need an optional feature?**
A: Use graceful degradation in Layer 2. Have a fallback behavior. Don't use try/except ImportError.

**Q: How do I add a new Layer 1 protocol?**
A: See "Pattern 1: Adding a New Protocol" above.

**Q: Why can't I import agent B from agent A?**
A: To prevent circular dependencies and maintain testability. If you need to coordinate, use Phoenix's agent registry instead.

---

## Related Documents

- `docs/ADR-002-three-layer-architecture.md` - Architectural Decision Record
- `BLOCKER2_FINAL_COMPLETION_REPORT.md` - Implementation details
- `config/phoenix.yaml` - Configuration example
