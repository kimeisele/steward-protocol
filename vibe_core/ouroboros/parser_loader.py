"""
ViolationParserLoader - Dynamic Discovery for Violation Parsers.

OPUS-307 Pattern: No more hardcoded imports!

This loader follows the VEDA-4 pattern:
    SHABDA   → Scan parsers/ directory
    ARTHA    → Validate ViolationSourceParser inheritance
    PRATYAYA → Check name and patterns properties
    KARMA    → Register parser instance

The system can now:
1. Auto-discover all parsers from vibe_core/ouroboros/parsers/
2. Scale to many parsers without code changes
3. Allow runtime addition of new parsers
4. Let the system write its own parsers (GAD-000)

GAD-000 Compliance:
    - Discoverability: list_parsers() returns all available parsers
    - Observability: get_parser_info() shows parser state
    - Composability: Multiple parsers can handle a single file
"""

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

from vibe_core.ouroboros.parsers.base import BaseViolationParser, ViolationSourceParser

logger = logging.getLogger("OUROBOROS.PARSER_LOADER")


class ViolationParserLoader:
    """
    VEDA-4 compliant loader for violation source parsers.

    Discovers ViolationSourceParser implementations from the parsers directory
    and registers them by name.

    Usage:
        loader = ViolationParserLoader()
        parsers = loader.discover_and_load()
        # parsers = {"report_md": ReportMdParser(), ...}

        # Find parser for a file
        parser = loader.get_parser_for(Path("REPORT.md"))
    """

    # Default scan path (parsers directory)
    DEFAULT_PARSERS_PATH = Path(__file__).parent / "parsers"

    # Files to skip during scanning
    SKIP_FILES = {"__init__.py", "base.py"}

    def __init__(
        self,
        scan_paths: Optional[List[Path]] = None,
    ):
        """
        Initialize the parser loader.

        Args:
            scan_paths: Override default scan paths (for extensibility)
        """
        self._scan_paths = scan_paths or [self.DEFAULT_PARSERS_PATH]
        self._cache: Optional[Dict[str, ViolationSourceParser]] = None

    def discover_and_load(
        self,
        force_refresh: bool = False,
    ) -> Dict[str, ViolationSourceParser]:
        """
        Discover and load all parser classes.

        Returns:
            Dict mapping parser_name -> ViolationSourceParser instance
        """
        if not force_refresh and self._cache is not None:
            return self._cache

        parsers: Dict[str, ViolationSourceParser] = {}

        for scan_path in self._scan_paths:
            if not scan_path.exists():
                logger.debug(f"[PARSER] Scan path does not exist: {scan_path}")
                continue

            logger.debug(f"[PARSER] Scanning {scan_path}...")

            for py_file in scan_path.glob("*.py"):
                # Skip excluded files
                if py_file.name in self.SKIP_FILES:
                    continue

                # SHABDA: Load the module
                module = self._load_module(py_file)
                if module is None:
                    continue

                # ARTHA + PRATYAYA: Find parser classes
                for parser_class in self._find_parser_classes(module):
                    # KARMA: Instantiate and register
                    try:
                        instance = parser_class()
                        name = instance.name

                        if name in parsers:
                            logger.warning(
                                f"[PARSER] Duplicate parser name '{name}' - "
                                f"keeping {type(parsers[name]).__name__}, "
                                f"ignoring {parser_class.__name__}"
                            )
                            continue

                        parsers[name] = instance
                        logger.debug(
                            f"[PARSER] Registered: {name} -> {parser_class.__name__} (patterns: {instance.patterns})"
                        )

                    except Exception as e:
                        logger.warning(f"[PARSER] Failed to register {parser_class.__name__}: {e}")

        logger.info(f"[PARSER] Loaded {len(parsers)} parsers")
        self._cache = parsers
        return parsers

    def _load_module(self, py_file: Path):
        """
        Dynamically load a Python module from file.

        SHABDA: Capture the intent (code).
        """
        module_name = f"ouroboros_parser_{py_file.stem}"

        # Check if already loaded
        if module_name in sys.modules:
            return sys.modules[module_name]

        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                logger.debug(f"[PARSER] Cannot create spec for {py_file}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

        except Exception as e:
            logger.warning(f"[PARSER] Failed to load {py_file}: {e}")
            return None

    def _find_parser_classes(self, module) -> List[Type[BaseViolationParser]]:
        """
        Find all ViolationSourceParser implementations in a module.

        ARTHA: Validate the meaning (proper inheritance).
        """
        parser_classes = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Must be defined in this module (not imported)
            if obj.__module__ != module.__name__:
                continue

            # Must be a BaseViolationParser subclass
            if not issubclass(obj, BaseViolationParser):
                continue

            # Must not be the base class itself
            if obj is BaseViolationParser:
                continue

            parser_classes.append(obj)

        return parser_classes

    def list_parsers(self) -> List[str]:
        """
        List all discovered parser names.

        GAD-000: Discoverability.
        """
        parsers = self.discover_and_load()
        return list(parsers.keys())

    def get_parser(self, name: str) -> Optional[ViolationSourceParser]:
        """Get a specific parser by name."""
        parsers = self.discover_and_load()
        return parsers.get(name)

    def get_parser_for(self, path: Path) -> Optional[ViolationSourceParser]:
        """
        Find a parser that can handle the given file.

        Returns the first parser whose can_parse() returns True.
        """
        parsers = self.discover_and_load()

        for parser in parsers.values():
            try:
                if parser.can_parse(path):
                    return parser
            except Exception as e:
                logger.warning(f"[PARSER] Error checking {parser.name} for {path}: {e}")

        return None

    def get_all_parsers_for(self, path: Path) -> List[ViolationSourceParser]:
        """
        Find all parsers that can handle the given file.

        Some files might be parseable by multiple parsers.
        """
        parsers = self.discover_and_load()
        matching = []

        for parser in parsers.values():
            try:
                if parser.can_parse(path):
                    matching.append(parser)
            except Exception as e:
                # OPUS-312: Log parser failures (don't swallow silently)
                import logging

                logging.getLogger("OUROBOROS").warning(
                    f"Parser {parser.__class__.__name__}.can_parse() failed for {path}: {e}"
                )

        return matching

    def get_all_patterns(self) -> List[str]:
        """
        Get all file patterns from all parsers.

        Useful for file discovery - you can glob for these patterns.
        """
        parsers = self.discover_and_load()
        patterns = []

        for parser in parsers.values():
            patterns.extend(parser.patterns)

        return list(set(patterns))  # Deduplicate

    def clear_cache(self) -> None:
        """Clear the cache (for hot-reloading)."""
        self._cache = None

    def add_scan_path(self, path: Path) -> None:
        """
        Add a custom scan path for extensibility.

        Use Case: Agent-written parsers in a separate directory.
        """
        if path not in self._scan_paths:
            self._scan_paths.append(path)
            self._cache = None  # Invalidate cache

    def status(self) -> Dict:
        """
        Get loader status for debugging.

        GAD-000: Observability.
        """
        parsers = self.discover_and_load()
        return {
            "loaded": len(parsers),
            "parsers": {
                name: {
                    "class": type(p).__name__,
                    "patterns": p.patterns,
                }
                for name, p in parsers.items()
            },
            "scan_paths": [str(p) for p in self._scan_paths],
            "all_patterns": self.get_all_patterns(),
        }


# Module-level singleton for convenience
_default_loader: Optional[ViolationParserLoader] = None


def get_parser_loader() -> ViolationParserLoader:
    """Get the default parser loader singleton."""
    global _default_loader
    if _default_loader is None:
        _default_loader = ViolationParserLoader()
    return _default_loader


def discover_parsers() -> Dict[str, ViolationSourceParser]:
    """Convenience function to discover all parsers."""
    return get_parser_loader().discover_and_load()


def get_parser_for(path: Path) -> Optional[ViolationSourceParser]:
    """Convenience function to get parser for a file."""
    return get_parser_loader().get_parser_for(path)
