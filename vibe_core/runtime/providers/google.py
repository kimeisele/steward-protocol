#!/usr/bin/env python3
"""
GAD-511: Google Gemini Provider Implementation
===============================================

Concrete implementation of LLMProvider for Google's Gemini models.

Features:
- Gemini 2.5 Flash (experimental, latest, fastest)
- Gemini 2.0 Flash support
- Gemini 1.5 Flash/Pro support (stable)
- Cost calculation based on Google pricing
- Retry logic with exponential backoff
- API key validation

Pricing (as of 2025-11-19):
- Gemini 2.5 Flash (Exp): $0.00/MTok (free during preview)
- Gemini 2.0 Flash (Exp): $0.00/MTok (free during preview)
- Gemini 1.5 Flash: $0.075/MTok input, $0.30/MTok output (≤128K tokens)
- Gemini 1.5 Pro: $1.25/MTok input, $5.00/MTok output (≤128K tokens)

Version: 1.2 (Updated for Gemini 2.5)
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


class GoogleProvider(LLMProvider):
    """
    Google Gemini provider implementation.

    Supports Gemini 2.5, 2.0, and 1.5 models (Flash/Pro).
    Handles API communication, retries, and cost calculation.
    """

    # Pricing table (USD per million tokens, ≤128K context)
    PRICING = {
        # Gemini 2.5 (latest, free during preview)
        "gemini-2.5-flash": {"input": 0.0, "output": 0.0},
        "gemini-2.5-flash-exp": {"input": 0.0, "output": 0.0},
        # Gemini 2.0 (experimental, free during preview)
        "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},
        # Gemini 1.5 (stable)
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-flash-latest": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-pro-latest": {"input": 1.25, "output": 5.00},
    }

    def __init__(self, api_key: str | None = None, **kwargs: Any):
        """
        Initialize Google Gemini provider.

        Args:
            api_key: Google API key
            **kwargs: Additional configuration (unused for now)

        Raises:
            ProviderNotAvailableError: If google-generativeai package not installed or API key invalid
        """
        self.api_key = api_key

        if not self.api_key:
            raise ProviderNotAvailableError(
                "Google API key required. Set GOOGLE_API_KEY environment variable."
            )

        try:
            import google.generativeai as genai

            # Force REST transport to avoid gRPC SSL issues in restricted environments
            genai.configure(api_key=self.api_key, transport="rest")
            self.genai = genai
            logger.info("Google Gemini provider initialized successfully (transport=REST)")
        except ImportError as e:
            raise ProviderNotAvailableError(
                "google-generativeai package not installed. Install with: pip install google-generativeai>=0.8.0"
            ) from e
        except Exception as e:
            raise ProviderNotAvailableError(
                f"Failed to initialize Google Gemini client: {e}"
            ) from e

    def invoke(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Invoke Gemini with a prompt.

        Args:
            prompt: Input prompt
            model: Gemini model identifier (default: gemini-2.5-flash)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            max_retries: Maximum retry attempts
            **kwargs: Additional Google-specific parameters

        Returns:
            LLMResponse with content and usage

        Raises:
            ProviderInvocationError: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # Create model instance
                gemini_model = self.genai.GenerativeModel(model)

                # Configure generation settings
                generation_config = {
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                }

                # Generate response
                response = gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config,
                )

                # Extract token usage (Google provides this in metadata)
                # Note: Google's API may not always provide exact token counts
                # We'll use best-effort estimation
                input_tokens = 0
                output_tokens = 0

                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                    output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

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

                # Extract text from response
                content = response.text if hasattr(response, "text") else str(response)

                # Determine finish reason
                finish_reason = "stop"
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "finish_reason"):
                        finish_reason = str(candidate.finish_reason)

                # Log success
                logger.info(
                    f"Google Gemini invocation successful: {model} "
                    f"(in: {usage.input_tokens}, out: {usage.output_tokens}, "
                    f"cost: ${usage.cost_usd:.4f})"
                )

                # Return standardized response
                return LLMResponse(
                    content=content,
                    usage=usage,
                    model=model,
                    finish_reason=finish_reason,
                    provider="google",
                )

            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Check if retryable error
                retryable_errors = ["ResourceExhausted", "ServiceUnavailable", "DeadlineExceeded"]
                is_retryable = any(err in error_name for err in retryable_errors)

                if is_retryable and attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2**attempt
                    logger.warning(
                        f"Google Gemini invocation failed ({error_name}), "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    # Non-retryable error or max retries reached
                    logger.error(f"Google Gemini invocation failed: {error_name} - {e!s}")
                    break

        # All retries failed
        raise ProviderInvocationError(
            f"Google Gemini invocation failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__} - {last_error!s}"
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost based on Google Gemini pricing.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Cost in USD
        """
        if model not in self.PRICING:
            logger.warning(
                f"Unknown Google Gemini model pricing: {model}, using 2.5 Flash defaults"
            )
            pricing = self.PRICING["gemini-2.5-flash"]
        else:
            pricing = self.PRICING[model]

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_available_models(self) -> list[str]:
        """Get list of available Google Gemini models"""
        return list(self.PRICING.keys())

    def is_available(self) -> bool:
        """Check if Google Gemini provider is available"""
        return self.api_key is not None and self.genai is not None
