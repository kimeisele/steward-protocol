"""
ARCH-064: KernelOracle - Single Source of Truth for System Capabilities

The Oracle is the **semantic backbone** of the system.
It provides deterministic, factual information about what the kernel can do.

This is not a suggestion, not a guess, not an LLM hallucination.
This is **The Truth** - read directly from kernel registries.

Key Design:
- Decoupled from CLI (not a print function)
- Structured data (dict) for semantic consumption
- Formatted text for human display
- Injected into Steward's system prompt (ARCH-064)
- Interface-agnostic (works for CLI, API, Voice)

Usage:
    oracle = KernelOracle(kernel)

    # For CLI display
    text = oracle.get_help_text()
    print(text)

    # For Steward's cortex (system prompt injection)
    capabilities = oracle.get_system_capabilities()
    # capabilities = {
    #     "cartridges": [...],
    #     "tools": [...],
    #     "meta_commands": [...]
    # }

Version: 1.0 (ARCH-064)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from vibe_core.cartridges.registry import get_default_cartridge_registry
from vibe_core.kernel import VibeKernel

logger = logging.getLogger(__name__)


class KernelOracle:
    """
    The Kernel Oracle: Single source of truth for system capabilities.

    Reads directly from kernel registries and provides:
    1. Structured capability data (for Steward's system prompt)
    2. Formatted help text (for CLI display)
    3. Metadata about cartridges, tools, commands

    This is the **semantic bridge** between code and language model.
    The Steward consumes this to know what it can actually do.
    """

    def __init__(self, kernel: VibeKernel, vibe_root: Path | None = None):
        """
        Initialize the Oracle with kernel reference.

        Args:
            kernel: Booted VibeKernel instance
            vibe_root: Path to vibe-agency root (for cartridge discovery)
        """
        self.kernel = kernel
        self.vibe_root = vibe_root or Path.cwd()

    # =========================================================================
    # DATA RETRIEVAL METHODS (Structured)
    # =========================================================================

    def get_cartridges(self) -> List[Dict[str, str]]:
        """
        Get list of installed cartridges with descriptions.

        Returns:
            List of dicts: [{"name": "steward", "description": "..."}]
        """
        cartridges = []

        try:
            cartridge_registry = get_default_cartridge_registry(self.vibe_root)
            cartridge_names = cartridge_registry.get_cartridge_names()

            for cartridge_name in cartridge_names:
                try:
                    cartridge = cartridge_registry.get_cartridge(cartridge_name)
                    spec = cartridge.get_spec()
                    cartridges.append(
                        {
                            "name": cartridge_name,
                            "description": spec.description,
                        }
                    )
                except Exception as e:
                    logger.debug(f"Error loading cartridge {cartridge_name}: {e}")
                    cartridges.append(
                        {
                            "name": cartridge_name,
                            "description": "(Unable to load)",
                        }
                    )

        except Exception as e:
            logger.debug(f"Error loading cartridge registry: {e}")

        return cartridges

    def get_tools(self) -> List[str]:
        """
        Get list of available tools.

        Returns:
            List of tool names: ["read_file", "write_file", ...]
        """
        tools = []

        try:
            operator = self.kernel.agent_registry.get("vibe-operator")
            if operator and hasattr(operator, "tool_registry"):
                tools = sorted(operator.tool_registry.list_tools())
        except Exception as e:
            logger.debug(f"Error accessing tool registry: {e}")

        return tools

    def get_meta_commands(self) -> List[Dict[str, str]]:
        """
        Get list of meta-commands (built-in commands).

        Returns:
            List of dicts: [{"command": "help", "description": "..."}]
        """
        return [
            {
                "command": "help, /help, ?",
                "description": "Show kernel help (offline, works always)",
            },
            {"command": "exit, quit, q", "description": "Shut down the operator"},
            {
                "command": "status",
                "description": "Show system status and agent registry",
            },
            {
                "command": "snapshot",
                "description": "Generate system introspection snapshot",
            },
            {"command": "task add <desc>", "description": "Add a task to your agenda"},
            {
                "command": "task list [status]",
                "description": "List tasks (pending, completed, all)",
            },
            {
                "command": "task complete <desc>",
                "description": "Mark task as complete",
            },
        ]

    def get_system_capabilities(self) -> Dict[str, Any]:
        """
        Get complete system capabilities as structured data.

        This is the **semantic payload** injected into the Steward's
        system prompt. It tells the LLM exactly what it can do.

        Returns:
            Dict with three keys:
            - cartridges: List of installed cartridges
            - tools: List of available tools
            - meta_commands: List of built-in commands
        """
        return {
            "cartridges": self.get_cartridges(),
            "tools": self.get_tools(),
            "meta_commands": self.get_meta_commands(),
        }

    # =========================================================================
    # TEXT FORMATTING METHODS (For Human Display)
    # =========================================================================

    def get_help_text(self) -> str:
        """
        Get formatted help text (for CLI display).

        This is what the user sees when they type 'help'.
        It's generated from the same data as the system prompt injection.

        Returns:
            Formatted help text as string
        """
        lines = []

        # Header (matches HUD styling)
        lines.append("")
        lines.append("─" * 70)
        lines.append("🛡️  KERNEL HELP (ARCH-063/064: Kernel Oracle)")
        lines.append("─" * 70)
        lines.append("")

        # SECTION 1: Cartridges
        lines.append("📦 INSTALLED CARTRIDGES:\n")
        cartridges = self.get_cartridges()
        if cartridges:
            for cartridge in cartridges:
                lines.append(f"   • {cartridge['name'].upper()}: {cartridge['description']}")
        else:
            lines.append("   (No cartridges registered)")
        lines.append("")

        # SECTION 2: Tools
        lines.append("🔧 AVAILABLE TOOLS:\n")
        tools = self.get_tools()
        if tools:
            for tool_name in tools:
                lines.append(f"   • {tool_name}")
        else:
            lines.append("   (No tools registered)")
        lines.append("")

        # SECTION 3: Meta Commands
        lines.append("⚡ META COMMANDS:\n")
        meta_commands = self.get_meta_commands()
        for cmd in meta_commands:
            lines.append(f"   • {cmd['command']:<20} → {cmd['description']}")

        # Footer
        lines.append("")
        lines.append("─" * 70)
        lines.append("")
        lines.append("💡 NATURAL LANGUAGE: For conversational help, just ask!")
        lines.append("   Examples: 'What can I do?', 'How do I build something?', etc.")
        lines.append("")
        lines.append("─" * 70)
        lines.append("")

        return "\n".join(lines)

    def get_cortex_text(self) -> str:
        """
        Get text formatted for Steward's system prompt injection.

        This is what the LLM sees in its system prompt.
        It's the same truth as CLI help, but formatted for semantic consumption.

        Returns:
            Formatted capabilities text for prompt injection
        """
        lines = [
            "## KERNEL CAPABILITIES (Ground Truth)\n",
            "The following represents the ACTUAL capabilities of your system.",
            "Quote these when users ask 'What can I do?' or similar questions.",
            "Do not hallucinate features not listed here.\n",
        ]

        # Cartridges
        lines.append("### Available Cartridges:")
        cartridges = self.get_cartridges()
        if cartridges:
            for cart in cartridges:
                lines.append(f"- **{cart['name']}**: {cart['description']}")
        else:
            lines.append("- (No cartridges registered)")
        lines.append("")

        # Tools
        lines.append("### Available Tools:")
        tools = self.get_tools()
        if tools:
            for tool in tools:
                lines.append(f"- `{tool}`")
        else:
            lines.append("- (No tools registered)")
        lines.append("")

        # Meta Commands
        lines.append("### Meta-Commands:")
        meta_commands = self.get_meta_commands()
        for cmd in meta_commands:
            lines.append(f"- **{cmd['command']}**: {cmd['description']}")
        lines.append("")

        lines.append(
            "---\n"
            "When users ask about capabilities, reference this section explicitly.\n"
            "Never invent features not listed above."
        )

        return "\n".join(lines)


# ============================================================================
# Singleton convenience function
# ============================================================================

_default_oracle: KernelOracle | None = None


def get_kernel_oracle(kernel: VibeKernel, vibe_root: Path | None = None) -> KernelOracle:
    """
    Get or create the default KernelOracle instance.

    Args:
        kernel: Booted VibeKernel instance
        vibe_root: Path to vibe-agency root

    Returns:
        KernelOracle instance
    """
    global _default_oracle
    if _default_oracle is None:
        _default_oracle = KernelOracle(kernel, vibe_root)
    return _default_oracle


__all__ = ["KernelOracle", "get_kernel_oracle"]
