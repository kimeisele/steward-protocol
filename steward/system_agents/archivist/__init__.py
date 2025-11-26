"""
ARCHIVIST - The Audit & Verification Agent for STEWARD Protocol.

The ARCHIVIST is an autonomous agent that:
1. Monitors events from other agents (e.g., HERALD)
2. Verifies cryptographic signatures
3. Creates attestations for verified events
4. Maintains an immutable audit trail

This demonstrates multi-agent federation in the Steward Protocol.
"""

__version__ = "1.0.0"
__all__ = ["ArchivistCartridge"]

from steward.system_agents.archivist.cartridge_main import ArchivistCartridge
