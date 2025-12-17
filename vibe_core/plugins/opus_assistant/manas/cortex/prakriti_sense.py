"""
OPUS-009: PRAKRITI SENSE - Das sechste Jnanendriya.

Sanskrit: Prakriti = Primordial Matter (State)
Sanskrit: Jnanendriya = Sense organ for knowledge

This cortex module gives MANAS the ability to PERCEIVE the unified state
of the entire system through the StateSyncHolon. Following Sankhya philosophy,
MANAS (Mind) needs Jnanendriyas (sense organs) to perceive Prakriti (state).

The 5 classical Jnanendriyas in OPUS-009:
- Sight    -> FileState (reading files)
- Hearing  -> EventBus (listening to events)
- Smell    -> GitState (sniffing changes)
- Taste    -> LedgerState (tasting history)
- Touch    -> KernelState (touching runtime)

This module adds the 6th sense:
- PRAKRITI SENSE -> StateSyncHolon (unified state awareness)

Capabilities:
1. perceive_state()    - Get Guna summary of all plugins
2. sense_lobotomy()    - Detect .gitignore violations (LOBOTOMY)
3. diagnose(path)      - Diagnose specific path's Guna
4. heal(path)          - Trigger Tamas->Rajas->Sattva healing
5. watch()             - Enable realtime watchdog monitoring
6. broadcast_state()   - Oracle API: emit state changes for other systems

"The mind (MANAS) without senses is blind.
 With PRAKRITI SENSE, MANAS sees the whole system."

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    required: true
    rationale: "Das sechste Jnanendriya - unified state perception for MANAS"
  - path: vibe_core/state/sync_holon.py
    required: true
    rationale: "The underlying StateSyncHolon that provides state awareness"

wiring:
  - pattern: "class PrakritiSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "from vibe_core.state.sync_holon import"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "def perceive_state"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "def sense_lobotomy"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "def diagnose"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
  - pattern: "def heal"
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py

semantic:
  - type: method_exists
    name: prakriti_sense_perceive
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    class: PrakritiSense
    method: perceive_state

  - type: method_exists
    name: prakriti_sense_diagnose
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    class: PrakritiSense
    method: diagnose

  - type: method_exists
    name: prakriti_sense_heal
    in: vibe_core/plugins/opus_assistant/manas/cortex/prakriti_sense.py
    class: PrakritiSense
    method: heal

tests:
  - tests/manas/cortex/test_prakriti_sense.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.state.sync_holon import (
    GovernanceViolation,
    StateGuna,
    StatePathInfo,
    StateSyncHolon,
    WatcherConfig,
)

if TYPE_CHECKING:
    from vibe_core.state.prakriti import Prakriti

logger = logging.getLogger("MANAS.Cortex.PrakritiSense")


@dataclass
class GunaSummary:
    """Summary of state Gunas across all plugins."""

    sattva_count: int  # Balanced, synced
    rajas_count: int  # Active, dirty
    tamas_count: int  # Dead, stale, ignored
    total_plugins: int
    total_paths: int

    @property
    def health_ratio(self) -> float:
        """Ratio of healthy (Sattva) state to total. 1.0 = perfect health."""
        if self.total_paths == 0:
            return 1.0
        return self.sattva_count / self.total_paths

    @property
    def needs_attention(self) -> bool:
        """True if any state is in Tamas (needs healing)."""
        return self.tamas_count > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sattva": self.sattva_count,
            "rajas": self.rajas_count,
            "tamas": self.tamas_count,
            "total_plugins": self.total_plugins,
            "total_paths": self.total_paths,
            "health_ratio": self.health_ratio,
            "needs_attention": self.needs_attention,
        }


@dataclass
class LobotomyReport:
    """Report of .gitignore violations (state files being ignored)."""

    has_lobotomy: bool
    violations: List[str]
    affected_plugins: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "has_lobotomy": self.has_lobotomy,
            "violations": self.violations,
            "affected_plugins": self.affected_plugins,
        }


class PrakritiSense:
    """
    Das sechste Jnanendriya - MANAS unified state perception.

    This cortex module connects MANAS to the StateSyncHolon,
    giving it awareness of all plugin state across the system.

    Following Sankhya: MANAS needs senses to perceive Prakriti.
    This IS that sense for unified state.

    Usage:
        sense = PrakritiSense(workspace=Path("."))
        summary = sense.perceive_state()
        if summary.needs_attention:
            for path in sense.get_tamas_paths():
                sense.heal(path.path)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        prakriti: Optional["Prakriti"] = None,
        enable_watcher: bool = False,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize PRAKRITI SENSE.

        Args:
            workspace: Workspace root (default: cwd)
            prakriti: Optional existing Prakriti instance
            enable_watcher: Enable realtime file watching
            config: Configuration dict from manas.yaml
        """
        self._workspace = workspace or Path.cwd()
        self._config: Dict[str, Any] = config or {}  # OPUS-092: Config wiring
        self._prakriti = prakriti
        self._sync_holon: Optional[StateSyncHolon] = None
        self._enable_watcher = enable_watcher

        # Oracle callbacks for broadcasting state changes
        self._state_listeners: List[Callable[[str, StatePathInfo], None]] = []

        logger.info("[PRAKRITI_SENSE] Initialized - Das sechste Jnanendriya")

    def _ensure_holon(self) -> StateSyncHolon:
        """Lazy-initialize the StateSyncHolon."""
        if self._sync_holon is None:
            # Get or create Prakriti
            if self._prakriti is None:
                from vibe_core.state.prakriti import Prakriti

                self._prakriti = Prakriti(workspace_path=self._workspace)

            # Create SyncHolon with watcher config
            watcher_config = WatcherConfig(enabled=self._enable_watcher)
            self._sync_holon = StateSyncHolon(
                prakriti=self._prakriti,
                kernel=None,  # No kernel injection (as requested)
                watcher_config=watcher_config,
            )

            # Initial discovery
            self._sync_holon.discover_state_paths()
            logger.debug("[PRAKRITI_SENSE] StateSyncHolon initialized and discovered")

        return self._sync_holon

    # =========================================================================
    # Core Perception Methods (Jnanendriya Interface)
    # =========================================================================

    def perceive_state(self, refresh: bool = False) -> GunaSummary:
        """
        Perceive the unified state of all plugins.

        This is the PRIMARY perception method - gives MANAS
        a birds-eye view of all state health across the system.

        Args:
            refresh: Force re-discovery of state paths

        Returns:
            GunaSummary with Sattva/Rajas/Tamas counts
        """
        holon = self._ensure_holon()

        if refresh:
            holon.discover_state_paths()

        guna_counts = holon.get_guna_summary()
        discovered = holon._discovered

        return GunaSummary(
            sattva_count=guna_counts.get("sattva", 0),
            rajas_count=guna_counts.get("rajas", 0),
            tamas_count=guna_counts.get("tamas", 0),
            total_plugins=len(discovered),
            total_paths=sum(len(infos) for infos in discovered.values()),
        )

    def sense_lobotomy(self) -> LobotomyReport:
        """
        Detect .gitignore violations (LOBOTOMY).

        "State files in .gitignore = Lobotomy"

        This checks if any discovered state paths are being
        ignored by git, which would cause state loss.

        Returns:
            LobotomyReport with violations
        """
        holon = self._ensure_holon()
        violations = []
        affected_plugins = []

        for plugin, infos in holon._discovered.items():
            for info in infos:
                if info.is_ignored:
                    violations.append(f"{plugin}: {info.path}")
                    if plugin not in affected_plugins:
                        affected_plugins.append(plugin)

        return LobotomyReport(
            has_lobotomy=len(violations) > 0,
            violations=violations,
            affected_plugins=affected_plugins,
        )

    def diagnose(self, path: Path) -> StateGuna:
        """
        Diagnose the Guna of a specific state path.

        Args:
            path: Path to diagnose

        Returns:
            StateGuna (SATTVA, RAJAS, or TAMAS)
        """
        holon = self._ensure_holon()
        return holon.diagnose_guna(path)

    def heal(self, path: Path) -> StateGuna:
        """
        Trigger healing for a state path.

        Pushes state from Tamas -> Rajas -> Sattva.

        Args:
            path: Path to heal

        Returns:
            New StateGuna after healing
        """
        holon = self._ensure_holon()
        new_guna = holon.heal_toward_sattva(path)

        # Broadcast to listeners (Oracle API)
        info = holon._analyze_path(path, "healed")
        self._broadcast_change("healed", info)

        logger.info(f"[PRAKRITI_SENSE] Healed {path} -> {new_guna.value}")
        return new_guna

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_tamas_paths(self) -> List[StatePathInfo]:
        """Get all paths currently in Tamas (need healing)."""
        holon = self._ensure_holon()
        return holon.get_tamas_paths()

    def get_rajas_paths(self) -> List[StatePathInfo]:
        """Get all paths currently in Rajas (active, need commit)."""
        holon = self._ensure_holon()
        return holon.get_rajas_paths()

    def get_all_discovered(self) -> Dict[str, List[StatePathInfo]]:
        """Get all discovered state paths by plugin."""
        holon = self._ensure_holon()
        return dict(holon._discovered)

    def get_plugin_state(self, plugin_name: str) -> List[StatePathInfo]:
        """Get state paths for a specific plugin."""
        holon = self._ensure_holon()
        return holon._discovered.get(plugin_name, [])

    # =========================================================================
    # Watchdog Control
    # =========================================================================

    def watch(self, enabled: bool = True) -> bool:
        """
        Enable/disable realtime file watching.

        When enabled, file changes are detected in realtime
        and can trigger state commits.

        Args:
            enabled: True to start watching, False to stop

        Returns:
            True if watcher is now in desired state
        """
        holon = self._ensure_holon()

        if enabled:
            return holon.start_watcher()
        else:
            holon.stop_watcher()
            return True

    def is_watching(self) -> bool:
        """Check if watcher is active."""
        if self._sync_holon is None:
            return False
        return self._sync_holon._watcher is not None

    def process_pending_changes(self) -> int:
        """
        Process any queued file changes and commit them.

        Returns:
            Number of files committed
        """
        holon = self._ensure_holon()
        return holon.process_commit_queue()

    # =========================================================================
    # Oracle API (Broadcast State Changes)
    # =========================================================================

    def register_listener(self, callback: Callable[[str, StatePathInfo], None]) -> None:
        """
        Register a listener for state changes (Oracle API).

        MANAS can serve as a "Sendemast" (broadcast tower) for state sync.
        Other systems can register to receive state change notifications.

        Args:
            callback: Function(event_type, StatePathInfo) to call on changes
        """
        self._state_listeners.append(callback)
        logger.debug(f"[PRAKRITI_SENSE] Registered listener (total: {len(self._state_listeners)})")

    def unregister_listener(self, callback: Callable[[str, StatePathInfo], None]) -> None:
        """Unregister a state change listener."""
        if callback in self._state_listeners:
            self._state_listeners.remove(callback)

    def _broadcast_change(self, event_type: str, info: StatePathInfo) -> None:
        """Broadcast a state change to all listeners."""
        for listener in self._state_listeners:
            try:
                listener(event_type, info)
            except Exception as e:
                logger.warning(f"[PRAKRITI_SENSE] Listener error: {e}")

    # =========================================================================
    # Lifecycle Hooks (for integration with CognitiveKernel)
    # =========================================================================

    def on_manas_boot(self) -> GunaSummary:
        """
        Called when MANAS boots - perform initial state discovery and healing.

        Returns:
            Initial GunaSummary
        """
        holon = self._ensure_holon()

        # Run boot sequence
        holon.on_boot()

        # Return summary
        return self.perceive_state()

    def on_manas_shutdown(self) -> None:
        """Called when MANAS shuts down - commit any pending state."""
        if self._sync_holon is not None:
            self._sync_holon.on_shutdown()

    def on_manas_tick(self) -> Optional[GunaSummary]:
        """
        Called on MANAS cognitive tick - check for state that needs attention.

        Returns:
            GunaSummary if any state needs attention, None if all healthy
        """
        summary = self.perceive_state()

        if summary.needs_attention:
            logger.info(
                f"[PRAKRITI_SENSE] State needs attention: {summary.tamas_count} Tamas, {summary.rajas_count} Rajas"
            )
            return summary

        return None

    # =========================================================================
    # Chat Integration (for Jnana handler)
    # =========================================================================

    def get_status_for_chat(self) -> str:
        """
        Get human-readable status for chat interface.

        Can be used by Jnana handler to respond to state queries.
        """
        summary = self.perceive_state()
        lobotomy = self.sense_lobotomy()

        lines = [
            "PRAKRITI SENSE - System State Overview",
            "=" * 40,
            "",
            f"Total Plugins: {summary.total_plugins}",
            f"Total State Paths: {summary.total_paths}",
            "",
            "Guna Distribution:",
            f"  Sattva (Balanced): {summary.sattva_count}",
            f"  Rajas (Active):    {summary.rajas_count}",
            f"  Tamas (Stale):     {summary.tamas_count}",
            "",
            f"Health Ratio: {summary.health_ratio:.1%}",
        ]

        if lobotomy.has_lobotomy:
            lines.extend(
                [
                    "",
                    "LOBOTOMY DETECTED!",
                    "The following state files are in .gitignore:",
                ]
            )
            for v in lobotomy.violations[:5]:
                lines.append(f"  - {v}")
            if len(lobotomy.violations) > 5:
                lines.append(f"  ... and {len(lobotomy.violations) - 5} more")

        if summary.needs_attention:
            lines.extend(
                [
                    "",
                    "ACTION NEEDED:",
                    f"  {summary.tamas_count} paths need healing",
                    "  Use 'heal state' to repair",
                ]
            )

        return "\n".join(lines)


# =============================================================================
# Chat Handler Integration
# =============================================================================


def handle_prakriti_query(content: str, workspace: Optional[Path] = None) -> str:
    """
    Handle prakriti/state queries from chat.

    Keywords: prakriti, state sense, guna, lobotomy

    Args:
        content: The chat message content
        workspace: Workspace path

    Returns:
        Response string
    """
    sense = PrakritiSense(workspace=workspace)
    content_lower = content.lower()

    if "lobotomy" in content_lower:
        report = sense.sense_lobotomy()
        if report.has_lobotomy:
            return (
                f"LOBOTOMY DETECTED!\n\n"
                f"State files in .gitignore = Memory Loss!\n\n"
                f"Affected plugins: {', '.join(report.affected_plugins)}\n\n"
                f"Violations:\n" + "\n".join(f"  - {v}" for v in report.violations)
            )
        else:
            return "No lobotomy detected. All state files are properly tracked."

    elif "heal" in content_lower:
        tamas_paths = sense.get_tamas_paths()
        if not tamas_paths:
            return "All state is healthy (Sattva). No healing needed."

        healed = 0
        for info in tamas_paths:
            sense.heal(info.path)
            healed += 1

        return f"Healed {healed} Tamas paths toward Sattva."

    else:
        # Default: show status
        return sense.get_status_for_chat()


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "PrakritiSense",
    "GunaSummary",
    "LobotomyReport",
    "handle_prakriti_query",
]
