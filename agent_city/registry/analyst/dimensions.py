"""
Multi-Dimensional Analysis Engine for ANALYST Agent.

Provides 4D context synthesis:
1. TEMPORAL  - Time-based patterns, velocity trends, rhythm
2. STRUCTURAL - Dependency graphs, coupling metrics, architecture
3. SEMANTIC  - Work classification, complexity, intent
4. PREDICTIVE - Related files, risk areas, recommendations

This is the DEEP analysis layer - not superficial commit counting.
RAG = Realtime Architecture Guide
"""

import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class GitInterface:
    """Low-level git command interface."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()

    def run(self, cmd: str) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=str(self.root_dir),
        )
        return result.stdout.strip()

    def run_format(self, format_str: str, since: Optional[str] = None, until: Optional[str] = None) -> List[str]:
        """Run git log with custom format."""
        cmd = f"log --pretty=format:{format_str}"
        if since:
            cmd += f" --since={since}"
        if until:
            cmd += f" --until={until}"
        output = self.run(cmd)
        return [line for line in output.split("\n") if line.strip()]


# =============================================================================
# DIMENSION 1: TEMPORAL
# =============================================================================


class TemporalDimension:
    """
    Temporal analysis - time-based patterns and rhythms.

    Provides:
    - Velocity trends (accelerating/decelerating)
    - Day-of-week patterns (when work happens)
    - Time-of-day patterns (work rhythms)
    - Activity bursts and quiet periods
    - Commit density analysis
    """

    def __init__(self, git: GitInterface):
        self.git = git

    def analyze_velocity_trend(self, periods: int = 4) -> Dict[str, Any]:
        """
        Analyze velocity trend over recent periods.

        Returns trend direction and momentum.
        """
        week_counts = []
        for i in range(periods):
            start = (datetime.now() - timedelta(weeks=i + 1)).strftime("%Y-%m-%d")
            end = (datetime.now() - timedelta(weeks=i)).strftime("%Y-%m-%d")

            cmd = f"rev-list --count HEAD --since={start} --until={end}"
            count = int(self.git.run(cmd) or "0")
            week_counts.append(count)

        # Calculate trend
        if len(week_counts) >= 2:
            recent = sum(week_counts[:2]) / 2
            older = sum(week_counts[2:]) / 2 if len(week_counts) > 2 else week_counts[0]

            if older == 0:
                trend_ratio = float("inf") if recent > 0 else 1.0
            else:
                trend_ratio = recent / older

            if trend_ratio > 1.3:
                trend = "ACCELERATING"
                momentum = "🚀"
            elif trend_ratio > 1.1:
                trend = "GROWING"
                momentum = "📈"
            elif trend_ratio < 0.7:
                trend = "DECELERATING"
                momentum = "📉"
            elif trend_ratio < 0.9:
                trend = "SLOWING"
                momentum = "🔻"
            else:
                trend = "STEADY"
                momentum = "➡️"
        else:
            trend = "INSUFFICIENT_DATA"
            momentum = "❓"
            trend_ratio = 1.0

        return {
            "weekly_counts": week_counts,
            "trend": trend,
            "momentum": momentum,
            "trend_ratio": round(trend_ratio, 2) if trend_ratio != float("inf") else "∞",
            "average_weekly": round(sum(week_counts) / len(week_counts), 1) if week_counts else 0,
        }

    def analyze_day_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze which days see most activity.

        Reveals work rhythm patterns.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get commits with day of week
        output = self.git.run(f"log --pretty=format:%ad --date=format:%A --since={since}")
        day_counts = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                day_counts[line.strip()] += 1

        # Order by day of week
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ordered = {day: day_counts.get(day, 0) for day in day_order}

        # Find peak and quiet days
        if ordered:
            peak_day = max(ordered.items(), key=lambda x: x[1])
            quiet_day = min(ordered.items(), key=lambda x: x[1])

            weekday_total = sum(ordered.get(d, 0) for d in day_order[:5])
            weekend_total = sum(ordered.get(d, 0) for d in day_order[5:])
        else:
            peak_day = ("Unknown", 0)
            quiet_day = ("Unknown", 0)
            weekday_total = 0
            weekend_total = 0

        return {
            "distribution": ordered,
            "peak_day": peak_day[0],
            "peak_count": peak_day[1],
            "quiet_day": quiet_day[0],
            "weekday_commits": weekday_total,
            "weekend_commits": weekend_total,
            "weekend_ratio": round(weekend_total / weekday_total, 2) if weekday_total > 0 else 0,
        }

    def analyze_hour_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze commit time patterns.

        Reveals working hours and rhythms.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        output = self.git.run(f"log --pretty=format:%ad --date=format:%H --since={since}")
        hour_counts = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                try:
                    hour = int(line.strip())
                    hour_counts[hour] += 1
                except ValueError:
                    pass

        # Categorize into periods
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))  # 6-11
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))  # 12-17
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))  # 18-23
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))  # 0-5

        total = morning + afternoon + evening + night
        if total > 0:
            if night > total * 0.3:
                work_style = "NIGHT_OWL"
            elif morning > afternoon:
                work_style = "EARLY_BIRD"
            elif evening > afternoon:
                work_style = "EVENING_CODER"
            else:
                work_style = "BUSINESS_HOURS"
        else:
            work_style = "UNKNOWN"

        # Find peak hour
        peak_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (12, 0)

        return {
            "hour_distribution": dict(sorted(hour_counts.items())),
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "night": night,
            "work_style": work_style,
            "peak_hour": peak_hour[0],
            "peak_hour_formatted": f"{peak_hour[0]:02d}:00",
        }

    def detect_activity_bursts(self, days: int = 30) -> Dict[str, Any]:
        """
        Detect bursts of high activity and quiet periods.

        Identifies sprints and downtime.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        output = self.git.run(f"log --pretty=format:%ad --date=format:%Y-%m-%d --since={since}")
        date_counts = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                date_counts[line.strip()] += 1

        if not date_counts:
            return {"bursts": [], "quiet_streaks": [], "avg_daily": 0}

        # Calculate stats
        counts = list(date_counts.values())
        avg = sum(counts) / len(counts)
        threshold_high = avg * 2
        threshold_low = avg * 0.3

        bursts = [(date, count) for date, count in date_counts.items() if count >= threshold_high]
        quiet = [(date, count) for date, count in date_counts.items() if count <= threshold_low]

        return {
            "average_daily_commits": round(avg, 1),
            "burst_days": sorted(bursts, key=lambda x: -x[1])[:5],
            "quiet_days": sorted(quiet, key=lambda x: x[1])[:5],
            "burst_threshold": round(threshold_high, 1),
            "total_active_days": len(date_counts),
        }

    def synthesize(self) -> Dict[str, Any]:
        """Synthesize full temporal dimension."""
        return {
            "velocity_trend": self.analyze_velocity_trend(),
            "day_patterns": self.analyze_day_patterns(),
            "hour_patterns": self.analyze_hour_patterns(),
            "activity_bursts": self.detect_activity_bursts(),
        }


# =============================================================================
# DIMENSION 2: STRUCTURAL
# =============================================================================


class StructuralDimension:
    """
    Structural analysis - architecture and dependencies.

    Provides:
    - Import dependency graphs
    - Module coupling metrics
    - Co-change patterns (files that change together)
    - Architectural hotspots
    - Package structure analysis
    """

    def __init__(self, git: GitInterface, root_dir: str = "."):
        self.git = git
        self.root_dir = Path(root_dir).resolve()

    def analyze_co_changes(self, days: int = 30, min_correlation: int = 3) -> Dict[str, Any]:
        """
        Analyze files that frequently change together.

        Reveals hidden coupling and dependencies.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get commits with their files
        output = self.git.run(f"log --pretty=format:COMMIT --name-only --since={since}")

        commits = []
        current_files: Set[str] = set()

        for line in output.split("\n"):
            if line == "COMMIT":
                if current_files:
                    commits.append(current_files)
                current_files = set()
            elif line.strip():
                current_files.add(line.strip())

        if current_files:
            commits.append(current_files)

        # Find co-occurrences
        co_changes: Dict[Tuple[str, str], int] = defaultdict(int)
        for file_set in commits:
            files = sorted(file_set)
            for i, f1 in enumerate(files):
                for f2 in files[i + 1 :]:
                    co_changes[(f1, f2)] += 1

        # Filter and sort
        significant = {k: v for k, v in co_changes.items() if v >= min_correlation}
        sorted_pairs = sorted(significant.items(), key=lambda x: -x[1])[:20]

        # Extract coupling clusters
        clusters: Dict[str, Set[str]] = defaultdict(set)
        for (f1, f2), count in sorted_pairs:
            clusters[f1].add(f2)
            clusters[f2].add(f1)

        # Find highest coupling
        coupling_scores = [(f, len(related)) for f, related in clusters.items()]
        coupling_scores.sort(key=lambda x: -x[1])

        return {
            "co_change_pairs": [(f"{a} ↔ {b}", count) for (a, b), count in sorted_pairs[:15]],
            "coupling_hotspots": coupling_scores[:10],
            "total_analyzed_commits": len(commits),
        }

    def analyze_import_graph(self, focus_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build import dependency graph for Python files.

        Returns dependency metrics and circular deps.
        """
        if focus_dirs is None:
            focus_dirs = ["steward", "vibe_core", "agent_city"]

        imports: Dict[str, List[str]] = {}
        import_pattern = re.compile(r"^(?:from\s+([\w.]+)|import\s+([\w.]+))")

        for focus_dir in focus_dirs:
            dir_path = self.root_dir / focus_dir
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    rel_path = str(py_file.relative_to(self.root_dir))

                    file_imports = []
                    for line in content.split("\n"):
                        match = import_pattern.match(line.strip())
                        if match:
                            module = match.group(1) or match.group(2)
                            # Only track internal imports
                            if module and any(module.startswith(d) for d in focus_dirs):
                                file_imports.append(module)

                    if file_imports:
                        imports[rel_path] = file_imports

                except Exception:
                    pass

        # Calculate metrics
        incoming: Dict[str, int] = defaultdict(int)
        outgoing: Dict[str, int] = defaultdict(int)

        for file, deps in imports.items():
            outgoing[file] = len(deps)
            for dep in deps:
                incoming[dep] += 1

        # Find architectural hubs (high incoming = depended upon)
        hubs = sorted(incoming.items(), key=lambda x: -x[1])[:10]

        # Find complexity indicators (high outgoing = depends on many)
        complex_files = sorted(outgoing.items(), key=lambda x: -x[1])[:10]

        return {
            "total_files_analyzed": len(imports),
            "architectural_hubs": hubs,
            "complex_files": complex_files,
            "total_internal_imports": sum(outgoing.values()),
        }

    def analyze_module_boundaries(self) -> Dict[str, Any]:
        """
        Analyze module boundaries and cross-module dependencies.

        Reveals architecture health.
        """
        # Get top-level modules
        modules = []
        for item in self.root_dir.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                if (item / "__init__.py").exists() or (item / "pyproject.toml").exists():
                    modules.append(item.name)

        # Count files per module
        module_stats = {}
        for module in modules:
            module_path = self.root_dir / module
            py_files = list(module_path.rglob("*.py"))
            yaml_files = list(module_path.rglob("*.yaml"))

            module_stats[module] = {
                "python_files": len(py_files),
                "yaml_files": len(yaml_files),
                "total_files": len(py_files) + len(yaml_files),
            }

        # Sort by size
        sorted_modules = sorted(module_stats.items(), key=lambda x: -x[1]["total_files"])

        return {
            "modules": dict(sorted_modules),
            "total_modules": len(modules),
            "largest_module": sorted_modules[0][0] if sorted_modules else None,
        }

    def synthesize(self) -> Dict[str, Any]:
        """Synthesize full structural dimension."""
        return {
            "co_changes": self.analyze_co_changes(),
            "import_graph": self.analyze_import_graph(),
            "module_boundaries": self.analyze_module_boundaries(),
        }


# =============================================================================
# DIMENSION 3: SEMANTIC
# =============================================================================


class SemanticDimension:
    """
    Semantic analysis - meaning and intent.

    Provides:
    - Commit type classification (feature/fix/refactor/docs/test)
    - Complexity indicators
    - Technical debt signals
    - Work category distribution
    """

    # Commit type patterns
    COMMIT_PATTERNS = {
        "feature": [r"^feat", r"^add", r"^implement", r"^new", r"^create"],
        "fix": [r"^fix", r"^bug", r"^resolve", r"^patch", r"^correct"],
        "refactor": [r"^refactor", r"^clean", r"^simplify", r"^extract", r"^move"],
        "docs": [r"^doc", r"^readme", r"^comment", r"^update.*doc"],
        "test": [r"^test", r"^spec", r"^coverage"],
        "chore": [r"^chore", r"^config", r"^ci", r"^build", r"^deps", r"^merge"],
        "style": [r"^style", r"^format", r"^lint"],
    }

    # Debt indicators in code
    DEBT_PATTERNS = [
        (r"TODO", "todo"),
        (r"FIXME", "fixme"),
        (r"HACK", "hack"),
        (r"XXX", "xxx"),
        (r"TEMP", "temp"),
        (r"DEPRECATED", "deprecated"),
    ]

    def __init__(self, git: GitInterface, root_dir: str = "."):
        self.git = git
        self.root_dir = Path(root_dir).resolve()

    def classify_commits(self, days: int = 30) -> Dict[str, Any]:
        """
        Classify commits by type based on message patterns.

        Reveals what kind of work is happening.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        output = self.git.run(f"log --pretty=format:%s --since={since}")

        classifications: Dict[str, int] = defaultdict(int)
        unclassified = 0

        for line in output.split("\n"):
            if not line.strip():
                continue

            msg = line.strip().lower()
            classified = False

            for category, patterns in self.COMMIT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, msg, re.IGNORECASE):
                        classifications[category] += 1
                        classified = True
                        break
                if classified:
                    break

            if not classified:
                classifications["other"] += 1
                unclassified += 1

        total = sum(classifications.values())

        # Calculate percentages
        percentages = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in classifications.items()}

        # Determine dominant work type
        if total > 0:
            dominant = max(classifications.items(), key=lambda x: x[1])
            dominant_type = dominant[0]
        else:
            dominant_type = "unknown"

        return {
            "distribution": dict(classifications),
            "percentages": percentages,
            "total_commits": total,
            "dominant_type": dominant_type,
            "unclassified_ratio": round(unclassified / total * 100, 1) if total > 0 else 0,
        }

    def analyze_technical_debt(self, focus_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan for technical debt indicators in code.

        Identifies areas needing attention.
        """
        if focus_dirs is None:
            focus_dirs = ["steward", "vibe_core", "agent_city"]

        debt_counts: Dict[str, int] = defaultdict(int)
        debt_locations: Dict[str, List[str]] = defaultdict(list)

        for focus_dir in focus_dirs:
            dir_path = self.root_dir / focus_dir
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    rel_path = str(py_file.relative_to(self.root_dir))

                    for pattern, debt_type in self.DEBT_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            debt_counts[debt_type] += len(matches)
                            if len(debt_locations[debt_type]) < 5:
                                debt_locations[debt_type].append(rel_path)

                except Exception:
                    pass

        total_debt = sum(debt_counts.values())

        # Calculate debt score (arbitrary but useful)
        debt_score = (
            debt_counts.get("fixme", 0) * 3
            + debt_counts.get("hack", 0) * 5
            + debt_counts.get("todo", 0) * 1
            + debt_counts.get("deprecated", 0) * 2
        )

        if debt_score < 10:
            debt_level = "LOW"
        elif debt_score < 50:
            debt_level = "MODERATE"
        elif debt_score < 100:
            debt_level = "HIGH"
        else:
            debt_level = "CRITICAL"

        return {
            "counts": dict(debt_counts),
            "total_markers": total_debt,
            "debt_score": debt_score,
            "debt_level": debt_level,
            "hotspot_files": {k: v for k, v in debt_locations.items() if v},
        }

    def analyze_complexity_signals(self) -> Dict[str, Any]:
        """
        Analyze code complexity signals.

        Uses simple heuristics for file complexity.
        """
        focus_dirs = ["steward", "vibe_core", "agent_city"]
        file_complexities: List[Tuple[str, int]] = []

        for focus_dir in focus_dirs:
            dir_path = self.root_dir / focus_dir
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    lines = content.split("\n")

                    # Simple complexity heuristics
                    line_count = len(lines)
                    class_count = len(re.findall(r"^class\s+", content, re.MULTILINE))
                    function_count = len(re.findall(r"^\s*def\s+", content, re.MULTILINE))
                    nested_ifs = len(re.findall(r"^\s{8,}if\s+", content, re.MULTILINE))

                    # Complexity score
                    complexity = line_count // 50 + class_count * 2 + function_count + nested_ifs * 3

                    if complexity > 10:  # Only track complex files
                        rel_path = str(py_file.relative_to(self.root_dir))
                        file_complexities.append((rel_path, complexity))

                except Exception:
                    pass

        # Sort by complexity
        sorted_files = sorted(file_complexities, key=lambda x: -x[1])[:15]

        return {
            "complex_files": sorted_files,
            "total_complex_files": len(file_complexities),
            "max_complexity": sorted_files[0][1] if sorted_files else 0,
        }

    def synthesize(self) -> Dict[str, Any]:
        """Synthesize full semantic dimension."""
        return {
            "commit_types": self.classify_commits(),
            "technical_debt": self.analyze_technical_debt(),
            "complexity": self.analyze_complexity_signals(),
        }


# =============================================================================
# DIMENSION 4: PREDICTIVE
# =============================================================================


class PredictiveDimension:
    """
    Predictive analysis - forward-looking insights.

    Provides:
    - Related file recommendations (if working on X, know Y)
    - Risk indicators (files that break often)
    - Development focus suggestions
    - Stability assessments
    """

    def __init__(self, git: GitInterface, root_dir: str = "."):
        self.git = git
        self.root_dir = Path(root_dir).resolve()

    def build_relatedness_map(self, days: int = 60) -> Dict[str, List[str]]:
        """
        Build a map of related files based on co-change history.

        If you're working on file A, these files are likely relevant.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        output = self.git.run(f"log --pretty=format:COMMIT --name-only --since={since}")

        commits = []
        current_files: Set[str] = set()

        for line in output.split("\n"):
            if line == "COMMIT":
                if current_files:
                    commits.append(current_files)
                current_files = set()
            elif line.strip() and not line.startswith("."):
                current_files.add(line.strip())

        if current_files:
            commits.append(current_files)

        # Build co-occurrence scores
        co_occurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for file_set in commits:
            for f1 in file_set:
                for f2 in file_set:
                    if f1 != f2:
                        co_occurrence[f1][f2] += 1

        # Build relatedness map (top related files for each)
        relatedness: Dict[str, List[str]] = {}
        for file, related in co_occurrence.items():
            sorted_related = sorted(related.items(), key=lambda x: -x[1])
            relatedness[file] = [f for f, count in sorted_related[:5] if count >= 2]

        return relatedness

    def identify_risk_areas(self, days: int = 30) -> Dict[str, Any]:
        """
        Identify files with high churn + recent fixes.

        These are areas likely to have issues.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get files involved in fix commits
        fix_output = self.git.run(f"log --grep=fix --pretty=format: --name-only --since={since}")
        fix_files = defaultdict(int)
        for line in fix_output.split("\n"):
            if line.strip():
                fix_files[line.strip()] += 1

        # Get high-churn files
        churn_output = self.git.run(f"log --pretty=format: --name-only --since={since}")
        churn_files = defaultdict(int)
        for line in churn_output.split("\n"):
            if line.strip():
                churn_files[line.strip()] += 1

        # Risk score = churn * fix_ratio
        risk_scores = []
        for file, churn in churn_files.items():
            fix_count = fix_files.get(file, 0)
            if fix_count > 0:
                risk_score = churn * (1 + fix_count * 0.5)
                risk_scores.append((file, round(risk_score, 1), fix_count))

        risk_scores.sort(key=lambda x: -x[1])

        return {
            "high_risk_files": risk_scores[:10],
            "total_files_with_fixes": len(fix_files),
            "total_fix_commits": sum(fix_files.values()),
        }

    def suggest_focus_areas(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest where to focus based on analysis.

        Synthesizes insights from other dimensions.
        """
        suggestions = []
        priorities = []

        # From temporal - velocity
        if "temporal" in context:
            trend = context["temporal"].get("velocity_trend", {}).get("trend", "")
            if trend == "ACCELERATING":
                suggestions.append("High activity period - good time for code reviews")
            elif trend == "DECELERATING":
                suggestions.append("Slower period - opportunity for refactoring and tech debt")

        # From structural - coupling
        if "structural" in context:
            hotspots = context["structural"].get("co_changes", {}).get("coupling_hotspots", [])
            if hotspots:
                top_coupled = hotspots[0][0] if hotspots else None
                if top_coupled:
                    priorities.append(f"Review coupling around: {top_coupled}")

        # From semantic - debt
        if "semantic" in context:
            debt_level = context["semantic"].get("technical_debt", {}).get("debt_level", "LOW")
            if debt_level in ["HIGH", "CRITICAL"]:
                suggestions.append(f"Technical debt is {debt_level} - schedule cleanup")
                priorities.append("Address FIXME and HACK markers")

            # From commit types
            dominant = context["semantic"].get("commit_types", {}).get("dominant_type", "")
            if dominant == "fix":
                suggestions.append("Many fixes lately - consider stability review")
            elif dominant == "feature":
                suggestions.append("Feature-heavy period - ensure test coverage")

        return {
            "suggestions": suggestions,
            "priorities": priorities,
            "generated_at": datetime.now().isoformat(),
        }

    def assess_stability(self, days: int = 14) -> Dict[str, Any]:
        """
        Assess overall project stability.

        Based on fix rate, churn patterns, and activity.
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Count total commits
        total = int(self.git.run(f"rev-list --count HEAD --since={since}") or "0")

        # Count fix commits
        fix_count = int(self.git.run(f"rev-list --count --grep=fix HEAD --since={since}") or "0")

        # Count revert commits
        revert_count = int(self.git.run(f"rev-list --count --grep=revert HEAD --since={since}") or "0")

        if total > 0:
            fix_ratio = fix_count / total
            revert_ratio = revert_count / total

            if fix_ratio > 0.4 or revert_ratio > 0.1:
                stability = "UNSTABLE"
                indicator = "⚠️"
            elif fix_ratio > 0.2:
                stability = "MODERATE"
                indicator = "🟡"
            else:
                stability = "STABLE"
                indicator = "🟢"
        else:
            stability = "INACTIVE"
            indicator = "⚪"
            fix_ratio = 0
            revert_ratio = 0

        return {
            "stability": stability,
            "indicator": indicator,
            "fix_ratio": round(fix_ratio * 100, 1),
            "revert_ratio": round(revert_ratio * 100, 1),
            "period_days": days,
            "total_commits": total,
        }

    def synthesize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize full predictive dimension."""
        relatedness = self.build_relatedness_map()
        risk = self.identify_risk_areas()
        stability = self.assess_stability()
        focus = self.suggest_focus_areas(context)

        return {
            "relatedness_map": dict(list(relatedness.items())[:20]),  # Limit for output
            "risk_areas": risk,
            "stability": stability,
            "focus_suggestions": focus,
        }


# =============================================================================
# MULTI-DIMENSIONAL SYNTHESIZER
# =============================================================================


class MultiDimensionalSynthesizer:
    """
    Synthesizes all four dimensions into unified context.

    This is the main interface for ANALYST agent.
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.git = GitInterface(str(self.root_dir))

        # Initialize dimensions
        self.temporal = TemporalDimension(self.git)
        self.structural = StructuralDimension(self.git, str(self.root_dir))
        self.semantic = SemanticDimension(self.git, str(self.root_dir))
        self.predictive = PredictiveDimension(self.git, str(self.root_dir))

    def synthesize_all(self) -> Dict[str, Any]:
        """
        Synthesize all dimensions into complete 4D context.

        Returns:
            Complete multi-dimensional analysis
        """
        # Build dimensions (order matters - predictive uses others)
        context = {}

        # Dimension 1: Temporal
        context["temporal"] = self.temporal.synthesize()

        # Dimension 2: Structural
        context["structural"] = self.structural.synthesize()

        # Dimension 3: Semantic
        context["semantic"] = self.semantic.synthesize()

        # Dimension 4: Predictive (uses context from other dimensions)
        context["predictive"] = self.predictive.synthesize(context)

        # Metadata
        context["metadata"] = {
            "synthesized_at": datetime.now().isoformat(),
            "dimensions": ["temporal", "structural", "semantic", "predictive"],
            "root_dir": str(self.root_dir),
        }

        return context

    def quick_insights(self) -> Dict[str, Any]:
        """
        Generate quick high-level insights.

        For rapid context without full analysis.
        """
        velocity = self.temporal.analyze_velocity_trend()
        stability = self.predictive.assess_stability()
        debt = self.semantic.analyze_technical_debt()
        commits = self.semantic.classify_commits(days=7)

        return {
            "velocity_trend": velocity["trend"],
            "momentum": velocity["momentum"],
            "stability": stability["stability"],
            "stability_indicator": stability["indicator"],
            "debt_level": debt["debt_level"],
            "dominant_work": commits["dominant_type"],
            "weekly_commits": velocity["average_weekly"],
        }
