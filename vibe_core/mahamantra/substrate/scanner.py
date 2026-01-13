"""
SCANNER - Auto-Discovery of Mahajana Declarations
==================================================

"vedaham samatitani vartamanani carjuna"
"O Arjuna, I know everything that has happened in the past..."
— Bhagavad Gita 7.26

Krishna KNOWS everything. The Scanner makes explicit what Krishna knows.

IMPLEMENTS: ScannerProtocol (from protocols/substrate/scanner.py)

PURPOSE:
    Scan the entire codebase and find all __mahajana__ declarations.
    Uses the shared ScannerProtocol for consistency.
    Adds Mahajana-specific alias resolution.

USAGE:
    from vibe_core.mahamantra.substrate.scanner import (
        get_scanner,
        scan_all,
        resolve_mahajana,
    )

    # Get scanner singleton
    scanner = get_scanner()
    result = scanner.scan()

    # Or use convenience function
    result = scan_all()

WATERTIGHT: No Any types. All typed explicitly.
NO HARDCODING: Config from ScannerProtocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Final,
    Iterator,
    List,
    Optional,
    Tuple,
)

# Import from substrate protocol - THE SOURCE OF TRUTH
from vibe_core.protocols.substrate.scanner import (
    Declaration,
    DeclarationType,
    FileStatus,
    ScanConfig,
    ScannerProtocol,
    ScanProgress,
    ScanResult,
    ScannedFile,
    extract_declarations,
    get_default_config,
    path_to_module,
)

from vibe_core.mahamantra.substrate.mahajana import Mahajana, Avatara, Quarter
from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# CONSTANTS (Only declaration attribute name - not paths!)
# =============================================================================

DECLARATION_ATTR: Final[str] = "__mahajana_card__"


# =============================================================================
# MAHAJANA ALIAS - Translation Layer (Mahamantra-specific)
# =============================================================================

@dataclass(frozen=True)
class MahajanaAlias:
    """
    Translation layer for Mahajana names.

    Maps Sanskrit names to English/German aliases and back.
    Supports position-based lookup.
    """
    name: str                    # Primary name (Sanskrit)
    position: int                # Position 0-15
    aliases: Tuple[str, ...]     # Alternative names
    description: str = ""        # What this mahajana does

    @property
    def all_names(self) -> Tuple[str, ...]:
        """All names including primary."""
        return (self.name,) + self.aliases


# The 16 Mahajana aliases (12 Mahajanas + 4 Avataras)
MAHAJANA_ALIASES: Final[Tuple[MahajanaAlias, ...]] = (
    # === GENESIS Quarter (0-3) ===
    MahajanaAlias(
        name="prithu",
        position=0,
        aliases=("boot", "bootstrap", "starter", "init"),
        description="System bootstrap and initialization",
    ),
    MahajanaAlias(
        name="brahma",
        position=1,
        aliases=("creator", "schöpfer", "genesis", "create"),
        description="Creation and allocation",
    ),
    MahajanaAlias(
        name="narada",
        position=2,
        aliases=("messenger", "bote", "communicate", "comm"),
        description="Communication and messaging",
    ),
    MahajanaAlias(
        name="shambhu",
        position=3,
        aliases=("destroyer", "zerstörer", "cleanup", "gc"),
        description="Destruction and garbage collection",
    ),

    # === DHARMA Quarter (4-7) ===
    MahajanaAlias(
        name="kumaras",
        position=4,
        aliases=("sages", "weisen", "knowledge", "wisdom"),
        description="Knowledge and wisdom",
    ),
    MahajanaAlias(
        name="manu",
        position=5,
        aliases=("lawgiver", "gesetzgeber", "rules", "policy"),
        description="Laws and policies",
    ),
    MahajanaAlias(
        name="kapila",
        position=6,
        aliases=("analyst", "analytiker", "analyze", "samkhya"),
        description="Analysis and philosophy",
    ),
    MahajanaAlias(
        name="vyasa",
        position=7,
        aliases=("compiler", "compiler", "document", "record"),
        description="Documentation and recording",
    ),

    # === KARMA Quarter (8-11) ===
    MahajanaAlias(
        name="parashurama",
        position=8,
        aliases=("warrior", "krieger", "execute", "action"),
        description="Execution and action",
    ),
    MahajanaAlias(
        name="prahlada",
        position=9,
        aliases=("devotee", "hingabe", "serve", "devotion"),
        description="Service and devotion",
    ),
    MahajanaAlias(
        name="janaka",
        position=10,
        aliases=("king", "könig", "duty", "dharma"),
        description="Duty and responsibility",
    ),
    MahajanaAlias(
        name="bhishma",
        position=11,
        aliases=("patriarch", "patriarch", "commit", "vow"),
        description="Commitment and immutability",
    ),

    # === MOKSHA Quarter (12-15) ===
    MahajanaAlias(
        name="nrisimha",
        position=12,
        aliases=("protector", "beschützer", "guard", "security"),
        description="Protection and security",
    ),
    MahajanaAlias(
        name="bali",
        position=13,
        aliases=("giver", "geber", "yield", "resource"),
        description="Resource management and yielding",
    ),
    MahajanaAlias(
        name="shuka",
        position=14,
        aliases=("seer", "seher", "vision", "insight"),
        description="Vision and insight",
    ),
    MahajanaAlias(
        name="yamaraja",
        position=15,
        aliases=("judge", "richter", "audit", "judgment"),
        description="Judgment and auditing",
    ),
)

# Build lookup tables
_NAME_TO_POSITION: Dict[str, int] = {}
_POSITION_TO_ALIAS: Dict[int, MahajanaAlias] = {}

for _alias in MAHAJANA_ALIASES:
    _POSITION_TO_ALIAS[_alias.position] = _alias
    for _name in _alias.all_names:
        _NAME_TO_POSITION[_name.lower()] = _alias.position


def resolve_mahajana(name_or_position: str | int) -> MahajanaAlias:
    """
    Resolve a mahajana by name, alias, or position.

    Args:
        name_or_position: Can be:
            - Sanskrit name: "brahma"
            - English alias: "creator"
            - German alias: "schöpfer"
            - Position: 1 or "1"

    Returns:
        MahajanaAlias for the resolved mahajana

    Raises:
        ValueError: If not found
    """
    # Try as position number
    if isinstance(name_or_position, int):
        if 0 <= name_or_position <= 15:
            return _POSITION_TO_ALIAS[name_or_position]
        raise ValueError(f"Position must be 0-15, got {name_or_position}")

    # Try as string position
    try:
        pos = int(name_or_position)
        if 0 <= pos <= 15:
            return _POSITION_TO_ALIAS[pos]
    except ValueError:
        pass

    # Try as name/alias
    name_lower = name_or_position.lower()
    if name_lower in _NAME_TO_POSITION:
        pos = _NAME_TO_POSITION[name_lower]
        return _POSITION_TO_ALIAS[pos]

    raise ValueError(f"Unknown mahajana: {name_or_position}")


def get_position(name_or_alias: str) -> int:
    """Get position number from name or alias."""
    return resolve_mahajana(name_or_alias).position


def get_name(position_or_alias: int | str) -> str:
    """Get primary (Sanskrit) name from position or alias."""
    return resolve_mahajana(position_or_alias).name


# =============================================================================
# SIMPLE DECLARATION - For backward compatibility
# =============================================================================

@dataclass
class SimpleDeclaration:
    """
    A simple declaration found in a file.

    For files that don't have full MahajanaCard but have:
    - __mahajana__ = "brahma"
    - __position__ = 1
    """
    file_path: Path
    module_path: str
    mahajana: Optional[str] = None
    position: Optional[int] = None

    @property
    def is_valid(self) -> bool:
        """Check if we have enough info to register."""
        return self.mahajana is not None or self.position is not None

    def resolve_position(self) -> int:
        """Resolve to position number."""
        if self.position is not None:
            return self.position
        if self.mahajana is not None:
            return get_position(self.mahajana)
        raise ValueError("No mahajana or position specified")


# =============================================================================
# MAHAJANA SCANNER - Implements ScannerProtocol
# =============================================================================

class MahajanaScanner:
    """
    Mahajana-aware scanner implementing ScannerProtocol.

    Uses the shared substrate protocol for scanning,
    adds Mahajana-specific alias resolution and tracking.

    NO HARDCODED PATHS - uses ScanConfig.
    """

    def __init__(self, config: Optional[ScanConfig] = None) -> None:
        """Initialize scanner with config."""
        self._config = config or get_default_config()
        self._progress: Optional[ScanProgress] = None
        self._callbacks: List[Callable[[ScanProgress], None]] = []
        self._cached_result: Optional[ScanResult] = None
        self._files_cache: List[ScannedFile] = []

    # =========================================================================
    # ScannerProtocol Implementation
    # =========================================================================

    def get_config(self) -> ScanConfig:
        """Get current scan configuration."""
        return self._config

    def set_config(self, config: ScanConfig) -> None:
        """Set scan configuration."""
        self._config = config
        self._cached_result = None  # Invalidate cache

    def scan(self, path: Optional[str] = None) -> ScanResult:
        """
        Scan for declarations.

        Args:
            path: Path to scan (uses config.base_path if None)

        Returns:
            ScanResult with all findings
        """
        base_path = Path(path) if path else self._get_base_path()
        start_time = datetime.now()

        # Reset state
        self._files_cache = []
        by_mahajana: Dict[str, int] = {}
        by_position: Dict[int, int] = {}
        by_type: Dict[str, int] = {}

        files_total = 0
        files_scanned = 0
        files_owned = 0
        files_orphan = 0
        files_skipped = 0
        files_error = 0
        declarations_found = 0

        # Scan directories from config
        include_dirs = self._config.get("include_dirs", [])
        exclude_patterns = self._config.get("exclude_patterns", [])
        detect_types = self._config.get("detect_declarations", [
            DeclarationType.MAHAJANA.value,
            DeclarationType.POSITION.value,
            DeclarationType.GENESIS.value,
        ])

        for dir_name in include_dirs:
            scan_dir = base_path / dir_name
            if not scan_dir.exists():
                continue

            for file_path in scan_dir.rglob("*.py"):
                files_total += 1

                # Check exclude patterns
                skip = False
                path_str = str(file_path)
                for pattern in exclude_patterns:
                    if pattern in path_str:
                        skip = True
                        break

                if skip:
                    files_skipped += 1
                    self._files_cache.append(ScannedFile(
                        path=str(file_path),
                        relative_path=str(file_path.relative_to(base_path)),
                        module_path=path_to_module(file_path, base_path),
                        status=FileStatus.SKIPPED.value,
                        size_bytes=0,
                        declarations=[],
                        scanned_at=datetime.now().isoformat(),
                    ))
                    continue

                # Scan the file
                scanned = self.scan_file(str(file_path))
                self._files_cache.append(scanned)

                if scanned.get("status") == FileStatus.ERROR.value:
                    files_error += 1
                elif scanned.get("status") == FileStatus.OWNED.value:
                    files_owned += 1
                    files_scanned += 1
                else:
                    files_orphan += 1
                    files_scanned += 1

                # Track declarations
                for decl in scanned.get("declarations", []):
                    declarations_found += 1
                    decl_type = decl.get("type", "")
                    by_type[decl_type] = by_type.get(decl_type, 0) + 1

                    if decl_type == DeclarationType.MAHAJANA.value:
                        mahajana = decl.get("value", "")
                        by_mahajana[mahajana] = by_mahajana.get(mahajana, 0) + 1
                        try:
                            pos = get_position(mahajana)
                            by_position[pos] = by_position.get(pos, 0) + 1
                        except ValueError:
                            pass

                    elif decl_type == DeclarationType.POSITION.value:
                        try:
                            pos = int(decl.get("value", "0"))
                            by_position[pos] = by_position.get(pos, 0) + 1
                            mahajana = get_name(pos)
                            by_mahajana[mahajana] = by_mahajana.get(mahajana, 0) + 1
                        except (ValueError, KeyError):
                            pass

                # Update progress
                self._update_progress(files_total, len(self._files_cache), str(file_path), start_time)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self._cached_result = ScanResult(
            config=self._config,
            files_total=files_total,
            files_scanned=files_scanned,
            files_owned=files_owned,
            files_orphan=files_orphan,
            files_skipped=files_skipped,
            files_error=files_error,
            declarations_found=declarations_found,
            by_mahajana=by_mahajana,
            by_position=by_position,
            by_declaration_type=by_type,
            files=self._files_cache,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            duration_seconds=duration,
        )

        return self._cached_result

    def scan_file(self, file_path: str) -> ScannedFile:
        """
        Scan a single file.

        Uses shared extract_declarations from substrate protocol.
        """
        path = Path(file_path)
        base_path = self._get_base_path()

        try:
            source = path.read_text(encoding="utf-8")
            size_bytes = len(source.encode("utf-8"))
        except Exception as e:
            return ScannedFile(
                path=str(path),
                relative_path=str(path),
                module_path="",
                status=FileStatus.ERROR.value,
                size_bytes=0,
                declarations=[],
                error_message=str(e),
                scanned_at=datetime.now().isoformat(),
            )

        # Use shared extraction utility
        detect_types = self._config.get("detect_declarations", [
            DeclarationType.MAHAJANA.value,
            DeclarationType.POSITION.value,
            DeclarationType.GENESIS.value,
        ])
        declarations = extract_declarations(source, file_path, detect_types)

        status = FileStatus.OWNED.value if declarations else FileStatus.ORPHAN.value

        return ScannedFile(
            path=str(path),
            relative_path=str(path.relative_to(base_path)) if str(path).startswith(str(base_path)) else str(path),
            module_path=path_to_module(path, base_path),
            status=status,
            size_bytes=size_bytes,
            declarations=declarations,
            scanned_at=datetime.now().isoformat(),
        )

    def iter_files(self, path: Optional[str] = None) -> Iterator[ScannedFile]:
        """Iterate over files lazily."""
        if not self._files_cache:
            self.scan(path)
        return iter(self._files_cache)

    def iter_files_lila(
        self,
        path: Optional[str] = None,
        phase: str = "navadvipa",
    ) -> Iterator[ScannedFile]:
        """
        Iterate over files with Chaitanya Lila Boundaries.

        LILA PAGINATION:
            - "navadvipa" phase: yields first 24 files
            - "puri" phase: yields files 24-47
            - "complete": yields files 48+

        This prevents exponential output for large codebases.

        Args:
            path: Path to scan
            phase: "navadvipa" (0-23), "puri" (24-47), or "complete" (full)

        Yields:
            ScannedFile objects, bounded by Lila phase
        """
        from vibe_core.mahamantra.substrate.byte import LILA_LIMIT

        NAVADVIPA_LIMIT = LILA_LIMIT // 2  # 24

        if not self._files_cache:
            self.scan(path)

        if phase == "navadvipa":
            # First 24 files
            for file in self._files_cache[:NAVADVIPA_LIMIT]:
                yield file
        elif phase == "puri":
            # Files 24-47
            for file in self._files_cache[NAVADVIPA_LIMIT:LILA_LIMIT]:
                yield file
        else:
            # Complete - but still in batches for memory
            for i, file in enumerate(self._files_cache):
                yield file
                # Yield control every 24 files (cooperative multitasking)
                if (i + 1) % NAVADVIPA_LIMIT == 0:
                    pass  # Could add async yield here

    def get_by_mahajana(self, mahajana: str) -> List[ScannedFile]:
        """Get all files owned by a mahajana."""
        if not self._files_cache:
            self.scan()
        return [
            f for f in self._files_cache
            if any(
                d.get("type") == DeclarationType.MAHAJANA.value and d.get("value") == mahajana
                for d in f.get("declarations", [])
            )
        ]

    def get_by_position(self, position: int) -> List[ScannedFile]:
        """Get all files at a position."""
        if not self._files_cache:
            self.scan()
        return [
            f for f in self._files_cache
            if any(
                d.get("type") == DeclarationType.POSITION.value and d.get("value") == str(position)
                for d in f.get("declarations", [])
            )
        ]

    def get_orphans(self) -> List[ScannedFile]:
        """Get all files without declarations."""
        if not self._files_cache:
            self.scan()
        return [f for f in self._files_cache if f.get("status") == FileStatus.ORPHAN.value]

    def get_owned(self) -> List[ScannedFile]:
        """Get all files with declarations."""
        if not self._files_cache:
            self.scan()
        return [f for f in self._files_cache if f.get("status") == FileStatus.OWNED.value]

    def get_progress(self) -> Optional[ScanProgress]:
        """Get current scan progress."""
        return self._progress

    def on_progress(self, callback: Callable[[ScanProgress], None]) -> None:
        """Register progress callback."""
        self._callbacks.append(callback)

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _get_base_path(self) -> Path:
        """Get base path from config or default."""
        base = self._config.get("base_path", "")
        if base:
            return Path(base)
        # Default to vibe_core directory
        return Path(__file__).parent.parent.parent

    def _update_progress(
        self,
        total: int,
        processed: int,
        current: str,
        start_time: datetime,
    ) -> None:
        """Update and emit progress."""
        self._progress = ScanProgress(
            files_total=total,
            files_processed=processed,
            current_file=current,
            percent_complete=(processed / total * 100) if total > 0 else 100,
            started_at=start_time.isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        for callback in self._callbacks:
            callback(self._progress)


# =============================================================================
# SINGLETON & CONVENIENCE FUNCTIONS
# =============================================================================

_scanner: Optional[MahajanaScanner] = None


def get_scanner(config: Optional[ScanConfig] = None) -> MahajanaScanner:
    """Get the global scanner instance."""
    global _scanner
    if _scanner is None or config is not None:
        _scanner = MahajanaScanner(config)
    return _scanner


def scan_all(base_path: Optional[Path] = None) -> ScanResult:
    """
    Scan the entire codebase for declarations.

    Convenience function using the global scanner.
    """
    scanner = get_scanner()
    return scanner.scan(str(base_path) if base_path else None)


def get_registry():
    """
    Get the DeclarationRegistry populated with scanned declarations.

    This is the main entry point for the ONE IMPORT pattern.
    """
    from vibe_core.mahamantra.protocols._declaration import DeclarationRegistry
    return DeclarationRegistry()


# =============================================================================
# CLI INTEGRATION - For governance CLI
# =============================================================================

def scan_for_governance() -> Dict:
    """
    Scan for governance CLI integration.

    Returns dict compatible with governance_cli.py expectations.
    """
    result = scan_all()

    return {
        "files_scanned": result.get("files_scanned", 0),
        "declarations_found": result.get("declarations_found", 0),
        "simple_declarations": result.get("declarations_found", 0),  # Same now
        "by_mahajana": result.get("by_mahajana", {}),
        "by_position": result.get("by_position", {}),
        "errors": [],  # Errors now in individual files
        "coverage": result.get("declarations_found", 0) / max(result.get("files_scanned", 1), 1) * 100,
    }


def print_scan_report() -> None:
    """Print a human-readable scan report."""
    result = scan_all()

    print(f"""
{'='*60}
  MAHAJANA DECLARATION SCAN
{'='*60}

  Files total:         {result.get('files_total', 0)}
  Files scanned:       {result.get('files_scanned', 0)}
  Files owned:         {result.get('files_owned', 0)}
  Files orphan:        {result.get('files_orphan', 0)}
  Files skipped:       {result.get('files_skipped', 0)}
  Declarations found:  {result.get('declarations_found', 0)}

  BY MAHAJANA:
""")

    by_mahajana = result.get("by_mahajana", {})
    for pos in range(16):
        alias = _POSITION_TO_ALIAS[pos]
        count = by_mahajana.get(alias.name, 0)
        bar = "#" * min(count, 30)
        print(f"    {pos:2} {alias.name:12} {bar} {count}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Alias (Mahamantra-specific)
    "MahajanaAlias",
    "MAHAJANA_ALIASES",
    "resolve_mahajana",
    "get_position",
    "get_name",
    # Declaration (backward compat)
    "SimpleDeclaration",
    # Scanner (implements ScannerProtocol)
    "MahajanaScanner",
    "get_scanner",
    "scan_all",
    "get_registry",
    # Re-export from substrate (convenience)
    "ScanConfig",
    "ScanResult",
    "ScannedFile",
    "Declaration",
    "ScanProgress",
    "FileStatus",
    "DeclarationType",
    # Governance
    "scan_for_governance",
    "print_scan_report",
    # Constants
    "DECLARATION_ATTR",
    # Lila-bounded iteration (for CLI/external use)
    # Use scanner.iter_files_lila() for paginated results
]
