"""
Cortex Loader - Auto-discovery for MANAS Cortex Modules.

OPUS-171 Phase 5.2: VEDA-4 Pattern for Cortex Discovery

INHERITS: CodeModuleLoader (VEDA-4 compliant)

PATTERN:
    Same as HandlerLoader/ActionLoader but for cortex adapters.
    Scans: vibe_core/plugins/opus_assistant/manas/cortex/adapters/*.py
    Discovers: Classes inheriting from BaseCortex

COMPLETES THE VEDA-4 STACK:
    SenseLoader     → Senses (perception)
    AnalyzerLoader  → Analyzers (analysis)
    HandlerLoader   → Handlers (routing)
    ActionLoader    → Actions (atomic execution)
    CortexLoader    → Cortex (complex execution) ← NEW

"The cortex modules are the organs of MANAS - each specialized for a domain."
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from vibe_core.loaders.base_loader import LoaderRegistry
from vibe_core.loaders.code_module_loader import (
    CodeMetadata,
    CodeModuleLoader,
    CodeModuleLoadError,
    CodeRegistry,
)

logger = logging.getLogger("CORTEX.LOADER")


# Type aliases
CortexRegistry = CodeRegistry
CortexMetadata = CodeMetadata


class CortexLoadError(CodeModuleLoadError):
    """Raised when cortex loading fails in STRICT MODE."""

    pass


class CortexLoader(CodeModuleLoader):
    """
    Auto-discovery loader for MANAS Cortex Modules.

    OPUS-171 Phase 5.2: VEDA-4 Pattern for Cortex.

    Cortex modules are execution engines wrapped in BaseCortex adapters.
    Each cortex adapter declares:
    - name: Unique cortex identifier (e.g., "shell", "sutra")
    - capabilities: List of capabilities it provides

    Usage:
        # Discover and load all cortex modules
        cortices, meta = CortexLoader.discover_and_load(
            workspace=Path.cwd(),
        )

        # Get cortex by name
        shell = CortexLoader.get_cortex("shell", workspace=Path.cwd())

        # Execute an intent
        result = shell.execute(intent)
    """

    # === LOADER CONFIG ===
    item_type = "cortex"
    scan_paths = [Path("vibe_core/plugins/opus_assistant/manas/cortex/adapters")]
    file_pattern = "*_adapter.py"
    base_class_name = "BaseCortex"

    # === STRICT MODE ===
    strict_mode = False  # Cortex adapters are optional (handlers can fallback)

    # === CACHE FOR CAPABILITY MAPPING ===
    _capability_map: Dict[str, str] = {}  # capability → cortex_name

    @classmethod
    def discover_and_load(
        cls,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """
        Discover and load all cortex adapters, building capability mappings.

        Returns:
            Tuple of (cortex_dict, metadata_dict)
        """
        cortices, meta = super().discover_and_load(workspace=workspace, config=config)

        # Build capability → cortex mapping
        cls._capability_map.clear()

        for name, cortex_cls in cortices.items():
            # Map each capability to this cortex
            capabilities = getattr(cortex_cls, "capabilities", [])
            for cap in capabilities:
                if cap not in cls._capability_map:
                    cls._capability_map[cap] = name
                else:
                    # If capability already mapped, prefer higher priority
                    existing_cls = cortices.get(cls._capability_map[cap])
                    if existing_cls:
                        existing_priority = getattr(existing_cls, "priority", 0)
                        new_priority = getattr(cortex_cls, "priority", 0)
                        if new_priority > existing_priority:
                            cls._capability_map[cap] = name

        logger.info(
            f"CortexLoader: {len(cortices)} cortex adapters loaded, {len(cls._capability_map)} capabilities mapped"
        )

        return cortices, meta

    @classmethod
    def get_cortex(
        cls,
        name: str,
        workspace: Optional[Path] = None,
        kernel: Optional[Any] = None,
    ) -> Optional[Any]:
        """
        Get a cortex by name.

        Args:
            name: Cortex name (e.g., "shell", "sutra")
            workspace: Workspace path
            kernel: Optional kernel for injection

        Returns:
            Cortex instance or None if not found
        """
        workspace = workspace or Path.cwd()

        # Load all cortex adapters (CodeModuleLoader returns instances)
        cortices, _ = cls.discover_and_load(workspace=workspace)

        if name not in cortices:
            logger.warning(f"CortexLoader: No cortex found with name '{name}'")
            return None

        # CodeModuleLoader already returns instantiated objects
        cortex = cortices[name]

        # Inject kernel if provided
        if kernel and hasattr(cortex, "inject_kernel"):
            cortex.inject_kernel(kernel)

        logger.debug(f"CortexLoader: Retrieved {name} cortex")
        return cortex

    @classmethod
    def get_cortex_for_capability(
        cls,
        capability: str,
        workspace: Optional[Path] = None,
        kernel: Optional[Any] = None,
    ) -> Optional[Any]:
        """
        Get a cortex that provides a specific capability.

        Args:
            capability: The capability needed (e.g., "git_commit")
            workspace: Workspace path
            kernel: Optional kernel for injection

        Returns:
            Instantiated cortex or None if not found
        """
        # Ensure loaded
        if not cls._capability_map:
            cls.discover_and_load(workspace=workspace)

        cortex_name = cls._capability_map.get(capability)
        if not cortex_name:
            logger.debug(f"CortexLoader: No cortex provides capability '{capability}'")
            return None

        return cls.get_cortex(cortex_name, workspace=workspace, kernel=kernel)

    @classmethod
    def list_cortices(cls, workspace: Optional[Path] = None) -> List[str]:
        """List all available cortex names."""
        cortices, _ = cls.discover_and_load(workspace=workspace)
        return list(cortices.keys())

    @classmethod
    def list_capabilities(cls, workspace: Optional[Path] = None) -> Dict[str, str]:
        """List all capabilities and which cortex provides them."""
        if not cls._capability_map:
            cls.discover_and_load(workspace=workspace)
        return dict(cls._capability_map)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the capability mapping cache."""
        cls._capability_map.clear()
        # Also clear the base class cache
        super().clear_cache()
        logger.debug("CortexLoader: Cache cleared")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_cortex(
    name: str,
    workspace: Optional[Path] = None,
    kernel: Optional[Any] = None,
) -> Optional[Any]:
    """
    Convenience function to get a cortex by name.

    Usage:
        from vibe_core.loaders import get_cortex

        shell = get_cortex("shell", workspace=Path.cwd())
        result = shell.execute(intent)
    """
    return CortexLoader.get_cortex(name, workspace=workspace, kernel=kernel)


def list_cortices(workspace: Optional[Path] = None) -> List[str]:
    """Convenience function to list all available cortex names."""
    return CortexLoader.list_cortices(workspace=workspace)
