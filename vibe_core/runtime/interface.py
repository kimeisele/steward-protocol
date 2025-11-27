"""
ARCH-065: Polymorphic Interface Manager

The brain that detects and switches between interface modes.

Vibe OS is a shapeshifter:
- Am I at a terminal? -> INTERACTIVE MODE (fancy UI, colors, wait for input)
- Am I in a pipe (Claude)? -> HEADLESS MODE (JSON/Text output, no wait loops)
- Am I part of a swarm? -> STEWARD MODE (Protocol-based, sovereign operation)

This module provides environment detection and mode switching.

Design:
- Detects actual runtime environment (not configuration)
- Supports explicit override via VIBE_MODE environment variable
- Falls back gracefully to headless when TTY is unavailable
- No side effects, pure detection logic
"""

import os
import sys
from enum import Enum


class InterfaceMode(Enum):
    """
    Three modes of operation for Vibe OS.

    INTERACTIVE: TTY detected, human at terminal
    - Shows HUD (status bar, capabilities, hints)
    - Waits for user input in REPL loop
    - For development, debugging, human-in-the-loop

    HEADLESS: Pipe/CI detected, automated context
    - No HUD, no input waiting
    - Outputs status messages and results
    - Clean exit so parent process can continue
    - For Claude integration, CI/CD, automation

    STEWARD: Protocol-based, sovereign operation
    - Reads from .steward/active_session.json
    - Processes task queue autonomously
    - For multi-agent coordination (GAD-000)
    """

    INTERACTIVE = "interactive"
    HEADLESS = "headless"
    STEWARD = "steward"


class InterfaceManager:
    """
    Detects runtime environment and selects appropriate interface mode.

    Physics-based detection:
    1. Check for explicit override (environment variable)
    2. Check for Steward protocol files
    3. Check if stdin is a TTY (the physics: are we connected to a terminal?)
    4. Default to headless (safe fallback for automated contexts)

    Example:
        >>> mode = InterfaceManager.detect_mode()
        >>> if mode == InterfaceMode.INTERACTIVE:
        ...     start_repl_loop()
        ... elif mode == InterfaceMode.HEADLESS:
        ...     boot_and_exit()
    """

    @staticmethod
    def detect_mode() -> InterfaceMode:
        """
        Detect the appropriate interface mode based on runtime environment.

        Detection order:
        1. Explicit override via VIBE_MODE environment variable
        2. Steward protocol (if .steward/active_session.json exists)
        3. TTY check (sys.stdin.isatty())
        4. Default to HEADLESS (safe fallback)

        Returns:
            InterfaceMode: The detected mode (INTERACTIVE, HEADLESS, or STEWARD)
        """
        # 1. Check for explicit override
        vibe_mode = os.environ.get("VIBE_MODE", "").lower()
        if vibe_mode == "headless":
            return InterfaceMode.HEADLESS
        if vibe_mode == "interactive":
            return InterfaceMode.INTERACTIVE
        if vibe_mode == "steward":
            return InterfaceMode.STEWARD

        # 2. Check for Steward protocol (future proofing for multi-agent)
        if os.path.exists(".steward/active_session.json"):
            return InterfaceMode.STEWARD

        # 3. The physics: Is stdin connected to a terminal?
        if sys.stdin.isatty():
            return InterfaceMode.INTERACTIVE

        # 4. Default fallback (safe for CI, pipes, automation)
        return InterfaceMode.HEADLESS

    @staticmethod
    def is_interactive() -> bool:
        """Check if running in interactive mode."""
        return InterfaceManager.detect_mode() == InterfaceMode.INTERACTIVE

    @staticmethod
    def is_headless() -> bool:
        """Check if running in headless mode."""
        return InterfaceManager.detect_mode() == InterfaceMode.HEADLESS

    @staticmethod
    def is_steward() -> bool:
        """Check if running in steward mode."""
        return InterfaceManager.detect_mode() == InterfaceMode.STEWARD
