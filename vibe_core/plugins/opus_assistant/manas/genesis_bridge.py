"""
OPUS-167: Genesis Bridge - Infrastructure Auto-Generation

Extracted from CognitiveKernel to reduce kernel size.
This bridge handles the "Stadtamt" service for GAD-000 compliant infrastructure.

The bridge delegates to:
1. vibe_core.genesis.GenesisService (OPUS-160) - preferred
2. cortex.genesis (OPUS-158) - legacy fallback

"Jedes Haus bekommt einen Briefkasten. Jede Straße ein Schild."
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .cortex.genesis import InfrastructureClassifier, InfrastructureGenerator
    from .cortex.shruta_sense import ShrutaPerception

logger = logging.getLogger("MANAS.GenesisBridge")


class GenesisBridge:
    """
    OPUS-167: Bridge to Infrastructure Genesis (Stadtamt Service).

    This class extracts the infrastructure generation logic from the kernel.
    It provides a clean interface for auto-generating GAD-000 compliant
    infrastructure when new directories are created.

    Usage:
        bridge = GenesisBridge(workspace=Path.cwd(), config={})

        # Process filesystem vibrations
        perception = shruta_sense.perceive()
        bridge.process_vibrations(perception)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize GenesisBridge.

        Args:
            workspace: Workspace root path
            config: Configuration from manas.yaml (genesis section)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}

        # Legacy components (OPUS-158)
        self._classifier: Optional["InfrastructureClassifier"] = None
        self._generator: Optional["InfrastructureGenerator"] = None

        self._enabled = self._config.get("genesis", {}).get("enabled", True)

        if self._enabled:
            self._init_legacy_genesis()

    def _init_legacy_genesis(self) -> None:
        """Initialize legacy OPUS-158 genesis components."""
        try:
            from .cortex.genesis import InfrastructureClassifier, InfrastructureGenerator

            self._classifier = InfrastructureClassifier(workspace=self._workspace)
            self._generator = InfrastructureGenerator(workspace=self._workspace)

            logger.info(
                "🏛️ GENESIS BRIDGE: Stadtamt Service activated (GAD-000 infrastructure)"
            )

        except Exception as e:
            logger.warning(f"🏛️ GENESIS BRIDGE: Could not initialize: {e}")
            self._classifier = None
            self._generator = None

    @property
    def is_enabled(self) -> bool:
        """Check if genesis is enabled."""
        return self._enabled

    @property
    def is_available(self) -> bool:
        """Check if legacy genesis is available."""
        return self._classifier is not None and self._generator is not None

    def process_vibrations(self, perception: "ShrutaPerception") -> None:
        """
        Process filesystem vibrations for Infrastructure Genesis.

        OPUS-160: Delegates to vibe_core.genesis.GenesisService (Stadtamt).
        Falls back to OPUS-158 legacy genesis if not available.

        Args:
            perception: Filesystem perception from ShrutaSense
        """
        if not self._enabled:
            return

        try:
            # Try to use vibe_core GenesisService (OPUS-160)
            from vibe_core.genesis import GenesisService, ModuleType

            genesis = GenesisService.get_instance(workspace=self._workspace)

            for vibration in perception.vibrations:
                # Only process directory creation events
                if vibration.event_type != "created" or not vibration.is_directory:
                    continue

                # Classify and ensure compliance via Stadtamt
                module_type = genesis.classify_path(vibration.path)

                if module_type == ModuleType.UNKNOWN:
                    continue

                # Call the Stadtamt for compliance
                result = genesis.ensure_compliance(vibration.path, module_type)

                if result.build_result and result.build_result.files_created_count > 0:
                    logger.info(
                        f"🏛️ STADTAMT: Created {result.build_result.files_created_count} files "
                        f"for {module_type.name}: {vibration.path.name}"
                    )

        except ImportError:
            # Fallback to OPUS-158 local genesis (legacy)
            self._process_legacy(perception)
        except Exception as e:
            logger.warning(f"🏛️ GENESIS: Error processing vibrations: {e}")

    def _process_legacy(self, perception: "ShrutaPerception") -> None:
        """
        Legacy genesis processing (OPUS-158 fallback).

        Used when vibe_core.genesis is not available.
        """
        if not self._classifier or not self._generator:
            return

        try:
            from .cortex.genesis import ModuleType

            for vibration in perception.vibrations:
                if vibration.event_type != "created" or not vibration.is_directory:
                    continue

                module_type = self._classifier.classify(vibration.path, is_directory=True)

                if module_type == ModuleType.UNKNOWN:
                    continue

                result = self._generator.generate(vibration.path, module_type)

                if result.files_created_count > 0:
                    logger.info(
                        f"🏛️ GENESIS (legacy): Auto-generated {result.files_created_count} files "
                        f"for {module_type.name}: {vibration.path.name}"
                    )

        except Exception as e:
            logger.warning(f"🏛️ GENESIS (legacy): Error: {e}")


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "GenesisBridge",
]
