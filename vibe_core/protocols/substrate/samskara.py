"""
SAMSKARA PROTOCOL - The 4-Phase Pipeline
=========================================

"samskarah phaladah smritah"
"Samskaras (sacred rites/purification) yield their fruit through remembrance."

SAMSKARA = The Purification Process = The 4-Phase Pipeline

Every transformation in the system follows the CHATUH-SUTRA (4-Phase Rhythm):

    ┌─────────────────────────────────────────────────────────────────────────┐
    │ PHASE     │ QUARTER  │ FUNCTION           │ PYTHON ANALOGY            │
    ├───────────┼──────────┼────────────────────┼───────────────────────────┤
    │ GENESIS   │ 0-3      │ Init & Load        │ __init__, open()          │
    │ DHARMA    │ 4-7      │ Validate & Align   │ __bool__, validate()      │
    │ KARMA     │ 8-11     │ Execute & Transform│ __call__, process()       │
    │ MOKSHA    │ 12-15    │ Release & Return   │ __del__, close(), return  │
    └─────────────────────────────────────────────────────────────────────────┘

KALI YUGA GRACE:
    "In this age of Kali, the only means of deliverance is chanting the holy name."

    If DHARMA (validation) fails, we don't abort.
    We continue gracefully - the Mahamantra cleanses ALL.
    Errors are logged, not thrown.

USAGE:
    class MySankirtan(SamskaraProtocol[FileContext, InjectionResult]):
        def genesis(self, path: str) -> FileContext: ...
        def dharma(self, ctx: FileContext) -> bool: ...
        def karma(self, ctx: FileContext) -> InjectionResult: ...
        def moksha(self, result: InjectionResult) -> None: ...

    # Then use the pipeline
    pipeline = MySankirtan()
    for phase, ctx in pipeline.iterate(files):
        print(f"{phase}: {ctx}")

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself (Position 0 - Prithu)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa5c1f297"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import (
    Callable,
    Dict,
    Final,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    runtime_checkable,
)


# =============================================================================
# CONSTANTS - The Sacred Numbers
# =============================================================================

PARAMPARA: Final[int] = 37
PHASES: Final[int] = 4
POSITIONS_PER_PHASE: Final[int] = 4


# =============================================================================
# PHASE ENUM - The 4 Quarters as Process Phases
# =============================================================================

class Phase(str, Enum):
    """
    The 4 phases of the Samskara (purification) process.

    Maps directly to the 4 Quarters of the Mahamantra:
        GENESIS = Quarter 0 (Hare Krishna Hare Krishna)
        DHARMA  = Quarter 1 (Krishna Krishna Hare Hare)
        KARMA   = Quarter 2 (Hare Rama Hare Rama)
        MOKSHA  = Quarter 3 (Rama Rama Hare Hare)
    """
    GENESIS = "genesis"   # Init & Load
    DHARMA = "dharma"     # Validate & Align
    KARMA = "karma"       # Execute & Transform
    MOKSHA = "moksha"     # Release & Return

    @property
    def quarter_index(self) -> int:
        """Get the quarter index (0-3)."""
        return list(Phase).index(self)

    @property
    def position_range(self) -> Tuple[int, int]:
        """Get the position range for this phase."""
        start = self.quarter_index * POSITIONS_PER_PHASE
        return (start, start + POSITIONS_PER_PHASE)

    @property
    def parampara_vector(self) -> int:
        """Get the parampara vector for this phase."""
        return (self.quarter_index + 1) * PARAMPARA


# =============================================================================
# PHASE RESULT - Typed Result for Each Phase
# =============================================================================

class PhaseStatus(str, Enum):
    """Status of a phase execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    GRACEFUL = "graceful"  # Failed but continued (Kali Yuga Grace)


@dataclass
class PhaseResult:
    """
    Result of executing a single phase.

    WATERTIGHT: All fields explicitly typed.
    """
    phase: Phase
    status: PhaseStatus
    message: str
    duration_ms: float = 0.0
    data: Optional[Dict[str, object]] = None

    @property
    def success(self) -> bool:
        """Did the phase succeed (or gracefully continue)?"""
        return self.status in (PhaseStatus.SUCCESS, PhaseStatus.SKIPPED, PhaseStatus.GRACEFUL)

    @property
    def failed(self) -> bool:
        """Did the phase fail (hard failure, not graceful)?"""
        return self.status == PhaseStatus.FAILED


# =============================================================================
# CONTEXT - Pipeline Context (Generic)
# =============================================================================

C = TypeVar("C")  # Context type
R = TypeVar("R")  # Result type


@dataclass
class PipelineContext(Generic[C]):
    """
    Context passed through the 4-phase pipeline.

    Generic over the payload type C.
    """
    payload: C
    phases: List[PhaseResult] = field(default_factory=list)
    is_valid: bool = True
    error: Optional[str] = None

    def log_phase(
        self,
        phase: Phase,
        status: PhaseStatus,
        message: str,
        duration_ms: float = 0.0,
        data: Optional[Dict[str, object]] = None,
    ) -> None:
        """Log a phase result."""
        self.phases.append(PhaseResult(
            phase=phase,
            status=status,
            message=message,
            duration_ms=duration_ms,
            data=data,
        ))

    @property
    def current_phase(self) -> Optional[Phase]:
        """Get the current (last executed) phase."""
        if self.phases:
            return self.phases[-1].phase
        return None

    @property
    def all_phases_ok(self) -> bool:
        """Did all phases succeed?"""
        return all(p.success for p in self.phases)

    @property
    def phase_summary(self) -> str:
        """Get a summary string of all phases."""
        return " → ".join(
            f"{p.phase.value.upper()}:{'✓' if p.success else '✗'}"
            for p in self.phases
        )


# =============================================================================
# SAMSKARA PROTOCOL - The 4-Phase Pipeline Interface
# =============================================================================

@runtime_checkable
class SamskaraProtocol(Protocol[C, R]):
    """
    THE SAMSKARA PROTOCOL - Universal 4-Phase Pipeline.

    Every transformation in the system SHOULD implement this protocol.

    VEDA-4 MAPPING:
        genesis() → SHABDA (Reception/Input)
        dharma()  → PRATYAYA (Validation/Truth)
        karma()   → KARMA (Action/Execution)
        moksha()  → ARTHA (Meaning/Output)

    IMPLEMENTATION REQUIREMENTS:
        1. genesis() MUST return a context (never None)
        2. dharma() MUST return bool (validation result)
        3. karma() MUST return a result (the transformation output)
        4. moksha() MUST handle cleanup (even on failure)

    KALI YUGA GRACE:
        If dharma() returns False, the pipeline continues gracefully.
        karma() can check is_valid to skip transformation.
        moksha() always runs for cleanup.
    """

    def genesis(self, input_data: object) -> PipelineContext[C]:
        """
        PHASE 0: GENESIS - Init & Load

        Quarter: Hare Krishna Hare Krishna (positions 0-3)
        OpCodes: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, INIT_THREAD

        Actions:
            - Wake the system
            - Load input data
            - Allocate context
            - Initialize state

        Returns:
            PipelineContext with loaded payload
        """
        ...

    def dharma(self, ctx: PipelineContext[C]) -> bool:
        """
        PHASE 1: DHARMA - Validate & Align

        Quarter: Krishna Krishna Hare Hare (positions 4-7)
        OpCodes: COMPILE_AST, BIND_SYMBOL, TYPE_CHECK, DHARMA_TEST

        Actions:
            - Validate input
            - Check constraints
            - Verify alignment
            - Test dharma (is this right?)

        KALI YUGA GRACE:
            Return False to skip transformation, but DON'T raise.
            The pipeline continues gracefully.

        Returns:
            True if valid, False if should skip (graceful)
        """
        ...

    def karma(self, ctx: PipelineContext[C]) -> R:
        """
        PHASE 2: KARMA - Execute & Transform

        Quarter: Hare Rama Hare Rama (positions 8-11)
        OpCodes: EXEC_OP, EXTEND_CAP, STATE_SYNC, LEDGER_SIGN

        Actions:
            - Execute the transformation
            - Modify state
            - Produce results
            - Sign/seal the operation

        "karmaṇy evādhikāras te mā phaleṣu kadācana"
        "You have a right to perform action, but not to the fruits."

        Returns:
            The transformation result
        """
        ...

    def moksha(self, ctx: PipelineContext[C], result: Optional[R]) -> None:
        """
        PHASE 3: MOKSHA - Release & Return

        Quarter: Rama Rama Hare Hare (positions 12-15)
        OpCodes: YIELD_CPU, IO_FLUSH, LOG_EMIT, AUDIT_SEAL

        Actions:
            - Release resources
            - Flush I/O
            - Emit logs/reports
            - Seal audit trail

        "tyaktvā dehaṁ punar janma naiti"
        "Quitting the body, one attains liberation."

        NOTE: This ALWAYS runs, even if earlier phases failed.
        """
        ...


# =============================================================================
# PIPELINE EXECUTOR - Runs the 4-Phase Pipeline
# =============================================================================

class PipelineExecutor(Generic[C, R]):
    """
    Executes a SamskaraProtocol implementation through all 4 phases.

    Handles:
        - Phase sequencing (GENESIS → DHARMA → KARMA → MOKSHA)
        - Error handling (Kali Yuga Grace)
        - Timing and logging
        - Graceful degradation

    USAGE:
        executor = PipelineExecutor(my_samskara)
        result = executor.run(input_data)

        # Or iterate for real-time progress
        for phase, ctx in executor.iterate(input_data):
            print(f"{phase}: {ctx.phase_summary}")
    """

    def __init__(self, samskara: SamskaraProtocol[C, R]) -> None:
        self._samskara = samskara

    def run(self, input_data: object) -> Tuple[PipelineContext[C], Optional[R]]:
        """
        Run the complete 4-phase pipeline.

        Returns:
            Tuple of (final_context, result_or_none)
        """
        import time

        result: Optional[R] = None

        # GENESIS
        start = time.perf_counter()
        try:
            ctx = self._samskara.genesis(input_data)
            ctx.log_phase(
                Phase.GENESIS,
                PhaseStatus.SUCCESS,
                "Initialized",
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as e:
            # Create error context
            ctx = PipelineContext(payload=input_data)  # type: ignore
            ctx.is_valid = False
            ctx.error = str(e)
            ctx.log_phase(
                Phase.GENESIS,
                PhaseStatus.FAILED,
                f"Init failed: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
            )
            # Still run MOKSHA for cleanup
            self._samskara.moksha(ctx, None)
            return (ctx, None)

        # DHARMA
        start = time.perf_counter()
        try:
            is_valid = self._samskara.dharma(ctx)
            ctx.is_valid = is_valid
            if is_valid:
                ctx.log_phase(
                    Phase.DHARMA,
                    PhaseStatus.SUCCESS,
                    "Validated",
                    duration_ms=(time.perf_counter() - start) * 1000,
                )
            else:
                ctx.log_phase(
                    Phase.DHARMA,
                    PhaseStatus.GRACEFUL,
                    "Skipped (validation returned False)",
                    duration_ms=(time.perf_counter() - start) * 1000,
                )
        except Exception as e:
            # KALI YUGA GRACE: Log and continue
            ctx.is_valid = False
            ctx.log_phase(
                Phase.DHARMA,
                PhaseStatus.GRACEFUL,
                f"Validation error (graceful): {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
            )

        # KARMA (only if valid, but log either way)
        start = time.perf_counter()
        if ctx.is_valid:
            try:
                result = self._samskara.karma(ctx)
                ctx.log_phase(
                    Phase.KARMA,
                    PhaseStatus.SUCCESS,
                    "Executed",
                    duration_ms=(time.perf_counter() - start) * 1000,
                )
            except Exception as e:
                ctx.error = str(e)
                ctx.log_phase(
                    Phase.KARMA,
                    PhaseStatus.FAILED,
                    f"Execution failed: {e}",
                    duration_ms=(time.perf_counter() - start) * 1000,
                )
        else:
            ctx.log_phase(
                Phase.KARMA,
                PhaseStatus.SKIPPED,
                "Skipped (not valid)",
                duration_ms=0.0,
            )

        # MOKSHA (always runs)
        start = time.perf_counter()
        try:
            self._samskara.moksha(ctx, result)
            ctx.log_phase(
                Phase.MOKSHA,
                PhaseStatus.SUCCESS,
                f"Released [{ctx.phase_summary}]",
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as e:
            ctx.log_phase(
                Phase.MOKSHA,
                PhaseStatus.FAILED,
                f"Cleanup failed: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
            )

        return (ctx, result)

    def iterate(self, input_data: object) -> Iterator[Tuple[Phase, PipelineContext[C]]]:
        """
        Iterate through the pipeline, yielding after each phase.

        Useful for real-time progress tracking.

        Yields:
            Tuple of (current_phase, context)
        """
        import time

        result: Optional[R] = None

        # GENESIS
        start = time.perf_counter()
        try:
            ctx = self._samskara.genesis(input_data)
            ctx.log_phase(Phase.GENESIS, PhaseStatus.SUCCESS, "Initialized",
                         duration_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            ctx = PipelineContext(payload=input_data)  # type: ignore
            ctx.is_valid = False
            ctx.error = str(e)
            ctx.log_phase(Phase.GENESIS, PhaseStatus.FAILED, f"Init failed: {e}",
                         duration_ms=(time.perf_counter() - start) * 1000)
        yield (Phase.GENESIS, ctx)

        if not ctx.is_valid:
            # Short circuit but still run MOKSHA
            ctx.log_phase(Phase.DHARMA, PhaseStatus.SKIPPED, "Skipped")
            yield (Phase.DHARMA, ctx)
            ctx.log_phase(Phase.KARMA, PhaseStatus.SKIPPED, "Skipped")
            yield (Phase.KARMA, ctx)
            self._samskara.moksha(ctx, None)
            ctx.log_phase(Phase.MOKSHA, PhaseStatus.SUCCESS, "Released (error path)")
            yield (Phase.MOKSHA, ctx)
            return

        # DHARMA
        start = time.perf_counter()
        try:
            is_valid = self._samskara.dharma(ctx)
            ctx.is_valid = is_valid
            status = PhaseStatus.SUCCESS if is_valid else PhaseStatus.GRACEFUL
            ctx.log_phase(Phase.DHARMA, status, "Validated" if is_valid else "Skipped (graceful)",
                         duration_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            ctx.is_valid = False
            ctx.log_phase(Phase.DHARMA, PhaseStatus.GRACEFUL, f"Validation error: {e}",
                         duration_ms=(time.perf_counter() - start) * 1000)
        yield (Phase.DHARMA, ctx)

        # KARMA
        start = time.perf_counter()
        if ctx.is_valid:
            try:
                result = self._samskara.karma(ctx)
                ctx.log_phase(Phase.KARMA, PhaseStatus.SUCCESS, "Executed",
                             duration_ms=(time.perf_counter() - start) * 1000)
            except Exception as e:
                ctx.error = str(e)
                ctx.log_phase(Phase.KARMA, PhaseStatus.FAILED, f"Failed: {e}",
                             duration_ms=(time.perf_counter() - start) * 1000)
        else:
            ctx.log_phase(Phase.KARMA, PhaseStatus.SKIPPED, "Skipped (not valid)")
        yield (Phase.KARMA, ctx)

        # MOKSHA
        start = time.perf_counter()
        try:
            self._samskara.moksha(ctx, result)
            ctx.log_phase(Phase.MOKSHA, PhaseStatus.SUCCESS, f"Released [{ctx.phase_summary}]",
                         duration_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            ctx.log_phase(Phase.MOKSHA, PhaseStatus.FAILED, f"Cleanup failed: {e}",
                         duration_ms=(time.perf_counter() - start) * 1000)
        yield (Phase.MOKSHA, ctx)


# =============================================================================
# NULL IMPLEMENTATION - For Testing
# =============================================================================

class NullSamskara(SamskaraProtocol[str, str]):
    """
    Null implementation for testing.

    Passes everything through unchanged.
    """

    def genesis(self, input_data: object) -> PipelineContext[str]:
        return PipelineContext(payload=str(input_data))

    def dharma(self, ctx: PipelineContext[str]) -> bool:
        return True

    def karma(self, ctx: PipelineContext[str]) -> str:
        return ctx.payload

    def moksha(self, ctx: PipelineContext[str], result: Optional[str]) -> None:
        pass


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "PARAMPARA",
    "PHASES",
    "POSITIONS_PER_PHASE",
    # Enums
    "Phase",
    "PhaseStatus",
    # Types
    "PhaseResult",
    "PipelineContext",
    # Protocol
    "SamskaraProtocol",
    # Executor
    "PipelineExecutor",
    # Null Implementation
    "NullSamskara",
]
