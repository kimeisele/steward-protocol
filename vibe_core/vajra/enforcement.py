"""
⚡ VAJRA Enforcement - Runtime Wiring Validation
================================================

Provides decorators and validators to enforce wiring at runtime.

PHILOSOPHY:
- Shadow mode (unwired) is PERMISSIVE but LOGGED
- Production should be WIRED - tests catch violations
- Enforcement can be strict or permissive based on context
"""

import functools
import logging
from typing import Callable, TypeVar

from vibe_core.vajra.protocol import is_wirable, is_wired

logger = logging.getLogger("VAJRA")

F = TypeVar("F", bound=Callable)


class WiringError(RuntimeError):
    """
    Raised when a component is used without being wired.

    This error indicates a violation of VAJRA protocol:
    - Component has inject_kernel() but was never called
    - Component is trying to access kernel resources while unwired
    """

    def __init__(self, component_name: str, method_name: str):
        self.component_name = component_name
        self.method_name = method_name
        super().__init__(
            f"⚡ VAJRA VIOLATION: {component_name}.{method_name}() called without kernel injection. "
            f"Call inject_kernel(kernel) first!"
        )


def check_wired(obj: object, strict: bool = False) -> bool:
    """
    Check if an object is properly wired.

    Args:
        obj: Object to check
        strict: If True, raise WiringError when not wired

    Returns:
        True if wired (or not wirable), False if unwired

    Raises:
        WiringError: If strict=True and object is unwired
    """
    if not is_wirable(obj):
        return True  # Non-wirable objects are "wired" by default

    wired = is_wired(obj)

    if not wired:
        name = getattr(obj, "__class__", type(obj)).__name__
        if strict:
            raise WiringError(name, "check_wired")
        logger.warning(f"⚡ VAJRA: {name} operating in SHADOW MODE (no kernel)")

    return wired


def assert_wired(method: F) -> F:
    """
    Decorator that asserts component is wired before method execution.

    In strict mode, raises WiringError.
    In permissive mode, logs warning and continues.

    Usage:
        class MyComponent:
            _vibe_kernel = None

            @assert_wired
            def execute(self):
                return self._vibe_kernel.ledger.get_all_events()

    The decorator checks self._vibe_kernel before calling the method.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not is_wired(self):
            name = self.__class__.__name__
            method_name = method.__name__

            # Check for strict mode flag
            strict = getattr(self, "_vajra_strict", False)

            if strict:
                raise WiringError(name, method_name)
            else:
                logger.warning(f"⚡ VAJRA: {name}.{method_name}() called in SHADOW MODE - results may be limited")

        return method(self, *args, **kwargs)

    return wrapper  # type: ignore


def require_wiring(strict: bool = True) -> Callable[[F], F]:
    """
    Decorator factory for configurable wiring enforcement.

    Args:
        strict: If True, raise error when unwired. If False, just warn.

    Usage:
        @require_wiring(strict=True)
        def critical_operation(self):
            ...

        @require_wiring(strict=False)
        def optional_operation(self):
            ...
    """

    def decorator(method: F) -> F:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not is_wired(self):
                name = self.__class__.__name__
                method_name = method.__name__

                if strict:
                    raise WiringError(name, method_name)
                else:
                    logger.warning(f"⚡ VAJRA: {name}.{method_name}() called in SHADOW MODE")

            return method(self, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


class StrictWiringContext:
    """
    Context manager for strict wiring enforcement.

    In tests, wrap code that should fail on unwired components:

        with StrictWiringContext():
            component.execute()  # Raises if unwired
    """

    _strict_mode: bool = False

    def __enter__(self):
        StrictWiringContext._strict_mode = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        StrictWiringContext._strict_mode = False
        return False

    @classmethod
    def is_strict(cls) -> bool:
        return cls._strict_mode
