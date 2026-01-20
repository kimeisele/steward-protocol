"""
INTENTS - Die zentrale Intent-Registry (SSOT)
=============================================

"mattaḥ sarvaṁ pravartate" - Everything emanates from Me.
— Bhagavad Gita 10.8

KEIN MANUAL LABOR. Die Intents sind HIER definiert.
MantraProtocol liest sie automatisch zur Import-Zeit.

STRUKTUR:
    Position (0-15) → Liste von Keywords die dieser Guardian handhabt

WATERTIGHT: No hardcoded intents in mahajana files.
"""

from typing import Dict, Final, List, Tuple

# =============================================================================
# THE INTENT MAP (SSOT)
# =============================================================================
# Derived from each Guardian's Dharmic Function, not random keywords.

INTENT_MAP: Final[Dict[int, Tuple[str, ...]]] = {
    # ==========================================================================
    # ALIGNED WITH seed.py ALL_GUARDIANS (SSOT)
    # Position → Guardian → Intents
    # ==========================================================================
    # === GENESIS QUARTER (0-3) ===
    0: ("boot", "wake", "start", "system", "init"),  # VYASA - System Wake (Genesis HEAD)
    1: ("create", "spawn", "genesis", "new", "born"),  # BRAHMA - Creation
    2: ("broadcast", "message", "communicate", "narada", "news", "chat", "talk", "ask", "help", "hello", "hi"),  # NARADA - Communication
    3: ("destroy", "dissolve", "transform", "shiva", "cleanup"),  # SHAMBHU - Transformation
    # === DHARMA QUARTER (4-7) ===
    4: ("scan", "compile", "document", "structure", "knowledge", "search", "find", "locate"),  # PRITHU - Compile/Structure (Dharma HEAD)
    5: ("purify", "cleanse", "shuddhi", "format", "lint"),  # KUMARAS - Purification
    6: ("analyze", "resolve", "enumerate", "logic", "inference", "understand", "explain", "why", "how", "debug"),  # KAPILA - Analysis
    7: ("rule", "law", "govern", "manu", "policy"),  # MANU - Governance
    # === KARMA QUARTER (8-11) ===
    8: ("execute", "run", "enforce", "parashurama", "action"),  # PARASHURAMA - Execution (Karma HEAD)
    9: ("protect", "defend", "prahlada", "devotion", "faith"),  # PRAHLADA - Protection
    10: ("schedule", "task", "janaka", "dharma", "duty"),  # JANAKA - Scheduling
    11: ("persist", "commit", "ledger", "bhishma", "store"),  # BHISHMA - Persistence
    # === MOKSHA QUARTER (12-15) ===
    12: ("guard", "kill", "security", "nrisimha", "terminate"),  # NRISIMHA - Security (Moksha HEAD)
    13: ("resource", "allocate", "bali", "give", "surrender"),  # BALI - Resources
    14: ("observe", "log", "shuka", "report", "narrate", "status"),  # SHUKA - Observation
    15: ("judge", "audit", "yamaraja", "verdict", "death"),  # YAMARAJA - Judgment
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_intents(position: int) -> Tuple[str, ...]:
    """Get intents for a position. Returns empty tuple if invalid."""
    return INTENT_MAP.get(position, ())


def get_position_for_intent(intent: str) -> int:
    """Find which position handles an intent. Returns -1 if not found."""
    intent_lower = intent.lower()
    for pos, intents in INTENT_MAP.items():
        if intent_lower in intents:
            return pos
    return -1


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "INTENT_MAP",
    "get_intents",
    "get_position_for_intent",
]
