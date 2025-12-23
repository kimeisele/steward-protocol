"""
OPUS-166: PranaSense - Agent Presence Awareness

Sanskrit: प्राण (Prana) = Life force, breath, vital energy

This cortex module gives MANAS the ability to sense agent presence.
Unlike other senses that perceive static information, PranaSense
perceives the LIVING STATE of agents via their node.json heartbeats.

"Prana is the breath of the universe. When an agent breathes (pulses),
 it leaves a trace. When it stops breathing, the trace vanishes."

Capabilities:
1. perceive()         - Get current agent presence state
2. get_alive_agents() - List all alive agents
3. get_dead_agents()  - List registered but not alive agents
4. detect_changes()   - Detect births/deaths since last perceive
5. watch_agent()      - Watch a specific agent's status

Integration with OPUS-166:
- Uses NodeState to detect node.json files
- Integrates with ShrutaSense for real-time vibration awareness
- Provides presence data to MANAS intent system

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prana_sense.py
    required: true
    rationale: "Agent presence awareness for MANAS"
  - path: vibe_core/state/node_state.py
    required: true
    rationale: "NodeState provides presence data"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
    rationale: "Base class for all senses"

wiring:
  - pattern: "class PranaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prana_sense.py
  - pattern: "class PranaPerception"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prana_sense.py

tests:
  - tests/manas/cortex/test_prana_sense.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# OPUS-167: Intent imports for generate_intents()
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)

from .base import BaseSense

logger = logging.getLogger("MANAS.Cortex.PranaSense")


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class AgentPresence:
    """
    Presence state of a single agent.

    Represents the "vital signs" of an agent.
    """

    agent_id: str
    cartridge_path: Path
    is_alive: bool
    status: str = "unknown"  # booting, online, busy, offline
    last_pulse: Optional[str] = None
    kala_state: Optional[Dict[str, Any]] = None
    mailbox_count: int = 0
    connected_to: List[str] = field(default_factory=list)


@dataclass
class PranaPerception:
    """Result of PranaSense perception."""

    alive_agents: List[AgentPresence]
    dead_agents: List[AgentPresence]
    total_registered: int
    total_alive: int
    total_dead: int
    births: List[str]  # Agents that came alive since last perceive
    deaths: List[str]  # Agents that died since last perceive
    timestamp: str


@dataclass
class PresenceChange:
    """A change in agent presence state."""

    agent_id: str
    change_type: str  # "birth", "death", "status_change"
    old_status: Optional[str]
    new_status: Optional[str]
    timestamp: str


# =============================================================================
# PranaSense Implementation
# =============================================================================


class PranaSense(BaseSense):
    """
    Agent Presence Awareness - The 7th Jnanendriya.

    Senses the "life force" of agents by monitoring their node.json
    heartbeat files. When an agent is alive, its node.json exists.
    When it dies, the file vanishes.

    Philosophy:
    - Prana is the universal life force
    - Each agent's node.json is its "breath" - proof of life
    - PranaSense perceives who is breathing and who has stopped
    """

    name = "prana_sense"

    # Cartridge root directories to scan
    CARTRIDGE_ROOTS = [
        "vibe_core/cartridges/agent_city",
        "vibe_core/cartridges/system",
    ]

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)

        # Track previous state for change detection
        self._last_alive: Set[str] = set()
        self._last_dead: Set[str] = set()

        # All known cartridges (registered agents)
        self._known_cartridges: Dict[str, Path] = {}

        # Discover cartridges on init
        self._discover_cartridges()

        logger.info(f"🫀 PranaSense initialized ({len(self._known_cartridges)} cartridges)")

    # =========================================================================
    # Public API
    # =========================================================================

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> PranaPerception:
        """
        Main perception method - returns current agent presence state.

        Also detects births/deaths since last perceive() call.
        """
        from datetime import datetime, timezone

        from vibe_core.state.node_state import NodeState

        alive_agents: List[AgentPresence] = []
        dead_agents: List[AgentPresence] = []
        current_alive: Set[str] = set()
        current_dead: Set[str] = set()

        # Check each known cartridge
        for agent_id, cartridge_path in self._known_cartridges.items():
            if NodeState.is_alive(cartridge_path):
                # Agent is alive - read its state
                snapshot = NodeState.read(cartridge_path)
                if snapshot:
                    presence = AgentPresence(
                        agent_id=agent_id,
                        cartridge_path=cartridge_path,
                        is_alive=True,
                        status=snapshot.status,
                        last_pulse=snapshot.pulse_at,
                        kala_state={
                            "sun_phase": snapshot.kala.sun_phase,
                            "moon_phase": snapshot.kala.moon_phase,
                        }
                        if snapshot.kala
                        else None,
                        mailbox_count=len([m for m in snapshot.mailbox if not m.read]),
                        connected_to=snapshot.synapses.connected_to if snapshot.synapses else [],
                    )
                else:
                    presence = AgentPresence(
                        agent_id=agent_id,
                        cartridge_path=cartridge_path,
                        is_alive=True,
                        status="online",
                    )
                alive_agents.append(presence)
                current_alive.add(agent_id)
            else:
                # Agent is dead (no node.json)
                dead_agents.append(
                    AgentPresence(
                        agent_id=agent_id,
                        cartridge_path=cartridge_path,
                        is_alive=False,
                        status="offline",
                    )
                )
                current_dead.add(agent_id)

        # Detect births and deaths
        births = current_alive - self._last_alive
        deaths = self._last_alive - current_alive

        # Log significant changes
        for agent_id in births:
            logger.info(f"🫀 BIRTH detected: {agent_id} is now alive!")
        for agent_id in deaths:
            logger.info(f"💀 DEATH detected: {agent_id} has stopped breathing!")

        # Update last state
        self._last_alive = current_alive
        self._last_dead = current_dead

        return PranaPerception(
            alive_agents=alive_agents,
            dead_agents=dead_agents,
            total_registered=len(self._known_cartridges),
            total_alive=len(alive_agents),
            total_dead=len(dead_agents),
            births=list(births),
            deaths=list(deaths),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def get_alive_agents(self) -> List[str]:
        """Get list of currently alive agent IDs."""
        from vibe_core.state.node_state import NodeState

        return [agent_id for agent_id, path in self._known_cartridges.items() if NodeState.is_alive(path)]

    def get_dead_agents(self) -> List[str]:
        """Get list of registered but not alive agent IDs."""
        alive = set(self.get_alive_agents())
        return [agent_id for agent_id in self._known_cartridges.keys() if agent_id not in alive]

    def is_agent_alive(self, agent_id: str) -> bool:
        """Check if a specific agent is alive."""
        from vibe_core.state.node_state import NodeState

        path = self._known_cartridges.get(agent_id)
        if not path:
            return False
        return NodeState.is_alive(path)

    def get_agent_presence(self, agent_id: str) -> Optional[AgentPresence]:
        """Get detailed presence info for a specific agent."""
        from vibe_core.state.node_state import NodeState

        path = self._known_cartridges.get(agent_id)
        if not path:
            return None

        if NodeState.is_alive(path):
            snapshot = NodeState.read(path)
            if snapshot:
                return AgentPresence(
                    agent_id=agent_id,
                    cartridge_path=path,
                    is_alive=True,
                    status=snapshot.status,
                    last_pulse=snapshot.pulse_at,
                    mailbox_count=len([m for m in snapshot.mailbox if not m.read]),
                )
        return AgentPresence(
            agent_id=agent_id,
            cartridge_path=path,
            is_alive=False,
            status="offline",
        )

    def refresh_cartridges(self) -> int:
        """Re-scan for cartridges (useful after agent creation)."""
        old_count = len(self._known_cartridges)
        self._discover_cartridges()
        new_count = len(self._known_cartridges)
        if new_count > old_count:
            logger.info(f"🫀 Discovered {new_count - old_count} new cartridges")
        return new_count

    # =========================================================================
    # ShrutaSense Integration
    # =========================================================================

    def handle_vibration(self, vibration: Any) -> Optional[PresenceChange]:
        """
        Handle a filesystem vibration from ShrutaSense.

        Filters for node.json changes and interprets them as
        agent presence changes.

        Args:
            vibration: A Vibration object from ShrutaSense

        Returns:
            PresenceChange if this was an agent presence change, None otherwise
        """
        from datetime import datetime, timezone

        # Only care about node.json files
        path_str = str(vibration.path)
        if not path_str.endswith("node.json"):
            return None

        # Determine agent ID from path
        cartridge_path = vibration.path.parent
        agent_id = cartridge_path.name

        if vibration.event_type == "created":
            logger.info(f"🫀 Agent birth detected via ShrutaSense: {agent_id}")
            return PresenceChange(
                agent_id=agent_id,
                change_type="birth",
                old_status=None,
                new_status="booting",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        elif vibration.event_type == "deleted":
            logger.info(f"💀 Agent death detected via ShrutaSense: {agent_id}")
            return PresenceChange(
                agent_id=agent_id,
                change_type="death",
                old_status="online",
                new_status=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        elif vibration.event_type == "modified":
            # Status update (pulse)
            return PresenceChange(
                agent_id=agent_id,
                change_type="status_change",
                old_status=None,
                new_status="online",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        return None

    def register_with_shruta(self, shruta_sense: Any) -> None:
        """
        Register as a vibration handler with ShrutaSense.

        This enables real-time presence awareness without polling.
        """
        shruta_sense.add_handler(self.handle_vibration)
        logger.info("🫀 PranaSense registered with ShrutaSense for real-time updates")

    # =========================================================================
    # OPUS-167: Intent Generation (Fractal Architecture)
    # =========================================================================

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List[Intent]:
        """
        Generate presence-related intents based on agent lifecycle events.

        OPUS-167: Fractal Architecture Restoration

        This method was migrated FROM cognitive_kernel._perceive_and_generate_presence_intents()
        TO here, restoring the proper "As Above, So Below" pattern where each
        sense is autonomous and generates its own intents.

        Returns:
            List of presence intents (agent death investigations)
        """
        intents: List[Intent] = []

        # Cooldown tracking (avoid spam from flaky agents)
        cooldown_minutes = 5
        cooldowns: Dict[str, datetime] = context.get("_prana_cooldowns", {}) if context else {}

        try:
            # Perceive current presence state
            perception = self.perceive()

            # React to deaths - generate investigation intents (with cooldown)
            now = datetime.utcnow()
            for death in perception.deaths:
                agent_id = death.agent_id

                # Check cooldown to avoid intent spam from flaky agents
                last_intent_time = cooldowns.get(agent_id)
                if last_intent_time:
                    elapsed = (now - last_intent_time).total_seconds() / 60
                    if elapsed < cooldown_minutes:
                        logger.debug(
                            f"🫀 PRANA SENSE: Skipping {agent_id} death intent - "
                            f"cooldown active ({elapsed:.1f}/{cooldown_minutes} min)"
                        )
                        continue

                presence = self.get_agent_presence(agent_id)

                # Mark cooldown BEFORE generating (avoid race conditions)
                cooldowns[agent_id] = now

                intent = Intent(
                    id=f"prana_death_{agent_id}_{now.strftime('%H%M%S')}",
                    intent_type="investigate_agent_death",
                    title=f"Agent {agent_id} died",
                    description=(
                        f"Agent '{agent_id}' is no longer responding. "
                        f"Last seen: {presence.last_seen if presence else 'unknown'}. "
                        f"Investigate cause and consider restart."
                    ),
                    reasoning=(
                        "PranaSense detected missing heartbeat (node.json deleted/stale). "
                        "Dead agents may indicate crashes, resource issues, or intentional shutdown."
                    ),
                    priority=IntentPriority.HIGH,
                    risk=IntentRisk.MEDIUM,
                    params={
                        "agent_id": agent_id,
                        "last_seen": presence.last_seen if presence else None,
                        "cartridge_path": str(presence.cartridge_path) if presence else None,
                    },
                    auto_executable=False,
                    related_files=[f"agents/{agent_id}/node.json"],
                )
                intents.append(intent)
                logger.info(f"🫀 PRANA SENSE: Agent '{agent_id}' died - investigation intent generated")

            # React to births - log and optionally generate welcome intent
            for birth in perception.births:
                agent_id = birth.agent_id
                logger.info(f"🫀 PRANA SENSE: Agent '{agent_id}' born - now alive")

            # Log summary
            if perception.deaths or perception.births:
                logger.info(
                    f"🫀 PRANA SENSE: {len(perception.deaths)} deaths, {len(perception.births)} births detected"
                )

        except Exception as e:
            logger.warning(f"🫀 PRANA SENSE: Intent generation failed: {e}")

        return intents

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _discover_cartridges(self) -> None:
        """Discover all cartridge directories with steward.json."""
        self._known_cartridges = {}

        for root_str in self.CARTRIDGE_ROOTS:
            root = self._workspace / root_str
            if not root.exists():
                continue

            for item in root.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    steward = item / "steward.json"
                    if steward.exists():
                        agent_id = item.name
                        self._known_cartridges[agent_id] = item

        logger.debug(f"Discovered {len(self._known_cartridges)} cartridges")


# =============================================================================
# Convenience Functions
# =============================================================================

_global_prana: Optional[PranaSense] = None


def get_prana_sense(workspace: Optional[Path] = None) -> PranaSense:
    """Get or create global PranaSense instance."""
    global _global_prana
    if _global_prana is None:
        _global_prana = PranaSense(workspace=workspace)
    return _global_prana
