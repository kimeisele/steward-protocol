"""
ViolationSourceParser - Protocol for violation source parsers.

VEDA-4 Pattern:
    SHABDA   → Declare parser identity (name, patterns)
    ARTHA    → Validate file matches patterns
    PRATYAYA → Check file can be parsed
    KARMA    → Execute parsing, return ViolationRecords

This protocol is runtime_checkable, so ViolationParserLoader can verify
implementations at discovery time.

GAD-000 Compliance:
    - Discoverability: Parsers declare what patterns they handle
    - Observability: Parsers expose their name and patterns
    - Composability: Multiple parsers can handle a single file
"""

import fnmatch
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Protocol, runtime_checkable

from vibe_core.ouroboros.ingestion import ViolationRecord

logger = logging.getLogger("OUROBOROS.PARSER")


@runtime_checkable
class ViolationSourceParser(Protocol):
    """
    Protocol for violation source parsers.

    Implement this protocol to create a new parser that can extract
    ViolationRecords from a specific file format.

    Example:
        class MyCustomParser(ViolationSourceParser):
            name = "my_custom_parser"
            patterns = ["**/*.custom", "**/*_report.txt"]

            def can_parse(self, path: Path) -> bool:
                return path.suffix == ".custom" or path.name.endswith("_report.txt")

            def parse(self, path: Path) -> List[ViolationRecord]:
                content = path.read_text()
                # ... extract violations ...
                return violations
    """

    @property
    def name(self) -> str:
        """
        Parser name for registration and logging.

        Should be unique across all parsers (e.g., "report_md", "watchman_json").
        """
        ...

    @property
    def patterns(self) -> List[str]:
        """
        File patterns this parser handles.

        Glob patterns like ["**/REPORT*.md", "**/*_report.md"].
        Used for efficient file discovery.
        """
        ...

    def can_parse(self, path: Path) -> bool:
        """
        Check if this parser can handle the given file.

        Called after pattern matching to do fine-grained validation.
        For example, checking file headers or content structure.

        Args:
            path: Path to the file

        Returns:
            True if parser can handle this file
        """
        ...

    def parse(self, path: Path) -> List[ViolationRecord]:
        """
        Parse violations from the file.

        Args:
            path: Path to the file

        Returns:
            List of ViolationRecord extracted from the file
        """
        ...


class BaseViolationParser(ABC):
    """
    Abstract base class for violation source parsers.

    Provides default implementation of pattern matching.
    Subclasses only need to implement parse().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Parser name (must be unique)."""
        ...

    @property
    @abstractmethod
    def patterns(self) -> List[str]:
        """Glob patterns this parser handles."""
        ...

    def can_parse(self, path: Path) -> bool:
        """
        Default implementation: check if path matches any pattern.

        Override for more specific validation (e.g., checking file headers).
        """
        for pattern in self.patterns:
            if fnmatch.fnmatch(str(path), pattern):
                return True
            # Also check just the filename against patterns without paths
            if fnmatch.fnmatch(path.name, pattern.replace("**/", "")):
                return True
        return False

    @abstractmethod
    def parse(self, path: Path) -> List[ViolationRecord]:
        """Parse violations from the file."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} patterns={self.patterns}>"
