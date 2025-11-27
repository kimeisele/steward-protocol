#!/usr/bin/env python3
"""
Prompt Runtime - AOS v0.2 Composition Engine

Composes atomized prompt fragments (core + task + knowledge + gates + context)
into a final executable prompt for LLM execution.

Usage:
    runtime = PromptRuntime()
    result = runtime.execute_task(
        agent_id="GENESIS_BLUEPRINT",
        task_id="select_core_modules",
        context={...}
    )

Error Handling:
    - AgentNotFoundError: Unknown agent_id
    - TaskNotFoundError: Unknown task_id
    - MalformedYAMLError: Invalid YAML syntax
    - CompositionError: Failed to compose prompt
"""

import logging
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml

# Configure logging early (before any logger usage)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CRITICAL FIX #1: Import workspace utilities without sys.path manipulation
# Load workspace_utils dynamically from scripts directory
# Path calculation: /vibe_core/runtime/prompt_runtime.py -> parent(runtime) -> parent(vibe_core) -> parent(PROJECT_ROOT)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_WORKSPACE_UTILS_PATH = _REPO_ROOT / "scripts" / "workspace_utils.py"

try:
    if _WORKSPACE_UTILS_PATH.exists():
        spec = spec_from_file_location("workspace_utils", _WORKSPACE_UTILS_PATH)
        if spec and spec.loader:
            workspace_utils = module_from_spec(spec)
            spec.loader.exec_module(workspace_utils)
            get_active_workspace = workspace_utils.get_active_workspace
            resolve_artifact_base_path = workspace_utils.resolve_artifact_base_path
            WORKSPACE_UTILS_AVAILABLE = True
        else:
            raise ImportError("Failed to load workspace_utils spec")
    else:
        raise ImportError(f"workspace_utils.py not found at {_WORKSPACE_UTILS_PATH}")
except ImportError as e:
    logger.debug(f"workspace_utils not available: {e}")
    WORKSPACE_UTILS_AVAILABLE = False
    get_active_workspace = None  # type: ignore
    resolve_artifact_base_path = None  # type: ignore


# Custom Exceptions
class PromptRuntimeError(Exception):
    """Base exception for all PromptRuntime errors"""

    pass


class AgentNotFoundError(PromptRuntimeError):
    """Raised when agent_id not found in AGENT_REGISTRY"""

    pass


class TaskNotFoundError(PromptRuntimeError):
    """Raised when task files not found"""

    pass


class MalformedYAMLError(PromptRuntimeError):
    """Raised when YAML parsing fails"""

    pass


class CompositionError(PromptRuntimeError):
    """Raised when prompt composition fails"""

    pass


@dataclass
class CompositionSpec:
    """Parsed _composition.yaml structure"""

    composition_version: str
    agent_id: str
    agent_version: str
    composition_order: list[dict]
    variables: dict[str, str]
    conflict_resolution: dict
    metadata: dict
    tools: list[str] = None  # GAD-003: List of available tool names


@dataclass
class TaskMetadata:
    """Parsed task_*.meta.yaml structure"""

    task_id: str
    phase: int
    description: str
    dependencies: list[str]
    inputs: list[dict]
    outputs: list[dict]
    validation_gates: list[str]
    estimated_complexity: str
    estimated_tokens: int


class PromptRuntime:
    """
    Runtime engine for composing and executing atomized prompts.

    This is a PROTOTYPE - demonstrates the composition concept.
    Production version would integrate with actual LLM API.
    """

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            # Auto-detect repo root (3 levels up from prompt_runtime.py)
            # vibe_core/runtime/prompt_runtime.py -> vibe-agency/
            self.base_path = Path(__file__).resolve().parent.parent.parent
        else:
            self.base_path = Path(base_path)
        self.knowledge_cache = {}  # Cache loaded YAML files

    def execute_task(self, agent_id: str, task_id: str, context: dict[str, Any]) -> str:
        """
        Compose and execute an atomized task.

        Args:
            agent_id: Agent identifier (e.g., "GENESIS_BLUEPRINT")
            task_id: Task identifier (e.g., "select_core_modules")
            context: Runtime context (project_id, artifacts, etc.)

        Returns:
            Composed prompt string ready for LLM execution

        Raises:
            AgentNotFoundError: If agent_id not found
            TaskNotFoundError: If task files not found
            MalformedYAMLError: If YAML parsing fails
            CompositionError: If prompt composition fails
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"Executing: {agent_id}.{task_id}")
            print(f"{'=' * 60}\n")
            logger.info(f"Starting composition: {agent_id}.{task_id}")

            # CRITICAL FIX #1: Resolve workspace paths BEFORE composition
            if WORKSPACE_UTILS_AVAILABLE:
                workspace_name = context.get("workspace_name", get_active_workspace())
                artifact_base = resolve_artifact_base_path(workspace_name)

                # Inject resolved paths into context
                context["_resolved_workspace"] = workspace_name
                context["_resolved_artifact_base_path"] = str(artifact_base)
                context["_resolved_planning_path"] = str(artifact_base / "planning")
                context["_resolved_coding_path"] = str(artifact_base / "coding")
                context["_resolved_qa_path"] = str(artifact_base / "qa")
                context["_resolved_deployment_path"] = str(artifact_base / "deployment")

                print(f"✓ Workspace context resolved: {workspace_name}")
                print(f"  Artifact base: {artifact_base}")
                logger.info(f"Workspace: {workspace_name}, Artifacts: {artifact_base}")
            else:
                logger.warning("Workspace utilities not available - paths NOT resolved")

            # 1. Load composition spec
            comp_spec = self._load_composition_spec(agent_id)
            print(f"✓ Loaded composition spec (v{comp_spec.composition_version})")
            logger.debug(f"Composition spec loaded: version {comp_spec.composition_version}")

            # 2. Load task metadata
            task_meta = self._load_task_metadata(agent_id, task_id)
            print(f"✓ Loaded task metadata (phase {task_meta.phase})")
            logger.debug(f"Task metadata loaded: phase {task_meta.phase}")

            # 3. Resolve knowledge dependencies
            knowledge_files = self._resolve_knowledge_deps(agent_id, task_meta)
            print(f"✓ Resolved {len(knowledge_files)} knowledge dependencies")
            logger.debug(f"Knowledge dependencies resolved: {len(knowledge_files)} files")

            # 4. Compose final prompt
            final_prompt = self._compose_prompt(
                agent_id=agent_id,
                composition_spec=comp_spec,
                task_id=task_id,
                task_meta=task_meta,
                knowledge_files=knowledge_files,
                runtime_context=context,
            )

            # Validate prompt size
            prompt_size = len(final_prompt)
            print(f"✓ Composed final prompt ({prompt_size:,} chars)")

            if prompt_size > 200000:
                logger.warning(
                    f"Prompt size ({prompt_size:,} chars) exceeds recommended limit (200,000 chars). "
                    "This may cause LLM context window issues."
                )

            # 5. Validation gates (dry-run)
            if task_meta.validation_gates:
                print(f"✓ Validation gates loaded: {', '.join(task_meta.validation_gates)}")
                logger.debug(f"Validation gates: {task_meta.validation_gates}")

            print(f"\n{'=' * 60}")
            print("COMPOSITION COMPLETE")
            print(f"{'=' * 60}\n")

            logger.info(f"Composition successful: {agent_id}.{task_id} ({prompt_size:,} chars)")
            return final_prompt

        except (AgentNotFoundError, TaskNotFoundError, MalformedYAMLError) as e:
            logger.error(f"Composition failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during composition: {e}", exc_info=True)
            raise CompositionError(f"Failed to compose prompt for {agent_id}.{task_id}: {e}") from e

    def _load_composition_spec(self, agent_id: str) -> CompositionSpec:
        """
        Load and parse _composition.yaml

        Args:
            agent_id: Agent identifier

        Returns:
            CompositionSpec object

        Raises:
            AgentNotFoundError: If agent_id invalid
            FileNotFoundError: If _composition.yaml missing
            MalformedYAMLError: If YAML parsing fails
        """
        agent_path = self._get_agent_path(agent_id)
        comp_file = agent_path / "_composition.yaml"

        if not comp_file.exists():
            raise FileNotFoundError(
                f"Composition file not found: {comp_file}\n"
                f"Expected location: {agent_path}/_composition.yaml\n"
                f"Fix: Ensure agent '{agent_id}' has _composition.yaml file"
            )

        try:
            with open(comp_file) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise MalformedYAMLError(
                f"Invalid YAML syntax in {comp_file}\n"
                f"Error: {e}\n"
                f"Fix: Check YAML syntax at line {e.problem_mark.line if hasattr(e, 'problem_mark') else 'unknown'}"
            ) from e

        # Validate required fields
        required_fields = ["composition_version", "agent_id", "agent_version", "composition_order"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise MalformedYAMLError(
                f"Missing required fields in {comp_file}: {', '.join(missing)}\n"
                f"Fix: Add missing fields to _composition.yaml"
            )

        # GAD-003: Load tool definitions if agent uses tools
        tools_list = data.get("tools", [])

        return CompositionSpec(
            composition_version=data["composition_version"],
            agent_id=data["agent_id"],
            agent_version=data["agent_version"],
            composition_order=data["composition_order"],
            variables=data.get("variables", {}),
            conflict_resolution=data.get("conflict_resolution", {}),
            metadata=data.get("metadata", {}),
            tools=tools_list if tools_list else None,
        )

    def _load_task_metadata(self, agent_id: str, task_id: str) -> TaskMetadata:
        """
        Load and parse task_*.meta.yaml

        Args:
            agent_id: Agent identifier
            task_id: Task identifier

        Returns:
            TaskMetadata object

        Raises:
            TaskNotFoundError: If task files not found
            MalformedYAMLError: If YAML parsing fails
        """
        agent_path = self._get_agent_path(agent_id)

        # Try with task_ prefix first, fall back to bare task_id
        meta_file = agent_path / "tasks" / f"task_{task_id}.meta.yaml"
        if not meta_file.exists():
            meta_file = agent_path / "tasks" / f"{task_id}.meta.yaml"

        if not meta_file.exists():
            # Provide helpful error with available tasks
            tasks_dir = agent_path / "tasks"
            available_tasks = []
            if tasks_dir.exists():
                available_tasks = [
                    f.stem.replace("task_", "").replace(".meta", "")
                    for f in tasks_dir.glob("task_*.meta.yaml")
                ]

            raise TaskNotFoundError(
                f"Task metadata not found: {task_id}\n"
                f"Agent: {agent_id}\n"
                f"Searched:\n"
                f"  - {agent_path}/tasks/task_{task_id}.meta.yaml\n"
                f"  - {agent_path}/tasks/{task_id}.meta.yaml\n"
                f"Available tasks: {', '.join(available_tasks) if available_tasks else 'none'}\n"
                f"Fix: Check task_id spelling or create task metadata file"
            )

        try:
            with open(meta_file) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise MalformedYAMLError(
                f"Invalid YAML syntax in {meta_file}\nError: {e}\nFix: Check YAML syntax"
            ) from e

        # Validate required fields
        if "task_id" not in data or "phase" not in data:
            raise MalformedYAMLError(
                f"Missing required fields in {meta_file}\n"
                f"Required: task_id, phase\n"
                f"Fix: Add missing fields to task metadata"
            )

        return TaskMetadata(
            task_id=data["task_id"],
            phase=data["phase"],
            description=data.get("description", data.get("notes", "No description")),
            dependencies=data.get("dependencies", []),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            validation_gates=data.get("validation_gates", []),
            estimated_complexity=data.get("estimated_complexity", "unknown"),
            estimated_tokens=data.get("estimated_tokens", 0),
        )

    def _resolve_knowledge_deps(self, agent_id: str, task_meta: TaskMetadata) -> list[str]:
        """
        Resolve which knowledge YAML files to load for this task.

        Returns list of file contents (as YAML strings).
        """
        agent_path = self._get_agent_path(agent_id)
        deps_file = agent_path / "_knowledge_deps.yaml"

        with open(deps_file) as f:
            deps = yaml.safe_load(f)

        knowledge_files = []

        # Load required knowledge
        for req in deps.get("required_knowledge", []):
            # Check if this task uses this knowledge file
            # Note: YAMLs use 'used_in_tasks', not 'used_by_tasks'
            used_tasks = req.get("used_in_tasks", req.get("used_by_tasks", []))
            if task_meta.task_id in used_tasks:
                content = self._load_knowledge_file(req["path"])
                knowledge_files.append(f"# {req['purpose']}\n{content}")

        # Load optional knowledge (if conditions met)
        for opt in deps.get("optional_knowledge", []):
            used_tasks = opt.get("used_in_tasks", opt.get("used_by_tasks", []))
            if task_meta.task_id in used_tasks:
                content = self._load_knowledge_file(opt["path"])
                knowledge_files.append(f"# {opt['purpose']}\n{content}")

        return knowledge_files

    def _load_knowledge_file(self, relative_path: str) -> str:
        """Load a knowledge YAML file (with caching)"""
        if relative_path in self.knowledge_cache:
            return self.knowledge_cache[relative_path]

        full_path = self.base_path / relative_path

        with open(full_path) as f:
            content = f.read()

        self.knowledge_cache[relative_path] = content
        return content

    def _compose_prompt(
        self,
        agent_id: str,
        composition_spec: CompositionSpec,
        task_id: str,
        task_meta: TaskMetadata,
        knowledge_files: list[str],
        runtime_context: dict[str, Any],
    ) -> str:
        """
        Compose the final prompt by combining fragments according to composition_order.
        """
        agent_path = self._get_agent_path(agent_id)
        composed_parts = []

        for step in composition_spec.composition_order:
            source = step["source"]
            step_type = step["type"]

            # === BASE PROMPT (Core Personality) ===
            if source.endswith(".md") and step_type == "base":
                core_prompt = self._load_file(agent_path / source)
                composed_parts.append(f"# === CORE PERSONALITY ===\n\n{core_prompt}")

            # === TOOLS (GAD-003 Phase 2) ===
            elif step_type == "tools":
                if composition_spec.tools:
                    tools_section = self._compose_tools_section(
                        source=source, available_tools=composition_spec.tools, agent_path=agent_path
                    )
                    composed_parts.append(f"# === AVAILABLE TOOLS ===\n\n{tools_section}")

            # === KNOWLEDGE FILES ===
            elif source == "${knowledge_files}" and step_type == "knowledge":
                if knowledge_files:
                    knowledge_section = "\n\n---\n\n".join(knowledge_files)
                    composed_parts.append(f"# === KNOWLEDGE BASE ===\n\n{knowledge_section}")

            # === TASK PROMPT ===
            elif source == "${task_prompt}" and step_type == "task":
                # Try with task_ prefix first, fall back to bare task_id
                task_file = agent_path / "tasks" / f"task_{task_id}.md"
                if not task_file.exists():
                    task_file = agent_path / "tasks" / f"{task_id}.md"
                task_prompt = self._load_file(task_file)
                composed_parts.append(f"# === TASK INSTRUCTIONS ===\n\n{task_prompt}")

            # === VALIDATION GATES ===
            elif source == "${gate_prompts}" and step_type == "validation":
                if task_meta.validation_gates:
                    gate_sections = []
                    for gate_id in task_meta.validation_gates:
                        gate_file = gate_id if gate_id.endswith(".md") else f"{gate_id}.md"
                        gate_prompt = self._load_file(agent_path / "gates" / gate_file)
                        gate_sections.append(gate_prompt)

                    gates_combined = "\n\n---\n\n".join(gate_sections)
                    composed_parts.append(f"# === VALIDATION GATES ===\n\n{gates_combined}")

            # === RUNTIME CONTEXT ===
            elif source == "${runtime_context}" and step_type == "context":
                context_str = self._format_runtime_context(runtime_context)
                composed_parts.append(f"# === RUNTIME CONTEXT ===\n\n{context_str}")

        # Combine all parts with separators
        final_prompt = "\n\n" + "=" * 60 + "\n\n".join(composed_parts)

        return final_prompt

    def _format_runtime_context(self, context: dict[str, Any]) -> str:
        """Format runtime context as markdown"""
        lines = ["**Runtime Context:**\n"]
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"- **{key}:**")
                for k, v in value.items():
                    lines.append(f"  - {k}: `{v}`")
            else:
                lines.append(f"- **{key}:** `{value}`")

        return "\n".join(lines)

    def _get_agent_path(self, agent_id: str) -> Path:
        """
        Get the path to an agent's directory

        Args:
            agent_id: Agent identifier

        Returns:
            Path to agent directory

        Raises:
            AgentNotFoundError: If agent_id not in registry
        """
        # Dynamic agent registry - supports all agents
        # NOTE: Legacy agency_os agents commented out - they no longer exist in the new architecture
        AGENT_REGISTRY = {
            # System Steward Framework (Active)
            "SSF_ROUTER": "system_steward_framework/agents/SSF_ROUTER",
            "AUDITOR": "system_steward_framework/agents/AUDITOR",
            "LEAD_ARCHITECT": "system_steward_framework/agents/LEAD_ARCHITECT",
            # Legacy agents (commented out - paths no longer exist):
            # "LEAN_CANVAS_VALIDATOR": "agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR",
            # "VIBE_ALIGNER": "agency_os/01_planning_framework/agents/VIBE_ALIGNER",
            # "GENESIS_BLUEPRINT": "agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT",
            # "GENESIS_UPDATE": "agency_os/01_planning_framework/agents/GENESIS_UPDATE",
            # "MARKET_RESEARCHER": "agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER",
            # "TECH_RESEARCHER": "agency_os/01_planning_framework/agents/research/TECH_RESEARCHER",
            # "FACT_VALIDATOR": "agency_os/01_planning_framework/agents/research/FACT_VALIDATOR",
            # "CODE_GENERATOR": "agency_os/02_code_gen_framework/agents/CODE_GENERATOR",
            # "QA_VALIDATOR": "agency_os/03_qa_framework/agents/QA_VALIDATOR",
            # "DEPLOY_MANAGER": "agency_os/04_deploy_framework/agents/DEPLOY_MANAGER",
            # "BUG_TRIAGE": "agency_os/05_maintenance_framework/agents/BUG_TRIAGE",
            # "AGENCY_OS_ORCHESTRATOR": "agency_os/core_system/agents/AGENCY_OS_ORCHESTRATOR",
        }

        if agent_id not in AGENT_REGISTRY:
            available = "\n  - ".join(sorted(AGENT_REGISTRY.keys()))
            raise AgentNotFoundError(
                f"Agent not found: '{agent_id}'\n\n"
                f"Available agents:\n  - {available}\n\n"
                f"Fix: Check agent_id spelling or add to AGENT_REGISTRY in prompt_runtime.py"
            )

        agent_path = self.base_path / AGENT_REGISTRY[agent_id]

        # Verify agent directory exists
        if not agent_path.exists():
            raise AgentNotFoundError(
                f"Agent directory not found: {agent_path}\n"
                f"Agent ID: {agent_id}\n"
                f"Expected path: {agent_path}\n"
                f"Fix: Ensure agent directory exists or update AGENT_REGISTRY"
            )

        return agent_path

    def _load_file(self, path: Path) -> str:
        """Load a file's contents"""
        with open(path) as f:
            return f.read()

    def _compose_tools_section(
        self, source: str, available_tools: list[str], agent_path: Path
    ) -> str:
        """
        Compose the tools section of the prompt (GAD-003 Phase 2)

        Args:
            source: Path to tool_definitions.yaml (relative to agent dir)
            available_tools: List of tool names to include
            agent_path: Path to agent directory (for resolving relative paths)

        Returns:
            Formatted markdown string with tool definitions
        """
        # Resolve the tool definitions file path
        # source is like "../../../00_system/orchestrator/tools/tool_definitions.yaml"
        # which is relative to the agent directory
        if Path(source).is_absolute():
            tool_defs_path = Path(source)
        else:
            tool_defs_path = (agent_path / source).resolve()

        # Load tool definitions
        try:
            with open(tool_defs_path) as f:
                all_tools = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Tool definitions file not found: {tool_defs_path}")
            return "*(No tools available - tool_definitions.yaml not found)*"
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in tool definitions: {e}")
            return "*(Tool definitions file has invalid YAML)*"

        # Filter to only requested tools
        tools_dict = all_tools.get("tools", {})
        filtered_tools = {
            name: tool for name, tool in tools_dict.items() if name in available_tools
        }

        if not filtered_tools:
            return "*(No tools available for this agent)*"

        # Format tools as markdown
        lines = []
        lines.append("You have access to the following research tools:\n")

        for tool_name, tool_def in filtered_tools.items():
            lines.append(f"## Tool: `{tool_name}`\n")
            lines.append(f"**Description:** {tool_def.get('description', 'No description')}\n")

            # Parameters
            params = tool_def.get("parameters", {})
            if params:
                lines.append("\n**Parameters:**")
                for param_name, param_spec in params.items():
                    required = " (required)" if param_spec.get("required", False) else " (optional)"
                    param_type = param_spec.get("type", "any")
                    param_desc = param_spec.get("description", "")
                    default = (
                        f", default: `{param_spec['default']}`" if "default" in param_spec else ""
                    )
                    lines.append(
                        f"- `{param_name}` ({param_type}){required}: {param_desc}{default}"
                    )

            # Returns
            returns = tool_def.get("returns", {})
            if returns:
                lines.append(f"\n**Returns:** {returns.get('description', 'No description')}")

            lines.append("\n---\n")

        # Add usage instructions
        lines.append("\n### How to use tools:\n")
        lines.append("To call a tool, use the following XML format in your response:\n")
        lines.append("```xml")
        lines.append('<tool_use name="tool_name">')
        lines.append("  <parameters>")
        lines.append("    <param_name>value</param_name>")
        lines.append("  </parameters>")
        lines.append("</tool_use>")
        lines.append("```\n")
        lines.append("You will receive the tool result, then you can continue your analysis.\n")

        return "\n".join(lines)


# =================================================================
# CLI Interface (for testing)
# =================================================================

if __name__ == "__main__":
    # Example usage
    runtime = PromptRuntime()

    context = {
        "project_id": "test_project_001",
        "current_phase": "PLANNING",
        "artifacts": {"feature_spec": "workspaces/test/artifacts/planning/feature_spec.json"},
        "workspace_path": "workspaces/test/",
    }

    # Test composition
    # Note: task_id must match the filename (task_01_select_core_modules -> "01_select_core_modules")
    composed_prompt = runtime.execute_task(
        agent_id="GENESIS_BLUEPRINT",
        task_id="01_select_core_modules",  # Matches task_01_select_core_modules.md
        context=context,
    )

    # Output to file for inspection
    output_file = Path("/home/user/vibe-agency/COMPOSED_PROMPT_EXAMPLE.md")
    with open(output_file, "w") as f:
        f.write(composed_prompt)

    print(f"✓ Composed prompt written to: {output_file}")
    print("\nFirst 500 chars of composed prompt:")
    print("-" * 60)
    print(composed_prompt[:500] + "...")
