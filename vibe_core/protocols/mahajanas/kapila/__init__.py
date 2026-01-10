"""
KAPILA - The 5th Mahajana (Analysis/Optimization)
=================================================
OpCodes: resolve_req (Bit 9), optimize (Bit 10)
Opulence: Jnana (Knowledge)

The founder of Sankhya philosophy.
Analytical discrimination between Prakriti and Purusha.

Kapila OWNS all analysis protocols:
- Request Resolution
- Optimization
- Profiling
- Metrics Collection
- Pattern Recognition
- Sankhya (Enumeration/Analysis)

Kapila counts, measures, analyzes. He does NOT act blindly.
"""

from typing import Protocol, runtime_checkable, Any, Dict


@runtime_checkable
class KapilaProtocol(Protocol):
    """
    The Analyst Protocol.
    Any system that analyzes/optimizes must implement this.
    """

    def analyze(self, target: Any) -> Dict[str, Any]:
        """
        Analyze the target.
        Returns analysis results as dict.
        """
        ...

    def optimize(self, target: Any) -> Any:
        """
        Optimize the target.
        Returns optimized version.
        """
        ...

    def get_metrics(self) -> Dict[str, float]:
        """Return collected metrics."""
        ...


class NullKapila:
    """
    The Unanalyzed.
    No analysis performed (for testing without metrics).
    """

    def analyze(self, target: Any) -> Dict[str, Any]:
        return {}

    def optimize(self, target: Any) -> Any:
        return target  # No optimization

    def get_metrics(self) -> Dict[str, float]:
        return {}


__all__ = ["KapilaProtocol", "NullKapila"]
