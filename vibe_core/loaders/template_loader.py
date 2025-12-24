"""
TemplateLoader - Jinja2 Template Loading following VEDA-4 Pattern.

Part of the Loaders family (CircuitLoader, PlaybookLoader, TemplateLoader).

VEDA-4 PATTERN:
    SHABDA   → scan_paths for .j2 files
    ARTHA    → parse template, extract metadata from header
    PRATYAYA → create Jinja2 Environment with filters
    KARMA    → render(template_name, **context)

ZERO REDUNDANCY:
    Templates contain STRUCTURE only, not DATA.
    Data comes from existing sources (pyproject.toml, kernel, steward.json).

Usage:
    from vibe_core.loaders import TemplateLoader

    loader = TemplateLoader()
    content = loader.render("readme.md.j2", project=data, agents=list)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Union

# OPUS-301: Lazy jinja2 import (saves ~225ms on boot)
if TYPE_CHECKING:
    from jinja2 import Environment

logger = logging.getLogger("TEMPLATE_LOADER")


class TemplateLoader:
    """
    Jinja2 template loader following UnifiedLoader pattern.

    Default scan paths:
        - knowledge/templates/
        - knowledge/interface/templates/
    """

    DEFAULT_SCAN_PATHS = [
        "knowledge/templates",
        "knowledge/interface/templates",
    ]

    def __init__(
        self,
        template_dir: Optional[Union[str, Path]] = None,
        scan_paths: Optional[List[Union[str, Path]]] = None,
    ):
        self._project_root = self._find_project_root()
        self._template_dirs: List[Path] = []
        self._env: Optional[Environment] = None

        if template_dir:
            self._template_dirs = [self._resolve_path(template_dir)]
        else:
            paths = scan_paths or self.DEFAULT_SCAN_PATHS
            for p in paths:
                resolved = self._resolve_path(p)
                if resolved.exists():
                    self._template_dirs.append(resolved)

        if not self._template_dirs:
            default_dir = self._project_root / "knowledge" / "templates"
            default_dir.mkdir(parents=True, exist_ok=True)
            self._template_dirs = [default_dir]

    def _find_project_root(self) -> Path:
        """Find project root via pyproject.toml."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "pyproject.toml").exists():
                return parent
        return current

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve path relative to project root."""
        p = Path(path)
        return p if p.is_absolute() else self._project_root / p

    @property
    def env(self) -> "Environment":
        """Get or create Jinja2 environment."""
        if self._env is None:
            from jinja2 import Environment, FileSystemLoader
            self._env = Environment(
                loader=FileSystemLoader([str(d) for d in self._template_dirs]),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            self._register_filters()
        return self._env

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters."""
        e = self._env

        # Collection
        e.filters["count"] = lambda x: len(x) if x else 0
        e.filters["first_n"] = lambda x, n: list(x)[:n] if x else []

        # String
        e.filters["truncate_str"] = lambda s, n: (str(s)[:n] + "...") if len(str(s)) > n else str(s)

        # Agent helpers
        e.filters["agent_names"] = lambda agents: [
            getattr(a, "name", str(a)) for a in (agents.values() if hasattr(agents, "values") else agents)
        ]

        # Markdown
        e.filters["md_link"] = lambda text, url: f"[{text}]({url})"

    def render(self, template_name: str, **context: Any) -> str:
        """Render template with context."""
        from jinja2 import TemplateNotFound
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            raise

    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        for d in self._template_dirs:
            if (d / template_name).exists():
                return True
        return False

    def list_templates(self, pattern: str = "*.j2") -> List[str]:
        """List available templates."""
        templates = []
        for d in self._template_dirs:
            if d.exists():
                templates.extend(f.name for f in d.glob(pattern))
        return sorted(set(templates))


# Singleton
_loader: Optional[TemplateLoader] = None


def get_template_loader() -> TemplateLoader:
    """Get shared loader instance."""
    global _loader
    if _loader is None:
        _loader = TemplateLoader()
    return _loader


def render_template(template_name: str, **context: Any) -> str:
    """Convenience function."""
    return get_template_loader().render(template_name, **context)
