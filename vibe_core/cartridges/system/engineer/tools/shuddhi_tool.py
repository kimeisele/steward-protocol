"""
Shuddhi Tool - The Surgical Instrument for the Engineer Agent.

Allows the Engineer to perform structural code healing using the Kernel's Shuddhi service.
This tool bridges the gap between the 'HEAL_CODEBASE' circuit and the Core Shuddhi Engine.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.io_service import DocumentType, KernelIOService
from vibe_core.protocols.shuddhi import ShuddhiService, ShuddhiStatus
from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("SHUDDHI_TOOL")


class ShuddhiHealTool(Tool):
    """
    Exposes the Kernel's Shuddhi service to the Engineer agent.

    Usage:
        steward do "heal violation in file.py rule unsafe_io_write"
    """

    def __init__(self):
        self.io_service: Optional[KernelIOService] = None
        self._kernel = None

    def set_io_service(self, io_service: KernelIOService) -> None:
        """Dependency Injection for Kernel IO Service."""
        self.io_service = io_service

    def set_kernel(self, kernel: Any) -> None:
        """Dependency Injection for Kernel."""
        self._kernel = kernel

    @property
    def name(self) -> str:
        return "engineer.heal_violation"

    @property
    def description(self) -> str:
        return (
            "Performs surgical, structural code healing on a file to fix specific architectural violations. "
            "Use this tool to resolve 'unsafe_io_write' or similar structural issues while preserving comments."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file needing healing"},
                "rule_id": {"type": "string", "description": "The ID of the violation rule (e.g., 'unsafe_io_write')"},
                "violation_type": {"type": "string", "description": "Alternative to rule_id"},
            },
            "required": ["file_path"],
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        if "file_path" not in parameters:
            raise ValueError("Missing file_path")
        if "rule_id" not in parameters and "violation_type" not in parameters:
            raise ValueError("Missing rule_id or violation_type")

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        file_path_str = parameters["file_path"]
        rule_id = parameters.get("rule_id") or parameters.get("violation_type")

        # 1. Access Shuddhi Service via DI
        try:
            shuddhi = ServiceRegistry.require(ShuddhiService)
        except RuntimeError:
            return ToolResult(success=False, error="ShuddhiService not available in ServiceRegistry")

        # 2. Access IO Service (injected)
        if not self.io_service:
            return ToolResult(success=False, error="KernelIOService not injected into ShuddhiHealTool")

        try:
            # 3. Purify
            path = Path(file_path_str)
            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {path}")

            result = shuddhi.purify(path, rule_id)

            # 4. Handle Result
            if result.status == ShuddhiStatus.PURIFIED:
                if not result.purified_code:
                    return ToolResult(success=False, error="Shuddhi reported success but returned no code")

                # 5. Write Back (Karma) via Kernel IO
                try:
                    rel_path = str(path.relative_to(Path.cwd()))
                except ValueError:
                    rel_path = str(path)

                write_result = self.io_service.write_document(
                    name=rel_path,
                    content=result.purified_code,
                    doc_type=DocumentType.READONLY,
                    writer_id="ENGINEER_SHUDDHI",
                    add_header=False,
                )

                if write_result.success:
                    # 6. LOG AS TASK (Holistic Loop)
                    # We try to use the kernel instance if injected, or fallback to DI
                    try:
                        task_service = None
                        if self._kernel and hasattr(self._kernel, "tasks"):
                            task_service = self._kernel.tasks
                        else:
                            from vibe_core.protocols.task import TaskService

                            task_service = ServiceRegistry.get(TaskService)

                        if task_service:
                            task_service.add_task(
                                title=f"HEALED: {rel_path}",
                                description=f"Violation {rule_id} fixed via Shuddhi.",
                                priority=50,
                                assigned_agent="engineer",
                            )
                    except Exception as e:
                        logger.warning(f"Could not record task: {e}")

                    return ToolResult(
                        success=True, output=f"Successfully healed {file_path_str} (Rule: {rule_id}).\nDiff applied."
                    )
                else:
                    return ToolResult(success=False, error=f"Write failed: {write_result.error}")

            elif result.status == ShuddhiStatus.SKIPPED:
                return ToolResult(success=True, output="Skipped: No violation found.")
            else:
                return ToolResult(success=False, error=f"Shuddhi Failed: {result.message}")

        except Exception as e:
            return ToolResult(success=False, error=f"Internal Shuddhi Error: {str(e)}")
