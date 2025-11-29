"""Task archival functionality."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .models import Task, TaskStatus


class TaskArchive:
    """Manages task archival."""

    def __init__(self, archive_path: Path):
        """
        Initialize task archive.

        Args:
            archive_path: Path to archive directory
        """
        self.archive_path = Path(archive_path)
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def archive_task(self, task: Task) -> bool:
        """
        Archive a completed task.

        Args:
            task: Task to archive

        Returns:
            True if archived successfully
        """
        # Update status to ARCHIVED
        task.status = TaskStatus.ARCHIVED

        # Write to archive file
        archive_file = self.archive_path / f"{task.id}.json"

        try:
            archive_file.write_text(json.dumps(task.to_dict(), indent=2))
            return True
        except Exception as e:
            print(f"Error archiving task {task.id}: {e}")
            return False

    def get_archived_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all archived tasks.

        Returns:
            List of archived task dictionaries
        """
        archived = []

        for task_file in self.archive_path.glob("*.json"):
            try:
                task_data = json.loads(task_file.read_text())
                archived.append(task_data)
            except Exception as e:
                print(f"Error reading archived task {task_file}: {e}")

        return archived

    def restore_task(self, task_id: str) -> Task:
        """
        Restore a task from archive.

        Args:
            task_id: ID of task to restore

        Returns:
            Restored task or None
        """
        archive_file = self.archive_path / f"{task_id}.json"

        if not archive_file.exists():
            return None

        try:
            task_data = json.loads(archive_file.read_text())
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data.get("description", ""),
                status=TaskStatus(task_data.get("status", "PENDING")),
                priority=task_data.get("priority", 0),
                assignee=task_data.get("assignee"),
                tags=task_data.get("tags", []),
            )
            return task
        except Exception as e:
            print(f"Error restoring task {task_id}: {e}")
            return None

    def purge_archive(self, older_than_days: int = 90) -> int:
        """
        Purge archived tasks older than specified days.

        Args:
            older_than_days: Archive tasks older than this many days

        Returns:
            Number of tasks purged
        """
        purged = 0
        threshold = datetime.now().timestamp() - (older_than_days * 86400)

        for task_file in self.archive_path.glob("*.json"):
            try:
                if task_file.stat().st_mtime < threshold:
                    task_file.unlink()
                    purged += 1
            except Exception as e:
                print(f"Error purging {task_file}: {e}")

        return purged
