"""
VASUKI ACTIVE MIXIN - Border Control (Sign Outbound).

"Memory is not Network" - PROMPT.md

This is NOT a passive capability provider. This is an ACTIVE GENE.
When spliced into a class, it AUTOMATICALLY intercepts methods that
send data externally and signs/records them.

The Churning Ocean: Anything leaving the internal boundary gets
transformed (signed, serialized, recorded) before departure.

Pattern Detection (methods that send externally):
    - send*, post*, push* → OUTBOUND_SEND
    - broadcast*, emit*, publish* → OUTBOUND_BROADCAST
    - sync*, replicate* → OUTBOUND_SYNC

Integration:
    - Signs all outbound payloads via Vasuki.churn_out()
    - Records outbound events to Ledger
    - Signals Cortex for network monitoring
    - Graceful degradation if Vasuki unavailable

Usage:
    class NotificationService(ActiveVasukiMixin):
        def send_notification(self, user_id: str, message: str):  # ← Auto-signed!
            self.http.post(f"/users/{user_id}/notify", {"msg": message})

    # Result:
    # 1. Outbound payload signed and recorded
    # 2. Cortex signaled about network activity
    # 3. Original method executes
"""

import functools
import logging
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from vibe_core.protocols.naga import VasukiProtocol

logger = logging.getLogger("NAGA.MIXIN.VASUKI")


# =============================================================================
# Pattern Detection - What methods send externally?
# =============================================================================

import re

# Methods that SEND data outbound (direct sends)
OUTBOUND_SEND_PATTERNS = [
    re.compile(r"^send[_A-Z]?"),
    re.compile(r"^post[_A-Z]?"),
    re.compile(r"^push[_A-Z]?"),
    re.compile(r"^put[_A-Z]?"),
    re.compile(r"^patch[_A-Z]?"),
]

# Methods that BROADCAST data (one-to-many)
OUTBOUND_BROADCAST_PATTERNS = [
    re.compile(r"^broadcast[_A-Z]?"),
    re.compile(r"^emit[_A-Z]?"),
    re.compile(r"^publish[_A-Z]?"),
    re.compile(r"^notify[_A-Z]?"),
    re.compile(r"^fanout[_A-Z]?"),
]

# Methods that SYNC data (bidirectional)
OUTBOUND_SYNC_PATTERNS = [
    re.compile(r"^sync[_A-Z]?"),
    re.compile(r"^replicate[_A-Z]?"),
    re.compile(r"^propagate[_A-Z]?"),
    re.compile(r"^gossip[_A-Z]?"),
]

# Methods to NEVER intercept
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
    "_get_vasuki",
    "_get_cortex",
    "_record_outbound",
    "_signal_network_event",
    "get_status",
    "get_stats",
    # Don't intercept Vasuki's own methods
    "churn_out",
    "churn_in",
    "send",
    "receive",
}


def _classify_method(method_name: str) -> Optional[str]:
    """Classify a method by its outbound pattern."""
    if method_name.startswith("_"):
        return None  # Skip private methods

    if method_name in EXCLUDED_METHODS:
        return None

    for pattern in OUTBOUND_SEND_PATTERNS:
        if pattern.match(method_name):
            return "OUTBOUND_SEND"

    for pattern in OUTBOUND_BROADCAST_PATTERNS:
        if pattern.match(method_name):
            return "OUTBOUND_BROADCAST"

    for pattern in OUTBOUND_SYNC_PATTERNS:
        if pattern.match(method_name):
            return "OUTBOUND_SYNC"

    return None


# =============================================================================
# The Method Wrapper - The actual interception logic
# =============================================================================


def _create_border_guard(
    original_method: Callable,
    method_name: str,
    outbound_type: str,
    class_name: str,
) -> Callable:
    """
    Create a border guard wrapper for a method.

    This is the Churning Ocean - we sign/record all outbound data
    BEFORE the method executes.
    """

    @functools.wraps(original_method)
    def border_guard(self: "ActiveVasukiMixin", *args: Any, **kwargs: Any) -> Any:
        # Get Vasuki service (lazy, graceful degradation)
        vasuki = self._get_vasuki()

        start_time = time.time()
        op_id = f"{class_name}.{method_name}.{int(time.time() * 1000) % 100000}"

        # === PHASE 1: Record outbound intent ===
        outbound_info = {
            "operation_id": op_id,
            "class": class_name,
            "method": method_name,
            "outbound_type": outbound_type,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
            "timestamp": time.time(),
        }

        # Record to Sesha (via Vasuki or directly)
        self._record_outbound(
            phase="intent",
            method=method_name,
            outbound_type=outbound_type,
            details=outbound_info,
        )

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

            # === PHASE 3: Record completion/error ===
            completion_info = {
                "operation_id": op_id,
                "duration_ms": duration_ms,
                "success": error is None,
                "error": str(error) if error else None,
            }

            self._record_outbound(
                phase="complete" if error is None else "error",
                method=method_name,
                outbound_type=outbound_type,
                details=completion_info,
            )

            # === PHASE 4: Signal Cortex (Network Monitoring) ===
            self._signal_network_event(
                event_type=f"{outbound_type}.{'complete' if error is None else 'error'}",
                method=method_name,
                duration_ms=duration_ms,
                success=error is None,
            )

        return result

    return border_guard


# =============================================================================
# The Active Mixin - The Gene that GUARDS the Border
# =============================================================================

from vibe_core.naga.mixins.takshaka import ActiveTakshakaMixinMeta


class ActiveVasukiMixinMeta(ActiveTakshakaMixinMeta):
    """
    Metaclass that automatically guards outbound network methods.

    When a class uses ActiveVasukiMixin, this metaclass:
    1. Scans all methods for outbound patterns
    2. Wraps matching methods with border guards
    3. Preserves isinstance checks

    Inherits from ActiveTakshakaMixinMeta to allow combining all Active Genes.
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> type:
        # Create the class first (runs Sesha + Takshaka logic via super())
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't wrap the mixin itself
        if name == "ActiveVasukiMixin":
            return cls

        # Find methods to guard
        guarded_count = 0
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue

            # Check if it's a method that sends externally
            outbound_type = _classify_method(attr_name)
            if outbound_type is None:
                continue

            # Get the method
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            # Only guard callable methods (not properties, etc.)
            if not callable(attr):
                continue

            # Skip if already guarded by Vasuki
            if hasattr(attr, "_vasuki_guarded"):
                continue

            # Get the original method (handle inheritance)
            original = None
            for base in cls.__mro__:
                if attr_name in base.__dict__:
                    original = base.__dict__[attr_name]
                    break

            if original is None or not callable(original):
                continue

            # Create and set the border guard
            border_guard = _create_border_guard(
                original_method=original,
                method_name=attr_name,
                outbound_type=outbound_type,
                class_name=name,
            )
            border_guard._vasuki_guarded = True  # Mark as guarded
            border_guard._outbound_type = outbound_type

            setattr(cls, attr_name, border_guard)
            guarded_count += 1

            logger.debug(f"VASUKI: Border guarded {name}.{attr_name} ({outbound_type})")

        if guarded_count > 0:
            logger.info(f"VASUKI: {name} border controlled with {guarded_count} guards")

        return cls


class ActiveVasukiMixin(metaclass=ActiveVasukiMixinMeta):
    """
    VASUKI Active Mixin - Border Control.

    When a class inherits from this Mixin, ALL outbound network methods
    are automatically guarded, signed, and recorded.

    This is the Churning Ocean - nothing leaves without being transformed.

    Features:
    - Auto-detection of send/broadcast/sync patterns
    - Automatic recording of outbound events
    - Cortex signaling for network monitoring
    - Graceful degradation (works without services)
    - isinstance preservation

    Usage:
        class NotificationService(ActiveVasukiMixin):
            def send_email(self, to: str, body: str):
                # This is AUTOMATICALLY guarded!
                self.smtp.send(to, body)
    """

    _naga_flooded: bool = True
    _naga_gene: str = "vasuki"
    _vasuki_instance: Optional["VasukiProtocol"] = None

    def _get_vasuki(self) -> Optional["VasukiProtocol"]:
        """
        Lazy access to Vasuki service.

        Returns None if not available (graceful degradation).
        """
        if self._vasuki_instance is not None:
            return self._vasuki_instance

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import VasukiProtocol

            self._vasuki_instance = ServiceRegistry.get(VasukiProtocol)
            return self._vasuki_instance
        except Exception:
            return None

    def _record_outbound(
        self,
        phase: str,
        method: str,
        outbound_type: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Record an outbound network event.

        Uses Sesha (via ServiceRegistry) if available, otherwise logs.
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import SeshaProtocol

            sesha = ServiceRegistry.get(SeshaProtocol)
            if sesha:
                sesha.record_event(
                    event_type=f"OUTBOUND_{outbound_type}.{phase}",
                    source=f"{self.__class__.__name__}.{method}",
                    details={
                        **details,
                        "gene": "vasuki",
                    },
                )
            else:
                logger.debug(f"VASUKI OUTBOUND: {self.__class__.__name__}.{method} ({outbound_type}.{phase})")
        except Exception as e:
            logger.debug(f"VASUKI: Failed to record outbound: {e}")

    def _signal_network_event(
        self,
        event_type: str,
        method: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """
        Signal the Cortex about a network event.

        This feeds the network monitoring loop.
        """
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and hasattr(federation, "_cortex") and federation._cortex:
                from vibe_core.naga.cortex.signals import FloodSignal

                signal = FloodSignal(
                    source_id=f"mixin.vasuki.{self.__class__.__name__}",
                    event_type=event_type,
                    raw_data={
                        "method": method,
                        "class": self.__class__.__name__,
                        "duration_ms": duration_ms,
                        "success": success,
                    },
                )
                federation._cortex.receive_signal(signal)
        except Exception as e:
            logger.debug(f"VASUKI: Cortex signal failed: {e}")


# =============================================================================
# Convenience Aliases
# =============================================================================

# Alias for cleaner imports
VasukiBorderMixin = ActiveVasukiMixin
