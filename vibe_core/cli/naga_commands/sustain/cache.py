"""
CACHE COMMAND - NRISIMHA's Protection
======================================

MAHAJANA: NRISIMHA (The Man-Lion Avatara)
OPCODE: CACHE_STATE (Position 12)
PHASE: SUSTAIN

WHY NRISIMHA?
- Nrisimha protects devotees (Prahlada) from destruction
- He preserves what is valuable
- CACHE_STATE is about preserving state for quick retrieval
- Nrisimha caches/protects state from being lost

MANTRA WORD: RAMA (Position 12)
"Rama preserves dharma"

CACHE_STATE = Cache important state for persistence.
Nrisimha protects, Nrisimha preserves, Nrisimha caches.

Usage:
    naga cache                    # Show cache status
    naga cache --stats            # Cache statistics
    naga cache --clear            # Clear all caches
    naga cache --warm             # Warm up caches
"""

import shutil
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.CACHE_STATE,
    name="cache",
    help_text="Cache state management (NRISIMHA's protection - SUSTAIN phase)")
class CacheCommand(NagaCommandBase):
    """
    Cache command implementation.

    NRISIMHA protects:
    - Application state
    - Computed results
    - Frequently accessed data
    - Session state

    The Protector preserves what is valuable.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute cache command.

        Args:
            args: Command arguments
                --stats: Show cache statistics
                --clear: Clear all caches
                --warm: Warm up caches

        Returns:
            NagaCommandResult with cache information
        """
        # Parse flags
        show_stats = "--stats" in args
        do_clear = "--clear" in args
        do_warm = "--warm" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "nrisimha"),
            ("opcode", "CACHE_STATE"),
            ("phase", "sustain"),
            ("position", "12"),
        ]

        output_parts.append("[NRISIMHA] Cache State")
        output_parts.append("=" * 50)

        # Get cache overview
        cache_info = self._get_cache_info()
        output_parts.append("")
        output_parts.append("  Cache Overview:")
        output_parts.append(f"    Pytest Cache:     {cache_info['pytest']}")
        output_parts.append(f"    Mypy Cache:       {cache_info['mypy']}")
        output_parts.append(f"    Vibe Cache:       {cache_info['vibe']}")
        output_parts.append(f"    Total Size:       {cache_info['total_size']}")

        if show_stats:
            stats = self._get_cache_stats()
            output_parts.append("")
            output_parts.append("  Cache Statistics:")
            for key, value in stats.items():
                output_parts.append(f"    {key}: {value}")

        if do_clear:
            cleared = self._clear_caches()
            output_parts.append("")
            output_parts.append("  Caches Cleared (Nrisimha's Renewal):")
            for cache_name, status in cleared.items():
                output_parts.append(f"    {cache_name}: {status}")
            data.append(("action", "clear"))

        if do_warm:
            warmed = self._warm_caches()
            output_parts.append("")
            output_parts.append("  Caches Warmed:")
            for cache_name, status in warmed.items():
                output_parts.append(f"    {cache_name}: {status}")
            data.append(("action", "warm"))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("CACHE_STATE: State preserved")

        return self.success(
            "\n".join(output_parts),
            data=tuple(data))

    def _get_cache_info(self) -> dict:
        """Get cache overview information."""
        cwd = Path.cwd()
        info = {}

        # Pytest cache
        pytest_cache = cwd / ".pytest_cache"
        info["pytest"] = "present" if pytest_cache.exists() else "none"

        # Mypy cache
        mypy_cache = cwd / ".mypy_cache"
        info["mypy"] = "present" if mypy_cache.exists() else "none"

        # Vibe cache
        vibe_cache = cwd / ".vibe" / "cache"
        info["vibe"] = "present" if vibe_cache.exists() else "none"

        # Calculate total size
        total_size = 0
        for cache_dir in [pytest_cache, mypy_cache, vibe_cache]:
            if cache_dir.exists():
                for f in cache_dir.rglob("*"):
                    if f.is_file():
                        total_size += f.stat().st_size

        info["total_size"] = f"{total_size / (1024 * 1024):.2f} MB"

        return info

    def _get_cache_stats(self) -> dict:
        """Get detailed cache statistics."""
        cwd = Path.cwd()
        stats = {}

        # Count cache files
        pytest_cache = cwd / ".pytest_cache"
        if pytest_cache.exists():
            stats["Pytest Files"] = str(len(list(pytest_cache.rglob("*"))))
        else:
            stats["Pytest Files"] = "0"

        mypy_cache = cwd / ".mypy_cache"
        if mypy_cache.exists():
            stats["Mypy Files"] = str(len(list(mypy_cache.rglob("*"))))
        else:
            stats["Mypy Files"] = "0"

        # Pycache count
        pycache_count = len(list(cwd.rglob("__pycache__")))
        stats["Pycache Dirs"] = str(pycache_count)

        return stats

    def _clear_caches(self) -> dict:
        """Clear all caches."""
        cwd = Path.cwd()
        cleared = {}

        # Clear pytest cache
        pytest_cache = cwd / ".pytest_cache"
        if pytest_cache.exists():
            try:
                shutil.rmtree(pytest_cache)
                cleared["pytest_cache"] = "cleared"
            except Exception:
                cleared["pytest_cache"] = "failed"
        else:
            cleared["pytest_cache"] = "not present"

        # Clear mypy cache
        mypy_cache = cwd / ".mypy_cache"
        if mypy_cache.exists():
            try:
                shutil.rmtree(mypy_cache)
                cleared["mypy_cache"] = "cleared"
            except Exception:
                cleared["mypy_cache"] = "failed"
        else:
            cleared["mypy_cache"] = "not present"

        return cleared

    def _warm_caches(self) -> dict:
        """Warm up caches."""
        warmed = {}

        # Warm by importing key modules
        try:
            from vibe_core.cli.naga_commands import discover_commands

            discover_commands()
            warmed["commands"] = "warmed"
        except Exception:
            warmed["commands"] = "failed"

        try:
            from vibe_core.protocols.substrate import MantraOpCode

            _ = list(MantraOpCode)
            warmed["opcodes"] = "warmed"
        except Exception:
            warmed["opcodes"] = "failed"

        return warmed


# Export for direct import
__all__ = ["CacheCommand"]
