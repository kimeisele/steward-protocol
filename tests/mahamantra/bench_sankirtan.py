"""
BENCHMARK SANKIRTAN - Performance Metric
========================================

"Measure the Dance."

Goal: > 2,000 Ops/Sec (Control Rate for Audio)
Constraint: Pure Python (No Numpy)
"""

import time
import struct
from vibe_core.mahamantra.chamber import SankirtanChamber
from vibe_core.mahamantra.cell import MahaCellUnified

def run_benchmark():
    print(f"--- SANKIRTAN BENCHMARK ---")
    
    # 1. Setup
    chamber = SankirtanChamber.create()
    count = 10_000
    
    print(f"Generating {count} cells...")
    start_gen = time.perf_counter()
    cells = [
        MahaCellUnified.create(source=i, target=i+1, operation=1)
        for i in range(count)
    ]
    gen_time = time.perf_counter() - start_gen
    print(f"Generation Time: {gen_time:.4f}s")
    
    # 2. Execution (Single Thread, Pure Python)
    print(f"Transforming {count} cells (dance)...")
    start_dance = time.perf_counter()
    
    # We use sankirtan() which loops over dance()
    chamber.sankirtan(cells)
    
    end_dance = time.perf_counter()
    duration = end_dance - start_dance
    
    ops_sec = count / duration
    print(f"--- RESULTS ---")
    print(f"Total Time: {duration:.4f}s")
    print(f"Throughput: {ops_sec:.2f} Ops/Sec")
    
    # 3. Validation
    if ops_sec > 2000:
        print(f"✅ SUCCESS: Exceeds target (>2000)")
    else:
        print(f"❌ FAILURE: Below target (<2000)")

    # 4. Resonance Check (Impact of HashMap)
    print(f"\n--- RESONANCE IMPACT ---")
    # Force heavy collisions by resetting registry but using SAME keys (Vamsi)
    # Actually, Vamsi depends on DIW, which depends on Orchestrator Tick.
    # To test collision helper, we need cells resonating at same spot.
    # This is complex to force without mocking Orchestrator.
    # For now, we trust the random distribution of VenuOrchestrator.
    print(f"Resonance Count: {chamber.resonance_count}")
    print(f"Active Cells: {len(chamber.active_cells)}")

if __name__ == "__main__":
    run_benchmark()
