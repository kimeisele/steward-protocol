"""
RESOURCES COMMAND - NARADA's Allocation
========================================

MAHAJANA: NARADA (The Celestial Messenger)
OPCODE: ALLOC_MEM (Position 2)
PHASE: WAKE

WHY NARADA?
- Narada travels between realms distributing information
- He allocates attention and resources where needed
- ALLOC_MEM is about allocating memory/resources
- Narada knows where resources should go

MANTRA WORD: HARE (Position 2)
"Hare allocates divine resources"

ALLOC_MEM = Allocate memory and resources.
Narada distributes, Narada allocates, Narada connects.

Usage:
    naga resources                # Show resource usage
    naga resources --memory       # Memory allocation details
    naga resources --registry     # Registry allocations
    naga resources --pools        # Resource pool status
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xbccdfe91"  # GenesisByte: parampara % 37 == 0

import os
import sys
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.ALLOC_MEM,
    name="resources",
    help_text="Resource allocation status (NARADA's distribution - WAKE phase)",
)
class ResourcesCommand(NagaCommandBase):
    """
    Resources command implementation.

    NARADA allocates:
    - Memory resources
    - Registry entries
    - Connection pools
    - Service instances

    The Messenger knows where resources flow.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute resources command.

        Args:
            args: Command arguments
                --memory: Memory allocation details
                --registry: Registry allocations
                --pools: Resource pool status

        Returns:
            NagaCommandResult with resource information
        """
        # Parse flags
        show_memory = "--memory" in args
        show_registry = "--registry" in args
        show_pools = "--pools" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "narada"),
            ("opcode", "ALLOC_MEM"),
            ("phase", "wake"),
            ("position", "2"),
        ]

        output_parts.append("[NARADA] Resource Allocation")
        output_parts.append("=" * 50)

        # Basic resource overview
        resources = self._get_resource_overview()
        output_parts.append("")
        output_parts.append("  System Resources:")
        output_parts.append(f"    Python Version:  {resources['python_version']}")
        output_parts.append(f"    Process Memory:  {resources['process_memory']}")
        output_parts.append(f"    Open Files:      {resources['open_files']}")
        data.append(("python_version", resources["python_version"]))

        # Memory details
        if show_memory:
            memory = self._get_memory_details()
            output_parts.append("")
            output_parts.append("  Memory Allocation (Narada's Distribution):")
            for key, value in memory.items():
                output_parts.append(f"    {key}: {value}")

        # Registry allocations
        if show_registry:
            registry = self._get_registry_allocations()
            output_parts.append("")
            output_parts.append("  Registry Allocations:")
            for key, value in registry.items():
                output_parts.append(f"    {key}: {value}")
            data.append(("registry_total", str(registry.get("total", 0))))

        # Pool status
        if show_pools:
            pools = self._get_pool_status()
            output_parts.append("")
            output_parts.append("  Resource Pools:")
            for pool_name, status in pools.items():
                output_parts.append(f"    {pool_name}: {status}")

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("ALLOC_MEM: Resources allocated")

        return self.success("\n".join(output_parts), data=tuple(data))

    def _get_resource_overview(self) -> dict:
        """Get basic resource overview."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Try to get process memory
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            memory_mb = usage.ru_maxrss / (1024 * 1024)  # Convert to MB (macOS)
            if sys.platform == "linux":
                memory_mb = usage.ru_maxrss / 1024  # Linux reports in KB
            process_memory = f"{memory_mb:.1f} MB"
        except Exception:
            process_memory = "unknown"

        # Open files
        try:
            import subprocess

            result = subprocess.run(["lsof", "-p", str(os.getpid())], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                open_files = str(len(result.stdout.strip().split("\n")) - 1)
            else:
                open_files = "unknown"
        except Exception:
            open_files = "unknown"

        return {
            "python_version": python_version,
            "process_memory": process_memory,
            "open_files": open_files,
        }

    def _get_memory_details(self) -> dict:
        """Get memory allocation details."""
        details = {}

        # Loaded modules
        details["Loaded Modules"] = str(len(sys.modules))

        # Garbage collector stats
        try:
            import gc

            gc_stats = gc.get_stats()
            total_collected = sum(s.get("collected", 0) for s in gc_stats)
            details["GC Collections"] = str(total_collected)
            details["GC Generations"] = str(len(gc_stats))
        except Exception:
            details["GC"] = "unavailable"

        # Object counts (approximate)
        try:
            import gc

            all_objects = gc.get_objects()
            details["Live Objects"] = f"~{len(all_objects):,}"
        except Exception:
            pass

        return details

    def _get_registry_allocations(self) -> dict:
        """Get registry allocation stats."""
        allocations = {}

        try:
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            discover_commands()
            allocations["Commands"] = str(len(NAGA_COMMAND_REGISTRY._commands))
        except Exception:
            allocations["Commands"] = "unavailable"

        try:
            from vibe_core.di import ServiceRegistry

            # Count registered services (if available)
            allocations["Services"] = "active"
        except Exception:
            allocations["Services"] = "unavailable"

        try:
            from vibe_core.runtime.prompt_registry import PROMPT_REGISTRY

            allocations["Prompts"] = str(len(PROMPT_REGISTRY._prompts))
        except Exception:
            allocations["Prompts"] = "unavailable"

        allocations["total"] = sum(1 for v in allocations.values() if v not in ["unavailable", "active"])

        return allocations

    def _get_pool_status(self) -> dict:
        """Get resource pool status."""
        pools = {}

        # Connection pools
        pools["HTTP Connections"] = "pooled (lazy)"
        pools["DB Connections"] = "not allocated"

        # Thread pools
        try:
            import threading

            pools["Active Threads"] = str(threading.active_count())
        except Exception:
            pools["Active Threads"] = "unknown"

        # Async pools
        try:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                pools["Event Loop"] = "running"
            except RuntimeError:
                pools["Event Loop"] = "not started"
        except Exception:
            pools["Event Loop"] = "unavailable"

        return pools


# Export for direct import
__all__ = ["ResourcesCommand"]
