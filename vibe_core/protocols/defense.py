"""
DEFENSE PROTOCOLS (The 4 Regulating Principles)
===============================================
"Dharma protects those who protect it."

Layer: 0 (Bhu Mandala / Universal Law)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x27d2bf20"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from typing import Optional, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")
ContextT = TypeVar("ContextT")


@runtime_checkable
class IDataSanitizer(Protocol):
    """
    DAYA (Mercy) - No Corrupt Data Ingestion.
    """

    @abstractmethod
    def enforce_purity(self, data: T, context: Optional[ContextT] = None) -> T:
        """
        Validates and sanitizes input data.
        Returns validated data or raises SecurityError.
        """
        ...


@runtime_checkable
class IOutputVerifier(Protocol):
    """
    SATYAM (Truthfulness) - No Hallucination.
    """

    @abstractmethod
    def enforce_truth(self, statement: T, evidence: Optional[ContextT] = None) -> bool:
        """
        Verifies if an output is grounded in truth.
        """
        ...


@runtime_checkable
class IResourceManager(Protocol):
    """
    TAPAS (Austerity) - No Resource Leaks.
    """

    @abstractmethod
    def enforce_sobriety(self, resource_id: str, limits: Optional[object] = None) -> bool:
        """
        Checks if resource usage is within austere limits.
        """
        ...


@runtime_checkable
class INetworkGuard(Protocol):
    """
    SAUCAM (Cleanliness) - No Unauthorized Connections.
    """

    @abstractmethod
    def enforce_chastity(self, destination: str, method: str = "GET") -> bool:
        """
        Checks if a network connection is authorized.
        """
        ...
