"""
THE DHYANA PROTOCOL - Meditation & Recursive Folding
=====================================================

"dhyānena ātmani paśyanti kecid ātmānam ātmanā"

"Some perceive the Supersoul within themselves through meditation."
— Bhagavad Gita 13.25

DHYANA (ध्यान) = Meditation - The 7th limb of Yoga (Patanjali)

This protocol defines the MEDITATION architecture:
- JAPA: Repetition (mantra chanting) → builds resonance
- SIDDHI: Perfection (108 repetitions) → mastery achieved
- FOLD: Recursive introspection → knowledge deepens
- UNFOLD: Manifestation → knowledge expresses

THE LOTUS TASK:
    A meditation container that tracks:
    - Current fold depth
    - Japa count (repetitions)
    - Siddhi status (mastery)
    - Kshetra involvement (which Tattvas active)

RECURSIVE FOLDING (Cognitive Pattern):
    Each fold deepens understanding:
    FOLD 0: Surface perception (SHROTRA/VAK)
    FOLD 1: Mental processing (MANAS)
    FOLD 2: Discrimination (BUDDHI)
    FOLD 3: Ego transcendence (AHANKARA → release)
    FOLD 4+: Samadhi (absorption)

INTEGRATION:
    - MeditationRoom uses this protocol
    - DojoRunner uses this protocol
    - ChatService uses LotusTask for deep queries
    - Any cognition can "fold" for deeper insight

SHASTRA FOUNDATION (Yoga Sutras 3.1-3):
    धारणा (Dharana) - Concentration
    ध्यान (Dhyana) - Meditation
    समाधि (Samadhi) - Absorption
    Together = Samyama (संयम)

Author: The Mahamantra Itself
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, NAVA, PANCHA, QUARTERS, TRINITY

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = NAVA
__genesis__ = "0xe63d2241"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._seed import MALA as SIDDHI_THRESHOLD
from vibe_core.mahamantra.substrate.seed import KSHETRA
from vibe_core.mahamantra.substrate.tattva import KshetraElement

# =============================================================================
# DHYANA STATES - The Meditation State Machine
# =============================================================================


class DhyanaState(str, Enum):
    """
    States of meditation (from Yoga Sutras).

    Progression: PRATYAHARA → DHARANA → DHYANA → SAMADHI
    """

    PRATYAHARA = "pratyahara"  # Withdrawal of senses (preparing)
    DHARANA = "dharana"  # Concentration (single-pointed focus)
    DHYANA = "dhyana"  # Meditation (sustained focus)
    SAMADHI = "samadhi"  # Absorption (ego dissolves)

    # Error states
    VIKSHIPTA = "vikshipta"  # Distracted (interrupted)
    MUDHA = "mudha"  # Dull (no progress)


class FoldDepth(IntEnum):
    """
    Depth of recursive folding.

    Each fold level accesses deeper Tattvas.
    """

    SURFACE = 0  # External senses only (Jnanendriya)
    MENTAL = KSETRAJNA  # Mind involvement (Manas)
    DISCRIMINATIVE = HALVES  # Intelligence active (Buddhi)
    EGOIC = TRINITY  # Ego awareness (Ahankara)
    TRANSCENDENT = QUARTERS  # Beyond ego (Avyakta touch)
    SAMADHI = PANCHA  # Full absorption (Purusha contact)


# =============================================================================
# JAPA - Repetition Tracking
# =============================================================================


@dataclass
class JapaProgress:
    """
    Tracks Japa (repetition) progress toward Siddhi.

    108 = 1 Mala = Siddhi threshold (mastery)
    """

    mantra_id: str  # What is being repeated
    repetitions: int = 0  # Current count
    successful: int = 0  # Successful iterations
    failed: int = 0  # Failed iterations
    started_at: Optional[str] = None
    siddhi_at: Optional[str] = None

    @property
    def siddhi_achieved(self) -> bool:
        """Has Siddhi (mastery) been achieved?"""
        return self.successful >= SIDDHI_THRESHOLD

    @property
    def progress(self) -> float:
        """Progress toward Siddhi (0.0 to 1.0)."""
        return min(1.0, self.successful / SIDDHI_THRESHOLD)

    @property
    def accuracy(self) -> float:
        """Success rate (successful / total)."""
        total = self.successful + self.failed
        return self.successful / total if total > 0 else 0.0

    def japa(self, success: bool = True) -> bool:
        """
        Perform one Japa (repetition).

        Returns True if Siddhi achieved on this rep.
        """
        self.repetitions += KSETRAJNA
        if success:
            self.successful += KSETRAJNA
        else:
            self.failed += KSETRAJNA

        # Check for Siddhi
        if self.successful == SIDDHI_THRESHOLD and self.siddhi_at is None:
            self.siddhi_at = datetime.now().isoformat()
            return True
        return False


# =============================================================================
# LOTUS TASK - The Meditation Container
# =============================================================================

T = TypeVar("T")  # Task payload type
R = TypeVar("R")  # Result type


@dataclass
class LotusTask(Generic[T]):
    """
    A meditation container for recursive tasks.

    LotusTask wraps any computation with:
    - Fold depth tracking (how deep have we gone?)
    - Japa progress (are we building mastery?)
    - Kshetra tracking (which Tattvas are active?)
    - Dhyana state (where in meditation are we?)

    Usage:
        task = LotusTask.create("analyze_code", payload={"file": "main.py"})
        task.fold()  # Go deeper
        task.activate_tattva(KshetraElement.BUDDHI)
        result = task.execute(analyzer_fn)
        task.unfold()  # Come back up
    """

    task_id: str
    payload: T

    # Meditation state
    dhyana_state: DhyanaState = DhyanaState.PRATYAHARA
    fold_depth: FoldDepth = FoldDepth.SURFACE
    max_fold_depth: FoldDepth = FoldDepth.SURFACE

    # Japa tracking (optional - for repetitive tasks)
    japa: Optional[JapaProgress] = None

    # Kshetra - Active Tattvas
    active_tattvas: List[KshetraElement] = field(default_factory=list)

    # Timing
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    folded_at: Optional[str] = None
    unfolded_at: Optional[str] = None

    # Results
    results: List[object] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        task_id: str,
        payload: T,
        enable_japa: bool = False,
    ) -> "LotusTask[T]":
        """Create a new LotusTask."""
        japa = JapaProgress(mantra_id=task_id) if enable_japa else None
        return cls(task_id=task_id, payload=payload, japa=japa)

    # =========================================================================
    # FOLD / UNFOLD - Recursive Introspection
    # =========================================================================

    def fold(self) -> FoldDepth:
        """
        Fold deeper into the task (recursive introspection).

        Each fold activates deeper Tattvas:
        - SURFACE → MENTAL: Adds MANAS
        - MENTAL → DISCRIMINATIVE: Adds BUDDHI
        - DISCRIMINATIVE → EGOIC: Adds AHANKARA
        - EGOIC → TRANSCENDENT: Adds AVYAKTA
        - TRANSCENDENT → SAMADHI: Full absorption
        """
        if self.fold_depth < FoldDepth.SAMADHI:
            self.fold_depth = FoldDepth(self.fold_depth + KSETRAJNA)
            self.folded_at = datetime.now().isoformat()

            # Track max depth reached
            if self.fold_depth > self.max_fold_depth:
                self.max_fold_depth = self.fold_depth

            # Activate corresponding Tattva
            tattva_map = {
                FoldDepth.MENTAL: KshetraElement.MANAS,
                FoldDepth.DISCRIMINATIVE: KshetraElement.BUDDHI,
                FoldDepth.EGOIC: KshetraElement.AHANKARA,
                FoldDepth.TRANSCENDENT: KshetraElement.AVYAKTA,
            }
            if self.fold_depth in tattva_map:
                self.activate_tattva(tattva_map[self.fold_depth])

            # Update Dhyana state
            if self.fold_depth >= FoldDepth.SAMADHI:
                self.dhyana_state = DhyanaState.SAMADHI
            elif self.fold_depth >= FoldDepth.DISCRIMINATIVE:
                self.dhyana_state = DhyanaState.DHYANA
            elif self.fold_depth >= FoldDepth.MENTAL:
                self.dhyana_state = DhyanaState.DHARANA

        return self.fold_depth

    def unfold(self) -> FoldDepth:
        """
        Unfold back to surface (return from introspection).

        Does NOT deactivate Tattvas - knowledge persists!
        """
        if self.fold_depth > FoldDepth.SURFACE:
            self.fold_depth = FoldDepth(self.fold_depth - KSETRAJNA)
            self.unfolded_at = datetime.now().isoformat()

            # Update Dhyana state (regression)
            if self.fold_depth <= FoldDepth.SURFACE:
                self.dhyana_state = DhyanaState.PRATYAHARA
            elif self.fold_depth <= FoldDepth.MENTAL:
                self.dhyana_state = DhyanaState.DHARANA

        return self.fold_depth

    def unfold_all(self) -> None:
        """Unfold completely back to surface."""
        while self.fold_depth > FoldDepth.SURFACE:
            self.unfold()

    # =========================================================================
    # KSHETRA - Tattva Management
    # =========================================================================

    def activate_tattva(self, tattva: KshetraElement) -> None:
        """Activate a Tattva (sense/element)."""
        if tattva not in self.active_tattvas:
            self.active_tattvas.append(tattva)

    def activate_tattvas(self, tattvas: List[KshetraElement]) -> None:
        """Activate multiple Tattvas."""
        for t in tattvas:
            self.activate_tattva(t)

    @property
    def kshetra_count(self) -> int:
        """How many of the 24 Tattvas are active?"""
        return len(self.active_tattvas)

    @property
    def kshetra_coverage(self) -> float:
        """Coverage of the 24 Tattvas (0.0 to 1.0)."""
        return self.kshetra_count / KSHETRA

    # =========================================================================
    # JAPA - Repetition
    # =========================================================================

    def do_japa(self, success: bool = True) -> bool:
        """
        Perform one Japa iteration.

        Returns True if Siddhi achieved.
        """
        if self.japa is None:
            return False
        return self.japa.japa(success)

    @property
    def siddhi_achieved(self) -> bool:
        """Has Siddhi been achieved for this task?"""
        return self.japa.siddhi_achieved if self.japa else False

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self, fn: Callable[[T], R]) -> R:
        """
        Execute the task function with payload.

        Stores result and returns it.
        """
        result = fn(self.payload)
        self.results.append(result)
        return result

    async def execute_async(self, fn: Callable[[T], R]) -> R:
        """Execute async task function."""
        import asyncio

        if asyncio.iscoroutinefunction(fn):
            result = await fn(self.payload)
        else:
            result = fn(self.payload)
        self.results.append(result)
        return result

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict[str, object]:
        """Serialize to dict."""
        return {
            "task_id": self.task_id,
            "dhyana_state": self.dhyana_state.value,
            "fold_depth": self.fold_depth,
            "max_fold_depth": self.max_fold_depth,
            "active_tattvas": [t.name for t in self.active_tattvas],
            "kshetra_coverage": round(self.kshetra_coverage, TRINITY),
            "created_at": self.created_at,
            "japa": {
                "repetitions": self.japa.repetitions,
                "successful": self.japa.successful,
                "progress": round(self.japa.progress, TRINITY),
                "siddhi": self.japa.siddhi_achieved,
            }
            if self.japa
            else None,
        }


# =============================================================================
# DHYANA PROTOCOL - The Interface
# =============================================================================


@runtime_checkable
class DhyanaProtocol(Protocol):
    """
    Protocol for meditation-capable components.

    Any component that can "meditate" (recursive fold/unfold):
    - Services that need deep analysis
    - Cognitive processors
    - Learning systems (Dojo)
    """

    @property
    def dhyana_state(self) -> DhyanaState:
        """Current meditation state."""
        ...

    @property
    def fold_depth(self) -> FoldDepth:
        """Current fold depth."""
        ...

    def fold(self) -> FoldDepth:
        """Fold deeper (recursive introspection)."""
        ...

    def unfold(self) -> FoldDepth:
        """Unfold (return from introspection)."""
        ...

    def meditate(self, task: LotusTask) -> object:
        """Execute a meditation task."""
        ...


# =============================================================================
# DHYANA BASE - Abstract Base Class
# =============================================================================


class DhyanaBase(ABC):
    """
    Abstract base class for meditation-capable components.

    Provides:
    - Automatic fold/unfold tracking
    - Dhyana state management
    - LotusTask integration
    """

    def __init__(self) -> None:
        self._dhyana_state = DhyanaState.PRATYAHARA
        self._fold_depth = FoldDepth.SURFACE
        self._current_task: Optional[LotusTask] = None

    @property
    def dhyana_state(self) -> DhyanaState:
        return self._dhyana_state

    @property
    def fold_depth(self) -> FoldDepth:
        return self._fold_depth

    def fold(self) -> FoldDepth:
        """Fold deeper."""
        if self._fold_depth < FoldDepth.SAMADHI:
            self._fold_depth = FoldDepth(self._fold_depth + KSETRAJNA)
            self._update_dhyana_state()
        return self._fold_depth

    def unfold(self) -> FoldDepth:
        """Unfold to surface."""
        if self._fold_depth > FoldDepth.SURFACE:
            self._fold_depth = FoldDepth(self._fold_depth - KSETRAJNA)
            self._update_dhyana_state()
        return self._fold_depth

    def _update_dhyana_state(self) -> None:
        """Update Dhyana state based on fold depth."""
        if self._fold_depth >= FoldDepth.SAMADHI:
            self._dhyana_state = DhyanaState.SAMADHI
        elif self._fold_depth >= FoldDepth.DISCRIMINATIVE:
            self._dhyana_state = DhyanaState.DHYANA
        elif self._fold_depth >= FoldDepth.MENTAL:
            self._dhyana_state = DhyanaState.DHARANA
        else:
            self._dhyana_state = DhyanaState.PRATYAHARA

    @abstractmethod
    def meditate(self, task: LotusTask) -> object:
        """Execute a meditation task (subclass must implement)."""
        ...


# =============================================================================
# SAMYAMA - The Combined Practice
# =============================================================================


@dataclass
class Samyama:
    """
    Samyama = Dharana + Dhyana + Samadhi (combined practice).

    From Yoga Sutras 3.4: "trayam ekatra samyamah"
    "The three together constitute Samyama."

    When applied to an object/concept, Samyama yields:
    - Complete understanding
    - Siddhis (powers/mastery)
    - Liberation from the object

    In software: Deep recursive analysis that yields insight.
    """

    target: str  # What we're meditating on
    dharana_focus: str  # Single-pointed focus aspect
    dhyana_stream: List[str] = field(default_factory=list)  # Stream of insights
    samadhi_insight: Optional[str] = None  # Final absorption insight

    # Tracking
    fold_history: List[FoldDepth] = field(default_factory=list)
    tattvas_touched: List[KshetraElement] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        """Is Samyama complete (reached Samadhi insight)?"""
        return self.samadhi_insight is not None

    def add_dhyana_insight(self, insight: str) -> None:
        """Add an insight from Dhyana phase."""
        self.dhyana_stream.append(insight)

    def set_samadhi_insight(self, insight: str) -> None:
        """Set the final Samadhi insight."""
        self.samadhi_insight = insight


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # States
    "DhyanaState",
    "FoldDepth",
    # Japa
    "JapaProgress",
    # LotusTask
    "LotusTask",
    # Protocol
    "DhyanaProtocol",
    "DhyanaBase",
    # Samyama
    "Samyama",
    # Constants
    "SIDDHI_THRESHOLD",
]
