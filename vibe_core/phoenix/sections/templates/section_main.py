"""
Templates Configuration - Jinja2 template registry and loader.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/templates/
    ARTHA: Parsed from config/templates.yaml
    PRATYAYA: Validated (template files must exist, syntax checked)
    KARMA: Instantiated as TemplatesConfig dataclass with lazy loading

This section eliminates 5 hardcoded BUILTIN_TEMPLATES violations:
    - action_handlers.py: status_summary, agent_list, simple templates
    - opus/renderer.py: panel templates
    - git.py, tasks.py: report templates

Templates are loaded from knowledge/templates/*.j2 with fallback to builtins.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xb4966502"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, Template, TemplateSyntaxError

    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    Environment = None
    FileSystemLoader = None
    Template = None
    TemplateSyntaxError = Exception

logger = logging.getLogger(__name__)


@dataclass
class TemplateEntry:
    """Single template configuration entry."""

    name: str
    file: str
    description: str = ""
    category: str = "general"
    # For inline templates (fallback only)
    inline: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "TemplateEntry":
        if isinstance(data, str):
            # Simple case: just the filename
            return cls(name=name, file=data)
        return cls(
            name=name,
            file=data.get("file", f"{name}.j2"),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            inline=data.get("inline"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "file": self.file,
            "description": self.description,
            "category": self.category,
        }
        if self.inline:
            result["inline"] = self.inline
        return result


@dataclass
class TemplatesConfig:
    """
    Master Templates Configuration.

    Auto-discovered by SectionLoader -> loads from config/templates.yaml

    Features:
    - Template registry with file paths
    - Lazy loading with caching
    - Jinja2 environment setup
    - Hot-reload support for development
    - Fallback to inline templates if file missing
    """

    section_id: str = "templates"
    source_file: str = "templates.yaml"

    # Template directory (relative to project root)
    template_dir: str = "knowledge/templates"

    # Hot-reload in development
    auto_reload: bool = True

    # Template registry
    templates: Dict[str, TemplateEntry] = field(default_factory=dict)

    # Runtime state (not serialized)
    _env: Optional[Any] = field(default=None, repr=False)
    _cache: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplatesConfig":
        """Create TemplatesConfig from YAML dictionary."""
        templates = {}
        for name, tpl_data in data.get("templates", {}).items():
            templates[name] = TemplateEntry.from_dict(name, tpl_data)

        return cls(
            template_dir=data.get("template_dir", "knowledge/templates"),
            auto_reload=data.get("auto_reload", True),
            templates=templates,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "template_dir": self.template_dir,
            "auto_reload": self.auto_reload,
            "templates": {name: t.to_dict() for name, t in self.templates.items()},
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Check template directory exists
        tpl_path = Path(self.template_dir)
        if not tpl_path.exists():
            errors.append(f"template_dir does not exist: {tpl_path}")

        # Check each registered template file
        for name, entry in self.templates.items():
            file_path = tpl_path / entry.file
            if not file_path.exists() and not entry.inline:
                errors.append(f"Template '{name}' file not found: {file_path}")

        return errors

    def _get_env(self) -> Optional[Any]:
        """Get or create Jinja2 environment."""
        if not HAS_JINJA:
            logger.warning("Jinja2 not installed, template rendering disabled")
            return None

        if self._env is None:
            tpl_path = Path(self.template_dir)
            if tpl_path.exists():
                self._env = Environment(
                    loader=FileSystemLoader(str(tpl_path)),
                    auto_reload=self.auto_reload,
                )
            else:
                logger.warning(f"Template directory not found: {tpl_path}")

        return self._env

    def get_template(self, name: str) -> Optional[Any]:
        """
        Get a template by name.

        Resolution order:
        1. File in template_dir (if exists)
        2. Inline template from config
        3. None (not found)
        """
        if not HAS_JINJA:
            return None

        # Check cache first
        if name in self._cache:
            return self._cache[name]

        entry = self.templates.get(name)
        if not entry:
            logger.debug(f"Template '{name}' not in registry")
            return None

        env = self._get_env()

        # Try file first
        if env:
            try:
                template = env.get_template(entry.file)
                self._cache[name] = template
                return template
            except Exception as e:
                logger.debug(f"Template file '{entry.file}' not found: {e}")

        # Fall back to inline
        if entry.inline:
            from jinja2 import Template

            template = Template(entry.inline)
            self._cache[name] = template
            return template

        return None

    def render(self, name: str, **context) -> Optional[str]:
        """
        Render a template with context.

        Args:
            name: Template name from registry
            **context: Template variables

        Returns:
            Rendered string or None if template not found
        """
        template = self.get_template(name)
        if template is None:
            return None

        try:
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template '{name}': {e}")
            return None

    def list_templates(self) -> Dict[str, str]:
        """List all registered templates with descriptions."""
        return {name: t.description for name, t in self.templates.items()}

    def clear_cache(self) -> None:
        """Clear template cache (for hot-reload)."""
        self._cache.clear()
        self._env = None
