"""
HERALD - Autonomous Intelligence Agent for Steward Protocol

A reference implementation demonstrating:
- Cryptographic identity verification (Steward Protocol)
- Autonomous content generation with governance
- Multi-platform distribution (Twitter, Reddit)
- Full audit trail and observability (GAD-000 compliance)

Vibe-OS Compatible (ARCH-050 Cartridge):
    from herald.cartridge_main import HeraldCartridge
    agent = HeraldCartridge()
    result = agent.run_campaign()

Standalone Execution:
    python herald/shim.py --action run
    python herald/shim.py --action publish
"""

from .cartridge_main import HeraldCartridge
from .tools import ResearchTool, ContentTool, BroadcastTool

__version__ = "3.0.0"
__author__ = "Steward Protocol"
__all__ = [
    "HeraldCartridge",
    "ResearchTool",
    "ContentTool",
    "BroadcastTool",
]
