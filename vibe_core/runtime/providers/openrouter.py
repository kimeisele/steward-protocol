#!/usr/bin/env python3
"""
GAD-511: OpenRouter Provider Implementation
============================================

Concrete implementation of LLMProvider for OpenRouter.
OpenRouter provides access to multiple LLM providers through a unified API.

Features:
- OpenAI-compatible API (uses openai SDK with custom base_url)
- Multi-model support (Anthropic, OpenAI, Google, etc. via OpenRouter)
- Cost calculation based on OpenRouter pricing
- Retry logic with exponential backoff

Version: 1.0 (GAD-511 Phase 2)
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import (
    LLMProvider,
    LLMResponse,
    LLMUsage,
    ProviderInvocationError,
    ProviderNotAvailableError,
)

logger = logging.getLogger(__name__)

# OpenRouter base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter provider implementation.

    OpenRouter provides unified access to multiple LLM providers
    through an OpenAI-compatible API interface.
    """

    # Approximate pricing table (USD per million tokens)
    # See: https://openrouter.ai/models for current pricing
    # Updated: 2025-12-14
    PRICING = {
        # Anthropic models via OpenRouter (2025)
        "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0},  # Premium reasoning
        "anthropic/claude-sonnet-4": {"input": 3.0, "output": 15.0},  # Balanced
        "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},  # Legacy
        "anthropic/claude-3.5-haiku": {"input": 0.80, "output": 4.0},  # Fast & cheap
        "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},  # Legacy
        # OpenAI models via OpenRouter
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "openai/gpt-4o": {"input": 5.0, "output": 15.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        # Google models via OpenRouter
        "google/gemini-pro": {"input": 0.5, "output": 1.5},
        "google/gemini-flash-1.5": {"input": 0.075, "output": 0.3},
        # Meta models via OpenRouter
        "meta-llama/llama-3.1-70b-instruct": {"input": 0.52, "output": 0.75},
        "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
        # Default fallback pricing
        "default": {"input": 1.0, "output": 3.0},
    }

    def __init__(self, api_key: str | None = None, **kwargs: Any):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            **kwargs: Additional configuration

        Raises:
            ProviderNotAvailableError: If openai package not installed or API key invalid
        """
        self.api_key = api_key

        if not self.api_key:
            raise ProviderNotAvailableError("OpenRouter API key required. Set OPENROUTER_API_KEY environment variable.")

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=OPENROUTER_BASE_URL,
            )
            logger.info("OpenRouter provider initialized successfully")
        except ImportError as e:
            raise ProviderNotAvailableError(
                "openai package not installed. Install with: pip install openai>=1.0.0"
            ) from e
        except Exception as e:
            raise ProviderNotAvailableError(f"Failed to initialize OpenRouter client: {e}") from e

    def invoke(
        self,
        prompt: str = "",
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        max_retries: int = 3,
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Invoke model via OpenRouter.

        Args:
            prompt: Input prompt (used if messages not provided)
            model: OpenRouter model identifier (e.g., "anthropic/claude-3.5-sonnet")
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            max_retries: Maximum retry attempts
            messages: Optional list of message dicts (native format, preferred)
            **kwargs: Additional OpenAI-compatible parameters

        Returns:
            LLMResponse with content and usage

        Raises:
            ProviderInvocationError: If all retries fail
        """
        # Use native messages if provided, otherwise wrap prompt
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages,
                    **kwargs,
                )

                # Extract usage (may be None for some models)
                input_tokens = response.usage.prompt_tokens if response.usage else 0
                output_tokens = response.usage.completion_tokens if response.usage else 0

                # Calculate cost
                cost = self.calculate_cost(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model=model,
                )

                # Create usage record
                usage = LLMUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model=model,
                    cost_usd=cost,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )

                # Log success
                logger.info(
                    f"OpenRouter invocation successful: {model} "
                    f"(in: {usage.input_tokens}, out: {usage.output_tokens}, "
                    f"cost: ${usage.cost_usd:.4f})"
                )

                # Return standardized response
                content = response.choices[0].message.content if response.choices else ""
                finish_reason = response.choices[0].finish_reason if response.choices else "unknown"

                return LLMResponse(
                    content=content or "",
                    usage=usage,
                    model=model,
                    finish_reason=finish_reason or "unknown",
                    provider="openrouter",
                )

            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Check if retryable error
                retryable_errors = [
                    "RateLimitError",
                    "APIConnectionError",
                    "APITimeoutError",
                    "ServiceUnavailableError",
                ]
                is_retryable = any(err in error_name for err in retryable_errors)

                if is_retryable and attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2**attempt
                    logger.warning(
                        f"OpenRouter invocation failed ({error_name}), "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    # Non-retryable error or max retries reached
                    logger.error(f"OpenRouter invocation failed: {error_name} - {e!s}")
                    break

        # All retries failed
        raise ProviderInvocationError(
            f"OpenRouter invocation failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__} - {last_error!s}"
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost based on OpenRouter pricing.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Cost in USD
        """
        if model in self.PRICING:
            pricing = self.PRICING[model]
        else:
            logger.warning(f"Unknown OpenRouter model pricing: {model}, using defaults")
            pricing = self.PRICING["default"]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_available_models(self) -> list[str]:
        """Get list of commonly used OpenRouter models"""
        return [k for k in self.PRICING.keys() if k != "default"]

    def is_available(self) -> bool:
        """Check if OpenRouter provider is available"""
        return self.api_key is not None and self.client is not None
