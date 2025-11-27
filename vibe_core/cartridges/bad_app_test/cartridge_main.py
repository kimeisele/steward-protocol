#!/usr/bin/env python3
"""
BadAppCartridge - Isolation Verification Test (ARCH-051)

This cartridge is intentionally broken to test that:
1. The Kernel isolates bad cartridges
2. The Kernel doesn't crash when a cartridge throws exceptions
3. The Kernel can gracefully handle and report failures

This is a PROOF-OF-CONCEPT that demonstrates enterprise stability.

WARNING: This is a test fixture. Do not use in production.
"""

import logging
from pathlib import Path

from vibe_core.cartridges.base import CartridgeBase

logger = logging.getLogger(__name__)


class BadAppCartridge(CartridgeBase):
    """
    A deliberately broken cartridge for isolation testing.

    This cartridge throws exceptions in various methods to prove that:
    - Kernel doesn't crash when loading a bad cartridge
    - Kernel isolates failures
    - Kernel reports problems gracefully
    """

    name = "bad_app_test"
    version = "0.0.1"
    description = "Broken test cartridge - verifies Kernel isolation"
    author = "Vibe Agency (Test)"

    def __init__(self, vibe_root: Path | None = None):
        """Initialize the bad app (intentionally throws during second phase)."""
        super().__init__(vibe_root=vibe_root)
        logger.warning("⚠️ BadAppCartridge loaded - This app is intentionally broken")

    def crash_on_demand(self) -> None:
        """
        Intentionally crash this cartridge.

        This method is called to verify kernel isolation.
        The kernel should catch this and isolate the cartridge.
        """
        logger.error("💥 BadAppCartridge is crashing intentionally")
        raise Exception(
            "BadAppCartridge intentional failure - This should be caught by Kernel isolation"
        )

    def crash_on_init(self) -> None:
        """Raise exception during initialization to test isolation."""
        raise RuntimeError("BadAppCartridge failed during initialization")

    def crash_on_execute(self) -> str:
        """Raise exception during execution to test isolation."""
        raise ValueError("BadAppCartridge failed during execution")

    def crash_with_division_by_zero(self) -> float:
        """Raise exception via division by zero."""
        return 1 / 0  # This will raise ZeroDivisionError

    def infinite_loop(self) -> None:
        """
        Start an infinite loop.
        Used to test timeout isolation (kernel should interrupt).
        """
        logger.warning("⚠️ BadAppCartridge starting infinite loop - should be interrupted")
        while True:
            pass  # Infinite loop

    def memory_leak(self) -> None:
        """Attempt to exhaust memory (kernel should isolate)."""
        large_list = []
        while True:
            large_list.append("x" * 1_000_000)  # Allocate ~1MB per iteration

    def corrupt_file(self) -> None:
        """
        Attempt to corrupt a system file.
        Kernel isolation should prevent this.
        """
        try:
            with open(self.vibe_root / ".vibe" / "state" / "active_mission.json", "w") as f:
                f.write("CORRUPTED BY BAD APP")
            logger.error("❌ BadAppCartridge corrupted a system file!")
        except Exception as e:
            logger.info(f"✅ File corruption prevented: {e}")

    def report_status(self) -> dict:
        """Report status (this should work even for bad cartridges)."""
        return {
            "name": self.name,
            "version": self.version,
            "status": "BROKEN",
            "warning": "This cartridge is intentionally broken for testing isolation",
        }


__all__ = ["BadAppCartridge"]
