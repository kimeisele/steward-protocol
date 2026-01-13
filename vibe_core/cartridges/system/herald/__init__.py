"""
HERALD - Autonomous Intelligence Agent for Steward Protocol

A reference implementation demonstrating:
- Cryptographic identity verification (Steward Protocol)
- Multi-platform distribution (Twitter, Reddit)
- Full audit trail and observability (GAD-000 compliance)

Note: Content generation moved to Marketer agent.

Vibe-OS Compatible (ARCH-050 Cartridge):
    from herald.cartridge_main import HeraldCartridge
    agent = HeraldCartridge()
    result = agent.run_campaign()

Standalone Execution:
    python herald/shim.py --action run
    python herald/shim.py --action publish
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xbb702914"  # GenesisByte: parampara % 37 == 0

from .cartridge_main import HeraldCartridge
from .tools import BroadcastTool, IdentityTool, ResearchTool, ScoutTool, Scribe

__version__ = "3.0.0"
__author__ = "Steward Protocol"
__all__ = [
    "HeraldCartridge",
    "ResearchTool",
    "BroadcastTool",
    "IdentityTool",
    "ScoutTool",
    "Scribe",
]
