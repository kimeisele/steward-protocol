"""MURALI Department Routing — heartbeat_count → department cycle.

Extracted from agency_director.py. Pure read-only router, no state mutation.

NOTE: This was previously wired to VenuOrchestrator DIW unpack, but
THE_FLUTE_CYCLE encodes MURALI in blocks of 4 (0,0,0,0,1,1,1,1,...).
With 4 heartbeats per GH Actions run, all 4 landed in the same quarter
(typically GENESIS). This meant DHARMA/KARMA/MOKSHA never executed —
the agent produced zero content for months.

Fix: use heartbeat_count % 4 directly. Each heartbeat = one department.
4 heartbeats = 1 full MURALI rotation. Simple, correct, deterministic.
"""

import logging

from vibe_core.mahamantra.substrate.core.seed import QUARTERS

logger = logging.getLogger("MOLTBOOK_MURALI")

# MURALI 4-bit phase (0-3) → department name
_MURALI_DEPARTMENTS = (
    "research",  # 0 GENESIS: scan, discover, extract topics
    "planning",  # 1 DHARMA: evaluate strategy, prioritize topics
    "execution",  # 2 KARMA: generate content, publish
    "learning",  # 3 MOKSHA: track engagement, analyze patterns
)


class MuraliRouter:
    """Cycle through 4 MURALI departments using heartbeat_count.

    Each heartbeat = one department. 4 heartbeats = 1 full rotation.
    heartbeat_count % 4 → 0=research, 1=planning, 2=execution, 3=learning.

    Previous design used DIW unpack from VenuOrchestrator, but THE_FLUTE_CYCLE
    encodes MURALI in blocks of 4. VenuOrchestrator resets to tick=0 each
    Python process start (GH Actions), so 4 heartbeats covered positions 0-3
    which ALL map to MURALI=0 (GENESIS). DHARMA/KARMA/MOKSHA never ran.
    """

    def current_department(self, fallback_tick: int = 0) -> str:
        """Map heartbeat count to department name.

        Args:
            fallback_tick: heartbeat_count — cycles through departments.
        """
        idx = fallback_tick % QUARTERS
        return _MURALI_DEPARTMENTS[idx]

    def should_prioritize(self, task: str, fallback_tick: int = 0) -> bool:
        """Does this task match the current MURALI phase?"""
        return task == self.current_department(fallback_tick)
