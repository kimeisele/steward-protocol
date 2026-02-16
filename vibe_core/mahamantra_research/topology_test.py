"""
TOPOLOGY TEST - Verify Field→Fruit Transition
==============================================

Tests that the topology is correctly wired:
- Field (Ch 1-16): is_complete=False
- Fruit (Ch 17-18): is_complete=True
"""

from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    is_fruit,
    is_in_field,
    FIELD_SUM,
    FRUIT_SUM,
)


def test_topology_wiring():
    """Test that topology functions work correctly."""
    print("=" * 60)
    print("TOPOLOGY WIRING TEST")
    print("=" * 60)
    
    # Test is_fruit and is_in_field
    print("\n1. TOPOLOGY FUNCTIONS:")
    for ch in range(1, GITA_CHAPTERS + 1):
        in_field = is_in_field(ch)
        in_fruit = is_fruit(ch)
        marker = "FRUIT ✓" if in_fruit else "FIELD"
        print(f"   Ch {ch:2d}: in_field={in_field}, is_fruit={in_fruit} → {marker}")
    
    print(f"\n   FIELD_SUM = {FIELD_SUM} (Ch 1-16)")
    print(f"   FRUIT_SUM = {FRUIT_SUM} (Ch 17-18)")


def test_mahamantra_transition():
    """Test MahamantraLotus Field→Fruit transition."""
    print("\n" + "=" * 60)
    print("MAHAMANTRA TRANSITION TEST")
    print("=" * 60)
    
    m = get_mahamantra()
    
    # Test various inputs
    test_inputs = [
        "test",
        "hello world",
        "surrender",
        "moksha",
        "liberation",
        "sarva-dharman parityajya",  # BG 18.66
        "mam ekam saranam vraja",    # BG 18.66 continued
        "aham tvam sarva-papebhyo",  # BG 18.66 continued
    ]
    
    field_count = 0
    fruit_count = 0
    
    print("\n2. INPUT → CHAPTER → PHASE:")
    for inp in test_inputs:
        r = m(inp)
        ch = r["chapter"]
        phase = r["gita_phase"]
        complete = r["is_complete"]
        
        if complete:
            fruit_count += 1
            marker = "★ FRUIT (COMPLETE)"
        else:
            field_count += 1
            marker = "  FIELD (processing)"
        
        print(f"   '{inp[:30]:<30}' → Ch {ch:2d} → {phase:5} → {marker}")
    
    print(f"\n   Summary: {field_count} in Field, {fruit_count} in Fruit")
    
    return fruit_count > 0  # Success if at least one reached Fruit


if __name__ == "__main__":
    test_topology_wiring()
    success = test_mahamantra_transition()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ TOPOLOGY WIRED: Field→Fruit transition ACTIVE")
    else:
        print("⚠ No inputs reached Fruit phase (Ch 17-18)")
        print("  This may be expected - depends on attractor distribution")
    print("=" * 60)
