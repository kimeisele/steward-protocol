"""
Silpa Cortex Adapter - VEDA-4 wrapper for SILPA code refactoring.

OPUS-171 Phase 5.2: Cortex Adapter Pattern

Wraps the existing SILPA (SilpaArchitect) in BaseCortex interface
for VEDA-4 auto-discovery via CortexLoader.

CAPABILITIES:
    - genesis_code: Generate new code
    - genesis_tests: Generate tests
    - refactor: Safe code refactoring
    - update_docstring: Update docstrings

USAGE:
    from vibe_core.loaders import get_cortex

    silpa = get_cortex("silpa", workspace=Path.cwd())
    result = silpa.execute(intent)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import (
    BaseCortex,
    cortex_error,
    cortex_success,
)

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.Adapter.Silpa")


class SilpaCortexAdapter(BaseCortex):
    """
    VEDA-4 adapter for SILPA code generation/refactoring.

    Wraps SilpaArchitect to provide unified BaseCortex interface.

    Discovery:
        CortexLoader.get_cortex("silpa")
    """

    # === CORTEX IDENTITY ===
    name = "silpa"
    capabilities = [
        "genesis_code",
        "genesis_tests",
        "genesis_module",
        "refactor",
        "update_docstring",
        "rename_function",
    ]
    priority = 10

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["KernelProtocol"] = None,
    ):
        super().__init__(workspace, kernel)
        self._architect = None

    def _get_architect(self):
        """Lazy-load SilpaArchitect."""
        if self._architect is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
                SilpaArchitect,
            )

            self._architect = SilpaArchitect(workspace=self._workspace)
        return self._architect

    def execute(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute a code generation/refactoring intent via SILPA.

        Supports:
            - genesis_tests: Generate test files
            - genesis_*: Code generation intents
            - refactor operations

        Args:
            intent: The intent to execute

        Returns:
            Dict with success, handler, message, and generation results
        """
        intent_type = intent.intent_type
        logger.info(f"🎨 SilpaCortexAdapter executing: {intent_type}")

        try:
            architect = self._get_architect()

            # Test generation
            if intent_type in ["genesis_tests", "create_tests"]:
                return self._execute_genesis_tests(intent, architect)

            # Code generation
            if intent_type.startswith("genesis_"):
                return self._execute_genesis(intent, architect)

            # Refactoring
            if intent_type in ["refactor", "update_docstring", "rename_function"]:
                return self._execute_refactor(intent, architect)

            # Default: acknowledge
            return cortex_success(
                handler=self.name,
                message=f"Silpa intent acknowledged: {intent_type}",
                intent_type=intent_type,
            )

        except Exception as e:
            logger.error(f"SilpaCortexAdapter error: {e}")
            return cortex_error(handler=self.name, error=str(e))

    def _execute_genesis_tests(self, intent: "Intent", architect: Any) -> Dict[str, Any]:
        """Generate tests for a target file."""
        target = intent.params.get("target_file")
        if not target:
            return cortex_error(
                handler=self.name,
                error="No target_file specified for test generation",
            )

        target_path = self._workspace / target

        if not target_path.exists():
            return cortex_error(
                handler=self.name,
                error=f"Target file not found: {target}",
            )

        # Generate test plan
        plan = architect.plan_test_generation(target_path)

        return cortex_success(
            handler=self.name,
            message=f"Test generation planned for {target}",
            target=str(target),
            test_file=plan.test_file if hasattr(plan, "test_file") else None,
            action="plan_created",
        )

    def _execute_genesis(self, intent: "Intent", architect: Any) -> Dict[str, Any]:
        """Execute code generation."""
        # Get generation parameters
        gen_type = intent.intent_type.replace("genesis_", "")
        target = intent.params.get("target")

        return cortex_success(
            handler=self.name,
            message=f"Code generation ({gen_type}) queued",
            generation_type=gen_type,
            target=target,
            action="genesis_queued",
        )

    def _execute_refactor(self, intent: "Intent", architect: Any) -> Dict[str, Any]:
        """Execute refactoring operation."""
        target_file = intent.params.get("target_file")
        refactor_type = intent.params.get("refactor_type", intent.intent_type)

        if not target_file:
            return cortex_error(
                handler=self.name,
                error="No target_file specified for refactoring",
            )

        return cortex_success(
            handler=self.name,
            message=f"Refactoring ({refactor_type}) queued for {target_file}",
            target_file=target_file,
            refactor_type=refactor_type,
            action="refactor_queued",
        )
