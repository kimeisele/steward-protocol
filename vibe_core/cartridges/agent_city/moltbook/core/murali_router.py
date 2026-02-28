"""MURALI Department Routing — VenuOrchestrator phase → department priority.

Extracted from agency_director.py. Pure read-only router, no state mutation.
"""

import logging

from vibe_core.mahamantra.substrate.core.seed import QUARTERS, WORDS

logger = logging.getLogger("MOLTBOOK_MURALI")

# MURALI 4-bit phase (0-3) → department name
_MURALI_DEPARTMENTS = {
    0: "research",  # GENESIS: scan, discover, extract topics
    1: "planning",  # DHARMA: evaluate strategy, prioritize topics
    2: "execution",  # KARMA: generate content, publish
    3: "learning",  # MOKSHA: track engagement, analyze patterns
}


class MuraliRouter:
    """Read-only access to VenuOrchestrator MURALI phase → department name.

    Uses DIW unpack (per CLAUDE.md: "DIW consumers MUST use diw.unpack()").
    Reads THE_FLUTE_CYCLE at current venu position, unpacks MURALI bits.

    If VenuOrchestrator is unavailable, uses fallback_tick (heartbeat_count)
    to cycle through all 4 departments.
    """

    def current_department(self, fallback_tick: int = 0) -> str:
        """Read current MURALI phase → department name via DIW unpack.

        Args:
            fallback_tick: Used to cycle departments when VenuOrchestrator
                is unavailable. Typically heartbeat_count.
        """
        try:
            from vibe_core.mahamantra import mahamantra
            from vibe_core.mahamantra.protocols.diw import unpack
            from vibe_core.mahamantra.substrate.vm.venu_orchestrator import THE_FLUTE_CYCLE

            venu = mahamantra.venu
            if venu is not None:
                position = venu.tick % WORDS
                diw = THE_FLUTE_CYCLE[position]
                murali = unpack(diw).murali
                return _MURALI_DEPARTMENTS.get(murali, "execution")
        except Exception as e:
            logger.warning(f"VenuOrchestrator/DIW access failed, using fallback_tick: {e}")

        # Fallback: cycle through departments using fallback_tick
        murali = fallback_tick % QUARTERS
        return _MURALI_DEPARTMENTS.get(murali, "execution")

    def should_prioritize(self, task: str, fallback_tick: int = 0) -> bool:
        """Does this task match the current MURALI phase?"""
        return task == self.current_department(fallback_tick)
