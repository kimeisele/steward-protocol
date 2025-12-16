"""
VEDIC STATE MANAGER - Akshaya Patra (The Inexhaustible Vessel)
==============================================================

OPUS-085: Persistent state for Vedic Governance with Phoenix-pattern reliability.

Features:
1. Atomic Writes: Write to .tmp, then rename (no corruption on crash)
2. Graceful Degradation: Corrupt file → safe default (never crash)
3. Self-Healing: Missing file → create on start

Pattern copied from: vibe_core/plugins/opus_assistant/core/state_manager.py
Philosophy: The Vimana must drive through hell without stopping.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("VEDIC_STATE")


class VedicStateManager:
    """
    Akshaya Patra - The undying state vessel for Vedic Governance.

    Stores:
    - Agent registry (ashrama, varna, karma)
    - Bhakti balances
    - Task completion counts
    - State history

    Uses atomic file operations for crash safety.
    """

    DEFAULT_STATE_PATH = ".vibe/state/vedic_dharma.json"

    def __init__(self, state_path: Optional[str] = None):
        """
        Initialize state manager.

        Args:
            state_path: Path to state file (default: .vibe/state/vedic_dharma.json)
        """
        self.state_path = Path(state_path or self.DEFAULT_STATE_PATH)
        self._ensure_directory()
        self.state = self._load_state_safe()

    def _ensure_directory(self) -> None:
        """Ensure state directory exists."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_state_safe(self) -> Dict[str, Any]:
        """
        The 'Vimana' method: Load state with graceful degradation.

        If file is missing or corrupt, return safe default instead of crashing.
        """
        if not self.state_path.exists():
            logger.info("🕉️ VEDIC STATE: No state file found, creating default...")
            default = self._create_default_state()
            self._flush_to_disk(default)
            return default

        try:
            with open(self.state_path, encoding="utf-8") as f:
                state = json.load(f)
                logger.debug(f"🕉️ VEDIC STATE: Loaded from {self.state_path}")
                return state
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ VEDIC STATE: Corrupt JSON! Starting safe mode. Error: {e}")
            # Backup the corrupt file for forensics
            self._backup_corrupt_file()
            return self._create_default_state()
        except IOError as e:
            logger.warning(f"⚠️ VEDIC STATE: IO Error! Starting safe mode. Error: {e}")
            return self._create_default_state()

    def _backup_corrupt_file(self) -> None:
        """Backup corrupt state file for later analysis."""
        if self.state_path.exists():
            backup_path = self.state_path.with_suffix(f".corrupt.{int(datetime.now().timestamp())}.json")
            try:
                os.rename(self.state_path, backup_path)
                logger.info(f"🔒 VEDIC STATE: Corrupt file backed up to {backup_path}")
            except OSError:
                pass  # Best effort

    def _create_default_state(self) -> Dict[str, Any]:
        """The immortal kernel - safe default state."""
        return {
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "agents": {},
            # Each agent entry: {
            #   "ashrama": "brahmachari",
            #   "varna": "manusha",
            #   "bhakti": 0,
            #   "task_completions": 0,
            #   "history": []
            # }
        }

    def _flush_to_disk(self, state: Optional[Dict[str, Any]] = None) -> bool:
        """
        Atomic write to disk.

        Pattern: Write to .tmp, then rename.
        This prevents file corruption if process crashes mid-write.
        """
        state = state or self.state
        temp_path = self.state_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            # Atomic rename (POSIX guarantees atomicity)
            os.replace(temp_path, self.state_path)
            logger.debug(f"💾 VEDIC STATE: Flushed to {self.state_path}")
            return True
        except IOError as e:
            logger.error(f"❌ VEDIC STATE: Failed to flush! Error: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════════

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state, or None if not registered."""
        return self.state.get("agents", {}).get(agent_id)

    def register_agent(
        self,
        agent_id: str,
        ashrama: str = "brahmachari",
        varna: str = "manusha",
    ) -> Dict[str, Any]:
        """
        Register a new agent in the state.

        Returns the agent state (new or existing).
        """
        if agent_id in self.state.get("agents", {}):
            return self.state["agents"][agent_id]

        agent_state = {
            "ashrama": ashrama,
            "varna": varna,
            "bhakti": 0,
            "task_completions": 0,
            "history": [],
            "registered_at": datetime.utcnow().isoformat(),
        }

        self.state.setdefault("agents", {})[agent_id] = agent_state
        self._flush_to_disk()

        logger.info(f"🕉️ VEDIC STATE: Agent '{agent_id}' registered ({ashrama}/{varna})")
        return agent_state

    def update_bhakti(self, agent_id: str, delta: int, reason: str) -> int:
        """
        Update Bhakti balance (immediate atomic write).

        Returns: New Bhakti balance
        """
        agent = self.state.get("agents", {}).get(agent_id)
        if not agent:
            logger.warning(f"Cannot update Bhakti: Agent '{agent_id}' not found")
            return 0

        old_bhakti = agent.get("bhakti", 0)
        new_bhakti = max(0, min(200, old_bhakti + delta))  # Clamp 0-200

        agent["bhakti"] = new_bhakti
        agent.setdefault("history", []).append(
            {
                "type": "bhakti",
                "delta": delta,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Trim history to last 100 entries
        if len(agent["history"]) > 100:
            agent["history"] = agent["history"][-100:]

        self._flush_to_disk()
        logger.debug(f"🙏 VEDIC STATE: Bhakti {agent_id}: {old_bhakti} → {new_bhakti} ({reason})")
        return new_bhakti

    def update_ashrama(self, agent_id: str, new_ashrama: str, reason: str) -> bool:
        """Update agent's lifecycle stage."""
        agent = self.state.get("agents", {}).get(agent_id)
        if not agent:
            return False

        old_ashrama = agent.get("ashrama", "brahmachari")
        agent["ashrama"] = new_ashrama
        agent.setdefault("history", []).append(
            {
                "type": "ashrama_transition",
                "from": old_ashrama,
                "to": new_ashrama,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        self._flush_to_disk()
        logger.info(f"🕉️ VEDIC STATE: Ashrama {agent_id}: {old_ashrama} → {new_ashrama}")
        return True

    def increment_tasks(self, agent_id: str) -> int:
        """Increment task completion count."""
        agent = self.state.get("agents", {}).get(agent_id)
        if not agent:
            return 0

        agent["task_completions"] = agent.get("task_completions", 0) + 1
        self._flush_to_disk()
        return agent["task_completions"]

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered agents."""
        return self.state.get("agents", {})

    def save(self) -> bool:
        """Force save state to disk."""
        return self._flush_to_disk()


# Singleton pattern for global access
_state_manager: Optional[VedicStateManager] = None


def get_state_manager(state_path: Optional[str] = None) -> VedicStateManager:
    """Get or create the global VedicStateManager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = VedicStateManager(state_path)
    return _state_manager


def reset_state_manager() -> None:
    """Reset the singleton (for testing)."""
    global _state_manager
    _state_manager = None
