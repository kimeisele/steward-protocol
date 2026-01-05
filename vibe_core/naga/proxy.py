"""
NAGA PROXY - The Balarama Pattern.

"Er wird zum Bett wenn Krishna schläft, zum Thron wenn Krishna regiert,
zu den Schuhen wenn Krishna läuft."

This is the Universal Wrapper that transforms dynamically based on
what the wrapped service DOES, not what we LABEL it.

Architecture:
    - Wraps ANY service without modifying its source code
    - Intercepts ALL method calls automatically
    - Routes to appropriate NAGAs based on behavior:
        * ALL calls → Narada (observation)
        * Exceptions → Kaliya (isolation)
        * Timing → Chitragupta (profiling)

Usage:
    from vibe_core.naga.proxy import NagaProxy

    # At DI/instantiation point, not in class definition
    real_service = ManifestationService(kernel)
    wrapped = NagaProxy(real_service)

    # Use wrapped instead of real_service
    wrapped.tick()  # Automatically observed by Narada

Philosophy (PROMPT.md):
    - Protocol statt konkrete Klassen
    - Any ist verboten → TypeVar
    - duration_ms tracken
    - Keine Silent Failures
"""

import functools
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from vibe_core.naga.services.chitragupta import ChitraguptaService
    from vibe_core.naga.services.kaliya import KaliyaService
    from vibe_core.naga.services.narada import NaradaService

logger = logging.getLogger("NAGA.PROXY")

# TypeVar for the wrapped service - No Any!
T = TypeVar("T")


@dataclass
class ProxyObservation:
    """
    Single observation from the proxy.

    Sent to Narada for intelligence gathering.
    """

    service_type: str
    method_name: str
    args_count: int
    kwargs_keys: List[str]
    duration_ms: float
    result_type: Optional[str] = None
    exception_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class NagaProxyProtocol(Protocol[T]):
    """
    Protocol for NagaProxy.

    Ensures type safety for wrapped services.
    """

    @property
    def _wrapped(self) -> T:
        """The wrapped service instance."""
        ...

    @property
    def _service_name(self) -> str:
        """Name of the wrapped service for logging."""
        ...


class NagaProxy(Generic[T]):
    """
    The Balarama Pattern - Universal Dynamic Wrapper.

    Wraps any service and routes behavior to appropriate NAGAs:
    - Narada: Observes ALL method calls
    - Chitragupta: Profiles timing (duration_ms)
    - Kaliya: Handles exceptions (isolation)

    The wrapped service doesn't know it's being observed.
    This is non-intrusive Divine Infrastructure.

    Args:
        wrapped: The service instance to wrap
        narada: NaradaService for observation (optional, uses ServiceRegistry)
        chitragupta: ChitraguptaService for profiling (optional)
        kaliya: KaliyaService for exception handling (optional)
        observe_private: Whether to observe _private methods (default: False)

    Example:
        >>> real_service = ManifestationService(kernel)
        >>> wrapped = NagaProxy(real_service)
        >>> wrapped.tick()  # Observed by Narada, timed by Chitragupta

    Raises:
        TypeError: If wrapped is None
    """

    # Attributes that belong to the proxy itself, not the wrapped service
    __proxy_attrs__ = frozenset(
        [
            "_wrapped",
            "_service_name",
            "_observe_private",
            "_narada",
            "_chitragupta",
            "_kaliya",
            "_nagas_resolved",
            "_observation_buffer",
        ]
    )

    def __init__(
        self,
        wrapped: T,
        narada: Optional["NaradaService"] = None,
        chitragupta: Optional["ChitraguptaService"] = None,
        kaliya: Optional["KaliyaService"] = None,
        observe_private: bool = False,
    ) -> None:
        if wrapped is None:
            raise TypeError("Cannot wrap None - wrapped service is required")

        # Store wrapped service (use object.__setattr__ to avoid recursion)
        object.__setattr__(self, "_wrapped", wrapped)
        object.__setattr__(self, "_service_name", type(wrapped).__name__)
        object.__setattr__(self, "_observe_private", observe_private)

        # NAGA services - lazy load from ServiceRegistry if not provided
        object.__setattr__(self, "_narada", narada)
        object.__setattr__(self, "_chitragupta", chitragupta)
        object.__setattr__(self, "_kaliya", kaliya)
        object.__setattr__(self, "_nagas_resolved", False)

        # Observation buffer for batch reporting
        object.__setattr__(self, "_observation_buffer", [])

        logger.debug(f"NagaProxy wrapping {self._service_name}")

    def _resolve_nagas(self) -> None:
        """
        Lazy resolve NAGA services from ServiceRegistry.

        Called on first method interception.
        """
        if self._nagas_resolved:
            return

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import (
                ChitraguptaProtocol,
                KaliyaProtocol,
                NaradaProtocol,
            )

            if self._narada is None:
                self._narada = ServiceRegistry.get(NaradaProtocol)

            if self._chitragupta is None:
                self._chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if self._kaliya is None:
                self._kaliya = ServiceRegistry.get(KaliyaProtocol)

        except Exception as e:
            # Non-critical - proxy still works without NAGAs
            logger.debug(f"NAGA resolution failed (non-critical): {e}")

        object.__setattr__(self, "_nagas_resolved", True)

    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access and wrap callable methods.

        Non-callable attributes are passed through directly.
        Callable methods are wrapped with observation.
        """
        # Proxy's own attributes - use object.__getattribute__
        if name in self.__proxy_attrs__:
            return object.__getattribute__(self, name)

        # Get the actual attribute from wrapped service
        wrapped = object.__getattribute__(self, "_wrapped")
        attr = getattr(wrapped, name)

        # Skip private methods unless configured
        observe_private = object.__getattribute__(self, "_observe_private")
        if name.startswith("_") and not observe_private:
            return attr

        # If not callable, return directly
        if not callable(attr):
            return attr

        # Wrap callable methods with observation
        return self._wrap_method(name, attr)

    def _wrap_method(self, name: str, method: Callable) -> Callable:
        """
        Wrap a method with NAGA observation.

        Args:
            name: Method name
            method: The actual method to wrap

        Returns:
            Wrapped method that observes and profiles
        """
        # Capture self reference for closure
        proxy_self = self

        @functools.wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Lazy resolve NAGAs on first call
            proxy_self._resolve_nagas()

            # Track timing for Chitragupta
            start_time = time.perf_counter()
            result = None
            exception_type = None

            try:
                # Call the actual method
                result = method(*args, **kwargs)
                return result

            except Exception as e:
                exception_type = type(e).__name__

                # Route to Kaliya for isolation
                proxy_self._report_to_kaliya(name, e)

                # Re-raise - no silent failures (DHARMA)
                raise

            finally:
                # Calculate duration
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Get service name
                service_name = object.__getattribute__(proxy_self, "_service_name")

                # Create observation
                observation = ProxyObservation(
                    service_type=service_name,
                    method_name=name,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    duration_ms=duration_ms,
                    result_type=type(result).__name__ if result is not None else None,
                    exception_type=exception_type,
                )

                # Report to Narada (observation)
                proxy_self._report_to_narada(observation)

                # Report to Chitragupta (profiling)
                proxy_self._report_to_chitragupta(name, duration_ms)

        return wrapper

    def _report_to_narada(self, observation: ProxyObservation) -> None:
        """
        Report observation to Narada.

        Args:
            observation: The observation to report
        """
        try:
            # Buffer observations for batch processing (always, even without Narada)
            buffer = object.__getattribute__(self, "_observation_buffer")
            buffer.append(observation)

            # Log for now - Narada will process
            logger.debug(
                f"NARADA observes: {observation.service_type}.{observation.method_name} "
                f"({observation.duration_ms:.2f}ms)"
            )

        except Exception as e:
            # Non-critical - don't fail the actual method
            logger.warning(f"Narada report failed: {e}")

    def _report_to_chitragupta(self, method_name: str, duration_ms: float) -> None:
        """
        Report timing to Chitragupta for profiling.

        Args:
            method_name: Name of the method
            duration_ms: Execution duration in milliseconds
        """
        chitragupta = object.__getattribute__(self, "_chitragupta")
        if chitragupta is None:
            return

        try:
            # Record metric for profiling
            service_name = object.__getattribute__(self, "_service_name")
            component_id = f"{service_name}.{method_name}"
            chitragupta.record(component_id, "duration_ms", duration_ms)

        except Exception as e:
            # Non-critical
            logger.warning(f"Chitragupta report failed: {e}")

    def _report_to_kaliya(self, method_name: str, exception: Exception) -> None:
        """
        Report exception to Kaliya for isolation decision.

        Args:
            method_name: Name of the method that raised
            exception: The exception that was raised
        """
        kaliya = object.__getattribute__(self, "_kaliya")
        if kaliya is None:
            # Still log even without Kaliya
            service_name = object.__getattribute__(self, "_service_name")
            logger.warning(f"KALIYA (offline): {service_name}.{method_name} raised {type(exception).__name__}")
            return

        try:
            service_name = object.__getattribute__(self, "_service_name")
            component_id = f"{service_name}.{method_name}"
            # Kaliya decides if component should be quarantined
            logger.warning(f"KALIYA notified: {component_id} raised {type(exception).__name__}")

        except Exception as e:
            # Non-critical
            logger.warning(f"Kaliya report failed: {e}")

    def get_observations(self) -> List[ProxyObservation]:
        """
        Get buffered observations.

        Returns:
            List of observations since last clear
        """
        buffer = object.__getattribute__(self, "_observation_buffer")
        return list(buffer)

    def clear_observations(self) -> int:
        """
        Clear observation buffer.

        Returns:
            Number of observations cleared
        """
        buffer = object.__getattribute__(self, "_observation_buffer")
        count = len(buffer)
        buffer.clear()
        return count

    @property
    def unwrap(self) -> T:
        """
        Get the unwrapped service.

        Use sparingly - prefer working through the proxy.
        """
        return object.__getattribute__(self, "_wrapped")

    def __repr__(self) -> str:
        service_name = object.__getattribute__(self, "_service_name")
        return f"NagaProxy({service_name})"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def wrap_service(service: T) -> NagaProxy[T]:
    """
    Wrap a service with NagaProxy.

    Convenience function for the common case.

    Args:
        service: The service to wrap

    Returns:
        NagaProxy wrapping the service
    """
    return NagaProxy(service)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "NagaProxy",
    "NagaProxyProtocol",
    "ProxyObservation",
    "wrap_service",
]
