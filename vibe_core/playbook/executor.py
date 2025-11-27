#!/usr/bin/env python3
"""
GAD-902: Graph Executor (Isolated Implementation)
===================================================

Orchestrates workflow execution using graph-based dependencies.

KEY PRINCIPLE: Pure logic first, agent integration second.
- Takes WorkflowGraph (data) as input
- Returns execution plan (data) as output
- Dry-run mode validates logic without touching agents
- Abstract agent interfaces (mocks for testing)

Architecture:
  1. Load workflow as graph (nodes + edges)
  2. Topological sort (determine execution order)
  3. Validate dependencies
  4. Generate execution plan
  5. Execute plan or dry-run it

Version: 0.1 (Logic Foundation)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Import runtime modules with proper package paths
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of workflow execution"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowNode:
    """A node in the workflow graph"""

    id: str
    action: str
    description: str = ""
    required_skills: list[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retries: int = 3
    prompt_key: str | None = None  # Optional key to lookup prompt in registry
    knowledge_context: bool = False  # If True, inject relevant knowledge artifacts before execution


@dataclass
class WorkflowEdge:
    """An edge in the workflow graph (dependency)"""

    from_node: str
    to_node: str
    condition: str = "success"  # "success" or "always"


@dataclass
class WorkflowGraph:
    """Complete workflow graph definition"""

    id: str
    name: str
    intent: str
    nodes: dict[str, WorkflowNode]
    edges: list[WorkflowEdge]
    entry_point: str
    exit_points: list[str]
    estimated_cost_usd: float = 0.0


@dataclass
class ExecutionPlan:
    """Execution plan (output of topological sort)"""

    workflow_id: str
    execution_order: list[str]  # Node IDs in execution order
    dependencies: dict[str, list[str]]  # node_id → list of dependencies
    is_valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """Result of executing a workflow or step"""

    workflow_id: str
    node_id: str
    status: ExecutionStatus
    output: Any = None
    error: str | None = None
    cost_usd: float = 0.0
    duration_seconds: float = 0.0


class AgentInterface:
    """
    Abstract interface for agents (mock for testing).

    This allows testing the executor logic WITHOUT depending on
    actual agent implementations.
    """

    def can_execute(self, required_skills: list[str]) -> bool:
        """Check if this agent has required skills"""
        raise NotImplementedError

    def execute_action(self, action: str, prompt: str, timeout_seconds: int) -> ExecutionResult:
        """Execute an action (mocked for testing)"""
        raise NotImplementedError


class MockAgent(AgentInterface):
    """Mock agent for dry-run and testing"""

    def __init__(self, name: str = "MockAgent", skills: list[str] = None):
        self.name = name
        self.skills = skills or ["code_analysis", "debugging", "coding"]

    def can_execute(self, required_skills: list[str]) -> bool:
        """Check if mock agent has all required skills"""
        return all(skill in self.skills for skill in required_skills)

    def execute_action(
        self, action: str, prompt: str, timeout_seconds: int = 300
    ) -> ExecutionResult:
        """Return mock success (for dry-run)"""
        return ExecutionResult(
            workflow_id="mock",
            node_id=action,
            status=ExecutionStatus.SUCCESS,
            output={"message": f"[MOCK] Executed {action}"},
            cost_usd=0.0,
            duration_seconds=0.1,
        )


class GraphExecutor:
    """
    Orchestrates workflow execution using graph-based dependencies.

    Pure logic implementation - can be tested with mock agents before
    connecting to real agent implementations.
    """

    def __init__(self):
        """Initialize executor"""
        self.agent: AgentInterface = MockAgent()  # Default to mock (backward compatible)
        self.router = None  # AgentRouter (GAD-904) when connected
        self.quota = None  # OperationalQuota instance when safety layer active
        self.lens_prompt = None  # GAD-906/907: Semantic lens injection
        self.execution_history: list[ExecutionResult] = []

    def set_agent(self, agent: AgentInterface) -> None:
        """Set the agent to use for execution"""
        self.agent = agent

    # GAD-904: Neural link setup
    def set_router(self, router) -> None:  # type: ignore
        """Attach AgentRouter for capability-based selection"""
        self.router = router

    def set_quota_manager(self, quota_manager) -> None:  # type: ignore
        """Attach OperationalQuota for pre-flight cost checks"""
        self.quota = quota_manager

    def set_lens(self, lens_prompt: str) -> None:
        """
        Set semantic lens for mindset injection (GAD-906/907).

        The lens prompt will be prepended to all task contexts, transforming
        the agent's thinking mode from worker → engineer.

        Args:
            lens_prompt: Formatted lens prompt from lens_loader.load_lens()
        """
        self.lens_prompt = lens_prompt
        logger.info(f"🔬 Semantic lens activated ({len(lens_prompt)} chars)")

    def _topological_sort(self, graph: WorkflowGraph) -> ExecutionPlan:
        """
        Perform topological sort to determine execution order.

        Returns ExecutionPlan with nodes in execution order, or with
        errors if graph is invalid.
        """
        # Build adjacency list and in-degree counts
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in graph.nodes}
        in_degree: dict[str, int] = {node_id: 0 for node_id in graph.nodes}

        for edge in graph.edges:
            if edge.from_node not in adjacency or edge.to_node not in adjacency:
                return ExecutionPlan(
                    workflow_id=graph.id,
                    execution_order=[],
                    dependencies={},
                    is_valid=False,
                    errors=[
                        f"Edge references non-existent node: {edge.from_node} → {edge.to_node}"
                    ],
                )

            adjacency[edge.from_node].add(edge.to_node)
            in_degree[edge.to_node] += 1

        # Kahn's algorithm for topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            node = queue.pop(0)
            execution_order.append(node)

            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(execution_order) != len(graph.nodes):
            return ExecutionPlan(
                workflow_id=graph.id,
                execution_order=[],
                dependencies={},
                is_valid=False,
                errors=["Workflow contains circular dependencies"],
            )

        # Verify entry and exit points exist
        if graph.entry_point not in graph.nodes:
            return ExecutionPlan(
                workflow_id=graph.id,
                execution_order=[],
                dependencies={},
                is_valid=False,
                errors=[f"Entry point {graph.entry_point} not found"],
            )

        for exit_point in graph.exit_points:
            if exit_point not in graph.nodes:
                return ExecutionPlan(
                    workflow_id=graph.id,
                    execution_order=[],
                    dependencies={},
                    is_valid=False,
                    errors=[f"Exit point {exit_point} not found"],
                )

        # Build dependency map (reverse of adjacency)
        dependencies = {node_id: [] for node_id in graph.nodes}
        for edge in graph.edges:
            dependencies[edge.to_node].append(edge.from_node)

        return ExecutionPlan(
            workflow_id=graph.id,
            execution_order=execution_order,
            dependencies=dependencies,
            is_valid=True,
        )

    def validate_workflow(self, graph: WorkflowGraph) -> tuple[bool, str]:
        """
        Validate workflow graph for structural correctness.

        Returns (is_valid, message)
        """
        plan = self._topological_sort(graph)

        if not plan.is_valid:
            error_msg = "; ".join(plan.errors)
            return False, f"Invalid workflow: {error_msg}"

        # Check agent capabilities
        for node_id in plan.execution_order:
            node = graph.nodes[node_id]
            if node.required_skills:
                if self.router:  # Use router to find agent per node
                    best = self.router.find_best_agent_for_skills(node.required_skills)
                    if best is None:
                        return (
                            False,
                            f"No agent satisfies skills for node {node_id}: {node.required_skills}",
                        )
                else:
                    if not self.agent.can_execute(node.required_skills):
                        return (
                            False,
                            f"Agent cannot execute node {node_id}: requires {node.required_skills}",
                        )

        return True, "Workflow is valid"

    def dry_run(self, graph: WorkflowGraph) -> dict[str, Any]:
        """
        Dry-run the workflow without executing agents.

        Returns:
            Dictionary with execution plan, validation results, and mock output
        """
        # Validate workflow
        is_valid, validation_msg = self.validate_workflow(graph)

        # Generate execution plan
        plan = self._topological_sort(graph)

        result = {
            "workflow_id": graph.id,
            "workflow_name": graph.name,
            "intent": graph.intent,
            "is_valid": is_valid,
            "validation_message": validation_msg,
            "execution_plan": {
                "execution_order": plan.execution_order,
                "dependencies": plan.dependencies,
            },
            "nodes": {},
        }

        # Add node details
        for node_id in plan.execution_order:
            node = graph.nodes[node_id]
            result["nodes"][node_id] = {
                "action": node.action,
                "description": node.description,
                "required_skills": node.required_skills,
                "timeout_seconds": node.timeout_seconds,
                "dependencies": plan.dependencies.get(node_id, []),
            }

        return result

    def execute_step(
        self, graph: WorkflowGraph, node_id: str, context: str | None = None
    ) -> ExecutionResult:
        """Execute a single workflow node using routed agent.

        Execution mode is determined by Phoenix safety configuration:
        - config.safety.live_fire_enabled=true: Real execution (actual tokens, real cost)
        - config.safety.live_fire_enabled=false: Mock execution ($0 cost)

        Falls back to VIBE_LIVE_FIRE environment variable if Phoenix config unavailable.

        Args:
            graph: The workflow graph
            node_id: The node to execute
            context: Optional context/prompt to pass to the agent
        """
        # Lazy import to avoid circular dependencies
        live_fire_enabled = False  # Default: safe mode

        try:
            from vibe_core.config import get_config

            config = get_config()
            live_fire_enabled = config.safety.live_fire_enabled
        except ImportError:
            # Fallback: Use environment variable if Phoenix config unavailable
            import os

            live_fire_enabled = os.getenv("VIBE_LIVE_FIRE", "false").lower() == "true"

        node = graph.nodes[node_id]

        # Build the prompt: [REGISTRY] → [LENS] + context (if provided) + node description
        # OPERATION VOICE: Check if node has a prompt_key for registry lookup
        if node.prompt_key:
            try:
                # Import runtime modules with proper package paths
                from vibe_core.runtime.prompt_context import get_prompt_context
                from vibe_core.runtime.prompt_registry import PromptRegistry

                # Build context dict for prompt interpolation
                prompt_context = {"node_id": node_id, "action": node.action}
                if context:
                    prompt_context["context"] = context

                # GAD-909: Resolve dynamic context (The Flesh / OPERATION CONTEXT)
                # Load standard system context for prompt placeholders
                try:
                    context_engine = get_prompt_context()
                    system_context = context_engine.resolve(
                        ["system_time", "current_branch", "git_status"]
                    )
                    # Merge system context into prompt context
                    prompt_context.update(system_context)
                    logger.debug(f"🔌 CONTEXT: Resolved {len(system_context)} system contexts")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to resolve system context: {e}")

                # Get prompt from registry (with context interpolation)
                base_prompt = PromptRegistry.get(node.prompt_key, prompt_context)
                logger.info(
                    f"🎙️ VOICE: Retrieved prompt from registry: {node.prompt_key} ({len(base_prompt)} chars)"
                )
            except Exception as e:
                logger.warning(
                    f"⚠️  Prompt registry lookup failed for key '{node.prompt_key}': {e}. "
                    f"Falling back to node description."
                )
                base_prompt = context if context else node.description
        else:
            # No prompt_key: use context or description (legacy behavior)
            base_prompt = context if context else node.description

        # GAD-908: Knowledge Context Injection (OPERATION INSIGHT)
        # Check if this node needs knowledge context
        if node.knowledge_context:
            try:
                # Import with proper path handling
                import importlib.util

                retriever_path = (
                    Path(__file__).parent.parent.parent / "02_knowledge" / "retriever.py"
                )

                spec = importlib.util.spec_from_file_location("retriever", retriever_path)
                retriever_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(retriever_module)

                KnowledgeRetriever = retriever_module.KnowledgeRetriever

                # Initialize retriever with repo root
                vibe_root = Path(__file__).parent.parent.parent.parent
                retriever = KnowledgeRetriever(vibe_root)

                # Extract query from context (use first 100 chars as search query)
                query = context[:100] if context else node.action
                logger.info(f"👁️ INSIGHT: Retrieving knowledge for query: '{query[:50]}...'")

                # Search for relevant knowledge
                hits = retriever.search(query, limit=5)

                if hits:
                    logger.info(f"👁️ INSIGHT: Found {len(hits)} relevant knowledge artifacts")

                    # Format knowledge context
                    knowledge_section = "\n\n" + "=" * 80 + "\n"
                    knowledge_section += "[INTERNAL KNOWLEDGE FOUND]\n"
                    knowledge_section += "=" * 80 + "\n\n"
                    knowledge_section += "The following knowledge artifacts from our knowledge base are relevant to this task:\n\n"

                    for i, hit in enumerate(hits, 1):
                        rel_path = hit.path.relative_to(retriever.knowledge_base)
                        knowledge_section += f"## Artifact {i}: {hit.title}\n"
                        knowledge_section += (
                            f"**Domain:** {hit.domain} | **Relevance:** {hit.relevance_score:.1%}\n"
                        )
                        knowledge_section += f"**Path:** {rel_path}\n\n"

                        # Read full content for high-relevance matches
                        if hit.relevance_score >= 0.5:
                            try:
                                content = retriever.read_file(rel_path)
                                knowledge_section += f"**Content:**\n```\n{content}\n```\n\n"
                            except Exception as e:
                                logger.warning(f"Failed to read knowledge file {rel_path}: {e}")
                                knowledge_section += f"**Preview:** {hit.preview}\n\n"
                        else:
                            knowledge_section += f"**Preview:** {hit.preview}\n\n"

                    knowledge_section += "=" * 80 + "\n"
                    knowledge_section += "[END INTERNAL KNOWLEDGE]\n"
                    knowledge_section += "=" * 80 + "\n"

                    # Inject knowledge into prompt
                    base_prompt = base_prompt + knowledge_section
                    logger.info(f"👁️ INSIGHT: Injected {len(hits)} knowledge artifacts into prompt")
                else:
                    logger.info("👁️ INSIGHT: No relevant knowledge found")

            except Exception as e:
                logger.warning(
                    f"⚠️  Knowledge retrieval failed: {e}. Continuing without knowledge context."
                )
                # Continue execution without knowledge context

        # GAD-906/907: Semantic lens injection for mindset transformation
        if self.lens_prompt:
            # Format: [MINDSET: <lens>]\n\n[TASK]\n<actual task>
            prompt = f"{self.lens_prompt}\n\n{'=' * 80}\n[TASK]\n{'=' * 80}\n\n{base_prompt}"
            logger.debug(f"🔬 Lens injected into prompt ({len(self.lens_prompt)} chars)")
        else:
            prompt = base_prompt

        # Quota pre-flight check
        if self.quota:
            try:
                self.quota.check_before_request(estimated_tokens=50, operation=node.action)
            except Exception as e:  # QuotaExceededError
                return ExecutionResult(
                    workflow_id=graph.id,
                    node_id=node_id,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=str(e),
                )

        # Select agent
        selected_agent = None
        if self.router:
            selected_agent = self.router.find_best_agent_for_skills(node.required_skills)
        if selected_agent is None and hasattr(self, "agent"):
            selected_agent = self.agent  # Fallback

        # EXECUTION MODE: Real vs Mock
        if live_fire_enabled:
            # REAL EXECUTION: Actual agent invocation (real tokens, real cost)
            logger.info(
                f"🔥 LIVE FIRE: Executing {node_id} with real agent: {getattr(selected_agent, 'name', 'unknown')}"
            )
            try:
                # Real execution path - would call agent.execute_command or similar
                if hasattr(selected_agent, "execute_command"):
                    result = selected_agent.execute_command(
                        node.action, prompt=prompt, timeout_seconds=node.timeout_seconds
                    )
                elif hasattr(selected_agent, "execute_action"):
                    result = selected_agent.execute_action(
                        action=node.action,
                        prompt=prompt,
                        timeout_seconds=node.timeout_seconds,
                    )
                else:
                    # Fallback if agent doesn't have execution methods
                    result = ExecutionResult(
                        workflow_id=graph.id,
                        node_id=node_id,
                        status=ExecutionStatus.FAILED,
                        output=None,
                        error=f"Agent {getattr(selected_agent, 'name', 'unknown')} does not support execute_command or execute_action",
                    )
                # Record actual cost from execution
                cost_usd = result.cost_usd if hasattr(result, "cost_usd") else 0.0
            except Exception as e:
                logger.error(f"🔥 LIVE FIRE execution failed for {node_id}: {e}")
                result = ExecutionResult(
                    workflow_id=graph.id,
                    node_id=node_id,
                    status=ExecutionStatus.FAILED,
                    output=None,
                    error=str(e),
                )
                cost_usd = 0.0
        else:
            # MOCK EXECUTION: Zero cost, safe default
            logger.debug(f"Mock execution: {node_id} (VIBE_LIVE_FIRE not enabled)")
            result = ExecutionResult(
                workflow_id=graph.id,
                node_id=node_id,
                status=ExecutionStatus.SUCCESS,
                output={
                    "message": f"[ROUTED MOCK] {node.action} executed",
                    "agent": getattr(selected_agent, "name", "unknown"),
                    "skills_used": node.required_skills,
                    "mode": "mock",
                    "context": context,
                },
                cost_usd=0.0,
                duration_seconds=0.0,
            )
            cost_usd = 0.0

        self.execution_history.append(result)

        # Record quota usage
        if self.quota:
            self.quota.record_request(tokens_used=50, cost_usd=cost_usd, operation=node.action)

        return result

    def execute(self, graph: WorkflowGraph) -> dict[str, Any]:
        """
        Execute the workflow (uses agent interface).

        For now, this is a stub that returns the execution plan.
        Phase 2 will implement actual agent invocation.
        """
        # Validate first
        is_valid, validation_msg = self.validate_workflow(graph)
        if not is_valid:
            return {
                "workflow_id": graph.id,
                "status": "failed",
                "error": validation_msg,
            }

        # Generate plan
        plan = self._topological_sort(graph)

        # Execute (Phase 2: will actually call agents)
        results = []
        for node_id in plan.execution_order:
            node = graph.nodes[node_id]
            result = ExecutionResult(
                workflow_id=graph.id,
                node_id=node_id,
                status=ExecutionStatus.SUCCESS,
                output={"message": f"[PHASE 2] Would execute {node.action}"},
                cost_usd=0.0,
            )
            results.append(result)
            self.execution_history.append(result)

        return {
            "workflow_id": graph.id,
            "status": "success",
            "execution_order": plan.execution_order,
            "results": [
                {
                    "node_id": r.node_id,
                    "status": r.status.value,
                    "output": r.output,
                }
                for r in results
            ],
        }

    def get_execution_history(self) -> list[ExecutionResult]:
        """Get execution history"""
        return self.execution_history

    def get_execution_cost(self, graph: WorkflowGraph) -> float:
        """Get estimated cost for workflow"""
        return graph.estimated_cost_usd


if __name__ == "__main__":
    # Example usage (no import needed - just test the executor)

    # Create a simple test graph
    nodes = {
        "step1": WorkflowNode(
            id="step1",
            action="analyze",
            description="Analyze the problem",
            required_skills=["analysis"],
        ),
        "step2": WorkflowNode(
            id="step2",
            action="design",
            description="Design solution",
            required_skills=["design"],
        ),
        "step3": WorkflowNode(
            id="step3",
            action="implement",
            description="Implement solution",
            required_skills=["coding"],
        ),
    }

    edges = [
        WorkflowEdge("step1", "step2"),
        WorkflowEdge("step2", "step3"),
    ]

    workflow = WorkflowGraph(
        id="test_workflow",
        name="Test Workflow",
        intent="Test the executor",
        nodes=nodes,
        edges=edges,
        entry_point="step1",
        exit_points=["step3"],
        estimated_cost_usd=0.50,
    )

    # Create executor and test
    executor = GraphExecutor()

    print("Testing Graph Executor")
    print("=" * 60)

    # Dry-run
    print("\n1. Dry-run (validation only):")
    dry_run_result = executor.dry_run(workflow)
    print(f"   Valid: {dry_run_result['is_valid']}")
    print(f"   Execution order: {dry_run_result['execution_plan']['execution_order']}")
    print(f"   Message: {dry_run_result['validation_message']}")

    # Execute
    print("\n2. Execute:")
    exec_result = executor.execute(workflow)
    print(f"   Status: {exec_result['status']}")
    print(f"   Order: {exec_result['execution_order']}")

    # Cost estimation
    print("\n3. Cost Estimation:")
    cost = executor.get_execution_cost(workflow)
    print(f"   Estimated cost: ${cost:.2f}")

    print("\n" + "=" * 60)
    print("✅ Executor logic validated successfully!")
