#!/usr/bin/env python3
"""
VibeCoreIntrospector - Dynamic discovery of vibe_core modules

Scans vibe_core/*.py files and extracts metadata from docstrings.
NO HARDCODING - discovers all modules dynamically.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class VibeCoreIntrospector:
    """Scan and extract metadata from vibe_core/*.py files."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.vibe_core_dir = self.root_dir / "vibe_core"

    def scan_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan all vibe_core/*.py files dynamically.

        Returns:
            {
                'sarga': {'purpose': '...', 'features': [...], 'lines': 354},
                'narasimha': {...},
                ...
            }
        """
        if not self.vibe_core_dir.exists():
            return {}

        modules = {}

        # Dynamic discovery - find all .py files
        for py_file in sorted(self.vibe_core_dir.glob("*.py")):
            if py_file.name.startswith("__"):
                continue

            module_name = py_file.stem
            metadata = self._extract_module_metadata(py_file)

            if metadata:
                metadata["file"] = str(py_file.relative_to(self.root_dir))
                metadata["lines"] = self._count_lines(py_file)
                modules[module_name] = metadata

        return modules

    def _extract_module_metadata(self, py_file: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from module docstring."""
        try:
            content = py_file.read_text()
        except Exception:
            return None

        # Extract module docstring
        docstring = self._extract_docstring(content)
        if not docstring:
            return None

        # Parse docstring for purpose and features
        lines = docstring.split("\n")
        purpose = lines[0].strip() if lines else "Unknown purpose"

        # Look for key concepts/features in docstring
        features = self._extract_features(docstring, content)

        return {
            "purpose": purpose,
            "description": docstring[:200],  # First 200 chars
            "features": features,
        }

    def _extract_docstring(self, content: str) -> str:
        """Extract module-level docstring."""
        match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_features(self, docstring: str, content: str) -> List[str]:
        """Extract key features from docstring and code."""
        features = []

        # Look for enums (common pattern in vibe_core)
        enum_matches = re.findall(r"class\s+(\w+)\(.*?Enum\)", content)
        if enum_matches:
            features.extend([f"{name} enum" for name in enum_matches[:3]])

        # Look for main classes
        class_matches = re.findall(r"class\s+(\w+)(?!\(.*?Enum)", content)
        if class_matches:
            features.extend([f"{name} class" for name in class_matches[:2]])

        # Look for key functions
        func_matches = re.findall(r"def\s+(\w+)\(", content)
        key_funcs = [f for f in func_matches if not f.startswith("_")][:3]
        if key_funcs:
            features.extend([f"{name}()" for name in key_funcs])

        return features[:5]  # Limit to 5 features

    def _count_lines(self, py_file: Path) -> int:
        """Count lines in file."""
        try:
            return len(py_file.read_text().split("\n"))
        except:
            return 0


class ToolsIntrospector:
    """Scan and extract metadata from agent tools (*/tools/*.py files)."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.agents_dir = self.root_dir / "steward" / "system_agents"

    def scan_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan all */tools/*.py files dynamically.

        Returns:
            {
                'envoy': [
                    {'name': 'milk_ocean', 'purpose': '...', 'lines': 741},
                    ...
                ],
                'civic': [...],
                ...
            }
        """
        if not self.agents_dir.exists():
            return {}

        tools_by_agent = {}

        # Dynamic discovery - find all agent directories
        for agent_dir in sorted(self.agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            tools_dir = agent_dir / "tools"
            if not tools_dir.exists():
                continue

            agent_name = agent_dir.name
            tools = []

            # Scan all tools for this agent
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.name.startswith("__"):
                    continue

                tool_metadata = self._extract_tool_metadata(tool_file)
                if tool_metadata:
                    tool_metadata["file"] = str(tool_file.relative_to(self.root_dir))
                    tool_metadata["lines"] = self._count_lines(tool_file)
                    tools.append(tool_metadata)

            if tools:
                tools_by_agent[agent_name] = tools

        return tools_by_agent

    def _extract_tool_metadata(self, tool_file: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from tool file."""
        try:
            content = tool_file.read_text()
        except Exception:
            return None

        # Extract module docstring
        docstring = self._extract_docstring(content)
        purpose = docstring.split("\n")[0].strip() if docstring else "Unknown tool"

        return {
            "name": tool_file.stem,
            "purpose": purpose,
            "description": docstring[:150] if docstring else "",
        }

    def _extract_docstring(self, content: str) -> str:
        """Extract module-level docstring."""
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _count_lines(self, tool_file: Path) -> int:
        """Count lines in file."""
        try:
            return len(tool_file.read_text().split("\n"))
        except:
            return 0
