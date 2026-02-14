from __future__ import annotations

from typing import NamedTuple, cast

from vibe_core.mahamantra.protocols._venu import DIWEvent
from vibe_core.mahamantra.research.language_runtime.venu_bridge import VenuTickBridge


class FakeOrchestrator:
    def __init__(self) -> None:
        self._subs = []

    @property
    def tick(self) -> int:
        return 0

    @property
    def mode(self) -> int:
        return 0

    @property
    def subscriber_count(self) -> int:
        return len(self._subs)

    def step(self) -> int:
        return 0

    def subscribe(self, subscriber) -> None:
        self._subs.append(subscriber)

    def unsubscribe(self, subscriber) -> None:
        try:
            self._subs.remove(subscriber)
        except ValueError:
            pass

    def set_mode(self, mode: int) -> None:
        _ = mode

    def reset(self) -> None:
        return None


def _event() -> DIWEvent:
    return cast(
        DIWEvent,
        {
            "diw": 123,
            "tick": 7,
            "position": 3,
            "phase": 1,
            "venu": 11,
            "vamsi": 22,
            "murali": 1,
            "mode": 0,
        },
    )


def test_attach_detach_uses_shared_orchestrator_contract() -> None:
    bridge = VenuTickBridge(max_events=4)
    orch = FakeOrchestrator()

    bridge.attach(orch)
    assert orch.subscriber_count == 1

    bridge.detach()
    assert orch.subscriber_count == 0


def test_latest_and_drain_return_typed_ticks() -> None:
    bridge = VenuTickBridge(max_events=4)

    bridge.on_diw(_event())
    latest = bridge.latest()
    assert latest is not None
    assert latest.tick == 7
    assert latest.position == 3

    drained = bridge.drain()
    assert len(drained) == 1
    assert drained[0].diw == 123
    assert bridge.latest() is None
