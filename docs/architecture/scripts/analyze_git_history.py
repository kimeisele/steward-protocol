#!/usr/bin/env python3
"""
GIT HISTORY ANALYZER
====================
Deep analysis of git history to understand architecture evolution.

Analyzes:
- Commit frequency by path (where is activity?)
- Major contributors per module
- Architecture-related commits (GAD, ARCH mentions)
- File churn (most changed files)
- Module age (when was each part created?)

Usage:
    python docs/architecture/scripts/analyze_git_history.py

Output:
    docs/architecture/GIT_HISTORY_ANALYSIS.yaml
"""

import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml


def run_git(cmd):
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + cmd.split(),
        capture_output=True,
        text=True,
        cwd=".",
    )
    return result.stdout.strip()


def get_commit_count():
    """Total commits."""
    return int(run_git("rev-list --count HEAD"))


def get_file_churn(limit=20):
    """Most frequently changed files."""
    output = run_git("log --pretty=format: --name-only")
    files = defaultdict(int)
    for line in output.split("\n"):
        if line.strip():
            files[line.strip()] += 1

    return dict(sorted(files.items(), key=lambda x: -x[1])[:limit])


def get_module_activity():
    """Commits per top-level module."""
    output = run_git("log --pretty=format: --name-only")
    modules = defaultdict(int)

    for line in output.split("\n"):
        if line.strip():
            parts = line.strip().split("/")
            if parts:
                module = parts[0]
                modules[module] += 1

    return dict(sorted(modules.items(), key=lambda x: -x[1]))


def get_arch_commits():
    """Commits mentioning architecture keywords."""
    keywords = ["GAD", "ARCH", "architecture", "kernel", "protocol"]
    arch_commits = {}

    for kw in keywords:
        output = run_git(f"log --oneline --grep={kw}")
        count = len([l for l in output.split("\n") if l.strip()])
        if count > 0:
            arch_commits[kw] = count

    return arch_commits


def get_recent_commits(limit=20):
    """Recent commits with their affected modules."""
    output = run_git(f"log --oneline -{limit}")
    commits = []
    for line in output.split("\n"):
        if line.strip():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                commits.append({"hash": parts[0], "message": parts[1][:80]})
    return commits


def get_first_commits_by_module():
    """When was each module first created?"""
    modules = ["vibe_core", "steward", "agent_city", "provider", "scripts", "docs"]
    first_commits = {}

    for module in modules:
        if Path(module).exists():
            output = run_git(f"log --reverse --oneline -- {module}")
            lines = [l for l in output.split("\n") if l.strip()]
            if lines:
                first = lines[0].split(" ", 1)
                first_commits[module] = {
                    "hash": first[0],
                    "message": first[1][:60] if len(first) > 1 else "",
                }

    return first_commits


def get_contributor_stats():
    """Top contributors by commit count."""
    output = run_git("shortlog -sn --no-merges HEAD")
    contributors = {}
    for line in output.split("\n"):
        if line.strip():
            match = re.match(r"\s*(\d+)\s+(.+)", line)
            if match:
                contributors[match.group(2)] = int(match.group(1))
    return contributors


def main():
    print("=" * 60)
    print("GIT HISTORY ANALYZER")
    print("=" * 60)
    print()

    analysis = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "total_commits": get_commit_count(),
        },
        "module_activity": {},
        "file_churn": {},
        "arch_commits": {},
        "module_origins": {},
        "contributors": {},
        "recent_commits": [],
    }

    print("Analyzing module activity...")
    analysis["module_activity"] = get_module_activity()
    print(f"   Found {len(analysis['module_activity'])} modules")

    print("Analyzing file churn...")
    analysis["file_churn"] = get_file_churn(15)
    print(f"   Top {len(analysis['file_churn'])} most changed files")

    print("Finding architecture-related commits...")
    analysis["arch_commits"] = get_arch_commits()
    print(f"   Found commits for {len(analysis['arch_commits'])} keywords")

    print("Finding module origins...")
    analysis["module_origins"] = get_first_commits_by_module()
    print(f"   Traced {len(analysis['module_origins'])} modules")

    print("Analyzing contributors...")
    analysis["contributors"] = get_contributor_stats()
    print(f"   Found {len(analysis['contributors'])} contributors")

    print("Getting recent commits...")
    analysis["recent_commits"] = get_recent_commits(15)

    # Write output
    output_path = Path("docs/architecture/GIT_HISTORY_ANALYSIS.yaml")
    with open(output_path, "w") as f:
        yaml.dump(analysis, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print()
    print(f"✅ Generated: {output_path}")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total commits: {analysis['meta']['total_commits']}")
    print()

    print("Module activity (top 5):")
    for mod, count in list(analysis["module_activity"].items())[:5]:
        print(f"   {mod}: {count} file changes")

    print()
    print("Architecture commits:")
    for kw, count in sorted(analysis["arch_commits"].items(), key=lambda x: -x[1]):
        print(f"   {kw}: {count} commits")

    print()
    print("Most churned files:")
    for f, count in list(analysis["file_churn"].items())[:5]:
        print(f"   {f}: {count} changes")


if __name__ == "__main__":
    main()
