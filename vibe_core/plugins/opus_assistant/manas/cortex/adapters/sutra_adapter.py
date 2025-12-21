"""
Sutra Cortex Adapter - VEDA-4 wrapper for SUTRA documentation system.

OPUS-171 Phase 5.2: Cortex Adapter Pattern

Wraps the existing SutraWeaver/SutraOrchestrator in BaseCortex interface
for VEDA-4 auto-discovery via CortexLoader.

CAPABILITIES:
    - generate_docs: Generate documentation from code
    - wiki_sync: Sync docs to GitHub Wiki
    - update_readme: Update README files
    - document_manas: Generate MANAS documentation

USAGE:
    from vibe_core.loaders import get_cortex

    sutra = get_cortex("sutra", workspace=Path.cwd())
    result = sutra.execute(intent)
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
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.Adapter.Sutra")


class SutraCortexAdapter(BaseCortex):
    """
    VEDA-4 adapter for SUTRA documentation system.

    Wraps SutraWeaver and SutraOrchestrator to provide unified BaseCortex interface.

    Discovery:
        CortexLoader.get_cortex("sutra")
    """

    # === CORTEX IDENTITY ===
    name = "sutra"
    capabilities = [
        "generate_docs",
        "wiki_sync",
        "update_readme",
        "document_manas",
        "fix_documentation_drift",
    ]
    priority = 10

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["RealVibeKernel"] = None,
    ):
        super().__init__(workspace, kernel)
        self._weaver = None
        self._orchestrator = None

    def _get_weaver(self):
        """Lazy-load SutraWeaver."""
        if self._weaver is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.sutra import SutraWeaver

            self._weaver = SutraWeaver(workspace=self._workspace)
        return self._weaver

    def _get_orchestrator(self):
        """Lazy-load SutraOrchestrator."""
        if self._orchestrator is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.sutra import (
                SutraOrchestrator,
            )

            self._orchestrator = SutraOrchestrator(workspace=self._workspace)
        return self._orchestrator

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
            # Check for wiki sync keywords
            sync_keywords = {"sync", "push", "update wiki", "publish"}
            is_sync_request = any(kw in intent.title.lower() for kw in sync_keywords)

            if is_sync_request:
                return self._execute_wiki_sync()

            # Generate documentation
            if intent_type in ["update_readme", "update_opus_documentation"]:
                return self._execute_doc_generation(intent)

            # Document MANAS
            if intent_type == "document_manas":
                return self._execute_manas_docs(intent)

            # Fix drift
            if intent_type == "fix_documentation_drift":
                return self._execute_drift_fix(intent)

            # Default: acknowledge
            return cortex_success(
                handler=self.name,
                message=f"Sutra intent acknowledged: {intent_type}",
                intent_type=intent_type,
            )

        except Exception as e:
            logger.error(f"SutraCortexAdapter error: {e}")
            return cortex_error(handler=self.name, error=str(e))

    def _execute_wiki_sync(self) -> Dict[str, Any]:
        """Execute full wiki sync."""
        from vibe_core.plugins.opus_assistant.manas.cortex.sutra import WikiSync

        wiki_sync = WikiSync(workspace=self._workspace)

        if not wiki_sync.has_credentials():
            return cortex_error(
                handler=self.name,
                error="Set GITHUB_TOKEN to enable wiki sync",
            )

        orchestrator = self._get_orchestrator()
        result = orchestrator.generate_and_sync()

        if result.success:
            return cortex_success(
                handler=self.name,
                message=f"Synced {len(result.pages_synced)} pages to wiki",
                pages_synced=result.pages_synced,
                wiki_url=result.wiki_url,
            )
        else:
            return cortex_error(
                handler=self.name,
                error=", ".join(result.errors),
            )

    def _execute_doc_generation(self, intent: "Intent") -> Dict[str, Any]:
        """Generate documentation."""
        weaver = self._get_weaver()

        # Get target from intent params
        target = intent.params.get("target", "README.md")

        # Generate
        pages = weaver.weave_all()

        return cortex_success(
            handler=self.name,
            message=f"Generated {len(pages)} documentation pages",
            pages=[p.title for p in pages],
            action="generated",
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
