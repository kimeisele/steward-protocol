#!/usr/bin/env python3
"""
WATCHMAN System Health Check Tool

READ-ONLY monitoring of system infrastructure.
Reports violations but NEVER modifies infrastructure.

Philosophy: "The Watchman observes. The Operator acts."

Checks:
1. Git hooks installation status
2. Hook validity (symlink integrity, content freshness)
3. Critical infrastructure files

This respects AGENT CITY architecture:
- Agent (WATCHMAN): Monitors and reports
- Operator (Human/Script): Executes infrastructure changes via scripts/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import subprocess


class SystemHealthCheck:
    """Read-only system health monitoring."""

    def __init__(self, repo_root: Path = None):
        """Initialize health checker."""
        self.repo_root = repo_root or Path.cwd()
        self.git_hooks_dir = self.repo_root / ".git" / "hooks"
        self.source_hooks_dir = self.repo_root / ".githooks"

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
                        "remediation": f"Run scripts/setup_hooks.py --fix",
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
                hook_status["valid"] = (
                    installed_hook.read_text() == source_hook.read_text()
                )
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
                lines.append(
                    f"  {ok_emoji} {hook_name}: {'OK' if hook_info['ok'] else hook_info['issue']}"
                )

        # Violations
        if report["violations"]:
            lines.append(f"\n🚨 Violations Found: {len(report['violations'])}")
            for v in report["violations"]:
                lines.append(
                    f"  • [{v['severity'].upper()}] {v['component']}: {v['issue']}"
                )
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
