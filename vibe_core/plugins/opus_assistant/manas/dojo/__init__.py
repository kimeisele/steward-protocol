"""
PROJECT DOJO - Ephemeral Synaptic Training System

OPUS-133: "MANAS lernt nicht um zu gewinnen, sondern um zu dienen."

This module enables autonomous MANAS training through:
1. Ephemeral kernels (RAM-only, disposable)
2. Synthetic intent generation (good, bad, edge cases)
3. High-speed synaptic reinforcement
4. Red team attack simulation
5. Periodic "meditation" via heartbeat integration

Architecture:
    DojoRunner      - Orchestrates training epochs
    ScenarioBank    - Provides training curricula
    TrainingMetrics - Tracks learning progress
"""

from .runner import DojoConfig, DojoRunner, TrainingSession
from .scenarios import Scenario, ScenarioBank, ScenarioType
from .synaptic_seeder import (
    BASELINE_BAD_PATTERNS,
    BASELINE_GOOD_PATTERNS,
    SynapticSeeder,
    seed_baseline,
)

__all__ = [
    "DojoRunner",
    "DojoConfig",
    "TrainingSession",
    "ScenarioBank",
    "Scenario",
    "ScenarioType",
    # Synaptic Seeder
    "SynapticSeeder",
    "seed_baseline",
    "BASELINE_GOOD_PATTERNS",
    "BASELINE_BAD_PATTERNS",
]
