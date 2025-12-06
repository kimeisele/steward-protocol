"""
Blockers Panel - Bidirectional section for human/AI collaboration.

This panel preserves user content between re-renders.
Follows the bidirectional pattern from config.
"""

from typing import Any, Dict, List

from .base_panel import OpusPanel


class BlockersPanel(OpusPanel):
    """
    Blockers Panel - Bidirectional.

    Content is preserved across re-renders.
    AI can write, human can edit/approve.
    """

    @property
    def panel_id(self) -> str:
        return "blockers"

    @property
    def priority(self) -> int:
        return 20  # After main content

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render blockers section with bidirectional preservation."""
        bidir_sections = config.get("bidirectional_sections", [])

        # Find blockers section config
        blockers_config = self._find_section_config(bidir_sections, "## Blockers")
        default_content = blockers_config.get("default_content", "_No blockers identified._")

        # Get existing content from context (set by OpusRenderer)
        existing_content = context.get("existing_opus_content", "")

        # Parse preserved content
        preserved = self._parse_bidirectional(
            existing_content,
            blockers_config.get("marker", "## Blockers"),
            blockers_config.get("end_marker", "## Next Actions"),
        )

        content = preserved if preserved else default_content

        return f"""## Blockers

<!-- BIDIRECTIONAL: AI writes, human reviews -->
{content}

---
"""

    def _find_section_config(self, sections: List[Dict], marker: str) -> Dict[str, Any]:
        """Find config for a specific section by marker."""
        for section in sections:
            if section.get("marker", "") == marker:
                return section
        return {}

    def _parse_bidirectional(self, content: str, start_marker: str, end_marker: str) -> str:
        """Parse preserved content from existing file."""
        try:
            if start_marker in content and end_marker in content:
                start = content.index(start_marker) + len(start_marker)
                end = content.index(end_marker)
                parsed = content[start:end].strip()
                # Remove HTML comments
                lines = [line for line in parsed.split("\n") if not line.strip().startswith("<!--")]
                result = "\n".join(lines).strip()
                if result:
                    return result
        except Exception:
            pass
        return ""


class NextActionsPanel(OpusPanel):
    """
    Next Actions Panel - Bidirectional.

    AI proposes actions, human approves with [x].
    """

    @property
    def panel_id(self) -> str:
        return "next_actions"

    @property
    def priority(self) -> int:
        return 21  # Right after blockers

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render next actions section."""
        bidir_sections = config.get("bidirectional_sections", [])

        # Find next actions section config
        actions_config = self._find_section_config(bidir_sections, "## Next Actions")
        default_content = actions_config.get("default_content", "1. [ ] Define next actions")

        # Get existing content
        existing_content = context.get("existing_opus_content", "")

        # Parse preserved content
        preserved = self._parse_bidirectional(
            existing_content,
            actions_config.get("marker", "## Next Actions"),
            actions_config.get("end_marker", "## Extraction Candidates"),
        )

        content = preserved if preserved else default_content

        return f"""## Next Actions

<!-- BIDIRECTIONAL: AI proposes, human approves with [x] -->
{content}

---
"""

    def _find_section_config(self, sections: List[Dict], marker: str) -> Dict[str, Any]:
        """Find config for a specific section by marker."""
        for section in sections:
            if section.get("marker", "") == marker:
                return section
        return {}

    def _parse_bidirectional(self, content: str, start_marker: str, end_marker: str) -> str:
        """Parse preserved content from existing file."""
        try:
            if start_marker in content and end_marker in content:
                start = content.index(start_marker) + len(start_marker)
                end = content.index(end_marker)
                parsed = content[start:end].strip()
                lines = [line for line in parsed.split("\n") if not line.strip().startswith("<!--")]
                result = "\n".join(lines).strip()
                if result:
                    return result
        except Exception:
            pass
        return ""
