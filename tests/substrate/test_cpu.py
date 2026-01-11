"""
Tests for MAHAMANTRA CPU - The Fractal Processor
================================================

Tests verify:
1. CPURegisters (H, K, R) increment and resonance
2. ProgramCounter position and cycle tracking
3. Instruction fetch-decode-execute
4. MantraCPU run cycles (vakya, mala)
5. Fractal decomposition at all levels
6. HARDENING: Edge cases, halt/resume, boundary conditions

THE MAHAMANTRA IS THE INSTRUCTION SET:
- 16 OpCodes = 16 Padas (words)
- 4 Quarters = 4 CPU Cycles
- 3 Names = 3 Registers (H, K, R)
- Perfect resonance: H=8, K=4, R=4
"""

import pytest
from datetime import datetime
from vibe_core.protocols.substrate.cpu import (
    # Enums
    FractalLevel,
    # Types
    RegisterState,
    InstructionResult,
    CPUState,
    # Classes
    CPURegisters,
    ProgramCounter,
    Instruction,
    MantraCPU,
    # Constants
    OPCODE_NAMES,
    OWNER_NAMES,
    INSTRUCTION_SET,
    # Functions
    get_instruction,
    get_cpu,
    step,
    run,
    # Protocol
    MantraCPUProtocol,
)
from vibe_core.protocols.substrate.byte import HolyName


# =============================================================================
# SECTION 1: FractalLevel Tests
# =============================================================================


class TestFractalLevel:
    """Test the FractalLevel enum."""

    def test_six_levels_exist(self):
        """There are exactly 6 fractal levels."""
        assert len(FractalLevel) == 6

    def test_level_order(self):
        """Levels are ordered from finest to coarsest."""
        assert FractalLevel.VARNA == 0     # Letter
        assert FractalLevel.AKSARA == 1    # Syllable
        assert FractalLevel.PADA == 2      # Word
        assert FractalLevel.VAKYA == 3     # Mantra
        assert FractalLevel.MALA == 4      # Round
        assert FractalLevel.SADHANA == 5   # Session


# =============================================================================
# SECTION 2: CPURegisters Tests
# =============================================================================


class TestCPURegisters:
    """Test the CPURegisters class (H, K, R registers)."""

    def test_initializes_to_zero(self):
        """Registers start at zero."""
        regs = CPURegisters()
        assert regs.hare == 0
        assert regs.krishna == 0
        assert regs.rama == 0

    def test_increment_hare(self):
        """HARE increments H register."""
        regs = CPURegisters()
        regs.increment(HolyName.HARE)
        assert regs.hare == 1
        assert regs.krishna == 0
        assert regs.rama == 0

    def test_increment_krishna(self):
        """KRISHNA increments K register."""
        regs = CPURegisters()
        regs.increment(HolyName.KRISHNA)
        assert regs.hare == 0
        assert regs.krishna == 1
        assert regs.rama == 0

    def test_increment_rama(self):
        """RAMA increments R register."""
        regs = CPURegisters()
        regs.increment(HolyName.RAMA)
        assert regs.hare == 0
        assert regs.krishna == 0
        assert regs.rama == 1

    def test_increment_void_no_change(self):
        """VOID doesn't change any register."""
        regs = CPURegisters()
        regs.increment(HolyName.VOID)
        assert regs.total == 0

    def test_total_property(self):
        """total returns sum of all registers."""
        regs = CPURegisters()
        regs.hare = 5
        regs.krishna = 3
        regs.rama = 2
        assert regs.total == 10

    def test_resonance_zero_when_empty(self):
        """Empty registers have zero resonance."""
        regs = CPURegisters()
        assert regs.resonance == 0.0

    def test_resonance_perfect_pattern(self):
        """Perfect 8:4:4 pattern has perfect resonance."""
        regs = CPURegisters()
        regs.hare = 8
        regs.krishna = 4
        regs.rama = 4
        # Perfect match to expected ratios
        assert regs.resonance == pytest.approx(1.0, abs=0.01)

    def test_resonance_in_range(self):
        """Resonance is always in [0.0, 1.0]."""
        regs = CPURegisters()
        for h in range(10):
            for k in range(10):
                for r in range(10):
                    regs.hare = h
                    regs.krishna = k
                    regs.rama = r
                    if regs.total > 0:
                        assert 0.0 <= regs.resonance <= 1.0

    def test_to_state_returns_typed_dict(self):
        """to_state() returns proper TypedDict."""
        regs = CPURegisters()
        regs.hare = 8
        regs.krishna = 4
        regs.rama = 4
        state = regs.to_state()
        assert state["hare_count"] == 8
        assert state["krishna_count"] == 4
        assert state["rama_count"] == 4
        assert state["total_count"] == 16
        assert "resonance" in state

    def test_reset(self):
        """reset() clears all registers."""
        regs = CPURegisters()
        regs.hare = 8
        regs.krishna = 4
        regs.rama = 4
        regs.reset()
        assert regs.hare == 0
        assert regs.krishna == 0
        assert regs.rama == 0


# =============================================================================
# SECTION 3: ProgramCounter Tests
# =============================================================================


class TestProgramCounter:
    """Test the ProgramCounter class."""

    def test_initializes_to_zero(self):
        """PC starts at position 0."""
        pc = ProgramCounter()
        assert pc.position == 0
        assert pc.cycle_count == 0

    def test_advance_increments(self):
        """advance() increments position by 1."""
        pc = ProgramCounter()
        old_pos = pc.advance()
        assert old_pos == 0
        assert pc.position == 1

    def test_advance_returns_old_position(self):
        """advance() returns position before advancing."""
        pc = ProgramCounter()
        pc.position = 5
        old = pc.advance()
        assert old == 5
        assert pc.position == 6

    def test_advance_with_steps(self):
        """advance() can take multiple steps."""
        pc = ProgramCounter()
        pc.advance(steps=3)
        assert pc.position == 3

    def test_wrap_around_at_16(self):
        """Position wraps from 15 to 0."""
        pc = ProgramCounter()
        pc.position = 15
        pc.advance()
        assert pc.position == 0

    def test_cycle_count_on_wrap(self):
        """Cycle count increases on wrap."""
        pc = ProgramCounter()
        pc.position = 15
        pc.advance()
        assert pc.cycle_count == 1

    def test_jump(self):
        """jump() sets position directly."""
        pc = ProgramCounter()
        pc.jump(10)
        assert pc.position == 10

    def test_jump_wraps(self):
        """jump() wraps on values >= 16."""
        pc = ProgramCounter()
        pc.jump(20)
        assert pc.position == 4  # 20 % 16

    def test_reset(self):
        """reset() clears position and cycle count."""
        pc = ProgramCounter()
        pc.position = 10
        pc.cycle_count = 5
        pc.reset()
        assert pc.position == 0
        assert pc.cycle_count == 0

    def test_quarter_property(self):
        """quarter property returns correct quarter (0-3)."""
        pc = ProgramCounter()
        pc.position = 0
        assert pc.quarter == 0
        pc.position = 4
        assert pc.quarter == 1
        pc.position = 8
        assert pc.quarter == 2
        pc.position = 12
        assert pc.quarter == 3

    def test_quarter_position_property(self):
        """quarter_position returns position within quarter."""
        pc = ProgramCounter()
        pc.position = 5
        assert pc.quarter == 1
        assert pc.quarter_position == 1  # 5 % 4


# =============================================================================
# SECTION 4: Instruction Tests
# =============================================================================


class TestInstruction:
    """Test the Instruction class."""

    def test_instruction_set_has_16(self):
        """INSTRUCTION_SET has exactly 16 instructions."""
        assert len(INSTRUCTION_SET) == 16

    def test_opcode_names_has_16(self):
        """OPCODE_NAMES has exactly 16 entries."""
        assert len(OPCODE_NAMES) == 16

    def test_owner_names_has_16(self):
        """OWNER_NAMES has exactly 16 entries."""
        assert len(OWNER_NAMES) == 16

    def test_get_instruction_valid_range(self):
        """get_instruction() works for 0-15."""
        for i in range(16):
            instr = get_instruction(i)
            assert instr.position == i

    def test_get_instruction_wraps(self):
        """get_instruction() wraps for position >= 16."""
        instr = get_instruction(20)
        assert instr.position == 4  # 20 % 16

    def test_instruction_has_correct_opcode(self):
        """Each instruction has its expected opcode."""
        assert INSTRUCTION_SET[0].opcode_name == "SYS_WAKE"
        assert INSTRUCTION_SET[4].opcode_name == "ASSERT_TRUTH"
        assert INSTRUCTION_SET[8].opcode_name == "FETCH_RES"
        assert INSTRUCTION_SET[12].opcode_name == "CACHE_STATE"
        assert INSTRUCTION_SET[15].opcode_name == "RESET_IP"

    def test_instruction_has_correct_owner(self):
        """Each instruction has its expected owner."""
        # 4 HEADs
        assert INSTRUCTION_SET[0].owner_name == "PRITHU"       # Q1 HEAD
        assert INSTRUCTION_SET[4].owner_name == "VYASA"        # Q2 HEAD
        assert INSTRUCTION_SET[8].owner_name == "PARASHURAMA"  # Q3 HEAD
        assert INSTRUCTION_SET[12].owner_name == "NRISIMHA"    # Q4 HEAD

    def test_instruction_quarter_assignment(self):
        """Each instruction knows its quarter."""
        for i in range(4):
            assert INSTRUCTION_SET[i].quarter == 0
        for i in range(4, 8):
            assert INSTRUCTION_SET[i].quarter == 1
        for i in range(8, 12):
            assert INSTRUCTION_SET[i].quarter == 2
        for i in range(12, 16):
            assert INSTRUCTION_SET[i].quarter == 3

    def test_instruction_holy_name(self):
        """Instruction returns correct HolyName."""
        # Position 0 should be HARE
        instr = INSTRUCTION_SET[0]
        assert instr.holy_name == HolyName.HARE
        # Position 1 should be KRISHNA
        instr = INSTRUCTION_SET[1]
        assert instr.holy_name == HolyName.KRISHNA

    def test_instruction_to_result(self):
        """to_result() creates proper InstructionResult."""
        instr = INSTRUCTION_SET[0]
        result = instr.to_result(success=True)
        assert result["position"] == 0
        assert result["opcode"] == "SYS_WAKE"
        assert result["owner"] == "PRITHU"
        assert result["quarter"] == 0
        assert result["success"] is True

    def test_instruction_is_frozen(self):
        """Instruction is immutable (frozen dataclass)."""
        instr = INSTRUCTION_SET[0]
        with pytest.raises(Exception):  # FrozenInstanceError
            instr.position = 5


# =============================================================================
# SECTION 5: MantraCPU Tests
# =============================================================================


class TestMantraCPU:
    """Test the MantraCPU class."""

    @pytest.fixture
    def cpu(self):
        """Create a fresh MantraCPU."""
        return MantraCPU()

    def test_initializes_correctly(self, cpu):
        """CPU initializes with zero state."""
        assert cpu.pc.position == 0
        assert cpu.registers.total == 0
        assert cpu.halted is False

    def test_fetch(self, cpu):
        """fetch() returns instruction at current PC."""
        instr = cpu.fetch()
        assert instr.position == 0
        assert instr.opcode_name == "SYS_WAKE"

    def test_decode(self, cpu):
        """decode() extracts HolyName from instruction."""
        instr = cpu.fetch()
        name = cpu.decode(instr)
        assert name == HolyName.HARE

    def test_execute_updates_registers(self, cpu):
        """execute() updates registers."""
        instr = cpu.fetch()
        cpu.execute(instr)
        assert cpu.registers.total == 1

    def test_step_complete_cycle(self, cpu):
        """step() performs fetch-decode-execute-advance."""
        result = cpu.step()
        assert result["success"] is True
        assert result["position"] == 0
        assert cpu.pc.position == 1  # Advanced
        assert cpu.registers.total == 1

    def test_step_when_halted(self, cpu):
        """step() returns failure when halted."""
        cpu.halt()
        result = cpu.step()
        assert result["success"] is False

    def test_run_16_cycles(self, cpu):
        """run(16) executes one complete vakya."""
        results = cpu.run(16)
        assert len(results) == 16
        # After 16 cycles: H=8, K=4, R=4
        assert cpu.registers.hare == 8
        assert cpu.registers.krishna == 4
        assert cpu.registers.rama == 4

    def test_run_vakya(self, cpu):
        """run_vakya() executes exactly 16 cycles."""
        results = cpu.run_vakya()
        assert len(results) == 16
        assert cpu.pc.cycle_count == 1

    def test_run_vakya_perfect_resonance(self, cpu):
        """After one vakya, resonance is perfect."""
        cpu.run_vakya()
        assert cpu.registers.resonance == pytest.approx(1.0, abs=0.01)

    def test_run_stops_when_halted(self, cpu):
        """run() stops early if halted."""
        cpu.step()
        cpu.step()
        cpu.halt()
        results = cpu.run(10)
        # Should only have executed before halt
        assert len(results) == 0  # Halted at start of run

    def test_get_state(self, cpu):
        """get_state() returns complete state."""
        cpu.run(5)
        state = cpu.get_state()
        assert state["program_counter"] == 5
        assert "registers" in state
        assert "current_quarter" in state
        assert "halted" in state
        assert "timestamp" in state

    def test_reset(self, cpu):
        """reset() clears all state."""
        cpu.run(10)
        cpu.reset()
        assert cpu.pc.position == 0
        assert cpu.registers.total == 0
        assert cpu.halted is False

    def test_halt_and_resume(self, cpu):
        """halt() and resume() control execution."""
        cpu.halt()
        assert cpu.halted is True
        cpu.resume()
        assert cpu.halted is False
        # Can execute again
        result = cpu.step()
        assert result["success"] is True

    def test_on_execute_callback(self, cpu):
        """on_execute callback is called for each instruction."""
        executed = []
        cpu.on_execute = lambda instr: executed.append(instr.position)
        cpu.run(5)
        assert executed == [0, 1, 2, 3, 4]


# =============================================================================
# SECTION 6: Fractal Decomposition Tests
# =============================================================================


class TestFractalDecomposition:
    """Test fractal decomposition at different levels."""

    @pytest.fixture
    def cpu(self):
        """Create CPU and execute one step."""
        c = MantraCPU()
        c.step()
        return c

    def test_decompose_pada_level(self, cpu):
        """PADA level shows the word."""
        result = cpu.decompose_at_level(FractalLevel.PADA)
        assert len(result) == 1
        assert result[0].lower() in ["hare", "harē"]

    def test_decompose_aksara_level(self, cpu):
        """AKSARA level shows syllables."""
        result = cpu.decompose_at_level(FractalLevel.AKSARA)
        # HARE has 2 syllables: ha, re
        assert len(result) == 2

    def test_decompose_varna_level(self, cpu):
        """VARNA level shows individual letters."""
        result = cpu.decompose_at_level(FractalLevel.VARNA)
        # Should have letters (varnas)
        assert len(result) > 0

    def test_decompose_vakya_level(self, cpu):
        """VAKYA level shows all 16 words."""
        result = cpu.decompose_at_level(FractalLevel.VAKYA)
        assert len(result) == 16

    def test_decompose_no_instruction(self):
        """Empty decomposition when no instruction executed."""
        cpu = MantraCPU()
        result = cpu.decompose_at_level(FractalLevel.PADA)
        assert result == []


# =============================================================================
# SECTION 7: Global Functions Tests
# =============================================================================


class TestGlobalFunctions:
    """Test global CPU functions."""

    def test_get_cpu_singleton(self):
        """get_cpu() returns singleton."""
        cpu1 = get_cpu()
        cpu2 = get_cpu()
        assert cpu1 is cpu2

    def test_step_global(self):
        """step() global function works."""
        cpu = get_cpu()
        cpu.reset()
        result = step()
        assert result["success"] is True

    def test_run_global(self):
        """run() global function works."""
        cpu = get_cpu()
        cpu.reset()
        results = run(4)
        assert len(results) == 4


# =============================================================================
# SECTION 8: HARDENING Tests
# =============================================================================


class TestHardening:
    """Hardening tests for edge cases and boundary conditions."""

    def test_large_cycle_count(self):
        """CPU handles large cycle counts."""
        cpu = MantraCPU()
        # 10 malas = 10 * 108 * 16 = 17,280 cycles
        results = cpu.run(1728)  # Just one mala
        assert len(results) == 1728
        assert cpu.pc.cycle_count == 108  # 1728 / 16 = 108

    def test_run_mala(self):
        """run_mala() executes 108 vakyas."""
        cpu = MantraCPU()
        results = cpu.run_mala()
        assert len(results) == 108 * 16
        # Registers should be 108x the single vakya
        assert cpu.registers.hare == 8 * 108
        assert cpu.registers.krishna == 4 * 108
        assert cpu.registers.rama == 4 * 108

    def test_explain_output(self):
        """explain() returns valid string."""
        cpu = MantraCPU()
        cpu.run(5)
        output = cpu.explain()
        assert "MAHAMANTRA CPU STATE" in output
        assert "Program Counter:" in output
        assert "REGISTERS:" in output

    def test_get_instruction_at(self):
        """get_instruction_at() returns correct instruction."""
        cpu = MantraCPU()
        instr = cpu.get_instruction_at(5)
        assert instr.position == 5
        assert instr.opcode_name == "RESOLVE_REQ"

    def test_concurrent_step_safe(self):
        """Multiple steps don't corrupt state."""
        cpu = MantraCPU()
        for _ in range(100):
            cpu.step()
        # State should be consistent
        assert cpu.registers.total == 100
        assert cpu.pc.position == 100 % 16

    def test_pc_wrap_stress(self):
        """PC wraps correctly under stress."""
        cpu = MantraCPU()
        # Run many cycles
        for _ in range(1000):
            cpu.step()
        # PC should be at position 1000 % 16 = 8
        assert cpu.pc.position == 1000 % 16

    def test_register_overflow_safety(self):
        """Registers handle large values."""
        regs = CPURegisters()
        for _ in range(10000):
            regs.increment(HolyName.HARE)
        assert regs.hare == 10000
        # Resonance should still be calculable
        assert 0.0 <= regs.resonance <= 1.0


# =============================================================================
# SECTION 9: Protocol Compliance Tests
# =============================================================================


class TestProtocolCompliance:
    """Test that MantraCPU implements MantraCPUProtocol."""

    def test_implements_protocol(self):
        """MantraCPU is an instance of MantraCPUProtocol."""
        cpu = MantraCPU()
        assert isinstance(cpu, MantraCPUProtocol)

    def test_has_fetch_method(self):
        """MantraCPU has fetch method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "fetch")
        assert callable(cpu.fetch)

    def test_has_decode_method(self):
        """MantraCPU has decode method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "decode")
        assert callable(cpu.decode)

    def test_has_execute_method(self):
        """MantraCPU has execute method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "execute")
        assert callable(cpu.execute)

    def test_has_step_method(self):
        """MantraCPU has step method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "step")
        assert callable(cpu.step)

    def test_has_run_method(self):
        """MantraCPU has run method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "run")
        assert callable(cpu.run)

    def test_has_get_state_method(self):
        """MantraCPU has get_state method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "get_state")
        assert callable(cpu.get_state)

    def test_has_reset_method(self):
        """MantraCPU has reset method."""
        cpu = MantraCPU()
        assert hasattr(cpu, "reset")
        assert callable(cpu.reset)
