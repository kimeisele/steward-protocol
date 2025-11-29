"""Data export engine for tasks."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from .models import Task


class ExportEngine:
    """Exports task data in various formats."""

    @staticmethod
    def export_to_json(tasks: Dict[str, Task], output_path: Path) -> bool:
        """
        Export tasks to JSON.

        Args:
            tasks: Dictionary of tasks
            output_path: Path to write JSON file

        Returns:
            True if successful
        """
        try:
            tasks_data = {task_id: task.to_dict() for task_id, task in tasks.items()}
            output_path.write_text(json.dumps(tasks_data, indent=2))
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    @staticmethod
    def export_to_csv(tasks: Dict[str, Task], output_path: Path) -> bool:
        """
        Export tasks to CSV.

        Args:
            tasks: Dictionary of tasks
            output_path: Path to write CSV file

        Returns:
            True if successful
        """
        try:
            with open(output_path, "w", newline="") as f:
                if not tasks:
                    return True

                # Get first task to determine fields
                first_task = next(iter(tasks.values()))
                fieldnames = list(first_task.to_dict().keys())

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for task in tasks.values():
                    writer.writerow(task.to_dict())

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    @staticmethod
    def export_to_markdown(tasks: Dict[str, Task], output_path: Path) -> bool:
        """
        Export tasks to Markdown.

        Args:
            tasks: Dictionary of tasks
            output_path: Path to write Markdown file

        Returns:
            True if successful
        """
        try:
            lines = ["# Task Export\n"]

            # Group by status
            by_status = {}
            for task in tasks.values():
                status = task.status.value
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(task)

            # Write sections
            for status in sorted(by_status.keys()):
                lines.append(f"\n## {status}\n")
                for task in sorted(by_status[status], key=lambda t: t.priority, reverse=True):
                    lines.append(f"- **{task.title}** (P{task.priority})")
                    if task.description:
                        lines.append(f"  - {task.description}")
                    if task.tags:
                        lines.append(f"  - Tags: {', '.join(task.tags)}")

            output_path.write_text("\n".join(lines))
            return True
        except Exception as e:
            print(f"Error exporting to Markdown: {e}")
            return False

    @staticmethod
    def export_summary(tasks: Dict[str, Task]) -> Dict[str, Any]:
        """
        Get a summary of task statistics.

        Args:
            tasks: Dictionary of tasks

        Returns:
            Summary statistics dictionary
        """
        by_status = {}
        total_priority = 0

        for task in tasks.values():
            status = task.status.value
            by_status[status] = by_status.get(status, 0) + 1
            total_priority += task.priority

        return {
            "total_tasks": len(tasks),
            "by_status": by_status,
            "avg_priority": total_priority / len(tasks) if tasks else 0,
        }
