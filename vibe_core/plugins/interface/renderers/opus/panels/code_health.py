"""
Code Health Panel - Scans for TODO, HACK, FIXME in codebase.

Shows technical debt that needs attention.
"""

from typing import TYPE_CHECKING

from . import BasePanel

if TYPE_CHECKING:
    pass


class CodeHealthPanel(BasePanel):
    """Scans codebase for TODO/HACK/FIXME markers."""

    @property
    def panel_id(self) -> str:
        return "code_health"

    @property
    def title(self) -> str:
        return "Code Health (TODO/HACK/FIXME)"

    @property
    def priority(self) -> int:
        return 10  # Show near top

    def render(self) -> str:
        """Scan and render code health markers."""
        # Scan patterns
        todos = self._scan_pattern(r"#\s*TODO", ["vibe_core/**/*.py"])
        hacks = self._scan_pattern(r"#\s*HACK", ["vibe_core/**/*.py"])
        fixmes = self._scan_pattern(r"#\s*FIXME", ["vibe_core/**/*.py"])

        lines = [f"## {self.title}", ""]

        # Summary
        total = len(todos) + len(hacks) + len(fixmes)
        if total == 0:
            lines.append("_No technical debt markers found_")
            return "\n".join(lines)

        lines.append(f"**Total: {total}** (TODO: {len(todos)}, HACK: {len(hacks)}, FIXME: {len(fixmes)})")
        lines.append("")

        # Critical: HACK and FIXME first
        if hacks or fixmes:
            lines.append("### Critical")
            lines.append("")
            for item in hacks:
                lines.append(f"- **HACK** `{item['file']}:{item['line']}` - {item['text'][:60]}")
            for item in fixmes:
                lines.append(f"- **FIXME** `{item['file']}:{item['line']}` - {item['text'][:60]}")
            lines.append("")

        # TODOs (collapsible if many)
        if todos:
            if len(todos) > 5:
                lines.append("<details>")
                lines.append(f"<summary>TODOs ({len(todos)})</summary>")
                lines.append("")
            else:
                lines.append("### TODOs")
                lines.append("")

            for item in todos[:20]:  # Limit to 20
                lines.append(f"- `{item['file']}:{item['line']}` - {item['text'][:60]}")

            if len(todos) > 20:
                lines.append(f"- _...and {len(todos) - 20} more_")

            if len(todos) > 5:
                lines.append("")
                lines.append("</details>")

        return "\n".join(lines)
