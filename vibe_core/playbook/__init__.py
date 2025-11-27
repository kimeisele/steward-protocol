"""
Playbook Package (OPERATION SEMANTIC MOTOR)
============================================

Graph-based workflow orchestration system for VIBE Agency.

This package contains:
- Semantic actions (the nodes in the graph)
- Workflow definitions (the edges and dependencies)
- Workflow executor (orchestration engine)

Architecture:
  Semantic Actions → Workflows → Graph Executor

The key insight: INTENT (what to do) is separate from EXECUTION (how to do it).
This enables dynamic agent assignment, custom domains, and reusable workflows.
"""

from vibe_core.playbook.executor import GraphExecutor

__version__ = "0.1"
__all__ = ["GraphExecutor"]
