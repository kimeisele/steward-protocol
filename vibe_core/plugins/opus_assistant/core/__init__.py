"""
OPUS Assistant Core - Pure logic, no UI dependencies.

This module provides DATA only. No rendering!
The interface plugin is responsible for all UI/rendering.

Components:
- VerificationEngine: @HARNESS verification logic
- DriftDetector: Code vs docs drift detection
- OpusGenerator: OPUS.md data generation (with section preservation)
- ConfigLoader: Fraktale config loading (defaults + system)
- OpusContextService: Dynamic runtime context synthesis (Phase 2)
- ObservationLogger: System journal for soft interaction (Phase 2.5)
"""

from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader, deep_merge
from vibe_core.plugins.opus_assistant.core.context_service import OpusContext, OpusContextService, SystemHealth
from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector, DriftReport
from vibe_core.plugins.opus_assistant.core.observation_logger import (
    Observation,
    ObservationJournal,
    ObservationLogger,
    ObservationSeverity,
)
from vibe_core.plugins.opus_assistant.core.opus_generator import OpusData, OpusGenerator
from vibe_core.plugins.opus_assistant.core.verification_logic import (
    HarnessResult,
    VerificationEngine,
    VerificationReport,
)

__all__ = [
    # Verification
    "VerificationEngine",
    "VerificationReport",
    "HarnessResult",
    # Drift Detection
    "DriftDetector",
    "DriftReport",
    # OPUS Generation
    "OpusGenerator",
    "OpusData",
    # Config
    "ConfigLoader",
    "deep_merge",
    # Context Service (Phase 2)
    "OpusContextService",
    "OpusContext",
    "SystemHealth",
    # Observation Logger (Phase 2.5)
    "ObservationLogger",
    "ObservationSeverity",
    "Observation",
    "ObservationJournal",
]
