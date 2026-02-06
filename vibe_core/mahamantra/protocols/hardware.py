from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT, HALVES, HARE_COUNT, KSETRAJNA, PANCHA,
    QUARTERS, SEVEN, SHARANAGATI, TRINITY, WORDS,
)

@runtime_checkable
class MahaHardwareProtocol(Protocol):
    """
    Protocol for MahaHardware: Silicon Altar Specification.
    
    Ensures hardware parameters match Mahamantra constants.
    """
    
    def spec(self) -> "HardwareSpec":
        """Get canonical hardware specification."""
        ...
        
    def verify(
        self,
        *,
        data_width: int,
        next_hop_width: int,
        branching_factor: int,
        nibble_size: int,
        pipeline_stages: int,
    ) -> "VerificationResult":
        """Verify parameters against Mahamantra."""
        ...
        
    def generate_verilog_params(self) -> str:
        """Generate SystemVerilog code."""
        ...
        
    def generate_vhdl_params(self) -> str:
        """Generate VHDL code."""
        ...
        
    def generate_c_defines(self) -> str:
        """Generate C header defines."""
        ...
        
    def pipeline_stages(self) -> Iterator["PipelineStageInfo"]:
        """Iterate over pipeline stages."""
        ...

class PipelineStage(Enum):
    """The 8 pipeline stages of LotusRouterCore."""
    L0_NIBBLE = 0
    L1_NIBBLE = KSETRAJNA
    L2_NIBBLE = HALVES
    L3_NIBBLE = TRINITY
    L4_NIBBLE = QUARTERS
    L5_NIBBLE = PANCHA
    L6_NIBBLE = SHARANAGATI
    L7_NIBBLE = SEVEN

@dataclass(frozen=True)
class PipelineStageInfo:
    """Information about a pipeline stage with Siksastakam mapping."""
    stage: int
    name: str
    bit_range: str
    sanskrit: str
    english: str
    hardware_effect: str
    
    @property
    def high_bit(self) -> int:
        """Get high bit from range string (e.g. '31-28' -> 31)."""
        separator = "-" if "-" in self.bit_range else ":"
        if separator in self.bit_range:
            return int(self.bit_range.split(separator)[0])
        return 0
        
    @property
    def low_bit(self) -> int:
        """Get low bit from range string (e.g. '31-28' -> 28)."""
        separator = "-" if "-" in self.bit_range else ":"
        if separator in self.bit_range:
            return int(self.bit_range.split(separator)[KSETRAJNA])
        return 0

@dataclass(frozen=True)
class HardwareSpec:
    """Complete hardware specification."""
    data_width: int
    next_hop_width: int
    branching_factor: int
    nibble_size: int
    pipeline_stages: int
    root_base_address: int
    
    @property
    def is_verified(self) -> bool:
        """Check if spec matches Mahamantra constants."""
        return (
            self.data_width == AKSARA_COUNT and 
            self.next_hop_width == WORDS and 
            self.branching_factor == WORDS and 
            self.nibble_size == QUARTERS and 
            self.pipeline_stages == HARE_COUNT and 
            (self.root_base_address & 0xFFFF0000) == 0xBA5E0000
        )

    @property
    def total_latency_cycles(self) -> int:
        return self.pipeline_stages

    @property
    def address_space(self) -> int:
        return HALVES ** self.data_width

    @property
    def max_next_hops(self) -> int:
        return HALVES ** self.next_hop_width
        
    def to_dict(self) -> dict:
        return {
            "data_width": self.data_width,
            "pipeline_stages": self.pipeline_stages,
            "is_verified": self.is_verified,
            "root_base_address": f"0x{self.root_base_address:08x}"
        }

@dataclass(frozen=True)
class VerificationResult:
    """Result of hardware verification."""
    is_valid: bool
    checks: List[Tuple[str, int, int, bool]]
    
    @property
    def summary(self) -> str:
        return f"Hardware Verification: {'PASSED' if self.is_valid else 'FAILED'}"
        
    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(KSETRAJNA for _, _, _, passed in self.checks if passed)
        
    @property
    def total_count(self) -> int:
        """Total number of checks."""
        return len(self.checks)
