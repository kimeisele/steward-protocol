#!/usr/bin/env python3
"""
LLM Client - Provider-Agnostic Adapter (GAD-511 Refactor)
===========================================================

Implements GAD-002 Decision 6 + GAD-511 Neural Adapter Strategy

Features:
- **Multi-provider support** (Anthropic, OpenAI, Local) via GAD-511
- Graceful failover (no crash if API key missing)
- Retry logic with exponential backoff
- Cost tracking (input/output tokens)
- Circuit breaker (GAD-509)
- Operational quotas (GAD-510)

**BACKWARD COMPATIBLE**: Maintains same API as previous version

Version: 2.0 (GAD-511)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenError
from .providers import LLMProvider, LLMProviderError, NoOpProvider, get_default_provider
from .quota_manager import OperationalQuota, QuotaExceededError, QuotaLimits

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES (Kept for backward compatibility)
# =============================================================================


@dataclass
class LLMUsage:
    """Token usage and cost information"""

    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float
    timestamp: str


@dataclass
class LLMResponse:
    """Standardized LLM response"""

    content: str
    usage: LLMUsage
    model: str
    finish_reason: str


# =============================================================================
# COST TRACKER (Kept unchanged for backward compatibility)
# =============================================================================


class CostTracker:
    """
    Tracks API costs across invocations.

    Now provider-agnostic - delegates cost calculation to providers.
    """

    def __init__(self):
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.invocations = []

    def record(
        self, input_tokens: int, output_tokens: int, model: str, cost_usd: float
    ) -> LLMUsage:
        """Record token usage (cost now provided by provider)"""
        usage = LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost_usd=cost_usd,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        self.total_cost += cost_usd
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.invocations.append(usage)

        return usage

    def get_summary(self) -> dict[str, Any]:
        """Get cost summary"""
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_invocations": len(self.invocations),
            "average_cost_per_invocation": (
                round(self.total_cost / len(self.invocations), 4) if self.invocations else 0
            ),
        }


# =============================================================================
# EXCEPTIONS (Kept unchanged for backward compatibility)
# =============================================================================


class LLMClientError(Exception):
    """Base exception for LLM client errors"""

    pass


class LLMInvocationError(LLMClientError):
    """Raised when LLM invocation fails after retries"""

    pass


class BudgetExceededError(LLMClientError):
    """Raised when budget limit is reached"""

    pass


# =============================================================================
# NO-OP CLIENT (Kept for backward compatibility with legacy code)
# =============================================================================


class NoOpClient:
    """
    Legacy NoOpClient for backward compatibility.

    **Deprecated**: Use providers.NoOpProvider instead (via GAD-511)
    """

    def __init__(self):
        logger.warning("NoOpClient initialized - running in knowledge-only mode")
        self.messages = self  # Make self.messages point to self for API compatibility

    def create(self, **kwargs) -> Any:
        """Mock messages.create() that returns empty response"""
        logger.warning("NoOpClient: Skipping LLM call (no API key)")

        # Return mock response object
        class MockResponse:
            def __init__(self):
                self.content = [MockContent()]
                self.usage = MockUsage()
                self.model = kwargs.get("model", "noop")
                self.stop_reason = "no_api_key"

        class MockContent:
            def __init__(self):
                self.text = "{}"  # Empty JSON response

        class MockUsage:
            def __init__(self):
                self.input_tokens = 0
                self.output_tokens = 0

        return MockResponse()


# =============================================================================
# LLM CLIENT (GAD-511 Refactored)
# =============================================================================


class LLMClient:
    """
    Provider-agnostic LLM client adapter.

    **GAD-511 Architecture**: Uses provider system for multi-provider support
    while maintaining backward-compatible API.

    **Backward Compatible**: Drop-in replacement for legacy LLMClient

    Features:
    - Multi-provider support (Anthropic, OpenAI, Local)
    - Graceful failover (NoOpProvider if no provider available)
    - Cost tracking via CostTracker
    - Circuit breaker (GAD-509)
    - Operational quotas (GAD-510)
    - Budget enforcement (optional)

    Usage:
        client = LLMClient()
        response = client.invoke(
            prompt="What is 2+2?",
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024
        )
        print(response.content)
        print(f"Cost: ${response.usage.cost_usd:.4f}")
    """

    def __init__(self, budget_limit: float | None = None, provider: LLMProvider | None = None):
        """
        Initialize LLM client.

        Args:
            budget_limit: Optional budget limit in USD (default: None = no limit)
            provider: Optional explicit provider (default: auto-detect via factory)
        """
        self.cost_tracker = CostTracker()
        self.budget_limit = budget_limit

        # Initialize safety layer (GAD-509 & GAD-510)
        self.circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout_seconds=30,
                window_size_seconds=60,
            )
        )
        self.quota_manager = OperationalQuota(
            limits=QuotaLimits(
                requests_per_minute=100,
                tokens_per_minute=100_000,
                cost_per_request_usd=0.50,
                cost_per_hour_usd=50.0,
                cost_per_day_usd=500.0,
            )
        )

        # Initialize provider (GAD-511)
        if provider is not None:
            self.provider = provider
        else:
            self.provider = get_default_provider()

        # Set mode for backward compatibility
        if isinstance(self.provider, NoOpProvider):
            self.mode = "noop"
            self.client = NoOpClient()  # For legacy code compatibility
            logger.info("LLM Client initialized with NoOp provider (mock mode)")
        else:
            self.mode = self.provider.get_provider_name().lower()
            self.client = None  # Not used in provider mode
            logger.info(f"LLM Client initialized with {self.provider.get_provider_name()} provider")

    def invoke(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        max_retries: int = 3,
    ) -> LLMResponse:
        """
        Invoke LLM with safety layer, retry logic, and cost tracking.

        **GAD-511**: Delegates to provider while maintaining safety guardrails

        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            LLMResponse with content and usage info

        Raises:
            BudgetExceededError: If budget limit reached
            QuotaExceededError: If operational quota exceeded
            CircuitBreakerOpenError: If circuit breaker is OPEN
            LLMInvocationError: If all retries fail
        """
        # Check budget before invocation
        if self.budget_limit and self.cost_tracker.total_cost >= self.budget_limit:
            raise BudgetExceededError(
                f"Budget limit reached: ${self.budget_limit:.2f} "
                f"(current: ${self.cost_tracker.total_cost:.4f})"
            )

        # Check operational quotas (GAD-510 pre-flight check)
        estimated_tokens = max_tokens
        try:
            self.quota_manager.check_before_request(
                estimated_tokens=estimated_tokens, operation=f"invoke({model})"
            )
        except QuotaExceededError as e:
            logger.error(f"Quota check failed: {e}")
            raise

        # Delegate to provider through circuit breaker
        try:

            def provider_invoke():
                return self.provider.invoke(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    max_retries=max_retries,
                )

            # Call provider through circuit breaker (GAD-509)
            provider_response = self.circuit_breaker.call(provider_invoke)

            # Track cost
            usage = self.cost_tracker.record(
                input_tokens=provider_response.usage.input_tokens,
                output_tokens=provider_response.usage.output_tokens,
                model=provider_response.model,
                cost_usd=provider_response.usage.cost_usd,
            )

            # Record quota usage (GAD-510)
            total_tokens = (
                provider_response.usage.input_tokens + provider_response.usage.output_tokens
            )
            self.quota_manager.record_request(
                tokens_used=total_tokens, cost_usd=usage.cost_usd, operation=f"invoke({model})"
            )

            # Log success
            provider_name = getattr(provider_response, "provider", "unknown")
            logger.info(
                f"LLM invocation successful: {model} via {provider_name} "
                f"(in: {usage.input_tokens}, out: {usage.output_tokens}, cost: ${usage.cost_usd:.4f})"
            )

            # Return standardized response (convert provider response to legacy format)
            return LLMResponse(
                content=provider_response.content,
                usage=usage,
                model=provider_response.model,
                finish_reason=provider_response.finish_reason,
            )

        except CircuitBreakerOpenError as e:
            logger.error(f"Circuit breaker OPEN: {e}")
            raise LLMInvocationError(f"LLM invocation failed: Circuit breaker OPEN - {e!s}")

        except QuotaExceededError:
            raise  # Re-raise quota errors

        except LLMProviderError as e:
            logger.error(f"Provider invocation failed: {e}")
            raise LLMInvocationError(f"LLM invocation failed: {e!s}")

        except Exception as e:
            logger.error(f"Unexpected error during invocation: {e}")
            raise LLMInvocationError(f"LLM invocation failed: {type(e).__name__} - {e!s}")

    def get_cost_summary(self) -> dict[str, Any]:
        """Get cost tracking summary"""
        summary = self.cost_tracker.get_summary()
        if self.budget_limit:
            summary["budget_limit_usd"] = self.budget_limit
            summary["budget_remaining_usd"] = round(
                self.budget_limit - self.cost_tracker.total_cost, 4
            )
            summary["budget_used_percent"] = round(
                (self.cost_tracker.total_cost / self.budget_limit) * 100, 2
            )
        return summary


# =============================================================================
# CLI INTERFACE (For testing)
# =============================================================================

if __name__ == "__main__":
    # Test LLM client with provider system
    print("Testing LLM Client (GAD-511 Provider System)...")
    print("=" * 60)

    # Initialize client
    client = LLMClient(budget_limit=1.0)

    print(f"Mode: {client.mode}")
    print(f"Provider: {client.provider.get_provider_name()}")
    print(f"Budget: ${client.budget_limit}")
    print()

    # Test invocation
    if client.mode != "noop":
        try:
            response = client.invoke(
                prompt="What is 2+2? Answer in one sentence.",
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
            )

            print("Response:")
            print(response.content)
            print()
            print("Usage:")
            print(f"  Input tokens: {response.usage.input_tokens}")
            print(f"  Output tokens: {response.usage.output_tokens}")
            print(f"  Cost: ${response.usage.cost_usd:.4f}")
            print()
            print("Cost Summary:")
            summary = client.get_cost_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error: {e}")
    else:
        print("NoOp mode - skipping test invocation")
        print("Set GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY to test real invocations")
