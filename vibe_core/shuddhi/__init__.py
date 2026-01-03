"""
Shuddhi - The Surgical Self-Healing Engine.

Architecture:
1. Analyzers (AST) - Detect violations with line/col coordinates
2. Locator (Bridge) - Map AST coordinates to CST nodes
3. Remedies (CST) - Apply surgical fixes preserving formatting
4. Engine - Orchestrate the Parse -> Transform -> Verify cycle
"""

from vibe_core.shuddhi.engine import ShuddhiEngine
from vibe_core.shuddhi.locator import ASTBridge, CSTLocator

__all__ = [
    "ShuddhiEngine",
    "ASTBridge",
    "CSTLocator",
]
