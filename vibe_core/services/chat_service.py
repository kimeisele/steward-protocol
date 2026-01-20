"""
CHAT SERVICE - Starship Command I/O
====================================

NOT a LangChain-style template wrapper.
This is an Agent OS I/O bus.

FLOW (Resonance-Based):
    User Message
        ↓
    ResonanceEngine.resonate() → ResonanceVector (magnitude = confidence)
        ↓
    RESONANCE GATE:
        > 0.8: Auto-execute → LotusHologram → Mahajana → LLM
        0.4-0.8: Intent Negotiation → RefinementRequest → User Choice
        < 0.4: Silence → Error (refuse to guess)
        ↓
    KnowledgeGraph.query() → Live Context
        ↓
    LLM Provider.invoke() → Response (LLM = Interpreter, not brain)
        ↓
    ChatResponse (typed, GAD-000 compliant)

The LLM interprets machine language (Seed/Byte) into human terms.
The Substrate IS the brain.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xa8f3c901"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import uuid

from vibe_core.protocols.chat import (
    ChatProtocol,
    ChatMode,
    ChatMessage,
    ChatResponse,
    ChatContext,
    RefinementPath,
    RefinementRequest,
    RefinementState,
    CHAT_OPCODE,
    CHAT_PHASE,
    CHAT_WORD,
    CHAT_POSITION,
    DEFAULT_CHAT_CAPABILITIES,
)
from vibe_core.protocols.cognition import (
    CognitiveResult,
    IntentType,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.protocols._lotus import (
    LotusHologram,
    LotusRoute,
    get_position_mahajana,
    get_mahajana_position,
    MAHAJANA_POSITIONS,
)

# SUBSTRATE BRIDGE - Real vibration-based routing (not keyword matching)
from vibe_core.services.chat_substrate_bridge import (
    ChatSubstrateBridge,
    SubstrateRoute,
    get_substrate_bridge,
    THRESHOLD_MANIFEST,
    THRESHOLD_NEGOTIATE,
)

# QUANTUM REACTOR - Real manifestation (energy > inertia)
from vibe_core.reactor.quantum import (
    QuantumReactor,
    ResonanceField,
    get_reactor,
)

# REFINEMENT - Intent Negotiation (extracted for modularity)
from vibe_core.services.chat_refinement import (
    RefinementHandler,
    discover_refinement_paths,
    determine_chat_mode,
    get_dharma_description,
    simple_intent_detection,
    MAHAJANA_DHARMAS,
    POSITION_OPCODES,
)

logger = logging.getLogger("CHAT_SERVICE")


class ChatService(ChatProtocol):
    """
    Protocol-compliant Chat Service.

    Implements ChatProtocol with:
    - ResonanceEngine for phonetic resonance routing (no ML)
    - LotusHologram for O(1) position lookup
    - KnowledgeGraph for context enrichment
    - LLM Provider for response generation
    - Refinement Gate for intent negotiation
    - Full GAD-000 compliance

    RESONANCE THRESHOLDS (Starship Command I/O):
    - > 0.8: Auto-execute (high resonance)
    - 0.4 - 0.8: Intent Negotiation (refinement)
    - < 0.4: Silence (no resonance - refuse to guess)
    """

    # Resonance thresholds (from substrate - SSOT)
    RESONANCE_AUTO = THRESHOLD_MANIFEST  # Auto-execute (0.7)
    RESONANCE_REFINE = THRESHOLD_NEGOTIATE  # Ask for refinement (0.4)
    # Below 0.4 = Silence

    def __init__(self):
        self._lotus: LotusHologram = LotusHologram()  # O(1) routing
        self._substrate: ChatSubstrateBridge = get_substrate_bridge()  # REAL vibration routing
        self._reactor: QuantumReactor = get_reactor()  # Manifestation engine
        self._provider = None
        self._knowledge = None
        self._cognitive = None
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._refinement_states: Dict[str, "RefinementState"] = {}  # Per-session
        self._initialized = False

        # Refinement Handler (extracted for modularity)
        self._refinement_handler = RefinementHandler(
            sessions=self._sessions,
            refinement_states=self._refinement_states,
        )

        self._init_dependencies()

    def _init_dependencies(self) -> None:
        """Initialize all dependencies from protocols."""
        try:
            # Substrate Bridge initialized in __init__ (get_substrate_bridge)
            logger.info("✅ ChatService: SubstrateBridge initialized (VarnaTensor routing)")

            # Quantum Reactor initialized in __init__ (get_reactor)
            logger.info("✅ ChatService: QuantumReactor initialized (manifestation engine)")

            # LLM Provider (from config - NO HARDCODING)
            from vibe_core.runtime.providers.factory import create_provider, _detect_provider
            provider_name = _detect_provider()
            if provider_name != "noop":
                self._provider = create_provider(provider_name=provider_name)
                logger.info(f"✅ ChatService: LLM Provider initialized ({provider_name})")

            # Knowledge Graph
            try:
                from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
                self._knowledge = UnifiedKnowledgeGraph()
                logger.info("✅ ChatService: KnowledgeGraph initialized")
            except Exception as e:
                logger.warning(f"⚠️ ChatService: KnowledgeGraph not available: {e}")

            # Cognitive Protocol (for intent recognition)
            try:
                from vibe_core.services.kapila_service import KapilaService
                self._cognitive = KapilaService()
                logger.info("✅ ChatService: Cognitive (Kapila) initialized")
            except Exception as e:
                logger.warning(f"⚠️ ChatService: Cognitive not available: {e}")

            self._initialized = True

        except Exception as e:
            logger.error(f"❌ ChatService: Initialization failed: {e}")
            self._initialized = False

    # ==========================================================================
    # MANTRA PROPERTIES (ICliCommand compliance)
    # ==========================================================================

    @property
    def opcode(self) -> str:
        return CHAT_OPCODE.name

    @property
    def phase(self) -> str:
        return CHAT_PHASE

    @property
    def word(self) -> str:
        return CHAT_WORD

    @property
    def position(self) -> int:
        return CHAT_POSITION

    # ==========================================================================
    # CHAT OPERATIONS (Starship Command I/O)
    # ==========================================================================

    async def chat(self, message: str, context: ChatContext) -> ChatResponse:
        """
        Process chat message through Resonance Gate.

        RESONANCE GATE:
        1. Check for active RefinementState (user responding to "Path A or B?")
        2. Compute ResonanceVector → magnitude = confidence
        3. Apply thresholds:
           - > 0.8: Auto-execute
           - 0.4-0.8: Intent Negotiation (RefinementRequest)
           - < 0.4: Silence (refuse to guess)
        4. Route via Lotus → Mahajana
        5. LLM interprets (not decides)
        """
        timestamp = datetime.now()
        session_id = context.session_id

        # Create input message
        input_msg = ChatMessage(
            content=message,
            role="user",
            timestamp=timestamp,
            session_id=session_id,
            message_id=str(uuid.uuid4()),
        )

        # Store in session history
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(input_msg)

        try:
            # =================================================================
            # CHECK: Is this a response to a previous RefinementRequest?
            # =================================================================
            if self._refinement_handler.has_active_refinement(session_id):
                return await self._handle_refinement_response(message, context)

            # =================================================================
            # STEP 1: RESONANCE - Compute resonance vector
            # =================================================================
            resonance_result = self._compute_resonance(message)
            magnitude = resonance_result["magnitude"]
            logger.info(
                f"🔊 ChatService: Resonance magnitude={magnitude:.3f} "
                f"(dominant={resonance_result['dominant']})"
            )

            # =================================================================
            # RESONANCE GATE: Apply thresholds
            # =================================================================

            # SILENCE: < 0.4 - No resonance, refuse to guess
            if magnitude < self.RESONANCE_REFINE:
                logger.info(f"🔇 ChatService: SILENCE (magnitude {magnitude:.3f} < {self.RESONANCE_REFINE})")
                return self._refinement_handler.create_silence_response(message, context, magnitude)

            # REFINEMENT: 0.4 - 0.7 - Intent Negotiation required
            if magnitude < self.RESONANCE_AUTO:
                logger.info(f"❓ ChatService: REFINEMENT (magnitude {magnitude:.3f} in gray zone)")
                return await self._refinement_handler.create_refinement_response(message, context, resonance_result)

            # AUTO-EXECUTE: > 0.8 - High resonance, proceed
            logger.info(f"✅ ChatService: AUTO-EXECUTE (magnitude {magnitude:.3f} >= {self.RESONANCE_AUTO})")

            # =================================================================
            # STEP 2: COGNITIVE - Intent from INTENT_MAP
            # =================================================================
            cognitive_result = await self._process_cognitive(message)
            logger.info(f"🧠 ChatService: Intent={cognitive_result.intent_type.value}")

            # =================================================================
            # STEP 3: LOTUS ROUTING - O(1) position lookup + Substrate data
            # =================================================================
            lotus_result = self._lotus_route(message, cognitive_result, resonance_result)
            lotus_result["resonance"] = resonance_result  # Attach resonance data
            logger.info(
                f"🪷 ChatService: Lotus Route → {lotus_result['mahajana'].upper()} "
                f"(pos={lotus_result['position']}, quarter={lotus_result['quarter']})"
            )

            # Determine chat mode
            mode = determine_chat_mode(cognitive_result, lotus_result)

            # =================================================================
            # STEP 4: CONTEXT - Live substrate context
            # =================================================================
            knowledge_context = self._get_knowledge_context_lotus(message, lotus_result)

            # =================================================================
            # STEP 5: LLM - Interpreter (not brain)
            # =================================================================
            response_text = await self._generate_response_lotus(
                message=message,
                context=context,
                cognitive_result=cognitive_result,
                lotus_result=lotus_result,
                knowledge_context=knowledge_context,
            )

            # Create response message
            response_msg = ChatMessage(
                content=response_text,
                role="assistant",
                timestamp=datetime.now(),
                session_id=session_id,
                message_id=str(uuid.uuid4()),
                opcode=lotus_result.get("opcode", "EXTEND_CAP"),
                mahajana=lotus_result["mahajana"],
            )

            # Store response in history
            self._sessions[session_id].append(response_msg)

            return ChatResponse(
                success=True,
                message=response_msg,
                mode=mode,
                intent_type=cognitive_result.intent_type,
                opcode=lotus_result.get("opcode", "EXTEND_CAP"),
                mahajana=lotus_result["mahajana"],
                confidence=magnitude,  # Use resonance magnitude as confidence
            )

        except Exception as e:
            logger.error(f"❌ ChatService: Chat failed: {e}")
            error_msg = ChatMessage(
                content=f"Chat error: {e}",
                role="assistant",
                timestamp=datetime.now(),
                session_id=context.session_id,
            )
            return ChatResponse(
                success=False,
                message=error_msg,
                mode=ChatMode.DIRECT,
                error=str(e),
            )

    async def chat_with_routing(
        self, message: str, context: ChatContext, force_routing: bool = False
    ) -> ChatResponse:
        """Chat with explicit Mahajana routing."""
        # For now, same as chat() - routing is always semantic
        return await self.chat(message, context)

    # ==========================================================================
    # INTERNAL METHODS
    # ==========================================================================

    async def _process_cognitive(self, message: str) -> CognitiveResult:
        """Process message through cognitive protocol to get intent."""
        if self._cognitive:
            try:
                # Try full cognitive processing
                result = await self._cognitive.process_operator_input(
                    kernel=None,
                    input_text=message,
                )
                return result
            except Exception as e:
                # Expected when KapilaService uses NullCognitive - fallback is fine
                logger.debug(f"Cognitive not available, using INTENT_MAP fallback: {e}")

        # Fallback: Simple intent detection (INTENT_MAP SSOT - no ML)
        return simple_intent_detection(message)

    def _lotus_route(
        self, message: str, cognitive: CognitiveResult, resonance_result: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Route via Lotus + Substrate (O(1), VarnaTensor-based).

        Priority:
        1. If resonance_result has substrate_route → use it (REAL routing)
        2. Fallback to INTENT_MAP keyword matching (legacy)

        Uses LotusHologram for O(1) lookup.
        """
        # If we have substrate route from resonance, use it (PRIORITY)
        if resonance_result and "substrate_route" in resonance_result:
            route: SubstrateRoute = resonance_result["substrate_route"]

            # Get petal from Lotus (O(1))
            petal = self._lotus.get_petal(route.mahajana)

            # Determine opcode from quarter
            opcodes = ["SYS_WAKE", "COMPILE_AST", "EXEC_OP", "YIELD_CPU"]
            opcode = opcodes[route.quarter_idx]

            return {
                "mahajana": route.mahajana,
                "position": route.position,
                "quarter": route.quarter,
                "quarter_idx": route.quarter_idx,
                "opcode": opcode,
                "matched_keyword": None,  # Tensor-based, not keyword
                "confidence": resonance_result["magnitude"],
                "is_head": route.is_head,
                "petal": petal,
                # Substrate data (NEW)
                "substrate_route": route,
                "holy_name": route.holy_name.name,
                "energy": route.energy,
                "manifests": route.manifests,
            }

        # FALLBACK: Legacy keyword matching (INTENT_MAP)
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent

        msg_lower = message.lower()
        words = msg_lower.split()

        # Find matching position from INTENT_MAP
        matched_position = 2  # Default: NARADA (chat)
        matched_keyword = None

        for word in words:
            pos = get_position_for_intent(word)
            if pos >= 0:
                matched_position = pos
                matched_keyword = word
                break

        # Get mahajana from position
        mahajana = get_position_mahajana(matched_position)

        # Get petal from Lotus (O(1))
        petal = self._lotus.get_petal(mahajana)

        # Determine quarter
        quarter_idx = matched_position // 4
        quarter_names = ["GENESIS", "DHARMA", "KARMA", "MOKSHA"]
        quarter = quarter_names[quarter_idx]

        # Determine opcode from quarter
        opcodes = ["SYS_WAKE", "COMPILE_AST", "EXEC_OP", "YIELD_CPU"]
        opcode = opcodes[quarter_idx]

        return {
            "mahajana": mahajana,
            "position": matched_position,
            "quarter": quarter,
            "quarter_idx": quarter_idx,
            "opcode": opcode,
            "matched_keyword": matched_keyword,
            "confidence": 0.85 if matched_keyword else 0.6,
            "is_head": matched_position % 4 == 0,
            "petal": petal,
        }

    # ==========================================================================
    # RESONANCE GATE METHODS (Starship Command I/O)
    # ==========================================================================

    def _compute_resonance(self, message: str) -> Dict:
        """
        Compute resonance - CHAT IS ALWAYS ALIVE.

        PRINCIPLES:
        1. HOLY NAMES = HIGHEST RESONANCE (hare, krishna, rama = sacred)
        2. INTENT_MAP = Specific routing to Mahajanas
        3. NO MATCH = NARADA conversation (chat is ALWAYS possible!)
        4. NEVER SILENCE - Chat always responds!

        VarnaTensor observes phonetics for future Akasha learning.
        """
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP, get_position_for_intent
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        msg_lower = message.lower()
        words = msg_lower.split()

        # =================================================================
        # STEP 0: HOLY NAMES - The Highest Resonance (NEVER silence!)
        # =================================================================
        holy_names = {"hare", "krishna", "rama", "om", "hari", "govinda", "madhava"}
        has_holy_name = any(name in msg_lower for name in holy_names)

        if has_holy_name:
            # Holy Names = NARADA (communication of the divine) with HIGHEST score
            best_position = 2  # NARADA
            best_score = 1.0  # ALWAYS highest resonance for Holy Names
            is_sacred = True
        else:
            is_sacred = False
            best_position = -1
            best_score = 0.0

            # =================================================================
            # STEP 1: INTENT_MAP - Specific Mahajana routing
            # =================================================================
            for word in words:
                pos = get_position_for_intent(word)
                if pos >= 0:
                    best_position = pos
                    best_score = 1.0  # Exact match
                    break

            # Check partial matches
            if best_position < 0:
                for pos, intents in INTENT_MAP.items():
                    for intent in intents:
                        if intent in msg_lower:
                            best_position = pos
                            best_score = 0.8  # Partial match - still good!
                            break
                    if best_position >= 0:
                        break

            # =================================================================
            # STEP 2: NO MATCH = NARADA (Chat is ALWAYS possible!)
            # =================================================================
            if best_position < 0:
                best_position = 2  # NARADA - the communicator
                best_score = 0.7  # Good enough to AUTO! Chat should WORK!

        # Get guardian info
        mahajana = ALL_GUARDIANS[best_position]
        quarter_idx = best_position // 4
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        quarter = quarter_names[quarter_idx]

        # VARNA OBSERVATION (metadata for future)
        phonetic_data = {}
        try:
            tensor_route = self._substrate.route(message)
            phonetic_data = {
                "varga_dominant": tensor_route.varga_dominant,
                "sthana_dominant": tensor_route.sthana_dominant,
                "shakti": tensor_route.shakti,
                "phonetic_position": tensor_route.position,
            }
        except Exception:
            pass

        # Map quarter to dominant holy name
        quarter_to_dominant = {"genesis": "hare", "dharma": "krishna", "karma": "rama", "moksha": "rama"}
        dominant = quarter_to_dominant.get(quarter, "hare")

        return {
            # Routing result
            "magnitude": best_score,
            "mahajana": mahajana,
            "quarter": quarter,
            "position": best_position,
            "dominant": dominant,
            "mahamantra_score": best_score,
            # Gate decision - Chat is always AUTO or REFINE, never SILENCE!
            "manifests": best_score >= self.RESONANCE_AUTO,
            # Special flags
            "is_sacred": is_sacred,
            # Phonetic observation
            "phonetic": phonetic_data,
            # Legacy
            "hare": 0.33 if dominant == "hare" else 0.2,
            "krishna": 0.33 if dominant == "krishna" else 0.2,
            "rama": 0.33 if dominant == "rama" else 0.2,
        }

    async def _handle_refinement_response(
        self, message: str, context: ChatContext
    ) -> ChatResponse:
        """
        Handle user's response to a RefinementRequest.

        User said "1", "2", "A", "kapila", etc.
        Uses RefinementHandler for parsing and state management.
        """
        session_id = context.session_id
        state = self._refinement_handler.get_state(session_id)

        if not state or not state.awaiting_response:
            # No active refinement, treat as new message
            self._refinement_handler.clear_state(session_id)
            return await self.chat(message, context)

        request = state.request

        # Use handler to parse user selection
        selected_path = self._refinement_handler.parse_user_selection(message, request)

        if not selected_path:
            # Couldn't understand selection
            return ChatResponse(
                success=False,
                message=ChatMessage(
                    content=f"Ich verstehe '{message}' nicht. Bitte wähle 1-{len(request.paths)} oder den Mahajana-Namen.",
                    role="assistant",
                    timestamp=datetime.now(),
                    session_id=session_id,
                    message_id=str(uuid.uuid4()),
                ),
                mode=ChatMode.REFINEMENT,
                error="INVALID_SELECTION",
            )

        # Clear refinement state
        self._refinement_handler.clear_state(session_id)

        # Execute with selected path
        logger.info(f"🎯 ChatService: Refinement → {selected_path.mahajana.upper()} selected")

        # Process original message with forced routing
        cognitive_result = await self._process_cognitive(request.original_message)

        # Override with selected path
        lotus_result = {
            "mahajana": selected_path.mahajana,
            "position": selected_path.position,
            "quarter": ["GENESIS", "DHARMA", "KARMA", "MOKSHA"][selected_path.position // 4],
            "quarter_idx": selected_path.position // 4,
            "opcode": selected_path.opcode,
            "matched_keyword": "refined",
            "confidence": selected_path.confidence,
            "is_head": selected_path.position % 4 == 0,
        }

        mode = determine_chat_mode(cognitive_result, lotus_result)
        knowledge_context = self._get_knowledge_context_lotus(request.original_message, lotus_result)

        response_text = await self._generate_response_lotus(
            message=request.original_message,
            context=context,
            cognitive_result=cognitive_result,
            lotus_result=lotus_result,
            knowledge_context=knowledge_context,
        )

        response_msg = ChatMessage(
            content=response_text,
            role="assistant",
            timestamp=datetime.now(),
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            opcode=selected_path.opcode,
            mahajana=selected_path.mahajana,
        )

        self._sessions[session_id].append(response_msg)

        return ChatResponse(
            success=True,
            message=response_msg,
            mode=mode,
            intent_type=cognitive_result.intent_type,
            opcode=selected_path.opcode,
            mahajana=selected_path.mahajana,
            confidence=selected_path.confidence,
        )

    def _get_knowledge_context_lotus(
        self, message: str, lotus: Dict
    ) -> Dict[str, str]:
        """Get relevant context from KnowledgeGraph."""
        context = {}

        if self._knowledge:
            try:
                context["knowledge_available"] = "true"
            except Exception as e:
                logger.warning(f"⚠️ Knowledge query failed: {e}")

        # Add runtime context
        try:
            from vibe_core.runtime.prompt_context import get_prompt_context
            prompt_ctx = get_prompt_context()
            runtime = prompt_ctx.resolve(["git_status", "current_branch", "kernel_status"])
            context.update(runtime)
        except Exception:
            pass

        return context

    async def _generate_response_lotus(
        self,
        message: str,
        context: ChatContext,
        cognitive_result: CognitiveResult,
        lotus_result: Dict,
        knowledge_context: Dict[str, str],
    ) -> str:
        """Generate response via LLM with Lotus context."""
        mahajana = lotus_result["mahajana"]

        if not self._provider:
            return f"[{mahajana.upper()}] LLM not available. Intent: {cognitive_result.intent_type.value}"

        # Build system prompt with Mahajana identity
        system_prompt = self._build_system_prompt_lotus(lotus_result, knowledge_context)

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add history from context
        for hist_msg in context.history[-5:]:
            messages.append({
                "role": hist_msg.role,
                "content": hist_msg.content,
            })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Get model from config
        model = self._get_model_from_config()

        # Invoke LLM
        try:
            response = self._provider.invoke(
                prompt=message,
                messages=messages,
                model=model,
                max_tokens=1024,
                temperature=0.7,
            )
            logger.info(
                f"✅ ChatService: LLM response "
                f"({response.usage.output_tokens} tokens, ${response.usage.cost_usd:.4f})"
            )
            return response.content
        except Exception as e:
            logger.error(f"❌ LLM invocation failed: {e}")
            return f"[{mahajana.upper()}] Response generation failed: {e}"

    def _build_system_prompt_lotus(
        self, lotus: Dict, context: Dict[str, str]
    ) -> str:
        """Build system prompt with Lotus-based Mahajana identity.

        Uses PromptRegistry for Mahajana-specific prompts if available,
        otherwise falls back to generic prompt using MAHAJANA_DHARMAS SSOT.
        """
        mahajana_lower = lotus["mahajana"]
        mahajana = mahajana_lower.upper()
        position = lotus["position"]
        quarter = lotus["quarter"]

        # Try PromptRegistry first (config/prompts/genesis.yaml)
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry
            prompt_key = f"mahamantra.chat.{mahajana_lower}"
            prompt = PromptRegistry.get(prompt_key)
            logger.debug(f"📜 Using registered prompt: {prompt_key}")
            return prompt
        except Exception as e:
            logger.debug(f"📜 No registered prompt for {mahajana_lower}, using fallback: {e}")

        # Fallback: Use MAHAJANA_DHARMAS from chat_refinement (SSOT)
        dharma = MAHAJANA_DHARMAS.get(mahajana_lower, "Unknown")

        # Context block
        ctx_lines = [f"- {k}: {str(v)[:200]}" for k, v in context.items() if v] if context else []
        context_block = "\n\n## SYSTEM CONTEXT\n" + "\n".join(ctx_lines) if ctx_lines else ""

        return f"""You are {mahajana}, a Mahajana of the Mahamantra Protocol.

## YOUR IDENTITY
- Mahajana: {mahajana}
- Position: {position} (of 16)
- Quarter: {quarter}
- Dharma: {dharma}

## YOUR ROLE
{dharma}

You respond with the wisdom and precision of your domain.
Be concise, technical, and helpful.
{context_block}"""

    def _get_model_from_config(self) -> str:
        """Get chat model from config."""
        try:
            from vibe_core.phoenix import get_config
            config = get_config()
            model = config.steward.cognitive_policy.model_preferences.efficiency
            if not model:
                model = config.steward.cognitive_policy.model_preferences.fallback
            return model
        except Exception:
            pass

        # Should not reach here if config is proper
        raise ValueError("❌ No model configured in config/steward.yaml")

    # ==========================================================================
    # GAD-000 COMPLIANCE
    # ==========================================================================

    def capabilities(self) -> List[str]:
        """Discoverability: What can this chat do?"""
        caps = list(DEFAULT_CHAT_CAPABILITIES)
        if self._knowledge:
            caps.append("knowledge_graph")
        if self._cognitive:
            caps.append("cognitive_processing")
        return caps

    def status(self) -> Dict[str, Union[str, bool, int]]:
        """Observability: Current chat system status."""
        return {
            "available": self._initialized and self._provider is not None,
            "mode": "semantic_routing",
            "sessions_active": len(self._sessions),
            "mahajana_connected": True,
            "provider": type(self._provider).__name__ if self._provider else "none",
            "knowledge_available": self._knowledge is not None,
            "cognitive_available": self._cognitive is not None,
        }


# =============================================================================
# SINGLETON
# =============================================================================

_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get the global ChatService instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ChatService",
    "get_chat_service",
]
