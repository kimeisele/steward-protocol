"""Validation framework for tasks."""

from typing import Any, Callable, Dict, List

from .models import Task, TaskStatus


class ValidationError(Exception):
    """Raised when task validation fails."""

    pass


class ValidatorRegistry:
    """Registry for task validators."""

    def __init__(self):
        """Initialize validator registry."""
        self.validators: Dict[str, List[Callable]] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register default validators."""
        self.register("title", self._validate_title)
        self.register("status", self._validate_status)
        self.register("priority", self._validate_priority)

    def register(self, field: str, validator: Callable):
        """
        Register a validator for a field.

        Args:
            field: Field name to validate
            validator: Callable that takes value and raises ValidationError
        """
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)

    def validate_task(self, task: Task) -> bool:
        """
        Validate a task.

        Args:
            task: Task to validate

        Returns:
            True if valid

        Raises:
            ValidationError if invalid
        """
        # Validate title
        if "title" in self.validators:
            for validator in self.validators["title"]:
                validator(task.title)

        # Validate status
        if "status" in self.validators:
            for validator in self.validators["status"]:
                validator(task.status)

        # Validate priority
        if "priority" in self.validators:
            for validator in self.validators["priority"]:
                validator(task.priority)

        return True

    @staticmethod
    def _validate_title(title: str):
        """Validate task title."""
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty")
        if len(title) > 500:
            raise ValidationError("Task title cannot exceed 500 characters")

    @staticmethod
    def _validate_status(status: TaskStatus):
        """Validate task status."""
        if not isinstance(status, TaskStatus):
            raise ValidationError(f"Invalid status: {status}")

    @staticmethod
    def _validate_priority(priority: int):
        """Validate task priority."""
        if not isinstance(priority, int):
            raise ValidationError("Priority must be an integer")
        if priority < 0 or priority > 100:
            raise ValidationError("Priority must be between 0 and 100")
