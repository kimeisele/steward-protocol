"""
⚙️ VIBE CORE: CAPABILITY REGISTRY MODULE ⚙️
==========================================

Capability Management System for Agent Governance.

This module implements the REVOKE_MANDATE feature, allowing selective
revocation of agent capabilities for security and governance.

Key Features:
- Selective capability revocation (not just all-or-nothing)
- Immutable audit trail in Parampara Ledger
- Permission model (Kernel/Civic/Self can revoke)
- Fail-closed security (unregistered agents have NO capabilities)

ARCH-050: STEWARD Protocol Agent Identity & Capabilities
GAD-XXXX: REVOKE_MANDATE Implementation (Phase 2)
"""

import logging
from typing import FrozenSet, List, Optional, Set

# Absolute imports after migration to mahajana structure
from vibe_core.kernel import VibeLedger
from vibe_core.protocols.capability import CapabilityModifyResult

logger = logging.getLogger("CAPABILITY_REGISTRY")


class CapabilityRegistry:
    """
    Manages agent capabilities with revocation support.

    This replaces the simple Dict[str, frozenset] pattern with a
    full-featured registry that supports:
    - Selective revocation of individual capabilities
    - Grant new capabilities (with permission check)
    - Audit trail for all capability changes
    - Permission model for who can modify capabilities
    """

    def __init__(self, ledger: VibeLedger):
        """
        Initialize the CapabilityRegistry.

        Args:
            ledger: VibeLedger for immutable audit trail
        """
        self._capabilities: Dict[str, Set[str]] = {}
        self._original_capabilities: Dict[str, FrozenSet[str]] = {}
        self._ledger = ledger

        # Core capabilities that all registered agents have
        # (basic operations needed for any agent to function)
        self._core_capabilities = frozenset(
            [
                "read_file",
                "write_file",
                "list_tasks",
                "add_task",
                "complete_task",
            ]
        )

        logger.info("🔐 CapabilityRegistry initialized")

    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """
        Register an agent with initial capabilities.

        This should be called once during agent registration.
        The initial capabilities are stored immutably for reference.

        Args:
            agent_id: The agent to register
            capabilities: List of initial capabilities
        """
        # Store as mutable set for revocation/grant
        self._capabilities[agent_id] = set(capabilities)

        # Store original as immutable reference
        self._original_capabilities[agent_id] = frozenset(capabilities)

        # Record registration in audit trail
        self._ledger.record_event(
            event_type="capability_registered",
            agent_id=agent_id,
            details={
                "capabilities": capabilities,
                "timestamp": self._get_timestamp(),
            },
        )

        logger.debug(f"🔐 Registered capabilities for '{agent_id}': {capabilities}")

    def has_capability(self, agent_id: str, capability: str) -> bool:
        """
        Check if an agent has a specific capability.

        This is the primary capability check used throughout the system.

        Args:
            agent_id: The agent to check
            capability: The capability required

        Returns:
            True if agent has the capability, False otherwise

        Security:
            - Uses mutable set (reflects revocations)
            - Unregistered agents have NO capabilities
            - Core capabilities granted to all registered agents
        """
        # Check if agent is registered
        if agent_id not in self._capabilities:
            logger.warning(f"⛔ CAPABILITY_DENIED: Unregistered agent '{agent_id}'")
            return False

        # Check if capability is in agent's set or core set
        agent_caps = self._capabilities[agent_id]
        has_cap = capability in agent_caps or capability in self._core_capabilities

        if not has_cap:
            logger.warning(
                f"⛔ CAPABILITY_DENIED: Agent '{agent_id}' lacks '{capability}'. "
                f"Current capabilities: {sorted(agent_caps)}"
            )

        return has_cap

    def revoke(
        self, agent_id: str, capabilities: List[str], revoker_id: str, reason: Optional[str] = None
    ) -> CapabilityModifyResult:
        """
        Revoke one or more capabilities from an agent.

        Args:
            agent_id: The agent to revoke from
            capabilities: List of capabilities to revoke
            revoker_id: The agent/system performing the revocation
            reason: Optional reason for revocation (for audit trail)

        Returns:
            Dictionary with:
                - success: bool
                - revoked: List of actually revoked capabilities
                - not_found: List of capabilities agent didn't have
                - message: Human-readable result

        Security:
            Permission check is caller's responsibility.
            This method trusts that the caller has verified permission.
        """
        # Check if agent is registered
        if agent_id not in self._capabilities:
            return {
                "success": False,
                "revoked": [],
                "not_found": capabilities,
                "message": f"Agent '{agent_id}' is not registered",
            }

        agent_caps = self._capabilities[agent_id]

        # Separate into revocable and not-found
        revoked = []
        not_found = []

        for cap in capabilities:
            if cap in agent_caps:
                agent_caps.remove(cap)
                revoked.append(cap)
                logger.info(f"🔒 REVOKED: '{cap}' from '{agent_id}' by '{revoker_id}'")
            else:
                not_found.append(cap)
                logger.debug(f"⚠️  Cannot revoke '{cap}' from '{agent_id}': not present")

        # Record in audit trail
        if revoked:
            self._ledger.record_event(
                event_type="capability_revoked",
                agent_id=agent_id,
                details={
                    "revoked_capabilities": revoked,
                    "revoker_id": revoker_id,
                    "reason": reason or "No reason provided",
                    "remaining_capabilities": sorted(agent_caps),
                    "timestamp": self._get_timestamp(),
                },
            )

        message = f"Revoked {len(revoked)} capability(ies) from '{agent_id}'"
        if not_found:
            message += f" ({len(not_found)} not found)"

        none_have_caps = all(cap not in agent_caps for cap in capabilities)
        return {"success": none_have_caps, "revoked": revoked, "not_found": not_found, "message": message}

    def grant(
        self, agent_id: str, capabilities: List[str], granter_id: str, reason: Optional[str] = None
    ) -> CapabilityModifyResult:
        """
        Grant new capabilities to an agent.

        Args:
            agent_id: The agent to grant to
            capabilities: List of capabilities to grant
            granter_id: The agent/system performing the grant
            reason: Optional reason for grant (for audit trail)

        Returns:
            Dictionary with:
                - success: bool
                - granted: List of newly granted capabilities
                - already_had: List of capabilities agent already had
                - message: Human-readable result

        Security:
            Permission check is caller's responsibility.
            This method trusts that the caller has verified permission.
        """
        # Check if agent is registered
        if agent_id not in self._capabilities:
            return {
                "success": False,
                "granted": [],
                "already_had": [],
                "message": f"Agent '{agent_id}' is not registered",
            }

        agent_caps = self._capabilities[agent_id]

        # Separate into new grants and already-had
        granted = []
        already_had = []

        for cap in capabilities:
            if cap in agent_caps:
                already_had.append(cap)
                logger.debug(f"⚠️  Cannot grant '{cap}' to '{agent_id}': already has it")
            else:
                agent_caps.add(cap)
                granted.append(cap)
                logger.info(f"🔓 GRANTED: '{cap}' to '{agent_id}' by '{granter_id}'")

        # Record in audit trail
        if granted:
            self._ledger.record_event(
                event_type="capability_granted",
                agent_id=agent_id,
                details={
                    "granted_capabilities": granted,
                    "granter_id": granter_id,
                    "reason": reason or "No reason provided",
                    "current_capabilities": sorted(agent_caps),
                    "timestamp": self._get_timestamp(),
                },
            )

        message = f"Granted {len(granted)} capability(ies) to '{agent_id}'"
        if already_had:
            message += f" ({len(already_had)} already had)"

        all_caps_present = all(cap in agent_caps for cap in capabilities)
        return {"success": all_caps_present, "granted": granted, "already_had": already_had, "message": message}

    def get_capabilities(self, agent_id: str) -> FrozenSet[str]:
        """
        Get all current capabilities for an agent.

        Args:
            agent_id: The agent to query

        Returns:
            Immutable set of capabilities (empty if unregistered)
        """
        if agent_id not in self._capabilities:
            return frozenset()

        # Return as frozenset (immutable) to prevent external modification
        return frozenset(self._capabilities[agent_id])

    def get_original_capabilities(self, agent_id: str) -> FrozenSet[str]:
        """
        Get the original capabilities assigned at registration.

        Useful for auditing what was revoked/granted since registration.

        Args:
            agent_id: The agent to query

        Returns:
            Immutable set of original capabilities (empty if unregistered)
        """
        return self._original_capabilities.get(agent_id, frozenset())

    def revoke_all(self, agent_id: str, revoker_id: str, reason: Optional[str] = None) -> bool:
        """
        Revoke ALL capabilities from an agent.

        This is the nuclear option - typically used by Narasimha kill-switch.

        Args:
            agent_id: The agent to revoke from
            revoker_id: The agent/system performing the revocation
            reason: Optional reason for revocation

        Returns:
            True if successful, False if agent not registered
        """
        if agent_id not in self._capabilities:
            return False

        # Get current capabilities before clearing
        original_caps = list(self._capabilities[agent_id])

        # Clear all capabilities
        self._capabilities[agent_id] = set()

        # Record in audit trail
        self._ledger.record_event(
            event_type="capability_revoked_all",
            agent_id=agent_id,
            details={
                "revoked_capabilities": original_caps,
                "revoker_id": revoker_id,
                "reason": reason or "TOTAL REVOCATION",
                "timestamp": self._get_timestamp(),
            },
        )

        logger.critical(f"🔒 ALL CAPABILITIES REVOKED from '{agent_id}' by '{revoker_id}'")
        return True

    def is_registered(self, agent_id: str) -> bool:
        """Check if an agent is registered in the capability system."""
        return agent_id in self._capabilities

    def list_all_agents(self) -> List[str]:
        """Get list of all registered agent IDs."""
        return list(self._capabilities.keys())

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()
