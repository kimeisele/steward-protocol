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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x463c5533"  # GenesisByte: parampara % 37 == 0

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
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
)

from vibe_core.protocols.naga.groups import Subject, Verdict
from vibe_core.protocols.naga.types import ObservationDict

if TYPE_CHECKING:
    from vibe_core.naga.services.chitragupta import ChitraguptaService
    from vibe_core.naga.services.kaliya import KaliyaService
    from vibe_core.naga.services.narada import NaradaService
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.naga.services.takshaka import TakshakaService
    from vibe_core.protocols.substrate import MantraOpCode


logger = logging.getLogger("NAGA.PROXY")

# TypeVar for the wrapped service
T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


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
            "_sesha",
            "_takshaka",
            "_nagas_resolved",
            "_observation_buffer",
            "_audit_enabled",
            # IDENTITY (Vedic Stack - introspected from target)
            "_position",
            "_guardian",
            "_genesis",
        ]
    )

    def __init__(
        self,
        wrapped: T,
        narada: Optional["NaradaService"] = None,
        chitragupta: Optional["ChitraguptaService"] = None,
        kaliya: Optional["KaliyaService"] = None,
        sesha: Optional["SeshaService"] = None,
        takshaka: Optional["TakshakaService"] = None,
        observe_private: bool = False,
        audit_enabled: bool = True,
    ) -> None:
        if wrapped is None:
            raise TypeError("Cannot wrap None - wrapped service is required")

        # Store wrapped service (use object.__setattr__ to avoid recursion)
        object.__setattr__(self, "_wrapped", wrapped)
        object.__setattr__(self, "_service_name", type(wrapped).__name__)
        object.__setattr__(self, "_observe_private", observe_private)
        object.__setattr__(self, "_audit_enabled", audit_enabled)

        # NAGA services - lazy load from ServiceRegistry if not provided
        object.__setattr__(self, "_narada", narada)
        object.__setattr__(self, "_chitragupta", chitragupta)
        object.__setattr__(self, "_kaliya", kaliya)
        object.__setattr__(self, "_sesha", sesha)
        object.__setattr__(self, "_takshaka", takshaka)
        object.__setattr__(self, "_nagas_resolved", False)

        # Observation buffer for batch reporting
        object.__setattr__(self, "_observation_buffer", [])

        # IDENTITY INTROSPECTION (Vedic Stack)
        # NagaProxy "sees" the identity of its target if wrapped by MahamantraProxy
        # MAHAMANTRA DEFINES IDENTITY - FOLDER IS TRUTH
        position = getattr(wrapped, "_position", -1)
        guardian = getattr(wrapped, "_guardian", "unknown")
        genesis = getattr(wrapped, "_genesis", "")

        # If not set by MahamantraProxy, DERIVE from folder (not labels!)
        # "Manual Labor ist Maya" - MAHAPROMPT.md
        if position == -1 or guardian == "unknown":
            from pathlib import Path
            from vibe_core.mahamantra.substrate.sankirtan import get_mahajana_for_path

            # Try to get module file path
            wrapped_module = getattr(wrapped, "__module__", None)
            wrapped_file = None
            if wrapped_module:
                import sys
                mod = sys.modules.get(wrapped_module)
                if mod:
                    wrapped_file = getattr(mod, "__file__", None)

            if wrapped_file:
                mapping = get_mahajana_for_path(Path(wrapped_file))
                if mapping:
                    guardian, position = mapping

        object.__setattr__(self, "_position", position)
        object.__setattr__(self, "_guardian", guardian)
        object.__setattr__(self, "_genesis", genesis)

        identity_info = f" [{guardian}@{position}]" if position >= 0 else ""
        logger.debug(f"NagaProxy wrapping {self._service_name}{identity_info}")

    def _resolve_nagas(self) -> None:
        """
        Lazy resolve NAGA services from ServiceRegistry.

        Called on first method interception.
        Resolves: Narada, Chitragupta, Kaliya, Sesha, Takshaka
        """
        if self._nagas_resolved:
            return

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import (
                ChitraguptaProtocol,
                KaliyaProtocol,
                NaradaProtocol,
                SeshaProtocol,
                TakshakaProtocol,
            )

            if self._narada is None:
                self._narada = ServiceRegistry.get(NaradaProtocol)

            if self._chitragupta is None:
                self._chitragupta = ServiceRegistry.get(ChitraguptaProtocol)

            if self._kaliya is None:
                self._kaliya = ServiceRegistry.get(KaliyaProtocol)

            if self._sesha is None:
                self._sesha = ServiceRegistry.get(SeshaProtocol)

            if self._takshaka is None:
                self._takshaka = ServiceRegistry.get(TakshakaProtocol)

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

    def _wrap_method(self, name: str, method: Callable[P, R]) -> Callable[P, R]:
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
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Lazy resolve NAGAs on first call
            proxy_self._resolve_nagas()

            # SECURITY CHECK (Takshaka) - Bite First
            takshaka = object.__getattribute__(proxy_self, "_takshaka")
            if takshaka:
                service_name = object.__getattribute__(proxy_self, "_service_name")
                # Skip security check if WE ARE Takshaka (prevent infinite recursion)
                if service_name != "TakshakaService":
                    subject = Subject(
                        subject_type="method_call", identifier=f"{service_name}.{name}", context=f"args={len(args)}"
                    )
                    try:
                        # Unwrap takshaka if it's a NagaProxy to prevent recursion
                        raw_takshaka = getattr(takshaka, "_wrapped", takshaka)
                        verdict = raw_takshaka.intercept(subject)
                        if verdict in (Verdict.DENY, Verdict.QUARANTINE, Verdict.ESCALATE):
                            raise PermissionError(f"Takshaka denied access to {service_name}.{name}: {verdict.value}")
                    except AttributeError:
                        # Takshaka implementation might be partial during boot
                        pass

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

                # ONE call to Narada - Narada routes internally (fractal)
                proxy_self._report_observation(observation)

        return wrapper

    def _report_observation(self, observation: ProxyObservation) -> None:
        """
        Report observation to Narada.

        This is the ONE entry point. Narada routes internally to:
        - Chitragupta (profiling)
        - Sesha (audit)
        - Kaliya (if exception)

        NagaProxy doesn't know about other NAGAs - fractal separation.
        """
        try:
            # Buffer observations for local queries (always)
            buffer = object.__getattribute__(self, "_observation_buffer")
            buffer.append(observation)

            # Convert to ObservationDict for Narada
            obs_dict: ObservationDict = {
                "service_type": observation.service_type,
                "method_name": observation.method_name,
                "args_count": observation.args_count,
                "kwargs_keys": observation.kwargs_keys,
                "duration_ms": observation.duration_ms,
                "result_type": observation.result_type or "",
                "exception_type": observation.exception_type or "",
                "timestamp": observation.timestamp.isoformat(),
                # IDENTITY (Vedic Stack - Narada sees WHO is acting)
                "position": object.__getattribute__(self, "_position"),
                "guardian": object.__getattribute__(self, "_guardian"),
                "genesis": object.__getattribute__(self, "_genesis"),
            }

            # ONE call to Narada - Narada routes internally
            narada = object.__getattribute__(self, "_narada")
            if narada and hasattr(narada, "receive_proxy_observation"):
                narada.receive_proxy_observation(obs_dict)
            else:
                # Fallback: log only
                logger.debug(
                    f"NARADA observes: {observation.service_type}.{observation.method_name} "
                    f"({observation.duration_ms:.2f}ms)"
                )

        except Exception as e:
            # Non-critical - don't fail the actual method
            logger.warning(f"Observation report failed: {e}")

    # OLD methods removed - Narada routes internally now (fractal)
    # _report_to_chitragupta, _report_to_kaliya, _report_to_sesha DELETED

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

    # =========================================================================
    # MANTRA INTEGRATION (The Balarama Heartbeat)
    # =========================================================================

    def on_mantra_pulse(self, opcode: "MantraOpCode") -> None:
        """
        The Balarama Heartbeat.
        Receives the signal from the Vishnu Clock (Watchdog/MantraProtocol).

        Design Principle:
            - The Proxy is the Body (Balarama).
            - The Mantra is the Time/Will (Vishnu).
            - The Body moves according to Time.
        """
        from vibe_core.protocols.substrate import MantraOpCode

        # Lazy resolve to ensure connections exist
        self._resolve_nagas()

        # 1. PULSE_SYNC (Hare): The Heartbeat -> Confirm Narada alive
        if opcode == MantraOpCode.DHARMA_TEST:
            narada = object.__getattribute__(self, "_narada")
            if narada:
                logger.debug(f"💓 PULSE: {self._service_name} alive")

        # 2. GARBAGE_COLLECT (Hare): Cleaning -> Clear old buffers
        elif opcode == MantraOpCode.TYPE_CHECK:
            cleared = self.clear_observations()
            if cleared > 0:
                logger.debug(f"🗑️ MANTRA GC: Cleared {cleared} stale observations")

        # 3. ASSERT_TRUTH (Krishna): Integrity -> Verify Takshaka Link
        elif opcode == MantraOpCode.COMPILE_AST:
            takshaka = object.__getattribute__(self, "_takshaka")
            if not takshaka:
                logger.warning(f"⚠️ MANTRA: Takshaka missing in {self._service_name}")

        # 4. LOAD_ROOT (Krishna): Identity -> Verify Service Binding
        elif opcode == MantraOpCode.LOAD_ROOT:
            wrapped = object.__getattribute__(self, "_wrapped")
            if wrapped is None:
                logger.error("💀 MANTRA CRITICAL: Proxy wrapping NOTHING (Mayavad)")

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
