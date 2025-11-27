"""
Specialist Agents - HAP Framework (Hierarchical Agent Pattern)
================================================================

Base classes and registry for phase-specific specialist agents.

Classes:
  - BaseAgent: Agent with persona, command execution, and knowledge access
  - BaseSpecialist: Abstract base class for all specialists
  - AgentRegistry: Global registry for specialist instances
  - ExecutionResult: Result of command execution
  - KnowledgeResult: Result of knowledge base queries
"""

from .base_agent import BaseAgent, ExecutionResult, KnowledgeResult
from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from .registry import AgentRegistry

# Specialist implementations (placeholder classes for Phase 2)
# TODO: Implement full specialization in v2.0
# Why: These are placeholder subclasses created during Phase 2 migration
# to support the HAP (Hierarchical Agent Pattern) framework architecture.
# Currently they inherit BaseSpecialist without custom logic.
# Phase 3: These remain as-is (no removal, for backward compatibility)
# Phase 4: Either implement specialized logic or remove if unused


class PlanningSpecialist(BaseSpecialist):
    """Planning phase specialist agent (Phase 2 placeholder)"""
    pass


class CodingSpecialist(BaseSpecialist):
    """Coding phase specialist agent (Phase 2 placeholder)"""
    pass


class TestingSpecialist(BaseSpecialist):
    """Testing phase specialist agent (Phase 2 placeholder)"""
    pass

__all__ = [
    "AgentRegistry",
    "BaseAgent",
    "BaseSpecialist",
    "CodingSpecialist",
    "ExecutionResult",
    "KnowledgeResult",
    "MissionContext",
    "PlanningSpecialist",
    "SpecialistResult",
    "TestingSpecialist",
]
