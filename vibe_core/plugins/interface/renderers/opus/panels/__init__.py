"""
OPUS Panels - Modular panel system for OPUS.md dashboard.

To add a new panel:
1. Create a new file in this directory (e.g., my_panel.py)
2. Implement a class that inherits from BasePanel
3. The panel is automatically discovered and registered

No need to edit the renderer!
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


# OPUS Phase 2: Safety limits for panel scanning
MAX_FILES_TO_SCAN = 500  # Prevent kernel freeze on large codebases
CACHE_TTL_SECONDS = 300  # 5 minutes


class BasePanel(ABC):
    """Base class for OPUS dashboard panels."""

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        self._root = Path(".")

        # OPUS Phase 2: In-memory cache for fast renders
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = CACHE_TTL_SECONDS

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

    # OPUS Phase 2: Caching methods
    def get_cached(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        entry = self._cache.get(key)
        if entry and time.time() - entry["ts"] < self._cache_ttl:
            return entry["data"]
        return None

    def set_cached(self, key: str, data: Any) -> None:
        """Store value in cache with timestamp."""
        self._cache[key] = {"data": data, "ts": time.time()}

    def get_ephemeral(self):
        """
        Get EphemeralStorage from kernel (GAD-000 Safe).

        Returns None if Envoy is not available.
        """
        # GAD-000: Safety Check - Don't assume Envoy exists
        if not hasattr(self.kernel, "envoy"):
            return None

        envoy = getattr(self.kernel, "envoy", None)
        if not envoy:
            return None

        return getattr(envoy, "_ephemeral", None)

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

    def _scan_pattern(self, pattern: str, paths: List[str], use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Scan files for a pattern (e.g., TODO, HACK, FIXME).

        OPUS Phase 2: Now with caching and safety limits.

        Args:
            pattern: Regex pattern to search for
            paths: List of glob patterns to search in
            use_cache: Whether to use cache (default True)

        Returns:
            List of matches with file, line, and text
        """
        # Check cache first (OPUS Phase 2)
        if use_cache:
            cache_key = f"scan:{pattern}:{':'.join(paths)}"
            cached = self.get_cached(cache_key)
            if cached is not None:
                return cached

        import re

        results = []
        files_scanned = 0

        for path_pattern in paths:
            for file_path in self._root.glob(path_pattern):
                # Safety limit (OPUS Phase 2)
                if files_scanned >= MAX_FILES_TO_SCAN:
                    break

                if not file_path.is_file():
                    continue

                files_scanned += 1

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

            # Break outer loop too if limit reached
            if files_scanned >= MAX_FILES_TO_SCAN:
                break

        # Cache the results (OPUS Phase 2)
        if use_cache:
            cache_key = f"scan:{pattern}:{':'.join(paths)}"
            self.set_cached(cache_key, results)

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
