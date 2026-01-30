from typing import Protocol, runtime_checkable, Iterator, List, Tuple
from dataclasses import dataclass
from enum import Enum

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
    L1_NIBBLE = 1
    L2_NIBBLE = 2
    L3_NIBBLE = 3
    L4_NIBBLE = 4
    L5_NIBBLE = 5
    L6_NIBBLE = 6
    L7_NIBBLE = 7

@dataclass(frozen=True)
class PipelineStageInfo:
    """Information about a pipeline stage with Siksastakam mapping."""
    stage: int
    name: str
    bit_range: str
    sanskrit: str
    english: str
    hardware_effect: str

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
        # Implementation stub or abstract
        return False
        
    def to_dict(self) -> dict:
        return {
            "data_width": self.data_width,
            "root_base_address": self.root_base_address
        }

@dataclass(frozen=True)
class VerificationResult:
    """Result of hardware verification."""
    is_valid: bool
    checks: List[Tuple[str, int, int, bool]]
    
    @property
    def summary(self) -> str:
        return f"Hardware Verification: {'PASSED' if self.is_valid else 'FAILED'}"
