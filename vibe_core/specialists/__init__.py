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

# Specialist implementations (aliases for compatibility)
class PlanningSpecialist(BaseSpecialist):
    """Planning phase specialist agent"""
    pass

class CodingSpecialist(BaseSpecialist):
    """Coding phase specialist agent"""
    pass

class TestingSpecialist(BaseSpecialist):
    """Testing phase specialist agent"""
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
