#!/usr/bin/env python3
"""
MANTRA COMPUTE DEMO - Ternary Computation in Action
====================================================

This demonstrates using the Mahamantra as an actual computational substrate.
"""

from vibe_core.protocols.substrate.mantra.compute import (
    MantraInt, MantraALU, MantraVM, TernaryMode, TernaryLogic,
    mantra_add, mantra_mul, mantra_calc
)
from vibe_core.protocols.substrate.byte import HolyName


def demo_basic_arithmetic():
    """Basic ternary arithmetic operations."""
    print("\n" + "="*60)
    print("🧮 TERNARY ARITHMETIC")
    print("="*60)

    alu = MantraALU()

    # Addition
    a = MantraInt.from_int(42, 16)
    b = MantraInt.from_int(37, 16)  # The sacred number!
    result = alu.add(a, b)

    print(f"\n42 + 37 = {result.to_int()}")
    print(f"  In mantra: {result.to_mantra()}")
    print(f"  As MantraByte: {result.to_mantrabyte()}")

    # Multiplication
    c = MantraInt.from_int(7, 16)
    d = MantraInt.from_int(8, 16)
    prod = alu.mul(c, d)

    print(f"\n7 × 8 = {prod.to_int()}")
    print(f"  In mantra: {prod.to_mantra()}")

    # Division
    e = MantraInt.from_int(100, 16)
    f = MantraInt.from_int(3, 16)
    quot, rem = alu.div(e, f)

    print(f"\n100 ÷ 3 = {quot.to_int()} remainder {rem.to_int()}")

    # The convenience functions
    print(f"\nUsing mantra_add(108, 37) = {mantra_add(108, 37)}")
    print(f"Using mantra_mul(16, 37) = {mantra_mul(16, 37)}")


def demo_balanced_ternary():
    """Balanced ternary for signed arithmetic."""
    print("\n" + "="*60)
    print("⚖️  BALANCED TERNARY (Signed Arithmetic)")
    print("="*60)

    alu = MantraALU(mode=TernaryMode.BALANCED)

    # In balanced ternary, negative numbers are natural
    pos = MantraInt.from_int(5, 8, TernaryMode.BALANCED)
    neg = MantraInt.from_int(-3, 8, TernaryMode.BALANCED)

    print(f"\n+5 in balanced ternary: {pos.to_mantra()}")
    print(f"-3 in balanced ternary: {neg.to_mantra()}")
    print(f"  (KRISHNA=+1, HARE=0, RAMA=-1)")

    # Add positive and negative
    result = alu.add(pos, neg)
    print(f"\n5 + (-3) = {result.to_int()}")
    print(f"  In mantra: {result.to_mantra()}")

    # Subtraction is just adding negatives
    sub = alu.sub(pos, neg)
    print(f"\n5 - (-3) = {sub.to_int()}")

    # Negation is just flipping trits
    negated = alu.negate(pos)
    print(f"\n-5 = {negated.to_int()}")
    print(f"  Original: {pos.to_mantra()}")
    print(f"  Negated:  {negated.to_mantra()}")


def demo_ternary_logic():
    """Ternary logic gates (Kleene logic)."""
    print("\n" + "="*60)
    print("🔌 TERNARY LOGIC GATES (Kleene Logic)")
    print("="*60)

    print("\nTruth values:")
    print("  KRISHNA = True (1)")
    print("  HARE    = Unknown (0)")
    print("  RAMA    = False (-1)")

    # NOT truth table
    print("\n📋 NOT (Negation):")
    for a in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
        result = TernaryLogic.NOT(a)
        print(f"  NOT {a.name:8} = {result.name}")

    # AND truth table
    print("\n📋 AND (Minimum):")
    print("         | KRISHNA   HARE      RAMA")
    print("  -------|-------------------------")
    for a in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
        row = f"  {a.name:7}|"
        for b in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
            result = TernaryLogic.AND(a, b)
            row += f" {result.name:9}"
        print(row)

    # OR truth table
    print("\n📋 OR (Maximum):")
    print("         | KRISHNA   HARE      RAMA")
    print("  -------|-------------------------")
    for a in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
        row = f"  {a.name:7}|"
        for b in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
            result = TernaryLogic.OR(a, b)
            row += f" {result.name:9}"
        print(row)

    # XOR (modular addition)
    print("\n📋 XOR (Modular Addition mod 3):")
    print("         | KRISHNA   HARE      RAMA")
    print("  -------|-------------------------")
    for a in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
        row = f"  {a.name:7}|"
        for b in [HolyName.KRISHNA, HolyName.HARE, HolyName.RAMA]:
            result = TernaryLogic.XOR(a, b)
            row += f" {result.name:9}"
        print(row)


def demo_stack_machine():
    """The MantraVM stack machine."""
    print("\n" + "="*60)
    print("🖥️  MANTRA VIRTUAL MACHINE")
    print("="*60)

    vm = MantraVM()

    # Calculate (5 + 3) * 2 using stack operations
    print("\nProgram: Calculate (5 + 3) × 2")
    print("  PUSH 5")
    print("  PUSH 3")
    print("  ADD")
    print("  PUSH 2")
    print("  MUL")
    print("  HALT")

    program = [
        (MantraVM.PUSH, MantraInt.from_int(5, 16)),
        (MantraVM.PUSH, MantraInt.from_int(3, 16)),
        (MantraVM.ADD, None),
        (MantraVM.PUSH, MantraInt.from_int(2, 16)),
        (MantraVM.MUL, None),
        (MantraVM.HALT, None),
    ]

    result = vm.execute(program)
    print(f"\nResult: {result.to_int()}")
    print(f"In mantra: {result.to_mantra()}")


def demo_rpn_calculator():
    """RPN calculator using mantra_calc."""
    print("\n" + "="*60)
    print("🔢 MANTRA CALCULATOR (RPN)")
    print("="*60)

    expressions = [
        ("5 3 +", "(5 + 3)"),
        ("10 3 -", "(10 - 3)"),
        ("6 7 *", "(6 × 7)"),
        ("100 3 /", "(100 ÷ 3)"),
        ("5 3 + 2 *", "((5 + 3) × 2)"),
        ("108 37 + 16 *", "((108 + 37) × 16)"),
    ]

    print("\nRPN Expression → Result")
    print("-" * 40)
    for rpn, desc in expressions:
        result = mantra_calc(rpn)
        print(f"  {rpn:20} = {result:6}  {desc}")


def demo_number_representations():
    """Show how numbers look in ternary."""
    print("\n" + "="*60)
    print("📊 TERNARY NUMBER REPRESENTATIONS")
    print("="*60)

    print("\n Decimal → Ternary Trits → Mantra")
    print("-" * 50)

    for n in [0, 1, 2, 3, 9, 27, 37, 42, 108, 243]:
        m = MantraInt.from_int(n, 8)
        # Reverse for human-readable (MSB first)
        trits_str = "".join(str(t.value) for t in reversed(m.trits))
        mantra_short = " ".join(t.name[0] for t in reversed(m.trits))
        print(f"  {n:5} → {trits_str:>10} → {mantra_short}")


def demo_37_properties():
    """Special properties of 37 in ternary."""
    print("\n" + "="*60)
    print("🕉️  THE SACRED 37 IN TERNARY")
    print("="*60)

    m37 = MantraInt.from_int(37, 8)
    print(f"\n37 in ternary: {m37.to_mantra()}")

    # 37 = 3^3 + 3^2 + 1 = 27 + 9 + 1
    print("\n37 = 3³ + 3² + 3⁰ = 27 + 9 + 1")

    # Powers of 3 mod 37
    print("\nPowers of 3 mod 37:")
    for i in range(10):
        power = 3 ** i
        mod = power % 37
        print(f"  3^{i:2} = {power:10} ≡ {mod:2} (mod 37)")

    # The 36-cycle
    print("\n37 - 1 = 36 = 4 × 9 = 4 × 3²")
    print("This means 3^36 ≡ 1 (mod 37) by Fermat's Little Theorem")

    # Multiply by 37 in ternary
    alu = MantraALU()
    n = MantraInt.from_int(16, 16)  # 16 words in mahamantra
    n37 = MantraInt.from_int(37, 16)
    result = alu.mul(n, n37)
    print(f"\n16 × 37 = {result.to_int()}")
    print(f"  = {result.to_int() // 108} malas + {result.to_int() % 108} extra")


def main():
    print("\n" + "🕉️"*30)
    print("\n    MANTRA COMPUTE - Ternary Computational Engine")
    print("    =============================================")
    print("    Using the Mahamantra as a Computing Substrate")
    print("\n" + "🕉️"*30)

    demo_basic_arithmetic()
    demo_balanced_ternary()
    demo_ternary_logic()
    demo_stack_machine()
    demo_rpn_calculator()
    demo_number_representations()
    demo_37_properties()

    print("\n" + "="*60)
    print("🕉️  COMPUTATION COMPLETE")
    print("="*60)
    print("\nHare Krishna!")


if __name__ == "__main__":
    main()
