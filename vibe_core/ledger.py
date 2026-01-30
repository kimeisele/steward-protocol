"""
DEPRECATED: Use vibe_core.mahamantra import.
SSOT PROXY: Redirects to vibe_core.mahamantra.substrate.ledger
"""
from vibe_core.mahamantra import SQLiteLedger, InMemoryLedger, VibeLedger

__all__ = ["SQLiteLedger", "InMemoryLedger", "VibeLedger"]
