"""
OPUS-307 D+++: Unified Capability Protocol

THE FRACTAL PRINCIPLE: Tool, Circuit, Agent are all CAPABILITIES.
The interface is identical. Pratyaya decides the executor.

Shabda (steward run X) → Pratyaya (CapabilityRegistry → Executor) → Karma (Result)

Types:
- ATOMIC: Tools (single action)
- MOLECULAR: Circuits (state machine)
- ORGANIC: Agents (autonomous entity)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, TypedDict, runtime_checkable


# =============================================================================
# WATERTIGHT TYPEDDICTS - No Dict[str, Any] for registry operations
# =============================================================================


class CapabilityModifyResult(TypedDict, total=False):
    """Result of a capability modification (grant/revoke). WATERTIGHT."""

    success: bool
    revoked: List[str]  # For revoke operations
    granted: List[str]  # For grant operations
    not_found: List[str]  # Capabilities not found
    already_had: List[str]  # Capabilities already present (for grant)
    message: str


class CapabilityType(Enum):
    """The three levels of capability complexity."""

    ATOMIC = "atomic"  # Tool - single action
    MOLECULAR = "molecular"  # Circuit - state machine
    ORGANIC = "organic"  # Agent - autonomous entity


@dataclass
class CapabilityResult:
    """
    Unified result from any capability execution.

    Same interface whether Tool, Circuit, or Agent.
    """

    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution trace (for debugging/audit)
    capability_id: str = ""
    capability_type: CapabilityType = CapabilityType.ATOMIC
    execution_time_ms: float = 0.0


@dataclass
class CapabilityMeta:
    """
    Unified metadata for any capability.

    Discoverable via CapabilityRegistry.
    """

    capability_id: str
    capability_type: CapabilityType
    description: str
    version: str = "1.0.0"

    # Schema for input validation
    parameters_schema: Dict[str, Any] = field(default_factory=dict)

    # Source info
    source_file: str = ""
    source_module: str = ""

    # Additional metadata
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False

    def __repr__(self) -> str:
        return f"<{self.capability_type.value}:{self.capability_id}>"


@runtime_checkable
class Capability(Protocol):
    """
    The universal interface for all capabilities.

    Whether Tool, Circuit, or Agent - they all implement this.
    Pratyaya doesn't care about the internal implementation.
    """

    @property
    def capability_id(self) -> str:
        """Unique identifier for this capability."""
        ...

    @property
    def capability_type(self) -> CapabilityType:
        """What kind of capability is this?"""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        ...

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """Schema for input validation."""
        ...

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate input parameters. Raise ValueError if invalid."""
        ...

    def execute(self, parameters: Dict[str, Any]) -> CapabilityResult:
        """Execute the capability and return unified result."""
        ...


class CapabilityAdapter(ABC):
    """
    Adapts existing Tools/Circuits/Agents to Capability protocol.

    This is the bridge that unifies the existing codebase.
    """

    @abstractmethod
    def adapt(self, source: Any) -> Capability:
        """Adapt a source object to Capability protocol."""
        ...

    @abstractmethod
    def get_meta(self, source: Any) -> CapabilityMeta:
        """Extract metadata from source object."""
        ...


# =============================================================================
# CAPABILITY REGISTRY PROTOCOL - WATERTIGHT Phase 2
# =============================================================================


@runtime_checkable
class CapabilityRegistryProtocol(Protocol):
    """
    Protocol for agent capability management.

    WATERTIGHT: All methods use typed returns, no Dict[str, Any].

    Implementations:
        - CapabilityRegistry (persistent with ledger audit trail)
        - NullCapabilityRegistry (for testing)

    Usage:
        registry = ServiceRegistry.get(CapabilityRegistryProtocol)
        registry.register_agent("agent_001", ["read_file", "write_file"])
    """

    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """
        Register an agent with initial capabilities.

        Args:
            agent_id: The agent to register
            capabilities: List of initial capabilities
        """
        ...

    def has_capability(self, agent_id: str, capability: str) -> bool:
        """
        Check if an agent has a specific capability.

        Args:
            agent_id: The agent to check
            capability: The capability required

        Returns:
            True if agent has the capability, False otherwise
        """
        ...

    def revoke(
        self,
        agent_id: str,
        capabilities: List[str],
        revoker_id: str,
        reason: Optional[str] = None,
    ) -> CapabilityModifyResult:
        """
        Revoke one or more capabilities from an agent.

        Args:
            agent_id: The agent to revoke from
            capabilities: List of capabilities to revoke
            revoker_id: The agent/system performing the revocation
            reason: Optional reason for revocation (for audit trail)

        Returns:
            CapabilityModifyResult with success, revoked, not_found, message
        """
        ...

    def grant(
        self,
        agent_id: str,
        capabilities: List[str],
        granter_id: str,
        reason: Optional[str] = None,
    ) -> CapabilityModifyResult:
        """
        Grant new capabilities to an agent.

        Args:
            agent_id: The agent to grant to
            capabilities: List of capabilities to grant
            granter_id: The agent/system performing the grant
            reason: Optional reason for grant (for audit trail)

        Returns:
            CapabilityModifyResult with success, granted, already_had, message
        """
        ...

    def get_capabilities(self, agent_id: str) -> FrozenSet[str]:
        """
        Get all current capabilities for an agent.

        Args:
            agent_id: The agent to query

        Returns:
            Immutable set of capabilities (empty if unregistered)
        """
        ...

    def get_original_capabilities(self, agent_id: str) -> FrozenSet[str]:
        """
        Get the original capabilities assigned at registration.

        Args:
            agent_id: The agent to query

        Returns:
            Immutable set of original capabilities (empty if unregistered)
        """
        ...

    def revoke_all(self, agent_id: str, revoker_id: str, reason: Optional[str] = None) -> bool:
        """
        Revoke ALL capabilities from an agent (nuclear option).

        Args:
            agent_id: The agent to revoke from
            revoker_id: The agent/system performing the revocation
            reason: Optional reason for revocation

        Returns:
            True if successful, False if agent not registered
        """
        ...

    def is_registered(self, agent_id: str) -> bool:
        """Check if an agent is registered in the capability system."""
        ...

    def list_all_agents(self) -> List[str]:
        """Get list of all registered agent IDs."""
        ...
