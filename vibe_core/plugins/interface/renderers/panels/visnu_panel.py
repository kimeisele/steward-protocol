"""
VISNU Panel - Kernel LOC tracking and extraction progress.

This is ONE panel that can be hot-swapped or disabled.
The config for this panel lives in config/opus.yaml under 'visnu:'.
"""

from pathlib import Path
from typing import Any, Dict, List

from .base_panel import OpusPanel


class VisnuPanel(OpusPanel):
    """
    VISNU Kernel Status Panel.

    Tracks:
    - Primary file LOC (kernel_impl.py)
    - Extracted modules LOC
    - Progress toward target
    """

    @property
    def panel_id(self) -> str:
        return "visnu"

    @property
    def section_id(self) -> str:
        return "visnu"  # Config section in opus.yaml

    @property
    def priority(self) -> int:
        return 0  # First panel

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render VISNU kernel status section."""
        visnu = config.get("visnu", {})
        tracked = config.get("tracked_files", {})

        # Get targets from config
        target_loc = visnu.get("target_loc", 1008)
        acceptable_loc = visnu.get("acceptable_loc", 1080)
        start_loc = visnu.get("start_loc", 1705)

        # Get primary file
        primary = tracked.get("primary", {})
        primary_path = primary.get("path", "vibe_core/kernel_impl.py")
        kernel_loc = self._count_loc(Path(primary_path))

        # Store in context for other panels
        context["kernel_loc"] = kernel_loc
        context["target_loc"] = target_loc

        # Get extracted files
        extracted_files = tracked.get("extracted", [])
        extracted_metrics = self._get_extracted_metrics(extracted_files)
        total_extracted = sum(m["loc"] for m in extracted_metrics)

        # Calculate status
        remaining = kernel_loc - target_loc
        if kernel_loc <= target_loc:
            status = "COMPLETE"
        elif kernel_loc <= acceptable_loc:
            status = "ACCEPTABLE"
        else:
            status = "IN_PROGRESS"

        # Progress bar
        progress_pct = max(0, min(100, int(100 * (start_loc - kernel_loc) / (start_loc - target_loc))))
        bar_filled = int(40 * progress_pct / 100)

        # Build extracted files table
        extracted_lines = self._format_extracted_table(extracted_metrics, total_extracted)

        return f"""## VISNU Kernel Status

| Metric | Current | Target | Delta | Status |
|--------|---------|--------|-------|--------|
| `{primary_path}` | **{kernel_loc}** LOC | {target_loc} | {remaining:+d} | {status} |

### Extracted Modules

| Module | LOC | Path |
|--------|-----|------|
{extracted_lines}
| **Total Extracted** | **{total_extracted}** LOC | - |

### Progress

```
[{"=" * bar_filled}{"." * (40 - bar_filled)}] {progress_pct}%
Target: {target_loc} | Acceptable: {acceptable_loc} | Current: {kernel_loc}
```

---
"""

    def _get_extracted_metrics(self, extracted_files: List[Dict]) -> List[Dict[str, Any]]:
        """Get LOC metrics for extracted files."""
        metrics = []
        for ef in extracted_files:
            path = ef.get("path", "")
            loc = self._count_loc(Path(path))
            metrics.append(
                {
                    "path": path,
                    "label": ef.get("label", path),
                    "loc": loc,
                }
            )
        return metrics

    def _format_extracted_table(self, metrics: List[Dict], total: int) -> str:
        """Format extracted modules as table rows."""
        lines = []
        for m in metrics:
            lines.append(f"| `{m['label']}` | {m['loc']} LOC | `{m['path']}` |")
        return "\n".join(lines)
