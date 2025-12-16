"""
MANAS Analyzers - Intent generation from system state.

OPUS-032: Modular analyzers for the 51% singularity.
OPUS-041: VAK (The Voice) - CI Monitor via ShellCortex.
OPUS-077: PRATYAYA - Self-falsification via Red Team.

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
"""

from .base import AnalyzerConfig, BaseAnalyzer
from .ci_monitor_analyzer import CIMonitorAnalyzer
from .contract_analyzer import ContractAnalyzer
from .pratyaya_analyzer import PratyayaAnalyzer
from .semantic_analyzer import SemanticAnalyzer

__all__ = [
    "BaseAnalyzer",
    "AnalyzerConfig",
    "ContractAnalyzer",
    "SemanticAnalyzer",
    "CIMonitorAnalyzer",
    "PratyayaAnalyzer",
]
