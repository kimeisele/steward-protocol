"""
OPUS-167: Logger Bridge - MANAS Observation Logging

Extracted from CognitiveKernel to reduce kernel size.
This bridge handles initialization and provides a clean interface
for logging MANAS thoughts to OPUS.md.

The actual logging is done by ObservationLogger from opus_assistant/core.
This bridge just handles the wiring and provides kernel-friendly methods.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("MANAS.LoggerBridge")


class LoggerBridge:
    """
    OPUS-167: Bridge to ObservationLogger for MANAS thoughts.

    This class extracts the observation logging logic from the kernel.
    It provides simple methods that the kernel can use without knowing
    the implementation details of ObservationLogger.

    Usage:
        bridge = LoggerBridge(workspace=Path.cwd(), config={})
        bridge.log_insight("Pattern recognized: test failures cluster")
        bridge.log_observation("Processing 5 intents", severity="info")
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize LoggerBridge.

        Args:
            workspace: Workspace root path
            config: Configuration from manas.yaml (observation_logger section)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}
        self._logger: Optional[Any] = None

        self._init_logger()

    def _init_logger(self) -> None:
        """Initialize the underlying ObservationLogger."""
        try:
            from vibe_core.plugins.opus_assistant.core.observation_logger import (
                ObservationLogger,
            )

            obs_config = self._config.get("observation_logger", {})
            self._logger = ObservationLogger(
                workspace_root=self._workspace,
                config=obs_config,
            )
            logger.info(f"📓 LOGGER BRIDGE: Initialized (config: {len(obs_config)} keys)")

        except Exception as e:
            logger.warning(f"📓 LOGGER BRIDGE: Could not initialize: {e}")
            self._logger = None

    @property
    def is_available(self) -> bool:
        """Check if the logger is available."""
        return self._logger is not None

    def log_insight(self, message: str, source: str = "MANAS") -> None:
        """
        Log an insight to OPUS.md journal.

        Use this to make MANAS's internal thoughts visible:
        - Dream insights from memory_review
        - Pattern recognitions
        - Self-debugging observations

        Args:
            message: The insight message
            source: Source identifier (default: MANAS)
        """
        if self._logger:
            self._logger.log_insight(message, source=source)
        # Also log to Python logger for file logs
        logger.info(f"💡 {source} INSIGHT: {message}")

    def log_observation(
        self,
        message: str,
        severity: str = "info",
        source: str = "MANAS",
    ) -> None:
        """
        Log an observation to OPUS.md journal.

        Args:
            message: The observation message
            severity: "info", "warn", "alert", or "insight"
            source: Source identifier (default: MANAS)
        """
        if self._logger:
            if severity == "insight":
                self._logger.log_insight(message, source=source)
            elif severity == "warn":
                self._logger.log_warn(message, source=source)
            elif severity == "alert":
                self._logger.log_alert(message, source=source)
            else:
                self._logger.log_info(message, source=source)

    def log_info(self, message: str, source: str = "MANAS") -> None:
        """Log an info message."""
        self.log_observation(message, severity="info", source=source)

    def log_warn(self, message: str, source: str = "MANAS") -> None:
        """Log a warning message."""
        self.log_observation(message, severity="warn", source=source)

    def log_alert(self, message: str, source: str = "MANAS") -> None:
        """Log an alert message."""
        self.log_observation(message, severity="alert", source=source)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "LoggerBridge",
]
