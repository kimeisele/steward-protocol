"""
CHAT INDRIYA - The Hearing/Speaking Sense Organ for User Communication
======================================================================

"sakhāya indriya-gaṇā jñānaṁ karma ca yat-kṛtam"
"The senses are the male friends that assist the living entity
in acquiring knowledge and engaging in activity."
— Srimad Bhagavatam 4.29.6

ARCHITECTURE (Gemini Critique Compliant):
=========================================

    User Input (raw text)
           ↓
    ChatIndriya (Sense Organ) ← Has VRTTI state (NIDRA → PRAMANA → etc)
           ↓
    TanmatraMessage (SABDA) ← Encapsulates INTENT (QUERY? COMMAND? PRAYER?)
           ↓
    Nadi (PRANA channel) ← ChatIndriya INTERFACES with, doesn't OWN
           ↓
    ChatSubstrateBridge → Mahajana routing

KEY INSIGHT:
============
Chat is an INDRIYA (sense organ), not a NADI (channel).
- The Indriya INTERFACES with the Nadi
- The Tanmatra FLOWS through the Nadi
- The Vrtti is the ENGAGEMENT STATE of the sense

This is a COMBINED sense: SROTRA (hearing) + VAK (speaking)
- Srotra receives user input
- Vak produces assistant output

ALL CONSTANTS DERIVED FROM SEED.PY.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9a3b7c02"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, Final, List, Optional

if TYPE_CHECKING:
    from vibe_core.mahamantra.protocols.sankalpa.types import ConscienceVerdict
    from vibe_core.protocols.chat import ChatResponse
from uuid import uuid4

# Import Indriya infrastructure
from vibe_core.mahamantra.protocols._indriya import (
    VRTTI_COUNT,
    IndriyaProtocol,
    IndriyaState,
    IndriyaType,
    Jnanendriya,
    Karmendriya,
    Tanmatra,
    TanmatraIntent,
    TanmatraMessage,
    Vrtti,
)

# Import Nadi infrastructure (for interfacing, not owning)
from vibe_core.mahamantra.substrate.nadi import (
    NadiMessage,
    NadiOp,
    NadiPriority,
    NadiProtocol,
    NadiType,
)

# Import ChatService (BRAIN) - ChatIndriya wraps this (Balarama Pattern)
from vibe_core.services.chat_substrate_bridge import SubstrateRoute  # For type hints only


# Lazy import to avoid circular dependency
def _get_chat_service():
    """Lazy import of ChatService to avoid circular imports."""
    from vibe_core.services.chat_service import get_chat_service

    return get_chat_service()


# Import seed constants
# GAD compliance
from vibe_core.mahamantra.protocols._gad import GADBase
from vibe_core.mahamantra.protocols._seed import HARE_COUNT
from vibe_core.mahamantra.protocols._seed import WORDS as SEED_WORDS

# CONSCIENCE - Dharmic alignment check (Buddhi function)
from vibe_core.mahamantra.protocols.sankalpa import (
    Ashrama,
    GunaState,
    check_conscience,
)

# NADI - Energy channels (the missing wiring!)
from vibe_core.mahamantra.substrate.nadi import (
    get_nadi,
)

# SHAKTI - Energy transmission through Prabhupada
from vibe_core.mahamantra.substrate.prabhupada import get_prabhupada
from vibe_core.mahamantra.substrate.seed import (
    NADI_RESONANCE,
    NAVA,
    PRANA_DURATION_MS,
    WORDS,
)

logger = logging.getLogger("CHAT_INDRIYA")


# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Chat session timeout = PRANA_DURATION_MS × WORDS = 4000 × 16 = 64000ms
CHAT_SESSION_TIMEOUT_MS: Final[int] = PRANA_DURATION_MS * WORDS  # 64000ms

# Max pending messages = NADI_RESONANCE = 72
CHAT_MESSAGE_BUFFER: Final[int] = NADI_RESONANCE  # 72

# Vrtti transition cooldown = PRANA_DURATION_MS / NAVA = 4000 / 9 ≈ 444ms
VRTTI_COOLDOWN_MS: Final[int] = PRANA_DURATION_MS // NAVA  # ~444ms

# Verification
assert CHAT_SESSION_TIMEOUT_MS == 64000, "Session timeout = 64 seconds"
assert CHAT_MESSAGE_BUFFER == 72, "Buffer = NADI_RESONANCE"


# =============================================================================
# CHAT SESSION - Stateful conversation tracking
# =============================================================================


@dataclass
class ChatSession:
    """
    A chat session tracking conversation state.

    Maps to Vrtti cycle:
    - New session starts in NIDRA (idle)
    - User message transitions to PRAMANA (active perception)
    - Processing transitions to VIKALPA (inference)
    - Response transitions to SMRTI (memory) or back to NIDRA
    """

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    tanmatras: List[TanmatraMessage] = field(default_factory=list)
    current_vrtti: Vrtti = Vrtti.NIDRA

    @property
    def is_expired(self) -> bool:
        """Session expired if inactive > timeout."""
        elapsed = (datetime.now() - self.last_activity).total_seconds() * 1000
        return elapsed > CHAT_SESSION_TIMEOUT_MS

    def touch(self) -> None:
        """Update last activity."""
        self.last_activity = datetime.now()

    def add_tanmatra(self, msg: TanmatraMessage) -> None:
        """Add a tanmatra to session history."""
        self.tanmatras.append(msg)
        self.message_count += 1
        self.touch()


# =============================================================================
# CHAT INDRIYA - The Hearing/Speaking Sense Organ
# =============================================================================


class ChatIndriya(GADBase):
    """
    Chat Indriya - Combined SROTRA (hearing) + VAK (speaking) sense organ.

    Implements IndriyaProtocol for proper sense organ behavior:
    - Has VRTTI state machine (engagement modes)
    - INTERFACES with Nadi (doesn't own it)
    - Sends/receives TanmatraMessages (not raw strings)

    FLOW:
    1. User speaks → ChatIndriya receives (SROTRA function)
    2. Vrtti transitions: NIDRA → PRAMANA
    3. TanmatraMessage created with INTENT classification
    4. Message sent through connected Nadi
    5. Response received
    6. ChatIndriya speaks back (VAK function)
    7. Vrtti transitions: PRAMANA → SMRTI → NIDRA
    """

    def __init__(
        self,
        service_id: str = "chat_indriya",
    ):
        super().__init__()  # Initialize GADBase

        self._service_id = service_id

        # The two senses this Indriya combines
        self._srotra = Jnanendriya.SROTRA  # Hearing (user input)
        self._vak = Karmendriya.VAK  # Speaking (assistant output)

        # Internal state for each sense function
        self._srotra_state = IndriyaState(indriya=self._srotra)
        self._vak_state = IndriyaState(indriya=self._vak)

        # ChatService (BRAIN) - lazy loaded to avoid circular imports
        # ChatIndriya WRAPS ChatService (Balarama Pattern)
        self._chat_service = None  # Lazy init

        # Session tracking
        self._sessions: Dict[str, ChatSession] = {}

        # Connected Nadi (externally provided, not owned)
        self._nadi: Optional[NadiProtocol] = None

        # Callbacks
        self._on_tanmatra: Optional[Callable[[TanmatraMessage], None]] = None
        self._on_vrtti_change: Optional[Callable[[Vrtti, Vrtti], None]] = None

        # Stats
        self._tanmatras_received = 0
        self._tanmatras_sent = 0
        self._vrtti_transitions = 0

    # =========================================================================
    # INDRIYA PROTOCOL IMPLEMENTATION
    # =========================================================================

    @property
    def indriya(self) -> IndriyaType:
        """Primary sense: SROTRA (hearing user input)."""
        return self._srotra

    @property
    def state(self) -> IndriyaState:
        """Get current state (SROTRA state as primary)."""
        return self._srotra_state

    @property
    def vrtti(self) -> Vrtti:
        """Get current engagement mode."""
        return self._srotra_state.vrtti

    @property
    def chat_service(self):
        """Lazy-load ChatService (Balarama Pattern: wrap, don't own)."""
        if self._chat_service is None:
            self._chat_service = _get_chat_service()
        return self._chat_service

    def transition(self, new_vrtti: Vrtti) -> bool:
        """
        Transition to a new vrtti state.

        Valid transitions:
        - NIDRA → PRAMANA (wake up to receive)
        - PRAMANA → VIKALPA (start processing)
        - VIKALPA → SMRTI (store result)
        - SMRTI → NIDRA (go idle)
        - Any → VIPARYAYA (error)
        - VIPARYAYA → NIDRA (recover)
        """
        old_vrtti = self._srotra_state.vrtti

        # Always allow transition to error state
        if new_vrtti == Vrtti.VIPARYAYA:
            self._do_transition(new_vrtti, old_vrtti)
            return True

        # Recovery from error only goes to NIDRA
        if old_vrtti == Vrtti.VIPARYAYA:
            if new_vrtti != Vrtti.NIDRA:
                return False
            self._do_transition(new_vrtti, old_vrtti)
            return True

        # Normal state machine
        valid_transitions = {
            Vrtti.NIDRA: [Vrtti.PRAMANA],  # Wake up
            Vrtti.PRAMANA: [Vrtti.VIKALPA, Vrtti.NIDRA],  # Process or idle
            Vrtti.VIKALPA: [Vrtti.SMRTI, Vrtti.PRAMANA],  # Store or continue
            Vrtti.SMRTI: [Vrtti.NIDRA, Vrtti.PRAMANA],  # Idle or continue
        }

        if new_vrtti in valid_transitions.get(old_vrtti, []):
            self._do_transition(new_vrtti, old_vrtti)
            return True

        logger.warning(f"Invalid vrtti transition: {old_vrtti.name} → {new_vrtti.name}")
        return False

    def _do_transition(self, new_vrtti: Vrtti, old_vrtti: Vrtti) -> None:
        """Execute vrtti transition."""
        self._srotra_state.transition_to(new_vrtti)
        self._vak_state.transition_to(new_vrtti)  # Keep both in sync
        self._vrtti_transitions += 1

        if self._on_vrtti_change:
            self._on_vrtti_change(old_vrtti, new_vrtti)

        logger.debug(f"Vrtti transition: {old_vrtti.name} → {new_vrtti.name}")

    def connect_to_nadi(self, nadi: NadiProtocol) -> bool:
        """
        Connect this sense organ to a Nadi.

        The Indriya INTERFACES with the Nadi, doesn't own it.
        """
        if self._nadi is not None:
            logger.warning("Already connected to a Nadi")
            return False

        self._nadi = nadi
        self._srotra_state.connect_nadi(nadi.endpoint_id)
        self._vak_state.connect_nadi(nadi.endpoint_id)

        logger.info(f"Connected to Nadi: {nadi.endpoint_id}")
        return True

    def disconnect_from_nadi(self) -> None:
        """Disconnect from the current Nadi."""
        if self._nadi is None:
            return

        self._srotra_state.disconnect_nadi()
        self._vak_state.disconnect_nadi()
        self._nadi = None

        logger.info("Disconnected from Nadi")

    def send_tanmatra(self, message: TanmatraMessage) -> bool:
        """
        Send a Tanmatra message through the connected Nadi.

        Only works if:
        - Connected to Nadi
        - Not in NIDRA (sleep) or VIPARYAYA (error) state
        """
        if self._nadi is None:
            logger.warning("Cannot send: not connected to Nadi")
            return False

        if self.vrtti in (Vrtti.NIDRA, Vrtti.VIPARYAYA):
            logger.warning(f"Cannot send in {self.vrtti.name} state")
            return False

        # Convert TanmatraMessage to NadiMessage
        nadi_msg = NadiMessage(
            source=self._nadi.endpoint_id,
            target="*",  # Broadcast
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND,
            payload={
                "type": "tanmatra",
                "message_id": message.message_id,
                "tanmatra": message.tanmatra.value,
                "intent": message.intent.value,
                "content": message.content,
                "source_indriya": message.source_indriya.value if message.source_indriya else None,
                "metadata": message.metadata,
            },
            priority=NadiPriority.RAJAS,
        )

        success = self._nadi.send(nadi_msg)
        if success:
            self._tanmatras_sent += 1

        return success

    def receive_tanmatra(self) -> Optional[TanmatraMessage]:
        """
        Receive a Tanmatra message from the connected Nadi.

        Returns None if nothing available or not connected.
        """
        if self._nadi is None:
            return None

        nadi_msg = self._nadi.receive()
        if nadi_msg is None:
            return None

        # Convert NadiMessage to TanmatraMessage
        payload = nadi_msg.payload
        if payload.get("type") != "tanmatra":
            return None

        tanmatra = TanmatraMessage(
            message_id=payload.get("message_id", str(uuid4())),
            tanmatra=Tanmatra(payload.get("tanmatra", "sabda")),
            intent=TanmatraIntent(payload.get("intent", "query")),
            content=payload.get("content", ""),
            timestamp=nadi_msg.timestamp,
            metadata=payload.get("metadata", {}),
        )

        self._tanmatras_received += 1

        if self._on_tanmatra:
            self._on_tanmatra(tanmatra)

        return tanmatra

    # =========================================================================
    # CHAT-SPECIFIC METHODS
    # =========================================================================

    async def chat(self, text: str, session_id: str) -> TanmatraMessage:
        """
        Process user input through complete Vrtti cycle (Balarama Pattern).

        WRAPS ChatService.chat() with sense organ state management:
        1. SROTRA receives (NIDRA → PRAMANA)
        2. Create TanmatraMessage with intent
        3. DELEGATE to ChatService (PRAMANA → VIKALPA)
        4. VAK speaks response (VIKALPA → SMRTI → NIDRA)
        5. Return response TanmatraMessage

        This is the Balarama Pattern: ChatIndriya wraps ChatService
        without modifying it, adding Vrtti state management.
        """
        from vibe_core.protocols.chat import ChatContext

        # Get/create session
        session = self._get_or_create_session(session_id)

        # === SROTRA (Hearing) - Wake up ===
        if self.vrtti == Vrtti.NIDRA:
            self.transition(Vrtti.PRAMANA)

        # Classify intent from text
        intent = self._classify_intent(text)

        # === CONSCIENCE CHECK (Buddhi function via VarnaTensor) ===
        # Analyze VIBRATION to determine intent_type (no string matching!)
        intent_type, position, quarter = self._analyze_vibration(text)
        conscience = check_conscience(intent_type, ashrama=Ashrama.GRIHASTHA)

        if not conscience.is_dharmic:
            # TAMASIC - The Steward blocks with care, not coldness
            logger.warning(f"🚫 STEWARD BLOCKS: {intent_type} (quarter={quarter})")
            self.transition(Vrtti.VIPARYAYA)  # Error state

            # Steward speaks with personality, not "Error 403"
            steward_message = self._steward_block_message(intent_type, conscience, quarter)

            blocked_tanmatra = TanmatraMessage(
                message_id=f"tm_{uuid4().hex[:8]}",
                tanmatra=Tanmatra.SABDA,
                intent=TanmatraIntent.RESPONSE,
                content=steward_message,
                source_indriya=self._vak,
                timestamp=datetime.now(),
                metadata={
                    "blocked": True,
                    "guna": conscience.guna.value,
                    "quarter": quarter,
                    "position": position,
                    "reason": conscience.reason,
                },
            )
            session.add_tanmatra(blocked_tanmatra)
            self.transition(Vrtti.NIDRA)  # Recover
            return blocked_tanmatra

        # Conscience passed (Sattvic or Rajasic)
        if conscience.guna == GunaState.RAJASIC:
            logger.info(f"⚠️ STEWARD CAUTION: {intent_type} (quarter={quarter})")

        # Create input TanmatraMessage
        input_tanmatra = TanmatraMessage(
            message_id=f"tm_{uuid4().hex[:8]}",
            tanmatra=Tanmatra.SABDA,  # Text = sound
            intent=intent,
            content=text,
            source_indriya=self._srotra,
            timestamp=datetime.now(),
        )
        session.add_tanmatra(input_tanmatra)
        self._tanmatras_received += 1

        # === DELEGATE to ChatService (BRAIN) via NADI ===
        self.transition(Vrtti.VIKALPA)  # Processing

        try:
            # NADI PATTERN: Send via PRANA channel (if connected)
            if self._nadi is not None and self._nadi.is_connected("chat_service"):
                # Message passing - the CORRECT architecture
                nadi_response = self._nadi.request(
                    target="chat_service",
                    operation=NadiOp.REQUEST,
                    payload={
                        "text": text,
                        "context": {"session_id": session_id},
                    },
                    timeout_ms=CHAT_SESSION_TIMEOUT_MS,  # 64000ms
                )

                if nadi_response is None:
                    raise TimeoutError("ChatService did not respond via Nadi")

                # Extract response from Nadi payload
                response = self._nadi_payload_to_response(nadi_response.payload)
                logger.debug("✅ Chat processed via NADI (message passing)")
            else:
                # FALLBACK: Direct call if Nadi not available
                logger.debug("⚠️ Nadi not connected, using direct call (fallback)")
                chat_context = ChatContext(
                    session_id=session_id,
                    history=[],
                )
                response = await self.chat_service.chat(text, chat_context)

            # === VAK (Speaking) - Create response ===
            self.transition(Vrtti.SMRTI)  # Store result

            response_tanmatra = TanmatraMessage(
                message_id=f"tm_{uuid4().hex[:8]}",
                tanmatra=Tanmatra.SABDA,
                intent=TanmatraIntent.RESPONSE,
                content=response.message.content if response.message else "",
                source_indriya=self._vak,
                timestamp=datetime.now(),
                metadata={
                    "success": response.success,
                    "mahajana": response.mahajana,
                    "in_response_to": input_tanmatra.message_id,
                },
            )
            session.add_tanmatra(response_tanmatra)
            self._tanmatras_sent += 1

            logger.info(f"Chat: intent={intent.name}, mahajana={response.mahajana}, success={response.success}")

        except Exception as e:
            # Error handling - transition to VIPARYAYA
            self.transition(Vrtti.VIPARYAYA)
            logger.error(f"Chat error: {e}")

            response_tanmatra = TanmatraMessage(
                message_id=f"tm_{uuid4().hex[:8]}",
                tanmatra=Tanmatra.SABDA,
                intent=TanmatraIntent.RESPONSE,
                content=f"Error: {e}",
                source_indriya=self._vak,
                timestamp=datetime.now(),
                metadata={"error": str(e), "in_response_to": input_tanmatra.message_id},
            )
            session.add_tanmatra(response_tanmatra)

            # Recover from error
            self.transition(Vrtti.NIDRA)
            return response_tanmatra

        # Return to idle
        self.transition(Vrtti.NIDRA)

        return response_tanmatra

    def process_user_input(self, text: str, session_id: str) -> TanmatraMessage:
        """
        DEPRECATED: Use chat() instead (async).

        Sync version that only classifies intent and creates TanmatraMessage.
        Does NOT call ChatService (use chat() for full processing).
        """
        # Get/create session
        session = self._get_or_create_session(session_id)

        # Wake up the sense
        if self.vrtti == Vrtti.NIDRA:
            self.transition(Vrtti.PRAMANA)

        # Classify intent from text
        intent = self._classify_intent(text)

        # Create TanmatraMessage
        tanmatra = TanmatraMessage(
            message_id=f"tm_{uuid4().hex[:8]}",
            tanmatra=Tanmatra.SABDA,  # Text = sound
            intent=intent,
            content=text,
            source_indriya=self._srotra,
            timestamp=datetime.now(),
        )

        # Store in session
        session.add_tanmatra(tanmatra)

        # Transition to processing
        self.transition(Vrtti.VIKALPA)

        logger.info(f"User input: intent={intent.name}")

        return tanmatra

    def send_response(
        self,
        text: str,
        session_id: str,
        request_tanmatra: Optional[TanmatraMessage] = None,
    ) -> TanmatraMessage:
        """
        Send assistant response.

        1. Create RESPONSE tanmatra
        2. Link to request if provided
        3. Store in session
        4. Transition to SMRTI (memory)
        """
        session = self._get_or_create_session(session_id)

        # Create response TanmatraMessage
        tanmatra = TanmatraMessage(
            message_id=f"tm_{uuid4().hex[:8]}",
            tanmatra=Tanmatra.SABDA,
            intent=TanmatraIntent.RESPONSE,
            content=text,
            source_indriya=self._vak,
            timestamp=datetime.now(),
        )

        if request_tanmatra:
            tanmatra.metadata["in_response_to"] = request_tanmatra.message_id

        # Store in session
        session.add_tanmatra(tanmatra)

        # Transition to memory state
        self.transition(Vrtti.SMRTI)

        # Then idle
        self.transition(Vrtti.NIDRA)

        logger.info(f"Response sent: session={session_id}")

        return tanmatra

    def _steward_block_message(
        self,
        intent_type: str,
        conscience: "ConscienceVerdict",
        quarter: str,
    ) -> str:
        """
        Generate Shakti-based block message.

        PHYSICS, not chatbot-speak:
        - Shakti = Energy transmission through Prabhupada
        - If Shakti < threshold, action cannot manifest
        - BASE_SHAKTI = HARE_COUNT / WORDS = 8/16 = 0.5

        The Steward reports PHYSICS, not opinions.
        """
        # Measure SHAKTI through Prabhupada (the transparent via medium)
        prabhupada = get_prabhupada()
        shakti = prabhupada.transmit_shakti(self)

        # Thresholds based on quarter (derived from Mahamantra position)
        # GENESIS (0-3): Needs full Shakti (creation)
        # DHARMA (4-7): Needs base Shakti (verification)
        # KARMA (8-11): Needs base Shakti (execution)
        # MOKSHA (12-15): Safe (audit)
        quarter_thresholds = {
            "GENESIS": HARE_COUNT / SEED_WORDS,  # 0.5 (full base)
            "DHARMA": HARE_COUNT / SEED_WORDS,  # 0.5
            "KARMA": HARE_COUNT / SEED_WORDS * 0.8,  # 0.4
            "MOKSHA": HARE_COUNT / SEED_WORDS * 0.2,  # 0.1
        }
        required_shakti = quarter_thresholds.get(quarter, HARE_COUNT / SEED_WORDS)

        # PHYSICS OUTPUT - No chatbot labern
        return f"""⚡ **Shakti Transmission Report**

**Action:** {intent_type}
**Quarter:** {quarter}

**Shakti:** {shakti:.2f}
**Required:** {required_shakti:.2f}
**Status:** {"✗ INSUFFICIENT" if shakti < required_shakti else "⚠ BLOCKED (Guna)"}

**Guna:** {conscience.guna.value.upper()}
**Reason:** {conscience.reason}

---
_Shakti = HARE_COUNT / WORDS = {HARE_COUNT}/{SEED_WORDS} = {HARE_COUNT / SEED_WORDS:.2f} (base)_
_Channel blocked → energy cannot manifest action._
"""

    def _nadi_payload_to_response(self, payload: dict) -> "ChatResponse":
        """
        Convert Nadi response payload back to ChatResponse.

        This is the reverse of ChatService._send_nadi_response().
        Enables clean message passing without tight coupling.
        """
        from vibe_core.protocols.chat import ChatMessage, ChatMode, ChatResponse

        content = payload.get("content", "")
        mode_value = payload.get("mode")

        return ChatResponse(
            success=payload.get("success", False),
            message=ChatMessage(
                role="assistant",
                content=content,
            )
            if content
            else None,
            mahajana=payload.get("mahajana"),
            mode=ChatMode(mode_value) if mode_value else None,
            confidence=payload.get("confidence", 0.0),
        )

    def _analyze_vibration(self, text: str) -> tuple[str, int, str]:
        """
        Analyze the VIBRATION of text using VarnaTensor/Substrate.

        Returns:
            tuple of (intent_type, position, quarter)

        MAHAMANTRA ROUTING:
        - Position 0-3 (GENESIS): Creation → needs genesis permission
        - Position 4-7 (DHARMA): Compilation → needs code_modify
        - Position 8-11 (KARMA): Execution → needs exec permission
        - Position 12-15 (MOKSHA): Audit/Cleanup → generally safe
        """
        from vibe_core.services.chat_substrate_bridge import get_substrate_bridge

        try:
            # Use the REAL substrate routing (VarnaTensor)
            bridge = get_substrate_bridge()
            route = bridge.route(text)

            position = route.position
            quarter = route.quarter.upper()

            # Map quarter to intent_type (permission requirement)
            quarter_to_intent = {
                "GENESIS": "genesis_action",  # Creation needs genesis
                "DHARMA": "code_modify",  # Compilation needs code_modify
                "KARMA": "refactor_major",  # Execution needs exec
                "MOKSHA": "review_todos",  # Audit is safe
            }

            intent_type = quarter_to_intent.get(quarter, "review_todos")

            logger.debug(f"🔊 Vibration: '{text[:30]}...' → pos={position}, quarter={quarter}, intent={intent_type}")

            return intent_type, position, quarter

        except Exception as e:
            logger.warning(f"Substrate routing failed, defaulting to safe: {e}")
            return "review_todos", 2, "GENESIS"  # Safe default: Narada/Query

    def _classify_intent(self, text: str) -> TanmatraIntent:
        """
        Classify the intent of user input.

        Simple heuristic classification:
        - Starts with verb/action word → COMMAND
        - Ends with ? → QUERY
        - Contains please/help → PRAYER
        - Very short/unclear → NOISE
        - Otherwise → QUERY (default)
        """
        text_lower = text.lower().strip()

        # Check for noise
        if len(text_lower) < 3:
            return TanmatraIntent.NOISE

        # Check for query
        if text_lower.endswith("?"):
            return TanmatraIntent.QUERY

        # Check for prayer/request
        prayer_words = ["please", "help", "could you", "would you", "can you"]
        if any(word in text_lower for word in prayer_words):
            return TanmatraIntent.PRAYER

        # Check for command (starts with imperative)
        command_starters = [
            "run",
            "execute",
            "do",
            "create",
            "delete",
            "update",
            "show",
            "list",
            "get",
            "set",
            "make",
            "build",
            "start",
            "stop",
            "find",
        ]
        first_word = text_lower.split()[0] if text_lower.split() else ""
        if first_word in command_starters:
            return TanmatraIntent.COMMAND

        # Default to query
        return TanmatraIntent.QUERY

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================

    def _get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(session_id=session_id)
            logger.info(f"New chat session: {session_id}")

        session = self._sessions[session_id]
        session.touch()
        return session

    def close_session(self, session_id: str) -> bool:
        """Close a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Closed session: {session_id}")
            return True
        return False

    def prune_expired_sessions(self) -> int:
        """Remove expired sessions."""
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        for sid in expired:
            del self._sessions[sid]

        if expired:
            logger.info(f"Pruned {len(expired)} expired sessions")

        return len(expired)

    # =========================================================================
    # GAD COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability."""
        return {
            "service": "chat_indriya",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "indriya_type": "combined",
            "srotra": self._srotra.name,
            "vak": self._vak.name,
            "current_vrtti": self.vrtti.name,
            "capabilities": [
                "intent_classification",
                "tanmatra_messaging",
                "vrtti_state_machine",
                "session_management",
            ],
        }

    def get_state(self) -> Dict[str, object]:
        """GAD Observability."""
        return {
            "service_id": self._service_id,
            "vrtti": self.vrtti.name,
            "srotra_connected": self._srotra_state.is_connected,
            "vak_connected": self._vak_state.is_connected,
            "active_sessions": len([s for s in self._sessions.values() if not s.is_expired]),
            "tanmatras_received": self._tanmatras_received,
            "tanmatras_sent": self._tanmatras_sent,
            "vrtti_transitions": self._vrtti_transitions,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def detect_drift(self) -> List[str]:
        """GAD Drift Detection."""
        issues = []

        # Check for stuck in error state
        if self.vrtti == Vrtti.VIPARYAYA:
            issues.append("Stuck in error (VIPARYAYA) state")

        # Check for expired sessions
        expired = sum(1 for s in self._sessions.values() if s.is_expired)
        if expired > len(self._sessions) // 2:
            issues.append(f"Too many expired sessions: {expired}")

        return issues

    def test_tapas(self) -> bool:
        """GAD Tapas: Resource efficiency."""
        return len(self._sessions) <= CHAT_MESSAGE_BUFFER

    def test_saucam(self) -> bool:
        """GAD Saucam: Connection purity."""
        # Both senses should be in same state
        return self._srotra_state.vrtti == self._vak_state.vrtti

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def set_on_tanmatra(self, callback: Callable[[TanmatraMessage], None]) -> None:
        """Set callback for incoming tanmatras."""
        self._on_tanmatra = callback

    def set_on_vrtti_change(self, callback: Callable[[Vrtti, Vrtti], None]) -> None:
        """Set callback for vrtti transitions."""
        self._on_vrtti_change = callback

    # =========================================================================
    # HEARTBEAT
    # =========================================================================

    def pulse(self) -> bool:
        """Send heartbeat and prune expired sessions."""
        self.prune_expired_sessions()
        self.chant()
        return True


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_chat_indriya(service_id: str = "chat_indriya") -> ChatIndriya:
    """
    Get ChatIndriya through ServiceRegistry (WIRED + NAGA-wrapped + NADI-connected).

    ARCHITECTURE:
        Raw ChatIndriya → Nadi Boot → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern
    - NADI connection (PRANA channel for User ↔ System)
    - NAGA observation (Narada sees all vrtti transitions)
    - NAGA profiling (Chitragupta tracks duration_ms)
    - NAGA isolation (Kaliya handles exceptions)

    Like ChatService, ChatIndriya becomes part of the observed infrastructure.
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(IndriyaProtocol)
    if existing is not None:
        return existing  # Return existing (possibly wrapped) instance

    # Create new instance
    instance = ChatIndriya(service_id)

    # NADI BOOT: Connect to PRANA channel (User ↔ System)
    nadi = None
    try:
        nadi = get_nadi(f"indriya_{service_id}", nadi_type=NadiType.PRANA)
        instance.connect_to_nadi(nadi)
        logger.info(f"✅ ChatIndriya Nadi booted (PRANA channel: indriya_{service_id})")
    except Exception as e:
        logger.warning(f"⚠️ ChatIndriya Nadi boot failed (fallback to direct): {e}")

    # NADI CONNECTION: Connect to ChatService (SAKHYAM - friendship)
    # First ensure ChatService exists so we can connect to it
    if nadi is not None:
        try:
            # Boot ChatService first (creates "chat_service" Nadi endpoint)
            from vibe_core.services.chat_service import get_chat_service

            _chat_service = get_chat_service()

            # Now connect to ChatService via Nadi
            if nadi.connect("chat_service"):
                logger.info("✅ ChatIndriya connected to ChatService via NADI (SAKHYAM)")
            else:
                logger.warning("⚠️ ChatIndriya could not connect to ChatService Nadi")
        except Exception as e:
            logger.warning(f"⚠️ ChatIndriya Nadi connection failed: {e}")

    # Register with ServiceRegistry (this applies NagaProxy wrapping!)
    ServiceRegistry.register(IndriyaProtocol, instance)
    logger.info("✅ ChatIndriya registered via ServiceRegistry (WIRED + NAGA-observed)")

    # Return the wrapped version from registry
    return ServiceRegistry.get(IndriyaProtocol)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CHAT_SESSION_TIMEOUT_MS",
    "CHAT_MESSAGE_BUFFER",
    "VRTTI_COOLDOWN_MS",
    # Data structures
    "ChatSession",
    # Service
    "ChatIndriya",
    # Factory
    "get_chat_indriya",
]
