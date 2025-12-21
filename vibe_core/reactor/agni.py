"""
🔥 OPUS-201: AgniEngine - The Resonance Reactor

"अग्निमीळे पुरोहितं" - "I worship Agni, the foremost" (Rig Veda 1.1.1)

Agni (Fire) is the cosmic transformer - turning intention into manifestation.
This engine computes resonance between intention (Sankalpa) and system state (Akasha).

Breaking the Binary: Instead of if/else, we compute harmonic interference.
"""

import hashlib
import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .atom import Guna, Varga, VarnaTensor, encode_intent

logger = logging.getLogger("REACTOR.AGNI")

# Try numpy, fallback to pure Python
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class ResonanceResult:
    """Result of a resonance computation."""

    resonance: float  # 0.0 - 1.0 (similarity)
    status: str  # SIDDHI, TAPAS, or DHUMRA
    intent_vector: Tuple[float, ...]
    field_vector: Tuple[float, ...]
    crypto_alignment: float  # How well crypto dimensions align


class AgniEngine:
    """
    The Quantum Reactor - Computing Dharmic Probability.

    Instead of boolean logic, we compute harmonic resonance between:
    - Sankalpa (Intention): The intent tensor
    - Akasha (Field): The current system state tensor

    Results:
    - SIDDHI: Resonance >= threshold -> Spontaneous manifestation
    - TAPAS: 0.3 <= Resonance < threshold -> Heat generated, action pending
    - DHUMRA: Resonance < 0.3 -> Smoke only (error/noise/attack)
    """

    # Threshold constants
    SIDDHI_THRESHOLD = 0.85  # Critical mass for manifestation
    DHUMRA_THRESHOLD = 0.30  # Below this is rejected

    def __init__(self, initial_field: Optional[Tuple[float, ...]] = None):
        """
        Initialize the Agni Engine.

        Args:
            initial_field: Initial Akasha field state (defaults to balanced)
        """
        # The Akasha Field: Current system state as a 4D vector
        # Starts in balanced state (Sattva)
        if initial_field is not None:
            self.akasha_field = initial_field
        else:
            self.akasha_field = (0.5, 0.5, 0.5, 1.0)  # Balanced, high integrity

        # Learning rate for field adaptation
        self.field_learning_rate = 0.1

        # Entropy pool for crypto-continuity
        self.entropy_pool = b""

        # History of recent computations (for pattern detection)
        self.history: List[ResonanceResult] = []
        self.max_history = 100

        logger.info("🔥 AGNI ENGINE IGNITED")

    def _dot_product(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Compute dot product of two vectors."""
        return sum(a * b for a, b in zip(v1, v2))

    def _norm(self, v: Tuple[float, ...]) -> float:
        """Compute L2 norm of a vector."""
        return math.sqrt(sum(x * x for x in v))

    def _cosine_similarity(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """
        Compute cosine similarity between two vectors.

        Returns value between -1.0 and 1.0, normalized to 0.0-1.0.
        """
        dot = self._dot_product(v1, v2)
        norm1 = self._norm(v1)
        norm2 = self._norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cosine = dot / (norm1 * norm2)
        # Normalize from [-1, 1] to [0, 1]
        return (cosine + 1.0) / 2.0

    def check_resonance(self, intent: VarnaTensor, context_hash: str = "") -> ResonanceResult:
        """
        Core Algorithm: Cosine Similarity in 4D space + Crypto binding.

        Args:
            intent: The intention as VarnaTensor
            context_hash: Current context hash (for crypto-alignment)

        Returns:
            ResonanceResult with computed values
        """
        # 1. Intent vector
        v_intent = intent.to_vector()

        # 2. Field vector (system state)
        v_field = self.akasha_field

        # 3. Base resonance (cosine similarity)
        raw_resonance = self._cosine_similarity(v_intent, v_field)

        # 4. Crypto alignment factor
        crypto_alignment = self._compute_crypto_alignment(intent, context_hash)

        # 5. Combined resonance with crypto weight
        # Crypto alignment modulates the resonance (can dampen dissonant actions)
        final_resonance = (raw_resonance * 0.7) + (crypto_alignment * 0.3)

        # 6. Determine status
        if final_resonance >= self.SIDDHI_THRESHOLD:
            status = "SIDDHI"  # Success - manifest
        elif final_resonance < self.DHUMRA_THRESHOLD:
            status = "DHUMRA"  # Smoke - reject
        else:
            status = "TAPAS"  # Heat - pending

        result = ResonanceResult(
            resonance=final_resonance,
            status=status,
            intent_vector=v_intent,
            field_vector=v_field,
            crypto_alignment=crypto_alignment,
        )

        # Record in history
        self._record_history(result)

        return result

    def _compute_crypto_alignment(self, intent: VarnaTensor, context_hash: str) -> float:
        """
        Compute how well the intent's crypto signature aligns with context.

        This creates the "ephemeral but crypto" effect - same intent in different
        contexts produces different alignment values.
        """
        if not context_hash:
            # No context = neutral alignment
            return 0.5

        # Mix intent entropy with context
        combined = f"{intent.entropy}:{context_hash}".encode()
        combined_hash = hashlib.sha256(combined).digest()

        # Compute alignment from hash properties
        alignment = sum(combined_hash) / (len(combined_hash) * 255)

        # Update entropy pool (creates chain)
        self.entropy_pool = hashlib.sha256(self.entropy_pool + combined_hash).digest()

        return alignment

    def ignite(self, intent: VarnaTensor, context_hash: str = "") -> str:
        """
        Attempt to ignite an action.

        Args:
            intent: The intention as VarnaTensor
            context_hash: Current context hash (ledger hash, session id, etc.)

        Returns:
            Status string: "SIDDHI", "TAPAS", or "DHUMRA"
        """
        result = self.check_resonance(intent, context_hash)

        # Log the reading
        varga_name = Varga(intent.varga).name if 0 <= intent.varga <= 4 else "?"
        logger.info(f"🔥 AGNI READING: {result.resonance:.4f} | Varga: {varga_name} | Status: {result.status}")

        if result.status == "SIDDHI":
            # Critical mass reached -> Update field (learning)
            self._update_field(intent)
            logger.info(f"✨ SIDDHI: Manifestation authorized for '{intent.source}'")

        elif result.status == "DHUMRA":
            logger.warning(f"⛔ DHUMRA: Dissonance detected, rejecting '{intent.source}'")
            # Increase field entropy to resist similar attacks
            self._harden_field()

        else:
            logger.info(f"🔥 TAPAS: Heat generated, awaiting conditions for '{intent.source}'")

        return result.status

    def _update_field(self, intent: VarnaTensor) -> None:
        """
        Neuroplasticity: The system learns from successful actions.

        The field vector approaches the intent vector (habituation).
        """
        v_intent = intent.to_vector()
        lr = self.field_learning_rate

        # Weighted average: field moves toward intent
        new_field = tuple((f * (1 - lr)) + (i * lr) for f, i in zip(self.akasha_field, v_intent))

        self.akasha_field = new_field
        logger.debug(f"Field updated: {self.akasha_field}")

    def _harden_field(self) -> None:
        """
        Security response: Increase crypto entropy after attack detection.

        Makes it harder for similar dissonant actions to pass.
        """
        # Increase the entropy dimension slightly
        current = list(self.akasha_field)
        current[3] = min(1.0, current[3] + 0.05)  # Boost crypto dimension
        self.akasha_field = tuple(current)
        logger.debug(f"Field hardened: {self.akasha_field}")

    def _record_history(self, result: ResonanceResult) -> None:
        """Record computation in history for pattern detection."""
        self.history.append(result)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    def get_field_state(self) -> dict:
        """Get current field state for debugging/display."""
        return {
            "akasha_field": self.akasha_field,
            "entropy_pool_hash": hashlib.sha256(self.entropy_pool).hexdigest()[:16],
            "history_count": len(self.history),
            "last_result": self.history[-1].status if self.history else None,
        }

    def reset_field(self) -> None:
        """Reset field to balanced state (useful for testing)."""
        self.akasha_field = (0.5, 0.5, 0.5, 1.0)
        self.entropy_pool = b""
        self.history = []
        logger.info("🔄 AGNI FIELD RESET")


# =============================================================================
# Convenience Functions
# =============================================================================

_global_engine: Optional[AgniEngine] = None


def get_agni() -> AgniEngine:
    """Get or create the global AgniEngine instance."""
    global _global_engine
    if _global_engine is None:
        _global_engine = AgniEngine()
    return _global_engine


def ignite_intent(intent_str: str, salt: str = "", context_hash: str = "") -> str:
    """
    Convenience function to encode and ignite an intent.

    Args:
        intent_str: The intent text
        salt: Cryptographic salt
        context_hash: Current context hash

    Returns:
        Status: "SIDDHI", "TAPAS", or "DHUMRA"
    """
    tensor = encode_intent(intent_str, salt)
    return get_agni().ignite(tensor, context_hash)


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("🔥 AgniEngine Self-Test\n")

    engine = AgniEngine()

    test_cases = [
        ("kernel_boot", "session123", "ledger_latest"),
        ("create_file", "session123", "ledger_latest"),
        ("DROP TABLE users", "malicious_salt", "wrong_context"),
        ("read_config", "session123", "ledger_latest"),
        ("deploy_production", "session123", "ledger_latest"),
    ]

    print("Testing various intents:\n")
    for intent_str, salt, ctx in test_cases:
        tensor = encode_intent(intent_str, salt)
        status = engine.ignite(tensor, ctx)
        print(f"  Intent: '{intent_str}' -> {status}\n")

    print(f"\n📊 Final Field State: {engine.get_field_state()}")
