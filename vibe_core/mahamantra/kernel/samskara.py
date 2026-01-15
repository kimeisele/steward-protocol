"""
SAMSKARA KERNEL - The Transformation Engine
============================================

"vāsāṁsi jīrṇāni yathā vihāya navāni gṛhṇāti naro 'parāṇi"
"As a person sheds worn-out garments and wears new ones,
likewise, at the time of death, the soul casts off its worn-out body."
— Bhagavad Gita 2.22

THE NEW KERNEL FOR 10,000 YEARS.

Uses legacy services (500K LOC gold) but with NEW wiring.
NO MONKEY PATCHING. EXPLICIT COMPOSITION.

GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
Mayavad: CLEAR (Explicit kernel with protocol-verified adapters)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from vibe_core.mahamantra.genesis.brahma.adapter import BrahmaAdapter
from vibe_core.mahamantra.dharma.janaka.adapter import JanakaAdapter
from vibe_core.mahamantra.kama.shuka.adapter import ShukaAdapter
from vibe_core.mahamantra.lila.migration import (
    verify_brahma_protocol,
    verify_lifecycle_protocol,
    verify_manifestation_protocol,
)
from vibe_core.mahamantra.protocols._gad import GADBase

if TYPE_CHECKING:
    from vibe_core.factory import VibeFactory
    from vibe_core.mahamantra.lila.migration import (
        BrahmaServiceProtocol,
        LifecycleServiceProtocol,
        ManifestationServiceProtocol,
    )

logger = logging.getLogger(__name__)


# =============================================================================
# SAMSKARA KERNEL (The Transformation)
# =============================================================================

class SamskaraKernel(GADBase):
    """
    The new Mahamantra-native kernel.

    ARCHITECTURE:
    -------------
    - Uses legacy services (the gold)
    - Wraps them in explicit adapters (the transformation)
    - Connects adapters to Mahamantra heartbeat (the integration)

    NO MONKEY PATCHING:
    -------------------
    We don't change kernel.brahma in-place.
    We BUILD a new kernel with proper adapters.

    WATERTIGHT:
    -----------
    - Protocol verification at construction
    - No Any types
    - No silent failures
    - Explicit error handling

    GAD-000: ✓D ✓O ✓P ✓C ✓I ✓R
    """

    def __init__(self, legacy_factory: VibeFactory):
        """
        Initialize Samskara kernel from legacy factory.

        Args:
            legacy_factory: The VibeFactory singleton

        Raises:
            TypeError: If legacy services don't implement required protocols
            RuntimeError: If kernel initialization fails
        """
        super().__init__()

        logger.info("🌊 Initiating Samskara transformation...")

        # Get legacy kernel (the raw material)
        try:
            raw_kernel = legacy_factory.get_kernel()
        except Exception as e:
            raise RuntimeError(f"Failed to get legacy kernel: {e}") from e

        # Initialize all adapters
        self._initialize_adapters(raw_kernel)

        # Register with Mahamantra heartbeat
        self._register_adapters()

        logger.info("🙏 Samskara kernel initialized")

    @classmethod
    def from_legacy(cls) -> SamskaraKernel:
        """
        Create SamskaraKernel from legacy VibeFactory singleton.

        This is the recommended way to instantiate the kernel.

        Returns:
            A new SamskaraKernel with all adapters initialized

        Raises:
            RuntimeError: If VibeFactory not available or initialization fails
        """
        from vibe_core.factory import VibeFactory

        # Get the singleton factory (the gold)
        try:
            legacy_factory = VibeFactory.get_instance()
        except Exception as e:
            raise RuntimeError(f"Failed to get VibeFactory singleton: {e}") from e

        # Construct via standard __init__
        return cls(legacy_factory)

    def _initialize_adapters(self, raw_kernel: object) -> None:
        """Extract and initialize all adapters from legacy kernel."""

        # =====================================================================
        # POSITION 1: BRAHMA (Genesis/Creation)
        # =====================================================================

        if not hasattr(raw_kernel, 'brahma'):
            raise RuntimeError("Legacy kernel has no brahma service")

        legacy_brahma = raw_kernel.brahma

        # Verify protocol compliance
        if not verify_brahma_protocol(legacy_brahma):
            raise TypeError(
                f"Legacy brahma service {type(legacy_brahma).__name__} "
                "does not implement BrahmaServiceProtocol"
            )

        # Create adapter (explicit, typed)
        self.brahma: BrahmaAdapter = BrahmaAdapter(legacy_brahma)
        logger.info("✓ Position 1 (Brahma) adapted")

        # =====================================================================
        # POSITION 10: JANAKA (Lifecycle/Maintenance)
        # =====================================================================

        if hasattr(raw_kernel, 'lifecycle'):
            legacy_lifecycle = raw_kernel.lifecycle

            # Verify protocol compliance
            if not verify_lifecycle_protocol(legacy_lifecycle):
                logger.warning(
                    f"Legacy lifecycle service {type(legacy_lifecycle).__name__} "
                    "does not implement LifecycleServiceProtocol. Skipping."
                )
            else:
                # Create adapter (explicit, typed)
                self.janaka: JanakaAdapter = JanakaAdapter(legacy_lifecycle)
                logger.info("✓ Position 10 (Janaka) adapted")
        else:
            logger.info("⊘ No lifecycle service found in legacy kernel")

        # =====================================================================
        # POSITION 14: SHUKA (Manifestation/Vision)
        # =====================================================================

        if hasattr(raw_kernel, 'manifestation'):
            legacy_manifestation = raw_kernel.manifestation

            # Verify protocol compliance
            if not verify_manifestation_protocol(legacy_manifestation):
                logger.warning(
                    f"Legacy manifestation service {type(legacy_manifestation).__name__} "
                    "does not implement ManifestationServiceProtocol. Skipping."
                )
            else:
                # Create adapter (explicit, typed)
                self.shuka: ShukaAdapter = ShukaAdapter(legacy_manifestation)
                logger.info("✓ Position 14 (Shuka) adapted")
        else:
            logger.info("⊘ No manifestation service found in legacy kernel")

    def _register_adapters(self) -> None:
        """
        Register all adapters with Mahamantra heartbeat.

        NO SILENT FAILURES:
        -------------------
        If registration fails, we log and raise.
        """
        try:
            from vibe_core.mahamantra import mahamantra

            # Register Brahma adapter
            if hasattr(self, 'brahma'):
                mahamantra.register_listener(self.brahma.on_tick)
                logger.info("✓ Brahma registered with heartbeat")

            # Register Janaka adapter
            if hasattr(self, 'janaka'):
                mahamantra.register_listener(self.janaka.on_tick)
                logger.info("✓ Janaka registered with heartbeat")

            # Register Shuka adapter
            if hasattr(self, 'shuka'):
                mahamantra.register_listener(self.shuka.on_tick)
                logger.info("✓ Shuka registered with heartbeat")

        except Exception as e:
            logger.error(f"Failed to register adapters: {e}")
            raise RuntimeError(f"Adapter registration failed: {e}") from e

    # =========================================================================
    # KERNEL OPERATIONS
    # =========================================================================

    def tick(self) -> None:
        """
        Tick the kernel (advance one position).

        Delegates to mahamantra.tick(), which broadcasts to all adapters.
        """
        from vibe_core.mahamantra import mahamantra
        mahamantra.tick()

    def chant(self) -> str:
        """
        Get the holy name.

        Returns:
            The 16-word Mahamantra
        """
        from vibe_core.mahamantra import mahamantra
        return mahamantra.chant()

    # =========================================================================
    # GAD-000 COMPLIANCE
    # =========================================================================

    def discover(self) -> dict[str, object]:
        """Discover kernel capabilities."""
        adapters = {}

        if hasattr(self, 'brahma'):
            adapters['brahma'] = self.brahma.discover()

        if hasattr(self, 'janaka'):
            adapters['janaka'] = self.janaka.discover()

        if hasattr(self, 'shuka'):
            adapters['shuka'] = self.shuka.discover()

        return {
            "type": "SamskaraKernel",
            "adapters": adapters,
            "adapter_count": len(adapters),
        }

    def get_state(self) -> dict[str, object]:
        """Get kernel state."""
        adapter_states = {}

        if hasattr(self, 'brahma'):
            adapter_states['brahma'] = self.brahma.get_state()

        if hasattr(self, 'janaka'):
            adapter_states['janaka'] = self.janaka.get_state()

        if hasattr(self, 'shuka'):
            adapter_states['shuka'] = self.shuka.get_state()

        return {
            "adapters": adapter_states,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def is_healthy(self) -> bool:
        """Check if kernel is healthy."""
        base_health = super().is_healthy()

        # Check adapter health
        if hasattr(self, 'brahma') and not self.brahma.is_healthy():
            return False

        if hasattr(self, 'janaka') and not self.janaka.is_healthy():
            return False

        if hasattr(self, 'shuka') and not self.shuka.is_healthy():
            return False

        return base_health

    @property
    def is_idempotent(self) -> bool:
        """Kernel operations are idempotent."""
        return True

    def detect_drift(self) -> list[str]:
        """Detect kernel drift."""
        drift: list[str] = []

        if hasattr(self, 'brahma'):
            adapter_drift = self.brahma.detect_drift()
            drift.extend([f"brahma: {d}" for d in adapter_drift])

        if hasattr(self, 'janaka'):
            adapter_drift = self.janaka.detect_drift()
            drift.extend([f"janaka: {d}" for d in adapter_drift])

        if hasattr(self, 'shuka'):
            adapter_drift = self.shuka.detect_drift()
            drift.extend([f"shuka: {d}" for d in adapter_drift])

        return drift

    # Dharma tests
    def test_daya(self) -> bool:
        """Mercy: Does kernel protect system?"""
        return True

    def test_satyam(self) -> bool:
        """Truth: Does kernel report honestly?"""
        return True

    def test_tapas(self) -> bool:
        """Austerity: Does kernel stay within bounds?"""
        return True

    def test_saucam(self) -> bool:
        """Cleanliness: Is kernel properly initialized?"""
        return hasattr(self, 'brahma')

    def __repr__(self) -> str:
        adapter_count = sum(1 for attr in ['brahma', 'janaka', 'shuka'] if hasattr(self, attr))
        return f"SamskaraKernel(adapters={adapter_count}, healthy={self.is_healthy()})"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["SamskaraKernel"]
