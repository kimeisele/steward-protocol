#!/usr/bin/env python3
"""
AGORA Cartridge - The Broadcast Channel

AGORA is the one-way communication system for the Steward Protocol federation.
- Sources (HERALD, STEWARD, SCIENCE) publish messages
- Receivers (PULSE, LENS, AMBASSADOR, etc.) listen and internalize
- No back-and-forth discussion (prevents hallucination loops)
- Immutable broadcast history (ledger-based)
- Diksha Principle: Teacher speaks, students hear, students act

This is NOT a chatroom. This is Parampara (chain of transmission).
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum

from vibe_core import VibeAgent, Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AGORA_MAIN")


class AgoraMessageType(Enum):
    """Agora message types (one-way flows)"""

    BROADCAST = "broadcast"  # General announcement
    DIRECTIVE = "directive"  # Command from STEWARD
    KNOWLEDGE = "knowledge"  # Teaching from SCIENCE
    NARRATIVE = "narrative"  # Content from HERALD
    SYSTEM = "system"  # Infrastructure message


class AgoraCartridge(VibeAgent):
    """
    AGORA System Cartridge.
    One-Way Broadcast Channel for Steward Protocol.

    Design Principle: Diksha (Transmission, not Discussion)
    - Sources publish (write-restricted)
    - Receivers listen (read-open)
    - One direction only (prevents echo chambers)
    - All messages immutable (ledger-recorded)

    Capabilities:
    - publish_message: Broadcast from authorized sources
    - listen_stream: Receive messages for an agent
    - get_broadcast_history: Read immutable history
    - subscribe_channel: Register listener to channel
    - verify_signal: Ensure no corruption in transmission
    """

    # List of authorized sources (only these can publish)
    AUTHORIZED_SOURCES = ["herald", "steward", "science"]

    def __init__(self):
        """Initialize AGORA as a SystemCartridge."""
        super().__init__(
            agent_id="agora",
            name="AGORA",
            version="1.0.0",
            author="Steward Protocol",
            description="The Broadcast Channel - One-way transmission system for federation",
            domain="INFRASTRUCTURE",
            capabilities=[
                "broadcast_publishing",
                "stream_listening",
                "message_routing",
                "transmission_verification",
                "history_auditing",
            ],
        )

        logger.info("📡 AGORA (VibeAgent v1.0) is online - Broadcast Channel Ready")

        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ AGORA has sworn the Constitutional Oath")

        # Broadcast channels (one per source)
        self.channels: Dict[str, List[Dict[str, Any]]] = {
            "herald": [],  # Content/Narrative stream
            "steward": [],  # Directive/Command stream
            "science": [],  # Knowledge/Teaching stream
            "system": [],  # System/Infrastructure stream
        }

        # Subscriptions (agent_id -> list of channels they listen to)
        self.subscriptions: Dict[str, List[str]] = {}

        # Message counter (for immutability verification)
        self.total_messages = 0

        logger.info("✅ AGORA: Ready for one-way broadcast transmission")

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process tasks from kernel scheduler.

        Supported actions:
        - publish_message: Broadcast from authorized source
        - listen_stream: Receive messages (one-directional)
        - subscribe_channel: Register listener
        - get_history: Read immutable broadcast history
        - verify_transmission: Check message integrity
        """
        try:
            action = task.payload.get("action", "status")
            logger.info(f"📡 AGORA processing: {action}")

            if action == "publish_message":
                result = await self._publish_message(task.payload)
            elif action == "listen_stream":
                result = await self._listen_stream(task.payload)
            elif action == "subscribe_channel":
                result = await self._subscribe_channel(task.payload)
            elif action == "get_history":
                result = await self._get_history(task.payload)
            elif action == "verify_transmission":
                result = await self._verify_transmission(task.payload)
            elif action == "status":
                result = self._status()
            else:
                result = {"error": f"Unknown action: {action}"}

            logger.info(f"✅ AGORA task completed: {action}")
            return result

        except Exception as e:
            logger.error(f"❌ AGORA task failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def _publish_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a message (Diksha transmission).
        Only authorized sources can publish.
        """
        source = payload.get("source", "")
        message_type = payload.get("type", "broadcast")
        content = payload.get("content", "")

        # Authorization check
        if source not in self.AUTHORIZED_SOURCES:
            logger.warning(f"❌ PUBLISH BLOCKED: Unauthorized source '{source}'")
            return {
                "status": "rejected",
                "reason": f"Source '{source}' not authorized to publish",
                "authorized_sources": self.AUTHORIZED_SOURCES,
            }

        # Create message with immutable timestamp
        message = {
            "message_id": f"MSG-{self.total_messages:06d}",
            "source": source,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "sequence": self.total_messages,
        }

        # Store in channel (immutable append-only)
        if source not in self.channels:
            self.channels[source] = []
        self.channels[source].append(message)
        self.total_messages += 1

        logger.info(f"📡 Message published by {source}: {message['message_id']}")

        return {
            "status": "published",
            "message_id": message["message_id"],
            "source": source,
            "sequence": self.total_messages - 1,
            "timestamp": message["timestamp"],
        }

    async def _listen_stream(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Listen to a broadcast stream (receive messages).
        One-directional: receive only, cannot send back.
        """
        agent_id = payload.get("agent_id", "")
        source = payload.get("source", "")  # Which source to listen to
        since_sequence = payload.get("since", 0)  # Resume from message N

        # Get messages from source
        if source not in self.channels:
            return {
                "status": "listening",
                "agent_id": agent_id,
                "source": source,
                "messages": [],
                "note": "No messages yet on this stream",
            }

        # Filter messages after since_sequence
        messages = [msg for msg in self.channels[source] if msg["sequence"] >= since_sequence]

        logger.info(f"🎧 {agent_id} listening to {source} stream ({len(messages)} new messages)")

        return {
            "status": "listening",
            "agent_id": agent_id,
            "source": source,
            "messages": messages,
            "count": len(messages),
            "next_sequence": self.total_messages,
        }

    async def _subscribe_channel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subscribe an agent to a broadcast channel.
        Registers agent as listener (read-only).
        """
        agent_id = payload.get("agent_id", "")
        channels = payload.get("channels", [])

        if agent_id not in self.subscriptions:
            self.subscriptions[agent_id] = []

        # Add subscriptions
        for channel in channels:
            if channel not in self.subscriptions[agent_id]:
                self.subscriptions[agent_id].append(channel)

        logger.info(f"✅ {agent_id} subscribed to channels: {channels}")

        return {
            "status": "subscribed",
            "agent_id": agent_id,
            "channels": self.subscriptions[agent_id],
            "total_subscriptions": len(self.subscriptions),
        }

    async def _get_history(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get immutable broadcast history.
        Ledger-recorded proof of all transmissions.
        """
        source = payload.get("source", "all")
        limit = payload.get("limit", 100)

        if source == "all":
            # Return history from all sources
            history = []
            for src in self.channels:
                history.extend(self.channels[src])
            history.sort(key=lambda x: x["sequence"])
            history = history[-limit:]
        else:
            history = self.channels.get(source, [])[-limit:]

        return {
            "status": "history_retrieved",
            "source": source,
            "total_messages": self.total_messages,
            "returned": len(history),
            "messages": history,
        }

    async def _verify_transmission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify transmission integrity (no corruption).
        Checks that message sequence is unbroken.
        """
        source = payload.get("source", "all")

        if source == "all":
            # Verify all channels
            corrupted = []
            for src, messages in self.channels.items():
                for i, msg in enumerate(messages):
                    if msg["sequence"] != i:
                        corrupted.append(f"{src}:{i}")
        else:
            corrupted = []
            messages = self.channels.get(source, [])
            for i, msg in enumerate(messages):
                if msg["sequence"] != i:
                    corrupted.append(i)

        if corrupted:
            logger.warning(f"⚠️  Transmission corruption detected: {corrupted}")
            return {"status": "corrupted", "corrupted_indices": corrupted}

        logger.info(f"✅ Transmission verified: No corruption detected")
        return {
            "status": "verified",
            "source": source,
            "total_messages": self.total_messages,
            "integrity": "CLEAN",
        }

    def _status(self) -> Dict[str, Any]:
        """Return AGORA status."""
        return {
            "agent_id": self.agent_id,
            "status": "online",
            "total_messages": self.total_messages,
            "channels": {ch: len(msgs) for ch, msgs in self.channels.items()},
            "subscriptions": len(self.subscriptions),
            "oath_sworn": getattr(self, "oath_sworn", False),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        return super().get_manifest()


if __name__ == "__main__":
    cartridge = AgoraCartridge()
    print(f"✅ {cartridge.name} system cartridge loaded")

    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "agora",
            "name": "AGORA",
            "status": "healthy",
            "domain": "GOVERNANCE",
            "capabilities": ["public_forum", "discussion"],
        }
