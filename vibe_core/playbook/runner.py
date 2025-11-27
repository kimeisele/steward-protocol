#!/usr/bin/env python3
"""
GAD-913: Playbook Runner (Cartridge Slot Implementation)
=========================================================

Connects Playbook definitions to CoreOrchestrator execution.

A "Playbook" is a YAML preset that configures the Orchestrator dynamically:
- Loads workflow definition (YAML)
- Validates it against schema
- Configures orchestrator with agents, phases, tools
- Executes the workflow to completion

This is the "Cartridge Slot" - insert a playbook, system executes it.

Responsibilities:
1. Load playbook YAML file
2. Validate against playbook schema (simpler than workflow schema)
3. Convert to Orchestrator configuration
4. Execute through CoreOrchestrator
5. Track execution and results

Version: 0.1 (Foundation)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class PlaybookError(Exception):
    """Base exception for playbook errors"""

    pass


class PlaybookValidationError(PlaybookError):
    """Raised when playbook validation fails"""

    pass


class PlaybookExecutionError(PlaybookError):
    """Raised when playbook execution fails"""

    pass


@dataclass
class PlaybookAgent:
    """Agent configuration from playbook"""

    name: str
    role: str
    skills: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybookTool:
    """Tool configuration from playbook"""

    name: str
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybookPhase:
    """SDLC phase configuration from playbook"""

    name: str
    description: str
    agents: list[str]  # Agent names to activate
    tools: list[str] = field(default_factory=list)  # Tool names to enable
    input_artifact: str | None = None
    output_artifact: str | None = None
    skip_if_present: str | None = None  # Skip phase if this artifact exists


@dataclass
class PlaybookDefinition:
    """Complete playbook definition"""

    id: str
    name: str
    description: str
    version: str
    phases: list[PlaybookPhase]
    agents: dict[str, PlaybookAgent]
    tools: dict[str, PlaybookTool]
    metadata: dict[str, Any] = field(default_factory=dict)


class PlaybookValidator:
    """Validates playbook YAML against schema"""

    def __init__(self):
        """Initialize validator"""
        pass

    def validate(self, data: dict[str, Any]) -> tuple[bool, str]:
        """
        Validate playbook data.

        Args:
            data: Parsed YAML data

        Returns:
            (is_valid, message)
        """
        # Check required top-level fields
        required_fields = ["id", "name", "description", "version", "phases", "agents"]
        for field_name in required_fields:
            if field_name not in data:
                return False, f"Missing required field: {field_name}"

        # Validate phases
        if not data.get("phases"):
            return False, "At least one phase is required"

        for i, phase in enumerate(data["phases"]):
            if "name" not in phase:
                return False, f"Phase {i} missing required field: name"
            if "agents" not in phase:
                return False, f"Phase {i} ({phase.get('name')}) missing required field: agents"
            if not isinstance(phase["agents"], list):
                return False, f"Phase {i} agents must be a list"

        # Validate agents
        if not data.get("agents"):
            return False, "At least one agent is required"

        for agent_name, agent_def in data.get("agents", {}).items():
            if "role" not in agent_def:
                return False, f"Agent '{agent_name}' missing required field: role"

        # Validate phase agent references
        available_agents = set(data["agents"].keys())
        for phase in data["phases"]:
            for agent_name in phase.get("agents", []):
                if agent_name not in available_agents:
                    return (
                        False,
                        f"Phase '{phase['name']}' references undefined agent: {agent_name}",
                    )

        return True, "Playbook is valid"


class PlaybookLoader:
    """Loads and validates playbook YAML files"""

    def __init__(self):
        """Initialize loader"""
        self.validator = PlaybookValidator()

    def load_playbook(self, yaml_path: str | Path) -> PlaybookDefinition:
        """
        Load and validate a playbook YAML file.

        Args:
            yaml_path: Path to playbook YAML file

        Returns:
            PlaybookDefinition object

        Raises:
            PlaybookError: If file cannot be loaded or is invalid
        """
        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            raise PlaybookError(f"Playbook file not found: {yaml_path}")

        # Load YAML
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            logger.info(f"Loaded playbook from {yaml_path}")
        except yaml.YAMLError as e:
            raise PlaybookError(f"Invalid YAML in {yaml_path}: {e}")

        if data is None:
            raise PlaybookError(f"Playbook file is empty: {yaml_path}")

        # Validate
        is_valid, message = self.validator.validate(data)
        if not is_valid:
            raise PlaybookValidationError(f"Playbook validation failed: {message}")

        logger.info(f"Playbook validated: {data['id']}")

        # Convert to PlaybookDefinition
        return self._build_playbook(data)

    def _build_playbook(self, data: dict[str, Any]) -> PlaybookDefinition:
        """Convert YAML dict to PlaybookDefinition"""

        # Parse agents
        agents = {}
        for agent_name, agent_def in data.get("agents", {}).items():
            agent = PlaybookAgent(
                name=agent_name,
                role=agent_def["role"],
                skills=agent_def.get("skills", []),
                config=agent_def.get("config", {}),
            )
            agents[agent_name] = agent

        # Parse tools
        tools = {}
        for tool_name, tool_def in data.get("tools", {}).items():
            if isinstance(tool_def, dict):
                tool = PlaybookTool(
                    name=tool_name,
                    enabled=tool_def.get("enabled", True),
                    config=tool_def.get("config", {}),
                )
            else:
                # Simple boolean or string
                tool = PlaybookTool(name=tool_name, enabled=bool(tool_def))
            tools[tool_name] = tool

        # Parse phases
        phases = []
        for phase_def in data.get("phases", []):
            phase = PlaybookPhase(
                name=phase_def["name"],
                description=phase_def.get("description", ""),
                agents=phase_def["agents"],
                tools=phase_def.get("tools", []),
                input_artifact=phase_def.get("input_artifact"),
                output_artifact=phase_def.get("output_artifact"),
                skip_if_present=phase_def.get("skip_if_present"),
            )
            phases.append(phase)

        # Build final definition
        playbook = PlaybookDefinition(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            phases=phases,
            agents=agents,
            tools=tools,
            metadata=data.get("metadata", {}),
        )

        logger.info(
            f"Built playbook: {playbook.name} ({playbook.id}) with "
            f"{len(playbook.phases)} phases, {len(playbook.agents)} agents"
        )

        return playbook


class PlaybookRegistry:
    """Registry of available playbooks"""

    def __init__(self, registry_dir: str | Path = None):
        """
        Initialize registry.

        Args:
            registry_dir: Directory containing playbook presets
        """
        if registry_dir is None:
            # Default: look in playbooks/presets/
            registry_dir = Path(__file__).parent.parent.parent / "playbooks" / "presets"

        self.registry_dir = Path(registry_dir)
        self.loader = PlaybookLoader()
        self.playbooks: dict[str, PlaybookDefinition] = {}

        logger.info(f"PlaybookRegistry initialized at {self.registry_dir}")

    def load_all(self) -> None:
        """Load all playbooks from registry directory"""
        if not self.registry_dir.exists():
            logger.warning(f"Registry directory not found: {self.registry_dir}")
            return

        for yaml_file in self.registry_dir.glob("*.yaml"):
            if yaml_file.name.startswith("_"):
                continue

            try:
                playbook = self.loader.load_playbook(yaml_file)
                self.playbooks[playbook.id] = playbook
                logger.info(f"Registered playbook: {playbook.id}")
            except PlaybookError as e:
                logger.error(f"Failed to load playbook {yaml_file.name}: {e}")

    def get(self, playbook_id: str) -> PlaybookDefinition | None:
        """Get playbook by ID"""
        return self.playbooks.get(playbook_id)

    def list(self) -> list[PlaybookDefinition]:
        """List all registered playbooks"""
        return list(self.playbooks.values())

    def has(self, playbook_id: str) -> bool:
        """Check if playbook exists"""
        return playbook_id in self.playbooks


class PlaybookRunner:
    """
    Executes playbooks using the Orchestrator.

    This is the main entry point for "cartridge slot" functionality.
    """

    def __init__(self, orchestrator=None):
        """
        Initialize runner.

        Args:
            orchestrator: CoreOrchestrator instance (optional for lazy loading)
        """
        self.orchestrator = orchestrator
        self.registry = PlaybookRegistry()
        self.loader = PlaybookLoader()
        self.execution_history: list[dict[str, Any]] = []

    def load_registry(self) -> None:
        """Load all playbooks from registry"""
        self.registry.load_all()
        logger.info(f"Loaded {len(self.registry.list())} playbooks from registry")

    def run_playbook(
        self, playbook_id: str, project_context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Execute a playbook by ID.

        Args:
            playbook_id: ID of playbook to execute
            project_context: Project context (name, description, etc.)

        Returns:
            Execution results dictionary

        Raises:
            PlaybookError: If playbook not found or execution fails
        """
        playbook = self.registry.get(playbook_id)
        if playbook is None:
            raise PlaybookError(f"Playbook not found: {playbook_id}")

        logger.info(f"Running playbook: {playbook.name} ({playbook.id})")

        return self.execute_playbook(playbook, project_context)

    def run_playbook_file(
        self, yaml_path: str | Path, project_context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Execute a playbook from YAML file.

        Args:
            yaml_path: Path to playbook YAML file
            project_context: Project context

        Returns:
            Execution results
        """
        playbook = self.loader.load_playbook(yaml_path)
        logger.info(f"Running playbook from file: {yaml_path}")
        return self.execute_playbook(playbook, project_context)

    def execute_playbook(
        self, playbook: PlaybookDefinition, project_context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Execute a playbook definition.

        Args:
            playbook: PlaybookDefinition to execute
            project_context: Project context

        Returns:
            Execution results
        """
        if self.orchestrator is None:
            # Try to import and instantiate CoreOrchestrator
            try:
                from apps.agency.orchestrator.core_orchestrator import CoreOrchestrator

                # Get repo root (parent of vibe_core)
                repo_root = Path(__file__).parent.parent.parent
                self.orchestrator = CoreOrchestrator(repo_root=repo_root)
                logger.info("Lazy-loaded CoreOrchestrator")
            except ImportError as e:
                raise PlaybookExecutionError(f"Cannot import CoreOrchestrator: {e}")
            except TypeError as e:
                raise PlaybookExecutionError(f"Cannot initialize CoreOrchestrator: {e}")

        result = {
            "playbook_id": playbook.id,
            "playbook_name": playbook.name,
            "status": "running",
            "phases_executed": [],
            "errors": [],
        }

        try:
            # Configure orchestrator with playbook
            logger.info(f"Configuring orchestrator for playbook: {playbook.id}")

            # Set up project context
            if project_context is None:
                project_context = {
                    "name": f"Playbook: {playbook.name}",
                    "description": playbook.description,
                }

            # Execute each phase
            for phase in playbook.phases:
                phase_result = self._execute_phase(phase, playbook)
                result["phases_executed"].append(phase_result)

                if phase_result.get("status") == "failed":
                    result["status"] = "failed"
                    result["errors"].append(phase_result.get("error"))
                    break

            if result["status"] == "running":
                result["status"] = "success"

        except Exception as e:
            logger.error(f"Playbook execution failed: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))

        self.execution_history.append(result)
        return result

    def _execute_phase(self, phase: PlaybookPhase, playbook: PlaybookDefinition) -> dict[str, Any]:
        """
        Execute a single phase.

        Args:
            phase: Phase to execute
            playbook: Parent playbook definition

        Returns:
            Phase execution result
        """
        logger.info(f"Executing phase: {phase.name}")

        result = {
            "phase_name": phase.name,
            "agents_activated": phase.agents,
            "tools_activated": phase.tools,
            "status": "success",
        }

        try:
            # In a real implementation, this would:
            # 1. Activate specified agents
            # 2. Enable specified tools
            # 3. Call orchestrator.execute_phase(phase)
            # 4. Track results

            # For now, just log the phase execution
            logger.info(f"  Agents: {', '.join(phase.agents)}")
            logger.info(f"  Tools: {', '.join(phase.tools)}")

        except Exception as e:
            logger.error(f"Phase execution failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def get_execution_history(self) -> list[dict[str, Any]]:
        """Get execution history"""
        return self.execution_history


def run_playbook_cli(
    playbook_id_or_path: str, project_context: dict[str, Any] = None
) -> dict[str, Any]:
    """
    Convenience function to run a playbook from CLI or scripts.

    Args:
        playbook_id_or_path: Playbook ID or file path
        project_context: Project context

    Returns:
        Execution results
    """
    runner = PlaybookRunner()

    # Try as ID first
    if Path(playbook_id_or_path).exists():
        return runner.run_playbook_file(playbook_id_or_path, project_context)
    else:
        runner.load_registry()
        return runner.run_playbook(playbook_id_or_path, project_context)


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 2:
        print("Usage: python runner.py <playbook_id_or_path>")
        sys.exit(1)

    playbook_arg = sys.argv[1]

    try:
        result = run_playbook_cli(playbook_arg)
        print("\n✅ Playbook execution complete:")
        print(f"   Status: {result['status']}")
        print(f"   Phases: {len(result['phases_executed'])}")
        if result.get("errors"):
            print(f"   Errors: {'; '.join(result['errors'])}")
    except PlaybookError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
