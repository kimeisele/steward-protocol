"""
OPUS-158: InfrastructureClassifier

Classifies new directories/files by their purpose.
Uses path patterns to determine what infrastructure is needed.

Sanskrit: वर्गीकरण (Vargeekarana) = Classification
"""

import fnmatch
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from vibe_core.genesis.types import ModuleType

logger = logging.getLogger("MANAS.GENESIS.CLASSIFIER")


class InfrastructureClassifier:
    """
    Classify new directories/files by their purpose.

    The first step in the Agent Virus loop:
        DETECT -> CLASSIFY -> GENERATE -> WIRE -> REPLICATE
                   ^^^^^

    Uses path patterns to determine what GAD-000 infrastructure is needed.
    """

    # Pattern -> ModuleType mapping
    # Order matters - more specific patterns should come first
    PATTERNS: List[Tuple[str, ModuleType]] = [
        # Senses (in cortex, ending with _sense.py)
        ("*/manas/cortex/*_sense.py", ModuleType.SENSE),
        # Actions (in cortex, ending with _action.py)
        ("*/manas/cortex/*_action.py", ModuleType.ACTION),
        # Analyzers (in analyzers directory)
        ("*/manas/analyzers/*", ModuleType.ANALYZER),
        # Plugins (top-level in plugins)
        ("vibe_core/plugins/*", ModuleType.PLUGIN),
        # Circuits
        ("*/circuits/*", ModuleType.CIRCUIT),
        ("vibe_core/playbook/circuits/*", ModuleType.CIRCUIT),
        # Phoenix sections
        ("vibe_core/phoenix/sections/*", ModuleType.SECTION),
        # Knowledge base
        ("knowledge/*", ModuleType.KNOWLEDGE),
        # Tests
        ("tests/*", ModuleType.TEST),
    ]

    # Directories to skip
    IGNORE_PATTERNS = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".git/*",
        "node_modules",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        "*.swp",
        "*.swo",
        "*~",
    ]

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize classifier.

        Args:
            workspace: Workspace root (for relative path resolution)
        """
        self._workspace = workspace or Path.cwd()

    def classify(self, path: Path, is_directory: bool = True) -> ModuleType:
        """
        Classify a path to determine required infrastructure.

        Args:
            path: Absolute or relative path to new file/directory
            is_directory: True if this is a directory

        Returns:
            ModuleType indicating what infrastructure to generate
        """
        # Normalize path
        if path.is_absolute():
            try:
                path = path.relative_to(self._workspace)
            except ValueError:
                # Path not under workspace
                return ModuleType.UNKNOWN

        path_str = str(path)

        # Check if should ignore
        if self._should_ignore(path_str):
            return ModuleType.UNKNOWN

        # Check each pattern
        for pattern, module_type in self.PATTERNS:
            if self._matches_pattern(path_str, pattern):
                logger.debug(f"Classified {path_str} as {module_type.name}")
                return module_type

        return ModuleType.UNKNOWN

    def classify_file(self, path: Path) -> ModuleType:
        """Classify a file path."""
        return self.classify(path, is_directory=False)

    def classify_directory(self, path: Path) -> ModuleType:
        """Classify a directory path."""
        return self.classify(path, is_directory=True)

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Match path against glob-like pattern.

        Supports:
            * - Match any characters except /
            ** - Match any characters including /
        """
        # Convert pattern to regex-compatible form
        # fnmatch already handles * correctly
        return fnmatch.fnmatch(path, pattern)

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch.fnmatch(path, pattern):
                return True
            # Also check just the basename
            if fnmatch.fnmatch(Path(path).name, pattern):
                return True
        return False

    def get_expected_files(self, module_type: ModuleType) -> List[str]:
        """
        Get list of files expected for a module type.

        This is the GAD-000 compliance checklist per type.
        """
        expected = {
            ModuleType.PLUGIN: [
                "__init__.py",
                "manifest.json",
                "plugin_main.py",
            ],
            ModuleType.ANALYZER: [
                # File must match *_analyzer.py pattern
                # Must inherit BaseAnalyzer
            ],
            ModuleType.SENSE: [
                # File must match *_sense.py pattern
                # Must inherit BaseSense
                # Must have perceive() method
            ],
            ModuleType.ACTION: [
                # File must match *_action.py pattern
                # Must inherit BaseAction
                # Must have handled_intent_types
                # Must have act() method
            ],
            ModuleType.SECTION: [
                "manifest.json",
            ],
            ModuleType.KNOWLEDGE: [
                "manifest.json",
            ],
            ModuleType.CIRCUIT: [
                # YAML file with circuit: section
            ],
            ModuleType.TEST: [
                # Test file with test_ prefix
            ],
        }
        return expected.get(module_type, [])
