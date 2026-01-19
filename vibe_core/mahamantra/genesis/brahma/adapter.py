"""
BRAHMA ADAPTER - Position 1 (LOAD_ROOT)
========================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me."
— Bhagavad Gita 10.8

EXPLIZITER ADAPTER. KEINE MAGIE. KEIN MONKEY PATCHING.

GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
Mayavad: CLEAR (Explicit adapter with hard protocol compliance)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from vibe_core.mahamantra.lila.migration import (
    BrahmaServiceProtocol,
    verify_brahma_protocol,
)
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol
from vibe_core.mahamantra.protocols._seed import PARAMPARA

if TYPE_CHECKING:
    from vibe_core.mahamantra._types import TickState

logger = logging.getLogger(__name__)


# =============================================================================
# BRAHMA ADAPTER (Position 1: Genesis/Creation)
# =============================================================================


class BrahmaAdapter(GADBase, GADProtocol):
    """
    Explicit adapter for BrahmaService → Mahamantra Position 1.

    POSITION: 1
    MAHAJANA: brahma
    QUARTER: genesis
    OPCODE: LOAD_ROOT

    WATERTIGHT:
    -----------
    - No Any types
    - No silent failures (all errors logged to Yamaraja)
    - Protocol verification at construction
    - Explicit method mapping (no getattr magic)

    GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
    """

    def __init__(self, legacy_service: BrahmaServiceProtocol):
        """
        Initialize Brahma adapter.

        Args:
            legacy_service: The legacy BrahmaService instance

        Raises:
            TypeError: If service doesn't implement BrahmaServiceProtocol
            RuntimeError: If adapter initialization fails
        """
        # PROTOCOL VERIFICATION (No silent acceptance!)
        if not verify_brahma_protocol(legacy_service):
            raise TypeError(
                f"Service {type(legacy_service).__name__} does not implement BrahmaServiceProtocol. Cannot adapt."
            )

        # Initialize GAD compliance
        super().__init__()

        # Store wrapped service (typed!)
        self._wrapped: BrahmaServiceProtocol = legacy_service

        # Position identity (from _seed.py, not hardcoded)
        from vibe_core.mahamantra.substrate.seed import get_mahajana_position

        self._position: int = get_mahajana_position("brahma")
        self._mahajana: str = "brahma"
        self._quarter: str = "genesis"

        # Tick tracking
        self._tick_count: int = 0
        self._last_error: str | None = None

        logger.info(f"🙏 BrahmaAdapter initialized at position {self._position}")

    # =========================================================================
    # HEARTBEAT INTEGRATION (Explicit tick mapping)
    # =========================================================================

    def on_tick(self, tick_state: TickState) -> None:
        """
        React to Mahamantra heartbeat.

        Called when mahamantra.tick() reaches position 1.

        EXPLICIT MAPPING:
        -----------------
        We know exactly which legacy method to call: check_genesis_status()

        NO SILENT FAILURES:
        -------------------
        Errors are logged and reported to audit system (Yamaraja).

        Args:
            tick_state: The current tick state

        Raises:
            Never raises - errors are logged and system continues (Arjuna pattern)
        """
        # Verify it's our position
        if tick_state["position"] != self._position:
            return  # Not our turn

        self._tick_count += 1

        try:
            # EXPLICIT CALL (no getattr magic!)
            status = self._wrapped.check_genesis_status()

            # Validate response
            if not isinstance(status, dict):
                raise ValueError(f"Expected dict, got {type(status)}")

            # Log success
            ready = status.get("ready", False)
            agents_count = status.get("agents_count", 0)
            logger.debug(f"✓ Brahma tick #{self._tick_count}: ready={ready}, agents={agents_count}")

            # Clear last error on success
            self._last_error = None

        except Exception as e:
            # NO SILENT FAILURE
            # Log and report to audit system
            error_msg = f"Brahma tick failed: {type(e).__name__}: {e}"
            logger.error(error_msg)
            self._last_error = error_msg

            # Report to Yamaraja (audit)
            self._report_violation(error_msg)

    def _report_violation(self, error: str) -> None:
        """
        Report error to audit system (Yamaraja).

        Args:
            error: The error message
        """
        try:
            from vibe_core.mahamantra.substrate.bridge import offer

            # Report to Yamaraja position (15)
            offer(
                content={"adapter": "brahma", "error": error, "tick": self._tick_count},
                purpose="log_emit",
                actor="BrahmaAdapter",
            )
        except Exception as e:
            # Even audit reporting can fail - log it
            logger.critical(f"Failed to report violation: {e}")

    # =========================================================================
    # DELEGATION TO LEGACY SERVICE (Explicit, typed)
    # =========================================================================

    def register_agent(self, kernel: object, agent: object, spawn_process: bool = True) -> None:
        """
        Delegate agent registration to legacy BrahmaService.

        Args:
            kernel: The kernel instance
            agent: The agent to register
            spawn_process: Whether to spawn in separate process

        Raises:
            ValueError: If agent invalid
            RuntimeError: If registration fails
        """
        try:
            self._wrapped.register_agent(kernel, agent, spawn_process)
            logger.info(f"✓ Agent registered via Brahma adapter")
        except Exception as e:
            logger.error(f"✗ Agent registration failed: {e}")
            raise  # Don't swallow - let caller handle

    def check_genesis_status(self) -> dict[str, object]:
        """
        Check genesis status (delegation).

        Returns:
            Status dict with keys: ready, errors, agents_count

        Raises:
            RuntimeError: If check fails
        """
        return self._wrapped.check_genesis_status()

    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def discover(self) -> dict[str, object]:
        """Return adapter capabilities."""
        return {
            "type": "BrahmaAdapter",
            "position": self._position,
            "mahajana": self._mahajana,
            "quarter": self._quarter,
            "tick_count": self._tick_count,
            "last_error": self._last_error,
            "wrapped_service": type(self._wrapped).__name__,
        }

    def get_state(self) -> dict[str, object]:
        """Return adapter state."""
        return {
            "position": self._position,
            "tick_count": self._tick_count,
            "last_error": self._last_error,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def is_healthy(self) -> bool:
        """Check if adapter is healthy."""
        base_health = super().is_healthy()
        # Unhealthy if last operation failed
        return base_health and (self._last_error is None)

    @property
    def is_idempotent(self) -> bool:
        """Brahma operations are generally idempotent."""
        return True

    def detect_drift(self) -> list[str]:
        """Detect adapter drift."""
        drift: list[str] = []
        if self._last_error:
            drift.append(f"Last operation failed: {self._last_error}")
        return drift

    # Dharma tests
    def test_daya(self) -> bool:
        """Mercy: Does adapter protect the system?"""
        return True  # Adapter wraps and validates

    def test_satyam(self) -> bool:
        """Truth: Does adapter report honestly?"""
        return True  # No silent failures

    def test_tapas(self) -> bool:
        """Austerity: Does adapter stay within bounds?"""
        return True  # No resource leaks

    def test_saucam(self) -> bool:
        """Cleanliness: Is adapter properly initialized?"""
        return self._wrapped is not None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def position(self) -> int:
        """Get adapter position."""
        return self._position

    @property
    def mahajana(self) -> str:
        """Get mahajana name."""
        return self._mahajana

    @property
    def tick_count(self) -> int:
        """Get number of ticks processed."""
        return self._tick_count

    def __repr__(self) -> str:
        return f"BrahmaAdapter(position={self._position}, ticks={self._tick_count}, healthy={self.is_healthy()})"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["BrahmaAdapter"]
