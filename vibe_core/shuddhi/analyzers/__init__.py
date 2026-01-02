"""
OPUS-212: Shuddhi Analyzers - The Diagnostic Tools.

This module contains AST-based analyzers that detect violations.
The analyzers work with the CSTLocator bridge to enable surgical fixes.
"""

from vibe_core.shuddhi.analyzers.lcom4 import (
    LCOM4GraphBuilder,
    LCOM4Result,
    calculate_lcom4,
    find_god_classes,
)
from vibe_core.shuddhi.analyzers.lcom4 import (
    analyze_file as analyze_file_lcom4,
)
from vibe_core.shuddhi.analyzers.narasimha import (
    NarasimhaGuardrail,
    SecurityViolation,
    Severity,
    analyze_source,
    get_critical_violations,
    get_fixable_violations,
)
from vibe_core.shuddhi.analyzers.narasimha import (
    analyze_file as analyze_file_security,
)

__all__ = [
    # LCOM4
    "LCOM4Result",
    "LCOM4GraphBuilder",
    "calculate_lcom4",
    "analyze_file_lcom4",
    "find_god_classes",
    # Narasimha
    "NarasimhaGuardrail",
    "SecurityViolation",
    "Severity",
    "analyze_file_security",
    "analyze_source",
    "get_critical_violations",
    "get_fixable_violations",
]
