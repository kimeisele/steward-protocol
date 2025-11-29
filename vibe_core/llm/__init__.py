"""
LLM integration for vibe-agency OS.

This module provides the LLM abstraction layer that enables agents
to perform cognitive work via language models.
"""

from vibe_core.llm.chain import ChainProvider
from vibe_core.llm.degradation_chain import (
    DegradationChain,
    DegradationLevel,
    DegradationResponse,
)
from vibe_core.llm.human_provider import HumanProvider
from vibe_core.llm.local_llama_provider import (
    LocalLlamaProvider,
    download_default_model,
)
from vibe_core.llm.provider import LLMError, LLMProvider
from vibe_core.llm.smart_local_provider import SmartLocalProvider
from vibe_core.llm.steward_provider import StewardProvider

__all__ = [
    "ChainProvider",
    "DegradationChain",
    "DegradationLevel",
    "DegradationResponse",
    "download_default_model",
    "HumanProvider",
    "LLMError",
    "LLMProvider",
    "LocalLlamaProvider",
    "SmartLocalProvider",
    "StewardProvider",
]
