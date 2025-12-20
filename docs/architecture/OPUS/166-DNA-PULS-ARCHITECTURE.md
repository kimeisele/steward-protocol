# OPUS-166: DNA + PULS - Agent State Architecture

## Status: ACTIVE
## Created: 2024-12-20

---

## Overview

Separates agent state into two orthogonal concerns:

| Layer | File | Lifecycle | Git | Purpose |
|-------|------|-----------|-----|---------|
| **DNA** | `steward.json` | Static | ✅ Committed | Identity, capabilities |
| **PULS** | `node.json` | Ephemeral | ❌ .gitignored | Runtime presence, mailbox |

## Rationale

### Three Types of Agent State

1. **DNA (steward.json)** - "Who you ARE"
   - Identity, permissions, capabilities
   - Static, version-controlled
   - Survives across all sessions
   - Already exists

2. **PULS (node.json)** - "What you're doing RIGHT NOW"
   - Online/offline status, heartbeat
   - Current KALA time state
   - Mailbox for inter-agent messages
   - **Ephemeral** - disappears when kernel stops
   - **NEW** - this OPUS

3. **Memory (State Holon Sync)** - "What you've experienced"
   - Task history, karma, completed actions
   - Persistent, committed to git
   - Already exists (OPUS-096)

### The Key Insight

When the kernel stops and `node.json` is deleted, the agent IS offline.
The file's existence represents reality - not a bug, the feature.

## Architecture

```
vibe_core/cartridges/agent_city/dharma/
├── steward.json      # DNA - Static identity (git-committed)
├── node.json         # PULS - Ephemeral presence (.gitignored)
└── .state/           # Memory - State Holon Sync (OPUS-096)
```

### node.json Schema

```json
{
  "status": "online",
  "pulse_at": "2024-12-20T10:30:00Z",
  "kala": {
    "sun_phase": "MIDDAY",
    "moon_phase": "WAXING_GIBBOUS",
    "tithi": 11,
    "paksha": "shukla",
    "rhythm_intensity": 0.78
  },
  "mailbox": [
    {
      "from": "envoy",
      "to": "dharma",
      "type": "signal",
      "payload": {"action": "review_required"},
      "sent_at": "2024-12-20T10:29:45Z"
    }
  ],
  "synapses": {
    "connected_to": ["envoy", "librarian"],
    "last_ping": "2024-12-20T10:29:50Z"
  }
}
```

## Lifecycle Integration

### On Boot (PRITHVI phase)

```python
# BootOrchestrator._act()
for cartridge in discovered_cartridges:
    NodeState.create(cartridge.path, status="booting")
```

### On Pulse (PRANA cycle)

```python
# PranaOrchestrator._act()
for cartridge in active_cartridges:
    NodeState.pulse(
        cartridge.path,
        status="online",
        kala_state=kala_plugin.get_state()
    )
```

### On Shutdown

```python
# BootOrchestrator.shutdown()
for cartridge in registered_cartridges:
    NodeState.die(cartridge.path)  # Deletes node.json
```

## Implementation

### NodeState Class

Located in `vibe_core/state/node_state.py`:

```python
class NodeState:
    """
    Ephemeral runtime state for cartridges.

    NOT persisted to git - represents live presence only.
    File existence = agent is alive.
    """

    NODE_FILE = "node.json"

    @staticmethod
    def get_path(cartridge_dir: Path) -> Path:
        return cartridge_dir / NodeState.NODE_FILE

    @staticmethod
    def create(cartridge_dir: Path, status: str = "booting") -> None:
        """Create node.json - agent is coming alive."""

    @staticmethod
    def pulse(cartridge_dir: Path, status: str, kala_state: dict) -> None:
        """Update heartbeat - agent is still alive."""

    @staticmethod
    def die(cartridge_dir: Path) -> None:
        """Delete node.json - agent is shutting down."""

    @staticmethod
    def is_alive(cartridge_dir: Path) -> bool:
        """Check if agent is alive (node.json exists)."""
```

### Mailbox Protocol

Inter-agent messaging via node.json mailbox:

```python
# Agent A sends message to Agent B
NodeState.send_message(
    from_agent="envoy",
    to_cartridge=dharma_path,
    msg_type="signal",
    payload={"action": "review_required"}
)

# Agent B reads mailbox
messages = NodeState.read_mailbox(dharma_path)
for msg in messages:
    process(msg)
    NodeState.ack_message(dharma_path, msg["id"])
```

## .gitignore Integration

Add to root `.gitignore`:

```gitignore
# OPUS-166: Ephemeral node state (runtime only)
**/node.json
```

## Relationship to Existing Systems

| System | Concern | This OPUS |
|--------|---------|-----------|
| steward.json | Static DNA | Unchanged - complements |
| State Holon Sync | Persistent memory | Unchanged - orthogonal |
| KALA Plugin | Time state | Writes to node.json |
| PRANA | Pulse cycle | Updates node.json |
| BootOrchestrator | Lifecycle | Creates/deletes node.json |

## Benefits

1. **Clear separation**: Identity vs presence vs memory
2. **No git pollution**: Runtime state doesn't create commits
3. **Reality representation**: File exists = agent alive
4. **Inter-agent comms**: Mailbox for synaptic messaging
5. **KALA integration**: Current cosmic time in each agent

## Test Plan

1. Unit tests for NodeState CRUD operations
2. E2E: kernel start creates node.json
3. E2E: kernel pulse updates node.json with KALA
4. E2E: kernel shutdown deletes node.json
5. E2E: mailbox send/receive between agents

---

## References

- OPUS-096: State Holon Sync (persistent state)
- OPUS-165: KALA Eternal Time Plugin
- OPUS-087: PRANA Orchestrator
- OPUS-095: Cognitive Abstraction
