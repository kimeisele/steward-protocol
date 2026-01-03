"""
OUROBOROS - The Self-Healing Loop

🐍 "The snake that eats its own tail"

This module implements the feedback loop that enables the system to:
1. SENSE: Detect violations from multiple sources (local, CI/CD, runtime)
2. REMEMBER: Persist violations in the Knowledge Graph
3. LEARN: Identify patterns and training gaps
4. HEAL: Apply remedies via Shuddhi
5. VERIFY: Confirm fixes worked

The Ouroboros loop is the immune system of the codebase.
"""

from .ingestion import ViolationIngester, ViolationSource
from .sync import CISyncService

__all__ = ["ViolationIngester", "ViolationSource", "CISyncService"]
