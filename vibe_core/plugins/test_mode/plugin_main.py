"""
Test Mode Plugin - Main Entry Point.
"""

import logging
from typing import TYPE_CHECKING, Optional

from vibe_core.plugin_protocol import KernelPlugin

from . import is_test_mode

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("TEST_MODE_PLUGIN")


class TestModePlugin(KernelPlugin):
    """
    Test Mode Plugin - Accelerates kernel for testing.

    Priority: 1 (runs before everything else)

    When enabled:
    - Skips tool discovery (saves 2-3s per kernel)
    - Skips process spawning (saves 1-2s per agent)
    - Uses in-memory storage only
    """

    @property
    def plugin_id(self) -> str:
        return "test_mode"

    @property
    def priority(self) -> int:
        return 1  # Runs first

    def __init__(self):
        self._kernel: Optional["KernelProtocol"] = None

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """Called when kernel boots."""
        self._kernel = kernel
        if is_test_mode():
            logger.info("TEST MODE: Kernel booting in test mode (fast path)")
