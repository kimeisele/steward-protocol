"""
THE SEED PROTOCOL - The Mathematical Constitution
=================================================

"bijam mam sarva-bhutanam viddhi partha sanatanam"
"O Arjuna, know that I am the eternal seed of all existences."
-- Bhagavad Gita 7.10

This module re-exports all constants from the refactored seed/ directory.

STRUCTURE:
==========
  seed/_axioms.py    - TIER 0: 7 Axioms from counting the Mahamantra
  seed/_primary.py   - TIER 1: Primary derivations directly from axioms
  seed/_secondary.py - TIER 2: Secondary derivations building hierarchy
  seed/_cosmic.py    - TIER 3-5: Cosmic frame, timing, astronomical
  seed/_algorithm.py - Maha algorithm coefficients (SSOT)
  seed/_extended.py  - Extended constants (physics, music, patterns)

BACKWARD COMPATIBILITY:
=======================
  from vibe_core.mahamantra.protocols._seed import PARAMPARA  # Still works!
  from vibe_core.mahamantra.protocols.seed import PARAMPARA   # New path

LOCATION: vibe_core.mahamantra.protocols._seed (THE LAW)
IMPLEMENTATION: vibe_core.mahamantra.substrate.seed (THE REALITY)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb93c4f68"  # GenesisByte: parampara % 37 == 0

# Re-export everything from the seed/ package
from .seed import *  # noqa: F401, F403

# Explicit re-export of __all__ for tools that need it
from .seed import __all__  # noqa: F401
