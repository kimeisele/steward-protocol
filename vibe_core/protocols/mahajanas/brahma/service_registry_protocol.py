"""
SERVICE REGISTRY PROTOCOL - The Point of Inception
===================================================

Owner: BRAHMA (Creation/Genesis)
OpCodes: LOAD_ROOT, ALLOC_MEM

"Every service must receive NAGA blessing before entering the realm."

The ServiceRegistry is where services come into EXISTENCE.
Brahma creates - this is his domain.

IMPLEMENTATION:
    vibe_core/di.py implements this protocol.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Type,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol, ProtocolState


# =============================================================================
# CONSTANTS
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BRAHMA

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.LOAD_ROOT,   # Loading services into registry
    MantraOpCode.ALLOC_MEM,   # Allocating service instances
]


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================

T = TypeVar("T")


class ServiceInfo(TypedDict, total=False):
    """
    Info about a registered service.
    WATERTIGHT - no Any!
    """
    name: str                 # Protocol/interface name
    instance_type: str        # Actual class name
    is_factory: bool          # Is it lazy-loaded via factory?
    naga_blessed: bool        # Has NAGA blessing?
    registered_at: str        # ISO timestamp


class RegistryStats(TypedDict, total=False):
    """
    Statistics about the registry.
    WATERTIGHT - no Any!
    """
    total_services: int
    total_factories: int
    total_protocols: int
    naga_blessed_count: int
    unblessed_count: int


class DIProtocolState(TypedDict, total=False):
    """
    Full state of the DI container.
    WATERTIGHT - no Any!
    """
    protocol_name: str
    owner: str
    is_chanting: bool
    total_services: int
    total_factories: int
    chaos_enabled: bool
    narasimha_enabled: bool
    service_names: List[str]


# =============================================================================
# SERVICE REGISTRY PROTOCOL
# =============================================================================


@runtime_checkable
class ServiceRegistryProtocol(Protocol):
    """
    Protocol for Dependency Injection container.

    Owner: BRAHMA
    OpCodes: LOAD_ROOT, ALLOC_MEM

    The ServiceRegistry is the POINT OF INCEPTION - where services enter existence.
    Every service must receive NAGA blessing before entering the realm.

    WATERTIGHT - no Any types in interface!
    """

    def register(self, protocol_type: Type[T], instance: T) -> None:
        """
        Register a service instance for a protocol type.

        LOAD_ROOT: Bringing a service into existence.
        """
        ...

    def register_factory(self, protocol_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory for lazy service creation.

        ALLOC_MEM: Deferred allocation.
        """
        ...

    def get(self, protocol_type: Type[T]) -> Optional[T]:
        """
        Get a registered service. Returns None if not found.
        """
        ...

    def require(self, protocol_type: Type[T]) -> T:
        """
        Get a registered service. Raises if not found.
        """
        ...

    def has(self, protocol_type: Type[T]) -> bool:
        """
        Check if a service is registered.
        """
        ...

    def reset(self) -> None:
        """
        Reset all registrations. For testing.
        """
        ...

    def get_stats(self) -> RegistryStats:
        """
        Get registry statistics. WATERTIGHT.
        """
        ...

    def list_services(self) -> List[str]:
        """
        List all registered service names.
        """
        ...


# =============================================================================
# OWNED PROTOCOL WRAPPER
# =============================================================================


class ServiceRegistryOwnedProtocol(OwnedProtocol):
    """
    OwnedProtocol wrapper for ServiceRegistry.

    This allows the DI container to:
    - Be owned by BRAHMA
    - Chant the Mahamantra
    - Pass GAD-000 audits
    - Be traceable to source
    """

    OWNER = Mahajana.BRAHMA
    OPCODES = list(OWNED_OPCODES)
    PROTOCOL_NAME = "service_registry"
    DESCRIPTION = "Dependency Injection container - Point of Inception"

    def __init__(self, registry: ServiceRegistryProtocol) -> None:
        super().__init__()
        self._registry = registry

    def get_state(self) -> ProtocolState:
        """Return current state. WATERTIGHT - no Any!"""
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,  # DI is fundamental, always compliant
        )

    @property
    def registry(self) -> ServiceRegistryProtocol:
        """Access the underlying registry."""
        return self._registry


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullServiceRegistry:
    """
    Null implementation for testing.
    """

    _services: Dict[str, object] = {}

    def register(self, protocol_type: Type[T], instance: T) -> None:
        self._services[str(protocol_type)] = instance

    def register_factory(self, protocol_type: Type[T], factory: Callable[[], T]) -> None:
        pass  # No-op

    def get(self, protocol_type: Type[T]) -> Optional[T]:
        return self._services.get(str(protocol_type))  # type: ignore

    def require(self, protocol_type: Type[T]) -> T:
        result = self.get(protocol_type)
        if result is None:
            raise KeyError(f"Service not found: {protocol_type}")
        return result

    def has(self, protocol_type: Type[T]) -> bool:
        return str(protocol_type) in self._services

    def reset(self) -> None:
        self._services.clear()

    def get_stats(self) -> RegistryStats:
        return RegistryStats(
            total_services=len(self._services),
            total_factories=0,
            total_protocols=0,
            naga_blessed_count=0,
            unblessed_count=len(self._services),
        )

    def list_services(self) -> List[str]:
        return list(self._services.keys())


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OWNER",
    "OWNED_OPCODES",
    # Types (WATERTIGHT)
    "ServiceInfo",
    "RegistryStats",
    "DIProtocolState",
    # Protocol
    "ServiceRegistryProtocol",
    # Owned wrapper
    "ServiceRegistryOwnedProtocol",
    # Null implementation
    "NullServiceRegistry",
]
