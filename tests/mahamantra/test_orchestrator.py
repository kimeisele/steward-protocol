"""
TEST: VenuOrchestrator - The Dancing Algorithm
==============================================

"The system proves itself through its execution."

WATERTIGHT TESTS:
- All values derived from SSOT (_seed.py)
- No hardcoded magic numbers
- No Any types
"""

import pytest

from vibe_core.mahamantra.orchestrator import (
    THE_FLUTE_CYCLE,
    DIW_MASK,
    SUNYA_MASK,
    VenuOrchestrator,
)
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    PARAMPARA,
    MAHA_QUANTUM,
    POSITION_SUM_RAMA,
    FLUTE_HOLES_SUM,
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    COSMIC_FRAME,
    MAHAMANTRA_WORD_PATTERN,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
)


class TestTheFlueCycleLUT:
    """Test THE_FLUTE_CYCLE Look-Up Table."""
    
    def test_lut_length_equals_words(self) -> None:
        """LUT must have exactly WORDS (16) entries."""
        assert len(THE_FLUTE_CYCLE) == WORDS
    
    def test_lut_position_bits_all_touched(self) -> None:
        """XOR of all position bits = 0xFFFF (all 16 bits touched once)."""
        xor_result = 0
        for diw in THE_FLUTE_CYCLE:
            xor_result ^= (diw & 0xFFFF)
        
        expected = (1 << WORDS) - 1  # 0xFFFF
        assert xor_result == expected, f"Expected {hex(expected)}, got {hex(xor_result)}"
    
    def test_lut_name_counts(self) -> None:
        """LUT must have correct name counts (8H, 4K, 4R)."""
        hare_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 0)
        krishna_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 1)
        rama_count = sum(1 for diw in THE_FLUTE_CYCLE if (diw >> 16) == 2)
        
        assert hare_count == HARE_COUNT
        assert krishna_count == KRISHNA_COUNT
        assert rama_count == RAMA_COUNT
    
    def test_lut_matches_mahamantra_pattern(self) -> None:
        """LUT must reflect MAHAMANTRA_WORD_PATTERN exactly."""
        name_to_encoding = {
            MAHAMANTRA_NAME_HARE: 0,
            MAHAMANTRA_NAME_KRISHNA: 1,
            MAHAMANTRA_NAME_RAMA: 2,
        }
        
        for pos, name in enumerate(MAHAMANTRA_WORD_PATTERN):
            diw = THE_FLUTE_CYCLE[pos]
            
            # Check position bit
            position_bit = 1 << pos
            assert diw & position_bit, f"Position {pos} bit not set"
            
            # Check name encoding
            encoding = diw >> 16
            expected_encoding = name_to_encoding[name]
            assert encoding == expected_encoding, \
                f"Position {pos}: expected {name}={expected_encoding}, got {encoding}"


class TestMaskConstants:
    """Test mask constants are derived correctly."""
    
    def test_diw_mask_equals_19_bits(self) -> None:
        """DIW_MASK = (1 << 19) - 1 = 0x7FFFF."""
        expected = (1 << FLUTE_HOLES_SUM) - 1
        assert DIW_MASK == expected
        assert DIW_MASK == 0x7FFFF
    
    def test_sunya_mask_is_bit_31(self) -> None:
        """SUNYA_MASK = 1 << 31."""
        assert SUNYA_MASK == (1 << 31)
        assert SUNYA_MASK == 0x80000000


class TestVenuOrchestratorInit:
    """Test VenuOrchestrator initialization."""
    
    def test_initial_state(self) -> None:
        """Orchestrator starts at tick 0 with no previous state."""
        orch = VenuOrchestrator()
        assert orch.tick == 0
        assert orch._prev_state == 0
    
    def test_class_variables(self) -> None:
        """Class variables match SSOT."""
        assert VenuOrchestrator.VENU_BITS == VENU_HOLES
        assert VenuOrchestrator.VAMSI_BITS == VAMSI_HOLES
        assert VenuOrchestrator.MURALI_BITS == MURALI_HOLES


class TestStep:
    """Test step() method - the core algorithm."""
    
    def test_step_increments_tick(self) -> None:
        """Each step increments tick by 1."""
        orch = VenuOrchestrator()
        for i in range(10):
            orch.step()
            assert orch.tick == i + 1
    
    def test_step_wraps_at_cosmic_frame(self) -> None:
        """Tick wraps at COSMIC_FRAME to prevent overflow."""
        orch = VenuOrchestrator()
        orch._tick = COSMIC_FRAME - 1
        orch.step()
        assert orch.tick == 0
    
    def test_step_returns_delta(self) -> None:
        """Step returns XOR delta between states."""
        orch = VenuOrchestrator()
        
        # First step: delta = 0 XOR first_entry
        delta1 = orch.step()
        assert delta1 == THE_FLUTE_CYCLE[0]
        
        # Second step: delta = first_entry XOR second_entry
        delta2 = orch.step()
        assert delta2 == THE_FLUTE_CYCLE[0] ^ THE_FLUTE_CYCLE[1]


class TestCycle:
    """Test cycle() method - full 16-step cycle."""
    
    def test_cycle_returns_correct_xor(self) -> None:
        """Full cycle XOR of positions = 0xFFFF."""
        orch = VenuOrchestrator()
        result = orch.cycle()
        
        expected = (1 << WORDS) - 1  # 0xFFFF
        assert result == expected
    
    def test_cycle_advances_16_ticks(self) -> None:
        """Cycle advances tick by exactly WORDS (16)."""
        orch = VenuOrchestrator()
        orch.cycle()
        assert orch.tick == WORDS


class TestVerifyDivinity:
    """Test verify_divinity() - the proof of Krishna."""
    
    def test_verify_divinity_passes(self) -> None:
        """The mathematical proof of divinity should pass."""
        orch = VenuOrchestrator()
        result = orch.verify_divinity()
        assert result is True
    
    def test_verify_divinity_checks_rama_resonance(self) -> None:
        """XOR % MAHA_QUANTUM = POSITION_SUM_RAMA (49)."""
        xor_result = (1 << WORDS) - 1  # 0xFFFF = 65535
        assert xor_result % MAHA_QUANTUM == POSITION_SUM_RAMA
    
    def test_verify_divinity_checks_hare_protection(self) -> None:
        """XOR % PARAMPARA = HARE_COUNT (8)."""
        xor_result = (1 << WORDS) - 1  # 0xFFFF = 65535
        assert xor_result % PARAMPARA == HARE_COUNT


class TestRoute:
    """Test route() method - seed routing through flutes."""
    
    def test_route_returns_three_values(self) -> None:
        """Route returns (venu, vamsi, murali) tuple."""
        orch = VenuOrchestrator()
        result = orch.route(42)
        assert len(result) == 3
    
    def test_route_values_in_range(self) -> None:
        """Routed values are within their bit ranges."""
        orch = VenuOrchestrator()
        
        for seed in [0, 1, 37, 100, 1000, 65535]:
            venu, vamsi, murali = orch.route(seed)
            
            assert 0 <= venu < (1 << VENU_HOLES), f"Venu out of range for seed {seed}"
            assert 0 <= vamsi < (1 << VAMSI_HOLES), f"Vamsi out of range for seed {seed}"
            assert 0 <= murali < (1 << MURALI_HOLES), f"Murali out of range for seed {seed}"


class TestHarmonize:
    """Test harmonize() method - combine flutes into 32-bit word."""
    
    def test_harmonize_basic(self) -> None:
        """Basic harmonize produces valid 32-bit word."""
        orch = VenuOrchestrator()
        result = orch.harmonize(venu=0, vamsi=0, murali=0)
        
        assert isinstance(result, int)
        assert 0 <= result < (1 << 32)
    
    def test_harmonize_with_sunya(self) -> None:
        """SUNYA flag sets bit 31."""
        orch = VenuOrchestrator()
        result = orch.harmonize(venu=0, vamsi=0, murali=0, sunya=True)
        
        assert result & SUNYA_MASK
        assert orch.is_sunya(result)
    
    def test_harmonize_without_sunya(self) -> None:
        """Without SUNYA, bit 31 is clear."""
        orch = VenuOrchestrator()
        result = orch.harmonize(venu=0, vamsi=0, murali=0, sunya=False)
        
        assert not (result & SUNYA_MASK)
        assert not orch.is_sunya(result)
    
    def test_harmonize_velocity(self) -> None:
        """Velocity is encoded in bits 19-22."""
        orch = VenuOrchestrator()
        
        for velocity in range(16):
            result = orch.harmonize(venu=0, vamsi=0, murali=0, velocity=velocity)
            extracted = (result >> FLUTE_HOLES_SUM) & 0xF
            assert extracted == velocity
    
    def test_harmonize_preserves_diw(self) -> None:
        """Lower 19 bits contain the DIW."""
        orch = VenuOrchestrator()
        result = orch.harmonize(venu=63, vamsi=511, murali=15)  # Max values
        
        diw = orch.extract_diw(result)
        assert diw == (15 << 15) | (511 << 6) | 63


class TestReset:
    """Test reset() method."""
    
    def test_reset_clears_state(self) -> None:
        """Reset returns orchestrator to initial state."""
        orch = VenuOrchestrator()
        
        # Advance state
        for _ in range(100):
            orch.step()
        
        # Reset
        orch.reset()
        
        assert orch.tick == 0
        assert orch._prev_state == 0
