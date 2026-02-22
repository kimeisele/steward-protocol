"""
CHAT REFINEMENT - Intent Negotiation Module
============================================

"When resonance is ambiguous, ask - don't guess."

RESONANCE THRESHOLDS:
- > 0.7: Auto-execute (high resonance)
- 0.4-0.7: Intent Negotiation (this module)
- < 0.4: Silence (refuse to guess)

Extracted from ChatService for modularity (<800 lines per file).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x66d82a7a"  # GenesisByte: parampara % 37 == 0

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from vibe_core.mahamantra.protocols._lotus import get_position_mahajana
from vibe_core.protocols.chat import (
    ChatContext,
    ChatMessage,
    ChatMode,
    ChatResponse,
    RefinementPath,
    RefinementRequest,
    RefinementState,
)
from vibe_core.protocols.cognition import CognitiveResult, IntentType

logger = logging.getLogger("CHAT_REFINEMENT")


# =============================================================================
# DHARMA DESCRIPTIONS (SSOT for Mahajana roles)
# =============================================================================

MAHAJANA_DHARMAS: Dict[str, str] = {
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

# OpCodes per position (16 positions)
POSITION_OPCODES: List[str] = [
    "SYS_WAKE",
    "LOAD_ROOT",
    "ALLOC_MEM",
    "BIND_CTX",
    "ASSERT_TRUTH",
    "RESOLVE_REQ",
    "GARBAGE_COLLECT",
    "PULSE_SYNC",
    "FETCH_RES",
    "EXEC_SERVICE",
    "CHECK_DHARMA",
    "COMMIT_LOG",
    "CACHE_STATE",
    "OPTIMIZE",
    "YIELD_CPU",
    "RESET_IP",
]


def get_dharma_description(mahajana: str) -> str:
    """Get dharma description for a Mahajana."""
    return MAHAJANA_DHARMAS.get(mahajana, "Unknown")


# =============================================================================
# REFINEMENT PATH DISCOVERY
# =============================================================================


def discover_refinement_paths(
    message: str,
    resonance: Dict,
    max_paths: int = 3,
) -> List[RefinementPath]:
    """
    Discover possible paths for refinement.

    Uses Mahajana capabilities and resonance to find candidates.
    NOT hardcoded - uses atomic discovery from INTENT_MAP.

    Args:
        message: Original user message
        resonance: Resonance result from substrate
        max_paths: Maximum number of paths to return

    Returns:
        List of RefinementPath candidates, sorted by confidence
    """
    from vibe_core.mahamantra import INTENT_MAP

    paths = []
    msg_lower = message.lower()

    # Score each position based on keyword overlap + resonance
    for position, keywords in INTENT_MAP.items():
        score = 0.0

        # Check keyword matches
        for keyword in keywords:
            if keyword in msg_lower:
                score += 0.3

        # Add resonance influence based on quarter alignment
        quarter = position // 4
        dominant = resonance.get("dominant", "void")

        if quarter == 0 and dominant == "hare":
            score += 0.2
        elif quarter == 1 and dominant == "krishna":
            score += 0.2
        elif quarter >= 2 and dominant == "rama":
            score += 0.2

        # Only include if score is meaningful
        if score >= 0.2:
            mahajana = get_position_mahajana(position)
            dharma_desc = get_dharma_description(mahajana)

            paths.append(
                RefinementPath(
                    mahajana=mahajana,
                    position=position,
                    description=dharma_desc,
                    confidence=min(score + resonance.get("magnitude", 0.5) * 0.5, 1.0),
                    opcode=POSITION_OPCODES[position],
                )
            )

    # Sort by confidence, return top N
    paths.sort(key=lambda p: p.confidence, reverse=True)
    return paths[:max_paths]


# =============================================================================
# REFINEMENT HANDLER
# =============================================================================


class RefinementHandler:
    """
    Handles Intent Negotiation (Refinement) for ambiguous resonance.

    When resonance magnitude is in the gray zone (0.4-0.7),
    this handler discovers possible paths and manages user selection.
    """

    def __init__(
        self,
        sessions: Dict[str, List[ChatMessage]],
        refinement_states: Dict[str, RefinementState],
    ):
        """
        Initialize handler with shared state references.

        Args:
            sessions: Reference to session history dict
            refinement_states: Reference to refinement states dict
        """
        self._sessions = sessions
        self._refinement_states = refinement_states

    def create_silence_response(self, message: str, context: ChatContext, magnitude: float) -> ChatResponse:
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

        if context.session_id in self._sessions:
            self._sessions[context.session_id].append(silence_msg)

        return ChatResponse(
            success=False,
            message=silence_msg,
            mode=ChatMode.SILENCE,
            confidence=magnitude,
            error="NO_RESONANCE",
        )

    async def create_refinement_response(self, message: str, context: ChatContext, resonance: Dict) -> ChatResponse:
        """
        Create REFINEMENT response when resonance is ambiguous (0.4-0.7).

        Discovers possible paths and asks user to choose.
        """
        # Discover paths based on resonance
        paths = discover_refinement_paths(message, resonance)

        if not paths:
            # Fallback: no clear paths, treat as silence
            return self.create_silence_response(message, context, resonance["magnitude"])

        # Build prompt
        path_options = "\n".join(
            f"  [{i + 1}] {p.mahajana.upper()}: {p.description} (resonance={p.confidence:.2f})"
            for i, p in enumerate(paths)
        )
        prompt = (
            f"Ich sehe {len(paths)} Pfade mit ahnlicher Resonanz:\n"
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

        if context.session_id in self._sessions:
            self._sessions[context.session_id].append(refinement_msg)

        return ChatResponse(
            success=True,
            message=refinement_msg,
            mode=ChatMode.REFINEMENT,
            confidence=resonance["magnitude"],
        )

    def parse_user_selection(self, message: str, request: RefinementRequest) -> Optional[RefinementPath]:
        """
        Parse user's response to a RefinementRequest.

        Supports:
        - Numeric selection: "1", "2", "3"
        - Mahajana name: "kapila", "narada"

        Returns:
            Selected RefinementPath or None if couldn't parse
        """
        msg_lower = message.strip().lower()

        # Try numeric selection (1, 2, 3)
        if msg_lower.isdigit():
            idx = int(msg_lower) - 1
            if 0 <= idx < len(request.paths):
                return request.paths[idx]

        # Try mahajana name
        for path in request.paths:
            if path.mahajana.lower() in msg_lower:
                return path

        return None

    def clear_state(self, session_id: str) -> None:
        """Clear refinement state for a session."""
        if session_id in self._refinement_states:
            del self._refinement_states[session_id]

    def has_active_refinement(self, session_id: str) -> bool:
        """Check if session has active refinement."""
        state = self._refinement_states.get(session_id)
        return state is not None and state.awaiting_response

    def get_state(self, session_id: str) -> Optional[RefinementState]:
        """Get refinement state for a session."""
        return self._refinement_states.get(session_id)


# =============================================================================
# MODE DETERMINATION
# =============================================================================


def determine_chat_mode(cognitive: CognitiveResult, lotus: Dict) -> ChatMode:
    """Determine chat mode based on Lotus routing."""
    if cognitive.intent_type == IntentType.CHAT:
        return ChatMode.DIRECT
    elif cognitive.intent_type == IntentType.QUERY:
        return ChatMode.QUERY
    elif lotus.get("is_head"):
        return ChatMode.SYSCALL
    else:
        return ChatMode.ROUTED


# =============================================================================
# SIMPLE INTENT DETECTION (SSOT-based, no ML)
# =============================================================================


def simple_intent_detection(message: str) -> CognitiveResult:
    """
    Intent detection using INTENT_MAP (SSOT).

    Uses mahamantra/substrate/intents.py - NO ML, pure dict lookup.
    Extracted from ChatService for modularity.
    """
    from vibe_core.mahamantra import get_position_for_intent

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


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAHAJANA_DHARMAS",
    "POSITION_OPCODES",
    # Functions
    "get_dharma_description",
    "discover_refinement_paths",
    "determine_chat_mode",
    "simple_intent_detection",
    # Handler
    "RefinementHandler",
]
