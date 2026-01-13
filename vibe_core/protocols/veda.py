"""
VEDA PROTOCOL - The Holy Pythonic Standard
===========================================

"vedaham samatitani vartamanani carjuna
bhavisyani ca bhutani mam tu veda na kascana"

"O Arjuna, I know everything that has happened in the past,
all that is happening in the present, and all things yet to come."
— Bhagavad Gita 7.26

THE FUSION:
    Veda-4 spirituelle Logik → Python Dunder Methods
    Das Objekt IST sein Verhalten. Kein Imperativ. Nur Sein.

MAPPING:
    ┌─────────────┬──────────────────────────────────────────┐
    │ VEDA-4      │ PYTHON DUNDERS                           │
    ├─────────────┼──────────────────────────────────────────┤
    │ SHABDA      │ __call__, __init__     (Reception)       │
    │ ARTHA       │ __repr__, __getitem__  (Meaning)         │
    │ PRATYAYA    │ __bool__, __eq__       (Validation)      │
    │ KARMA       │ __iter__, __await__    (Action/Flow)     │
    └─────────────┴──────────────────────────────────────────┘

USAGE:
    @runtime_checkable
    class MyAgent(VedaProtocol):
        def __call__(self, instruction): ...  # SHABDA: Receive
        def __repr__(self): ...               # ARTHA: Identity
        def __bool__(self): ...               # PRATYAYA: Valid?
        def __iter__(self): ...               # KARMA: Flow

    # Then usage is PYTHONIC:
    agent("Do something")      # SHABDA
    print(agent)               # ARTHA
    if agent:                  # PRATYAYA
        for result in agent:   # KARMA
            ...

WATERTIGHT: All typed. No Any. Protocol-first.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0xe8dbfd14"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Generic,
    Iterator,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)


# =============================================================================
# TYPE VARIABLES
# =============================================================================

T = TypeVar("T")           # Input type
R = TypeVar("R")           # Result type
K = TypeVar("K")           # Key type for indexing
V = TypeVar("V")           # Value type for indexing


# =============================================================================
# SHABDA PROTOCOL - Reception / Input
# =============================================================================


@runtime_checkable
class ShabdaProtocol(Protocol[T, R]):
    """
    SHABDA: The Sound. Reception of instruction.

    "śabda-brahman" - The Word is Brahman.

    Maps to:
        __call__  → Receive and process instruction
        __init__  → Initial configuration (birth)

    Pythonic:
        agent("Do X")           # Call with instruction
        Agent(config)           # Initialize with config
    """

    def __call__(self, instruction: T) -> R:
        """
        Receive instruction (Shabda) and return result.

        This is the PRIMARY interface. An entity that cannot
        receive instructions is deaf to the world.
        """
        ...


# =============================================================================
# ARTHA PROTOCOL - Meaning / Identity
# =============================================================================


@runtime_checkable
class ArthaProtocol(Protocol[K, V]):
    """
    ARTHA: The Meaning. Identity and substance.

    "artha" = meaning, purpose, wealth, substance.

    Maps to:
        __repr__     → Reveal true form (for debugging/logging)
        __str__      → Human-readable form
        __getitem__  → Access internal meaning by key
        __len__      → Measure of substance

    Pythonic:
        str(agent)              # "Agent(name='Brahma', pos=1)"
        agent["capability"]     # Access internal state
        len(agent)              # How much substance?
    """

    def __repr__(self) -> str:
        """
        Reveal the true form (Svarupa).

        This should return a string that could recreate the object.
        Like looking in a mirror and seeing your eternal form.
        """
        ...

    def __getitem__(self, key: K) -> V:
        """
        Access internal meaning by key.

        The substance is indexed. Each part has a name.
        Like accessing the different limbs of the Virat-Rupa.
        """
        ...


@runtime_checkable
class ArthaFullProtocol(ArthaProtocol[K, V], Protocol[K, V]):
    """Extended Artha with __str__ and __len__."""

    def __str__(self) -> str:
        """Human-readable form (Nama-Rupa)."""
        ...

    def __len__(self) -> int:
        """Measure of substance (how much meaning?)."""
        ...


# =============================================================================
# PRATYAYA PROTOCOL - Validation / Truth
# =============================================================================


@runtime_checkable
class PratyayaProtocol(Protocol):
    """
    PRATYAYA: Belief/Validation. Is it true? Is it connected?

    "pratyaya" = faith, trust, confidence, proof.

    Maps to:
        __bool__     → Is this entity valid/alive?
        __eq__       → Is this entity the same as another?
        __hash__     → Unique identity fingerprint

    Pythonic:
        if agent:               # Is agent valid/connected?
        if a == b:              # Are these the same entity?
        {agent}                 # Can be put in sets (unique)
    """

    def __bool__(self) -> bool:
        """
        Is this entity valid/connected?

        Returns True if:
        - The entity is properly initialized
        - The entity is connected to its source (Parampara)
        - The entity has life force (Prana)

        "asato ma sad gamaya" - Lead me from unreal to real.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """
        Identity comparison.

        Two entities are equal if they have the same essence,
        not just the same appearance. Like recognizing Krishna
        in any of His forms.
        """
        ...


@runtime_checkable
class PratyayaFullProtocol(PratyayaProtocol, Protocol):
    """Extended Pratyaya with __hash__ and __contains__."""

    def __hash__(self) -> int:
        """Unique identity fingerprint (for sets/dicts)."""
        ...

    def __contains__(self, item: object) -> bool:
        """Does this entity contain the given item?"""
        ...


# =============================================================================
# KARMA PROTOCOL - Action / Flow
# =============================================================================


@runtime_checkable
class KarmaProtocol(Protocol[R]):
    """
    KARMA: Action and its fruits. The flow of consequences.

    "karmaṇy evādhikāras te mā phaleṣu kadācana"
    "You have a right to perform action, but not to the fruits."
    — Bhagavad Gita 2.47

    Maps to:
        __iter__     → Synchronous flow of results
        __next__     → Get next result in flow

    Pythonic:
        for result in agent:    # Iterate over results
            process(result)
    """

    def __iter__(self) -> Iterator[R]:
        """
        The flow of karma (results/consequences).

        Each iteration is a "fruit" of the action.
        The iterator may be infinite (like Ananta).
        """
        ...


@runtime_checkable
class KarmaAsyncProtocol(Protocol[R]):
    """
    Async Karma for non-blocking operations.

    Maps to:
        __aiter__    → Async flow of results
        __await__    → Await single result
    """

    def __aiter__(self) -> AsyncIterator[R]:
        """Async flow of karma."""
        ...

    def __await__(self) -> Iterator[R]:
        """Await the completion of karma."""
        ...


# =============================================================================
# THE COMPLETE VEDA PROTOCOL
# =============================================================================


@runtime_checkable
class VedaProtocol(
    ShabdaProtocol[T, R],
    ArthaProtocol[str, object],
    PratyayaProtocol,
    KarmaProtocol[R],
    Protocol[T, R],
):
    """
    The Complete Veda-4 Protocol.

    An entity implementing this protocol is "Vedic" - it follows
    the eternal principles encoded in Python's dunder methods.

    IMPLEMENTATION CHECKLIST:
        □ __call__(instruction: T) -> R      # SHABDA: Receive
        □ __repr__() -> str                  # ARTHA: Identity
        □ __getitem__(key: str) -> object    # ARTHA: Access
        □ __bool__() -> bool                 # PRATYAYA: Valid?
        □ __eq__(other) -> bool              # PRATYAYA: Same?
        □ __iter__() -> Iterator[R]          # KARMA: Flow

    PYTHONIC USAGE:
        result = agent("instruction")   # SHABDA
        print(agent)                    # ARTHA
        value = agent["key"]            # ARTHA
        if agent:                       # PRATYAYA
            for r in agent:             # KARMA
                ...
    """
    pass


@runtime_checkable
class VedaFullProtocol(
    ShabdaProtocol[T, R],
    ArthaFullProtocol[str, object],
    PratyayaFullProtocol,
    KarmaProtocol[R],
    KarmaAsyncProtocol[R],
    Protocol[T, R],
):
    """
    The Complete Veda-4 Protocol with all extensions.

    Includes:
        - __str__, __len__ (extended Artha)
        - __hash__, __contains__ (extended Pratyaya)
        - __aiter__, __await__ (async Karma)
    """
    pass


# =============================================================================
# VEDA-4 MIXIN BASE CLASSES
# =============================================================================


class ShabdaMixin:
    """
    Mixin providing default SHABDA behavior.

    Override __call__ to customize instruction handling.
    """

    def __call__(self, instruction: T) -> R:
        """Default: echo instruction back."""
        return instruction  # type: ignore


class ArthaMixin:
    """
    Mixin providing default ARTHA behavior.

    Override __repr__ and __getitem__ for custom identity.
    """

    def __repr__(self) -> str:
        """Default: class name with id."""
        return f"{self.__class__.__name__}(id={id(self)})"

    def __str__(self) -> str:
        """Default: same as repr."""
        return self.__repr__()

    def __getitem__(self, key: str) -> object:
        """Default: access __dict__."""
        if hasattr(self, "__dict__"):
            return self.__dict__.get(key)
        raise KeyError(key)

    def __len__(self) -> int:
        """Default: count of attributes."""
        if hasattr(self, "__dict__"):
            return len(self.__dict__)
        return 0


class PratyayaMixin:
    """
    Mixin providing default PRATYAYA behavior.

    Override __bool__ for custom validation logic.
    """

    def __bool__(self) -> bool:
        """Default: always valid (optimistic)."""
        return True

    def __eq__(self, other: object) -> bool:
        """Default: compare by id."""
        if not isinstance(other, self.__class__):
            return False
        return id(self) == id(other)

    def __hash__(self) -> int:
        """Default: hash of id."""
        return hash(id(self))


class KarmaMixin:
    """
    Mixin providing default KARMA behavior.

    Override __iter__ for custom result flow.
    """

    def __iter__(self) -> Iterator[R]:
        """Default: empty iterator (no karma yet)."""
        return iter([])


class VedaMixin(ShabdaMixin, ArthaMixin, PratyayaMixin, KarmaMixin):
    """
    Complete Veda-4 Mixin providing all four protocols.

    Inherit from this to get sensible defaults for all dunders.
    Then override what you need.

    Example:
        class MyAgent(VedaMixin):
            def __init__(self, name: str):
                self.name = name

            def __call__(self, instruction: str) -> str:
                return f"{self.name} received: {instruction}"

            def __repr__(self) -> str:
                return f"MyAgent(name={self.name!r})"

            def __bool__(self) -> bool:
                return bool(self.name)  # Valid if has name
    """
    pass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def is_vedic(obj: object) -> bool:
    """
    Check if an object follows the Veda Protocol.

    Returns True if object implements all four phases.
    """
    return isinstance(obj, VedaProtocol)


def is_shabda(obj: object) -> bool:
    """Check if object can receive instructions (__call__)."""
    return isinstance(obj, ShabdaProtocol)


def is_artha(obj: object) -> bool:
    """Check if object has meaning (__repr__, __getitem__)."""
    return isinstance(obj, ArthaProtocol)


def is_pratyaya(obj: object) -> bool:
    """Check if object can be validated (__bool__, __eq__)."""
    return isinstance(obj, PratyayaProtocol)


def is_karma(obj: object) -> bool:
    """Check if object produces results (__iter__)."""
    return isinstance(obj, KarmaProtocol)


def veda_audit(obj: object) -> dict:
    """
    Audit an object's Veda compliance.

    Returns dict with compliance status for each phase.
    """
    return {
        "shabda": is_shabda(obj),
        "artha": is_artha(obj),
        "pratyaya": is_pratyaya(obj),
        "karma": is_karma(obj),
        "full_veda": is_vedic(obj),
        "class": obj.__class__.__name__,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core Protocols
    "ShabdaProtocol",
    "ArthaProtocol",
    "ArthaFullProtocol",
    "PratyayaProtocol",
    "PratyayaFullProtocol",
    "KarmaProtocol",
    "KarmaAsyncProtocol",
    # Complete Protocols
    "VedaProtocol",
    "VedaFullProtocol",
    # Mixins
    "ShabdaMixin",
    "ArthaMixin",
    "PratyayaMixin",
    "KarmaMixin",
    "VedaMixin",
    # Helpers
    "is_vedic",
    "is_shabda",
    "is_artha",
    "is_pratyaya",
    "is_karma",
    "veda_audit",
]
