"""
SCANNER PROTOCOL - Substrate-Level Code Discovery
==================================================

Layer -1: SUBSTRATE (shared foundation)

"vedaham samatitani vartamanani carjuna"
"O Arjuna, I know everything that has happened in the past..."
— Bhagavad Gita 7.26

PURPOSE:
    Universal scanner protocol for code discovery.
    Used by multiple consumers:
    - Mahajanas (Yamaraja/Watchman, Kapila/Analysis, Kumaras/Shuddhi)
    - Discovery Engine (adoption pipeline)
    - Sankirtan (mass DNA injection)
    - Any j+1 or j-1 system that needs scanning

DESIGN:
    - NO HARDCODED PATHS - config injected via protocol
    - AST-based parsing - uses standard library ast
    - Watertight types - no Any
    - Protocol-first - interface before implementation

USAGE:
    from vibe_core.protocols.substrate.scanner import (
        ScannerProtocol,
        ScanConfig,
        ScanResult,
    )

    class MyScannerImpl(ScannerProtocol):
        def scan(self, config: ScanConfig) -> ScanResult:
            ...

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypedDict,
    runtime_checkable,
)

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================


class FileStatus(str, Enum):
    """Status of a scanned file."""

    PENDING = "pending"
    SCANNED = "scanned"
    OWNED = "owned"  # Has mahajana declaration
    INFERRED = "inferred"  # Heuristically identified (Census)
    ORPHAN = "orphan"  # No declaration
    SKIPPED = "skipped"  # Test file, __pycache__, etc.
    ERROR = "error"  # Failed to parse


class DeclarationType(str, Enum):
    """Types of declarations we can detect."""

    MAHAJANA = "mahajana"  # __mahajana__ = "brahma"
    POSITION = "position"  # __position__ = 1
    GENESIS = "genesis"  # __genesis__ = "0x..."
    OWNER = "owner"  # OWNER = Mahajana.BRAHMA
    PROTOCOL_BASE = "protocol_base"  # class FooProtocolBase(WorkerProtocol)


class ScanConfig(TypedDict, total=False):
    """
    Configuration for scanning. WATERTIGHT.

    Injected via protocol - NO HARDCODING.
    """

    base_path: str  # Root path to scan
    include_dirs: List[str]  # Directories to include
    exclude_patterns: List[str]  # Patterns to skip
    file_extensions: List[str]  # Extensions to scan (default: [".py"])
    max_depth: int  # Max recursion depth (0 = unlimited)
    follow_symlinks: bool  # Follow symbolic links
    parse_docstrings: bool  # Extract docstrings
    detect_declarations: List[str]  # DeclarationType values to detect


class Declaration(TypedDict, total=False):
    """
    A detected declaration. WATERTIGHT.
    """

    type: str  # DeclarationType value
    name: str  # Declaration name (e.g., "brahma")
    value: str  # Raw value as string
    line_number: int  # Line in file
    verified: bool  # Passed validation (e.g., parampara % 37 == 0)


class ScannedFile(TypedDict, total=False):
    """
    Result of scanning a single file. WATERTIGHT.
    """

    path: str  # Absolute file path
    relative_path: str  # Path relative to base
    module_path: str  # Python module path
    status: str  # FileStatus value
    size_bytes: int  # File size
    declarations: List[Declaration]  # Found declarations
    error_message: str  # Error if status == ERROR
    scanned_at: str  # ISO timestamp
    inference: Dict[str, object]  # Heuristic analysis results (identity, score)


class ScanResult(TypedDict, total=False):
    """
    Result of a full scan operation. WATERTIGHT.
    """

    config: ScanConfig  # Config used
    files_total: int  # Total files found
    files_scanned: int  # Successfully scanned
    files_owned: int  # With declarations
    files_inferred: int  # Heuristically identified
    files_orphan: int  # Without declarations
    files_skipped: int  # Skipped (tests, etc.)
    files_error: int  # Failed to parse
    declarations_found: int  # Total declarations
    by_mahajana: Dict[str, int]  # Count per mahajana
    by_position: Dict[int, int]  # Count per position
    by_declaration_type: Dict[str, int]  # Count per type
    files: List[ScannedFile]  # All scanned files
    started_at: str  # ISO timestamp
    completed_at: str  # ISO timestamp
    duration_seconds: float  # Scan duration


class ScanProgress(TypedDict, total=False):
    """
    Progress during scanning. WATERTIGHT.
    """

    files_total: int
    files_processed: int
    current_file: str
    percent_complete: float
    started_at: str
    updated_at: str


# =============================================================================
# DEFAULT CONFIG (Can be overridden via protocol)
# =============================================================================


def get_default_config() -> ScanConfig:
    """
    Get default scan configuration.

    IMPORTANT: This is a FALLBACK. Proper config should come
    from Shuka/Phoenix config system.
    """
    return ScanConfig(
        base_path="",  # Must be set by caller
        include_dirs=[
            "protocols",
            "mahamantra",
            "naga",
            "plugins",
            "cartridges",
            "services",
            "cli",
            "ouroboros",
            "shuddhi",
            "phoenix",
            "runtime",
            "state",
        ],
        exclude_patterns=[
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "test_",
            "_test.py",
            "tests/",
            "conftest.py",
        ],
        file_extensions=[".py"],
        max_depth=0,  # Unlimited
        follow_symlinks=False,
        parse_docstrings=False,
        detect_declarations=[
            DeclarationType.MAHAJANA.value,
            DeclarationType.POSITION.value,
            DeclarationType.GENESIS.value,
        ],
    )


# =============================================================================
# AST EXTRACTION (Shared utility - no hardcoding)
# =============================================================================


def extract_declarations(
    source: str,
    file_path: str,
    declaration_types: List[str],
) -> List[Declaration]:
    """
    Extract declarations from Python source using AST.

    Args:
        source: Python source code
        file_path: Path for error messages
        declaration_types: Which declarations to look for

    Returns:
        List of found declarations
    """
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    declarations: List[Declaration] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    decl = _extract_assignment(target, node, declaration_types)
                    if decl:
                        declarations.append(decl)

    return declarations


def _extract_assignment(
    target: ast.Name,
    node: ast.Assign,
    declaration_types: List[str],
) -> Optional[Declaration]:
    """Extract a single assignment declaration."""
    name = target.id

    # __mahajana__ = "brahma"
    if name == "__mahajana__" and DeclarationType.MAHAJANA.value in declaration_types:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
            # Skip templates like "{mahajana}"
            if "{" not in value and value:
                return Declaration(
                    type=DeclarationType.MAHAJANA.value,
                    name="mahajana",
                    value=value,
                    line_number=node.lineno,
                    verified=True,
                )

    # __position__ = 1
    elif name == "__position__" and DeclarationType.POSITION.value in declaration_types:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
            return Declaration(
                type=DeclarationType.POSITION.value,
                name="position",
                value=str(node.value.value),
                line_number=node.lineno,
                verified=0 <= node.value.value <= 15,
            )

    # __genesis__ = "0x..."
    elif name == "__genesis__" and DeclarationType.GENESIS.value in declaration_types:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
            # Verify parampara % 37 == 0
            verified = False
            try:
                int_val = int(value, 16)
                verified = int_val % 37 == 0
            except ValueError as _exc:
                logger.exception("Unexpected error: %s", _exc)
            return Declaration(
                type=DeclarationType.GENESIS.value,
                name="genesis",
                value=value,
                line_number=node.lineno,
                verified=verified,
            )

    return None


def path_to_module(path: Path, base_path: Path) -> str:
    """
    Convert file path to Python module path.

    Args:
        path: File path
        base_path: Base path to make relative to

    Returns:
        Module path like "vibe_core.protocols.mahajanas.brahma"
    """
    try:
        rel_path = path.relative_to(base_path)
        parts = rel_path.parts

        # Remove .py extension
        if parts[-1].endswith(".py"):
            parts = parts[:-1] + (parts[-1][:-3],)

        # Find vibe_core in path
        try:
            idx = parts.index("vibe_core")
            parts = parts[idx:]
        except ValueError as _exc:
            logger.exception("Unexpected error: %s", _exc)

        return ".".join(parts)
    except ValueError:
        return str(path)


# =============================================================================
# SCANNER PROTOCOL
# =============================================================================


@runtime_checkable
class ScannerProtocol(Protocol):
    """
    Universal code scanning protocol.

    Layer -1 SUBSTRATE - used by multiple consumers.

    Consumers:
        - Mahajanas (Yamaraja, Kapila, Kumaras)
        - DiscoveryEngine
        - Sankirtan
        - Any j+1 or j-1 system

    WATERTIGHT - no Any types!
    """

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_config(self) -> ScanConfig:
        """
        Get current scan configuration.

        Should come from Shuka/Phoenix config, not hardcoded.
        """
        ...

    def set_config(self, config: ScanConfig) -> None:
        """Set scan configuration."""
        ...

    # =========================================================================
    # Scanning
    # =========================================================================

    def scan(self, path: Optional[str] = None) -> ScanResult:
        """
        Scan for declarations.

        Args:
            path: Path to scan (uses config.base_path if None)

        Returns:
            ScanResult with all findings
        """
        ...

    def scan_file(self, file_path: str) -> ScannedFile:
        """
        Scan a single file.

        Args:
            file_path: Path to Python file

        Returns:
            ScannedFile with declarations
        """
        ...

    def iter_files(
        self,
        path: Optional[str] = None,
    ) -> Iterator[ScannedFile]:
        """
        Iterate over files lazily.

        For large codebases where loading all at once is too much.
        """
        ...

    # =========================================================================
    # Queries
    # =========================================================================

    def get_by_mahajana(self, mahajana: str) -> List[ScannedFile]:
        """Get all files owned by a mahajana."""
        ...

    def get_by_position(self, position: int) -> List[ScannedFile]:
        """Get all files at a position."""
        ...

    def get_orphans(self) -> List[ScannedFile]:
        """Get all files without declarations."""
        ...

    def get_owned(self) -> List[ScannedFile]:
        """Get all files with declarations."""
        ...

    # =========================================================================
    # Progress (for long scans)
    # =========================================================================

    def get_progress(self) -> Optional[ScanProgress]:
        """Get current scan progress (if scanning)."""
        ...

    def on_progress(
        self,
        callback: Callable[[ScanProgress], None],
    ) -> None:
        """Register progress callback."""
        ...


# =============================================================================
# NULL SCANNER (For testing)
# =============================================================================


class NullScanner:
    """
    Null implementation for testing.
    Returns empty results.
    """

    def __init__(self) -> None:
        self._config = get_default_config()
        self._progress: Optional[ScanProgress] = None
        self._callbacks: List[Callable[[ScanProgress], None]] = []

    def get_config(self) -> ScanConfig:
        return self._config

    def set_config(self, config: ScanConfig) -> None:
        self._config = config

    def scan(self, path: Optional[str] = None) -> ScanResult:
        return ScanResult(
            config=self._config,
            files_total=0,
            files_scanned=0,
            files_owned=0,
            files_orphan=0,
            files_skipped=0,
            files_error=0,
            declarations_found=0,
            by_mahajana={},
            by_position={},
            by_declaration_type={},
            files=[],
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            duration_seconds=0.0,
        )

    def scan_file(self, file_path: str) -> ScannedFile:
        return ScannedFile(
            path=file_path,
            relative_path=file_path,
            module_path="",
            status=FileStatus.SKIPPED.value,
            size_bytes=0,
            declarations=[],
            scanned_at=datetime.now().isoformat(),
        )

    def iter_files(
        self,
        path: Optional[str] = None,
    ) -> Iterator[ScannedFile]:
        return iter([])

    def get_by_mahajana(self, mahajana: str) -> List[ScannedFile]:
        return []

    def get_by_position(self, position: int) -> List[ScannedFile]:
        return []

    def get_orphans(self) -> List[ScannedFile]:
        return []

    def get_owned(self) -> List[ScannedFile]:
        return []

    def get_progress(self) -> Optional[ScanProgress]:
        return self._progress

    def on_progress(
        self,
        callback: Callable[[ScanProgress], None],
    ) -> None:
        self._callbacks.append(callback)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "FileStatus",
    "DeclarationType",
    # Types (WATERTIGHT)
    "ScanConfig",
    "Declaration",
    "ScannedFile",
    "ScanResult",
    "ScanProgress",
    # Functions
    "get_default_config",
    "extract_declarations",
    "path_to_module",
    # Protocol
    "ScannerProtocol",
    # Null Implementation
    "NullScanner",
]
