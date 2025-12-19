#!/usr/bin/env python3
"""
SettingsSection Protocol - Plugin Architecture for SETTINGS.md Sections

Each section is self-contained:
- Renders its own markdown
- Parses its own commands
- Executes its own logic

This allows infinite scalability without modifying core code.

Usage:
    class ProviderSection(SettingsSection):
        @property
        def section_id(self) -> str:
            return "provider"

        @property
        def priority(self) -> int:
            return 10  # Lower = renders first

        def render(self, context: SectionContext) -> List[str]:
            return ["## 🔌 Provider Config", ...]

        def handles_command(self, key: str) -> bool:
            return key == "provider"

        def execute(self, key: str, value: str, context: SectionContext) -> SettingsResult:
            # Do the work
            return SettingsResult(success=True, message="Provider changed")
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SectionContext:
    """
    Context passed to sections for rendering and execution.

    Contains all data a section might need, without coupling to kernel.
    """

    # Kernel snapshot data
    kernel_status: str = "UNKNOWN"
    agent_count: int = 0
    queue_length: int = 0
    total_events: int = 0

    # Phoenix config data
    config: Dict[str, Any] = field(default_factory=dict)

    # Current settings state
    live_fire_enabled: bool = False
    provider_name: str = "unknown"
    provider_info: Dict[str, str] = field(default_factory=dict)

    # For command execution
    ledger_callback: Optional[Any] = None  # For audit logging


@dataclass
class SettingsResult:
    """Result of executing a settings command (OPUS-111: renamed from SettingsResult)."""

    success: bool
    message: str
    requires_restart: bool = False
    side_effects: Dict[str, Any] = field(default_factory=dict)


class SettingsSection(ABC):
    """
    Abstract base class for SETTINGS.md sections.

    Follows same pattern as KernelPlugin for consistency.
    Auto-discovered from vibe_core/settings/sections/
    """

    @property
    @abstractmethod
    def section_id(self) -> str:
        """Unique identifier for this section."""
        pass

    @property
    def priority(self) -> int:
        """
        Render priority (lower = renders first).

        Default sections:
        - 10: Provider
        - 20: Execution Mode
        - 50: Kernel Config
        - 100: Agent Registry
        """
        return 100

    @property
    def title(self) -> str:
        """Section title for markdown heading."""
        return f"## {self.section_id.title()}"

    @abstractmethod
    def render(self, context: SectionContext) -> List[str]:
        """
        Render this section as markdown lines.

        Args:
            context: Current settings context

        Returns:
            List of markdown lines
        """
        pass

    @abstractmethod
    def handles_command(self, key: str) -> bool:
        """
        Check if this section handles the given SET command key.

        Args:
            key: The command key (e.g., "provider", "mode")

        Returns:
            True if this section handles the command
        """
        pass

    @abstractmethod
    def execute(self, key: str, value: str, context: SectionContext) -> SettingsResult:
        """
        Execute a SET command.

        Args:
            key: The command key
            value: The command value
            context: Current settings context

        Returns:
            SettingsResult with success/failure and message
        """
        pass

    def validate(self, key: str, value: str) -> Optional[str]:
        """
        Validate a command value before execution.

        Args:
            key: The command key
            value: The value to validate

        Returns:
            Error message if invalid, None if valid
        """
        return None
