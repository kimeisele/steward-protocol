#!/usr/bin/env python3
"""
WATCHMAN System Health Check Tool (Tool Protocol)

READ-ONLY monitoring of system infrastructure.
Tool Protocol compliant for kernel-managed execution.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xeea8fce7"  # GenesisByte: parampara % 37 == 0

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult


class SystemHealthCheck(Tool):
    """Read-only system health monitoring (Tool Protocol)."""

    def __init__(self, repo_root: Path = None):
        """Initialize health checker."""
        self.repo_root = repo_root or Path.cwd()
        self.git_hooks_dir = self.repo_root / ".git" / "hooks"
        self.source_hooks_dir = self.repo_root / ".githooks"

    @property
    def name(self) -> str:
        return "watchman.health"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "System health monitoring - check git hooks, infrastructure files"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'check_all'",
            },
            "repo_root": {
                "type": "string",
                "required": False,
                "description": "Repository root path (default: current directory)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["check_all"]:
            raise ValueError(f"Invalid action: {action}. Must be 'check_all'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute health check."""
        try:
            action = parameters["action"]

            if action == "check_all":
                repo_root = parameters.get("repo_root")
                if repo_root:
                    self.repo_root = Path(repo_root)
                    self.git_hooks_dir = self.repo_root / ".git" / "hooks"
                    self.source_hooks_dir = self.repo_root / ".githooks"

                report = self.check_all()

                return ToolResult(
                    success=True,
                    output=report,
                    metadata={
                        "action": "check_all",
                        "status": report["status"],
                        "violations_count": len(report["violations"]),
                    },
                )

        except Exception as e:
            error_msg = f"Health check failed: {type(e).__name__}: {e!s}"
            return ToolResult(success=False, error=error_msg)

    def check_all(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive report."""
        report = {
            "status": "healthy",
            "checks": {},
            "violations": [],
            "recommendations": [],
        }

        # Check git hooks
        hooks_status = self._check_git_hooks()
        report["checks"]["git_hooks"] = hooks_status

        if not hooks_status["all_ok"]:
            report["status"] = "unhealthy"
            report["violations"].extend(hooks_status["violations"])
            report["recommendations"].append("Run: python scripts/setup_hooks.py --fix")

        return report

    def _check_git_hooks(self) -> Dict[str, Any]:
        """Check git hooks installation status (READ-ONLY)."""
        required_hooks = ["pre-commit"]

        status = {"all_ok": True, "hooks": {}, "violations": []}

        for hook_name in required_hooks:
            hook_status = self._check_single_hook(hook_name)
            status["hooks"][hook_name] = hook_status

            if not hook_status["ok"]:
                status["all_ok"] = False
                status["violations"].append(
                    {
                        "severity": "warning",
                        "component": f"git_hook_{hook_name}",
                        "issue": hook_status["issue"],
                        "remediation": "Run scripts/setup_hooks.py --fix",
                    }
                )

        return status

    def _check_single_hook(self, hook_name: str) -> Dict[str, Any]:
        """Check a single git hook (READ-ONLY)."""
        source_hook = self.source_hooks_dir / hook_name
        installed_hook = self.git_hooks_dir / hook_name

        hook_status = {
            "ok": True,
            "issue": None,
            "source_exists": source_hook.exists(),
            "installed": installed_hook.exists(),
            "is_symlink": False,
            "valid": False,
        }

        # Check source exists
        if not hook_status["source_exists"]:
            hook_status["ok"] = False
            hook_status["issue"] = f"Source hook not found: {source_hook}"
            return hook_status

        # Check installed
        if not hook_status["installed"]:
            hook_status["ok"] = False
            hook_status["issue"] = f"Hook not installed: {hook_name}"
            return hook_status

        # Check validity
        hook_status["is_symlink"] = installed_hook.is_symlink()

        if installed_hook.is_symlink():
            # Verify symlink points to correct target
            try:
                target = installed_hook.resolve()
                hook_status["valid"] = target == source_hook.resolve()
            except Exception as e:
                hook_status["ok"] = False
                hook_status["issue"] = f"Broken symlink: {e}"
                return hook_status
        else:
            # Verify content matches
            try:
                hook_status["valid"] = installed_hook.read_text() == source_hook.read_text()
            except Exception as e:
                hook_status["ok"] = False
                hook_status["issue"] = f"Cannot read hook: {e}"
                return hook_status

        if not hook_status["valid"]:
            hook_status["ok"] = False
            hook_status["issue"] = f"Hook outdated or invalid: {hook_name}"

        return hook_status

    def format_report(self, report: Dict[str, Any]) -> str:
        """Format health report for human reading."""
        lines = []

        lines.append("=" * 70)
        lines.append("🏥 WATCHMAN SYSTEM HEALTH CHECK")
        lines.append("=" * 70)

        # Overall status
        status_emoji = "✅" if report["status"] == "healthy" else "⚠️"
        lines.append(f"\n{status_emoji} Overall Status: {report['status'].upper()}")

        # Git hooks
        if "git_hooks" in report["checks"]:
            lines.append("\n📌 Git Hooks:")
            for hook_name, hook_info in report["checks"]["git_hooks"]["hooks"].items():
                ok_emoji = "✅" if hook_info["ok"] else "❌"
                lines.append(f"  {ok_emoji} {hook_name}: {'OK' if hook_info['ok'] else hook_info['issue']}")

        # Violations
        if report["violations"]:
            lines.append(f"\n🚨 Violations Found: {len(report['violations'])}")
            for v in report["violations"]:
                lines.append(f"  • [{v['severity'].upper()}] {v['component']}: {v['issue']}")
                lines.append(f"    → {v['remediation']}")

        # Recommendations
        if report["recommendations"]:
            lines.append("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                lines.append(f"  • {rec}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)


def main():
    """Main entry point for standalone execution."""
    try:
        # Find repo root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        sys.exit(1)

    # Run health check
    checker = SystemHealthCheck(repo_root)
    report = checker.check_all()

    # Print report
    print(checker.format_report(report))

    # Exit with appropriate code
    sys.exit(0 if report["status"] == "healthy" else 1)


if __name__ == "__main__":
    main()


__all__ = ["SystemHealthCheck"]
