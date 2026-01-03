"""
Shuddhi Log Monitor - The Passive Guardian of GAD-000.

Scans the system journal for errors and creates healing tasks.
This bridges the gap between 'Log Reality' and 'Managed Action'.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.protocols.task import TaskProtocol

logger = logging.getLogger("SHUDDHI.LOG")


class LogMonitor:
    def __init__(self, journal_path: Path, task_service: TaskProtocol):
        self.journal_path = journal_path
        self.task_service = task_service
        self._error_patterns = [
            {
                "id": "import_error",
                "regex": r"ImportError: cannot import name '(.+?)' from '(.+?)'",
                "rule": "import_fixer",
            },
            {
                "id": "name_error",
                "regex": r"NameError: name '(.+?)' is not defined",
                "rule": "import_fixer",  # Often missing imports
            },
        ]

    def scan_and_task(self) -> int:
        """Scans the journal and creates tasks for known error patterns."""
        if not self.journal_path.exists():
            return 0

        created_count = 0
        try:
            # Read last N lines of journal
            lines = self.journal_path.read_text().splitlines()[-100:]

            for line in lines:
                for pattern in self._error_patterns:
                    match = re.search(pattern["regex"], line)
                    if match:
                        error_detail = match.group(0)
                        title = f"AUTO-HEAL: {pattern['id']}"

                        # Check if task already exists to avoid spamming
                        existing = [t for t in self.task_service.list_tasks() if t.title == title]
                        if not existing:
                            self.task_service.add_task(
                                title=title,
                                description=f"Log Monitor detected a system error:\n{error_detail}\nSuggested Rule: {pattern['rule']}",
                                priority=90,  # High priority for boot errors
                                assigned_agent="engineer",
                            )
                            logger.info(f"🚨 LogMonitor created task: {title}")
                            created_count += 1

        except Exception as e:
            logger.error(f"Failed to scan logs: {e}")

        return created_count
