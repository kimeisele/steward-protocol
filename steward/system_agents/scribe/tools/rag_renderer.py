#!/usr/bin/env python3
"""
SCRIBE RAG Renderer - Generate RAG.md (Realtime Architecture Guide)

RAG = Realtime Architecture Guide (NOT Retrieval Augmented Generation!)

Provides:
- Git activity timeline (7d, 30d, 90d)
- Hot files (high churn indicators)
- Module activity patterns
- Dependency connections
- Focus area recommendations

Data source: ANALYST agent context synthesis

Tool Protocol Compliant (Kernel-Managed).
"""

import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

# Import from shared base
from .base import Tool, ToolResult, get_kernel_status, load_template


class RagRenderer(Tool):
    """Render RAG.md - Realtime Architecture Guide."""

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)

    @property
    def name(self) -> str:
        return "scribe.rag_renderer"

    @property
    def description(self) -> str:
        return "Generate RAG.md - Realtime Architecture Guide (Git-based context)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to analyze and render RAG.md",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate renderer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be 'generate'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute renderer operation."""
        try:
            action = parameters["action"]
            if action == "generate":
                content = self._analyze_and_render()
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    # =========================================================================
    # GIT ANALYSIS (Inline - no external dependency)
    # =========================================================================

    def _run_git(self, cmd: str) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=str(self.root_dir),
        )
        return result.stdout.strip()

    def _analyze_git_activity(self, days: int = 7) -> Dict[str, Any]:
        """Analyze git activity for specified period."""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get commits
        commits_output = self._run_git(f"log --oneline --since={since_date}")
        commits = [line for line in commits_output.split("\n") if line.strip()]

        # Get file changes
        files_output = self._run_git(f"log --pretty=format: --name-only --since={since_date}")
        file_changes = defaultdict(int)
        for line in files_output.split("\n"):
            if line.strip():
                file_changes[line.strip()] += 1

        hot_files = dict(sorted(file_changes.items(), key=lambda x: -x[1])[:15])

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

    def _analyze_file_churn(self, limit: int = 15) -> Dict[str, int]:
        """Analyze all-time file churn."""
        output = self._run_git("log --pretty=format: --name-only")
        files = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                files[line.strip()] += 1

        return dict(sorted(files.items(), key=lambda x: -x[1])[:limit])

    def _analyze_connections(self, hot_files: Dict[str, int]) -> List[Dict[str, Any]]:
        """Analyze connections for hot files."""
        connections = []

        for file_path in list(hot_files.keys())[:10]:
            if file_path.endswith(".py"):
                full_path = self.root_dir / file_path
                if full_path.exists():
                    try:
                        content = full_path.read_text()
                        import_count = sum(
                            1 for line in content.split("\n") if line.strip().startswith(("import ", "from "))
                        )
                        connections.append(
                            {
                                "file": file_path,
                                "changes": hot_files[file_path],
                                "import_count": import_count,
                            }
                        )
                    except Exception:
                        pass

        return connections

    def _synthesize_context(self) -> Dict[str, Any]:
        """Synthesize full context for RAG.md."""
        # Timeline analysis
        short_term = self._analyze_git_activity(days=7)
        mid_term = self._analyze_git_activity(days=30)
        long_term = self._analyze_git_activity(days=90)

        # All-time churn
        all_time_churn = self._analyze_file_churn(limit=15)

        # Connections
        connections = self._analyze_connections(all_time_churn)

        # Total commits
        try:
            total_commits = int(self._run_git("rev-list --count HEAD") or "0")
        except Exception:
            total_commits = 0

        return {
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

    # =========================================================================
    # RENDERING
    # =========================================================================

    def _analyze_and_render(self) -> str:
        """Analyze repository and render RAG.md content."""
        # Get context
        context = self._synthesize_context()

        # Get kernel status
        kernel_status = get_kernel_status()

        # Timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Load and render template
        template = load_template("rag.jinja2")
        content = template.render(
            timestamp=timestamp,
            generator="SCRIBE (via ANALYST)",
            kernel_status=kernel_status,
            context=context,
        )

        return content
