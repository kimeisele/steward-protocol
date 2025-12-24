#!/usr/bin/env python3
"""
DocRenderer - Markdown document rendering for Kernel output.

EXTRACTED FROM kernel_impl.py to reduce kernel churn.

ARCHITECTURE: DocRenderer produces CONTENT. Kernel I/O Service WRITES.

Kernel should ONLY:
1. Collect state (snapshot)
2. Call DocRenderer.render_all(snapshot, state, io_service)
3. I/O Service handles atomic writes + audit trail

Kernel should NOT:
- Format markdown
- Know about document structure
- Have 100+ line render methods
- Write files directly (use io_service)

This module handles all markdown generation for:
- OPERATIONS.md (operations dashboard)
- SETTINGS.md (configuration interface)
- ENVOY.md (user request terminal)

See: docs/architecture/KERNEL_IO_ARCHITECTURE.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService

logger = logging.getLogger(__name__)


@dataclass
class SettingsRenderState:
    """State needed for SETTINGS.md rendering."""

    ledger_path: str
    varna_registry: Dict[str, object]  # agent_id -> Varna enum
    ashrama_registry: Dict[str, object]  # agent_id -> AshramaTransition
    execution_history: List[Dict[str, object]]
    # UI Enhancement: Phoenix config state
    provider_info: Optional[Dict[str, str]] = None  # Provider name, models, etc.
    live_fire_enabled: bool = False  # Execution mode


@dataclass
class EnvoyRenderState:
    """State needed for ENVOY.md rendering."""

    pending_tasks: Dict[str, Dict[str, object]]
    request_history: List[Dict[str, object]]
    available_routes: List[Dict[str, object]]
    extract_request_fn: Optional[Callable[[Path], str]] = None


class DocRenderer:
    """
    Centralized document renderer for kernel markdown output.

    ARCHITECTURE: Produces content, uses I/O Service for writes.
    When io_service is provided, all writes go through the central I/O layer
    with atomic writes, file locking, and audit trail.

    Usage:
        # With I/O Service (preferred):
        renderer = DocRenderer(io_service=kernel.io)
        renderer.render_operations(snapshot)

        # Legacy mode (direct writes, deprecated):
        renderer = DocRenderer()
        renderer.render_operations(snapshot)  # Falls back to Path.write_text()
    """

    def __init__(self, io_service: Optional["KernelIOService"] = None):
        """
        Initialize DocRenderer.

        Args:
            io_service: Kernel I/O Service for centralized file writes.
                        If None, falls back to direct writes (deprecated).
        """
        self._io = io_service
        if not io_service:
            logger.warning("⚠️  DocRenderer initialized without io_service - using deprecated direct writes")

    def _write_document(
        self,
        name: str,
        lines: List[str],
        writer_id: str = "DOC_RENDERER",
        bidirectional: bool = False,
    ) -> Optional[float]:
        """
        Write document content through I/O Service or fallback.

        Args:
            name: Document filename (e.g., "OPERATIONS.md")
            lines: Content lines to write
            writer_id: ID for audit trail
            bidirectional: If True, use BIDIRECTIONAL doc type

        Returns:
            File mtime after write, or None on error
        """
        content = "\n".join(lines)

        if self._io:
            # Use I/O Service (preferred path)
            from vibe_core.io_service import DocumentType

            doc_type = DocumentType.BIDIRECTIONAL if bidirectional else DocumentType.READONLY
            result = self._io.write_document(
                name=name,
                content=content,
                doc_type=doc_type,
                writer_id=writer_id,
                add_header=False,  # DocRenderer adds its own header
            )
            if result.success:
                return result.mtime
            logger.error(f"❌ I/O Service write failed: {result.error}")
            return None
        else:
            # Fallback: direct write (deprecated)
            try:
                output_path = Path(name)
                output_path.write_text(content)
                return output_path.stat().st_mtime
            except Exception as e:
                logger.error(f"❌ Direct write failed: {e}")
                return None

    @staticmethod
    def render_unified_header(generator: str, snapshot: Dict[str, object]) -> List[str]:
        """
        Generate unified header for auto-generated markdown files.

        Args:
            generator: Name of the generator (e.g., 'KERNEL', 'SCRIBE')
            snapshot: Kernel snapshot data

        Returns:
            List of header lines to prepend to markdown file
        """
        timestamp = snapshot.get("timestamp", datetime.utcnow().isoformat())
        kernel_status = snapshot.get("kernel_status", "UNKNOWN")
        agent_count = len(snapshot.get("agents", {}))

        return [
            "<!--",
            "╔══════════════════════════════════════════════════════════════════════╗",
            f"║  AUTO-GENERATED by {generator}",
            f"║  Last Updated: {timestamp}",
            f"║  Kernel: 🟢 {kernel_status} ({agent_count} agents)",
            "╠══════════════════════════════════════════════════════════════════════╣",
            "║  📚 Auto-Docs: README | INDEX | AGENTS | CITYMAP | HELP             ║",
            "║                DASHBOARD | RAG | OPERATIONS | SETTINGS | ENVOY      ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            "-->",
            "",
            "> **📚 Auto-Generated Docs:** [README](README.md) · [INDEX](INDEX.md) · [AGENTS](AGENTS.md) · [CITYMAP](CITYMAP.md) · [HELP](HELP.md) · [DASHBOARD](DASHBOARD.md) · [RAG](RAG.md) · [OPERATIONS](OPERATIONS.md) · [SETTINGS](SETTINGS.md) · [ENVOY](ENVOY.md)",
            "",
        ]

    @staticmethod
    def extract_quick_note(file_path: Path) -> str:
        """
        Extract preserved Quick Note content from existing file.

        Quick Note format:
        ## 📝 Quick Note
        > [User content here - preserved across re-renders]

        Args:
            file_path: Path to the markdown file

        Returns:
            The user's Quick Note content, or empty string if not found
        """
        try:
            if not file_path.exists():
                return ""

            content = file_path.read_text()
            lines = content.split("\n")

            in_quick_note = False
            note_lines = []

            for line in lines:
                if "## 📝 Quick Note" in line:
                    in_quick_note = True
                    continue

                if in_quick_note:
                    # Stop at next section
                    if line.strip().startswith("## ") or line.strip().startswith("---"):
                        break
                    # Collect note content (skip empty lines at start)
                    if line.strip() or note_lines:
                        note_lines.append(line)

            # Trim trailing empty lines
            while note_lines and not note_lines[-1].strip():
                note_lines.pop()

            return "\n".join(note_lines)

        except Exception:
            return ""

    @staticmethod
    def render_quick_note_section(existing_note: str = "") -> List[str]:
        """
        Render the Quick Note section with preserved content.

        Args:
            existing_note: Previously saved note content

        Returns:
            List of lines for the Quick Note section
        """
        lines = [
            "## 📝 Quick Note",
            "",
            "> This note is preserved across re-renders. Write anything you want to remember.",
            "",
        ]

        if existing_note.strip():
            lines.append(existing_note)
        else:
            lines.append("_Your note here..._")

        lines.extend(["", "---", ""])
        return lines

    def _render_settings_sections(self, state: "SettingsRenderState") -> List[str]:
        """
        Render all plugin-based settings sections.

        Uses the SettingsSection plugin architecture for scalability.
        Each section is self-contained and auto-discovered.

        Args:
            state: Current settings render state

        Returns:
            List of markdown lines from all sections
        """
        lines = []

        try:
            from vibe_core.settings import SectionContext, get_section_loader

            # Build section context from state
            context = SectionContext(
                live_fire_enabled=state.live_fire_enabled,
                provider_info=state.provider_info or {},
                provider_name=state.provider_info.get("name", "unknown") if state.provider_info else "unknown",
            )

            # Load and render all sections (sorted by priority)
            loader = get_section_loader()
            for section in loader.load_all():
                try:
                    section_lines = section.render(context)
                    lines.extend(section_lines)
                except Exception as e:
                    logger.error(f"Failed to render section '{section.section_id}': {e}")
                    lines.extend([f"<!-- Section '{section.section_id}' failed to render: {e} -->", ""])

        except ImportError as e:
            # Fallback if settings module not available
            logger.warning(f"Settings sections not available: {e}")
            lines.extend(
                [
                    "---",
                    "",
                    "_Settings sections not available. Install vibe_core.settings module._",
                    "",
                ]
            )

        return lines

    def render_operations(self, snapshot: Dict[str, object], output_path: Path = Path("OPERATIONS.md")) -> None:
        """
        Render OPERATIONS.md from snapshot data.

        Args:
            snapshot: Kernel snapshot data
            output_path: Path to write output (default: OPERATIONS.md)
        """
        try:
            # Unified header
            lines = self.render_unified_header("KERNEL", snapshot)

            lines.extend(
                [
                    "# 🏗️ OPERATIONS DASHBOARD",
                    "",
                    "## 📊 Kernel Status",
                    f"- Kernel: {snapshot['kernel_status']}",
                    f"- Agents Registered: {len(snapshot['agents'])}",
                    f"- Queue Length: {snapshot['scheduler']['queue_length']}",
                    f"- Completed Tasks: {snapshot['scheduler']['completed']}",
                    f"- Total Events: {snapshot['ledger_stats']['total_events']}",
                    "",
                    "## 🤖 Agent Status",
                ]
            )

            for agent_id, status in snapshot["agents"].items():
                lines.append(f"\n### {agent_id}")
                if "error" in status:
                    lines.append(f"❌ Error: {status['error']}")
                else:
                    for key, value in status.items():
                        lines.append(f"- {key}: {value}")

            lines.extend(
                [
                    "",
                    "---",
                    "*This dashboard is auto-generated by the kernel heartbeat.*",
                ]
            )

            # Write through I/O Service (or fallback)
            mtime = self._write_document(
                name=str(output_path),
                lines=lines,
                writer_id="KERNEL_OPS",
            )
            if mtime:
                logger.info("📋 Operations dashboard rendered")

        except Exception as e:
            logger.error(f"❌ Failed to render dashboard: {e}")

    def render_settings(
        self,
        snapshot: Dict[str, object],
        state: SettingsRenderState,
        output_path: Path = Path("SETTINGS.md"),
    ) -> Optional[float]:
        """
        Render SETTINGS.md from snapshot data.

        PHASE 1: READ-ONLY projection of kernel configuration.
        PHASE 2: Command Queue for SETTINGS -> REALITY sync.

        Args:
            snapshot: Kernel snapshot data
            state: Settings-specific state (registries, history)
            output_path: Path to write output (default: SETTINGS.md)

        Returns:
            New file mtime after write (for change detection), or None on error
        """
        try:
            # Extract existing Quick Note before re-rendering
            existing_note = self.extract_quick_note(output_path)

            # Unified header
            lines = self.render_unified_header("KERNEL", snapshot)

            # Quick Note section (preserved across renders)
            lines.extend(self.render_quick_note_section(existing_note))

            lines.extend(
                [
                    "# ⚙️ SYSTEM SETTINGS",
                    "",
                    "**Mode:** INTERACTIVE (Command Queue enabled)",
                    "",
                    "> Write SET commands in the Pending Commands section below.",
                    "",
                    "## 🔧 Kernel Configuration",
                    "",
                    f"- **Status:** {snapshot['kernel_status']}",
                    f"- **Ledger Path:** {state.ledger_path}",
                    f"- **Agents Registered:** {len(snapshot['agents'])}",
                    f"- **Queue Length:** {snapshot['scheduler']['queue_length']}",
                    f"- **Total Events:** {snapshot['ledger_stats']['total_events']}",
                    "",
                ]
            )

            # Render plugin-based settings sections
            lines.extend(self._render_settings_sections(state))

            # Add agent registry details
            lines.extend(
                [
                    "## 🤖 Agent Registry",
                    "",
                    "Current agent configuration and status:",
                    "",
                ]
            )

            for agent_id, status in snapshot["agents"].items():
                lines.append(f"### `{agent_id}`")
                lines.append("")

                if "error" in status:
                    lines.append(f"❌ **Error:** {status['error']}")
                else:
                    # Display all status fields
                    for key, value in status.items():
                        # Format value nicely
                        if isinstance(value, list):
                            value_str = ", ".join(f"`{v}`" for v in value)
                        elif isinstance(value, dict):
                            value_str = f"{len(value)} items"
                        else:
                            value_str = f"{value}"
                        lines.append(f"- **{key}:** {value_str}")

                # Add governance info if available
                varna = state.varna_registry.get(agent_id)
                ashrama_transition = state.ashrama_registry.get(agent_id)

                if varna:
                    lines.append(f"- **Varna (Class):** `{varna.value}`")

                if ashrama_transition:
                    lines.append(f"- **Ashrama (Stage):** `{ashrama_transition.current_ashrama.value}`")
                    permissions = ashrama_transition.get_current_permissions()
                    if permissions:
                        lines.append(f"- **Permissions:** {', '.join(f'`{p}`' for p in permissions)}")

                lines.append("")

            # Add Command Queue sections
            lines.extend(
                [
                    "---",
                    "",
                    "## ⚡ Pending Commands",
                    "",
                    "> **Write your commands here.** The kernel will process them on the next tick.",
                    "> Commands are executed in order and then moved to the Execution Ledger below.",
                    "",
                    "**Available Commands:**",
                    "- `SET kernel.log_level=DEBUG` - Change log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)",
                    "- `SET kernel.verbose=true` - Enable/disable verbose mode (true/false)",
                    "- `PAUSE agent.<agent_id>` - Pause an agent (stops task execution)",
                    "- `RESUME agent.<agent_id>` - Resume a paused agent",
                    "- `RESTART agent.<agent_id>` - Restart an agent (pause + resume)",
                    "- `REFRESH topology` - Force refresh agent topology",
                    "",
                    "**Example:**",
                    "```",
                    "- SET kernel.log_level=DEBUG",
                    "- RESTART agent.scribe",
                    "```",
                    "",
                    "_No pending commands. Add commands above this line._",
                    "",
                    "---",
                    "",
                    "## 🏛️ Execution Ledger",
                    "",
                    "> **Read-Only.** This section shows the last 10 executed commands.",
                    "> The kernel updates this automatically after processing commands.",
                    "",
                ]
            )

            # Add execution history
            if state.execution_history:
                for entry in reversed(list(state.execution_history)):
                    timestamp = entry.get("timestamp", "unknown")
                    status = entry.get("status", "UNKNOWN")
                    command = entry.get("command", "")
                    reason = entry.get("reason", "")

                    # Format status emoji
                    status_emoji = "✅" if status == "SUCCESS" else "❌"

                    # Format command text
                    if isinstance(command, dict):
                        action = command.get("action", "")
                        if action == "SET":
                            cmd_text = f"SET {command.get('key')}={command.get('value')}"
                        elif action == "PAUSE":
                            cmd_text = f"PAUSE {command.get('agent_id')}"
                        elif action == "RESUME":
                            cmd_text = f"RESUME {command.get('agent_id')}"
                        else:
                            cmd_text = str(command)
                    else:
                        cmd_text = str(command)

                    # Build ledger line
                    line_parts = [f"- [{status_emoji} {status} @ {timestamp}]", cmd_text]
                    if reason:
                        line_parts.append(f"(Reason: {reason})")

                    lines.append(" ".join(line_parts))
            else:
                lines.append("_No commands executed yet._")

            lines.extend(
                [
                    "",
                    "---",
                    (
                        "*This file is auto-generated by the kernel pulse. "
                        "Edit the Pending Commands section to control the system.*"
                    ),
                ]
            )

            # Write through I/O Service (or fallback)
            mtime = self._write_document(
                name=str(output_path),
                lines=lines,
                writer_id="KERNEL_SETTINGS",
                bidirectional=True,  # SETTINGS.md is bidirectional
            )
            if mtime:
                logger.info("⚙️  Settings file rendered: SETTINGS.md")
                return mtime
            return None

        except Exception as e:
            logger.error(f"❌ Failed to render settings file: {e}")
            return None

    def render_envoy(
        self,
        snapshot: Dict[str, object],
        state: EnvoyRenderState,
        output_path: Path = Path("ENVOY.md"),
    ) -> None:
        """
        Render ENVOY.md terminal interface.

        ENVOY.md is the user-facing terminal where humans can:
        - Write natural language requests
        - See task status (QUEUED, RUNNING, COMPLETED, FAILED)
        - View execution history

        The kernel PRESERVES user content in the Request section.
        Only Status and Response sections are updated by the kernel.

        Args:
            snapshot: Kernel snapshot data
            state: Envoy-specific state (tasks, history, routes)
            output_path: Path to write output (default: ENVOY.md)
        """
        try:
            # If file exists, preserve the user's Request section
            existing_request = ""
            if output_path.exists() and state.extract_request_fn:
                existing_request = state.extract_request_fn(output_path)

            # Unified header
            lines = self.render_unified_header("KERNEL", snapshot)

            lines.extend(
                [
                    "# 📬 ENVOY TERMINAL",
                    "",
                    "**Mode:** INTERACTIVE (async dispatch)",
                    "",
                    "> Write your request below. The kernel routes it through PlaybookRouter",
                    "> and dispatches tasks to agents asynchronously. No LLM required.",
                    "",
                    "---",
                    "",
                    "## 💬 Request",
                    "",
                    "> **Write your request here.** The kernel will process it on the next tick.",
                    "> Requests are routed via PlaybookRouter (pattern matching) and dispatched async.",
                    "",
                ]
            )

            # Preserve user's request if it exists
            if existing_request.strip():
                lines.append(existing_request)
            else:
                lines.append("_No pending request. Write your request above this line._")

            lines.extend(
                [
                    "",
                    "---",
                    "",
                    "## 📊 Status",
                    "",
                ]
            )

            # Show pending/running tasks
            if state.pending_tasks:
                for task_id, task_meta in state.pending_tasks.items():
                    status = task_meta.get("status", "QUEUED")
                    request = task_meta.get("request", "")[:50]
                    route = task_meta.get("route", "unknown")
                    status_emoji = {
                        "QUEUED": "⏳",
                        "RUNNING": "🔄",
                        "COMPLETED": "✅",
                        "FAILED": "❌",
                    }.get(status, "❓")
                    lines.append(f"- {status_emoji} **{status}** | `{route}` | {request}...")
            else:
                lines.append("_No active tasks._")

            lines.extend(
                [
                    "",
                    "---",
                    "",
                    "## 📜 Response History",
                    "",
                    "> **Read-Only.** This section shows the last 20 processed requests.",
                    "",
                ]
            )

            # Show execution history
            if state.request_history:
                for entry in reversed(list(state.request_history)):
                    timestamp = entry.get("timestamp", "unknown")
                    status = entry.get("status", "UNKNOWN")
                    request = entry.get("request", "")[:40]
                    response = entry.get("response", "")[:60]
                    route = entry.get("route", "unknown")

                    status_emoji = "✅" if status == "COMPLETED" else "❌"
                    lines.append(f"### [{status_emoji} {timestamp}] {route}")
                    lines.append(f"**Request:** {request}...")
                    lines.append(f"**Response:** {response}...")
                    lines.append("")
            else:
                lines.append("_No requests processed yet._")

            lines.extend(
                [
                    "",
                    "---",
                    "",
                    "## 🎯 Available Routes",
                    "",
                    "The PlaybookRouter matches your request to these routes:",
                    "",
                ]
            )

            # List available routes from PlaybookRouter
            for route in state.available_routes[:5]:  # Show top 5
                name = route.get("name", "unknown")
                desc = route.get("description", "")
                examples = route.get("examples", [])[:2]
                lines.append(f"- **{name}**: {desc}")
                if examples:
                    lines.append(f"  - Examples: {', '.join(examples)}")

            lines.extend(
                [
                    "",
                    "---",
                    "*This terminal is auto-generated by the kernel pulse. Write requests in the Request section.*",
                ]
            )

            # Write through I/O Service (or fallback)
            mtime = self._write_document(
                name=str(output_path),
                lines=lines,
                writer_id="KERNEL_ENVOY",
                bidirectional=True,  # ENVOY.md is bidirectional
            )
            if mtime:
                logger.info("📬 ENVOY.md terminal rendered")

        except Exception as e:
            logger.error(f"❌ Failed to render ENVOY.md: {e}")

    def render_all(
        self,
        snapshot: Dict[str, object],
        settings_state: Optional[SettingsRenderState] = None,
        envoy_state: Optional[EnvoyRenderState] = None,
    ) -> Dict[str, object]:
        """
        Render all kernel-generated markdown files.

        Args:
            snapshot: Kernel snapshot data
            settings_state: State for SETTINGS.md (optional)
            envoy_state: State for ENVOY.md (optional)

        Returns:
            Dict with render results (e.g., {'settings_mtime': float})
        """
        results = {}

        # Always render OPERATIONS.md
        self.render_operations(snapshot)

        # Render SETTINGS.md if state provided
        if settings_state:
            mtime = self.render_settings(snapshot, settings_state)
            if mtime:
                results["settings_mtime"] = mtime

        # Render ENVOY.md if state provided
        if envoy_state:
            self.render_envoy(snapshot, envoy_state)

        return results


# Convenience function for simple usage
def render_kernel_docs(
    snapshot: Dict[str, object],
    io_service: Optional["KernelIOService"] = None,
) -> None:
    """
    Quick render of OPERATIONS.md only (no state needed).

    Args:
        snapshot: Kernel snapshot data
        io_service: Optional I/O Service for centralized writes
    """
    DocRenderer(io_service=io_service).render_operations(snapshot)
