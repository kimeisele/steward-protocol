"""
MATRIX Renderer - Routing Patch Bay View.

Displays all discovered circuits and playbooks from existing loaders.
Just a VIEW into what exists - connecting the cables.

Uses CircuitLoader/PlaybookLoader caching - no duplicate work.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("RENDERER_MATRIX")


class MatrixRenderer(BaseRenderer):
    """
    Routing Patch Bay - View into CircuitLoader + PlaybookLoader.

    Shows all discovered routes in the system.
    Loaders handle caching internally.
    """

    def __init__(self, kernel: "KernelProtocol"):
        super().__init__(kernel)

    @property
    def name(self) -> str:
        return "matrix"

    def render(self) -> None:
        """Render MATRIX.md from discovered circuits and playbooks."""
        try:
            circuits = self._gather_circuits()
            playbooks = self._gather_playbooks()

            content = self._build_content(circuits, playbooks)

            self.kernel.io.write_document(
                name="MATRIX.md",
                content=content,
                doc_type=DocumentType.READONLY,
                writer_id="RENDERER_MATRIX",
            )

            logger.debug(f"MATRIX.md rendered ({len(circuits)} circuits, {len(playbooks)} playbooks)")

        except Exception as e:
            logger.error(f"Failed to render MATRIX.md: {e}")

    def _gather_circuits(self) -> List[Dict[str, Any]]:
        """Get all circuits from CircuitLoader (loader handles caching)."""
        try:
            from vibe_core.loaders import CircuitLoader

            registry, _ = CircuitLoader.discover_and_load()
            return self._parse_circuits(registry)
        except Exception as e:
            logger.warning(f"Circuit discovery failed: {e}")
            return []

    def _parse_circuits(self, registry: Dict) -> List[Dict[str, Any]]:
        """Parse circuit registry into display format. No transformation - show what exists."""
        circuits = []
        for circuit_id, meta in registry.items():
            circuits.append(
                {
                    "id": circuit_id,
                    "type": meta.get("type", "circuit"),
                    "domain": meta.get("domain", "-"),
                    "version": meta.get("version", "-"),
                    "status": "ACTIVE",
                }
            )
        return circuits

    def _gather_playbooks(self) -> List[Dict[str, Any]]:
        """Get all playbooks from PlaybookLoader (loader handles caching)."""
        try:
            from vibe_core.loaders import PlaybookLoader

            registry, _ = PlaybookLoader.discover_and_load()
            return self._parse_playbooks(registry)
        except Exception as e:
            logger.warning(f"Playbook discovery failed: {e}")
            return []

    def _parse_playbooks(self, registry: Dict) -> List[Dict[str, Any]]:
        """Parse playbook registry into display format. No transformation - show what exists."""
        playbooks = []
        for playbook_id, meta in registry.items():
            playbooks.append(
                {
                    "id": playbook_id,
                    "type": meta.get("type", "playbook") if isinstance(meta, dict) else "playbook",
                    "domain": meta.get("domain", "-") if isinstance(meta, dict) else "-",
                    "version": meta.get("version", "-") if isinstance(meta, dict) else "-",
                    "status": "ACTIVE",
                }
            )
        return playbooks

    def _build_content(self, circuits: List[Dict], playbooks: List[Dict]) -> str:
        """Build the MATRIX.md content. Simple table - no transformation."""
        lines = [
            "# MATRIX",
            "",
            "> **Routing Patch Bay** - Discovered circuits and playbooks",
            "",
            "## Circuits",
            "",
            "| ID | Type | Domain | Version |",
            "|----|------|--------|---------|",
        ]

        if circuits:
            for c in sorted(circuits, key=lambda x: x["id"]):
                lines.append(f"| {c['id']} | {c['type']} | {c['domain']} | {c['version']} |")
        else:
            lines.append("| *None* | - | - | - |")

        lines.extend(
            [
                "",
                "## Playbooks",
                "",
                "| ID | Type | Domain | Version |",
                "|----|------|--------|---------|",
            ]
        )

        if playbooks:
            for p in sorted(playbooks, key=lambda x: x["id"]):
                lines.append(f"| {p['id']} | {p['type']} | {p['domain']} | {p['version']} |")
        else:
            lines.append("| *None* | - | - | - |")

        lines.extend(
            [
                "",
                "---",
                "",
                f"**Total:** {len(circuits)} circuits, {len(playbooks)} playbooks",
                "",
                f"*Auto-generated · {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            ]
        )

        return "\n".join(lines)
