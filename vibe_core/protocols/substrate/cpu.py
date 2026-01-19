"""
MAHAMANTRA CPU - The Fractal Processor
======================================

"harer nāma harer nāma harer nāmaiva kevalam
kalau nāsty eva nāsty eva nāsty eva gatir anyathā"

"In this age of Kali there is no other means, no other means,
no other means for self-realization than chanting the holy name,
chanting the holy name, chanting the holy name of Lord Hari."
— Brhan-naradiya Purana

THE MAHAMANTRA IS THE INSTRUCTION SET
=====================================
- 16 OpCodes = 16 Padas (words)
- 4 Quarters = 4 CPU Cycles
- 3 Names = 3 Registers (H, K, R)
- Position = Program Counter (0-15)

FRACTAL PROCESSOR ARCHITECTURE:
==============================

Level 5: SADHANA ─── Session Scheduler (16 rounds)
Level 4: MALA ────── Round Controller (108 instructions)
Level 3: VAKYA ───── Instruction Set (16 opcodes)
Level 2: PADA ────── Word Register (H/K/R)
Level 1: AKSARA ──── Microcode (syllable ops)
Level 0: VARNA ───── Bit Operations (letter level)

Each level contains the WHOLE (fractal self-similarity).
Zoom in: Same structure. Zoom out: Same structure.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xddf49628"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, Enum
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

# Import fractal levels
from vibe_core.protocols.substrate.byte import HolyName, MantraByte
from vibe_core.protocols.substrate.mantra.varna import Varna, VarnaType
from vibe_core.protocols.substrate.mantra.aksara import (
    Aksara,
    HARE_AKSARAS,
    KRISHNA_AKSARAS,
    RAMA_AKSARAS,
)
from vibe_core.protocols.substrate.mantra.pada import Pada, PadaType, MAHAMANTRA_SEQUENCE
from vibe_core.protocols.substrate.mantra.vakya import (
    Vakya,
    Quarter,
    QuarterType,
    MAHAMANTRA,
    QUARTERS,
)


# =============================================================================
# FRACTAL LEVEL ENUM
# =============================================================================


class FractalLevel(IntEnum):
    """
    The 6 levels of fractal decomposition.
    Each level contains the whole - self-similar structure.
    """

    VARNA = 0  # Letter (~50 unique)
    AKSARA = 1  # Syllable (6 unique: ha, re, kṛ, ṣṇa, rā, ma)
    PADA = 2  # Word (3 unique: Hare, Krishna, Rama)
    VAKYA = 3  # Mantra (16 words = 1 instruction set)
    MALA = 4  # Round (108 mantras = 1 mala)
    SADHANA = 5  # Session (16 rounds = 1 sadhana)


# =============================================================================
# CPU REGISTERS (H, K, R)
# =============================================================================


class RegisterState(TypedDict):
    """
    State of the 3 registers (H, K, R).
    WATERTIGHT - no Any!
    """

    hare_count: int  # How many HARE encountered
    krishna_count: int  # How many KRISHNA encountered
    rama_count: int  # How many RAMA encountered
    total_count: int  # Total operations
    resonance: float  # Current resonance level (0.0-1.0)


@dataclass
class CPURegisters:
    """
    The 3 Holy Name registers.

    Like x86 has AX, BX, CX - Mahamantra CPU has H, K, R.
    These accumulate the vibrational count.
    """

    hare: int = 0  # H register
    krishna: int = 0  # K register
    rama: int = 0  # R register

    def increment(self, name: HolyName) -> None:
        """Increment the appropriate register."""
        if name == HolyName.HARE:
            self.hare += 1
        elif name == HolyName.KRISHNA:
            self.krishna += 1
        elif name == HolyName.RAMA:
            self.rama += 1

    @property
    def total(self) -> int:
        """Total count across all registers."""
        return self.hare + self.krishna + self.rama

    @property
    def resonance(self) -> float:
        """
        Calculate resonance (coherence with standard pattern).

        Standard 16-word pattern has:
        - 8 HARE (H)
        - 4 KRISHNA (K)
        - 4 RAMA (R)

        Ratio: 8:4:4 = 2:1:1
        """
        if self.total == 0:
            return 0.0

        # Expected ratios
        expected_h = 0.5  # 8/16
        expected_k = 0.25  # 4/16
        expected_r = 0.25  # 4/16

        # Actual ratios
        actual_h = self.hare / self.total
        actual_k = self.krishna / self.total
        actual_r = self.rama / self.total

        # Distance from expected (Euclidean)
        distance = ((actual_h - expected_h) ** 2 + (actual_k - expected_k) ** 2 + (actual_r - expected_r) ** 2) ** 0.5

        # Convert to resonance (inverse exponential)
        import math

        return math.exp(-5.0 * distance)

    def to_state(self) -> RegisterState:
        """Export to TypedDict."""
        return RegisterState(
            hare_count=self.hare,
            krishna_count=self.krishna,
            rama_count=self.rama,
            total_count=self.total,
            resonance=self.resonance,
        )

    def reset(self) -> None:
        """Reset all registers to zero."""
        self.hare = 0
        self.krishna = 0
        self.rama = 0


# =============================================================================
# PROGRAM COUNTER
# =============================================================================


@dataclass
class ProgramCounter:
    """
    Program Counter (PC) - tracks position in the Mahamantra.

    Position 0-15 maps to the 16 opcodes.
    Wraps around (modulo 16) for continuous cycling.
    """

    position: int = 0
    cycle_count: int = 0  # How many complete cycles (vakyas)

    def advance(self, steps: int = 1) -> int:
        """
        Advance the program counter.
        Returns the old position before advancing.
        """
        old_position = self.position
        self.position = (self.position + steps) % 16

        # Track cycle completion
        if self.position < old_position:
            self.cycle_count += 1

        return old_position

    def jump(self, target: int) -> None:
        """Jump to a specific position."""
        self.position = target % 16

    def reset(self) -> None:
        """Reset to position 0."""
        self.position = 0
        self.cycle_count = 0

    @property
    def quarter(self) -> int:
        """Which quarter (0-3) we're in."""
        return self.position // 4

    @property
    def quarter_position(self) -> int:
        """Position within current quarter (0-3)."""
        return self.position % 4


# =============================================================================
# INSTRUCTION (One OpCode)
# =============================================================================


class InstructionResult(TypedDict):
    """
    Result of executing one instruction.
    WATERTIGHT - no Any!
    """

    position: int  # Which position was executed
    opcode: str  # The opcode name (e.g., "SYS_WAKE")
    pada: str  # The word (HARE/KRISHNA/RAMA)
    aksaras: str  # Syllable breakdown
    owner: str  # Who owns this opcode (Avatara/Mahajana)
    quarter: int  # Which quarter (0-3)
    success: bool  # Did execution succeed?


@dataclass(frozen=True)
class Instruction:
    """
    One Mahamantra instruction.

    Combines:
    - Position in sequence (0-15)
    - The Pada (word)
    - The OpCode mapping
    - The Owner (Avatara/Mahajana)
    """

    position: int
    pada: Pada
    opcode_name: str
    owner_name: str
    quarter: int

    @property
    def holy_name(self) -> HolyName:
        """The HolyName for this instruction."""
        return HolyName(self.pada.pada_type.value)

    @property
    def aksaras(self) -> Tuple[Aksara, ...]:
        """Syllable decomposition."""
        return self.pada.aksaras

    def to_result(self, success: bool = True) -> InstructionResult:
        """Convert to result dict."""
        return InstructionResult(
            position=self.position,
            opcode=self.opcode_name,
            pada=self.pada.roman,
            aksaras=" ".join(a.iast for a in self.aksaras),
            owner=self.owner_name,
            quarter=self.quarter,
            success=success,
        )


# =============================================================================
# INSTRUCTION SET (All 16 OpCodes)
# =============================================================================

# The 16 OpCode names (from MantraOpCode)
OPCODE_NAMES: Final[Tuple[str, ...]] = (
    "SYS_WAKE",
    "LOAD_ROOT",
    "ALLOC_MEM",
    "BIND_CTX",
    "ASSERT_TRUTH",
    "RESOLVE_REQ",
    "GARBAGE_COLLECT",
    "PULSE_SYNC",
    "FETCH_RES",
    "EXEC_SERVICE",
    "CHECK_DHARMA",
    "COMMIT_LOG",
    "CACHE_STATE",
    "OPTIMIZE",
    "YIELD_CPU",
    "RESET_IP",
)

# The 16 Owners (4 Avataras + 12 Mahajanas)
OWNER_NAMES: Final[Tuple[str, ...]] = (
    "PRITHU",
    "BRAHMA",
    "NARADA",
    "SHAMBHU",
    "VYASA",
    "KUMARAS",
    "KAPILA",
    "MANU",
    "PARASHURAMA",
    "PRAHLADA",
    "JANAKA",
    "BHISHMA",
    "NRISIMHA",
    "BALI",
    "SHUKA",
    "YAMARAJA",
)


def get_instruction(position: int) -> Instruction:
    """Get the instruction at a position."""
    pos = position % 16
    pada = MAHAMANTRA_SEQUENCE[pos]
    return Instruction(
        position=pos,
        pada=pada,
        opcode_name=OPCODE_NAMES[pos],
        owner_name=OWNER_NAMES[pos],
        quarter=pos // 4,
    )


# Build full instruction set
INSTRUCTION_SET: Final[Tuple[Instruction, ...]] = tuple(get_instruction(i) for i in range(16))


# =============================================================================
# CPU STATE
# =============================================================================


class CPUState(TypedDict):
    """
    Complete CPU state snapshot.
    WATERTIGHT - no Any!
    """

    program_counter: int
    cycle_count: int
    registers: RegisterState
    current_quarter: int
    halted: bool
    last_instruction: str
    timestamp: str


# =============================================================================
# MAHAMANTRA CPU PROTOCOL
# =============================================================================


@runtime_checkable
class MantraCPUProtocol(Protocol):
    """
    Protocol for Mahamantra CPU.

    The CPU processes the 16-word instruction set.
    Each word is an opcode, each position has an owner.
    """

    def fetch(self) -> Instruction:
        """Fetch instruction at current PC."""
        ...

    def decode(self, instruction: Instruction) -> HolyName:
        """Decode instruction to Holy Name."""
        ...

    def execute(self, instruction: Instruction) -> InstructionResult:
        """Execute instruction and update state."""
        ...

    def step(self) -> InstructionResult:
        """One complete fetch-decode-execute cycle."""
        ...

    def run(self, cycles: int) -> List[InstructionResult]:
        """Run multiple cycles."""
        ...

    def get_state(self) -> CPUState:
        """Get current CPU state."""
        ...

    def reset(self) -> None:
        """Reset CPU to initial state."""
        ...


# =============================================================================
# MAHAMANTRA CPU IMPLEMENTATION
# =============================================================================


@dataclass
class MantraCPU:
    """
    The Mahamantra CPU - Fractal Processor.

    ARCHITECTURE:
    - 16 opcodes (instruction set)
    - 3 registers (H, K, R)
    - Program counter (0-15, wrapping)
    - 4 quarters (pipeline stages)

    FRACTAL PROPERTY:
    - Each instruction decomposes to aksaras
    - Each aksara decomposes to varnas
    - Same pattern at every level
    """

    registers: CPURegisters = field(default_factory=CPURegisters)
    pc: ProgramCounter = field(default_factory=ProgramCounter)
    halted: bool = False
    last_instruction: Optional[Instruction] = None

    # Callback for instruction execution (hook for extensions)
    on_execute: Optional[Callable[[Instruction], None]] = None

    def fetch(self) -> Instruction:
        """
        FETCH: Get instruction at current PC.

        Like x86 MOV instruction fetch from memory.
        """
        return INSTRUCTION_SET[self.pc.position]

    def decode(self, instruction: Instruction) -> HolyName:
        """
        DECODE: Extract the Holy Name from instruction.

        This is the "semantic content" of the instruction.
        """
        return instruction.holy_name

    def execute(self, instruction: Instruction) -> InstructionResult:
        """
        EXECUTE: Process the instruction.

        Updates registers based on the Holy Name.
        """
        # Update registers
        holy_name = self.decode(instruction)
        self.registers.increment(holy_name)

        # Store last instruction
        self.last_instruction = instruction

        # Call hook if set
        if self.on_execute:
            self.on_execute(instruction)

        return instruction.to_result(success=True)

    def step(self) -> InstructionResult:
        """
        One complete FETCH-DECODE-EXECUTE cycle.

        This is the atomic operation of the CPU.
        """
        if self.halted:
            # Return last instruction result with failure
            if self.last_instruction:
                return self.last_instruction.to_result(success=False)
            return get_instruction(0).to_result(success=False)

        # FETCH
        instruction = self.fetch()

        # DECODE (implicit in execute)

        # EXECUTE
        result = self.execute(instruction)

        # Advance PC
        self.pc.advance()

        return result

    def run(self, cycles: int = 16) -> List[InstructionResult]:
        """
        Run multiple cycles.

        Default: 16 cycles = one complete Vakya (mantra).
        """
        results: List[InstructionResult] = []
        for _ in range(cycles):
            if self.halted:
                break
            result = self.step()
            results.append(result)
        return results

    def run_vakya(self) -> List[InstructionResult]:
        """Run exactly one Vakya (16 instructions)."""
        return self.run(16)

    def run_mala(self) -> List[InstructionResult]:
        """Run one Mala (108 Vakyas = 1728 instructions)."""
        return self.run(108 * 16)

    def get_state(self) -> CPUState:
        """Get complete CPU state snapshot."""
        return CPUState(
            program_counter=self.pc.position,
            cycle_count=self.pc.cycle_count,
            registers=self.registers.to_state(),
            current_quarter=self.pc.quarter,
            halted=self.halted,
            last_instruction=self.last_instruction.opcode_name if self.last_instruction else "",
            timestamp=datetime.now().isoformat(),
        )

    def reset(self) -> None:
        """Reset CPU to initial state."""
        self.registers.reset()
        self.pc.reset()
        self.halted = False
        self.last_instruction = None

    def halt(self) -> None:
        """Halt the CPU."""
        self.halted = True

    def resume(self) -> None:
        """Resume from halt."""
        self.halted = False

    # =========================================================================
    # FRACTAL DECOMPOSITION
    # =========================================================================

    def decompose_at_level(self, level: FractalLevel) -> List[str]:
        """
        Decompose current instruction at specified fractal level.

        This shows the self-similar structure:
        - PADA level: Just the word
        - AKSARA level: Syllable breakdown
        - VARNA level: Letter breakdown
        """
        if not self.last_instruction:
            return []

        pada = self.last_instruction.pada

        if level == FractalLevel.PADA:
            return [pada.roman]

        elif level == FractalLevel.AKSARA:
            return [a.iast for a in pada.aksaras]

        elif level == FractalLevel.VARNA:
            result = []
            for aksara in pada.aksaras:
                for char in aksara.devanagari:
                    result.append(char)
            return result

        elif level == FractalLevel.VAKYA:
            # Return all 16 words
            return [p.roman for p in MAHAMANTRA_SEQUENCE]

        else:
            return [pada.roman]

    def get_instruction_at(self, position: int) -> Instruction:
        """Get instruction at any position (0-15)."""
        return INSTRUCTION_SET[position % 16]

    def explain(self) -> str:
        """
        Explain current CPU state in human-readable form.
        """
        state = self.get_state()
        lines = [
            "═══════════════════════════════════════════════════════",
            "           MAHAMANTRA CPU STATE",
            "═══════════════════════════════════════════════════════",
            "",
            f"  Program Counter: {state['program_counter']} (Quarter {state['current_quarter'] + 1})",
            f"  Cycle Count: {state['cycle_count']}",
            f"  Halted: {state['halted']}",
            "",
            "  REGISTERS:",
            f"    H (Hare):    {state['registers']['hare_count']}",
            f"    K (Krishna): {state['registers']['krishna_count']}",
            f"    R (Rama):    {state['registers']['rama_count']}",
            f"    Total:       {state['registers']['total_count']}",
            f"    Resonance:   {state['registers']['resonance']:.3f}",
            "",
        ]

        if state["last_instruction"]:
            lines.append(f"  Last Instruction: {state['last_instruction']}")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)


# =============================================================================
# GLOBAL CPU INSTANCE
# =============================================================================

_global_cpu: Optional[MantraCPU] = None


def get_cpu() -> MantraCPU:
    """Get the global MantraCPU instance."""
    global _global_cpu
    if _global_cpu is None:
        _global_cpu = MantraCPU()
    return _global_cpu


def step() -> InstructionResult:
    """Execute one CPU step."""
    return get_cpu().step()


def run(cycles: int = 16) -> List[InstructionResult]:
    """Run the CPU for specified cycles."""
    return get_cpu().run(cycles)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "FractalLevel",
    # Types
    "RegisterState",
    "InstructionResult",
    "CPUState",
    # Classes
    "CPURegisters",
    "ProgramCounter",
    "Instruction",
    "MantraCPU",
    # Constants
    "OPCODE_NAMES",
    "OWNER_NAMES",
    "INSTRUCTION_SET",
    # Functions
    "get_instruction",
    "get_cpu",
    "step",
    "run",
    # Protocol
    "MantraCPUProtocol",
]
