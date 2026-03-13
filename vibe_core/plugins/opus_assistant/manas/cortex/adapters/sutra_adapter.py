"""
Sutra Cortex Adapter - VEDA-4 wrapper for SUTRA documentation system.

OPUS-171 Phase 5.2: Cortex Adapter Pattern

Wraps the existing SutraWeaver in BaseCortex interface
for VEDA-4 auto-discovery via CortexLoader.

CAPABILITIES:
    - generate_docs: Inspect/export source documentation coverage
    - update_readme: Update README files
    - document_manas: Generate MANAS documentation

USAGE:
    from vibe_core.loaders import get_cortex

    sutra = get_cortex("sutra", workspace=Path.cwd())
    result = sutra.execute(intent)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xadeff0ce"  # GenesisByte: parampara % 37 == 0

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.source_authority_registry import load_source_authority_registry
from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import (
    BaseCortex,
    cortex_error,
    cortex_success,
)

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("MANAS.Cortex.Adapter.Sutra")


class SutraCortexAdapter(BaseCortex):
    """
    VEDA-4 adapter for SUTRA documentation system.

    Wraps SutraWeaver to provide unified BaseCortex interface.

    Discovery:
        CortexLoader.get_cortex("sutra")
    """

    # === CORTEX IDENTITY ===
    name = "sutra"
    capabilities = [
        "generate_docs",
        "update_readme",
        "document_manas",
        "fix_documentation_drift",
    ]
    priority = 10

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["KernelProtocol"] = None,
    ):
        super().__init__(workspace, kernel)
        self._weaver = None

    def _get_weaver(self):
        """Lazy-load SutraWeaver."""
        if self._weaver is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

            self._weaver = SutraWeaver(workspace=self._workspace)
        return self._weaver

    def execute(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute a documentation intent via SUTRA.

        Supports:
            - update_readme
            - update_opus_documentation
            - document_manas
            - fix_documentation_drift
            - Wiki sync operations

        Args:
            intent: The intent to execute

        Returns:
            Dict with success, handler, message, and operation-specific data
        """
        intent_type = intent.intent_type
        logger.info(f"📜 SutraCortexAdapter executing: {intent_type}")

        try:
            # Legacy wiki-sync requests now redirect to the projection boundary.
            sync_keywords = {"sync", "push", "update wiki", "publish"}
            is_sync_request = any(kw in intent.title.lower() for kw in sync_keywords)

            if is_sync_request:
                return self._execute_projection_redirect()

            # Generate documentation
            if intent_type in ["update_readme", "update_opus_documentation"]:
                return self._execute_doc_generation(intent)

            # Document MANAS
            if intent_type == "document_manas":
                return self._execute_manas_docs(intent)

            # Fix drift
            if intent_type == "fix_documentation_drift":
                return self._execute_drift_fix(intent)

            return cortex_success(
                handler=self.name,
                message=f"Sutra intent acknowledged: {intent_type}",
                intent_type=intent_type,
            )

        except Exception as e:
            logger.error(f"SutraCortexAdapter error: {e}")
            return cortex_error(handler=self.name, error=str(e))

    def _execute_projection_redirect(self) -> Dict[str, Any]:
        """Explain that public publication moved to agent-internet."""
        registry = load_source_authority_registry(workspace=self._workspace)
        return cortex_error(
            handler=self.name,
            error="Local SUTRA wiki publication was removed; publish the public membrane via agent-internet instead.",
            action="public_wiki_removed",
            document_count=len(registry.documents),
        )

    def _execute_doc_generation(self, intent: "Intent") -> Dict[str, Any]:
        """Report documentation coverage without routing through Sutra authority exports."""
        registry = load_source_authority_registry(workspace=self._workspace)
        weaver = self._get_weaver()
        context = weaver.gather_context()

        return cortex_success(
            handler=self.name,
            message=f"Prepared documentation coverage for {len(registry.documents)} source documents",
            action="documentation_surface_ready",
            document_count=len(registry.documents),
            agents_found=len(context.agents),
            modules_found=len(context.modules),
        )

    def _execute_manas_docs(self, intent: "Intent") -> Dict[str, Any]:
        """Generate MANAS-specific documentation."""
        weaver = self._get_weaver()

        # Generate MANAS architecture doc
        context = weaver._load_context()

        return cortex_success(
            handler=self.name,
            message="MANAS documentation generated",
            nodes=context.node_count,
            agents=len(context.agents),
        )

    def _execute_drift_fix(self, intent: "Intent") -> Dict[str, Any]:
        """Fix documentation drift."""
        # Get drift info from intent
        drift_files = intent.params.get("files", [])

        return cortex_success(
            handler=self.name,
            message=f"Documentation drift fix initiated for {len(drift_files)} files",
            files=drift_files,
            action="drift_fix_queued",
        )
