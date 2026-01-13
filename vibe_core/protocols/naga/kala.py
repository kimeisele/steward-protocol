"""
KALA PROTOCOL - The Timekeeper (Layer 0)

"Kalo 'smi loka-ksaya-krt pravrddho" - Time I am, the great destroyer of worlds.

SCOPE:
This protocol defines the Cyclical Nature of Time (Yugas) within the System Runtime.
It does NOT track wall-clock time. It tracks ENTROPY and LIFECYCLE.

THE 4 YUGAS (System States):
1. SATYA (Golden): Boot / Clean State. 100% Dharma (4 Legs).
2. TRETA (Silver): Initialization / Allocation. 75% Dharma (3 Legs).
3. DVAPARA (Bronze): Operation / Service. 50% Dharma (2 Legs).
4. KALI (Iron): Degradation / High Load. 25% Dharma (1 Leg - Mercy).

WATERTIGHT STANDARD:
- Protocol First (Dependency Inversion).
- Typed Enums (No Strings).
- Deterministic State Transitions.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x6e43006e"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable

# =============================================================================
# TYPES & ENUMS (The Vocabulary of Time)
# =============================================================================


class Yuga(str, Enum):
    """The 4 Ages of the System Lifecycle."""

    SATYA = "satya"  # Boot / Meditation / Clean
    TRETA = "treta"  # Setup / Yajna / Allocation
    DVAPARA = "dvapara"  # Run / Worship / Service
    KALI = "kali"  # Decay / Sankirtana / Error Handling

    # Special: The Golden Age within Kali (10,000 commits)
    CAITANYA_ERA = "caitanya_era"


class TimeQuality(str, Enum):
    """The Quality (Guna) of the current moment."""

    SATTVA = "sattva"  # Goodness / Clarity (Satya/Treta)
    RAJAS = "rajas"  # Passion / Activity (Dvapara)
    TAMAS = "tamas"  # Ignorance / Inertia (Kali)


@dataclass
class TimeContext:
    """Snippet of Time State."""

    yuga: Yuga
    dharma_legs: int
    uptime_seconds: float
    entropy_level: float  # 0.0 to 1.0
    quality: TimeQuality
    recommended_process: str


# =============================================================================
# KALA PROTOCOL (The Interface)
# =============================================================================


@runtime_checkable
class KalaProtocol(Protocol):
    """
    The Protocol of Time.

    Any component that claims to track Time must implement this.
    """

    def get_current_yuga(self) -> Yuga:
        """Determine the current Yuga based on Entropy/Uptime."""
        ...

    def get_dharma_legs(self) -> int:
        """
        How many legs of Dharma are standing?
        Satya=4, Treta=3, Dvapara=2, Kali=1.
        """
        ...

    def get_time_context(self) -> TimeContext:
        """Get the full context of the current moment."""
        ...

    def is_action_permitted(self, cost: str) -> bool:
        """
        Is this action permitted in the current Yuga?
        E.g. Expensive Yajnas (Transactions) are forbidden in Kali.
        """
        ...


# =============================================================================
# NULL IMPLEMENTATION (The Void)
# =============================================================================


class NullKala:
    """The Void - Time does not exist."""

    def get_current_yuga(self) -> Yuga:
        return Yuga.KALI  # Assert Worst Case (Safety)

    def get_dharma_legs(self) -> int:
        return 1

    def get_time_context(self) -> TimeContext:
        return TimeContext(
            yuga=Yuga.KALI,
            dharma_legs=1,
            uptime_seconds=0.0,
            entropy_level=1.0,
            quality=TimeQuality.TAMAS,
            recommended_process="CHANT",
        )

    def is_action_permitted(self, cost: str) -> bool:
        return False  # Nothing permitted in Void


# =============================================================================
# KALA TIMEKEEPER (The Implementation)
# =============================================================================


class KalaTimeKeeper:
    """
    The Industrial Timekeeper.

    Determines Yuga based on Process Uptime and Entropy (Error Rate).
    """

    def __init__(self, start_time: Optional[datetime] = None):
        self._start_time = start_time or datetime.now()
        # Thresholds (in seconds) for Yuga transitions (LITERAL process lifecycle)
        # The Yugas ARE the process phases, not metaphors for them.
        self._satya_duration = 10.0  # Boot phase
        self._treta_duration = 60.0  # Init phase
        self._dvapara_duration = 3600.0  # Run phase

    def _calculate_uptime(self) -> float:
        return (datetime.now() - self._start_time).total_seconds()

    def get_current_yuga(self) -> Yuga:
        uptime = self._calculate_uptime()

        if uptime < self._satya_duration:
            return Yuga.SATYA
        elif uptime < self._treta_duration:
            return Yuga.TRETA
        elif uptime < self._dvapara_duration:
            return Yuga.DVAPARA
        else:
            return Yuga.KALI

    def get_dharma_legs(self) -> int:
        yuga = self.get_current_yuga()
        if yuga == Yuga.SATYA:
            return 4
        if yuga == Yuga.TRETA:
            return 3
        if yuga == Yuga.DVAPARA:
            return 2
        return 1

    def get_time_context(self) -> TimeContext:
        yuga = self.get_current_yuga()

        # Determine Quality
        quality = TimeQuality.SATTVA
        if yuga == Yuga.DVAPARA:
            quality = TimeQuality.RAJAS
        if yuga == Yuga.KALI:
            quality = TimeQuality.TAMAS

        # Determine Process
        process = "MEDITATION"
        if yuga == Yuga.TRETA:
            process = "YAJNA"
        if yuga == Yuga.DVAPARA:
            process = "WORSHIP"
        if yuga == Yuga.KALI:
            process = "SANKIRTANA"

        return TimeContext(
            yuga=yuga,
            dharma_legs=self.get_dharma_legs(),
            uptime_seconds=self._calculate_uptime(),
            entropy_level=0.0,  # Placeholder for real entropy
            quality=quality,
            recommended_process=process,
        )

    def is_action_permitted(self, cost: str) -> bool:
        """
        Permission Logic:
        - HIGH cost (Yajna) only in Satya/Treta.
        - MEDIUM cost (Worship) in Dvapara.
        - LOW cost (Chant) always.
        """
        yuga = self.get_current_yuga()
        cost = cost.upper()

        if cost == "HIGH":
            return yuga in (Yuga.SATYA, Yuga.TRETA)
        if cost == "MEDIUM":
            return yuga != Yuga.KALI

        return True  # LOW cost always allowed
