"""
MAHAMANTRA GPU - Parallel Resonance Processor
=============================================

"yajñaiḥ saṅkīrtana-prāyair yajanti hi su-medhasaḥ"

"In this age of Kali, intelligent persons perform congregational
chanting to worship the incarnation of Godhead."
— Srimad Bhagavatam 11.5.32

CONGREGATIONAL CHANTING = PARALLEL PROCESSING
============================================

When many devotees chant together, the resonance multiplies.
This is the "GPU" of the Mahamantra - parallel processing
of n mantras simultaneously.

ARCHITECTURE:
=============

1. THREAD: One MantraCPU instance processing one stream
2. WARP: 16 threads (one per Mahamantra position)
3. BLOCK: 108 warps (one mala)
4. GRID: n blocks (congregational size)

RESONANCE COHERENCE:
===================

When multiple mantras resonate:
- In-phase: Amplification (constructive interference)
- Out-of-phase: Cancellation (destructive interference)
- Coherent congregation: Maximum amplification

The GPU computes this interference pattern.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x0ca3720d"  # GenesisByte: parampara % 37 == 0

import math
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    runtime_checkable,
)

from vibe_core.protocols.substrate.cpu import (
    MantraCPU,
    CPUState,
    InstructionResult,
    FractalLevel,
    INSTRUCTION_SET,
)
from vibe_core.protocols.substrate.byte import HolyName


# =============================================================================
# GPU THREAD (One Mantra Stream)
# =============================================================================


class ThreadState(TypedDict):
    """
    State of one GPU thread.
    WATERTIGHT - no Any!
    """
    thread_id: int
    cpu_state: CPUState
    cycles_executed: int
    resonance: float
    phase: float  # Phase angle (0 to 2π)


@dataclass
class GPUThread:
    """
    One GPU thread - processes one mantra stream.

    Each thread has its own MantraCPU instance.
    Threads can be synchronized for coherent resonance.
    """
    thread_id: int
    cpu: MantraCPU = field(default_factory=MantraCPU)
    cycles_executed: int = 0
    phase: float = 0.0  # Phase angle for interference calculation

    def run(self, cycles: int = 16) -> List[InstructionResult]:
        """Run this thread for specified cycles."""
        results = self.cpu.run(cycles)
        self.cycles_executed += len(results)
        return results

    def get_resonance(self) -> float:
        """Get current resonance from CPU registers."""
        return self.cpu.registers.resonance

    def get_state(self) -> ThreadState:
        """Get thread state."""
        return ThreadState(
            thread_id=self.thread_id,
            cpu_state=self.cpu.get_state(),
            cycles_executed=self.cycles_executed,
            resonance=self.get_resonance(),
            phase=self.phase,
        )

    def set_phase(self, phase: float) -> None:
        """Set phase for interference calculation."""
        self.phase = phase % (2 * math.pi)

    def reset(self) -> None:
        """Reset thread state."""
        self.cpu.reset()
        self.cycles_executed = 0
        self.phase = 0.0


# =============================================================================
# GPU WARP (16 Threads - One Position Each)
# =============================================================================


class WarpState(TypedDict):
    """
    State of a warp (16 threads).
    WATERTIGHT - no Any!
    """
    warp_id: int
    threads: List[ThreadState]
    total_resonance: float
    coherence: float
    dominant_position: int


@dataclass
class GPUWarp:
    """
    A warp of 16 threads - one per Mahamantra position.

    In GPU architecture, a warp executes in lockstep.
    Here, each thread processes the same position simultaneously,
    creating resonance through parallel vibration.
    """
    warp_id: int
    threads: List[GPUThread] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize 16 threads if not provided."""
        if not self.threads:
            self.threads = [GPUThread(thread_id=i) for i in range(16)]
            # Set phases for each thread (distributed evenly)
            for i, thread in enumerate(self.threads):
                # Start each thread at its corresponding position
                thread.cpu.pc.jump(i)
                # Set phase based on position
                thread.phase = (i / 16) * 2 * math.pi

    def run_lockstep(self, cycles_per_thread: int = 1) -> List[List[InstructionResult]]:
        """
        Run all threads in lockstep (SIMD-style).

        Each thread executes the same number of cycles simultaneously.
        Returns results from all threads.
        """
        results: List[List[InstructionResult]] = []
        for thread in self.threads:
            thread_results = thread.run(cycles_per_thread)
            results.append(thread_results)
        return results

    def compute_interference(self) -> float:
        """
        Compute interference pattern from all threads.

        Uses wave superposition:
        - Each thread contributes amplitude * cos(phase)
        - Coherent phases → constructive interference
        - Random phases → cancellation
        """
        total_amplitude = 0.0

        for thread in self.threads:
            amplitude = thread.get_resonance()
            phase = thread.phase
            # Wave contribution
            total_amplitude += amplitude * math.cos(phase)

        # Normalize by number of threads
        return abs(total_amplitude) / len(self.threads)

    def get_coherence(self) -> float:
        """
        Compute coherence (how synchronized the threads are).

        High coherence = threads are in phase = maximum resonance.
        """
        if not self.threads:
            return 0.0

        # Collect all resonance values
        resonances = [t.get_resonance() for t in self.threads]
        mean_res = sum(resonances) / len(resonances)

        if mean_res == 0:
            return 0.0

        # Variance measures spread
        variance = sum((r - mean_res) ** 2 for r in resonances) / len(resonances)

        # Coherence is inverse of normalized variance
        return math.exp(-variance / (mean_res ** 2 + 0.001))

    def get_dominant_position(self) -> int:
        """Get position with highest resonance."""
        max_resonance = 0.0
        dominant = 0

        for thread in self.threads:
            res = thread.get_resonance()
            if res > max_resonance:
                max_resonance = res
                dominant = thread.cpu.pc.position

        return dominant

    def get_state(self) -> WarpState:
        """Get warp state."""
        return WarpState(
            warp_id=self.warp_id,
            threads=[t.get_state() for t in self.threads],
            total_resonance=sum(t.get_resonance() for t in self.threads),
            coherence=self.get_coherence(),
            dominant_position=self.get_dominant_position(),
        )

    def reset(self) -> None:
        """Reset all threads."""
        for i, thread in enumerate(self.threads):
            thread.reset()
            thread.cpu.pc.jump(i)
            thread.phase = (i / 16) * 2 * math.pi


# =============================================================================
# GPU BLOCK (108 Warps - One Mala)
# =============================================================================


class BlockState(TypedDict):
    """
    State of a block (108 warps = 1 mala).
    WATERTIGHT - no Any!
    """
    block_id: int
    warps_completed: int
    total_resonance: float
    average_coherence: float
    mala_progress: float  # 0.0 to 1.0


@dataclass
class GPUBlock:
    """
    A block of 108 warps - one complete mala.

    108 is the sacred number:
    - 108 beads on a mala
    - 108 mantras per round
    - 108 x 16 = 1728 words per round
    """
    block_id: int
    warps: List[GPUWarp] = field(default_factory=list)
    warps_completed: int = 0

    def __post_init__(self) -> None:
        """Initialize 108 warps if not provided."""
        if not self.warps:
            self.warps = [GPUWarp(warp_id=i) for i in range(108)]

    def run_warp(self, warp_index: int) -> WarpState:
        """Run a single warp and return its state."""
        if 0 <= warp_index < 108:
            warp = self.warps[warp_index]
            warp.run_lockstep(16)  # One complete vakya per thread
            self.warps_completed = max(self.warps_completed, warp_index + 1)
            return warp.get_state()
        raise IndexError(f"Warp index {warp_index} out of range (0-107)")

    def run_mala(self) -> List[WarpState]:
        """Run complete mala (all 108 warps)."""
        results: List[WarpState] = []
        for i in range(108):
            state = self.run_warp(i)
            results.append(state)
        return results

    def get_total_resonance(self) -> float:
        """Get total resonance across all warps."""
        return sum(
            sum(t.get_resonance() for t in warp.threads)
            for warp in self.warps[:self.warps_completed]
        )

    def get_average_coherence(self) -> float:
        """Get average coherence across completed warps."""
        if self.warps_completed == 0:
            return 0.0
        return sum(
            warp.get_coherence()
            for warp in self.warps[:self.warps_completed]
        ) / self.warps_completed

    def get_state(self) -> BlockState:
        """Get block state."""
        return BlockState(
            block_id=self.block_id,
            warps_completed=self.warps_completed,
            total_resonance=self.get_total_resonance(),
            average_coherence=self.get_average_coherence(),
            mala_progress=self.warps_completed / 108,
        )

    def reset(self) -> None:
        """Reset all warps."""
        for warp in self.warps:
            warp.reset()
        self.warps_completed = 0


# =============================================================================
# GPU GRID (n Blocks - Congregation)
# =============================================================================


class GridState(TypedDict):
    """
    State of the GPU grid (congregation).
    WATERTIGHT - no Any!
    """
    grid_size: int
    blocks_active: int
    total_resonance: float
    congregational_coherence: float
    total_cycles: int


@dataclass
class GPUGrid:
    """
    The GPU Grid - represents congregational chanting.

    Multiple blocks (malas) running in parallel.
    This is the "sankirtan" - congregational chanting.
    """
    grid_size: int = 1  # Number of parallel blocks
    blocks: List[GPUBlock] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize blocks if not provided."""
        if not self.blocks:
            self.blocks = [GPUBlock(block_id=i) for i in range(self.grid_size)]

    def launch(self, cycles_per_block: int = 108 * 16) -> List[BlockState]:
        """
        Launch the grid - run all blocks.

        Default: Each block runs one complete mala.
        """
        results: List[BlockState] = []
        for block in self.blocks:
            block.run_mala()
            results.append(block.get_state())
        return results

    def launch_parallel(self, cycles_per_block: int = 108 * 16) -> List[BlockState]:
        """
        Launch grid with true parallel execution.

        Uses ThreadPoolExecutor for concurrent processing.
        """
        results: List[BlockState] = []

        def run_block(block: GPUBlock) -> BlockState:
            block.run_mala()
            return block.get_state()

        with ThreadPoolExecutor(max_workers=self.grid_size) as executor:
            futures: List[Future[BlockState]] = [
                executor.submit(run_block, block)
                for block in self.blocks
            ]
            for future in futures:
                results.append(future.result())

        return results

    def get_congregational_coherence(self) -> float:
        """
        Compute coherence across the entire congregation.

        When many chanters are synchronized, resonance multiplies.
        """
        if not self.blocks:
            return 0.0

        coherences = [b.get_average_coherence() for b in self.blocks]
        if not coherences:
            return 0.0

        # Average coherence across all blocks
        mean_coherence = sum(coherences) / len(coherences)

        # Boost for multiple synchronized blocks
        sync_boost = math.log(len(self.blocks) + 1) / math.log(16 + 1)

        return min(1.0, mean_coherence * (1 + sync_boost))

    def get_state(self) -> GridState:
        """Get grid state."""
        return GridState(
            grid_size=self.grid_size,
            blocks_active=len(self.blocks),
            total_resonance=sum(b.get_total_resonance() for b in self.blocks),
            congregational_coherence=self.get_congregational_coherence(),
            total_cycles=sum(b.warps_completed * 16 * 16 for b in self.blocks),
        )

    def reset(self) -> None:
        """Reset all blocks."""
        for block in self.blocks:
            block.reset()


# =============================================================================
# MAHAMANTRA GPU PROTOCOL
# =============================================================================


@runtime_checkable
class MantraGPUProtocol(Protocol):
    """
    Protocol for Mahamantra GPU.

    Provides parallel processing of multiple mantra streams.
    """

    def create_thread(self) -> GPUThread:
        """Create a new GPU thread."""
        ...

    def create_warp(self) -> GPUWarp:
        """Create a new warp (16 threads)."""
        ...

    def create_block(self) -> GPUBlock:
        """Create a new block (108 warps)."""
        ...

    def launch_grid(self, size: int) -> GridState:
        """Launch a grid of specified size."""
        ...

    def compute_resonance_matrix(self, inputs: List[str]) -> List[float]:
        """Compute resonance for multiple inputs in parallel."""
        ...


# =============================================================================
# MAHAMANTRA GPU IMPLEMENTATION
# =============================================================================


@dataclass
class MantraGPU:
    """
    The Mahamantra GPU - Parallel Resonance Processor.

    SANKIRTAN = PARALLEL PROCESSING

    When many devotees chant together:
    - Each devotee = one thread
    - 16 synchronized = one warp
    - 108 rounds = one block (mala)
    - Many devotees = grid (congregation)

    The resonance multiplies through coherent parallel vibration.
    """

    # Current grid
    grid: Optional[GPUGrid] = None

    # Statistics
    total_threads_created: int = 0
    total_warps_created: int = 0
    total_blocks_created: int = 0

    def create_thread(self) -> GPUThread:
        """Create a new GPU thread."""
        self.total_threads_created += 1
        return GPUThread(thread_id=self.total_threads_created)

    def create_warp(self) -> GPUWarp:
        """Create a new warp (16 threads)."""
        self.total_warps_created += 1
        return GPUWarp(warp_id=self.total_warps_created)

    def create_block(self) -> GPUBlock:
        """Create a new block (108 warps)."""
        self.total_blocks_created += 1
        return GPUBlock(block_id=self.total_blocks_created)

    def launch_grid(self, size: int = 1, parallel: bool = False) -> GridState:
        """
        Launch a grid of specified size.

        Args:
            size: Number of parallel blocks (chanters)
            parallel: Use true parallel execution

        Returns:
            GridState with results
        """
        self.grid = GPUGrid(grid_size=size)

        if parallel:
            self.grid.launch_parallel()
        else:
            self.grid.launch()

        return self.grid.get_state()

    def compute_resonance_parallel(self, positions: List[int]) -> List[float]:
        """
        Compute resonance at multiple positions in parallel.

        Each position gets its own thread.
        """
        threads = [GPUThread(thread_id=i) for i in range(len(positions))]

        # Set each thread to start at its position
        for thread, pos in zip(threads, positions):
            thread.cpu.pc.jump(pos)

        # Run each thread for one vakya
        for thread in threads:
            thread.run(16)

        # Return resonances
        return [t.get_resonance() for t in threads]

    def sankirtan(self, devotee_count: int = 16) -> GridState:
        """
        Simulate congregational chanting (sankirtan).

        Args:
            devotee_count: Number of devotees chanting together

        Returns:
            GridState showing congregational resonance
        """
        # Each devotee is a thread, organized into warps
        warps_needed = (devotee_count + 15) // 16
        blocks_needed = (warps_needed + 107) // 108

        # Create grid
        self.grid = GPUGrid(grid_size=max(1, blocks_needed))

        # Run one round (108 mantras per devotee)
        self.grid.launch()

        return self.grid.get_state()

    def explain(self) -> str:
        """Explain current GPU state."""
        if not self.grid:
            return "GPU idle - no grid launched"

        state = self.grid.get_state()

        lines = [
            "═══════════════════════════════════════════════════════",
            "           MAHAMANTRA GPU STATE (SANKIRTAN)",
            "═══════════════════════════════════════════════════════",
            "",
            f"  Grid Size: {state['grid_size']} blocks",
            f"  Active Blocks: {state['blocks_active']}",
            f"  Total Cycles: {state['total_cycles']:,}",
            "",
            f"  Total Resonance: {state['total_resonance']:.3f}",
            f"  Congregational Coherence: {state['congregational_coherence']:.3f}",
            "",
            "═══════════════════════════════════════════════════════",
        ]

        return "\n".join(lines)


# =============================================================================
# GLOBAL GPU INSTANCE
# =============================================================================

_global_gpu: Optional[MantraGPU] = None


def get_gpu() -> MantraGPU:
    """Get the global MantraGPU instance."""
    global _global_gpu
    if _global_gpu is None:
        _global_gpu = MantraGPU()
    return _global_gpu


def sankirtan(devotee_count: int = 16) -> GridState:
    """Convenience: Run sankirtan with specified devotees."""
    return get_gpu().sankirtan(devotee_count)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ThreadState",
    "WarpState",
    "BlockState",
    "GridState",
    # Classes
    "GPUThread",
    "GPUWarp",
    "GPUBlock",
    "GPUGrid",
    "MantraGPU",
    # Protocol
    "MantraGPUProtocol",
    # Functions
    "get_gpu",
    "sankirtan",
]
