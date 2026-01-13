"""
OPUS-050: VEDA (The Four-Fold Knowledge) - Processing Pipeline.

Sanskrit: Veda = Knowledge, Wisdom, Sacred Texts.

This module implements the eternal four-fold principle that appears
throughout Vedic philosophy and can be applied to any process:

    Shabda → Artha → Pratyaya → Karma
    (Word)  (Meaning) (Trust)   (Action)

Architecture:
    User Input "Prüfe Drift"
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │  SHABDA (Das Wort)                              │
    │  - Tokenize input                               │
    │  - Identify language                            │
    │  - Extract raw keywords                         │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │  ARTHA (Die Bedeutung)                          │
    │  - Map tokens to intents                        │
    │  - Resolve semantic meaning                     │
    │  - Determine route/handler                      │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │  PRATYAYA (Das Vertrauen)                       │
    │  - Check authorization                          │
    │  - Validate system state                        │
    │  - Verify preconditions                         │
    └─────────────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────────────┐
    │  KARMA (Die Handlung)                           │
    │  - Execute the action                           │
    │  - Return results                               │
    │  - Record for memory                            │
    └─────────────────────────────────────────────────┘

"First the word is heard (Shabda), then its meaning understood (Artha),
then trust is established (Pratyaya), and only then can action flow (Karma)."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x0bcd4ded"  # GenesisByte: parampara % 37 == 0

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Cortex.Veda")


# =============================================================================
# SECTION 1: DATA MODELS
# =============================================================================


class VedaIntent(Enum):
    """Semantic intents recognized by the VEDA pipeline."""

    # System queries
    STATUS = "status"
    INTENTS = "intents"
    CAPABILITIES = "capabilities"
    HELP = "help"

    # DHARMA (Architecture)
    DRIFT = "drift"
    ARCHITECTURE = "architecture"
    COMPLIANCE = "compliance"

    # MANDALA (Configuration)
    MANDALA = "mandala"

    # AKASHA (Knowledge Graph)
    AKASHA = "akasha"
    KNOWLEDGE = "knowledge"
    DEPENDENCIES = "dependencies"

    # SILPA (Self-Refactoring)
    SILPA = "silpa"
    REFACTOR = "refactor"

    # SUTRA (Wiki Documentation)
    SUTRA = "sutra"
    WIKI = "wiki"

    # SANKALPA (Proactive Strategy)
    SANKALPA = "sankalpa"
    MISSIONS = "missions"
    STRATEGY = "strategy"

    # KRIYA (Actions)
    ACTION = "action"

    # Fallback
    CHAT = "chat"
    UNKNOWN = "unknown"


class VedaLanguage(Enum):
    """Detected input language."""

    ENGLISH = "en"
    GERMAN = "de"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class VedaTrustLevel(Enum):
    """Trust/Authorization levels."""

    SYSTEM = "system"  # Full system access
    ADMIN = "admin"  # Administrative access
    USER = "user"  # Normal user access
    GUEST = "guest"  # Limited access
    BLOCKED = "blocked"  # No access


@dataclass
class ShabdaResult:
    """
    Result of Shabda (Word) phase - Tokenization and keyword extraction.

    This is the raw linguistic analysis before semantic interpretation.
    """

    raw_input: str
    normalized: str  # Lowercase, trimmed
    tokens: List[str]
    keywords: Set[str]
    language: VedaLanguage
    is_question: bool
    is_command: bool
    word_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_input": self.raw_input,
            "normalized": self.normalized,
            "tokens": self.tokens,
            "keywords": list(self.keywords),
            "language": self.language.value,
            "is_question": self.is_question,
            "is_command": self.is_command,
            "word_count": self.word_count,
        }


@dataclass
class ArthaResult:
    """
    Result of Artha (Meaning) phase - Semantic interpretation.

    Maps raw tokens to actionable intents.
    """

    primary_intent: VedaIntent
    secondary_intents: List[VedaIntent]
    confidence: float  # 0.0 - 1.0
    handler_route: str  # Which handler should process this
    extracted_entities: Dict[str, Any]  # Named entities found
    context_hints: List[str]  # Hints for downstream processing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_intent": self.primary_intent.value,
            "secondary_intents": [i.value for i in self.secondary_intents],
            "confidence": self.confidence,
            "handler_route": self.handler_route,
            "extracted_entities": self.extracted_entities,
            "context_hints": self.context_hints,
        }


@dataclass
class PratyayaResult:
    """
    Result of Pratyaya (Trust) phase - Authorization check.

    Validates whether the action can proceed.
    """

    authorized: bool
    trust_level: VedaTrustLevel
    reason: Optional[str]  # Why blocked/allowed
    preconditions_met: bool
    system_ready: bool
    warnings: List[str]  # Non-blocking concerns

    def to_dict(self) -> Dict[str, Any]:
        return {
            "authorized": self.authorized,
            "trust_level": self.trust_level.value,
            "reason": self.reason,
            "preconditions_met": self.preconditions_met,
            "system_ready": self.system_ready,
            "warnings": self.warnings,
        }


@dataclass
class KarmaResult:
    """
    Result of Karma (Action) phase - Execution result.

    The final outcome of processing.
    """

    success: bool
    content: str
    error: Optional[str]
    execution_time_ms: float
    action_taken: str
    side_effects: List[str]  # What changed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "action_taken": self.action_taken,
            "side_effects": self.side_effects,
        }


@dataclass
class VedaContext:
    """
    Complete context passed through all four phases.

    This is the "sacred vessel" that carries data through the pipeline.
    """

    # Input
    original_message: Any  # SamvadaMessage

    # Phase results (populated as we progress)
    shabda: Optional[ShabdaResult] = None
    artha: Optional[ArthaResult] = None
    pratyaya: Optional[PratyayaResult] = None
    karma: Optional[KarmaResult] = None

    # Metadata
    pipeline_started: bool = False
    current_phase: str = "init"
    phase_history: List[str] = field(default_factory=list)

    def advance_to(self, phase: str) -> None:
        """Advance to the next phase."""
        self.phase_history.append(phase)
        self.current_phase = phase


# =============================================================================
# SECTION 2: SHABDA - The Word (Input Processing)
# =============================================================================


class Shabda:
    """
    Shabda (Das Wort) - Input Reception and Tokenization.

    The first phase: hearing and breaking down the raw input.
    No interpretation yet - just linguistic analysis.

    "First, the word must be heard clearly."
    """

    # German keywords for language detection
    GERMAN_INDICATORS = {
        "prüfe",
        "zeige",
        "was",
        "wie",
        "warum",
        "bitte",
        "hilfe",
        "der",
        "die",
        "das",
        "ist",
        "sind",
        "verstöße",
        "architektur",
        "status",
        "ja",
        "nein",
        "und",
        "oder",
        "für",
        "mit",
        "auf",
    }

    # Question indicators
    QUESTION_WORDS = {
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "which",
        "was",
        "warum",
        "wie",
        "wann",
        "wo",
        "wer",
        "welche",
    }

    # Command indicators
    COMMAND_WORDS = {
        "check",
        "run",
        "show",
        "list",
        "get",
        "start",
        "stop",
        "create",
        "delete",
        "update",
        "prüfe",
        "zeige",
        "liste",
        "starte",
        "stoppe",
        "erstelle",
        "lösche",
        "aktualisiere",
    }

    def process(self, raw_input: str) -> ShabdaResult:
        """
        Process raw input into tokens and keywords.

        Args:
            raw_input: The raw user input string

        Returns:
            ShabdaResult with linguistic analysis
        """
        logger.debug(f"SHABDA: Processing '{raw_input[:50]}...'")

        # Normalize
        normalized = raw_input.strip().lower()

        # Tokenize (simple word splitting, preserve hyphenated words)
        tokens = re.findall(r"[\w-]+", normalized)

        # Extract keywords (remove common stop words)
        stop_words = {"the", "a", "an", "is", "are", "to", "of", "in", "for", "and", "or"}
        keywords = {t for t in tokens if t not in stop_words and len(t) > 1}

        # Detect language
        language = self._detect_language(tokens)

        # Check if question
        is_question = "?" in raw_input or any(t in self.QUESTION_WORDS for t in tokens)

        # Check if command
        is_command = any(t in self.COMMAND_WORDS for t in tokens[:3])  # First 3 words

        return ShabdaResult(
            raw_input=raw_input,
            normalized=normalized,
            tokens=tokens,
            keywords=keywords,
            language=language,
            is_question=is_question,
            is_command=is_command,
            word_count=len(tokens),
        )

    def _detect_language(self, tokens: List[str]) -> VedaLanguage:
        """Detect the language of the input."""
        german_count = sum(1 for t in tokens if t in self.GERMAN_INDICATORS)

        if len(tokens) == 0:
            return VedaLanguage.UNKNOWN
        elif german_count >= len(tokens) * 0.3:
            return VedaLanguage.GERMAN
        elif german_count > 0:
            return VedaLanguage.MIXED
        else:
            return VedaLanguage.ENGLISH


# =============================================================================
# SECTION 3: ARTHA - The Meaning (Intent Extraction)
# =============================================================================


class Artha:
    """
    Artha (Die Bedeutung) - Semantic Meaning Extraction.

    The second phase: understanding what the words mean.
    Maps tokens to intents and determines routing.

    "Then, the meaning must be understood."
    """

    # Intent keyword mappings (multi-language)
    INTENT_KEYWORDS: Dict[VedaIntent, Set[str]] = {
        VedaIntent.STATUS: {"status", "health", "system", "gesundheit", "zustand"},
        VedaIntent.INTENTS: {"intents", "intent", "pending", "queue", "absichten"},
        VedaIntent.CAPABILITIES: {"capabilities", "capability", "fähigkeiten", "können"},
        VedaIntent.HELP: {"help", "hilfe", "?", "commands", "befehle"},
        VedaIntent.DRIFT: {
            "drift",
            "verstöße",
            "verstoße",
            "architektur-drift",
            "violations",
            "outlaws",
        },
        VedaIntent.ARCHITECTURE: {
            "architecture",
            "architektur",
            "struktur",
            "structure",
            "audit",
        },
        VedaIntent.COMPLIANCE: {"compliance", "score", "konformität", "dharma"},
        VedaIntent.MANDALA: {
            "mandala",
            "config",
            "konfiguration",
            "configuration",
            "agents",
            "cartridges",
            "capabilities",
        },
        VedaIntent.AKASHA: {
            "akasha",
            "knowledge",
            "wissen",
            "graph",
            "dependencies",
            "abhängigkeiten",
            "depends",
            "hängt",
            "constraints",
            "einschränkungen",
        },
        VedaIntent.KNOWLEDGE: {
            "what is",
            "was ist",
            "describe",
            "beschreibe",
        },
        VedaIntent.DEPENDENCIES: {
            "depends on",
            "abhängig von",
            "what depends",
            "was hängt ab",
        },
        VedaIntent.SILPA: {
            "silpa",
            "refactor",
            "refaktorieren",
            "umbau",
            "docstring",
            "rename",
            "extract",
            "consolidate",
        },
        VedaIntent.REFACTOR: {
            "refactor",
            "refaktoriere",
            "update docstring",
            "docstring aktualisieren",
        },
        VedaIntent.SUTRA: {
            "sutra",
            "wiki",
            "documentation",
            "dokumentation",
            "docs",
            "generate wiki",
            "update wiki",
            "sync wiki",
        },
        VedaIntent.WIKI: {
            "wiki",
            "preview wiki",
            "generate documentation",
            "pantheon",
            "law",
            "map",
        },
        VedaIntent.SANKALPA: {
            "sankalpa",
            "will",
            "vow",
            "goals",
            "ziele",
            "proactive",
            "proaktiv",
            "autonomous",
            "autonom",
        },
        VedaIntent.MISSIONS: {
            "missions",
            "missionen",
            "objectives",
            "list missions",
        },
        VedaIntent.STRATEGY: {
            "strategy",
            "strategie",
            "strategies",
            "plan",
        },
        VedaIntent.ACTION: {
            # English action verbs (state-changing)
            "run",
            "execute",
            "create",
            "delete",
            "update",
            "fix",
            "build",
            "start",
            "stop",
            "restart",
            "deploy",
            "migrate",
            # German action verbs (KRIYA integration)
            "ausführen",
            "erstelle",
            "lösche",
            "repariere",
            "starte",
            "stoppe",
            "baue",
            "führe",  # as in "führe durch"
        },
    }

    # Handler route mappings
    INTENT_ROUTES: Dict[VedaIntent, str] = {
        VedaIntent.STATUS: "_handle_status",
        VedaIntent.INTENTS: "_handle_intents",
        VedaIntent.CAPABILITIES: "_handle_capabilities",
        VedaIntent.HELP: "_handle_help",
        VedaIntent.DRIFT: "_handle_drift",
        VedaIntent.ARCHITECTURE: "_handle_drift",
        VedaIntent.COMPLIANCE: "_handle_drift",
        VedaIntent.MANDALA: "_handle_mandala",
        VedaIntent.AKASHA: "_handle_akasha",
        VedaIntent.KNOWLEDGE: "_handle_akasha",
        VedaIntent.DEPENDENCIES: "_handle_akasha",
        VedaIntent.SILPA: "_handle_silpa",
        VedaIntent.REFACTOR: "_handle_silpa",
        VedaIntent.SUTRA: "_handle_sutra",
        VedaIntent.WIKI: "_handle_sutra",
        VedaIntent.SANKALPA: "_handle_sankalpa",
        VedaIntent.MISSIONS: "_handle_sankalpa",
        VedaIntent.STRATEGY: "_handle_sankalpa",
        VedaIntent.ACTION: "_handle_action",
        VedaIntent.CHAT: "_handle_chat_llm",
        VedaIntent.UNKNOWN: "_handle_chat_llm",
    }

    def process(self, shabda: ShabdaResult) -> ArthaResult:
        """
        Extract semantic meaning from tokenized input.

        Args:
            shabda: Result from Shabda phase

        Returns:
            ArthaResult with intent and routing information
        """
        logger.debug(f"ARTHA: Interpreting keywords {shabda.keywords}")

        intents_found: List[tuple[VedaIntent, float]] = []

        # Score each intent based on keyword matches
        for intent, keywords in self.INTENT_KEYWORDS.items():
            matches = shabda.keywords & keywords
            if matches:
                score = len(matches) / len(keywords)
                intents_found.append((intent, score))

        # Sort by score
        intents_found.sort(key=lambda x: x[1], reverse=True)

        if intents_found:
            primary_intent = intents_found[0][0]
            confidence = intents_found[0][1]
            secondary_intents = [i[0] for i in intents_found[1:3]]
        else:
            # Default to chat for unrecognized inputs
            primary_intent = VedaIntent.CHAT
            confidence = 0.5
            secondary_intents = []

        # Determine route
        handler_route = self.INTENT_ROUTES.get(primary_intent, "_handle_chat_llm")

        # Extract entities (simple pattern matching for now)
        entities = self._extract_entities(shabda)

        # Generate context hints
        hints = self._generate_hints(shabda, primary_intent)

        return ArthaResult(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            handler_route=handler_route,
            extracted_entities=entities,
            context_hints=hints,
        )

    def _extract_entities(self, shabda: ShabdaResult) -> Dict[str, Any]:
        """Extract named entities from input."""
        entities: Dict[str, Any] = {}

        # Look for file paths
        path_pattern = r"[\w./\\-]+\.\w+"
        paths = re.findall(path_pattern, shabda.normalized)
        if paths:
            entities["paths"] = paths

        # Look for numbers
        numbers = re.findall(r"\d+", shabda.normalized)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]

        return entities

    def _generate_hints(self, shabda: ShabdaResult, intent: VedaIntent) -> List[str]:
        """Generate processing hints based on analysis."""
        hints = []

        if shabda.is_question:
            hints.append("user_expects_explanation")
        if shabda.is_command:
            hints.append("user_expects_action")
        if shabda.language == VedaLanguage.GERMAN:
            hints.append("respond_in_german")
        if intent in {VedaIntent.DRIFT, VedaIntent.ARCHITECTURE, VedaIntent.COMPLIANCE}:
            hints.append("dharma_context_needed")
        if intent in {VedaIntent.AKASHA, VedaIntent.KNOWLEDGE, VedaIntent.DEPENDENCIES}:
            hints.append("akasha_context_needed")
        if intent in {VedaIntent.SILPA, VedaIntent.REFACTOR}:
            hints.append("silpa_context_needed")
        if intent in {VedaIntent.SUTRA, VedaIntent.WIKI}:
            hints.append("sutra_context_needed")
        if intent in {VedaIntent.SANKALPA, VedaIntent.MISSIONS, VedaIntent.STRATEGY}:
            hints.append("sankalpa_context_needed")

        return hints


# =============================================================================
# SECTION 4: PRATYAYA - The Trust (Authorization)
# =============================================================================


class Pratyaya:
    """
    Pratyaya (Das Vertrauen) - Trust and Authorization Check.

    The third phase: validating that the action can proceed.
    Checks permissions, system state, and preconditions.

    "Trust must be established before action."
    """

    # Actions that require elevated trust
    # NOTE: ACTION (KRIYA) is intentionally NOT elevated because it only creates
    # intent proposals, it doesn't execute them. Actual execution requires
    # separate approval through the CognitiveKernel.
    ELEVATED_ACTIONS: Set[VedaIntent] = {
        # Reserved for future dangerous operations like:
        # VedaIntent.EXECUTE,  # Actually running commands
        # VedaIntent.DELETE,   # Deleting files
    }

    # Actions that require system readiness
    SYSTEM_REQUIRED: Set[VedaIntent] = {
        VedaIntent.STATUS,
        VedaIntent.DRIFT,
        VedaIntent.ARCHITECTURE,
        VedaIntent.COMPLIANCE,
    }

    def __init__(self, default_trust: VedaTrustLevel = VedaTrustLevel.USER):
        """Initialize with default trust level."""
        self._default_trust = default_trust
        self._system_ready = True  # Can be updated dynamically

    def set_system_ready(self, ready: bool) -> None:
        """Update system readiness state."""
        self._system_ready = ready

    def process(self, artha: ArthaResult, trust_level: Optional[VedaTrustLevel] = None) -> PratyayaResult:
        """
        Check authorization for the intended action.

        Args:
            artha: Result from Artha phase
            trust_level: Override trust level (default: USER)

        Returns:
            PratyayaResult with authorization decision
        """
        logger.debug(f"PRATYAYA: Checking trust for intent {artha.primary_intent}")

        effective_trust = trust_level or self._default_trust
        warnings: List[str] = []

        # Check elevated access requirements
        if artha.primary_intent in self.ELEVATED_ACTIONS:
            if effective_trust not in {VedaTrustLevel.SYSTEM, VedaTrustLevel.ADMIN}:
                return PratyayaResult(
                    authorized=False,
                    trust_level=effective_trust,
                    reason=f"Intent '{artha.primary_intent.value}' requires admin access",
                    preconditions_met=False,
                    system_ready=self._system_ready,
                    warnings=["elevated_access_required"],
                )

        # Check system readiness
        if artha.primary_intent in self.SYSTEM_REQUIRED and not self._system_ready:
            warnings.append("system_not_fully_ready")

        # Check for blocked trust
        if effective_trust == VedaTrustLevel.BLOCKED:
            return PratyayaResult(
                authorized=False,
                trust_level=effective_trust,
                reason="Access blocked",
                preconditions_met=False,
                system_ready=self._system_ready,
                warnings=["access_blocked"],
            )

        # Default: authorized
        return PratyayaResult(
            authorized=True,
            trust_level=effective_trust,
            reason="Access granted",
            preconditions_met=True,
            system_ready=self._system_ready,
            warnings=warnings,
        )


# =============================================================================
# SECTION 5: KARMA - The Action (Execution)
# =============================================================================


class Karma:
    """
    Karma (Die Handlung) - Action Execution.

    The fourth phase: performing the actual action.
    This is the culmination of the pipeline.

    "Finally, action must flow."
    """

    def __init__(self):
        """Initialize Karma executor."""
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, route: str, handler: Callable) -> None:
        """
        Register a handler for a route.

        Args:
            route: The handler route (e.g., "_handle_status")
            handler: Async callable that takes VedaContext
        """
        self._handlers[route] = handler
        logger.debug(f"KARMA: Registered handler for route '{route}'")

    def get_handler(self, route: str) -> Optional[Callable]:
        """Get handler for a route."""
        return self._handlers.get(route)

    async def execute(self, ctx: VedaContext) -> KarmaResult:
        """
        Execute the action based on pipeline context.

        Args:
            ctx: Full VedaContext with all phase results

        Returns:
            KarmaResult with execution outcome
        """
        import time

        start_time = time.time()

        if not ctx.artha:
            return KarmaResult(
                success=False,
                content="",
                error="No Artha result - meaning not extracted",
                execution_time_ms=0,
                action_taken="none",
                side_effects=[],
            )

        if not ctx.pratyaya or not ctx.pratyaya.authorized:
            reason = ctx.pratyaya.reason if ctx.pratyaya else "Authorization not checked"
            return KarmaResult(
                success=False,
                content="",
                error=f"Not authorized: {reason}",
                execution_time_ms=0,
                action_taken="blocked",
                side_effects=[],
            )

        route = ctx.artha.handler_route
        handler = self._handlers.get(route)

        if not handler:
            # Return a default result if no handler registered
            logger.warning(f"KARMA: No handler for route '{route}'")
            elapsed = (time.time() - start_time) * 1000

            return KarmaResult(
                success=False,
                content="",
                error=f"No handler registered for route '{route}'",
                execution_time_ms=elapsed,
                action_taken="none",
                side_effects=[],
            )

        try:
            logger.debug(f"KARMA: Executing handler '{route}'")
            result = await handler(ctx)
            elapsed = (time.time() - start_time) * 1000

            return KarmaResult(
                success=True,
                content=result if isinstance(result, str) else str(result),
                error=None,
                execution_time_ms=elapsed,
                action_taken=route,
                side_effects=[],
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"KARMA: Handler '{route}' failed: {e}")

            return KarmaResult(
                success=False,
                content="",
                error=str(e),
                execution_time_ms=elapsed,
                action_taken=f"{route}_failed",
                side_effects=[],
            )


# =============================================================================
# SECTION 6: VEDA PIPELINE - The Sacred Conductor
# =============================================================================


class VedaPipeline:
    """
    The Four-Fold Processing Pipeline.

    Orchestrates Shabda → Artha → Pratyaya → Karma in perfect sequence.

    Usage:
        pipeline = VedaPipeline()
        pipeline.karma.register_handler("_handle_status", my_status_handler)
        result = await pipeline.process(message)
    """

    def __init__(self, default_trust: VedaTrustLevel = VedaTrustLevel.USER):
        """
        Initialize the VEDA pipeline.

        Args:
            default_trust: Default trust level for authorization
        """
        self.shabda = Shabda()
        self.artha = Artha()
        self.pratyaya = Pratyaya(default_trust=default_trust)
        self.karma = Karma()

        logger.info("🕉️ VEDA Pipeline initialized")

    async def process(
        self,
        message: Any,
        trust_level: Optional[VedaTrustLevel] = None,
    ) -> VedaContext:
        """
        Process a message through all four phases.

        Args:
            message: The input message (must have .content attribute)
            trust_level: Optional trust level override

        Returns:
            VedaContext with all phase results
        """
        logger.info("🕉️ VEDA: Beginning four-fold processing")

        ctx = VedaContext(original_message=message)
        ctx.pipeline_started = True

        # Phase 1: SHABDA (Das Wort)
        ctx.advance_to("shabda")
        content = message.content if hasattr(message, "content") else str(message)
        ctx.shabda = self.shabda.process(content)
        logger.debug(f"SHABDA complete: {len(ctx.shabda.tokens)} tokens")

        # Phase 2: ARTHA (Die Bedeutung)
        ctx.advance_to("artha")
        ctx.artha = self.artha.process(ctx.shabda)
        logger.debug(f"ARTHA complete: intent={ctx.artha.primary_intent.value}")

        # Phase 3: PRATYAYA (Das Vertrauen)
        ctx.advance_to("pratyaya")
        ctx.pratyaya = self.pratyaya.process(ctx.artha, trust_level)
        logger.debug(f"PRATYAYA complete: authorized={ctx.pratyaya.authorized}")

        # Phase 4: KARMA (Die Handlung)
        ctx.advance_to("karma")
        ctx.karma = await self.karma.execute(ctx)
        logger.debug(f"KARMA complete: success={ctx.karma.success}")

        logger.info(f"🕉️ VEDA: Processing complete ({ctx.karma.execution_time_ms:.1f}ms)")
        return ctx

    def process_shabda_only(self, content: str) -> ShabdaResult:
        """Process only the Shabda phase (for testing/debugging)."""
        return self.shabda.process(content)

    def process_artha_only(self, shabda: ShabdaResult) -> ArthaResult:
        """Process only the Artha phase (for testing/debugging)."""
        return self.artha.process(shabda)
