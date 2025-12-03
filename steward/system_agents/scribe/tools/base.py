#!/usr/bin/env python3
"""
SCRIBE Tool Base - Shared boilerplate for all renderers

Eliminates DRY violation across renderer modules.
Provides Tool and ToolResult for both kernel-managed and standalone modes.
Includes template loading utilities.

Tool Protocol Compliant.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, Template

# Circuit YAML path for auto-generated docs registry
CIRCUIT_PATH = "vibe_core/playbook/circuits/doc_index_render.yaml"

# Tool Protocol import - optional for standalone mode
try:
    from vibe_core.tools.tool_protocol import Tool as KernelTool
    from vibe_core.tools.tool_protocol import ToolResult as KernelToolResult

    TOOL_PROTOCOL_AVAILABLE = True

    # Use kernel versions
    Tool = KernelTool
    ToolResult = KernelToolResult

except ImportError:
    TOOL_PROTOCOL_AVAILABLE = False

    # Standalone fallback implementations
    class Tool:
        """Base class for tools (standalone mode)."""

        @property
        def name(self) -> str:
            raise NotImplementedError

        @property
        def description(self) -> str:
            raise NotImplementedError

        @property
        def parameters_schema(self) -> dict[str, Any]:
            raise NotImplementedError

        def validate(self, parameters: dict[str, Any]) -> None:
            raise NotImplementedError

        def execute(self, parameters: dict[str, Any]) -> "ToolResult":
            raise NotImplementedError

    class ToolResult:
        """Result of tool execution (standalone mode)."""

        def __init__(self, success: bool, output: Any = None, error: str = None):
            self.success = success
            self.output = output
            self.error = error

        def __repr__(self) -> str:
            if self.success:
                return f"ToolResult(success=True, output={self.output!r})"
            return f"ToolResult(success=False, error={self.error!r})"


def get_template_dir() -> Path:
    """Get the SCRIBE templates directory path."""
    return Path(__file__).parent.parent / "templates"


def get_kernel_status(root_dir: str = ".") -> Dict[str, Any]:
    """
    Check kernel status by reading vibe_snapshot.json.

    Returns kernel status dict for unified header template:
    {
        'running': bool,
        'status': str,  # 'RUNNING' | 'NOT DETECTED'
        'agents': int,
        'last_pulse': str,  # timestamp or 'never'
    }

    Logic:
    - If vibe_snapshot.json exists and timestamp < 5 min old -> RUNNING
    - Otherwise -> NOT DETECTED
    """
    snapshot_path = Path(root_dir) / "vibe_snapshot.json"
    max_age_seconds = 300  # 5 minutes

    result = {
        "running": False,
        "status": "NOT DETECTED",
        "agents": 0,
        "last_pulse": "never",
    }

    if not snapshot_path.exists():
        return result

    try:
        data = json.loads(snapshot_path.read_text())

        # Check timestamp freshness
        timestamp_str = data.get("timestamp", "")
        if timestamp_str:
            result["last_pulse"] = timestamp_str

            # Parse ISO timestamp and check age
            from datetime import datetime

            try:
                pulse_time = datetime.fromisoformat(timestamp_str)
                age_seconds = (datetime.now() - pulse_time).total_seconds()

                if age_seconds < max_age_seconds:
                    result["running"] = True
                    result["status"] = data.get("kernel_status", "RUNNING")
                    result["agents"] = len(data.get("agents", {}))
                else:
                    result["status"] = f"STALE ({int(age_seconds)}s ago)"
            except ValueError:
                pass

    except (json.JSONDecodeError, OSError):
        pass

    return result


def load_template(template_name: str, fallback: Optional[str] = None) -> Template:
    """Load a Jinja2 template from the templates directory.

    Args:
        template_name: Name of template file (e.g., 'readme.jinja2')
        fallback: Optional fallback template string if file not found

    Returns:
        Jinja2 Template object
    """
    template_dir = get_template_dir()
    template_file = template_dir / template_name

    if template_file.exists():
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        return env.get_template(template_name)
    elif fallback:
        return Template(fallback)
    else:
        raise FileNotFoundError(f"Template not found: {template_name}")


def get_auto_docs(root_dir: str = ".") -> List[Dict[str, str]]:
    """Load auto-generated docs registry from circuit YAML.

    Returns list of auto-generated doc entries from doc_index_render.yaml.
    This is the SINGLE SOURCE OF TRUTH for header navigation.

    Returns:
        List of dicts with 'name', 'file', 'description' keys
    """
    circuit_file = Path(root_dir) / CIRCUIT_PATH
    if not circuit_file.exists():
        # Fallback if circuit not found
        return [
            {"name": "README", "file": "README.md"},
            {"name": "INDEX", "file": "INDEX.md"},
        ]

    try:
        with open(circuit_file) as f:
            data = yaml.safe_load(f)
        circuit = data.get("circuit", {})
        return circuit.get("auto_generated_docs", [])
    except (yaml.YAMLError, OSError):
        return []


def format_auto_docs_nav(auto_docs: List[Dict[str, str]]) -> str:
    """Format auto-docs list as markdown navigation string.

    Args:
        auto_docs: List from get_auto_docs()

    Returns:
        Markdown string like "[README](README.md) · [INDEX](INDEX.md) · ..."
    """
    links = [f"[{doc['name']}]({doc['file']})" for doc in auto_docs]
    return " · ".join(links)


def format_auto_docs_box(auto_docs: List[Dict[str, str]]) -> str:
    """Format auto-docs list for ASCII box in header.

    Args:
        auto_docs: List from get_auto_docs()

    Returns:
        Two-line string for ASCII box display
    """
    names = [doc["name"] for doc in auto_docs]
    # Split into two lines of ~6 items each
    mid = (len(names) + 1) // 2
    line1 = " | ".join(names[:mid])
    line2 = " | ".join(names[mid:]) if mid < len(names) else ""
    return line1, line2


__all__ = [
    "Tool",
    "ToolResult",
    "TOOL_PROTOCOL_AVAILABLE",
    "get_template_dir",
    "get_kernel_status",
    "load_template",
    "get_auto_docs",
    "format_auto_docs_nav",
    "format_auto_docs_box",
]
