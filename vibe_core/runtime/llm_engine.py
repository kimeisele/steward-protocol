"""
🧠 LLM ENGINE (GAD-6000: NEURO-SYMBOLIC FUSION)
The Voice of Agent City.

REFACTORED: Now delegates to providers/ (GAD-511 Neural Adapter Strategy).
This file is a THIN WRAPPER for backwards compatibility.

Single Source of Truth: vibe_core/runtime/providers/
"""

import logging
import os
from typing import Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import LLMProtocol

logger = logging.getLogger("LLM_ENGINE")


class LLMEngine(LLMProtocol):
    """
    🧠 Neuro-Symbolic Bridge (THIN WRAPPER)

    REFACTORED: All LLM calls now delegate to providers/factory.
    This class exists for backwards compatibility with 16 legacy users.

    Serves two primary functions:
    1. Conversational: speak() for agent personality responses (mock/templates)
    2. Code Generation: generate_code() -> delegates to providers/
    """

    def __init__(self):
        """Initialize LLM Engine. Provider detection delegated to factory."""
        # Keep env detection for backwards compat logging
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        # Provider detection now handled by factory
        from vibe_core.runtime.providers.factory import _detect_provider

        self.provider = os.getenv("LLM_PROVIDER", "").lower() or _detect_provider()
        self.model = os.getenv("LLM_MODEL", "")
        self.base_url = os.getenv("LLM_BASE_URL")

        # Internal provider instance (lazy loaded)
        self._provider_instance = None

        if self.provider == "mock" or not self.api_key:
            logger.warning("⚠️  NO API KEY FOUND. Running in MOCK MODE.")
        else:
            logger.info(f"🧠 LLM Engine initialized (Provider: {self.provider})")

    def _get_provider(self):
        """Lazy load provider from factory (Single Source of Truth)."""
        if self._provider_instance is None:
            from vibe_core.runtime.providers.factory import create_provider

            try:
                self._provider_instance = create_provider(
                    provider_name=self.provider if self.provider != "mock" else None,
                    model_name=self.model if self.model else None,
                )
            except Exception as e:
                logger.warning(f"⚠️  Could not create provider: {e}")
                self._provider_instance = None

        return self._provider_instance

    # ===== CONVERSATIONAL INTERFACE (Agent Persona) =====
    # These are mock/template responses - no LLM calls needed

    def speak(self, agent_name: str, context: str, user_input: str) -> str:
        """Generate a conversational response based on agent persona."""
        return self._generate_response(agent_name, context, user_input)

    def _generate_response(self, agent_name: str, context: str, user_input: str) -> str:
        """Generate a synthetic response (deterministic templates)."""
        agent_upper = agent_name.upper()

        if "governance" in context.lower() or "action" in context.lower():
            return self._response_action(agent_upper, user_input)
        elif "creation" in context.lower() or "content" in context.lower():
            return self._response_creation(agent_upper, user_input)
        elif "query" in context.lower() or "briefing" in context.lower():
            return self._response_query(agent_upper, user_input)
        else:
            return self._response_default(agent_upper, user_input)

    def _response_action(self, agent: str, user_input: str) -> str:
        return (
            f"**🤖 {agent}:** Acknowledged. I'm executing the governance action.\n\n"
            f"*Your request:* `{user_input}`\n\n"
            f"Processing through deterministic routing engine."
        )

    def _response_creation(self, agent: str, user_input: str) -> str:
        return (
            f"**🤖 {agent}:** Creative engine activated.\n\n"
            f"*Brief:* `{user_input}`\n\n"
            f"Synthesizing across knowledge graphs."
        )

    def _response_query(self, agent: str, user_input: str) -> str:
        return (
            f"**🤖 {agent}:** Intelligence briefing compiled.\n\n"
            f"*Your question:* `{user_input}`\n\n"
            f"Drawing from real-time ledger state."
        )

    def _response_default(self, agent: str, user_input: str) -> str:
        return (
            f"**🤖 {agent}:** Signal received.\n\n"
            f"*You said:* `{user_input}`\n\n"
            f"Analyzing intent against knowledge graph."
        )

    # ===== CODE GENERATION INTERFACE =====
    # REFACTORED: Delegates to providers/factory (Single Source of Truth)

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate code based on a feature specification.

        REFACTORED: Now delegates to providers/factory instead of
        maintaining parallel _call_* implementations.
        """
        if not system_prompt:
            system_prompt = (
                "You are an Expert Senior Software Engineer. "
                "Generate production-ready, clean Python code. "
                "Include type hints and docstrings. "
                "Output ONLY valid Python code, no markdown formatting."
            )

        logger.info(f"🧠 Generating code (provider: {self.provider})...")

        # Mock mode fallback
        if self.provider == "mock" or not self.api_key:
            return self._call_mock(prompt)

        # DELEGATION: Use providers/factory (Single Source of Truth)
        provider = self._get_provider()
        if provider is None:
            logger.warning("⚠️  No provider available, falling back to mock")
            return self._call_mock(prompt)

        try:
            response = provider.invoke(
                prompt=prompt,
                system_prompt=system_prompt,
                model=self.model if self.model else None,
            )
            return self._clean_output(response.content)

        except Exception as e:
            logger.error(f"❌ Provider call failed: {e}")
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

    def _call_mock(self, prompt: str) -> str:
        """Mock code generation - returns error message, NOT fake code."""
        logger.warning("⚠️  LLM ENGINE: No API key - cannot generate code")

        return f"""# ============================================================
# ERROR: LLM CODE GENERATION FAILED
# ============================================================
# Reason: No LLM API key configured
#
# To enable code generation, set one of these environment variables:
#   - ANTHROPIC_API_KEY
#   - OPENROUTER_API_KEY
#   - OPENAI_API_KEY
#
# Original prompt (truncated):
# {prompt[:100]}...
# ============================================================

raise NotImplementedError(
    "LLM code generation is not available. "
    "Configure an API key to enable this feature."
)
"""

    def _clean_output(self, content: str) -> str:
        """Strips markdown code blocks from LLM output."""
        if not content:
            return ""
        return content.replace("```python", "").replace("```", "").strip()


# Singleton instance for module-level access
llm = LLMEngine()

# Register in DI container
ServiceRegistry.register(LLMProtocol, llm)

logger.info(f"🧠 LLM Engine initialized (Provider: {llm.provider})")


# ===== PUBLIC API CONVENIENCE FUNCTION =====
def ask_cortex(prompt: str, system_prompt: str = None) -> str:
    """
    Public API: Ask the Cortex (LLM Engine) for code generation.
    Delegates to providers/ via LLMEngine wrapper.
    """
    return llm.generate_code(prompt, system_prompt)
