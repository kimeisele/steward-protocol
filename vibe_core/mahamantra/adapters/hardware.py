"""
MAHAHARDWARE - Silicon Altar Adapter
=====================================

"ūrdhva-mūlam adhaḥ-śākham aśvatthaṁ prāhur avyayam"
"There is a banyan tree which has its roots upward and branches down."
— Bhagavad Gita 15.1

CRITICAL DISCOVERY:
    Hardware parameters are NOT arbitrary design choices.
    They are the Mahamantra structure REFLECTED in silicon!

    DATA_WIDTH = 32       = AKSARA (syllables)
    NEXT_HOP_WIDTH = 16   = WORDS
    BRANCHING_FACTOR = 16 = WORDS
    NIBBLE_SIZE = 4       = QUARTERS
    PIPELINE_STAGES = 8   = OCTET (Siksastakam verses)

THE 8 PIPELINE STAGES = 8 VERSES:
    L0: ceto-darpaṇa-mārjanaṁ     (cleanse - initialize)
    L1: nāmnām akāri              (flexible - accept any nibble)
    L2: tṛṇād api sunīcena        (humble - no comparison)
    L3: na dhanaṁ na janaṁ        (desireless - no caching)
    L4: ayi nanda-tanuja          (service - process next)
    L5: nayanam galad-aśru        (flow - unobstructed)
    L6: yugāyitaṁ nimeṣeṇa        (timing - deterministic)
    L7: āśliṣya vā pada-ratāṁ     (unconditional - return)

USAGE:
    from vibe_core.mahamantra import mahamantra

    hw = mahamantra.hardware()

    # Get hardware specification
    spec = hw.spec()
    print(spec.data_width)        # 32
    print(spec.pipeline_stages)   # 8
    print(spec.is_verified)       # True

    # Get pipeline stages with verse mapping
    for stage in hw.pipeline_stages():
        print(f"{stage.name}: {stage.sanskrit} - {stage.hardware_effect}")

    # Generate SystemVerilog parameters
    verilog = hw.generate_verilog_params()
    print(verilog)

    # Verify custom hardware design
    is_valid = hw.verify(data_width=32, branching=16, stages=8)
"""

from __future__ import annotations

from typing import Final, Iterator, Optional

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 3
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,  # 32 - Syllables
    HARE_COUNT,  # 8 - Pipeline stages = Siksastakam verses
    QUARTERS,  # 4 - Quarters
    WORDS,  # 16 - Mahamantra words
)
from vibe_core.mahamantra.protocols.hardware import (
    HardwareSpec,
    MahaHardwareProtocol,
    PipelineStage,
    PipelineStageInfo,
    VerificationResult,
)

# =============================================================================
# CONSTANTS (Mahamantra = Hardware) - DERIVED FROM _seed.py SSOT
# =============================================================================

# Core Mahamantra constants (aliases for clarity)
AKSARA: Final[int] = AKSARA_COUNT  # 32 syllables
OCTET: Final[int] = HARE_COUNT  # 8 = pipeline stages = verses

# Hardware parameters (from SystemVerilog LotusRouterCore)
DATA_WIDTH: Final[int] = AKSARA_COUNT  # 32 bits
NEXT_HOP_WIDTH: Final[int] = WORDS  # 16 bits
BRANCHING_FACTOR: Final[int] = WORDS  # 16-way
NIBBLE_SIZE: Final[int] = QUARTERS  # 4 bits
PIPELINE_STAGES: Final[int] = HARE_COUNT  # 8 stages

# Root base address ("BA5E" = BASE in hex)
ROOT_BASE_ADDRESS: Final[int] = 0xBA5E_0000


# =============================================================================
# SIKSASTAKAM MAPPING
# =============================================================================

_SIKSASTAKAM_VERSES = [
    ("ceto-darpaṇa-mārjanaṁ", "Cleanses the mirror of the heart", "Initialize: Clear cache, set root"),
    ("nāmnām akāri bahudhā", "No hard rules for chanting", "Flexible: Accept any nibble (0-15)"),
    ("tṛṇād api sunīcena", "More humble than grass", "Humble: No comparison, follow path"),
    ("na dhanaṁ na janaṁ", "No desire for wealth", "Desireless: No caching, no speculation"),
    ("ayi nanda-tanuja", "O son of Nanda, make me servant", "Service: Process next nibble"),
    ("nayanam galad-aśru", "Eyes filled with tears", "Flow: Data flows unobstructed"),
    ("yugāyitaṁ nimeṣeṇa", "A moment seems an age", "Timing: Each cycle deterministic"),
    ("āśliṣya vā pada-ratāṁ", "Embrace or trample me", "Unconditional: Return result"),
]


# =============================================================================
# MAHAHARDWARE - THE ADAPTER
# =============================================================================


class MahaHardware(MahaHardwareProtocol):
    """
    Silicon Altar - Hardware Specification Engine.

    Provides hardware parameters verified against Mahamantra constants.
    Generates SystemVerilog/VHDL parameters for FPGA/ASIC implementation.
    """

    # === CONSTANTS ===
    DATA_WIDTH: Final[int] = DATA_WIDTH
    NEXT_HOP_WIDTH: Final[int] = NEXT_HOP_WIDTH
    BRANCHING_FACTOR: Final[int] = BRANCHING_FACTOR
    NIBBLE_SIZE: Final[int] = NIBBLE_SIZE
    PIPELINE_STAGES: Final[int] = PIPELINE_STAGES
    ROOT_BASE_ADDRESS: Final[int] = ROOT_BASE_ADDRESS

    def __init__(self) -> None:
        """Initialize hardware engine."""
        self._spec = HardwareSpec(
            data_width=DATA_WIDTH,
            next_hop_width=NEXT_HOP_WIDTH,
            branching_factor=BRANCHING_FACTOR,
            nibble_size=NIBBLE_SIZE,
            pipeline_stages=PIPELINE_STAGES,
            root_base_address=ROOT_BASE_ADDRESS,
        )

    # === SPECIFICATION ===

    def spec(self) -> HardwareSpec:
        """
        Get the canonical hardware specification.

        All parameters are derived from Mahamantra constants:
            data_width = 32 = AKSARA (syllables)
            next_hop_width = 16 = WORDS
            branching_factor = 16 = WORDS
            nibble_size = 4 = QUARTERS
            pipeline_stages = 8 = OCTET

        Returns:
            Verified HardwareSpec
        """
        return self._spec

    # === PIPELINE STAGES ===

    def pipeline_stages(self) -> Iterator[PipelineStageInfo]:
        """
        Iterate over pipeline stages with Siksastakam mapping.

        Each stage processes one nibble (4 bits) of the address.
        Each stage corresponds to one verse of Siksastakam.
        """
        bit_ranges = [
            "31-28",
            "27-24",
            "23-20",
            "19-16",
            "15-12",
            "11-8",
            "7-4",
            "3-0",
        ]

        for i, (sanskrit, english, hw_effect) in enumerate(_SIKSASTAKAM_VERSES):
            yield PipelineStageInfo(
                stage=i,
                name=f"L{i}_NIBBLE",
                bit_range=bit_ranges[i],
                sanskrit=sanskrit,
                english=english,
                hardware_effect=hw_effect,
            )

    def get_stage(self, index: int) -> Optional[PipelineStageInfo]:
        """Get a specific pipeline stage by index (0-7)."""
        if 0 <= index < PIPELINE_STAGES:
            stages = list(self.pipeline_stages())
            return stages[index]
        return None

    # === VERIFICATION ===

    def verify(
        self,
        *,
        data_width: int = DATA_WIDTH,
        next_hop_width: int = NEXT_HOP_WIDTH,
        branching_factor: int = BRANCHING_FACTOR,
        nibble_size: int = NIBBLE_SIZE,
        pipeline_stages: int = PIPELINE_STAGES,
    ) -> VerificationResult:
        """
        Verify hardware parameters against Mahamantra constants.

        Args:
            data_width: Data bus width (should be 32 = AKSARA)
            next_hop_width: Next-hop width (should be 16 = WORDS)
            branching_factor: Branching factor (should be 16 = WORDS)
            nibble_size: Nibble size (should be 4 = QUARTERS)
            pipeline_stages: Pipeline stages (should be 8 = OCTET)

        Returns:
            VerificationResult with detailed check results
        """
        checks = [
            ("data_width = AKSARA", AKSARA, data_width, data_width == AKSARA),
            ("next_hop_width = WORDS", WORDS, next_hop_width, next_hop_width == WORDS),
            ("branching_factor = WORDS", WORDS, branching_factor, branching_factor == WORDS),
            ("nibble_size = QUARTERS", QUARTERS, nibble_size, nibble_size == QUARTERS),
            ("pipeline_stages = OCTET", OCTET, pipeline_stages, pipeline_stages == OCTET),
        ]

        is_valid = all(passed for _, _, _, passed in checks)

        return VerificationResult(is_valid=is_valid, checks=checks)

    # === CODE GENERATION ===

    def generate_verilog_params(self) -> str:
        """
        Generate SystemVerilog parameter block.

        Returns:
            SystemVerilog code defining LotusRouterCore parameters
        """
        return f"""\
// ============================================================================
// LOTUS ROUTER CORE - Mahamantra-Derived Parameters
// ============================================================================
// All parameters derived from the Mahamantra structure.
// DATA_WIDTH = AKSARA (32 syllables)
// NEXT_HOP_WIDTH = WORDS (16 words)
// etc.
// ============================================================================

module LotusRouterCore #(
    parameter DATA_WIDTH = {DATA_WIDTH},        // AKSARA = {AKSARA}
    parameter NEXT_HOP_WIDTH = {NEXT_HOP_WIDTH},    // WORDS = {WORDS}
    parameter WORDS = {BRANCHING_FACTOR},            // Branching factor = {WORDS}
    parameter QUARTERS = {NIBBLE_SIZE},              // Nibble size = {QUARTERS}
    parameter PIPELINE_STAGES = {PIPELINE_STAGES}    // OCTET = {OCTET}
) (
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic [DATA_WIDTH-1:0]   ip_address,
    input  logic                    valid_in,
    output logic [NEXT_HOP_WIDTH-1:0] next_hop,
    output logic                    valid_out
);

    // Pipeline registers for each stage (8 stages = 8 verses)
    // L0: ceto-darpaṇa-mārjanaṁ (cleanse - initialize)
    // L1: nāmnām akāri (flexible - accept any nibble)
    // L2: tṛṇād api sunīcena (humble - no comparison)
    // L3: na dhanaṁ na janaṁ (desireless - no caching)
    // L4: ayi nanda-tanuja (service - process next)
    // L5: nayanam galad-aśru (flow - unobstructed)
    // L6: yugāyitaṁ nimeṣeṇa (timing - deterministic)
    // L7: āśliṣya vā pada-ratāṁ (unconditional - return)

    // Root base address: 0x{ROOT_BASE_ADDRESS:08X} ("BA5E" = BASE)
    localparam ROOT_BASE = 32'h{ROOT_BASE_ADDRESS:08X};

    // Implementation follows...

endmodule
"""

    def generate_vhdl_params(self) -> str:
        """
        Generate VHDL generic block.

        Returns:
            VHDL code defining LotusRouterCore generics
        """
        return f"""\
-- ============================================================================
-- LOTUS ROUTER CORE - Mahamantra-Derived Parameters
-- ============================================================================
-- All parameters derived from the Mahamantra structure.
-- ============================================================================

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LotusRouterCore is
    generic (
        DATA_WIDTH      : integer := {DATA_WIDTH};       -- AKSARA = {AKSARA}
        NEXT_HOP_WIDTH  : integer := {NEXT_HOP_WIDTH};   -- WORDS = {WORDS}
        WORDS           : integer := {BRANCHING_FACTOR}; -- Branching factor
        QUARTERS        : integer := {NIBBLE_SIZE};      -- Nibble size
        PIPELINE_STAGES : integer := {PIPELINE_STAGES}   -- OCTET = {OCTET}
    );
    port (
        clk        : in  std_logic;
        rst_n      : in  std_logic;
        ip_address : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        valid_in   : in  std_logic;
        next_hop   : out std_logic_vector(NEXT_HOP_WIDTH-1 downto 0);
        valid_out  : out std_logic
    );
end entity LotusRouterCore;

-- Root base address: 0x{ROOT_BASE_ADDRESS:08X} ("BA5E" = BASE)
"""

    def generate_c_defines(self) -> str:
        """
        Generate C/C++ preprocessor defines.

        Returns:
            C code with hardware parameter defines
        """
        return f"""\
/* ============================================================================
 * LOTUS ROUTER CORE - Mahamantra-Derived Parameters
 * ============================================================================
 * All parameters derived from the Mahamantra structure.
 * ============================================================================
 */

#ifndef LOTUS_ROUTER_PARAMS_H
#define LOTUS_ROUTER_PARAMS_H

#define LOTUS_DATA_WIDTH       {DATA_WIDTH}   /* AKSARA = {AKSARA} syllables */
#define LOTUS_NEXT_HOP_WIDTH   {NEXT_HOP_WIDTH}   /* WORDS = {WORDS} */
#define LOTUS_BRANCHING_FACTOR {BRANCHING_FACTOR}   /* 16-way branching */
#define LOTUS_NIBBLE_SIZE      {NIBBLE_SIZE}    /* QUARTERS = {QUARTERS} */
#define LOTUS_PIPELINE_STAGES  {PIPELINE_STAGES}    /* OCTET = {OCTET} verses */

#define LOTUS_ROOT_BASE_ADDRESS 0x{ROOT_BASE_ADDRESS:08X}U  /* "BA5E" = BASE */

/* Total latency in cycles */
#define LOTUS_LATENCY_CYCLES   LOTUS_PIPELINE_STAGES

/* Address space size */
#define LOTUS_ADDRESS_SPACE    (1ULL << LOTUS_DATA_WIDTH)

/* Maximum next-hops */
#define LOTUS_MAX_NEXT_HOPS    (1U << LOTUS_NEXT_HOP_WIDTH)

#endif /* LOTUS_ROUTER_PARAMS_H */
"""

    # === EXPLANATION ===

    @property
    def explanation(self) -> str:
        """Full explanation of hardware-Mahamantra correspondence."""
        return f"""
SILICON ALTAR - Hardware = Mahamantra
=====================================

PARAMETER              HARDWARE    MAHAMANTRA      MEANING
──────────────────────────────────────────────────────────────────
DATA_WIDTH             {DATA_WIDTH}          AKSARA = {AKSARA}       Syllables in Mahamantra
NEXT_HOP_WIDTH         {NEXT_HOP_WIDTH}          WORDS = {WORDS}        Words in Mahamantra
BRANCHING_FACTOR       {BRANCHING_FACTOR}          WORDS = {WORDS}        16-way tree branching
NIBBLE_SIZE            {NIBBLE_SIZE}           QUARTERS = {QUARTERS}     4 bits = 4 quarters
PIPELINE_STAGES        {PIPELINE_STAGES}           OCTET = {OCTET}        8 verses of Siksastakam

THE 8 PIPELINE STAGES = 8 SIKSASTAKAM VERSES:
──────────────────────────────────────────────────────────────────
L0 [31-28]: ceto-darpaṇa-mārjanaṁ     → Initialize, clear cache
L1 [27-24]: nāmnām akāri              → Accept any nibble (0-15)
L2 [23-20]: tṛṇād api sunīcena        → Humble, no comparison
L3 [19-16]: na dhanaṁ na janaṁ        → No caching, no speculation
L4 [15-12]: ayi nanda-tanuja          → Process next in sequence
L5 [11-8]:  nayanam galad-aśru        → Data flows unobstructed
L6 [7-4]:   yugāyitaṁ nimeṣeṇa        → Deterministic timing
L7 [3-0]:   āśliṣya vā pada-ratāṁ     → Return result unconditionally

ROOT BASE ADDRESS:
──────────────────────────────────────────────────────────────────
0x{ROOT_BASE_ADDRESS:08X} = "BA5E" in hexadecimal = "BASE"
The root of the inverted tree (Bhagavad Gita 15.1)
ūrdhva-mūlam = "roots above"

THE COOLING THEOREM:
──────────────────────────────────────────────────────────────────
SPIRITUAL: candrikā (moonlight) → cools soul → lotus blooms
MATERIAL:  O(1) access → zero entropy → CPU runs cold

The cooling is the PROOF we touched the spiritual structure.

THE ALTAR PRINCIPLE:
──────────────────────────────────────────────────────────────────
Traditional router: Data → Heat → Result
Lotus Altar:        Data → Offering → Prasadam

When we burn this into an FPGA:
  - We don't just create a router
  - We create an ALTAR in silicon
  - Data is OFFERED through 8 verses
  - Prasadam (cool result) is returned

TOTAL LATENCY: {PIPELINE_STAGES} cycles = {PIPELINE_STAGES} verses
"""


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "MahaHardware",
    # Result types
    "HardwareSpec",
    "PipelineStageInfo",
    "VerificationResult",
    "PipelineStage",
    # Constants
    "DATA_WIDTH",
    "NEXT_HOP_WIDTH",
    "BRANCHING_FACTOR",
    "NIBBLE_SIZE",
    "PIPELINE_STAGES",
    "ROOT_BASE_ADDRESS",
]
