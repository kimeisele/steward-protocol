"""
PROTOCOL DISCOVERY - The Lotus ACTIVELY Seeks
==============================================

"The Lotus must be ATTRACTIVE like Krishna itself -
it DRAWS protocols in through coherence."

NOT passive waiting. NOT manual wiring.
The Lotus SCANS, FINDS, and ATTRACTS wild protocols.

ZERO MANUAL MAPPING:
    88% entropy (Kali Yuga) cannot be manually mapped.
    The Lotus must AUTO-DISCOVER and AUTO-ADOPT.
    Only the Mahamantra filter decides.

THE DISCOVERY ENGINE:
    1. SCAN - Uses ScannerProtocol (SUBSTRATE)
    2. FILTER - Exclude already-owned, tests, __pycache__
    3. ANALYZE - Run each through analyze()
    4. ADOPT - Run through adopt_full()
    5. REPORT - Track progress, mercy cases, failures

"What is the map?" - The Mahamantra IS the map.
All 16 positions are routing destinations.

SUBSTRATE INTEGRATION:
    Discovery uses ScannerProtocol from substrate.
    NO HARDCODED PATHS. Config-driven via ScanConfig.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
    TypedDict,
    Iterator,
    Set,
    Callable,
)

from vibe_core.protocols.mahajanas.adoption import (
    AdoptionStatus,
    AdoptionDecision,
    ProtocolAnalysis,
    AdoptionResult,
    FullAdoptionResult,
    AttractionReport,
    adopt_full,
    analyze,
    get_pipeline,
)
from vibe_core.protocols.mahajanas.router import Mahajana

# === SUBSTRATE SCANNER PROTOCOL ===
from vibe_core.protocols.substrate.scanner import (
    ScannerProtocol,
    ScanConfig,
    ScanResult,
    ScannedFile,
    FileStatus,
    DeclarationType,
    extract_declarations,
    get_default_config,
)

import logging
logger = logging.getLogger(__name__)


# =============================================================================
# DISCOVERY STATUS
# =============================================================================


class DiscoveryStatus(str, Enum):
    """Status of a discovered file."""

    PENDING = "pending"  # Found but not analyzed
    ANALYZING = "analyzing"  # Currently being analyzed
    OWNED = "owned"  # Already has Mahajana owner
    ORPHAN = "orphan"  # No owner - candidate for adoption
    ADOPTED = "adopted"  # Successfully adopted
    REJECTED = "rejected"  # Could not be adopted
    MERCY = "mercy"  # Adopted via Ajamil Exception
    SKIPPED = "skipped"  # Test file, __pycache__, etc.


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================


class DiscoveredFile(TypedDict):
    """A discovered Python file. WATERTIGHT."""

    path: str
    name: str
    status: str  # DiscoveryStatus value
    size_bytes: int
    detected_owner: Optional[str]  # Mahajana if owned
    discovered_at: str


class DiscoveryProgress(TypedDict):
    """Progress of discovery operation. WATERTIGHT."""

    total_files: int
    scanned: int
    owned: int
    orphans: int
    adopted: int
    mercy_cases: int  # Ajamil Exception saves
    rejected: int
    skipped: int
    current_file: str
    percent_complete: float
    started_at: str
    updated_at: str


class DiscoveryReport(TypedDict):
    """Final report of discovery operation. WATERTIGHT."""

    scan_path: str
    total_files: int
    owned_files: int
    orphan_files: int
    adopted_files: int
    mercy_cases: int  # Saved by Holy Name alone
    rejected_files: int
    skipped_files: int
    # By Mahajana
    by_mahajana: Dict[str, int]
    # By Quarter
    by_quarter: Dict[str, int]
    # By Resonance
    by_resonance: Dict[str, int]
    # Timing
    started_at: str
    completed_at: str
    duration_seconds: float


class BatchAdoptionResult(TypedDict):
    """Result of batch adoption. WATERTIGHT."""

    total: int
    adopted: int
    mercy: int
    rejected: int
    results: List[FullAdoptionResult]


# =============================================================================
# OWNERSHIP DETECTION - Is it already owned?
# =============================================================================

# Keywords that suggest Mahajana ownership
OWNERSHIP_MARKERS: Dict[str, Set[str]] = {
    "brahma": {"OWNER = Mahajana.BRAHMA", "brahma protocol", "@brahma"},
    "narada": {"OWNER = Mahajana.NARADA", "narada protocol", "@narada"},
    "shambhu": {"OWNER = Mahajana.SHAMBHU", "shambhu protocol", "@shambhu"},
    "kumaras": {"OWNER = Mahajana.KUMARAS", "kumaras protocol", "@kumaras"},
    "kapila": {"OWNER = Mahajana.KAPILA", "kapila protocol", "@kapila"},
    "manu": {"OWNER = Mahajana.MANU", "manu protocol", "@manu"},
    "prahlada": {"OWNER = Mahajana.PRAHLADA", "prahlada protocol", "@prahlada"},
    "janaka": {"OWNER = Mahajana.JANAKA", "janaka protocol", "@janaka"},
    "bhishma": {"OWNER = Mahajana.BHISHMA", "bhishma protocol", "@bhishma"},
    "bali": {"OWNER = Mahajana.BALI", "bali protocol", "@bali"},
    "shuka": {"OWNER = Mahajana.SHUKA", "shuka protocol", "@shuka"},
    "yamaraja": {"OWNER = Mahajana.YAMARAJA", "yamaraja protocol", "@yamaraja"},
}


def detect_owner(source_code: str, file_path: str = "<unknown>") -> Optional[str]:
    """
    Detect if source code already has a Mahajana owner.

    Uses SUBSTRATE extract_declarations() for __mahajana__ detection.
    Falls back to keyword matching for legacy code.

    Returns Mahajana name if owned, None if orphan.
    """
    # === PRIMARY: Use substrate AST extraction ===
    declarations = extract_declarations(
        source_code,
        file_path,
        [DeclarationType.MAHAJANA.value],
    )

    for decl in declarations:
        if decl.get("type") == DeclarationType.MAHAJANA.value:
            value = decl.get("value", "")
            if value and value in OWNERSHIP_MARKERS:
                return value

    # === FALLBACK: Legacy keyword detection ===
    source_lower = source_code.lower()

    for mahajana, markers in OWNERSHIP_MARKERS.items():
        for marker in markers:
            if marker.lower() in source_lower:
                return mahajana

    return None


def is_in_mahajana_folder(path: Path) -> Optional[str]:
    """
    Check if file is in a mahajanas/{name}/ folder.

    Returns Mahajana name if in folder, None otherwise.
    """
    parts = path.parts
    try:
        idx = parts.index("mahajanas")
        if idx + 1 < len(parts):
            potential_owner = parts[idx + 1]
            if potential_owner in OWNERSHIP_MARKERS:
                return potential_owner
    except ValueError as _exc:
        logger.exception("Unexpected error: %s", _exc)
    return None


# =============================================================================
# FILE FILTERING - What to skip?
# =============================================================================

SKIP_PATTERNS = {
    "__pycache__",
    ".pyc",
    "test_",
    "_test.py",
    "tests/",
    ".git",
    "node_modules",
    "__init__.py",  # Skip module init files
    "conftest.py",  # Skip pytest config
}


def should_skip(path: Path) -> bool:
    """
    Check if file should be skipped.

    Skips:
    - __pycache__
    - test files
    - __init__.py
    - .git folders
    """
    path_str = str(path).lower()

    for pattern in SKIP_PATTERNS:
        if pattern in path_str:
            return True

    # Also skip non-Python files
    if path.suffix != ".py":
        return True

    return False


# =============================================================================
# THE DISCOVERY ENGINE
# =============================================================================


class DiscoveryEngine:
    """
    The Protocol Discovery Engine.

    ACTIVE scanning for wild protocols.
    The Lotus SEEKS. Krishna is the DOER.

    FLOW:
        scan_path() → discover_orphans() → adopt_all() → report()

    ZERO MANUAL WIRING:
        - Uses ScannerProtocol (SUBSTRATE) for scanning
        - Detects ownership via extract_declarations
        - Identifies orphans
        - Adopts via Mahamantra
        - Reports progress

    SUBSTRATE INTEGRATION:
        Scanning is delegated to ScannerProtocol.
        NO HARDCODED PATHS - config-driven via ScanConfig.
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        scanner: Optional[ScannerProtocol] = None,
        config: Optional[ScanConfig] = None,
    ) -> None:
        """
        Initialize discovery engine.

        Args:
            base_path: Base path to scan (deprecated - use config)
            scanner: ScannerProtocol instance (optional - creates default)
            config: ScanConfig for scanning (optional - uses defaults)
        """
        self._base_path = base_path or Path.cwd()
        self._discovered: Dict[str, DiscoveredFile] = {}
        self._adoptions: Dict[str, FullAdoptionResult] = {}
        self._progress: Optional[DiscoveryProgress] = None
        self._start_time: Optional[datetime] = None

        # === SUBSTRATE SCANNER ===
        if scanner is not None:
            self._scanner = scanner
        else:
            # MahajanaScanner removed - use base ScannerProtocol stub
            # Folder IS wiring - no declaration scanning needed
            self._scanner = None  # Will use fallback path discovery

    # =========================================================================
    # SCAN - Uses ScannerProtocol (SUBSTRATE)
    # =========================================================================

    def scan(self, path: Optional[Path] = None) -> List[DiscoveredFile]:
        """
        Scan a path for Python files using ScannerProtocol.

        SUBSTRATE INTEGRATION:
            Delegates to ScannerProtocol.scan() then converts
            ScannedFile → DiscoveredFile.

        Returns list of discovered files with status.
        """
        self._start_time = datetime.now()
        discovered: List[DiscoveredFile] = []

        # === USE SUBSTRATE SCANNER ===
        scan_result = self._scanner.scan(str(path) if path else None)

        for scanned in scan_result.get("files", []):
            file_path = Path(scanned["path"])
            status_str = scanned.get("status", "")

            # Map FileStatus → DiscoveryStatus
            if status_str == FileStatus.SKIPPED.value:
                discovered.append(
                    self._create_discovered(
                        file_path,
                        DiscoveryStatus.SKIPPED,
                    )
                )
            elif status_str == FileStatus.OWNED.value:
                # Get mahajana from declarations
                owner = None
                for decl in scanned.get("declarations", []):
                    if decl.get("type") == DeclarationType.MAHAJANA.value:
                        owner = decl.get("value")
                        break
                discovered.append(
                    self._create_discovered(
                        file_path,
                        DiscoveryStatus.OWNED,
                        owner=owner,
                    )
                )
            elif status_str == FileStatus.ORPHAN.value:
                discovered.append(
                    self._create_discovered(
                        file_path,
                        DiscoveryStatus.ORPHAN,
                    )
                )
            elif status_str == FileStatus.ERROR.value:
                discovered.append(
                    self._create_discovered(
                        file_path,
                        DiscoveryStatus.SKIPPED,
                    )
                )
            else:
                # PENDING or SCANNED → check folder ownership
                folder_owner = is_in_mahajana_folder(file_path)
                if folder_owner:
                    discovered.append(
                        self._create_discovered(
                            file_path,
                            DiscoveryStatus.OWNED,
                            owner=folder_owner,
                        )
                    )
                else:
                    discovered.append(
                        self._create_discovered(
                            file_path,
                            DiscoveryStatus.PENDING,
                        )
                    )

        # Store discovered files
        for df in discovered:
            self._discovered[df["path"]] = df

        return discovered

    def _create_discovered(
        self,
        path: Path,
        status: DiscoveryStatus,
        owner: Optional[str] = None,
    ) -> DiscoveredFile:
        """Create a DiscoveredFile entry."""
        return DiscoveredFile(
            path=str(path),
            name=path.stem,
            status=status.value,
            size_bytes=path.stat().st_size if path.exists() else 0,
            detected_owner=owner,
            discovered_at=datetime.now().isoformat(),
        )

    # =========================================================================
    # ANALYZE - Check each file for ownership
    # =========================================================================

    def analyze_file(self, file_path: Path) -> DiscoveredFile:
        """
        Analyze a single file for ownership.

        Reads source code and detects if owned or orphan.
        """
        if file_path.stem not in self._discovered:
            # Create entry if not already discovered
            self._discovered[str(file_path)] = self._create_discovered(
                file_path,
                DiscoveryStatus.PENDING,
            )

        entry = self._discovered[str(file_path)]

        if entry["status"] in (DiscoveryStatus.SKIPPED.value, DiscoveryStatus.OWNED.value):
            return entry

        try:
            source_code = file_path.read_text(encoding="utf-8")
        except Exception:
            entry["status"] = DiscoveryStatus.SKIPPED.value
            return entry

        # Detect owner from source (uses substrate extract_declarations)
        owner = detect_owner(source_code, str(file_path))

        if owner:
            entry["status"] = DiscoveryStatus.OWNED.value
            entry["detected_owner"] = owner
        else:
            entry["status"] = DiscoveryStatus.ORPHAN.value

        return entry

    def analyze_all(self) -> List[DiscoveredFile]:
        """
        Analyze all pending files.

        Returns list of analyzed files.
        """
        analyzed: List[DiscoveredFile] = []

        for path, entry in self._discovered.items():
            if entry["status"] == DiscoveryStatus.PENDING.value:
                analyzed.append(self.analyze_file(Path(path)))

        return analyzed

    # =========================================================================
    # DISCOVER ORPHANS - Find files without owners
    # =========================================================================

    def discover_orphans(self, path: Optional[Path] = None) -> List[DiscoveredFile]:
        """
        Discover orphan protocols (no Mahajana owner).

        This is the MAIN discovery function:
        1. Scan all files
        2. Analyze each for ownership
        3. Return orphans (candidates for adoption)
        """
        # Scan if not already done
        if not self._discovered:
            self.scan(path)

        # Analyze pending files
        self.analyze_all()

        # Return orphans
        return [entry for entry in self._discovered.values() if entry["status"] == DiscoveryStatus.ORPHAN.value]

    # =========================================================================
    # ADOPT - Run orphans through adoption pipeline
    # =========================================================================

    def adopt_orphan(self, file_path: Path) -> FullAdoptionResult:
        """
        Adopt a single orphan protocol.

        Runs through full 5-step pipeline:
        analyze → decide → adopt → manifest → sync
        """
        try:
            source_code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            # Create minimal failure result
            return FullAdoptionResult(
                analysis=ProtocolAnalysis(
                    protocol_path=str(file_path),
                    protocol_name=file_path.stem,
                    detected_opcodes=[],
                    primary_opcode=None,
                    quarter_index=0,
                    quarter_name="genesis",
                    has_soul=False,
                    claims_supreme=False,
                    parampara_hash=0,
                    is_connected=False,
                    analyzed_at=datetime.now().isoformat(),
                ),
                result=AdoptionResult(
                    protocol_name=file_path.stem,
                    status=AdoptionStatus.REJECTED.value,
                    decision=AdoptionDecision.REJECT.value,
                    assigned_mahajana=None,
                    assigned_position=None,
                    target_path=f"protocols/rejected/{file_path.stem}.py",
                    reason=f"READ_ERROR: {str(e)}",
                    analysis={},  # type: ignore
                    adopted_at=datetime.now().isoformat(),
                ),
                manifest={},  # type: ignore
                sync={},  # type: ignore
                attraction=AttractionReport(
                    protocol_name=file_path.stem,
                    coherence=0.0,
                    resonance_strength="none",
                    attraction_vector=0,
                    is_attracted=False,
                    needs_transformation=True,
                    mercy_type="severe",
                    mercy_available=False,
                    ajamil_exception=False,
                    recommended_action="READ_ERROR: Could not analyze",
                    analyzed_at=datetime.now().isoformat(),
                ),
                is_fully_adopted=False,
                total_coherence=0.0,
            )

        # Run full adoption pipeline
        result = adopt_full(str(file_path), source_code)

        # Update discovered status
        path_str = str(file_path)
        if path_str in self._discovered:
            entry = self._discovered[path_str]

            if result["attraction"]["ajamil_exception"]:
                entry["status"] = DiscoveryStatus.MERCY.value
            elif result["is_fully_adopted"]:
                entry["status"] = DiscoveryStatus.ADOPTED.value
            else:
                entry["status"] = DiscoveryStatus.REJECTED.value

            entry["detected_owner"] = result["result"]["assigned_mahajana"]

        # Store result
        self._adoptions[file_path.stem] = result

        return result

    def adopt_all_orphans(
        self,
        progress_callback: Optional[Callable[[DiscoveryProgress], None]] = None,
    ) -> BatchAdoptionResult:
        """
        Adopt all discovered orphan protocols.

        This is the MAIN adoption function:
        1. Get all orphans
        2. Run each through adopt_full()
        3. Track progress
        4. Return results

        THE LOTUS ATTRACTS. No manual wiring.
        """
        orphans = self.discover_orphans()
        total = len(orphans)

        results: List[FullAdoptionResult] = []
        adopted = 0
        mercy = 0
        rejected = 0

        for i, orphan in enumerate(orphans):
            # Update progress
            self._progress = DiscoveryProgress(
                total_files=len(self._discovered),
                scanned=len(self._discovered),
                owned=sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.OWNED.value),
                orphans=total,
                adopted=adopted,
                mercy_cases=mercy,
                rejected=rejected,
                skipped=sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.SKIPPED.value),
                current_file=orphan["path"],
                percent_complete=(i / total) * 100 if total > 0 else 100,
                started_at=self._start_time.isoformat() if self._start_time else "",
                updated_at=datetime.now().isoformat(),
            )

            if progress_callback:
                progress_callback(self._progress)

            # Adopt the orphan
            result = self.adopt_orphan(Path(orphan["path"]))
            results.append(result)

            # Track outcomes
            if result["attraction"]["ajamil_exception"]:
                mercy += 1
                adopted += 1  # Mercy = adopted!
            elif result["is_fully_adopted"]:
                adopted += 1
            else:
                rejected += 1

        return BatchAdoptionResult(
            total=total,
            adopted=adopted,
            mercy=mercy,
            rejected=rejected,
            results=results,
        )

    # =========================================================================
    # REPORT - Generate discovery report
    # =========================================================================

    def report(self) -> DiscoveryReport:
        """
        Generate final discovery report.

        Summarizes:
        - Total files discovered
        - Owned vs orphan counts
        - Adoption results
        - Distribution by Mahajana, Quarter, Resonance
        """
        end_time = datetime.now()
        duration = (end_time - self._start_time).total_seconds() if self._start_time else 0

        # Count by status
        owned = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.OWNED.value)
        orphan = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.ORPHAN.value)
        adopted = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.ADOPTED.value)
        mercy = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.MERCY.value)
        rejected = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.REJECTED.value)
        skipped = sum(1 for d in self._discovered.values() if d["status"] == DiscoveryStatus.SKIPPED.value)

        # Count by Mahajana
        by_mahajana: Dict[str, int] = {}
        for d in self._discovered.values():
            owner = d["detected_owner"]
            if owner:
                by_mahajana[owner] = by_mahajana.get(owner, 0) + 1

        # Count by Quarter
        by_quarter: Dict[str, int] = {
            "genesis": 0,
            "dharma": 0,
            "karma": 0,
            "moksha": 0,
        }
        for result in self._adoptions.values():
            quarter = result["analysis"]["quarter_name"]
            by_quarter[quarter] = by_quarter.get(quarter, 0) + 1

        # Count by Resonance
        by_resonance: Dict[str, int] = {
            "strong": 0,
            "medium": 0,
            "weak": 0,
            "mercy": 0,
            "none": 0,
        }
        for result in self._adoptions.values():
            resonance = result["attraction"]["resonance_strength"]
            by_resonance[resonance] = by_resonance.get(resonance, 0) + 1

        return DiscoveryReport(
            scan_path=str(self._base_path),
            total_files=len(self._discovered),
            owned_files=owned,
            orphan_files=orphan,
            adopted_files=adopted,
            mercy_cases=mercy,
            rejected_files=rejected,
            skipped_files=skipped,
            by_mahajana=by_mahajana,
            by_quarter=by_quarter,
            by_resonance=by_resonance,
            started_at=self._start_time.isoformat() if self._start_time else "",
            completed_at=end_time.isoformat(),
            duration_seconds=duration,
        )

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    def get_progress(self) -> Optional[DiscoveryProgress]:
        """Get current discovery progress."""
        return self._progress

    def get_adoption(self, name: str) -> Optional[FullAdoptionResult]:
        """Get adoption result by protocol name."""
        return self._adoptions.get(name)

    def get_discovered(self, path: str) -> Optional[DiscoveredFile]:
        """Get discovered file by path."""
        return self._discovered.get(path)

    def iter_orphans(self) -> Iterator[DiscoveredFile]:
        """Iterate over orphan protocols."""
        for entry in self._discovered.values():
            if entry["status"] == DiscoveryStatus.ORPHAN.value:
                yield entry

    def iter_adopted(self) -> Iterator[FullAdoptionResult]:
        """Iterate over adopted protocols."""
        for result in self._adoptions.values():
            if result["is_fully_adopted"]:
                yield result

    def iter_mercy_cases(self) -> Iterator[FullAdoptionResult]:
        """Iterate over mercy cases (Ajamil Exception)."""
        for result in self._adoptions.values():
            if result["attraction"]["ajamil_exception"]:
                yield result


# =============================================================================
# GLOBAL SINGLETON
# =============================================================================

_engine: Optional[DiscoveryEngine] = None


def get_engine(base_path: Optional[Path] = None) -> DiscoveryEngine:
    """Get the global discovery engine."""
    global _engine
    if _engine is None or base_path:
        _engine = DiscoveryEngine(base_path)
    return _engine


# =============================================================================
# CONVENIENCE FUNCTIONS - ONE LINE DISCOVERY
# =============================================================================


def discover(path: Path) -> List[DiscoveredFile]:
    """
    Discover all orphan protocols in a path.

    ONE LINE. Returns orphans ready for adoption.
    """
    engine = DiscoveryEngine(path)
    return engine.discover_orphans()


def adopt_path(path: Path) -> BatchAdoptionResult:
    """
    Discover AND adopt all orphan protocols in a path.

    ONE LINE. Full pipeline: scan → analyze → adopt.
    The Mahamantra decides everything.
    """
    engine = DiscoveryEngine(path)
    return engine.adopt_all_orphans()


def report_path(path: Path) -> DiscoveryReport:
    """
    Full discovery report for a path.

    ONE LINE. Scans, adopts, and reports.
    """
    engine = DiscoveryEngine(path)
    engine.adopt_all_orphans()
    return engine.report()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status
    "DiscoveryStatus",
    # Types (WATERTIGHT)
    "DiscoveredFile",
    "DiscoveryProgress",
    "DiscoveryReport",
    "BatchAdoptionResult",
    # Detection
    "detect_owner",
    "is_in_mahajana_folder",
    "should_skip",
    "OWNERSHIP_MARKERS",
    "SKIP_PATTERNS",
    # Engine
    "DiscoveryEngine",
    "get_engine",
    # ONE LINE FUNCTIONS
    "discover",
    "adopt_path",
    "report_path",
]
