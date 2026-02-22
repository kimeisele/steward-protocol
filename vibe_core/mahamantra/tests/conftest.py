"""
Test configuration for mahamantra tests.

Resets module-level singletons between test modules to prevent
state pollution (Chamber accumulates prana, Composition tracks count, etc.).
"""

import pytest


@pytest.fixture(autouse=True, scope="function")
def _reset_singletons():
    """Reset MUTABLE STATE between tests without destroying stateless caches.

    WHAT RESETS (mutable — leaks between tests):
      - Chamber: prana, dance cycles, Antaranga bytes → .reset()
      - Lotus: _akash accumulator, instance → fresh instance
      - Composition: _compositions counter, _last_context
      - Wordnet LRU caches: input-dependent results

    WHAT SURVIVES (stateless — expensive to rebuild, safe to keep):
      - _PipelineCache: only function refs + constants (20 imports saved)
      - _ENGINE: completely stateless (no __init__, no instance vars)
      - _KERNEL: MahaLLMKernel singleton (stateless router)
      - Wordnet JSON data: _word_entries, _synset_list, _sid_to_int (immutable)
      - _word_chain_sets: derived from immutable JSON (frozensets)

    This cuts per-test overhead from ~20 import resolutions + 16KB alloc
    to a few dict clears and an Antaranga ctypes.memset.
    """
    yield

    # --- Chamber: reset state, keep the allocation ---
    import vibe_core.mahamantra.substrate.chamber as chamber_mod

    if chamber_mod._chamber_instance is not None:
        chamber_mod._chamber_instance.reset()

    # --- Lotus: fresh instance, but _PipelineCache survives ---
    import vibe_core.mahamantra.substrate.lotus_core as lotus_mod

    lotus_mod._mahamantra_instance = None
    # _PIPELINE is stateless (function refs + constants) — DO NOT reset

    # --- Lotus class-level Akash state (accumulates across instances) ---
    from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

    MahamantraLotus._akash = {
        "resonance_level": 0,
        "accumulated_value": 0,
        "total_beats": 0,
        "total_rounds": 0,
        "attractor_counts": {},
        "last_seed": None,
        "last_position": None,
        "last_attractor": None,
    }

    # --- Composition: reset counters, keep scorers ---
    import vibe_core.mahamantra.adapters.composition as comp_mod

    if comp_mod._composition_instance is not None:
        comp_mod._composition_instance._compositions = 0
        comp_mod._composition_instance._last_context = {}

    # --- Engine: stateless, DO NOT reset ---
    # --- MahaLLMKernel: stateless router, DO NOT reset ---

    # --- Wordnet: clear input-dependent LRU caches only ---
    # JSON data (_word_entries, _synset_list, _sid_to_int) is immutable.
    # _word_chain_sets is derived from immutable data (frozensets).
    import vibe_core.mahamantra.substrate.wordnet_bridge as wb_mod

    wb_mod._input_chain_ints.cache_clear()
    wb_mod._input_stems.cache_clear()
