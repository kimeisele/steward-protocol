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
    # === GENESIS QUARTER (0-3) - Boot/Load/Alloc/Init ===
    0: ("wake", "boot", "start", "init", "up"),  # VYASA (SYS_WAKE) - Awakening
    1: ("create", "spawn", "genesis", "new", "born", "load"),  # BRAHMA (LOAD_ROOT) - Creation
    2: ("broadcast", "message", "communicate", "news"),  # NARADA (ALLOC_MEM) - Communication
    3: ("destroy", "dissolve", "transform", "cleanup", "thread"),  # SHAMBHU (INIT_THREAD) - Transformation
    # === DHARMA QUARTER (4-7) - Compile/Bind/Check/Test ===
    4: ("compile", "scan", "infrastructure", "file", "disk"),  # PRITHU (COMPILE_AST) - Structure
    5: ("purify", "cleanse", "format", "lint", "bind"),  # KUMARAS (BIND_SYMBOL) - Purification
    6: ("analyze", "resolve", "enumerate", "logic", "type"),  # KAPILA (TYPE_CHECK) - Analysis
    7: ("rule", "law", "govern", "policy", "test"),  # MANU (DHARMA_TEST) - Governance
    # === KARMA QUARTER (8-11) - Exec/Extend/Sync/Sign ===
    8: ("execute", "run", "enforce", "action"),  # PARASHURAMA (EXEC_OP) - Execution
    9: ("protect", "defend", "devotion", "faith", "extend"),  # PRAHLADA (EXTEND_CAP) - Protection
    10: ("schedule", "task", "duty", "sync"),  # JANAKA (STATE_SYNC) - Scheduling
    11: ("persist", "commit", "ledger", "store", "sign"),  # BHISHMA (LEDGER_SIGN) - Persistence
    # === MOKSHA QUARTER (12-15) - Yield/Flush/Log/Seal ===
    12: ("guard", "kill", "security", "terminate", "yield"),  # NRISIMHA (YIELD_CPU) - Security
    13: ("resource", "allocate", "give", "surrender", "flush"),  # BALI (IO_FLUSH) - Resources
    14: ("observe", "log", "report", "narrate", "status"),  # SHUKA (LOG_EMIT) - Observation
    15: ("judge", "audit", "verdict", "death", "seal"),  # YAMARAJA (AUDIT_SEAL) - Judgment
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
