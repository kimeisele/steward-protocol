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
__genesis__ = "0xa2d91d8c"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Union

if TYPE_CHECKING:
    from vibe_core.mahamantra.reactor.shadow import ShadowReactor
    from vibe_core.mahamantra.substrate.samana_bridge import SamanaBridge, SamanaFold
import uuid

# NAGA INTEGRATION - The Invisible Guardians enhance chat intelligence
# NAGAs INFORM, they don't CONTROL (GAD-000 principle)
from typing import TYPE_CHECKING

from vibe_core.mahamantra.protocols._lotus import (
    MAHAJANA_POSITIONS,
    LotusBase,
    LotusHologram,
    LotusMode,
    LotusRoute,
    LotusState,
    get_mahajana_position,
    get_position_mahajana,
)
from vibe_core.mahamantra.substrate.harmonics import (
    THRESHOLD_AUTO as HARMONIC_AUTO,
)
from vibe_core.mahamantra.substrate.harmonics import (
    THRESHOLD_REFINE as HARMONIC_REFINE,
)

# RESONANCE HARMONICS - Derived from Seed, not hardcoded!
# NADI/MALA = 72/108 = 2/3, LILA/MALA = 48/108 = 4/9
from vibe_core.mahamantra.substrate.harmonics import (
    ResonanceHarmonics,
)

# NADI - Energy channels (User ↔ System via PRANA)
from vibe_core.mahamantra.substrate.nadi import (
    NadiMessage,
    NadiOp,
    NadiProtocol,
    NadiType,
    get_nadi,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode

# KSHETRA - The 24 Tattvas (BG 13.6-7)
# Chat invokes: SHROTRA (hear), VAK (speak), MANAS (think), BUDDHI (understand)
from vibe_core.mahamantra.substrate.tattva import (
    JNANENDRIYAS,
    KARMENDRIYAS,
    KshetraElement,
)
from vibe_core.protocols.chat import (
    CHAT_OPCODE,
    CHAT_PHASE,
    CHAT_POSITION,
    CHAT_WORD,
    DEFAULT_CHAT_CAPABILITIES,
    ChatContext,
    ChatMessage,
    ChatMode,
    ChatProtocol,
    ChatResponse,
    RefinementPath,
    RefinementRequest,
    RefinementState,
)
from vibe_core.protocols.cognition import (
    CognitiveResult,
    IntentType,
)

# QUANTUM REACTOR - Real manifestation (energy > inertia)
from vibe_core.reactor.quantum import (
    QuantumReactor,
    ResonanceField,
    get_reactor,
)

# REFINEMENT - Intent Negotiation (extracted for modularity)
from vibe_core.services.chat_refinement import (
    MAHAJANA_DHARMAS,
    POSITION_OPCODES,
    RefinementHandler,
    determine_chat_mode,
    discover_refinement_paths,
    get_dharma_description,
    simple_intent_detection,
)

# SUBSTRATE BRIDGE - Real vibration-based routing (not keyword matching)
from vibe_core.services.chat_substrate_bridge import (
    ChatSubstrateBridge,
    SubstrateRoute,
    get_substrate_bridge,
)

if TYPE_CHECKING:
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.services.narada import NaradaService
    from vibe_core.protocols.naga import NagaContext

logger = logging.getLogger("CHAT_SERVICE")


class ChatService(ChatProtocol, LotusBase):
    """
    Protocol-compliant Chat Service - LOTUS WRAPPED.

    Implements ChatProtocol AND LotusProtocol:
    - ResonanceEngine for phonetic resonance routing (no ML)
    - LotusHologram for O(1) position lookup
    - KnowledgeGraph for context enrichment
    - LLM Provider for response generation
    - Refinement Gate for intent negotiation
    - Full GAD-000 compliance
    - LOTUS LIFECYCLE: SEED → STEM → BLOOM → GARUDA
    - KSHETRA INTEGRATION: All 24 Tattvas involved in chat

    RESONANCE THRESHOLDS (Starship Command I/O):
    - > 0.8: Auto-execute (high resonance)
    - 0.4 - 0.8: Intent Negotiation (refinement)
    - < 0.4: Silence (no resonance - refuse to guess)

    LOTUS POSITION: 9 (PRAHLADA - protected devotee, resilient communication)
    KSHETRA ELEMENTS ACTIVE IN CHAT:
    - SHROTRA (10): Hearing - receive user input
    - VAK (14): Speaking - send response
    - MANAS (19): Mind - process message
    - BUDDHI (7): Intelligence - understand intent
    - AHANKARA (6): Ego - identity of responder (Mahajana)
    """

    # LOTUS POSITION: PRAHLADA (9) - Protected devotee, resilient communication
    LOTUS_POSITION = CHAT_POSITION  # 9 = PRAHLADA
    LOTUS_NAME = "chat_service"

    # Resonance thresholds - DERIVED FROM SEED (Mantra Seed Math, not Asura Müll!)
    # NADI/MALA = 72/108 = 2/3 ≈ 0.667 (was ~0.7 hardcoded)
    # LILA/MALA = 48/108 = 4/9 ≈ 0.444 (was ~0.4 hardcoded)
    @property
    def RESONANCE_AUTO(self) -> float:
        """Auto-execute threshold: NADI/MALA = 2/3 (Perfect Fifth)."""
        return HARMONIC_AUTO  # 0.666...

    @property
    def RESONANCE_REFINE(self) -> float:
        """Refinement threshold: LILA/MALA = 4/9 (Lila zone)."""
        return HARMONIC_REFINE  # 0.444...

    def __init__(self):
        # LOTUS BASE INIT - Position 7 (MANU)
        LotusBase.__init__(self)

        self._lotus: LotusHologram = LotusHologram()  # O(1) routing
        self._substrate: ChatSubstrateBridge = get_substrate_bridge()  # REAL vibration routing
        self._reactor: QuantumReactor = get_reactor()  # Manifestation engine
        self._provider = None
        self._knowledge = None
        self._cognitive = None
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._refinement_states: Dict[str, "RefinementState"] = {}  # Per-session
        self._initialized = False

        # NAGA Integration (The Invisible Guardians)
        # NAGAs ENHANCE existing systems - they INFORM, not CONTROL
        self._naga_cortex: Optional["NagaCortex"] = None  # Intelligence hub
        self._narada: Optional["NaradaService"] = None  # Observation service

        # Shadow Reactor (Living City - Task Execution beyond chat)
        # When routing to PARASHURAMA (pos 8), spawn tasks that outlive the response
        self._shadow_reactor: Optional["ShadowReactor"] = None

        # NADI - Energy channel for receiving chat requests via message passing
        # Instead of direct function calls, ChatIndriya sends via PRANA Nadi
        self._nadi: Optional[NadiProtocol] = None
        self._nadi_subscription_id: Optional[str] = None

        # Mahamantra Config (SSOT for holy names, thresholds, etc.)
        # Simple injection point, max effect - NO HARDCODING!
        self._mahamantra_config = None

        # Refinement Handler (extracted for modularity)
        self._refinement_handler = RefinementHandler(
            sessions=self._sessions,
            refinement_states=self._refinement_states,
        )

        # KSHETRA TRACKING - Which Tattvas are active during chat
        # Chat involves multiple senses working together (like human interaction!)
        self._active_kshetra: List[KshetraElement] = []

        self._init_dependencies()

    def _init_dependencies(self) -> None:
        """Initialize all dependencies from protocols."""
        try:
            # Mahamantra Config (SSOT - holy names, thresholds, chat defaults)
            # Simple injection point, max effect - NO HARDCODING!
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                self._mahamantra_config = config.mahamantra
                logger.info(
                    f"✅ ChatService: MahamantraConfig loaded "
                    f"({len(self._mahamantra_config.holy_names.seed)} holy names)"
                )
            except Exception as e:
                logger.warning(f"⚠️ ChatService: MahamantraConfig not available: {e}")

            # Substrate Bridge initialized in __init__ (get_substrate_bridge)
            logger.info("✅ ChatService: SubstrateBridge initialized (VarnaTensor routing)")

            # Quantum Reactor initialized in __init__ (get_reactor)
            logger.info("✅ ChatService: QuantumReactor initialized (manifestation engine)")

            # LLM Provider (via ServiceRegistry - NAGA OBSERVED!)
            from vibe_core.runtime.providers.factory import _detect_provider, get_llm_provider

            provider_name = _detect_provider()
            if provider_name != "noop":
                self._provider = get_llm_provider()  # ServiceRegistry-wrapped!
                logger.info(f"✅ ChatService: LLM Provider initialized ({provider_name}) [NAGA-observed]")

            # Knowledge Graph (via ServiceRegistry - NAGA OBSERVED!)
            try:
                from vibe_core.knowledge.graph import get_knowledge_graph

                self._knowledge = get_knowledge_graph()  # ServiceRegistry-wrapped!
                logger.info("✅ ChatService: KnowledgeGraph initialized [NAGA-observed]")
            except Exception as e:
                logger.warning(f"⚠️ ChatService: KnowledgeGraph not available: {e}")

            # Cognitive Protocol (via ServiceRegistry - NAGA OBSERVED!)
            try:
                from vibe_core.services.kapila_service import get_kapila_service

                self._cognitive = get_kapila_service()  # ServiceRegistry-wrapped!
                logger.info("✅ ChatService: Cognitive (Kapila) initialized [NAGA-observed]")
            except Exception as e:
                logger.warning(f"⚠️ ChatService: Cognitive not available: {e}")

            # Shadow Reactor (Living City - Task Execution via Yajna Cycle)
            # When routing to PARASHURAMA (pos 8), we can spawn tasks that
            # live beyond the chat response. This is the path to Living City.
            try:
                from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor

                self._shadow_reactor = get_shadow_reactor()
                logger.info("✅ ChatService: ShadowReactor initialized (Yajna Cycle enabled)")
            except Exception as e:
                self._shadow_reactor = None
                logger.warning(f"⚠️ ChatService: ShadowReactor not available: {e}")

            # NAGA Integration (The Invisible Guardians)
            # NAGAs ENHANCE, they don't REPLACE - GAD-000 principle
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import NagaFederationProtocol

                naga = ServiceRegistry.get(NagaFederationProtocol)
                if naga:
                    self._naga_cortex = naga.cortex
                    self._narada = naga._narada
                    logger.info("✅ ChatService: NAGA Federation wired (Cortex + Narada)")
                else:
                    logger.debug("⚠️ ChatService: NAGA Federation not available (normal for CLI)")
            except Exception as e:
                logger.debug(f"⚠️ ChatService: NAGA not available: {e}")

            self._initialized = True

        except Exception as e:
            logger.error(f"❌ ChatService: Initialization failed: {e}")
            self._initialized = False

    # ==========================================================================
    # NADI METHODS (Message Passing Interface)
    # ==========================================================================

    def _boot_nadi(self) -> None:
        """
        Boot Nadi endpoint and subscribe to chat requests.

        This enables ChatIndriya to send messages via PRANA channel
        instead of direct function calls. Message passing > method calls.
        """
        try:
            self._nadi = get_nadi("chat_service", nadi_type=NadiType.PRANA)

            # Subscribe to REQUEST operations from ChatIndriya
            self._nadi_subscription_id = self._nadi.subscribe(NadiOp.REQUEST, self._handle_nadi_request)
            logger.info("✅ ChatService Nadi booted (PRANA channel: chat_service)")
        except Exception as e:
            logger.warning(f"⚠️ ChatService Nadi boot failed: {e}")
            self._nadi = None

    def _handle_nadi_request(self, message: NadiMessage) -> None:
        """
        Handle incoming chat requests via Nadi.

        Called by Nadi subscription when REQUEST operation received.
        Processes async and sends response back via Nadi.respond().
        """
        import asyncio

        payload = message.payload
        text = payload.get("text", "")
        context_data = payload.get("context", {})

        # Reconstruct ChatContext
        context = ChatContext(
            session_id=context_data.get("session_id", "nadi"),
            history=[],
        )

        # Process async - handle both running and new event loops
        try:
            loop = asyncio.get_running_loop()
            # Already in async context - schedule and let it complete
            future = asyncio.ensure_future(self.chat(text, context))
            future.add_done_callback(lambda f: self._send_nadi_response(message, f.result()))
        except RuntimeError:
            # No running loop - create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(self.chat(text, context))
                self._send_nadi_response(message, response)
            finally:
                loop.close()

    def _send_nadi_response(self, original: NadiMessage, response: ChatResponse) -> None:
        """
        Send response back via Nadi.

        Packages ChatResponse into Nadi-friendly dict payload.
        Uses correlation_id from original message for matching.
        """
        if self._nadi is None:
            logger.warning("Cannot send Nadi response: Nadi not booted")
            return

        try:
            self._nadi.respond(
                original,
                {
                    "success": response.success,
                    "content": response.message.content if response.message else "",
                    "mahajana": response.mahajana,
                    "mode": response.mode.value if response.mode else None,
                    "confidence": response.confidence,
                },
            )
        except Exception as e:
            logger.error(f"Failed to send Nadi response: {e}")

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
    # LOTUS LIFECYCLE (SEED → STEM → BLOOM → GARUDA)
    # ==========================================================================

    def _lotus_seed(self, message: str) -> None:
        """
        SEED MODE: Receive input - template mode.

        Activates KSHETRA elements for reception:
        - SHROTRA (10): Hearing the user input
        - MANAS (19): Mind receives the message
        """
        self._state.mode = LotusMode.SEED
        self._active_kshetra = [
            KshetraElement.SHROTRA,  # Hearing
            KshetraElement.MANAS,  # Mind
        ]
        logger.debug(f"🌱 LOTUS SEED: Receiving '{message[:30]}...' (SHROTRA + MANAS)")

    def _lotus_stem(self, resonance_result: Dict) -> None:
        """
        STEM MODE: Route to Mahajana - bridge mode.

        Activates KSHETRA elements for understanding:
        - BUDDHI (7): Intelligence/discrimination - understand intent
        - AHANKARA (6): Ego - identify which Mahajana responds
        """
        self._state.mode = LotusMode.STEM
        self._active_kshetra.extend(
            [
                KshetraElement.BUDDHI,  # Intelligence
                KshetraElement.AHANKARA,  # Identity (which Mahajana?)
            ]
        )
        mahajana = resonance_result.get("mahajana", "narada")
        logger.debug(f"🌿 LOTUS STEM: Routing to {mahajana.upper()} (BUDDHI + AHANKARA)")

    def _lotus_bloom(self, lotus_result: Dict) -> None:
        """
        BLOOM MODE: Unfold response - manifesting 1 → N.

        Activates KSHETRA elements for response generation:
        - VAK (14): Speaking - generate response
        - All 5 TANMATRAS for rich output (SHABDA, SPARSHA, RUPA, RASA, GANDHA)
        """
        self._state.mode = LotusMode.BLOOM
        self._active_kshetra.extend(
            [
                KshetraElement.VAK,  # Speaking
                KshetraElement.SHABDA,  # Sound tanmatra (response text)
            ]
        )
        logger.debug("🌸 LOTUS BLOOM: Unfolding response (VAK + SHABDA)")

    def _lotus_garuda(self, executed: bool) -> None:
        """
        GARUDA MODE: Execute action - transport mode.

        If action required (PARASHURAMA/BRAHMA routing), activates:
        - PANI (15): Hands - execution/manipulation
        - PADA (16): Feet - navigation through codebase
        """
        self._state.mode = LotusMode.GARUDA
        if executed:
            self._active_kshetra.extend(
                [
                    KshetraElement.PANI,  # Hands (execution)
                    KshetraElement.PADA,  # Feet (navigation)
                ]
            )
        # Complete the cycle - chant!
        self.chant()
        logger.debug(f"🦅 LOTUS GARUDA: Cycle complete (kshetra={len(self._active_kshetra)} tattvas)")

    def get_active_kshetra(self) -> List[KshetraElement]:
        """Get currently active Kshetra elements in this chat cycle."""
        return self._active_kshetra.copy()

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

        # =================================================================
        # LOTUS LIFECYCLE: SEED - Receive input (SHROTRA + MANAS)
        # =================================================================
        self._lotus_seed(message)

        # =================================================================
        # NAGA OBSERVATION: Report chat start (Narada sees all)
        # =================================================================
        self._report_to_narada("START", message, context)

        # =================================================================
        # NAGA INTELLIGENCE: Get Cortex context (NAGAs INFORM, not CONTROL)
        # =================================================================
        naga_context = self._get_naga_intelligence()

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
                f"🔊 ChatService: Resonance magnitude={magnitude:.3f} (dominant={resonance_result['dominant']})"
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
            # LOTUS LIFECYCLE: STEM - Route to Mahajana (BUDDHI + AHANKARA)
            # =================================================================
            self._lotus_stem(resonance_result)

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
            # STEP 4: EXECUTION - If actionable, DO IT (not just talk!)
            # Living City: Try ShadowReactor for PARASHURAMA/BRAHMA positions,
            # fall back to cli_bridge for simple commands.
            # =================================================================
            execution_result = None
            if cognitive_result.intent_type == IntentType.EXECUTE or mode == ChatMode.SYSCALL:
                # Try Shadow Reactor first for PARASHURAMA (8) / BRAHMA (1) positions
                # These benefit from the Yajna Cycle (task isolation, async execution)
                position = lotus_result.get("position", 2)
                if position in [1, 8]:
                    execution_result = await self._execute_via_shadow(message, lotus_result, context)
                    if execution_result:
                        logger.info(f"🔥 ChatService: EXECUTED via ShadowReactor → {execution_result}")

                # Fall back to cli_bridge for other positions or if Shadow unavailable
                if execution_result is None:
                    execution_result = await self._execute_via_bridge(message, lotus_result)
                    logger.info(f"⚡ ChatService: EXECUTED via cli_bridge → {execution_result}")

            # =================================================================
            # STEP 5: CONTEXT - Live substrate context + execution result + NAGA
            # =================================================================
            knowledge_context = self._get_knowledge_context_lotus(message, lotus_result)
            if execution_result:
                knowledge_context["execution_result"] = str(execution_result)

            # Add NAGA intelligence to context (NAGAs INFORM)
            if naga_context:
                if naga_context.active_threats:
                    knowledge_context["naga_threats"] = str(len(naga_context.active_threats))
                if naga_context.anomaly_count > 0:
                    knowledge_context["naga_anomalies"] = str(naga_context.anomaly_count)
                knowledge_context["naga_reason"] = naga_context.reason_code.value

            # =================================================================
            # LOTUS LIFECYCLE: BLOOM - Unfold response (VAK + SHABDA)
            # =================================================================
            self._lotus_bloom(lotus_result)

            # =================================================================
            # STEP 6: LLM - Interpreter (responds to execution, not decides)
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

            response = ChatResponse(
                success=True,
                message=response_msg,
                mode=mode,
                intent_type=cognitive_result.intent_type,
                opcode=lotus_result.get("opcode", "EXTEND_CAP"),
                mahajana=lotus_result["mahajana"],
                confidence=magnitude,  # Use resonance magnitude as confidence
            )

            # =================================================================
            # LOTUS LIFECYCLE: GARUDA - Complete cycle (PANI + PADA if executed)
            # =================================================================
            self._lotus_garuda(executed=execution_result is not None)

            # =================================================================
            # NAGA OBSERVATION: Report chat success (Narada sees all)
            # =================================================================
            self._report_to_narada("END", message, context, response)

            # Log complete Kshetra involvement
            kshetra_names = [e.name for e in self._active_kshetra]
            logger.info(
                f"🕉️ ChatService: Lotus cycle complete - {len(self._active_kshetra)} Tattvas active: {kshetra_names}"
            )

            return response

        except Exception as e:
            logger.error(f"❌ ChatService: Chat failed: {e}")
            error_msg = ChatMessage(
                content=f"Chat error: {e}",
                role="assistant",
                timestamp=datetime.now(),
                session_id=context.session_id,
            )
            error_response = ChatResponse(
                success=False,
                message=error_msg,
                mode=ChatMode.DIRECT,
                error=str(e),
            )
            # NAGA OBSERVATION: Report chat error (Narada sees all)
            self._report_to_narada("ERROR", message, context, error_response)
            return error_response

    async def chat_with_routing(self, message: str, context: ChatContext, force_routing: bool = False) -> ChatResponse:
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
        # Word boundary check to avoid false matches (e.g., "om" in "random")
        # Holy names loaded from config (SSOT: config/mahamantra.yaml)
        # =================================================================
        if self._mahamantra_config:
            holy_names = self._mahamantra_config.holy_names.get_all_names()
        else:
            # Fallback if config not loaded (shouldn't happen)
            holy_names = {"hare", "krishna", "rama", "om", "hari", "govinda", "madhava"}
        has_holy_name = any(name in words for name in holy_names)

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
            # Partial match score = MALA/FIELD = 108/144 = 3/4 = 0.75 (Perfect Fourth)
            if best_position < 0:
                partial_score = 108 / 144  # 0.75 - harmonic ratio
                for pos, intents in INTENT_MAP.items():
                    for intent in intents:
                        if intent in msg_lower:
                            best_position = pos
                            best_score = partial_score  # 3/4 - above AUTO, below full
                            break
                    if best_position >= 0:
                        break

            # =================================================================
            # STEP 2: NO MATCH = NARADA (Chat is ALWAYS possible!)
            # Default score is EXACTLY at AUTO threshold (NADI/MALA = 2/3)
            # =================================================================
            if best_position < 0:
                best_position = 2  # NARADA - the communicator
                best_score = HARMONIC_AUTO  # NADI/MALA = 2/3 ≈ 0.667 (AUTO!)

        # Get guardian info
        mahajana = ALL_GUARDIANS[best_position]
        quarter_idx = best_position // 4
        quarter_names = ["genesis", "dharma", "karma", "moksha"]
        quarter = quarter_names[quarter_idx]

        # VARNA OBSERVATION + REAL SUBSTRATE ROUTING
        # The SubstrateRoute is the BRAIN, not just metadata!
        phonetic_data = {}
        substrate_route = None  # Will be set if substrate routing succeeds
        try:
            tensor_route = self._substrate.route(message)
            substrate_route = tensor_route  # REAL ROUTING - not just metadata!
            phonetic_data = {
                "varga_dominant": tensor_route.varga_dominant,
                "sthana_dominant": tensor_route.sthana_dominant,
                "shakti": tensor_route.shakti,
                "phonetic_position": tensor_route.position,
            }
            # If substrate routing succeeds AND it's not a sacred message,
            # USE IT for routing (not INTENT_MAP!)
            # HOLY NAMES have priority - they're always highest resonance!
            if tensor_route.manifests and not is_sacred:
                best_position = tensor_route.position
                best_score = tensor_route.energy
                mahajana = tensor_route.mahajana
                quarter = tensor_route.quarter.lower()
        except Exception as e:
            logger.debug(f"Substrate routing failed (fallback to INTENT_MAP): {e}")

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
            # CRITICAL: SubstrateRoute for REAL Mahamantra routing!
            # This enables _lotus_route() to use VarnaTensor-based routing
            # instead of falling back to INTENT_MAP keyword matching
            "substrate_route": substrate_route,
            # Legacy
            "hare": 0.33 if dominant == "hare" else 0.2,
            "krishna": 0.33 if dominant == "krishna" else 0.2,
            "rama": 0.33 if dominant == "rama" else 0.2,
        }

    # ==========================================================================
    # NAGA INTEGRATION (The Invisible Guardians)
    # NAGAs INFORM, they don't CONTROL - GAD-000 principle
    # ==========================================================================

    def _get_naga_intelligence(self) -> Optional["NagaContext"]:
        """
        Get aggregated NAGA intelligence for chat decisions.

        PULL-BASED: Chat calls this when it needs context.
        NAGAs INFORM, they don't CONTROL.

        Returns:
            NagaContext with typed intelligence, or None if NAGA unavailable
        """
        if not self._naga_cortex:
            return None

        try:
            context = self._naga_cortex.get_context_for_manas()
            logger.debug(
                f"🐍 NAGA Context: threats={len(context.active_threats)}, "
                f"anomalies={context.anomaly_count}, reason={context.reason_code.value}"
            )
            return context
        except Exception as e:
            logger.debug(f"⚠️ NAGA intelligence unavailable: {e}")
            return None

    def _report_to_narada(
        self,
        event_type: str,
        message: str,
        context: ChatContext,
        result: Optional[ChatResponse] = None,
    ) -> None:
        """
        Report chat event to Narada for observation tracking.

        NARADA SEES ALL - The cosmic journalist.
        Every chat interaction is observed for:
        - Audit trail (GAD-000 compliance)
        - Pattern analysis (Cortex learning)
        - Mahajana routing metrics

        Args:
            event_type: Type of event (CHAT_START, CHAT_END, CHAT_ERROR, etc.)
            message: The user message
            context: Chat context
            result: Optional chat response (for CHAT_END events)
        """
        if not self._narada:
            return

        try:
            # Build observation data
            data = f"session={context.session_id},message_len={len(message)}"
            if result:
                data += f",mode={result.mode.value},success={result.success}"
                if result.mahajana:
                    data += f",mahajana={result.mahajana}"
                if result.confidence:
                    data += f",confidence={result.confidence:.3f}"

            # Observe via Narada
            observation = self._narada.observe(
                event_type=f"CHAT_{event_type}",
                source="chat_service",
                data=data,
            )
            logger.debug(f"🐍 Narada observed: CHAT_{event_type}")
        except Exception as e:
            # NARADA SAFETY: Observation failure must NEVER kill the application
            logger.debug(f"⚠️ Narada observation failed: {e}")

    async def _execute_via_bridge(self, message: str, lotus_result: Dict) -> Optional[Dict]:
        """
        Execute command via CLI Bridge - Chat actually DOES things!

        ROYAL DELEGATION: steward chat "boot" → cli_bridge.route("boot") → EXECUTION!
        """
        try:
            from vibe_core.mahamantra.cli.bridge import cli_bridge

            # Extract command from message (first word or matched keyword)
            words = message.lower().split()
            command = lotus_result.get("matched_keyword") or words[0] if words else "help"

            # Extract args (remaining words)
            args = words[1:] if len(words) > 1 else []

            # EXECUTE!
            logger.info(f"⚡ Executing: cli_bridge.route('{command}', {args})")
            result = cli_bridge.route(command, args)

            return {
                "success": result.success,
                "exit_code": result.exit_code,
                "position": result.position,
                "handler": result.handler,
                "fallback": result.fallback,
                "error": result.error,
            }
        except Exception as e:
            logger.warning(f"⚠️ Bridge execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _await_fold(
        self,
        bridge: "SamanaBridge",
        dispatch_id: str,
        timeout_ms: int = 5000,
    ) -> Optional["SamanaFold"]:
        """
        MOKSHA: Await the fold (result) from TaskKernel.

        VEDA-4 PATTERN:
        - GENESIS: Message received
        - DHARMA: Routed to Mahajana
        - KARMA: Dispatched to TaskKernel
        - MOKSHA: Fold returns here ← WE ARE HERE

        Args:
            bridge: SamanaBridge to poll
            dispatch_id: The dispatch to wait for
            timeout_ms: Max wait time (default 5s)

        Returns:
            SamanaFold if completed, None if timeout
        """
        import asyncio

        poll_interval_ms = 100  # Check every 100ms
        elapsed = 0

        while elapsed < timeout_ms:
            # Check for completed fold
            fold = bridge.get_fold(dispatch_id)
            if fold is not None:
                logger.info(f"🕉️ MOKSHA: Fold received for {dispatch_id} (status={fold.status})")
                return fold

            # Also receive any pending folds from Nadi
            bridge.receive_folds()

            # Wait and retry
            await asyncio.sleep(poll_interval_ms / 1000)
            elapsed += poll_interval_ms

        logger.warning(f"⏰ MOKSHA: Timeout waiting for fold {dispatch_id}")
        return None

    async def _execute_via_shadow(
        self,
        message: str,
        lotus_result: Dict,
        context: ChatContext,
    ) -> Optional[Dict]:
        """
        Execute task via ShadowReactor - The Yajna Cycle.

        VEDA-4 PATTERN (Complete Cycle):
        - GENESIS: Task created from message
        - DHARMA: Routed to position (PARASHURAMA/BRAHMA)
        - KARMA: Dispatched to TaskKernel
        - MOKSHA: Fold awaited and returned

        WHEN TO USE:
        - Position 8 (PARASHURAMA) = Execute/Transform
        - Position 1 (BRAHMA) = Create/Generate
        - Complex tasks that benefit from isolation

        Returns:
            Dict with execution result, or None if not supported
        """
        if self._shadow_reactor is None:
            logger.debug("ShadowReactor not available, falling back to cli_bridge")
            return None

        try:
            position = lotus_result.get("position", 2)

            # Only use Shadow for PARASHURAMA (8) or BRAHMA (1) positions
            # These are "action" positions that benefit from task isolation
            if position not in [1, 8]:
                return None

            bridge = self._shadow_reactor.samana_bridge

            # Create task from message
            task_id = f"chat_{context.session_id[:8]}_{position}"
            task_description = f"Execute: {message[:50]}"

            # Parse action from message for TaskKernel execution
            # TaskKernel checks for 'action' or 'tool_call' in metadata
            words = message.lower().split()
            action = words[0] if words else "unknown"
            action_args = words[1:] if len(words) > 1 else []

            # Dispatch to TaskKernel via SamanaBridge
            dispatch_id = bridge.dispatch(
                task_id=task_id,
                task_description=task_description,
                position=position,
                phase="bhoga" if position < 8 else "prasadam",
                payload={
                    # Action spec for TaskKernel execution
                    "action": action,
                    "context": {
                        "args": action_args,
                        "message": message,
                        "mahajana": lotus_result.get("mahajana"),
                        "session_id": context.session_id,
                        "position": position,
                    },
                },
            )

            if dispatch_id:
                logger.info(
                    f"🔥 KARMA: Dispatched {task_id} → {dispatch_id} "
                    f"(position={position}, phase={'bhoga' if position < 8 else 'prasadam'})"
                )

                # =============================================================
                # MOKSHA: Await the fold (Complete the Yajna Cycle)
                # =============================================================
                fold = await self._await_fold(bridge, dispatch_id, timeout_ms=5000)

                if fold:
                    # Full cycle complete: GENESIS → DHARMA → KARMA → MOKSHA
                    return {
                        "success": fold.status == "completed",
                        "dispatch_id": dispatch_id,
                        "task_id": task_id,
                        "position": position,
                        "mode": "shadow_reactor",
                        "veda_cycle": "complete",
                        "fold_status": fold.status,
                        "output": fold.output,
                        "duration_ms": fold.duration_ms,
                        "reinforcement": fold.reinforcement_signal,
                    }
                else:
                    # Timeout - task still running (async continuation)
                    return {
                        "success": True,
                        "dispatch_id": dispatch_id,
                        "task_id": task_id,
                        "position": position,
                        "mode": "shadow_reactor",
                        "veda_cycle": "karma_only",  # Moksha pending
                        "note": "Task running in Yajna Cycle. Check back later.",
                    }
            else:
                logger.warning("⚠️ KARMA: Dispatch failed (no capacity?)")
                return None

        except Exception as e:
            logger.warning(f"⚠️ Shadow execution failed: {e}")
            return None

    async def _handle_refinement_response(self, message: str, context: ChatContext) -> ChatResponse:
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

    def _get_knowledge_context_lotus(self, message: str, lotus: Dict) -> Dict[str, str]:
        """
        Get relevant context - makes Chat SELF-AWARE.

        Includes:
        - Available CLI commands (from cli_bridge)
        - Runtime context (git, kernel)
        - Mahajana capabilities
        """
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

        # Add CLI capabilities - SELF-AWARENESS
        # Chat needs to know what commands it can execute
        try:
            from vibe_core.mahamantra.cli.bridge import cli_bridge

            routes = cli_bridge.list_routes()
            # Group by mahajana for relevance
            current_mahajana = lotus.get("mahajana", "narada")
            relevant_commands = [r[0] for r in routes if r[2] == current_mahajana][:10]
            all_commands = [r[0] for r in routes][:20]

            context["available_commands"] = ", ".join(all_commands)
            context["mahajana_commands"] = ", ".join(relevant_commands) if relevant_commands else "general"
            context["total_commands"] = str(len(routes))
        except Exception as e:
            logger.debug(f"CLI discovery failed: {e}")

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
            messages.append(
                {
                    "role": hist_msg.role,
                    "content": hist_msg.content,
                }
            )

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
                f"✅ ChatService: LLM response ({response.usage.output_tokens} tokens, ${response.usage.cost_usd:.4f})"
            )
            return response.content
        except Exception as e:
            logger.error(f"❌ LLM invocation failed: {e}")
            return f"[{mahajana.upper()}] Response generation failed: {e}"

    def _build_system_prompt_lotus(self, lotus: Dict, context: Dict[str, str]) -> str:
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
            # NAGA Integration status
            "naga_cortex_available": self._naga_cortex is not None,
            "naga_narada_available": self._narada is not None,
            # Mahamantra Config status
            "mahamantra_config_loaded": self._mahamantra_config is not None,
            "holy_names_count": len(self._mahamantra_config.holy_names.seed) if self._mahamantra_config else 0,
        }


# =============================================================================
# SINGLETON - VIA SERVICE REGISTRY (WIRED, NOT ISLAND!)
# =============================================================================


def get_chat_service() -> ChatService:
    """
    Get ChatService through ServiceRegistry (WIRED).

    CRITICAL FIX: ChatService was an ISLAND - created directly via standalone
    factory, bypassing kernel boot, DI, and NagaProxy wrapping.

    Now it goes through ServiceRegistry:
    1. First call: Create + Register + Return (with NagaProxy if enabled)
    2. Subsequent calls: Return registered instance

    This ensures:
    - NagaProxy can observe/guard all chat operations
    - Proper DI integration with kernel
    - No more silent cascade failures
    """
    from vibe_core.di import ServiceRegistry

    # Try to get from registry first (may already be registered by kernel/plugin)
    try:
        existing = ServiceRegistry.get(ChatProtocol)
        if existing is not None:
            return existing
    except Exception:
        pass  # Not registered yet, we'll create and register

    # Create and register - this triggers NagaProxy wrapping if enabled!
    instance = ChatService()

    # NADI BOOT: Enable message passing from ChatIndriya
    instance._boot_nadi()

    ServiceRegistry.register(ChatProtocol, instance)
    logger.info("✅ ChatService registered via ServiceRegistry (WIRED + NADI-enabled)")

    return ServiceRegistry.get(ChatProtocol)  # Return wrapped version!


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ChatService",
    "get_chat_service",
]
