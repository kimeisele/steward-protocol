#!/usr/bin/env python3
"""
SCRIBE Introspection Module - Extract metadata from codebase
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class CartridgeIntrospector:
    """Scan and extract metadata from cartridge files."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.agents: Dict[str, Dict[str, Any]] = {}

    def scan_all(self, scan_path: Path = None) -> Dict[str, Dict[str, Any]]:
        """Scan all */cartridge_main.py files."""
        if scan_path is None:
            scan_path = self.root_dir

        cartridge_files = sorted(scan_path.glob("*/cartridge_main.py"))
        self.agents = {}

        for cartridge_file in cartridge_files:
            agent_name = cartridge_file.parent.name
            agent_path = cartridge_file.parent  # Store full path
            metadata = self._extract_metadata(cartridge_file, agent_name, agent_path)
            if metadata:
                self.agents[agent_name] = metadata

        return self.agents

    def _extract_metadata(
        self, cartridge_file: Path, agent_name: str, agent_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Extract metadata from a cartridge file."""
        try:
            content = cartridge_file.read_text()
        except Exception as e:
            print(f"Error reading {cartridge_file}: {e}")
            return None

        # Extract module docstring
        module_doc = self._extract_module_docstring(content)

        # Extract class name
        class_match = re.search(r"class\s+(\w+Cartridge)\s*\(", content)
        if not class_match:
            return None
        class_name = class_match.group(1)

        # Extract class docstring
        class_doc = self._extract_class_docstring(content, class_name)

        # Extract metadata fields
        metadata = {
            "agent_name": agent_name,
            "agent_name_pretty": agent_name.upper(),
            "class_name": class_name,
            "module_doc": module_doc,
            "class_doc": class_doc,
            "version": self._extract_field(content, "version"),
            "description": self._extract_field(content, "description"),
            "author": self._extract_field(content, "author"),
            "domain": self._extract_field(content, "domain"),
            "tools": self._discover_tools(agent_path),  # Pass full path!
        }

        return metadata

    def _extract_module_docstring(self, content: str) -> str:
        """Extract module-level docstring."""
        match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            first_line = text.split("\n")[0].strip()
            return first_line
        return ""

    def _extract_class_docstring(self, content: str, class_name: str) -> str:
        """Extract class docstring."""
        pattern = rf'class\s+{class_name}\s*\(.*?"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            lines = text.split("\n")
            return lines[0].strip() if lines else ""
        return ""

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract field value from code."""
        pattern = rf'{field_name}\s*=\s*["\']([^"\']*)["\']'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return "1.0.0" if field_name == "version" else ""

    def _discover_tools(self, agent_path: Path) -> List[Dict[str, str]]:
        """Find all tools for an agent."""
        tools_dir = agent_path / "tools"
        tools = []

        if tools_dir.exists():
            for tool_file in sorted(tools_dir.glob("*.py")):
                if tool_file.name == "__init__.py":
                    continue

                tool_name = self._tool_filename_to_name(tool_file.stem)
                tool_doc = self._extract_tool_docstring(tool_file)

                tools.append(
                    {
                        "name": tool_name,
                        "file": tool_file.stem + ".py",
                        "description": tool_doc,
                    }
                )

        return tools

    def _tool_filename_to_name(self, filename: str) -> str:
        """Convert filename to tool name."""
        name = filename.replace("_tool", "").replace("_", " ").title().replace(" ", "")
        return name

    def _extract_tool_docstring(self, tool_file: Path) -> str:
        """Extract docstring from tool file."""
        try:
            content = tool_file.read_text()
            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                text = match.group(1).strip()
                first_line = text.split("\n")[0].strip()
                return first_line
            return ""
        except:
            return ""


class ScriptIntrospector:
    """Scan and extract metadata from scripts."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def discover_entry_points(self) -> List[Dict[str, str]]:
        """Find all scripts in scripts/ directory."""
        scripts_dir = self.root_dir / "scripts"
        entry_points = []

        if not scripts_dir.exists():
            return entry_points

        for script_file in sorted(scripts_dir.glob("*.py")):
            if script_file.name == "__init__.py":
                continue

            name = script_file.stem
            description = self._extract_script_doc(script_file)

            entry_points.append(
                {
                    "name": name,
                    "path": str(script_file.relative_to(self.root_dir)),
                    "description": description,
                }
            )

        return entry_points

    def _extract_script_doc(self, script_file: Path) -> str:
        """Extract docstring from script."""
        try:
            content = script_file.read_text()
            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                text = match.group(1).strip()
                first_line = text.split("\n")[0].strip()
                return first_line
            return ""
        except:
            return ""


class ConfigIntrospector:
    """Load and analyze configuration files."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def get_pyproject_info(self) -> Dict[str, Any]:
        """Parse pyproject.toml for project info."""
        import toml

        pyproject_file = self.root_dir / "pyproject.toml"
        if pyproject_file.exists():
            try:
                data = toml.load(str(pyproject_file))
                project = data.get("project", {})
                return {
                    "name": project.get("name", "steward-protocol"),
                    "version": project.get("version", "0.2.0"),
                    "description": project.get("description", ""),
                    "readme": project.get("readme", "README.md"),
                    "python_requires": project.get("requires-python", ">=3.8"),
                }
            except:
                pass

        return {}

    def get_readme_exists(self) -> bool:
        """Check if README.md exists."""
        return (self.root_dir / "README.md").exists()

    def load_agents_from_registry(self) -> List[str]:
        """Extract agent names from AGENTS.md if it exists."""
        agents_file = self.root_dir / "AGENTS.md"
        agents = []

        if agents_file.exists():
            try:
                content = agents_file.read_text()
                pattern = r"### 🤖 (\w+)"
                matches = re.findall(pattern, content)
                agents = list(dict.fromkeys(matches))
            except:
                pass

        return agents
