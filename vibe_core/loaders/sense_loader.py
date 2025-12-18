"""
Sense Loader - Auto-discovery for MANAS Cortex Senses.

OPUS-099: VEDA-4 Pattern for Cortex Auto-Discovery

The 5 Jnanendriyas (Perception Organs) in Samkhya:
- TVAK (Touch)       → PrakritiSense  (System state)
- CHAKSHU (Sight)    → SutraSense     (Doc/Code gaps)
- RASANA (Taste)     → DharmaSense    (Ethical alignment)
- (Future: SHROTRA, GHRANA when converted to BaseSense)

INHERITS: CodeModuleLoader (VEDA-4 compliant)

PATTERN:
    Same as ActionLoader but for senses (cortex perception modules).
    Scans: vibe_core/plugins/opus_assistant/manas/cortex/*_sense.py
    Discovers: Classes inheriting from BaseSense
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeRegistry,
)

logger = logging.getLogger("SENSE.LOADER")


# Type aliases (backward compat)
SenseRegistry = CodeRegistry
SenseMetadata = CodeMetadata


class SenseLoadError(CodeModuleLoadError):
    """Raised when sense loading fails in STRICT MODE."""

    pass


class SenseLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Cortex Senses (Jnanendriyas).

    INHERITS: CodeModuleLoader for VEDA-4 compliance.

    Usage:
        # Discover and instantiate all senses
        senses, meta = SenseLoader.discover_and_load(workspace=Path.cwd())

        # In CognitiveKernel - just use the dict directly
        self._senses = senses
        prakriti = senses.get("prakriti_sense")
    """

    # === LOADER CONFIG ===
    item_type = "sense"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex")]
    file_pattern = "*_sense.py"
    base_class_name = "BaseSense"

    # === STRICT MODE ===
    strict_mode = True

    # === SENSE-SPECIFIC METHODS ===

    @classmethod
    def get_sense(cls, name: str, workspace: Optional[Path] = None) -> Optional[Any]:
        """Get a specific sense by name."""
        return cls.get_item(name, workspace)

    @classmethod
    def list_senses(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all discovered sense names."""
        return cls.list_items(workspace)


# Register with LoaderRegistry - VEDA-4 COMPLIANT
LoaderRegistry.register("sense", SenseLoader)
