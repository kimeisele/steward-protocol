"""
VYASADEVA - The Knowledge Compiler (DHARMA HEAD)
=================================================

"Vyasadeva is celebrated as a shaktyavesha-avatara because
he was specifically empowered by the Lord to compile all
Vedic knowledge for the Kali Yuga."
- Srimad Bhagavatam 1.4.17

SHAKTI: Jnana-shakti (The Knowledge Potency)
OPCODE: ASSERT_TRUTH (Position 4 - HEAD of Q2 DHARMA)
VYUHA: SANKARSHANA (Dharma Cycle)

STORY (SB 1.4-7):
Vyasadeva saw that people in Kali Yuga would be short-lived and
lacking intelligence. He divided the one Veda into four.
He then wrote the Puranas, Mahabharata, and finally the
Srimad Bhagavatam (the spotless Purana).

ARCHITECTURAL MEANING:

Vyasa = Knowledge Compiler/Validator

He does NOT execute business logic. He:
1. ASSERTS truth (validates knowledge)
2. COMPILES knowledge (organizes information)
3. DIVIDES (separates concerns)
4. SYNTHESIZES (creates comprehensive understanding)

RELATION TO OTHER ROLES:

| Role       | Analogy                    | Function                  |
|------------|----------------------------|---------------------------|
| KRISHNA    | The Source of All Knowledge| Original author           |
| VISHNU     | The Maintainer             | Preserves knowledge       |
| VYASA      | The Compiler               | Organizes and validates   |
| KUMARAS    | The Purity Checkers        | Verify dharmic compliance |
| KAPILA     | The Analyzer               | Deep philosophical analysis|
| MANU       | The Lawgiver               | Practical application     |

PROTOCOL LEVEL:

Vyasa operates at Level 0 (AVATARA/EXECUTIVE).
He is the HEAD of the DHARMA cycle (Q2).
His workers are: KUMARAS, KAPILA, MANU

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Final, List, Optional, Protocol, TypedDict, runtime_checkable

from vibe_core.protocols.avataras import (
    Avatara,
    AvatarType,
    BaseAvatara,
    MilkingResult,
    MilkingRole,
    MilkingSetup,
    Shakti,
)


# =============================================================================
# KNOWLEDGE TYPES (What Vyasa compiles)
# =============================================================================


class TruthAssertion(TypedDict, total=False):
    """
    An assertion of truth to be validated.
    WATERTIGHT - no Any!
    """
    statement: str        # The statement to validate
    source: str           # Where it came from
    context: str          # Contextual information
    lineage_hash: int     # Parampara verification
    timestamp: str        # ISO format


class ValidationResult(TypedDict, total=False):
    """
    Result of truth validation.
    WATERTIGHT - no Any!
    """
    valid: bool
    statement: str
    confidence: float     # 0.0 to 1.0
    reason: str           # Why valid/invalid
    contradictions: str   # Any contradicting statements
    lineage_verified: bool


class KnowledgeCompilation(TypedDict, total=False):
    """
    A compiled body of knowledge.
    WATERTIGHT - no Any!
    """
    title: str
    category: str         # "veda", "purana", "itihasa", "sutra"
    entries: int          # Number of entries
    compiled_at: str      # ISO timestamp
    compiler_id: str      # Usually "vyasa"
    checksum: str         # SHA-256 of content


class DharmaVerdict(TypedDict, total=False):
    """
    A dharmic verdict on an action.
    WATERTIGHT - no Any!
    """
    action: str
    dharmic: bool         # Is it dharmic?
    reasoning: str        # Why
    precedents: str       # Supporting scriptural references
    exceptions: str       # Any contextual exceptions


# =============================================================================
# STANDARD MILKING SETUPS (Knowledge Extraction)
# =============================================================================

# Vyasa extracts knowledge through different channels

MILKING_SHRUTI: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="brahma",
        role_type="kalb",
        description="Stimulates with original Vedic knowledge",
    ),
    melker=MilkingRole(
        identity="vyasa",
        role_type="melker",
        description="Compiles and organizes",
    ),
    topf=MilkingRole(
        identity="shruti_store",
        role_type="topf",
        description="Permanent revealed knowledge",
    ),
    resource="vedic_knowledge",
    source="brahma_sampradaya",
)

MILKING_SMRTI: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="rishis",
        role_type="kalb",
        description="Stimulates with practical observations",
    ),
    melker=MilkingRole(
        identity="vyasa",
        role_type="melker",
        description="Compiles into applicable knowledge",
    ),
    topf=MilkingRole(
        identity="smrti_store",
        role_type="topf",
        description="Remembered/derived knowledge",
    ),
    resource="practical_knowledge",
    source="rishi_experience",
)

MILKING_NYAYA: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="kapila",
        role_type="kalb",
        description="Stimulates with analytical questions",
    ),
    melker=MilkingRole(
        identity="vyasa",
        role_type="melker",
        description="Synthesizes philosophical truth",
    ),
    topf=MilkingRole(
        identity="nyaya_store",
        role_type="topf",
        description="Logical/philosophical conclusions",
    ),
    resource="philosophical_truth",
    source="samkhya_analysis",
)


# =============================================================================
# VYASA PROTOCOL
# =============================================================================


@runtime_checkable
class VyasaProtocol(Protocol):
    """
    The Knowledge Compiler Protocol.

    Any system that manages truth assertion and knowledge compilation
    MUST implement this.

    Vyasa is the PERSON responsible - not abstract "validation".
    """

    def assert_truth(self, assertion: TruthAssertion) -> ValidationResult:
        """
        Assert and validate a truth statement.

        This is ASSERT_TRUTH opcode implementation.
        The HEAD of DHARMA cycle validates knowledge.
        """
        ...

    def compile(self, sources: List[str], category: str) -> KnowledgeCompilation:
        """
        Compile knowledge from multiple sources.

        Like Vyasa compiling the Vedas:
        - Gather from sources
        - Organize by category
        - Verify consistency
        - Create searchable compilation
        """
        ...

    def divide(self, compilation_id: str, criteria: str) -> List[str]:
        """
        Divide a compilation into parts.

        Like Vyasa dividing the one Veda into four:
        - By subject matter
        - By complexity
        - By audience
        - By application

        Returns list of new compilation IDs.
        """
        ...

    def verify_dharma(self, action: str, context: str) -> DharmaVerdict:
        """
        Verify if an action is dharmic.

        Vyasa as the compiler of dharma-shastra
        can determine dharmic validity.
        """
        ...

    def get_compilation(self, compilation_id: str) -> Optional[KnowledgeCompilation]:
        """Get a knowledge compilation by ID."""
        ...

    def search(self, query: str, category: Optional[str] = None) -> List[str]:
        """
        Search compiled knowledge.

        Returns matching entry IDs.
        """
        ...


# =============================================================================
# VYASA IMPLEMENTATION
# =============================================================================


class Vyasa(BaseAvatara):
    """
    Vyasadeva - The Knowledge Compiler.

    SHAKTI: Jnana (Knowledge)
    HEAD: DHARMA cycle (SANKARSHANA)
    WORKERS: Kumaras, Kapila, Manu

    He asserts truth, compiles knowledge, divides for understanding.
    Without Vyasa, no organized knowledge. Without knowledge, no dharma.

    ANTI-MAYAVAD: This is not abstract "validation".
    VYASA (the Person) compiles it. He is the Supreme Compiler.
    """

    AVATARA_NAME = "Vyasa"
    AVATARA_SHAKTI = Shakti.JNANA
    AVATARA_TYPE = AvatarType.SHAKTYAVESHA
    DOMAIN = "Knowledge Compilation/Truth Assertion"
    DESCRIPTION = "The Knowledge Compiler - asserts truth, compiles knowledge"

    def __init__(self) -> None:
        super().__init__()
        self._compilations: Dict[str, KnowledgeCompilation] = {}
        self._assertions: Dict[str, ValidationResult] = {}
        self._verdicts: Dict[str, DharmaVerdict] = {}
        self._compilation_counter = 0

    # =========================================================================
    # TRUTH OPERATIONS
    # =========================================================================

    def assert_truth(self, assertion: TruthAssertion) -> ValidationResult:
        """
        Assert and validate a truth statement.

        ASSERT_TRUTH opcode implementation.
        """
        if not self._empowered:
            return ValidationResult(
                valid=False,
                statement=assertion.get("statement", ""),
                confidence=0.0,
                reason="Vyasa not empowered - no valid parampara",
                contradictions="",
                lineage_verified=False,
            )

        # Verify lineage
        lineage_hash = assertion.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        # For now, simple validation logic
        # In real implementation, would check against knowledge base
        statement = assertion.get("statement", "")

        result = ValidationResult(
            valid=True if statement else False,
            statement=statement,
            confidence=0.9 if lineage_ok else 0.5,
            reason="Validated by Vyasa" if statement else "Empty statement",
            contradictions="",
            lineage_verified=lineage_ok,
        )

        # Store assertion
        assertion_id = f"assertion_{len(self._assertions)}"
        self._assertions[assertion_id] = result

        return result

    def compile(self, sources: List[str], category: str) -> KnowledgeCompilation:
        """Compile knowledge from sources."""
        self._compilation_counter += 1
        comp_id = f"compilation_{self._compilation_counter}"

        compilation = KnowledgeCompilation(
            title=f"Compilation {self._compilation_counter}",
            category=category,
            entries=len(sources),
            compiled_at=datetime.now().isoformat(),
            compiler_id="vyasa",
            checksum=f"sha256:{comp_id}",  # Simplified
        )

        self._compilations[comp_id] = compilation
        return compilation

    def divide(self, compilation_id: str, criteria: str) -> List[str]:
        """Divide a compilation into parts."""
        if compilation_id not in self._compilations:
            return []

        # Simplified: create two sub-compilations
        self._compilation_counter += 1
        sub1_id = f"compilation_{self._compilation_counter}"
        self._compilation_counter += 1
        sub2_id = f"compilation_{self._compilation_counter}"

        original = self._compilations[compilation_id]
        half = original.get("entries", 0) // 2

        self._compilations[sub1_id] = KnowledgeCompilation(
            title=f"{original.get('title', '')} Part 1",
            category=original.get("category", ""),
            entries=half,
            compiled_at=datetime.now().isoformat(),
            compiler_id="vyasa",
            checksum=f"sha256:{sub1_id}",
        )

        self._compilations[sub2_id] = KnowledgeCompilation(
            title=f"{original.get('title', '')} Part 2",
            category=original.get("category", ""),
            entries=original.get("entries", 0) - half,
            compiled_at=datetime.now().isoformat(),
            compiler_id="vyasa",
            checksum=f"sha256:{sub2_id}",
        )

        return [sub1_id, sub2_id]

    def verify_dharma(self, action: str, context: str) -> DharmaVerdict:
        """Verify if an action is dharmic."""
        verdict = DharmaVerdict(
            action=action,
            dharmic=True,  # Simplified - real impl would check rules
            reasoning=f"Action '{action}' verified in context '{context}'",
            precedents="BG 18.66 - surrender to Krishna is supreme dharma",
            exceptions="Context-dependent exceptions may apply",
        )

        verdict_id = f"verdict_{len(self._verdicts)}"
        self._verdicts[verdict_id] = verdict

        return verdict

    def get_compilation(self, compilation_id: str) -> Optional[KnowledgeCompilation]:
        """Get a knowledge compilation by ID."""
        return self._compilations.get(compilation_id)

    def search(self, query: str, category: Optional[str] = None) -> List[str]:
        """Search compiled knowledge."""
        results = []
        for comp_id, comp in self._compilations.items():
            if category and comp.get("category") != category:
                continue
            if query.lower() in comp.get("title", "").lower():
                results.append(comp_id)
        return results

    # =========================================================================
    # MILKING PROTOCOL
    # =========================================================================

    def _do_milk(self, setup: MilkingSetup) -> MilkingResult:
        """Extract knowledge according to setup."""
        return MilkingResult(
            resource=setup.resource,
            amount=1.0,  # Knowledge is qualitative
            quality=0.95,
            source_id=setup.source,
            operator_id=self.AVATARA_NAME,
            timestamp=datetime.now().isoformat(),
            lineage_verified=self._empowered,
        )


# =============================================================================
# NULL VYASA (For Testing)
# =============================================================================


class NullVyasa(Vyasa):
    """The Uncompiled. No knowledge (for testing)."""

    def __init__(self) -> None:
        super().__init__()
        self._empowered = True  # Always empowered for null

    def assert_truth(self, assertion: TruthAssertion) -> ValidationResult:
        return ValidationResult(
            valid=True,
            statement=assertion.get("statement", ""),
            confidence=1.0,
            reason="NullVyasa accepts all",
            contradictions="",
            lineage_verified=True,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "TruthAssertion",
    "ValidationResult",
    "KnowledgeCompilation",
    "DharmaVerdict",
    # Milking setups
    "MILKING_SHRUTI",
    "MILKING_SMRTI",
    "MILKING_NYAYA",
    # Protocol
    "VyasaProtocol",
    # Implementation
    "Vyasa",
    "NullVyasa",
]
