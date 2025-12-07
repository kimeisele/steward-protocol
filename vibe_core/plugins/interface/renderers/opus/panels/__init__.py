"""
OPUS Panels - Modular panel system for OPUS.md dashboard.

To add a new panel:
1. Create a new file in this directory (e.g., my_panel.py)
2. Implement a class that inherits from BasePanel
3. The panel is automatically discovered and registered

No need to edit the renderer!
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class BasePanel(ABC):
    """Base class for OPUS dashboard panels."""

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self._root = Path(".")

    @property
    @abstractmethod
    def panel_id(self) -> str:
        """Unique panel ID (used in data source: opus.{panel_id})."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Panel title shown in markdown."""
        pass

    @property
    def priority(self) -> int:
        """Lower = shown first. Default 50."""
        return 50

    @abstractmethod
    def render(self) -> str:
        """Render panel content as markdown."""
        pass

    # Utility methods
    def _count_loc(self, path: str) -> int:
        """Count lines in a file."""
        try:
            full_path = self._root / path
            if full_path.exists():
                return len(full_path.read_text().splitlines())
        except Exception:
            pass
        return 0

    def _scan_pattern(self, pattern: str, paths: List[str]) -> List[Dict[str, Any]]:
        """Scan files for a pattern (e.g., TODO, HACK, FIXME)."""
        import re

        results = []

        for path_pattern in paths:
            for file_path in self._root.glob(path_pattern):
                if not file_path.is_file():
                    continue
                try:
                    content = file_path.read_text()
                    for i, line in enumerate(content.splitlines(), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append(
                                {
                                    "file": str(file_path.relative_to(self._root)),
                                    "line": i,
                                    "text": line.strip()[:80],
                                }
                            )
                except Exception:
                    pass

        return results


def discover_panels(kernel: "RealVibeKernel") -> List[BasePanel]:
    """Discover and instantiate all panels in this directory."""
    import importlib
    import pkgutil

    panels = []
    panels_dir = Path(__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(panels_dir)]):
        if module_name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePanel) and attr is not BasePanel:
                    panels.append(attr(kernel))
        except Exception:
            pass

    # Sort by priority
    panels.sort(key=lambda p: p.priority)
    return panels
