"""
Dependency Injection Container for Vibe Core.

OPUS-209 Phase 0: Foundation for kernel extraction.

Replaces: 5 different singleton patterns scattered across codebase:
- StateService: Dict registry `_instances`
- Weaver: Global variable `_global_weaver`
- EventBus: Multiple patterns
- CycleRegistry: Global variable
- SynapseStore: Class dict `_instances`

Usage:
    # Register a service
    ServiceRegistry.register(VibeLedger, SQLiteLedger(path))

    # Get a service
    ledger = ServiceRegistry.get(VibeLedger)

    # Get or raise
    ledger = ServiceRegistry.require(VibeLedger)

    # Testing - reset all
    ServiceRegistry.reset()
"""

import logging
import threading
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger("DI")
T = TypeVar("T")


class ServiceRegistry:
    """
    Centralized Dependency Injection Container.

    Thread-safe. Singleton-aware. Test-friendly.

    Design Principles:
    1. Single source of truth for service instances
    2. Interface-based registration (register interface, get interface)
    3. Factory support for lazy instantiation
    4. Thread-safe with minimal locking overhead
    5. Easy reset for testing
    """

    _services: Dict[str, Any] = {}
    _factories: Dict[str, Callable] = {}
    _lock = threading.Lock()

    @classmethod
    def register(cls, interface: Type[T], instance: T) -> None:
        """
        Register a concrete instance for an interface.

        Args:
            interface: The interface/protocol type (e.g., VibeLedger)
            instance: The concrete implementation (e.g., SQLiteLedger)

        Example:
            ServiceRegistry.register(VibeLedger, SQLiteLedger("/path/to/db"))
        """
        with cls._lock:
            name = interface.__name__
            cls._services[name] = instance
            logger.debug(f"[DI] Registered: {name}")

    @classmethod
    def register_factory(cls, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory for lazy instantiation.

        The factory is called on first get() and cached thereafter.

        Args:
            interface: The interface/protocol type
            factory: Callable that returns an instance

        Example:
            ServiceRegistry.register_factory(
                VibeLedger,
                lambda: SQLiteLedger(config.paths.ledger)
            )
        """
        with cls._lock:
            name = interface.__name__
            cls._factories[name] = factory
            logger.debug(f"[DI] Registered factory: {name}")

    @classmethod
    def get(cls, interface: Type[T]) -> Optional[T]:
        """
        Get a service by interface type.

        Returns None if not registered (use require() for strict access).

        Args:
            interface: The interface/protocol type

        Returns:
            The registered instance, or None if not found
        """
        with cls._lock:
            name = interface.__name__

            # Instance first (already created)
            if name in cls._services:
                return cls._services[name]

            # Factory fallback (lazy instantiation)
            if name in cls._factories:
                instance = cls._factories[name]()
                cls._services[name] = instance
                logger.debug(f"[DI] Lazy-created: {name}")
                return instance

            return None

    @classmethod
    def require(cls, interface: Type[T]) -> T:
        """
        Get a service or raise RuntimeError if not registered.

        Use this when the service MUST exist (fail-fast).

        Args:
            interface: The interface/protocol type

        Returns:
            The registered instance

        Raises:
            RuntimeError: If service not registered
        """
        service = cls.get(interface)
        if service is None:
            raise RuntimeError(f"[DI] Service not registered: {interface.__name__}")
        return service

    @classmethod
    def reset(cls) -> None:
        """
        Reset all services.

        FOR TESTING ONLY. Clears all registered instances.
        Factories are preserved (they can recreate instances).
        """
        with cls._lock:
            cls._services.clear()
            logger.warning("[DI] Registry reset (test mode)")

    @classmethod
    def reset_all(cls) -> None:
        """
        Reset everything including factories.

        FOR TESTING ONLY. Complete wipe.
        """
        with cls._lock:
            cls._services.clear()
            cls._factories.clear()
            logger.warning("[DI] Registry fully reset (test mode)")

    @classmethod
    def is_registered(cls, interface: Type[T]) -> bool:
        """
        Check if a service is registered (instance or factory).

        Args:
            interface: The interface/protocol type

        Returns:
            True if registered, False otherwise
        """
        with cls._lock:
            name = interface.__name__
            return name in cls._services or name in cls._factories

    @classmethod
    def list_services(cls) -> Dict[str, str]:
        """
        List all registered services (for debugging).

        Returns:
            Dict of {interface_name: instance_type}
        """
        with cls._lock:
            result = {}
            for name, instance in cls._services.items():
                result[name] = type(instance).__name__
            for name in cls._factories:
                if name not in result:
                    result[name] = "(factory - not yet instantiated)"
            return result
