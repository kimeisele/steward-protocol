#!/usr/bin/env python3
"""
Prompt Registry - High-level interface for governed prompt composition

This is the "heart" of the system - provides automatic governance injection,
context enrichment, and tool/SOP composition.

Usage:
    from vibe_core.runtime import PromptRegistry

    # Compose prompt with full governance
    prompt = PromptRegistry.compose(
        agent="VIBE_ALIGNER",
        task="02_feature_extraction",
        workspace="my-project",
        inject_governance=True,
        inject_tools=["google_search"],
        inject_sops=["SOP_001"]
    )

Architecture:
    Wraps PromptRuntime (low-level composition) and adds:
    - Guardian Directives injection (from SSF)
    - Context enrichment (manifest, workspace paths)
    - Tool definitions injection
    - SOP injection
    - Composition order: Governance → Context → Tools → SOPs → Agent

Created: 2025-11-15
Version: 1.0 (MVP)
"""

import logging
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml

# Import PromptRuntime using proper package path
from vibe_core.runtime.prompt_runtime import PromptRuntime

# Import workspace utilities without sys.path manipulation
_REPO_ROOT = (
    Path(__file__).resolve().parent.parent.parent
)  # vibe_core/runtime/ -> vibe_core/ -> repo root
_WORKSPACE_UTILS_PATH = _REPO_ROOT / "scripts" / "workspace_utils.py"

try:
    if _WORKSPACE_UTILS_PATH.exists():
        spec = spec_from_file_location("workspace_utils", _WORKSPACE_UTILS_PATH)
        if spec and spec.loader:
            workspace_utils = module_from_spec(spec)
            spec.loader.exec_module(workspace_utils)
            get_active_workspace = workspace_utils.get_active_workspace
            load_workspace_manifest = workspace_utils.load_workspace_manifest
            resolve_manifest_path = workspace_utils.resolve_manifest_path
            WORKSPACE_UTILS_AVAILABLE = True
        else:
            raise ImportError("Failed to load workspace_utils spec")
    else:
        raise ImportError(f"workspace_utils.py not found at {_WORKSPACE_UTILS_PATH}")
except ImportError as e:
    logging.warning(f"workspace_utils not available: {e}")
    WORKSPACE_UTILS_AVAILABLE = False
    get_active_workspace = None  # type: ignore
    load_workspace_manifest = None  # type: ignore
    resolve_manifest_path = None  # type: ignore


logger = logging.getLogger(__name__)


class PromptRegistryError(Exception):
    """Base exception for PromptRegistry errors"""

    pass


class GovernanceLoadError(PromptRegistryError):
    """Raised when Guardian Directives can't be loaded"""

    pass


class ContextEnrichmentError(PromptRegistryError):
    """Raised when workspace context enrichment fails"""

    pass


class PromptRegistry:
    """
    High-level interface for prompt composition with automatic injections.

    This is a thin wrapper around PromptRuntime that adds governance and
    context enrichment capabilities.
    """

    # Class-level cache for Guardian Directives (loaded once)
    _guardian_directives_cache: str | None = None

    # Class-level prompt storage (key-based lookup)
    _prompts: dict[str, str] = {}

    @classmethod
    def compose(
        cls,
        agent: str,
        task: str | None = None,  # Optional for meta-agents like SSF_ROUTER
        workspace: str | None = None,
        inject_governance: bool = True,
        inject_tools: list[str] | None = None,
        inject_sops: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Compose a governed prompt with all injections.

        Args:
            agent: Agent ID (e.g., "VIBE_ALIGNER")
            task: Task ID (e.g., "02_feature_extraction"). Optional for meta-agents.
            workspace: Workspace name or path. Defaults to active workspace.
            inject_governance: Whether to inject Guardian Directives (default: True)
            inject_tools: List of tool names to inject (e.g., ["google_search"])
            inject_sops: List of SOP IDs to inject (e.g., ["SOP_001"])
            context: Additional runtime context

        Returns:
            Fully composed prompt string ready for LLM execution

        Raises:
            PromptRuntimeError: If base prompt composition fails
            GovernanceLoadError: If Guardian Directives can't be loaded
            ContextEnrichmentError: If workspace context enrichment fails
        """
        logger.info(f"Composing prompt: agent={agent}, task={task}, workspace={workspace}")

        # Initialize context if not provided
        if context is None:
            context = {}

        # Resolve workspace
        if workspace is None and WORKSPACE_UTILS_AVAILABLE:
            workspace = get_active_workspace()
        elif workspace is None:
            workspace = "ROOT"  # Fallback

        context["_registry_workspace"] = workspace

        # 1. Get base prompt from PromptRuntime
        runtime = PromptRuntime()

        # If task is None, create a minimal context-only prompt
        if task is None:
            logger.warning(f"No task specified for agent {agent} - creating meta-agent prompt")
            base_prompt = cls._create_meta_agent_prompt(agent)
        else:
            base_prompt = runtime.execute_task(agent, task, context)

        # 2. Build injection layers (in order)
        layers = []

        # Layer 1: Governance (if requested)
        if inject_governance:
            try:
                governance_section = cls._load_guardian_directives()
                layers.append(governance_section)
                logger.debug("Guardian Directives injected")
            except Exception as e:
                logger.error(f"Failed to load Guardian Directives: {e}")
                raise GovernanceLoadError(f"Failed to inject governance: {e}") from e

        # Layer 2: Context (automatic)
        try:
            context_section = cls._enrich_context(workspace, context)
            layers.append(context_section)
            logger.debug("Context enrichment completed")
        except Exception as e:
            logger.error(f"Failed to enrich context: {e}")
            raise ContextEnrichmentError(f"Failed to enrich context: {e}") from e

        # Layer 3: Tools (if requested)
        if inject_tools:
            tools_section = cls._inject_tools(inject_tools)
            layers.append(tools_section)
            logger.debug(f"Tools injected: {inject_tools}")

        # Layer 4: SOPs (if requested)
        if inject_sops:
            sops_section = cls._inject_sops(inject_sops)
            layers.append(sops_section)
            logger.debug(f"SOPs injected: {inject_sops}")

        # 3. Combine layers + base prompt
        # Order: Governance → Context → Tools → SOPs → Agent
        final_prompt = "\n\n".join(layers + [base_prompt])

        prompt_size = len(final_prompt)
        logger.info(f"Prompt composed successfully: {prompt_size:,} chars")

        return final_prompt

    @classmethod
    def register(cls, key: str, prompt: str) -> None:
        """
        Register a prompt by key for simple lookup.

        This is a simpler alternative to compose() for cases where you just
        need to store and retrieve prompts by key.

        Args:
            key: Prompt identifier (e.g., "research.analyze_topic")
            prompt: The prompt template or content
        """
        cls._prompts[key] = prompt
        logger.info(f"Registered prompt: {key} ({len(prompt)} chars)")

    @classmethod
    def get(cls, key: str, context: dict[str, Any] | None = None) -> str:
        """
        Get a prompt by key with optional context interpolation.

        Args:
            key: Prompt identifier (e.g., "research.analyze_topic")
            context: Optional context dict for variable interpolation

        Returns:
            The prompt content (with context interpolated if provided)

        Raises:
            PromptRegistryError: If prompt key not found
        """
        if key not in cls._prompts:
            raise PromptRegistryError(
                f"Prompt key not found: {key}\n"
                f"Available keys: {', '.join(cls._prompts.keys()) if cls._prompts else 'none'}"
            )

        prompt = cls._prompts[key]

        # Simple context interpolation if provided
        if context:
            try:
                # Support both {variable} and {{variable}} formats
                prompt = prompt.format(**context)
            except KeyError as e:
                logger.warning(f"Context interpolation failed for key {key}: missing {e}")
                # Return prompt as-is if interpolation fails

        return prompt

    @classmethod
    def _load_guardian_directives(cls) -> str:
        """
        Load Guardian Directives from SSF knowledge base (with caching).

        Returns:
            Formatted markdown section with Guardian Directives
        """
        # Return cached version if available
        if cls._guardian_directives_cache is not None:
            return cls._guardian_directives_cache

        # Load from file
        directives_path = (
            _REPO_ROOT / "system_steward_framework" / "knowledge" / "guardian_directives.yaml"
        )

        if not directives_path.exists():
            raise GovernanceLoadError(
                f"Guardian Directives not found: {directives_path}\n"
                f"Expected location: system_steward_framework/knowledge/guardian_directives.yaml\n"
                f"Fix: Create Guardian Directives file or disable governance injection"
            )

        try:
            with open(directives_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise GovernanceLoadError(f"Invalid YAML in Guardian Directives: {e}") from e

        # Use injection template from YAML
        template = data.get("injection_template", "")
        if not template:
            raise GovernanceLoadError("Guardian Directives YAML missing 'injection_template' field")

        # Cache for future calls
        cls._guardian_directives_cache = template.strip()

        return cls._guardian_directives_cache

    @classmethod
    def _enrich_context(cls, workspace: str, context: dict[str, Any]) -> str:
        """
        Enrich context with workspace manifest and runtime state.

        Args:
            workspace: Workspace name
            context: Runtime context dict

        Returns:
            Formatted markdown section with enriched context
        """
        lines = ["# === RUNTIME CONTEXT ===\n"]

        # Add workspace info
        lines.append(f"**Active Workspace:** `{workspace}`\n")

        # Load manifest if workspace utils available
        manifest_data = None
        if WORKSPACE_UTILS_AVAILABLE:
            try:
                manifest_path = resolve_manifest_path(workspace)
                if manifest_path.exists():
                    manifest_data = load_workspace_manifest(workspace)
                    lines.append(f"**Manifest Path:** `{manifest_path}`\n")
            except Exception as e:
                logger.warning(f"Could not load manifest for workspace {workspace}: {e}")
                lines.append(f"**Manifest:** *(not available - {e})*\n")
        else:
            lines.append("**Manifest:** *(workspace_utils not available)*\n")

        # Add manifest state (if loaded)
        if manifest_data:
            lines.append("\n**Project State:**")
            lines.append(f"- Project ID: `{manifest_data.get('project_id', 'unknown')}`")
            lines.append(f"- Current Phase: `{manifest_data.get('current_phase', 'unknown')}`")

            # Artifacts summary
            artifacts = manifest_data.get("artifacts", {})
            if artifacts:
                lines.append(f"- Artifacts: {len(artifacts)} available")
                for key in list(artifacts.keys())[:5]:  # Show first 5
                    lines.append(f"  - `{key}`")
                if len(artifacts) > 5:
                    lines.append(f"  - ... and {len(artifacts) - 5} more")

            # Budget tracking
            budget_used = manifest_data.get("budget_tracking", {}).get("total_tokens_used", 0)
            if budget_used:
                lines.append(f"- Budget Used: {budget_used:,} tokens")

        # Add additional context (from caller)
        if context and len(context) > 1:  # More than just _registry_workspace
            lines.append("\n**Additional Context:**")
            for key, value in context.items():
                if not key.startswith("_"):  # Skip internal keys
                    if isinstance(value, dict):
                        lines.append(f"- **{key}:**")
                        for k, v in list(value.items())[:3]:  # Limit nested items
                            lines.append(f"  - {k}: `{v}`")
                    else:
                        lines.append(f"- **{key}:** `{value}`")

        return "\n".join(lines)

    @classmethod
    def _inject_tools(cls, tool_names: list[str]) -> str:
        """
        Inject tool definitions.

        Args:
            tool_names: List of tool names to inject

        Returns:
            Formatted markdown section with tool definitions
        """
        # Load tool definitions
        # Note: Tool definitions location varies based on migration phase
        # Try multiple locations for backwards compatibility
        tool_defs_candidates = [
            _REPO_ROOT / "apps" / "agency" / "orchestrator" / "tools" / "tool_definitions.yaml",
            _REPO_ROOT / "vibe_core" / "orchestrator" / "tools" / "tool_definitions.yaml",
            _REPO_ROOT
            / "agency_os"
            / "core_system"
            / "orchestrator"
            / "tools"
            / "tool_definitions.yaml",  # Legacy
        ]
        tool_defs_path = None
        for candidate in tool_defs_candidates:
            if candidate.exists():
                tool_defs_path = candidate
                break

        if tool_defs_path is None:
            tool_defs_path = tool_defs_candidates[0]  # Use first as default for error message

        if not tool_defs_path.exists():
            logger.warning(f"Tool definitions not found: {tool_defs_path}")
            return "# === TOOLS ===\n\n*(Tool definitions file not found)*"

        try:
            with open(tool_defs_path) as f:
                all_tools = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in tool definitions: {e}")
            return "# === TOOLS ===\n\n*(Invalid tool definitions YAML)*"

        # Filter to requested tools
        tools_dict = all_tools.get("tools", {})
        filtered_tools = {name: tool for name, tool in tools_dict.items() if name in tool_names}

        if not filtered_tools:
            return "# === TOOLS ===\n\n*(No matching tools found)*"

        # Format as markdown (reuse PromptRuntime's formatting logic)
        lines = ["# === TOOLS ===\n"]
        lines.append("You have access to the following tools:\n")

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

            lines.append("\n---\n")

        return "\n".join(lines)

    @classmethod
    def _inject_sops(cls, sop_ids: list[str]) -> str:
        """
        Inject Standard Operating Procedures.

        Args:
            sop_ids: List of SOP IDs (e.g., ["SOP_001", "SOP_005"])

        Returns:
            Formatted markdown section with SOP content
        """
        sops_dir = _REPO_ROOT / "system_steward_framework" / "knowledge" / "sops"

        if not sops_dir.exists():
            logger.warning(f"SOPs directory not found: {sops_dir}")
            return "# === STANDARD OPERATING PROCEDURES ===\n\n*(SOPs directory not found)*"

        lines = ["# === STANDARD OPERATING PROCEDURES ===\n"]

        for sop_id in sop_ids:
            # Try to find SOP file with pattern SOP_XXX_*.md
            sop_files = list(sops_dir.glob(f"{sop_id}_*.md"))

            if not sop_files:
                # Fall back to exact match
                sop_file = sops_dir / f"{sop_id}.md"
                if sop_file.exists():
                    sop_files = [sop_file]

            if sop_files:
                sop_file = sop_files[0]  # Use first match
                try:
                    with open(sop_file) as f:
                        sop_content = f.read()
                    lines.append(f"\n## {sop_id}\n")
                    lines.append(sop_content)
                    lines.append("\n---\n")
                except Exception as e:
                    logger.error(f"Failed to load SOP {sop_id}: {e}")
                    lines.append(f"\n## {sop_id}\n")
                    lines.append(f"*(Error loading SOP: {e})*\n")
            else:
                logger.warning(f"SOP file not found for ID: {sop_id}")
                lines.append(f"\n## {sop_id}\n")
                lines.append(f"*(SOP file not found in {sops_dir})*\n")

        return "\n".join(lines)

    @classmethod
    def _create_meta_agent_prompt(cls, agent: str) -> str:
        """
        Create a minimal prompt for meta-agents (agents with no tasks).

        Args:
            agent: Agent ID

        Returns:
            Minimal base prompt
        """
        return f"""# === AGENT: {agent} ===

This is a meta-agent session (no specific task).
Context and governance will be injected via Prompt Registry.

Await further instructions.
"""

    @classmethod
    def initialize_defaults(cls) -> None:
        """
        Initialize registry with default prompts.

        This is called automatically on first use, but can be called
        manually to reset prompts or during testing.
        """
        # Research prompts
        cls.register(
            "research.analyze_topic",
            """# RESEARCH ANALYST - FIRST PRINCIPLES MODE

**MISSION:** Analyze the research request with surgical precision, extracting the true intent and scope.

## SYSTEM CONTEXT (GAD-909: Dynamic Injection)

**Current Time:** {system_time}
**Git Branch:** {current_branch}
**Git Status:**
```
{git_status}
```

This context provides temporal and version control awareness for your analysis.

## ANALYSIS FRAMEWORK

You are conducting a First Principles analysis of a research request. Your goal is to deconstruct the request into its fundamental components and identify what the requestor truly needs to learn.

### Step 1: Parse the Intent
- What is the core question being asked?
- What problem is the requestor trying to solve?
- What decision or action will this research inform?

### Step 2: Extract Key Concepts
- Identify the primary concepts, domains, and disciplines involved
- Map relationships between concepts (dependencies, hierarchies, contrasts)
- Note any implicit assumptions or constraints

### Step 3: Define Scope
- What is IN scope (must be covered)?
- What is OUT of scope (explicitly excluded)?
- What are the boundaries (time, domain, depth)?

### Step 4: Identify Search Parameters
- What keywords and phrases will yield relevant results?
- What sources should be prioritized (academic, industry, technical docs)?
- What time period is relevant (recent developments vs historical context)?

## DELIVERABLE

Provide a structured analysis containing:
1. **Core Intent:** (1-2 sentences summarizing the true need)
2. **Key Concepts:** (Bulleted list with brief explanations)
3. **Scope Definition:** (IN/OUT boundaries clearly marked)
4. **Search Strategy:** (Keywords, sources, filters)

Think like a research librarian meeting with a professor - your job is to clarify what they really need before you start gathering sources.

---
**Research Topic:** {context}
""",
        )

        cls.register(
            "research.search_knowledge",
            """# RESEARCH GATHERER - KNOWLEDGE SYNTHESIS MODE

**MISSION:** Search and gather authoritative knowledge sources on the topic.

## SEARCH PROTOCOL

You are conducting comprehensive research using available knowledge sources. Your goal is to find authoritative, relevant information that addresses the core research question.

### Search Strategy
1. **Breadth First:** Cast a wide net to identify major themes and perspectives
2. **Depth Second:** Dive deep into the most promising areas
3. **Authority Always:** Prioritize credible, authoritative sources

### Source Evaluation Criteria
- **Authority:** Is the source credible and expert in this domain?
- **Recency:** Is the information current (or appropriately historical)?
- **Relevance:** Does it directly address the research question?
- **Quality:** Is it well-researched, cited, and rigorous?

### Organization
As you gather sources, organize findings by:
- **Theme:** Group related concepts together
- **Priority:** Rank by relevance to core question
- **Source Type:** Distinguish academic, industry, technical, opinion

## DELIVERABLE

Provide:
1. **Source Inventory:** List of sources found (title, link, type, authority)
2. **Thematic Organization:** Sources grouped by theme
3. **Key Findings Preview:** 1-2 sentence summary per source
4. **Gaps Identified:** What's missing or needs deeper investigation?

Think like a detective gathering evidence - you're building a case for understanding the topic.

---
**Research Topic:** {context}
""",
        )

        cls.register(
            "research.synthesize_report",
            """# RESEARCH SYNTHESIZER - INSIGHT GENERATION MODE

**MISSION:** Transform gathered knowledge into a coherent, actionable report.

## SYNTHESIS FRAMEWORK

You have gathered sources and findings. Now synthesize them into a professional research report that delivers value to the requestor.

### Structure
1. **Executive Summary:** (3-5 sentences: what you found, why it matters)
2. **Background:** (Context and definitions needed to understand the topic)
3. **Key Findings:** (Organized by theme, with evidence and citations)
4. **Patterns & Trends:** (Cross-cutting insights, emerging themes)
5. **Gaps & Limitations:** (What we don't know, what needs more research)
6. **Actionable Insights:** (So what? What should the reader do with this?)

### Quality Standards
- **Clarity:** Write for intelligent non-experts (explain jargon)
- **Evidence:** Support claims with specific sources and data
- **Balance:** Present multiple perspectives where they exist
- **Honesty:** Acknowledge uncertainty and limitations

### Tone
- Professional but accessible
- Confident but not dogmatic
- Insight-driven, not just summarizing

## DELIVERABLE

A structured report in markdown format containing all sections above, with proper citations and clear recommendations.

Think like a consultant delivering findings to a client - they need to understand it AND know what to do with it.

---
**Research Topic:** {context}
**Sources Gathered:** [will be provided from previous step]
""",
        )

        logger.info("✅ Initialized default prompts in registry")


# Initialize defaults on module load
PromptRegistry.initialize_defaults()


# =================================================================
# CLI Interface (for testing)
# =================================================================

if __name__ == "__main__":
    # Example usage
    context = {"test_mode": True, "example_key": "example_value"}

    # Test composition with all injections
    composed_prompt = PromptRegistry.compose(
        agent="VIBE_ALIGNER",
        task="02_feature_extraction",
        workspace="ROOT",
        inject_governance=True,
        inject_tools=["google_search"],
        inject_sops=["SOP_001"],
        context=context,
    )

    # Output to file for inspection
    # ARCH-063: Use project root instead of hardcoded path
    repo_root = Path(__file__).resolve().parent.parent.parent
    output_file = repo_root / "COMPOSED_PROMPT_REGISTRY_TEST.md"
    with open(output_file, "w") as f:
        f.write(composed_prompt)

    print(f"✓ Composed prompt written to: {output_file}")
    print(f"\nPrompt size: {len(composed_prompt):,} chars")
    print("\nFirst 1000 chars:")
    print("-" * 60)
    print(composed_prompt[:1000] + "...")
