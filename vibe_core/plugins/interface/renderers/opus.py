"""
OPUS Renderer - Architecture Operations Dashboard

Bidirectional workspace for AI-driven architecture operations.
Reads from docs/architecture/OPUS/manifest.json and renders OPUS.md.

Features:
- Real-time kernel LOC tracking
- Phase status from manifest
- Blockers section (AI can write)
- Next actions (AI proposes, human approves)
- Links to analysis circuits
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPUS")


class OpusRenderer(BaseRenderer):
    """Renders OPUS.md - AI workspace for architecture operations."""

    def __init__(self, kernel: "RealVibeKernel", config: Dict[str, Any] = None):
        super().__init__(kernel)
        self.config = config or {}
        self.manifest_path = Path("docs/architecture/OPUS/manifest.json")
        self.kernel_path = Path("vibe_core/kernel_impl.py")

    @property
    def name(self) -> str:
        """Unique name of the renderer."""
        return "opus"

    def _get_kernel_loc(self) -> int:
        """Get current kernel lines of code."""
        try:
            if self.kernel_path.exists():
                return len(self.kernel_path.read_text().splitlines())
        except Exception as e:
            logger.warning(f"Could not count kernel LOC: {e}")
        return 0

    def _load_manifest(self) -> Dict[str, Any]:
        """Load OPUS manifest."""
        try:
            if self.manifest_path.exists():
                return json.loads(self.manifest_path.read_text())
        except Exception as e:
            logger.warning(f"Could not load OPUS manifest: {e}")
        return {}

    def _parse_existing_blockers(self, content: str) -> str:
        """Extract user-written blockers from existing OPUS.md."""
        # Preserve content between Blockers and Next Actions
        try:
            if "## Blockers" in content and "## Next Actions" in content:
                start = content.index("## Blockers")
                end = content.index("## Next Actions")
                blockers_section = content[start:end]
                # Extract just the content after the header
                lines = blockers_section.split("\n")[2:]  # Skip header and comment
                user_blockers = "\n".join(l for l in lines if l.strip() and not l.startswith("<!--"))
                return user_blockers if user_blockers.strip() else "None currently."
        except Exception:
            pass
        return "None currently."

    def _parse_existing_actions(self, content: str) -> str:
        """Extract user-written actions from existing OPUS.md."""
        try:
            if "## Next Actions" in content and "## Available Circuits" in content:
                start = content.index("## Next Actions")
                end = content.index("## Available Circuits")
                actions_section = content[start:end]
                lines = actions_section.split("\n")[2:]
                user_actions = "\n".join(l for l in lines if l.strip() and not l.startswith("<!--"))
                return user_actions if user_actions.strip() else "1. [ ] No actions defined"
        except Exception:
            pass
        return "1. [ ] No actions defined"

    def render(self) -> Optional[str]:
        """Render OPUS.md content."""
        manifest = self._load_manifest()
        kernel_loc = self._get_kernel_loc()
        target_loc = manifest.get("goals", {}).get("kernel_loc_target", 1008)

        # Read existing content for bidirectional preservation
        existing_content = ""
        output_path = Path(self.config.get("output", "OPUS.md"))
        if output_path.exists():
            existing_content = output_path.read_text()

        blockers = self._parse_existing_blockers(existing_content)
        next_actions = self._parse_existing_actions(existing_content)

        # Calculate status
        if kernel_loc <= target_loc:
            status = "COMPLETE"
        elif kernel_loc <= target_loc + 100:
            status = "ALMOST"
        else:
            status = "IN_PROGRESS"

        # Get extraction history from manifest
        phases = manifest.get("phases", [])
        extraction_log = manifest.get("extraction_log", [])

        # Build phase checklist
        phase_lines = []
        for phase in phases:
            checkbox = "[x]" if phase.get("status") == "complete" else "[ ]"
            delta = phase.get("loc_delta", "?")
            phase_lines.append(f"- {checkbox} {phase.get('name', 'Unknown')} ({delta} LOC)")

        # Build extraction log table
        log_lines = [
            "| Date | Component | LOC Before | LOC After | Delta |",
            "|------|-----------|------------|-----------|-------|",
        ]
        for entry in extraction_log[-10:]:  # Last 10 entries
            log_lines.append(
                f"| {entry.get('date', '?')} | {entry.get('component', '?')} | "
                f"{entry.get('loc_before', '?')} | {entry.get('loc_after', '?')} | "
                f"{entry.get('delta', '?')} |"
            )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# OPUS - Architecture Operations Dashboard

> Bidirectional workspace for kernel refactoring and architecture decisions.
> This file is rendered by InterfacePlugin and can trigger circuits.

## Current Focus: VISNU Kernel Extraction

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| kernel_impl.py LOC | {kernel_loc} | {target_loc} | {status} |
| Remaining to extract | {kernel_loc - target_loc} | 0 | {"DONE" if kernel_loc <= target_loc else "PENDING"} |

## Phase Status

{chr(10).join(phase_lines) if phase_lines else "No phases defined in manifest."}

## Extraction Log

{chr(10).join(log_lines)}

## Blockers

<!-- AI can write here to flag issues -->
{blockers}

## Next Actions

<!-- AI proposes, human approves -->
{next_actions}

## Available Circuits

<!-- Links to analysis playbooks -->
- `steward run kernel-analysis` - Analyze kernel structure
- `steward run loc-count` - Count lines of code
- `steward run test-suite` - Run tests with timeout

---
*Rendered by: OpusRenderer | Last updated: {timestamp}*
"""


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OpusRenderer:
    """Factory function for renderer discovery."""
    return OpusRenderer(kernel, config)
