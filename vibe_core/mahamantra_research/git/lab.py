"""
GIT LAB - Echte Git-Analyse mit MahaMantra Computation
======================================================

Analysiert ECHTEN CONTENT (Diffs, Paths), nicht zufällige Hashes.

INTEGRATION:
    - MahaCompression: Intent extraction (TAMAS/RAJAS/SATTVA/SUDDHA)
    - MahaResonator: Attractor finding (fixed point vs cycle)
    - GitaResonance: Verse matching from attractors
    - 65536 buckets: Full 16^4 position space

"yad yad vibhūtimat sattvaṁ śrīmad ūrjitam eva vā
 tat tad evāvagaccha tvaṁ mama tejo-'ṁśa-sambhavam" (BG 10.41)
"""

__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x87cc2df2"

import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.adapters.gita_resonance import GitaResonance, MatchResult, VerseMatch
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, PARAMPARA, WORDS
from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator, ResonanceResult

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

# 16^4 = 65536 intent buckets (full Mahamantra position space)
INTENT_BUCKETS = WORDS**4


@dataclass
class CommitIntent:
    """Ein Commit mit full MahaMantra computation."""

    hash: str
    author: str
    date: str
    message: str
    files: List[str]
    diff_size: int
    # MahaCompression results
    guna: str  # TAMAS/RAJAS/SATTVA/SUDDHA
    seed: int
    position: int  # 0-15 in lotus
    # MahaResonator results
    attractor: int  # Computed attractor (136=VAIKUNTHA or cycle)
    cycles_to_converge: int
    cycle_length: int  # 1 = fixed point, >1 = samsara cycle
    trajectory_class: str  # "vaikuntha" or "samsara"
    # GitaResonance results
    verse_id: Optional[str] = None  # e.g., "BG.18.66"
    verse_guna: Optional[str] = None
    verse_dominant: Optional[str] = None  # HARE/KRISHNA/RAMA


@dataclass
class IntentReport:
    """Aggregierte Intent-Analyse mit full MahaMantra computation."""

    total: int
    by_guna: Dict[str, int]
    by_position: Dict[int, int]
    by_author_guna: Dict[str, Dict[str, int]]
    hotspots: Dict[str, int]  # Most changed files
    # MahaResonator aggregates
    by_trajectory: Dict[str, int]  # vaikuntha vs samsara
    by_attractor: Dict[int, int]
    avg_cycles_to_converge: float
    # GitaResonance aggregates
    by_verse_chapter: Dict[int, int]  # Which chapters resonate
    by_verse_guna: Dict[str, int]
    by_dominant_name: Dict[str, int]  # HARE/KRISHNA/RAMA distribution


class GitLab:
    """
    Git Research Lab - Full MahaMantra Computation.

    INTEGRATES:
    1. MahaCompression: Diff content -> Intent (TAMAS/RAJAS/SATTVA/SUDDHA)
    2. MahaResonator: Seed -> Attractor (VAIKUNTHA vs SAMSARA)
    3. GitaResonance: Attractor -> Gita verse matching
    4. 65536 buckets: Full position space utilization

    NO STATIC FOLDER MAPPING. All values COMPUTED at runtime from 7 axioms.
    """

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo = Path(repo_path) if repo_path else Path.cwd()
        self.compressor = MahaCompression()
        self.resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        self.gita = GitaResonance()

    def _git(self, *args: str, timeout: int = 30) -> str:
        """Run git command."""
        cmd = ["git", "-C", str(self.repo)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()

    def get_commit_with_diff(self, commit_hash: str) -> Tuple[str, List[str], int]:
        """Hole diff und files für einen commit."""
        # Get diff content
        diff = self._git("show", "--format=", "--stat", commit_hash)
        diff_full = self._git("show", "--format=", "-p", commit_hash)

        # Parse files from stat
        files = []
        for line in diff.split("\n"):
            if "|" in line:
                fname = line.split("|")[0].strip()
                if fname:
                    files.append(fname)

        return diff_full, files, len(diff_full)

    def analyze_commits(self, months: int = 6, limit: int = 100) -> List[CommitIntent]:
        """
        Analysiere commits mit MahaCompression.

        Args:
            months: Zeitraum
            limit: Max commits (Diffs sind teuer)
        """
        # Get commit list
        output = self._git(
            "log", f"--since={months} months ago", f"-n{limit}", "--format=%H|%an|%ad|%s", "--date=short"
        )

        results = []
        for line in output.split("\n"):
            if not line.strip():
                continue

            parts = line.split("|", 3)
            if len(parts) < 4:
                continue

            hash_, author, date, message = parts

            try:
                diff, files, diff_size = self.get_commit_with_diff(hash_)

                # 1. MahaCompression: DIFF CONTENT -> Intent
                content = f"{message}\n{diff}"
                compression = self.compressor.compress(content)

                # 2. MahaResonator: Seed -> Attractor
                resonance = self.resonator.find_attractor(compression.seed)
                trajectory_class = "vaikuntha" if resonance.attractor == 136 else "samsara"

                # 3. GitaResonance: Attractor -> Verse
                gita_result = self.gita.match(resonance.attractor)
                verse_id = None
                verse_guna = None
                verse_dominant = None
                if gita_result.best_match:
                    verse_id = gita_result.best_match.verse_id
                    verse_guna = gita_result.best_match.guna
                    verse_dominant = gita_result.best_match.dominant_name

                results.append(
                    CommitIntent(
                        hash=hash_[:8],
                        author=author,
                        date=date,
                        message=message[:60],
                        files=files[:5],  # Top 5 files
                        diff_size=diff_size,
                        # MahaCompression
                        guna=compression.intent_level.guna.value,
                        seed=compression.seed,
                        position=compression.position,
                        # MahaResonator
                        attractor=resonance.attractor,
                        cycles_to_converge=resonance.cycles_to_converge,
                        cycle_length=resonance.cycle_length,
                        trajectory_class=trajectory_class,
                        # GitaResonance
                        verse_id=verse_id,
                        verse_guna=verse_guna,
                        verse_dominant=verse_dominant,
                    )
                )
            except Exception as e:
                # Skip problematic commits
                continue

        return results

    def aggregate(self, commits: List[CommitIntent]) -> IntentReport:
        """Aggregiere Intent-Daten with full MahaMantra computation."""
        by_guna: Dict[str, int] = Counter()
        by_position: Dict[int, int] = Counter()
        by_author_guna: Dict[str, Dict[str, int]] = {}
        all_files: List[str] = []

        # MahaResonator aggregates
        by_trajectory: Dict[str, int] = Counter()
        by_attractor: Dict[int, int] = Counter()
        total_cycles = 0

        # GitaResonance aggregates
        by_verse_chapter: Dict[int, int] = Counter()
        by_verse_guna: Dict[str, int] = Counter()
        by_dominant_name: Dict[str, int] = Counter()

        for c in commits:
            by_guna[c.guna] += 1
            by_position[c.position] += 1
            all_files.extend(c.files)

            if c.author not in by_author_guna:
                by_author_guna[c.author] = Counter()
            by_author_guna[c.author][c.guna] += 1

            # MahaResonator
            by_trajectory[c.trajectory_class] += 1
            by_attractor[c.attractor] += 1
            total_cycles += c.cycles_to_converge

            # GitaResonance
            if c.verse_id:
                # Extract chapter from verse_id (e.g., "BG.18.66" -> 18)
                parts = c.verse_id.split(".")
                if len(parts) >= 2:
                    try:
                        chapter = int(parts[1])
                        by_verse_chapter[chapter] += 1
                    except ValueError:
                        pass
            if c.verse_guna:
                by_verse_guna[c.verse_guna] += 1
            if c.verse_dominant:
                by_dominant_name[c.verse_dominant] += 1

        hotspots = dict(Counter(all_files).most_common(10))
        avg_cycles = total_cycles / len(commits) if commits else 0.0

        return IntentReport(
            total=len(commits),
            by_guna=dict(by_guna),
            by_position=dict(by_position),
            by_author_guna={k: dict(v) for k, v in by_author_guna.items()},
            hotspots=hotspots,
            # MahaResonator
            by_trajectory=dict(by_trajectory),
            by_attractor=dict(by_attractor),
            avg_cycles_to_converge=avg_cycles,
            # GitaResonance
            by_verse_chapter=dict(by_verse_chapter),
            by_verse_guna=dict(by_verse_guna),
            by_dominant_name=dict(by_dominant_name),
        )

    def analyze(self, months: int = 6, limit: int = 100) -> IntentReport:
        """Full analysis."""
        commits = self.analyze_commits(months, limit)
        return self.aggregate(commits)

    def report(self, months: int = 6, limit: int = 100) -> str:
        """Generiere Report with full MahaMantra computation."""
        commits = self.analyze_commits(months, limit)
        agg = self.aggregate(commits)

        lines = [
            "=" * 70,
            f"GIT MAHAMANTRA ANALYSIS - {months} Monate, {agg.total} Commits",
            "=" * 70,
            "",
            "┌─────────────────────────────────────────────────────────────────────┐",
            "│ INTENT DISTRIBUTION (MahaCompression)                               │",
            "├─────────────────────────────────────────────────────────────────────┤",
            f"│  SUDDHA (pure/optimal):    {agg.by_guna.get('suddha', 0):5d}                               │",
            f"│  SATTVA (clean/stable):    {agg.by_guna.get('sattva', 0):5d}                               │",
            f"│  RAJAS (hacky/rushed):     {agg.by_guna.get('rajas', 0):5d}                               │",
            f"│  TAMAS (broken/corrupt):   {agg.by_guna.get('tamas', 0):5d}                               │",
            "└─────────────────────────────────────────────────────────────────────┘",
            "",
            "┌─────────────────────────────────────────────────────────────────────┐",
            "│ TRAJECTORY CLASSIFICATION (MahaResonator)                           │",
            "├─────────────────────────────────────────────────────────────────────┤",
        ]

        vaikuntha = agg.by_trajectory.get("vaikuntha", 0)
        samsara = agg.by_trajectory.get("samsara", 0)
        total = vaikuntha + samsara if (vaikuntha + samsara) > 0 else 1
        vaikuntha_pct = (vaikuntha / total) * 100
        samsara_pct = (samsara / total) * 100

        lines.extend(
            [
                f"│  VAIKUNTHA (→136, fixed):  {vaikuntha:5d} ({vaikuntha_pct:5.1f}%)                       │",
                f"│  SAMSARA (→4-cycle):       {samsara:5d} ({samsara_pct:5.1f}%)                       │",
                f"│  Avg cycles to converge:   {agg.avg_cycles_to_converge:5.1f}                               │",
                "└─────────────────────────────────────────────────────────────────────┘",
                "",
                "┌─────────────────────────────────────────────────────────────────────┐",
                "│ GITA RESONANCE DISTRIBUTION                                         │",
                "├─────────────────────────────────────────────────────────────────────┤",
            ]
        )

        # Dominant name distribution (HARE/KRISHNA/RAMA)
        hare = agg.by_dominant_name.get("HARE", 0)
        krishna = agg.by_dominant_name.get("KRISHNA", 0)
        rama = agg.by_dominant_name.get("RAMA", 0)
        lines.extend(
            [
                f"│  HARE (INPUT/LOAD):        {hare:5d}                                   │",
                f"│  KRISHNA (COMPUTE):        {krishna:5d}                                   │",
                f"│  RAMA (OUTPUT/STORE):      {rama:5d}                                   │",
                "├─────────────────────────────────────────────────────────────────────┤",
            ]
        )

        # Top resonant chapters
        top_chapters = sorted(agg.by_verse_chapter.items(), key=lambda x: -x[1])[:5]
        lines.append("│  Top resonant chapters:                                            │")
        for ch, count in top_chapters:
            lines.append(f"│    Chapter {ch:2d}: {count:4d} commits                                     │")
        lines.append("└─────────────────────────────────────────────────────────────────────┘")

        # Author profiles
        lines.extend(
            [
                "",
                "AUTHOR INTENT PROFILE:",
            ]
        )
        for author, gunas in agg.by_author_guna.items():
            profile = ", ".join(f"{g}:{c}" for g, c in sorted(gunas.items()))
            lines.append(f"  {author}: {profile}")

        # Lotus positions
        lines.extend(
            [
                "",
                "LOTUS POSITION DISTRIBUTION (0-15):",
            ]
        )
        for pos in sorted(agg.by_position.keys()):
            count = agg.by_position[pos]
            bar = "█" * min(count, 30)
            lines.append(f"  {pos:2d}: {bar} ({count})")

        # Hotspots
        lines.extend(
            [
                "",
                "FILE HOTSPOTS (most changed):",
            ]
        )
        for fname, count in list(agg.hotspots.items())[:10]:
            lines.append(f"  {count:3d}x {fname}")

        # Recent commits with full analysis
        lines.extend(
            [
                "",
                "-" * 70,
                "RECENT COMMITS (with full MahaMantra analysis):",
                "-" * 70,
            ]
        )

        for c in commits[:20]:
            guna_symbol = {
                "suddha": "★",
                "sattva": "●",
                "rajas": "◐",
                "tamas": "○",
            }.get(c.guna, "?")
            traj_symbol = "⬆" if c.trajectory_class == "vaikuntha" else "⟳"
            verse = c.verse_id or "---"
            lines.append(f"  {guna_symbol}{traj_symbol} [{c.guna:6s}] {c.date} {c.message[:40]}")
            lines.append(f"       → {verse} | attractor={c.attractor} | cycles={c.cycles_to_converge}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def print_report(self, months: int = 6, limit: int = 100) -> None:
        """Print to stdout."""
        print(self.report(months, limit))
