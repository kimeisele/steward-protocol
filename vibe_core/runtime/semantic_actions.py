#!/usr/bin/env python3
"""
Semantic Actions Framework (OPERATION SEMANTIC MOTOR - Phase 1)
================================================================

The "Nodes" in VIBE's graph-based orchestration system.

Semantic Actions decouple INTENT from EXECUTION. Instead of:
  "if tests_failing → debug" (hardcoded business logic)

We have:
  ACTION: "debug_workflow"
  INTENT: "Investigate and fix test failures"
  NODES: ["analyze_logs", "identify_root_cause", "generate_fix", "verify_fix"]
  AGENTS: ["ResearcherAgent", "CoderAgent", "ReviewerAgent"]

This enables:
1. Reusable workflows across domains (testing, coding, research, design)
2. Agent capability matching (choose agent based on required skills)
3. Custom domain support (add new workflows without code changes)
4. Graph-based orchestration (explicit step dependencies)

Architecture:
  ┌─────────────────────────────────────────────────────┐
  │         Semantic Actions (Nodes)                    │
  │  - DEBUG, IMPLEMENT, RESEARCH, REVIEW, PLAN, etc   │
  └────────────────┬────────────────────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────────────────┐
  │      Workflow Graph (Edges & Dependencies)          │
  │  - Step A → Step B → Step C (control flow)          │
  │  - Agent capabilities match required skills         │
  └────────────────┬────────────────────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────────────────┐
  │   Graph Executor (Orchestration & Monitoring)       │
  │  - Execute nodes respecting dependencies            │
  │  - Collect metrics and results                      │
  │  - Handle failures with graceful degradation        │
  └─────────────────────────────────────────────────────┘

Version: 0.1 (Foundation)
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SemanticActionType(Enum):
    """Semantic action types (the "intents" in the system)"""

    # Development Actions
    DEBUG = "debug"  # Investigate and fix issues
    IMPLEMENT = "implement"  # Build new functionality
    REFACTOR = "refactor"  # Improve existing code
    REVIEW = "review"  # Code review and validation
    TEST = "test"  # Testing and verification

    # Research Actions
    RESEARCH = "research"  # Investigate and document
    ANALYZE = "analyze"  # Deep analysis of systems
    SYNTHESIZE = "synthesize"  # Combine findings into recommendations

    # Planning Actions
    PLAN = "plan"  # Strategic planning
    DESIGN = "design"  # System design and architecture

    # Operational Actions
    MONITOR = "monitor"  # System monitoring and health
    RESPOND = "respond"  # Incident response


@dataclass
class SemanticAction:
    """
    A semantic action is an intent-driven task.

    Separates WHAT (intent) from HOW (execution).
    Enables dynamic routing to appropriate agents.
    """

    action_type: SemanticActionType
    name: str  # e.g., "debug_test_failures"
    intent: str  # e.g., "Find and fix test failures"
    description: str  # Detailed description
    required_skills: list[str] = field(default_factory=list)  # e.g., ["code_analysis", "debugging"]
    input_schema: dict[str, Any] = field(default_factory=dict)  # Expected input structure
    output_schema: dict[str, Any] = field(default_factory=dict)  # Expected output structure
    estimated_cost_usd: float = 0.0  # Estimated API cost
    timeout_seconds: int = 300  # Execution timeout
    prompt_key: str | None = None  # Optional key to lookup prompt in registry
    knowledge_context: bool = False  # If True, inject relevant knowledge artifacts before execution

    def __str__(self) -> str:
        return f"SemanticAction({self.name}: {self.intent})"


@dataclass
class ActionStep:
    """
    A step within a semantic action.

    Actions are composed of steps that can be executed in sequence
    or in parallel, with explicit dependencies.
    """

    id: str  # e.g., "debug_001"
    name: str  # e.g., "analyze_logs"
    action_type: SemanticActionType
    depends_on: list[str] = field(default_factory=list)  # Step IDs this depends on
    executor: Callable | None = None  # Function to execute
    retry_count: int = 3
    timeout_seconds: int = 300

    def __str__(self) -> str:
        return f"ActionStep({self.id}: {self.name})"


# Pre-defined Semantic Actions (Common Workflows)
SEMANTIC_ACTIONS_REGISTRY = {
    "debug_test_failures": SemanticAction(
        action_type=SemanticActionType.DEBUG,
        name="debug_test_failures",
        intent="Investigate test failures and propose fixes",
        description="Analyze test output, identify root causes, and generate fixes",
        required_skills=["code_analysis", "debugging", "test_interpretation"],
        estimated_cost_usd=0.25,
    ),
    "implement_feature": SemanticAction(
        action_type=SemanticActionType.IMPLEMENT,
        name="implement_feature",
        intent="Build new feature or functionality",
        description="Design, implement, test, and document new feature",
        required_skills=["coding", "architecture", "testing"],
        estimated_cost_usd=1.50,
    ),
    "refactor_code": SemanticAction(
        action_type=SemanticActionType.REFACTOR,
        name="refactor_code",
        intent="Improve code quality and maintainability",
        description="Analyze code, identify improvements, refactor, and verify",
        required_skills=["code_analysis", "refactoring", "testing"],
        estimated_cost_usd=0.50,
    ),
    "code_review": SemanticAction(
        action_type=SemanticActionType.REVIEW,
        name="code_review",
        intent="Review code changes for quality and best practices",
        description="Analyze code changes, verify patterns, check tests",
        required_skills=["code_analysis", "testing", "pattern_knowledge"],
        estimated_cost_usd=0.30,
    ),
    "research_topic": SemanticAction(
        action_type=SemanticActionType.RESEARCH,
        name="research_topic",
        intent="Research and document a topic",
        description="Investigate topic, gather insights, create documentation",
        required_skills=["research", "documentation", "synthesis"],
        estimated_cost_usd=0.75,
    ),
}


class SemanticActionsRegistry:
    """
    Registry of available semantic actions.

    Acts as the central catalog of intents the system can handle.
    Enables dynamic lookup and capability matching.
    """

    def __init__(self):
        """Initialize with default actions"""
        self.actions = SEMANTIC_ACTIONS_REGISTRY.copy()

    def register_action(self, action: SemanticAction) -> None:
        """Register a new semantic action"""
        self.actions[action.name] = action
        logger.info(f"Registered semantic action: {action.name}")

    def get_action(self, action_name: str) -> SemanticAction | None:
        """Get a semantic action by name"""
        return self.actions.get(action_name)

    def find_matching_actions(self, required_skills: list[str]) -> list[SemanticAction]:
        """Find actions that match required skills"""
        return [
            action
            for action in self.actions.values()
            if all(skill in action.required_skills for skill in required_skills)
        ]

    def list_actions_by_type(self, action_type: SemanticActionType) -> list[SemanticAction]:
        """List all actions of a specific type"""
        return [action for action in self.actions.values() if action.action_type == action_type]

    def get_total_estimated_cost(self, action_names: list[str]) -> float:
        """Calculate total estimated cost for a set of actions"""
        total = 0.0
        for name in action_names:
            action = self.get_action(name)
            if action:
                total += action.estimated_cost_usd
        return total


# Global registry instance
_default_registry = SemanticActionsRegistry()


def get_registry() -> SemanticActionsRegistry:
    """Get the global semantic actions registry"""
    return _default_registry


if __name__ == "__main__":
    # Example usage
    registry = get_registry()

    print("Available Semantic Actions:")
    print("=" * 60)

    for action_type in SemanticActionType:
        actions = registry.list_actions_by_type(action_type)
        if actions:
            print(f"\n{action_type.value.upper()}:")
            for action in actions:
                print(f"  - {action.name}")
                print(f"    Intent: {action.intent}")
                print(f"    Skills: {', '.join(action.required_skills)}")
                print(f"    Est. Cost: ${action.estimated_cost_usd:.2f}")

    print("\n" + "=" * 60)
    print(f"Total Actions Registered: {len(registry.actions)}")
    print(
        f"Total Estimated Cost: ${registry.get_total_estimated_cost(list(registry.actions.keys())):.2f}"
    )
