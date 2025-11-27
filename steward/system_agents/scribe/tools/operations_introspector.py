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
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


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
        try:
            content = workflow_file.read_text()
            data = yaml.safe_load(content)

            if not data:
                return None

            # Extract name
            name = data.get('name', workflow_file.stem)

            # Extract triggers
            triggers = []
            on_config = data.get('on', {})

            if isinstance(on_config, dict):
                triggers = list(on_config.keys())
            elif isinstance(on_config, list):
                triggers = on_config
            elif isinstance(on_config, str):
                triggers = [on_config]

            # Extract branches (if any)
            branches = []
            if isinstance(on_config, dict):
                for trigger in ['push', 'pull_request']:
                    if trigger in on_config and isinstance(on_config[trigger], dict):
                        branches.extend(on_config[trigger].get('branches', []))

            return {
                'name': name,
                'file': workflow_file.name,
                'triggers': triggers,
                'branches': list(set(branches)) if branches else ['any'],
            }

        except Exception as e:
            return {
                'name': workflow_file.stem,
                'file': workflow_file.name,
                'triggers': ['unknown'],
                'branches': [],
                'error': str(e)[:50]
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
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'

            # Get last commit
            log_result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%s|%an|%ar'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            last_commit = {'hash': 'unknown', 'message': 'unknown', 'author': 'unknown', 'time': 'unknown'}
            if log_result.returncode == 0 and log_result.stdout.strip():
                parts = log_result.stdout.strip().split('|')
                if len(parts) == 4:
                    last_commit = {
                        'hash': parts[0][:7],
                        'message': parts[1][:60],
                        'author': parts[2],
                        'time': parts[3],
                    }

            # Get status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            status = 'clean' if not status_result.stdout.strip() else 'modified'

            return {
                'last_commit': last_commit,
                'current_branch': current_branch,
                'status': status,
            }

        except Exception as e:
            return {
                'last_commit': {'hash': 'error', 'message': str(e)[:50], 'author': 'unknown', 'time': 'unknown'},
                'current_branch': 'unknown',
                'status': 'error',
            }


class ParameterIntrospector:
    """Scan code for tunable constants."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def scan_economy_params(self) -> Dict[str, Any]:
        """Scan economy.py for tunable parameters."""
        economy_file = self.root_dir / "steward" / "system_agents" / "civic" / "tools" / "economy.py"

        if not economy_file.exists():
            return {}

        try:
            content = economy_file.read_text()

            params = {}

            # Look for STARTING_BALANCE or similar
            patterns = {
                'starting_credits': r'STARTING.*?=\s*(\d+)',
                'api_cost': r'API.*?COST.*?=\s*(\d+)',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    params[key] = int(match.group(1))

            # Default values if not found
            if 'starting_credits' not in params:
                params['starting_credits'] = 100  # Known default

            return params

        except Exception:
            return {'starting_credits': 100}

    def scan_security_params(self) -> Dict[str, Any]:
        """Scan narasimha.py for security parameters."""
        narasimha_file = self.root_dir / "vibe_core" / "narasimha.py"

        if not narasimha_file.exists():
            return {}

        try:
            content = narasimha_file.read_text()

            # Extract UNFORGIVABLE_CRIMES list
            crimes_match = re.search(
                r'UNFORGIVABLE_CRIMES\s*=\s*\[(.*?)\]',
                content,
                re.DOTALL
            )

            crimes = []
            if crimes_match:
                crimes_text = crimes_match.group(1)
                crimes = [
                    c.strip().strip('"').strip("'")
                    for c in crimes_text.split(',')
                    if c.strip()
                ]

            return {
                'unforgivable_crimes': crimes,
                'location': 'vibe_core/narasimha.py',
            }

        except Exception:
            return {'unforgivable_crimes': []}

    def scan_all_params(self) -> Dict[str, Any]:
        """Scan all tunable parameters."""
        return {
            'economy': self.scan_economy_params(),
            'security': self.scan_security_params(),
        }
