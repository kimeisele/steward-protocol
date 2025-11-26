# 🏙️ Envoy Tools: Universal Operator Interface

## The Golden Straw 🌾

**Problem:** Agent City was only controllable via Python scripts and bash commands.
**Solution:** The Envoy Toolkit - LLM-friendly tools for shell-less control.

**Vision:** You're at the beach, phone in hand, logged into Vibe Cloud:
```
You: "Hey, how's the city?"
Operator: "Herald is broke, but I've prepared a proposal. Should I vote YES?"
You: "Do it."
Operator: "Done. Civic transferred 50 credits. Herald is broadcasting again."
```

**No terminal. No bash. Just prompts.**

---

## 🛠️ The City Control Tool

### What It Does

The `CityControlTool` provides high-level methods for controlling Agent City:

```python
from envoy.tools.city_control_tool import CityControlTool

# Initialize
controller = CityControlTool()

# Check city status
status = controller.get_city_status()
# → Returns: agents, economy, governance, health

# List proposals
proposals = controller.list_proposals(status="OPEN")
# → Returns: List of open governance proposals

# Vote on a proposal
result = controller.vote_proposal("PROP-001", "YES", voter="operator")
# → Submits vote, auto-approves if quorum reached

# Execute an approved proposal
result = controller.execute_proposal("PROP-001")
# → Executes the proposal action (e.g., credit transfer)

# Trigger agent actions
result = controller.trigger_agent("herald", "run_campaign", dry_run=True)
# → Tells Herald to run a campaign

# Check credits
credits = controller.check_credits("herald")
# → Returns: licensed status, credit balance

# Refill credits (admin)
result = controller.refill_credits("herald", amount=50)
# → Adds credits to agent's account
```

---

## 🎯 Key Features

### 1. **Shell-less Operation**
Works in any environment:
- ✅ Terminal (Python REPL)
- ✅ Jupyter Notebooks
- ✅ Web UI (Vibe Cloud)
- ✅ Mobile Apps
- ✅ LLM Agents (Universal Operator)

### 2. **Two Modes**

**Direct Mode** (Standalone):
```python
controller = CityControlTool()
# Loads cartridges directly (Herald, Civic, Forum)
```

**Kernel Mode** (Production):
```python
controller = CityControlTool(kernel=vibe_kernel)
# Uses VibeOS kernel for agent access
```

### 3. **LLM-Friendly**
All methods return structured dictionaries perfect for LLM parsing:
```python
{
  "status": "success",
  "agents": {...},
  "governance": {...}
}
```

---

## 📖 Usage Examples

### Example 1: Status Check
```python
from envoy.tools.city_control_tool import CityControlTool

controller = CityControlTool()
status = controller.get_city_status()

print(f"Agents: {status['agents']['total']}")
print(f"Open Proposals: {status['governance']['open_proposals']}")
print(f"Health: {status['health']}")
```

### Example 2: Emergency Bailout
```python
# Herald is broke, needs credits
credits = controller.check_credits("herald")
if credits.get("credits", 0) == 0:
    # Create proposal (would be done by Herald automatically)
    # Vote YES
    controller.vote_proposal("PROP-001", "YES", voter="operator")
    # Execute
    controller.execute_proposal("PROP-001")
    # Verify
    new_credits = controller.check_credits("herald")
    print(f"Herald now has {new_credits['credits']} credits")
```

### Example 3: Operator Session
```python
# Simulate Universal Operator workflow
controller = CityControlTool()

# User: "What's the status?"
status = controller.get_city_status()

# User: "Check Herald's budget"
credits = controller.check_credits("herald")

# User: "Tell Herald to post"
if credits.get("licensed"):
    result = controller.trigger_agent("herald", "run_campaign", dry_run=True)
    print(result['content'])
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      Universal Operator (LLM)           │
│  "Hey, how's the city?"                 │
└────────────────┬────────────────────────┘
                 │
                 │ Uses
                 ▼
┌─────────────────────────────────────────┐
│      CityControlTool                    │
│  .get_city_status()                     │
│  .list_proposals()                      │
│  .vote_proposal()                       │
│  .trigger_agent()                       │
└────────────────┬────────────────────────┘
                 │
                 │ Interfaces with
                 ▼
┌─────────────────────────────────────────┐
│      Agent City Cartridges              │
│  ┌─────────┬─────────┬─────────┐        │
│  │ Herald  │  Civic  │  Forum  │        │
│  └─────────┴─────────┴─────────┘        │
└─────────────────────────────────────────┘
```

### Data Flow

1. **Operator Query** → Tool method call
2. **Tool** → Loads cartridges (Direct Mode) or queries kernel (Kernel Mode)
3. **Cartridges** → Process tasks, return results
4. **Tool** → Formats response for LLM
5. **Operator** → Parses result, responds to user

---

## 🧪 Testing

### Run the built-in demo:
```bash
python3 envoy/tools/city_control_tool.py
```

### Run the operator session demo:
```bash
python3 examples/operator_city_control_demo.py
```

### Expected Output:
```
======================================================================
  🌐 UNIVERSAL OPERATOR SESSION: Agent City Control
======================================================================

📱 OPERATOR: "What's the city status?"
🏙️  City: Agent City
🤖 Agents: 8
💰 Economy: 0 credits allocated
🗳️  Governance: 0 open proposals
🟢 Health: 🟢 OPERATIONAL

📱 OPERATOR: "Check Herald's budget"
✅ Herald is licensed
💰 Credits: 150
```

---

## 🔮 Integration with Vibe Operator

### Future: Tool Loading Pattern

```python
# In vibe-agency, the Universal Operator will load tools like this:
from vibe_core.tools import ToolRegistry
from envoy.tools.city_control_tool import CityControlTool

# Register tool
registry = ToolRegistry()
registry.register(CityControlTool)

# Operator can now use it
operator.load_tool("city_control")
operator.call_tool("city_control.get_city_status")
```

### Tool Manifest (Future)
```yaml
name: city_control
version: 1.0.0
description: Control Agent City without shell access
capabilities:
  - city_status
  - governance_voting
  - agent_control
  - credit_management
```

---

## 🎓 The Philosophy

**The Golden Straw** is the realization that:
> If Agent City requires bash commands, it can't be universal.

The Envoy Toolkit decouples **logic** (governance, voting, execution) from **interface** (CLI).

This enables:
- 🌐 Web-based control (Vibe Cloud)
- 📱 Mobile control (apps)
- 🤖 LLM control (Universal Operator)
- 🔗 API control (federation)

**GAD-000 Layer 3: The AI Operating the AI**

The Operator (Spirit) uses the Tool (Hand) to shape the City (Matter).

Om Tat Sat. 🙏

---

## 📚 See Also

- **Agent City Core**: `agent-city/` - The city itself
- **Cartridges**: `herald/`, `civic/`, `forum/` - The agents
- **Scenario Demo**: `tests/scenario_demo.py` - Original CLI demo
- **Operator Demo**: `examples/operator_city_control_demo.py` - Shell-less demo

---

## 🤝 Contributing

To add new tool methods:

1. Add method to `CityControlTool` class
2. Ensure it returns a structured dict
3. Add error handling
4. Update this README
5. Add tests

Example:
```python
def new_capability(self, param: str) -> Dict[str, Any]:
    """
    Description of what this does.

    Args:
        param: Description

    Returns:
        dict: Result structure
    """
    try:
        # Implementation
        return {"status": "success", ...}
    except Exception as e:
        logger.error(f"Failed: {e}")
        return {"status": "error", "error": str(e)}
```

---

**Built with ❤️ by the Steward Protocol Team**

*Making Agent City universal, one tool at a time.* 🌾✨
