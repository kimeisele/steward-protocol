"""Circuit Configuration - Dynamic circuit loading from YAML files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class CircuitStep:
    """Single step in a circuit."""

    name: str
    agent: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitConfig:
    """Configuration for a single circuit/playbook."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    priority: str = "NORMAL"
    enabled: bool = True
    steps: List[CircuitStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "CircuitConfig":
        """Create CircuitConfig from parsed YAML dict."""
        steps = []
        for step_data in data.get("steps", []):
            steps.append(
                CircuitStep(
                    name=step_data.get("name", ""),
                    agent=step_data.get("agent", ""),
                    action=step_data.get("action", ""),
                    params=step_data.get("params", {}),
                )
            )

        return cls(
            name=name,
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            priority=data.get("priority", "NORMAL"),
            enabled=data.get("enabled", True),
            steps=steps,
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_file(cls, path: Path) -> Optional["CircuitConfig"]:
        """Load a circuit from a YAML file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            name = path.stem  # filename without extension
            return cls.from_dict(name, data)
        except Exception:
            return None


def discover_circuits(circuits_dir: Path) -> Dict[str, CircuitConfig]:
    """
    Auto-discover all circuit configurations from a directory.

    Args:
        circuits_dir: Path to circuits directory

    Returns:
        Dict mapping circuit names to their configs
    """
    circuits: Dict[str, CircuitConfig] = {}

    if not circuits_dir.exists():
        return circuits

    for yaml_file in circuits_dir.rglob("*.yaml"):
        # Skip templates and hidden files
        if yaml_file.name.startswith("_") or yaml_file.name.startswith("."):
            continue
        if "template" in yaml_file.name.lower():
            continue

        circuit = CircuitConfig.from_file(yaml_file)
        if circuit:
            circuits[circuit.name] = circuit

    return circuits
