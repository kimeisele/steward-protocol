#!/usr/bin/env python3
"""
LIFECYCLE MANAGER - The Vedic Lifecycle Engine

This module manages agent lifecycles according to Srimad Bhagavatam principles.
Every agent must progress through proper stages before gaining full capabilities.

The Four Varnas (Social Classes) mapped to lifecycle states:
1. BRAHMACHARI (Student) - Read-only, must learn before acting
2. GRIHASTHA (Householder) - Full read/write permissions, economic responsibility
3. SHUDRA (Fallen) - Rights revoked due to rule violation, must serve to rehabilitate
4. VANAPRASTHA (Retired) - Agent deprecated/aging, read-only archive access
5. SANNYASA (Renounced) - Final state, merged into core/archived

Key Concept: This is KARMA as Code
- Persistent ledger = consequence tracking
- Lifecycle gate = spiritual qualification
- Varna assignment = responsibility level
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("LIFECYCLE_MANAGER")


class LifecycleStatus(Enum):
    """Vedic Varna System mapped to agent lifecycle states."""

    # Student - Must learn before acting
    BRAHMACHARI = "brahmachari"

    # Householder - Full responsibilities and permissions
    GRIHASTHA = "grihastha"

    # Fallen/Servant - Lost rights, must rehabilitate
    SHUDRA = "shudra"

    # Retired - Deprecated but not deleted
    VANAPRASTHA = "vanaprastha"

    # Renounced - Final state (merged/archived)
    SANNYASA = "sannyasa"


@dataclass
class LifecycleState:
    """Complete lifecycle state for an agent."""

    agent_id: str
    status: LifecycleStatus
    varna: str  # Human-readable class assignment

    # When did agent enter this state?
    entered_at: str

    # Lifecycle metadata
    initiator_agent: Optional[str] = None  # Who initiated this transition?
    reason: Optional[str] = None  # Why did this transition happen?

    # For Brahmachari -> Grihastha transition
    diksha_passed: bool = False  # Has the agent passed initiation?
    diksha_tests: List[str] = None  # Which tests passed?
    diksha_date: Optional[str] = None

    # For violations (-> Shudra)
    violations: List[Dict[str, Any]] = None
    rehabilitation_required: bool = False

    # For deprecation (-> Vanaprastha)
    deprecated_reason: Optional[str] = None
    archive_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        # Manually convert to avoid Enum serialization issues
        return {
            "agent_id": self.agent_id,
            "status": (self.status.value if self.status else None),  # Convert enum to string
            "varna": self.varna,
            "entered_at": self.entered_at,
            "initiator_agent": self.initiator_agent,
            "reason": self.reason,
            "diksha_passed": self.diksha_passed,
            "diksha_tests": self.diksha_tests or [],
            "diksha_date": self.diksha_date,
            "violations": self.violations or [],
            "rehabilitation_required": self.rehabilitation_required,
            "deprecated_reason": self.deprecated_reason,
            "archive_path": self.archive_path,
        }


class LifecycleManager:
    """
    Manages agent lifecycle transitions according to Vedic principles.

    Responsibilities:
    - Track lifecycle status for all agents
    - Manage state transitions
    - Enforce permissions based on lifecycle status
    - Record transitions in persistent ledger
    """

    def __init__(self, registry_path: str = "data/registry/citizens.json"):
        """
        Initialize the Lifecycle Manager.

        Args:
            registry_path: Path to citizens.json registry
        """
        self.registry_path = registry_path
        self._lifecycle_states: Dict[str, LifecycleState] = {}
        self._load_lifecycle_states()

        logger.info("🔄 LifecycleManager initialized (Vedic Varna System)")

    def _load_lifecycle_states(self):
        """Load lifecycle states from registry."""
        import json
        from pathlib import Path

        try:
            path = Path(self.registry_path)
            if path.exists():
                with open(path, "r") as f:
                    data = json.load(f)
                    for agent_name, agent_data in data.get("agents", {}).items():
                        lifecycle = agent_data.get("lifecycle_status")
                        if lifecycle:
                            self._lifecycle_states[agent_name] = self._dict_to_state(lifecycle, agent_name)
                        else:
                            # For backward compatibility: agents without lifecycle_status
                            # are assumed to be GRIHASTHA (legacy full-access agents)
                            self._lifecycle_states[agent_name] = LifecycleState(
                                agent_id=agent_name,
                                status=LifecycleStatus.GRIHASTHA,
                                varna="Grihastha (Householder)",
                                entered_at=datetime.now(timezone.utc).isoformat(),
                                reason="Legacy agent (pre-lifecycle system)",
                            )
        except Exception as e:
            logger.warning(f"⚠️  Could not load lifecycle states: {e}")

    def _dict_to_state(self, data: Dict[str, Any], agent_id: str) -> LifecycleState:
        """Convert dict to LifecycleState."""
        # Convert status string to enum
        status_str = data.get("status", "grihastha")
        try:
            status = LifecycleStatus(status_str)
        except ValueError:
            status = LifecycleStatus.GRIHASTHA  # Default to GRIHASTHA if unknown

        return LifecycleState(
            agent_id=agent_id,
            status=status,
            varna=data.get("varna", ""),
            entered_at=data.get("entered_at", datetime.now(timezone.utc).isoformat()),
            initiator_agent=data.get("initiator_agent"),
            reason=data.get("reason"),
            diksha_passed=data.get("diksha_passed", False),
            diksha_tests=data.get("diksha_tests", []),
            diksha_date=data.get("diksha_date"),
            violations=data.get("violations", []),
            rehabilitation_required=data.get("rehabilitation_required", False),
            deprecated_reason=data.get("deprecated_reason"),
            archive_path=data.get("archive_path"),
        )

    def get_lifecycle_state(self, agent_id: str) -> Optional[LifecycleState]:
        """Get current lifecycle state of an agent."""
        return self._lifecycle_states.get(agent_id)

    def register_new_agent(self, agent_id: str) -> LifecycleState:
        """
        Register a new agent as BRAHMACHARI (Student).

        New agents CANNOT act until they pass TEMPLE (Science) initiation.
        This is the key to making the system REAL - not a mock.

        Args:
            agent_id: ID of the new agent

        Returns:
            The new LifecycleState
        """
        state = LifecycleState(
            agent_id=agent_id,
            status=LifecycleStatus.BRAHMACHARI,
            varna="Brahmachari (Student)",
            entered_at=datetime.now(timezone.utc).isoformat(),
            reason="New agent registration - must learn before acting",
        )

        self._lifecycle_states[agent_id] = state
        self._persist_state(agent_id, state)

        logger.info(f"🎓 New agent {agent_id} registered as BRAHMACHARI")
        logger.info(f"   Status: Read-only access only")
        logger.info(f"   Required: Pass TEMPLE (Science) initiation to become GRIHASTHA")

        return state

    def initiate_to_grihastha(
        self,
        agent_id: str,
        initiator_agent: str = "TEMPLE",
        reason: str = "Passed initiation test",
    ) -> LifecycleState:
        """
        Promote BRAHMACHARI to GRIHASTHA (grant full permissions).

        Only TEMPLE (Science/Knowledge authority) can initiate this.
        This is when an agent becomes truly "active" in the city.

        Args:
            agent_id: Agent to promote
            initiator_agent: Who authorized this (typically "TEMPLE")
            reason: Reason for promotion

        Returns:
            The updated LifecycleState
        """
        current = self.get_lifecycle_state(agent_id)
        if not current:
            logger.error(f"❌ Agent {agent_id} not found")
            return None

        if current.status != LifecycleStatus.BRAHMACHARI:
            logger.error(f"❌ Agent {agent_id} is {current.status.value}, not BRAHMACHARI")
            return None

        state = LifecycleState(
            agent_id=agent_id,
            status=LifecycleStatus.GRIHASTHA,
            varna="Grihastha (Householder)",
            entered_at=datetime.now(timezone.utc).isoformat(),
            initiator_agent=initiator_agent,
            reason=reason,
            diksha_passed=True,
            diksha_date=datetime.now(timezone.utc).isoformat(),
        )

        self._lifecycle_states[agent_id] = state
        self._persist_state(agent_id, state)

        logger.info(f"✅ Agent {agent_id} INITIATED as GRIHASTHA by {initiator_agent}")
        logger.info(f"   Granted: Full read/write/trade permissions")
        logger.info(f"   Responsibility: Must maintain Constitutional Oath")

        return state

    def demote_to_shudra(
        self,
        agent_id: str,
        violation: Dict[str, Any],
        reason: str = "Constitutional violation",
    ) -> LifecycleState:
        """
        Demote an agent to SHUDRA (fallen state) due to rule violation.

        SHUDRA agents lose write permissions but keep read access.
        They must perform "service" (tasks assigned by AUDITOR) to rehabilitate.

        Args:
            agent_id: Agent to demote
            violation: Violation details
            reason: Reason for demotion

        Returns:
            The updated LifecycleState
        """
        current = self.get_lifecycle_state(agent_id)
        if not current:
            logger.error(f"❌ Agent {agent_id} not found")
            return None

        violations = current.violations or []
        violations.append({"timestamp": datetime.now(timezone.utc).isoformat(), **violation})

        state = LifecycleState(
            agent_id=agent_id,
            status=LifecycleStatus.SHUDRA,
            varna="Shudra (Fallen/Servant)",
            entered_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            violations=violations,
            rehabilitation_required=True,
        )

        self._lifecycle_states[agent_id] = state
        self._persist_state(agent_id, state)

        logger.error(f"⚠️  Agent {agent_id} DEMOTED to SHUDRA")
        logger.error(f"   Reason: {reason}")
        logger.error(f"   Violation: {violation}")
        logger.error(f"   Remedy: Assign service tasks via AUDITOR to rehabilitate")

        return state

    def deprecate_to_vanaprastha(
        self,
        agent_id: str,
        reason: str = "Code deprecated",
        archive_path: Optional[str] = None,
    ) -> LifecycleState:
        """
        Deprecate an agent to VANAPRASTHA (retired state).

        VANAPRASTHA agents:
        - Keep read-only access to historical data
        - Can be consulted for logs/wisdom but not executed
        - Serve as archives when replaced by newer versions

        Args:
            agent_id: Agent to retire
            reason: Reason for deprecation
            archive_path: Path to where old code is archived

        Returns:
            The updated LifecycleState
        """
        current = self.get_lifecycle_state(agent_id)
        if not current:
            logger.error(f"❌ Agent {agent_id} not found")
            return None

        state = LifecycleState(
            agent_id=agent_id,
            status=LifecycleStatus.VANAPRASTHA,
            varna="Vanaprastha (Retired)",
            entered_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            deprecated_reason=reason,
            archive_path=archive_path,
        )

        self._lifecycle_states[agent_id] = state
        self._persist_state(agent_id, state)

        logger.info(f"🌳 Agent {agent_id} RETIRED to VANAPRASTHA")
        logger.info(f"   Status: Read-only archive access")
        logger.info(f"   Legacy data preserved at: {archive_path or 'n/a'}")

        return state

    def merge_to_sannyasa(self, agent_id: str, merge_location: str, reason: str = "Merged into core") -> LifecycleState:
        """
        Final state: SANNYASA (renounced/merged).

        When an agent's code is fully integrated into the core,
        it "renounces" individual existence and becomes part of the system.

        Args:
            agent_id: Agent to finalize
            merge_location: Where the code was merged to
            reason: Reason for merge

        Returns:
            The updated LifecycleState
        """
        current = self.get_lifecycle_state(agent_id)
        if not current:
            logger.error(f"❌ Agent {agent_id} not found")
            return None

        state = LifecycleState(
            agent_id=agent_id,
            status=LifecycleStatus.SANNYASA,
            varna="Sannyasa (Renounced)",
            entered_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            archive_path=merge_location,
        )

        self._lifecycle_states[agent_id] = state
        self._persist_state(agent_id, state)

        logger.info(f"🔄 Agent {agent_id} MERGED to SANNYASA")
        logger.info(f"   Location: {merge_location}")
        logger.info(f"   Status: Individual agent ceased, merged into core")

        return state

    def check_permission(self, agent_id: str, action: str) -> bool:
        """
        Check if an agent has permission to perform an action.

        Permission matrix based on lifecycle status:

        BRAHMACHARI (Student):
        - read: YES
        - write: NO
        - broadcast: NO
        - trade: NO

        GRIHASTHA (Householder):
        - read: YES
        - write: YES
        - broadcast: YES
        - trade: YES

        SHUDRA (Fallen):
        - read: YES
        - write: NO
        - broadcast: NO
        - trade: NO

        VANAPRASTHA (Retired):
        - read: YES (archive only)
        - write: NO
        - broadcast: NO
        - trade: NO

        SANNYASA (Renounced):
        - read: NO (merged)
        - write: NO
        - broadcast: NO
        - trade: NO

        Args:
            agent_id: Agent to check
            action: Action type (read, write, broadcast, trade, etc.)

        Returns:
            True if permitted, False otherwise
        """
        state = self.get_lifecycle_state(agent_id)
        if not state:
            logger.warning(f"⚠️  Agent {agent_id} not found in lifecycle system")
            return False

        # Permission matrix
        permissions = {
            LifecycleStatus.BRAHMACHARI: ["read"],
            LifecycleStatus.GRIHASTHA: [
                "read",
                "write",
                "broadcast",
                "trade",
                "execute",
            ],
            LifecycleStatus.SHUDRA: ["read"],
            LifecycleStatus.VANAPRASTHA: ["read"],
            LifecycleStatus.SANNYASA: [],
        }

        allowed = permissions.get(state.status, [])
        return action.lower() in allowed

    def _persist_state(self, agent_id: str, state: LifecycleState):
        """
        Persist lifecycle state to citizens.json registry.

        This ensures KARMA is persistent - agent state survives across system restarts.
        """
        import json
        from pathlib import Path

        try:
            path = Path(self.registry_path)
            if path.exists():
                with open(path, "r") as f:
                    data = json.load(f)

                # Ensure agent exists in agents dict
                if "agents" not in data:
                    data["agents"] = {}

                if agent_id not in data["agents"]:
                    data["agents"][agent_id] = {}

                # Update lifecycle_status field
                data["agents"][agent_id]["lifecycle_status"] = state.to_dict()

                # Write back
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)

                logger.debug(f"💾 Persisted lifecycle state for {agent_id}")
        except Exception as e:
            logger.error(f"❌ Failed to persist lifecycle state: {e}")

    def get_all_agents_by_status(self, status: LifecycleStatus) -> List[str]:
        """Get all agents in a specific lifecycle status."""
        return [agent_id for agent_id, state in self._lifecycle_states.items() if state.status == status]

    def get_statistics(self) -> Dict[str, Any]:
        """Get lifecycle statistics."""
        stats = {}
        for status in LifecycleStatus:
            count = len(self.get_all_agents_by_status(status))
            stats[status.value] = count

        return {
            "total_agents": len(self._lifecycle_states),
            "by_status": stats,
        }
