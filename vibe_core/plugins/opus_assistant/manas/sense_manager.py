"""
OPUS-167: Sense Manager - VEDA-4 Compliant Sense Initialization

REFACTORED: Uses SenseLoader (VEDA-4) instead of hardcoded init methods.

This class manages all 7 Jnanendriyas (sense organs) for MANAS:
1. PrakritiSense - System state perception (Guna)
2. DharmaSense   - Ethical alignment checking
3. SutraSense    - Documentation gap detection (Doc→Code)
4. ShrutaSense   - Filesystem event listening
5. PranaSense    - Agent lifecycle awareness
6. KarmaSense    - Historical pattern detection (chronic pain)
7. VivekaSense   - Coverage gap discrimination (Code→Doc)

Architecture:
    ┌─────────────────────────────────────────┐
    │         SENSE MANAGER (VEDA-4)          │
    │  ┌─────────────────────────────────┐    │
    │  │   SenseLoader.discover_and_load │    │
    │  │        ↓ Auto-discovery ↓       │    │
    │  │      7 Jnanendriyas (Senses)    │    │
    │  └─────────────────────────────────┘    │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
                 COGNITIVE KERNEL
               (Uses senses for OODA)

VEDA-4 PATTERN:
    SHABDA   (शब्द)    → SenseLoader scans cortex/*_sense.py
    ARTHA    (अर्थ)    → Validates BaseSense inheritance
    PRATYAYA (प्रत्यय) → Checks enabled status
    KARMA    (कर्म)    → Instantiates with workspace
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .cortex.dharma_sense import DharmaSense
    from .cortex.karma_sense import KarmaSense
    from .cortex.prakriti_sense import PrakritiSense
    from .cortex.prana_sense import PranaSense
    from .cortex.shruta_sense import ShrutaSense
    from .cortex.sutra_sense import SutraSense
    from .cortex.viveka_sense import VivekaSense

logger = logging.getLogger("MANAS.SenseManager")


@dataclass
class SenseBootResult:
    """Result of booting a sense."""

    sense_name: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class SenseManager:
    """
    OPUS-167: VEDA-4 Compliant Sense Manager.

    Uses SenseLoader for auto-discovery instead of hardcoded init methods.

    Usage:
        manager = SenseManager(workspace=Path.cwd(), config={})

        # Boot all senses (uses SenseLoader internally)
        results = manager.boot_all()

        # Get specific sense
        prakriti = manager.prakriti_sense

        # Inject sense (for testing or external initialization)
        manager.inject("prakriti_sense", prakriti_instance)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize SenseManager.

        Args:
            workspace: Workspace root path
            config: Full MANAS configuration (from config/manas.yaml)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}

        # VEDA-4: Single dict for all senses (populated by loader)
        self._senses: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

        # Boot state tracking
        self._booted = False

        logger.debug("🧘 SENSE MANAGER: Initialized (VEDA-4 mode)")

    # =========================================================================
    # SENSE PROPERTIES (Lazy Access via Loader)
    # =========================================================================

    @property
    def prakriti_sense(self) -> Optional["PrakritiSense"]:
        """Get Prakriti Sense (system state perception)."""
        self._ensure_booted()
        return self._senses.get("prakriti_sense")

    @property
    def dharma_sense(self) -> Optional["DharmaSense"]:
        """Get Dharma Sense (ethical alignment)."""
        self._ensure_booted()
        return self._senses.get("dharma_sense")

    @property
    def sutra_sense(self) -> Optional["SutraSense"]:
        """Get Sutra Sense (documentation gaps)."""
        self._ensure_booted()
        return self._senses.get("sutra_sense")

    @property
    def shruta_sense(self) -> Optional["ShrutaSense"]:
        """Get Shruta Sense (filesystem events)."""
        self._ensure_booted()
        return self._senses.get("shruta_sense")

    @property
    def prana_sense(self) -> Optional["PranaSense"]:
        """Get Prana Sense (agent lifecycle)."""
        self._ensure_booted()
        return self._senses.get("prana_sense")

    @property
    def karma_sense(self) -> Optional["KarmaSense"]:
        """Get Karma Sense (historical patterns / chronic pain)."""
        self._ensure_booted()
        return self._senses.get("karma_sense")

    @property
    def viveka_sense(self) -> Optional["VivekaSense"]:
        """Get Viveka Sense (coverage gap discrimination)."""
        self._ensure_booted()
        return self._senses.get("viveka_sense")

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def boot_all(self) -> List[SenseBootResult]:
        """
        Boot all senses using VEDA-4 SenseLoader.

        Returns:
            List of boot results for each sense
        """
        if self._booted:
            logger.debug("🧘 SENSE MANAGER: Already booted")
            return self._generate_results()

        # Import here to avoid circular imports
        from vibe_core.loaders.sense_loader import SenseLoader

        results: List[SenseBootResult] = []

        try:
            # VEDA-4: Single unified discovery and loading
            logger.info("🧘 SENSE MANAGER: Booting senses via SenseLoader (VEDA-4)...")
            self._senses, self._metadata = SenseLoader.discover_and_load(
                workspace=self._workspace,
                config=self._config,
            )

            # Generate boot results from discovered senses
            for sense_name, sense in self._senses.items():
                result = self._create_boot_result(sense_name, sense)
                results.append(result)

            self._booted = True

            successful = sum(1 for r in results if r.success)
            logger.info(f"🧘 SENSE MANAGER: Booted {successful}/{len(results)} senses (VEDA-4)")

        except Exception as e:
            logger.error(f"🧘 SENSE MANAGER: Boot failed: {e}")
            results.append(
                SenseBootResult(
                    sense_name="__boot__",
                    success=False,
                    message=f"SenseLoader failed: {e}",
                )
            )

        return results

    def inject(self, sense_name: str, instance: Any) -> None:
        """
        Inject a sense instance (for testing or external initialization).

        Args:
            sense_name: Name of the sense (e.g., "prakriti_sense")
            instance: The sense instance to inject
        """
        self._senses[sense_name] = instance
        logger.debug(f"🧘 SENSE MANAGER: Injected {sense_name}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all sense states."""
        self._ensure_booted()

        return {
            "prakriti_initialized": self._senses.get("prakriti_sense") is not None,
            "dharma_initialized": self._senses.get("dharma_sense") is not None,
            "sutra_initialized": self._senses.get("sutra_sense") is not None,
            "shruta_initialized": self._senses.get("shruta_sense") is not None,
            "prana_initialized": self._senses.get("prana_sense") is not None,
            "karma_initialized": self._senses.get("karma_sense") is not None,
            "viveka_initialized": self._senses.get("viveka_sense") is not None,
            "total_booted": len(self._senses),
            "total_senses": 7,
            "loader": "SenseLoader (VEDA-4)",
        }

    def get_sense(self, name: str) -> Optional[Any]:
        """
        Get any sense by name (generic accessor).

        Args:
            name: Sense name (e.g., "prakriti_sense", "karma_sense")

        Returns:
            Sense instance or None
        """
        self._ensure_booted()
        return self._senses.get(name)

    def list_senses(self) -> List[str]:
        """List all loaded sense names."""
        self._ensure_booted()
        return list(self._senses.keys())

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _ensure_booted(self) -> None:
        """Ensure senses are booted (lazy boot on first access)."""
        if not self._booted:
            self.boot_all()

    def _create_boot_result(self, sense_name: str, sense: Any) -> SenseBootResult:
        """
        Create a SenseBootResult from a loaded sense.

        Tries to extract boot summary data from sense-specific methods.
        """
        try:
            data: Dict[str, Any] = {}
            message = "Initialized"

            # Sense-specific boot data extraction
            if sense_name == "prakriti_sense" and hasattr(sense, "on_manas_boot"):
                summary = sense.on_manas_boot()
                if summary:
                    data["total_paths"] = getattr(summary, "total_paths", 0)
                    data["health"] = getattr(summary, "health_ratio", 0.0)
                    message = f"Health: {data['health']:.0%}"
                    logger.info(f"👁️ PRAKRITI SENSE: Total: {data['total_paths']}, Health: {data['health']:.0%}")

            elif sense_name == "dharma_sense" and hasattr(sense, "get_dharma_summary"):
                summary = sense.get_dharma_summary()
                if summary:
                    data["bhakti"] = getattr(summary, "bhakti_score", 0)
                    message = f"Bhakti: {data['bhakti']}"
                    logger.info(f"🙏 DHARMA SENSE: Bhakti: {data['bhakti']}")

            elif sense_name == "karma_sense" and hasattr(sense, "find_hotspots"):
                report = sense.find_hotspots()
                if report:
                    data["hotspots"] = getattr(report, "hotspot_count", 0)
                    data["health"] = getattr(report, "health_score", 0.0)
                    message = f"Hotspots: {data['hotspots']}"
                    logger.info(f"🔮 KARMA SENSE: Hotspots: {data['hotspots']}, Health: {data['health']:.0%}")

            elif sense_name == "sutra_sense":
                logger.info("📜 SUTRA SENSE: Initialized")

            elif sense_name == "shruta_sense":
                logger.info("👂 SHRUTA SENSE: Initialized")

            elif sense_name == "prana_sense":
                logger.info("🫀 PRANA SENSE: Initialized")

            elif sense_name == "viveka_sense":
                logger.info("🔍 VIVEKA SENSE: Initialized")

            else:
                # Unknown sense - still log it
                logger.info(f"✨ {sense_name.upper()}: Initialized")

            return SenseBootResult(
                sense_name=sense_name,
                success=True,
                message=message,
                data=data if data else None,
            )

        except Exception as e:
            logger.warning(f"🧘 {sense_name}: Boot introspection failed: {e}")
            return SenseBootResult(
                sense_name=sense_name,
                success=True,  # Sense loaded, just no extra data
                message=f"Initialized (no summary: {e})",
            )

    def _generate_results(self) -> List[SenseBootResult]:
        """Generate boot results from already-loaded senses."""
        return [
            SenseBootResult(
                sense_name=name,
                success=True,
                message="Already booted",
            )
            for name in self._senses.keys()
        ]


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "SenseManager",
    "SenseBootResult",
]
