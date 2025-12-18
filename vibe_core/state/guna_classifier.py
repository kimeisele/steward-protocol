"""
OPUS-106: GunaClassifier - State Tri-Guna Diagnosis

"All state oscillates through three modes. This is NATURAL."

The Tri-Guna (Three Qualities) from Samkhya philosophy:
- SATTVA (सत्त्व): Balance, harmony, purity - state is synced, clean
- RAJAS (रजस्): Activity, passion, change - state is dirty, transforming
- TAMAS (तमस्): Inertia, darkness, stagnation - state is stale, broken, dead

This classifier diagnoses the current Guna of any state path and provides
metrics for system health monitoring.

NOTE: This is about STATE oscillation, not about agents.
See OPUS-086 for agent-level Guna classification.
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("GUNA_CLASSIFIER")


# =============================================================================
# Enums and Data Classes
# =============================================================================


class StateGuna(Enum):
    """
    The three modes of state (Tri-Guna for State).

    SATTVA: Balance - synced, clean, at rest
    RAJAS: Activity - dirty, changing, active
    TAMAS: Inertia - stale, broken, ignored, dead
    """

    SATTVA = "sattva"  # Balance - synced, clean
    RAJAS = "rajas"  # Activity - dirty, changing
    TAMAS = "tamas"  # Inertia - stale, broken, ignored


class TamasReason(Enum):
    """Specific reasons why state is classified as Tamas."""

    MISSING = "missing"  # Path doesn't exist
    IGNORED = "gitignored"  # In .gitignore (LOBOTOMY!)
    CORRUPT = "corrupt"  # Can't read/parse
    STALE = "stale"  # Too old (>threshold)
    LOCKED = "locked"  # Has lock file
    ORPHANED = "orphaned"  # No plugin claims it
    EMPTY = "empty"  # Exists but empty


@dataclass
class GunaThresholds:
    """Configurable thresholds for Guna classification."""

    stale_days: float = 7.0  # Days without modification -> Tamas
    max_age_hours: float = 168  # 7 days in hours
    min_file_size: int = 2  # Bytes - smaller is "empty"


@dataclass
class GunaClassification:
    """Result of classifying a state path."""

    path: Path
    guna: StateGuna
    reason: Optional[str] = None
    tamas_reason: Optional[TamasReason] = None
    confidence: float = 1.0
    age_hours: Optional[float] = None
    content_hash: Optional[str] = None
    is_dirty: bool = False
    is_ignored: bool = False
    last_modified: Optional[float] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/API."""
        return {
            "path": str(self.path),
            "guna": self.guna.value,
            "reason": self.reason,
            "tamas_reason": self.tamas_reason.value if self.tamas_reason else None,
            "confidence": self.confidence,
            "age_hours": self.age_hours,
            "is_dirty": self.is_dirty,
            "is_ignored": self.is_ignored,
            "file_size": self.file_size,
        }


@dataclass
class SystemGunaReport:
    """Aggregate Guna report for the entire system."""

    timestamp: float
    total_paths: int
    sattva_count: int
    rajas_count: int
    tamas_count: int
    classifications: List[GunaClassification]
    tamas_paths: List[Path] = field(default_factory=list)
    health_score: float = 0.0  # 0.0 = all Tamas, 1.0 = all Sattva

    @property
    def guna_distribution(self) -> Dict[str, float]:
        """Get percentage distribution of Gunas."""
        if self.total_paths == 0:
            return {"sattva": 0.0, "rajas": 0.0, "tamas": 0.0}
        return {
            "sattva": self.sattva_count / self.total_paths,
            "rajas": self.rajas_count / self.total_paths,
            "tamas": self.tamas_count / self.total_paths,
        }


# =============================================================================
# Main Class: GunaClassifier
# =============================================================================


class GunaClassifier:
    """
    State Tri-Guna Classifier.

    Diagnoses the current Guna of state paths and provides system health metrics.

    The classifier looks at:
    - File existence and readability
    - Git tracking status (is it ignored? LOBOTOMY!)
    - Age/staleness
    - Content validity (can it be parsed?)
    - Dirty status (uncommitted changes)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        thresholds: Optional[GunaThresholds] = None,
        git_state: Optional[Any] = None,
    ):
        """
        Initialize the classifier.

        Args:
            workspace: Root workspace path
            thresholds: Custom thresholds for classification
            git_state: Optional GitState instance for dirty/ignored checks
        """
        self.workspace = workspace or Path.cwd()
        self.thresholds = thresholds or GunaThresholds()
        self.git_state = git_state
        self._gitignore_patterns: Optional[List[str]] = None
        logger.info("[GUNA] Classifier initialized")

    # =========================================================================
    # Main API
    # =========================================================================

    def classify(self, path: Path) -> GunaClassification:
        """
        Classify a single state path.

        Args:
            path: Path to classify

        Returns:
            GunaClassification with diagnosis
        """
        # Make path absolute if relative
        if not path.is_absolute():
            path = self.workspace / path

        # Start building classification
        classification = GunaClassification(path=path, guna=StateGuna.SATTVA)

        # === TAMAS CHECKS (ordered by severity) ===

        # Check 1: Does it exist?
        if not path.exists():
            return self._classify_tamas(path, TamasReason.MISSING, "Path does not exist")

        # Check 2: Is it gitignored? (LOBOTOMY!)
        if self._is_ignored(path):
            return self._classify_tamas(path, TamasReason.IGNORED, "Path is in .gitignore (LOBOTOMY!)")

        # Check 3: Can we read it?
        if not self._is_readable(path):
            return self._classify_tamas(path, TamasReason.CORRUPT, "Path is not readable (corrupt)")

        # Check 4: Is it empty?
        file_size = self._get_size(path)
        if file_size is not None and file_size < self.thresholds.min_file_size:
            return self._classify_tamas(path, TamasReason.EMPTY, f"File is too small ({file_size} bytes)")

        # Check 5: Is it stale?
        age_hours = self._get_age_hours(path)
        if age_hours is not None and age_hours > self.thresholds.max_age_hours:
            return self._classify_tamas(path, TamasReason.STALE, f"File is stale ({age_hours:.1f} hours old)")

        # Check 6: Is there a lock file?
        if self._has_lock(path):
            return self._classify_tamas(path, TamasReason.LOCKED, "File is locked")

        # === RAJAS CHECK ===

        # Check 7: Is it dirty (uncommitted changes)?
        is_dirty = self._is_dirty(path)
        if is_dirty:
            classification.guna = StateGuna.RAJAS
            classification.reason = "Has uncommitted changes"
            classification.is_dirty = True

        # === SATTVA (default if nothing else) ===
        else:
            classification.guna = StateGuna.SATTVA
            classification.reason = "Clean and synced"

        # Add metadata
        classification.age_hours = age_hours
        classification.file_size = file_size
        classification.last_modified = self._get_mtime(path)
        classification.content_hash = self._get_hash(path)
        classification.is_ignored = False

        return classification

    def classify_many(self, paths: List[Path]) -> List[GunaClassification]:
        """
        Classify multiple paths.

        Args:
            paths: List of paths to classify

        Returns:
            List of classifications
        """
        return [self.classify(path) for path in paths]

    def generate_report(self, paths: List[Path]) -> SystemGunaReport:
        """
        Generate a system-wide Guna report.

        Args:
            paths: All state paths in the system

        Returns:
            SystemGunaReport with aggregate metrics
        """
        classifications = self.classify_many(paths)

        sattva_count = sum(1 for c in classifications if c.guna == StateGuna.SATTVA)
        rajas_count = sum(1 for c in classifications if c.guna == StateGuna.RAJAS)
        tamas_count = sum(1 for c in classifications if c.guna == StateGuna.TAMAS)

        tamas_paths = [c.path for c in classifications if c.guna == StateGuna.TAMAS]

        # Health score: Sattva = 1.0, Rajas = 0.5, Tamas = 0.0
        total = len(classifications)
        if total > 0:
            health_score = (sattva_count * 1.0 + rajas_count * 0.5) / total
        else:
            health_score = 1.0  # No paths = healthy

        return SystemGunaReport(
            timestamp=time.time(),
            total_paths=total,
            sattva_count=sattva_count,
            rajas_count=rajas_count,
            tamas_count=tamas_count,
            classifications=classifications,
            tamas_paths=tamas_paths,
            health_score=health_score,
        )

    # =========================================================================
    # Helpers
    # =========================================================================

    def _classify_tamas(self, path: Path, reason: TamasReason, message: str) -> GunaClassification:
        """Create a Tamas classification."""
        return GunaClassification(
            path=path,
            guna=StateGuna.TAMAS,
            reason=message,
            tamas_reason=reason,
            confidence=1.0,
            is_ignored=(reason == TamasReason.IGNORED),
        )

    def _is_ignored(self, path: Path) -> bool:
        """Check if path is in .gitignore."""
        # Try git state first
        if self.git_state and hasattr(self.git_state, "check_ignore"):
            try:
                return self.git_state.check_ignore(path)
            except Exception:
                pass

        # Fallback: manual check
        if self._gitignore_patterns is None:
            self._load_gitignore_patterns()

        try:
            path_str = str(path.relative_to(self.workspace))
        except ValueError:
            path_str = str(path)

        for pattern in self._gitignore_patterns or []:
            if not pattern or pattern.startswith("#"):
                continue
            # Simple pattern matching
            if pattern in path_str:
                return True
            try:
                if path.match(pattern):
                    return True
            except Exception:
                pass

        return False

    def _load_gitignore_patterns(self) -> None:
        """Load .gitignore patterns."""
        gitignore = self.workspace / ".gitignore"
        if gitignore.exists():
            try:
                self._gitignore_patterns = gitignore.read_text().splitlines()
            except Exception:
                self._gitignore_patterns = []
        else:
            self._gitignore_patterns = []

    def _is_readable(self, path: Path) -> bool:
        """Check if path can be read without errors."""
        try:
            if path.is_file():
                path.read_bytes()
            elif path.is_dir():
                list(path.iterdir())
            return True
        except Exception:
            return False

    def _get_size(self, path: Path) -> Optional[int]:
        """Get file size in bytes."""
        try:
            if path.is_file():
                return path.stat().st_size
            return None
        except Exception:
            return None

    def _get_mtime(self, path: Path) -> Optional[float]:
        """Get modification time."""
        try:
            return path.stat().st_mtime
        except Exception:
            return None

    def _get_age_hours(self, path: Path) -> Optional[float]:
        """Get age in hours since last modification."""
        mtime = self._get_mtime(path)
        if mtime is None:
            return None
        return (time.time() - mtime) / 3600

    def _get_hash(self, path: Path) -> Optional[str]:
        """Get content hash (first 16 chars of SHA256)."""
        try:
            if path.is_file():
                content = path.read_bytes()
                return hashlib.sha256(content).hexdigest()[:16]
            return None
        except Exception:
            return None

    def _has_lock(self, path: Path) -> bool:
        """Check if path has an associated lock file."""
        lock_patterns = [
            path.with_suffix(path.suffix + ".lock"),
            path.parent / f".{path.name}.lock",
            path.parent / "index.lock" if "git" in str(path) else None,
        ]
        return any(lock and lock.exists() for lock in lock_patterns if lock)

    def _is_dirty(self, path: Path) -> bool:
        """Check if path has uncommitted changes."""
        if self.git_state:
            try:
                if hasattr(self.git_state, "is_path_dirty"):
                    return self.git_state.is_path_dirty(path)
                elif hasattr(self.git_state, "is_dirty"):
                    # Fall back to general dirty check
                    return self.git_state.is_dirty()
            except Exception:
                pass
        return False


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "GunaClassifier",
    "StateGuna",
    "TamasReason",
    "GunaThresholds",
    "GunaClassification",
    "SystemGunaReport",
]
