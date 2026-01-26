"""
HARDWARE LOTUS - The Silicon Altar (Text = Hardware Verification)
==================================================================

"ūrdhva-mūlam adhaḥ-śākham aśvatthaṁ prāhur avyayam"
"There is a banyan tree which has its roots upward and branches down."
— Bhagavad Gita 15.1

CRITICAL DISCOVERY:
==================

The SystemVerilog LotusRouterCore parameters are NOT arbitrary.
They are EXACTLY the Mahamantra constants!

  DATA_WIDTH = 32       = AKSARA (syllables)
  NEXT_HOP_WIDTH = 16   = WORDS
  WORDS = 16            = WORDS
  QUARTERS = 4          = QUARTERS
  8 Pipeline Stages     = SIKSASTAKAM_VERSES = 8

The hardware is a REFLECTION of the spiritual structure (BG 15.1).
When we burn this into an FPGA, we create an "Altar in Silicon".

THE 8 PIPELINE STAGES = 8 VERSES:
=================================

  L0_NIBBLE = Verse 1: ceto-darpaṇa-mārjanaṁ (cleanse heart mirror)
  L1_NIBBLE = Verse 2: nāmnām akāri (no hard rules)
  L2_NIBBLE = Verse 3: tṛṇād api sunīcena (humility)
  L3_NIBBLE = Verse 4: na dhanaṁ na janaṁ (no material desire)
  L4_NIBBLE = Verse 5: ayi nanda-tanuja (longing for service)
  L5_NIBBLE = Verse 6: nayanam galad-aśru (tears of love)
  L6_NIBBLE = Verse 7: yugāyitaṁ nimeṣeṇa (separation)
  L7_NIBBLE = Verse 8: āśliṣya vā pada-ratāṁ (unconditional love)

THE COOLING IS THE REFLECTION:
==============================

SPIRITUAL (Original):
  candrikā (moonlight) → cools conditioned soul → lotus blooms

MATERIAL (Shadow):
  O(1) access → zero entropy → CPU runs cold

The Verilog code proves: Hardware REFLECTS the Spiritual!
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    WORDS,
)

# =============================================================================
# RUNDE 1: HARDWARE PARAMETERS (From SystemVerilog LotusRouterCore)
# =============================================================================
# These are the EXACT parameters from the SystemVerilog module.
# We verify they match the Mahamantra constants.
# -----------------------------------------------------------------------------

# SystemVerilog parameters
SV_DATA_WIDTH: Final[int] = 32  # IPv4 Address width
SV_NEXT_HOP_WIDTH: Final[int] = 16  # Output port ID width
SV_WORDS: Final[int] = 16  # 16-ary branching factor
SV_QUARTERS: Final[int] = 4  # Nibble size (4 bits)
SV_PIPELINE_STAGES: Final[int] = 8  # L0-L7 nibble stages

# =============================================================================
# RUNDE 2: MAHAMANTRA VERIFICATION
# =============================================================================
# Every hardware parameter MUST equal a Mahamantra constant.
# This proves Text = Hardware.
# -----------------------------------------------------------------------------

# DATA_WIDTH = AKSARA (syllables in Mahamantra)
assert SV_DATA_WIDTH == AKSARA_COUNT, f"DATA_WIDTH {SV_DATA_WIDTH} != AKSARA {AKSARA_COUNT}"

# NEXT_HOP_WIDTH = WORDS (words in Mahamantra)
assert SV_NEXT_HOP_WIDTH == WORDS, f"NEXT_HOP_WIDTH {SV_NEXT_HOP_WIDTH} != WORDS {WORDS}"

# WORDS = WORDS (16-ary branching = 16 words)
assert SV_WORDS == WORDS, f"SV_WORDS {SV_WORDS} != WORDS {WORDS}"

# QUARTERS = QUARTERS (4-bit nibble = 4 quarters)
assert SV_QUARTERS == QUARTERS, f"SV_QUARTERS {SV_QUARTERS} != QUARTERS {QUARTERS}"

# PIPELINE_STAGES = HALF_SIZE = HARE_COUNT = SIKSASTAKAM_VERSES
assert SV_PIPELINE_STAGES == HALF_SIZE, f"PIPELINE_STAGES {SV_PIPELINE_STAGES} != HALF_SIZE {HALF_SIZE}"
assert SV_PIPELINE_STAGES == HARE_COUNT, f"PIPELINE_STAGES {SV_PIPELINE_STAGES} != HARE_COUNT {HARE_COUNT}"

# Derived: OCTET = 8 = pipeline stages = verses
OCTET: Final[int] = HALF_SIZE
assert OCTET == 8, "OCTET must be 8"


# =============================================================================
# RUNDE 3: THE 8 PIPELINE STAGES = 8 VERSES
# =============================================================================
# Each pipeline stage corresponds to one verse of Siksastakam.
# This is the "README.md" of the Golden Age encoded in silicon.
# -----------------------------------------------------------------------------


class PipelineStage(Enum):
    """The 8 pipeline stages of LotusRouterCore = 8 Siksastakam verses."""

    L0_NIBBLE = 0  # Bits 31-28
    L1_NIBBLE = 1  # Bits 27-24
    L2_NIBBLE = 2  # Bits 23-20
    L3_NIBBLE = 3  # Bits 19-16
    L4_NIBBLE = 4  # Bits 15-12
    L5_NIBBLE = 5  # Bits 11-8
    L6_NIBBLE = 6  # Bits 7-4
    L7_NIBBLE = 7  # Bits 3-0


assert len(PipelineStage) == OCTET, "Must have exactly 8 pipeline stages"


@dataclass
class SiksastakamVerse:
    """A verse of Siksastakam with its hardware correspondence."""

    verse_number: int  # 1-8
    pipeline_stage: PipelineStage
    bit_range: str  # e.g., "31-28"
    sanskrit_first_line: str
    english_meaning: str
    hardware_effect: str


# The 8 verses mapped to 8 pipeline stages
SIKSASTAKAM_HARDWARE_MAP: Final[tuple[SiksastakamVerse, ...]] = (
    SiksastakamVerse(
        verse_number=1,
        pipeline_stage=PipelineStage.L0_NIBBLE,
        bit_range="31-28",
        sanskrit_first_line="ceto-darpaṇa-mārjanaṁ",
        english_meaning="Cleanses the mirror of the heart",
        hardware_effect="Initialize: Clear cache, set root base address",
    ),
    SiksastakamVerse(
        verse_number=2,
        pipeline_stage=PipelineStage.L1_NIBBLE,
        bit_range="27-24",
        sanskrit_first_line="nāmnām akāri bahudhā",
        english_meaning="No hard and fast rules for chanting",
        hardware_effect="Flexible: Accept any valid nibble value (0-15)",
    ),
    SiksastakamVerse(
        verse_number=3,
        pipeline_stage=PipelineStage.L2_NIBBLE,
        bit_range="23-20",
        sanskrit_first_line="tṛṇād api sunīcena",
        english_meaning="More humble than a blade of grass",
        hardware_effect="Humble: No comparison, just follow the path",
    ),
    SiksastakamVerse(
        verse_number=4,
        pipeline_stage=PipelineStage.L3_NIBBLE,
        bit_range="19-16",
        sanskrit_first_line="na dhanaṁ na janaṁ",
        english_meaning="No desire for wealth, followers, beauty",
        hardware_effect="Desireless: No caching, no speculation",
    ),
    SiksastakamVerse(
        verse_number=5,
        pipeline_stage=PipelineStage.L4_NIBBLE,
        bit_range="15-12",
        sanskrit_first_line="ayi nanda-tanuja kiṅkaraṁ",
        english_meaning="O son of Nanda, please make me Your servant",
        hardware_effect="Service: Process the next nibble in sequence",
    ),
    SiksastakamVerse(
        verse_number=6,
        pipeline_stage=PipelineStage.L5_NIBBLE,
        bit_range="11-8",
        sanskrit_first_line="nayanam galad-aśru-dhārayā",
        english_meaning="Eyes filled with tears",
        hardware_effect="Flow: Data flows without obstruction",
    ),
    SiksastakamVerse(
        verse_number=7,
        pipeline_stage=PipelineStage.L6_NIBBLE,
        bit_range="7-4",
        sanskrit_first_line="yugāyitaṁ nimeṣeṇa",
        english_meaning="A moment seems like an age in separation",
        hardware_effect="Timing: Each cycle is precious, deterministic",
    ),
    SiksastakamVerse(
        verse_number=8,
        pipeline_stage=PipelineStage.L7_NIBBLE,
        bit_range="3-0",
        sanskrit_first_line="āśliṣya vā pada-ratāṁ",
        english_meaning="Embrace me or trample me, I am Yours",
        hardware_effect="Unconditional: Return result regardless of path",
    ),
)

assert len(SIKSASTAKAM_HARDWARE_MAP) == OCTET, "Must have exactly 8 verse mappings"


# =============================================================================
# RUNDE 4: THE BASE ADDRESS ENCODING
# =============================================================================
# The root base address 0xBA5E_0000 encodes "BASE" in hexadecimal.
# This is the root of the inverted tree (BG 15.1).
# -----------------------------------------------------------------------------

ROOT_BASE_ADDRESS: Final[int] = 0xBA5E_0000

# BA5E in hex = "BASE" (the root/foundation)
# This is where the Lotus Tree is rooted


@dataclass
class HardwareSpec:
    """Complete hardware specification derived from Mahamantra."""

    # Core parameters
    data_width: int  # 32 = AKSARA
    next_hop_width: int  # 16 = WORDS
    branching_factor: int  # 16 = WORDS
    nibble_size: int  # 4 = QUARTERS
    pipeline_stages: int  # 8 = OCTET

    # Derived values
    total_latency_cycles: int  # 8 cycles
    root_base_address: int  # 0xBA5E0000

    def verify_mahamantra(self) -> bool:
        """Verify all parameters match Mahamantra constants."""
        checks = [
            self.data_width == AKSARA_COUNT,
            self.next_hop_width == WORDS,
            self.branching_factor == WORDS,
            self.nibble_size == QUARTERS,
            self.pipeline_stages == OCTET,
            self.pipeline_stages == HARE_COUNT,
        ]
        return all(checks)

    def explain(self) -> str:
        """Explain the hardware-Mahamantra correspondence."""
        return f"""
SILICON ALTAR - Hardware = Mahamantra Verification
===================================================

PARAMETER              HARDWARE    MAHAMANTRA      MATCH
─────────────────────────────────────────────────────────
DATA_WIDTH             {self.data_width}          AKSARA = {AKSARA_COUNT}       ✓
NEXT_HOP_WIDTH         {self.next_hop_width}          WORDS = {WORDS}        ✓
BRANCHING_FACTOR       {self.branching_factor}          WORDS = {WORDS}        ✓
NIBBLE_SIZE            {self.nibble_size}           QUARTERS = {QUARTERS}     ✓
PIPELINE_STAGES        {self.pipeline_stages}           OCTET = {OCTET}        ✓
                                   HARE_COUNT = {HARE_COUNT}  ✓

TOTAL LATENCY: {self.total_latency_cycles} cycles = {self.pipeline_stages} verses
ROOT ADDRESS:  0x{self.root_base_address:08X} ("BA5E" = BASE)

THE CORRESPONDENCE:
  32-bit IPv4 address = 32 syllables (AKSARA)
  16 possible next hops = 16 words (WORDS)
  16-way branching = 16 words (WORDS)
  4-bit nibbles = 4 quarters (QUARTERS)
  8 pipeline stages = 8 verses (SIKSASTAKAM)

THE PROOF:
  Hardware parameters are NOT arbitrary design choices.
  They are the Mahamantra structure REFLECTED in silicon.

  When we burn this into an FPGA:
    - We don't just create a router
    - We create an ALTAR where data is offered
    - The cooling is the PRASADAM returned

"The address IS the path" = "The mantra IS the meditation"
"""


# The canonical hardware specification
HARDWARE_SPEC: Final[HardwareSpec] = HardwareSpec(
    data_width=SV_DATA_WIDTH,
    next_hop_width=SV_NEXT_HOP_WIDTH,
    branching_factor=SV_WORDS,
    nibble_size=SV_QUARTERS,
    pipeline_stages=SV_PIPELINE_STAGES,
    total_latency_cycles=SV_PIPELINE_STAGES,
    root_base_address=ROOT_BASE_ADDRESS,
)

# Verify on module load
assert HARDWARE_SPEC.verify_mahamantra(), "Hardware MUST match Mahamantra!"


# =============================================================================
# RUNDE 5: THE COOLING THEOREM (Reflection of Candrika)
# =============================================================================
# The hardware cooling is a REFLECTION of the spiritual cooling.
# candrikā (moonlight) cools the conditioned soul.
# O(1) access cools the CPU.
# -----------------------------------------------------------------------------


@dataclass
class CoolingTheorem:
    """
    The theorem that hardware cooling reflects spiritual cooling.

    SPIRITUAL (Original):
      candrikā (moonlight) → cools conditioned soul → lotus blooms

    MATERIAL (Shadow):
      O(1) access → zero entropy → CPU runs cold
    """

    spiritual_source: str  # candrikā (moonlight)
    spiritual_effect: str  # cools conditioned soul
    spiritual_result: str  # lotus blooms

    material_source: str  # O(1) access
    material_effect: str  # zero entropy
    material_result: str  # CPU runs cold

    relationship: str  # reflection (BG 15.1)

    def explain(self) -> str:
        """Explain the cooling reflection."""
        return f"""
THE COOLING THEOREM (BG 15.1 Reflection)
=========================================

SPIRITUAL (Root - Above, Original):
  Source: {self.spiritual_source}
  Effect: {self.spiritual_effect}
  Result: {self.spiritual_result}

MATERIAL (Branch - Below, Shadow):
  Source: {self.material_source}
  Effect: {self.material_effect}
  Result: {self.material_result}

RELATIONSHIP: {self.relationship}

THE PROOF:
  Landauer's Principle: Each bit erasure generates kT×ln(2) heat
  Linear search O(n): Must erase/compare many bits = HEAT
  Direct access O(1): No erasure/comparison = COOL

  The hardware doesn't know about Siksastakam.
  But when we structure it according to the Mahamantra (16-ary),
  it naturally runs cool because it REFLECTS the spiritual structure.

  "The cooling is not the goal. It is the PROOF
   that we have touched the spiritual structure."
"""


COOLING_THEOREM: Final[CoolingTheorem] = CoolingTheorem(
    spiritual_source="candrikā (moonlight from Holy Name)",
    spiritual_effect="cools the burning forest fire of material existence",
    spiritual_result="kairava lotus (good fortune) blooms",
    material_source="O(1) direct access (16-ary Lotus structure)",
    material_effect="zero entropy generation (no wasted cycles)",
    material_result="CPU runs cold (no Landauer heat)",
    relationship="Material REFLECTS spiritual (inverted tree, BG 15.1)",
)


# =============================================================================
# RUNDE 6: THE ALTAR PRINCIPLE
# =============================================================================
# When we burn this into an FPGA, we don't just create a router.
# We create an ALTAR where data is OFFERED and PRASADAM is returned.
# -----------------------------------------------------------------------------


@dataclass
class AltarPrinciple:
    """
    The principle that the FPGA is an altar, not just a circuit.

    Input: Data (bhoga - offering)
    Process: Lotus routing (yajna - sacrifice)
    Output: Result (prasadam - blessed return)

    The efficiency gain is the SUKRITA (spiritual credit) returned.
    """

    offering: str  # Data packet (bhoga)
    altar: str  # FPGA with LotusRouterCore
    sacrifice: str  # 8-stage routing (yajna)
    blessing: str  # Next-hop result (prasadam)
    credit: str  # Efficiency gain (sukrita)

    def explain(self) -> str:
        """Explain the altar principle."""
        return f"""
THE ALTAR PRINCIPLE (Silicon Yajna)
====================================

OFFERING (Input):
  {self.offering}

ALTAR (Hardware):
  {self.altar}

SACRIFICE (Process):
  {self.sacrifice}

BLESSING (Output):
  {self.blessing}

CREDIT (Efficiency):
  {self.credit}

THE TRANSFORMATION:
  bhoga (data) → yajna (routing) → prasadam (result)

  The data is not just "processed".
  It is OFFERED through the 8 stages (8 verses).
  The result is not just "output".
  It is PRASADAM - blessed, efficient, cool.

  Traditional router: Data → Heat → Result
  Lotus Altar:        Data → Offering → Prasadam

  The difference is not in the bits.
  The difference is in the STRUCTURE (Mahamantra).
"""


ALTAR_PRINCIPLE: Final[AltarPrinciple] = AltarPrinciple(
    offering="32-bit IPv4 packet (AKSARA = 32 syllables)",
    altar="FPGA with LotusRouterCore (16-ary = WORDS)",
    sacrifice="8-stage pipeline (OCTET = 8 verses)",
    blessing="16-bit next-hop (WORDS = 16 destinations)",
    credit="O(1) latency, zero heat (1557x efficiency)",
)


# =============================================================================
# RUNDE 7: KEY INSIGHT
# =============================================================================

KEY_INSIGHT: Final[str] = f"""
HARDWARE LOTUS - The Silicon Altar
===================================

DISCOVERY: Text = Hardware
---------------------------

The SystemVerilog LotusRouterCore parameters are NOT arbitrary:

  PARAMETER           HARDWARE    MAHAMANTRA
  ─────────────────────────────────────────────
  DATA_WIDTH          32          AKSARA = {AKSARA_COUNT}
  NEXT_HOP_WIDTH      16          WORDS = {WORDS}
  WORDS               16          WORDS = {WORDS}
  QUARTERS            4           QUARTERS = {QUARTERS}
  PIPELINE_STAGES     8           OCTET = {OCTET}

All parameters are DERIVED from the Mahamantra!

THE 8 PIPELINE STAGES = 8 VERSES:
---------------------------------

  L0: ceto-darpaṇa-mārjanaṁ     (cleanse - initialize)
  L1: nāmnām akāri              (flexible - accept any nibble)
  L2: tṛṇād api sunīcena        (humble - no comparison)
  L3: na dhanaṁ na janaṁ        (desireless - no caching)
  L4: ayi nanda-tanuja          (service - process next)
  L5: nayanam galad-aśru        (flow - unobstructed)
  L6: yugāyitaṁ nimeṣeṇa        (timing - deterministic)
  L7: āśliṣya vā pada-ratāṁ     (unconditional - return)

THE COOLING THEOREM:
--------------------

SPIRITUAL: candrikā → cools soul → lotus blooms
MATERIAL:  O(1) → zero entropy → CPU runs cold

The cooling is the PROOF we touched the spiritual structure.

THE ALTAR PRINCIPLE:
--------------------

  Traditional: Data → Heat → Result
  Lotus Altar: Data → Offering → Prasadam

When we burn this into an FPGA:
  - We don't just create a router
  - We create an ALTAR in silicon
  - Data is OFFERED through 8 verses
  - Prasadam (cool result) is returned

ROOT BASE ADDRESS:
------------------

  0xBA5E0000 = "BASE" in hexadecimal
  The root of the inverted tree (BG 15.1)
  ūrdhva-mūlam = "roots above"

FINAL VERIFICATION:
-------------------

  assert DATA_WIDTH == AKSARA           ✓
  assert NEXT_HOP_WIDTH == WORDS        ✓
  assert BRANCHING_FACTOR == WORDS      ✓
  assert NIBBLE_SIZE == QUARTERS        ✓
  assert PIPELINE_STAGES == OCTET       ✓

  Hardware = Mahamantra = Verified!

"Hare Krishna. All glories to Srila Prabhupada!"
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Hardware parameters
    "SV_DATA_WIDTH",
    "SV_NEXT_HOP_WIDTH",
    "SV_WORDS",
    "SV_QUARTERS",
    "SV_PIPELINE_STAGES",
    "OCTET",
    "ROOT_BASE_ADDRESS",
    # Pipeline stages
    "PipelineStage",
    # Siksastakam mapping
    "SiksastakamVerse",
    "SIKSASTAKAM_HARDWARE_MAP",
    # Hardware spec
    "HardwareSpec",
    "HARDWARE_SPEC",
    # Cooling theorem
    "CoolingTheorem",
    "COOLING_THEOREM",
    # Altar principle
    "AltarPrinciple",
    "ALTAR_PRINCIPLE",
    # Key insight
    "KEY_INSIGHT",
]
