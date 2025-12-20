"""
PROJECT DOJO v2 - Ephemeral Synaptic Training System

OPUS-133: "MANAS lernt nicht um zu gewinnen, sondern um zu dienen."

v2 Architecture (German Engineering):
    Data:       YAML curricula (curricula/*.yaml)
    Code:       Pure Python engine (runner.py, agency.py)
    Runtime:    Ephemeral kernels (:memory:)
    Agency:     Self-directed training (CuriosityTracker)

Components:
    DojoRunner      - Orchestrates training epochs
    CurriculumLoader- Loads YAML-based curricula (DATA separate from CODE)
    DojoAgency      - MANAS self-directed training (Curiosity → enter_dojo)
    ScenarioBank    - Legacy hardcoded curricula (deprecated)

Rooms:
    Arena   - Active training with VivekaAction
    Library - Research via Tavily API (TODO)
    Mirror  - Self-inspection and gap analysis (TODO)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/__init__.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
    required: true
-->
"""

# v2: YAML Curricula
# v2: MANAS Agency
from .agency import (
    CuriosityTracker,
    DojoAgency,
    SankalpaValidation,
    SankalpaValidator,
    get_dojo_agency,
)
from .curriculum_loader import CurriculumLoader, CurriculumMeta, LoadedCurriculum

# Core
from .runner import DojoConfig, DojoRunner, TrainingSession

# Legacy (for backward compatibility)
from .scenarios import Scenario, ScenarioBank, ScenarioType
from .synaptic_seeder import (
    BASELINE_BAD_PATTERNS,
    BASELINE_GOOD_PATTERNS,
    SynapticSeeder,
    seed_baseline,
)

__all__ = [
    # v2: YAML Curricula
    "CurriculumLoader",
    "CurriculumMeta",
    "LoadedCurriculum",
    # v2: MANAS Agency
    "DojoAgency",
    "CuriosityTracker",
    "SankalpaValidator",
    "SankalpaValidation",
    "get_dojo_agency",
    # Core
    "DojoRunner",
    "DojoConfig",
    "TrainingSession",
    # Legacy
    "ScenarioBank",
    "Scenario",
    "ScenarioType",
    # Synaptic Seeder
    "SynapticSeeder",
    "seed_baseline",
    "BASELINE_GOOD_PATTERNS",
    "BASELINE_BAD_PATTERNS",
]
