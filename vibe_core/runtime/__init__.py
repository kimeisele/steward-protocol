"""
Runtime Components Package
===========================

GAD-002 Phase 3 Implementation

Contains runtime components for the orchestrator:
- llm_client.py: LLM client with graceful failover
- prompt_runtime.py: Prompt composition runtime
- prompt_registry.py: Prompt registry with governance injection
- prompt_context.py: Dynamic context engine for prompt injection (GAD-909)
"""

from .llm_client import CostTracker, LLMClient, NoOpClient
from .prompt_context import PromptContext, get_prompt_context
from .prompt_registry import PromptRegistry

__all__ = [
    "CostTracker",
    "LLMClient",
    "NoOpClient",
    "PromptContext",
    "PromptRegistry",
    "get_prompt_context",
]
