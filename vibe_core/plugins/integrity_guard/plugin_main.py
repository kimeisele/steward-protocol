"""
IntegrityGuardPlugin - The Law of the Land (VEDA-4 Compliant)

Enforces architectural standards and system health at boot time.
If the Law is violated, the Kernel is refused sanction.
"""

import logging
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("INTEGRITY_GUARD")

class IntegrityGuardPlugin(KernelPlugin):
    """
    Sovereign Integrity Guard Aditya.
    
    Enforces the 'Law of the Land' (Sthula integrity and life force tests).
    """

    @property
    def plugin_id(self) -> str:
        return "integrity_guard"

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        SHABDA: Sanctioning the Kernel boot.
        """
        if getattr(kernel, "_test_mode", False):
            logger.info("🧪 IntegrityGuard: Test mode - bypassing enforcement.")
            return HookResult.ok()

        # 1. PRATYAYA: Check conditions
        if config and not config.get("enabled", True):
            logger.info("⚖️  IntegrityGuard: Enforcement disabled by config.")
            return HookResult.ok()

        logger.info("⚖️  IntegrityGuard: Enforcing Law of the Land...")

        try:
            # 2. KARMA: Execute enforcement
            self._enforce_standard(kernel)
            logger.info("⚖️  IntegrityGuard: Law verified. Kernel sanctioned.")
            return HookResult.ok()

        except Exception as e:
            logger.critical(f"🚫 INTEGRITY VETO: {e}")
            logger.critical("   The Law has been violated. Sanction denied.")
            # Hard exit - The Kernel cannot exist without the Law
            sys.exit(1)

    def _enforce_standard(self, kernel: "RealVibeKernel") -> None:
        """Run standard checks (lint, fast tests)."""
        
        # 1. Lint Check
        logger.info("   - Checking Sthula integrity (Lint)...")
        cmd_lint = [sys.executable, "-m", "ruff", "check", "vibe_core", "--select", "F,E9"]
        res_lint = subprocess.run(cmd_lint, capture_output=True, text=True)
        if res_lint.returncode != 0:
            logger.error(f"Lint Violation Output:\n{res_lint.stdout}")
            raise RuntimeError("Critical lint violations detected in vibe_core.")

                # 2. Smoke Test

                logger.info("   - Verifying Life Force (Smoke Tests)...")

                # Pass VIBE_NO_LOCK to sub-tests to avoid Ouroboros lock collision

                test_env = os.environ.copy()

                test_env["VIBE_NO_LOCK"] = "1"

                test_env["VIBE_NO_GIT_COMMIT"] = "1"

                

                cmd_test = [sys.executable, "-m", "pytest", "-m", "fast", "--tb=short", "--maxfail=1"]

                res_test = subprocess.run(cmd_test, capture_output=True, text=True, env=test_env)

                if res_test.returncode != 0:

                    logger.error(f"Test Failure Output:\n{res_test.stdout}")

                    raise RuntimeError("Fundamental system tests failed.")

        