"""
OPUS.md Generator - Auto-generates OPUS.md with section preservation.

OPUS-029 Phase 1: The plugin generates OPUS.md but RESPECTS existing content.

Architecture:
- Plugin generates DATA (this module)
- Interface plugin RENDERS to markdown (not our job!)
- OPUS.md in root is the "UI" (GAD-000: transparent, LLM-readable)

Section Preservation:
- Auto-generated sections: Replaced on every boot
- Human sections (<!-- HUMAN -->): NEVER touched
- AI sections (<!-- AI -->): NEVER touched
- Unknown sections: Preserved

Section Markers:
    <!-- @AUTO-GENERATED START -->
    ... auto content ...
    <!-- @AUTO-GENERATED END -->

    <!-- @HUMAN START -->
    ... human notes, preserved forever ...
    <!-- @HUMAN END -->

    <!-- @AI START -->
    ... AI assistant notes, preserved ...
    <!-- @AI END -->
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x73b1c66c"  # GenesisByte: parampara % 37 == 0

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class OpusSection:
    """A section of OPUS.md content."""

    name: str
    content: str
    section_type: str  # "auto", "human", "ai", "unknown"
    preserved: bool = False  # True if this section was preserved from existing file


@dataclass
class OpusData:
    """
    Data structure for OPUS.md generation.

    This is what the plugin produces. The RENDERER (interface plugin)
    converts this to markdown. We do NOT render here!
    """

    # Metadata
    generated_at: str
    workspace: str
    version: str = "1.0.0"

    # Verification results
    verification: Dict[str, Any] = field(default_factory=dict)

    # Drift detection results
    drift: Dict[str, Any] = field(default_factory=dict)

    # Plugin status
    plugins: List[Dict[str, Any]] = field(default_factory=list)

    # Preserved sections from existing OPUS.md
    preserved_sections: Dict[str, str] = field(default_factory=dict)

    # Errors/warnings
    warnings: List[str] = field(default_factory=list)


class OpusGenerator:
    """
    Generates OPUS.md data with section preservation.

    IMPORTANT: This class produces DATA, not markdown!
    The interface plugin is responsible for rendering.

    Usage:
        generator = OpusGenerator(workspace_root=Path("."))
        data = generator.generate()
        # Pass 'data' to interface plugin for rendering
    """

    # Section markers
    AUTO_START = "<!-- @AUTO-GENERATED START -->"
    AUTO_END = "<!-- @AUTO-GENERATED END -->"
    HUMAN_START = "<!-- @HUMAN START -->"
    HUMAN_END = "<!-- @HUMAN END -->"
    AI_START = "<!-- @AI START -->"
    AI_END = "<!-- @AI END -->"

    def __init__(self, workspace_root: Path):
        """
        Initialize generator.

        Args:
            workspace_root: Project root directory
        """
        self._root = Path(workspace_root)
        self._opus_path = self._root / "OPUS.md"

    def generate(self, include_verification: bool = True) -> OpusData:
        """
        Generate OPUS.md data.

        This collects all data needed for OPUS.md but does NOT render it.
        The interface plugin handles rendering.

        Args:
            include_verification: Whether to run verification (slower)

        Returns:
            OpusData with all information needed for rendering
        """
        data = OpusData(
            generated_at=datetime.utcnow().isoformat(),
            workspace=str(self._root),
        )

        # Preserve existing sections
        if self._opus_path.exists():
            data.preserved_sections = self._extract_preserved_sections()
            if data.preserved_sections:
                data.warnings.append(f"Preserved {len(data.preserved_sections)} sections from existing OPUS.md")

        # Run verification if requested
        if include_verification:
            from .verification_logic import VerificationEngine

            engine = VerificationEngine(workspace_root=self._root)
            data.verification = engine.run_verification(quick=True)

        # Collect plugin status
        data.plugins = self._collect_plugin_status()

        return data

    def _extract_preserved_sections(self) -> Dict[str, str]:
        """
        Extract HUMAN and AI sections from existing OPUS.md.

        These sections are NEVER overwritten.

        Returns:
            Dict mapping section name to content
        """
        preserved = {}

        try:
            content = self._opus_path.read_text()
        except Exception:
            return preserved

        # Extract HUMAN sections
        human_pattern = rf"{re.escape(self.HUMAN_START)}(.*?){re.escape(self.HUMAN_END)}"
        for i, match in enumerate(re.finditer(human_pattern, content, re.DOTALL)):
            section_content = match.group(1).strip()
            if section_content:
                preserved[f"human_{i}"] = section_content

        # Extract AI sections
        ai_pattern = rf"{re.escape(self.AI_START)}(.*?){re.escape(self.AI_END)}"
        for i, match in enumerate(re.finditer(ai_pattern, content, re.DOTALL)):
            section_content = match.group(1).strip()
            if section_content:
                preserved[f"ai_{i}"] = section_content

        return preserved

    def _collect_plugin_status(self) -> List[Dict[str, Any]]:
        """
        Collect status of all plugins.

        Returns:
            List of plugin status dicts
        """
        plugins = []
        plugins_dir = self._root / "vibe_core" / "plugins"

        if not plugins_dir.exists():
            return plugins

        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            if plugin_dir.name.startswith("_"):
                continue

            manifest_path = plugin_dir / "manifest.json"
            if not manifest_path.exists():
                continue

            try:
                import json

                manifest = json.loads(manifest_path.read_text())
                plugins.append(
                    {
                        "id": manifest.get("id", plugin_dir.name),
                        "name": manifest.get("name", plugin_dir.name),
                        "version": manifest.get("version", "?"),
                        "enabled": manifest.get("enabled", True),
                        "has_tests": (plugin_dir / "tests").exists(),
                    }
                )
            except Exception:
                plugins.append(
                    {
                        "id": plugin_dir.name,
                        "name": plugin_dir.name,
                        "version": "?",
                        "enabled": False,
                        "error": "Failed to load manifest",
                    }
                )

        return sorted(plugins, key=lambda p: p.get("id", ""))

    def get_preserved_sections(self) -> Dict[str, str]:
        """
        Get preserved sections from existing OPUS.md.

        Public API for interface plugin to access preserved content.
        """
        if self._opus_path.exists():
            return self._extract_preserved_sections()
        return {}

    def has_existing_opus(self) -> bool:
        """Check if OPUS.md already exists."""
        return self._opus_path.exists()
