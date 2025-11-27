"""
Agenda Management Tools for vibe-agency OS (ARCH-045)

Provides tools for managing the backlog/agenda system.
These tools allow agents to add, list, and complete tasks in the persistent backlog.

The backlog is stored as BACKLOG.md in the workspace directory for human readability
and persistence across sessions.
"""

import logging
from pathlib import Path
from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger(__name__)

# Path to the backlog file
BACKLOG_PATH = Path("workspace/BACKLOG.md")


class AddTaskTool(Tool):
    """
    Tool for adding a task to the agenda/backlog.

    Allows agents to quickly record tasks that need to be done,
    with priority level and optional archival.

    Example:
        >>> tool = AddTaskTool()
        >>> result = tool.execute({
        ...     "description": "Fix Phoenix Config",
        ...     "priority": "HIGH"
        ... })
    """

    @property
    def name(self) -> str:
        return "add_task"

    @property
    def description(self) -> str:
        return "Add a task to the agenda/backlog with a priority level"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "description": {
                "type": "string",
                "required": True,
                "description": "Task description (brief but clear)",
            },
            "priority": {
                "type": "string",
                "required": False,
                "description": "Priority level: HIGH, MEDIUM, LOW (default: MEDIUM)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "description" not in parameters:
            raise ValueError("Missing required parameter: description")

        description = parameters["description"]
        if not isinstance(description, str):
            raise TypeError(f"description must be a string, got {type(description).__name__}")

        if not description.strip():
            raise ValueError("description cannot be empty")

        if "priority" in parameters:
            priority = parameters["priority"]
            if not isinstance(priority, str):
                raise TypeError(f"priority must be a string, got {type(priority).__name__}")

            valid_priorities = ["HIGH", "MEDIUM", "LOW"]
            if priority.upper() not in valid_priorities:
                raise ValueError(f"priority must be one of {valid_priorities}, got {priority}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute task addition.

        Appends a new task to the Outstanding Tasks section of BACKLOG.md.

        Args:
            parameters: {
                "description": "Task description",
                "priority": "HIGH|MEDIUM|LOW" (optional, default: MEDIUM)
            }

        Returns:
            ToolResult with success status
        """
        try:
            description = parameters["description"].strip()
            priority = parameters.get("priority", "MEDIUM").upper()

            # Ensure backlog file exists
            if not BACKLOG_PATH.exists():
                logger.warning(f"Backlog file not found at {BACKLOG_PATH}, creating it")
                BACKLOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                BACKLOG_PATH.write_text(
                    "# VIBE AGENCY BACKLOG\n\n"
                    "## Outstanding Tasks\n\n"
                    "## Completed Tasks\n\n"
                    "*(Archive of completed work)*\n"
                )

            # Read current backlog
            content = BACKLOG_PATH.read_text()

            # Find the Outstanding Tasks section
            outstanding_idx = content.find("## Outstanding Tasks")
            completed_idx = content.find("## Completed Tasks")

            if outstanding_idx == -1 or completed_idx == -1:
                return ToolResult(
                    success=False,
                    error="Invalid BACKLOG.md format: missing Outstanding/Completed sections",
                )

            # Extract the section between Outstanding Tasks and Completed Tasks
            before_outstanding = content[:outstanding_idx]
            outstanding_section = content[
                outstanding_idx + len("## Outstanding Tasks") : completed_idx
            ]
            after_completed = content[completed_idx:]

            # Add new task to outstanding section
            new_task_line = f"- [ ] [{priority}] {description}\n"

            # If outstanding section is empty or only whitespace, add at the beginning
            if outstanding_section.strip() == "":
                new_outstanding = "\n" + new_task_line + "\n"
            else:
                # Add before the Completed Tasks section
                new_outstanding = outstanding_section.rstrip() + "\n" + new_task_line + "\n"

            # Reconstruct the file
            new_content = (
                before_outstanding + "## Outstanding Tasks" + new_outstanding + after_completed
            )

            # Write back
            BACKLOG_PATH.write_text(new_content)

            logger.info(f"AddTaskTool: Added task '[{priority}] {description}' to backlog")
            return ToolResult(
                success=True,
                output=f"Task added: [{priority}] {description}",
            )

        except Exception as e:
            logger.error(f"AddTaskTool error: {e}")
            return ToolResult(success=False, error=str(e))


class ListTasksTool(Tool):
    """
    Tool for listing tasks from the backlog.

    Allows agents to review outstanding and completed tasks.

    Example:
        >>> tool = ListTasksTool()
        >>> result = tool.execute({"status": "pending"})
        >>> print(result.output)  # List of pending tasks
    """

    @property
    def name(self) -> str:
        return "list_tasks"

    @property
    def description(self) -> str:
        return "List tasks from the agenda/backlog (pending or completed)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "status": {
                "type": "string",
                "required": False,
                "description": "Task status: pending or completed (default: pending)",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "status" in parameters:
            status = parameters["status"]
            if not isinstance(status, str):
                raise TypeError(f"status must be a string, got {type(status).__name__}")

            valid_statuses = ["pending", "completed"]
            if status.lower() not in valid_statuses:
                raise ValueError(f"status must be one of {valid_statuses}, got {status}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute task listing.

        Reads the backlog and returns tasks matching the status filter.

        Args:
            parameters: {
                "status": "pending|completed" (optional, default: pending)
            }

        Returns:
            ToolResult with formatted task list
        """
        try:
            status = parameters.get("status", "pending").lower()

            # Read backlog
            if not BACKLOG_PATH.exists():
                return ToolResult(
                    success=True,
                    output="Backlog is empty (no tasks yet)",
                )

            content = BACKLOG_PATH.read_text()

            # Extract the appropriate section
            if status == "pending":
                outstanding_idx = content.find("## Outstanding Tasks")
                completed_idx = content.find("## Completed Tasks")

                if outstanding_idx == -1 or completed_idx == -1:
                    return ToolResult(
                        success=False,
                        error="Invalid BACKLOG.md format",
                    )

                section_content = content[
                    outstanding_idx + len("## Outstanding Tasks") : completed_idx
                ]
                section_title = "OUTSTANDING TASKS"

            else:  # completed
                completed_idx = content.find("## Completed Tasks")
                if completed_idx == -1:
                    return ToolResult(
                        success=False,
                        error="Invalid BACKLOG.md format",
                    )

                section_content = content[completed_idx + len("## Completed Tasks") :]
                section_title = "COMPLETED TASKS"

            # Parse tasks from markdown
            tasks = []
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith("- ["):
                    tasks.append(line)

            if not tasks:
                return ToolResult(
                    success=True,
                    output=f"{section_title}: None",
                )

            # Format output
            output = f"{section_title}:\n" + "\n".join(f"  {task}" for task in tasks)

            logger.info(f"ListTasksTool: Listed {len(tasks)} {status} tasks")
            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"ListTasksTool error: {e}")
            return ToolResult(success=False, error=str(e))


class CompleteTaskTool(Tool):
    """
    Tool for marking a task as completed.

    Moves a task from Outstanding to Completed section.

    Example:
        >>> tool = CompleteTaskTool()
        >>> result = tool.execute({
        ...     "task_description": "Fix Phoenix Config"
        ... })
    """

    @property
    def name(self) -> str:
        return "complete_task"

    @property
    def description(self) -> str:
        return "Mark a task as completed (move from pending to completed section)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "task_description": {
                "type": "string",
                "required": True,
                "description": "Description of the task to complete (partial match is OK)",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "task_description" not in parameters:
            raise ValueError("Missing required parameter: task_description")

        desc = parameters["task_description"]
        if not isinstance(desc, str):
            raise TypeError(f"task_description must be a string, got {type(desc).__name__}")

        if not desc.strip():
            raise ValueError("task_description cannot be empty")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute task completion.

        Finds and completes the task matching the description.

        Args:
            parameters: {
                "task_description": "Partial description of task to complete"
            }

        Returns:
            ToolResult with success status
        """
        try:
            search_term = parameters["task_description"].strip()

            # Read backlog
            if not BACKLOG_PATH.exists():
                return ToolResult(
                    success=False,
                    error="Backlog file not found",
                )

            content = BACKLOG_PATH.read_text()

            # Find the sections
            outstanding_idx = content.find("## Outstanding Tasks")
            completed_idx = content.find("## Completed Tasks")

            if outstanding_idx == -1 or completed_idx == -1:
                return ToolResult(
                    success=False,
                    error="Invalid BACKLOG.md format",
                )

            before_outstanding = content[:outstanding_idx]
            outstanding_section = content[
                outstanding_idx + len("## Outstanding Tasks") : completed_idx
            ]
            after_completed = content[completed_idx:]

            # Find and extract the task
            lines = outstanding_section.split("\n")
            found_task = None
            found_index = -1

            for i, line in enumerate(lines):
                if line.strip().startswith("- [ ]") and search_term.lower() in line.lower():
                    found_task = line
                    found_index = i
                    break

            if found_task is None:
                return ToolResult(
                    success=False,
                    error=f"Task matching '{search_term}' not found in outstanding tasks",
                )

            # Mark as completed (check the box)
            completed_task = found_task.replace("- [ ]", "- [x]", 1)

            # Remove from outstanding and add to completed
            new_outstanding_lines = lines[:found_index] + lines[found_index + 1 :]
            new_outstanding = "\n".join(new_outstanding_lines)

            # Add to completed section
            completed_lines = after_completed.split("\n")
            # Find the start of actual content in completed section (skip section header)
            insert_idx = 1  # After "## Completed Tasks"
            for i, line in enumerate(completed_lines):
                if line.strip() and not line.strip().startswith("*"):
                    insert_idx = i
                    break

            # Insert the completed task
            completed_lines.insert(insert_idx, completed_task)
            new_completed = "\n".join(completed_lines)

            # Reconstruct the file
            new_content = (
                before_outstanding + "## Outstanding Tasks" + new_outstanding + "\n" + new_completed
            )

            # Write back
            BACKLOG_PATH.write_text(new_content)

            logger.info(f"CompleteTaskTool: Marked task as completed: {found_task.strip()}")
            return ToolResult(
                success=True,
                output=f"Task completed: {found_task.strip()}",
            )

        except Exception as e:
            logger.error(f"CompleteTaskTool error: {e}")
            return ToolResult(success=False, error=str(e))
