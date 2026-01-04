"""
TEST MODE PLUGIN PACKAGE
Exposes global state functions for backward compatibility.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("TEST_MODE")

# Global test mode state
_test_mode_enabled = False
_skip_tool_discovery = False
_skip_process_spawn = False


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


from .plugin_main import TestModePlugin

__all__ = [
    "enable_test_mode",
    "disable_test_mode",
    "is_test_mode",
    "should_skip_tool_discovery",
    "should_skip_process_spawn",
    "TestModePlugin",
]
