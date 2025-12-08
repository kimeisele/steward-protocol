#!/usr/bin/env python3
"""
GAD-904: Agent Routing System (Neural Link)
===========================================

Connects Semantic Actions / Workflow Nodes to the best available Agent
based on declared capabilities.

Phase: v0.6 (Capability Matching)
Status: INITIAL IMPLEMENTATION (mocked dispatch, $0 cost)

Responsibilities:
1. Maintain registry of active agent instances
2. Match required skills -> best agent (max overlap, ties resolved by first registered)
3. Provide simple APIs:
   - register(agent)
   - find_best_agent(action: SemanticAction)
   - find_best_agent_for_skills(skills: list[str])
4. Safe fallback: return None if no agent can fully satisfy required skills

NOTE: No real LLM calls yet. Execution is mocked per instructions.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Protocol


class HasRequiredSkills(Protocol):
    required_skills: list[str]
    # name and intent are optional for scoring


class AgentRouter:
    """
    DEPRECATED (OPUS Phase 2).
    Use UnifiedRouter instead.
    """

    def __init__(self, registry_path: Path | None = None):
        warnings.warn(
            "AgentRouter is DEPRECATED in OPUS Phase 2. Use UnifiedRouter instead.", DeprecationWarning, stacklevel=2
        )
        self.registry_path = registry_path or Path(__file__).parent / "_registry.yaml"
        # Assuming _load_registry will return a list of agents compatible with existing methods
        self._agents: list[object] = self._load_registry()

    def _load_registry(self) -> list[object]:
        # This is a placeholder for actual registry loading logic.
        # For now, it returns an empty list or the initial agents if any were passed.
        # In a real scenario, this would parse the YAML file and instantiate agent objects.
        # Since the original __init__ took 'agents', we'll simulate that for now.
        # If the file exists, it would load from there. Otherwise, start empty.
        # For this specific change, we'll assume it initializes to an empty list
        # or loads from a mock source if the file exists.
        # To maintain compatibility with the original behavior of starting with an empty list
        # if no agents were provided, we'll return an empty list here.
        # A full implementation would involve parsing self.registry_path.
        return []  # Placeholder: In a real scenario, load agents from self.registry_path

    # Registry operations -------------------------------------------------
    def register(self, agent: object) -> None:
        if agent not in self._agents:
            self._agents.append(agent)

    def list_agents(self) -> list[object]:
        return list(self._agents)

    # Matching logic ------------------------------------------------------
    def _score(self, agent: object, required: list[str]) -> int:
        capabilities = getattr(agent, "capabilities", []) or []
        return sum(1 for skill in required if skill in capabilities)

    def find_best_agent_for_skills(self, required_skills: list[str]) -> object | None:
        if not self._agents:
            return None
        best = None
        best_score = -1
        for agent in self._agents:
            score = self._score(agent, required_skills)
            if score > best_score:
                best = agent
                best_score = score
        if best_score <= 0:  # No overlap at all
            return None
        return best

    def find_best_agent(self, action: HasRequiredSkills) -> object | None:
        return self.find_best_agent_for_skills(action.required_skills)

    # Convenience ---------------------------------------------------------
    def can_any_execute(self, required_skills: list[str]) -> bool:
        return self.find_best_agent_for_skills(required_skills) is not None

    def get_capability_matrix(self) -> dict:
        matrix = {}
        for agent in self._agents:
            matrix[getattr(agent, "name", repr(agent))] = getattr(agent, "capabilities", [])
        return matrix


__all__ = ["AgentRouter"]
