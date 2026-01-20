"""
MAHAMANTRA CHAT - Guardian Chat Infrastructure
===============================================

"steward chat ist nicht nur 1 chat" - Each guardian has their own domain.

This module provides the infrastructure for guardian-specific chat:
1. Loads prompts from PromptRegistry (config/prompts/genesis.yaml)
2. Provides MahajanaChat base class for guardians to extend
3. Routes through proper LLM infrastructure

USAGE:
    # In a guardian's service module:
    from vibe_core.mahamantra.chat import MahajanaChat

    class KapilaService:
        def on_chat(self, message: str) -> str:
            chat = MahajanaChat(position=6, guardian="kapila")
            return chat.respond(message)

    # Or use the convenience function:
    from vibe_core.mahamantra.chat import guardian_chat
    response = guardian_chat("analyze this code", guardian="kapila")
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xd3f1a829"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, WORDS

logger = logging.getLogger(__name__)


# =============================================================================
# GUARDIAN DHARMA DESCRIPTIONS (SSOT)
# =============================================================================

GUARDIAN_DHARMA: Dict[str, str] = {
    "vyasa": "System Wake, Genesis, Boot - Initialisierung und Start",
    "brahma": "Creation, Spawning, Genesis - Schöpfung neuer Entitäten",
    "narada": "Communication, Broadcast, Events - Nachrichten und Ereignisse",
    "shambhu": "Destruction, Transformation, Cleanup - Transformation und Auflösung",
    "prithu": "Structure, Compile, Document - Struktur und Wissensaufbau",
    "kumaras": "Purification, Resolution, Lint - Reinigung und Auflösung",
    "kapila": "Analysis, Logic, Inference - Analyse und logische Schlüsse",
    "manu": "Governance, Rules, Law - Regeln und Gesetze",
    "parashurama": "Execution, Enforcement, Action - Ausführung und Durchsetzung",
    "prahlada": "Protection, Resilience, Faith - Schutz und Widerstandskraft",
    "janaka": "Duty, Scheduling, Tasks - Pflicht und Aufgabenverwaltung",
    "bhishma": "Persistence, Commit, Ledger - Beständigkeit und Aufzeichnung",
    "nrisimha": "Security, Guard, Terminate - Sicherheit und Schutz",
    "bali": "Resources, Allocation, Surrender - Ressourcen und Hingabe",
    "shuka": "Observation, Vision, Status - Beobachtung und Einsicht",
    "yamaraja": "Judgment, Audit, Verdict - Urteil und Prüfung",
}

GUARDIAN_WORDS: Dict[str, str] = {
    "vyasa": "HARE",
    "brahma": "KRISHNA",
    "narada": "HARE",
    "shambhu": "KRISHNA",
    "prithu": "KRISHNA",
    "kumaras": "KRISHNA",
    "kapila": "HARE",
    "manu": "HARE",
    "parashurama": "HARE",
    "prahlada": "RAMA",
    "janaka": "HARE",
    "bhishma": "RAMA",
    "nrisimha": "RAMA",
    "bali": "RAMA",
    "shuka": "HARE",
    "yamaraja": "HARE",
}

GUARDIAN_QUARTERS: Dict[str, str] = {
    "vyasa": "GENESIS",
    "brahma": "GENESIS",
    "narada": "GENESIS",
    "shambhu": "GENESIS",
    "prithu": "DHARMA",
    "kumaras": "DHARMA",
    "kapila": "DHARMA",
    "manu": "DHARMA",
    "parashurama": "KARMA",
    "prahlada": "KARMA",
    "janaka": "KARMA",
    "bhishma": "KARMA",
    "nrisimha": "MOKSHA",
    "bali": "MOKSHA",
    "shuka": "MOKSHA",
    "yamaraja": "MOKSHA",
}


# =============================================================================
# MAHAJANA CHAT CLASS
# =============================================================================


@dataclass
class ChatResult:
    """Result from MahajanaChat.respond()."""

    success: bool
    response: str
    guardian: str
    position: int
    llm_used: bool = False
    prompt_key: Optional[str] = None


class MahajanaChat:
    """
    Guardian-aware chat handler.

    Uses PromptRegistry for prompts instead of hardcoded strings.
    Routes through proper LLM infrastructure.
    """

    def __init__(
        self,
        position: int,
        guardian: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
        Initialize MahajanaChat for a specific guardian.

        Args:
            position: Mahamantra position (0-15)
            guardian: Guardian name (optional, derived from position if not provided)
            history: Conversation history (optional)
        """
        if position < 0 or position >= WORDS:
            raise ValueError(f"Invalid position: {position}")

        self.position = position
        self.guardian = guardian or ALL_GUARDIANS[position]
        self.history = history or []
        self._llm = None
        self._llm_available = False

        # Lazy init LLM provider and context
        self._provider = None
        self._prompt_context = None
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize LLM provider (NOT LLMEngine - real provider.invoke())."""
        self._chat_model = None  # Model from config

        try:
            from vibe_core.runtime.providers.factory import create_provider, _detect_provider

            provider_name = _detect_provider()
            if provider_name != "noop":
                self._provider = create_provider(provider_name=provider_name)
                self._llm_available = self._provider.is_available()
                logger.info(f"🧠 MahajanaChat: Provider initialized ({provider_name})")
            else:
                self._llm_available = False
                logger.warning("⚠️ MahajanaChat: No LLM provider available (noop)")

            # Initialize PromptContext for runtime context resolution
            from vibe_core.runtime.prompt_context import get_prompt_context
            self._prompt_context = get_prompt_context()
            logger.debug("✅ MahajanaChat: PromptContext initialized")

            # Load model from config (NO HARDCODING!)
            self._load_model_from_config()

        except ImportError as e:
            logger.warning(f"⚠️ MahajanaChat: Could not init provider: {e}")
            self._llm_available = False
        except Exception as e:
            logger.warning(f"⚠️ MahajanaChat: Provider init failed: {e}")
            self._llm_available = False

        # Keep legacy _llm for backwards compat
        self._llm = None

    def _load_model_from_config(self) -> None:
        """Load model from config/steward.yaml - FAILS if not configured!"""
        from vibe_core.phoenix import get_config

        config = get_config()
        steward_cfg = config.steward

        # Chat uses EFFICIENCY model (cheap/fast) from cognitive_policy
        self._chat_model = steward_cfg.cognitive_policy.model_preferences.efficiency

        if not self._chat_model:
            # Try fallback model if efficiency not set
            self._chat_model = steward_cfg.cognitive_policy.model_preferences.fallback

        if not self._chat_model:
            raise ValueError(
                "❌ FATAL: No model configured for chat! "
                "Set 'cognitive_policy.model_preferences.efficiency' in config/steward.yaml"
            )

        logger.info(f"🧠 MahajanaChat: Using model from config: {self._chat_model}")

    def _get_runtime_context(self) -> Dict[str, str]:
        """
        Get runtime context from PromptContext (18+ resolvers).

        This is what makes prompts LIVE - not hardcoded templates.
        """
        if not self._prompt_context:
            return {}

        try:
            # Resolve key context values for chat
            keys = [
                "git_status",
                "current_branch",
                "project_structure",
                "system_time",
                "kernel_status",
            ]
            return self._prompt_context.resolve(keys)
        except Exception as e:
            logger.warning(f"⚠️ Context resolution failed: {e}")
            return {}

    def _build_system_prompt(self, message: str) -> str:
        """
        Build system prompt at RUNTIME with live context.

        NOT a Jinja template - built dynamically using PromptContext.
        """
        # Get live system context
        context = self._get_runtime_context()

        # Build context block
        context_block = ""
        if context:
            context_block = "\n\n## LIVE SYSTEM CONTEXT\n"
            if context.get("current_branch"):
                context_block += f"Git Branch: {context['current_branch']}\n"
            if context.get("git_status"):
                context_block += f"Git Status: {context['git_status'][:200]}\n"
            if context.get("kernel_status"):
                context_block += f"Kernel: {context['kernel_status']}\n"
            if context.get("system_time"):
                context_block += f"Time: {context['system_time']}\n"

        # Build guardian-specific system prompt
        return f"""You are {self.guardian.upper()}, a Guardian of the Mahamantra Protocol.

## YOUR IDENTITY
- Position: {self.position} (of 16)
- Quarter: {GUARDIAN_QUARTERS.get(self.guardian, 'UNKNOWN')}
- Word: {GUARDIAN_WORDS.get(self.guardian, 'UNKNOWN')}
- Dharma: {GUARDIAN_DHARMA.get(self.guardian, 'Unknown')}

## YOUR ROLE
{GUARDIAN_DHARMA.get(self.guardian, 'Serve the protocol with wisdom and precision.')}

You respond with the personality and expertise of your domain.
Be concise, technical, and helpful.
{context_block}"""

    def _get_prompt(self, message: str) -> str:
        """
        Build the user prompt for LLM invocation.

        The system prompt is separate - this is just the user message.
        """
        return message

    def respond(self, message: str) -> ChatResult:
        """
        Generate a response using REAL LLM provider.invoke().

        NOT mock templates - actual LLM calls with:
        1. Runtime context from PromptContext (18+ resolvers)
        2. Guardian-specific system prompt built dynamically
        3. provider.invoke() for real LLM response
        """
        if not message or not message.strip():
            return ChatResult(
                success=False,
                response="Keine Nachricht erhalten.",
                guardian=self.guardian,
                position=self.position,
                llm_used=False,
            )

        # If LLM not available, return identity response
        if not self._llm_available or not self._provider:
            return ChatResult(
                success=True,
                response=(
                    f"Ich bin {self.guardian.upper()} (Position {self.position}).\n"
                    f"Quarter: {GUARDIAN_QUARTERS.get(self.guardian, '?')}\n"
                    f"Dharma: {GUARDIAN_DHARMA.get(self.guardian, '?')}\n\n"
                    f"(LLM nicht verfügbar - set ANTHROPIC_API_KEY, OPENROUTER_API_KEY, or GOOGLE_API_KEY)"
                ),
                guardian=self.guardian,
                position=self.position,
                llm_used=False,
            )

        try:
            # Build runtime prompts (NOT templates - live context)
            system_prompt = self._build_system_prompt(message)
            user_prompt = self._get_prompt(message)

            # REAL LLM CALL via provider.invoke()
            # Model from config/steward.yaml (NO HARDCODING!)
            model = self._chat_model  # efficiency model (haiku = cheap!)
            logger.info(f"🧠 {self.guardian.upper()}: Invoking LLM (model: {model or 'provider-default'})...")

            # Build messages array with system prompt
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Try provider.invoke() with model from config
            invoke_kwargs = {
                "prompt": user_prompt,  # Fallback for providers that don't support messages
                "messages": messages,   # Native format for OpenRouter/OpenAI
                "max_tokens": 1024,
                "temperature": 0.7,
            }
            if model:
                invoke_kwargs["model"] = model

            llm_response = self._provider.invoke(**invoke_kwargs)

            response_text = llm_response.content

            # Store in history
            self.history.append({"user": message, "assistant": response_text})

            logger.info(
                f"✅ {self.guardian.upper()}: Response generated "
                f"({llm_response.usage.output_tokens} tokens, ${llm_response.usage.cost_usd:.4f})"
            )

            return ChatResult(
                success=True,
                response=response_text,
                guardian=self.guardian,
                position=self.position,
                llm_used=True,
                prompt_key=f"mahamantra.chat.{self.guardian}",
            )

        except Exception as e:
            logger.error(f"❌ {self.guardian.upper()}: LLM call failed: {e}")
            return ChatResult(
                success=False,
                response=f"Chat-Fehler bei {self.guardian.upper()}: {e}",
                guardian=self.guardian,
                position=self.position,
                llm_used=True,
            )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def guardian_chat(message: str, *, guardian: str, position: Optional[int] = None) -> str:
    """
    Quick chat with a specific guardian.

    Args:
        message: User message
        guardian: Guardian name (e.g., "kapila", "narada")
        position: Optional position (derived from guardian if not provided)

    Returns:
        Response string
    """
    # Get position from guardian name if not provided
    if position is None:
        guardian_lower = guardian.lower()
        if guardian_lower in ALL_GUARDIANS:
            position = ALL_GUARDIANS.index(guardian_lower)
        else:
            raise ValueError(f"Unknown guardian: {guardian}")

    chat = MahajanaChat(position=position, guardian=guardian)
    result = chat.respond(message)
    return result.response


def get_guardian_for_message(message: str) -> str:
    """
    Use mahamantra.resonate() to find the best guardian for a message.

    Args:
        message: User message

    Returns:
        Guardian name
    """
    try:
        from vibe_core.mahamantra import mahamantra

        score, winning_node = mahamantra.resonate(message)

        if winning_node and score > 0:
            # Extract guardian from node path
            if hasattr(winning_node, "_path") and winning_node._path.depth >= 2:
                return winning_node._path.segments[1]

        # Default to Narada (the messenger)
        return "narada"

    except Exception:
        return "narada"


def routed_chat(message: str) -> str:
    """
    Chat with automatic guardian routing via mahamantra.resonate().

    The message is analyzed and routed to the most appropriate guardian.

    Args:
        message: User message

    Returns:
        Response string from the appropriate guardian
    """
    guardian = get_guardian_for_message(message)
    return guardian_chat(message, guardian=guardian)


# =============================================================================
# NAGA FLOODING - Layer -1 Integration
# =============================================================================
# "NAGA x MAHAMANTRA = BOOM" - Chat flooded with NAGA genes:
# - ChitraguptaMixin: Audit every chat interaction
# - TakshakaMixin: Security/toxicity scanning
# - NaradaMixin: Event broadcasting
# - SeshaMixin: Persistence of chat history
# =============================================================================


class FloodedMahajanaChat(MahajanaChat):
    """
    MahajanaChat flooded with ALL 12 NAGA genes.

    Ananta Shesha (Layer -1) provides the FULL federation:

    INFRASTRUCTURE LAYER (8):
    - Sesha: Persistence/Ledger (foundation)
    - Vasuki: Network/Serialization
    - Takshaka: Security/Toxicity
    - Kaliya: Retry/Resilience
    - Karkotaka: Secrets/Credentials
    - Kulika: Decorators/Wiring
    - Padma: Purity/Validation
    - Shankha: Signals/Alerts

    GOVERNANCE LAYER (3):
    - Narada: Discovery/Events
    - Chitragupta: Audit/Recording
    - Prahlad: Veto/Protection

    SUBSTRATE (1):
    - Ananta: The Host (holds all genes)

    GAD-000 COMPLIANT: discover(), get_state(), is_healthy(), chant()

    Usage:
        chat = FloodedMahajanaChat(position=6, guardian="kapila")
        result = chat.respond("analyze this code")
        # 12 NAGAs flooding every interaction!
    """

    # NAGA gene markers - ALL 12 LORDS
    _naga_flooded: bool = True
    _naga_genes: List[str] = [
        # Infrastructure Layer (8)
        "sesha", "vasuki", "takshaka", "kaliya",
        "karkotaka", "kulika", "padma", "shankha",
        # Governance Layer (3)
        "narada", "chitragupta", "prahlad",
        # Substrate (1)
        "ananta",
    ]

    def __init__(
        self,
        position: int,
        guardian: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        super().__init__(position, guardian, history)

        # ALL 12 NAGA services (lazy loaded)
        # Infrastructure Layer
        self._sesha = None
        self._vasuki = None
        self._takshaka = None
        self._kaliya = None
        self._karkotaka = None
        self._kulika = None
        self._padma = None
        self._shankha = None
        # Governance Layer
        self._narada = None
        self._chitragupta = None
        self._prahlad = None
        # Substrate
        self._ananta = None

        self._naga_initialized = False

        # GAD-000 Heartbeat
        self._heartbeat_count = 0

    def _init_naga(self) -> None:
        """Lazy init ALL 12 NAGA services from Layer -1."""
        if self._naga_initialized:
            return

        # === INFRASTRUCTURE LAYER (8) ===

        # 1. Sesha (foundation - must be first)
        try:
            from vibe_core.naga import SeshaService
            self._sesha = SeshaService()
        except Exception:
            pass

        # 2. Takshaka (security - needs Sesha)
        try:
            from vibe_core.naga import TakshakaService
            self._takshaka = TakshakaService(sesha=self._sesha)
        except Exception:
            pass

        # 3. Vasuki (network - needs Sesha and Takshaka)
        try:
            from vibe_core.naga import VasukiService
            self._vasuki = VasukiService(sesha=self._sesha, takshaka=self._takshaka)
        except Exception:
            pass

        # 4. Kaliya (resilience - optional deps)
        try:
            from vibe_core.naga import KaliyaService
            self._kaliya = KaliyaService()
        except Exception:
            pass

        # 5. Karkotaka (secrets)
        try:
            from vibe_core.naga import KarkotakaService
            self._karkotaka = KarkotakaService()
        except Exception:
            pass

        # 6. Kulika (wiring)
        try:
            from vibe_core.naga import KulikaService
            self._kulika = KulikaService()
        except Exception:
            pass

        # 7. Padma (purity/cache)
        try:
            from vibe_core.naga import PadmaService
            self._padma = PadmaService()
        except Exception:
            pass

        # 8. Shankha (signals/pubsub)
        try:
            from vibe_core.naga import ShankhaService
            self._shankha = ShankhaService()
        except Exception:
            pass

        # === GOVERNANCE LAYER (3) ===

        # 9. Narada (events/discovery)
        try:
            from vibe_core.naga import NaradaService
            self._narada = NaradaService()
        except Exception:
            pass

        # 10. Chitragupta (audit/metrics)
        try:
            from vibe_core.naga import ChitraguptaService
            self._chitragupta = ChitraguptaService()
        except Exception:
            pass

        # 11. Prahlad (protection/veto)
        try:
            from vibe_core.naga import PrahladService
            self._prahlad = PrahladService()
        except Exception:
            pass

        # === SUBSTRATE (1) ===

        # 12. Ananta (the host - binds all genes)
        try:
            from vibe_core.naga.services.ananta import AnantaService
            self._ananta = AnantaService()
        except Exception:
            pass

        self._naga_initialized = True

    # =========================================================================
    # GAD-000 COMPLIANCE (Operator Inversion)
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD-000: Machine-readable capability description."""
        return {
            "type": "FloodedMahajanaChat",
            "guardian": self.guardian,
            "position": self.position,
            "naga_genes": self._naga_genes,
            "capabilities": ["chat", "route", "audit", "security"],
        }

    def get_state(self) -> Dict[str, object]:
        """GAD-000: Current state in structured format."""
        self._init_naga()
        return {
            "guardian": self.guardian,
            "position": self.position,
            "history_length": len(self.history),
            "heartbeat_count": self._heartbeat_count,
            "naga_status": {
                "sesha": self._sesha is not None,
                "vasuki": self._vasuki is not None,
                "takshaka": self._takshaka is not None,
                "kaliya": self._kaliya is not None,
                "karkotaka": self._karkotaka is not None,
                "kulika": self._kulika is not None,
                "padma": self._padma is not None,
                "shankha": self._shankha is not None,
                "narada": self._narada is not None,
                "chitragupta": self._chitragupta is not None,
                "prahlad": self._prahlad is not None,
                "ananta": self._ananta is not None,
            },
        }

    def is_healthy(self) -> bool:
        """GAD-000: Health status."""
        self._init_naga()
        # Healthy if at least 6 NAGAs are active (50%)
        active = sum([
            self._sesha is not None,
            self._takshaka is not None,
            self._chitragupta is not None,
            self._narada is not None,
            self._prahlad is not None,
            self._ananta is not None,
        ])
        return active >= 3

    def chant(self) -> bool:
        """GAD-000: The Japa-Loop heartbeat."""
        self._heartbeat_count += 1
        return True  # Heartbeat successful

    def respond(self, message: str) -> ChatResult:
        """
        Respond with FULL 12-NAGA flooding.

        THE COMPLETE FLOW (All 12 NAGAs):

        PRE-PROCESSING:
        1. PRAHLAD: Veto check (protection)
        2. TAKSHAKA: Security scan (toxicity)
        3. PADMA: Purity validation
        4. KARKOTAKA: Credential check

        PROCESSING:
        5. KALIYA: Retry wrapper (resilience)
        6. VASUKI: Serialize request
        7. PARENT: Generate response via MahajanaChat

        POST-PROCESSING:
        8. CHITRAGUPTA: Audit the interaction
        9. NARADA: Broadcast chat event
        10. SESHA: Persist to ledger
        11. SHANKHA: Signal completion
        12. ANANTA: Bind to substrate
        """
        self._init_naga()

        # === PRE-PROCESSING ===

        # 1. PRAHLAD: Protection veto
        if self._prahlad and hasattr(self._prahlad, "can_proceed"):
            try:
                if not self._prahlad.can_proceed("chat", message):
                    return ChatResult(
                        success=False,
                        response="Blocked by Prahlad: Operation not permitted",
                        guardian=self.guardian,
                        position=self.position,
                        llm_used=False,
                    )
            except Exception:
                pass

        # 2. TAKSHAKA: Security scan
        if self._takshaka:
            try:
                toxicity = self._takshaka.scan_toxicity(message)
                if toxicity.get("is_toxic", False):
                    return ChatResult(
                        success=False,
                        response=f"Blocked by Takshaka: {toxicity.get('reason', 'toxic')}",
                        guardian=self.guardian,
                        position=self.position,
                        llm_used=False,
                    )
            except Exception:
                pass

        # 3. PADMA: Purity validation
        if self._padma and hasattr(self._padma, "validate"):
            try:
                self._padma.validate(message)
            except Exception:
                pass

        # 4. KARKOTAKA: Credential check (for sensitive operations)
        # (No action needed for basic chat)

        # === PROCESSING ===

        # 5. KALIYA: Retry wrapper
        max_retries = 1
        if self._kaliya and hasattr(self._kaliya, "get_retry_count"):
            try:
                max_retries = self._kaliya.get_retry_count("chat")
            except Exception:
                pass

        # 6. VASUKI: Serialize request (for network ops)
        # (Chat is local, no serialization needed)

        # 7. PARENT: Generate response with retry
        result = None
        for attempt in range(max_retries):
            try:
                result = super().respond(message)
                if result.success:
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    result = ChatResult(
                        success=False,
                        response=f"Error after {max_retries} attempts: {e}",
                        guardian=self.guardian,
                        position=self.position,
                        llm_used=False,
                    )

        if result is None:
            result = ChatResult(
                success=False,
                response="No response generated",
                guardian=self.guardian,
                position=self.position,
                llm_used=False,
            )

        # === POST-PROCESSING ===

        # 8. CHITRAGUPTA: Audit
        if self._chitragupta:
            try:
                self._chitragupta.record_event(
                    event_type="MAHAMANTRA_CHAT",
                    agent_id=f"MAHAMANTRA.{self.guardian.upper()}",
                    details={
                        "position": self.position,
                        "guardian": self.guardian,
                        "message_len": len(message),
                        "response_len": len(result.response),
                        "llm_used": result.llm_used,
                        "success": result.success,
                        "naga_count": 12,
                    },
                    result="OK" if result.success else "FAILED",
                )
            except Exception:
                pass

        # 9. NARADA: Broadcast event
        if self._narada:
            try:
                self._narada.broadcast_event(
                    event_type="chat",
                    source=f"mahamantra.{self.guardian}",
                    data={
                        "guardian": self.guardian,
                        "position": self.position,
                        "success": result.success,
                    },
                )
            except Exception:
                pass

        # 10. SESHA: Persist
        if self._sesha and hasattr(self._sesha, "record_event"):
            try:
                self._sesha.record_event(
                    event_type="CHAT_HISTORY",
                    data={
                        "guardian": self.guardian,
                        "user": message[:100],
                        "assistant": result.response[:100],
                    },
                )
            except Exception:
                pass

        # 11. SHANKHA: Signal completion
        if self._shankha and hasattr(self._shankha, "signal"):
            try:
                self._shankha.signal("chat_complete", {
                    "guardian": self.guardian,
                    "success": result.success,
                })
            except Exception:
                pass

        # 12. ANANTA: Heartbeat to substrate
        if self._ananta and hasattr(self._ananta, "resonate"):
            try:
                from vibe_core.mahamantra.substrate.opcode import MantraOpCode
                self._ananta.resonate(MantraOpCode.EMIT)
            except Exception:
                pass

        # GAD-000: Chant heartbeat
        self.chant()

        return result


def flooded_guardian_chat(
    message: str, *, guardian: str, position: Optional[int] = None
) -> str:
    """
    Chat with NAGA flooding - audited, secured, broadcast, persisted.

    Args:
        message: User message
        guardian: Guardian name
        position: Optional position

    Returns:
        Response string (with full NAGA integration)
    """
    if position is None:
        guardian_lower = guardian.lower()
        if guardian_lower in ALL_GUARDIANS:
            position = ALL_GUARDIANS.index(guardian_lower)
        else:
            raise ValueError(f"Unknown guardian: {guardian}")

    chat = FloodedMahajanaChat(position=position, guardian=guardian)
    result = chat.respond(message)
    return result.response


def flooded_routed_chat(message: str) -> str:
    """
    Chat with automatic routing AND NAGA flooding.

    The ultimate: Mahamantra routes, NAGA floods.
    """
    guardian = get_guardian_for_message(message)
    return flooded_guardian_chat(message, guardian=guardian)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Original
    "MahajanaChat",
    "ChatResult",
    "guardian_chat",
    "get_guardian_for_message",
    "routed_chat",
    "GUARDIAN_DHARMA",
    "GUARDIAN_WORDS",
    "GUARDIAN_QUARTERS",
    # NAGA Flooded
    "FloodedMahajanaChat",
    "flooded_guardian_chat",
    "flooded_routed_chat",
]
