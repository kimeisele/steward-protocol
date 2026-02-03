"""
GIT LAB - Echte Git-Analyse mit MahaCompression
================================================

Analysiert ECHTEN CONTENT (Diffs, Paths), nicht zufällige Hashes.
MahaCompression extrahiert INTENT aus dem Code.
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
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


@dataclass
class CommitIntent:
    """Ein Commit mit Intent-Analyse."""

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


@dataclass
class IntentReport:
    """Aggregierte Intent-Analyse."""

    total: int
    by_guna: Dict[str, int]
    by_position: Dict[int, int]
    by_author_guna: Dict[str, Dict[str, int]]
    hotspots: Dict[str, int]  # Most changed files


class GitLab:
    """
    Git Research Lab - Production MahaCompression.

    Analysiert:
    1. Diff content -> Intent (TAMAS/RAJAS/SATTVA/SUDDHA)
    2. File paths -> Lotus position
    3. Aggregiert patterns
    """

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo = Path(repo_path) if repo_path else Path.cwd()
        self.compressor = MahaCompression()

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

                # Compress the DIFF CONTENT (not the hash!)
                content = f"{message}\n{diff}"
                compression = self.compressor.compress(content)

                results.append(
                    CommitIntent(
                        hash=hash_[:8],
                        author=author,
                        date=date,
                        message=message[:60],
                        files=files[:5],  # Top 5 files
                        diff_size=diff_size,
                        guna=compression.intent_level.guna.value,
                        seed=compression.seed,
                        position=compression.position,
                    )
                )
            except Exception as e:
                # Skip problematic commits
                continue

        return results

    def aggregate(self, commits: List[CommitIntent]) -> IntentReport:
        """Aggregiere Intent-Daten."""
        by_guna: Dict[str, int] = Counter()
        by_position: Dict[int, int] = Counter()
        by_author_guna: Dict[str, Dict[str, int]] = {}
        all_files: List[str] = []

        for c in commits:
            by_guna[c.guna] += 1
            by_position[c.position] += 1
            all_files.extend(c.files)

            if c.author not in by_author_guna:
                by_author_guna[c.author] = Counter()
            by_author_guna[c.author][c.guna] += 1

        hotspots = dict(Counter(all_files).most_common(10))

        return IntentReport(
            total=len(commits),
            by_guna=dict(by_guna),
            by_position=dict(by_position),
            by_author_guna={k: dict(v) for k, v in by_author_guna.items()},
            hotspots=hotspots,
        )

    def analyze(self, months: int = 6, limit: int = 100) -> IntentReport:
        """Full analysis."""
        commits = self.analyze_commits(months, limit)
        return self.aggregate(commits)

    def report(self, months: int = 6, limit: int = 100) -> str:
        """Generiere Report."""
        commits = self.analyze_commits(months, limit)
        agg = self.aggregate(commits)

        lines = [
            "=" * 70,
            f"GIT INTENT ANALYSIS - {months} Monate, {agg.total} Commits",
            "=" * 70,
            "",
            "GUNA DISTRIBUTION (Intent Quality):",
            f"  SUDDHA (pure/optimal):    {agg.by_guna.get('suddha', 0)}",
            f"  SATTVA (clean/stable):    {agg.by_guna.get('sattva', 0)}",
            f"  RAJAS (hacky/rushed):     {agg.by_guna.get('rajas', 0)}",
            f"  TAMAS (broken/corrupt):   {agg.by_guna.get('tamas', 0)}",
            "",
            "AUTHOR INTENT PROFILE:",
        ]

        for author, gunas in agg.by_author_guna.items():
            profile = ", ".join(f"{g}:{c}" for g, c in sorted(gunas.items()))
            lines.append(f"  {author}: {profile}")

        lines.extend(
            [
                "",
                "LOTUS POSITION DISTRIBUTION (0-15):",
            ]
        )

        # Show top positions
        for pos in sorted(agg.by_position.keys()):
            count = agg.by_position[pos]
            bar = "#" * min(count, 30)
            lines.append(f"  {pos:2d}: {bar} ({count})")

        lines.extend(
            [
                "",
                "FILE HOTSPOTS (most changed):",
            ]
        )
        for fname, count in list(agg.hotspots.items())[:10]:
            lines.append(f"  {count:3d}x {fname}")

        lines.extend(
            [
                "",
                "-" * 70,
                "RECENT COMMITS (with intent):",
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
            lines.append(f"  {guna_symbol} [{c.guna:6s}] {c.date} {c.message}")

        lines.append("=" * 70)
        return "\n".join(lines)

    def print_report(self, months: int = 6, limit: int = 100) -> None:
        """Print to stdout."""
        print(self.report(months, limit))
