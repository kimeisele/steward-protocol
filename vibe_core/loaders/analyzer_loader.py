"""
Analyzer Loader - Auto-discovery for MANAS Analyzers.

OPUS-098: VEDA-4 Pattern for Analyzer Discovery

INHERITS: CodeModuleLoader (VEDA-4 compliant)

PATTERN:
    Same as ActionLoader/SenseLoader but for analyzers.
    Scans: vibe_core/plugins/opus_assistant/manas/analyzers/*.py
    Discovers: Classes inheriting from BaseAnalyzer
"""

import logging
from pathlib import Path
from typing import Any, List, Optional

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeRegistry,
)

logger = logging.getLogger("ANALYZER.LOADER")


# Type aliases (backward compat)
AnalyzerRegistry = CodeRegistry
AnalyzerMetadata = CodeMetadata


class AnalyzerLoadError(CodeModuleLoadError):
    """Raised when analyzer loading fails in STRICT MODE."""

    pass


class AnalyzerLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Analyzers.

    INHERITS: CodeModuleLoader for VEDA-4 compliance.

    Usage:
        # Discover and instantiate all analyzers
        analyzers, meta = AnalyzerLoader.discover_and_load(workspace=Path.cwd())

        # In IntentGenerator - just use the list directly
        self._modular_analyzers = list(analyzers.values())
    """

    # === LOADER CONFIG ===
    item_type = "analyzer"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/analyzers")]
    file_pattern = "*.py"
    base_class_name = "BaseAnalyzer"

    # === STRICT MODE ===
    strict_mode = True

    # === ANALYZER-SPECIFIC METHODS ===

    @classmethod
    def get_analyzer(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific analyzer by name."""
        return cls.get_item(name, workspace)

    @classmethod
    def list_analyzers(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered analyzer names."""
        return cls.list_items(workspace)


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("analyzer", AnalyzerLoader)
