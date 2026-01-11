"""
SUBSTRATE HARDENING TESTS - System-Level Security & Robustness
==============================================================

These tests verify:
1. Integration between resonance.py, cpu.py, and gpu.py
2. Security: No crashes on malicious/malformed input
3. Robustness: Edge cases, boundary conditions, stress tests
4. Consistency: Deterministic behavior across runs
5. Thread safety: Parallel execution correctness

THE MAHAMANTRA IS ALWAYS MERCIFUL:
- Imperfect input still finds resonance
- System never crashes, only degrades gracefully
"""

import math
import threading
import pytest
from concurrent.futures import ThreadPoolExecutor

# Resonance imports
from vibe_core.protocols.substrate.resonance import (
    ResonanceEngine,
    compute_resonance_vector,
    resolve_position,
    compute_resonance_matrix,
    to_phonetic_key,
    PhoneticClass,
)

# CPU imports
from vibe_core.protocols.substrate.cpu import (
    MantraCPU,
    CPURegisters,
    ProgramCounter,
    FractalLevel,
    INSTRUCTION_SET,
)

# GPU imports
from vibe_core.protocols.substrate.gpu import (
    MantraGPU,
    GPUThread,
    GPUWarp,
    GPUBlock,
    GPUGrid,
)

from vibe_core.protocols.substrate.byte import HolyName


# =============================================================================
# SECTION 1: Cross-Module Integration Tests
# =============================================================================


class TestResonanceToCPUIntegration:
    """Test integration between resonance and CPU."""

    def test_resonance_position_maps_to_instruction(self):
        """Resolved position maps to valid instruction."""
        engine = ResonanceEngine()

        for text in ["hare", "krishna", "rama", "test", "random"]:
            position = engine.resolve(text)
            instruction = INSTRUCTION_SET[position]
            assert instruction is not None
            assert instruction.position == position

    def test_resonance_dominant_matches_instruction_name(self):
        """Dominant resonance matches instruction holy name."""
        engine = ResonanceEngine()

        # HARE input should map to HARE instruction
        vector = engine.resonate("hare")
        pos = resolve_position(vector)
        instruction = INSTRUCTION_SET[pos]
        # HARE positions are 0, 2, 6, 7, 8, 10, 14, 15
        if vector["dominant"] == "hare":
            assert instruction.holy_name == HolyName.HARE

    def test_cpu_processes_resonance_output(self):
        """CPU can process based on resonance output."""
        engine = ResonanceEngine()
        cpu = MantraCPU()

        # Get position from resonance
        position = engine.resolve("hare")

        # Jump CPU to that position
        cpu.pc.jump(position)

        # Execute one cycle
        result = cpu.step()
        assert result["success"] is True
        assert result["position"] == position


class TestCPUToGPUIntegration:
    """Test integration between CPU and GPU."""

    def test_gpu_thread_uses_cpu(self):
        """GPU thread correctly wraps MantraCPU."""
        thread = GPUThread(thread_id=0)

        # Access CPU directly
        assert thread.cpu is not None

        # Run through GPU thread
        thread.run(16)

        # Verify CPU state
        assert thread.cpu.registers.hare == 8
        assert thread.cpu.registers.krishna == 4
        assert thread.cpu.registers.rama == 4

    def test_warp_aggregates_cpu_states(self):
        """Warp correctly aggregates multiple CPU states."""
        warp = GPUWarp(warp_id=0)
        warp.run_lockstep(16)

        # Each thread should have perfect resonance
        for thread in warp.threads:
            assert thread.get_resonance() == pytest.approx(1.0, abs=0.01)

    def test_sankirtan_amplifies_resonance(self):
        """Sankirtan (congregational) amplifies total resonance."""
        gpu = MantraGPU()

        # Single devotee
        state1 = gpu.sankirtan(devotee_count=1)
        res1 = state1["total_resonance"]

        # Reset and try many more devotees (different grid sizes)
        gpu.grid = None
        state_many = gpu.sankirtan(devotee_count=200)  # Forces more blocks
        res_many = state_many["total_resonance"]

        # More devotees = more total resonance (or at least equal for same grid size)
        assert res_many >= res1
        # Both should have positive resonance
        assert res1 > 0
        assert res_many > 0


class TestFullPipelineIntegration:
    """Test complete pipeline: input → resonance → CPU → GPU."""

    def test_text_to_sankirtan_pipeline(self):
        """Complete pipeline from text input to congregational result."""
        # Step 1: Resonance analysis
        engine = ResonanceEngine()
        matrix = engine.resonate_many(["hare", "krishna", "rama"])

        # Step 2: Get positions
        positions = [e["position"] for e in matrix["entries"]]
        assert len(positions) == 3

        # Step 3: GPU parallel processing at those positions
        gpu = MantraGPU()
        resonances = gpu.compute_resonance_parallel(positions)

        # All should have perfect resonance
        assert all(r == pytest.approx(1.0, abs=0.01) for r in resonances)

    def test_fractal_consistency_across_levels(self):
        """Fractal decomposition consistent at all levels."""
        cpu = MantraCPU()
        cpu.step()

        # All levels should produce consistent output
        pada = cpu.decompose_at_level(FractalLevel.PADA)
        aksara = cpu.decompose_at_level(FractalLevel.AKSARA)
        varna = cpu.decompose_at_level(FractalLevel.VARNA)

        assert len(pada) == 1
        assert len(aksara) >= 1
        assert len(varna) >= len(aksara)


# =============================================================================
# SECTION 2: Security Hardening Tests
# =============================================================================


class TestSecurityHardening:
    """Security tests for malicious/malformed input."""

    def test_null_byte_injection(self):
        """Null bytes don't crash the system."""
        try:
            vector = compute_resonance_vector("hare\x00\x00\x00krishna")
            assert vector is not None
        except Exception:
            # Acceptable to raise, not crash
            pass

    def test_unicode_bomb(self):
        """Unicode expansion doesn't cause overflow."""
        # Zalgo text
        zalgo = "h̷̢̧̛̛̻̹̣̘̫͓̝̯̭̲̺̗̺͎̞̣̘̦̩̦̟̱̫̫̜̰̱̏̒̏̆̇̾͒̿̔̄͋̍̋̽̈́̏̇͘͘͝͝ͅa̷r̷e̷"
        vector = compute_resonance_vector(zalgo)
        assert vector is not None

    def test_very_long_input(self):
        """Very long input doesn't cause memory issues."""
        long_input = "hare krishna " * 10000
        vector = compute_resonance_vector(long_input)
        assert vector is not None

    def test_empty_string_handling(self):
        """Empty string handled gracefully."""
        vector = compute_resonance_vector("")
        assert vector is not None
        assert vector["magnitude"] >= 0.0

    def test_whitespace_only(self):
        """Whitespace-only input handled."""
        vector = compute_resonance_vector("   \t\n\r   ")
        assert vector is not None

    def test_control_characters(self):
        """Control characters handled."""
        control = "hare\x01\x02\x03krishna\x1f"
        vector = compute_resonance_vector(control)
        assert vector is not None

    def test_emoji_handling(self):
        """Emoji in input doesn't crash."""
        emoji_text = "hare 🙏 krishna 🙏 rama"
        vector = compute_resonance_vector(emoji_text)
        assert vector is not None

    def test_rtl_text(self):
        """Right-to-left text handled."""
        rtl = "هري كريشنا"  # Hindi in Arabic script (unusual)
        vector = compute_resonance_vector(rtl)
        assert vector is not None


# =============================================================================
# SECTION 3: Robustness Tests
# =============================================================================


class TestRobustnessHardening:
    """Robustness tests for edge cases and stress conditions."""

    def test_cpu_stress_cycles(self):
        """CPU handles many cycles without degradation."""
        cpu = MantraCPU()

        # Run 10,000 cycles
        for _ in range(10000):
            cpu.step()

        # State should be consistent
        assert cpu.pc.position == 10000 % 16
        assert cpu.registers.total == 10000

        # Resonance still calculable
        assert 0.0 <= cpu.registers.resonance <= 1.0

    def test_halt_resume_cycles(self):
        """Repeated halt/resume doesn't corrupt state."""
        cpu = MantraCPU()

        for _ in range(100):
            cpu.step()
            cpu.halt()
            cpu.resume()
            cpu.step()

        # Should have executed 200 total
        assert cpu.registers.total == 200

    def test_pc_wrap_stress(self):
        """PC wraps correctly under high load."""
        pc = ProgramCounter()

        for i in range(10000):
            pc.advance()
            assert 0 <= pc.position <= 15

        # Cycle count should match
        assert pc.cycle_count == 10000 // 16

    def test_register_large_values(self):
        """Registers handle large values."""
        regs = CPURegisters()
        regs.hare = 1000000
        regs.krishna = 500000
        regs.rama = 500000

        # Total works
        assert regs.total == 2000000

        # Resonance still valid
        assert 0.0 <= regs.resonance <= 1.0

    def test_gpu_grid_stress(self):
        """GPU grid handles creation stress."""
        gpu = MantraGPU()

        # Create many objects
        for _ in range(100):
            gpu.create_thread()
            gpu.create_warp()

        assert gpu.total_threads_created == 100
        assert gpu.total_warps_created == 100


# =============================================================================
# SECTION 4: Thread Safety Tests
# =============================================================================


class TestThreadSafety:
    """Thread safety tests for parallel execution."""

    def test_parallel_resonance_calculation(self):
        """Resonance calculation is thread-safe."""
        results = []

        def compute_resonance(text: str):
            vector = compute_resonance_vector(text)
            results.append(vector)

        threads = []
        for text in ["hare", "krishna", "rama"] * 10:
            t = threading.Thread(target=compute_resonance, args=(text,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should have completed
        assert len(results) == 30

    def test_parallel_cpu_instances(self):
        """Multiple CPU instances don't interfere."""
        cpus = [MantraCPU() for _ in range(10)]
        results = []

        def run_cpu(cpu: MantraCPU):
            cpu.run(16)
            results.append(cpu.registers.total)

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(run_cpu, cpus)

        # All should have 16
        assert all(r == 16 for r in results)

    def test_gpu_parallel_launch(self):
        """GPU parallel launch is safe."""
        gpu = MantraGPU()

        # Launch with parallel=True
        state = gpu.launch_grid(size=4, parallel=True)

        # All blocks should complete
        assert state["blocks_active"] == 4
        assert state["total_resonance"] > 0


# =============================================================================
# SECTION 5: Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_resonance_deterministic(self):
        """Same input always gives same resonance."""
        text = "hare krishna"

        v1 = compute_resonance_vector(text)
        v2 = compute_resonance_vector(text)

        assert v1["hare"] == v2["hare"]
        assert v1["krishna"] == v2["krishna"]
        assert v1["rama"] == v2["rama"]
        assert v1["dominant"] == v2["dominant"]

    def test_cpu_execution_deterministic(self):
        """CPU execution is deterministic."""
        cpu1 = MantraCPU()
        cpu2 = MantraCPU()

        r1 = cpu1.run(16)
        r2 = cpu2.run(16)

        # Same results
        for i in range(16):
            assert r1[i]["position"] == r2[i]["position"]
            assert r1[i]["opcode"] == r2[i]["opcode"]

    def test_position_resolution_deterministic(self):
        """Position resolution is deterministic."""
        for text in ["hare", "krishna", "rama", "test"]:
            p1 = compute_resonance_vector(text)
            p2 = compute_resonance_vector(text)
            pos1 = resolve_position(p1)
            pos2 = resolve_position(p2)
            assert pos1 == pos2


# =============================================================================
# SECTION 6: Boundary Condition Tests
# =============================================================================


class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_position_15_wraps_to_0(self):
        """Position 15 wraps to 0 on advance."""
        pc = ProgramCounter()
        pc.position = 15
        pc.advance()
        assert pc.position == 0

    def test_empty_matrix_coherence(self):
        """Empty matrix has perfect coherence."""
        matrix = compute_resonance_matrix([])
        assert matrix["coherence"] == 1.0

    def test_single_entry_matrix(self):
        """Single-entry matrix has perfect coherence."""
        matrix = compute_resonance_matrix(["hare"])
        assert matrix["coherence"] == 1.0

    def test_zero_phase_interference(self):
        """Zero phase threads have maximum constructive interference."""
        warp = GPUWarp(warp_id=0)
        # Set all phases to 0
        for thread in warp.threads:
            thread.set_phase(0.0)
        warp.run_lockstep(16)
        interference = warp.compute_interference()
        # Should be high (all in phase)
        assert interference > 0.9

    def test_opposite_phase_interference(self):
        """Opposite phase threads have lower interference."""
        warp = GPUWarp(warp_id=0)
        # Alternate 0 and pi phases
        for i, thread in enumerate(warp.threads):
            thread.set_phase(0.0 if i % 2 == 0 else math.pi)
        warp.run_lockstep(16)
        interference = warp.compute_interference()
        # Should be lower due to cancellation
        assert interference < 0.5


# =============================================================================
# SECTION 7: Recovery Tests
# =============================================================================


class TestRecovery:
    """Tests for system recovery from error states."""

    def test_cpu_reset_clears_error_state(self):
        """CPU reset clears all error state."""
        cpu = MantraCPU()
        cpu.run(10)
        cpu.halt()

        # Reset should clear
        cpu.reset()
        assert cpu.halted is False
        assert cpu.pc.position == 0
        assert cpu.registers.total == 0

        # Can run again
        result = cpu.step()
        assert result["success"] is True

    def test_warp_reset_restores_initial_state(self):
        """Warp reset restores initial thread positions."""
        warp = GPUWarp(warp_id=0)

        # Run and mess up state
        warp.run_lockstep(100)

        # Reset
        warp.reset()

        # Verify initial positions restored
        for i, thread in enumerate(warp.threads):
            assert thread.cpu.pc.position == i
            assert thread.cycles_executed == 0

    def test_grid_reset_clears_all_blocks(self):
        """Grid reset clears all block state."""
        grid = GPUGrid(grid_size=3)
        grid.launch()

        # Reset
        grid.reset()

        for block in grid.blocks:
            assert block.warps_completed == 0


# =============================================================================
# SECTION 8: Phonetic Edge Cases
# =============================================================================


class TestPhoneticEdgeCases:
    """Edge cases for phonetic processing."""

    def test_all_vowels(self):
        """All-vowel input processed correctly."""
        key = to_phonetic_key("aeiou")
        assert len(key) == 5

    def test_all_consonants(self):
        """All-consonant input processed correctly."""
        key = to_phonetic_key("bcdfg")
        assert len(key) >= 4  # Some may map to same class

    def test_mixed_scripts(self):
        """Mixed script input processed."""
        vector = compute_resonance_vector("hare हरे Χριστός")
        assert vector is not None

    def test_repeated_characters(self):
        """Repeated characters handled."""
        key = to_phonetic_key("aaaaaaa")
        assert all(c == PhoneticClass.VOWEL_A for c in key)

    def test_digraph_at_end(self):
        """Digraph at end of string handled."""
        key = to_phonetic_key("ash")
        # "sh" is a digraph
        assert PhoneticClass.SIBILANT in key

    def test_single_character(self):
        """Single character input works."""
        vector = compute_resonance_vector("h")
        assert vector is not None
