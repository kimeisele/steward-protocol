#!/usr/bin/env python3
"""
SCRIBE RAG Renderer - Generate RAG.md (Realtime Architecture Guide)

RAG = Realtime Architecture Guide (NOT Retrieval Augmented Generation!)

This renderer works WITH the ANALYST agent:
- ANALYST provides the 4D multi-dimensional context
- SCRIBE renders the context to RAG.md

NO analysis duplication - ANALYST is the single source of truth.

Tool Protocol Compliant (Kernel-Managed).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Import from shared base
from .base import (
    Tool,
    ToolResult,
    get_kernel_status,
    load_template,
)


class RagRenderer(Tool):
    """
    Render RAG.md - Realtime Architecture Guide.

    Uses ANALYST agent for 4D multi-dimensional context.
    """

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)
        self._analyst = None

    @property
    def name(self) -> str:
        return "scribe.rag_renderer"

    @property
    def description(self) -> str:
        return "Generate RAG.md using ANALYST 4D context synthesis"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to render RAG.md with 4D analysis",
            },
            "scope": {
                "type": "string",
                "required": False,
                "description": "Analysis scope: 'short_term', 'mid_term', 'long_term', 'full'",
                "default": "full",
            },
            "depth": {
                "type": "string",
                "required": False,
                "description": "Analysis depth: 'quick', 'standard', 'comprehensive'",
                "default": "comprehensive",
            },
        }

    def _get_analyst(self):
        """Lazy load ANALYST agent."""
        if self._analyst is None:
            try:
                from agent_city.registry.analyst.cartridge_main import AnalystCartridge

                self._analyst = AnalystCartridge()
            except ImportError:
                raise ImportError("ANALYST agent not found. Ensure agent_city.registry.analyst is available.")
        return self._analyst

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate renderer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be 'generate'")

        # Validate optional scope
        scope = parameters.get("scope", "full")
        valid_scopes = ["short_term", "mid_term", "long_term", "full"]
        if scope not in valid_scopes:
            raise ValueError(f"Invalid scope: {scope}. Must be one of {valid_scopes}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute renderer operation."""
        try:
            action = parameters["action"]
            if action == "generate":
                scope = parameters.get("scope", "full")
                depth = parameters.get("depth", "comprehensive")
                content = self._render_with_analyst(scope=scope, depth=depth)
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _render_with_analyst(self, scope: str = "full", depth: str = "comprehensive") -> str:
        """
        Render RAG.md using ANALYST 4D context synthesis.

        This is the proper integration - ANALYST does analysis,
        SCRIBE does rendering. No duplication.
        """
        # Get ANALYST agent
        analyst = self._get_analyst()

        # Get 4D context from ANALYST (via VEDA-4 circuit)
        context = analyst.synthesize_context(scope=scope, depth=depth)

        # Check for errors
        if "error" in context:
            raise RuntimeError(f"ANALYST synthesis failed: {context['error']}")

        # Get kernel status
        kernel_status = get_kernel_status()

        # Timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Load and render template
        template = load_template("rag.jinja2")
        content = template.render(
            timestamp=timestamp,
            generator="SCRIBE (via ANALYST v2.0)",
            kernel_status=kernel_status,
            context=context,
        )

        return content

    def render_quick(self) -> Dict[str, Any]:
        """
        Quick render - just get insights without full RAG.md.

        Useful for status checks.
        """
        analyst = self._get_analyst()
        return analyst.quick_insights()


# Convenience function for direct usage
def generate_rag_md(root_dir: str = ".", scope: str = "full", depth: str = "comprehensive") -> str:
    """
    Generate RAG.md content.

    Args:
        root_dir: Repository root directory
        scope: Analysis scope (short_term, mid_term, long_term, full)
        depth: Analysis depth (quick, standard, comprehensive)

    Returns:
        RAG.md content as string
    """
    renderer = RagRenderer(root_dir)
    result = renderer.execute({"action": "generate", "scope": scope, "depth": depth})

    if result.success:
        return result.output
    else:
        raise RuntimeError(f"RAG.md generation failed: {result.error}")


# Direct testing
if __name__ == "__main__":
    print("=" * 60)
    print("SCRIBE RAG Renderer - 4D Analysis")
    print("=" * 60)

    renderer = RagRenderer()

    # Quick insights
    print("\n📊 Quick Insights:")
    try:
        insights = renderer.render_quick()
        for key, value in insights.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  Error: {e}")

    # Full render
    print("\n📝 Generating RAG.md...")
    try:
        result = renderer.execute({"action": "generate", "scope": "full"})
        if result.success:
            print(f"  Success! ({len(result.output)} characters)")
            print("\n  Preview (first 500 chars):")
            print(result.output[:500])
        else:
            print(f"  Error: {result.error}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 60)
