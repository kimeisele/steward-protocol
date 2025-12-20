"""
OPUS-159: Genesis Service

The unified API for infrastructure genesis.
This is the Front Desk of the Stadtamt.

Consumers (MANAS, Engineer, etc.) call this service.
It coordinates: Compliance → Templates → Builder
"""

import fnmatch
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .builder import InfrastructureBuilder
from .compliance import ComplianceBureau
from .templates import TemplateRegistry
from .types import BuildResult, ComplianceReport, GenesisResult, ModuleType

logger = logging.getLogger("GENESIS.SERVICE")


class GenesisService:
    """
    The unified API for infrastructure genesis.

    This is what MANAS and Engineer call.
    The Front Desk of the Stadtamt.
    """

    _instance: Optional["GenesisService"] = None

    # Path patterns for module type detection
    PATH_PATTERNS: List[Tuple[str, ModuleType]] = [
        # More specific patterns first
        ("*/manas/cortex/*_sense.py", ModuleType.SENSE),
        ("*/manas/cortex/*_action.py", ModuleType.ACTION),
        ("*/manas/analyzers/*", ModuleType.ANALYZER),
        ("vibe_core/plugins/*", ModuleType.PLUGIN),
        ("vibe_core/cartridges/*/*", ModuleType.CARTRIDGE),
        ("vibe_core/phoenix/sections/*", ModuleType.SECTION),
        ("knowledge/*", ModuleType.KNOWLEDGE),
        ("*/circuits/*", ModuleType.CIRCUIT),
        ("*/tools/*", ModuleType.TOOL),
    ]

    # Directories to ignore
    IGNORE_PATTERNS = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".git/*",
        "node_modules",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
    ]

    def __init__(
        self,
        workspace: Optional[Path] = None,
        dry_run: bool = False,
    ):
        """
        Initialize the Genesis Service.

        Args:
            workspace: Workspace root path
            dry_run: If True, don't write files
        """
        self._workspace = workspace or Path.cwd()
        self._dry_run = dry_run

        # Initialize components
        self._compliance = ComplianceBureau(workspace=self._workspace)
        self._templates = TemplateRegistry.get_instance()
        self._builder = InfrastructureBuilder(
            workspace=self._workspace,
            template_registry=self._templates,
            dry_run=dry_run,
        )

    @classmethod
    def get_instance(cls, workspace: Optional[Path] = None) -> "GenesisService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(workspace=workspace)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None

    @property
    def compliance(self) -> ComplianceBureau:
        """Access the Compliance Bureau."""
        return self._compliance

    @property
    def templates(self) -> TemplateRegistry:
        """Access the Template Registry."""
        return self._templates

    @property
    def builder(self) -> InfrastructureBuilder:
        """Access the Infrastructure Builder."""
        return self._builder

    def classify_path(self, path: Path) -> ModuleType:
        """
        Classify a path to determine module type.

        Args:
            path: Path to classify (absolute or relative)

        Returns:
            ModuleType for the path
        """
        # Normalize to relative path
        if path.is_absolute():
            try:
                path = path.relative_to(self._workspace)
            except ValueError:
                return ModuleType.UNKNOWN

        path_str = str(path)

        # Check if should ignore
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return ModuleType.UNKNOWN

        # Check patterns
        for pattern, module_type in self.PATH_PATTERNS:
            if fnmatch.fnmatch(path_str, pattern):
                return module_type

        return ModuleType.UNKNOWN

    def ensure_compliance(
        self,
        path: Path,
        module_type: Optional[ModuleType] = None,
    ) -> GenesisResult:
        """
        Ensure a module is GAD-000 compliant.

        1. Check current compliance
        2. Build missing infrastructure
        3. Verify result

        Args:
            path: Path to the module
            module_type: Type of module (auto-detected if not provided)

        Returns:
            GenesisResult with compliance and build details
        """
        # Auto-detect type if not provided
        if module_type is None:
            module_type = self.classify_path(path)

        if module_type == ModuleType.UNKNOWN:
            return GenesisResult(
                path=path,
                module_type=module_type,
            )

        # Check compliance before
        compliance_before = self._compliance.audit(path, module_type)

        # If already compliant, return early
        if compliance_before.passed and not compliance_before.missing_files:
            logger.debug(f"Already compliant: {path}")
            return GenesisResult(
                path=path,
                module_type=module_type,
                compliance_before=compliance_before,
                compliance_after=compliance_before,
            )

        # Build missing infrastructure
        build_result = self._builder.repair(
            path=path,
            module_type=module_type,
            missing_files=compliance_before.missing_files,
        )

        # Check compliance after
        compliance_after = self._compliance.audit(path, module_type)

        result = GenesisResult(
            path=path,
            module_type=module_type,
            compliance_before=compliance_before,
            compliance_after=compliance_after,
            build_result=build_result,
        )

        if build_result.files_created_count > 0:
            logger.info(
                f"🏛️ Genesis: Created {build_result.files_created_count} files for {module_type.name}: {path.name}"
            )

        return result

    def scaffold_new(
        self,
        path: Path,
        module_type: ModuleType,
        context: Optional[Dict] = None,
    ) -> GenesisResult:
        """
        Scaffold a completely new module.

        Args:
            path: Target directory
            module_type: Type of module
            context: Template context variables

        Returns:
            GenesisResult with build details
        """
        if module_type == ModuleType.UNKNOWN:
            return GenesisResult(
                path=path,
                module_type=module_type,
                build_result=BuildResult(
                    path=path,
                    module_type=module_type,
                    errors=["Cannot scaffold UNKNOWN module type"],
                ),
            )

        # Build infrastructure
        build_result = self._builder.build(
            path=path,
            module_type=module_type,
            context=context,
        )

        # Check compliance after
        compliance_after = None
        if build_result.success:
            compliance_after = self._compliance.audit(path, module_type)

        result = GenesisResult(
            path=path,
            module_type=module_type,
            build_result=build_result,
            compliance_after=compliance_after,
        )

        if build_result.success:
            logger.info(
                f"🏛️ Genesis: Scaffolded new {module_type.name}: {path.name} ({build_result.files_created_count} files)"
            )

        return result

    def quick_check(self, path: Path) -> bool:
        """
        Fast check: Is this path GAD-000 compliant?

        Returns True if minimum infrastructure exists.
        """
        module_type = self.classify_path(path)
        if module_type == ModuleType.UNKNOWN:
            return True  # Don't flag unknown paths

        return self._compliance.quick_check(path, module_type)

    def get_required_files(self, module_type: ModuleType) -> List[str]:
        """Get list of required files for a module type."""
        return self._templates.get_required_files(module_type)
