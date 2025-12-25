"""
OPUS-307: Prompts CLI

CLI interface for PromptRegistry.

Usage:
    steward prompts list              # List all registered prompts
    steward prompts get <key>         # Show prompt content
    steward prompts info              # Show registry status
"""

import logging
from typing import List

from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.runtime.prompt_registry import PromptRegistry

logger = logging.getLogger("PROMPTS_CLI")


@register_cli
class PromptsCLI:
    """
    CLI for Prompt management via PromptRegistry.

    OPUS-307: Unified prompt access.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="prompts",
            description="Prompt registry management (list, get, info)",
            domain="system",
            subcommands=["list", "get", "info"],
            tags=["prompts", "llm", "system"],
        )

    def __init__(self):
        """Initialize prompts CLI."""
        # Ensure defaults are loaded
        PromptRegistry.initialize_defaults()

    def run(self, args: List[str]) -> int:
        """Execute prompts command."""
        if not args:
            return self._cmd_list([])

        subcommand = args[0]
        sub_args = args[1:]

        commands = {
            "list": self._cmd_list,
            "get": self._cmd_get,
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
        """List all registered prompts."""
        prompts = PromptRegistry._prompts

        print(f"\n{'=' * 60}")
        print(f"REGISTERED PROMPTS ({len(prompts)} total)")
        print(f"{'=' * 60}\n")

        if not prompts:
            print("  No prompts registered.")
        else:
            # Group by namespace
            grouped = {}
            for key in sorted(prompts.keys()):
                if "." in key:
                    namespace = key.split(".")[0]
                else:
                    namespace = "default"
                if namespace not in grouped:
                    grouped[namespace] = []
                grouped[namespace].append(key)

            for namespace in sorted(grouped.keys()):
                print(f"  [{namespace}]")
                for key in grouped[namespace]:
                    content = prompts[key]
                    chars = len(content)
                    preview = content[:50].replace("\n", " ")
                    print(f"    {key:<30} ({chars} chars) {preview}...")
                print()

        print(f"{'=' * 60}")
        return 0

    def _cmd_get(self, args: List[str]) -> int:
        """Show prompt content."""
        if not args:
            print("Usage: steward prompts get <key>")
            return 1

        key = args[0]

        try:
            prompt = PromptRegistry.get(key)
            print(f"\n{'=' * 60}")
            print(f"PROMPT: {key}")
            print(f"{'=' * 60}\n")
            print(prompt)
            print(f"\n{'=' * 60}")
            return 0
        except KeyError as e:
            print(f"Prompt not found: {key}")
            print(f"Available: {', '.join(PromptRegistry._prompts.keys())}")
            return 1

    def _cmd_info(self, args: List[str]) -> int:
        """Show registry status."""
        prompts = PromptRegistry._prompts
        guardian_loaded = PromptRegistry._guardian_directives_cache is not None

        print(f"\n{'=' * 60}")
        print("PROMPT REGISTRY STATUS")
        print(f"{'=' * 60}\n")
        print(f"  Registered prompts: {len(prompts)}")
        print(f"  Guardian directives: {'Loaded' if guardian_loaded else 'Not loaded'}")

        # Namespace breakdown
        namespaces = {}
        for key in prompts.keys():
            ns = key.split(".")[0] if "." in key else "default"
            namespaces[ns] = namespaces.get(ns, 0) + 1

        print("\n  Namespaces:")
        for ns, count in sorted(namespaces.items()):
            print(f"    {ns}: {count} prompts")

        # Total chars
        total_chars = sum(len(p) for p in prompts.values())
        print(f"\n  Total content: {total_chars:,} chars")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_help(self, args: List[str]) -> int:
        """Show help."""
        print("""
Usage: steward prompts <command> [args]

Commands:
  list              List all registered prompts
  get <key>         Show prompt content
  info              Show registry status

Examples:
  steward prompts list
  steward prompts get genesis.action
  steward prompts info
""")
        return 0
