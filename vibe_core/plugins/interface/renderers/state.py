"""
STATE.md Renderer - Prakriti State Inspector

OPUS-014: X-ray into the 3-layer state system.
OPUS-151: This file IS the state truth, not a reflection of it.

The Operator (human or AI) exists IN this reality.
STATE.md doesn't "show" state - it IS state made visible.

Architecture Pattern:
- Uses render_sections() from BaseRenderer (config-driven)
- Registers data sources for each Prakriti layer
- NO hardcoded generate_content() - sections come from interface.yaml
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol


class StateRenderer(BaseRenderer):
    """Manifests the Prakriti state truth.

    Three layers (as per OPUS-009):
    - STHULA (Physical): Git, Files, Ledger
    - PRANA (Runtime): Kernel, Ephemeral
    - PURUSHA (Identity): Personas
    """

    def __init__(self, kernel: "KernelProtocol"):
        super().__init__(kernel)
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "state"

    @property
    def output_file(self) -> str:
        return "STATE.md"

    @property
    def doc_type(self):
        """Document type for IO service."""
        from vibe_core.io_service import DocumentType

        return DocumentType.READONLY

    def render(self) -> None:
        """Render STATE.md using config-driven sections.

        This is the CORRECT pattern - uses interface.yaml sections.
        """
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            # Fallback if no sections defined
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    def generate_content(self) -> Optional[str]:
        """Fallback content generation if config sections not defined.

        This should NOT be used once interface.yaml has state sections.
        """
        lines = [
            "# STATE",
            "",
            "> The Prakriti State Inspector",
            "> OPUS-009: The Repository IS the Mind",
            "",
        ]

        # Header
        lines.extend(self._format_header())
        lines.append("")

        # STHULA Layer
        lines.append("## Layer 1: STHULA (Physical)")
        lines.append("")
        sthula = self._get_sthula_state()
        lines.extend(self._format_layer_table(sthula))
        lines.append("")

        # PRANA Layer
        lines.append("## Layer 2: PRANA (Runtime)")
        lines.append("")
        prana = self._get_prana_state()
        lines.extend(self._format_layer_table(prana))
        lines.append("")

        # PURUSHA Layer
        lines.append("## Layer 3: PURUSHA (Identity)")
        lines.append("")
        purusha = self._get_purusha_state()
        lines.extend(self._format_layer_table(purusha))
        lines.append("")

        # Session Info
        lines.append("## Session")
        lines.append("")
        session = self._get_session_state()
        lines.extend(self._format_session(session))

        return "\n".join(lines)

    # =========================================================================
    # DATA SOURCE REGISTRATION
    # =========================================================================

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        # Layer sources
        self.register_data_source("state.sthula", self._get_sthula_state)
        self.register_data_source("state.prana", self._get_prana_state)
        self.register_data_source("state.purusha", self._get_purusha_state)

        # Component sources
        self.register_data_source("state.git", self._get_git_status)
        self.register_data_source("state.files", self._get_files_status)
        self.register_data_source("state.ledger", self._get_ledger_status)
        self.register_data_source("state.kernel", self._get_kernel_status)
        self.register_data_source("state.ephemeral", self._get_ephemeral_status)
        self.register_data_source("state.personas", self._get_personas_status)
        self.register_data_source("state.session", self._get_session_state)

        # Summary
        self.register_data_source("state.summary", self._get_state_summary)

    # =========================================================================
    # DATA RETRIEVAL (FROM PRAKRITI)
    # =========================================================================

    def _get_prakriti(self) -> Optional[Any]:
        """Get Prakriti instance from kernel."""
        if hasattr(self.kernel, "prakriti"):
            return self.kernel.prakriti
        return None

    def _get_sthula_state(self) -> Dict[str, Any]:
        """Get Layer 1 (Physical) state."""
        prakriti = self._get_prakriti()
        if not prakriti:
            return {"status": "unavailable", "message": "Prakriti not initialized"}

        return {
            "Git": self._get_git_status(),
            "Files": self._get_files_status(),
            "Ledger": self._get_ledger_status(),
        }

    def _get_prana_state(self) -> Dict[str, Any]:
        """Get Layer 2 (Runtime) state."""
        prakriti = self._get_prakriti()
        if not prakriti:
            return {"status": "unavailable", "message": "Prakriti not initialized"}

        return {
            "Kernel": self._get_kernel_status(),
            "Ephemeral": self._get_ephemeral_status(),
        }

    def _get_purusha_state(self) -> Dict[str, Any]:
        """Get Layer 3 (Identity) state."""
        prakriti = self._get_prakriti()
        if not prakriti:
            return {"status": "unavailable", "message": "Prakriti not initialized"}

        return {
            "Personas": self._get_personas_status(),
        }

    def _get_git_status(self) -> Dict[str, Any]:
        """Get Git state."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "git"):
            return {"branch": "unknown", "dirty": "N/A"}

        try:
            branch = prakriti.git.current_branch()
            is_dirty = prakriti.git.is_dirty()
            return {
                "branch": branch,
                "dirty": is_dirty,
                "status": "clean" if not is_dirty else "modified",
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_files_status(self) -> Dict[str, Any]:
        """Get Files state."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "files"):
            return {"status": "unavailable"}

        try:
            status = prakriti.files.status()
            return status if isinstance(status, dict) else {"status": status}
        except Exception as e:
            return {"error": str(e)}

    def _get_ledger_status(self) -> Dict[str, Any]:
        """Get Ledger state."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "ledger"):
            return {"status": "unavailable"}

        try:
            if hasattr(prakriti.ledger, "get_status"):
                return prakriti.ledger.get_status()
            return {"status": "active"}
        except Exception as e:
            return {"error": str(e)}

    def _get_kernel_status(self) -> Dict[str, Any]:
        """Get Kernel state."""
        try:
            if hasattr(self.kernel, "status"):
                return {"status": self.kernel.status}
            return {"status": "running"}
        except Exception as e:
            return {"error": str(e)}

    def _get_ephemeral_status(self) -> Dict[str, Any]:
        """Get Ephemeral (runtime) state."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "ephemeral"):
            return {"status": "unavailable"}

        try:
            status = prakriti.ephemeral.status()
            return status if isinstance(status, dict) else {"status": status}
        except Exception as e:
            return {"error": str(e)}

    def _get_personas_status(self) -> Dict[str, Any]:
        """Get Personas state."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "personas"):
            return {"count": 0, "status": "unavailable"}

        try:
            # Get persona list
            if hasattr(prakriti.personas, "list_personas"):
                personas = prakriti.personas.list_personas()
                return {"count": len(personas), "active": personas}
            return {"status": "active"}
        except Exception as e:
            return {"error": str(e)}

    def _get_session_state(self) -> Dict[str, Any]:
        """Get current session info."""
        prakriti = self._get_prakriti()
        if not prakriti or not hasattr(prakriti, "session") or not prakriti.session:
            return {"session_id": None, "status": "no session"}

        session = prakriti.session
        return {
            "session_id": session.session_id[:8] if session.session_id else None,
            "boot_time": session.boot_time,
            "commit_count": session.commit_count,
            "crash_recovery": session.crash_recovery,
        }

    def _get_state_summary(self) -> Dict[str, Any]:
        """Get overall state summary."""
        prakriti = self._get_prakriti()
        if not prakriti:
            return {"status": "Prakriti not initialized"}

        try:
            return prakriti.get_system_status()
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # FORMATTING
    # =========================================================================

    def _format_header(self) -> List[str]:
        """Format document header."""
        prakriti = self._get_prakriti()
        if prakriti and hasattr(prakriti, "get_capabilities"):
            caps = prakriti.get_capabilities()
            version = caps.get("version", "unknown")
            return [f"**Prakriti Version**: {version}"]
        return []

    def _format_layer_table(self, data: Dict[str, Any]) -> List[str]:
        """Format layer data as table."""
        lines = ["| Component | Status |", "| --- | --- |"]
        for key, value in data.items():
            if isinstance(value, dict):
                status = value.get("status", value.get("branch", str(value)))
            else:
                status = str(value)
            lines.append(f"| {key} | {status} |")
        return lines

    def _format_session(self, session: Dict[str, Any]) -> List[str]:
        """Format session info."""
        if not session.get("session_id"):
            return ["_No active session_"]

        lines = []
        lines.append(f"- **Session ID**: `{session.get('session_id')}`")
        lines.append(f"- **Commits**: {session.get('commit_count', 0)}")
        if session.get("crash_recovery"):
            lines.append("- **Recovery Mode**: Yes")
        return lines


def create_renderer(kernel: "KernelProtocol", config: Dict[str, Any]) -> StateRenderer:
    """Factory function for InterfacePlugin."""
    return StateRenderer(kernel)
