"""Documentation Cortex Adapter - neutral wrapper for documentation surface inspection."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import BaseCortex, cortex_error, cortex_success
from vibe_core.source_authority_registry import load_source_authority_registry

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("MANAS.Cortex.Adapter.Documentation")


class DocumentationCortexAdapter(BaseCortex):
    """VEDA-4 adapter for documentation surface inspection."""

    name = "documentation"
    capabilities = ["generate_docs", "update_readme", "document_manas", "fix_documentation_drift"]
    priority = 10

    def __init__(self, workspace: Optional[Path] = None, kernel: Optional["KernelProtocol"] = None):
        super().__init__(workspace, kernel)
        self._builder = None

    def _get_builder(self):
        if self._builder is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.documentation_surface import DocumentationSurfaceBuilder

            self._builder = DocumentationSurfaceBuilder(workspace=self._workspace)
        return self._builder

    def execute(self, intent: "Intent") -> Dict[str, Any]:
        intent_type = intent.intent_type
        logger.info("📜 DocumentationCortexAdapter executing: %s", intent_type)
        try:
            sync_keywords = {"sync", "push", "update wiki", "publish"}
            if any(kw in intent.title.lower() for kw in sync_keywords):
                return self._execute_projection_redirect()
            if intent_type in ["update_readme", "update_opus_documentation"]:
                return self._execute_doc_generation()
            if intent_type == "document_manas":
                return self._execute_manas_docs()
            if intent_type == "fix_documentation_drift":
                return self._execute_drift_fix(intent)
            return cortex_success(
                handler=self.name, message=f"Documentation intent acknowledged: {intent_type}", intent_type=intent_type
            )
        except Exception as exc:
            logger.error("DocumentationCortexAdapter error: %s", exc)
            return cortex_error(handler=self.name, error=str(exc))

    def _execute_projection_redirect(self) -> Dict[str, Any]:
        registry = load_source_authority_registry(workspace=self._workspace)
        return cortex_error(
            handler=self.name,
            error="Local wiki publication was removed; publish the public membrane via agent-internet instead.",
            action="public_wiki_removed",
            document_count=len(registry.documents),
        )

    def _execute_doc_generation(self) -> Dict[str, Any]:
        registry = load_source_authority_registry(workspace=self._workspace)
        context = self._get_builder().gather_context()
        return cortex_success(
            handler=self.name,
            message=f"Prepared documentation coverage for {len(registry.documents)} source documents",
            action="documentation_surface_ready",
            document_count=len(registry.documents),
            agents_found=len(context.agents),
            modules_found=len(context.modules),
        )

    def _execute_manas_docs(self) -> Dict[str, Any]:
        context = self._get_builder().gather_context()
        return cortex_success(
            handler=self.name,
            message="MANAS documentation context generated",
            nodes=context.node_count,
            agents=len(context.agents),
        )

    def _execute_drift_fix(self, intent: "Intent") -> Dict[str, Any]:
        drift_files = intent.params.get("files", [])
        return cortex_success(
            handler=self.name,
            message=f"Documentation drift fix initiated for {len(drift_files)} files",
            files=drift_files,
            action="drift_fix_queued",
        )
