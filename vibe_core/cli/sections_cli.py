"""
OPUS-307: Sections CLI

CLI interface for SectionService (Phoenix config sections).

Usage:
    steward sections list              # List all sections
    steward sections info <name>       # Show section details
"""

import logging
from pathlib import Path
from typing import List, Optional

from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.section_service import SectionService

logger = logging.getLogger("SECTIONS_CLI")


@register_cli
class SectionsCLI:
    """
    CLI for Section management via SectionService.

    OPUS-307: Unified section access.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="sections",
            description="Phoenix sections management (list, info)",
            domain="system",
            subcommands=["list", "info"],
            tags=["sections", "phoenix", "config"],
        )

    def __init__(self):
        """Initialize sections CLI."""
        self._service: Optional[SectionService] = None

    def _get_service(self) -> SectionService:
        """Get SectionService instance."""
        if self._service is None:
            self._service = SectionService.get_instance(Path.cwd())
            self._service.scan()
        return self._service

    def run(self, args: List[str]) -> int:
        """Execute sections command."""
        if not args:
            return self._cmd_list([])

        subcommand = args[0]
        sub_args = args[1:]

        commands = {
            "list": self._cmd_list,
            "info": self._cmd_info,
            "--help": self._cmd_help,
            "-h": self._cmd_help,
        }

        handler = commands.get(subcommand)
        if handler:
            return handler(sub_args)

        print(f"Unknown subcommand: {subcommand}")
        return self._cmd_help([])

    def _cmd_list(self, args: List[str]) -> int:
        """List all sections."""
        svc = self._get_service()
        sections = svc.list()

        print(f"\n{'=' * 60}")
        print(f"PHOENIX SECTIONS ({len(sections)} total)")
        print(f"{'=' * 60}\n")

        for section in sections:
            yaml_marker = "[YAML]" if section.loaded_from_yaml else "[DEFAULT]"
            print(f"  {section.section_id:<20} priority={section.priority:<3} {yaml_marker}")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_info(self, args: List[str]) -> int:
        """Show section details."""
        if not args:
            print("Usage: steward sections info <section_id>")
            return 1

        section_id = args[0]
        svc = self._get_service()
        section = svc.get(section_id)

        if not section:
            print(f"Section not found: {section_id}")
            return 1

        print(f"\n{'=' * 60}")
        print(f"SECTION: {section.section_id}")
        print(f"{'=' * 60}\n")
        print(f"  Priority:        {section.priority}")
        print(f"  Path:            {section.path}")
        print(f"  From YAML:       {section.loaded_from_yaml}")

        # Try to load instance for more details
        instance = svc.load(section_id)
        if instance:
            print(f"  Instance Type:   {type(instance).__name__}")
            if hasattr(instance, "to_dict"):
                data = instance.to_dict()
                print(f"  Config Keys:     {', '.join(data.keys())}")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_help(self, args: List[str]) -> int:
        """Show help."""
        print("""
Usage: steward sections <command> [args]

Commands:
  list              List all Phoenix config sections
  info <section_id> Show section details

Examples:
  steward sections list
  steward sections info kernel
  steward sections info llm
""")
        return 0
