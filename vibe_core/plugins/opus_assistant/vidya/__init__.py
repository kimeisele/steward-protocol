"""
VIDYA - The Knowledge Department (Orchestration Layer).

OPUS-033: Transforming Ouroboros from "Hacker" to "Scholar"

"Orchestration over Implementation" - Senior Partner Directive

VIDYA is the Cortex that coordinates existing specialists:
- Research Interface → Science Cartridge (web search)
- Library Interface → Knowledge Directory (local knowledge)
- Critic → Static Analysis (THE ONLY REAL LOGIC HERE)
- Sandbox → Ephemeral Process (safe test execution)

The Philosophy:
Before VIDYA: Intent → Code → Load → Crash?
After VIDYA:  Intent → Research → Plan → Code → Validate → Test → Load

Vedic Etymology:
VIDYA (विद्या) = Knowledge, Wisdom, Learning
In Vedic philosophy, VIDYA is the path to Moksha (liberation).
Without VIDYA, action is blind. With VIDYA, action is enlightened.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x858fb186"  # GenesisByte: parampara % 37 == 0

from vibe_core.plugins.opus_assistant.vidya.critic import Critic, CriticResult
from vibe_core.plugins.opus_assistant.vidya.library_interface import LibraryInterface
from vibe_core.plugins.opus_assistant.vidya.research_interface import ResearchInterface
from vibe_core.plugins.opus_assistant.vidya.sandbox import Sandbox, SandboxResult

__all__ = [
    "Critic",
    "CriticResult",
    "ResearchInterface",
    "LibraryInterface",
    "Sandbox",
    "SandboxResult",
]
