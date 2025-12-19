"""
Specialist Agents - HAP Framework (Hierarchical Agent Pattern)
================================================================

Base classes and registry for phase-specific specialist agents.

Classes:
  - BaseAgent: Agent with persona, command execution, and knowledge access
  - BaseSpecialist: Abstract base class for all specialists
  - AgentRegistry: Global registry for specialist instances
  - CommandResult: Result of command execution
  - KnowledgeResult: Result of knowledge base queries

STATUS: Phase-specific specialists are NOT IMPLEMENTED.
The base classes (BaseAgent, BaseSpecialist) work, but the specific
implementations (Planning, Coding, Testing) are stubs.
"""

from .base_agent import BaseAgent, CommandResult, KnowledgeResult
from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from .registry import AgentRegistry

# NOTE: These specialists exist for backward compatibility but raise errors if used.
# When implementing: Remove the NotImplementedError and add real logic.


class PlanningSpecialist(BaseSpecialist):
    """
    Planning phase specialist agent.

    STATUS: NOT IMPLEMENTED
    """

    def execute_mission(self, context: MissionContext) -> SpecialistResult:
        raise NotImplementedError(
            "PlanningSpecialist is not implemented. Use the playbook system for planning workflows instead."
        )


class CodingSpecialist(BaseSpecialist):
    """
    Coding phase specialist agent.

    STATUS: NOT IMPLEMENTED
    """

    def execute_mission(self, context: MissionContext) -> SpecialistResult:
        raise NotImplementedError(
            "CodingSpecialist is not implemented. Use the Engineer agent (engineer.builder tool) for code generation."
        )


class TestingSpecialist(BaseSpecialist):
    """
    Testing phase specialist agent.

    STATUS: NOT IMPLEMENTED
    """

    def execute_mission(self, context: MissionContext) -> SpecialistResult:
        raise NotImplementedError(
            "TestingSpecialist is not implemented. Use the Watchman agent for system verification."
        )


__all__ = [
    "AgentRegistry",
    "BaseAgent",
    "BaseSpecialist",
    "CodingSpecialist",
    "CommandResult",
    "KnowledgeResult",
    "MissionContext",
    "PlanningSpecialist",
    "SpecialistResult",
    "TestingSpecialist",
]
