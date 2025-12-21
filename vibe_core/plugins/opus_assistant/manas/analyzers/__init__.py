"""
MANAS Analyzers - Intent generation from system state.

OPUS-032: Modular analyzers for the 51% singularity.
OPUS-041: VAK (The Voice) - CI Monitor via ShellCortex.
OPUS-077: PRATYAYA - Self-falsification via Red Team.
OPUS-171: VEDA-4 auto-discovery via AnalyzerLoader.

Each analyzer examines a specific aspect of system state and generates
intents when action is needed.

Architecture:
- BaseAnalyzer: Abstract interface for all analyzers
- ContractAnalyzer: @HARNESS violations → repair intents (50% - homeostasis)
- SemanticAnalyzer: Missing coverage → creation intents (51% - growth)
- CIMonitorAnalyzer: System status → observability intents (OPUS-041)
- PratyayaAnalyzer: Self-mutation testing → security intents (OPUS-077)

The 50%/51%/52% distinction:
- 50% analyzers fix what's BROKEN (immune system)
- 51% analyzers create what's MISSING (genesis impulse)
- 52% analyzers VERIFY the system can defend itself (self-falsification)

Usage:
    # Static imports (for type hints and IDE support)
    from vibe_core.plugins.opus_assistant.manas.analyzers import ContractAnalyzer

    # Auto-discovery (OPUS-171: VEDA-4 pattern - recommended for runtime)
    from vibe_core.plugins.opus_assistant.manas.analyzers import get_all_analyzers
    analyzers = get_all_analyzers(workspace=Path.cwd())
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Base classes (always needed for type hints)
from .base import AnalyzerConfig, BaseAnalyzer

# Static imports for IDE support and backward compatibility
# These are also auto-discovered by AnalyzerLoader
from .ci_monitor_analyzer import CIMonitorAnalyzer
from .contract_analyzer import ContractAnalyzer
from .doc_harness_analyzer import DocHarnessAnalyzer
from .inverse_scan_analyzer import InverseScanAnalyzer
from .pratyaya_analyzer import PratyayaAnalyzer
from .semantic_analyzer import SemanticAnalyzer
from .triage_analyzer import TriageAnalyzer

# =============================================================================
# OPUS-171: VEDA-4 Auto-Discovery (Recommended for Runtime)
# =============================================================================


def get_all_analyzers(
    workspace: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, BaseAnalyzer]:
    """
    Get all analyzers via VEDA-4 auto-discovery.

    This is the RECOMMENDED way to get analyzers at runtime.
    New analyzers are automatically discovered without editing __init__.py.

    Args:
        workspace: Workspace path (default: cwd)
        config: Optional config to pass to analyzers

    Returns:
        Dict mapping analyzer names to instances

    Example:
        analyzers = get_all_analyzers()
        for name, analyzer in analyzers.items():
            intents = analyzer.analyze(state)
    """
    from vibe_core.loaders import AnalyzerLoader

    analyzers, _ = AnalyzerLoader.discover_and_load(
        workspace=workspace,
        config=config,
    )
    return analyzers


def list_analyzers(workspace: Optional[Path] = None) -> List[str]:
    """List all discovered analyzer names via VEDA-4 auto-discovery."""
    from vibe_core.loaders import AnalyzerLoader

    return AnalyzerLoader.list_analyzers(workspace)


__all__ = [
    # Base classes
    "BaseAnalyzer",
    "AnalyzerConfig",
    # Static exports (backward compat)
    "ContractAnalyzer",
    "SemanticAnalyzer",
    "CIMonitorAnalyzer",
    "PratyayaAnalyzer",
    "DocHarnessAnalyzer",
    "TriageAnalyzer",
    "InverseScanAnalyzer",
    # OPUS-171: Auto-discovery helpers
    "get_all_analyzers",
    "list_analyzers",
]
