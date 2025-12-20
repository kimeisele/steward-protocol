"""
OPUS-159: Infrastructure Builder

The actual construction worker.
Uses templates to generate infrastructure.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any, Dict, Optional

from .templates import TemplateRegistry
from .types import BuildResult, ModuleType

logger = logging.getLogger("GENESIS.BUILDER")


class InfrastructureBuilder:
    """
    The actual construction worker.

    Uses templates to generate infrastructure.
    Reports what was created/skipped.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        template_registry: Optional[TemplateRegistry] = None,
        dry_run: bool = False,
    ):
        """
        Initialize the builder.

        Args:
            workspace: Workspace root path
            template_registry: Custom template registry (optional)
            dry_run: If True, don't write files
        """
        self._workspace = workspace or Path.cwd()
        self._templates = template_registry or TemplateRegistry.get_instance()
        self._dry_run = dry_run

    def build(
        self,
        path: Path,
        module_type: ModuleType,
        context: Optional[Dict[str, Any]] = None,
    ) -> BuildResult:
        """
        Build infrastructure for a module.

        Args:
            path: Target directory
            module_type: Type of module
            context: Template context variables

        Returns:
            BuildResult with details of what was created
        """
        result = BuildResult(path=path, module_type=module_type)

        if module_type == ModuleType.UNKNOWN:
            result.errors.append("Cannot build infrastructure for UNKNOWN type")
            return result

        # Prepare context with defaults
        full_context = self._prepare_context(path, module_type, context)

        # Get templates for this module type
        templates = self._templates.get_templates(module_type)

        if not templates:
            result.errors.append(f"No templates found for {module_type.name}")
            return result

        # Ensure directory exists
        if not self._dry_run:
            path.mkdir(parents=True, exist_ok=True)

        # Build each template
        for template_key, template in templates.items():
            try:
                # Render filename (may contain variables)
                filename = Template(template.filename).safe_substitute(full_context)

                # Render content
                content = template.render(full_context)

                # Write file
                file_path = path / filename
                if file_path.exists():
                    result.skipped_files.append(filename)
                else:
                    if not self._dry_run:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content)
                        logger.info(f"Created: {file_path}")
                    result.created_files[filename] = file_path

            except Exception as e:
                result.errors.append(f"Failed to build {template_key}: {e}")
                logger.error(f"Build error for {template_key}: {e}")

        return result

    def repair(
        self,
        path: Path,
        module_type: ModuleType,
        missing_files: Optional[list] = None,
    ) -> BuildResult:
        """
        Repair missing infrastructure (self-healing).

        Only creates files that are missing.

        Args:
            path: Target directory
            module_type: Type of module
            missing_files: Specific files to repair (optional)

        Returns:
            BuildResult with details of what was repaired
        """
        result = BuildResult(path=path, module_type=module_type)

        # Prepare context
        context = self._prepare_context(path, module_type, None)

        # Get templates
        templates = self._templates.get_templates(module_type)

        for template_key, template in templates.items():
            # Render filename
            filename = Template(template.filename).safe_substitute(context)
            file_path = path / filename

            # Only repair if missing
            if file_path.exists():
                result.skipped_files.append(filename)
                continue

            # Only repair specific files if requested
            if missing_files and filename not in missing_files:
                continue

            try:
                content = template.render(context)

                if not self._dry_run:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)
                    logger.info(f"Repaired: {file_path}")

                result.created_files[filename] = file_path

            except Exception as e:
                result.errors.append(f"Failed to repair {filename}: {e}")

        return result

    def _prepare_context(
        self,
        path: Path,
        module_type: ModuleType,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepare template context with defaults."""
        name = path.name

        # Convert name to various formats
        defaults = {
            "id": name,
            "id_upper": name.upper(),
            "name": name.replace("_", " ").title(),
            "class_name": self._to_class_name(name),
            "description": f"Auto-generated {module_type.name.lower()}: {name}",
            "domain": "general",
            "timestamp": datetime.now().isoformat(),
            "module_type": module_type.name,
        }

        # Merge with provided context
        if context:
            defaults.update(context)

        return defaults

    def _to_class_name(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return "".join(word.title() for word in name.split("_"))
