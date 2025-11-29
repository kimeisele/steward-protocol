#!/usr/bin/env python3
"""
Project Introspector - Extract metadata from project files
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProjectIntrospector:
    """Extract metadata from pyproject.toml, git, etc."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def get_project_metadata(self) -> Dict[str, str]:
        """Extract metadata from pyproject.toml"""
        pyproject = self.root_dir / "pyproject.toml"
        metadata = {
            "name": "Steward Protocol",
            "version": "1.0.0",
            "description": "Constitutional AI Agent Operating System",
            "python_version": "3.11+",
            "license": "MIT",
        }

        if not pyproject.exists():
            return metadata

        try:
            content = pyproject.read_text()

            # Extract name
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                metadata["name"] = name_match.group(1)

            # Extract version
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                metadata["version"] = version_match.group(1)

            # Extract description
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if desc_match:
                metadata["description"] = desc_match.group(1)

            # Extract python version
            python_match = re.search(r'python\s*=\s*["\']([^"\']+)["\']', content)
            if python_match:
                metadata["python_version"] = python_match.group(1)

        except Exception as e:
            print(f"Warning: Could not parse pyproject.toml: {e}")

        return metadata

    def get_git_stats(self) -> Dict[str, Any]:
        """Extract git statistics"""
        stats = {"commit_count": 0, "contributors": [], "recent_commits": []}

        try:
            # Get commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                stats["commit_count"] = int(result.stdout.strip())

            # Get contributors
            result = subprocess.run(
                ["git", "log", "--format=%an", "--all"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                contributors = set(result.stdout.strip().split("\n"))
                stats["contributors"] = sorted(list(contributors))[:5]  # Top 5

            # Get recent commits (last 3)
            result = subprocess.run(
                ["git", "log", "--oneline", "-3"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                stats["recent_commits"] = [c.strip() for c in commits if c.strip()]

        except Exception as e:
            print(f"Warning: Could not extract git stats: {e}")

        return stats

    def count_system_agents(self) -> int:
        """Count system agents"""
        agents_dir = self.root_dir / "steward" / "system_agents"
        if not agents_dir.exists():
            return 0

        cartridges = list(agents_dir.glob("*/cartridge_main.py"))
        return len(cartridges)

    def get_governance_summary(self) -> str:
        """Extract governance summary from CONSTITUTION.md"""
        constitution = self.root_dir / "CONSTITUTION.md"
        if not constitution.exists():
            return "Constitutional governance enforced at kernel level"

        try:
            content = constitution.read_text()
            # Extract first paragraph after title
            lines = content.split("\n")
            summary_lines = []
            in_summary = False
            for line in lines:
                if line.strip().startswith("#"):
                    in_summary = True
                    continue
                if in_summary and line.strip():
                    summary_lines.append(line.strip())
                    if len(summary_lines) >= 2:
                        break

            if summary_lines:
                return " ".join(summary_lines)
        except:
            pass

        return "Constitutional governance enforced at kernel level"

    def get_agent_list(self) -> List[Dict[str, str]]:
        """Get list of actual agents with their metadata"""
        from .introspector import CartridgeIntrospector

        agents_dir = self.root_dir / "steward" / "system_agents"
        if not agents_dir.exists():
            return []

        introspector = CartridgeIntrospector(str(self.root_dir))
        agents_data = introspector.scan_all(agents_dir)

        # Convert to simple list format for template
        agents_list = []
        for agent_name, metadata in sorted(agents_data.items()):
            agents_list.append(
                {
                    "name": agent_name.upper(),
                    "role": metadata.get("description", "Specialized Agent"),
                    "class": metadata.get("class_name", ""),
                    "version": metadata.get("version", "1.0.0"),
                }
            )

        return agents_list

    def get_all_metadata(self) -> Dict[str, Any]:
        """Get all project metadata"""
        return {
            "project": self.get_project_metadata(),
            "git": self.get_git_stats(),
            "agent_count": self.count_system_agents(),
            "governance": self.get_governance_summary(),
            "agents": self.get_agent_list(),
        }
