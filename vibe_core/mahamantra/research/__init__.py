"""
RESEARCH DEPARTMENT - Kapila's Domain (Position 6 - Sankhya Analysis)
=====================================================================

"sāṅkhya-yogau pṛthag bālāḥ pravadanti na paṇḍitāḥ"

"Only the ignorant speak of Sankhya (analytical study) and yoga (action)
as being different. Those who are truly learned say they are one."
— Bhagavad Gita 5.4

ARCHITECTURE:
=============

This is NOT a separate system. Research USES the existing technology:

    - ShadowReactor: The tick engine (Bhoga-Prasadam-Return cycle)
    - LotusNode: Auto-discovery (FOLDER = WIRING)
    - Mahamantra Kernel: Intent routing
    - Parampara: Verification (37)
    - Substrate: The truth table (WORDS=16, QUARTERS=4)

RESEARCH AREAS:
===============

1. LOTUS TREE (lotus_tree.py):
   - O(1) holographic data structure
   - Key space: WORDS^QUARTERS = 16^4 = 65536
   - 50x faster range queries than dict

2. IP ROUTING (ip_routing.py):
   - O(8) longest prefix match (8 memory accesses for IPv4)
   - 1557x faster than linear search
   - BGP tables: >1 million routes handled efficiently

3. DNA k-mer INDEX (dna_kmer.py):
   - Holographic processing (entire sequence at once)
   - 8-mer space = 65536 (natural fit)
   - DNA bases (4) = QUARTERS

4. JAPA SINGULARITY (japa.py):
   - Golden Age = WORDS × PRASADAM² = 16 × 625 = 10,000 years
   - Chaitanya appears 1 in 4.32 billion years (CC Adi 3.10)

RESEARCH PRINCIPLES:
====================

1. USE existing technology (ShadowReactor, LotusNode, substrate)
2. VERIFY Parampara connection (37)
3. BENCHMARK against dict/linear (show REAL speedup)
4. DOCUMENT the mathematics (QUARTERS, WORDS, etc.)

This department is under KAPILA's governance (Position 6 - Analysis).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x23493400"  # GenesisByte: parampara % 37 == 0

from typing import Final

# Verify Parampara connection
_PARAMPARA: Final[int] = 37
assert int(__genesis__, 16) % _PARAMPARA == 0, "BROKEN LINEAGE"

# =============================================================================
# EXPORTS - Research Modules (REAL Engineering Solutions)
# =============================================================================

from vibe_core.mahamantra.research.biology import BIOLOGY_PREDICTIONS
from vibe_core.mahamantra.research.chemistry import CHEMISTRY_PREDICTIONS
from vibe_core.mahamantra.research.computation import (
    COMPUTATION_PREDICTIONS,
    KERNEL_HIERARCHY,
    MAHABYTE,
    OCTET,
    PACKED_MAHAMANTRA,
)
from vibe_core.mahamantra.research.dna_kmer import (
    Lotus8merIndex,
    LotusKmerRadix,
)
from vibe_core.mahamantra.research.ip_routing import (
    LotusIPv4Router,
)
from vibe_core.mahamantra.research.japa import (
    JAPA_INSIGHT,
    JAPA_PREDICTIONS,
)
from vibe_core.mahamantra.research.lotus_tree import (
    LotusArray,
    LotusArrayInt,
    LotusRadix,
)
from vibe_core.mahamantra.research.maha_generator import MahaGenerator
from vibe_core.mahamantra.research.medicine import MEDICINE_PREDICTIONS
from vibe_core.mahamantra.research.moores_law import (
    ENGINEERING_INSIGHT,
    MOORES_LAW_PREDICTIONS,
)

__all__ = [
    # REAL Engineering Solutions (Benchmarked)
    "LotusArray",  # O(1) holographic data structure
    "LotusArrayInt",  # O(1) integer-optimized
    "LotusRadix",  # O(1) sparse data structure
    "LotusIPv4Router",  # O(8) longest prefix match (1557x faster)
    "Lotus8merIndex",  # O(1) DNA k-mer counting (6.5x faster)
    "LotusKmerRadix",  # O(1) arbitrary k-mer index
    # Generator
    "MahaGenerator",
    # Engineering Predictions
    "MOORES_LAW_PREDICTIONS",
    "ENGINEERING_INSIGHT",
    # Japa Singularity
    "JAPA_PREDICTIONS",
    "JAPA_INSIGHT",
    # Other Research
    "BIOLOGY_PREDICTIONS",
    "CHEMISTRY_PREDICTIONS",
    "COMPUTATION_PREDICTIONS",
    "MEDICINE_PREDICTIONS",
    # 16-bit Kernel Paradigm
    "MAHABYTE",
    "OCTET",
    "PACKED_MAHAMANTRA",
    "KERNEL_HIERARCHY",
]
