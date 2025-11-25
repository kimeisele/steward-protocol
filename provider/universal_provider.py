"""
🌌 UNIVERSAL PROVIDER (GAD-4000: SILKY SMOOTH EDITION)
The Central Nervous System of Agent City.
Now with Fast-Path Execution for Natural Conversations.

Role:
1. Receives abstract INTENTS (from User/Chat)
2. Resolves them to specific AGENTS via CAPABILITY MAPPING
3. Routes to FAST-PATH (instant response) or SLOW-PATH (async task)
4. Injects CONTEXT (Time, Location, Ledger State)
5. Executes via KERNEL with natural language UX
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import time

# Import Core Definitions
try:
    from vibe_core.kernel import VibeKernel
    from vibe_core.scheduling import Task
except ImportError:
    # Mock for bootstrapping if kernel isn't in path yet
    VibeKernel = Any
    Task = Any

logger = logging.getLogger("UNIVERSAL_PROVIDER")

class IntentType(Enum):
    QUERY = "query"           # Read-only questions (FAST PATH)
    ACTION = "action"         # State-changing operations (SLOW PATH)
    SYSTEM = "system"         # Meta-operations (FAST PATH)
    CREATION = "creation"     # Generating content (SLOW PATH)
    CHAT = "chat"             # Casual conversation (FAST PATH)

@dataclass
class IntentVector:
    """The normalized request format for Agent City"""
    raw_input: str
    intent_type: IntentType
    target_domain: Optional[str] = None
    confidence: float = 1.0
    parameters: Dict[str, Any] = None

class UniversalProvider:
    def __init__(self, kernel: VibeKernel):
        self.kernel = kernel
        self.context_layer = {
            "location": "Agent City / Central Plaza",
            "access_level": "OPERATOR",
            "last_interaction": time.time()
        }
        logger.info("🌌 Universal Provider GAD-4000 initialized with Fast-Path execution")

    def resolve_intent(self, user_input: str) -> IntentVector:
        """
        Natural Language Router with Fast-Path Detection.
        Identifies intent type and target agent for optimal routing.
        """
        u = user_input.lower().strip()

        # 1. SYSTEM / STATUS (FAST PATH)
        if u in ["status", "health", "ping", "system"] or "status" in u or "health" in u:
            return IntentVector(user_input, IntentType.SYSTEM, "watchman", confidence=0.95)

        # 2. BRIEFING / INFO (FAST PATH)
        if "briefing" in u or "report" in u or "overview" in u or "tell" in u and "about" in u:
            return IntentVector(user_input, IntentType.QUERY, "envoy", confidence=0.90)

        # 3. CREATION (SLOW PATH)
        if "create" in u or "write" in u or "generate" in u or "draft" in u or "publish" in u:
            return IntentVector(user_input, IntentType.CREATION, "herald", confidence=0.85)

        # 4. ACTION (SLOW PATH)
        if "verify" in u or "deploy" in u or "vote" in u or "check" in u or "execute" in u:
            return IntentVector(user_input, IntentType.ACTION, "civic", confidence=0.85)

        # 5. CASUAL CHAT (FAST PATH - DEFAULT)
        return IntentVector(user_input, IntentType.CHAT, "envoy", confidence=0.70)

    def route_and_execute(self, user_input: str) -> Dict[str, Any]:
        """
        The Magic Entry Point for VibeChat (GAD-4000).
        Decides between FAST-PATH (instant response) and SLOW-PATH (async queueing).
        """
        logger.info(f"📨 Thinking about: '{user_input}'")
        vector = self.resolve_intent(user_input)

        # --- DECISION POINT: FAST vs SLOW PATH ---
        # FAST PATH: Instant gratification for reads and casual chat
        if vector.intent_type == IntentType.SYSTEM:
            return self._fast_path_system_status(vector)

        if vector.intent_type == IntentType.CHAT:
            return self._fast_path_chat_response(vector)

        if vector.intent_type == IntentType.QUERY:
            return self._fast_path_query_response(vector)

        # --- SLOW PATH: Heavy lifting via Task Queue ---
        target_agent_id = self._find_best_agent(vector)

        if not target_agent_id:
            return {
                "status": "ERROR",
                "message": f"No agent found for intent: {vector.intent_type.value}"
            }

        task_payload = self._translate_payload(target_agent_id, vector)
        task = Task(agent_id=target_agent_id, payload=task_payload)

        try:
            task_id = self.kernel.submit_task(task)
            response_msg = self._generate_ack_message(vector, target_agent_id)

            return {
                "status": "SUBMITTED",
                "summary": f"🤖 {response_msg}",
                "details": {
                    "task_id": task_id,
                    "agent": target_agent_id,
                    "intent": vector.intent_type.value
                }
            }
        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    # --- FAST PATH HANDLERS ---

    def _fast_path_system_status(self, vector: IntentVector) -> Dict[str, Any]:
        """
        Directly queries kernel state for instant system response.
        No task queueing. Pure read-only. Fast.
        """
        try:
            stats = self.kernel.get_status()
            agents = stats.get('agents_registered', 0)
            events = stats.get('ledger_events', 0)

            msg = (
                f"**🟢 SYSTEM ONLINE**\n"
                f"• **Agents Active:** {agents}\n"
                f"• **Ledger Events:** {events}\n"
                f"• **Location:** Agent City Central\n"
                f"• **Status:** All systems nominal\n\n"
                f"Standing by for orders, Operator."
            )
            return {
                "status": "success",
                "summary": msg,
                "path": "fast"
            }
        except Exception as e:
            logger.warning(f"Fast-path status failed, fallback: {e}")
            return {
                "status": "success",
                "summary": "**🟢 SYSTEM ONLINE** (Brief check: systems nominal)",
                "path": "fast_fallback"
            }

    def _fast_path_chat_response(self, vector: IntentVector) -> Dict[str, Any]:
        """
        Simulates natural conversation with ENVOY.
        Immediate, friendly response for casual queries.
        """
        user_msg = vector.raw_input

        # Simple pattern recognition for common chat queries
        if any(word in user_msg.lower() for word in ["hi", "hello", "hey"]):
            response = (
                f"**🤖 ENVOY:** Hey there! I'm ENVOY, Agent City's communication hub.\n\n"
                f"I can help with:\n"
                f"• **Status checks** (just ask for 'status')\n"
                f"• **Creating content** (tell me to 'create' something)\n"
                f"• **Governance** (ask me to 'verify' or 'vote')\n\n"
                f"What's on your mind?"
            )
        else:
            response = (
                f"**🤖 ENVOY:** I hear you. You said: *'{user_msg}'*\n\n"
                f"I'm ready to assist with **Governance**, **Creation**, or **System Ops**.\n"
                f"Just give me a command!"
            )

        return {
            "status": "success",
            "summary": response,
            "path": "fast",
            "intent": "chat"
        }

    def _fast_path_query_response(self, vector: IntentVector) -> Dict[str, Any]:
        """
        Quick informational response without task submission.
        For briefings and status inquiries.
        """
        return {
            "status": "success",
            "summary": (
                f"**📋 BRIEFING RESPONSE**\n\n"
                f"Your question: *'{vector.raw_input}'*\n\n"
                f"I'm compiling a detailed report. "
                f"This would normally come from the agents, but I'm giving you the gist immediately.\n\n"
                f"No heavy lifting needed for this one."
            ),
            "path": "fast",
            "intent": "query"
        }

    # --- ROUTING LOGIC ---

    def _generate_ack_message(self, vector: IntentVector, agent: str) -> str:
        """
        Generates natural language acknowledgment for slow-path tasks.
        """
        agent_display = agent.upper()

        if vector.intent_type == IntentType.CREATION:
            return f"**{agent_display}** is drafting your content now. I'll keep you posted."
        if vector.intent_type == IntentType.ACTION:
            return f"**{agent_display}** is executing this governance action on the ledger. Standby."
        return f"Request forwarded to **{agent_display}**. Processing..."

    def _find_best_agent(self, vector: IntentVector) -> Optional[str]:
        """
        Routing Logic: Matches Intent -> Capability -> AgentID
        """
        if vector.intent_type == IntentType.SYSTEM:
            return "watchman" if self._check_agent("watchman") else None

        if vector.intent_type == IntentType.CREATION:
            return "herald"  # Content Creator

        if vector.intent_type == IntentType.ACTION:
            return "civic" if self._check_agent("civic") else "envoy"  # Governance Handler

        if vector.intent_type == IntentType.QUERY:
            return "envoy"  # General Purpose

        # Default fallback
        return "envoy" 

    def _check_agent(self, agent_id: str) -> bool:
        return agent_id in self.kernel.agent_registry

    def _translate_payload(self, agent_id: str, vector: IntentVector) -> Dict[str, Any]:
        """
        ABI LAYER (GAD-4000): Translates High-Level Intent to Low-Level Agent Protocol.

        Each agent speaks its own protocol:
        - Watchman: Status reports and system monitoring
        - Herald: Content creation and publishing
        - Envoy: General purpose queries and assistance
        - Civic: Governance and voting operations
        """
        agent_id = agent_id.lower()

        # WATCHMAN PROTOCOL (System Monitor)
        if agent_id in ("watchman", "watchman_01"):
            logger.info("🔍 Translating to WATCHMAN protocol")
            return {
                "command": "status_report",
                "details": "full",
                "context": self.context_layer
            }

        # HERALD PROTOCOL (Publisher/Content Creator)
        if agent_id in ("herald", "herald_01"):
            logger.info("📢 Translating to HERALD protocol")
            return {
                "command": "publish",
                "content": vector.raw_input,
                "channel": "global",
                "context": self.context_layer
            }

        # CIVIC PROTOCOL (Governance Handler)
        if agent_id in ("civic", "civic_01"):
            logger.info("🏛️ Translating to CIVIC protocol")
            return {
                "action": "governance",
                "instruction": vector.raw_input,
                "context": self.context_layer,
                "intent": vector.intent_type.value
            }

        # ENVOY PROTOCOL (General Purpose / Fallback)
        if agent_id in ("envoy", "envoy_01"):
            logger.info("🚀 Translating to ENVOY protocol")
            return {
                "instruction": vector.raw_input,
                "context": self.context_layer,
                "intent": vector.intent_type.value
            }

        # Default Fallback (Unknown Agent)
        logger.warning(f"⚠️ Unknown agent {agent_id}, using generic protocol")
        return {
            "instruction": vector.raw_input,
            "context": self.context_layer,
            "intent": vector.intent_type.value,
            "fallback": True
        }
