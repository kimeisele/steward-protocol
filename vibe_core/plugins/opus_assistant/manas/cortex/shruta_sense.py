"""
OPUS-156: ShrutaSense - Das Hörende System

Sanskrit: श्रुत (Shruta) = "That which is heard"
Sanskrit: श्रुति (Shruti) = Sacred texts "heard" by the Rishis

This cortex module gives MANAS the ability to HEAR the filesystem.
Unlike other senses that are polled, ShrutaSense maintains awareness
of filesystem vibrations (changes) between perception cycles.

"Am Anfang war Dunkelheit. Brahma HÖRTE bevor er SAH."
"At the beginning was darkness. Brahma HEARD before he SAW."

Capabilities:
1. start_listening()    - Begin monitoring filesystem paths
2. perceive()           - Get buffered vibrations since last call
3. get_vibrations()     - Get recent vibration history
4. get_hot_paths()      - Find paths with frequent changes
5. calculate_resonance()- Get layer resonance for a path

The 6th Jnanendriya - Foundation of all perception.
Sound (Shabda) precedes Form (Rupa).

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
    required: true
    rationale: "The 6th Jnanendriya - hearing filesystem vibrations"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
    rationale: "Base class for all senses"

wiring:
  - pattern: "class ShrutaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
  - pattern: "class Vibration"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py
  - pattern: "def start_listening"
    in: vibe_core/plugins/opus_assistant/manas/cortex/shruta_sense.py

tests:
  - tests/manas/cortex/test_shruta_sense.py
-->
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .base import BaseSense

logger = logging.getLogger("MANAS.Cortex.ShrutaSense")


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class Vibration:
    """
    A filesystem vibration (change event).

    Sanskrit: स्पन्द (Spanda) = Vibration/Pulsation

    Each change in the filesystem creates a vibration that
    ShrutaSense detects and records.
    """

    event_type: str  # "created", "modified", "deleted"
    path: Path
    timestamp: float
    is_directory: bool = False
    resonance_layer: Optional[str] = None  # KERNEL, COGNITION, etc.
    file_hash: Optional[str] = None  # For detecting actual content changes

    def __str__(self) -> str:
        emoji = {
            "created": "✨",
            "modified": "📝",
            "deleted": "🗑️",
        }.get(self.event_type, "👂")
        layer = f"[{self.resonance_layer}]" if self.resonance_layer else ""
        return f"{emoji} {self.event_type}: {self.path.name} {layer}"


@dataclass
class FileSnapshot:
    """Snapshot of a file's state for change detection."""

    path: Path
    mtime: float
    size: int
    exists: bool
    content_hash: Optional[str] = None


@dataclass
class ShrutaPerception:
    """Result of ShrutaSense perception."""

    vibrations: List[Vibration]
    total_count: int
    by_type: Dict[str, int]
    by_layer: Dict[str, int]
    hot_paths: List[tuple]  # (path, change_count)
    is_listening: bool


# =============================================================================
# ShrutaSense Implementation
# =============================================================================


class ShrutaSense(BaseSense):
    """
    The 6th Jnanendriya - Hearing filesystem vibrations.

    Unlike watchdog-based implementations, this uses polling
    with snapshot comparison. This is more portable and doesn't
    require additional dependencies.

    Philosophy:
    - Brahma heard "tapa" in darkness before seeing creation
    - ShrutaSense hears filesystem changes before MANAS sees them
    - Sound (Shabda) is the foundation of perception
    """

    name = "shruta_sense"

    # Paths to ignore
    IGNORED_PATTERNS: Set[str] = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".opus_state",
        ".venv",
        "node_modules",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
    }

    # Default poll interval (seconds)
    DEFAULT_POLL_INTERVAL = 2.0

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)

        # Monitoring state
        self._is_listening = False
        self._poll_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Snapshot storage: path -> FileSnapshot
        self._snapshots: Dict[str, FileSnapshot] = {}

        # Vibration buffer (recent changes)
        self._vibration_buffer: deque = deque(maxlen=1000)

        # Change counters for hot path detection
        self._change_counts: Counter = Counter()

        # External handlers
        self._handlers: List[Callable[[Vibration], None]] = []

        # Watch paths
        self._watch_paths: List[Path] = []

        # Poll interval
        self._poll_interval = self._config.get("poll_interval", self.DEFAULT_POLL_INTERVAL)

        logger.info("👂 ShrutaSense initialized")

    # =========================================================================
    # Public API
    # =========================================================================

    def start_listening(
        self,
        paths: Optional[List[Path]] = None,
        poll_interval: Optional[float] = None,
    ) -> None:
        """
        Start listening to filesystem vibrations.

        Args:
            paths: Paths to monitor (default: vibe_core/, tests/, docs/)
            poll_interval: Seconds between polls (default: 2.0)
        """
        if self._is_listening:
            logger.warning("ShrutaSense already listening")
            return

        # Set watch paths
        self._watch_paths = paths or [
            self._workspace / "vibe_core",
            self._workspace / "tests",
            self._workspace / "docs",
        ]

        if poll_interval:
            self._poll_interval = poll_interval

        # Take initial snapshot
        self._take_snapshot()

        # Start polling thread
        self._stop_event.clear()
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="ShrutaSense-Poller",
        )
        self._poll_thread.start()
        self._is_listening = True

        watched = ", ".join(str(p.name) for p in self._watch_paths if p.exists())
        logger.info(f"🕉️ ShrutaSense listening to: {watched}")

    def stop_listening(self) -> None:
        """Stop listening to filesystem vibrations."""
        if not self._is_listening:
            return

        self._stop_event.set()
        if self._poll_thread:
            self._poll_thread.join(timeout=5.0)
            self._poll_thread = None

        self._is_listening = False
        logger.info("🔇 ShrutaSense stopped listening")

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> ShrutaPerception:
        """
        Main perception method - returns buffered vibrations.

        This clears the buffer after reading, so each perceive()
        returns only NEW vibrations since last call.
        """
        # Get and clear buffer
        vibrations = list(self._vibration_buffer)
        self._vibration_buffer.clear()

        # Group by type
        by_type: Dict[str, int] = Counter()
        by_layer: Dict[str, int] = Counter()

        for v in vibrations:
            by_type[v.event_type] += 1
            if v.resonance_layer:
                by_layer[v.resonance_layer] += 1

        # Get hot paths
        hot_paths = self._change_counts.most_common(10)

        return ShrutaPerception(
            vibrations=vibrations,
            total_count=len(vibrations),
            by_type=dict(by_type),
            by_layer=dict(by_layer),
            hot_paths=hot_paths,
            is_listening=self._is_listening,
        )

    def get_vibrations(self, limit: int = 100) -> List[Vibration]:
        """Get recent vibrations without clearing buffer."""
        return list(self._vibration_buffer)[-limit:]

    def get_hot_paths(self, limit: int = 10) -> List[tuple]:
        """Get paths with most frequent changes."""
        return self._change_counts.most_common(limit)

    def add_handler(self, handler: Callable[[Vibration], None]) -> None:
        """Add a vibration handler callback."""
        self._handlers.append(handler)

    def remove_handler(self, handler: Callable[[Vibration], None]) -> None:
        """Remove a vibration handler callback."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    # =========================================================================
    # Resonance Calculation
    # =========================================================================

    def calculate_resonance(self, path: Path) -> tuple:
        """
        Calculate the resonance layer for a path.

        Returns:
            (layer_name, varga_value) or (None, None) if unknown
        """
        try:
            from vibe_core.plugins.opus_assistant.manas.akshara import (
                VARGA_LAYERS,
                map_path_to_varga,
            )

            varga = map_path_to_varga(str(path))
            layer = VARGA_LAYERS.get(varga, "UNKNOWN")
            return layer, varga.value
        except ImportError:
            return None, None

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _poll_loop(self) -> None:
        """Background polling loop."""
        while not self._stop_event.is_set():
            try:
                self._detect_changes()
            except Exception as e:
                logger.error(f"ShrutaSense poll error: {e}")

            self._stop_event.wait(self._poll_interval)

    def _take_snapshot(self) -> None:
        """Take initial filesystem snapshot."""
        self._snapshots.clear()

        for watch_path in self._watch_paths:
            if not watch_path.exists():
                continue

            for root, dirs, files in os.walk(watch_path):
                # Filter ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore(d)]

                for filename in files:
                    if self._should_ignore(filename):
                        continue

                    filepath = Path(root) / filename
                    self._snapshot_file(filepath)

    def _snapshot_file(self, filepath: Path) -> Optional[FileSnapshot]:
        """Take snapshot of a single file."""
        try:
            stat = filepath.stat()
            snapshot = FileSnapshot(
                path=filepath,
                mtime=stat.st_mtime,
                size=stat.st_size,
                exists=True,
            )
            self._snapshots[str(filepath)] = snapshot
            return snapshot
        except (OSError, IOError):
            return None

    def _detect_changes(self) -> None:
        """Detect filesystem changes since last snapshot."""
        current_files: Set[str] = set()

        for watch_path in self._watch_paths:
            if not watch_path.exists():
                continue

            for root, dirs, files in os.walk(watch_path):
                # Filter ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore(d)]

                for filename in files:
                    if self._should_ignore(filename):
                        continue

                    filepath = Path(root) / filename
                    filepath_str = str(filepath)
                    current_files.add(filepath_str)

                    try:
                        stat = filepath.stat()
                    except (OSError, IOError):
                        continue

                    old_snapshot = self._snapshots.get(filepath_str)

                    if old_snapshot is None:
                        # New file
                        self._emit_vibration("created", filepath)
                        self._snapshot_file(filepath)

                    elif stat.st_mtime > old_snapshot.mtime:
                        # Modified file
                        self._emit_vibration("modified", filepath)
                        self._snapshot_file(filepath)

        # Detect deletions
        deleted_paths = set(self._snapshots.keys()) - current_files
        for deleted_path in deleted_paths:
            self._emit_vibration("deleted", Path(deleted_path))
            del self._snapshots[deleted_path]

    def _emit_vibration(self, event_type: str, path: Path) -> None:
        """Create and emit a vibration."""
        # Calculate resonance
        layer, _ = self.calculate_resonance(path)

        vibration = Vibration(
            event_type=event_type,
            path=path,
            timestamp=time.time(),
            is_directory=path.is_dir() if path.exists() else False,
            resonance_layer=layer,
        )

        # Buffer it
        self._vibration_buffer.append(vibration)

        # Update counters
        self._change_counts[str(path)] += 1

        # Notify handlers
        for handler in self._handlers:
            try:
                handler(vibration)
            except Exception as e:
                logger.error(f"Vibration handler error: {e}")

        # Log
        logger.debug(str(vibration))

    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored."""
        for pattern in self.IGNORED_PATTERNS:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False

    # =========================================================================
    # Auto-Discovery Integration (Future)
    # =========================================================================

    def on_python_file_created(self, vibration: Vibration) -> None:
        """
        Handle new Python file creation.

        This is a hook for auto-discovery integration.
        When a new .py file is created, we can:
        1. Trigger Akasha scan
        2. Update knowledge graph
        3. Generate discovery intent
        """
        if not str(vibration.path).endswith(".py"):
            return

        logger.info(f"✨ New Python module detected: {vibration.path.name}")

        # Future: Trigger Akasha scan
        # Future: Generate discovery intent
        # Future: Auto-register if it's a plugin

    def register_auto_discovery(self) -> None:
        """Register auto-discovery handler."""
        self.add_handler(self.on_python_file_created)
        logger.info("🔌 Auto-discovery handler registered")


# =============================================================================
# Convenience Functions
# =============================================================================

_global_shruta: Optional[ShrutaSense] = None


def get_shruta_sense(workspace: Optional[Path] = None) -> ShrutaSense:
    """Get or create global ShrutaSense instance."""
    global _global_shruta
    if _global_shruta is None:
        _global_shruta = ShrutaSense(workspace=workspace)
    return _global_shruta


def start_listening(paths: Optional[List[Path]] = None) -> ShrutaSense:
    """Convenience function to start listening."""
    sense = get_shruta_sense()
    sense.start_listening(paths)
    return sense
