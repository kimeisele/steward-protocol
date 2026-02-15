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

    # Reset after each test function
    import vibe_core.mahamantra.adapters.composition as comp_mod
    comp_mod._composition_instance = None

    import vibe_core.mahamantra.substrate.language.engine as eng_mod
    eng_mod._ENGINE = None
