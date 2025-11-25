"""
🌌 UNIVERSAL PROVIDER (GAD-5000: DHARMIC EDITION)
The Central Nervous System of Agent City.
Now with Deterministic Knowledge Graph Routing (Sankhya + Karma).

Role:
1. Receives abstract INTENTS (from User/Chat)
2. Analyzes input via CONCEPT MAP (semantic normalization)
3. Matches against INTENT RULES (deterministic routing)
4. Routes to FAST-PATH (instant response) or SLOW-PATH (async task)
5. Injects CONTEXT (Time, Location, Ledger State)
6. Executes via KERNEL with natural language UX

Architecture:
- Sankhya: Breaks input into atomic concepts via knowledge/concept_map.yaml
- Dharma: Applies deterministic rules from knowledge/intent_rules.yaml
- Karma: Executes routed action with perfect determinism
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import yaml
from pathlib import Path

# Import Core Definitions
try:
    from vibe_core.kernel import VibeKernel
    from vibe_core.scheduling import Task
except ImportError:
    # Mock for bootstrapping if kernel isn't in path yet
    VibeKernel = Any
    Task = Any

# Import LLM Engine (GAD-6000)
try:
    from services.llm_engine import llm
except ImportError:
    llm = None

logger = logging.getLogger("UNIVERSAL_PROVIDER")

class DeterministicRouter:
    """
    🧠 SANKHYA ANALYSIS ENGINE
    Breaks raw input into atomic semantic concepts.
    Then applies strict DHARMA (rules) for deterministic routing.
    """
    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.concepts = self._load_yaml("concept_map.yaml")
        self.rules = self._load_yaml("intent_rules.yaml").get("rules", [])
        logger.info("🧠 Deterministic Knowledge Graph loaded (SANKHYA + DHARMA)")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML file from knowledge directory"""
        filepath = self.knowledge_dir / filename
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️  Knowledge base not found: {filepath}")
            # Return empty structure to allow graceful degradation
            return {"rules": []} if filename == "intent_rules.yaml" else {}
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            return {"rules": []} if filename == "intent_rules.yaml" else {}

    def analyze(self, text: str) -> Set[str]:
        """
        SANKHYA: Breaks text down into atomic concepts.
        Scans all categories (actions, domains, entities, patterns).
        """
        found_concepts = set()
        if not self.concepts:
            return found_concepts

        text_lower = text.lower()
        tokens = text_lower.split()

        # Scan all concept categories
        for category, mappings in self.concepts.items():
            if not isinstance(mappings, dict):
                continue

            for concept, keywords in mappings.items():
                # Check if any keyword matches
                for keyword in keywords:
                    # Substring match for flexibility
                    if any(keyword in token for token in tokens):
                        found_concepts.add(concept)

        return found_concepts

    def route(self, text: str, fallback_rules: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        KARMA: Finds the deterministic route (agent, path, intent_type).
        Rules are evaluated top-to-bottom by priority.
        First matching rule wins.
        """
        active_concepts = self.analyze(text)
        logger.info(f"🔍 Detected Concepts: {active_concepts}")

        # Use provided rules or fall back to YAML-loaded rules
        rules_to_check = self.rules if self.rules else (fallback_rules or [])

        # Iterate rules by priority (top to bottom)
        for rule in rules_to_check:
            triggers = set(rule.get("triggers", []))

            # Logic: Does the input contain ALL required triggers?
            # Empty triggers = Fallback rule
            if not triggers or triggers.issubset(active_concepts):
                return {
                    "agent": rule.get("agent", "envoy"),
                    "rule_name": rule.get("name", "Unknown Rule"),
                    "response_type": rule.get("response_type", "FAST"),
                    "intent_type": rule.get("intent_type", "CHAT"),
                    "concepts": active_concepts,
                    "matched_triggers": triggers & active_concepts if triggers else set()
                }

        # Ultimate fallback (should not reach here if YAML has fallback rule)
        logger.warning("⚠️  No rules matched, using hard fallback")
        return {
            "agent": "envoy",
            "rule_name": "Hard Fallback",
            "response_type": "FAST",
            "intent_type": "CHAT",
            "concepts": active_concepts,
            "matched_triggers": set()
        }


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
    def __init__(self, kernel: VibeKernel, knowledge_dir: str = "knowledge"):
        self.kernel = kernel
        self.context_layer = {
            "location": "Agent City / Central Plaza",
            "access_level": "OPERATOR",
            "last_interaction": time.time()
        }
        # Initialize the deterministic router with knowledge graphs
        self.router = DeterministicRouter(knowledge_dir=knowledge_dir)
        logger.info("🌌 Universal Provider GAD-5000 (DHARMIC) initialized with deterministic routing")

    def resolve_intent(self, user_input: str) -> IntentVector:
        """
        DHARMIC ROUTING: Uses deterministic knowledge graphs to resolve intent.
        Backed by concept maps and intent rules from YAML configuration.
        Gracefully falls back to legacy logic if knowledge graphs unavailable.
        """
        # Step 1: SANKHYA - Analyze input via knowledge graph
        route_result = self.router.route(user_input)

        # Step 2: MAP ROUTER OUTPUT TO INTENTVECTOR
        intent_type_str = route_result.get("intent_type", "CHAT")
        target_agent = route_result.get("agent", "envoy")
        rule_name = route_result.get("rule_name", "Unknown")

        # Convert string intent_type to enum
        intent_map = {
            "SYSTEM": IntentType.SYSTEM,
            "QUERY": IntentType.QUERY,
            "CREATION": IntentType.CREATION,
            "ACTION": IntentType.ACTION,
            "CHAT": IntentType.CHAT
        }
        intent_type = intent_map.get(intent_type_str, IntentType.CHAT)

        # Determine confidence based on rule match
        matched_triggers = route_result.get("matched_triggers", set())
        confidence = 0.95 if matched_triggers else 0.70

        logger.info(f"⚖️  Dharmic Ruling: '{user_input}' -> {target_agent} ({rule_name})")

        return IntentVector(
            raw_input=user_input,
            intent_type=intent_type,
            target_domain=target_agent,
            confidence=confidence,
            parameters={"rule": rule_name, "concepts": list(route_result.get("concepts", []))}
        )

    def route_and_execute(self, user_input: str) -> Dict[str, Any]:
        """
        The Magic Entry Point for VibeChat (GAD-5000 DHARMIC).
        Uses deterministic routing to decide between FAST-PATH (instant response)
        and SLOW-PATH (async queueing).
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
                "path": "slow",
                "summary": f"🤖 {response_msg}",
                "details": {
                    "task_id": task_id,
                    "agent": target_agent_id,
                    "intent": vector.intent_type.value
                }
            }
        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            return {
                "status": "FAILED",
                "path": "slow",
                "error": str(e)
            }

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
        Natural conversation via LLM Engine (GAD-6000).
        Immediate, dynamic response for casual queries.
        Routed to ENVOY agent with context.
        """
        user_msg = vector.raw_input
        agent_name = "ENVOY"

        # Generate context for LLM
        context = "Fast-path conversational response to casual user query"

        # Generate dynamic response via LLM Engine
        if llm:
            response = llm.speak(agent_name, context, user_msg)
        else:
            # Fallback to static response if LLM unavailable
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
        Generates dynamic acknowledgment for slow-path tasks via LLM Engine.
        Contextualizes the task type (creation, action, etc.) for natural language.
        """
        agent_display = agent.upper()
        user_input = vector.raw_input

        # Build context based on intent type
        if vector.intent_type == IntentType.CREATION:
            context = f"User initiated CREATION task. {agent_display} agent is handling content generation. Confirm receipt and mention background processing."
        elif vector.intent_type == IntentType.ACTION:
            context = f"User initiated ACTION/GOVERNANCE task. {agent_display} agent is handling state-changing operation. Confirm and mention ledger immutability."
        else:
            context = f"User initiated task. {agent_display} agent is processing. Confirm receipt."

        # Generate dynamic acknowledgment via LLM Engine
        if llm:
            return llm.speak(agent_display, context, user_input)
        else:
            # Fallback to static response
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
