"""
GAD BASE - Lightweight Protocol/ABC for Inheritance (O(1) Load)
================================================================

This module provides ONLY the Protocol and ABC definitions needed
for class inheritance. The full GAD implementation is in _gad.py.

SIKSASTAKAM:
    Effect #1: ceto-darpaṇa-mārjanaṁ → Only load what's needed
    Import time: <5ms (vs 200ms+ for full _gad.py)

USAGE:
    # For class definition (inheritance):
    from vibe_core.mahamantra.protocols._gad_base import GADBase, GADProtocol

    # For full GAD functionality:
    from vibe_core.mahamantra.protocols._gad import GADAudit, MantraHeartbeat, ...
"""

from __future__ import annotations

__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x3b37ae67"

from abc import ABC, abstractmethod
from typing import Dict, List, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.mahamantra.protocols._gad import GADAudit, MantraHeartbeat


@runtime_checkable
class GADProtocol(Protocol):
    """
    The GAD-000 Protocol - Operator Inversion Principle.

    LIGHTWEIGHT VERSION: Just the interface, no imports.
    """

    def discover(self) -> Dict[str, object]:
        """Return machine-readable capability description."""
        ...

    def get_state(self) -> Dict[str, object]:
        """Return current state in structured format."""
        ...

    def is_healthy(self) -> bool:
        """Return health status."""
        ...

    @property
    def is_idempotent(self) -> bool:
        """Return True if operation is idempotent."""
        ...

    def detect_drift(self) -> List[str]:
        """Detect deviations from signed intent."""
        ...

    def test_daya(self) -> bool:
        """Mercy test."""
        ...

    def test_satyam(self) -> bool:
        """Truthfulness test."""
        ...

    def test_tapas(self) -> bool:
        """Austerity test."""
        ...

    def test_saucam(self) -> bool:
        """Cleanliness test."""
        ...

    def chant(self) -> bool:
        """Chant once - the Japa-Loop heartbeat."""
        ...

    def audit(self) -> "GADAudit":
        """Perform GAD-000 audit."""
        ...


class GADBase(ABC):
    """
    Abstract Base Class for GAD-000 compliant components.

    LAZY VERSION: Heartbeat is only initialized on first access.
    """

    _heartbeat: "MantraHeartbeat | None" = None

    def __init__(self) -> None:
        # LAZY: Don't create heartbeat here - defer to first access
        pass

    @property
    def heartbeat(self) -> "MantraHeartbeat":
        """Lazy-load the heartbeat on first access."""
        if self._heartbeat is None:
            from vibe_core.mahamantra.protocols._gad import MantraHeartbeat
            from vibe_core.mahamantra.substrate.prabhupada import prabhupada as acharya

            self._heartbeat = MantraHeartbeat()
            self._heartbeat.jiva_connected = acharya.verify_link(self)
        return self._heartbeat

    def chant(self) -> bool:
        """Chant once - the Japa-Loop heartbeat."""
        return self.heartbeat.chant()

    @abstractmethod
    def discover(self) -> Dict[str, object]:
        """Return machine-readable capability description."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, object]:
        """Return current state."""
        pass

    def is_healthy(self) -> bool:
        """Default health check."""
        from vibe_core.mahamantra.protocols._gad import JapaState
        return self.heartbeat.state != JapaState.DISCONNECTED

    @property
    def is_idempotent(self) -> bool:
        """Override in subclass."""
        return True

    def detect_drift(self) -> List[str]:
        """Override in subclass."""
        return []

    def test_daya(self) -> bool:
        """Override in subclass."""
        return True

    def test_satyam(self) -> bool:
        """Override in subclass."""
        return True

    def test_tapas(self) -> bool:
        """Override in subclass."""
        return True

    def test_saucam(self) -> bool:
        """Override in subclass."""
        return True

    def audit(self) -> "GADAudit":
        """Perform GAD-000 audit with lazy imports."""
        from vibe_core.mahamantra.protocols._gad import GADAudit, CRITERIA_COUNT, DHARMA_COUNT

        # Detect Golden Era (lazy)
        try:
            from vibe_core.mahamantra.protocols._singularity import is_in_golden_period
            in_golden = is_in_golden_period()
        except ImportError:
            in_golden = False

        is_proxied = getattr(self, "is_wrapped", False)
        mercy_active = in_golden and is_proxied

        return GADAudit(
            discoverability=bool(self.discover()),
            observability=bool(self.get_state()),
            parseability=True,
            composability=True,
            idempotency=self.is_idempotent,
            recoverability=len(self.detect_drift()) == 0,
            sovereign_present=self.heartbeat.jiva_connected,
            signature_valid=self.heartbeat.krishna_present and self.heartbeat.jiva_connected,
            mercy_mode=mercy_active,
            daya=self.test_daya(),
            satyam=self.test_satyam(),
            tapas=self.test_tapas(),
            saucam=self.test_saucam(),
        )


__all__ = ["GADProtocol", "GADBase"]
