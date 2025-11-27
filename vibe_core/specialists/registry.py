#!/usr/bin/env python3
"""
AgentRegistry - ARCH-009
Centralized registry for specialist agents

This registry maps ProjectPhase to BaseSpecialist classes, providing a clean
injection point for:
- HAP (Hierarchical Agent Pattern) specialist routing
- MAD (Mission Architecture Dimension) context updates (future 5D/6D)
- Dynamic specialist loading based on mission constraints

Why Registry Pattern:
- Eliminates hardcoded if/elif blocks in orchestrator
- Enables runtime specialist substitution (future: A/B testing, rollback)
- Foundation for evolutionary logic (5D: MAD dimension routing)
- Single source of truth for phase → specialist mapping

Future Evolution (5D/6D):
- Registry will accept MAD context to select specialist variants
- Registry will enable "specialist swapping" based on mission profile
- Registry will support multi-specialist coordination (6D: cross-phase)
"""

import logging
from enum import Enum

from .base_specialist import BaseSpecialist

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Centralized registry for specialist agents (HAP pattern)

    Maps ProjectPhase → BaseSpecialist class for dynamic handler resolution.

    Usage:
        registry = AgentRegistry()
        specialist_class = registry.get_specialist(ProjectPhase.CODING)
        specialist = specialist_class(mission_id, store, guard, orchestrator)

    Future (5D/6D):
        registry = AgentRegistry(mad_context=mission_architecture)
        specialist_class = registry.get_specialist(
            phase=ProjectPhase.CODING,
            mad_context=mad_context  # Enable variant selection
        )
    """

    def __init__(self):
        """Initialize the agent registry with default specialists"""
        self._registry: dict[Enum, type[BaseSpecialist]] = {}
        self._initialize_default_registry()

    def _initialize_default_registry(self) -> None:
        """
        Initialize registry with default specialist mappings

        This maps each ProjectPhase to its corresponding specialist class.
        """
        # Import ProjectPhase from apps.agency types (no circular dependency)
        from apps.agency.orchestrator.types import ProjectPhase
        from apps.agency.specialists import (
            CodingSpecialist,
            DeploymentSpecialist,
            MaintenanceSpecialist,
            PlanningSpecialist,
            TestingSpecialist,
        )

        self._registry = {
            ProjectPhase.PLANNING: PlanningSpecialist,
            ProjectPhase.CODING: CodingSpecialist,
            ProjectPhase.TESTING: TestingSpecialist,
            ProjectPhase.DEPLOYMENT: DeploymentSpecialist,
            ProjectPhase.MAINTENANCE: MaintenanceSpecialist,
        }

        logger.info(f"✅ AgentRegistry initialized with {len(self._registry)} specialists")

    def get_specialist(self, phase: Enum) -> type[BaseSpecialist]:
        """
        Get specialist class for a given phase

        Args:
            phase: ProjectPhase enum value

        Returns:
            BaseSpecialist subclass for the phase

        Raises:
            ValueError: If no specialist registered for phase

        Example:
            specialist_class = registry.get_specialist(ProjectPhase.CODING)
            specialist = specialist_class(mission_id, store, guard, orchestrator)
        """
        if phase not in self._registry:
            raise ValueError(
                f"No specialist registered for phase: {phase}. "
                f"Available phases: {list(self._registry.keys())}"
            )

        specialist_class = self._registry[phase]
        logger.debug(f"Retrieved specialist: {specialist_class.__name__} for phase: {phase.value}")

        return specialist_class

    def register_specialist(self, phase: Enum, specialist_class: type[BaseSpecialist]) -> None:
        """
        Register or override a specialist for a phase

        This enables:
        - Runtime specialist swapping
        - A/B testing of specialist variants
        - Mission-specific specialist customization (future 5D)

        Args:
            phase: ProjectPhase enum value
            specialist_class: BaseSpecialist subclass to register

        Example:
            # Override CODING specialist with custom variant
            registry.register_specialist(
                ProjectPhase.CODING,
                CustomCodingSpecialist
            )
        """
        if not issubclass(specialist_class, BaseSpecialist):
            raise TypeError(
                f"Specialist class must inherit from BaseSpecialist, "
                f"got: {specialist_class.__name__}"
            )

        old_specialist = self._registry.get(phase)
        self._registry[phase] = specialist_class

        if old_specialist:
            logger.info(
                f"🔄 Specialist override: {phase.value} "
                f"({old_specialist.__name__} → {specialist_class.__name__})"
            )
        else:
            logger.info(f"➕ Specialist registered: {phase.value} → {specialist_class.__name__}")

    def list_specialists(self) -> dict[str, str]:
        """
        List all registered specialists

        Returns:
            Dictionary mapping phase names to specialist class names

        Example:
            >>> registry.list_specialists()
            {
                'PLANNING': 'PlanningSpecialist',
                'CODING': 'CodingSpecialist',
                ...
            }
        """
        return {phase.value: specialist.__name__ for phase, specialist in self._registry.items()}

    def __repr__(self) -> str:
        """String representation for debugging"""
        specialists = ", ".join(
            f"{phase.value}→{cls.__name__}" for phase, cls in self._registry.items()
        )
        return f"AgentRegistry({len(self._registry)} specialists: {specialists})"


# ============================================================================
# Singleton Instance (Optional - for convenience)
# ============================================================================

_default_registry = None


def get_default_registry() -> AgentRegistry:
    """
    Get the default global registry instance (singleton pattern)

    This is optional - orchestrator can create its own registry instance.
    Singleton pattern is provided for convenience and testing.

    Returns:
        Global AgentRegistry instance

    Example:
        registry = get_default_registry()
        specialist_class = registry.get_specialist(ProjectPhase.CODING)
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = AgentRegistry()
    return _default_registry
