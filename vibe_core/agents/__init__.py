"""
Agent implementations for vibe-agency OS.

This module provides concrete agent implementations that integrate
with the kernel via the VibeAgent protocol.
"""

from vibe_core.agents.context_aware_agent import ContextAwareAgent
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.agents.specialist_agent import SpecialistAgent
from vibe_core.agents.specialist_factory import SpecialistFactoryAgent

__all__ = ["ContextAwareAgent", "SimpleLLMAgent", "SpecialistAgent", "SpecialistFactoryAgent"]
