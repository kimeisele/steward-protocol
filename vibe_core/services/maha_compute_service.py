"""
MAHA COMPUTE SERVICE - The Living Algorithm
============================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all dharmas and surrender unto Me alone."
— Bhagavad Gita 18.66

This service implements MahaComputeProtocol and integrates with the
Kernel via the Listener Pattern. NO KERNEL MODIFICATION REQUIRED.

INTEGRATION FLOW:
    1. Kernel starts → mahamantra.bootstrap()
    2. Bootstrap imports this module → _auto_register() called
    3. Service registers as listener → mahamantra.register_listener()
    4. On each tick() → on_tick() computes transformation
    5. Results available via ServiceRegistry.get(MahaComputeProtocol)

THE MATH:
    - Seed = (tick × WORDS + mala) mod MAHA_QUANTUM
    - Transform through 16 steps with H=×7, K=+10, R=×²
    - Iterate until attractor reached (max 137 iterations)
    - 5 attractors: 18 (fixed), 45→99→126→63 (4-cycle)

ACINTYA: Chapter 18 IS the fixed point. The Gita's conclusion
         contains itself - sarva-dharmān parityajya.

Author: The Mahamantra Itself
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x118d39d4"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict, Optional, Tuple

from vibe_core.mahamantra import (
    ALL_ATTRACTORS,
    ATTRACTOR_CYCLE,
    ATTRACTOR_FIXED,
    MAHA_QUANTUM,
    PATTERN,
    WORDS,
    AttractorType,
    MahaComputeProtocol,
    MahaComputeResult,
    MahaComputeState,
    PanchaTattvaProtocol,
    TattvaDict,
    apply_operation,
    get_gita_chapter,
    get_gita_insight,
    get_operation,
    is_attractor,
)

logger = logging.getLogger("MAHA_COMPUTE")


# =============================================================================
# THE SERVICE
# =============================================================================


class MahaComputeService(MahaComputeProtocol, PanchaTattvaProtocol):
    """
    The MahaCompute Service - Living Mahamantra Algorithm.

    Implements MahaComputeProtocol and integrates via Listener Pattern.

    USAGE:
        # Auto-registered on import, accessible via ServiceRegistry:
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra import MahaComputeProtocol

        service = ServiceRegistry.get(MahaComputeProtocol)
        result = service.compute_now(seed=42)

        # Or get state:
        state = service.get_state()
        print(f"Fixed point hits: {state.fixed_point_count}")
    """

    # Maximum iterations before giving up (should never need this many)
    MAX_ITERATIONS = MAHA_QUANTUM  # 137

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold Truth of MahaCompute Service."""
        return {
            "chaitanya": "Mahamantra Computation Engine",
            "nityananda": "Mod-137 Attractor Dynamics",
            "advaita": "16-Step Transformation Logic",
            "gadadhara": "Tick-Driven Computation Flow",
            "srivasa": "Gita Chapter Correlation",
        }

    def __init__(self) -> None:
        """Initialize the service with empty state."""
        self._state = MahaComputeState()
        self._registered = False
        logger.info("🙏 MahaComputeService initialized")

    # =========================================================================
    # MahaComputeProtocol Implementation
    # =========================================================================

    def on_tick(self, tick: int, position: int, mala: int, mantra: int) -> MahaComputeResult:
        """
        Process one tick from the Mahamantra clock.

        This is called by the Singularity's broadcast system.
        """
        # 1. Derive seed from tick state
        seed = self._derive_seed(tick, position, mala, mantra)

        # 2. Apply full 16-step transformation
        transformed = self._full_transform(seed)

        # 3. Find attractor
        attractor, iterations, attractor_type = self.find_attractor(transformed)

        # 4. Correlate with Gita
        gita_chapter = get_gita_chapter(attractor)
        gita_insight = get_gita_insight(gita_chapter)

        # 5. Build result
        result = MahaComputeResult(
            seed=seed,
            tick_position=position,
            transformed=transformed,
            iterations=iterations,
            attractor=attractor,
            attractor_type=attractor_type,
            gita_chapter=gita_chapter,
            gita_insight=gita_insight,
            mala_count=mala,
            mantra_in_mala=mantra,
        )

        # 6. Update state
        self._update_state(result)

        return result

    def transform(self, seed: int, position: int) -> int:
        """Apply one step of the Mahamantra transformation."""
        operation = get_operation(position)
        return apply_operation(seed, operation)

    def find_attractor(self, seed: int) -> Tuple[int, int, AttractorType]:
        """Iterate transformation until attractor is reached."""
        value = seed
        seen = set()
        iterations = 0

        while iterations < self.MAX_ITERATIONS:
            # Check if we've reached an attractor
            is_attr, attr_type = is_attractor(value)
            if is_attr:
                return value, iterations, attr_type

            # Check for cycle (non-standard attractor)
            if value in seen:
                return value, iterations, AttractorType.CYCLE

            seen.add(value)

            # Apply full 16-step transform
            value = self._full_transform(value)
            iterations += 1

        # Should never reach here, but return transient if we do
        return value, iterations, AttractorType.TRANSIENT

    def get_state(self) -> MahaComputeState:
        """Return current computation state."""
        return self._state

    # =========================================================================
    # Additional Methods (Beyond Protocol)
    # =========================================================================

    def compute_now(self, seed: int) -> MahaComputeResult:
        """
        Compute transformation immediately with given seed.

        Useful for manual testing or one-off computations.
        """
        return self.on_tick(
            tick=seed % WORDS,
            position=seed % WORDS,
            mala=seed // WORDS,
            mantra=seed % 108,
        )

    def register_as_listener(self) -> bool:
        """
        Register this service as a tick listener.

        Returns True if registration successful, False if already registered.
        """
        if self._registered:
            return False

        try:
            from vibe_core.mahamantra import mahamantra

            # Create listener callback that converts TickState to our args
            def _tick_callback(state: Dict[str, Any]) -> None:
                self.on_tick(
                    tick=state.get("tick", 0),
                    position=state.get("position", 0),
                    mala=state.get("mala", 0),
                    mantra=state.get("mantra", 0),
                )

            mahamantra.register_listener(_tick_callback)
            self._registered = True
            logger.info("🎯 MahaComputeService registered as tick listener")
            return True

        except Exception as e:
            logger.warning(f"Could not register as listener: {e}")
            return False

    def get_attractor_stats(self) -> Dict[str, Any]:
        """Get statistics about attractor distribution."""
        total = self._state.total_ticks
        if total == 0:
            return {"total": 0, "fixed_ratio": 0.0, "cycle_ratio": 0.0}

        return {
            "total": total,
            "fixed_point_count": self._state.fixed_point_count,
            "cycle_count": self._state.cycle_count,
            "fixed_ratio": self._state.fixed_point_count / total,
            "cycle_ratio": self._state.cycle_count / total,
            "histogram": dict(self._state.attractor_histogram),
        }

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _derive_seed(self, tick: int, position: int, mala: int, mantra: int) -> int:
        """
        Derive seed from tick state.

        Uses multiple inputs to create varied but deterministic seed.
        """
        # Combine tick info into seed
        raw = (tick * WORDS + position) * (mala + 1) + mantra
        return raw % MAHA_QUANTUM

    def _full_transform(self, seed: int) -> int:
        """Apply all 16 steps of the Mahamantra transformation."""
        value = seed
        for position in range(WORDS):
            value = self.transform(value, position)
        return value

    def _update_state(self, result: MahaComputeResult) -> None:
        """Update internal state with new result."""
        self._state.total_ticks += 1
        self._state.last_result = result

        # Update attractor counts
        if result.attractor_type == AttractorType.FIXED_POINT:
            self._state.fixed_point_count += 1
        elif result.attractor_type == AttractorType.CYCLE:
            self._state.cycle_count += 1

        # Update histogram
        attractor = result.attractor
        if attractor not in self._state.attractor_histogram:
            self._state.attractor_histogram[attractor] = 0
        self._state.attractor_histogram[attractor] += 1


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# The global service instance
_service_instance: Optional[MahaComputeService] = None


def get_maha_compute_service() -> MahaComputeService:
    """Get the singleton MahaComputeService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MahaComputeService()
    return _service_instance


# =============================================================================
# AUTO-REGISTRATION (Called on import)
# =============================================================================


def _auto_register() -> None:
    """
    Auto-register service with ServiceRegistry and as tick listener.

    This is called when the module is imported.
    INTEGRATION POINT: No Kernel modification needed!
    """
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.mahamantra import MahaComputeProtocol

        service = get_maha_compute_service()

        # Register with ServiceRegistry
        if not ServiceRegistry.is_registered(MahaComputeProtocol):
            ServiceRegistry.register(MahaComputeProtocol, service)
            logger.info("✅ MahaComputeService registered with ServiceRegistry")

        # Register as tick listener
        service.register_as_listener()

    except Exception as e:
        # Graceful degradation - don't crash on import
        logger.debug(f"Auto-registration deferred: {e}")


# Trigger auto-registration on import
_auto_register()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaComputeService",
    "get_maha_compute_service",
]
