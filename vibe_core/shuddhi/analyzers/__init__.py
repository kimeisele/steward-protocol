"""
OPUS-212: Shuddhi Analyzers - The Diagnostic Tools.

NOTE: Security scanning is handled by Watchman's StandardsInspectionTool
(vibe_core/cartridges/system/watchman/tools/standards_inspection.py)
with rules defined in config/standards.yaml.

This module contains ONLY analyzers that Watchman doesn't provide:
- LCOM4: Cohesion analysis for God Class detection (future use)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x50a92813"  # GenesisByte: parampara % 37 == 0

from vibe_core.shuddhi.analyzers.lcom4 import (
    LCOM4GraphBuilder,
    LCOM4Result,
    calculate_lcom4,
    find_god_classes,
)
from vibe_core.shuddhi.analyzers.lcom4 import (
    analyze_file as analyze_file_lcom4,
)

__all__ = [
    # LCOM4 - NOT for automatic refactoring yet, just metrics
    "LCOM4Result",
    "LCOM4GraphBuilder",
    "calculate_lcom4",
    "analyze_file_lcom4",
    "find_god_classes",
]
