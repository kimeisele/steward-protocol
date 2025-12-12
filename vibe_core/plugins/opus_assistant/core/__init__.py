"""
OPUS Assistant Core - Pure logic, no UI dependencies.

This module provides DATA only. No rendering!
The interface plugin is responsible for all UI/rendering.

Components:
- VerificationEngine: @HARNESS verification logic
- DriftDetector: Code vs docs drift detection
- OpusGenerator: OPUS.md data generation (with section preservation)
"""

from .drift_detector import DriftDetector, DriftReport
from .opus_generator import OpusData, OpusGenerator
from .verification_logic import HarnessResult, VerificationEngine, VerificationReport

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
]
