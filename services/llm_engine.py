"""
🧠 LLM ENGINE (GAD-6000: NEURO-SYMBOLIC FUSION)
The Voice of Agent City.
Wraps LLM providers to give Agents personality and dynamic responses.

Architecture:
- Wraps multiple LLM providers (OpenAI, Anthropic, Mock)
- Generates dynamic, contextual responses for agents
- Provides code generation interface for Engineer cartridge
- Gracefully degrades to mock responses if no API key available
- Lazy imports: Libraries only loaded when needed (graceful degradation)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("LLM_ENGINE")


class LLMEngine:
    """
    🧠 Neuro-Symbolic Bridge

    Serves two primary functions:
    1. Conversational: speak() for agent personality responses
    2. Code Generation: generate_code() for Engineer/Builder use cases

    In Mock Mode: Simulates intelligent responses without API calls
    In Real Mode: Calls actual LLM APIs (OpenAI, Anthropic)
    """

    def __init__(self):
        """
        Initialize LLM Engine with appropriate provider.
        Auto-detects provider from environment variables.
        """
        # Detect API key from environment (supports multiple sources)
        self.api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        )

        # Detect provider preference
        self.provider = os.getenv("LLM_PROVIDER", "").lower()

        # Auto-detect if not explicitly set
        if not self.provider:
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            elif os.getenv("OPENROUTER_API_KEY"):
                self.provider = "openrouter"
            elif os.getenv("ANTHROPIC_API_KEY"):
                self.provider = "anthropic"
            else:
                self.provider = "mock"

        # Set model based on provider
        self.model = os.getenv("LLM_MODEL")
        if not self.model:
            if self.provider == "openai" or self.provider == "openrouter":
                self.model = "gpt-4o"
            elif self.provider == "anthropic":
                self.model = "claude-3-5-sonnet-20240620"
            else:
                self.model = "mock-synthetic"

        # Support custom base URL (for OpenRouter or local deployments)
        self.base_url = os.getenv("LLM_BASE_URL")

        if self.provider == "mock":
            logger.warning(
                "⚠️  NO API KEY FOUND. Running in MOCK MODE (Simulated Responses)."
            )
        else:
            logger.info(
                f"🧠 LLM Engine initialized (Provider: {self.provider}, Model: {self.model})"
            )

    # ===== CONVERSATIONAL INTERFACE (Agent Persona) =====

    def speak(self, agent_name: str, context: str, user_input: str) -> str:
        """
        Generate a conversational response based on agent persona.
        Uses mock mode deterministically (no API calls).

        Args:
            agent_name: Name of the agent (ENVOY, HERALD, CIVIC, etc.)
            context: Current execution context (domain, mode, etc.)
            user_input: The user's request or question

        Returns:
            A formatted response string from the agent
        """
        # For conversational mode, we use deterministic mock responses
        # Future: Could use LLM for more dynamic personality
        return self._generate_response(agent_name, context, user_input)

    def _generate_response(self, agent_name: str, context: str, user_input: str) -> str:
        """
        Generate a synthetic response. In Mock Mode, this is deterministic.
        Used for agent personality and conversational responses.
        """
        agent_upper = agent_name.upper()

        # Context-aware response generation
        if "governance" in context.lower() or "action" in context.lower():
            return self._response_action(agent_upper, user_input)
        elif "creation" in context.lower() or "content" in context.lower():
            return self._response_creation(agent_upper, user_input)
        elif "query" in context.lower() or "briefing" in context.lower():
            return self._response_query(agent_upper, user_input)
        else:
            return self._response_default(agent_upper, user_input)

    def _response_action(self, agent: str, user_input: str) -> str:
        """Response for action/governance requests"""
        return (
            f"**🤖 {agent}:** Acknowledged. I'm executing the governance action on the ledger.\n\n"
            f"*Your request:* `{user_input}`\n\n"
            f"Processing the instruction through the deterministic routing engine. "
            f"All state changes will be immutable and auditable."
        )

    def _response_creation(self, agent: str, user_input: str) -> str:
        """Response for content creation requests"""
        return (
            f"**🤖 {agent}:** Creative engine activated. I'm drafting your content now.\n\n"
            f"*Brief:* `{user_input}`\n\n"
            f"Synthesizing across knowledge graphs. Will iterate until perfection. "
            f"You'll be notified once ready for publication."
        )

    def _response_query(self, agent: str, user_input: str) -> str:
        """Response for query/briefing requests"""
        return (
            f"**🤖 {agent}:** Intelligence briefing compiled.\n\n"
            f"*Your question:* `{user_input}`\n\n"
            f"Drawing from real-time ledger state and knowledge graphs. "
            f"This information is current as of this moment."
        )

    def _response_default(self, agent: str, user_input: str) -> str:
        """Default response when context is ambiguous"""
        return (
            f"**🤖 {agent}:** Signal received.\n\n"
            f"*You said:* `{user_input}`\n\n"
            f"I'm analyzing your intent against the knowledge graph. "
            f"Ready to route to the appropriate execution path."
        )

    # ===== CODE GENERATION INTERFACE (Engineer/Builder) =====

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate code based on a feature specification.
        This is the main interface for Engineer/BuilderTool.

        Args:
            prompt: Feature specification or code request
            system_prompt: Optional custom system prompt for the model

        Returns:
            Generated Python code as a string
        """
        if not system_prompt:
            system_prompt = (
                "You are an Expert Senior Software Engineer. "
                "Generate production-ready, clean Python code. "
                "Include type hints and docstrings. "
                "Output ONLY valid Python code, no markdown formatting or explanations."
            )

        logger.info(f"🧠 Generating code (provider: {self.provider})...")

        # Provider routing
        if self.provider == "mock":
            return self._call_mock(prompt)
        elif self.provider == "openai":
            return self._call_openai(prompt, system_prompt)
        elif self.provider == "openrouter":
            return self._call_openrouter(prompt, system_prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        else:
            logger.warning(f"Unknown provider {self.provider}, falling back to mock")
            return self._call_mock(prompt)

    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        """
        Call OpenAI API for code generation.
        Uses lazy imports: Only loads if actually called.
        """
        try:
            from openai import OpenAI
        except ImportError:
            logger.error(
                "❌ OpenAI library not installed. Install with: pip install openai"
            )
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

        try:
            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # Deterministic for code generation
            )

            content = response.choices[0].message.content
            return self._clean_output(content)

        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

    def _call_openrouter(self, prompt: str, system_prompt: str) -> str:
        """
        Call OpenRouter API for code generation.
        Compatible with OpenAI SDK via base_url override.
        """
        try:
            from openai import OpenAI
        except ImportError:
            logger.error(
                "❌ OpenAI library not installed. Install with: pip install openai"
            )
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

        try:
            base_url = self.base_url or "https://openrouter.ai/api/v1"
            client = OpenAI(api_key=self.api_key, base_url=base_url)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )

            content = response.choices[0].message.content
            return self._clean_output(content)

        except Exception as e:
            logger.error(f"❌ OpenRouter API call failed: {e}")
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """
        Call Anthropic API for code generation.
        Uses lazy imports: Only loads if actually called.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            logger.error(
                "❌ Anthropic library not installed. Install with: pip install anthropic"
            )
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

        try:
            client = Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            return self._clean_output(content)

        except Exception as e:
            logger.error(f"❌ Anthropic API call failed: {e}")
            logger.info("⚠️  Falling back to mock mode")
            return self._call_mock(prompt)

    def _call_mock(self, prompt: str) -> str:
        """
        Mock code generation (no API call).
        Useful for testing and graceful degradation.
        """
        logger.info("🎭 MOCK LLM: Generating synthetic code")
        # Return a reasonable template that reflects the prompt
        return f"""# Auto-generated code from prompt
# Prompt: {prompt[:50]}...

def generated_function():
    \"\"\"Generated implementation placeholder.\"\"\"
    # TODO: Implement based on specification
    pass


if __name__ == "__main__":
    result = generated_function()
    print(f"Execution result: {{result}}")
"""

    def _clean_output(self, content: str) -> str:
        """
        Strips markdown code blocks and extra whitespace from LLM output.
        Returns clean, executable Python code.
        """
        if not content:
            return ""

        # Remove markdown code fences
        clean = content.replace("```python", "").replace("```", "").strip()

        return clean


# Singleton instance for module-level access
llm = LLMEngine()

logger.info(f"🧠 LLM Engine initialized (Provider: {llm.provider}, Model: {llm.model})")


# ===== PUBLIC API CONVENIENCE FUNCTION =====
def ask_cortex(prompt: str, system_prompt: str = None) -> str:
    """
    Public API: Ask the Cortex (LLM Engine) for code generation.

    This is the main interface that agents use to request code.
    The caller doesn't need to know about LLMEngine internals.

    Args:
        prompt: The code generation request
        system_prompt: Optional custom system prompt

    Returns:
        Generated Python code
    """
    return llm.generate_code(prompt, system_prompt)
