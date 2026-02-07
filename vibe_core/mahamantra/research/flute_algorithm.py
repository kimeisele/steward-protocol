"""
FLUTE ALGORITHM RESEARCH — Using the EXISTING Arsenal
======================================================

"venum kvanantam aravinda-dalayataksham"
— Brahma-samhita 5.30

WHAT EXISTS (the arsenal we must USE, not reinvent):
    MahaSynth          — 16-step modular sequencer with presets, ADSR, LFO, feedback
                          phoneme_step() bridges Sanskrit → synth, spell_cycle() runs words
    SankirtanChamber   — Resonance space: dance() applies DIW to cells, kirtan() = cycles×16
                          _accumulated_diw tracks XOR resonance, modes auto-escalate
    VenuOrchestrator   — 19-bit DIW LUT, step() O(1), 3 modes, DIW subscribers
    MahaCellUnified    — 72-byte header + lifecycle (prana/integrity/cycle)
    varnamala_codec    — Sanskrit ↔ RAMA coords (0-48, 6 bits each)
    pancha_walk        — 4D coordinates: element/varga/sub/harmonic (100% bijective)

THE GAP (what's missing):
    The chain is OPEN, not CLOSED:
        Synth → DIW → Chamber → Cell (STOP)
    Should be:
        Synth → DIW → Chamber → Cell → Resonance → back into Synth (FEEDBACK)

    The MahaSynth has feedback param. The Chamber has _accumulated_diw.
    They are NOT connected. This research connects them.

EXPERIMENTS:
    1. Use MahaSynth.spell_cycle() to run Mahajana names through the synth
    2. Use SankirtanChamber to transform cells with DIW
    3. Close the loop: cell resonance feeds back into synth
    4. Compare presets: which one makes Mahajana structure emerge?
    5. The Chaitanya equation: what if the synth chants continuously?

THIS IS RESEARCH. Dirty experiments in mahamantra/research/. Not production.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Dict, Final, List, NamedTuple, Tuple

sys.path.insert(0, "/Users/ss/projects/steward-protocol")

from vibe_core.mahamantra.protocols.seed._axioms import WORDS, TRINITY, HALVES
from vibe_core.mahamantra.protocols.seed._extended import MAHAMANTRA_WORD_PATTERN
from vibe_core.mahamantra.protocols.seed._primary import (
    KSETRAJNA, NAVA, QUARTERS, SHARANAGATI,
)
from vibe_core.mahamantra.protocols.seed._secondary import (
    JIVA_CYCLE, MALA, MAHAJANA_COUNT, PARAMPARA, QUALITIES, SEVEN, TEN,
)
from vibe_core.mahamantra.protocols.seed._algorithm import (
    MAHA_ADD, MAHA_MULT, MAHA_OP_MAP, MAHA_SQ,
)

PATTERN: Final[Tuple[str, ...]] = MAHAMANTRA_WORD_PATTERN


def run_experiments():
    """Run all research experiments using the EXISTING arsenal."""

    print("=" * 70)
    print("FLUTE ALGORITHM RESEARCH — Using the Existing Arsenal")
    print("=" * 70)

    # =========================================================================
    # EXP 1: MahaSynth — Run Mahajana names through spell_cycle()
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 1: MahaSynth.spell_cycle() — Mahajana names as phoneme sequences")
    print("="*70)

    from vibe_core.mahamantra.adapters.synth import MahaSynth, SYNTH_PRESETS
    from vibe_core.mahamantra.substrate.varnamala_codec import encode
    from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, MAHAMANTRA

    for preset_name in ["quantum", "classical", "wide", "nava"]:
        synth = MahaSynth(preset=preset_name)
        print(f"\n  Preset: {preset_name} (mod={synth.mod_space})")
        print(f"  {'pos':>4} {'name':<15} {'coords':<25} {'final':>6} {'attractor':>10}")
        print(f"  {'-'*65}")

        for i, gname in enumerate(ALL_GUARDIANS):
            coords = encode(gname)
            if not coords:
                continue
            # spell_cycle: each phoneme coord drives one synth step
            result = synth.spell_cycle(coords, seed=sum(coords))
            # Also find attractor for comparison
            resonance = synth.resonate(sum(coords))
            word = ["H", "K", "R"][MAHAMANTRA[i]]
            print(f"  {i:>4} {gname:<15} {str(coords):<25} {result.final_value:>6} {resonance.attractor:>10} ({word})")

    # =========================================================================
    # EXP 2: SankirtanChamber — Transform cells with DIW
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 2: SankirtanChamber — Mahajana names as cells through kirtan()")
    print("="*70)

    from vibe_core.mahamantra.substrate.chamber import SankirtanChamber, reset_chamber
    from vibe_core.mahamantra.substrate.cell import MahaCellUnified

    reset_chamber()
    chamber = SankirtanChamber.create()

    print(f"\n  {'pos':>4} {'name':<15} {'prana_before':>12} {'prana_after':>12} {'integrity':>10} {'cycles':>7}")
    print(f"  {'-'*65}")

    cell_results = []
    for i, gname in enumerate(ALL_GUARDIANS):
        cell = MahaCellUnified.from_content(gname, register=False)
        prana_before = cell.lifecycle.prana

        # 1 kirtan cycle = 16 dance() calls = 16 DIW applications
        result_cell = chamber.dance(cell)

        cell_results.append({
            "pos": i,
            "name": gname,
            "prana": result_cell.lifecycle.prana,
            "integrity": result_cell.lifecycle.integrity,
            "cycle": result_cell.lifecycle.cycle,
            "word": ["H", "K", "R"][MAHAMANTRA[i]],
        })

        print(f"  {i:>4} {gname:<15} {prana_before:>12} {result_cell.lifecycle.prana:>12} {result_cell.lifecycle.integrity:>10.4f} {result_cell.lifecycle.cycle:>7}")

    print(f"\n  Chamber stats: {chamber.total_transformations} transformations, {chamber.resonance_count} resonances")
    print(f"  Accumulated DIW: {chamber._accumulated_diw} (0x{chamber._accumulated_diw:05x})")

    # =========================================================================
    # EXP 3: Close the Loop — Cell resonance feeds back into synth
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 3: CLOSED LOOP — Cell prana feeds back as synth seed")
    print("="*70)

    synth = MahaSynth(preset="quantum")
    reset_chamber()
    chamber = SankirtanChamber.create()

    print(f"\n  Round 1: Name → Synth → Cell → Prana")
    print(f"  Round 2: Prana → Synth → Cell → Prana (feedback)")
    print(f"  Round 3: Prana → Synth → Cell → Prana (convergence?)")

    for i, gname in enumerate(ALL_GUARDIANS):
        coords = encode(gname)
        if not coords:
            continue

        # Round 1: Name → Synth
        r1 = synth.spell_cycle(coords, seed=sum(coords))
        seed1 = r1.final_value

        # Round 1: Synth output → Cell
        cell = MahaCellUnified.from_content(gname, register=False)
        cell = chamber.dance(cell)
        prana1 = cell.lifecycle.prana

        # Round 2: Prana → Synth (FEEDBACK!)
        r2 = synth.spell_cycle(coords, seed=prana1)
        seed2 = r2.final_value

        # Round 3: Convergence check
        r3 = synth.spell_cycle(coords, seed=seed2)
        seed3 = r3.final_value

        converged = "✓" if seed2 == seed3 else "→"
        word = ["H", "K", "R"][MAHAMANTRA[i]]
        print(f"  pos {i:>2} {gname:<15} {sum(coords):>4}→{seed1:>4}→{seed2:>4}→{seed3:>4} {converged} ({word})")

    # =========================================================================
    # EXP 4: Sankirtan — Mass chanting, do cells cluster by quarter?
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 4: Sankirtan — Mass chanting, quarter clustering")
    print("="*70)

    reset_chamber()
    chamber = SankirtanChamber.create()

    all_cells = []
    for gname in ALL_GUARDIANS:
        cell = MahaCellUnified.from_content(gname, register=False)
        all_cells.append(cell)

    cluster = chamber.sankirtan(all_cells)
    print(f"\n  Cluster attractor: {cluster.resonance_attractor}")
    print(f"  Cluster coherence: {cluster.coherence:.4f}")
    print(f"  Cells in cluster: {len(cluster.cells)}")

    # Check if cells group by quarter
    quarter_prana = defaultdict(list)
    for i, cell in enumerate(cluster.cells):
        q = i // (WORDS // QUARTERS)
        quarter_prana[q].append(cell.lifecycle.prana)

    print(f"\n  Prana by quarter:")
    for q in sorted(quarter_prana):
        vals = quarter_prana[q]
        avg = sum(vals) / len(vals)
        print(f"    Q{q}: avg={avg:.0f}, range=[{min(vals)}, {max(vals)}]")

    # =========================================================================
    # EXP 5: Chaitanya Equation — Continuous chanting (many rounds)
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 5: Chaitanya Equation — Does continuous chanting converge?")
    print("="*70)

    reset_chamber()
    chamber = SankirtanChamber.create()

    # Take one name and chant it through many kirtan rounds
    test_name = "kumaras"
    cell = MahaCellUnified.from_content(test_name, register=False)

    print(f"\n  Chanting '{test_name}' through {MAHAJANA_COUNT} kirtan rounds:")
    print(f"  {'round':>6} {'prana':>8} {'integrity':>10} {'cycle':>7} {'acc_diw':>10}")
    print(f"  {'-'*50}")

    for round_num in range(1, MAHAJANA_COUNT + 1):
        cell = chamber.kirtan(cell, cycles=1)
        if round_num <= 4 or round_num >= MAHAJANA_COUNT - 1:
            print(f"  {round_num:>6} {cell.lifecycle.prana:>8} {cell.lifecycle.integrity:>10.4f} {cell.lifecycle.cycle:>7} {chamber._accumulated_diw:>10}")
        elif round_num == 5:
            print(f"  {'...':>6}")

    print(f"\n  Final: prana={cell.lifecycle.prana}, integrity={cell.lifecycle.integrity:.4f}")
    print(f"  Chamber: {chamber.total_transformations} total transformations")

    # =========================================================================
    # EXP 6: Preset comparison — which preset best separates Mahajanas?
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 6: Which synth preset best differentiates Mahajana names?")
    print("="*70)

    for preset_name in sorted(SYNTH_PRESETS.keys()):
        synth = MahaSynth(preset=preset_name)
        attractors = set()
        final_vals = set()
        for gname in ALL_GUARDIANS:
            coords = encode(gname)
            if not coords:
                continue
            r = synth.spell_cycle(coords, seed=sum(coords))
            final_vals.add(r.final_value)
            res = synth.resonate(sum(coords))
            attractors.add(res.attractor)

        print(f"  {preset_name:<12} mod={synth.mod_space:>4}: {len(final_vals):>2}/16 unique finals, {len(attractors):>2} attractors")

    # =========================================================================
    # EXP 7: The 3 Ur-Names — Hare, Krishna, Rama through spell_cycle
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 7: The 3 Ur-Names through spell_cycle (all presets)")
    print("="*70)

    for ur_name in ["hare", "kṛṣṇa", "rāma"]:
        coords = encode(ur_name)
        if not coords:
            print(f"  {ur_name}: no encoding")
            continue
        print(f"\n  {ur_name}: coords={coords}, sum={sum(coords)}")
        for preset_name in ["quantum", "classical", "wide"]:
            synth = MahaSynth(preset=preset_name)
            r = synth.spell_cycle(coords, seed=sum(coords))
            res = synth.resonate(sum(coords))
            print(f"    {preset_name:<12}: spell→{r.final_value:>4}, attractor→{res.attractor:>4} (cycle_len={res.cycle_length})")

    # =========================================================================
    # EXP 8: VenuOrchestrator DIW analysis — what does the LUT actually produce?
    # =========================================================================
    print(f"\n{'='*70}")
    print("EXP 8: VenuOrchestrator — THE_FLUTE_CYCLE LUT analysis")
    print("="*70)

    from vibe_core.mahamantra.substrate.venu_orchestrator import THE_FLUTE_CYCLE
    from vibe_core.mahamantra.protocols.diw import unpack, DIW_MASK

    print(f"\n  {'pos':>4} {'word':<3} {'DIW':>8} {'VENU':>5} {'VAMSI':>6} {'MURALI':>7}")
    print(f"  {'-'*40}")

    cycle_xor = 0
    for pos, diw in enumerate(THE_FLUTE_CYCLE):
        parts = unpack(diw)
        word = MAHAMANTRA_WORD_PATTERN[pos]
        cycle_xor ^= diw & DIW_MASK
        print(f"  {pos:>4} {word:<3} {diw:>8} {parts.venu:>5} {parts.vamsi:>6} {parts.murali:>7}")

    print(f"\n  Cycle XOR: {cycle_xor} (0x{cycle_xor:05x})")
    print(f"  Cycle XOR mod PARAMPARA({PARAMPARA}): {cycle_xor % PARAMPARA}")
    print(f"  Cycle XOR mod MALA({MALA}): {cycle_xor % MALA}")


if __name__ == "__main__":
    run_experiments()
