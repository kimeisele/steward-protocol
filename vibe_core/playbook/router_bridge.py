#!/usr/bin/env python3
"""
GAD-905: Router Bridge (Playbook → Registry Translation)
========================================================

Connects the Playbook system to the Agent Registry (ProjectPhase orchestration).

MISSION (P0-001):
- Takes Workflow (from Playbook) and maps to ProjectPhase (for Registry)
- Creates translation layer: User Intent → Playbook → RouterBridge → Registry → Specialist
- Bridges semantic workflow nodes to SDLC phase-based execution

Architecture:
  1. PlaybookRouter: Routes user intent to appropriate playbook
  2. RouterBridge: Translates WorkflowGraph → ProjectPhase + specialist assignments
  3. AgentRegistry: Manages specialists and execution context

Version: 0.1 (MVP - Static Mapping)
Status: INITIAL IMPLEMENTATION
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.playbook.executor import WorkflowGraph, WorkflowNode

logger = logging.getLogger(__name__)


class WorkflowPhaseMapping(Enum):
    """Maps workflow intents to SDLC phases"""

    # Planning workflows → PLANNING phase
    MARKET_RESEARCH = "PLANNING"
    REQUIREMENTS_ANALYSIS = "PLANNING"
    ARCHITECTURE_DESIGN = "PLANNING"
    TECHNICAL_DESIGN = "PLANNING"

    # Coding workflows → CODING phase
    IMPLEMENTATION = "CODING"
    CODE_GENERATION = "CODING"
    REFACTORING = "CODING"

    # Testing workflows → TESTING phase
    TEST_DESIGN = "TESTING"
    TEST_EXECUTION = "TESTING"
    BUG_ANALYSIS = "TESTING"

    # Deployment workflows → DEPLOYMENT phase
    DEPLOYMENT_PREP = "DEPLOYMENT"
    RELEASE_PLANNING = "DEPLOYMENT"
    PRODUCTION_ROLLOUT = "DEPLOYMENT"

    # Maintenance workflows → MAINTENANCE phase
    MONITORING = "MAINTENANCE"
    INCIDENT_RESPONSE = "MAINTENANCE"
    PERFORMANCE_TUNING = "MAINTENANCE"


@dataclass
class RoutedAction:
    """A routed action with phase context and specialist assignment"""

    workflow_node_id: str
    node_action: str
    target_phase: str  # ProjectPhase enum name (PLANNING, CODING, etc.)
    required_skills: list[str] = field(default_factory=list)
    prompt_key: str | None = None
    timeout_seconds: int = 300
    retries: int = 3
    metadata: dict = field(default_factory=dict)


@dataclass
class RouterBridgeContext:
    """Context for a bridged workflow execution"""

    workflow_id: str
    workflow_name: str
    user_intent: str
    target_phase: str  # Primary ProjectPhase for this workflow
    routed_actions: list[RoutedAction] = field(default_factory=list)
    workflow_metadata: dict = field(default_factory=dict)


class RouterBridge:
    """
    Translates playbook workflows to registry-based execution.

    RESPONSIBILITIES:
    1. Map workflow intent to ProjectPhase
    2. Decompose WorkflowGraph into phase-specific tasks
    3. Assign required skills to each action
    4. Generate routing context for orchestrator delegation

    USAGE:
        bridge = RouterBridge()
        context = bridge.bridge_workflow(workflow_graph)
        orchestrator.route_to_phase(context.target_phase, context.routed_actions)
    """

    def __init__(self):
        """Initialize the router bridge"""
        self._phase_mapping = WorkflowPhaseMapping

    def bridge_workflow(self, workflow_graph: WorkflowGraph) -> RouterBridgeContext:
        """
        Bridge a WorkflowGraph to registry-based execution.

        Args:
            workflow_graph: The playbook workflow to bridge

        Returns:
            RouterBridgeContext with routed actions and phase assignment
        """
        logger.info(
            f"🌉 Bridging workflow: {workflow_graph.name} (intent: {workflow_graph.intent})"
        )

        # Step 1: Determine target phase from workflow intent
        target_phase = self._map_intent_to_phase(workflow_graph.intent)
        logger.debug(f"   → Mapped intent '{workflow_graph.intent}' to phase: {target_phase}")

        # Step 2: Route each workflow node
        routed_actions = self._route_nodes(workflow_graph.nodes, target_phase)
        logger.debug(f"   → Routed {len(routed_actions)} actions")

        # Step 3: Build context
        context = RouterBridgeContext(
            workflow_id=workflow_graph.id,
            workflow_name=workflow_graph.name,
            user_intent=workflow_graph.intent,
            target_phase=target_phase,
            routed_actions=routed_actions,
            workflow_metadata={
                "entry_point": workflow_graph.entry_point,
                "exit_points": workflow_graph.exit_points,
                "estimated_cost_usd": workflow_graph.estimated_cost_usd,
            },
        )

        logger.info(f"   ✅ Workflow bridged: {len(routed_actions)} actions → {target_phase}")
        return context

    def _map_intent_to_phase(self, intent: str) -> str:
        """
        Map workflow intent to ProjectPhase.

        Args:
            intent: User-provided workflow intent

        Returns:
            ProjectPhase name (PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE)

        LOGIC:
        - Try direct enum lookup first
        - Fall back to intent pattern matching
        - Default to PLANNING if unsure
        """
        # Try direct enum lookup (case-insensitive)
        intent_upper = intent.upper().replace(" ", "_")
        try:
            mapping = WorkflowPhaseMapping[intent_upper]
            return mapping.value
        except KeyError:
            pass

        # Pattern matching for common intents
        intent_lower = intent.lower()

        if any(word in intent_lower for word in ["plan", "research", "analysis", "design"]):
            return "PLANNING"
        elif any(word in intent_lower for word in ["code", "implement", "develop", "generate"]):
            return "CODING"
        elif any(word in intent_lower for word in ["test", "validate", "verify", "bug"]):
            return "TESTING"
        elif any(word in intent_lower for word in ["deploy", "release", "rollout", "production"]):
            return "DEPLOYMENT"
        elif any(word in intent_lower for word in ["maintain", "monitor", "support", "incident"]):
            return "MAINTENANCE"

        logger.warning(f"⚠️  Could not map intent '{intent}' to phase, defaulting to PLANNING")
        return "PLANNING"

    def _route_nodes(self, nodes: dict[str, WorkflowNode], target_phase: str) -> list[RoutedAction]:
        """
        Route workflow nodes to target phase.

        Args:
            nodes: Dict of WorkflowNode objects from the workflow
            target_phase: The target ProjectPhase for this workflow

        Returns:
            List of RoutedAction objects ready for orchestrator delegation
        """
        routed = []

        for node_id, node in nodes.items():
            # Create a routed action for this node
            action = RoutedAction(
                workflow_node_id=node_id,
                node_action=node.action,
                target_phase=target_phase,
                required_skills=node.required_skills,
                prompt_key=node.prompt_key,
                timeout_seconds=node.timeout_seconds,
                retries=node.retries,
                metadata={
                    "description": node.description,
                    "knowledge_context": node.knowledge_context,
                },
            )
            routed.append(action)

        return routed

    def validate_bridged_context(self, context: RouterBridgeContext) -> bool:
        """
        Validate that a bridged context is ready for execution.

        Args:
            context: The RouterBridgeContext to validate

        Returns:
            True if valid, False otherwise
        """
        if not context.workflow_id:
            logger.error("❌ Validation failed: Missing workflow_id")
            return False

        if not context.target_phase:
            logger.error("❌ Validation failed: Missing target_phase")
            return False

        if not context.routed_actions:
            logger.warning("⚠️  Validation warning: No routed actions (may be empty workflow)")
            return False

        logger.debug(f"✅ Validation passed: {context.workflow_id} → {context.target_phase}")
        return True


__all__ = ["RoutedAction", "RouterBridge", "RouterBridgeContext", "WorkflowPhaseMapping"]
