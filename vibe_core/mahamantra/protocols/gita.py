from typing import Protocol, runtime_checkable, Tuple, Optional
from vibe_core.mahamantra.protocols._seed import GITA_CHAPTERS
from dataclasses import dataclass


@runtime_checkable
class GitaResonanceProtocol(Protocol):
    """
    Protocol for GitaResonance: Computed Response via Verse Matching.

    Responsible for matching Attractors (Int) to Gita Verses (Wisdom).
    """

    def match(self, attractor: int) -> "MatchResult":
        """Match by attractor value."""
        ...

    def match_chapter(self, chapter: int) -> "MatchResult":
        """Match by chapter number."""
        ...

    def match_verse(self, chapter: int, verse: int) -> "MatchResult":
        """Match specific verse."""
        ...


@dataclass(frozen=True)
class VerseMatch:
    """A matched verse."""

    verse_id: str
    chapter: int
    verse: int
    attractor: int
    guna: str
    dominant_name: str
    resonance_hare: float
    resonance_krishna: float
    resonance_rama: float
    phonetic_hash: str
    position: int
    text: Optional[str] = None


@dataclass(frozen=True)
class MatchResult:
    """Result of a resonance match."""

    query_attractor: int
    query_type: str
    matches: Tuple[VerseMatch, ...]

    @property
    def best_match(self) -> Optional[VerseMatch]:
        return self.matches[0] if self.matches else None


# Aliases for backward compatibility
VerseResult = VerseMatch
ChapterResult = MatchResult


@dataclass(frozen=True)
class ResonanceStats:
    """Statistics about the resonance index."""

    total_verses: int = 700
    total_chapters: int = GITA_CHAPTERS
    unique_attractors: int = 0
    avg_resonance_hare: float = 0.0
    avg_resonance_krishna: float = 0.0
    avg_resonance_rama: float = 0.0
