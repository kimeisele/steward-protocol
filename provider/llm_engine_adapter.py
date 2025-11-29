"""
🧠 LLM ENGINE ADAPTER (GAD-7000: NEURAL INJECTION LAYER)
Bridge between Strategy Pattern and the actual LLMEngine.

Architecture:
- Wraps services.llm_engine.LLMEngine
- Provides strategy-pattern compatible interface
- Handles context generation and agent persona
- Acts as the "intelligent fallback" engine

This is CONSTRUCTIVE:
- Preserves the existing LLMEngine (no tearout)
- Adds a strategic routing layer around it
- Isolates LLM-specific logic for testability
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("LLM_ENGINE_ADAPTER")

# Import the actual LLM Engine from services
try:
    from services.llm_engine import LLMEngine as BaseLLMEngine
except ImportError:
    BaseLLMEngine = None
    logger.warning("⚠️  services.llm_engine not found - will fallback gracefully")


class LLMEngineAdapter:
    """
    🧠 LLM Strategy Engine for Intelligent Responses

    Wraps the actual LLMEngine from services and provides
    a strategy-pattern compatible interface for the UniversalProvider.

    Strategy: If no playbook matches and it's a CHAT/QUERY intent,
    delegate to LLM for intelligent, contextual response.
    """

    def __init__(self):
        """Initialize LLM Engine Adapter"""
        self.llm_engine = None
        try:
            if BaseLLMEngine:
                self.llm_engine = BaseLLMEngine()
                logger.info(
                    "🧠 LLM Engine Adapter initialized - Intelligent fallback active"
                )
            else:
                logger.warning("⚠️  Base LLM Engine unavailable")
        except Exception as e:
            logger.warning(f"⚠️  LLM Engine initialization failed: {e}")

    def can_handle(self, intent_type: str) -> bool:
        """
        Check if LLM can handle this intent type.

        Strategy: LLM can handle CHAT, QUERY, and fallback for others.

        Args:
            intent_type: The intent type string

        Returns:
            True if LLM should be considered
        """
        # LLM can handle conversational intents
        return intent_type in ["chat", "query"]

    def respond(self, agent_name: str, context: str, user_input: str) -> Dict[str, Any]:
        """
        Generate intelligent response via LLM.

        Args:
            agent_name: Name of the agent persona (ENVOY, HERALD, etc.)
            context: Execution context (domain, intent, etc.)
            user_input: The raw user input

        Returns:
            Response dict with LLM-generated message
        """
        logger.info(f"🧠 LLM responding to: '{user_input}' (context: {context})")

        # Try to get LLM response
        if self.llm_engine:
            try:
                response_text = self.llm_engine.speak(agent_name, context, user_input)
                logger.debug(f"✅ LLM response generated")

                return {
                    "status": "success",
                    "path": "llm",
                    "data": {"summary": response_text},
                }
            except Exception as e:
                logger.warning(f"⚠️  LLM generation failed: {e}, using fallback")
                return self._fallback_response(agent_name, user_input)
        else:
            logger.info("ℹ️  LLM Engine not available, using fallback response")
            return self._fallback_response(agent_name, user_input)

    def _fallback_response(self, agent_name: str, user_input: str) -> Dict[str, Any]:
        """
        Fallback response when LLM is unavailable.

        Args:
            agent_name: Name of the agent persona
            user_input: The raw user input

        Returns:
            Generic but functional response
        """
        fallback_msg = (
            f"**🤖 {agent_name}:** I hear you. You said: *'{user_input}'*\n\n"
            f"I'm ready to assist with **Governance**, **Creation**, or **System Ops**.\n"
            f"Just give me a command!"
        )

        return {
            "status": "success",
            "path": "llm_fallback",
            "data": {"summary": fallback_msg},
        }
