"""
Task Scheduler Protocol - Backwards Compatibility Re-export

GAP-018 FIX: Canonical source is now protocols/ledger.py
This file exists for backwards compatibility only.
"""

# Re-export from canonical source
from .ledger import VibeScheduler

__all__ = ["VibeScheduler"]
