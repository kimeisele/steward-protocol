"""
OPUS State Paths - Unified State Path Resolution

This module provides the SINGLE source of truth for opus_assistant state paths.
All MANAS components should use these helpers instead of hardcoding ".opus_state/".

Architecture:
    StateService (vibe_core/state/state_service.py)
    └── plugin_id="opus_assistant"
        → .vibe/state/plugins/opus_assistant/

Heritage Migration:
    StateService.load() auto-migrates from .opus_state/ on first read.
    This provides backwards compatibility during migration.

Usage:
    from vibe_core.plugins.opus_assistant.core.state_paths import (
        get_opus_state_path,
        get_opus_state_service,
        STATE_FILES,
    )

    # Get path for a specific file
    path = get_opus_state_path(workspace, "synapses.json")

    # Get full StateService for save/load operations
    service = get_opus_state_service(workspace)
    service.save("synapses.json", data)
    data = service.load("synapses.json", default={})

Migration Status: Phase 1 (2026-01-04)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("OPUS.STATE_PATHS")

# ============================================================================
# STATE FILE CONSTANTS
# ============================================================================
# Centralized file name definitions for consistency across MANAS components.

STATE_FILES = {
    # Core MANAS state
    "intents": "manas_intents.json",
    "memory": "manas_memory.json",
    "awareness": "manas_awareness.json",
    "session": "session.json",
    # Cognitive state
    "synapses": "synapses.json",
    "decisions": "viveka_decisions.json",
    "reinforcement": "last_reinforcement.json",
    "karma": "karma_log.json",
    # Strategic state
    "sankalpa": "sankalpa.json",
    "sutra_history": "sutra_intent_history.json",
    "sanskrit_matrix": "sanskrit_matrix.json",
    "akshara_graph": "akshara_graph.json",
    # Training state
    "curiosity": "curiosity.json",
    # Logs (JSONL)
    "observations": "observations.jsonl",
    "karma_history": "karma_history.jsonl",
    "syscalls": "syscalls.jsonl",
    # Treasury
    "treasury": "treasury.json",
    # Heartbeat
    "heartbeat": "prana_heartbeat.json",
}

# Subdirectories within state root
STATE_DIRS = {
    "logs": "logs",
    "dojo_sessions": "dojo_sessions",
    "mirror": "mirror",
    "library": "library",
}


# ============================================================================
# PATH RESOLUTION
# ============================================================================


def get_opus_state_service(workspace: Optional[Path] = None):
    """
    Get StateService instance for opus_assistant plugin.

    Returns a StateService configured for:
        .vibe/state/plugins/opus_assistant/

    The returned service handles:
        - Atomic writes with backup rotation
        - JSONL append operations
        - Auto-commit integration with Weaver
        - Heritage migration from .opus_state/

    Args:
        workspace: Project root path. Auto-detected if None.

    Returns:
        StateService instance for opus_assistant
    """
    from vibe_core.state.state_service import get_state_service

    if workspace is None:
        workspace = _find_project_root()

    return get_state_service(workspace, plugin_id="opus_assistant")


def get_opus_state_path(workspace: Optional[Path] = None, filename: str = "") -> Path:
    """
    Get path to an opus_assistant state file.

    Uses StateService's plugin namespacing:
        → .vibe/state/plugins/opus_assistant/{filename}

    Heritage: StateService.load() auto-migrates from .opus_state/{filename}
    on first read.

    Args:
        workspace: Project root path. Auto-detected if None.
        filename: State file name (e.g., "synapses.json")

    Returns:
        Absolute path to the state file

    Example:
        path = get_opus_state_path(workspace, "synapses.json")
        # → /project/.vibe/state/plugins/opus_assistant/synapses.json

        path = get_opus_state_path(workspace, STATE_FILES["intents"])
        # → /project/.vibe/state/plugins/opus_assistant/manas_intents.json
    """
    service = get_opus_state_service(workspace)
    if filename:
        return service.state_root / filename
    return service.state_root


def get_opus_state_dir(workspace: Optional[Path] = None, subdir: str = "") -> Path:
    """
    Get path to an opus_assistant state subdirectory.

    Args:
        workspace: Project root path. Auto-detected if None.
        subdir: Subdirectory name (e.g., "logs", "dojo_sessions")

    Returns:
        Absolute path to the subdirectory (created if needed)

    Example:
        path = get_opus_state_dir(workspace, "logs")
        # → /project/.vibe/state/plugins/opus_assistant/logs/
    """
    service = get_opus_state_service(workspace)
    if subdir:
        dir_path = service.state_root / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    return service.state_root


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def load_opus_state(
    workspace: Optional[Path] = None,
    filename: str = "",
    default: Any = None,
) -> Any:
    """
    Load state from opus_assistant state file.

    Handles heritage migration automatically - if file exists at
    .opus_state/{filename} but not at .vibe/state/plugins/opus_assistant/,
    it will be copied on first read.

    Args:
        workspace: Project root path
        filename: State file name
        default: Default value if file doesn't exist

    Returns:
        Loaded data or default
    """
    service = get_opus_state_service(workspace)
    return service.load(filename, default=default)


def save_opus_state(
    workspace: Optional[Path] = None,
    filename: str = "",
    data: Any = None,
    create_backup: bool = True,
) -> bool:
    """
    Save state to opus_assistant state file.

    Args:
        workspace: Project root path
        filename: State file name
        data: Data to save (will be JSON serialized)
        create_backup: Whether to create backup before overwriting

    Returns:
        True if save succeeded
    """
    service = get_opus_state_service(workspace)
    result = service.save(filename, data, create_backup=create_backup)
    return result.success


def append_opus_state(
    workspace: Optional[Path] = None,
    filename: str = "",
    entry: Dict[str, Any] = None,
) -> bool:
    """
    Append entry to opus_assistant JSONL state file.

    Args:
        workspace: Project root path
        filename: JSONL file name (e.g., "observations.jsonl")
        entry: Dictionary to append

    Returns:
        True if append succeeded
    """
    if entry is None:
        entry = {}
    service = get_opus_state_service(workspace)
    result = service.append(filename, entry)
    return result.success


# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================


def get_legacy_path(workspace: Path, filename: str) -> Path:
    """
    Get legacy .opus_state/ path (for migration checking only).

    DO NOT use this for new code. This is only for:
    - Checking if legacy file exists
    - One-time migration scripts

    Args:
        workspace: Project root
        filename: State file name

    Returns:
        Path to legacy location (may not exist)
    """
    return workspace / ".opus_state" / filename


def has_legacy_state(workspace: Path, filename: str) -> bool:
    """
    Check if legacy .opus_state/ file exists.

    Useful for migration status checks.

    Args:
        workspace: Project root
        filename: State file name

    Returns:
        True if legacy file exists
    """
    return get_legacy_path(workspace, filename).exists()


# ============================================================================
# INTERNAL HELPERS
# ============================================================================


def _find_project_root() -> Path:
    """
    Find project root by searching upward for pyproject.toml or .git.

    Returns:
        Project root path
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return Path.cwd()
