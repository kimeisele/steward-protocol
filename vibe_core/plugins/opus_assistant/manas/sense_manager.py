"""
OPUS-167: Sense Manager - Unified Sense Initialization

Extracted from CognitiveKernel to reduce kernel size and improve separation
of concerns. The SenseManager handles:

1. Initialization of all 7 Jnanendriyas (senses)
2. Boot-time perception for each sense
3. Lazy loading and caching
4. Unified configuration

The kernel orchestrates the OODA cycle, but the SenseManager
handles sense lifecycle.

Architecture:
    ┌─────────────────────────────────────────┐
    │            SENSE MANAGER                 │
    │  ┌─────────────────────────────────┐    │
    │  │      7 Jnanendriyas (Senses)    │    │
    │  │                                 │    │
    │  │  Prakriti │ Dharma │ Sutra     │    │
    │  │  Shruta   │ Prana              │    │
    │  │  Karma    │ Viveka             │    │
    │  └─────────────────────────────────┘    │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
                 COGNITIVE KERNEL
               (Uses senses for OODA)
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
    OPUS-167: Unified Sense Initialization and Management.

    This class manages all 7 Jnanendriyas (sense organs) for MANAS:
    1. PrakritiSense - System state perception (Guna)
    2. DharmaSense - Ethical alignment checking
    3. SutraSense - Documentation gap detection (Doc→Code)
    4. ShrutaSense - Filesystem event listening
    5. PranaSense - Agent lifecycle awareness
    6. KarmaSense - Historical pattern detection (chronic pain)
    7. VivekaSense - Coverage gap discrimination (Code→Doc)

    Usage:
        manager = SenseManager(workspace=Path.cwd(), config={})

        # Boot all senses
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

        # Sense instances (lazily initialized)
        self._prakriti: Optional["PrakritiSense"] = None
        self._dharma: Optional["DharmaSense"] = None
        self._sutra: Optional["SutraSense"] = None
        self._shruta: Optional["ShrutaSense"] = None
        self._prana: Optional["PranaSense"] = None
        self._karma: Optional["KarmaSense"] = None
        self._viveka: Optional["VivekaSense"] = None

        # Boot state tracking
        self._booted: Dict[str, bool] = {}

        logger.debug("🧘 SENSE MANAGER: Initialized")

    # =========================================================================
    # SENSE PROPERTIES (Lazy Access)
    # =========================================================================

    @property
    def prakriti_sense(self) -> Optional["PrakritiSense"]:
        """Get Prakriti Sense (system state perception)."""
        if self._prakriti is None and "prakriti_sense" not in self._booted:
            self._init_prakriti()
        return self._prakriti

    @property
    def dharma_sense(self) -> Optional["DharmaSense"]:
        """Get Dharma Sense (ethical alignment)."""
        if self._dharma is None and "dharma_sense" not in self._booted:
            self._init_dharma()
        return self._dharma

    @property
    def sutra_sense(self) -> Optional["SutraSense"]:
        """Get Sutra Sense (documentation gaps)."""
        if self._sutra is None and "sutra_sense" not in self._booted:
            self._init_sutra()
        return self._sutra

    @property
    def shruta_sense(self) -> Optional["ShrutaSense"]:
        """Get Shruta Sense (filesystem events)."""
        if self._shruta is None and "shruta_sense" not in self._booted:
            self._init_shruta()
        return self._shruta

    @property
    def prana_sense(self) -> Optional["PranaSense"]:
        """Get Prana Sense (agent lifecycle)."""
        if self._prana is None and "prana_sense" not in self._booted:
            self._init_prana()
        return self._prana

    @property
    def karma_sense(self) -> Optional["KarmaSense"]:
        """Get Karma Sense (historical patterns / chronic pain)."""
        if self._karma is None and "karma_sense" not in self._booted:
            self._init_karma()
        return self._karma

    @property
    def viveka_sense(self) -> Optional["VivekaSense"]:
        """Get Viveka Sense (coverage gap discrimination)."""
        if self._viveka is None and "viveka_sense" not in self._booted:
            self._init_viveka()
        return self._viveka

    # =========================================================================
    # INITIALIZATION METHODS
    # =========================================================================

    def _init_prakriti(self) -> SenseBootResult:
        """Initialize Prakriti Sense - System state perception."""
        self._booted["prakriti_sense"] = True
        try:
            from .cortex.prakriti_sense import PrakritiSense

            sense_config = self._config.get("prakriti_sense", {})
            self._prakriti = PrakritiSense(
                workspace=self._workspace,
                config=sense_config,
            )
            # Boot perception
            summary = self._prakriti.on_manas_boot()
            logger.info(
                f"👁️ PRAKRITI SENSE: Initialized - Total: {summary.total_paths}, Health: {summary.health_ratio:.0%}"
            )
            return SenseBootResult(
                sense_name="prakriti_sense",
                success=True,
                message=f"Health: {summary.health_ratio:.0%}",
                data={"total_paths": summary.total_paths, "health": summary.health_ratio},
            )
        except Exception as e:
            logger.warning(f"👁️ PRAKRITI SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="prakriti_sense",
                success=False,
                message=str(e),
            )

    def _init_dharma(self) -> SenseBootResult:
        """Initialize Dharma Sense - Ethical alignment checker."""
        self._booted["dharma_sense"] = True
        try:
            from .cortex.dharma_sense import DharmaSense

            sense_config = self._config.get("dharma_sense", {})
            self._dharma = DharmaSense(
                workspace=self._workspace,
                config=sense_config,
            )
            # Get summary (OPUS-167 FIX: method is get_dharma_summary, not get_summary)
            summary = self._dharma.get_dharma_summary()
            logger.info(f"🙏 DHARMA SENSE: Initialized - Bhakti: {summary.bhakti_score}")
            return SenseBootResult(
                sense_name="dharma_sense",
                success=True,
                message=f"Bhakti: {summary.bhakti_score}",
                data={"bhakti": summary.bhakti_score},
            )
        except Exception as e:
            logger.warning(f"🙏 DHARMA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="dharma_sense",
                success=False,
                message=str(e),
            )

    def _init_sutra(self) -> SenseBootResult:
        """Initialize Sutra Sense - Documentation gap detector."""
        self._booted["sutra_sense"] = True
        try:
            from .cortex.sutra_sense import SutraSense

            sense_config = self._config.get("sutra_sense", {})
            self._sutra = SutraSense(
                workspace=self._workspace,
                config=sense_config,
            )
            logger.info("📜 SUTRA SENSE: Initialized")
            return SenseBootResult(
                sense_name="sutra_sense",
                success=True,
                message="Initialized",
            )
        except Exception as e:
            logger.warning(f"📜 SUTRA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="sutra_sense",
                success=False,
                message=str(e),
            )

    def _init_shruta(self) -> SenseBootResult:
        """Initialize Shruta Sense - Filesystem event listener."""
        self._booted["shruta_sense"] = True
        try:
            from .cortex.shruta_sense import ShrutaSense

            sense_config = self._config.get("shruta_sense", {})
            self._shruta = ShrutaSense(
                workspace=self._workspace,
                config=sense_config,
            )
            logger.info("👂 SHRUTA SENSE: Initialized")
            return SenseBootResult(
                sense_name="shruta_sense",
                success=True,
                message="Initialized",
            )
        except Exception as e:
            logger.warning(f"👂 SHRUTA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="shruta_sense",
                success=False,
                message=str(e),
            )

    def _init_prana(self) -> SenseBootResult:
        """Initialize Prana Sense - Agent lifecycle awareness."""
        self._booted["prana_sense"] = True
        try:
            from .cortex.prana_sense import PranaSense

            sense_config = self._config.get("prana_sense", {})
            self._prana = PranaSense(
                workspace=self._workspace,
                config=sense_config,
            )
            logger.info("🫀 PRANA SENSE: Initialized")
            return SenseBootResult(
                sense_name="prana_sense",
                success=True,
                message="Initialized",
            )
        except Exception as e:
            logger.warning(f"🫀 PRANA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="prana_sense",
                success=False,
                message=str(e),
            )

    def _init_karma(self) -> SenseBootResult:
        """Initialize Karma Sense - Historical pattern detection."""
        self._booted["karma_sense"] = True
        try:
            from .cortex.karma_sense import KarmaSense

            sense_config = self._config.get("karma_sense", {})
            self._karma = KarmaSense(
                workspace=self._workspace,
                config=sense_config,
            )
            # Get summary
            report = self._karma.find_hotspots()
            logger.info(
                f"🔮 KARMA SENSE: Initialized - Hotspots: {report.hotspot_count}, Health: {report.health_score:.0%}"
            )
            return SenseBootResult(
                sense_name="karma_sense",
                success=True,
                message=f"Hotspots: {report.hotspot_count}",
                data={"hotspots": report.hotspot_count, "health": report.health_score},
            )
        except Exception as e:
            logger.warning(f"🔮 KARMA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="karma_sense",
                success=False,
                message=str(e),
            )

    def _init_viveka(self) -> SenseBootResult:
        """Initialize Viveka Sense - Coverage gap discrimination."""
        self._booted["viveka_sense"] = True
        try:
            from .cortex.viveka_sense import VivekaSense

            sense_config = self._config.get("viveka_sense", {})
            self._viveka = VivekaSense(
                workspace=self._workspace,
                config=sense_config,
            )
            logger.info("🔍 VIVEKA SENSE: Initialized")
            return SenseBootResult(
                sense_name="viveka_sense",
                success=True,
                message="Initialized",
            )
        except Exception as e:
            logger.warning(f"🔍 VIVEKA SENSE: Failed to initialize: {e}")
            return SenseBootResult(
                sense_name="viveka_sense",
                success=False,
                message=str(e),
            )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def boot_all(self) -> List[SenseBootResult]:
        """
        Boot all senses at once.

        Returns:
            List of boot results for each sense
        """
        results = []

        # Boot in order of importance
        results.append(self._init_prakriti())
        results.append(self._init_dharma())
        results.append(self._init_sutra())
        results.append(self._init_shruta())
        results.append(self._init_prana())
        results.append(self._init_karma())
        results.append(self._init_viveka())

        successful = sum(1 for r in results if r.success)
        logger.info(f"🧘 SENSE MANAGER: Booted {successful}/7 senses")

        return results

    def inject(self, sense_name: str, instance: Any) -> None:
        """
        Inject a sense instance (for testing or external initialization).

        Args:
            sense_name: Name of the sense (e.g., "prakriti_sense")
            instance: The sense instance to inject
        """
        self._booted[sense_name] = True

        if sense_name == "prakriti_sense":
            self._prakriti = instance
        elif sense_name == "dharma_sense":
            self._dharma = instance
        elif sense_name == "sutra_sense":
            self._sutra = instance
        elif sense_name == "shruta_sense":
            self._shruta = instance
        elif sense_name == "prana_sense":
            self._prana = instance
        elif sense_name == "karma_sense":
            self._karma = instance
        elif sense_name == "viveka_sense":
            self._viveka = instance
        else:
            raise ValueError(f"Unknown sense: {sense_name}")

        logger.debug(f"🧘 SENSE MANAGER: Injected {sense_name}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all sense states."""
        senses = [
            self._prakriti,
            self._dharma,
            self._sutra,
            self._shruta,
            self._prana,
            self._karma,
            self._viveka,
        ]
        return {
            "prakriti_initialized": self._prakriti is not None,
            "dharma_initialized": self._dharma is not None,
            "sutra_initialized": self._sutra is not None,
            "shruta_initialized": self._shruta is not None,
            "prana_initialized": self._prana is not None,
            "karma_initialized": self._karma is not None,
            "viveka_initialized": self._viveka is not None,
            "total_booted": sum(1 for s in senses if s is not None),
            "total_senses": 7,
        }


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "SenseManager",
    "SenseBootResult",
]
