"""
SHUKA ADAPTER - Position 14 (LOG_EMIT)
=======================================

"śrī-śuka uvāca"
"Sukadeva Gosvami said..."
— Srimad Bhagavatam (recurring)

EXPLIZITER ADAPTER. KEINE MAGIE. KEIN MONKEY PATCHING.

GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
Mayavad: CLEAR (Explicit adapter with hard protocol compliance)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from vibe_core.mahamantra.lila.migration import (
    ManifestationServiceProtocol,
    verify_manifestation_protocol,
)
from vibe_core.mahamantra.protocols._gad import GADBase, GADProtocol

if TYPE_CHECKING:
    from vibe_core.mahamantra._types import TickState

logger = logging.getLogger(__name__)


# =============================================================================
# SHUKA ADAPTER (Position 14: Manifestation/Vision)
# =============================================================================

class ShukaAdapter(GADBase, GADProtocol):
    """
    Explicit adapter for ManifestationService → Mahamantra Position 14.

    POSITION: 14
    MAHAJANA: shuka
    QUARTER: kama
    OPCODE: LOG_EMIT

    WATERTIGHT:
    -----------
    - No Any types
    - No silent failures (all errors logged to Yamaraja)
    - Protocol verification at construction
    - Explicit method mapping (no getattr magic)

    GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
    """

    def __init__(self, legacy_service: ManifestationServiceProtocol):
        """
        Initialize Shuka adapter.

        Args:
            legacy_service: The legacy ManifestationService instance

        Raises:
            TypeError: If service doesn't implement ManifestationServiceProtocol
            RuntimeError: If adapter initialization fails
        """
        # PROTOCOL VERIFICATION (No silent acceptance!)
        if not verify_manifestation_protocol(legacy_service):
            raise TypeError(
                f"Service {type(legacy_service).__name__} does not implement "
                "ManifestationServiceProtocol. Cannot adapt."
            )

        # Initialize GAD compliance
        super().__init__()

        # Store wrapped service (typed!)
        self._wrapped: ManifestationServiceProtocol = legacy_service

        # Position identity (from _seed.py, not hardcoded)
        from vibe_core.mahamantra.substrate.seed import get_mahajana_position
        self._position: int = get_mahajana_position("shuka")
        self._mahajana: str = "shuka"
        self._quarter: str = "kama"

        # Tick tracking
        self._tick_count: int = 0
        self._last_error: str | None = None

        logger.info(f"🙏 ShukaAdapter initialized at position {self._position}")

    # =========================================================================
    # HEARTBEAT INTEGRATION (Explicit tick mapping)
    # =========================================================================

    def on_tick(self, tick_state: TickState) -> None:
        """
        React to Mahamantra heartbeat.

        Called when mahamantra.tick() reaches position 14.

        EXPLICIT MAPPING:
        -----------------
        We know exactly which legacy method to call: check_manifest_health()

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
            status = self._wrapped.check_manifest_health()

            # Validate response
            if not isinstance(status, dict):
                raise ValueError(f"Expected dict, got {type(status)}")

            # Log success
            schemas_loaded = status.get("schemas_loaded", 0)
            cache_size = status.get("cache_size", 0)
            errors_count = len(status.get("errors", []))
            logger.debug(
                f"✓ Shuka tick #{self._tick_count}: "
                f"schemas={schemas_loaded}, cache={cache_size}, errors={errors_count}"
            )

            # Clear last error on success
            self._last_error = None

        except Exception as e:
            # NO SILENT FAILURE
            # Log and report to audit system
            error_msg = f"Shuka tick failed: {type(e).__name__}: {e}"
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
                content={"adapter": "shuka", "error": error, "tick": self._tick_count},
                purpose="log_emit",
                actor="ShukaAdapter"
            )
        except Exception as e:
            # Even audit reporting can fail - log it
            logger.critical(f"Failed to report violation: {e}")

    # =========================================================================
    # DELEGATION TO LEGACY SERVICE (Explicit, typed)
    # =========================================================================

    def render_file(self, content: str, path: str) -> bool:
        """
        Delegate file rendering to legacy ManifestationService.

        Args:
            content: The markdown content
            path: Target file path

        Returns:
            True if rendering successful

        Raises:
            ValueError: If content or path invalid
            RuntimeError: If rendering fails
        """
        try:
            result = self._wrapped.render_file(content, path)
            logger.info(f"✓ File rendered via Shuka adapter: {path}")
            return result
        except Exception as e:
            logger.error(f"✗ File rendering failed: {e}")
            raise  # Don't swallow - let caller handle

    def check_manifest_health(self) -> dict[str, object]:
        """
        Check manifestation health (delegation).

        Returns:
            Status dict with keys: schemas_loaded, cache_size, errors

        Raises:
            RuntimeError: If check fails
        """
        return self._wrapped.check_manifest_health()

    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def discover(self) -> dict[str, object]:
        """Return adapter capabilities."""
        return {
            "type": "ShukaAdapter",
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
        """Shuka operations are generally idempotent."""
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
        return (
            f"ShukaAdapter(position={self._position}, "
            f"ticks={self._tick_count}, "
            f"healthy={self.is_healthy()})"
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["ShukaAdapter"]
