"""Bridge from shared Venu orchestration into research runtime ticks."""

from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Deque, Optional, Tuple

from vibe_core.di import ServiceRegistry
from vibe_core.mahamantra.protocols._venu import DIWEvent, DIWSubscriberProtocol, VenuOrchestratorProtocol

from .contracts import RuntimeTick


class VenuTickBridge(DIWSubscriberProtocol):
    """Consumes DIW events and exposes typed runtime ticks.

    IMPORTANT: this class does not create a new orchestrator. It attaches to the
    shared orchestrator registered by VenuService.
    """

    __slots__ = ("_events", "_lock", "_attached_to", "_name")

    def __init__(self, max_events: int = 64, subscriber_name: str = "language_runtime_bridge") -> None:
        if max_events < 1:
            raise ValueError("max_events must be >= 1")
        self._events: Deque[RuntimeTick] = deque(maxlen=max_events)
        self._lock = Lock()
        self._attached_to: Optional[VenuOrchestratorProtocol] = None
        self._name = subscriber_name

    @property
    def subscriber_name(self) -> str:
        return self._name

    def on_diw(self, event: DIWEvent) -> None:
        tick = RuntimeTick(
            tick=event["tick"],
            position=event["position"],
            phase=event["phase"],
            mode=event["mode"],
            diw=event["diw"],
            venu=event["venu"],
            vamsi=event["vamsi"],
            murali=event["murali"],
        )
        with self._lock:
            self._events.append(tick)

    def attach(self, orchestrator: Optional[VenuOrchestratorProtocol] = None) -> VenuOrchestratorProtocol:
        """Attach to an existing orchestrator (explicit or DI registry)."""
        resolved = orchestrator or ServiceRegistry.get(VenuOrchestratorProtocol)
        if resolved is None:
            raise RuntimeError("VenuOrchestratorProtocol is not registered")

        if self._attached_to is resolved:
            return resolved

        if self._attached_to is not None:
            self.detach()

        resolved.subscribe(self)
        self._attached_to = resolved
        return resolved

    def detach(self) -> None:
        """Detach from currently attached orchestrator."""
        if self._attached_to is None:
            return
        self._attached_to.unsubscribe(self)
        self._attached_to = None

    def latest(self) -> Optional[RuntimeTick]:
        """Get the latest tick snapshot, if any."""
        with self._lock:
            if not self._events:
                return None
            return self._events[-1]

    def drain(self) -> Tuple[RuntimeTick, ...]:
        """Drain all buffered ticks and clear buffer."""
        with self._lock:
            data = tuple(self._events)
            self._events.clear()
        return data
