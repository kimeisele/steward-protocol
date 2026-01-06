"""
Dependency Injection Container for Vibe Core.

OPUS-209 Phase 0: Foundation for kernel extraction.

Replaces: 5 different singleton patterns scattered across codebase:
- StateService: Dict registry `_instances`
- Weaver: Global variable `_global_weaver`
- EventBus: Multiple patterns
- CycleRegistry: Global variable
- SynapseStore: Class dict `_instances`

NAGA LOKA INTEGRATION:
    The ServiceRegistry is the POINT OF INCEPTION - where services enter existence.
    Every service must receive NAGA blessing before entering the realm.

    Blessing Check (Hybrid Mode):
    1. Priority A: Check if instance inherits from NagaBaseService
    2. Priority B: Check for _naga_flooded marker (Soft Flood via Mixins)
    3. Priority C: Check if wrapped in NagaProxy (Hard Flood)
    4. If unblessed: Log DHARMA_BREACH, enforce for critical services

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
from typing import Callable, Dict, Optional, Protocol, Type, TypeVar, runtime_checkable

logger = logging.getLogger("DI")
T = TypeVar("T")


@runtime_checkable
class ServiceInstance(Protocol):
    """Protocol for any service that can be registered in the DI container."""

    pass  # Marker protocol - any object qualifies


class ThreatDetails:
    """Type-safe threat details for Narasimha reporting."""

    __slots__ = ("caller", "target", "extra")

    def __init__(self, caller: str, target: str, **extra: str) -> None:
        self.caller = caller
        self.target = target
        self.extra = extra

    def get(self, key: str, default: str = "UNKNOWN") -> str:
        if key == "caller":
            return self.caller
        if key == "target":
            return self.target
        return self.extra.get(key, default)


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
    6. CHAOS INJECTION for antifragility testing (Prahlad)
    7. NARASIMHA GATEKEEPER for security validation

    Security:
    The Narasimha Gatekeeper validates:
    - register(): Services must be from allowed modules (optional)
    - inject_chaos(): Only authorized callers (Prahlad)
    - All operations logged to threat detection
    """

    _services: Dict[str, object] = {}  # object not Any - heterogeneous but typed
    _factories: Dict[str, Callable[[], object]] = {}
    _chaos_injectors: Dict[str, Callable[[], object]] = {}  # Prahlad chaos testing
    _chaos_enabled: bool = False
    _lock = threading.Lock()

    # NARASIMHA GATEKEEPER
    _narasimha_enabled: bool = False
    _blessed_modules: set[str] = set()  # Allowed module prefixes for registration
    _chaos_authorized_callers: set[str] = {"PrahladService", "chaos_probe_real"}  # Who can inject chaos

    # NAGA LOKA - Blessing Enforcement (Point of Inception)
    _naga_blessing_enabled: bool = False
    _naga_strict_mode: bool = False  # If True, reject unblessed critical services
    _naga_critical_services: set[str] = {
        # Services that MUST be NAGA-blessed (security critical)
        "PluginServiceProtocol",
        "PluginService",
        "TaskManager",
        "VibeLedger",
        "CISyncService",
    }
    _naga_blessing_violations: list[str] = []  # Track DHARMA breaches for audit

    @classmethod
    def register(cls, interface: Type[T], instance: T) -> None:
        """
        Register a concrete instance for an interface.

        NAGA LOKA: Point of Inception - every service receives blessing check.

        Args:
            interface: The interface/protocol type (e.g., VibeLedger)
            instance: The concrete implementation (e.g., SQLiteLedger)

        Example:
            ServiceRegistry.register(VibeLedger, SQLiteLedger("/path/to/db"))

        Raises:
            DharmaViolation: If strict mode and critical service is unblessed
        """
        with cls._lock:
            name = interface.__name__

            # === NAGA LOKA: Blessing Check (Point of Inception) ===
            if cls._naga_blessing_enabled:
                is_blessed = cls._check_naga_blessing(instance)

                if not is_blessed:
                    instance_type = type(instance).__name__
                    violation = f"{name} ({instance_type})"
                    cls._naga_blessing_violations.append(violation)

                    # Log DHARMA BREACH (Narada observes)
                    logger.warning(f"[DI] DHARMA BREACH: {violation} registered without NAGA blessing")

                    # Strict mode: Reject unblessed critical services
                    if cls._naga_strict_mode and name in cls._naga_critical_services:
                        raise RuntimeError(
                            f"[DI] DHARMA VIOLATION: Critical service {name} must be NAGA-blessed. "
                            f"Use NagaBaseService inheritance or apply Soft Flood."
                        )

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

        Note:
            If chaos mode is enabled and a chaos injector is registered
            for this interface, the chaos injector is called instead.
            This allows Prahlad to test system resilience.
        """
        with cls._lock:
            name = interface.__name__

            # CHAOS INJECTION: If enabled, chaos injector takes precedence
            if cls._chaos_enabled and name in cls._chaos_injectors:
                logger.warning(f"[DI] CHAOS: Injecting for {name}")
                return cls._chaos_injectors[name]()

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

    # =========================================================================
    # CHAOS INJECTION (Prahlad Antifragility Testing)
    # =========================================================================

    @classmethod
    def inject_chaos(cls, interface: Type[T], injector: Callable[[], T]) -> None:
        """
        Register a chaos injector for antifragility testing.

        SECURITY: When Narasimha Gatekeeper is enabled, only authorized
        callers (PrahladService) can inject chaos. This prevents
        malicious code from poisoning the service registry.

        When chaos mode is enabled, this injector replaces the normal
        service resolution. Use to test system resilience:

        - Return a broken/slow/malicious mock
        - Raise exceptions
        - Return None unexpectedly
        - Return a working but subtly wrong implementation

        Args:
            interface: The interface/protocol type to poison
            injector: Callable that returns the chaos version

        Raises:
            PermissionError: If Narasimha blocks unauthorized caller
        """
        import inspect

        # NARASIMHA GATEKEEPER: Check caller authorization
        if cls._narasimha_enabled:
            frame = inspect.currentframe()
            caller_info = ""
            try:
                if frame and frame.f_back:
                    caller_frame = frame.f_back
                    caller_info = f"{caller_frame.f_code.co_name}"
                    # Also check class name if available
                    if "self" in caller_frame.f_locals:
                        caller_class = type(caller_frame.f_locals["self"]).__name__
                        caller_info = f"{caller_class}.{caller_info}"
            finally:
                del frame

            # Check if caller is authorized
            authorized = any(auth in caller_info for auth in cls._chaos_authorized_callers)
            if not authorized:
                cls._report_threat(
                    threat_type="UNAUTHORIZED_CHAOS_INJECTION",
                    details=ThreatDetails(
                        caller=caller_info,
                        target=interface.__name__,
                    ),
                )
                raise PermissionError(
                    f"[DI] NARASIMHA BLOCKED: Unauthorized chaos injection by {caller_info}. "
                    f"Only {cls._chaos_authorized_callers} can inject chaos."
                )

        with cls._lock:
            name = interface.__name__
            cls._chaos_injectors[name] = injector
            logger.info(f"[DI] CHAOS: Registered injector for {name}")

    @classmethod
    def enable_chaos(cls) -> None:
        """
        Enable chaos mode.

        When enabled, chaos injectors take precedence over normal services.
        Call this before running antifragility tests.
        """
        with cls._lock:
            cls._chaos_enabled = True
            logger.warning("[DI] CHAOS MODE ENABLED - Service resolution poisoned")

    @classmethod
    def disable_chaos(cls) -> None:
        """
        Disable chaos mode.

        Returns to normal service resolution.
        """
        with cls._lock:
            cls._chaos_enabled = False
            logger.info("[DI] CHAOS MODE DISABLED - Normal service resolution")

    @classmethod
    def clear_chaos(cls) -> None:
        """
        Clear all chaos injectors and disable chaos mode.

        Call this after antifragility tests to restore normal operation.
        """
        with cls._lock:
            cls._chaos_injectors.clear()
            cls._chaos_enabled = False
            logger.info("[DI] CHAOS: All injectors cleared, mode disabled")

    @classmethod
    def is_chaos_enabled(cls) -> bool:
        """Check if chaos mode is currently enabled."""
        return cls._chaos_enabled

    @classmethod
    def list_chaos_injectors(cls) -> list:
        """List all registered chaos injectors (for debugging)."""
        with cls._lock:
            return list(cls._chaos_injectors.keys())

    # =========================================================================
    # NARASIMHA GATEKEEPER (Security Layer)
    # =========================================================================

    @classmethod
    def enable_narasimha(cls) -> None:
        """
        Enable the Narasimha Gatekeeper.

        When enabled:
        - inject_chaos() only allowed by authorized callers
        - Threats are reported to the Narasimha protocol
        - All sensitive operations are logged

        This is the SHIELD before the SPEAR (chaos testing).
        """
        with cls._lock:
            cls._narasimha_enabled = True
            logger.warning("[DI] NARASIMHA GATEKEEPER ENABLED - Security validation active")

    @classmethod
    def disable_narasimha(cls) -> None:
        """Disable the Narasimha Gatekeeper (for testing only)."""
        with cls._lock:
            cls._narasimha_enabled = False
            logger.info("[DI] NARASIMHA GATEKEEPER DISABLED")

    @classmethod
    def is_narasimha_enabled(cls) -> bool:
        """Check if Narasimha Gatekeeper is active."""
        return cls._narasimha_enabled

    @classmethod
    def authorize_chaos_caller(cls, caller_name: str) -> None:
        """
        Authorize an additional caller to inject chaos.

        Args:
            caller_name: Function or class name to authorize
        """
        with cls._lock:
            cls._chaos_authorized_callers.add(caller_name)
            logger.info(f"[DI] NARASIMHA: Authorized {caller_name} for chaos injection")

    @classmethod
    def _report_threat(cls, threat_type: str, details: ThreatDetails) -> None:
        """
        Report a threat to the Narasimha protocol.

        This connects the ServiceRegistry security to the main
        Narasimha threat detection system.

        Args:
            threat_type: Type of threat (e.g., UNAUTHORIZED_CHAOS_INJECTION)
            details: ThreatDetails with caller and target info
        """
        try:
            import time

            from vibe_core.narasimha import ThreatIndicator, ThreatLevel, get_narasimha

            narasimha = get_narasimha()
            indicator = ThreatIndicator(
                indicator_type=threat_type,
                agent_id=details.caller,
                severity=ThreatLevel.RED,
                description=f"ServiceRegistry security violation: {threat_type}",
                evidence={"caller": details.caller, "target": details.target, **details.extra},
                timestamp=time.time(),
            )
            narasimha.register_threat(indicator)
            logger.critical(f"[DI] NARASIMHA THREAT: {threat_type} - caller={details.caller}, target={details.target}")

        except Exception as e:
            # Graceful degradation - still log even if Narasimha unavailable
            logger.error(f"[DI] THREAT (Narasimha unavailable): {threat_type} - {details.caller} - {e}")

    # =========================================================================
    # NAGA LOKA - Blessing Enforcement (Point of Inception)
    # =========================================================================

    @classmethod
    def _check_naga_blessing(cls, instance: object) -> bool:
        """
        Check if a service instance is NAGA-blessed.

        A service is blessed if it has NAGA infrastructure integration:
        1. Inherits from NagaBaseService (self-monitoring)
        2. Has _naga_flooded marker (Soft Flood via Mixins)
        3. Is wrapped in NagaProxy (Hard Flood)

        Args:
            instance: The service instance to check

        Returns:
            True if blessed, False if naked/unprotected
        """
        instance_type = type(instance)

        # Priority A: Check NagaBaseService inheritance
        try:
            from vibe_core.naga.services.base import NagaBaseService

            if isinstance(instance, NagaBaseService):
                return True
        except ImportError:
            pass  # NAGAs not available - graceful degradation

        # Priority B: Check _naga_flooded marker (Soft Flood via Mixins)
        if getattr(instance_type, "_naga_flooded", False):
            return True

        # Priority C: Check NagaProxy wrapping (Hard Flood)
        try:
            from vibe_core.naga.proxy import NagaProxy

            if isinstance(instance, NagaProxy):
                return True
        except ImportError:
            pass

        # Priority D: Check NagaCapabilityMixin inheritance
        try:
            from vibe_core.naga.mixins import NagaCapabilityMixin

            if isinstance(instance, NagaCapabilityMixin):
                return True
        except ImportError:
            pass

        return False

    @classmethod
    def enable_naga_blessing(cls, strict: bool = False) -> None:
        """
        Enable NAGA blessing enforcement.

        When enabled, all service registrations are checked for NAGA blessing.
        Unblessed services trigger DHARMA_BREACH warnings.

        Args:
            strict: If True, reject unblessed critical services (default: False)
        """
        with cls._lock:
            cls._naga_blessing_enabled = True
            cls._naga_strict_mode = strict
            cls._naga_blessing_violations.clear()
            mode = "STRICT" if strict else "WARNING"
            logger.warning(f"[DI] NAGA LOKA ENABLED - Blessing enforcement active ({mode} mode)")

    @classmethod
    def disable_naga_blessing(cls) -> None:
        """Disable NAGA blessing enforcement (for testing)."""
        with cls._lock:
            cls._naga_blessing_enabled = False
            cls._naga_strict_mode = False
            logger.info("[DI] NAGA LOKA DISABLED")

    @classmethod
    def is_naga_blessing_enabled(cls) -> bool:
        """Check if NAGA blessing enforcement is active."""
        return cls._naga_blessing_enabled

    @classmethod
    def get_blessing_violations(cls) -> list:
        """
        Get list of DHARMA breaches (unblessed service registrations).

        Returns:
            List of "{interface} ({instance_type})" strings
        """
        with cls._lock:
            return list(cls._naga_blessing_violations)

    @classmethod
    def add_critical_service(cls, service_name: str) -> None:
        """
        Add a service to the critical list (requires blessing in strict mode).

        Args:
            service_name: Interface name to mark as critical
        """
        with cls._lock:
            cls._naga_critical_services.add(service_name)
            logger.debug(f"[DI] Added critical service: {service_name}")

    @classmethod
    def clear_blessing_violations(cls) -> int:
        """
        Clear the violation log.

        Returns:
            Number of violations cleared
        """
        with cls._lock:
            count = len(cls._naga_blessing_violations)
            cls._naga_blessing_violations.clear()
            return count
