"""
OPUS-082: Shiva Lifecycle Manager

"The Destroyer of Illusions"

Shiva manages the lifecycle of thoughts (intents) in MANAS:
- Detects when intents are fulfilled externally (by humans or other agents)
- Archives stale/expired intents
- Keeps the mind (MANAS) clean and focused

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    COGNITIVE KERNEL                          │
    │  ┌───────────────────┐  ┌───────────────────┐               │
    │  │  Intent Generator │  │  Shiva Lifecycle  │               │
    │  │  (Brahma)         │  │  (Destruction)    │               │
    │  │  Creates thoughts │  │  Cleans thoughts  │               │
    │  └───────────────────┘  └───────────────────┘               │
    │           │                      │                           │
    │           ▼                      ▼                           │
    │  ┌───────────────────────────────────────────┐              │
    │  │           INTENT BUFFER                    │              │
    │  │  pending → executed → archived             │              │
    │  │           ↘ fulfilled_externally → archived│              │
    │  └───────────────────────────────────────────┘              │
    └─────────────────────────────────────────────────────────────┘

Philosophy:
    A thought that no longer reflects reality is an illusion.
    Shiva destroys illusions, not truth.
    Git is Truth. If Git says "no changes", the "commit changes" thought is illusion.
"""

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .intent_generator import Intent

if TYPE_CHECKING:
    from .cognitive_kernel import CognitiveKernel

logger = logging.getLogger("MANAS.SHIVA")


@dataclass
class FulfillmentResult:
    """Result of checking if an intent was fulfilled externally."""

    fulfilled: bool
    reason: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class ShivaLifecycleManager:
    """
    Shiva - The Lifecycle Manager for MANAS intents.

    Responsibilities:
    1. Check if intents were fulfilled externally
    2. Sweep and archive stale intents
    3. Keep the intent buffer clean
    """

    def __init__(self, workspace: Path, config: Optional[Dict[str, Any]] = None):
        self._workspace = workspace
        self._config = config or {}
        self._kernel: Optional["CognitiveKernel"] = None
        logger.info(f"🕉️ Shiva: Lifecycle Manager initialized (config: {len(self._config)} keys)")

    def inject_kernel(self, kernel: "CognitiveKernel") -> None:
        """Inject the CognitiveKernel for access to intent buffer."""
        self._kernel = kernel
        logger.debug("Shiva: Kernel injected")

    def check_external_fulfillment(self, intent: Intent) -> FulfillmentResult:
        """
        Check if an intent was fulfilled by external work.

        This is Shiva's core function: detecting when reality has
        already satisfied an intent, making the intent an "illusion".

        Args:
            intent: The intent to check

        Returns:
            FulfillmentResult indicating if fulfilled and why
        """
        intent_type = intent.intent_type

        # Dispatch to specific checkers based on intent type
        if intent_type == "semantic_gap_test":
            return self._check_test_intent(intent)
        elif intent_type == "commit_pending_changes":
            return self._check_commit_intent(intent)
        elif intent_type == "ci_status_failure":
            return self._check_ci_status_intent(intent)
        elif intent_type == "update_documentation":
            return self._check_docs_intent(intent)
        else:
            # Unknown intent type - can't verify
            return FulfillmentResult(
                fulfilled=False,
                reason="unknown_intent_type",
                details={"intent_type": intent_type},
            )

    def _check_test_intent(self, intent: Intent) -> FulfillmentResult:
        """Check if test creation intent was fulfilled."""
        untested_files = intent.params.get("untested_files", [])
        tests_found = []

        for file in untested_files:
            # Look for test file in common locations
            test_paths = [
                self._workspace / "tests" / "manas" / f"test_{file}",
                self._workspace / "tests" / f"test_{file}",
                self._workspace / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "tests" / f"test_{file}",
            ]

            for test_path in test_paths:
                if test_path.exists():
                    tests_found.append(str(test_path))
                    break

        if tests_found:
            return FulfillmentResult(
                fulfilled=True,
                reason="test_file_exists",
                details={"tests_found": tests_found, "checked_files": untested_files},
            )

        return FulfillmentResult(
            fulfilled=False,
            reason="tests_not_found",
            details={"checked_files": untested_files},
        )

    def _check_commit_intent(self, intent: Intent) -> FulfillmentResult:
        """Check if commit intent was fulfilled (git is clean)."""
        if not self._git_has_changes():
            return FulfillmentResult(fulfilled=True, reason="git_clean", details={"status": "no_changes"})

        return FulfillmentResult(fulfilled=False, reason="git_has_changes", details={"status": "dirty"})

    def _check_ci_status_intent(self, intent: Intent) -> FulfillmentResult:
        """Check if CI status issue was resolved."""
        # For now, just check if kernel status is OK
        # In future, could check actual CI status via GitHub API
        return FulfillmentResult(
            fulfilled=False,
            reason="ci_status_not_verified",
            details={"note": "CI status checking not implemented yet"},
        )

    def _check_docs_intent(self, intent: Intent) -> FulfillmentResult:
        """Check if documentation intent was fulfilled."""
        target_file = intent.params.get("file")
        if target_file:
            doc_path = self._workspace / target_file
            if doc_path.exists():
                return FulfillmentResult(
                    fulfilled=True,
                    reason="doc_file_exists",
                    details={"file": str(doc_path)},
                )

        return FulfillmentResult(
            fulfilled=False,
            reason="doc_not_found",
            details={"target_file": target_file},
        )

    def _git_has_changes(self) -> bool:
        """Check if git working directory has uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self._workspace,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Shiva: Git status check failed: {e}")
            return True  # Assume dirty if can't check

    def sweep_stale_intents(self) -> int:
        """
        Sweep through intent buffer and archive fulfilled/stale intents.

        Returns:
            Number of intents archived
        """
        if not self._kernel:
            logger.warning("Shiva: No kernel injected, cannot sweep")
            return 0

        archived = 0

        # OPUS-174: Use _buffer (IntentBuffer), not _intent_buffer
        for entry in self._kernel._buffer:
            if entry.status != "pending":
                continue

            result = self.check_external_fulfillment(entry.intent)
            if result.fulfilled:
                entry.status = "fulfilled_externally"
                entry.execution_result = {
                    "shiva_fulfilled": True,
                    "reason": result.reason,
                    "details": result.details,
                }
                archived += 1
                logger.info(f"🕉️ Shiva: Archived '{entry.intent.title}' - {result.reason}")

        if archived > 0:
            # IntentBuffer.save() persists to disk
            self._kernel._buffer.save()
            logger.info(f"🕉️ Shiva: Swept {archived} fulfilled intents")

        return archived
