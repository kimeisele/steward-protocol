"""
GC COMMAND - KAPILA's Analysis & Cleanup
========================================

MAHAJANA: KAPILA (The Analyzer)
OPCODE: GARBAGE_COLLECT (Position 7)
PHASE: PURIFY

WHY KAPILA?
- Kapila founded Sankhya philosophy (analytical enumeration)
- He analyzed prakriti into 24 elements
- GARBAGE_COLLECT is about analyzing what is unused and cleaning it
- Kapila analyzes, categorizes, and removes what is not needed

MANTRA WORD: HARE (Position 7)
"Hare removes what is not needed"

GARBAGE_COLLECT = Analyze and clean unused resources.
Kapila's philosophy: understand the components, remove the unnecessary.

Usage:
    naga gc                       # Show what can be cleaned
    naga gc --analyze             # Deep analysis only
    naga gc --clean               # Actually clean (with confirmation)
    naga gc --cache               # Clean caches only
    naga gc --pycache             # Clean __pycache__ directories
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x71f7ff96"  # GenesisByte: parampara % 37 == 0

import os
import shutil
from pathlib import Path
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode

import logging
logger = logging.getLogger(__name__)


@naga_command(
    opcode=MantraOpCode.TYPE_CHECK,
    name="gc",
    help_text="Analyze and clean unused resources (KAPILA's analysis - PURIFY phase)",
)
class GcCommand(NagaCommandBase):
    """
    Garbage collection command implementation.

    KAPILA analyzes and cleans:
    - __pycache__ directories
    - .pyc files
    - Build artifacts
    - Stale cache files
    - Unused dependencies (analysis only)

    Kapila's Sankhya: enumerate, analyze, clean.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute gc command.

        Args:
            args: Command arguments
                --analyze: Deep analysis only (no cleaning)
                --clean: Actually clean (requires confirmation)
                --cache: Clean caches only
                --pycache: Clean __pycache__ directories only

        Returns:
            NagaCommandResult with gc analysis/results
        """
        # Parse flags
        analyze_only = "--analyze" in args
        do_clean = "--clean" in args
        cache_only = "--cache" in args
        pycache_only = "--pycache" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "kapila"),
            ("opcode", "GARBAGE_COLLECT"),
            ("phase", "purify"),
            ("position", "7"),
        ]

        output_parts.append("[KAPILA] Garbage Collection Analysis")
        output_parts.append("=" * 50)

        # Analyze what can be cleaned
        analysis = self._analyze_garbage()

        output_parts.append("")
        output_parts.append("  Sankhya Analysis (24 Elements → Resources):")
        output_parts.append(f"    __pycache__ dirs:    {analysis['pycache_count']}")
        output_parts.append(f"    .pyc files:          {analysis['pyc_count']}")
        output_parts.append(f"    Build artifacts:     {analysis['build_count']}")
        output_parts.append(f"    Total size:          {analysis['total_size_mb']:.2f} MB")

        data.append(("pycache_count", str(analysis["pycache_count"])))
        data.append(("pyc_count", str(analysis["pyc_count"])))
        data.append(("total_size_mb", f"{analysis['total_size_mb']:.2f}"))

        if analyze_only:
            output_parts.append("")
            output_parts.append("  Analysis complete. Use --clean to remove.")
            data.append(("action", "analyze"))

        elif do_clean:
            output_parts.append("")
            if pycache_only:
                cleaned = self._clean_pycache()
                output_parts.append(f"  Cleaned {cleaned} __pycache__ directories.")
                data.append(("cleaned_pycache", str(cleaned)))
            elif cache_only:
                cleaned = self._clean_caches()
                output_parts.append(f"  Cleaned {cleaned} cache items.")
                data.append(("cleaned_caches", str(cleaned)))
            else:
                cleaned_pycache = self._clean_pycache()
                cleaned_pyc = self._clean_pyc_files()
                output_parts.append(f"  Cleaned {cleaned_pycache} __pycache__ dirs.")
                output_parts.append(f"  Cleaned {cleaned_pyc} .pyc files.")
                data.append(("cleaned_pycache", str(cleaned_pycache)))
                data.append(("cleaned_pyc", str(cleaned_pyc)))
            data.append(("action", "clean"))

        else:
            output_parts.append("")
            output_parts.append("  Options:")
            output_parts.append("    --analyze    Deep analysis only")
            output_parts.append("    --clean      Actually remove garbage")
            output_parts.append("    --pycache    Clean __pycache__ only")
            output_parts.append("    --cache      Clean all caches")
            data.append(("action", "info"))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("GARBAGE_COLLECT: Analysis complete")

        return self.success("\n".join(output_parts), data=tuple(data))

    def _analyze_garbage(self) -> dict:
        """Analyze what garbage exists."""
        cwd = Path.cwd()

        pycache_dirs = list(cwd.rglob("__pycache__"))
        pyc_files = list(cwd.rglob("*.pyc"))

        # Build artifacts
        build_dirs = []
        for name in ["build", "dist", "*.egg-info"]:
            build_dirs.extend(cwd.glob(name))

        # Calculate size
        total_size = 0
        for d in pycache_dirs:
            if d.exists():
                total_size += sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        for f in pyc_files:
            if f.exists():
                total_size += f.stat().st_size

        return {
            "pycache_count": len(pycache_dirs),
            "pyc_count": len(pyc_files),
            "build_count": len(build_dirs),
            "total_size_mb": total_size / (1024 * 1024),
            "pycache_dirs": pycache_dirs,
            "pyc_files": pyc_files,
            "build_dirs": build_dirs,
        }

    def _clean_pycache(self) -> int:
        """Clean __pycache__ directories."""
        cwd = Path.cwd()
        cleaned = 0

        for pycache in cwd.rglob("__pycache__"):
            if pycache.exists() and pycache.is_dir():
                try:
                    shutil.rmtree(pycache)
                    cleaned += 1
                except Exception as _exc:
                    logger.exception("Unexpected error: %s", _exc)

        return cleaned

    def _clean_pyc_files(self) -> int:
        """Clean .pyc files."""
        cwd = Path.cwd()
        cleaned = 0

        for pyc in cwd.rglob("*.pyc"):
            if pyc.exists():
                try:
                    pyc.unlink()
                    cleaned += 1
                except Exception as _exc:
                    logger.exception("Unexpected error: %s", _exc)

        return cleaned

    def _clean_caches(self) -> int:
        """Clean various cache directories."""
        cwd = Path.cwd()
        cleaned = 0

        # Clean __pycache__
        cleaned += self._clean_pycache()

        # Clean .pyc
        cleaned += self._clean_pyc_files()

        # Clean pytest cache
        pytest_cache = cwd / ".pytest_cache"
        if pytest_cache.exists():
            try:
                shutil.rmtree(pytest_cache)
                cleaned += 1
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

        # Clean mypy cache
        mypy_cache = cwd / ".mypy_cache"
        if mypy_cache.exists():
            try:
                shutil.rmtree(mypy_cache)
                cleaned += 1
            except Exception as _exc:
                logger.exception("Unexpected error: %s", _exc)

        return cleaned


# Export for direct import
__all__ = ["GcCommand"]
