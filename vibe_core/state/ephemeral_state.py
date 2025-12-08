"""
EphemeralState - Layer 2 (PRANA) Ephemeral Storage

Chain of Thought and temporary state storage for Prakriti.
Data here is NOT persisted to disk - it lives in memory only.

GAD-000 Compliant:
- All methods return dict/dataclass
- get_capabilities() for discoverability
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("EPHEMERAL_STATE")


@dataclass
class ThoughtEntry:
    """A single thought in the Chain of Thought."""

    timestamp: float
    agent_id: str
    thought: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Session context for an agent."""

    agent_id: str
    started_at: float
    message_count: int = 0
    recent_circuits: List[str] = field(default_factory=list)
    phase: str = "IDLE"


class EphemeralState:
    """Ephemeral (in-memory) state for Prakriti.

    Stores:
    - Chain of Thought (agent reasoning)
    - Session context
    - Temporary working data

    This data is NOT persisted. It lives only in memory
    and is lost on kernel shutdown.
    """

    # Max entries to keep in chain of thought
    MAX_THOUGHTS = 100
    MAX_RECENT_CIRCUITS = 10

    def __init__(self):
        # Chain of Thought storage
        self._thoughts: List[ThoughtEntry] = []

        # Session contexts per agent
        self._sessions: Dict[str, SessionContext] = {}

        # General key-value store
        self._store: Dict[str, Any] = {}

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "get",
                "set",
                "delete",
                "add_thought",
                "get_thoughts",
                "get_session",
                "update_session",
            ],
            "persistent": False,
            "max_thoughts": self.MAX_THOUGHTS,
        }

    # =========================================================================
    # Key-Value Store
    # =========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from ephemeral store."""
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in ephemeral store."""
        self._store[key] = value

    def delete(self, key: str) -> bool:
        """Delete a key from ephemeral store."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def keys(self) -> List[str]:
        """Get all keys in ephemeral store."""
        return list(self._store.keys())

    # =========================================================================
    # Chain of Thought
    # =========================================================================

    def add_thought(
        self,
        agent_id: str,
        thought: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a thought to the Chain of Thought.

        Args:
            agent_id: ID of the thinking agent
            thought: The thought content
            context: Optional context dict
        """
        entry = ThoughtEntry(
            timestamp=time.time(),
            agent_id=agent_id,
            thought=thought,
            context=context or {},
        )
        self._thoughts.append(entry)

        # Trim if too long
        if len(self._thoughts) > self.MAX_THOUGHTS:
            self._thoughts = self._thoughts[-self.MAX_THOUGHTS :]

    def get_thoughts(
        self,
        agent_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[ThoughtEntry]:
        """Get recent thoughts.

        Args:
            agent_id: Optional filter by agent
            limit: Max thoughts to return

        Returns:
            List of ThoughtEntry objects
        """
        thoughts = self._thoughts

        if agent_id:
            thoughts = [t for t in thoughts if t.agent_id == agent_id]

        return thoughts[-limit:]

    def clear_thoughts(self, agent_id: Optional[str] = None) -> int:
        """Clear thoughts.

        Args:
            agent_id: Optional - only clear for this agent

        Returns:
            Number of thoughts cleared
        """
        if agent_id:
            before = len(self._thoughts)
            self._thoughts = [t for t in self._thoughts if t.agent_id != agent_id]
            return before - len(self._thoughts)
        else:
            count = len(self._thoughts)
            self._thoughts = []
            return count

    # =========================================================================
    # Session Context
    # =========================================================================

    def get_session(self, agent_id: str) -> SessionContext:
        """Get or create session context for agent."""
        if agent_id not in self._sessions:
            self._sessions[agent_id] = SessionContext(
                agent_id=agent_id,
                started_at=time.time(),
            )
        return self._sessions[agent_id]

    def update_session(
        self,
        agent_id: str,
        phase: Optional[str] = None,
        circuit: Optional[str] = None,
    ) -> SessionContext:
        """Update session context.

        Args:
            agent_id: Agent ID
            phase: New session phase
            circuit: Circuit that was just used

        Returns:
            Updated SessionContext
        """
        session = self.get_session(agent_id)

        if phase:
            session.phase = phase

        if circuit:
            session.recent_circuits.append(circuit)
            # Trim to max
            if len(session.recent_circuits) > self.MAX_RECENT_CIRCUITS:
                session.recent_circuits = session.recent_circuits[-self.MAX_RECENT_CIRCUITS :]

        session.message_count += 1
        return session

    # =========================================================================
    # Status
    # =========================================================================

    def status(self) -> Dict[str, Any]:
        """Get ephemeral state status."""
        return {
            "store_keys": len(self._store),
            "thought_count": len(self._thoughts),
            "session_count": len(self._sessions),
            "active_sessions": [
                {"agent_id": s.agent_id, "phase": s.phase, "messages": s.message_count} for s in self._sessions.values()
            ],
        }

    def clear_all(self) -> Dict[str, int]:
        """Clear all ephemeral state.

        Returns:
            Dict with counts of cleared items
        """
        counts = {
            "store": len(self._store),
            "thoughts": len(self._thoughts),
            "sessions": len(self._sessions),
        }

        self._store = {}
        self._thoughts = []
        self._sessions = {}

        return counts
