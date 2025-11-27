#!/usr/bin/env python3
"""
GAD-511: Anthropic Provider Implementation
===========================================

Concrete implementation of LLMProvider for Anthropic's Claude models.

Features:
- Claude 3.5 Sonnet support
- Cost calculation based on Anthropic pricing
- Retry logic with exponential backoff
- API key validation

Pricing (as of 2025-01-29):
- Claude 3.5 Sonnet: $3/MTok input, $15/MTok output

Version: 1.0 (GAD-511)
"""

import logging
import time
from datetime import datetime
from typing import Any

from .base import (
    LLMProvider,
    LLMResponse,
    LLMUsage,
    ProviderInvocationError,
    ProviderNotAvailableError,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider implementation.

    Supports Claude 3.5 Sonnet and future Claude models.
    Handles API communication, retries, and cost calculation.
    """

    # Pricing table (USD per million tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20250129": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-latest": {"input": 3.0, "output": 15.0},
    }

    def __init__(self, api_key: str | None = None, **kwargs: Any):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            **kwargs: Additional configuration (unused for now)

        Raises:
            ProviderNotAvailableError: If anthropic package not installed or API key invalid
        """
        self.api_key = api_key

        if not self.api_key:
            raise ProviderNotAvailableError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
            )

        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key)
            logger.info("Anthropic provider initialized successfully")
        except ImportError as e:
            raise ProviderNotAvailableError(
                "anthropic package not installed. Install with: pip install anthropic>=0.18.0"
            ) from e
        except Exception as e:
            raise ProviderNotAvailableError(f"Failed to initialize Anthropic client: {e}") from e

    def invoke(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Invoke Claude with a prompt.

        Args:
            prompt: Input prompt
            model: Claude model identifier
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            max_retries: Maximum retry attempts
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            LLMResponse with content and usage

        Raises:
            ProviderInvocationError: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs,
                )

                # Calculate cost
                cost = self.calculate_cost(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    model=model,
                )

                # Create usage record
                usage = LLMUsage(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    model=model,
                    cost_usd=cost,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )

                # Log success
                logger.info(
                    f"Anthropic invocation successful: {model} "
                    f"(in: {usage.input_tokens}, out: {usage.output_tokens}, "
                    f"cost: ${usage.cost_usd:.4f})"
                )

                # Return standardized response
                return LLMResponse(
                    content=response.content[0].text,
                    usage=usage,
                    model=response.model,
                    finish_reason=response.stop_reason,
                    provider="anthropic",
                )

            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Check if retryable error
                retryable_errors = ["RateLimitError", "APIConnectionError", "APITimeoutError"]
                is_retryable = any(err in error_name for err in retryable_errors)

                if is_retryable and attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2**attempt
                    logger.warning(
                        f"Anthropic invocation failed ({error_name}), "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    # Non-retryable error or max retries reached
                    logger.error(f"Anthropic invocation failed: {error_name} - {e!s}")
                    break

        # All retries failed
        raise ProviderInvocationError(
            f"Anthropic invocation failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__} - {last_error!s}"
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost based on Anthropic pricing.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Cost in USD
        """
        if model not in self.PRICING:
            logger.warning(f"Unknown Anthropic model pricing: {model}, using Sonnet defaults")
            pricing = self.PRICING["claude-3-5-sonnet-20241022"]
        else:
            pricing = self.PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_available_models(self) -> list[str]:
        """Get list of available Anthropic models"""
        return list(self.PRICING.keys())

    def is_available(self) -> bool:
        """Check if Anthropic provider is available"""
        return self.api_key is not None and self.client is not None
