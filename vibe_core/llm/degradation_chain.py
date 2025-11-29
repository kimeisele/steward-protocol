"""
Graceful Degradation Chain for Offline Operation.

Fallback order:
1. SemanticRouter (>0.85 confidence) -> Direct execution
2. SemanticRouter (0.60-0.85) -> Execute with clarification
3. LocalLLM (if available) -> Generate response
4. Templates (always available) -> Static response
5. Error with guidance -> Tell user what to install
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set

logger = logging.getLogger("DEGRADATION_CHAIN")


class DegradationLevel(Enum):
    """Current system capability level."""

    FULL = "full"  # Local LLM available
    TEMPLATES = "templates"  # Only templates available
    MINIMAL = "minimal"  # Nothing available


@dataclass
class DegradationResponse:
    """Response with degradation metadata."""

    content: str
    level: DegradationLevel
    confidence: float
    fallback_used: str
    user_guidance: Optional[str] = None


class DegradationChain:
    """
    Manages graceful degradation when LLM is unavailable.

    Usage:
        chain = DegradationChain()
        response = chain.respond(user_input, semantic_confidence)
    """

    def __init__(self):
        self._local_llm = None
        self._templates = self._load_templates()
        self._level = self._detect_level()
        logger.info(f"DegradationChain initialized (level: {self._level.value})")

    def _detect_level(self) -> DegradationLevel:
        """Detect current system capability."""
        try:
            from vibe_core.llm.local_llama_provider import LocalLlamaProvider

            if LocalLlamaProvider.model_exists():
                self._local_llm = LocalLlamaProvider()
                if self._local_llm.is_available:
                    return DegradationLevel.FULL
        except ImportError:
            logger.debug("LocalLlamaProvider not available (not installed)")
        except Exception as e:
            logger.warning(f"Local LLM check failed: {e}")

        if self._templates:
            return DegradationLevel.TEMPLATES

        return DegradationLevel.MINIMAL

    def _load_templates(self) -> Dict[str, str]:
        """Load response templates."""
        return {
            "greeting": "Willkommen in Agent City. Ich bin bereit zu helfen.",
            "status": "Agent City ist online. Alle Systeme nominal.",
            "unknown": "Ich verstehe deine Anfrage. Bitte sei spezifischer.",
            "error": "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
            "no_llm": ("Kein lokales LLM installiert. Fuer bessere Antworten: steward install-llm"),
        }

    def respond(
        self,
        user_input: str,
        semantic_confidence: float,
        detected_intent: Optional[str] = None,
        concepts: Optional[Set[str]] = None,
    ) -> DegradationResponse:
        """Generate response with graceful degradation."""

        # SATYA (>0.85): High confidence
        if semantic_confidence >= 0.85:
            return DegradationResponse(
                content="[SATYA: Direct execution by SemanticRouter]",
                level=self._level,
                confidence=semantic_confidence,
                fallback_used="none",
            )

        # MANTHAN (0.60-0.85): Medium confidence
        if semantic_confidence >= 0.60:
            clarification = self._generate_clarification(user_input, detected_intent)
            return DegradationResponse(
                content=clarification,
                level=self._level,
                confidence=semantic_confidence,
                fallback_used="clarification",
            )

        # NETI NETI (<0.60): Low confidence
        return self._neti_neti_fallback(user_input, semantic_confidence, concepts)

    def _generate_clarification(self, user_input: str, intent: Optional[str]) -> str:
        """Generate clarification request."""
        if intent:
            return f"Ich glaube du meinst '{intent}'. Kannst du das bestaetigen?"
        return f"Ich verstehe: '{user_input[:50]}...'. Was genau soll ich tun?"

    def _neti_neti_fallback(
        self, user_input: str, confidence: float, concepts: Optional[Set[str]] = None
    ) -> DegradationResponse:
        """NETI NETI fallback chain."""

        # Get knowledge context
        knowledge_context = ""
        if concepts:
            try:
                from vibe_core.knowledge.resolver import get_resolver

                resolver = get_resolver()
                for concept in concepts:
                    knowledge_context += resolver.compile_context(concept) + "\n\n"
            except Exception as e:
                logger.debug(f"Knowledge compilation failed: {e}")

        # Try LocalLLM with knowledge
        if self._local_llm is not None:
            try:
                compiled_prompt = self._compile_prompt(user_input, knowledge_context)
                response = self._local_llm.chat([{"role": "system", "content": compiled_prompt}])
                return DegradationResponse(
                    content=response,
                    level=DegradationLevel.FULL,
                    confidence=confidence,
                    fallback_used="local_llm_with_knowledge" if knowledge_context else "local_llm",
                )
            except Exception as e:
                logger.warning(f"LocalLLM failed: {e}")

        # Try Templates
        template_key = self._match_template(user_input)
        if template_key:
            content = self._templates[template_key]
            if self._level != DegradationLevel.FULL:
                content += "\n\n" + self._templates["no_llm"]

            return DegradationResponse(
                content=content,
                level=self._level,
                confidence=confidence,
                fallback_used=f"template:{template_key}",
                user_guidance="Fuer intelligentere Antworten: steward install-llm",
            )

        # Last resort
        return DegradationResponse(
            content=self._templates["unknown"] + "\n\n" + self._templates["no_llm"],
            level=DegradationLevel.MINIMAL,
            confidence=confidence,
            fallback_used="template:unknown",
            user_guidance="Fuer intelligentere Antworten: steward install-llm",
        )

    def _compile_prompt(self, user_input: str, knowledge: str) -> str:
        """Compile prompt with knowledge context for local LLM."""
        if knowledge:
            return f"""Du bist ein Agent in Agent City.

{knowledge}

AUFGABE: Beantworte die folgende Anfrage basierend auf dem obigen Wissen.
Wenn das Wissen nicht ausreicht, sage es ehrlich.

USER: {user_input}

ANTWORT:"""
        else:
            return user_input

    def _match_template(self, user_input: str) -> Optional[str]:
        """Simple keyword matching."""
        lower = user_input.lower()

        if any(w in lower for w in ["hallo", "hi", "hey", "guten"]):
            return "greeting"
        if any(w in lower for w in ["status", "health", "alive"]):
            return "status"

        return "unknown"

    @property
    def current_level(self) -> DegradationLevel:
        return self._level

    def get_status(self) -> Dict[str, Any]:
        """Get status for introspection."""
        return {
            "level": self._level.value,
            "local_llm_available": self._local_llm is not None,
            "templates_loaded": len(self._templates),
        }
