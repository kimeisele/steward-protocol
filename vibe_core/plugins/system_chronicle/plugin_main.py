"""
📜 SYSTEM CHRONICLE PLUGIN - The Memory Sealer

OPUS-091: Heartbeat Purification
Bridges PRANA pulse cycle with Chronicle Cartridge for automatic Git commits.

Philosophy:
"The pulse detects changes. Chronicle seals them in history."

This plugin runs during CLEANUP phase and:
1. Checks git status (are there changes?)
2. If dirty: Creates a signed commit via GitTools
3. Logs results for audit trail

NOTE: This plugin DELEGATES to ChronicleCartridge.GitTools.
No duplicated Git logic - we reuse what exists.
"""

import logging
from typing import TYPE_CHECKING, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult, PulsePhase

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SYSTEM_CHRONICLE_PLUGIN")


class SystemChroniclePlugin(KernelPlugin):
    """
    Bridge between PRANA pulse and Chronicle Git tooling.

    Runs during CLEANUP phase to seal repository history after heartbeat changes.
    """

    @property
    def plugin_id(self) -> str:
        return "system_chronicle"

    @property
    def pulse_phase(self) -> PulsePhase:
        """Run during CLEANUP phase (after all mutations applied)."""
        return PulsePhase.CLEANUP

    def on_pulse(self, kernel: "RealVibeKernel", transaction) -> HookResult:
        """
        Execute during CLEANUP phase of pulse cycle.

        Checks git status and creates a commit if there are changes.
        Uses GitTools from ChronicleCartridge (delegation pattern).

        Args:
            kernel: The kernel instance
            transaction: PulseTransaction for registering mutations

        Returns:
            HookResult with commit details if successful
        """
        try:
            # Import GitTools (from existing Chronicle system)
            from vibe_core.cartridges.system.chronicle.tools.git_tools import GitTools

            logger.info("📜 Chronicle: Checking repository status...")

            tools = GitTools()
            status = tools.get_status()

            if not status.get("success"):
                logger.warning("⚠️  Chronicle: Could not get git status")
                return HookResult.ok(data={"status": "skipped", "reason": "git_unavailable"})

            if not status.get("dirty"):
                logger.debug("📝 Chronicle: No changes to commit")
                return HookResult.ok(data={"status": "clean", "files_changed": []})

            # Git is dirty - create commit
            files_changed = status.get("files_changed", [])
            logger.info(f"📜 Chronicle: Found {len(files_changed)} changed files. Sealing history...")

            commit_result = tools.seal_history(
                message="🫀 Heartbeat Pulse: System auto-save",
                files=None,  # Commit all staged (or all modified if nothing staged)
                sign=True,  # Sign the commit
            )

            if commit_result.get("success"):
                commit_hash = commit_result.get("commit_hash", "unknown")[:8]
                logger.info(f"✅ Chronicle: History sealed ({commit_hash})")
                return HookResult.ok(
                    data={
                        "status": "committed",
                        "commit_hash": commit_hash,
                        "message": commit_result.get("message"),
                        "files": files_changed,
                    }
                )
            else:
                logger.warning(f"⚠️  Chronicle: Commit failed - {commit_result.get('error', 'unknown error')}")
                return HookResult.error(f"Commit failed: {commit_result.get('error')}")

        except ImportError as e:
            logger.warning(f"⚠️  Chronicle: GitTools not available ({e})")
            return HookResult.ok(data={"status": "skipped", "reason": "chronicle_unavailable"})

        except Exception as e:
            logger.error(f"❌ Chronicle: Unexpected error during pulse - {e}", exc_info=True)
            return HookResult.error(f"Pulse execution failed: {e}")
