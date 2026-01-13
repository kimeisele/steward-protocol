"""
Prompts Configuration - LLM prompt registry and loader.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/prompts/
    ARTHA: Parsed from config/prompts.yaml
    PRATYAYA: Validated (prompt files must exist)
    KARMA: Instantiated as PromptsConfig dataclass with lazy loading

This section eliminates 38 inline f-string prompt violations:
    - deterministic_executor.py: context extraction prompts
    - blueprint_generator.py: parameter extraction prompts
    - circuit_engine.py: agent routing prompts
    - degradation_chain.py: fallback prompts
    - boot_sequence.py: system prompts
    - operator_adapter.py: operator prompts

Prompts are loaded from knowledge/prompts/*.yaml or *.j2
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0x80b8b1b9"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, Template

    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    Environment = None
    FileSystemLoader = None
    Template = None

logger = logging.getLogger(__name__)


@dataclass
class PromptEntry:
    """Single prompt configuration entry."""

    name: str
    file: str
    description: str = ""
    category: str = "general"
    # Model hint (for graceful degradation)
    model_hint: Optional[str] = None
    # Max tokens hint
    max_tokens: Optional[int] = None
    # Temperature hint
    temperature: Optional[float] = None
    # For inline prompts (fallback only)
    inline: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "PromptEntry":
        if isinstance(data, str):
            # Simple case: just the filename
            return cls(name=name, file=data)
        return cls(
            name=name,
            file=data.get("file", f"{name}.j2"),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            model_hint=data.get("model_hint"),
            max_tokens=data.get("max_tokens"),
            temperature=data.get("temperature"),
            inline=data.get("inline"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "file": self.file,
            "description": self.description,
            "category": self.category,
        }
        if self.model_hint:
            result["model_hint"] = self.model_hint
        if self.max_tokens:
            result["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.inline:
            result["inline"] = self.inline
        return result


@dataclass
class PromptsConfig:
    """
    Master Prompts Configuration.

    Auto-discovered by SectionLoader -> loads from config/prompts.yaml

    Features:
    - Prompt registry with file paths
    - Lazy loading with caching
    - Jinja2 template support for dynamic prompts
    - Model hints for graceful degradation
    - Fallback to inline prompts if file missing
    """

    section_id: str = "prompts"
    source_file: str = "prompts.yaml"

    # Prompt directory (relative to project root)
    prompt_dir: str = "knowledge/prompts"

    # Hot-reload in development
    auto_reload: bool = True

    # Prompt registry
    prompts: Dict[str, PromptEntry] = field(default_factory=dict)

    # Runtime state (not serialized)
    _env: Optional[Any] = field(default=None, repr=False)
    _cache: Dict[str, str] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptsConfig":
        """Create PromptsConfig from YAML dictionary."""
        prompts = {}
        for name, prompt_data in data.get("prompts", {}).items():
            prompts[name] = PromptEntry.from_dict(name, prompt_data)

        return cls(
            prompt_dir=data.get("prompt_dir", "knowledge/prompts"),
            auto_reload=data.get("auto_reload", True),
            prompts=prompts,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "prompt_dir": self.prompt_dir,
            "auto_reload": self.auto_reload,
            "prompts": {name: p.to_dict() for name, p in self.prompts.items()},
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Check prompt directory exists
        prompt_path = Path(self.prompt_dir)
        if not prompt_path.exists():
            errors.append(f"prompt_dir does not exist: {prompt_path}")

        # Check each registered prompt file
        for name, entry in self.prompts.items():
            file_path = prompt_path / entry.file
            if not file_path.exists() and not entry.inline:
                errors.append(f"Prompt '{name}' file not found: {file_path}")

        return errors

    def _get_env(self) -> Optional[Any]:
        """Get or create Jinja2 environment."""
        if not HAS_JINJA:
            logger.warning("Jinja2 not installed, prompt templating disabled")
            return None

        if self._env is None:
            prompt_path = Path(self.prompt_dir)
            if prompt_path.exists():
                self._env = Environment(
                    loader=FileSystemLoader(str(prompt_path)),
                    auto_reload=self.auto_reload,
                )
            else:
                logger.warning(f"Prompt directory not found: {prompt_path}")

        return self._env

    def get_prompt(self, name: str, **context) -> Optional[str]:
        """
        Get a prompt by name, optionally with context.

        Resolution order:
        1. File in prompt_dir (if exists) - rendered with context if .j2
        2. Inline prompt from config
        3. None (not found)

        Args:
            name: Prompt name from registry
            **context: Template variables for .j2 prompts

        Returns:
            Prompt string or None if not found
        """
        entry = self.prompts.get(name)
        if not entry:
            logger.debug(f"Prompt '{name}' not in registry")
            return None

        # Check cache (only for static prompts without context)
        cache_key = f"{name}:{hash(frozenset(context.items()))}" if context else name
        if cache_key in self._cache:
            return self._cache[cache_key]

        prompt_path = Path(self.prompt_dir) / entry.file

        # Try file first
        if prompt_path.exists():
            if entry.file.endswith(".j2") and HAS_JINJA:
                # Jinja2 template
                env = self._get_env()
                if env:
                    try:
                        template = env.get_template(entry.file)
                        result = template.render(**context)
                        if not context:  # Cache static results
                            self._cache[cache_key] = result
                        return result
                    except Exception as e:
                        logger.error(f"Error rendering prompt '{name}': {e}")
            else:
                # Plain text
                result = prompt_path.read_text()
                self._cache[cache_key] = result
                return result

        # Fall back to inline
        if entry.inline:
            if HAS_JINJA and "{" in entry.inline:
                from jinja2 import Template

                try:
                    result = Template(entry.inline).render(**context)
                    return result
                except Exception as e:
                    logger.error(f"Error rendering inline prompt '{name}': {e}")
            return entry.inline

        return None

    def get_entry(self, name: str) -> Optional[PromptEntry]:
        """Get prompt entry for metadata (model_hint, max_tokens, etc.)."""
        return self.prompts.get(name)

    def list_prompts(self) -> Dict[str, str]:
        """List all registered prompts with descriptions."""
        return {name: p.description for name, p in self.prompts.items()}

    def list_by_category(self, category: str) -> List[str]:
        """List prompts in a category."""
        return [name for name, p in self.prompts.items() if p.category == category]

    def clear_cache(self) -> None:
        """Clear prompt cache (for hot-reload)."""
        self._cache.clear()
        self._env = None
