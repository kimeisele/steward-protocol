"""
Architecture Plans Panel - Lists OPUS docs from filesystem.

NO manifest.json dependency. Reads directly from docs/architecture/OPUS/.
"""

from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

from . import BasePanel

if TYPE_CHECKING:
    pass


class ArchitecturePlansPanel(BasePanel):
    """Lists architecture plans directly from docs/architecture/OPUS/."""

    @property
    def panel_id(self) -> str:
        return "architecture_plans"

    @property
    def title(self) -> str:
        return "Architecture Plans"

    @property
    def priority(self) -> int:
        return 5

    def _get_opus_docs(self) -> List[Tuple[str, Path]]:
        """Get all .md files from docs/architecture/OPUS/, sorted by name."""
        opus_dir = self._root / "docs/architecture/OPUS"
        if not opus_dir.exists():
            return []

        docs = []
        for f in sorted(opus_dir.glob("*.md")):
            # Skip index/readme type files
            if f.name.lower() in ("readme.md", "index.md", "008-index.md"):
                continue
            docs.append((f.stem, f))
        return docs

    def render(self) -> str:
        """Render architecture plans from filesystem."""
        docs = self._get_opus_docs()

        lines = [f"## {self.title}", ""]

        if not docs:
            lines.append("_No OPUS docs found in docs/architecture/OPUS/_")
            return "\n".join(lines)

        lines.append(f"**{len(docs)} documents** in `docs/architecture/OPUS/`")
        lines.append("")

        for name, path in docs:
            rel_path = f"docs/architecture/OPUS/{path.name}"
            lines.append(f"- [{name}]({rel_path})")

        return "\n".join(lines)
