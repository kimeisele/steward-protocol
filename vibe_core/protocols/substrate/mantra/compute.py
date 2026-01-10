"""
MANTRA COMPUTE - Ternary Computational Engine
==============================================

"The Absolute Truth is realized in three phases of understanding:
Brahman, Paramatma, and Bhagavan." - Srimad Bhagavatam 1.2.11

This module implements a complete ternary (base-3) computational engine
using the Mahamantra as the substrate. Each trit (ternary digit) is a
holy name:

    HARE    = 0 (śūnya/zero - the calling)
    KRISHNA = 1 (eka/one - all-attractive)
    RAMA    = 2 (dvi/two - all-pleasure)

Balanced Ternary (-1, 0, +1):
    HARE    =  0 (neutral)
    KRISHNA = +1 (positive/sattvic)
    RAMA    = -1 (negative - but NOT bad, just opposite polarity)

This gives us:
- 3^16 = 43,046,721 possible states in a 16-trit MantraByte
- Natural representation of signed integers without two's complement
- Efficient carry propagation in addition
- The Soviet Setun computer used balanced ternary (1958)!

OM TAT SAT
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Tuple, Optional, Callable
import operator

from ..byte import MantraByte, MantraTrit, HolyName


# =============================================================================
# TERNARY VALUE SYSTEMS
# =============================================================================

class TernaryMode(IntEnum):
    """Two interpretations of ternary digits."""
    UNBALANCED = 0  # {0, 1, 2} - standard base-3
    BALANCED = 1    # {-1, 0, +1} - symmetric around zero


# Balanced ternary mapping
BALANCED_MAP = {
    HolyName.HARE: 0,      # Neutral
    HolyName.KRISHNA: 1,   # Positive
    HolyName.RAMA: -1,     # Negative (opposite polarity)
}

BALANCED_REVERSE = {
    -1: HolyName.RAMA,
    0: HolyName.HARE,
    1: HolyName.KRISHNA,
}


# =============================================================================
# TRIT OPERATIONS (Single Digit)
# =============================================================================

def trit_to_int(trit: HolyName, mode: TernaryMode = TernaryMode.UNBALANCED) -> int:
    """Convert a single trit to integer value."""
    if mode == TernaryMode.BALANCED:
        return BALANCED_MAP[trit]
    return trit.value  # 0, 1, 2


def int_to_trit(value: int, mode: TernaryMode = TernaryMode.UNBALANCED) -> HolyName:
    """Convert integer to trit (with wrapping)."""
    if mode == TernaryMode.BALANCED:
        # Normalize to -1, 0, 1
        value = ((value + 1) % 3) - 1
        return BALANCED_REVERSE[value]
    return HolyName(value % 3)


# =============================================================================
# TERNARY LOGIC GATES
# =============================================================================

@dataclass
class TernaryLogic:
    """
    Ternary logic operations.

    In ternary logic, we have three truth values:
        HARE    = Unknown/Maybe (0)
        KRISHNA = True (1)
        RAMA    = False (2 or -1)

    This is Kleene's strong logic of indeterminacy.
    """

    @staticmethod
    def NOT(a: HolyName) -> HolyName:
        """
        Ternary NOT (negation).

        KRISHNA (True)  → RAMA (False)
        RAMA (False)    → KRISHNA (True)
        HARE (Unknown)  → HARE (Unknown)
        """
        if a == HolyName.KRISHNA:
            return HolyName.RAMA
        elif a == HolyName.RAMA:
            return HolyName.KRISHNA
        return HolyName.HARE  # Unknown stays unknown

    @staticmethod
    def AND(a: HolyName, b: HolyName) -> HolyName:
        """
        Ternary AND (minimum).

        True AND True = True
        False AND anything = False
        Unknown AND True = Unknown
        """
        # Use min in the order: RAMA(False) < HARE(Unknown) < KRISHNA(True)
        order = {HolyName.RAMA: 0, HolyName.HARE: 1, HolyName.KRISHNA: 2}
        reverse = {0: HolyName.RAMA, 1: HolyName.HARE, 2: HolyName.KRISHNA}
        return reverse[min(order[a], order[b])]

    @staticmethod
    def OR(a: HolyName, b: HolyName) -> HolyName:
        """
        Ternary OR (maximum).

        True OR anything = True
        False OR False = False
        Unknown OR False = Unknown
        """
        order = {HolyName.RAMA: 0, HolyName.HARE: 1, HolyName.KRISHNA: 2}
        reverse = {0: HolyName.RAMA, 1: HolyName.HARE, 2: HolyName.KRISHNA}
        return reverse[max(order[a], order[b])]

    @staticmethod
    def XOR(a: HolyName, b: HolyName) -> HolyName:
        """
        Ternary XOR (modular addition).

        Result = (a + b) mod 3
        """
        return HolyName((a.value + b.value) % 3)

    @staticmethod
    def NAND(a: HolyName, b: HolyName) -> HolyName:
        """Ternary NAND = NOT(AND(a, b))"""
        return TernaryLogic.NOT(TernaryLogic.AND(a, b))

    @staticmethod
    def NOR(a: HolyName, b: HolyName) -> HolyName:
        """Ternary NOR = NOT(OR(a, b))"""
        return TernaryLogic.NOT(TernaryLogic.OR(a, b))

    @staticmethod
    def CONSENSUS(a: HolyName, b: HolyName) -> HolyName:
        """
        Consensus gate - returns value only if both agree.

        Same → that value
        Different → Unknown (HARE)
        """
        if a == b:
            return a
        return HolyName.HARE

    @staticmethod
    def ACCEPT(a: HolyName, b: HolyName) -> HolyName:
        """
        Accept gate - if a is unknown, use b.

        Used for default/fallback logic.
        """
        if a == HolyName.HARE:
            return b
        return a


# =============================================================================
# MANTRA INTEGER - Arbitrary Precision Ternary Number
# =============================================================================

@dataclass
class MantraInt:
    """
    A ternary integer using MantraByte as storage.

    Can operate in unbalanced (0,1,2) or balanced (-1,0,+1) mode.
    """
    trits: List[HolyName]
    mode: TernaryMode = TernaryMode.UNBALANCED

    @classmethod
    def from_int(cls, value: int, width: int = 16, mode: TernaryMode = TernaryMode.UNBALANCED) -> 'MantraInt':
        """Convert Python int to MantraInt."""
        trits = []

        if mode == TernaryMode.BALANCED:
            # Balanced ternary conversion
            negative = value < 0
            value = abs(value)

            for _ in range(width):
                remainder = value % 3
                if remainder == 2:
                    remainder = -1
                    value += 1
                trits.append(BALANCED_REVERSE[remainder if not negative else -remainder])
                value //= 3
        else:
            # Unbalanced ternary conversion
            for _ in range(width):
                trits.append(HolyName(value % 3))
                value //= 3

        return cls(trits=trits, mode=mode)

    def to_int(self) -> int:
        """Convert MantraInt to Python int."""
        result = 0
        multiplier = 1

        for trit in self.trits:
            result += trit_to_int(trit, self.mode) * multiplier
            multiplier *= 3

        return result

    @classmethod
    def from_mantrabyte(cls, mb: MantraByte, mode: TernaryMode = TernaryMode.UNBALANCED) -> 'MantraInt':
        """Create from existing MantraByte."""
        trits = [mb.get_trit(i) for i in range(len(mb))]
        return cls(trits=trits, mode=mode)

    def to_mantrabyte(self) -> MantraByte:
        """Convert to MantraByte."""
        return MantraByte.from_trits(self.trits)

    def __len__(self) -> int:
        return len(self.trits)

    def __repr__(self) -> str:
        val = self.to_int()
        mode_str = "B" if self.mode == TernaryMode.BALANCED else "U"
        return f"MantraInt({val}, {mode_str}{len(self.trits)})"

    def to_mantra(self) -> str:
        """Display as mantra sequence."""
        return " ".join(t.name.lower() for t in self.trits)


# =============================================================================
# TERNARY ARITHMETIC LOGIC UNIT (ALU)
# =============================================================================

@dataclass
class MantraALU:
    """
    Arithmetic Logic Unit using ternary (Mantra) computation.

    Operations:
    - ADD, SUB, MUL, DIV (arithmetic)
    - AND, OR, XOR, NOT (logic)
    - SHL, SHR (shift)
    - CMP (compare)
    """

    mode: TernaryMode = TernaryMode.UNBALANCED

    # Status flags
    zero: bool = False      # Result is zero
    negative: bool = False  # Result is negative (balanced mode)
    overflow: bool = False  # Overflow occurred

    def _normalize_width(self, a: MantraInt, b: MantraInt) -> Tuple[MantraInt, MantraInt]:
        """Ensure both operands have same width."""
        max_width = max(len(a), len(b))

        if len(a) < max_width:
            a = MantraInt(a.trits + [HolyName.HARE] * (max_width - len(a)), a.mode)
        if len(b) < max_width:
            b = MantraInt(b.trits + [HolyName.HARE] * (max_width - len(b)), b.mode)

        return a, b

    def add(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """
        Ternary addition with carry propagation.

        In balanced ternary, this is remarkably elegant:
        - No special handling for negative numbers
        - Carry is always -1, 0, or +1
        """
        a, b = self._normalize_width(a, b)
        result_trits = []
        carry = 0

        for i in range(len(a)):
            # Get trit values
            va = trit_to_int(a.trits[i], self.mode)
            vb = trit_to_int(b.trits[i], self.mode)

            # Sum with carry
            total = va + vb + carry

            if self.mode == TernaryMode.BALANCED:
                # Balanced: normalize to -1, 0, +1
                if total > 1:
                    carry = 1
                    total -= 3
                elif total < -1:
                    carry = -1
                    total += 3
                else:
                    carry = 0
            else:
                # Unbalanced: standard base-3
                carry = total // 3
                total = total % 3

            result_trits.append(int_to_trit(total, self.mode))

        self.overflow = carry != 0
        result = MantraInt(result_trits, self.mode)
        self.zero = result.to_int() == 0
        self.negative = result.to_int() < 0

        return result

    def sub(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """Subtraction = a + (-b)."""
        neg_b = self.negate(b)
        return self.add(a, neg_b)

    def negate(self, a: MantraInt) -> MantraInt:
        """Negate a MantraInt."""
        if self.mode == TernaryMode.BALANCED:
            # In balanced ternary, just flip all trits
            negated = [BALANCED_REVERSE[-BALANCED_MAP[t]] for t in a.trits]
            return MantraInt(negated, self.mode)
        else:
            # In unbalanced, compute 3^n - 1 - a (complement)
            # Simpler: convert to int, negate, convert back
            return MantraInt.from_int(-a.to_int(), len(a), self.mode)

    def mul(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """
        Ternary multiplication.

        Uses shift-and-add algorithm.
        """
        a, b = self._normalize_width(a, b)
        width = len(a) * 2  # Result can be double width

        result = MantraInt.from_int(0, width, self.mode)

        for i in range(len(b)):
            trit_val = trit_to_int(b.trits[i], self.mode)

            if trit_val != 0:
                # Shift a left by i positions
                shifted = self.shl(a, i, width)

                # Multiply by trit value
                if trit_val == -1:  # RAMA in balanced
                    shifted = self.negate(shifted)
                elif trit_val == 2:  # RAMA in unbalanced
                    shifted = self.add(shifted, shifted)

                result = self.add(result, shifted)

        self.zero = result.to_int() == 0
        self.negative = result.to_int() < 0
        return result

    def div(self, a: MantraInt, b: MantraInt) -> Tuple[MantraInt, MantraInt]:
        """
        Ternary division returning (quotient, remainder).
        """
        dividend = a.to_int()
        divisor = b.to_int()

        if divisor == 0:
            raise ZeroDivisionError("Division by HARE (zero)")

        quotient = dividend // divisor
        remainder = dividend % divisor

        return (
            MantraInt.from_int(quotient, len(a), self.mode),
            MantraInt.from_int(remainder, len(a), self.mode)
        )

    def shl(self, a: MantraInt, positions: int, width: Optional[int] = None) -> MantraInt:
        """Shift left (multiply by 3^positions)."""
        if width is None:
            width = len(a)

        trits = [HolyName.HARE] * positions + a.trits
        trits = trits[:width]  # Truncate to width

        # Pad if needed
        while len(trits) < width:
            trits.append(HolyName.HARE)

        return MantraInt(trits, self.mode)

    def shr(self, a: MantraInt, positions: int) -> MantraInt:
        """Shift right (divide by 3^positions)."""
        trits = a.trits[positions:] + [HolyName.HARE] * positions
        return MantraInt(trits[:len(a)], self.mode)

    def bitwise_and(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """Trit-wise AND."""
        a, b = self._normalize_width(a, b)
        result = [TernaryLogic.AND(a.trits[i], b.trits[i]) for i in range(len(a))]
        return MantraInt(result, self.mode)

    def bitwise_or(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """Trit-wise OR."""
        a, b = self._normalize_width(a, b)
        result = [TernaryLogic.OR(a.trits[i], b.trits[i]) for i in range(len(a))]
        return MantraInt(result, self.mode)

    def bitwise_xor(self, a: MantraInt, b: MantraInt) -> MantraInt:
        """Trit-wise XOR (modular addition)."""
        a, b = self._normalize_width(a, b)
        result = [TernaryLogic.XOR(a.trits[i], b.trits[i]) for i in range(len(a))]
        return MantraInt(result, self.mode)

    def bitwise_not(self, a: MantraInt) -> MantraInt:
        """Trit-wise NOT."""
        result = [TernaryLogic.NOT(t) for t in a.trits]
        return MantraInt(result, self.mode)

    def cmp(self, a: MantraInt, b: MantraInt) -> int:
        """
        Compare two MantraInts.

        Returns:
            -1 (RAMA): a < b
             0 (HARE): a == b
            +1 (KRISHNA): a > b
        """
        diff = a.to_int() - b.to_int()
        if diff < 0:
            return -1
        elif diff > 0:
            return 1
        return 0


# =============================================================================
# MANTRA STACK MACHINE
# =============================================================================

@dataclass
class MantraVM:
    """
    A simple stack-based virtual machine using ternary computation.

    Opcodes (ternary encoding):
        HARE HARE     = NOP (0)
        HARE KRISHNA  = PUSH (1)
        HARE RAMA     = POP (2)
        KRISHNA HARE  = ADD (3)
        KRISHNA KRISHNA = SUB (4)
        KRISHNA RAMA  = MUL (5)
        RAMA HARE     = DIV (6)
        RAMA KRISHNA  = DUP (7)
        RAMA RAMA     = HALT (8)
    """

    stack: List[MantraInt] = field(default_factory=list)
    alu: MantraALU = field(default_factory=MantraALU)
    halted: bool = False
    pc: int = 0  # Program counter

    # Opcodes
    NOP = 0
    PUSH = 1
    POP = 2
    ADD = 3
    SUB = 4
    MUL = 5
    DIV = 6
    DUP = 7
    HALT = 8

    def push(self, value: MantraInt) -> None:
        """Push value onto stack."""
        self.stack.append(value)

    def pop(self) -> MantraInt:
        """Pop value from stack."""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def peek(self) -> MantraInt:
        """Peek at top of stack."""
        if not self.stack:
            raise RuntimeError("Stack empty")
        return self.stack[-1]

    def execute(self, program: List[Tuple[int, Optional[MantraInt]]]) -> MantraInt:
        """
        Execute a program.

        Program is a list of (opcode, optional_arg) tuples.
        Returns top of stack when halted.
        """
        self.pc = 0
        self.halted = False

        while not self.halted and self.pc < len(program):
            opcode, arg = program[self.pc]

            if opcode == self.NOP:
                pass
            elif opcode == self.PUSH:
                if arg is None:
                    raise RuntimeError("PUSH requires argument")
                self.push(arg)
            elif opcode == self.POP:
                self.pop()
            elif opcode == self.ADD:
                b = self.pop()
                a = self.pop()
                self.push(self.alu.add(a, b))
            elif opcode == self.SUB:
                b = self.pop()
                a = self.pop()
                self.push(self.alu.sub(a, b))
            elif opcode == self.MUL:
                b = self.pop()
                a = self.pop()
                self.push(self.alu.mul(a, b))
            elif opcode == self.DIV:
                b = self.pop()
                a = self.pop()
                q, _ = self.alu.div(a, b)
                self.push(q)
            elif opcode == self.DUP:
                self.push(self.peek())
            elif opcode == self.HALT:
                self.halted = True
            else:
                raise RuntimeError(f"Unknown opcode: {opcode}")

            self.pc += 1

        return self.peek() if self.stack else MantraInt.from_int(0, 16, self.alu.mode)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def mantra_add(a: int, b: int, width: int = 16) -> int:
    """Add two integers using ternary arithmetic."""
    alu = MantraALU()
    ma = MantraInt.from_int(a, width)
    mb = MantraInt.from_int(b, width)
    return alu.add(ma, mb).to_int()


def mantra_mul(a: int, b: int, width: int = 16) -> int:
    """Multiply two integers using ternary arithmetic."""
    alu = MantraALU()
    ma = MantraInt.from_int(a, width)
    mb = MantraInt.from_int(b, width)
    return alu.mul(ma, mb).to_int()


def mantra_calc(expression: str) -> int:
    """
    Simple calculator using MantraVM.

    Supports: +, -, *, / with integer operands
    Example: "5 3 + 2 *" (RPN) = (5 + 3) * 2 = 16
    """
    vm = MantraVM()
    tokens = expression.split()
    program = []

    for token in tokens:
        if token == '+':
            program.append((MantraVM.ADD, None))
        elif token == '-':
            program.append((MantraVM.SUB, None))
        elif token == '*':
            program.append((MantraVM.MUL, None))
        elif token == '/':
            program.append((MantraVM.DIV, None))
        else:
            # Assume it's a number
            val = MantraInt.from_int(int(token), 16)
            program.append((MantraVM.PUSH, val))

    program.append((MantraVM.HALT, None))
    result = vm.execute(program)
    return result.to_int()


__all__ = [
    "TernaryMode",
    "TernaryLogic",
    "MantraInt",
    "MantraALU",
    "MantraVM",
    "mantra_add",
    "mantra_mul",
    "mantra_calc",
    "trit_to_int",
    "int_to_trit",
]
