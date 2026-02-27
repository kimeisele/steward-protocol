"""
CAPABILITY PROTOCOLS — The 5 Pancha Tattva as Runtime Contracts
===============================================================

"pañca-tattvātmakaṁ kṛṣṇaṁ bhakta-rūpa-svarūpakam"

Each TattvaGate in lotus_core.__call__() maps to ONE capability protocol.
Components that register a gate hook MUST satisfy the corresponding protocol.

GATE 0 — CHAITANYA (PARSE)    → MantraCapability    (receive + compress)
GATE 1 — NITYANANDA (VALIDATE) → StorageCapability   (load + verify)
GATE 2 — ADVAITA (EXECUTE)     → InferCapability     (reason + match)
GATE 3 — GADADHARA (RESULT)    → SyncCapability      (route + flow)
GATE 4 — SRIVASA (SYNC)        → EnforceCapability   (govern + commit)

These are runtime_checkable Protocols — isinstance() works at runtime.
TattvaRegistry.register() will verify capability compliance.
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x3f7a1b2e"

from typing import Any, Dict, Protocol, runtime_checkable

# =============================================================================
# GATE 0: CHAITANYA — MantraCapability (PARSE / Identity)
# =============================================================================
# "Who/What is this?"
# Receives raw input, identifies it, compresses it to a seed.
# In __call__: SRAVANAM + NAMA + KIRTANAM


@runtime_checkable
class MantraCapability(Protocol):
    """Components that can receive and identify input."""

    def parse(self, input_data: Any) -> Dict[str, Any]:
        """
        Parse raw input into structured form.

        Returns dict with at minimum:
            input_text: str
            seed: int (or None if not yet compressed)
            input_coords: tuple (RAMA coordinates)
        """
        ...


# =============================================================================
# GATE 1: NITYANANDA — StorageCapability (VALIDATE / Substrate)
# =============================================================================
# "What does this rest upon?"
# Loads state, derives attractor from seed, verifies parampara.
# In __call__: PADA_SEVANAM + ARCANAM


@runtime_checkable
class StorageCapability(Protocol):
    """Components that provide substrate/foundation for computation."""

    def validate(self, seed: int) -> Dict[str, Any]:
        """
        Validate seed against substrate.

        Returns dict with at minimum:
            attractor: int
            parampara_verified: bool
        """
        ...


# =============================================================================
# GATE 2: ADVAITA — InferCapability (EXECUTE / Bridge)
# =============================================================================
# "How does this connect?"
# Performs resonance matching, finds verse connections.
# In __call__: SMARANAM + VANDANAM


@runtime_checkable
class InferCapability(Protocol):
    """Components that can reason and find connections."""

    def infer(self, seed: int, attractor: int) -> Dict[str, Any]:
        """
        Perform inference/resonance from seed+attractor.

        Returns dict with at minimum:
            resonant_words: list
            verse_info: dict or None
        """
        ...


# =============================================================================
# GATE 3: GADADHARA — SyncCapability (RESULT / Energy)
# =============================================================================
# "How does energy flow?"
# Determines position, routing, phoneme signature.
# In __call__: DASYAM + SHABDA


@runtime_checkable
class SyncCapability(Protocol):
    """Components that route results and manage energy flow."""

    def route(self, attractor: int) -> Dict[str, Any]:
        """
        Route attractor to position and determine flow.

        Returns dict with at minimum:
            position: int (0-15)
            guardian: str
            quarter: str
        """
        ...


# =============================================================================
# GATE 4: SRIVASA — EnforceCapability (SYNC / Governance)
# =============================================================================
# "Who governs this?"
# Creates cells, runs chamber, commits results.
# In __call__: SAKHYAM + KIRTAN + YAJNA + ATMA_NIVEDANAM


@runtime_checkable
class EnforceCapability(Protocol):
    """Components that enforce governance and commit results."""

    def enforce(self, position: int, seed: int, attractor: int) -> Dict[str, Any]:
        """
        Enforce governance rules and produce final result.

        Returns dict with at minimum:
            cell: object (MahaCellUnified)
            committed: bool
        """
        ...


# =============================================================================
# GATE CAPABILITY MAP — Links TattvaGate to its Protocol
# =============================================================================
# Lazy import to avoid circular dependency with pancha_tattva.py
# (pancha_tattva defines TattvaGate AND imports Capability protocols)

_GATE_CAPABILITY_CACHE = None


def _get_gate_capability():
    """Lazy-build the gate→capability map (avoids circular import)."""
    global _GATE_CAPABILITY_CACHE
    if _GATE_CAPABILITY_CACHE is None:
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate

        _GATE_CAPABILITY_CACHE = {
            TattvaGate.PARSE: MantraCapability,
            TattvaGate.VALIDATE: StorageCapability,
            TattvaGate.EXECUTE: InferCapability,
            TattvaGate.RESULT: SyncCapability,
            TattvaGate.SYNC: EnforceCapability,
        }
    return _GATE_CAPABILITY_CACHE


def get_capability_for_gate(gate) -> type:
    """Get the capability Protocol class for a TattvaGate."""
    return _get_gate_capability()[gate]


def check_capability(obj: object, gate) -> bool:
    """Check if an object satisfies the capability for a gate."""
    cap = _get_gate_capability()[gate]
    return isinstance(obj, cap)


# Module-level lazy attribute for GATE_CAPABILITY
def __getattr__(name):
    if name == "GATE_CAPABILITY":
        return _get_gate_capability()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [  # noqa: F822 — GATE_CAPABILITY is lazy via __getattr__
    "MantraCapability",
    "StorageCapability",
    "InferCapability",
    "SyncCapability",
    "EnforceCapability",
    "GATE_CAPABILITY",
    "get_capability_for_gate",
    "check_capability",
]
