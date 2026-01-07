"""
CapabilityEnforcerService - Layer 0 Security Service

GEMINI DECISION: "Security cannot be a plugin."

This is NOT a plugin. This is a core Kernel service that:
1. Cannot be disabled or unloaded
2. Cannot be hot-swapped at runtime
3. Must be injected at kernel construction

The enforcer handles PERMISSION CHECKS only.
Actual capability STORAGE is in CapabilityRegistry.

PERMISSION MODEL:
    Revoke:
        - KERNEL can revoke from anyone
        - CIVIC can revoke from anyone (governance)
        - NARASIMHA can revoke from anyone (kill-switch)
        - Agents can revoke from themselves (voluntary)

    Grant:
        - KERNEL can grant to anyone
        - CIVIC can grant to anyone (governance)
        - No self-grant (prevents privilege escalation)

Usage:
    # In kernel __init__:
    self._capability_enforcer = CapabilityEnforcerService()

    # In revoke_capability:
    if not self._capability_enforcer.can_revoke(revoker_id, target_id):
        return permission_denied_error
"""

import logging
from typing import List, Optional, Protocol, Set, runtime_checkable

from vibe_core.protocols.universal import EnforceContext, EnforceProtocol, Rule, Verdict

logger = logging.getLogger("CAPABILITY_ENFORCER")


# Privileged system identities
SYSTEM_IDENTITIES: Set[str] = {"KERNEL", "NARASIMHA", "civic"}

# Identities that can grant capabilities
GRANTERS: Set[str] = {"KERNEL", "civic"}


@runtime_checkable
class CapabilityEnforcerProtocol(Protocol):
    """
    Protocol for capability enforcement.

    Note: This protocol exists for testing/mocking only.
    In production, the enforcer is NOT hot-swappable.
    """

    def can_revoke(self, revoker_id: str, target_id: str) -> bool:
        """Check if revoker can revoke from target."""
        ...

    def can_grant(self, granter_id: str) -> bool:
        """Check if granter can grant capabilities."""
        ...

    def can_access(self, agent_id: str, capability: str, context: Optional[dict] = None) -> bool:
        """Check if agent can access a capability."""
        ...


class CapabilityEnforcerService(EnforceProtocol):
    """
    Layer 0 Security Service - Capability Permission Enforcement.

    This service implements the permission model for capability operations.
    It is injected into the kernel at construction and cannot be replaced.
    """

    def __init__(self, additional_granters: Optional[List[str]] = None):
        """
        Initialize the enforcer.

        Args:
            additional_granters: Extra identities that can grant (for testing)
        """
        self._granters = GRANTERS.copy()
        if additional_granters:
            self._granters.update(additional_granters)

        self._system_identities = SYSTEM_IDENTITIES.copy()
        logger.info("🔐 CapabilityEnforcerService initialized (Layer 0 Security)")

    def can_revoke(self, revoker_id: str, target_id: str) -> bool:
        """
        Check if revoker_id has permission to revoke capabilities from target_id.

        Permission Model:
            - KERNEL can revoke from anyone
            - CIVIC can revoke from anyone (governance)
            - NARASIMHA can revoke from anyone (kill-switch)
            - Agents can revoke from themselves (voluntary)

        Args:
            revoker_id: The entity attempting to revoke
            target_id: The agent whose capabilities would be revoked

        Returns:
            True if permitted, False otherwise
        """
        # System identities have full revocation permissions
        if revoker_id in self._system_identities:
            logger.debug(f"✅ Revoke permitted: {revoker_id} (system) -> {target_id}")
            return True

        # Self-revocation allowed (Principle of Least Privilege)
        if revoker_id == target_id:
            logger.debug(f"✅ Self-revoke permitted: {revoker_id}")
            return True

        # All other cases denied
        logger.warning(f"❌ Revoke denied: {revoker_id} cannot revoke from {target_id}")
        return False

    def can_grant(self, granter_id: str) -> bool:
        """
        Check if granter_id has permission to grant capabilities.

        Permission Model:
            - KERNEL can grant to anyone
            - CIVIC can grant to anyone (governance)
            - No self-grant (prevents privilege escalation)

        Args:
            granter_id: The entity attempting to grant

        Returns:
            True if permitted, False otherwise
        """
        if granter_id in self._granters:
            logger.debug(f"✅ Grant permitted: {granter_id}")
            return True

        logger.warning(f"❌ Grant denied: {granter_id} is not authorized to grant capabilities")
        return False

    def can_access(
        self,
        agent_id: str,
        capability: str,
        context: Optional[dict] = None,
    ) -> bool:
        """
        Check if agent can access a capability (for runtime checks).

        This is a placeholder for more complex access control logic.
        Currently, access is granted if the agent has the capability
        registered (checked by kernel._check_agent_capability).

        Args:
            agent_id: The agent attempting access
            capability: The capability being accessed
            context: Optional context for the access (e.g., resource being accessed)

        Returns:
            True if permitted (default, defer to capability registry)
        """
        # For now, we defer to the capability registry check in the kernel
        # This method can be extended for:
        # - Time-based access control
        # - Rate limiting
        # - Context-aware permissions
        # - Audit logging
        return True

    def add_granter(self, identity: str) -> None:
        """
        Add a new identity that can grant capabilities.

        WARNING: This should only be called during kernel initialization.
        Runtime modification could be a security risk.

        Args:
            identity: The identity to add as a granter
        """
        logger.warning(f"⚠️ Adding granter: {identity} (security modification)")
        self._granters.add(identity)

    def add_system_identity(self, identity: str) -> None:
        """
        Add a new system identity with full permissions.

        WARNING: This should only be called during kernel initialization.

        Args:
            identity: The identity to add as system
        """
        logger.warning(f"⚠️ Adding system identity: {identity} (security modification)")
        self._system_identities.add(identity)

        return {
            "service": "CapabilityEnforcerService",
            "layer": 0,
            "hot_swappable": False,
            "granters": sorted(self._granters),
            "system_identities": sorted(self._system_identities),
        }

    # =========================================================================
    # ENFORCE PROTOCOL IMPLEMENTATION (SAMKHYA)
    # =========================================================================

    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        """
        Enforce permissions via Atomic Protocol (SAMKHYA: YAMARAJA MODE).

        NRISIMHA UPGRADE:
        - Strict Anti-Mayavad Check: No Sovereign = No Service.
        - Identity Binding: Caller ID must match Sovereign ID.
        """
        # 1. ANTI-MAYAVAD CHECK (The 37th Principle)
        if not context.sovereign:
            logger.critical(
                f"🛑 ANTI-MAYAVAD VIOLATION: Anonymous enforcement attempt. Action: {action}, Caller: {context.caller_id}"
            )
            return Verdict.DENY

        # 2. IDENTITY BINDING (Satyam)
        # Wenn der Caller behauptet "Alice" zu sein, muss der Sovereign Key zu "Alice" gehören.
        if context.caller_id != context.sovereign.identity_id:
            logger.critical(
                f"⚠️ IDENTITY MISMATCH: Caller '{context.caller_id}' claims Sovereign '{context.sovereign.identity_id}'"
            )
            return Verdict.DENY

        # 3. EXECUTE LOGIC
        allowed = False

        try:
            if action == "revoke":
                # context.resource is the target agent ID
                allowed = self.can_revoke(context.caller_id, context.resource)

            elif action == "grant":
                # context.caller_id is the granter
                allowed = self.can_grant(context.caller_id)

            elif action == "access":
                # context.resource is the capability ID
                allowed = self.can_access(context.caller_id, context.resource)

            else:
                logger.warning(f"❌ Unknown action for enforcement: {action}")
                return Verdict.DENY

        except Exception as e:
            logger.error(f"🔥 Enforcer Exception: {str(e)}")
            return Verdict.ESCALATE  # Fehler im Gesetz -> Eskalation an Mensch/Admin

        # 4. VERDICT & LOGGING (Chitragupta)
        verdict = Verdict.ALLOW if allowed else Verdict.DENY

        # Log critical denials for audit
        if verdict == Verdict.DENY:
            logger.warning(f"🛡️ DENIED: {context.caller_id} -> {action} {context.resource}")

        return verdict

    def check(self, action: str) -> bool:
        """
        Quick check if action type is supported.
        Note: Cannot check permission without context (caller).
        """
        return action in {"revoke", "grant", "access"}

    def get_rules(self) -> List[Rule]:
        """Get active rules (Static Policy)."""
        rules = []

        # System identities rule
        for identity in self._system_identities:
            rules.append(
                Rule(
                    id=f"system-{identity}",
                    pattern="*",
                    verdict=Verdict.ALLOW,
                    priority=100,
                    description=f"{identity} has full permissions",
                )
            )

        # Granters rule
        for granter in self._granters:
            rules.append(
                Rule(
                    id=f"granter-{granter}",
                    pattern="grant",
                    verdict=Verdict.ALLOW,
                    priority=90,
                    description=f"{granter} can grant capabilities",
                )
            )

        return rules
