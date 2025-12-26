"""
OPUS-308: Manifestation Protocol Interfaces

This module defines the CONTRACTS for the Markdown Manifestation system.
NO IMPLEMENTATIONS HERE - only Protocol definitions.

Philosophy (from OPUS-151 & GAD-000):
    "The Markdown files are not the map. They are the territory."
    "Is this designed for an AI to operate on behalf of a human?"

    Manifestations are not "outputs" - they are declarations of truth
    into the operating reality. The Operator (human or AI) EXISTS in
    this reality, not outside looking in.

Architecture:
    Layer 3: SemanticUIProtocol     (plugins use THIS)
    Layer 2: ManifestationProtocol  (structure & I/O)
    Layer 1: KernelIOService        (EXISTS - no changes needed)

Key Concepts:
    - HOLON: Each manifestation is whole in itself AND part of greater whole
    - SKIN: The bidirectional membrane between entity and operator
    - @LIVE/@HUMAN/@AI: Section ownership determines who can write

The Schema dictates the Parser. See: docs/architecture/OPUS/308-SCHEMAS.yaml
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

# =============================================================================
# ENUMS
# =============================================================================


class SectionOwnership(Enum):
    """Who owns a section and can write to it."""

    LIVE = "live"  # System writes, overwrites on each render
    HUMAN = "human"  # User writes, system preserves EXACTLY
    AI = "ai"  # AI writes, user can override
    SHARED = "shared"  # Both can write (requires merge strategy)


class ManifestationType(Enum):
    """Direction of data flow for a manifestation."""

    READONLY = "readonly"  # System → User only
    BIDIRECTIONAL = "bidirectional"  # System ↔ User
    SNAPSHOT = "snapshot"  # Point-in-time capture


class ManifestationState(Enum):
    """Lifecycle state of a manifestation."""

    DORMANT = "dormant"  # Entity exists but not manifested
    LIVE = "live"  # File exists, actively updated
    PAUSED = "paused"  # File exists, shows "PAUSED" status
    ARCHIVED = "archived"  # Moved to .archive/, immutable
    DELETED = "deleted"  # Gone (or tombstone marker)


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class Section:
    """A parsed section from a manifestation."""

    id: str
    owner: SectionOwnership
    content: str
    title: Optional[str] = None


@dataclass
class ManifestHeader:
    """The identity header of a manifested document."""

    entity_id: str
    schema: str
    version: str
    manifest_type: ManifestationType
    generated: str  # ISO timestamp


@dataclass
class ManifestationConfig:
    """Configuration for how an entity wants to manifest."""

    output: str  # Filename: "ENVOY.md"
    location: str  # "root" | ".vibe" | custom path
    manifest_type: ManifestationType
    schema: str  # Schema name from 308-SCHEMAS.yaml


@dataclass
class Command:
    """A parsed command from a @HUMAN section."""

    raw: str  # Original text
    action: str  # Parsed action (SET, RESTART, etc.)
    args: Dict[str, Any]  # Parsed arguments
    timestamp: Optional[str] = None


# =============================================================================
# LAYER 2: STRUCTURE PROTOCOL
# =============================================================================


class ManifestationProtocol(Protocol):
    """
    LAYER 2: STRUCTURE & I/O

    Handles the 'Skin'. Knows NOTHING about what Agents are.
    Uses schema definitions, NOT regex hacks.

    Responsibilities:
    - Spawn new manifestations from schema
    - Parse sections respecting ownership
    - Merge new LIVE content with preserved HUMAN content
    - Resilient parsing (never lose data)
    """

    def spawn(
        self,
        path: Path,
        schema: str,
        initial_state: Dict[str, Any],
    ) -> bool:
        """
        Create a new manifestation from a schema.

        Args:
            path: Where to create the file
            schema: Schema name from 308-SCHEMAS.yaml
            initial_state: Data for initial @LIVE sections

        Returns:
            True if created successfully
        """
        ...

    def read_structure(self, path: Path) -> Dict[str, Section]:
        """
        Parse a manifestation into its sections.

        Uses RESILIENT parsing:
        - Missing close tags → section ends at next header or EOF
        - Duplicate IDs → preserve in _recovery section
        - Never lose data

        Returns:
            Dict mapping section_id to Section
        """
        ...

    def read_header(self, path: Path) -> Optional[ManifestHeader]:
        """
        Extract the manifest header from a file.

        Returns None if file doesn't have a valid manifest header.
        """
        ...

    def update_live_sections(
        self,
        path: Path,
        sections: Dict[str, str],
    ) -> bool:
        """
        THE ATOMIC MERGE - The Magic.

        Takes new @LIVE data, merges with existing @HUMAN data on disk.

        Process:
        1. Read existing file
        2. Extract all @HUMAN sections (preserve exactly)
        3. Render new @LIVE sections
        4. Merge: new @LIVE + preserved @HUMAN
        5. Write atomically via KernelIOService

        Args:
            path: The manifestation file
            sections: Dict of section_id → new content for @LIVE sections

        Returns:
            True if updated successfully
        """
        ...

    def annotate_error(
        self,
        path: Path,
        section_id: str,
        line_content: str,
        error_message: str,
    ) -> bool:
        """
        THE RED PEN - In-file error annotation.

        "Invisible = Doesn't Exist" (GAD-000)

        When parsing @HUMAN sections, errors MUST be visible IN THE FILE.
        This method inserts an @ERROR annotation after the offending line.

        Example:
            Before: "- SET mode=turbo"
            After:  "- SET mode=turbo\n<!-- @ERROR: Unknown mode 'turbo' -->"

        Args:
            path: The manifestation file
            section_id: Which section contains the error
            line_content: The line that caused the error
            error_message: Human-readable error explanation

        Returns:
            True if annotation was written
        """
        ...

    def annotate_success(
        self,
        path: Path,
        section_id: str,
        line_content: str,
        result_message: str,
    ) -> bool:
        """
        THE GREEN PEN - In-file success annotation.

        Confirms that a user command was executed successfully.

        Example:
            Before: "- RESTART agent.herald"
            After:  "- RESTART agent.herald\n<!-- @OK: Executed at 12:34:56 -->"

        Args:
            path: The manifestation file
            section_id: Which section contains the command
            line_content: The command that was executed
            result_message: Success confirmation message

        Returns:
            True if annotation was written
        """
        ...

    def render_section_error(
        self,
        section_id: str,
        error: Exception,
        trace_id: str,
    ) -> str:
        """
        Generate error placeholder for a crashed section.

        Section Crash Isolation: one section's failure must not
        destroy the entire file. This generates a visible error
        placeholder while other sections render normally.

        Args:
            section_id: Which section crashed
            error: The exception that occurred
            trace_id: ID for log correlation

        Returns:
            Markdown content showing the error placeholder
        """
        ...


# =============================================================================
# LAYER 2: INDEX PROTOCOL
# =============================================================================


class ManifestIndexProtocol(Protocol):
    """
    In-memory index of all manifestations.

    Solves the O(n) I/O problem:
    - Scans ONCE at boot
    - Updates via File Watcher events
    - Lookups are O(1)

    The filesystem is the Source of Truth.
    The index is the Access Pattern.
    """

    def rebuild(self) -> None:
        """
        Full scan of all manifestation locations.
        ONLY called at boot or explicit refresh.
        """
        ...

    def find(self, entity_id: str) -> Optional[Path]:
        """O(1) lookup by entity ID."""
        ...

    def find_by_path(self, path: Path) -> Optional[str]:
        """O(1) reverse lookup: path → entity_id."""
        ...

    def all_manifestations(self) -> List[Path]:
        """Return all known manifestation paths."""
        ...

    # File watcher event handlers
    def on_file_created(self, path: Path) -> None:
        """Update index when new file detected."""
        ...

    def on_file_deleted(self, path: Path) -> None:
        """Update index when file removed."""
        ...

    def on_file_moved(self, old_path: Path, new_path: Path) -> None:
        """Update index when file moved."""
        ...


# =============================================================================
# LAYER 2: CHANGE DETECTOR PROTOCOL
# =============================================================================


class ChangeDetectorProtocol(Protocol):
    """
    Hash-based change detection to prevent infinite loops.

    The Loop of Death:
    1. System updates @LIVE status
    2. File Watcher: "Change detected!"
    3. System reads for @HUMAN input
    4. System re-renders for consistency
    5. File Watcher: "Change detected!"
    6. GOTO 2

    Solution: Only trigger logic if @HUMAN sections actually changed.
    """

    def should_process(self, path: Path) -> bool:
        """
        Check if file change warrants processing.

        Returns True only if @HUMAN sections changed.
        Returns False if only @LIVE sections changed (our own write).
        """
        ...

    def update_hash(self, path: Path, human_content: str) -> None:
        """Update stored hash after processing user changes."""
        ...


# =============================================================================
# LAYER 3: SEMANTIC PROTOCOL
# =============================================================================


class SemanticUIProtocol(Protocol):
    """
    LAYER 3: SEMANTIC

    The 'Brain' interacting with the Skin.
    THIS is what plugins use. Nothing below.

    High-level operations that don't know about markdown structure.
    """

    # Discovery (uses ManifestIndex - O(1))
    def find_manifestation(self, entity_id: str) -> Optional[Path]:
        """Find where an entity is manifested."""
        ...

    def is_manifested(self, entity_id: str) -> bool:
        """Check if an entity has a manifestation."""
        ...

    # Status Operations
    def set_status(self, entity_id: str, status: str) -> None:
        """Update the status section of an entity's manifestation."""
        ...

    def get_status(self, entity_id: str) -> Optional[str]:
        """Read the current status of an entity."""
        ...

    # Command Queue Operations
    def get_user_commands(self, entity_id: str) -> List[Command]:
        """
        Pop and return all pending user commands.

        Reads @HUMAN command section, parses commands,
        returns them, and clears the section.
        """
        ...

    def record_execution(
        self,
        entity_id: str,
        command: Command,
        result: str,
    ) -> None:
        """Record that a command was executed."""
        ...

    # Lifecycle Operations
    def spawn(
        self,
        entity_id: str,
        config: ManifestationConfig,
        initial_state: Dict[str, Any],
    ) -> Path:
        """
        Spawn a new manifestation for an entity.

        This is how plugins REQUEST manifestation.
        They don't write files directly.
        """
        ...

    def archive(self, entity_id: str) -> None:
        """Move a manifestation to .archive/ with timestamp."""
        ...

    def delete(self, entity_id: str) -> None:
        """Remove a manifestation entirely."""
        ...


# =============================================================================
# PLUGIN MANIFESTATION PROTOCOL
# =============================================================================


@dataclass
class ManifestationDeclaration:
    """
    How a plugin declares its manifestation in manifest.json.

    Example in manifest.json:
        "manifestation": {
            "output": "ENVOY.md",
            "schema": "agent_standard",
            "frequency": "tick"
        }
    """

    output: str  # Filename: "ENVOY.md"
    schema: str  # Schema from 308-SCHEMAS.yaml
    frequency: str = "tick"  # "tick" | "on_change" | "manual"
    location: str = "root"  # "root" | ".vibe" | custom path


class Manifestable(Protocol):
    """
    THE PLUGIN CONTRACT FOR MANIFESTATION.

    Any plugin that wants to manifest as Markdown MUST implement this.
    The plugin provides DATA, the Kernel renders the Markdown.

    This is INVERSION OF CONTROL:
    - OLD: Plugin writes its own Markdown (chaos)
    - NEW: Plugin provides data, Kernel manifests (order)

    Usage in plugin:
        class EnvoyPlugin(KernelPlugin, Manifestable):
            def get_manifestation_data(self) -> Dict[str, Any]:
                return {
                    "status": {"state": "RUNNING", "circuits": 20},
                    "capabilities": self.list_circuits(),
                }
    """

    def get_manifestation_data(self) -> Dict[str, Any]:
        """
        Return data for @LIVE sections.

        Keys should match section IDs from the schema.
        Values are the raw data - ManifestationService handles formatting.

        Returns:
            Dict mapping section_id to section data
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "SectionOwnership",
    "ManifestationType",
    "ManifestationState",
    # Data Structures
    "Section",
    "ManifestHeader",
    "ManifestationConfig",
    "ManifestationDeclaration",
    "Command",
    # Protocols
    "ManifestationProtocol",
    "ManifestIndexProtocol",
    "ChangeDetectorProtocol",
    "SemanticUIProtocol",
    "Manifestable",
]
