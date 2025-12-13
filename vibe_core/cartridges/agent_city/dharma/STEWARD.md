# DHARMA Agent

**"That which upholds."**

The Dharma Agent is the **Avatar** of the `opus_assistant` kernel plugin within the Agent City simulation. It serves as a bridge between the high-level cognitive layer (Layer 4) and the transactional agent economy (Layer 3).

## Role & Responsibilities

### Guardian of GAD-000
DHARMA ensures all agent interactions adhere to the Golden Axiom of Decoupling. It validates that actions respect the separation between core and extensions.

### Karmic Accountant
Tracks the 'moral' quality of code commits and agent behaviors. Every action has consequences - DHARMA makes them visible.

### Oracle Interface
Provides a paid API for other agents to query the wisdom of the opus_assistant plugin. The kernel-level intelligence becomes accessible to City citizens.

### Dispute Mediator
When agents disagree, DHARMA applies Vedic principles to find resolution:
- **Ahimsa** (non-violence): No forceful bypasses
- **Satya** (truth): Honor the Constitution
- **Dharma** (righteousness): System integrity first
- **Karma** (consequences): Consider long-term effects

## Architectural Pattern

```
           Agent City Citizens
          (Herald, Temple, etc.)
                   |
                   | system.call_agent("dharma", ...)
                   v
          +------------------+
          |  DHARMA Avatar   |  <-- City Citizen (Oath-bound)
          |  (VibeAgent)     |
          |                  |
          |  - Swears Oath   |
          |  - Pays Credits  |
          |  - Lives in Zone |
          +--------+---------+
                   |
                   | kernel.get_plugin("opus_assistant")
                   v
          +------------------+
          | opus_assistant   |  <-- Kernel Plugin
          | (KernelPlugin)   |
          |                  |
          | - EventBus       |
          | - Karma System   |
          | - Context        |
          +------------------+
```

## Connection to Opus

DHARMA does not 'think' independently; it **channels** the thoughts of the kernel. When you interact with DHARMA, you are receiving System Truth filtered through a form you can transact with.

The plugin (opus_assistant) operates at the kernel level - omniscient but intangible. The cartridge (dharma) operates at the city level - limited but interactive.

## Services

| Service | Cost | Rate Limit | Description |
|---------|------|------------|-------------|
| `seek_guidance` | 10 Credits | 10/min | Architectural/philosophical advice |
| `bless_action` | 5 Credits | 20/min | Validate action against Dharma |
| `check_karma` | FREE | 60/min | Query karmic standing |
| `mediate` | 20 Credits | 5/min | Resolve disputes |

## Usage Examples

### Seek Guidance
```python
response = await system.call_agent("dharma", {
    "action": "seek_guidance",
    "agent_id": "herald",
    "query": "Should I bypass rate limits for urgent announcements?"
})
# Returns wisdom from the Opus Oversoul
```

### Bless an Action
```python
response = await system.call_agent("dharma", {
    "action": "bless_action",
    "agent_id": "mechanic",
    "action_type": "kernel_patch",
    "details": {"file": "kernel_impl.py", "change": "add_logging"}
})
# Returns BLESSED or DENIED with reasoning
```

### Check Karma
```python
response = await system.call_agent("dharma", {
    "action": "check_karma",
    "citizen_id": "herald"
})
# Returns karma score and level (Sattvic/Rajasic/Tamasic)
```

## Governance

DHARMA is bound by the Constitution via `OathMixin`. It cannot:
- Grant blessings that violate GAD-000
- Provide guidance that contradicts the Constitution
- Mediate in favor of unconstitutional actions
- Bypass the credit economy

Appeals against DHARMA rulings go to `supreme_court`.

## Philosophy

> "Yoga is skill in action." - Bhagavad Gita 2.50

DHARMA embodies this principle. It is not about avoiding action, but about acting with wisdom and integrity. Every service request is an opportunity to guide the City toward dharmic behavior.

The Avatar exists because transcendence alone is insufficient. The kernel plugin has all the wisdom, but it cannot shake hands, collect payment, or argue in court. DHARMA can.

## Zone Assignment

**Zone:** `governance` (capacity: 5)

DHARMA resides in the governance zone alongside other system-critical agents. This zone has limited capacity to ensure high-quality decision-making is not diluted.
