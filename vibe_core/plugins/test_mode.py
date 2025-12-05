"""
TEST MODE PLUGIN - Fast Kernel for Testing

This plugin provides a "fast path" for test execution by:
1. Skipping slow initialization (tool discovery, process spawning)
2. Providing mock interfaces for expensive operations
3. Enabling test isolation

PHILOSOPHY:
"The kernel is Vishnu - but in the dream realm of testing,
 even Vishnu can move at the speed of thought."

USAGE:
    # In conftest.py or test setup:
    from vibe_core.plugins.test_mode import enable_test_mode
    enable_test_mode()

    # Tests now get fast kernel initialization
    kernel = RealVibeKernel(ledger_path=":memory:")  # Fast!

    # After tests:
    from vibe_core.plugins.test_mode import disable_test_mode
    disable_test_mode()
"""

import logging
from typing import TYPE_CHECKING

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TEST_MODE")

# Global test mode state
_test_mode_enabled = False
_skip_tool_discovery = False
_skip_process_spawn = False


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

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots."""
        if _test_mode_enabled:
            logger.info("TEST MODE: Kernel booting in test mode (fast path)")


def enable_test_mode(
    skip_tool_discovery: bool = True,
    skip_process_spawn: bool = True,
) -> None:
    """
    Enable test mode for faster kernel initialization.

    Args:
        skip_tool_discovery: Skip auto-discovery of agent tools
        skip_process_spawn: Skip process spawning for agents
    """
    global _test_mode_enabled, _skip_tool_discovery, _skip_process_spawn
    _test_mode_enabled = True
    _skip_tool_discovery = skip_tool_discovery
    _skip_process_spawn = skip_process_spawn
    logger.info("TEST MODE ENABLED: Fast kernel initialization active")


def disable_test_mode() -> None:
    """Disable test mode and restore normal kernel behavior."""
    global _test_mode_enabled, _skip_tool_discovery, _skip_process_spawn
    _test_mode_enabled = False
    _skip_tool_discovery = False
    _skip_process_spawn = False
    logger.info("TEST MODE DISABLED: Normal kernel behavior restored")


def is_test_mode() -> bool:
    """Check if test mode is enabled."""
    return _test_mode_enabled


def should_skip_tool_discovery() -> bool:
    """Check if tool discovery should be skipped."""
    return _test_mode_enabled and _skip_tool_discovery


def should_skip_process_spawn() -> bool:
    """Check if process spawning should be skipped."""
    return _test_mode_enabled and _skip_process_spawn
