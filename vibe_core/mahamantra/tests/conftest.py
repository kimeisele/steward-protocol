"""
Test configuration for mahamantra tests.

Resets module-level singletons between test modules to prevent
state pollution (Chamber accumulates prana, Composition tracks count, etc.).
"""

import pytest


@pytest.fixture(autouse=True, scope="function")
def _reset_singletons():
    """Reset singletons that leak state between tests.

    Chamber, Composition, Engine, and MahamantraLotus are module-level
    singletons that accumulate state (prana, dance cycles, compositions).
    Without reset, test ordering changes results — especially PranaScorer
    which reads accumulated Antaranga prana.
    """
    yield

    # Reset ALL singletons that accumulate state between tests.
    # Chamber is the worst — prana, dance cycles, Antaranga bytearray.
    # Lotus caches _PipelineCache + _mahamantra_instance.
    # Composition + Engine track counts and last_context.

    import vibe_core.mahamantra.adapters.composition as comp_mod
    comp_mod._composition_instance = None

    import vibe_core.mahamantra.substrate.language.engine as eng_mod
    eng_mod._ENGINE = None

    import vibe_core.mahamantra.substrate.chamber as chamber_mod
    chamber_mod._chamber_instance = None

    import vibe_core.mahamantra.substrate.lotus_core as lotus_mod
    lotus_mod._mahamantra_instance = None
    lotus_mod._PIPELINE = None

    import vibe_core.mahamantra.substrate.maha_llm_kernel as kernel_mod
    kernel_mod._KERNEL = None

    import vibe_core.mahamantra.substrate.wordnet_bridge as wb_mod
    wb_mod._token_to_chains = None
    wb_mod._word_chain_sets.clear()
    wb_mod._word_entries = None
    wb_mod._synset_list = None
    wb_mod._sid_to_int = None
    wb_mod._input_chain_ints.cache_clear()
    wb_mod._input_stems.cache_clear()
