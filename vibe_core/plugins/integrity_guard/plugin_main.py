"""
IntegrityGuardPlugin - The Law of the Land (VEDA-4 Compliant)

Enforces architectural standards and system health at boot time.
If the Law is violated, the Kernel is refused sanction.
"""

import logging
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.plugin_protocol import VibePlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("INTEGRITY_GUARD")

class IntegrityGuardPlugin(VibePlugin):
    """
    Sovereign Integrity Guard Aditya.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.plugin_id = "integrity_guard"
        self.config = config or {}
        # Priority is handled by the manifest (-100)

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        SHABDA: Sanctioning the Kernel boot.
        """
        if kernel._test_mode:
            logger.info("🧪 IntegrityGuard: Test mode - bypassing enforcement.")
            return

        # 1. PRATYAYA: Check conditions
        if not self.config.get("enabled", True):
            return

        logger.info("⚖️  IntegrityGuard: Enforcing Law of the Land...")

        try:
            # 2. KARMA: Execute enforcement
            self._enforce_standard(kernel)
            logger.info("⚖️  IntegrityGuard: Law verified. Kernel sanctioned.")

        except Exception as e:
            logger.critical(f"🚫 INTEGRITY VETO: {e}")
            logger.critical("   The Law has been violated. Sanction denied.")
            # Hard exit - The Kernel cannot exist without the Law
            sys.exit(1)

    def _enforce_standard(self, kernel: "RealVibeKernel") -> None:
        """Run standard checks (lint, fast tests)."""
        
        # In a real Bharat architecture, these would be separate Tools
        # But for this Aditya, we keep it contained.
        
        # 1. Lint Check
        logger.info("   - Checking Sthula integrity (Lint)...")
        # We only check vibe_core for boot-time speed
        cmd_lint = [sys.executable, "-m", "ruff", "check", "vibe_core", "--select", "F,E9"]
        res_lint = subprocess.run(cmd_lint, capture_output=True, text=True)
        if res_lint.returncode != 0:
            print(res_lint.stdout)
            raise RuntimeError("Critical lint violations detected in vibe_core.")

        # 2. Smoke Test
        logger.info("   - Verifying Life Force (Smoke Tests)...")
        cmd_test = [sys.executable, "-m", "pytest", "-m", "fast", "--tb=short"]
        res_test = subprocess.run(cmd_test, capture_output=True, text=True)
        if res_test.returncode != 0:
            print(res_test.stdout)
            raise RuntimeError("Fundamental system tests failed.")

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        pass

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        pass

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        pass
