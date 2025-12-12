"""
OPUS Assistant Core - Pure logic, no UI dependencies.
"""

from .verification_logic import HarnessResult, VerificationEngine, VerificationReport

__all__ = ["VerificationEngine", "VerificationReport", "HarnessResult"]
