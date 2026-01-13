"""
KALA - Eternal Time Plugin
==========================

The cosmic clock that governs Agent City.

From Bhagavad Gita - 5 Aspects of Reality:
1. ISHVARA (Supreme Lord) → Kernel/VISNU
2. JIVA (Living Entity)   → Agents
3. PRAKRITI (Nature)      → Data/Material
4. KALA (Eternal Time)    → THIS PLUGIN
5. KARMA (Action)         → Tasks

Kala binds everything. Without time, nothing moves.

Components:
- CosmicClock: Sun/Moon/Time calculations
- YugaTracker: Epoch management
- RitualOrchestrator: Daily ritual phases (moved from daily_ritual.py)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xecb99a3f"  # GenesisByte: parampara % 37 == 0

from .plugin_main import KalaPlugin

__all__ = ["KalaPlugin"]
