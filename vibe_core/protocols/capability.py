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
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


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
