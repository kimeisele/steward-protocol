"""
Git Renderer (History).
Ported from GitHistoryPluginV2.

UNIFIED UI: Implements generate_content() pattern.
"""

import logging
import re
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_GIT")

# Auto-generated files to EXCLUDE from meaningful analysis
AUTO_GENERATED_FILES = {
    "OPERATIONS.md",
    "AGENTS.md",
    "TASKS.md",
    "CITYMAP.md",
    "HELP.md",
    "SETTINGS.md",
    "ENVOY.md",
    "DASHBOARD.md",
    "INDEX.md",
    "RAG.md",
    "EPHEMERAL.md",
    "STEWARD.md",
    "MATRIX.md",
    "QUESTIONS.md",
    "GIT.md",  # Don't analyze ourselves!
    "data/registry/citizens.json",
    "scripts/governance/kernel_hashes.json",
}

AUTO_GENERATED_PATTERNS = [
    r"test_output.*\.txt$",
    r".*\.log$",
    r"vibe_snapshot\.json$",
]


@dataclass
class CommitInfo:
    """Enhanced commit analysis."""

    hash: str
    author: str
    timestamp: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int
    files: List[str]

    # Semantic analysis
    is_meaningful: bool = True  # False if only auto-generated files
    affected_subsystems: Set[str] = field(default_factory=set)
    risk_level: str = "low"  # low, medium, high, critical


@dataclass
class SubsystemHealth:
    """Health metrics for a subsystem (e.g., kernel, plugins, tests)."""

    name: str
    commit_count: int
    net_lines_changed: int
    files: Set[str]
    last_changed: datetime
    risk_level: str  # stable, evolving, volatile, critical


@dataclass
class GitAnalysisV2:
    """Intelligent git repository analysis."""

    # Time window
    start_date: datetime
    end_date: datetime
    days_analyzed: int

    # Filtered commit stats (MEANINGFUL commits only)
    total_commits: int
    meaningful_commits: int  # Excludes auto-gen only commits
    commits_per_day: float
    commits_per_hour: float

    # Code stats (MEANINGFUL files only)
    total_insertions: int
    total_deletions: int
    net_change: int
    files_changed: int

    # Pattern detection
    refactoring_commits: int
    feature_commits: int
    fix_commits: int
    docs_commits: int
    test_commits: int

    # NEW: Semantic analysis
    architecture_changes: int  # Commits affecting core architecture
    breaking_changes: int  # Commits with "BREAKING" or major refactors
    plugin_additions: int  # New plugins added

    # Subsystem health
    subsystems: Dict[str, SubsystemHealth]

    # Top contributors
    authors: Dict[str, int]

    # Meaningful file heatmap (auto-gen EXCLUDED)
    top_files: Dict[str, int]

    # Recent meaningful activity
    commits: List[CommitInfo]

    # Health metrics
    commit_velocity_trend: str
    large_commit_count: int
    merge_commit_count: int

    # NEW: Risk assessment
    overall_risk: str  # low, medium, high, critical
    risk_factors: List[str]  # Specific concerns

    # NEW: Recommendations
    actionable_insights: List[str]


class GitAnalyzerV2:
    """Intelligent git analyzer with semantic understanding."""

    @staticmethod
    def is_auto_generated(filename: str) -> bool:
        """Check if file is auto-generated and should be excluded."""
        if filename in AUTO_GENERATED_FILES:
            return True

        for pattern in AUTO_GENERATED_PATTERNS:
            if re.match(pattern, filename):
                return True

        return False

    @staticmethod
    def classify_file(filename: str) -> Set[str]:
        """Classify file into subsystems."""
        subsystems = set()

        if filename.startswith("vibe_core/kernel"):
            subsystems.add("kernel")
        elif filename.startswith("vibe_core/plugins/"):
            subsystems.add("plugins")
        elif filename.startswith("vibe_core/protocols/"):
            subsystems.add("protocols")
        elif filename.startswith("vibe_core/cartridges/system/"):
            subsystems.add("system_agents")
        elif filename.startswith("vibe_core/cartridges/agent_city/"):
            subsystems.add("citizen_agents")
        elif filename.startswith("tests/"):
            subsystems.add("tests")
        elif filename.startswith("docs/"):
            subsystems.add("docs")
        elif filename.startswith("scripts/"):
            subsystems.add("scripts")
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            subsystems.add("config")

        return subsystems

    @staticmethod
    def assess_commit_risk(commit: CommitInfo) -> str:
        """Assess risk level of a commit."""
        # Critical risk
        if "kernel" in commit.affected_subsystems and commit.insertions + commit.deletions > 200:
            return "critical"

        if any(kw in commit.message.lower() for kw in ["breaking", "dangerous", "critical"]):
            return "critical"

        # High risk
        if commit.insertions + commit.deletions > 1000:
            return "high"

        if "protocols" in commit.affected_subsystems and commit.insertions + commit.deletions > 100:
            return "high"

        # Medium risk
        if commit.insertions + commit.deletions > 500:
            return "medium"

        # Low risk (default)
        return "low"

    @staticmethod
    def get_commit_history(days: int = 7, path: Path = Path(".")) -> List[CommitInfo]:
        """Get commit history with semantic analysis."""
        since = datetime.now() - timedelta(days=days)
        since_str = since.strftime("%Y-%m-%d")

        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={since_str}",
                    "--pretty=format:%H|%an|%at|%s",
                    "--numstat",
                ],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            commits = []
            current_commit = None
            current_files = []

            for line in result.stdout.splitlines():
                if "|" in line and not line.startswith(" "):
                    # Save previous commit
                    if current_commit:
                        # Filter auto-generated files
                        meaningful_files = [f for f in current_files if not GitAnalyzerV2.is_auto_generated(f)]

                        # Mark commit as meaningful only if it has non-auto-gen files
                        current_commit.is_meaningful = len(meaningful_files) > 0

                        # Classify affected subsystems
                        for f in meaningful_files:
                            current_commit.affected_subsystems.update(GitAnalyzerV2.classify_file(f))

                        # Assess risk
                        current_commit.risk_level = GitAnalyzerV2.assess_commit_risk(current_commit)

                        current_commit.files = current_files
                        commits.append(current_commit)
                        current_files = []

                    # Parse new commit
                    parts = line.split("|")
                    if len(parts) >= 4:
                        current_commit = CommitInfo(
                            hash=parts[0],
                            author=parts[1],
                            timestamp=datetime.fromtimestamp(int(parts[2])),
                            message=parts[3],
                            files_changed=0,
                            insertions=0,
                            deletions=0,
                            files=[],
                        )
                elif line.strip() and current_commit:
                    # File stat line
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        try:
                            insertions = int(parts[0]) if parts[0] != "-" else 0
                            deletions = int(parts[1]) if parts[1] != "-" else 0
                            filename = parts[2]

                            # Always count ALL files for completeness
                            current_commit.insertions += insertions
                            current_commit.deletions += deletions
                            current_commit.files_changed += 1
                            current_files.append(filename)
                        except ValueError:
                            pass

            # Add last commit
            if current_commit:
                meaningful_files = [f for f in current_files if not GitAnalyzerV2.is_auto_generated(f)]
                current_commit.is_meaningful = len(meaningful_files) > 0
                for f in meaningful_files:
                    current_commit.affected_subsystems.update(GitAnalyzerV2.classify_file(f))
                current_commit.risk_level = GitAnalyzerV2.assess_commit_risk(current_commit)
                current_commit.files = current_files
                commits.append(current_commit)

            return commits

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Failed to get git history: {e}")
            return []

    @staticmethod
    def analyze_commits(commits: List[CommitInfo], days: int) -> GitAnalysisV2:
        """Analyze commits with semantic intelligence."""
        if not commits:
            return GitAnalysisV2(
                start_date=datetime.now() - timedelta(days=days),
                end_date=datetime.now(),
                days_analyzed=days,
                total_commits=0,
                meaningful_commits=0,
                commits_per_day=0.0,
                commits_per_hour=0.0,
                total_insertions=0,
                total_deletions=0,
                net_change=0,
                files_changed=0,
                refactoring_commits=0,
                feature_commits=0,
                fix_commits=0,
                docs_commits=0,
                test_commits=0,
                architecture_changes=0,
                breaking_changes=0,
                plugin_additions=0,
                subsystems={},
                authors={},
                top_files={},
                commits=[],
                commit_velocity_trend="unknown",
                large_commit_count=0,
                merge_commit_count=0,
                overall_risk="low",
                risk_factors=[],
                actionable_insights=[],
            )

        # Filter meaningful commits
        meaningful = [c for c in commits if c.is_meaningful]
        total_commits = len(commits)
        meaningful_commits = len(meaningful)

        # Stats (ONLY meaningful commits)
        total_insertions = sum(c.insertions for c in meaningful)
        total_deletions = sum(c.deletions for c in meaningful)
        net_change = total_insertions - total_deletions

        # Author stats
        authors: Dict[str, int] = defaultdict(int)
        for c in meaningful:
            authors[c.author] += 1

        # File stats (EXCLUDE auto-generated)
        file_changes: Dict[str, int] = defaultdict(int)
        for c in meaningful:
            for f in c.files:
                if not GitAnalyzerV2.is_auto_generated(f):
                    file_changes[f] += 1

        top_files = dict(sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:15])

        # Pattern detection
        refactoring = sum(
            1
            for c in meaningful
            if any(kw in c.message.lower() for kw in ["refactor", "extract", "consolidate", "cleanup", "simplify"])
        )
        feature = sum(1 for c in meaningful if any(kw in c.message.lower() for kw in ["feat", "add", "implement"]))
        fix = sum(1 for c in meaningful if any(kw in c.message.lower() for kw in ["fix", "bug", "error"]))
        docs = sum(1 for c in meaningful if any(kw in c.message.lower() for kw in ["docs", "readme", "doc"]))
        test_commits = sum(1 for c in meaningful if any(kw in c.message.lower() for kw in ["test", "spec", "coverage"]))

        # NEW: Semantic patterns
        architecture_changes = sum(
            1 for c in meaningful if "kernel" in c.affected_subsystems or "protocols" in c.affected_subsystems
        )
        breaking_changes = sum(1 for c in meaningful if "breaking" in c.message.lower() or c.risk_level == "critical")
        plugin_additions = sum(
            1
            for c in meaningful
            if "vibe_core/plugins/" in " ".join(c.files)
            and any(kw in c.message.lower() for kw in ["add", "new", "create"])
        )

        # Subsystem health
        subsystems: Dict[str, SubsystemHealth] = {}
        for c in meaningful:
            for subsystem in c.affected_subsystems:
                if subsystem not in subsystems:
                    subsystems[subsystem] = SubsystemHealth(
                        name=subsystem,
                        commit_count=0,
                        net_lines_changed=0,
                        files=set(),
                        last_changed=c.timestamp,
                        risk_level="stable",
                    )

                subsystems[subsystem].commit_count += 1
                subsystems[subsystem].net_lines_changed += c.insertions - c.deletions
                subsystems[subsystem].files.update(f for f in c.files if not GitAnalyzerV2.is_auto_generated(f))
                if c.timestamp > subsystems[subsystem].last_changed:
                    subsystems[subsystem].last_changed = c.timestamp

        # Assess subsystem risk
        for subsystem in subsystems.values():
            if subsystem.commit_count > 50:
                subsystem.risk_level = "volatile"
            elif subsystem.commit_count > 20:
                subsystem.risk_level = "evolving"
            else:
                subsystem.risk_level = "stable"

        # Health metrics
        large_commits = sum(1 for c in meaningful if (c.insertions + c.deletions) > 500)
        merge_commits = sum(1 for c in meaningful if c.message.lower().startswith("merge"))

        # Velocity trend
        mid = len(meaningful) // 2
        first_half = meaningful[:mid]
        second_half = meaningful[mid:]
        trend = "stable"
        if len(second_half) > len(first_half) * 1.2:
            trend = "increasing"
        elif len(second_half) < len(first_half) * 0.8:
            trend = "decreasing"

        # Risk assessment
        risk_factors = []
        overall_risk = "low"

        if meaningful_commits / days > 50:
            risk_factors.append("Very high commit velocity (>50/day) - potential burnout risk")
            overall_risk = "high"
        elif meaningful_commits / days > 30:
            risk_factors.append("High commit velocity (>30/day) - monitor for quality")
            overall_risk = "medium" if overall_risk == "low" else overall_risk

        if large_commits > meaningful_commits * 0.3:
            risk_factors.append(f"Many large commits ({large_commits}/{meaningful_commits}) - scope creep risk")
            overall_risk = "high"

        if architecture_changes > meaningful_commits * 0.2:
            risk_factors.append(f"Frequent architecture changes ({architecture_changes} commits) - stability risk")
            overall_risk = "medium" if overall_risk == "low" else overall_risk

        if test_commits < meaningful_commits * 0.05:
            risk_factors.append(f"Low test coverage ({test_commits} test commits) - quality risk")
            overall_risk = "medium" if overall_risk == "low" else overall_risk

        # Actionable insights
        insights = []

        if not risk_factors:
            insights.append("✅ Repository health is GOOD - no major concerns detected")

        if refactoring > feature * 1.5:
            insights.append("🔧 Refactoring phase detected - ensure new features don't get blocked")

        if fix > feature * 1.5:
            insights.append("🐛 Bug-fixing phase detected - consider root cause analysis")

        if "kernel" in subsystems and subsystems["kernel"].risk_level == "volatile":
            insights.append("⚠️ Kernel is VOLATILE - freeze features and stabilize core")

        if "plugins" in subsystems and subsystems["plugins"].commit_count > 30:
            insights.append("📦 Plugin ecosystem is GROWING - document plugin architecture")

        if "tests" in subsystems and subsystems["tests"].commit_count < meaningful_commits * 0.1:
            insights.append("🧪 Test infrastructure LAGGING - prioritize test coverage")

        return GitAnalysisV2(
            start_date=min(c.timestamp for c in commits),
            end_date=max(c.timestamp for c in commits),
            days_analyzed=days,
            total_commits=total_commits,
            meaningful_commits=meaningful_commits,
            commits_per_day=meaningful_commits / days if days > 0 else 0,
            commits_per_hour=meaningful_commits / (days * 24) if days > 0 else 0,
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            net_change=net_change,
            files_changed=len(file_changes),
            refactoring_commits=refactoring,
            feature_commits=feature,
            fix_commits=fix,
            docs_commits=docs,
            test_commits=test_commits,
            architecture_changes=architecture_changes,
            breaking_changes=breaking_changes,
            plugin_additions=plugin_additions,
            subsystems=subsystems,
            authors=dict(authors),
            top_files=top_files,
            commits=meaningful,  # Only meaningful commits
            commit_velocity_trend=trend,
            large_commit_count=large_commits,
            merge_commit_count=merge_commits,
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            actionable_insights=insights,
        )


class GitMarkdownRendererV2:
    """Renders INTELLIGENT GIT.md."""

    @staticmethod
    def render_to_string(analysis: GitAnalysisV2) -> str:
        """Render comprehensive GIT.md content (does NOT write - returns string)."""

        # Risk emoji
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }

        content = f"""# Git Repository Analysis

> "Git history is the memory of the system - understand it to improve" - Srimad DevOps Purana

**Analysis Period**: {analysis.start_date.strftime("%Y-%m-%d")} to {analysis.end_date.strftime("%Y-%m-%d")} ({analysis.days_analyzed} days)

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Overall Health**: {risk_emoji.get(analysis.overall_risk, "⚪")} **{analysis.overall_risk.upper()}**

---

## 🎯 Executive Summary

**Meaningful Work Done**: {analysis.meaningful_commits} commits ({analysis.total_commits - analysis.meaningful_commits} auto-generated excluded)

**Key Metrics**:
- **Velocity**: {analysis.commits_per_day:.1f} commits/day ({analysis.commit_velocity_trend.upper()} trend)
- **Net Code Change**: {analysis.net_change:+,} lines
- **Subsystems Affected**: {len(analysis.subsystems)}

**Work Breakdown**:
- 🐛 Bug Fixes: {analysis.fix_commits} ({analysis.fix_commits / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0:.1f}%)
- ✨ Features: {analysis.feature_commits} ({analysis.feature_commits / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0:.1f}%)
- 🔧 Refactoring: {analysis.refactoring_commits} ({analysis.refactoring_commits / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0:.1f}%)
- 📝 Documentation: {analysis.docs_commits} ({analysis.docs_commits / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0:.1f}%)
- ✅ Tests: {analysis.test_commits} ({analysis.test_commits / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0:.1f}%)

---

## 🚨 Risk Assessment

"""

        if analysis.risk_factors:
            for factor in analysis.risk_factors:
                content += f"- {risk_emoji.get(analysis.overall_risk, '⚪')} {factor}\n"
        else:
            content += "- ✅ No major risks detected\n"

        content += """
---

## 💡 Actionable Insights

"""

        for insight in analysis.actionable_insights:
            content += f"{insight}\n\n"

        content += """
---

## 🏗️ Subsystem Health

| Subsystem | Commits | Net Lines | Files | Status | Last Changed |
|-----------|---------|-----------|-------|--------|--------------|
"""

        for name, subsystem in sorted(analysis.subsystems.items(), key=lambda x: x[1].commit_count, reverse=True):
            status_emoji = {"stable": "🟢", "evolving": "🟡", "volatile": "🟠", "critical": "🔴"}
            content += f"| `{name}` | {subsystem.commit_count} | {subsystem.net_lines_changed:+,} | {len(subsystem.files)} | {status_emoji.get(subsystem.risk_level, '⚪')} {subsystem.risk_level.upper()} | {subsystem.last_changed.strftime('%m-%d')} |\n"

        content += f"""
---

## 📊 Detailed Statistics

### Code Changes (Meaningful Files Only)

| Metric | Value |
|--------|-------|
| Total Commits | {analysis.total_commits} |
| Meaningful Commits | {analysis.meaningful_commits} |
| Auto-Generated (Excluded) | {analysis.total_commits - analysis.meaningful_commits} |
| Files Changed | {analysis.files_changed} |
| Lines Added | +{analysis.total_insertions:,} |
| Lines Removed | -{analysis.total_deletions:,} |
| Net Change | {analysis.net_change:+,} |

### Special Events

| Type | Count |
|------|-------|
| 🏗️ Architecture Changes | {analysis.architecture_changes} |
| ⚠️ Breaking Changes | {analysis.breaking_changes} |
| 📦 Plugin Additions | {analysis.plugin_additions} |
| 📏 Large Commits (>500 lines) | {analysis.large_commit_count} |
| 🔀 Merge Commits | {analysis.merge_commit_count} |

---

## 👥 Top Contributors

| Author | Commits | % of Total |
|--------|---------|-----------|
"""

        top_authors = sorted(analysis.authors.items(), key=lambda x: x[1], reverse=True)[:5]
        for author, count in top_authors:
            pct = count / analysis.meaningful_commits * 100 if analysis.meaningful_commits > 0 else 0
            content += f"| {author} | {count} | {pct:.1f}% |\n"

        content += """
---

## 🔥 File Change Heatmap (Auto-Generated EXCLUDED)

| File | Changes | Subsystem |
|------|---------|-----------|
"""

        for file, count in list(analysis.top_files.items())[:15]:
            bar = "█" * min(count, 20)
            subsystems = GitAnalyzerV2.classify_file(file)
            subsystem_str = ", ".join(subsystems) if subsystems else "other"
            content += f"| `{file}` | {bar} {count} | {subsystem_str} |\n"

        content += """
---

## 📜 Recent Meaningful Activity (Last 20 Commits)

| Date | Author | Message | Changes | Risk |
|------|--------|---------|---------|------|
"""

        for commit in analysis.commits[:20]:
            msg = commit.message[:50] + "..." if len(commit.message) > 50 else commit.message
            changes = f"+{commit.insertions}/-{commit.deletions}"
            date_str = commit.timestamp.strftime("%m-%d %H:%M")
            risk = risk_emoji.get(commit.risk_level, "⚪")
            content += f"| {date_str} | {commit.author} | {msg} | {changes} | {risk} |\n"

        content += """
---

## 🎛️ Configuration

**Analysis Settings**:
- Time Window: 7 days (configurable)
- Update Frequency: Every 50 kernel ticks (configurable)
- Auto-Generated Files: EXCLUDED from analysis

**Excluded Files** (auto-generated):
- OPERATIONS.md, AGENTS.md, TASKS.md, CITYMAP.md, HELP.md, SETTINGS.md
- ENVOY.md, DASHBOARD.md, INDEX.md, RAG.md, EPHEMERAL.md
- citizens.json, kernel_hashes.json, test_output*.txt

**To force update**: `kernel.plugins['interface'].renderers['git'].force_update()`

---

*Generated by GitHistoryPlugin V2 - Part of the Steward Protocol*
"""
        return content


class GitRenderer(BaseRenderer):
    """
    Git Renderer (History).
    Renders GIT.md with intelligent repository analysis.
    """

    def __init__(self, kernel: "RealVibeKernel", analysis_days: int = 7, update_interval_seconds: int = 300):
        super().__init__(kernel)
        self.analysis_days = analysis_days
        self.update_interval = update_interval_seconds
        self.last_update = 0.0
        self.analyzer = GitAnalyzerV2()
        self.renderer = GitMarkdownRendererV2()
        self.last_analysis: Optional[GitAnalysisV2] = None

        # Initial check
        if (
            not subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5,
            ).returncode
            == 0
        ):
            logger.warning("⚠️  Not a git repository - GitRenderer disabled")
            self.disabled = True
        else:
            self.disabled = False
            logger.info(f"📊 GitRenderer initialized (analyzing last {self.analysis_days} days)")

        self._register_data_sources()

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        self.register_data_source("git.status", self._get_git_status)
        self.register_data_source("git.log", self._get_git_log)

    def _get_git_status(self) -> Dict:
        """Get git status for status section."""
        if self.disabled:
            return {"status": "disabled", "message": "Not a git repository"}
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return {
                "clean": len(lines) == 0,
                "modified": len([l for l in lines if l.startswith(" M") or l.startswith("M ")]),
                "untracked": len([l for l in lines if l.startswith("??")]),
                "staged": len([l for l in lines if l.startswith("A ") or l.startswith("M ")]),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_git_log(self) -> List[Dict]:
        """Get recent commits for log section."""
        if self.disabled:
            return [{"hash": "-", "message": "Git disabled", "author": "-"}]
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%h|%s|%an"], capture_output=True, text=True, timeout=5
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 2)
                    commits.append(
                        {
                            "Hash": parts[0] if len(parts) > 0 else "?",
                            "Message": parts[1][:50] if len(parts) > 1 else "?",
                            "Author": parts[2] if len(parts) > 2 else "?",
                        }
                    )
            return commits if commits else [{"Hash": "-", "Message": "No commits", "Author": "-"}]
        except Exception as e:
            return [{"Hash": "-", "Message": str(e), "Author": "-"}]

    def render(self) -> None:
        """Render GIT.md using config-driven sections."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    @property
    def name(self) -> str:
        return "git"

    @property
    def output_file(self) -> str:
        return "GIT.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate GIT.md content (UNIFIED UI pattern)."""
        if self.disabled:
            return None

        # Throttle updates (default 5 minutes)
        now = time.time()
        if now - self.last_update < self.update_interval:
            # Return cached analysis if available
            if self.last_analysis:
                return self.renderer.render_to_string(self.last_analysis)
            return None

        self.last_update = now

        try:
            commits = self.analyzer.get_commit_history(days=self.analysis_days)
            analysis = self.analyzer.analyze_commits(commits, self.analysis_days)
            self.last_analysis = analysis
            return self.renderer.render_to_string(analysis)
        except Exception as e:
            logger.error(f"Git analysis failed: {e}")
            return None

    def force_update(self) -> None:
        """Force immediate update on next render cycle."""
        logger.info("🔄 Scheduled forced git analysis update")
        self.last_update = 0.0
