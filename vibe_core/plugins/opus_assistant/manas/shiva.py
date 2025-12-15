"""
SHIVA - The Intent Lifecycle Manager & Destroyer of Stale Thoughts.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ShivaLifecycleManager:
    """
    Shiva manages the lifecycle of thoughts (intents).
    He checks 'Git Truth' to see if intents are already fulfilled.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def sweep_and_archive(self, intent_buffer: List[Any]) -> int:
        """
        Scans the buffer for pending intents that are already fulfilled in reality.
        Returns the number of intents archived.
        """
        archived_count = 0

        for entry in intent_buffer:
            # Handle both object (with .status) and dict access for robustness
            if hasattr(entry, "status"):
                status = entry.status
            else:
                status = entry.get("status")

            if status != "pending":
                continue

            # Handle both object and dict for intent
            if hasattr(entry, "intent"):
                intent = entry.intent
            else:
                intent = entry.get("intent")

            if self._is_fulfilled_externally(intent):
                title = getattr(intent, "title", intent.get("title", "Unknown"))
                logger.info(f"🔱 SHIVA: Intent '{title}' is already fulfilled. Archiving.")

                if hasattr(entry, "status"):
                    entry.status = "fulfilled_externally"
                    entry.execution_result = {"source": "Shiva", "reason": "Reality check passed"}
                else:
                    entry["status"] = "fulfilled_externally"
                    entry["execution_result"] = {"source": "Shiva", "reason": "Reality check passed"}

                archived_count += 1

        return archived_count

    def _is_fulfilled_externally(self, intent: Any) -> bool:
        """Check if reality matches the intent."""

        # Safe attribute access
        intent_type = getattr(intent, "intent_type", intent.get("intent_type"))
        params = getattr(intent, "params", intent.get("params", {}))
        intent_id = getattr(intent, "id", intent.get("id"))
        title = getattr(intent, "title", intent.get("title", ""))

        # CASE 1: Missing Tests (semantic_gap_test)
        if intent_type == "semantic_gap_test":
            missing_files = params.get("untested_files", [])
            if not missing_files:
                return True  # Nothing to test? Done.

            # Check if tests exist now
            all_exist = True
            for f in missing_files:
                # Naive check: does test_{f} exist in tests/manas/ or plugin tests?
                base_name = f.replace(".py", "")
                test_name = f"test_{base_name}.py"

                # Check common locations (adjust based on project structure)
                possible_paths = [
                    self.project_root / "tests" / "manas" / test_name,
                    self.project_root / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "tests" / test_name,
                    self.project_root / "tests" / "unit" / test_name,
                ]

                if not any(p.exists() for p in possible_paths):
                    # logger.debug(f"Shiva: Still missing test for {f}")
                    all_exist = False
                    break

            return all_exist

        # CASE 2: Pending Commits (manas_0001)
        if intent_id == "manas_0001" or "commit" in title.lower():
            # If git status is clean, this is done.
            # Simpler: If we just ran a maintenance commit, assume these are stale.
            # For now, let's not auto-close generic commits without git check,
            # but we can close specific IDs if we know we fixed them.
            pass

        return False
