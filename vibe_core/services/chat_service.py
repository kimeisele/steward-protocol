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

    # Resonance thresholds (configurable)
    RESONANCE_AUTO = 0.7  # Auto-execute (lowered from 0.8)
    RESONANCE_REFINE = 0.4  # Ask for refinement
    # Below 0.4 = Silence

    def __init__(self):
        self._lotus: LotusHologram = LotusHologram()  # O(1) routing
        self._resonance = None  # ResonanceEngine
        self._provider = None
        self._knowledge = None
        self._cognitive = None
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._refinement_states: Dict[str, "RefinementState"] = {}  # Per-session
        self._initialized = False

        self._init_dependencies()

    def _init_dependencies(self) -> None:
        """Initialize all dependencies from protocols."""
        try:
            # ResonanceEngine (phonetic resonance - the real routing)
            from vibe_core.protocols.substrate.resonance import get_resonance_engine
            self._resonance = get_resonance_engine()
            logger.info("✅ ChatService: ResonanceEngine initialized")

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
            if session_id in self._refinement_states:
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
                return self._create_silence_response(message, context, magnitude)

            # REFINEMENT: 0.4 - 0.8 - Intent Negotiation required
            if magnitude < self.RESONANCE_AUTO:
                logger.info(f"❓ ChatService: REFINEMENT (magnitude {magnitude:.3f} in gray zone)")
                return await self._create_refinement_response(message, context, resonance_result)

            # AUTO-EXECUTE: > 0.8 - High resonance, proceed
            logger.info(f"✅ ChatService: AUTO-EXECUTE (magnitude {magnitude:.3f} >= {self.RESONANCE_AUTO})")

            # =================================================================
            # STEP 2: COGNITIVE - Intent from INTENT_MAP
            # =================================================================
            cognitive_result = await self._process_cognitive(message)
            logger.info(f"🧠 ChatService: Intent={cognitive_result.intent_type.value}")

            # =================================================================
            # STEP 3: LOTUS ROUTING - O(1) position lookup
            # =================================================================
            lotus_result = self._lotus_route(message, cognitive_result)
            lotus_result["resonance"] = resonance_result  # Attach resonance data
            logger.info(
                f"🪷 ChatService: Lotus Route → {lotus_result['mahajana'].upper()} "
                f"(pos={lotus_result['position']}, quarter={lotus_result['quarter']})"
            )

            # Determine chat mode
            mode = self._determine_mode_lotus(cognitive_result, lotus_result)

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
        return self._simple_intent_detection(message)

    def _simple_intent_detection(self, message: str) -> CognitiveResult:
        """
        Intent detection using INTENT_MAP (SSOT).

        Uses mahamantra/substrate/intents.py - NO ML, pure dict lookup.
        """
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP, get_position_for_intent

        msg_lower = message.lower()
        words = msg_lower.split()

        # Find matching position from INTENT_MAP (SSOT)
        matched_position = -1
        matched_intent = None

        for word in words:
            pos = get_position_for_intent(word)
            if pos >= 0:
                matched_position = pos
                matched_intent = word
                break

        # Map position to intent type
        if matched_position >= 0:
            # Determine intent type from quarter
            quarter = matched_position // 4
            if quarter == 0:  # GENESIS - system ops
                intent = IntentType.EXECUTE
                syscall = "SYS_WAKE"
            elif quarter == 1:  # DHARMA - knowledge ops
                intent = IntentType.QUERY
                syscall = "COMPILE_AST"
            elif quarter == 2:  # KARMA - action ops
                intent = IntentType.EXECUTE
                syscall = "EXEC_OP"
            else:  # MOKSHA - meta ops
                intent = IntentType.QUERY
                syscall = "YIELD_CPU"

            return CognitiveResult(
                intent_type=intent,
                confidence=0.85,  # High confidence from SSOT match
                syscall_type=syscall,
                target=matched_intent,
            )

        # No match in INTENT_MAP → Default to NARADA (position 2, chat)
        return CognitiveResult(
            intent_type=IntentType.CHAT,
            confidence=0.6,  # Lower confidence for default
            syscall_type=None,
        )

    def _lotus_route(self, message: str, cognitive: CognitiveResult) -> Dict[str, any]:
        """
        Route via Lotus (O(1), no ML).

        Uses INTENT_MAP for keyword → position mapping.
        Uses LotusHologram for routing.
        """
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent
        from vibe_core.mahamantra.protocols._lotus import Quarter

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
        Compute COMBINED resonance:
        1. Phonetic resonance (ResonanceEngine - HARE/KRISHNA/RAMA)
        2. Intent resonance (INTENT_MAP - action keywords)

        The combined magnitude determines routing confidence.
        """
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent

        # Get phonetic resonance (spiritual layer)
        phonetic = {"hare": 0.2, "krishna": 0.2, "rama": 0.2, "dominant": "void", "magnitude": 0.3}
        if self._resonance:
            try:
                vector = self._resonance.resonate(message)
                phonetic = dict(vector)
            except Exception:
                pass

        # Get intent resonance (practical layer)
        words = message.lower().split()
        intent_match = False
        intent_position = -1

        for word in words:
            pos = get_position_for_intent(word)
            if pos >= 0:
                intent_match = True
                intent_position = pos
                break

        # Calculate intent magnitude
        if intent_match:
            intent_magnitude = 0.9  # Strong signal from INTENT_MAP
        elif len(words) > 2:
            intent_magnitude = 0.5  # Some context available
        else:
            intent_magnitude = 0.3  # Very little to work with

        # COMBINE: Intent has higher weight for practical routing
        # Phonetic adds spiritual context
        combined_magnitude = (intent_magnitude * 0.7) + (phonetic["magnitude"] * 0.3)

        # Override dominant based on intent position
        if intent_position >= 0:
            quarter = intent_position // 4
            if quarter == 0:
                dominant = "hare"  # GENESIS
            elif quarter == 1:
                dominant = "krishna"  # DHARMA
            else:
                dominant = "rama"  # KARMA/MOKSHA
        else:
            dominant = phonetic["dominant"]

        return {
            "hare": phonetic["hare"],
            "krishna": phonetic["krishna"],
            "rama": phonetic["rama"],
            "dominant": dominant,
            "magnitude": combined_magnitude,
            "intent_match": intent_match,
            "intent_position": intent_position,
            "phonetic_magnitude": phonetic["magnitude"],
            "intent_magnitude": intent_magnitude,
        }

    def _create_silence_response(
        self, message: str, context: ChatContext, magnitude: float
    ) -> ChatResponse:
        """
        Create SILENCE response when resonance is too low.

        < 0.4 magnitude = refuse to guess, ask for clearer input.
        """
        silence_msg = ChatMessage(
            content=(
                f"Keine Resonanz im Substrat (magnitude={magnitude:.3f}). "
                "Deine Eingabe erzeugt keine klare Schwingung. "
                "Bitte formuliere konkreter: Was willst du tun?"
            ),
            role="assistant",
            timestamp=datetime.now(),
            session_id=context.session_id,
            message_id=str(uuid.uuid4()),
        )

        self._sessions[context.session_id].append(silence_msg)

        return ChatResponse(
            success=False,
            message=silence_msg,
            mode=ChatMode.SILENCE,
            confidence=magnitude,
            error="NO_RESONANCE",
        )

    async def _create_refinement_response(
        self, message: str, context: ChatContext, resonance: Dict
    ) -> ChatResponse:
        """
        Create REFINEMENT response when resonance is ambiguous (0.4-0.8).

        Discovers possible paths and asks user to choose.
        """
        # Discover paths based on resonance
        paths = self._discover_refinement_paths(message, resonance)

        if not paths:
            # Fallback: no clear paths, treat as silence
            return self._create_silence_response(message, context, resonance["magnitude"])

        # Build prompt
        path_options = "\n".join(
            f"  [{i+1}] {p.mahajana.upper()}: {p.description} (resonance={p.confidence:.2f})"
            for i, p in enumerate(paths)
        )
        prompt = (
            f"Ich sehe {len(paths)} Pfade mit ähnlicher Resonanz:\n"
            f"{path_options}\n\n"
            f"Welchen Dienst soll ich beanspruchen? (1-{len(paths)})"
        )

        # Create RefinementRequest
        request = RefinementRequest(
            original_message=message,
            paths=paths,
            prompt=prompt,
            resonance_magnitude=resonance["magnitude"],
            session_id=context.session_id,
        )

        # Store state for next response
        self._refinement_states[context.session_id] = RefinementState(request=request)

        # Create response with refinement mode
        refinement_msg = ChatMessage(
            content=prompt,
            role="assistant",
            timestamp=datetime.now(),
            session_id=context.session_id,
            message_id=str(uuid.uuid4()),
        )

        self._sessions[context.session_id].append(refinement_msg)

        return ChatResponse(
            success=True,
            message=refinement_msg,
            mode=ChatMode.REFINEMENT,
            confidence=resonance["magnitude"],
        )

    def _discover_refinement_paths(
        self, message: str, resonance: Dict
    ) -> List[RefinementPath]:
        """
        Discover possible paths for refinement.

        Uses Mahajana capabilities and resonance to find candidates.
        NOT hardcoded - uses atomic discovery.
        """
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        paths = []
        msg_lower = message.lower()

        # Score each position based on keyword overlap + resonance
        for position, keywords in INTENT_MAP.items():
            score = 0.0

            # Check keyword matches
            for keyword in keywords:
                if keyword in msg_lower:
                    score += 0.3

            # Add resonance influence
            quarter = position // 4
            if quarter == 0 and resonance["dominant"] == "hare":
                score += 0.2
            elif quarter == 1 and resonance["dominant"] == "krishna":
                score += 0.2
            elif quarter >= 2 and resonance["dominant"] == "rama":
                score += 0.2

            # Only include if score is meaningful
            if score >= 0.2:
                mahajana = get_position_mahajana(position)
                dharma_desc = self._get_dharma_description(mahajana)
                opcodes = ["SYS_WAKE", "LOAD_ROOT", "ALLOC_MEM", "BIND_CTX",
                          "ASSERT_TRUTH", "RESOLVE_REQ", "GARBAGE_COLLECT", "PULSE_SYNC",
                          "FETCH_RES", "EXEC_SERVICE", "CHECK_DHARMA", "COMMIT_LOG",
                          "CACHE_STATE", "OPTIMIZE", "YIELD_CPU", "RESET_IP"]

                paths.append(RefinementPath(
                    mahajana=mahajana,
                    position=position,
                    description=dharma_desc,
                    confidence=min(score + resonance["magnitude"] * 0.5, 1.0),
                    opcode=opcodes[position],
                ))

        # Sort by confidence, return top 3
        paths.sort(key=lambda p: p.confidence, reverse=True)
        return paths[:3]

    def _get_dharma_description(self, mahajana: str) -> str:
        """Get dharma description for a Mahajana."""
        dharmas = {
            "vyasa": "System Genesis, Boot, Wake",
            "brahma": "Creation, Spawning, Genesis",
            "narada": "Communication, Broadcast, News",
            "shambhu": "Transformation, Dissolution, Cleanup",
            "prithu": "Documentation, Structure, Knowledge",
            "kumaras": "Purification, Cleansing, Formatting",
            "kapila": "Analysis, Logic, Inference",
            "manu": "Governance, Rules, Policy",
            "parashurama": "Execution, Enforcement, Action",
            "prahlada": "Protection, Devotion, Faith",
            "janaka": "Scheduling, Tasks, Duty",
            "bhishma": "Persistence, Ledger, Storage",
            "nrisimha": "Security, Guarding, Termination",
            "bali": "Resources, Allocation, Surrender",
            "shuka": "Observation, Logging, Reports",
            "yamaraja": "Judgment, Audit, Verdict",
        }
        return dharmas.get(mahajana, "Unknown")

    async def _handle_refinement_response(
        self, message: str, context: ChatContext
    ) -> ChatResponse:
        """
        Handle user's response to a RefinementRequest.

        User said "1", "2", "A", "kapila", etc.
        """
        session_id = context.session_id
        state = self._refinement_states.get(session_id)

        if not state or not state.awaiting_response:
            # No active refinement, treat as new message
            del self._refinement_states[session_id]
            return await self.chat(message, context)

        request = state.request
        selected_path = None

        # Try to match user input to a path
        msg_lower = message.strip().lower()

        # Try numeric selection (1, 2, 3)
        if msg_lower.isdigit():
            idx = int(msg_lower) - 1
            if 0 <= idx < len(request.paths):
                selected_path = request.paths[idx]

        # Try mahajana name
        if not selected_path:
            for path in request.paths:
                if path.mahajana.lower() in msg_lower:
                    selected_path = path
                    break

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
        del self._refinement_states[session_id]

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

        mode = self._determine_mode_lotus(cognitive_result, lotus_result)
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

    def _determine_mode_lotus(
        self, cognitive: CognitiveResult, lotus: Dict
    ) -> ChatMode:
        """Determine chat mode based on Lotus routing."""
        if cognitive.intent_type == IntentType.CHAT:
            return ChatMode.DIRECT
        elif cognitive.intent_type == IntentType.QUERY:
            return ChatMode.QUERY
        elif lotus.get("is_head"):
            return ChatMode.SYSCALL
        else:
            return ChatMode.ROUTED

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
        otherwise falls back to generic prompt.
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

        # Fallback: Mahajana dharma descriptions
        dharmas = {
            "vyasa": "System Genesis, Boot, Wake",
            "brahma": "Creation, Spawning, Genesis",
            "narada": "Communication, Broadcast, News",
            "shambhu": "Transformation, Dissolution, Cleanup",
            "prithu": "Documentation, Structure, Knowledge",
            "kumaras": "Purification, Cleansing, Formatting",
            "kapila": "Analysis, Logic, Inference",
            "manu": "Governance, Rules, Policy",
            "parashurama": "Execution, Enforcement, Action",
            "prahlada": "Protection, Devotion, Faith",
            "janaka": "Scheduling, Tasks, Duty",
            "bhishma": "Persistence, Ledger, Storage",
            "nrisimha": "Security, Guarding, Termination",
            "bali": "Resources, Allocation, Surrender",
            "shuka": "Observation, Logging, Reports",
            "yamaraja": "Judgment, Audit, Verdict",
        }
        dharma = dharmas.get(mahajana_lower, "Unknown")

        # Context block
        context_block = ""
        if context:
            context_block = "\n\n## SYSTEM CONTEXT\n"
            for k, v in context.items():
                if v:
                    context_block += f"- {k}: {str(v)[:200]}\n"

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
