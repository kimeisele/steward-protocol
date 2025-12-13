"""
Boot Mode - Startup Configuration for Different Execution Contexts

OPUS-031 Layer 4: Autonomous Conductor requires fast, lightweight boot.

Boot Modes:
-----------
FULL: Complete boot with all agents, gateway, discovery (default)
      - Agent discovery and process spawning
      - Network gateway thread
      - Daily ritual heartbeat
      - Full conveyor belt (BootSequence)
      - Used by: `steward start`, production servers

HEADLESS: Lightweight boot for autonomous execution (< 5 seconds)
          - NO agent discovery or process spawning
          - NO network gateway
          - NO daily ritual
          - StateManager + LLM + FileSystem only
          - Used by: `steward execute --headless`, CI/CD, maintenance circuits

MINIMAL: Bare kernel for testing
         - Kernel only, no plugins
         - No external dependencies
         - Used by: Unit tests, mocks

Architecture:
    BootMode is passed to BootOrchestrator and RealVibeKernel.
    Each Sarga phase checks boot_mode to decide what to skip.
"""

from enum import Enum


class BootMode(str, Enum):
    """Boot mode determines which components are loaded at startup."""

    FULL = "full"  # All components (default)
    HEADLESS = "headless"  # Lightweight for autonomous execution
    MINIMAL = "minimal"  # Bare kernel for testing

    def is_headless(self) -> bool:
        """Check if this is a headless boot (no heavy components)."""
        return self in (BootMode.HEADLESS, BootMode.MINIMAL)

    def should_skip_agents(self) -> bool:
        """Check if agent discovery should be skipped."""
        return self in (BootMode.HEADLESS, BootMode.MINIMAL)

    def should_skip_gateway(self) -> bool:
        """Check if network gateway should be skipped."""
        return self in (BootMode.HEADLESS, BootMode.MINIMAL)

    def should_skip_daily_ritual(self) -> bool:
        """Check if daily ritual should be skipped."""
        return self in (BootMode.HEADLESS, BootMode.MINIMAL)

    def should_load_plugins(self) -> bool:
        """Check if plugins should be loaded."""
        # Plugins are needed even in headless for OPUS StateManager
        return self != BootMode.MINIMAL
