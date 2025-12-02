"""
THE ANALYST - Repository Analysis & Context Synthesis Agent.
Part of the Steward Protocol Federation.

Role: Context Provider / Intelligence Gatherer
Mission: Analyze repository to provide real-time context for agents.

RAG = Realtime Architecture Guide
(NOT Retrieval Augmented Generation - we redefine it!)

GOLDEN TEMPLATE COMPLIANT:
- Tool Protocol Compliant (tools via kernel)
- Constitutional Oath
- Works FOR SCRIBE to generate RAG.md
"""

import logging
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Constitutional Oath Mixin (Golden Template Pattern)
from steward.oath_mixin import OathMixin

# VibeOS Integration
from vibe_core import Task, VibeAgent

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ANALYST_AGENT")


class AnalystCartridge(VibeAgent, OathMixin):
    """
    The Analyst Agent Cartridge.
    Specialized in repository analysis and context synthesis.

    RAG = Realtime Architecture Guide

    Provides:
    - Git history analysis (churn, activity, timeline)
    - Dependency analysis (imports, relationships)
    - Context synthesis (what you need to know)
    """

    def __init__(self):
        """Initialize the Analyst as a VibeAgent."""
        super().__init__(
            agent_id="analyst",
            name="ANALYST",
            version="1.0.0",
            author="Steward Protocol",
            description="Repository analysis and context synthesis agent",
            domain="RESEARCH",
            capabilities=["git_analysis", "dependency_analysis", "context_synthesis"],
        )

        logger.info("🔍 THE ANALYST is online (RAG - Realtime Architecture Guide)")

        # Golden Template Pattern: Initialize Constitutional Oath
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        logger.info("✅ ANALYST has sworn the Constitutional Oath")

        # Configuration
        self.config = {
            "git_depth": 90,  # Days of history
            "churn_threshold": 10,  # Hot file threshold
            "dependency_depth": 3,  # Import chain depth
        }

        logger.info("✅ ANALYST: Ready to provide context")

    # =========================================================================
    # GIT ANALYSIS
    # =========================================================================

    def _run_git(self, cmd: str) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=".",
        )
        return result.stdout.strip()

    def analyze_git_activity(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze git activity for the specified period.

        Returns:
            Dict with commits, hot_files, module_activity
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get commits in period
        commits_output = self._run_git(f"log --oneline --since={since_date}")
        commits = [line for line in commits_output.split("\n") if line.strip()]

        # Get file changes
        files_output = self._run_git(f"log --pretty=format: --name-only --since={since_date}")
        file_changes = defaultdict(int)
        for line in files_output.split("\n"):
            if line.strip():
                file_changes[line.strip()] += 1

        # Sort by change frequency
        hot_files = dict(sorted(file_changes.items(), key=lambda x: -x[1])[:20])

        # Module activity
        module_activity = defaultdict(int)
        for file_path, count in file_changes.items():
            parts = file_path.split("/")
            if parts:
                module_activity[parts[0]] += count

        return {
            "period_days": days,
            "total_commits": len(commits),
            "recent_commits": commits[:10],
            "hot_files": hot_files,
            "module_activity": dict(sorted(module_activity.items(), key=lambda x: -x[1])),
        }

    def analyze_file_churn(self, limit: int = 20) -> Dict[str, int]:
        """
        Analyze file churn (most frequently changed files all-time).

        Returns:
            Dict of file_path -> change_count
        """
        output = self._run_git("log --pretty=format: --name-only")
        files = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                files[line.strip()] += 1

        return dict(sorted(files.items(), key=lambda x: -x[1])[:limit])

    # =========================================================================
    # DEPENDENCY ANALYSIS
    # =========================================================================

    def analyze_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze dependencies for a specific file.

        Returns:
            Dict with imports, dependents, related_files
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        content = path.read_text()
        imports = []

        # Extract Python imports
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)

        return {
            "file": file_path,
            "imports": imports[:20],
            "import_count": len(imports),
        }

    def analyze_hot_connections(self) -> List[Dict[str, Any]]:
        """
        Analyze connections between hot files.

        Returns:
            List of connection patterns
        """
        hot_files = self.analyze_file_churn(limit=10)
        connections = []

        for file_path in hot_files.keys():
            if file_path.endswith(".py") and Path(file_path).exists():
                deps = self.analyze_dependencies(file_path)
                connections.append(
                    {
                        "file": file_path,
                        "changes": hot_files[file_path],
                        "import_count": deps.get("import_count", 0),
                    }
                )

        return connections

    # =========================================================================
    # CONTEXT SYNTHESIS
    # =========================================================================

    def synthesize_context(self) -> Dict[str, Any]:
        """
        Synthesize full context for RAG.md generation.

        This is the main output used by SCRIBE to render RAG.md.

        Returns:
            Complete context dictionary
        """
        logger.info("🔍 ANALYST: Synthesizing context...")

        # Short-term (7 days)
        short_term = self.analyze_git_activity(days=7)

        # Mid-term (30 days)
        mid_term = self.analyze_git_activity(days=30)

        # Long-term (90 days)
        long_term = self.analyze_git_activity(days=90)

        # All-time churn
        all_time_churn = self.analyze_file_churn(limit=15)

        # Hot connections
        connections = self.analyze_hot_connections()

        # Get total commit count
        total_commits = int(self._run_git("rev-list --count HEAD") or "0")

        context = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_commits": total_commits,
            "timeline": {
                "short_term": short_term,
                "mid_term": mid_term,
                "long_term": long_term,
            },
            "hot_files": all_time_churn,
            "connections": connections,
            "summary": {
                "active_modules": list(short_term["module_activity"].keys())[:5],
                "focus_areas": list(short_term["hot_files"].keys())[:5],
                "velocity_7d": short_term["total_commits"],
                "velocity_30d": mid_term["total_commits"],
            },
        }

        logger.info(f"✅ ANALYST: Context synthesized ({total_commits} total commits)")
        return context

    # =========================================================================
    # TASK HANDLER (VibeAgent Protocol)
    # =========================================================================

    def handle_task(self, task: Task) -> Dict[str, Any]:
        """
        Handle incoming tasks (VibeAgent protocol).

        Supported actions:
        - analyze_git: Analyze git activity
        - analyze_deps: Analyze file dependencies
        - synthesize: Full context synthesis for RAG.md
        """
        action = task.payload.get("action", "synthesize")
        logger.info(f"🔍 ANALYST received task: {action}")

        try:
            if action == "analyze_git":
                days = task.payload.get("days", 7)
                return {
                    "status": "success",
                    "result": self.analyze_git_activity(days=days),
                }

            elif action == "analyze_deps":
                file_path = task.payload.get("file_path", "")
                return {
                    "status": "success",
                    "result": self.analyze_dependencies(file_path),
                }

            elif action == "synthesize":
                return {
                    "status": "success",
                    "result": self.synthesize_context(),
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                }

        except Exception as e:
            logger.error(f"❌ ANALYST task failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }


# For direct testing
if __name__ == "__main__":
    analyst = AnalystCartridge()
    context = analyst.synthesize_context()
    print("\nContext Summary:")
    print(f"  Total Commits: {context['total_commits']}")
    print(f"  7-Day Velocity: {context['summary']['velocity_7d']}")
    print(f"  Focus Areas: {context['summary']['focus_areas']}")
