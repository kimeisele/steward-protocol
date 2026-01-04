#!/usr/bin/env python3
"""
NAGA Toxicity Scan Tool (Tool Protocol).

Scan content for toxicity using Takshaka's Kaliya Filter.
Tool Protocol compliant for kernel-managed execution.

"Takshaka beißt ohne Warnung" - No mercy for toxic content.
"""

import logging
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("NAGA.TOOL.SCAN")


class ToxicityScanTool(Tool):
    """Toxicity scanning using Takshaka (Tool Protocol)."""

    def __init__(self):
        """Initialize toxicity scanner."""
        self._federation = None

    @property
    def name(self) -> str:
        return "naga.scan"

    @property
    def description(self) -> str:
        return "Scan content for toxicity using Takshaka's Kaliya Filter"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'scan'",
            },
            "content": {
                "type": "string",
                "required": True,
                "description": "Content to scan for toxicity",
            },
            "threshold": {
                "type": "number",
                "required": False,
                "description": "Custom toxicity threshold (0.0-1.0)",
            },
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        if parameters["action"] != "scan":
            raise ValueError("Invalid action. Must be 'scan'")

        if "content" not in parameters:
            raise ValueError("Missing required parameter: content")

        if "threshold" in parameters:
            threshold = parameters["threshold"]
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                raise ValueError("threshold must be a number between 0.0 and 1.0")

    def _get_federation(self):
        """Lazy-load federation from ServiceRegistry."""
        if self._federation is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.naga import NagaOrchestrator

                try:
                    self._federation = ServiceRegistry.get("NagaOrchestrator")
                except Exception:
                    self._federation = ServiceRegistry.get(NagaOrchestrator)
            except Exception as e:
                logger.debug(f"NagaOrchestrator not available: {e}")
                return None
        return self._federation

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute toxicity scan."""
        try:
            content = parameters["content"]
            threshold = parameters.get("threshold")

            federation = self._get_federation()

            if not federation or not federation.takshaka:
                return ToolResult(
                    success=True,
                    output={
                        "toxicity": 0.0,
                        "blocked": False,
                        "patterns": [],
                        "warning": "Takshaka not available - scan skipped",
                    },
                    metadata={"action": "scan", "available": False},
                )

            # Perform toxicity scan
            result = federation.takshaka.scan_toxicity(content)

            # Determine if blocked based on threshold
            effective_threshold = threshold if threshold is not None else 0.3
            blocked = result.score >= effective_threshold if hasattr(result, "score") else result.blocked

            output = {
                "toxicity": result.score if hasattr(result, "score") else 0.0,
                "blocked": blocked,
                "patterns": result.patterns if hasattr(result, "patterns") else [],
                "scanned_length": len(content),
                "threshold_used": effective_threshold,
            }

            # Log if toxic content detected
            if blocked:
                logger.warning(f"Toxic content detected (score={output['toxicity']:.2f})")

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "action": "scan",
                    "blocked": blocked,
                    "toxicity": output["toxicity"],
                },
            )

        except Exception as e:
            error_msg = f"Toxicity scan failed: {type(e).__name__}: {e!s}"
            logger.error(error_msg)
            return ToolResult(success=False, error=error_msg)

    def format_report(self, output: Dict[str, Any]) -> str:
        """Format scan result for human reading."""
        lines = []
        lines.append("=" * 50)
        lines.append("    TAKSHAKA TOXICITY SCAN")
        lines.append("=" * 50)

        toxicity = output.get("toxicity", 0.0)
        blocked = output.get("blocked", False)

        status_emoji = "" if blocked else ""
        status_text = "BLOCKED" if blocked else "CLEAN"

        lines.append(f"\n{status_emoji} Status: {status_text}")
        lines.append(f"   Toxicity Score: {toxicity:.2f}")
        lines.append(f"   Threshold: {output.get('threshold_used', 0.3):.2f}")
        lines.append(f"   Content Length: {output.get('scanned_length', 0)} chars")

        patterns = output.get("patterns", [])
        if patterns:
            lines.append(f"\n   Patterns Matched: {len(patterns)}")
            for p in patterns[:5]:  # Limit to 5
                lines.append(f"     - {p}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


__all__ = ["ToxicityScanTool"]
