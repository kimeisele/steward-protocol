"""
IDENTITY COMMAND - BRAHMA's Creation
=====================================

MAHAJANA: BRAHMA (The Creator)
OPCODE: LOAD_ROOT (Position 1)
PHASE: WAKE

WHY BRAHMA?
- Brahma creates the universe from the root (lotus from Vishnu's navel)
- He establishes identity and lineage
- LOAD_ROOT is about loading the fundamental identity/config
- Brahma creates the root from which all else springs

MANTRA WORD: HARE (Position 1)
"Hare establishes the root identity"

LOAD_ROOT = Load the root configuration and identity.
Brahma creates, Brahma identifies, Brahma roots.

Usage:
    naga identity                 # Show current identity
    naga identity --config        # Show loaded configuration
    naga identity --lineage       # Show project lineage
    naga identity --root          # Show root paths
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x79a4fa88"  # GenesisByte: parampara % 37 == 0

import os
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.LOAD_ROOT,
    name="identity",
    help_text="Load root identity and config (BRAHMA's creation - WAKE phase)",
)
class IdentityCommand(NagaCommandBase):
    """
    Identity command implementation.

    BRAHMA loads:
    - Project identity (name, version)
    - Root configuration
    - Lineage information
    - Path structure

    The Creator establishes what IS.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute identity command.

        Args:
            args: Command arguments
                --config: Show loaded configuration
                --lineage: Show project lineage
                --root: Show root paths

        Returns:
            NagaCommandResult with identity information
        """
        # Parse flags
        show_config = "--config" in args
        show_lineage = "--lineage" in args
        show_root = "--root" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "brahma"),
            ("opcode", "LOAD_ROOT"),
            ("phase", "wake"),
            ("position", "1"),
        ]

        output_parts.append("[BRAHMA] Root Identity")
        output_parts.append("=" * 50)

        # Always show basic identity
        identity = self._get_identity()
        output_parts.append("")
        output_parts.append(f"  Project:     {identity['name']}")
        output_parts.append(f"  Version:     {identity['version']}")
        output_parts.append(f"  Root:        {identity['root']}")
        data.append(("project", identity["name"]))
        data.append(("version", identity["version"]))

        # Show config
        if show_config:
            config = self._get_config()
            output_parts.append("")
            output_parts.append("  Configuration:")
            for key, value in config.items():
                output_parts.append(f"    {key}: {value}")

        # Show lineage
        if show_lineage:
            lineage = self._get_lineage()
            output_parts.append("")
            output_parts.append("  Lineage (Brahma's Creation):")
            for item in lineage:
                output_parts.append(f"    {item}")

        # Show root paths
        if show_root:
            roots = self._get_root_paths()
            output_parts.append("")
            output_parts.append("  Root Paths:")
            for name, path in roots.items():
                exists = "✓" if Path(path).exists() else "✗"
                output_parts.append(f"    {exists} {name}: {path}")

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("LOAD_ROOT: Identity established")

        return self.success("\n".join(output_parts), data=tuple(data))

    def _get_identity(self) -> dict:
        """Get project identity."""
        cwd = Path.cwd()

        # Try to find pyproject.toml
        pyproject = cwd / "pyproject.toml"
        name = "unknown"
        version = "0.0.0"

        if pyproject.exists():
            try:
                content = pyproject.read_text()
                for line in content.split("\n"):
                    if line.startswith("name"):
                        name = line.split("=")[1].strip().strip("\"'")
                    if line.startswith("version"):
                        version = line.split("=")[1].strip().strip("\"'")
            except Exception:
                pass

        return {
            "name": name,
            "version": version,
            "root": str(cwd),
        }

    def _get_config(self) -> dict:
        """Get loaded configuration."""
        config = {}

        # Check for common config files
        cwd = Path.cwd()
        config_files = [
            "pyproject.toml",
            ".vibe/config.yaml",
            ".env",
        ]

        for cf in config_files:
            path = cwd / cf
            config[cf] = "loaded" if path.exists() else "not found"

        # Environment
        config["VIBE_ENV"] = os.environ.get("VIBE_ENV", "development")

        return config

    def _get_lineage(self) -> list:
        """Get project lineage."""
        lineage = []

        # Check git for origin
        try:
            import subprocess

            result = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=Path.cwd(), timeout=5
            )
            if result.returncode == 0:
                lineage.append(f"Origin: {result.stdout.strip()}")
        except Exception:
            lineage.append("Origin: (not a git repo)")

        # Check for vibe ancestry
        vibe_dir = Path.cwd() / ".vibe"
        if vibe_dir.exists():
            lineage.append("Ancestry: .vibe directory present")
            lineage.append("Protocol: Steward Protocol v1")
        else:
            lineage.append("Ancestry: No .vibe lineage")

        return lineage

    def _get_root_paths(self) -> dict:
        """Get important root paths."""
        cwd = Path.cwd()

        return {
            "project_root": str(cwd),
            "vibe_core": str(cwd / "vibe_core"),
            "protocols": str(cwd / "vibe_core" / "protocols"),
            "tests": str(cwd / "tests"),
            "config": str(cwd / ".vibe"),
        }


# Export for direct import
__all__ = ["IdentityCommand"]
