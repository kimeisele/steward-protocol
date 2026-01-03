"""
ViolationSourceLoader - Discovery for Violation Source Files.

VEDA-4 Pattern:
    SHABDA   → Query parser patterns
    ARTHA    → Scan configured paths for matching files
    PRATYAYA → Validate files are parseable
    KARMA    → Return discovered sources

This loader:
1. Gets file patterns from ViolationParserLoader
2. Scans configured directories for matching files
3. Returns paths sorted by modification time (newest first)
4. Allows dynamic configuration of scan paths

GAD-000 Compliance:
    - Discoverability: list_sources() shows all found files
    - Observability: status() shows loader state
    - Composability: Works with ViolationParserLoader
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from vibe_core.ouroboros.parser_loader import ViolationParserLoader, get_parser_loader

logger = logging.getLogger("OUROBOROS.SOURCE_LOADER")


@dataclass
class ViolationSourceFile:
    """
    A discovered violation source file.

    Includes path, parser info, and metadata.
    """

    path: Path
    parser_name: str
    patterns_matched: List[str]
    mtime: float  # Modification time for sorting

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def relative_to(self) -> Path:
        """Relative path from current directory."""
        try:
            return self.path.relative_to(Path.cwd())
        except ValueError:
            return self.path


class ViolationSourceLoader:
    """
    VEDA-4 compliant loader for violation source files.

    Discovers files that can be parsed for violations.

    Usage:
        loader = ViolationSourceLoader()
        sources = loader.discover_sources()
        # [ViolationSourceFile(path=REPORT.md, parser=report_md), ...]
    """

    # Default scan paths (from project root)
    DEFAULT_SCAN_PATHS = [
        Path("."),  # Project root
        Path("docs"),
        Path("docs/architecture"),
        Path(".prakriti/violations"),
    ]

    def __init__(
        self,
        scan_paths: Optional[List[Path]] = None,
        parser_loader: Optional[ViolationParserLoader] = None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize the source loader.

        Args:
            scan_paths: Override default scan paths
            parser_loader: Custom parser loader (for testing)
            project_root: Project root for resolving relative paths
        """
        self._project_root = project_root or Path.cwd()
        self._scan_paths = scan_paths or [self._project_root / p for p in self.DEFAULT_SCAN_PATHS]
        self._parser_loader = parser_loader
        self._cache: Optional[List[ViolationSourceFile]] = None

    @property
    def parser_loader(self) -> ViolationParserLoader:
        """Lazy-load parser loader."""
        if self._parser_loader is None:
            self._parser_loader = get_parser_loader()
        return self._parser_loader

    def discover_sources(
        self,
        force_refresh: bool = False,
    ) -> List[ViolationSourceFile]:
        """
        Discover all violation source files.

        Returns files sorted by modification time (newest first).
        """
        if not force_refresh and self._cache is not None:
            return self._cache

        sources: List[ViolationSourceFile] = []
        seen_paths: set = set()

        # Get all patterns from all parsers
        patterns = self.parser_loader.get_all_patterns()
        parsers = self.parser_loader.discover_and_load()

        logger.debug(f"[SOURCE] Searching with patterns: {patterns}")

        for scan_path in self._scan_paths:
            if not scan_path.exists():
                continue

            # Glob for each pattern
            for pattern in patterns:
                # Convert ** pattern to work with glob
                glob_pattern = pattern.replace("**/", "")

                for path in scan_path.glob(glob_pattern):
                    if not path.is_file():
                        continue

                    # Skip already seen
                    abs_path = path.resolve()
                    if abs_path in seen_paths:
                        continue
                    seen_paths.add(abs_path)

                    # Find matching parser
                    parser = self.parser_loader.get_parser_for(path)
                    if parser is None:
                        continue

                    # Create source entry
                    sources.append(
                        ViolationSourceFile(
                            path=path,
                            parser_name=parser.name,
                            patterns_matched=[p for p in parser.patterns if self._matches_pattern(path, p)],
                            mtime=path.stat().st_mtime,
                        )
                    )

        # Sort by modification time (newest first)
        sources.sort(key=lambda s: s.mtime, reverse=True)

        logger.info(f"[SOURCE] Discovered {len(sources)} violation source files")
        self._cache = sources
        return sources

    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        import fnmatch

        pattern_clean = pattern.replace("**/", "")
        return fnmatch.fnmatch(path.name, pattern_clean) or fnmatch.fnmatch(str(path), pattern)

    def list_sources(self) -> List[str]:
        """
        List all discovered source file paths.

        GAD-000: Discoverability.
        """
        sources = self.discover_sources()
        return [str(s.path) for s in sources]

    def get_sources_by_parser(self, parser_name: str) -> List[ViolationSourceFile]:
        """Get all sources for a specific parser."""
        sources = self.discover_sources()
        return [s for s in sources if s.parser_name == parser_name]

    def get_newest_source(self, parser_name: Optional[str] = None) -> Optional[ViolationSourceFile]:
        """Get the most recently modified source file."""
        sources = self.discover_sources()
        if parser_name:
            sources = [s for s in sources if s.parser_name == parser_name]
        return sources[0] if sources else None

    def add_scan_path(self, path: Path) -> None:
        """Add a custom scan path."""
        abs_path = path if path.is_absolute() else self._project_root / path
        if abs_path not in self._scan_paths:
            self._scan_paths.append(abs_path)
            self._cache = None  # Invalidate cache

    def clear_cache(self) -> None:
        """Clear the cache (for hot-reloading)."""
        self._cache = None

    def status(self) -> Dict:
        """
        Get loader status for debugging.

        GAD-000: Observability.
        """
        sources = self.discover_sources()
        return {
            "discovered": len(sources),
            "scan_paths": [str(p) for p in self._scan_paths],
            "sources": [
                {
                    "path": str(s.path),
                    "parser": s.parser_name,
                    "name": s.name,
                }
                for s in sources
            ],
            "by_parser": {
                parser_name: len([s for s in sources if s.parser_name == parser_name])
                for parser_name in set(s.parser_name for s in sources)
            },
        }


# Module-level singleton for convenience
_default_loader: Optional[ViolationSourceLoader] = None


def get_source_loader(project_root: Optional[Path] = None) -> ViolationSourceLoader:
    """Get the default source loader singleton."""
    global _default_loader
    if _default_loader is None or project_root is not None:
        _default_loader = ViolationSourceLoader(project_root=project_root)
    return _default_loader


def discover_sources() -> List[ViolationSourceFile]:
    """Convenience function to discover all sources."""
    return get_source_loader().discover_sources()
