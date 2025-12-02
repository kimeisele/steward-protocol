#!/usr/bin/env python3
"""
Operations Introspector - Dynamic discovery of system operations

Scans for:
- CI/CD workflows (.github/workflows/*.yml)
- Git activity (git log)
- Tunable parameters (code constants)

NO HARDCODING - discovers everything dynamically.
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class WorkflowIntrospector:
    """Scan GitHub Actions workflows dynamically."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.workflows_dir = self.root_dir / ".github" / "workflows"

    def scan_all(self) -> List[Dict[str, Any]]:
        """
        Scan all workflow files.

        Returns:
            [
                {
                    'name': 'Integration Tests',
                    'file': 'integration-tests.yml',
                    'triggers': ['push', 'pull_request'],
                    'branches': ['main', 'claude/*'],
                },
                ...
            ]
        """
        if not self.workflows_dir.exists():
            return []

        workflows = []

        for workflow_file in sorted(self.workflows_dir.glob("*.yml")):
            workflow_data = self._parse_workflow(workflow_file)
            if workflow_data:
                workflows.append(workflow_data)

        return workflows

    def _parse_workflow(self, workflow_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a workflow YAML file."""
        content = workflow_file.read_text()

        # First try YAML parsing
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            # YAML failed (embedded code), fall back to regex
            return self._parse_workflow_regex(workflow_file, content)

        if not data:
            return None

        # Extract name
        name = data.get("name", workflow_file.stem)

        # Extract triggers - YAML 1.1 treats 'on' as boolean True
        on_config = data.get("on") or data.get(True) or {}

        triggers = []
        if isinstance(on_config, dict):
            triggers = list(on_config.keys())
        elif isinstance(on_config, list):
            triggers = on_config
        elif isinstance(on_config, str):
            triggers = [on_config]

        # Extract branches (if any)
        branches = []
        if isinstance(on_config, dict):
            for trigger in ["push", "pull_request"]:
                if trigger in on_config and isinstance(on_config[trigger], dict):
                    branches.extend(on_config[trigger].get("branches", []))

        return {
            "name": name,
            "file": workflow_file.name,
            "triggers": triggers,
            "branches": list(set(branches)) if branches else ["any"],
        }

    def _parse_workflow_regex(self, workflow_file: Path, content: str) -> Dict[str, Any]:
        """Fallback regex parsing for workflows with embedded code."""
        # Extract name
        name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else workflow_file.stem

        # Extract triggers from 'on:' section
        triggers = []
        on_match = re.search(r"^on:\s*\n((?:  .+\n)+)", content, re.MULTILINE)
        if on_match:
            on_block = on_match.group(1)
            # Find trigger types (indented lines that end with ':')
            trigger_matches = re.findall(r"^  (\w+):", on_block, re.MULTILINE)
            triggers = trigger_matches

        # Extract branches
        branches = []
        branch_matches = re.findall(r"branches:\s*\[([^\]]+)\]", content)
        for match in branch_matches:
            branches.extend([b.strip().strip("'\"") for b in match.split(",")])

        return {
            "name": name,
            "file": workflow_file.name,
            "triggers": triggers if triggers else ["workflow"],
            "branches": list(set(branches)) if branches else ["any"],
        }


class GitActivityIntrospector:
    """Scan Git activity dynamically."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def get_activity(self) -> Dict[str, Any]:
        """
        Get Git activity.

        Returns:
            {
                'last_commit': {
                    'hash': 'abc123',
                    'message': 'feat: ...',
                    'author': 'Name',
                    'time': '2 hours ago',
                },
                'current_branch': 'claude/...',
                'status': 'clean' | 'modified',
            }
        """
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Get last commit
            log_result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%an|%ar"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )

            last_commit = {
                "hash": "unknown",
                "message": "unknown",
                "author": "unknown",
                "time": "unknown",
            }
            if log_result.returncode == 0 and log_result.stdout.strip():
                parts = log_result.stdout.strip().split("|")
                if len(parts) == 4:
                    last_commit = {
                        "hash": parts[0][:7],
                        "message": parts[1][:60],
                        "author": parts[2],
                        "time": parts[3],
                    }

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            status = "clean" if not status_result.stdout.strip() else "modified"

            return {
                "last_commit": last_commit,
                "current_branch": current_branch,
                "status": status,
            }

        except Exception as e:
            return {
                "last_commit": {
                    "hash": "error",
                    "message": str(e)[:50],
                    "author": "unknown",
                    "time": "unknown",
                },
                "current_branch": "unknown",
                "status": "error",
            }


class ParameterIntrospector:
    """Scan code for tunable constants."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def scan_economy_params(self) -> Dict[str, Any]:
        """Scan CIVIC tools for economic parameters."""
        params = {}

        # Search multiple files for economy parameters
        civic_tools = self.root_dir / "steward" / "system_agents" / "civic" / "tools"
        registry_file = self.root_dir / "steward" / "system_agents" / "civic" / "registry_agent.py"

        files_to_scan = []
        if civic_tools.exists():
            files_to_scan.extend(civic_tools.glob("*.py"))
        if registry_file.exists():
            files_to_scan.append(registry_file)

        for file_path in files_to_scan:
            try:
                content = file_path.read_text()

                # Look for initial_credits pattern
                if "starting_credits" not in params:
                    match = re.search(r'initial_credits["\']?\s*[,:=]\s*(\d+)', content)
                    if match:
                        params["starting_credits"] = int(match.group(1))
                        params["starting_credits_source"] = file_path.name

                # Look for transaction costs
                if "transfer_cost" not in params:
                    match = re.search(r"(?:transfer|transaction).*?cost.*?=\s*(\d+)", content, re.IGNORECASE)
                    if match:
                        params["transfer_cost"] = int(match.group(1))

            except Exception:
                continue

        # If still not found, note it's not discoverable
        if "starting_credits" not in params:
            params["starting_credits"] = "not discoverable"
            params["note"] = "No STARTING_CREDITS constant found - values inline in code"

        return params

    def scan_security_params(self) -> Dict[str, Any]:
        """Scan narasimha.py for security parameters."""
        narasimha_file = self.root_dir / "vibe_core" / "narasimha.py"

        if not narasimha_file.exists():
            return {}

        try:
            content = narasimha_file.read_text()

            # Extract UNFORGIVABLE_CRIMES list - find string literals only
            crimes_match = re.search(r"UNFORGIVABLE_CRIMES\s*=\s*\[(.*?)\]", content, re.DOTALL)

            crimes = []
            if crimes_match:
                crimes_text = crimes_match.group(1)
                # Extract only quoted strings (handles comments correctly)
                string_pattern = r'"([^"]+)"|\'([^\']+)\''
                matches = re.findall(string_pattern, crimes_text)
                # re.findall with groups returns tuples, get non-empty value
                crimes = [m[0] or m[1] for m in matches]

            return {
                "unforgivable_crimes": crimes,
                "location": "vibe_core/narasimha.py",
            }

        except Exception:
            return {"unforgivable_crimes": []}

    def scan_all_params(self) -> Dict[str, Any]:
        """Scan all tunable parameters."""
        return {
            "economy": self.scan_economy_params(),
            "security": self.scan_security_params(),
        }
