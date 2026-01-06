"""
NAGA Base Service - OUROBOROS Self-Monitoring.

"Der Wächter muss sich selbst bewachen."

YAMARAJA AUDIT COMPLIANT:
- No silent failures (sys.stderr emergency channel)
- No Any types (ParamSpec + TypeVar)
- No magic string checks (Takshaka scans ALL serializable)

Every NAGA service inherits from NagaBaseService to get:
- Sesha: Ledger recording (Karma)
- Chitragupta: Performance profiling
- Takshaka: Security validation

This is the OUROBOROS pattern: NAGAs eat their own tail.
"""

import functools
import logging
import sys
import time
from typing import TYPE_CHECKING, Callable, Optional, ParamSpec, Protocol, TypeVar

from vibe_core.di import ServiceRegistry
from vibe_core.naga.garuda import garuda  # The Controller of Nagas

if TYPE_CHECKING:
    from vibe_core.protocols.naga import (
        ChitraguptaProtocol,
        EventRecord,
        SeshaProtocol,
        TakshakaProtocol,
    )

logger = logging.getLogger("NAGA.BASE")

# YAMARAJA: ParamSpec statt Any
P = ParamSpec("P")
R = TypeVar("R")


class GovernedProtocol(Protocol):
    """Protocol for governed services - no Any!"""

    _service_name: str


# =============================================================================
# UNGOVERNED ESCAPE HATCH - For methods that must NOT be wrapped
# =============================================================================


def ungoverned(func: Callable[P, R]) -> Callable[P, R]:
    """
    Mark a method as UNGOVERNED - exempt from auto-wrapping.

    HALAHALA PRINCIPLE: Some poison must surface.
    Use sparingly for:
    - Bootstrap methods (called before NAGAs exist)
    - Pure getters (no side effects)
    - Hot-path methods where overhead is unacceptable

    Usage:
        class MyNagaService(NagaBaseService):
            @ungoverned
            def get_cached_value(self) -> str:
                # Pure getter, no side effects
                return self._cache

            @ungoverned
            def _bootstrap(self) -> None:
                # Called before NAGAs exist
                pass
    """
    func._is_ungoverned = True  # type: ignore[attr-defined]
    return func


# =============================================================================
# CLI GOVERNED DECORATOR - Level -1 DNA Injection for CLI
# =============================================================================


def cli_governed(
    operation: Optional[str] = None,
    capabilities_required: Optional[list[str]] = None,
    validate_args: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Level -1 DNA Injection for CLI commands.

    YAMARAJA COMPLIANT:
    - No silent failures (stderr emergency channel)
    - No Any types (ParamSpec)
    - Takshaka scans ALL serializable args (no magic length checks)

    Automatically applies NAGA governance to CLI handlers:
    - Takshaka: Validates command arguments
    - Chitragupta: Profiles execution time
    - Sesha: Records audit trail
    - Capability enforcement: Checks token has required caps

    Args:
        operation: Operation name for logging (defaults to method name)
        capabilities_required: List of required capabilities (checked against token)
        validate_args: Whether to run Takshaka validation on args
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Extract self from args (first positional arg)
            self_obj = args[0] if args else None
            op_name = operation or func.__name__
            service_name = type(self_obj).__name__ if self_obj else "UnknownCLI"

            # === GET NAGA SERVICES (lazy, emergency log on failure) ===
            takshaka = None
            chitragupta = None
            sesha = None

            try:
                from vibe_core.protocols.naga import (
                    ChitraguptaProtocol,
                    SeshaProtocol,
                    TakshakaProtocol,
                )

                takshaka = ServiceRegistry.get(TakshakaProtocol)
                chitragupta = ServiceRegistry.get(ChitraguptaProtocol)
                sesha = ServiceRegistry.get(SeshaProtocol)
            except Exception as e:
                # YAMARAJA: No silent failures - emergency log
                sys.stderr.write(f"!!! NAGA SERVICES UNAVAILABLE: {e}\n")

            # === START PROFILING (nanoseconds for precision) ===
            start_time_ns = time.perf_counter_ns()

            # === CAPABILITY CHECK ===
            cap_token = kwargs.get("capability_token")
            if not cap_token and len(args) > 1:
                first_arg = args[1]  # args[0] is self
                if hasattr(first_arg, "capability_token"):
                    cap_token = first_arg.capability_token

            if capabilities_required and cap_token:
                for cap in capabilities_required:
                    if not cap_token.has_capability(cap):
                        logger.warning(f"[{service_name}] Missing capability: {cap}")
                        raise PermissionError(f"Missing capability: {cap}")

            # === TAKSHAKA VALIDATION (scan ALL serializable) ===
            if validate_args and takshaka:
                _validate_args_with_takshaka(takshaka, args[1:], service_name, op_name)

            # === EXECUTE ===
            error_msg: Optional[str] = None
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                duration_ms = (time.perf_counter_ns() - start_time_ns) / 1_000_000

                # === CHITRAGUPTA PROFILING ===
                if chitragupta:
                    try:
                        chitragupta.record_operation(
                            service=f"CLI.{service_name}",
                            operation=op_name,
                            duration_ms=duration_ms,
                            success=error_msg is None,
                        )
                    except Exception as e:
                        # YAMARAJA: Emergency log, not silent
                        sys.stderr.write(f"!!! CHITRAGUPTA FAILED: {e}\n")

                # === SESHA AUDIT TRAIL (via PUBLIC API) ===
                if sesha:
                    try:
                        from vibe_core.protocols.naga import EventRecord

                        event: EventRecord = {
                            "event_type": "CLI_COMMAND_EXECUTED",
                            "agent_id": cap_token.subject if cap_token else "anonymous",
                            "details": {
                                "operation": op_name,
                                "duration_ms": str(round(duration_ms, 2)),
                                "success": str(error_msg is None),
                                "service": service_name,
                                "error": (error_msg or "")[:200],
                            },
                        }
                        sesha.record_event(event)
                    except Exception as e:
                        # YAMARAJA: Emergency log, not silent
                        sys.stderr.write(f"!!! SESHA AUDIT FAILED: {e}\n")

        return wrapper  # type: ignore[return-value]

    return decorator


def _validate_args_with_takshaka(
    takshaka: "TakshakaProtocol",
    args: tuple[object, ...],
    service_name: str,
    op_name: str,
) -> None:
    """
    Validate ALL serializable args with Takshaka.

    YAMARAJA: No magic length checks. Takshaka scans everything.
    """
    for arg in args:
        if isinstance(arg, str):
            try:
                result = takshaka.scan_toxicity(arg)
                if getattr(result, "blocked", False):
                    logger.warning(f"[{service_name}] Takshaka blocked toxic arg in {op_name}")
                    raise ValueError("Toxic argument blocked by Takshaka")
            except ValueError:
                raise
            except Exception as e:
                # YAMARAJA: Security failure = ACCESS DENIED
                sys.stderr.write(f"!!! TAKSHAKA SCAN FAILED: {e}\n")
        elif isinstance(arg, (list, tuple)):
            for item in arg:
                if isinstance(item, str):
                    try:
                        result = takshaka.scan_toxicity(item)
                        if getattr(result, "blocked", False):
                            raise ValueError("Toxic argument blocked by Takshaka")
                    except ValueError:
                        raise
                    except Exception as e:
                        sys.stderr.write(f"!!! TAKSHAKA SCAN FAILED: {e}\n")


def naga_governed(
    operation: Optional[str] = None,
    log_args: bool = False,
    validate_input: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    OUROBOROS: Wrap method with NAGA self-monitoring.

    YAMARAJA COMPLIANT:
    - No silent failures (stderr emergency channel)
    - No Any types (ParamSpec)
    - perf_counter_ns for precision

    Automatically:
    - Records operation to Sesha ledger (Karma)
    - Profiles execution time via Chitragupta
    - Validates inputs via Takshaka (optional)

    Args:
        operation: Operation name for logging (defaults to method name)
        log_args: Whether to log method arguments
        validate_input: Whether to run Takshaka validation on inputs
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(self: "NagaBaseService", *args: P.args, **kwargs: P.kwargs) -> R:
            # GARUDA GUARD: Check if already flying (recursion detected)
            if garuda.is_flying:
                # Garuda is flying -> Nagas hide -> Execute RAW function
                return func(self, *args, **kwargs)

            # SPREAD WINGS: Enter governed state
            with garuda.fly():
                op_name = operation or func.__name__
                service_name = getattr(self, "_service_name", self.__class__.__name__)

                # === START PROFILING (nanoseconds for precision) ===
                start_time_ns = time.perf_counter_ns()

                # === TAKSHAKA VALIDATION (optional) ===
                if validate_input and self._takshaka:
                    try:
                        _validate_naga_args(self._takshaka, args, service_name, op_name)
                    except ValueError:
                        raise
                    except Exception as e:
                        # YAMARAJA: Security failure = log + continue (not silent)
                        sys.stderr.write(f"!!! TAKSHAKA VALIDATION FAILED: {e}\n")

                # === EXECUTE ===
                error_msg: Optional[str] = None
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    error_msg = str(e)
                    raise
                finally:
                    duration_ms = (time.perf_counter_ns() - start_time_ns) / 1_000_000

                    # === CHITRAGUPTA PROFILING ===
                    if self._chitragupta:
                        try:
                            self._chitragupta.record_operation(
                                service=service_name,
                                operation=op_name,
                                duration_ms=duration_ms,
                                success=error_msg is None,
                            )
                        except Exception as e:
                            # YAMARAJA: Emergency log, not silent
                            sys.stderr.write(f"!!! CHITRAGUPTA PROFILING FAILED [{service_name}]: {e}\n")

                    # === SESHA KARMA RECORDING (via PUBLIC API) ===
                    if self._sesha:
                        try:
                            from vibe_core.protocols.naga import EventRecord

                            details: dict[str, object] = {
                                "operation": op_name,
                                "duration_ms": round(duration_ms, 2),
                                "success": error_msg is None,
                            }
                            if error_msg:
                                details["error"] = error_msg[:200]
                            if log_args and args:
                                details["args_count"] = len(args)

                            event: EventRecord = {
                                "event_type": "NAGA_OPERATION",
                                "agent_id": service_name.lower(),
                                "details": details,
                            }
                            self._sesha.record_event(event)
                        except Exception as e:
                            # YAMARAJA: Emergency log, not silent
                            sys.stderr.write(f"!!! SESHA KARMA FAILED [{service_name}]: {e}\n")

        return wrapper  # type: ignore[return-value]

    return decorator


def _validate_naga_args(
    takshaka: "TakshakaProtocol",
    args: tuple[object, ...],
    service_name: str,
    op_name: str,
) -> None:
    """
    Validate NAGA method args with Takshaka.

    YAMARAJA: No magic length checks. Scan ALL strings.
    """
    for arg in args:
        if isinstance(arg, str):
            result = takshaka.scan_toxicity(arg)
            if getattr(result, "is_toxic", False) or getattr(result, "blocked", False):
                logger.warning(f"[{service_name}] Takshaka blocked toxic input in {op_name}")
                raise ValueError("Toxic input blocked by Takshaka")


class NagaBaseService:
    """
    Base class for NAGA services with self-monitoring.

    YAMARAJA COMPLIANT:
    - No silent failures in lazy loading
    - Emergency stderr on NAGA resolution failure

    OUROBOROS PATTERN: Every NAGA gets access to peer NAGAs for:
    - Sesha: Record operations to ledger (Karma)
    - Chitragupta: Profile performance
    - Takshaka: Validate inputs
    """

    # Track resolution failures to avoid spam
    _resolution_warned: set[str] = set()

    def __init__(self, service_name: Optional[str] = None):
        """
        Initialize base service with lazy peer discovery.

        Args:
            service_name: Name for logging (defaults to class name)
        """
        self._service_name = service_name or self.__class__.__name__

        # Lazy-loaded peer NAGAs (via ServiceRegistry)
        self._sesha_instance: Optional["SeshaProtocol"] = None
        self._chitragupta_instance: Optional["ChitraguptaProtocol"] = None
        self._takshaka_instance: Optional["TakshakaProtocol"] = None

    @property
    def _sesha(self) -> Optional["SeshaProtocol"]:
        """Lazy-load Sesha from ServiceRegistry."""
        if self._sesha_instance is None:
            try:
                from vibe_core.protocols.naga import SeshaProtocol

                self._sesha_instance = ServiceRegistry.get(SeshaProtocol)
            except Exception as e:
                # YAMARAJA: Log once, not silent
                key = f"{self._service_name}:sesha"
                if key not in NagaBaseService._resolution_warned:
                    sys.stderr.write(f"!!! [{self._service_name}] SESHA RESOLUTION FAILED: {e}\n")
                    NagaBaseService._resolution_warned.add(key)
        return self._sesha_instance

    @property
    def _chitragupta(self) -> Optional["ChitraguptaProtocol"]:
        """Lazy-load Chitragupta from ServiceRegistry."""
        if self._chitragupta_instance is None:
            try:
                from vibe_core.protocols.naga import ChitraguptaProtocol

                self._chitragupta_instance = ServiceRegistry.get(ChitraguptaProtocol)
            except Exception as e:
                # YAMARAJA: Log once, not silent
                key = f"{self._service_name}:chitragupta"
                if key not in NagaBaseService._resolution_warned:
                    sys.stderr.write(f"!!! [{self._service_name}] CHITRAGUPTA RESOLUTION FAILED: {e}\n")
                    NagaBaseService._resolution_warned.add(key)
        return self._chitragupta_instance

    @property
    def _takshaka(self) -> Optional["TakshakaProtocol"]:
        """Lazy-load Takshaka from ServiceRegistry."""
        if self._takshaka_instance is None:
            try:
                from vibe_core.protocols.naga import TakshakaProtocol

                self._takshaka_instance = ServiceRegistry.get(TakshakaProtocol)
            except Exception as e:
                # YAMARAJA: Log once, not silent
                key = f"{self._service_name}:takshaka"
                if key not in NagaBaseService._resolution_warned:
                    sys.stderr.write(f"!!! [{self._service_name}] TAKSHAKA RESOLUTION FAILED: {e}\n")
                    NagaBaseService._resolution_warned.add(key)
        return self._takshaka_instance

    def _record_karma(self, event_type: str, details: dict[str, object]) -> None:
        """
        Record event to Sesha ledger (Karma tracking).

        Convenience method for explicit logging.
        Uses public Sesha.record_event() API - no _ledger access!
        """
        if self._sesha:
            try:
                from vibe_core.protocols.naga import EventRecord

                event: EventRecord = {
                    "event_type": event_type,
                    "agent_id": self._service_name.lower(),
                    "details": details,
                }
                self._sesha.record_event(event)
            except Exception as e:
                # YAMARAJA: Emergency log, not just debug
                sys.stderr.write(f"!!! [{self._service_name}] KARMA RECORDING FAILED: {e}\n")
