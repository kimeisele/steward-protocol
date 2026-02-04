"""
SANKIRTAN - The Mass Chanting / DNA Injection
==============================================

"harer nama harer nama harer namaiva kevalam
kalau nasty eva nasty eva nasty eva gatir anyatha"

"In this age of Kali there is no other way, no other way,
no other way for self-realization than chanting the holy name."

SANKIRTAN = ASHVAMEDHA = The Horse Sacrifice

The Mahamantra does not manually wire. It CHANTS.
The chanting spreads. Files awaken. The system dances.

THE 4-PHASE PIPELINE (Chatuh-Sutra):
====================================

    ┌─────────────────────────────────────────────────────────────────────┐
    │ PHASE     │ QUARTER  │ OPCODES           │ FUNCTION               │
    ├───────────┼──────────┼───────────────────┼────────────────────────┤
    │ Phase 0   │ GENESIS  │ WAKE/LOAD/ALLOC   │ Init & Load file       │
    │ Phase 1   │ DHARMA   │ COMPILE/CHECK     │ Validate & Align       │
    │ Phase 2   │ KARMA    │ EXEC/INJECT       │ Execute DNA injection  │
    │ Phase 3   │ MOKSHA   │ FLUSH/LOG/SEAL    │ Release & Report       │
    └─────────────────────────────────────────────────────────────────────┘

KALI YUGA GRACE:
================
    "Free for all sinners" - Graceful failure handling.
    If Phase 1 (Dharma/Validate) fails, we don't abort.
    We chant on. The Mahamantra cleanses ALL.

NO MANUAL WIRING. The folder structure IS the wiring.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HALVES, HARE_COUNT, KSETRAJNA, PANCHA, PARAMPARA, QUARTERS, TEN, TRINITY, WORDS)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 2 - Communication/Broadcast
__position__ = HALVES
__genesis__ = "0x2c80316d"  # GenesisByte: parampara % 37 == 0

import ast
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Final, Iterator, List, Optional, Tuple

from vibe_core.mahamantra.protocols._pancha import TattvaDict

# Import SankirtanProtocol (THE LAW)
from vibe_core.mahamantra.protocols._sankirtan import (
    GenesisByte,
    InjectionRequest,
    SankirtanProtocol,
    WiringStats,
)
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS

# Import SSOT Pipeline types (Aliased to avoid collision with local types)
from vibe_core.mahamantra.substrate.samskara import (
    Phase,
    PhaseResult as SamskaraPhaseResult,
    PhaseStatus,
    PipelineContext as SamskaraPipelineContext,
    PipelineExecutor,
    SamskaraProtocol,
)
from vibe_core.mahamantra.substrate.mahajana import Quarter
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.wiring import (
    POSITION_BY_INDEX,
    POSITION_BY_NAME,
)

logger = logging.getLogger("SANKIRTAN")


# =============================================================================
# CONSTANTS
# =============================================================================

# NOTE: SCAN_DIRECTORIES is now DERIVED from FOLDER_MAHAJANA_MAP (see below)
# This is PROTOCOL-DRIVEN, not hardcoded.
# The map defines ownership, the scan follows ownership.

# Skip patterns
SKIP_PATTERNS: Final[Tuple[str, ...]] = (
    "__pycache__",
    ".pyc",
    "test_",
    "_test.py",
    "tests/",
)

# Folder-to-Guardian GOVERNANCE mapping
#
# NOTE: Trivial entries like "mahajanas/vyasa" -> "vyasa" are NO LONGER NEEDED.
#       Auto-detection handles any path containing a guardian name.
#
# This map contains ONLY semantic governance decisions:
# - Which guardian owns which domain/folder?
# - This is POLICY, not ontology.
#
# The ontology (Position -> Guardian) lives in MAHAMANTRA_POSITIONS (SSOT).
# This map defines WHO is responsible for WHAT folder.
FOLDER_MAHAJANA_MAP: Final[Dict[str, str]] = {
    # === DOMAIN-BASED MAPPING (Semantic Governance) ===
    # GENESIS Quarter (Creation/Bootstrap)
    "runtime": "brahma",  # Creation/Bootstrap
    "phoenix": "brahma",  # Resurrection
    "genesis": "brahma",  # Creation scripts
    # DHARMA Quarter (Law/Structure)
    "protocols": "vyasa",  # Compilation/Knowledge
    "governance": "manu",  # Law/Rules
    "state": "bhishma",  # Immutable state
    # KARMA Quarter (Action/Service)
    "cli": "narada",  # Communication
    "services": "janaka",  # Duty/Service
    "plugins": "prahlada",  # Devotion/Extensions
    "cartridges": "prahlada",  # Modular capabilities
    "agents": "prahlada",  # Agent execution
    # MOKSHA Quarter (Liberation/Intelligence)
    "naga": "yamaraja",  # Security/Judgment
    "ouroboros": "shambhu",  # Destruction/Cycle
    "cortex": "shuka",  # Vision/Intelligence
    "shuddhi": "kapila",  # Analysis/Purification
    # === INFRASTRUCTURE (Foundation Layer) ===
    "mahamantra": "prithu",  # Foundation of all
    "loaders": "brahma",  # Bootstrap loaders
    "config": "manu",  # Configuration = Law
    "settings": "manu",  # Settings = Rules
    # === TOOLS & UTILITIES ===
    "tools": "parashurama",  # Tools = Weapons
    "utils": "kumaras",  # Pure utilities
    "scripts": "parashurama",  # Execution scripts
    # === KNOWLEDGE & STORAGE ===
    "knowledge": "vyasa",  # Knowledge = Vyasa's domain
    "store": "bali",  # Storage = Sacrifice (give up)
    "llm": "shuka",  # LLM = Transcendent vision
    # === ORCHESTRATION ===
    "reactor": "shambhu",  # Reaction = Transformation
    "scheduling": "yamaraja",  # Time/Death = Yamaraja
    "task_management": "janaka",  # Tasks = Duty
    "steward": "janaka",  # Stewardship = Service
    # === GATEWAY & COMMUNICATION ===
    "gateway": "narada",  # Gateway = Travel/Communication
    "playbook": "narada",  # Playbooks = Instructions
    # === SPECIAL DOMAINS ===
    "specialists": "kapila",  # Specialists = Analysis
    "vajra": "nrisimha",  # Vajra = Protection/Power
    # === MAHAMANTRA SUBFOLDERS (more specific = higher priority) ===
    # NOTE: Guardian names in these paths will auto-detect, but we keep
    #       domain-level mappings for semantic clarity
    "mahamantra/substrate": "prithu",  # Foundation (when no specific guardian)
    "mahamantra/kernel": "brahma",  # Genesis (when no specific guardian)
    "mahamantra/protocols": "vyasa",  # Compilation protocols
    "protocols/universal": "vyasa",  # Universal compilation
    "protocols/substrate": "prithu",  # Substrate foundation
    # === PHOENIX SECTIONS (config domains) ===
    "phoenix/sections/naga": "yamaraja",  # Security config
    "phoenix/sections/agents": "prahlada",  # Agent config
    "phoenix/sections/quality": "kumaras",  # Quality config
    "phoenix/sections/guardrails": "kumaras",  # Guardrails config
    "phoenix/sections/test_governance": "yamaraja",  # Test governance
    "phoenix/sections/llm": "shuka",  # LLM config
    "phoenix/sections/prompts": "shuka",  # Prompts config
    "phoenix/sections/providers": "shuka",  # Provider config
    "phoenix/sections/quotas": "manu",  # Quotas/limits
    "phoenix/sections/runtime": "brahma",  # Runtime config
    "phoenix/sections/paths": "brahma",  # Paths config
    "phoenix/sections/templates": "brahma",  # Templates config
    "phoenix/sections/kernel": "brahma",  # Kernel config
    "phoenix/sections/cli": "narada",  # CLI config
    "phoenix/sections/interface": "narada",  # Interface config
    "phoenix/sections/apis": "narada",  # APIs config
    "phoenix/sections/steward": "janaka",  # Steward config
    "phoenix/sections/manas": "kapila",  # Mind/analysis config
    "phoenix/sections/city": "janaka",  # City/matrix config
    # === RESEARCH (Knowledge/Discovery) ===
    # FOLDER IS WIRING: research/quarter → quarter HEAD
    "mahamantra/research": "vyasa",  # Research = Knowledge = Vyasa
    "mahamantra/research/genesis": "brahma",  # Genesis quarter research
    "mahamantra/research/dharma": "vyasa",  # Dharma quarter research
    "mahamantra/research/karma": "narada",  # Karma quarter research
    "mahamantra/research/moksha": "kapila",  # Moksha quarter research (Analysis)
}


# DERIVED: Scan directories come from the map (protocol-driven, not hardcoded)
# Extract top-level directories from FOLDER_MAHAJANA_MAP
def _derive_scan_directories() -> Tuple[str, ...]:
    """Derive scan directories from FOLDER_MAHAJANA_MAP keys."""
    dirs = set()
    for folder in FOLDER_MAHAJANA_MAP.keys():
        # Get top-level directory (before first /)
        top_level = folder.split("/")[0]
        if top_level != "mahajanas":  # mahajanas is a special folder
            dirs.add(top_level)
    # Add root "." for root-level files
    dirs.add(".")
    return tuple(sorted(dirs))


SCAN_DIRECTORIES: Final[Tuple[str, ...]] = _derive_scan_directories()


# =============================================================================
# 4-PHASE PIPELINE (Chatuh-Sutra)
# =============================================================================


@dataclass
class PhaseResult:
    """Result of a single phase in the pipeline."""

    phase: Quarter
    success: bool
    message: str
    data: Optional[Dict] = None


@dataclass
class PipelineContext:
    """
    Context passed through the 4-phase pipeline.

    Contains all state needed for processing a single file.
    """

    file_path: Path
    content: Optional[str] = None
    mahajana: Optional[str] = None
    position: Optional[int] = None
    is_valid: bool = True
    was_already_owned: bool = False
    error: Optional[str] = None
    phases: List[PhaseResult] = field(default_factory=list)

    def log_phase(self, phase: Quarter, success: bool, message: str, data: Optional[Dict] = None) -> None:
        """Log a phase result."""
        self.phases.append(PhaseResult(phase, success, message, data))

        # Log with appropriate level
        phase_name = phase.value.upper()
        if success:
            logger.debug(f"[{phase_name}] {self.file_path.name}: {message}")
        else:
            logger.warning(f"[{phase_name}] {self.file_path.name}: {message}")

    @property
    def all_phases_ok(self) -> bool:
        """Did all phases succeed?"""
        return all(p.success for p in self.phases)

    @property
    def last_phase(self) -> Optional[Quarter]:
        """Get the last executed phase."""
        if self.phases:
            return self.phases[-KSETRAJNA].phase
        return None


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass
class InjectionResult:
    """Result of injecting one file."""

    file_path: str
    mahajana: str
    position: int
    success: bool
    was_dry_run: bool
    message: str


@dataclass
class SankirtanResult:
    """Result of mass sankirtan injection."""

    files_scanned: int = 0
    files_injected: int = 0
    files_skipped: int = 0
    files_already_owned: int = 0
    files_failed: int = 0
    was_dry_run: bool = True
    injections: List[InjectionResult] = field(default_factory=list)
    by_mahajana: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


# =============================================================================
# FOLDER-TO-MAHAJANA MAPPING
# =============================================================================

# Cache for guardian names (loaded once from Registry)
_GUARDIAN_NAMES_CACHE: Optional[List[str]] = None


def _get_all_guardian_names() -> List[str]:
    """
    Get all guardian names from the Registry.

    Cached for performance (loaded once at module import).

    Returns:
        List of all guardian names (lowercase)
    """
    global _GUARDIAN_NAMES_CACHE
    if _GUARDIAN_NAMES_CACHE is None:
        _GUARDIAN_NAMES_CACHE = [
            POSITION_BY_INDEX[i].guardian.value
            for i in range(WORDS)
            if POSITION_BY_INDEX[i] is not None
        ]
    return _GUARDIAN_NAMES_CACHE


# =============================================================================
# VALIDATION - Ensure map guardians exist in Registry
# =============================================================================


def _validate_governance_map() -> None:
    """
    Validate that all guardians in FOLDER_MAHAJANA_MAP exist in the Registry.

    Raises:
        ValueError: If any guardian in the map doesn't exist in the position table.
    """
    valid_guardians = set(_get_all_guardian_names())
    map_guardians = set(FOLDER_MAHAJANA_MAP.values())

    invalid = map_guardians - valid_guardians
    if invalid:
        raise ValueError(
            f"GOVERNANCE MAP VALIDATION FAILED: "
            f"Unknown guardians in FOLDER_MAHAJANA_MAP: {invalid}. "
            f"Valid guardians from MAHAMANTRA_POSITIONS: {sorted(valid_guardians)}"
        )


# Run validation at module import time (fail fast!)
_validate_governance_map()


def get_mahajana_for_path(file_path: Path) -> Optional[Tuple[str, int]]:
    """
    Determine Mahajana for a file based on FOLDER_IS_WIRING.

    STRATEGY (Priority order):
    1. AUTO-DETECT: Guardian name in path (e.g., "mahajanas/vyasa" -> vyasa)
    2. GOVERNANCE MAP: Explicit folder ownership (e.g., "protocols" -> vyasa)
    3. HASH FALLBACK: Deterministic distribution

    SECURITY: Path is normalized FIRST to prevent traversal attacks.
    "protocols/../naga/evil.py" -> "naga/evil.py" (maps to yamaraja, not vyasa)

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (mahajana_name, position) or None if cannot determine.
    """
    import os

    # SECURITY: Normalize path to prevent traversal attacks like "../"
    # This ensures "protocols/../naga/evil.py" becomes "naga/evil.py"
    normalized_path = os.path.normpath(str(file_path))
    path_str = normalized_path.lower()

    # STEP 1: AUTO-DETECT - Check if any guardian name is in the path
    # This eliminates the need for trivial entries like "mahajanas/vyasa" -> "vyasa"
    for guardian_name in _get_all_guardian_names():
        if guardian_name in path_str:
            mapping = POSITION_BY_NAME.get(guardian_name)
            if mapping:
                return (guardian_name, mapping.index)

    # STEP 2: GOVERNANCE MAP - Check explicit mappings (longest match first)
    for folder, mahajana in sorted(FOLDER_MAHAJANA_MAP.items(), key=lambda x: -len(x[0])):
        if folder in path_str:
            mapping = POSITION_BY_NAME.get(mahajana)
            if mapping:
                return (mahajana, mapping.index)

    # STEP 3: HASH FALLBACK - Deterministic assignment
    # This ensures deterministic assignment for unknown paths
    # P0-FIX: Use deterministic hash instead of Python's randomized hash()
    import hashlib
    path_bytes = path_str.encode('utf-8')
    path_hash_int = int.from_bytes(hashlib.sha256(path_bytes).digest()[:QUARTERS], byteorder='big')
    path_hash = path_hash_int % WORDS  # SSOT
    mapping = MAHAMANTRA_POSITIONS[path_hash]
    return (mapping.guardian.value, mapping.index)


# =============================================================================
# DNA INJECTION (Balarama Pattern - Static)
# =============================================================================

DNA_TEMPLATE: Final[str] = """# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "{mahajana}"
__position__ = {position}
__genesis__ = "{genesis_hash}"  # GenesisByte: parampara % 37 == 0
"""


def compute_genesis_hash(mahajana: str, position: int, file_path: str = "") -> str:
    """
    Compute GenesisByte hash - PURE RAM COMPUTATION.

    The hash must satisfy: int(hash, 16) % 37 == 0 (Parampara verification).

    PARADIGM SHIFT (Yoga Maya):
        OLD: identity = f"{mahajana}:{position}:{file_path}" (Maha Maya - material)
        NEW: identity = f"{mahajana}:{position}" (Yoga Maya - spiritual)

    The file_path parameter is DEPRECATED and IGNORED.
    Genesis is computed from ARCHETYPE (mahajana + position) only.
    This makes Genesis HOLOGRAPHIC - same input → same output ALWAYS.

    The Mantra protects itself - RAM computation, not filesystem dependency.
    """
    import hashlib

    # YOGA MAYA: Pure archetype identity (NO FILE PATH!)
    # file_path parameter kept for backward compatibility but IGNORED
    identity = f"{mahajana}:{position}"
    raw_hash = hashlib.sha256(identity.encode()).hexdigest()[:HARE_COUNT]

    # Adjust to be divisible by 37 (Parampara alignment)
    base_value = int(raw_hash, WORDS)
    adjusted = base_value - (base_value % PARAMPARA)

    return f"0x{adjusted:08x}"


def has_declaration(content: str) -> bool:
    """Check if file already has __mahajana__ declaration."""
    return "__mahajana__" in content


def inject_declaration(content: str, mahajana: str, position: int, file_path: str = "") -> str:
    """
    Inject DNA declaration into file content.

    Inserts after module docstring AND after from __future__ imports.
    Includes GenesisByte hash (parampara % 37 == 0).

    IMPORTANT: Python requires `from __future__` to be at the very beginning
    (after docstring). We MUST respect this.
    """
    lines = content.split("\n")
    insert_idx = 0

    # Skip shebang
    if lines and lines[0].startswith("#!"):
        insert_idx = KSETRAJNA

    # Skip module docstring
    in_docstring = False
    docstring_char = None
    for i, line in enumerate(lines[insert_idx:], start=insert_idx):
        stripped = line.strip()

        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:TRINITY]
                if stripped.count(docstring_char) >= HALVES:
                    # Single-line docstring
                    insert_idx = i + KSETRAJNA
                    continue
                in_docstring = True
            elif stripped.startswith("#"):
                continue
            elif stripped == "":
                continue
            elif stripped.startswith("from __future__"):
                # MUST skip from __future__ imports - Python requirement!
                insert_idx = i + KSETRAJNA
                continue
            else:
                # Found non-docstring, non-comment, non-empty, non-future line
                insert_idx = i
                break
        else:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
                insert_idx = i + KSETRAJNA

    # Compute GenesisByte hash (TÜV Plakette at birth)
    genesis_hash = compute_genesis_hash(mahajana, position, file_path)

    # Generate DNA block
    dna_block = DNA_TEMPLATE.format(
        mahajana=mahajana,
        position=position,
        genesis_hash=genesis_hash,
    )

    # Insert
    lines.insert(insert_idx, dna_block)
    return "\n".join(lines)


def inject_file(file_path: str, mahajana: str, dry_run: bool = True) -> bool:
    """
    Inject Mahajana identity into a single file.

    Uses Balarama Pattern (DNA surgery) with GenesisByte seal.

    Args:
        file_path: Path to file
        mahajana: Mahajana name
        dry_run: If True, don't actually write

    Returns:
        True if injection successful/would succeed.
    """
    path = Path(file_path)
    if not path.exists():
        return False

    # Get position
    mapping = POSITION_BY_NAME.get(mahajana.lower())
    if not mapping:
        return False

    try:
        content = path.read_text()

        # Already has declaration?
        if has_declaration(content):
            return False

        # Inject with GenesisByte
        new_content = inject_declaration(
            content,
            mahajana,
            mapping.index,
            file_path=str(path),
        )

        if not dry_run:
            path.write_text(new_content)

        return True

    except Exception:
        return False


# =============================================================================
# THE 4 PHASES - Chatuh-Sutra Implementation
# =============================================================================


def _genesis_phase(ctx: PipelineContext) -> PipelineContext:
    """
    PHASE 0: GENESIS - Init & Load

    Quarter: Hare Krishna Hare Krishna
    OpCodes: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, INIT_THREAD

    Actions:
        - Wake the file (open for reading)
        - Load content
        - Allocate context (determine mahajana from folder)
        - Initialize processing state
    """
    try:
        # SYS_WAKE: Check file exists
        if not ctx.file_path.exists():
            ctx.is_valid = False
            ctx.log_phase(Quarter.GENESIS, False, "File not found")
            return ctx

        # LOAD_ROOT: Read file content
        ctx.content = ctx.file_path.read_text()

        # ALLOC_MEM: Determine Mahajana from folder structure
        mapping = get_mahajana_for_path(ctx.file_path)
        if mapping:
            ctx.mahajana, ctx.position = mapping
        else:
            ctx.is_valid = False
            ctx.log_phase(Quarter.GENESIS, False, "Cannot determine mahajana")
            return ctx

        # INIT_THREAD: Mark as loaded
        ctx.log_phase(Quarter.GENESIS, True, f"Loaded ({len(ctx.content)} bytes) → {ctx.mahajana}")
        return ctx

    except Exception as e:
        ctx.is_valid = False
        ctx.error = str(e)
        ctx.log_phase(Quarter.GENESIS, False, f"Load failed: {e}")
        return ctx


def _dharma_phase(ctx: PipelineContext) -> PipelineContext:
    """
    PHASE 1: DHARMA - Validate & Align

    Quarter: Krishna Krishna Hare Hare
    OpCodes: COMPILE_AST, BIND_SYMBOL, TYPE_CHECK, DHARMA_TEST

    Actions:
        - Compile AST (check if valid Python)
        - Check if already has __mahajana__
        - Type check (is this a .py file?)
        - Dharma test (should we inject?)

    KALI YUGA GRACE: Even if validation fails, we continue gracefully.
    """
    if not ctx.is_valid or not ctx.content:
        ctx.log_phase(Quarter.DHARMA, False, "Skipped (no content)")
        return ctx

    try:
        # COMPILE_AST: Check if valid Python (GRACEFUL - don't fail on syntax error)
        try:
            ast.parse(ctx.content)
        except SyntaxError as e:
            # KALI YUGA GRACE: Syntax errors don't stop us
            # We can still inject the header
            logger.debug(f"[DHARMA] Syntax warning (graceful): {e}")

        # BIND_SYMBOL: Check for existing declaration
        if has_declaration(ctx.content):
            ctx.was_already_owned = True
            ctx.is_valid = False  # Don't inject, but not an error
            ctx.log_phase(Quarter.DHARMA, True, "Already owned")
            return ctx

        # TYPE_CHECK: Is this a Python file?
        if ctx.file_path.suffix != ".py":
            ctx.is_valid = False
            ctx.log_phase(Quarter.DHARMA, False, "Not a Python file")
            return ctx

        # DHARMA_TEST: Passed all checks
        ctx.log_phase(Quarter.DHARMA, True, "Validated for injection")
        return ctx

    except Exception as e:
        # KALI YUGA GRACE: Continue even on unexpected errors
        ctx.error = str(e)
        ctx.log_phase(Quarter.DHARMA, False, f"Validation error (graceful): {e}")
        # Don't set is_valid=False - we may still be able to inject
        return ctx


def _karma_phase(ctx: PipelineContext, dry_run: bool = True) -> PipelineContext:
    """
    PHASE 2: KARMA - Execute & Inject

    Quarter: Hare Rama Hare Rama
    OpCodes: EXEC_OP, EXTEND_CAP, STATE_SYNC, LEDGER_SIGN

    Actions:
        - Execute injection (write DNA header)
        - Extend capabilities (add __mahajana__)
        - Sync state (update file)
        - Sign ledger (compute genesis hash)

    "karmaṇy evādhikāras te" - You have a right to perform action.
    """
    if not ctx.is_valid or ctx.was_already_owned:
        ctx.log_phase(Quarter.KARMA, True, "Skipped (not eligible)")
        return ctx

    if not ctx.content or not ctx.mahajana or ctx.position is None:
        ctx.log_phase(Quarter.KARMA, False, "Missing context data")
        return ctx

    try:
        # EXEC_OP + EXTEND_CAP: Generate new content with injection
        new_content = inject_declaration(
            ctx.content,
            ctx.mahajana,
            ctx.position,
            file_path=str(ctx.file_path),
        )

        # STATE_SYNC: Write to file (if not dry run)
        if not dry_run:
            ctx.file_path.write_text(new_content)
            ctx.log_phase(Quarter.KARMA, True, "Injected (LIVE)")
        else:
            ctx.log_phase(Quarter.KARMA, True, "Would inject (DRY-RUN)")

        return ctx

    except Exception as e:
        ctx.error = str(e)
        ctx.log_phase(Quarter.KARMA, False, f"Injection failed: {e}")
        return ctx


def _moksha_phase(ctx: PipelineContext) -> PipelineContext:
    """
    PHASE 3: MOKSHA - Release & Report

    Quarter: Rama Rama Hare Hare
    OpCodes: YIELD_CPU, IO_FLUSH, LOG_EMIT, AUDIT_SEAL

    Actions:
        - Yield CPU (release file handle)
        - Flush I/O (ensure written)
        - Emit log (report status)
        - Seal audit (final verification)

    "tyaktvā dehaṁ punar janma naiti" - Quitting the body, attaining liberation.
    """
    # YIELD_CPU + IO_FLUSH: Content already written, file handle closed
    # (Python handles this automatically)

    # LOG_EMIT: Create summary
    phase_summary = " → ".join(f"{p.phase.value.upper()}:{'✓' if p.success else '✗'}" for p in ctx.phases)

    # AUDIT_SEAL: Final status
    if ctx.was_already_owned:
        status = "ALREADY_OWNED"
    elif ctx.all_phases_ok:
        status = "SUCCESS"
    elif ctx.error:
        status = f"ERROR: {ctx.error}"
    else:
        status = "SKIPPED"

    ctx.log_phase(Quarter.MOKSHA, True, f"{status} [{phase_summary}]")

    return ctx


def process_file_pipeline(file_path: Path, dry_run: bool = True) -> PipelineContext:
    """
    Process a single file through the 4-phase pipeline.

    The Chatuh-Sutra: GENESIS → DHARMA → KARMA → MOKSHA

    Args:
        file_path: Path to the file
        dry_run: If True, don't actually write

    Returns:
        PipelineContext with all phase results
    """
    ctx = PipelineContext(file_path=file_path)

    # GENESIS: Init & Load
    ctx = _genesis_phase(ctx)

    # DHARMA: Validate & Align
    ctx = _dharma_phase(ctx)

    # KARMA: Execute & Inject
    ctx = _karma_phase(ctx, dry_run=dry_run)

    # MOKSHA: Release & Report
    ctx = _moksha_phase(ctx)

    return ctx


def iterate_sankirtan(
    base_path: Optional[Path] = None,
    dry_run: bool = True,
) -> Iterator[Tuple[Quarter, PipelineContext]]:
    """
    Generator that yields each phase as files are processed.

    This allows watching the sankirtan in real-time:

        for phase, ctx in iterate_sankirtan():
            print(f"{phase.value}: {ctx.file_path.name}")

    Yields:
        Tuple of (current_quarter, context)
    """
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent

    for dir_name in SCAN_DIRECTORIES:
        scan_dir = base_path / dir_name
        if not scan_dir.exists():
            continue

        for file_path in scan_dir.rglob("*.py"):
            # Skip patterns
            skip = False
            for pattern in SKIP_PATTERNS:
                if pattern in str(file_path):
                    skip = True
                    break
            if skip:
                continue

            # Process through pipeline, yielding each phase
            ctx = PipelineContext(file_path=file_path)

            # GENESIS
            ctx = _genesis_phase(ctx)
            yield (Quarter.GENESIS, ctx)

            # DHARMA
            ctx = _dharma_phase(ctx)
            yield (Quarter.DHARMA, ctx)

            # KARMA
            ctx = _karma_phase(ctx, dry_run=dry_run)
            yield (Quarter.KARMA, ctx)

            # MOKSHA
            ctx = _moksha_phase(ctx)
            yield (Quarter.MOKSHA, ctx)


# =============================================================================
# SANKIRTAN - MASS INJECTION
# =============================================================================


def chant_over_files(
    files: List[Path],
    dry_run: bool = True,
) -> SankirtanResult:
    """
    SANKIRTAN: Chant over specific files (4-phase pipeline).

    SSOT INTEGRATION:
        Scanner discovers → Sankirtan transforms.
        This function takes files from Scanner.get_orphans().

    THE CHATUH-SUTRA (4-Phase Pipeline):
        GENESIS → DHARMA → KARMA → MOKSHA

    Args:
        files: List of file paths to process (from Scanner)
        dry_run: If True, only report what would be done.

    Returns:
        SankirtanResult with counts and details.
    """
    result = SankirtanResult(was_dry_run=dry_run)
    phase_counts: Dict[str, int] = {q.value: 0 for q in Quarter}

    logger.info(f"SANKIRTAN chanting over {len(files)} files (dry_run={dry_run})")
    logger.info("=" * 60)

    for file_path in files:
        result.files_scanned += KSETRAJNA

        # === THE 4-PHASE PIPELINE ===
        ctx = process_file_pipeline(file_path, dry_run=dry_run)

        # Track phase progression
        for phase_result in ctx.phases:
            phase_counts[phase_result.phase.value] += KSETRAJNA

        # Categorize result
        if ctx.was_already_owned:
            result.files_already_owned += KSETRAJNA
        elif ctx.all_phases_ok and ctx.is_valid:
            karma_phases = [p for p in ctx.phases if p.phase == Quarter.KARMA]
            if karma_phases and "inject" in karma_phases[0].message.lower():
                result.files_injected += KSETRAJNA
                if ctx.mahajana:
                    result.by_mahajana[ctx.mahajana] = result.by_mahajana.get(ctx.mahajana, 0) + KSETRAJNA

                result.injections.append(
                    InjectionResult(
                        file_path=str(file_path),
                        mahajana=ctx.mahajana or "unknown",
                        position=ctx.position or 0,
                        success=True,
                        was_dry_run=dry_run,
                        message=f"{'Would inject' if dry_run else 'Injected'} {ctx.mahajana}",
                    )
                )
            else:
                result.files_skipped += KSETRAJNA
        elif ctx.error:
            result.files_failed += KSETRAJNA
            result.errors.append(f"{file_path}: {ctx.error}")
        else:
            result.files_skipped += KSETRAJNA

    logger.info("=" * 60)
    logger.info(
        f"SANKIRTAN complete: {result.files_injected} injected, "
        f"{result.files_already_owned} owned, {result.files_failed} failed"
    )

    return result


def perform_sankirtan(
    base_path: Optional[Path] = None,
    dry_run: bool = True,
    use_scanner: bool = True,
) -> SankirtanResult:
    """
    SANKIRTAN: Mass DNA injection using 4-phase pipeline.

    SSOT ARCHITECTURE:
        use_scanner=True  → MahajanaScanner discovers orphans → chant_over_files()
        use_scanner=False → Legacy rglob scanning (deprecated)

    THE CHATUH-SUTRA (4-Phase Pipeline):
        GENESIS → DHARMA → KARMA → MOKSHA

    For each file:
        - GENESIS: Init & Load (SYS_WAKE, LOAD_ROOT)
        - DHARMA: Validate & Align (COMPILE_AST, CHECK)
        - KARMA: Execute & Inject (EXEC_OP, STATE_SYNC)
        - MOKSHA: Release & Report (IO_FLUSH, AUDIT_SEAL)

    KALI YUGA GRACE:
        If DHARMA fails, we don't abort - we chant on gracefully.
        The Mahamantra cleanses ALL.

    Args:
        base_path: Base path to scan (default: vibe_core/)
        dry_run: If True, only report what would be done.
        use_scanner: If True (default), use MahajanaScanner SSOT.

    Returns:
        SankirtanResult with counts and details.
    """
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent

    # Scanner removed - folder IS wiring. Use direct file discovery.
    # (use_scanner flag ignored - scanner was backwards thinking)
    result = SankirtanResult(was_dry_run=dry_run)
    phase_counts: Dict[str, int] = {q.value: 0 for q in Quarter}

    logger.info(f"SANKIRTAN begins (dry_run={dry_run}) [LEGACY MODE]")
    logger.info("=" * 60)

    # Scan directories
    for dir_name in SCAN_DIRECTORIES:
        scan_dir = base_path / dir_name
        if not scan_dir.exists():
            continue

        for file_path in scan_dir.rglob("*.py"):
            # Skip patterns
            skip = False
            for pattern in SKIP_PATTERNS:
                if pattern in str(file_path):
                    skip = True
                    break
            if skip:
                result.files_skipped += KSETRAJNA
                continue

            result.files_scanned += KSETRAJNA

            # === THE 4-PHASE PIPELINE ===
            ctx = process_file_pipeline(file_path, dry_run=dry_run)

            # Track phase progression
            for phase_result in ctx.phases:
                phase_counts[phase_result.phase.value] += KSETRAJNA

            # Categorize result
            if ctx.was_already_owned:
                result.files_already_owned += KSETRAJNA
            elif ctx.all_phases_ok and ctx.is_valid:
                # Only count as injected if KARMA phase actually ran
                karma_phases = [p for p in ctx.phases if p.phase == Quarter.KARMA]
                if karma_phases and "inject" in karma_phases[0].message.lower():
                    result.files_injected += KSETRAJNA
                    if ctx.mahajana:
                        result.by_mahajana[ctx.mahajana] = result.by_mahajana.get(ctx.mahajana, 0) + KSETRAJNA

                    result.injections.append(
                        InjectionResult(
                            file_path=str(file_path),
                            mahajana=ctx.mahajana or "unknown",
                            position=ctx.position or 0,
                            success=True,
                            was_dry_run=dry_run,
                            message=f"{'Would inject' if dry_run else 'Injected'} {ctx.mahajana}",
                        )
                    )
                else:
                    result.files_skipped += KSETRAJNA
            elif ctx.error:
                result.files_failed += KSETRAJNA
                result.errors.append(f"{file_path}: {ctx.error}")
            else:
                result.files_skipped += KSETRAJNA

    logger.info("=" * 60)
    logger.info(
        f"SANKIRTAN complete: {result.files_injected} injected, {result.files_already_owned} owned, {result.files_failed} failed"
    )

    return result


def print_sankirtan_report(result: SankirtanResult) -> None:
    """Print human-readable sankirtan report."""
    mode = "[DRY-RUN]" if result.was_dry_run else "[LIVE]"

    print(f"""
{"=" * 60}
  SANKIRTAN REPORT {mode}
{"=" * 60}

  Files scanned:      {result.files_scanned}
  Files injected:     {result.files_injected}
  Files skipped:      {result.files_skipped}
  Already owned:      {result.files_already_owned}
  Failed:             {result.files_failed}

  BY MAHAJANA:
""")

    for pos in range(WORDS):
        mapping = MAHAMANTRA_POSITIONS[pos]
        guardian_name = mapping.guardian.value
        count = result.by_mahajana.get(guardian_name, 0)
        bar = "#" * min(count, 30)
        print(f"    {pos:2} {guardian_name:12} {bar} {count}")

    if result.errors:
        print(f"\n  ERRORS ({len(result.errors)}):")
        for err in result.errors[:PANCHA]:
            print(f"    - {err}")
        if len(result.errors) > PANCHA:
            print(f"    ... and {len(result.errors) - PANCHA} more")

    print(f"""
{"=" * 60}
  {"READY TO INJECT" if result.was_dry_run else "INJECTION COMPLETE"}
{"=" * 60}
""")


# =============================================================================
# CLI ENTRY POINT (Self-Manifesting via cli.yaml)
# =============================================================================


def cli_sankirtan(
    target: Optional[str] = None,
    live: bool = False,
    report: bool = False,
) -> Dict[str, object]:
    """
    CLI Entry Point for Sankirtan command.

    Called by CLILoaderProtocol via mahamantra/cli.yaml manifest.
    NO HARDCODING in UnifiedCLI - the truth is IN the module.

    Args:
        target: Filter by path or Mahajana name
        live: If True, execute injection. If False, dry-run.
        report: If True, print detailed report.

    Returns:
        Dict with injection results (machine-readable).
    """
    from pathlib import Path

    # Determine base path
    base_path: Optional[Path] = None
    if target:
        # Check if target is a path
        potential_path = Path(target)
        if potential_path.exists():
            base_path = potential_path
        # Otherwise target is a Mahajana filter (future feature)

    # Perform sankirtan
    dry_run = not live
    result = perform_sankirtan(base_path=base_path, dry_run=dry_run)

    # Print report if requested
    if report:
        print_sankirtan_report(result)

    # Return machine-readable result
    return {
        "success": True,
        "dry_run": result.was_dry_run,
        "files_scanned": result.files_scanned,
        "files_injected": result.files_injected,
        "files_skipped": result.files_skipped,
        "files_already_owned": result.files_already_owned,
        "files_failed": result.files_failed,
        "by_mahajana": result.by_mahajana,
        "errors": result.errors[:TEN] if result.errors else [],
    }


# =============================================================================
# SANKIRTAN SAMSKARA - Protocol-Based Implementation
# =============================================================================


@dataclass
class FilePayload:
    """Payload for file injection pipeline."""

    file_path: Path
    content: Optional[str] = None
    mahajana: Optional[str] = None
    position: Optional[int] = None
    was_already_owned: bool = False


class SankirtanSamskara:
    """
    Protocol-based Sankirtan implementation.

    IMPLEMENTS:
        - SamskaraProtocol[FilePayload, InjectionResult] (Lifecycle)
        - SankirtanProtocol (Capability)

    This class wraps the 4-phase functions in a proper protocol implementation.
    Use this instead of the raw functions for type-safe pipeline execution.

    USAGE:
        samskara = SankirtanSamskara(dry_run=True)
        executor = PipelineExecutor(samskara)

        # Single file
        ctx, result = executor.run(Path("my_file.py"))

        # Multiple files with iteration
        for phase, ctx in executor.iterate(Path("my_file.py")):
            print(f"{phase}: {ctx.payload.file_path}")
    """

    def __init__(self, dry_run: bool = True) -> None:
        self._dry_run = dry_run

    @property
    def __tattva__(self) -> TattvaDict:
        """Pancha Tattva definition."""
        return {
            "chaitanya": "Sankirtan Implementation",
            "nityananda": "Seed Protocol",
            "advaita": "Injection Logic",
            "gadadhara": "File Flow",
            "srivasa": "Permission Governance",
        }

    def calculate_genesis_byte(self, path: str, position: int) -> GenesisByte:
        """Calculate GenesisByte (Protocol Implementation)."""
        # Determine Mahajana from path if possible, or use unknown
        # This is a simplification, ideally we pass mahajana too
        mahajana = "unknown"
        mapping = get_mahajana_for_path(Path(path))
        if mapping:
            mahajana = mapping[0]

        hash_str = compute_genesis_hash(mahajana, position, path)
        vector = int(hash_str, WORDS)
        return {"hash": hash_str, "vector": vector, "is_valid": vector % PARAMPARA == 0}

    def inject(self, request: InjectionRequest) -> bool:
        """Inject DNA (Protocol Implementation)."""
        return inject_file(request["path"], request["mahajana"], dry_run=self._dry_run)

    def heal_wiring(self, base_path: Optional[str] = None, dry_run: bool = True) -> WiringStats:
        """Heal filesystem wiring (Protocol Implementation)."""
        # Convert str to Path if needed
        path_obj = Path(base_path) if base_path else None
        return heal_wiring(path_obj, dry_run=dry_run)

    def genesis(self, input_data: object) -> SamskaraPipelineContext[FilePayload]:
        """
        GENESIS: Init & Load the file.

        Wraps _genesis_phase logic.
        """
        if isinstance(input_data, Path):
            file_path = input_data
        elif isinstance(input_data, str):
            file_path = Path(input_data)
        else:
            raise TypeError(f"Expected Path or str, got {type(input_data)}")

        payload = FilePayload(file_path=file_path)

        try:
            if not file_path.exists():
                ctx = SamskaraPipelineContext(payload=payload)
                ctx.is_valid = False
                ctx.error = "File not found"
                return ctx

            payload.content = file_path.read_text()

            mapping = get_mahajana_for_path(file_path)
            if mapping:
                payload.mahajana, payload.position = mapping
            else:
                ctx = SamskaraPipelineContext(payload=payload)
                ctx.is_valid = False
                ctx.error = "Cannot determine mahajana"
                return ctx

            return SamskaraPipelineContext(payload=payload)

        except Exception as e:
            ctx = SamskaraPipelineContext(payload=payload)
            ctx.is_valid = False
            ctx.error = str(e)
            return ctx

    def dharma(self, ctx: SamskaraPipelineContext[FilePayload]) -> bool:
        """
        DHARMA: Validate the file.

        Wraps _dharma_phase logic with KALI YUGA GRACE.

        IMPORTANT: Returns True for "already owned" so karma() can
        return the proper InjectionResult. The payload.was_already_owned
        flag tells karma() what to do.
        """
        payload = ctx.payload

        if not ctx.is_valid or not payload.content:
            return False

        try:
            # Check syntax (graceful)
            try:
                ast.parse(payload.content)
            except SyntaxError as _exc:
                logger.exception("Unexpected error: %s", _exc)

            # Check for existing declaration
            if has_declaration(payload.content):
                payload.was_already_owned = True
                # Return True so karma() runs and returns "Already owned" result
                return True

            # Check file type
            if payload.file_path.suffix != ".py":
                return False

            return True

        except Exception:
            return False  # KALI YUGA GRACE

    def karma(self, ctx: SamskaraPipelineContext[FilePayload]) -> InjectionResult:
        """
        KARMA: Execute DNA injection.

        Wraps _karma_phase logic.
        """
        payload = ctx.payload

        if payload.was_already_owned:
            return InjectionResult(
                file_path=str(payload.file_path),
                mahajana=payload.mahajana or "unknown",
                position=payload.position or 0,
                success=True,
                was_dry_run=self._dry_run,
                message="Already owned",
            )

        if not ctx.is_valid or not payload.content or not payload.mahajana:
            return InjectionResult(
                file_path=str(payload.file_path),
                mahajana=payload.mahajana or "unknown",
                position=payload.position or 0,
                success=False,
                was_dry_run=self._dry_run,
                message="Not eligible",
            )

        try:
            new_content = inject_declaration(
                payload.content,
                payload.mahajana,
                payload.position or 0,
                file_path=str(payload.file_path),
            )

            if not self._dry_run:
                payload.file_path.write_text(new_content)

            return InjectionResult(
                file_path=str(payload.file_path),
                mahajana=payload.mahajana,
                position=payload.position or 0,
                success=True,
                was_dry_run=self._dry_run,
                message=f"{'Would inject' if self._dry_run else 'Injected'} {payload.mahajana}",
            )

        except Exception as e:
            return InjectionResult(
                file_path=str(payload.file_path),
                mahajana=payload.mahajana or "unknown",
                position=payload.position or 0,
                success=False,
                was_dry_run=self._dry_run,
                message=f"Injection failed: {e}",
            )

    def moksha(
        self,
        ctx: SamskaraPipelineContext[FilePayload],
        result: Optional[InjectionResult],
    ) -> None:
        """
        MOKSHA: Release & Report.

        Logs the final status.
        """
        payload = ctx.payload
        if result:
            logger.debug(f"[MOKSHA] {payload.file_path.name}: {result.message} [{ctx.phase_summary}]")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol-Based Implementation
    "FilePayload",
    "SankirtanSamskara",
    # 4-Phase Pipeline
    "PhaseResult",
    "PipelineContext",
    "process_file_pipeline",
    "iterate_sankirtan",
    # Result types
    "InjectionResult",
    "SankirtanResult",
    # Functions (SSOT)
    "chant_over_files",  # NEW: Takes files from Scanner
    "perform_sankirtan",  # Uses Scanner by default
    "get_mahajana_for_path",
    "has_declaration",
    "inject_declaration",
    "inject_file",
    "print_sankirtan_report",
    # CLI Entry Point
    "cli_sankirtan",
    # Constants
    "FOLDER_MAHAJANA_MAP",
    "heal_wiring",
]

# =============================================================================
# HEAL WIRING - The Royal Decree
# =============================================================================


def heal_wiring(base_path: Optional[Path] = None, dry_run: bool = True) -> Dict[str, int]:
    """
    HEAL WIRING: The King manages his territory.

    Scans all 16 Mahajana folders.
    Generates perfect __init__.py from StandardBlueprint.
    Overwrites if incorrect or missing.

    Args:
        base_path: Base path to vibe_core (default: auto-detect)
        dry_run: If True, only report.

    Returns:
        Stats dict (checked, healed, skipped, failed)
    """
    from vibe_core.mahamantra.protocols._blueprint import StandardBlueprint
    from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS

    if base_path is None:
        base_path = Path(__file__).parent.parent.parent

    stats = {"checked": 0, "healed": 0, "skipped": 0, "failed": 0}
    blueprint = StandardBlueprint()
    template = blueprint.get_template("__init__")

    logger.info(f"👑 HEAL WIRING (dry_run={dry_run})")

    for pos in MAHAMANTRA_POSITIONS:
        stats["checked"] += KSETRAJNA

        # Determine paths
        guardian = pos.guardian.value
        quarter = pos.quarter.value
        folder_path = base_path / "mahamantra" / quarter / guardian
        init_path = folder_path / "__init__.py"

        try:
            # Create folder if missing
            if not folder_path.exists():
                if not dry_run:
                    folder_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  Created folder: {quarter}/{guardian}")

            # Determine Service Class (Mapping Logic)
            # This logic maps guardian to service class/module
            service_class = f"{guardian.capitalize()}Service"
            # Special cases or standard mapping?
            # Standard: vibe_core.services.{guardian}_service
            service_module = f"vibe_core.services.{guardian}_service"

            # Special case: Nrisimha -> NrisimhaWatchdog
            if guardian == "nrisimha":
                service_class = "NrisimhaWatchdog"  # But we alias it as NrisimhaService in __init__ usually?
                # In previous patch we used:
                # if name == "NrisimhaService": from ... import NrisimhaWatchdog return NrisimhaWatchdog
                # So the class name exported is NrisimhaWatchdog, but accessed as Service?
                # Let's stick to the pattern I established: Alias = Service Name
                service_class = "NrisimhaService"
                service_module = "vibe_core.services.nrisimha"

            # Calculate Genesis Hash
            # Virtual path for hash calculation (relative to root)
            rel_path = f"vibe_core/mahamantra/{quarter}/{guardian}/__init__.py"
            genesis_hash = compute_genesis_hash(guardian, pos.index, rel_path)

            # Generate Content
            content = template["content_pattern"].format(
                mahajana_upper=guardian.upper(),
                position=pos.index,
                quarter_upper=quarter.upper(),
                opcode=pos.opcode.name if pos.opcode else "UNKNOWN",
                guardian_type="HEAD" if pos.is_head else "WORKER",
                vector=pos.parampara_vector,
                mahajana=guardian,
                quarter=quarter,
                genesis_hash=genesis_hash,
                service_class=service_class,
                service_module=service_module,
            )

            # Check existing
            needs_update = True
            if init_path.exists():
                current_content = init_path.read_text()
                # Simple check: if content is identical (ignoring whitespace maybe?)
                if current_content.strip() == content.strip():
                    needs_update = False

            if needs_update:
                if not dry_run:
                    init_path.write_text(content)
                    logger.info(f"  ✨ Healed: {quarter}/{guardian}/__init__.py")
                else:
                    logger.info(f"  Would heal: {quarter}/{guardian}/__init__.py")
                stats["healed"] += KSETRAJNA
            else:
                stats["skipped"] += KSETRAJNA

        except Exception as e:
            logger.error(f"  ❌ Failed {guardian}: {e}")
            stats["failed"] += KSETRAJNA

    return stats
