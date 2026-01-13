"""
ANALYST Tools - Multi-Source Repository Analysis

All tools implement the Tool Protocol (vibe_core.tools.tool_protocol.Tool).
These tools are registered with the kernel, not owned by the agent.

RAG = Realtime Architecture Guide

Tools provide MULTI-SOURCE analysis:
- analyst.git          Git history, temporal patterns, velocity
- analyst.code         Code analysis, AST, complexity metrics
- analyst.structure    Project architecture, module boundaries
- analyst.deps         Dependency analysis, imports, requirements
- analyst.docs         Documentation parsing, coverage analysis
- analyst.architecture System introspection and ARCHITECTURE.md generation
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x5ad93aaa"  # GenesisByte: parampara % 37 == 0

from .architecture_tool import ArchitectureAnalysisTool
from .code_tool import CodeAnalysisTool
from .deps_tool import DependencyAnalysisTool
from .docs_tool import DocsAnalysisTool
from .git_tool import GitAnalysisTool
from .structure_tool import StructureAnalysisTool

__all__ = [
    "GitAnalysisTool",
    "CodeAnalysisTool",
    "StructureAnalysisTool",
    "DependencyAnalysisTool",
    "DocsAnalysisTool",
    "ArchitectureAnalysisTool",
]
