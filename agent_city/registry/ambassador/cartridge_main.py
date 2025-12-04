#!/usr/bin/env python3
"""
AMBASSADOR Cartridge - Community & Developer Relations Agent

AMBASSADOR is the bridge between Steward Protocol and the community.
- Discord community management
- GitHub interaction and support
- Onboarding assistance
- Community sentiment monitoring
- Developer relations

Inherits from VibeAgent + OathMixin for kernel integration.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from vibe_core import Task, VibeAgent

# Constitutional Oath Mixin
from vibe_core.steward import OathMixin

# Import Router and Playbook components for proper system integration
try:
    from steward.system_agents.envoy.tools.milk_ocean import MilkOceanRouter

    MILK_OCEAN_AVAILABLE = True
except ImportError:
    MilkOceanRouter = None
    MILK_OCEAN_AVAILABLE = False
    logger = logging.getLogger("AMBASSADOR_MAIN")
    logger.warning("⚠️  MilkOceanRouter not available - using fallback")

try:
    from vibe_core.playbook.executor import GraphExecutor, WorkflowEdge, WorkflowGraph, WorkflowNode
    from vibe_core.playbook.router import AgentRouter

    PLAYBOOK_AVAILABLE = True
except ImportError:
    GraphExecutor = None
    WorkflowGraph = None
    WorkflowNode = None
    WorkflowEdge = None
    AgentRouter = None
    PLAYBOOK_AVAILABLE = False
    logger = logging.getLogger("AMBASSADOR_MAIN")
    logger.warning("⚠️  Playbook system not available - using fallback")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AMBASSADOR_MAIN")


class AmbassadorCartridge(VibeAgent, OathMixin):
    """
    AMBASSADOR Agent Cartridge.
    Community Engagement & Developer Relations.

    Capabilities:
    - Discord bot operations
    - GitHub issue/PR management
    - Onboarding automation
    - Community sentiment monitoring
    - Event coordination
    - Knowledge base management

    Integration:
    - Kernel-native VibeAgent
    - Task-responsive process() method
    - Event sourcing via ledger
    - Identity-ready (Steward Protocol)
    """

    def __init__(self):
        """Initialize AMBASSADOR as a VibeAgent."""
        super().__init__(
            agent_id="ambassador",
            name="AMBASSADOR",
            version="1.0.0",
            author="Steward Protocol",
            description="Community engagement and developer relations",
            domain="DIPLOMACY",
            capabilities=[
                "discord_bot",
                "github_api",
                "onboarding_protocol",
                "sentiment_analysis",
                "event_coordination",
                "knowledge_base",
            ],
        )

        logger.info("🤝 AMBASSADOR (VibeAgent v1.0) is online - Community Ready")

        # Constitutional Oath binding (Golden Template pattern)
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        logger.info("✅ AMBASSADOR has sworn the Constitutional Oath")

        # Initialize Router and Playbook components for proper system integration
        self.milk_ocean_router = None
        self.graph_executor = None
        self.agent_router = None

        if MILK_OCEAN_AVAILABLE:
            try:
                self.milk_ocean_router = MilkOceanRouter()
                logger.info("🌊 Milk Ocean Router initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize MilkOceanRouter: {e}")

        if PLAYBOOK_AVAILABLE:
            try:
                self.graph_executor = GraphExecutor()
                self.agent_router = AgentRouter()
                logger.info("📊 Playbook Executor & AgentRouter initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize Playbook system: {e}")

        # State tracking
        self.active_conversations: Dict[str, Dict] = {}
        self.onboarded_users: List[str] = []
        self.community_sentiment_score = 0.0
        self.issues_resolved = 0
        self.last_check_time = None

        logger.info("✅ AMBASSADOR: Ready for community engagement")

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process task from kernel scheduler.

        Supported actions:
        - answer_question: Respond to community questions
        - onboard_user: Guide new users
        - monitor_sentiment: Track community health
        - manage_issues: Coordinate GitHub issues
        - coordinate_event: Organize community events
        - manage_faq: Update knowledge base
        """
        try:
            action = task.payload.get("action", "status")

            logger.info(f"🤝 AMBASSADOR processing task: {action}")

            if action == "answer_question":
                result = await self._answer_question(task.payload)
            elif action == "onboard_user":
                result = await self._onboard_user(task.payload)
            elif action == "monitor_sentiment":
                result = await self._monitor_sentiment(task.payload)
            elif action == "manage_issues":
                result = await self._manage_issues(task.payload)
            elif action == "coordinate_event":
                result = await self._coordinate_event(task.payload)
            elif action == "manage_faq":
                result = await self._manage_faq(task.payload)
            elif action == "status":
                result = self._status()
            else:
                result = {"error": f"Unknown action: {action}"}

            logger.info(f"✅ AMBASSADOR task completed: {action}")
            return result

        except Exception as e:
            logger.error(f"❌ AMBASSADOR task failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def _answer_question(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer a community question using Router → Playbook → Execution pipeline.

        This method respects the system architecture:
        1. Route through MilkOceanRouter (Triage)
        2. Create Playbook based on priority
        3. Execute via GraphExecutor (Real agent dispatch)
        """
        question = payload.get("question", "")
        user_id = payload.get("user_id", "anonymous")

        logger.info(f"🤝 Answering question from {user_id}: {question[:50]}...")

        # Track the conversation
        conversation_id = f"{user_id}_{datetime.utcnow().timestamp()}"
        self.active_conversations[conversation_id] = {
            "question": question,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processing",
        }

        # ========== STEP 1: Route through Milk Ocean (Triage) ==========
        if not self.milk_ocean_router:
            logger.warning("⚠️  MilkOceanRouter not available - using simple fallback")
            return self._simple_fallback_answer(question, user_id, conversation_id)

        try:
            routing_decision = self.milk_ocean_router.process_prayer(question, agent_id="ambassador", critical=False)

            logger.info(f"🌊 Routing decision: {routing_decision.get('path', 'unknown')}")

            # Handle different routing paths
            if routing_decision.get("status") == "blocked":
                return {
                    "status": "blocked",
                    "user_id": user_id,
                    "question": question,
                    "reason": routing_decision.get("reason"),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            elif routing_decision.get("status") == "queued":
                # Lazy queue - return early
                return {
                    "status": "queued",
                    "user_id": user_id,
                    "question": question,
                    "message": "Your question will be processed during off-peak hours",
                    "request_id": routing_decision.get("request_id"),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # ========== STEP 2: Create Playbook for Flash/Science ==========
            priority = routing_decision.get("path", "flash")  # flash or science
            playbook = self._create_qa_playbook(question, priority)

            # ========== STEP 3: Execute Playbook ==========
            if not self.graph_executor:
                logger.warning("⚠️  GraphExecutor not available - using simple response")
                return self._simple_fallback_answer(question, user_id, conversation_id)

            logger.info(f"📊 Executing Q&A playbook (priority: {priority})")
            result = self.graph_executor.execute(playbook)

            # Update conversation tracking
            self.active_conversations[conversation_id]["status"] = "completed"
            self.active_conversations[conversation_id]["result"] = result.get("status")

            # Extract answer from workflow results
            answer = self._extract_answer_from_results(result)

            return {
                "status": "answered",
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "method": f"playbook_{priority}",
                "workflow_id": result.get("workflow_id"),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Question answering failed: {e}")
            self.active_conversations[conversation_id]["status"] = "failed"
            self.active_conversations[conversation_id]["error"] = str(e)

            return {
                "status": "error",
                "user_id": user_id,
                "question": question,
                "error": f"Failed to process question: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _create_qa_playbook(self, question: str, priority: str) -> "WorkflowGraph":
        """
        Create a workflow for answering community questions.

        The playbook follows deterministic routing: classify → retrieve → generate
        """
        nodes = {
            "generate_answer": WorkflowNode(
                id="generate_answer",
                action="answer_community_question",
                description=f"Generate answer to: {question}",
                required_skills=["knowledge_base", "content_generation", priority],
            )
        }

        edges = []  # Single node for MVP

        return WorkflowGraph(
            id="ambassador_qa",
            name="Community Q&A",
            intent=question,
            nodes=nodes,
            edges=edges,
            entry_point="generate_answer",
            exit_points=["generate_answer"],
        )

    def _extract_answer_from_results(self, workflow_result: Dict[str, Any]) -> str:
        """Extract the answer from workflow execution results."""
        results = workflow_result.get("results", [])

        if not results:
            return "No answer generated (workflow returned empty results)"

        # Get the last result (should be generate_answer node)
        last_result = results[-1]
        output = last_result.get("output", {})

        if isinstance(output, dict):
            return output.get("answer") or output.get("message") or str(output)
        else:
            return str(output)

    def _simple_fallback_answer(self, question: str, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """Simple fallback when Router/Playbook unavailable."""
        fallback_answer = (
            f"Hello! I'm AMBASSADOR, the community liaison for Steward Protocol.\n\n"
            f"Your question: '{question}'\n\n"
            f"I'm currently running in fallback mode (Router/Playbook system not available). "
            f"For full functionality, please ensure all system components are initialized.\n\n"
            f"You can find more information in our documentation:\n"
            f"- README.md for quick start\n"
            f"- AGENTS.md for agent registry\n"
            f"- HELP.md for operations guide"
        )

        self.active_conversations[conversation_id]["status"] = "answered_fallback"

        return {
            "status": "answered",
            "user_id": user_id,
            "question": question,
            "answer": fallback_answer,
            "method": "fallback",
            "note": "Router/Playbook system not available",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _onboard_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Onboard a new user."""
        user_id = payload.get("user_id", "")
        user_name = payload.get("user_name", "")

        # Track the onboarding attempt (basic tracking works)
        self.onboarded_users.append(user_id)

        return {
            "status": "partial",
            "user_id": user_id,
            "user_name": user_name,
            "total_onboarded": len(self.onboarded_users),
            "timestamp": datetime.utcnow().isoformat(),
            "note": (
                "Basic onboarding tracking is working. "
                "Full workflow (welcome message, starter pack, docs) not implemented."
            ),
        }

    async def _monitor_sentiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor community sentiment."""
        channel = payload.get("channel", "general")
        period = payload.get("period", "24h")

        return {
            "status": "not_implemented",
            "channel": channel,
            "period": period,
            "sentiment_score": None,
            "timestamp": datetime.utcnow().isoformat(),
            "error": ("Sentiment monitoring is not implemented. Requires integration with message analysis service."),
        }

    async def _manage_issues(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Manage GitHub issues and PRs."""
        action_type = payload.get("action_type", "list")
        issue_filter = payload.get("filter", "open")

        return {
            "status": "not_implemented",
            "action": action_type,
            "filter": issue_filter,
            "timestamp": datetime.utcnow().isoformat(),
            "error": (
                "GitHub issue management is not implemented. Requires GitHub API integration (gh CLI or PyGithub)."
            ),
        }

    async def _coordinate_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a community event."""
        event_name = payload.get("event_name", "")
        event_date = payload.get("event_date", "")
        event_type = payload.get("event_type", "meeting")

        return {
            "status": "not_implemented",
            "event_name": event_name,
            "event_date": event_date,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "error": ("Event coordination is not implemented. Requires calendar/scheduling service integration."),
        }

    async def _manage_faq(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Manage FAQ and knowledge base."""
        action = payload.get("action", "list")

        return {
            "status": "not_implemented",
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "error": ("FAQ management is not implemented. Requires knowledge base integration."),
        }

    def _status(self) -> Dict[str, Any]:
        """Return AMBASSADOR status."""
        return {
            "agent_id": self.agent_id,
            "status": "online",
            "active_conversations": len(self.active_conversations),
            "users_onboarded": len(self.onboarded_users),
            "community_sentiment": self.community_sentiment_score,
            "issues_resolved": self.issues_resolved,
            "oath_sworn": getattr(self, "oath_sworn", False),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        return super().get_manifest()


# Instantiate the cartridge
if __name__ == "__main__":
    cartridge = AmbassadorCartridge()
    print(f"✅ {cartridge.name} cartridge loaded")

    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "ambassador",
            "name": "AMBASSADOR",
            "status": "healthy",
            "domain": "GOVERNANCE",
            "capabilities": ["diplomacy", "external_relations"],
        }
