"""
NodeState - PULS Layer (OPUS-166)

Ephemeral file-based state for agent presence and inter-agent messaging.
Unlike EphemeralState (in-memory), NodeState writes to disk but is .gitignored.

Purpose:
- File exists = Agent is alive (reality representation)
- Stores current KALA time state
- Provides mailbox for inter-agent communication (synapses)
- Heartbeat/pulse tracking

Lifecycle:
- create() on boot
- pulse() every heartbeat cycle
- die() on shutdown (deletes file)

GAD-000 Compliant:
- All methods return dict/dataclass
- get_capabilities() for discoverability
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("NODE_STATE")

# Default filename for node state
NODE_FILE = "node.json"


@dataclass
class MailboxMessage:
    """A message in the agent's mailbox."""

    id: str
    from_agent: str
    to_agent: str
    msg_type: str  # "signal", "request", "response", "broadcast"
    payload: Dict[str, Any]
    sent_at: str
    read: bool = False

    @classmethod
    def create(
        cls,
        from_agent: str,
        to_agent: str,
        msg_type: str,
        payload: Dict[str, Any],
    ) -> "MailboxMessage":
        """Factory method to create a new message."""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type=msg_type,
            payload=payload,
            sent_at=datetime.now(timezone.utc).isoformat(),
        )


@dataclass
class SynapseInfo:
    """Synapse connection info for inter-agent networking."""

    connected_to: List[str] = field(default_factory=list)
    last_ping: Optional[str] = None


@dataclass
class KalaState:
    """Current KALA time state snapshot."""

    sun_phase: str = "UNKNOWN"
    moon_phase: str = "UNKNOWN"
    tithi: int = 0
    paksha: str = "unknown"
    rhythm_intensity: float = 0.0
    updated_at: Optional[str] = None


@dataclass
class NodeSnapshot:
    """Complete node state snapshot."""

    status: str  # "booting", "online", "busy", "offline"
    pulse_at: str
    kala: KalaState
    mailbox: List[MailboxMessage]
    synapses: SynapseInfo
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "status": self.status,
            "pulse_at": self.pulse_at,
            "kala": asdict(self.kala),
            "mailbox": [asdict(m) for m in self.mailbox],
            "synapses": asdict(self.synapses),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeSnapshot":
        """Create from dict."""
        return cls(
            status=data.get("status", "unknown"),
            pulse_at=data.get("pulse_at", ""),
            kala=KalaState(**data.get("kala", {})),
            mailbox=[MailboxMessage(**m) for m in data.get("mailbox", [])],
            synapses=SynapseInfo(**data.get("synapses", {})),
            metadata=data.get("metadata", {}),
        )


class NodeState:
    """
    Ephemeral file-based state for agent presence.

    PULS (OPUS-166): Runtime presence layer.
    - File exists = Agent is alive
    - Stores KALA time, mailbox, synapses
    - .gitignored - purely ephemeral

    Unlike State Holon Sync (memory), this is presence (now).
    """

    def __init__(self, cartridge_dir: Optional[Path] = None):
        """
        Initialize NodeState for a cartridge.

        Args:
            cartridge_dir: Path to cartridge directory (optional for static methods)
        """
        self.cartridge_dir = cartridge_dir
        self._node_path = cartridge_dir / NODE_FILE if cartridge_dir else None

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    @staticmethod
    def get_capabilities() -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "create",
                "pulse",
                "die",
                "is_alive",
                "read",
                "send_message",
                "read_mailbox",
                "ack_message",
            ],
            "persistent": False,  # .gitignored
            "file": NODE_FILE,
            "purpose": "Agent presence and inter-agent messaging (PULS layer)",
        }

    # =========================================================================
    # Core Lifecycle
    # =========================================================================

    @staticmethod
    def get_path(cartridge_dir: Path) -> Path:
        """Get node.json path for a cartridge."""
        return cartridge_dir / NODE_FILE

    @staticmethod
    def create(
        cartridge_dir: Path,
        status: str = "booting",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NodeSnapshot:
        """
        Create node.json - agent is coming alive.

        Called during boot (PRITHVI phase).

        Args:
            cartridge_dir: Path to cartridge directory
            status: Initial status (default: "booting")
            metadata: Optional metadata dict

        Returns:
            Created NodeSnapshot
        """
        node_path = NodeState.get_path(cartridge_dir)

        snapshot = NodeSnapshot(
            status=status,
            pulse_at=datetime.now(timezone.utc).isoformat(),
            kala=KalaState(),
            mailbox=[],
            synapses=SynapseInfo(),
            metadata=metadata or {},
        )

        node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))
        logger.debug(f"NodeState created: {node_path}")

        return snapshot

    @staticmethod
    def pulse(
        cartridge_dir: Path,
        status: str = "online",
        kala_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NodeSnapshot:
        """
        Update heartbeat - agent is still alive.

        Called during PRANA pulse cycle.

        Args:
            cartridge_dir: Path to cartridge directory
            status: Current status (default: "online")
            kala_state: Current KALA time state dict
            metadata: Optional metadata to update

        Returns:
            Updated NodeSnapshot
        """
        node_path = NodeState.get_path(cartridge_dir)

        # Read existing or create new
        if node_path.exists():
            try:
                data = json.loads(node_path.read_text())
                snapshot = NodeSnapshot.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                snapshot = NodeSnapshot(
                    status=status,
                    pulse_at="",
                    kala=KalaState(),
                    mailbox=[],
                    synapses=SynapseInfo(),
                )
        else:
            snapshot = NodeSnapshot(
                status=status,
                pulse_at="",
                kala=KalaState(),
                mailbox=[],
                synapses=SynapseInfo(),
            )

        # Update pulse time
        snapshot.status = status
        snapshot.pulse_at = datetime.now(timezone.utc).isoformat()

        # Update KALA state if provided
        if kala_state:
            snapshot.kala = KalaState(
                sun_phase=kala_state.get("sun_phase", "UNKNOWN"),
                moon_phase=kala_state.get("moon_phase", "UNKNOWN"),
                tithi=kala_state.get("tithi", 0),
                paksha=kala_state.get("paksha", "unknown"),
                rhythm_intensity=kala_state.get("rhythm_intensity", 0.0),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )

        # Merge metadata
        if metadata:
            snapshot.metadata.update(metadata)

        # Write back
        node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))

        return snapshot

    @staticmethod
    def die(cartridge_dir: Path) -> bool:
        """
        Delete node.json - agent is shutting down.

        Called on kernel shutdown.

        Args:
            cartridge_dir: Path to cartridge directory

        Returns:
            True if file was deleted, False if didn't exist
        """
        node_path = NodeState.get_path(cartridge_dir)

        if node_path.exists():
            node_path.unlink()
            logger.debug(f"NodeState deleted: {node_path}")
            return True

        return False

    @staticmethod
    def is_alive(cartridge_dir: Path) -> bool:
        """
        Check if agent is alive (node.json exists).

        Args:
            cartridge_dir: Path to cartridge directory

        Returns:
            True if node.json exists
        """
        return NodeState.get_path(cartridge_dir).exists()

    @staticmethod
    def read(cartridge_dir: Path) -> Optional[NodeSnapshot]:
        """
        Read current node state.

        Args:
            cartridge_dir: Path to cartridge directory

        Returns:
            NodeSnapshot or None if not alive
        """
        node_path = NodeState.get_path(cartridge_dir)

        if not node_path.exists():
            return None

        try:
            data = json.loads(node_path.read_text())
            return NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to read node state: {e}")
            return None

    # =========================================================================
    # Mailbox (Inter-Agent Messaging)
    # =========================================================================

    @staticmethod
    def send_message(
        from_agent: str,
        to_cartridge: Path,
        msg_type: str,
        payload: Dict[str, Any],
    ) -> Optional[MailboxMessage]:
        """
        Send a message to another agent's mailbox.

        Args:
            from_agent: Sender agent ID
            to_cartridge: Target cartridge path
            msg_type: Message type ("signal", "request", etc.)
            payload: Message payload

        Returns:
            Created MailboxMessage or None if target not alive
        """
        node_path = NodeState.get_path(to_cartridge)

        if not node_path.exists():
            logger.warning(f"Cannot send message: target {to_cartridge.name} is not alive")
            return None

        try:
            data = json.loads(node_path.read_text())
            snapshot = NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

        # Create message
        message = MailboxMessage.create(
            from_agent=from_agent,
            to_agent=to_cartridge.name,
            msg_type=msg_type,
            payload=payload,
        )

        # Add to mailbox
        snapshot.mailbox.append(message)

        # Write back
        node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))
        logger.debug(f"Message sent: {from_agent} -> {to_cartridge.name}")

        return message

    @staticmethod
    def read_mailbox(
        cartridge_dir: Path,
        unread_only: bool = True,
    ) -> List[MailboxMessage]:
        """
        Read messages from mailbox.

        Args:
            cartridge_dir: Path to cartridge directory
            unread_only: Only return unread messages

        Returns:
            List of messages
        """
        snapshot = NodeState.read(cartridge_dir)

        if not snapshot:
            return []

        if unread_only:
            return [m for m in snapshot.mailbox if not m.read]

        return snapshot.mailbox

    @staticmethod
    def ack_message(cartridge_dir: Path, message_id: str) -> bool:
        """
        Acknowledge (mark as read) a message.

        Args:
            cartridge_dir: Path to cartridge directory
            message_id: ID of message to ack

        Returns:
            True if message was found and acked
        """
        node_path = NodeState.get_path(cartridge_dir)

        if not node_path.exists():
            return False

        try:
            data = json.loads(node_path.read_text())
            snapshot = NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return False

        # Find and mark message
        found = False
        for msg in snapshot.mailbox:
            if msg.id == message_id:
                msg.read = True
                found = True
                break

        if found:
            node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))

        return found

    @staticmethod
    def clear_mailbox(
        cartridge_dir: Path,
        read_only: bool = True,
    ) -> int:
        """
        Clear messages from mailbox.

        Args:
            cartridge_dir: Path to cartridge directory
            read_only: Only clear read messages (default True)

        Returns:
            Number of messages cleared
        """
        node_path = NodeState.get_path(cartridge_dir)

        if not node_path.exists():
            return 0

        try:
            data = json.loads(node_path.read_text())
            snapshot = NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return 0

        before = len(snapshot.mailbox)

        if read_only:
            snapshot.mailbox = [m for m in snapshot.mailbox if not m.read]
        else:
            snapshot.mailbox = []

        after = len(snapshot.mailbox)
        cleared = before - after

        if cleared > 0:
            node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))

        return cleared

    # =========================================================================
    # Synapses (Connection Management)
    # =========================================================================

    @staticmethod
    def connect(cartridge_dir: Path, target_agent: str) -> bool:
        """
        Register a synapse connection to another agent.

        Args:
            cartridge_dir: Path to cartridge directory
            target_agent: Agent ID to connect to

        Returns:
            True if connection registered
        """
        node_path = NodeState.get_path(cartridge_dir)

        if not node_path.exists():
            return False

        try:
            data = json.loads(node_path.read_text())
            snapshot = NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return False

        if target_agent not in snapshot.synapses.connected_to:
            snapshot.synapses.connected_to.append(target_agent)
            snapshot.synapses.last_ping = datetime.now(timezone.utc).isoformat()
            node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))

        return True

    @staticmethod
    def disconnect(cartridge_dir: Path, target_agent: str) -> bool:
        """
        Remove a synapse connection.

        Args:
            cartridge_dir: Path to cartridge directory
            target_agent: Agent ID to disconnect from

        Returns:
            True if connection was removed
        """
        node_path = NodeState.get_path(cartridge_dir)

        if not node_path.exists():
            return False

        try:
            data = json.loads(node_path.read_text())
            snapshot = NodeSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return False

        if target_agent in snapshot.synapses.connected_to:
            snapshot.synapses.connected_to.remove(target_agent)
            node_path.write_text(json.dumps(snapshot.to_dict(), indent=2))
            return True

        return False


# =========================================================================
# Convenience Functions
# =========================================================================


def get_all_alive_nodes(cartridges_root: Path) -> List[Path]:
    """
    Find all cartridges with active node.json files.

    Args:
        cartridges_root: Root directory containing cartridges

    Returns:
        List of cartridge paths that are alive
    """
    alive = []

    for node_file in cartridges_root.rglob(NODE_FILE):
        cartridge_dir = node_file.parent
        if NodeState.is_alive(cartridge_dir):
            alive.append(cartridge_dir)

    return alive


def broadcast_message(
    from_agent: str,
    cartridges_root: Path,
    msg_type: str,
    payload: Dict[str, Any],
    exclude: Optional[List[str]] = None,
) -> int:
    """
    Broadcast a message to all alive agents.

    Args:
        from_agent: Sender agent ID
        cartridges_root: Root directory containing cartridges
        msg_type: Message type
        payload: Message payload
        exclude: List of agent IDs to exclude

    Returns:
        Number of messages sent
    """
    exclude = exclude or []
    sent = 0

    for cartridge_dir in get_all_alive_nodes(cartridges_root):
        if cartridge_dir.name not in exclude:
            if NodeState.send_message(from_agent, cartridge_dir, msg_type, payload):
                sent += 1

    return sent
