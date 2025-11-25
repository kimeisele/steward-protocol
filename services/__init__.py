"""
🧠 SERVICES LAYER
Shared utilities and integrations for Agent City.

Modules:
- llm_engine: LLM provider wrapper for generating dynamic agent responses
"""

from .llm_engine import LLMEngine, llm

__all__ = ["LLMEngine", "llm"]
