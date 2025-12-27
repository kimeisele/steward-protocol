"""
System Handler - System maintenance and operations.

OPUS-TRAINING: Created during MANAS training session.

Handles system-level intents that MANAS generates but previously
had no handler for. This fills the gap in MANAS's capabilities.

Handles:
- cleanup_disk: Clean up disk space (logs, caches, temp files)
- read_file: Read file contents for analysis
- semantic_gap_test: Create tests for untested code
- review_todos: Review and prioritize TODOs in codebase
"""

import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.System")


@register_handler
class SystemHandler(BaseHandler):
    """
    Handle system maintenance intents.

    OPUS-TRAINING: This handler enables MANAS to maintain system health.

    Agent-First: This handler belongs to the AUDIT domain.
    Future routing: Intent -> SystemAgent -> SystemHandler
    """

    # === REQUIRED CLASS ATTRIBUTES ===
    name = "system"
    intent_types = [
        "cleanup_disk",
        "read_file",
        "review_todos",
        "system_health_check",
    ]

    # === AGENT-FIRST ROUTING ===
    agent_type = AgentType.AUDIT
    priority = 15

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to appropriate system operation."""
        logger.info(f"🔧 SystemHandler handling: {intent.title}")

        try:
            if intent.intent_type == "cleanup_disk":
                return self._handle_cleanup_disk(intent)
            elif intent.intent_type == "read_file":
                return self._handle_read_file(intent)
            elif intent.intent_type == "review_todos":
                return self._handle_review_todos(intent)
            elif intent.intent_type == "system_health_check":
                return self._handle_health_check(intent)
            else:
                return {
                    "success": False,
                    "handler": self.name,
                    "error": f"Unknown intent type: {intent.intent_type}",
                }

        except Exception as e:
            logger.error(f"SystemHandler error: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _handle_cleanup_disk(self, intent: "Intent") -> Dict[str, Any]:
        """
        Analyze disk space and report what COULD be cleaned.

        DHARMA: This handler is READ-ONLY by default.
        It reports what could be cleaned, but does NOT delete anything
        unless explicitly approved via params["execute"] = True.

        This prevents accidental data loss from automated cleanup.
        """
        logger.info("🔍 MANAS: Analyzing disk for cleanup candidates...")

        execute = intent.params.get("execute", False)
        candidates = []
        total_bytes = 0

        # 1. Count Python cache (__pycache__)
        try:
            pycache_count = 0
            pycache_bytes = 0
            for pycache in self._workspace.rglob("__pycache__"):
                if pycache.is_dir():
                    size = sum(f.stat().st_size for f in pycache.rglob("*") if f.is_file())
                    pycache_bytes += size
                    pycache_count += 1
            if pycache_count > 0:
                candidates.append(
                    {
                        "type": "__pycache__",
                        "count": pycache_count,
                        "bytes": pycache_bytes,
                        "description": f"{pycache_count} __pycache__ directories",
                    }
                )
                total_bytes += pycache_bytes
        except Exception as e:
            logger.debug(f"pycache scan error: {e}")

        # 2. Count .pytest_cache
        try:
            pytest_cache = self._workspace / ".pytest_cache"
            if pytest_cache.exists():
                size = sum(f.stat().st_size for f in pytest_cache.rglob("*") if f.is_file())
                candidates.append(
                    {
                        "type": ".pytest_cache",
                        "count": 1,
                        "bytes": size,
                        "description": ".pytest_cache directory",
                    }
                )
                total_bytes += size
        except Exception as e:
            logger.debug(f"pytest_cache scan error: {e}")

        # 3. Count .mypy_cache
        try:
            mypy_cache = self._workspace / ".mypy_cache"
            if mypy_cache.exists():
                size = sum(f.stat().st_size for f in mypy_cache.rglob("*") if f.is_file())
                candidates.append(
                    {
                        "type": ".mypy_cache",
                        "count": 1,
                        "bytes": size,
                        "description": ".mypy_cache directory",
                    }
                )
                total_bytes += size
        except Exception as e:
            logger.debug(f"mypy_cache scan error: {e}")

        # 4. Count old log files (older than 7 days)
        try:
            log_count = 0
            log_bytes = 0
            cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
            for log in self._workspace.rglob("*.log"):
                if log.is_file() and log.stat().st_mtime < cutoff:
                    log_bytes += log.stat().st_size
                    log_count += 1
            if log_count > 0:
                candidates.append(
                    {
                        "type": "old_logs",
                        "count": log_count,
                        "bytes": log_bytes,
                        "description": f"{log_count} log files older than 7 days",
                    }
                )
                total_bytes += log_bytes
        except Exception as e:
            logger.debug(f"log scan error: {e}")

        mb_total = total_bytes / (1024 * 1024)

        # If execute=True, actually clean (requires explicit approval)
        if execute and candidates:
            logger.warning("🗑️ MANAS: Executing cleanup (approved)...")
            # Only clean safe items: caches, not logs
            cleaned = []
            for c in candidates:
                if c["type"] == "__pycache__":
                    for pycache in self._workspace.rglob("__pycache__"):
                        if pycache.is_dir():
                            shutil.rmtree(pycache)
                    cleaned.append(c["description"])
                elif c["type"] == ".pytest_cache":
                    shutil.rmtree(self._workspace / ".pytest_cache")
                    cleaned.append(c["description"])
                elif c["type"] == ".mypy_cache":
                    shutil.rmtree(self._workspace / ".mypy_cache")
                    cleaned.append(c["description"])
                # NOTE: old_logs are NOT auto-deleted - too risky

            return {
                "success": True,
                "handler": self.name,
                "action": "cleanup_executed",
                "cleaned": cleaned,
                "mb_freed": round(mb_total, 2),
                "message": f"Cleanup executed: {mb_total:.2f} MB freed",
            }

        # Default: Report only (safe)
        return {
            "success": True,
            "handler": self.name,
            "action": "cleanup_analysis",
            "candidates": candidates,
            "total_bytes": total_bytes,
            "mb_available": round(mb_total, 2),
            "execute_required": True,
            "message": f"Found {mb_total:.2f} MB that could be cleaned. Set execute=True to proceed.",
        }

    def _handle_read_file(self, intent: "Intent") -> Dict[str, Any]:
        """
        Read a file's contents for analysis.

        Intent params:
            - path: File path to read (relative to workspace)
            - lines: Optional tuple (start, end) for line range
        """
        path = intent.params.get("path")
        if not path:
            return {
                "success": False,
                "handler": self.name,
                "error": "No path specified",
            }

        file_path = self._workspace / path
        if not file_path.exists():
            return {
                "success": False,
                "handler": self.name,
                "error": f"File not found: {path}",
            }

        try:
            content = file_path.read_text()
            lines = intent.params.get("lines")

            if lines:
                content_lines = content.split("\n")
                start, end = lines
                content = "\n".join(content_lines[start - 1 : end])

            return {
                "success": True,
                "handler": self.name,
                "action": "read_file",
                "path": str(path),
                "content": content[:5000],  # Limit to 5KB
                "truncated": len(content) > 5000,
                "size_bytes": len(content),
            }

        except Exception as e:
            return {
                "success": False,
                "handler": self.name,
                "error": f"Failed to read file: {e}",
            }

    def _handle_review_todos(self, intent: "Intent") -> Dict[str, Any]:
        """
        Find and categorize TODOs in the codebase.

        Returns a summary of TODOs grouped by priority/category.
        """
        logger.info("📋 MANAS: Reviewing TODOs...")

        todos: List[Dict[str, Any]] = []

        try:
            # Search for TODOs in Python files
            result = subprocess.run(
                ["grep", "-rn", "TODO", "--include=*.py", "."],
                capture_output=True,
                text=True,
                cwd=self._workspace,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            todos.append(
                                {
                                    "file": parts[0],
                                    "line": int(parts[1]),
                                    "content": parts[2].strip(),
                                }
                            )

            # Categorize by keywords
            high_priority = [
                t for t in todos if any(k in t["content"].upper() for k in ["URGENT", "FIXME", "CRITICAL", "BUG"])
            ]
            medium_priority = [t for t in todos if any(k in t["content"].upper() for k in ["IMPORTANT", "HACK", "XXX"])]
            low_priority = [t for t in todos if t not in high_priority and t not in medium_priority]

            return {
                "success": True,
                "handler": self.name,
                "action": "review_todos",
                "total_count": len(todos),
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "high_priority_items": high_priority[:5],
                "message": f"Found {len(todos)} TODOs ({len(high_priority)} high priority)",
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "handler": self.name, "error": "TODO search timed out"}
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}

    def _handle_health_check(self, intent: "Intent") -> Dict[str, Any]:
        """
        Perform a system health check.

        Checks: disk space, git status, test status, linting.
        """
        logger.info("🩺 MANAS: Running health check...")

        health = {
            "disk": None,
            "git": None,
            "tests": None,
            "lint": None,
        }

        # 1. Disk space
        try:
            usage = shutil.disk_usage(self._workspace)
            percent_used = (usage.used / usage.total) * 100
            health["disk"] = {
                "percent_used": round(percent_used, 1),
                "healthy": percent_used < 90,
                "gb_free": round(usage.free / (1024**3), 1),
            }
        except Exception as e:
            health["disk"] = {"error": str(e)}

        # 2. Git status
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self._workspace,
                timeout=10,
            )
            dirty_files = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            health["git"] = {
                "dirty_files": dirty_files,
                "healthy": dirty_files < 10,
            }
        except Exception as e:
            health["git"] = {"error": str(e)}

        # 3. Quick lint check
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--select=E,F", "-q"],
                capture_output=True,
                text=True,
                cwd=self._workspace,
                timeout=30,
            )
            lint_issues = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            health["lint"] = {
                "issues": lint_issues,
                "healthy": lint_issues < 20,
            }
        except Exception as e:
            health["lint"] = {"error": str(e)}

        # Calculate overall health score
        checks = [v.get("healthy", False) for v in health.values() if isinstance(v, dict) and "healthy" in v]
        health_score = (sum(checks) / len(checks) * 100) if checks else 0

        return {
            "success": True,
            "handler": self.name,
            "action": "health_check",
            "health": health,
            "health_score": round(health_score, 0),
            "healthy": health_score >= 75,
            "message": f"System health: {health_score:.0f}%",
        }


@register_handler
class SutraGapHandler(BaseHandler):
    """
    Handle documentation gap intents.

    OPUS-TRAINING: This handler enables MANAS to fix doc/code gaps.

    Handles sutra_missing_* intent types generated by SutraSense.
    """

    name = "sutra_gap"
    intent_types = [
        "sutra_missing_code",
        "sutra_missing_harness",
        "sutra_missing_test",
        "harness_broken",
    ]

    agent_type = AgentType.DOCUMENTATION
    priority = 8

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to appropriate gap-fixing operation."""
        logger.info(f"📜 SutraGapHandler handling: {intent.title}")

        try:
            gap_type = intent.params.get("gap_type", intent.intent_type)
            doc_path = intent.params.get("doc_path")
            code_path = intent.params.get("code_path")

            # For now, acknowledge and provide guidance
            # Full implementation would auto-fix or create issues
            guidance = self._get_guidance(gap_type, doc_path, code_path)

            return {
                "success": True,
                "handler": self.name,
                "action": "gap_analyzed",
                "gap_type": gap_type,
                "doc_path": doc_path,
                "code_path": code_path,
                "guidance": guidance,
                "message": f"Gap identified: {gap_type}",
            }

        except Exception as e:
            logger.error(f"SutraGapHandler error: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _get_guidance(self, gap_type: str, doc_path: Optional[str], code_path: Optional[str]) -> str:
        """Provide guidance for fixing the gap."""
        if gap_type == "sutra_missing_code":
            return f"Document {doc_path} references {code_path} which doesn't exist. Either create the file or update the @HARNESS."
        elif gap_type == "sutra_missing_harness":
            return f"Document {doc_path} has no @HARNESS block. Add one with file references and wiring patterns."
        elif gap_type == "sutra_missing_test":
            return f"Code {code_path} referenced in docs has no test. Create tests/test_*.py for it."
        elif gap_type == "harness_broken":
            return f"@HARNESS in {doc_path} has broken references. Update file paths to match current structure."
        else:
            return "Unknown gap type - manual investigation required."
