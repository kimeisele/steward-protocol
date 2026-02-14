"""
GATE PROVIDERS — The 5 Watchers at the TattvaGates
====================================================

"pañca-tattvātmakaṁ kṛṣṇaṁ bhakta-rūpa-svarūpakam"

Each TattvaGate in lotus_core.__call__() now has a REAL provider.
Providers are Observer-Adapters: they receive the pipeline context,
perform validation/tracking/logging, but do NOT alter the flow.

GATE 0 — CHAITANYA (PARSE)    → MantraGateProvider    (input validation + seed tracking)
GATE 1 — NITYANANDA (VALIDATE) → StorageGateProvider   (substrate verification)
GATE 2 — ADVAITA (EXECUTE)     → InferGateProvider     (resonance tracking)
GATE 3 — GADADHARA (RESULT)    → SyncGateProvider      (routing verification)
GATE 4 — SRIVASA (SYNC)        → EnforceGateProvider   (governance enforcement via StateService)

Registration:
    wire_gate_providers()  — called once at boot, registers all 5 in TattvaRegistry.
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x5ad7f6c5"

import logging
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from pathlib import Path
    from vibe_core.state.state_service import StateServiceProtocol


logger = logging.getLogger("MAHAMANTRA.GATES")


# =============================================================================
# GUNA I/O POLICY — The Gate's Teeth
# =============================================================================
# The Vedic model (protocols/universal/guna.py, BG 14.5):
#
# VISHUDDHA:  S=0 R=0 T=0 V=1.0  — Transcendental. The Name itself. Bypasses.
# SATTVA:     S>R, S>T, V=0      — Material goodness. Read/observe only.
# RAJAS:      R>S, R>T, V=0      — Material passion. Write/create.
# TAMAS:      T>S, T>R, V=0      — Material ignorance. Destroy/flush.
# VOID:       S=0 R=0 T=0 V=0    — Mayavad. No existence. No right.
#
# The Guna is DERIVED from the OpCode (guna.py SSOT), not from text content.
# VISHUDDHA is checked via is_vishuddha() — chant/tick/mahamantra bypass.
# =============================================================================


class IOPolicy(Enum):
    """I/O policy derived from Guna. The Gate's teeth."""
    VISHUDDHA = "vishuddha"        # Transcendental: bypasses the Gate entirely
    CACHE_ONLY = "cache_only"      # SATTVA: RAM only, no disk touch
    WRITE_BEHIND = "write_behind"  # RAJAS: RAM cache, deferred flush
    SYNC_FLUSH = "sync_flush"      # TAMAS: Immediate disk write
    DENIED = "denied"              # VOID: No Guna = Mayavad = no right


# =============================================================================
# WATERTIGHT TYPES — No Any, No dict, No list
# =============================================================================

class ParseResult(TypedDict):
    valid: bool
    input_type: str
    parse_count: int
    reason: str

class ValidateResult(TypedDict):
    valid: bool
    seed: int
    validate_count: int
    reason: str

class InferResult(TypedDict):
    seed: int
    attractor: int
    attractor_frequency: int
    unique_attractors: int

class RouteResult(TypedDict):
    attractor: int
    position: int
    position_frequency: int

class EnforceResult(TypedDict):
    position: int
    seed: int
    attractor: int
    committed: bool
    enforce_count: int

class IOWriteResult(TypedDict):
    success: bool
    cached: bool
    flushed: bool
    actor: str
    file: str
    guna_policy: str
    reason: str

class AuditEntry(TypedDict, total=False):
    actor: str
    file: str
    allowed: bool
    cached: bool
    flushed: bool
    guna_policy: str
    denied_reason: str

class ParseStats(TypedDict):
    parse_count: int
    last_input_type: Optional[str]

class ValidateStats(TypedDict):
    validate_count: int
    rejection_count: int

class InferStats(TypedDict):
    infer_count: int
    unique_attractors: int
    top_attractors: list

class RouteStats(TypedDict):
    route_count: int
    position_distribution: Dict[int, int]

class EnforceStats(TypedDict):
    enforce_count: int
    last_position: Optional[int]
    last_seed: Optional[int]
    last_opcode: Optional[str]
    last_guna: Optional[str]
    state_service_available: bool
    writes_total: int
    writes_cached: int
    writes_flushed: int
    writes_denied: int
    sattva_blocks: int
    audit_log_size: int


# =============================================================================
# GATE 0: CHAITANYA — MantraGateProvider (PARSE / Identity)
# =============================================================================
# Observer at the entry gate. Validates input shape, tracks seed generation.

class MantraGateProvider:
    """Watcher at PARSE gate — validates and tracks incoming input."""

    __slots__ = ("_parse_count", "_last_input_type")

    def __init__(self) -> None:
        self._parse_count: int = 0
        self._last_input_type: Optional[str] = None

    def parse(self, input_data: object) -> ParseResult:
        """
        Observe the PARSE gate.

        Validates input is not None, tracks input type and count.
        Returns observation metadata (not used by pipeline — observer only).
        """
        self._parse_count += 1
        self._last_input_type = type(input_data).__name__

        if input_data is None:
            logger.warning("PARSE gate: received None input")
            return ParseResult(valid=False, reason="null_input", input_type="NoneType", parse_count=self._parse_count)

        logger.debug(
            "PARSE gate: input #%d type=%s",
            self._parse_count, self._last_input_type,
        )
        return ParseResult(
            valid=True,
            input_type=self._last_input_type,
            parse_count=self._parse_count,
            reason="",
        )

    @property
    def stats(self) -> ParseStats:
        return ParseStats(
            parse_count=self._parse_count,
            last_input_type=self._last_input_type,
        )


# =============================================================================
# GATE 1: NITYANANDA — StorageGateProvider (VALIDATE / Substrate)
# =============================================================================
# Observer at the validation gate. Verifies seed is within valid range.

class StorageGateProvider:
    """Watcher at VALIDATE gate — verifies seed integrity."""

    __slots__ = ("_validate_count", "_rejection_count")

    def __init__(self) -> None:
        self._validate_count: int = 0
        self._rejection_count: int = 0

    def validate(self, seed: int) -> ValidateResult:
        """
        Observe the VALIDATE gate.

        Checks seed is a valid integer within expected range.
        """
        self._validate_count += 1

        if not isinstance(seed, int):
            self._rejection_count += 1
            logger.warning("VALIDATE gate: seed is %s, not int", type(seed).__name__)
            return ValidateResult(valid=False, reason="non_integer_seed", seed=0, validate_count=self._validate_count)

        if seed < 0:
            self._rejection_count += 1
            logger.warning("VALIDATE gate: negative seed %d", seed)
            return ValidateResult(valid=False, reason="negative_seed", seed=seed, validate_count=self._validate_count)

        logger.debug("VALIDATE gate: seed=%d (#%d)", seed, self._validate_count)
        return ValidateResult(
            valid=True,
            seed=seed,
            validate_count=self._validate_count,
            reason="",
        )

    @property
    def stats(self) -> ValidateStats:
        return ValidateStats(
            validate_count=self._validate_count,
            rejection_count=self._rejection_count,
        )


# =============================================================================
# GATE 2: ADVAITA — InferGateProvider (EXECUTE / Bridge)
# =============================================================================
# Observer at the execution gate. Tracks attractor distribution.

class InferGateProvider:
    """Watcher at EXECUTE gate — tracks inference patterns."""

    __slots__ = ("_infer_count", "_attractor_seen")

    def __init__(self) -> None:
        self._infer_count: int = 0
        self._attractor_seen: Dict[int, int] = {}

    def infer(self, seed: int, attractor: int) -> InferResult:
        """
        Observe the EXECUTE gate.

        Tracks which attractors are being hit and how often.
        """
        self._infer_count += 1
        self._attractor_seen[attractor] = self._attractor_seen.get(attractor, 0) + 1

        logger.debug(
            "EXECUTE gate: seed=%d attractor=%d (seen %dx)",
            seed, attractor, self._attractor_seen[attractor],
        )
        return InferResult(
            seed=seed,
            attractor=attractor,
            attractor_frequency=self._attractor_seen[attractor],
            unique_attractors=len(self._attractor_seen),
        )

    @property
    def stats(self) -> InferStats:
        return InferStats(
            infer_count=self._infer_count,
            unique_attractors=len(self._attractor_seen),
            top_attractors=sorted(
                self._attractor_seen.items(), key=lambda x: x[1], reverse=True
            )[:5],
        )


# =============================================================================
# GATE 3: GADADHARA — SyncGateProvider (RESULT / Energy)
# =============================================================================
# Observer at the result gate. Tracks position distribution across the 16 words.

class SyncGateProvider:
    """Watcher at RESULT gate — tracks routing and energy flow."""

    __slots__ = ("_route_count", "_position_hits")

    def __init__(self) -> None:
        self._route_count: int = 0
        self._position_hits: Dict[int, int] = {}

    def route(self, attractor: int) -> RouteResult:
        """
        Observe the RESULT gate.

        Tracks which positions are being routed to.
        Position = attractor % 16 (same as lotus_core.__call__).
        """
        self._route_count += 1
        position = attractor % 16
        self._position_hits[position] = self._position_hits.get(position, 0) + 1

        logger.debug(
            "RESULT gate: attractor=%d → position=%d (hit %dx)",
            attractor, position, self._position_hits[position],
        )
        return RouteResult(
            attractor=attractor,
            position=position,
            position_frequency=self._position_hits[position],
        )

    @property
    def stats(self) -> RouteStats:
        return RouteStats(
            route_count=self._route_count,
            position_distribution=dict(sorted(self._position_hits.items())),
        )


# =============================================================================
# GATE 4: SRIVASA — EnforceGateProvider (SYNC / I/O Governance)
# =============================================================================
# CONTROLLER at the governance gate. All state I/O flows through here.
# This is the CRITICAL gate — where governance meets I/O.
#
# Two roles:
#   1. Pipeline observer (called by _fire_gate in lotus_core.__call__)
#   2. I/O controller (called by any module that wants to write state)
#
# Usage for state writers:
#   from vibe_core.mahamantra.substrate.gate_providers import get_sync_gate
#   gate = get_sync_gate()
#   gate.write("maha_state.json", data, actor="maha_state")

class EnforceGateProvider:
    """Controller at SYNC gate — governs all state I/O through StateService."""

    __slots__ = (
        "_enforce_count", "_state_service", "_last_position", "_last_seed",
        "_last_opcode", "_last_guna",
        "_writes_total", "_writes_denied", "_writes_cached", "_writes_flushed",
        "_sattva_blocks",
        "_audit_log",
    )

    def __init__(self) -> None:
        self._enforce_count: int = 0
        self._state_service: Optional["StateServiceProtocol"] = None
        self._last_position: Optional[int] = None
        self._last_seed: Optional[int] = None
        self._last_opcode: Optional[object] = None
        self._last_guna: Optional[object] = None
        self._writes_total: int = 0
        self._writes_denied: int = 0
        self._writes_cached: int = 0
        self._writes_flushed: int = 0
        self._sattva_blocks: int = 0
        self._audit_log: List[AuditEntry] = []

    def _get_state_service(self) -> Optional["StateServiceProtocol"]:
        """Lazy-resolve StateService. Falls back to direct import."""
        if self._state_service is not None:
            return self._state_service
        # Try DI registry first
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols import StateServiceProtocol
            svc = ServiceRegistry.get(StateServiceProtocol)
            if svc is not None:
                self._state_service = svc
                return svc
        except (ImportError, AttributeError, KeyError):
            pass
        # Fallback: direct import
        try:
            from vibe_core.state.state_service import get_state_service
            self._state_service = get_state_service()
        except (ImportError, RuntimeError):
            pass
        return self._state_service

    # =========================================================================
    # ROLE 1: Pipeline Observer (called by _fire_gate in lotus_core.__call__)
    # =========================================================================

    def enforce(self, position: int, seed: int, attractor: int,
                opcode: Optional[object] = None, guna: Optional[object] = None) -> EnforceResult:
        """
        Pipeline checkpoint at SYNC gate.

        Tracks governance events. Now Guna-aware: the gate knows
        the nature of the operation (SATTVA/RAJAS/TAMAS).

        The Guna is DERIVED from the OpCode, not from text content.
        See substrate/guna.py: "The Guna is DERIVED from the OpCode."
        """
        self._enforce_count += 1
        self._last_position = position
        self._last_seed = seed
        self._last_opcode = opcode
        self._last_guna = guna

        state_svc = self._get_state_service()
        committed = False
        if state_svc is not None:
            try:
                state_svc.mark_dirty(
                    state_svc.state_root / "gate_audit.json"
                )
                committed = True
            except (AttributeError, OSError) as exc:
                logger.debug("SYNC gate: StateService mark_dirty failed: %s", exc)

        guna_name = getattr(guna, 'name', str(guna)) if guna is not None else 'NONE'
        opcode_name = getattr(opcode, 'name', str(opcode)) if opcode is not None else 'NONE'
        logger.debug(
            "SYNC gate: position=%d seed=%d attractor=%d guna=%s opcode=%s committed=%s (#%d)",
            position, seed, attractor, guna_name, opcode_name, committed, self._enforce_count,
        )
        return EnforceResult(
            position=position,
            seed=seed,
            attractor=attractor,
            committed=committed,
            enforce_count=self._enforce_count,
        )

    # =========================================================================
    # ROLE 2: I/O Controller (called by any state writer)
    # =========================================================================
    # Ksetrajna: The Gate KNOWS the field and DECIDES.
    # The Guna determines the I/O policy. No Guna = no write.
    # =========================================================================

    # Guna → IOPolicy LUT. Three material entries. Not in table = DENIED.
    _GUNA_POLICY: Dict[int, IOPolicy] = {}  # populated at module load

    @staticmethod
    def _resolve_policy(guna: object, *, actor: str = "") -> IOPolicy:
        """
        Derive I/O policy from Guna. The full Vedic model.

        VISHUDDHA → VISHUDDHA  (transcendental: chant/tick/mahamantra bypass)
        SATTVA    → CACHE_ONLY (material goodness: read-only, no disk)
        RAJAS     → WRITE_BEHIND (material passion: write, deferred flush)
        TAMAS     → SYNC_FLUSH (material ignorance: destroy, immediate flush)
        None/VOID → DENIED    (Mayavad: no Guna = no existence = no right)
        """
        from vibe_core.mahamantra.substrate.guna import is_vishuddha
        if actor and is_vishuddha(actor):
            return IOPolicy.VISHUDDHA
        if guna is None:
            return IOPolicy.DENIED
        try:
            guna_val = int(guna)
        except (ValueError, TypeError):
            return IOPolicy.DENIED
        return EnforceGateProvider._GUNA_POLICY.get(guna_val, IOPolicy.DENIED)

    def write(
        self,
        filename: str,
        data: object,
        *,
        actor: str = "unknown",
        guna: object = None,
        create_backup: bool = True,
    ) -> IOWriteResult:
        """
        Governed state write. ALL state I/O should flow through here.

        The Guna determines the I/O policy (BG 14.5):
            VISHUDDHA → Bypass (the Name IS the source, no gate holds it)
            SATTVA    → DENIED (read-only operations don't write)
            RAJAS     → Write to RAM cache (deferred disk flush)
            TAMAS     → Write to RAM cache + immediate sync flush to disk
            None/VOID → DENIED (Mayavad: no Guna = no right to write)

        Args:
            filename: State filename (e.g. "maha_state.json")
            data: JSON-serializable data to write
            actor: Who is writing (for audit trail)
            guna: The Guna of the operation (from OpCode). Determines policy.
            create_backup: Whether StateService should create backup

        Returns:
            IOWriteResult with typed success/failure metadata
        """
        self._writes_total += 1
        policy = self._resolve_policy(guna, actor=actor)

        # ── VISHUDDHA: The Name transcends the Gate. No confirmation needed. ──
        # Falls through to RAJAS path (write-behind) but with vishuddha audit.
        if policy == IOPolicy.VISHUDDHA:
            policy_for_write = IOPolicy.WRITE_BEHIND  # mechanism is Rajas
            # but the AUDIT records it as vishuddha (transcendental origin)
            return self._do_write(
                filename, data, actor=actor, policy=policy,
                mechanism=policy_for_write, create_backup=create_backup,
            )

        # ── DENIED or SATTVA: No right to write. ──
        if policy in (IOPolicy.DENIED, IOPolicy.CACHE_ONLY):
            reason = "void_no_guna" if policy == IOPolicy.DENIED else "sattva_read_only"
            if policy == IOPolicy.CACHE_ONLY:
                self._sattva_blocks += 1
            self._writes_denied += 1
            self._record_audit(AuditEntry(
                actor=actor, file=filename, allowed=False,
                guna_policy=policy.value, denied_reason=reason,
            ))
            logger.debug(
                "SYNC I/O BLOCKED: %s tried to write %s (%s)",
                actor, filename, reason,
            )
            return IOWriteResult(
                success=False, cached=False, flushed=False,
                actor=actor, file=filename,
                guna_policy=policy.value, reason=reason,
            )

        # ── RAJAS / TAMAS: Material write path ──
        return self._do_write(
            filename, data, actor=actor, policy=policy,
            mechanism=policy, create_backup=create_backup,
        )

    def _do_write(
        self,
        filename: str,
        data: object,
        *,
        actor: str,
        policy: IOPolicy,
        mechanism: IOPolicy,
        create_backup: bool,
    ) -> IOWriteResult:
        """
        Internal write executor. Separated from policy decision.

        Args:
            policy: The Guna-derived policy (for audit — e.g. VISHUDDHA)
            mechanism: The actual I/O mechanism (WRITE_BEHIND or SYNC_FLUSH)
        """
        state_svc = self._get_state_service()
        if state_svc is None:
            self._writes_denied += 1
            self._record_audit(AuditEntry(
                actor=actor, file=filename, allowed=False,
                guna_policy=policy.value, denied_reason="no_state_service",
            ))
            return IOWriteResult(
                success=False, cached=False, flushed=False,
                actor=actor, file=filename,
                guna_policy=policy.value, reason="no_state_service",
            )

        try:
            state_svc.save(filename, data, create_backup=create_backup)
            self._writes_cached += 1
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("SYNC I/O: StateService.save failed for %s: %s", filename, exc)
            self._writes_denied += 1
            self._record_audit(AuditEntry(
                actor=actor, file=filename, allowed=False,
                guna_policy=policy.value, denied_reason=str(exc),
            ))
            return IOWriteResult(
                success=False, cached=False, flushed=False,
                actor=actor, file=filename,
                guna_policy=policy.value, reason=str(exc),
            )

        flushed = False
        if mechanism == IOPolicy.SYNC_FLUSH:
            try:
                state_svc.flush(filename)
                self._writes_flushed += 1
                flushed = True
            except (OSError, ValueError, RuntimeError) as exc:
                logger.warning("SYNC I/O: TAMAS flush failed for %s: %s", filename, exc)

        self._record_audit(AuditEntry(
            actor=actor, file=filename, allowed=True,
            cached=True, flushed=flushed, guna_policy=policy.value,
        ))
        return IOWriteResult(
            success=True, cached=True, flushed=flushed,
            actor=actor, file=filename,
            guna_policy=policy.value, reason="",
        )

    # =========================================================================
    # ROLE 3: Source File Writer (called by HealingIntentResolver)
    # =========================================================================
    # The Healing Pipeline needs to write Python source, NOT state JSON.
    # This is DIFFERENT from write() which uses StateService.
    # write_source() still enforces Guna policy + audit trail.
    # RAJAS = allowed (healing commit is an act of creation).
    # SATTVA = blocked (analysis doesn't touch disk).
    # =========================================================================

    def write_source(
        self,
        file_path: "Path",
        content: str,
        *,
        actor: str = "unknown",
        guna: object = None,
        backup: bool = True,
    ) -> IOWriteResult:
        """
        Governed source-file write. For healing Maya-Sync.

        Same Guna policy as write(), but writes Python source to disk
        instead of going through StateService.

        Args:
            file_path: Absolute path to the Python source file.
            content: The reconstructed source code to write.
            actor: Who is writing (for audit trail).
            guna: The Guna of the operation. RAJAS required for writes.
            backup: If True, create .bak before overwriting.

        Returns:
            IOWriteResult with typed success/failure metadata.
        """
        from pathlib import Path as _Path

        self._writes_total += 1
        policy = self._resolve_policy(guna, actor=actor)
        fname = str(file_path)

        # ── VISHUDDHA: Transcendental bypass → falls through to write ──
        if policy == IOPolicy.VISHUDDHA:
            return self._do_write_source(
                _Path(file_path), content, actor=actor,
                policy=policy, backup=backup,
            )

        # ── DENIED or SATTVA: No right to write source. ──
        if policy in (IOPolicy.DENIED, IOPolicy.CACHE_ONLY):
            reason = "void_no_guna" if policy == IOPolicy.DENIED else "sattva_read_only"
            if policy == IOPolicy.CACHE_ONLY:
                self._sattva_blocks += 1
            self._writes_denied += 1
            self._record_audit(AuditEntry(
                actor=actor, file=fname, allowed=False,
                guna_policy=policy.value, denied_reason=reason,
            ))
            logger.debug(
                "SYNC SOURCE BLOCKED: %s tried to write %s (%s)",
                actor, fname, reason,
            )
            return IOWriteResult(
                success=False, cached=False, flushed=False,
                actor=actor, file=fname,
                guna_policy=policy.value, reason=reason,
            )

        # ── RAJAS / TAMAS: Material write path (source file) ──
        return self._do_write_source(
            _Path(file_path), content, actor=actor,
            policy=policy, backup=backup,
        )

    def _do_write_source(
        self,
        file_path: "Path",
        content: str,
        *,
        actor: str,
        policy: IOPolicy,
        backup: bool,
    ) -> IOWriteResult:
        """Internal source-file write executor."""
        import shutil
        fname = str(file_path)

        try:
            # Backup before overwrite
            if backup and file_path.exists():
                bak = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, bak)

            # Write
            file_path.write_text(content, encoding="utf-8")
            self._writes_flushed += 1

            self._record_audit(AuditEntry(
                actor=actor, file=fname, allowed=True,
                cached=False, flushed=True, guna_policy=policy.value,
            ))
            logger.debug(
                "SYNC SOURCE OK: %s wrote %s (policy=%s)",
                actor, fname, policy.value,
            )
            return IOWriteResult(
                success=True, cached=False, flushed=True,
                actor=actor, file=fname,
                guna_policy=policy.value, reason="",
            )

        except OSError as exc:
            self._writes_denied += 1
            self._record_audit(AuditEntry(
                actor=actor, file=fname, allowed=False,
                guna_policy=policy.value, denied_reason=str(exc),
            ))
            logger.warning("SYNC SOURCE FAILED: %s → %s: %s", actor, fname, exc)
            return IOWriteResult(
                success=False, cached=False, flushed=False,
                actor=actor, file=fname,
                guna_policy=policy.value, reason=str(exc),
            )

    def flush(self, filename: Optional[str] = None) -> int:
        """
        Flush cached state to disk via StateService.

        Args:
            filename: Specific file to flush, or None for all.

        Returns:
            Number of files flushed.
        """
        state_svc = self._get_state_service()
        if state_svc is None:
            return 0
        try:
            return state_svc.flush(filename)
        except (OSError, ValueError, RuntimeError) as exc:
            logger.error("SYNC I/O: flush failed: %s", exc)
            return 0

    def load(self, filename: str, default: object = None) -> object:
        """
        Governed state read. Reads from StateService cache first.

        Args:
            filename: State filename to load
            default: Default value if not found

        Returns:
            Loaded data or default
        """
        state_svc = self._get_state_service()
        if state_svc is not None:
            try:
                return state_svc.load(filename, default=default)
            except (OSError, ValueError, KeyError) as exc:
                logger.debug("SYNC I/O: load failed for %s: %s", filename, exc)
        return default

    def _record_audit(self, entry: AuditEntry) -> None:
        """Append to bounded audit log (max 1000 entries)."""
        self._audit_log.append(entry)
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-500:]

    @property
    def stats(self) -> EnforceStats:
        return EnforceStats(
            enforce_count=self._enforce_count,
            last_position=self._last_position,
            last_seed=self._last_seed,
            last_opcode=getattr(self._last_opcode, 'name', None),
            last_guna=getattr(self._last_guna, 'name', None),
            state_service_available=self._get_state_service() is not None,
            writes_total=self._writes_total,
            writes_cached=self._writes_cached,
            writes_flushed=self._writes_flushed,
            writes_denied=self._writes_denied,
            sattva_blocks=self._sattva_blocks,
            audit_log_size=len(self._audit_log),
        )


# =============================================================================
# GUNA → IOPOLICY LUT (populated once at module load, no if-else)
# =============================================================================
# Import Guna HERE (not at top) to avoid circular imports.
# The LUT is the SSOT. If it's not in the table, it's DENIED.

def _populate_guna_policy_lut() -> None:
    """Build the Guna→IOPolicy lookup table. Called once at module load."""
    from vibe_core.mahamantra.substrate.guna import Guna
    EnforceGateProvider._GUNA_POLICY = {
        int(Guna.SATTVA): IOPolicy.CACHE_ONLY,
        int(Guna.RAJAS): IOPolicy.WRITE_BEHIND,
        int(Guna.TAMAS): IOPolicy.SYNC_FLUSH,
    }

_populate_guna_policy_lut()


# =============================================================================
# I/O SENTINEL — Armed at module load, not at boot
# =============================================================================
# The sentinel watches json.dump/json.dumps calls system-wide.
# Armed here because gate_providers is imported by every mahamantra path.
# No boot dependency. No wiring step. Just: import → armed.

def _arm_io_sentinel() -> None:
    """Arm the I/O sentinel. Called once at module load."""
    from vibe_core.mahamantra.substrate.io_sentinel import arm
    arm()

_arm_io_sentinel()


# =============================================================================
# WIRING — Register all 5 providers at boot
# =============================================================================

# Singleton instances (one per process, like VenuOrchestrator)
_PROVIDERS: Optional[Dict[str, object]] = None


def get_providers() -> Dict[str, object]:
    """Get or create the singleton gate provider instances."""
    global _PROVIDERS
    if _PROVIDERS is None:
        _PROVIDERS = {
            "mantra_gate": MantraGateProvider(),
            "storage_gate": StorageGateProvider(),
            "infer_gate": InferGateProvider(),
            "sync_gate": SyncGateProvider(),
            "enforce_gate": EnforceGateProvider(),
        }
    return _PROVIDERS


def get_sync_gate() -> EnforceGateProvider:
    """Get the singleton SYNC gate (I/O Controller).

    This is the ONE entry point for governed state I/O.
    Any module that wants to write state calls this.

    Usage:
        gate = get_sync_gate()
        gate.write("my_state.json", data, actor="my_module")
    """
    return get_providers()["enforce_gate"]  # type: ignore[return-value]


def wire_gate_providers() -> int:
    """
    Register all 5 gate providers in TattvaRegistry.

    Called once at boot. Returns number of successfully registered providers.
    Safe to call multiple times (idempotent — checks existing registrations).
    """
    from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
    from vibe_core.mahamantra.substrate.tattva_registry import get_registry

    registry = get_registry()
    providers = get_providers()

    gate_map = {
        "mantra_gate": TattvaGate.PARSE,
        "storage_gate": TattvaGate.VALIDATE,
        "infer_gate": TattvaGate.EXECUTE,
        "sync_gate": TattvaGate.RESULT,
        "enforce_gate": TattvaGate.SYNC,
    }

    registered = 0
    for name, gate in gate_map.items():
        # Skip if already registered
        if registry.gate_provider_count(gate) > 0:
            existing = registry.get_gate_providers(gate)
            if any(n == name for n, _ in existing):
                continue

        obj = providers[name]
        if registry.register_gate_provider(name, obj, gate):
            registered += 1
            logger.info("Gate provider wired: %s → %s", name, gate.name)
        else:
            logger.error("Gate provider FAILED: %s → %s", name, gate.name)

    if registered:
        logger.info("🚪 %d gate providers wired (5 gates armed)", registered)

    return registered


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IOPolicy",
    "MantraGateProvider",
    "StorageGateProvider",
    "InferGateProvider",
    "SyncGateProvider",
    "EnforceGateProvider",
    "get_providers",
    "get_sync_gate",
    "wire_gate_providers",
]
