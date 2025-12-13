"""
MANAS Analyzers - Intent generation from system state.

OPUS-032: Modular analyzers for the 51% singularity.

Each analyzer examines a specific aspect of system state and generates
intents when action is needed.

Architecture:
- BaseAnalyzer: Abstract interface for all analyzers
- ContractAnalyzer: @HARNESS violations → repair intents (50% - homeostasis)
- SemanticAnalyzer: Missing coverage → creation intents (51% - growth)

The 50%/51% distinction:
- 50% analyzers fix what's BROKEN (immune system)
- 51% analyzers create what's MISSING (genesis impulse)
"""

from .base import AnalyzerConfig, BaseAnalyzer
from .contract_analyzer import ContractAnalyzer

__all__ = ["BaseAnalyzer", "AnalyzerConfig", "ContractAnalyzer"]
