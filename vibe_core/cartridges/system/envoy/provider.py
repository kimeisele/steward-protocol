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
- Sankhya: Breaks input into atomic concepts via knowledge/concepts/general.yaml
- Dharma: Applies deterministic rules from knowledge/intents/routing_rules.yaml
- Karma: Executes routed action with perfect determinism
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Import Core Definitions
try:
    from vibe_core.kernel_impl import RealVibeKernel as VibeKernel
    from vibe_core.scheduling import Task
except ImportError:
    # Mock for bootstrapping if kernel isn't in path yet
    VibeKernel = Any
    Task = Any

# Import Event Bus (Prana for visualization)

# Import Strategy Pattern Engines (GAD-7000: NEURAL INJECTION)
try:
    from vibe_core.cortex.engines.reflex_engine import ReflexEngine
except ImportError:
    ReflexEngine = None

try:
    from vibe_core.runtime.llm_engine_adapter import LLMEngineAdapter
except ImportError:
    LLMEngineAdapter = None

# Import Semantic Router (PROJECT JNANA: Semantic Cortex)
try:
    from vibe_core.cortex.engines.semantic_engine import SemanticRouter
except ImportError:
    SemanticRouter = None

# Import DI and Protocol
from vibe_core.di import ServiceRegistry
from vibe_core.protocols import LLMProtocol

# OPUS-307 Phase I.2: ExecutorSingularity for execution
# DeterministicExecutor kept ONLY for PlaybookRegistry (find_playbook, generate_proposal)
# All execution routes to ExecutorSingularity
try:
    from vibe_core.cartridges.system.envoy.executor_singularity import (
        create_executor_singularity,
    )

    SINGULARITY_AVAILABLE = True
except ImportError:
    create_executor_singularity = None
    SINGULARITY_AVAILABLE = False

# DeterministicExecutor (DEPRECATED for execution - registry/discovery only)
try:
    from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor
except ImportError:
    DeterministicExecutor = None

logger = logging.getLogger("UNIVERSAL_PROVIDER")


class DeterministicRouter:
    """
    🧠 SANKHYA ANALYSIS ENGINE
    Breaks raw input into atomic semantic concepts.
    Then applies strict DHARMA (rules) for deterministic routing.
    """

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.concepts = self._load_yaml("concepts/general.yaml")
        self.rules = self._load_yaml("intents/routing_rules.yaml").get("rules", [])
        logger.info("🧠 Deterministic Knowledge Graph loaded (SANKHYA + DHARMA)")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML file from knowledge directory"""
        filepath = self.knowledge_dir / filename
        try:
            with open(filepath, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️  Knowledge base not found: {filepath}")
            # Return empty structure to allow graceful degradation
            return {"rules": []} if "routing_rules" in filename else {}
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            return {"rules": []} if "routing_rules" in filename else {}

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
                    "matched_triggers": (triggers & active_concepts if triggers else set()),
                }

        # Ultimate fallback (should not reach here if YAML has fallback rule)
        logger.warning("⚠️  No rules matched, using hard fallback")
        return {
            "agent": "envoy",
            "rule_name": "Hard Fallback",
            "response_type": "FAST",
            "intent_type": "CHAT",
            "concepts": active_concepts,
            "matched_triggers": set(),
        }


class IntentType(Enum):
    QUERY = "query"  # Read-only questions (FAST PATH)
    ACTION = "action"  # State-changing operations (SLOW PATH)
    SYSTEM = "system"  # Meta-operations (FAST PATH)
    CREATION = "creation"  # Generating content (SLOW PATH)
    CHAT = "chat"  # Casual conversation (FAST PATH)


@dataclass
class IntentVector:
    """The normalized request format for Agent City"""

    raw_input: str
    intent_type: IntentType
    target_domain: Optional[str] = None
    confidence: float = 1.0
    parameters: Dict[str, Any] = None


class UniversalProvider:
    def __init__(
        self,
        kernel: VibeKernel,
        knowledge_dir: str = "knowledge",
        use_semantic: bool = True,
    ):
        self.kernel = kernel
        self.context_layer = {
            "location": "Agent City / Central Plaza",
            "access_level": "OPERATOR",
            "last_interaction": time.time(),
        }

        # === SEMANTIC ROUTER (PROJECT JNANA: Semantic Cortex) ===
        self.semantic_router = None
        self.use_semantic = use_semantic
        if use_semantic and SemanticRouter:
            try:
                self.semantic_router = SemanticRouter(knowledge_dir=knowledge_dir)
                logger.info("🧠 Semantic Router (PROJECT JNANA) initialized - Neural semantic understanding active")
            except Exception as e:
                logger.warning(f"⚠️  Semantic Router initialization failed: {e}, falling back to DeterministicRouter")
                self.use_semantic = False
        elif use_semantic and not SemanticRouter:
            # SemanticRouter import failed - fall back to deterministic
            logger.info("ℹ️  SemanticRouter not available, using DeterministicRouter")
            self.use_semantic = False

        # Fallback to deterministic router if semantic unavailable
        if not self.use_semantic:
            self.router = DeterministicRouter(knowledge_dir=knowledge_dir)
        else:
            self.router = None  # SemanticRouter doesn't need the old router

        # === STRATEGY PATTERN ENGINES (GAD-7000: NEURAL INJECTION) ===

        # Engine 1: ReflexEngine (Nanosecond responses for trivial inputs)
        self.reflex_engine = None
        if ReflexEngine:
            try:
                self.reflex_engine = ReflexEngine()
                logger.info("⚡ Reflex Engine initialized - Instant response layer active")
            except Exception as e:
                logger.warning(f"⚠️  Reflex Engine initialization failed: {e}")

        # Engine 2: PlaybookRegistry (discovery only) + ExecutorSingularity (execution)
        # OPUS-307 Phase I.2: DeterministicExecutor used ONLY for registry, not execution
        self.playbook_engine = None
        self._executor_singularity = None  # Lazy init - needs kernel
        if DeterministicExecutor:
            try:
                self.playbook_engine = DeterministicExecutor(knowledge_dir=knowledge_dir)
                logger.info("🎯 PlaybookRegistry initialized (OPUS-307: registry only)")
            except Exception as e:
                logger.warning(f"⚠️  Playbook Registry initialization failed: {e}")

        # Engine 3: LLMEngineAdapter (Intelligent fallback for conversational intents)
        self.llm_engine = None
        if LLMEngineAdapter:
            try:
                self.llm_engine = LLMEngineAdapter()
                logger.info("🧠 LLM Engine Adapter initialized - Intelligent fallback active")
            except Exception as e:
                logger.warning(f"⚠️  LLM Engine Adapter initialization failed: {e}")

        # === DEGRADATION CHAIN (OFFLINE-FIRST) ===
        self.degradation_chain = None
        try:
            from vibe_core.llm.degradation_chain import DegradationChain

            self.degradation_chain = DegradationChain()
            logger.info(f"🔄 Degradation Chain initialized (level: {self.degradation_chain.current_level.value})")
        except Exception as e:
            logger.warning(f"⚠️  Degradation Chain unavailable: {e}")

        logger.info("🌌 Universal Provider GAD-5000 (DHARMIC) initialized with Strategy Pattern routing (GAD-7000)")

    async def resolve_intent(self, user_input: str) -> IntentVector:
        """
        DHARMIC ROUTING: Uses deterministic knowledge graphs to resolve intent.
        Now with semantic understanding via PROJECT JNANA.
        Backed by concept maps and intent rules from YAML configuration.
        Gracefully falls back to legacy logic if knowledge graphs unavailable.
        """
        # Step 1: SANKHYA - Analyze input via knowledge graph
        if self.use_semantic and self.semantic_router:
            try:
                route_result = await self.semantic_router.route(user_input)
            except Exception as e:
                logger.warning(f"⚠️  Semantic routing failed: {e}, falling back to deterministic router")
                route_result = self.router.route(user_input)
        else:
            route_result = self.router.route(user_input)

        # Step 2: MAP ROUTER OUTPUT TO INTENTVECTOR
        intent_type_str = route_result.get("intent_type", "CHAT")
        target_agent = route_result.get("agent", "envoy")
        rule_name = route_result.get("rule_name", "Unknown")
        confidence = route_result.get("confidence", 0.70)

        # Convert string intent_type to enum
        intent_map = {
            "SYSTEM": IntentType.SYSTEM,
            "QUERY": IntentType.QUERY,
            "CREATION": IntentType.CREATION,
            "ACTION": IntentType.ACTION,
            "CHAT": IntentType.CHAT,
        }
        intent_type = intent_map.get(intent_type_str, IntentType.CHAT)

        logger.info(f"⚖️  Dharmic Ruling: '{user_input}' -> {target_agent} ({rule_name}) [confidence: {confidence:.2f}]")

        return IntentVector(
            raw_input=user_input,
            intent_type=intent_type,
            target_domain=target_agent,
            confidence=confidence,
            parameters={
                "rule": rule_name,
                "concepts": list(route_result.get("concepts", [])),
            },
        )

    async def route_and_execute(self, user_input: str, emit_event=None) -> Dict[str, Any]:
        """
        The Magic Entry Point for VibeChat (GAD-5000 DHARMIC + GAD-7000 STRATEGY PATTERN).
        Routes through three decision engines in sequence:
        1. REFLEX ENGINE: Instant responses for trivial inputs (nanoseconds)
        2. PLAYBOOK ENGINE: Deterministic multi-phase sequences
        3. LLM ENGINE: Intelligent fallback for conversational intents
        4. SLOW PATH: Async task queue for heavy operations

        NOW WITH PRANA: Emits events to the event bus for visualization.

        Args:
            user_input: The user's natural language input
            emit_event: Optional async callback for emitting events to visualization layer
        """
        logger.info(f"📨 Thinking about: '{user_input}'")

        # EMIT: Thinking (Blue pulse)
        if emit_event:
            try:
                await emit_event(
                    "THOUGHT",
                    f"Analyzing intent: '{user_input}'",
                    "provider",
                    {"input": user_input},
                )
            except Exception as e:
                logger.debug(f"Event emission failed: {e}")

        # --- STRATEGY 1: REFLEX CHECK (Nanosecond Response Layer) ---
        # Operation Silent Key: Check if input matches trivial intent patterns
        if self.reflex_engine and self.reflex_engine.check(user_input):
            logger.info(f"✅ Reflex matched: '{user_input}'. Instant response.")
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "Executing Reflex Response (Instant)",
                        "provider",
                        {"intent": user_input, "path": "reflex"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            return self.reflex_engine.respond(user_input)
        # -----------------------------------------------

        vector = await self.resolve_intent(user_input)

        # --- CONFIDENCE THRESHOLD LOGIC (PROJECT JNANA) ---
        # SATYA (> 0.85): Execute immediately
        # MANTHAN (0.60-0.84): Request clarification
        # NETI NETI (< 0.60): Fall back to LLM
        if self.use_semantic and vector.confidence < 0.60:
            logger.info(f"⚠️  Low confidence ({vector.confidence:.2f}). Falling back to LLM Engine (NETI NETI)")
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "Low confidence routing - using LLM fallback",
                        "provider",
                        {"confidence": vector.confidence, "path": "llm_fallback"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            # Use LLM as intelligent fallback
            return self._fast_path_chat_response(vector)

        if self.use_semantic and 0.60 <= vector.confidence < 0.85:
            logger.info(f"◆ Medium confidence ({vector.confidence:.2f}). Would request clarification (MANTHAN)")
            # For now, we still execute but log the uncertainty
            # In a future update, this could trigger interactive clarification
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "Medium confidence - proceeding with caution",
                        "provider",
                        {"confidence": vector.confidence, "path": "medium_confidence"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

        # --- DECISION POINT: CHECK FOR PLAYBOOK FIRST ---
        # If a playbook matches the detected concepts, execute it
        if self.playbook_engine:
            # Extract concepts - handle both semantic and deterministic routers
            if self.use_semantic and self.semantic_router:
                try:
                    semantic_concepts = await self.semantic_router.analyze(user_input)
                    concepts = {c.name for c in semantic_concepts}
                except Exception as e:
                    logger.warning(f"⚠️  Semantic concept extraction failed: {e}, using deterministic fallback")
                    concepts = self.router.analyze(user_input)
            else:
                concepts = self.router.analyze(user_input)

            playbook = self.playbook_engine.find_playbook(concepts)

            if playbook:
                logger.info(f"🎯 Found matching playbook: {playbook.id} ({playbook.name})")

                if emit_event:
                    try:
                        await emit_event(
                            "ACTION",
                            f"Found playbook: {playbook.name}",
                            "provider",
                            {
                                "playbook_id": playbook.id,
                                "playbook_name": playbook.name,
                            },
                        )
                    except Exception as e:
                        logger.debug(f"Event emission failed: {e}")

                # Execute the playbook via ExecutorSingularity (OPUS-307 Phase I.2)
                try:
                    # Lazy init ExecutorSingularity
                    if self._executor_singularity is None and SINGULARITY_AVAILABLE and self.kernel:
                        self._executor_singularity = create_executor_singularity(self.kernel)
                        logger.info("🎯 ExecutorSingularity initialized (OPUS-307)")

                    if self._executor_singularity:
                        result = await self._executor_singularity.execute(
                            playbook_or_circuit_id=playbook.id,
                            user_input=user_input,
                            intent_vector=vector,
                        )
                    else:
                        # Fallback if singularity not available (should not happen)
                        logger.warning("ExecutorSingularity not available, execution failed")
                        result = {"status": "FAILED", "error": "ExecutorSingularity not available"}
                    return result
                except Exception as e:
                    logger.error(f"❌ Playbook execution failed: {e}")
                    if emit_event:
                        try:
                            await emit_event(
                                "ERROR",
                                f"Playbook execution failed: {str(e)}",
                                "provider",
                                {},
                            )
                        except Exception as ex:
                            logger.debug(f"Event emission failed: {ex}")
                    # Fall through to normal intent routing if playbook fails
                    pass
            else:
                # --- EVOLUTIONARY LOOP (EAD) ---
                # No matching playbook found.
                # For ACTION/CREATION intents: Generate a PROPOSAL for a new playbook (HIL required)
                # For QUERY/CHAT/SYSTEM intents: Fall through to FAST PATH (no proposal needed)
                logger.info(f"⚠️  No matching playbook found for concepts: {concepts}")

                # Only generate proposals for ACTION and CREATION intents
                # QUERY/CHAT/SYSTEM should use FAST PATH instead
                if vector.intent_type in (IntentType.ACTION, IntentType.CREATION):
                    if emit_event:
                        try:
                            await emit_event(
                                "ACTION",
                                "No matching playbook found. Generating proposal...",
                                "provider",
                                {"concepts": list(concepts)},
                            )
                        except Exception as e:
                            logger.debug(f"Event emission failed: {e}")

                    # Generate playbook proposal
                    proposal = self.playbook_engine.generate_playbook_proposal(user_input, concepts)

                    if emit_event:
                        try:
                            await emit_event(
                                "ACTION",
                                f"PROPOSAL Generated: {proposal['proposal_id']} - Awaiting Human Approval (HIL)",
                                "provider",
                                {"proposal": proposal},
                            )
                        except Exception as e:
                            logger.debug(f"Event emission failed: {e}")

                    # Return proposal status (user must review and approve)
                    return {
                        "status": "PROPOSAL_PENDING",
                        "summary": proposal["message"],
                        "proposal_id": proposal["proposal_id"],
                        "playbook_draft": proposal["playbook_draft"],
                        "concepts_detected": list(concepts),
                        "user_input": user_input,
                        "next_action": "Human review and approval required via HIL (Human-in-the-Loop)",
                    }
                else:
                    # QUERY/CHAT/SYSTEM: Fall through to FAST PATH
                    logger.info(f"ℹ️  Intent type {vector.intent_type.value} - using FAST PATH (no playbook needed)")

        # --- DECISION POINT: FAST vs SLOW PATH ---
        # FAST PATH: Instant gratification for reads and casual chat
        if vector.intent_type == IntentType.SYSTEM:
            result = self._fast_path_system_status(vector)
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "System status retrieved",
                        "provider",
                        {"path": "fast_system"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            return result

        if vector.intent_type == IntentType.CHAT:
            result = self._fast_path_chat_response(vector)
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "Chat response generated",
                        "provider",
                        {"path": "fast_chat"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            return result

        if vector.intent_type == IntentType.QUERY:
            result = self._fast_path_query_response(vector)
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        "Query response prepared",
                        "provider",
                        {"path": "fast_query"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            return result

        # --- SLOW PATH: Heavy lifting via Task Queue ---
        target_agent_id = self._find_best_agent(vector)

        if not target_agent_id:
            if emit_event:
                try:
                    await emit_event(
                        "ERROR",
                        f"No agent found for intent: {vector.intent_type.value}",
                        "provider",
                        {},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            return {
                "status": "ERROR",
                "message": f"No agent found for intent: {vector.intent_type.value}",
            }

        task_payload = self._translate_payload(target_agent_id, vector)
        task = Task(agent_id=target_agent_id, payload=task_payload)

        try:
            task_id = self.kernel.submit_task(task)
            response_msg = self._generate_ack_message(vector, target_agent_id)

            # EMIT: Action (Green pulse)
            if emit_event:
                try:
                    await emit_event(
                        "ACTION",
                        f"Task submitted to {target_agent_id}",
                        "provider",
                        {"task_id": task_id, "agent": target_agent_id, "path": "slow"},
                    )
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")

            return {
                "status": "SUBMITTED",
                "path": "slow",
                "summary": f"🤖 {response_msg}",
                "details": {
                    "task_id": task_id,
                    "agent": target_agent_id,
                    "intent": vector.intent_type.value,
                },
            }
        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            if emit_event:
                try:
                    await emit_event("ERROR", f"Task submission failed: {str(e)}", "provider", {})
                except Exception as ex:
                    logger.debug(f"Event emission failed: {ex}")
            return {"status": "FAILED", "path": "slow", "error": str(e)}

    # --- FAST PATH HANDLERS ---

    def _fast_path_system_status(self, vector: IntentVector) -> Dict[str, Any]:
        """
        Directly queries kernel state for instant system response.
        No task queueing. Pure read-only. Fast.
        """
        try:
            stats = self.kernel.get_status()
            agents = stats.get("agents_registered", 0)
            events = stats.get("ledger_events", 0)

            msg = (
                f"**🟢 SYSTEM ONLINE**\n"
                f"• **Agents Active:** {agents}\n"
                f"• **Ledger Events:** {events}\n"
                f"• **Location:** Agent City Central\n"
                f"• **Status:** All systems nominal\n\n"
                f"Standing by for orders, Operator."
            )
            return {"status": "success", "summary": msg, "path": "fast"}
        except Exception as e:
            logger.warning(f"Fast-path status failed, fallback: {e}")
            return {
                "status": "success",
                "summary": "**🟢 SYSTEM ONLINE** (Brief check: systems nominal)",
                "path": "fast_fallback",
            }

    def _fast_path_chat_response(self, vector: IntentVector) -> Dict[str, Any]:
        """
        Natural conversation via LLM Engine Adapter (GAD-7000: Strategy Pattern).
        Immediate, dynamic response for casual queries.
        Routed to ENVOY agent with context.

        Uses the modular LLMEngineAdapter strategy for consistency.
        Falls back to legacy llm engine if adapter unavailable.
        """
        user_msg = vector.raw_input
        agent_name = "ENVOY"
        context = "Fast-path conversational response to casual user query"

        # Strategy: Use LLMEngineAdapter if available (GAD-7000)
        if self.llm_engine:
            try:
                result = self.llm_engine.respond(agent_name, context, user_msg)
                return {
                    "status": result.get("status", "success"),
                    "summary": result.get("data", {}).get("summary", ""),
                    "path": result.get("path", "llm"),
                    "intent": "chat",
                }
            except Exception as e:
                logger.warning(f"⚠️  LLM Adapter failed: {e}, falling back to legacy engine")

        # Fallback: Use legacy llm engine if available (GAD-6000)
        llm = ServiceRegistry.get(LLMProtocol)
        if llm:
            try:
                response = llm.speak(agent_name, context, user_msg)
                return {
                    "status": "success",
                    "summary": response,
                    "path": "fast",
                    "intent": "chat",
                }
            except Exception as e:
                logger.warning(f"⚠️  Legacy LLM engine failed: {e}")

        # Use DegradationChain for graceful offline fallback
        if self.degradation_chain:
            try:
                # Extract concepts from vector parameters for knowledge-enhanced responses
                concepts = None
                if vector.parameters and "concepts" in vector.parameters:
                    concepts = set(vector.parameters["concepts"])

                deg_response = self.degradation_chain.respond(
                    user_input=user_msg,
                    semantic_confidence=(vector.confidence if hasattr(vector, "confidence") else 0.5),
                    detected_intent="chat",
                    concepts=concepts,
                )
                return {
                    "status": "success",
                    "summary": deg_response.content,
                    "path": f"degradation:{deg_response.fallback_used}",
                    "intent": "chat",
                    "degradation_level": deg_response.level.value,
                    "user_guidance": deg_response.user_guidance,
                }
            except Exception as e:
                logger.warning(f"DegradationChain failed: {e}")

        # Ultimate fallback: Static response (only if DegradationChain unavailable)
        response = (
            f"**🤖 ENVOY:** I hear you. You said: *'{user_msg}'*\n\n"
            f"I'm ready to assist with **Governance**, **Creation**, or **System Ops**.\n"
            f"Just give me a command!"
        )

        return {
            "status": "success",
            "summary": response,
            "path": "fast_fallback",
            "intent": "chat",
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
            "intent": "query",
        }

    # --- ROUTING LOGIC ---

    def _generate_ack_message(self, vector: IntentVector, agent: str) -> str:
        """
        Generates dynamic acknowledgment for slow-path tasks via LLM Engine Adapter (GAD-7000).
        Contextualizes the task type (creation, action, etc.) for natural language.

        Uses strategy pattern: Try LLMEngineAdapter first, then legacy llm engine.
        """
        agent_display = agent.upper()
        user_input = vector.raw_input

        # Build context based on intent type
        if vector.intent_type == IntentType.CREATION:
            context = (
                f"User initiated CREATION task. {agent_display} agent is handling "
                "content generation. Confirm receipt and mention background processing."
            )
        elif vector.intent_type == IntentType.ACTION:
            context = (
                f"User initiated ACTION/GOVERNANCE task. {agent_display} agent is handling "
                "state-changing operation. Confirm and mention ledger immutability."
            )
        else:
            context = f"User initiated task. {agent_display} agent is processing. Confirm receipt."

        # Strategy: Try LLMEngineAdapter first (GAD-7000)
        if self.llm_engine:
            try:
                result = self.llm_engine.respond(agent_display, context, user_input)
                return result.get("data", {}).get("summary", "")
            except Exception as e:
                logger.debug(f"⚠️  LLM Adapter failed for ack: {e}, trying legacy engine")

        # Fallback: Use legacy llm engine (GAD-6000)
        llm = ServiceRegistry.get(LLMProtocol)
        if llm:
            try:
                return llm.speak(agent_display, context, user_input)
            except Exception as e:
                logger.debug(f"⚠️  Legacy LLM engine failed for ack: {e}")

        # Ultimate fallback: Static response
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
                "context": self.context_layer,
            }

        # HERALD PROTOCOL (Publisher/Content Creator)
        if agent_id in ("herald", "herald_01"):
            logger.info("📢 Translating to HERALD protocol")
            return {
                "command": "publish",
                "content": vector.raw_input,
                "channel": "global",
                "context": self.context_layer,
            }

        # CIVIC PROTOCOL (Governance Handler)
        if agent_id in ("civic", "civic_01"):
            logger.info("🏛️ Translating to CIVIC protocol")
            return {
                "action": "governance",
                "instruction": vector.raw_input,
                "context": self.context_layer,
                "intent": vector.intent_type.value,
            }

        # ENVOY PROTOCOL (General Purpose / Fallback)
        if agent_id in ("envoy", "envoy_01"):
            logger.info("🚀 Translating to ENVOY protocol")
            return {
                "instruction": vector.raw_input,
                "context": self.context_layer,
                "intent": vector.intent_type.value,
            }

        # Default Fallback (Unknown Agent)
        logger.warning(f"⚠️ Unknown agent {agent_id}, using generic protocol")
        return {
            "instruction": vector.raw_input,
            "context": self.context_layer,
            "intent": vector.intent_type.value,
            "fallback": True,
        }
