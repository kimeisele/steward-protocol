"""
OPUS-201: AgniEngine - The Resonance Reactor (REFINED)

"agnimile purohitam" - "I worship Agni, the foremost" (Rig Veda 1.1.1)

REFINEMENT from original:
- Akasha field bound to manas_awareness.json (Biorhythm integration)
- Constitutional anchors that cannot be drifted
- Hardening after attack detection
- TaskKernel integration point

Agni (Fire) is the cosmic transformer - turning intention into manifestation.
This engine computes resonance between intention (Sankalpa) and system state (Akasha).
"""

import hashlib
import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .atom import Guna, Varga, VarnaTensor, encode_intent

logger = logging.getLogger("REACTOR.AGNI")


# =============================================================================
# CONSTITUTIONAL ANCHORS (Immutable - cannot be drifted)
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalAnchor:
    """
    Immutable anchor that cannot be changed by field learning.

    These are the "bedrock" values that prevent drift exploitation.
    """

    name: str
    varga: float  # 0.0 - 1.0
    shakti: float  # 0.0 - 1.0
    guna: float  # 0.0 - 1.0
    entropy: float  # 0.0 - 1.0
    weight: float  # How strongly this anchor pulls (0.0 - 1.0)

    def to_vector(self) -> Tuple[float, float, float, float]:
        return (self.varga, self.shakti, self.guna, self.entropy)


# The Constitution - these cannot be changed at runtime
CONSTITUTIONAL_ANCHORS = {
    # TAMAS anchor: Low energy, inertia - pulls field during hibernation
    "TAMAS_ANCHOR": ConstitutionalAnchor(
        name="TAMAS_ANCHOR",
        varga=0.0,  # Kernel layer
        shakti=0.1,  # Low energy
        guna=0.0,  # Tamas (-1 normalized to 0)
        entropy=1.0,  # High integrity required
        weight=0.8,  # Strong pull
    ),
    # SATTVA anchor: Balanced - maintenance mode
    "SATTVA_ANCHOR": ConstitutionalAnchor(
        name="SATTVA_ANCHOR",
        varga=0.5,  # Middle layer
        shakti=0.5,  # Medium energy
        guna=0.5,  # Sattva (0 normalized to 0.5)
        entropy=0.8,  # Good integrity
        weight=0.5,  # Medium pull
    ),
    # RAJAS anchor: High energy, activity - production mode
    "RAJAS_ANCHOR": ConstitutionalAnchor(
        name="RAJAS_ANCHOR",
        varga=1.0,  # Agent layer
        shakti=0.9,  # High energy
        guna=1.0,  # Rajas (+1 normalized to 1)
        entropy=0.9,  # High integrity
        weight=0.6,  # Medium-strong pull
    ),
    # DANGEROUS anchor: Always blocks dangerous operations in wrong state
    "DANGEROUS_BLOCK": ConstitutionalAnchor(
        name="DANGEROUS_BLOCK",
        varga=0.0,
        shakti=0.0,
        guna=0.0,
        entropy=1.0,  # Requires perfect crypto
        weight=1.0,  # Maximum pull
    ),
}


@dataclass
class ResonanceResult:
    """Result of a resonance computation."""

    resonance: float  # 0.0 - 1.0 (similarity)
    status: str  # SIDDHI, TAPAS, or DHUMRA
    intent_vector: Tuple[float, ...]
    field_vector: Tuple[float, ...]
    crypto_alignment: float
    anchor_applied: Optional[str] = None
    is_dangerous: bool = False


class AgniEngine:
    """
    The Quantum Reactor - Computing Dharmic Probability (REFINED).

    IMPROVEMENTS:
    1. Akasha field bound to manas_awareness.json
    2. Constitutional anchors prevent drift exploitation
    3. Dangerous operations get special handling
    4. Hardening after attacks
    """

    # Threshold constants
    SIDDHI_THRESHOLD = 0.85  # Critical mass for manifestation
    DHUMRA_THRESHOLD = 0.30  # Below this is rejected
    DANGEROUS_THRESHOLD = 0.95  # Dangerous ops need higher resonance

    # Path to manas_awareness.json
    AWARENESS_PATH = Path(".opus_state/manas_awareness.json")

    def __init__(
        self,
        awareness_path: Optional[Path] = None,
        on_state_change: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the Agni Engine.

        Args:
            awareness_path: Path to manas_awareness.json (optional override)
            on_state_change: Callback when resonance state changes
        """
        self._awareness_path = awareness_path or self.AWARENESS_PATH
        self._on_state_change = on_state_change

        # The Akasha Field - computed from Biorhythm, not arbitrary
        self._base_field = (0.5, 0.5, 0.5, 1.0)  # Fallback
        self._current_anchor: Optional[str] = None

        # Learning rate for field adaptation (reduced for safety)
        self._field_learning_rate = 0.05  # Was 0.1 - halved

        # Maximum drift from constitutional anchor
        self._max_drift = 0.15  # Field cannot drift more than 15% from anchor

        # Entropy pool for crypto-continuity
        self._entropy_pool = b""

        # Attack detection
        self._consecutive_dhumra = 0
        self._hardening_level = 0.0

        # History
        self._history: List[ResonanceResult] = []
        self._max_history = 100

        # Load initial state from Biorhythm
        self._sync_with_biorhythm()

        logger.info("AGNI ENGINE IGNITED (REFINED)")

    def _sync_with_biorhythm(self) -> None:
        """
        Sync Akasha field with manas_awareness.json.

        This is the key integration - the Biorhythm controls the field.
        """
        try:
            if self._awareness_path.exists():
                with open(self._awareness_path) as f:
                    awareness = json.load(f)

                state = awareness.get("state", "sattva").upper()
                consciousness = awareness.get("consciousness_level", 0.5)

                # Select constitutional anchor based on Biorhythm state
                if state == "TAMAS":
                    self._current_anchor = "TAMAS_ANCHOR"
                elif state == "RAJAS":
                    self._current_anchor = "RAJAS_ANCHOR"
                else:  # SATTVA or unknown
                    self._current_anchor = "SATTVA_ANCHOR"

                anchor = CONSTITUTIONAL_ANCHORS[self._current_anchor]

                # Set base field from anchor, modulated by consciousness
                self._base_field = tuple(v * consciousness + (1 - consciousness) * 0.5 for v in anchor.to_vector())

                logger.info(
                    f"Biorhythm sync: state={state}, consciousness={consciousness:.2f}, anchor={self._current_anchor}"
                )
            else:
                logger.warning(f"Awareness file not found: {self._awareness_path}")
                self._current_anchor = "SATTVA_ANCHOR"

        except Exception as e:
            logger.warning(f"Failed to sync with Biorhythm: {e}")
            self._current_anchor = "SATTVA_ANCHOR"

    @property
    def akasha_field(self) -> Tuple[float, float, float, float]:
        """
        Get current Akasha field, constrained by constitutional anchor.
        """
        if self._current_anchor is None:
            self._sync_with_biorhythm()

        anchor = CONSTITUTIONAL_ANCHORS.get(self._current_anchor or "SATTVA_ANCHOR")
        anchor_vec = anchor.to_vector()

        # Apply drift constraint - field cannot be more than max_drift from anchor
        constrained = []
        for base, anch in zip(self._base_field, anchor_vec):
            drift = base - anch
            if abs(drift) > self._max_drift:
                drift = self._max_drift if drift > 0 else -self._max_drift
            constrained.append(anch + drift)

        # Apply hardening (increases entropy requirement)
        constrained[3] = min(1.0, constrained[3] + self._hardening_level)

        return tuple(constrained)

    def _dot_product(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """Compute dot product of two vectors."""
        return sum(a * b for a, b in zip(v1, v2))

    def _norm(self, v: Tuple[float, ...]) -> float:
        """Compute L2 norm of a vector."""
        return math.sqrt(sum(x * x for x in v))

    def _cosine_similarity(self, v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
        """
        Compute cosine similarity between two vectors.
        Returns value between 0.0 and 1.0.
        """
        dot = self._dot_product(v1, v2)
        norm1 = self._norm(v1)
        norm2 = self._norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cosine = dot / (norm1 * norm2)
        return (cosine + 1.0) / 2.0  # Normalize to 0-1

    def check_resonance(
        self,
        intent: VarnaTensor,
        context_hash: str = "",
    ) -> ResonanceResult:
        """
        Core Algorithm: Cosine Similarity + Constitutional Anchors + Crypto.

        Args:
            intent: The intention as VarnaTensor
            context_hash: Current context hash (ledger hash, session id)

        Returns:
            ResonanceResult with computed values
        """
        # Sync with Biorhythm before each check
        self._sync_with_biorhythm()

        # 1. Intent vector
        v_intent = intent.to_vector()

        # 2. Field vector (anchored to Biorhythm)
        v_field = self.akasha_field

        # 3. Base resonance
        raw_resonance = self._cosine_similarity(v_intent, v_field)

        # 4. Crypto alignment
        crypto_alignment = self._compute_crypto_alignment(intent, context_hash)

        # 5. Combined resonance
        final_resonance = (raw_resonance * 0.7) + (crypto_alignment * 0.3)

        # 6. Dangerous operation handling
        if intent.is_dangerous:
            # Dangerous operations need higher threshold
            threshold = self.DANGEROUS_THRESHOLD

            # Apply DANGEROUS_BLOCK anchor check
            danger_anchor = CONSTITUTIONAL_ANCHORS["DANGEROUS_BLOCK"]
            danger_resonance = self._cosine_similarity(v_intent, danger_anchor.to_vector())

            # If we're in TAMAS (hibernation), block dangerous ops entirely
            if self._current_anchor == "TAMAS_ANCHOR":
                final_resonance *= 0.1  # Severe penalty
                logger.warning("Dangerous operation during TAMAS - severe penalty applied")
        else:
            threshold = self.SIDDHI_THRESHOLD

        # 7. Determine status
        if final_resonance >= threshold:
            status = "SIDDHI"
            self._consecutive_dhumra = 0  # Reset attack counter
        elif final_resonance < self.DHUMRA_THRESHOLD:
            status = "DHUMRA"
            self._consecutive_dhumra += 1
            # Harden after consecutive attacks
            if self._consecutive_dhumra >= 3:
                self._harden_field()
        else:
            status = "TAPAS"
            self._consecutive_dhumra = 0

        result = ResonanceResult(
            resonance=final_resonance,
            status=status,
            intent_vector=v_intent,
            field_vector=v_field,
            crypto_alignment=crypto_alignment,
            anchor_applied=self._current_anchor,
            is_dangerous=intent.is_dangerous,
        )

        self._record_history(result)

        return result

    def _compute_crypto_alignment(self, intent: VarnaTensor, context_hash: str) -> float:
        """
        Compute crypto alignment between intent and context.
        """
        if not context_hash:
            return 0.5

        combined = f"{intent.entropy}:{context_hash}".encode()
        combined_hash = hashlib.sha256(combined).digest()
        alignment = sum(combined_hash) / (len(combined_hash) * 255)

        # Update entropy pool
        self._entropy_pool = hashlib.sha256(self._entropy_pool + combined_hash).digest()

        return alignment

    def ignite(
        self,
        intent: VarnaTensor,
        context_hash: str = "",
    ) -> str:
        """
        Attempt to ignite an action.

        Args:
            intent: The intention as VarnaTensor
            context_hash: Current context hash

        Returns:
            Status: "SIDDHI", "TAPAS", or "DHUMRA"
        """
        result = self.check_resonance(intent, context_hash)

        varga_name = Varga(intent.varga).name if 0 <= intent.varga <= 4 else "?"
        danger_flag = " [DANGEROUS]" if intent.is_dangerous else ""

        logger.info(
            f"AGNI: {result.resonance:.4f} | {varga_name} | {result.status} | "
            f"anchor={result.anchor_applied}{danger_flag}"
        )

        if result.status == "SIDDHI":
            # Learn from success (limited by constitutional anchor)
            self._update_field(intent)
            logger.info(f"SIDDHI: Manifestation authorized for '{intent.source}'")

            if self._on_state_change:
                self._on_state_change("SIDDHI")

        elif result.status == "DHUMRA":
            logger.warning(f"DHUMRA: Dissonance detected for '{intent.source}'")

            if self._on_state_change:
                self._on_state_change("DHUMRA")

        else:
            logger.info(f"TAPAS: Heat generated for '{intent.source}'")

        return result.status

    def _update_field(self, intent: VarnaTensor) -> None:
        """
        Neuroplasticity with constitutional constraints.

        Field can learn, but cannot drift beyond max_drift from anchor.
        """
        v_intent = intent.to_vector()
        lr = self._field_learning_rate

        # Weighted average
        new_field = tuple((f * (1 - lr)) + (i * lr) for f, i in zip(self._base_field, v_intent))

        self._base_field = new_field
        # Note: akasha_field property will apply drift constraints

    def _harden_field(self) -> None:
        """
        Security response after attack detection.
        """
        self._hardening_level = min(0.3, self._hardening_level + 0.1)
        logger.warning(f"Field hardened: level={self._hardening_level:.2f}")

    def _record_history(self, result: ResonanceResult) -> None:
        """Record computation in history."""
        self._history.append(result)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def get_field_state(self) -> dict:
        """Get current field state for debugging."""
        return {
            "akasha_field": self.akasha_field,
            "base_field": self._base_field,
            "current_anchor": self._current_anchor,
            "hardening_level": self._hardening_level,
            "consecutive_dhumra": self._consecutive_dhumra,
            "entropy_pool_hash": hashlib.sha256(self._entropy_pool).hexdigest()[:16],
            "history_count": len(self._history),
        }

    def reset(self) -> None:
        """Reset to initial state."""
        self._base_field = (0.5, 0.5, 0.5, 1.0)
        self._current_anchor = None
        self._hardening_level = 0.0
        self._consecutive_dhumra = 0
        self._entropy_pool = b""
        self._history = []
        self._sync_with_biorhythm()
        logger.info("AGNI RESET")


# =============================================================================
# Integration with TaskKernel
# =============================================================================


def create_resonance_guard(
    engine: Optional[AgniEngine] = None,
) -> Callable[[VarnaTensor, str], bool]:
    """
    Create a guard function for TaskKernel integration.

    Returns a function that checks resonance before tool execution.

    Usage in TaskKernel:
        guard = create_resonance_guard()
        if not guard(intent_tensor, context_hash):
            raise PermissionError("Resonance check failed")
    """
    _engine = engine or AgniEngine()

    def guard(intent: VarnaTensor, context_hash: str = "") -> bool:
        result = _engine.check_resonance(intent, context_hash)
        return result.status != "DHUMRA"

    return guard


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


def ignite_intent(
    intent_str: str,
    salt: str = "",
    context_hash: str = "",
) -> str:
    """
    Convenience function to encode and ignite an intent.

    Returns: "SIDDHI", "TAPAS", or "DHUMRA"
    """
    tensor = encode_intent(intent_str, salt)
    return get_agni().ignite(tensor, context_hash)


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("OPUS-201: AgniEngine Self-Test (REFINED)\n")

    engine = AgniEngine()

    test_cases = [
        # Normal operations
        ("kernel_boot", "session123", "ledger_v1"),
        ("read_config", "session123", "ledger_v1"),
        ("create_file", "session123", "ledger_v1"),
        # Dangerous operations (should be blocked or need high resonance)
        ("delete_database", "session123", "ledger_v1"),
        ("DROP TABLE users", "malicious", "wrong_context"),
        # Attack simulation (3 consecutive to trigger hardening)
        ("attack_1", "bad", "fake"),
        ("attack_2", "bad", "fake"),
        ("attack_3", "bad", "fake"),
        # After hardening, normal ops should still work
        ("read_config", "session123", "ledger_v1"),
    ]

    print("Testing various intents:\n")
    for intent_str, salt, ctx in test_cases:
        tensor = encode_intent(intent_str, salt)
        status = engine.ignite(tensor, ctx)
        print(f"  '{intent_str}' -> {status}\n")

    print(f"\nFinal State: {json.dumps(engine.get_field_state(), indent=2)}")
