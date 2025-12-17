"""
Prakriti State Panel - Shows unified state across all three layers.

OPUS-027: The Repository IS the Mind

Displays:
- Session status (if kernel session active)
- Layer 1 (STHULA): Git + Ledger sync status
- Layer 2 (PRANA): Kernel runtime state
- Layer 3 (PURUSHA): Active persona
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from . import BasePanel

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import GunaSummary


class PrakritiStatePanel(BasePanel):
    """Shows Prakriti unified state across all three layers."""

    @property
    def panel_id(self) -> str:
        return "prakriti_state"

    @property
    def title(self) -> str:
        return "Prakriti State (OPUS-027)"

    @property
    def priority(self) -> int:
        return 5  # Show at top (before verification)

    def render(self) -> str:
        """Render Prakriti state panel."""
        lines = [f"## {self.title}", ""]

        # Try to get Prakriti from kernel
        prakriti = self._get_prakriti()

        if not prakriti:
            lines.append("_Prakriti not available (kernel not running or not initialized)_")
            return "\n".join(lines)

        # Session status
        session = getattr(prakriti, "session", None)
        if session:
            lines.append("### 📍 Active Session")
            lines.append("")
            lines.append("| Property | Value |")
            lines.append("| --- | --- |")
            lines.append(f"| Session ID | `{session.session_id}` |")
            lines.append(f"| Boot Commit | `{session.boot_commit[:7]}` |")
            lines.append(f"| Commits | {session.commit_count} |")
            lines.append(f"| Crash Recovery | {'⚠️ Yes' if session.crash_recovery else '✅ No'} |")
            lines.append("")
        else:
            lines.append("### 📍 Session")
            lines.append("")
            lines.append("_No active session (kernel may be stopped)_")
            lines.append("")

        # Layer status table
        lines.append("### 🔮 Three Layers")
        lines.append("")
        lines.append("| Layer | Name | Status | Details |")
        lines.append("| --- | --- | --- | --- |")

        # Layer 1: STHULA (Physical)
        sthula_status = self._get_sthula_status(prakriti)
        lines.append(f"| 1 | STHULA (Physical) | {sthula_status['icon']} | {sthula_status['details']} |")

        # Layer 2: PRANA (Runtime)
        prana_status = self._get_prana_status(prakriti)
        lines.append(f"| 2 | PRANA (Runtime) | {prana_status['icon']} | {prana_status['details']} |")

        # Layer 3: PURUSHA (Identity)
        purusha_status = self._get_purusha_status(prakriti)
        lines.append(f"| 3 | PURUSHA (Identity) | {purusha_status['icon']} | {purusha_status['details']} |")

        lines.append("")

        # Git/Ledger sync indicator (Cryptographic Zipper)
        sync_status = self._get_sync_status(prakriti)
        lines.append("### 🔗 Cryptographic Zipper")
        lines.append("")
        lines.append("| Component | Hash | Synced |")
        lines.append("| --- | --- | --- |")
        lines.append(f"| Git HEAD | `{sync_status['git_sha']}` | {sync_status['sync_icon']} |")
        lines.append(f"| Ledger HEAD | `{sync_status['ledger_hash']}` | {sync_status['sync_icon']} |")
        lines.append("")

        if not sync_status["synced"]:
            lines.append("⚠️ **Drift Detected**: Git and Ledger are out of sync")
            lines.append("")

        # 🔮 TRI-GUNA Status (OPUS-009 Wire 1)
        guna_summary = self._get_guna_summary()
        if guna_summary:
            lines.append("### 🔮 Tri-Guna (State Health)")
            lines.append("")
            lines.append("| Guna | Count | Meaning |")
            lines.append("| --- | --- | --- |")
            lines.append(f"| ✅ Sattva | {guna_summary.sattva_count} | Synced & Clean |")
            lines.append(f"| 🟡 Rajas | {guna_summary.rajas_count} | Active & Dirty |")
            lines.append(f"| ❌ Tamas | {guna_summary.tamas_count} | Stale & Broken |")
            lines.append("")

            if guna_summary.needs_attention:
                lines.append(f"⚠️ **Healing Required**: {guna_summary.tamas_count} paths in Tamas")
                lines.append("")
            elif guna_summary.rajas_count > 0:
                lines.append(f"🔄 **Activity Detected**: {guna_summary.rajas_count} paths changing")
                lines.append("")

        return "\n".join(lines)

    def _get_prakriti(self) -> Optional[Any]:
        """Get Prakriti instance from kernel or create standalone."""
        # Try kernel first
        if hasattr(self.kernel, "prakriti"):
            return self.kernel.prakriti

        # Fallback: Create standalone instance for read-only status
        try:
            from vibe_core.state.prakriti import Prakriti

            return Prakriti(self._root)
        except Exception:
            return None

    def _get_sthula_status(self, prakriti: Any) -> Dict[str, str]:
        """Get Layer 1 (STHULA) status."""
        try:
            git_status = prakriti.git.status()
            is_dirty = git_status.get("is_dirty", False)
            branch = git_status.get("branch", "unknown")

            if is_dirty:
                return {"icon": "🟡", "details": f"Dirty on `{branch}`"}
            else:
                return {"icon": "✅", "details": f"Clean on `{branch}`"}
        except Exception as e:
            return {"icon": "❌", "details": f"Error: {str(e)[:30]}"}

    def _get_prana_status(self, prakriti: Any) -> Dict[str, str]:
        """Get Layer 2 (PRANA) status."""
        try:
            # kernel.status is a property returning KernelStatus enum
            status = self.kernel.status
            agents = getattr(self.kernel, "_agents", {})
            agent_count = len(agents) if isinstance(agents, dict) else 0

            # KernelStatus is an enum: STOPPED, BOOTING, RUNNING, HALTED
            status_value = status.value if hasattr(status, "value") else str(status)

            if status_value == "RUNNING":
                return {"icon": "✅", "details": f"Running ({agent_count} agents)"}
            elif status_value == "STOPPED":
                return {"icon": "⏹️", "details": "Stopped"}
            elif status_value == "BOOTING":
                return {"icon": "🔄", "details": "Booting..."}
            elif status_value == "HALTED":
                return {"icon": "🛑", "details": "HALTED (Narasimha)"}
            else:
                return {"icon": "🟡", "details": f"State: {status_value}"}
        except Exception as e:
            return {"icon": "❌", "details": f"Error: {str(e)[:30]}"}

    def _get_purusha_status(self, prakriti: Any) -> Dict[str, str]:
        """Get Layer 3 (PURUSHA) status."""
        try:
            personas_status = prakriti.personas.status()
            active = personas_status.get("active_persona")
            available = personas_status.get("available_personas", [])

            if active:
                return {"icon": "✅", "details": f"Active: `{active}`"}
            elif available:
                return {"icon": "⚪", "details": f"{len(available)} available, none active"}
            else:
                return {"icon": "⚪", "details": "No personas defined"}
        except Exception as e:
            return {"icon": "❌", "details": f"Error: {str(e)[:30]}"}

    def _get_sync_status(self, prakriti: Any) -> Dict[str, Any]:
        """Get Git/Ledger sync status (Cryptographic Zipper)."""
        result = {
            "git_sha": "unknown",
            "ledger_hash": "unknown",
            "synced": False,
            "sync_icon": "❓",
        }

        try:
            # Git HEAD
            git_sha = prakriti.git.head_sha()
            result["git_sha"] = git_sha[:12] if git_sha else "no commits"

            # Ledger HEAD
            ledger_hash = prakriti.ledger.get_current_head_hash()
            result["ledger_hash"] = ledger_hash[:12] if ledger_hash else "empty"

            # Check sync
            last_sync = prakriti.ledger.get_last_sync_commit()
            if last_sync and git_sha and last_sync == git_sha:
                result["synced"] = True
                result["sync_icon"] = "✅"
            elif not last_sync:
                # No ledger entries yet - OK for fresh repos
                result["synced"] = True
                result["sync_icon"] = "⚪"
            else:
                result["synced"] = False
                result["sync_icon"] = "⚠️"

        except Exception:
            result["sync_icon"] = "❌"

        return result

    def _get_guna_summary(self) -> Optional["GunaSummary"]:
        """Get Tri-Guna summary from PrakritiSense (OPUS-009 Wire 1)."""
        try:
            # Try to get from MANAS CognitiveKernel first
            manas = getattr(self.kernel, "manas", None)
            if manas and hasattr(manas, "_prakriti_sense"):
                prakriti_sense = manas._prakriti_sense
                if prakriti_sense:
                    return prakriti_sense.perceive_state()

            # Fallback: Create standalone PrakritiSense for read-only
            from pathlib import Path

            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import PrakritiSense

            root = getattr(self, "_root", None) or Path(".")
            sense = PrakritiSense(root)
            return sense.perceive_state()
        except Exception as e:
            # Log but don't crash - Tri-Guna is nice to have
            import logging

            logging.getLogger("PRAKRITI_PANEL").debug(f"PrakritiSense unavailable: {e}")
            return None
