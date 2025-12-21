"""
OPUS-201: Quantum Resonance Engine - Breaking the Binary

"न सत् तन्नासदुच्यते" - "It is not said to be existent or non-existent"
(Bhagavad Gita 13.12 - describing the field beyond duality)

This is NOT boolean logic. This is RESONANCE.

Instead of: if (condition) → true/false
We compute: resonance(A, B) → continuous energy field

The hash is not verification - it's MASS.
Mass influences gravitational pull in the resonance field.
Actions don't get "allowed" - they MANIFEST when energy overcomes inertia.
"""

import hashlib
import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .matrix import Guna, Varga, VarnaTensor, encode


@dataclass
class ResonanceField:
    """
    The result of a resonance computation.

    This is NOT boolean. It's a continuous energy field.
    """

    # Core resonance values
    phonetic_resonance: float  # How well phonetic structures align
    mass_resonance: float  # How crypto masses interact
    total_energy: float  # Combined field energy

    # Component breakdown
    varga_alignment: float  # Articulation point alignment
    sthana_alignment: float  # Position alignment
    guna_harmony: float  # Mode compatibility

    # The tensors that produced this field
    source_tensor: VarnaTensor
    target_tensor: VarnaTensor

    # Entropy chain (for causality tracking)
    field_hash: str

    def __repr__(self) -> str:
        return (
            f"ResonanceField(E={self.total_energy:.4f}, φ={self.phonetic_resonance:.3f}, m={self.mass_resonance:.3f})"
        )


class QuantumReactor:
    """
    The Sanskrit Quantum Reactor - Resonance-Based Computation.

    Core Principles:
    1. No boolean logic - only continuous resonance fields
    2. Crypto hash is MASS - influences gravitational pull
    3. Energy accumulates through the entropy chain
    4. Actions manifest when energy overcomes field inertia

    This is a computational paradigm, not a security layer.
    """

    def __init__(self, initial_inertia: float = 0.5):
        """
        Initialize the reactor.

        Args:
            initial_inertia: Base resistance of the field (0.0-1.0)
        """
        # The Akasha field - current state tensor
        self._akasha: Optional[VarnaTensor] = None

        # Field inertia - resistance to change
        self._inertia = initial_inertia

        # Entropy chain - accumulated cryptographic mass
        self._entropy_chain = b""

        # Resonance history
        self._history: List[ResonanceField] = []

        # Learning rate for field adaptation
        self._plasticity = 0.1

    @property
    def akasha(self) -> VarnaTensor:
        """Current field state."""
        if self._akasha is None:
            # Initialize to balanced state
            self._akasha = encode("om", self._chain_hash())
        return self._akasha

    def _chain_hash(self) -> str:
        """Get current entropy chain hash."""
        return hashlib.sha256(self._entropy_chain).hexdigest()[:16]

    def _extend_chain(self, data: bytes) -> None:
        """Extend the entropy chain."""
        self._entropy_chain = hashlib.sha256(self._entropy_chain + data).digest()

    def _cosine_similarity(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """
        Compute cosine similarity between vectors.

        This is the basic resonance measure.
        """
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)

    def _compute_varga_alignment(self, t1: VarnaTensor, t2: VarnaTensor) -> float:
        """
        Compute alignment between articulation point distributions.

        Higher alignment = sounds originate from similar mouth positions.
        """
        return self._cosine_similarity(t1.varga_vector, t2.varga_vector)

    def _compute_sthana_alignment(self, t1: VarnaTensor, t2: VarnaTensor) -> float:
        """
        Compute alignment between position distributions.

        Higher alignment = similar energy patterns.
        """
        return self._cosine_similarity(t1.sthana_vector, t2.sthana_vector)

    def _compute_guna_harmony(self, t1: VarnaTensor, t2: VarnaTensor) -> float:
        """
        Compute harmony between modes.

        - Same mode = full harmony (1.0)
        - Adjacent modes = partial harmony (0.5)
        - Opposite modes = dissonance (0.0)
        """
        diff = abs(t1.guna - t2.guna)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.5
        else:
            return 0.0

    def _compute_mass_interaction(self, t1: VarnaTensor, t2: VarnaTensor) -> float:
        """
        Compute how cryptographic masses interact.

        Like gravitational interaction: higher combined mass = stronger pull.
        Similar masses resonate more strongly.
        """
        # Combined mass (product)
        combined = t1.entropy * t2.entropy

        # Mass similarity (1.0 when equal)
        diff = abs(t1.entropy - t2.entropy)
        similarity = 1.0 - diff

        # Gravitational-like interaction
        return (combined * 0.4) + (similarity * 0.6)

    def resonate(self, intent: VarnaTensor, target: Optional[VarnaTensor] = None) -> ResonanceField:
        """
        Compute resonance between intent and target (or current field).

        This is the CORE COMPUTATION - not boolean, but continuous.

        Args:
            intent: The input tensor
            target: Target to resonate with (defaults to akasha field)

        Returns:
            ResonanceField with computed energy values
        """
        if target is None:
            target = self.akasha

        # 1. Phonetic resonance components
        varga_align = self._compute_varga_alignment(intent, target)
        sthana_align = self._compute_sthana_alignment(intent, target)
        guna_harmony = self._compute_guna_harmony(intent, target)

        # Combined phonetic resonance (weighted)
        phonetic = varga_align * 0.4 + sthana_align * 0.3 + guna_harmony * 0.3

        # 2. Mass resonance (crypto dimension)
        mass = self._compute_mass_interaction(intent, target)

        # 3. Energy combination
        # Phonetic is the carrier wave, mass modulates amplitude
        shakti_factor = (intent.shakti + target.shakti) / 2
        total_energy = phonetic * shakti_factor * (0.7 + mass * 0.3)

        # 4. Create field hash (for chain continuity)
        field_data = f"{intent.source}:{target.source}:{total_energy}".encode()
        self._extend_chain(field_data)

        result = ResonanceField(
            phonetic_resonance=phonetic,
            mass_resonance=mass,
            total_energy=total_energy,
            varga_alignment=varga_align,
            sthana_alignment=sthana_align,
            guna_harmony=guna_harmony,
            source_tensor=intent,
            target_tensor=target,
            field_hash=self._chain_hash(),
        )

        self._history.append(result)
        return result

    def manifest(
        self, intent_text: str, salt: str = "", callback: Optional[Callable[[ResonanceField], None]] = None
    ) -> ResonanceField:
        """
        Attempt to manifest an intent.

        This is the high-level API. Intent manifests when energy
        overcomes field inertia.

        Args:
            intent_text: The intent string
            salt: Cryptographic salt (session context)
            callback: Optional callback when manifestation occurs

        Returns:
            ResonanceField describing the computation
        """
        # Encode intent
        intent = encode(intent_text, salt or self._chain_hash())

        # Compute resonance
        field = self.resonate(intent)

        # Check manifestation condition
        # Energy must overcome inertia
        if field.total_energy > self._inertia:
            # MANIFESTATION - update the akasha field
            self._update_akasha(intent, field)

            if callback:
                callback(field)

        return field

    def _update_akasha(self, intent: VarnaTensor, field: ResonanceField) -> None:
        """
        Update the akasha field after manifestation.

        The field learns from successful manifestations (plasticity).
        """
        if self._akasha is None:
            self._akasha = intent
            return

        # Blend current field with manifested intent
        lr = self._plasticity * field.total_energy  # Stronger = more learning

        new_varga = tuple((1 - lr) * a + lr * b for a, b in zip(self._akasha.varga_vector, intent.varga_vector))
        new_sthana = tuple((1 - lr) * a + lr * b for a, b in zip(self._akasha.sthana_vector, intent.sthana_vector))
        new_shakti = (1 - lr) * self._akasha.shakti + lr * intent.shakti

        # Create new akasha state
        self._akasha = VarnaTensor(
            varga_vector=new_varga,
            sthana_vector=new_sthana,
            shakti=new_shakti,
            guna=intent.guna,  # Adopt manifest intent's guna
            entropy=field.mass_resonance,  # Use field mass
            source="akasha",
            phoneme_count=0,
        )

    def get_state(self) -> dict:
        """Get current reactor state for debugging."""
        return {
            "inertia": self._inertia,
            "chain_hash": self._chain_hash(),
            "history_length": len(self._history),
            "akasha": repr(self.akasha) if self._akasha else None,
            "last_energy": self._history[-1].total_energy if self._history else None,
        }

    def set_inertia(self, inertia: float) -> None:
        """Set field inertia (resistance to manifestation)."""
        self._inertia = max(0.0, min(1.0, inertia))

    def reset(self) -> None:
        """Reset reactor to initial state."""
        self._akasha = None
        self._entropy_chain = b""
        self._history = []


# =============================================================================
# Convenience functions
# =============================================================================

_global_reactor: Optional[QuantumReactor] = None


def get_reactor() -> QuantumReactor:
    """Get or create global reactor instance."""
    global _global_reactor
    if _global_reactor is None:
        _global_reactor = QuantumReactor()
    return _global_reactor


def compute_resonance(text1: str, text2: str, salt: str = "") -> float:
    """
    Convenience function to compute resonance between two texts.

    Returns: Total energy (0.0 - 1.0)
    """
    t1 = encode(text1, salt)
    t2 = encode(text2, salt)
    reactor = QuantumReactor()
    field = reactor.resonate(t1, t2)
    return field.total_energy


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    print("OPUS-201: Quantum Resonance Engine\n")
    print("=" * 60)

    reactor = QuantumReactor(initial_inertia=0.3)

    test_pairs = [
        # Similar phonetics should resonate
        ("kernel", "kernel"),  # Identical
        ("kernel", "kernal"),  # Similar (typo)
        ("kernel", "connect"),  # Different Varga (k vs c)
        ("kernel", "print"),  # Very different (k vs p)
        # Same text, different salt = different mass
        ("boot", "session1"),
        ("boot", "session2"),
    ]

    print("\nResonance Computations:")
    print("-" * 60)

    for i, (t1, t2) in enumerate(test_pairs):
        if i < 4:
            # Pair comparison
            tensor1 = encode(t1, "")
            tensor2 = encode(t2, "")
            field = reactor.resonate(tensor1, tensor2)
            print(f"\n'{t1}' ~ '{t2}'")
        else:
            # Salt comparison
            tensor = encode("boot", t2)  # t2 is salt here
            field = reactor.resonate(tensor)
            print(f"\n'boot' with salt='{t2}'")

        print(f"  {field}")
        print(f"  Varga align:  {field.varga_alignment:.3f}")
        print(f"  Sthana align: {field.sthana_alignment:.3f}")
        print(f"  Guna harmony: {field.guna_harmony:.3f}")
        print(f"  Mass:         {field.mass_resonance:.3f}")

    print("\n" + "=" * 60)
    print("\nManifestation Test:")
    print("-" * 60)

    reactor.reset()
    reactor.set_inertia(0.4)

    intents = [
        "kernel_boot",  # Should manifest (k-heavy)
        "connect_api",  # Different varga, might not manifest
        "kernel_init",  # Similar to akasha after first manifest
    ]

    for intent in intents:
        field = reactor.manifest(intent, salt="demo")
        manifested = "MANIFESTED" if field.total_energy > reactor._inertia else "PENDING"
        print(f"\n'{intent}' → {manifested}")
        print(f"  Energy: {field.total_energy:.4f} (inertia: {reactor._inertia:.2f})")

    print(f"\nFinal reactor state: {reactor.get_state()}")
