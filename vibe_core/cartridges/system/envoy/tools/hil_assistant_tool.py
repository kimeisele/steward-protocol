#!/usr/bin/env python3
"""
HIL Assistant Tool - Verbal Abstraction Daemon (VAD) Layer (Tool Protocol)

This tool implements the "Soft Interface" for the Human-In-The-Loop (HIL).
It filters the complexity of the VibeOS kernel and Agent City, presenting
only the "Next Best Action" and strategic summaries.

Architecture:
- GAD-000 (Operator Inversion): Hides kernel details.
- GAD-800 (Graceful Degradation): Reduces cognitive load.

Tool Protocol compliant for kernel-managed execution.
"""

import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HIL_ASSISTANT")


class HILAssistantTool(Tool):
    """
    The Verbal Abstraction Daemon (VAD) for the HIL.

    Transforms complex system states into simple, strategic directives.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        super().__init__(services)
        logger.info("🧠 HIL Assistant (VAD Layer) initialized")

    @property
    def name(self) -> str:
        return "envoy.hil"

    @property
    def description(self) -> str:
        return "HIL Assistant - transform complex reports into strategic directives"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'get_next_action'",
            },
            "full_report": {
                "type": "string",
                "required": True,
                "description": "The full report to analyze",
            },
            "context": {
                "type": "dict",
                "required": False,
                "description": "Optional context dictionary",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if "full_report" not in parameters:
            raise ValueError("Missing required parameter: full_report")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute HIL assistance."""
        try:
            action = parameters["action"]
            full_report = parameters["full_report"]
            context = parameters.get("context")

            if action == "get_next_action":
                summary = self.get_next_action_summary(full_report, context)
                return ToolResult(
                    success=True,
                    output={"summary": summary},
                    metadata={"action": "get_next_action"},
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}",
                )

        except Exception as e:
            error_msg = f"HIL Assistant failed: {type(e).__name__}: {e!s}"
            logger.error(f"HILAssistantTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)
        """
        Analyze a full report and extract the Next Best Action.

        Args:
            full_report: The raw, complex report (e.g., G.A.P. Report markdown).
            context: Optional additional context (e.g., current system state).

        Returns:
            str: A concise, strategic summary for the HIL.
        """
        logger.info("🔍 Analyzing report for strategic insights...")

        # 1. Analyze Report Type & Status
        is_gap_report = "Governability Audit Proof" in full_report
        is_success = "✅" in full_report or "SUCCESS" in full_report
        is_failure = "❌" in full_report or "FAILED" in full_report

        # 2. Extract Key Information (Regex/Parsing)
        campaign_id = self._extract_campaign_id(full_report)
        crisis_detected = "Crisis Detection" in full_report
        correction_executed = "Self-Correction" in full_report

        # 3. Formulate Strategic Advice
        summary = []

        summary.append("**🤖 HIL ASSISTANT: STRATEGIC BRIEFING**")
        summary.append("---")

        if is_gap_report:
            if is_success:
                summary.append("✅ **SYSTEM STATUS: OPTIMAL**")
                summary.append(
                    "The mission was executed successfully. Governance constraints were enforced and self-corrected."
                )

                if crisis_detected and correction_executed:
                    summary.append(
                        "🛡️  **Governance Proof:** The system successfully handled a license crisis via PROP-009."
                    )

                if campaign_id:
                    summary.append(f"🚀 **Value Created:** Campaign `{campaign_id}` is live and compliant.")

                summary.append("\n👉 **NEXT BEST ACTION:**")
                summary.append("   **Review the G.A.P. Report proof and authorize deployment to production channels.**")
                summary.append("   *(No further intervention required for this mission)*")

            elif is_failure:
                summary.append("⚠️ **SYSTEM STATUS: ATTENTION REQUIRED**")
                summary.append("The mission encountered an error that could not be self-corrected.")
                summary.append("\n👉 **NEXT BEST ACTION:**")
                summary.append("   **Inspect the error logs in the report and provide manual guidance.**")

        else:
            # Generic Report Handling
            summary.append("ℹ️ **SYSTEM UPDATE**")
            summary.append("A new report is available.")
            summary.append("\n👉 **NEXT BEST ACTION:**")
            summary.append("   **Read the report summary.**")

        return "\n".join(summary)

    def _extract_campaign_id(self, text: str) -> Optional[str]:
        """Extract campaign ID from text."""
        match = re.search(r"CAMP-\d+", text)
        return match.group(0) if match else None


if __name__ == "__main__":
    # Test the tool
    tool = HILAssistantTool()
    sample_report = """
    # Mission Cost-Efficient Scaling Proof
    **Type:** Governability Audit Proof

    ## Crisis Detection
    System detected governance constraint violation...

    ## Self-Correction
    System executed PROP-009...

    ## Value Creation
    Campaign CAMP-123456 executed successfully...

    ✅ Campaign completed successfully
    """
    print(tool.get_next_action_summary(sample_report))


__all__ = ["HILAssistantTool"]
