"""
⚡ VAJRA Enforcement - Runtime Wiring Validation
================================================

Provides decorators and validators to enforce wiring at runtime.

PHILOSOPHY:
- Shadow mode (unwired) is PERMISSIVE but LOGGED
- Production should be WIRED - tests catch violations
- Enforcement can be strict or permissive based on context

DHARMA ENFORCEMENT:
- VajraEnforcer uses PhoenixConfig as source of truth
- Detects and corrects drift between runtime state and config
- Logs enforcement actions for audit trail
"""

import functools
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar

from vibe_core.vajra.protocol import is_wirable, is_wired

if TYPE_CHECKING:
    from vibe_core.phoenix.config import PhoenixConfig

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


class VajraEnforcer:
    """
    VAJRA Dharma Enforcer - Runtime Config Integrity.

    Uses PhoenixConfig as the source of truth and enforces it against
    runtime state. Detects drift and corrects it.

    Philosophy:
    - Config is LAW (Dharma)
    - State must obey Config
    - Drift is automatically corrected
    - All corrections are logged for audit trail

    Usage:
        config = PhoenixConfig.from_files()
        enforcer = VajraEnforcer(config)

        # Detect drift
        has_drift = enforcer.detect_drift("manas", runtime_state)

        # Enforce and correct
        corrected = enforcer.gloss_over("manas", runtime_state)
    """

    def __init__(self, phoenix_config: "PhoenixConfig"):
        """
        Initialize VAJRA with PhoenixConfig.

        Args:
            phoenix_config: The Phoenix configuration (source of truth)
        """
        from vibe_core.phoenix.config import PhoenixConfig

        if not isinstance(phoenix_config, PhoenixConfig):
            raise TypeError(f"Expected PhoenixConfig, got {type(phoenix_config)}")

        self.config = phoenix_config
        self.corrections_applied = 0

    def detect_drift(self, section_id: str, runtime_state: Dict[str, Any]) -> bool:
        """
        Detect if runtime state drifts from config.

        Args:
            section_id: Section name (e.g., "manas")
            runtime_state: Current runtime values

        Returns:
            True if drift detected, False otherwise
        """
        section = self.config.get_section(section_id)
        if section is None:
            logger.warning(f"⚡ VAJRA: Section '{section_id}' not found in config")
            return False

        # Check each key in runtime state against config
        for key, runtime_value in runtime_state.items():
            if not hasattr(section, key):
                logger.debug(f"⚡ VAJRA: Config section '{section_id}' has no attribute '{key}'")
                continue

            config_value = getattr(section, key)
            if runtime_value != config_value:
                logger.debug(
                    f"⚡ VAJRA: Drift detected in {section_id}.{key}: state={runtime_value}, config={config_value}"
                )
                return True

        return False

    def gloss_over(self, section_id: str, runtime_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce config as law - correct any drift in runtime state.

        This is VAJRA's primary enforcement method. It returns a corrected
        copy of the runtime state that matches the config exactly.

        Args:
            section_id: Section name (e.g., "manas")
            runtime_state: Current runtime values (will be copied and corrected)

        Returns:
            Corrected state matching config values
        """
        section = self.config.get_section(section_id)
        if section is None:
            logger.warning(f"⚡ VAJRA: Cannot enforce '{section_id}' - section not found")
            return runtime_state.copy()

        # Create corrected copy
        corrected = runtime_state.copy()
        corrections = []

        # Apply config values to corrected state
        for key in runtime_state:
            if not hasattr(section, key):
                continue

            config_value = getattr(section, key)
            current_value = corrected.get(key)

            if current_value != config_value:
                corrected[key] = config_value
                corrections.append(f"{key}: {current_value} → {config_value}")
                self.corrections_applied += 1

        if corrections:
            logger.info(f"⚡ VAJRA: Enforced Dharma on {section_id}. Corrections: {'; '.join(corrections)}")

        return corrected

    def enforce_integrity(self, section_id: str, runtime_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias for gloss_over() - enforce config integrity.

        Args:
            section_id: Section name
            runtime_state: Current runtime values

        Returns:
            Corrected state matching config
        """
        return self.gloss_over(section_id, runtime_state)
