"""
SESHA ACTIVE MIXIN - The Scribe (Auto-Ledger).

"Kein Bit fällt ins Nichts" - PROMPT.md

This is NOT a passive capability provider. This is an ACTIVE GENE.
When spliced into a class, it AUTOMATICALLY intercepts state-mutating
methods and records them to the Ledger.

The Ashvamedha Horse: Wherever this Mixin goes, it claims territory
for NAGA sovereignty. The host class doesn't need to know.

Pattern Detection:
    - save*, write*, store*, persist* → STATE_MUTATION
    - update*, modify*, set_* → STATE_MUTATION
    - delete*, remove*, clear* → STATE_DELETION
    - create*, add*, insert* → STATE_CREATION

Integration:
    - Records to Sesha (Ledger) before/after execution
    - Signals to Cortex for Ouroboros loop
    - Graceful degradation if services unavailable

Usage:
    class UserService(ActiveSeshaMixin):
        def save_user(self, user):  # ← Auto-intercepted!
            self.db.save(user)

    # Result:
    # 1. Ledger: STATE_MUTATION.save_user.start
    # 2. Original method executes
    # 3. Ledger: STATE_MUTATION.save_user.complete
    # 4. Cortex: StateChangeSignal emitted
"""

import functools
import logging
import re
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.protocols.naga import SeshaProtocol

logger = logging.getLogger("NAGA.MIXIN.SESHA")

# =============================================================================
# Pattern Detection - What methods trigger auto-recording?
# =============================================================================

# Patterns that indicate state mutation (compiled for performance)
STATE_MUTATION_PATTERNS = [
    re.compile(r"^save[_A-Z]?"),
    re.compile(r"^write[_A-Z]?"),
    re.compile(r"^store[_A-Z]?"),
    re.compile(r"^persist[_A-Z]?"),
    re.compile(r"^update[_A-Z]?"),
    re.compile(r"^modify[_A-Z]?"),
    re.compile(r"^set_[a-z]"),
]

STATE_DELETION_PATTERNS = [
    re.compile(r"^delete[_A-Z]?"),
    re.compile(r"^remove[_A-Z]?"),
    re.compile(r"^clear[_A-Z]?"),
    re.compile(r"^drop[_A-Z]?"),
    re.compile(r"^destroy[_A-Z]?"),
]

STATE_CREATION_PATTERNS = [
    re.compile(r"^create[_A-Z]?"),
    re.compile(r"^add[_A-Z]?"),
    re.compile(r"^insert[_A-Z]?"),
    re.compile(r"^new[_A-Z]?"),
    re.compile(r"^register[_A-Z]?"),
]

# Methods to NEVER intercept (avoid infinite loops)
EXCLUDED_METHODS: Set[str] = {
    "__init__",
    "__new__",
    "__del__",
    "__repr__",
    "__str__",
    "__hash__",
    "__eq__",
    "__ne__",
    "__getattr__",
    "__setattr__",
    "__getattribute__",
    "_get_sesha",
    "_get_cortex",
    "_record_to_ledger",
    "_signal_cortex",
    "_is_interceptable",
    "get_status",
    "get_stats",
}


def _classify_method(method_name: str) -> Optional[str]:
    """Classify a method by its state-change pattern."""
    if method_name.startswith("_"):
        return None  # Skip private methods

    if method_name in EXCLUDED_METHODS:
        return None

    for pattern in STATE_MUTATION_PATTERNS:
        if pattern.match(method_name):
            return "STATE_MUTATION"

    for pattern in STATE_DELETION_PATTERNS:
        if pattern.match(method_name):
            return "STATE_DELETION"

    for pattern in STATE_CREATION_PATTERNS:
        if pattern.match(method_name):
            return "STATE_CREATION"

    return None


# =============================================================================
# The Method Wrapper - The actual interception logic
# =============================================================================


def _create_interceptor(
    original_method: Callable,
    method_name: str,
    event_type: str,
    class_name: str,
) -> Callable:
    """
    Create an interceptor wrapper for a method.

    This is where the magic happens - we wrap the original method
    with Ledger recording and Cortex signaling.
    """

    @functools.wraps(original_method)
    def interceptor(self: "ActiveSeshaMixin", *args: Any, **kwargs: Any) -> Any:
        # Get services (lazy, graceful degradation)
        sesha = self._get_sesha()

        # Generate unique operation ID
        op_id = f"{class_name}.{method_name}.{int(time.time() * 1000) % 100000}"
        start_time = time.time()

        # === PHASE 1: Record START to Ledger ===
        if sesha:
            try:
                sesha.record_event(
                    event_type=f"{event_type}.start",
                    source=class_name,
                    details={
                        "operation_id": op_id,
                        "method": method_name,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    },
                )
            except Exception as e:
                logger.debug(f"SESHA: Failed to record start: {e}")

        # === PHASE 2: Execute Original Method ===
        error: Optional[Exception] = None
        result: Any = None

        try:
            result = original_method(self, *args, **kwargs)
        except Exception as e:
            error = e
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            # === PHASE 3: Record COMPLETE/ERROR to Ledger ===
            if sesha:
                try:
                    if error:
                        sesha.record_event(
                            event_type=f"{event_type}.error",
                            source=class_name,
                            details={
                                "operation_id": op_id,
                                "method": method_name,
                                "error": str(error),
                                "error_type": type(error).__name__,
                                "duration_ms": duration_ms,
                            },
                        )
                    else:
                        sesha.record_event(
                            event_type=f"{event_type}.complete",
                            source=class_name,
                            details={
                                "operation_id": op_id,
                                "method": method_name,
                                "duration_ms": duration_ms,
                                "has_result": result is not None,
                            },
                        )
                except Exception as e:
                    logger.debug(f"SESHA: Failed to record complete: {e}")

            # === PHASE 4: Signal Cortex (Ouroboros Loop) ===
            self._signal_cortex(
                event_type=event_type,
                method=method_name,
                duration_ms=duration_ms,
                success=error is None,
            )

        return result

    return interceptor


# =============================================================================
# The Active Mixin - The Gene that LIVES
# =============================================================================

from vibe_core.naga.mixins.meta import NagaActiveMixinMeta


class ActiveSeshaMixinMeta(NagaActiveMixinMeta):
    """
    Metaclass that automatically wraps state-mutating methods.

    When a class uses ActiveSeshaMixin, this metaclass:
    1. Scans all methods for state-mutation patterns
    2. Wraps matching methods with interceptors
    3. Preserves isinstance checks

    Inherits from NagaActiveMixinMeta to allow combining with other Active Genes.
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> type:
        # Create the class first
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't wrap the mixin itself
        if name == "ActiveSeshaMixin":
            return cls

        # Find methods to wrap
        wrapped_count = 0
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue

            # Check if it's a method that should be intercepted
            event_type = _classify_method(attr_name)
            if event_type is None:
                continue

            # Get the method
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            # Only wrap callable methods (not properties, etc.)
            if not callable(attr):
                continue

            # Skip if already wrapped
            if hasattr(attr, "_sesha_wrapped"):
                continue

            # Get the original method (handle inheritance)
            original = None
            for base in cls.__mro__:
                if attr_name in base.__dict__:
                    original = base.__dict__[attr_name]
                    break

            if original is None or not callable(original):
                continue

            # Create and set the interceptor
            interceptor = _create_interceptor(
                original_method=original,
                method_name=attr_name,
                event_type=event_type,
                class_name=name,
            )
            interceptor._sesha_wrapped = True  # Mark as wrapped

            setattr(cls, attr_name, interceptor)
            wrapped_count += 1

            logger.debug(f"SESHA: Wrapped {name}.{attr_name} ({event_type})")

        if wrapped_count > 0:
            logger.info(f"SESHA: {name} flooded with {wrapped_count} interceptors")

        return cls


class ActiveSeshaMixin(metaclass=ActiveSeshaMixinMeta):
    """
    SESHA Active Mixin - The Scribe.

    When a class inherits from this Mixin, ALL state-mutating methods
    are automatically intercepted and recorded to the Ledger.

    This is the Ashvamedha Horse - wherever it goes, it claims territory.

    Features:
    - Auto-detection of save/update/delete/create patterns
    - Automatic Ledger recording (before + after)
    - Cortex signaling for Ouroboros loop
    - Graceful degradation (works without services)
    - isinstance preservation

    Usage:
        class UserService(ActiveSeshaMixin):
            def save_user(self, user):
                # This is AUTOMATICALLY recorded!
                self.db.save(user)
    """

    _naga_flooded: bool = True
    _naga_gene: str = "sesha"
    _sesha_instance: Optional["SeshaProtocol"] = None

    def _get_sesha(self) -> Optional["SeshaProtocol"]:
        """
        Lazy access to Sesha service.

        Returns None if not available (graceful degradation).
        """
        if self._sesha_instance is not None:
            return self._sesha_instance

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            self._sesha_instance = ServiceRegistry.get(SeshaProtocol)
            return self._sesha_instance
        except Exception:
            return None

    def _signal_cortex(
        self,
        event_type: str,
        method: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """
        Signal the Cortex about a state change.

        This completes the Ouroboros loop:
        Action → Ledger → Cortex → Analysis → Reaction
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and hasattr(federation, "_cortex") and federation._cortex:
                # Create a signal for the Cortex
                from vibe_core.naga.cortex.signals import StateChangeSignal

                signal = StateChangeSignal(
                    source=self.__class__.__name__,
                    event_type=event_type,
                    method=method,
                    duration_ms=duration_ms,
                    success=success,
                )
                federation._cortex.receive_signal(signal)
        except Exception as e:
            # Graceful degradation - don't break the app
            logger.debug(f"SESHA: Cortex signal failed: {e}")


# =============================================================================
# Convenience - Direct import of the Active Mixin
# =============================================================================

# Alias for cleaner imports
SeshaScribeMixin = ActiveSeshaMixin
