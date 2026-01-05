"""
NAGA Base Service - OUROBOROS Self-Monitoring.

"Der Wächter muss sich selbst bewachen."

Every NAGA service inherits from NagaBaseService to get:
- Sesha: Ledger recording (Karma)
- Chitragupta: Performance profiling
- Takshaka: Security validation

The @naga_governed decorator wraps methods for automatic:
- Execution timing → Chitragupta
- Operation logging → Sesha
- Input validation → Takshaka

This is the OUROBOROS pattern: NAGAs eat their own tail.
"""

import functools
import logging
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar

from vibe_core.di import ServiceRegistry

if TYPE_CHECKING:
    from vibe_core.protocols.naga import (
        ChitraguptaProtocol,
        SeshaProtocol,
        TakshakaProtocol,
    )

logger = logging.getLogger("NAGA.BASE")

F = TypeVar("F", bound=Callable[..., Any])


def naga_governed(
    operation: Optional[str] = None,
    log_args: bool = False,
    validate_input: bool = False,
) -> Callable[[F], F]:
    """
    OUROBOROS: Wrap method with NAGA self-monitoring.

    Automatically:
    - Records operation to Sesha ledger (Karma)
    - Profiles execution time via Chitragupta
    - Validates inputs via Takshaka (optional)

    Usage:
        class MyNagaService(NagaBaseService):
            @naga_governed(operation="heal")
            def heal(self, target: str) -> bool:
                ...

    Args:
        operation: Operation name for logging (defaults to method name)
        log_args: Whether to log method arguments
        validate_input: Whether to run Takshaka validation on inputs
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: "NagaBaseService", *args: Any, **kwargs: Any) -> Any:
            op_name = operation or func.__name__
            service_name = getattr(self, "_service_name", self.__class__.__name__)

            # === START PROFILING ===
            start_time = time.time()

            # === TAKSHAKA VALIDATION (optional) ===
            if validate_input and self._takshaka:
                for arg in args:
                    if isinstance(arg, str) and len(arg) > 10:
                        try:
                            result = self._takshaka.scan_toxicity(arg)
                            if result.is_toxic:
                                logger.warning(f"[{service_name}] Takshaka blocked toxic input in {op_name}")
                                # Record violation
                                if self._sesha and hasattr(self._sesha, "_ledger"):
                                    self._sesha._ledger.record_event(
                                        event_type="NAGA_TOXIC_INPUT",
                                        agent_id=service_name.lower(),
                                        details={
                                            "operation": op_name,
                                            "toxicity": result.score,
                                        },
                                    )
                                raise ValueError("Toxic input blocked by Takshaka")
                        except Exception as e:
                            if "Toxic input" in str(e):
                                raise
                            # Takshaka unavailable - continue without validation
                            pass

            # === EXECUTE ===
            error_msg = None
            result = None
            try:
                result = func(self, *args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                # === END PROFILING ===
                duration_ms = (time.time() - start_time) * 1000

                # === CHITRAGUPTA PROFILING ===
                if self._chitragupta:
                    try:
                        self._chitragupta.record_operation(
                            service=service_name,
                            operation=op_name,
                            duration_ms=duration_ms,
                            success=error_msg is None,
                        )
                    except Exception:
                        pass  # Don't fail on profiling errors

                # === SESHA KARMA RECORDING ===
                if self._sesha and hasattr(self._sesha, "_ledger"):
                    try:
                        details = {
                            "operation": op_name,
                            "duration_ms": round(duration_ms, 2),
                            "success": error_msg is None,
                        }
                        if error_msg:
                            details["error"] = error_msg[:200]
                        if log_args and args:
                            details["args_count"] = len(args)

                        self._sesha._ledger.record_event(
                            event_type="NAGA_OPERATION",
                            agent_id=service_name.lower(),
                            details=details,
                        )
                    except Exception:
                        pass  # Don't fail on logging errors

        return wrapper  # type: ignore

    return decorator


class NagaBaseService:
    """
    Base class for NAGA services with self-monitoring.

    OUROBOROS PATTERN: Every NAGA gets access to peer NAGAs for:
    - Sesha: Record operations to ledger (Karma)
    - Chitragupta: Profile performance
    - Takshaka: Validate inputs

    Usage:
        class MyService(NagaBaseService):
            def __init__(self, ledger=None):
                super().__init__(service_name="MyService")
                self._ledger = ledger

            @naga_governed(operation="process")
            def process(self, data: str) -> bool:
                # Automatically profiled and logged
                return True
    """

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
            except Exception:
                pass
        return self._sesha_instance

    @property
    def _chitragupta(self) -> Optional["ChitraguptaProtocol"]:
        """Lazy-load Chitragupta from ServiceRegistry."""
        if self._chitragupta_instance is None:
            try:
                from vibe_core.protocols.naga import ChitraguptaProtocol

                self._chitragupta_instance = ServiceRegistry.get(ChitraguptaProtocol)
            except Exception:
                pass
        return self._chitragupta_instance

    @property
    def _takshaka(self) -> Optional["TakshakaProtocol"]:
        """Lazy-load Takshaka from ServiceRegistry."""
        if self._takshaka_instance is None:
            try:
                from vibe_core.protocols.naga import TakshakaProtocol

                self._takshaka_instance = ServiceRegistry.get(TakshakaProtocol)
            except Exception:
                pass
        return self._takshaka_instance

    def _record_karma(self, event_type: str, details: dict) -> None:
        """
        Record event to Sesha ledger (Karma tracking).

        Convenience method for explicit logging.
        """
        if self._sesha and hasattr(self._sesha, "_ledger"):
            try:
                self._sesha._ledger.record_event(
                    event_type=event_type,
                    agent_id=self._service_name.lower(),
                    details=details,
                )
            except Exception as e:
                logger.debug(f"[{self._service_name}] Karma recording failed: {e}")
