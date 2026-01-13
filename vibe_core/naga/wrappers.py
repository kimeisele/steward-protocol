"""
ASHVAMEDHA WRAPPERS (The Golden Armor)
=====================================
Layer: -1 (Naga Loka / Substrate Enforcement)

Strict Mode: No Any.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xfec408c5"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Generic, Optional, TypeVar, Union

# Defense Implementations
from vibe_core.naga.defenses.daya import DataSanitizer
from vibe_core.naga.defenses.satyam import OutputVerifier
from vibe_core.protocols.substrate import MantraOpCode, mantra_governed
from vibe_core.protocols.universal import (
    Classification,
    ClassifyInput,
    EnforceContext,
    EnforceProtocol,
    Evaluation,
    Inference,
    InferenceInput,
    InferProtocol,
    MemoryValue,
    ReadResult,
    ReadWriteProtocol,
    SovereignContext,
    StoreRecallProtocol,
    SyncProtocol,
    SyncResult,
    Verdict,
)

T = TypeVar("T")
ContextT = TypeVar("ContextT", bound=SovereignContext)

import logging

logger = logging.getLogger("ASHVAMEDHA")


class MantraBase:
    """Base class for Mantra Wrappers to provide Resonance."""

    def resonate(self, opcode: MantraOpCode) -> bool:
        # Core Mantra Logic (could delegate to ananta/substrate later)
        # Log the resonance for Verification (Test observes this)
        logger.info(f"🕉️  [MANTRA] {opcode.name} | Source: {self.__class__.__name__}")
        return True


class AshvamedhaBase(MantraBase):
    """Base class for Ashvamedha wrappers."""

    def __init__(self, inner: object):
        super().__init__()
        self._inner = inner
        self._daya = DataSanitizer()
        self._satyam = OutputVerifier()


class AshvamedhaReadWrite(AshvamedhaBase, ReadWriteProtocol):
    """Wraps ReadWrite with DAYA (Input Sanctity) and MANTRA (SYS_WAKE)."""

    @mantra_governed(MantraOpCode.SYS_WAKE)
    def read(self, key: str, context: Optional[SovereignContext] = None) -> ReadResult:
        # DAYA: Sanitize Input Key
        clean_key = self._daya.enforce_purity(key, context)  # type: ignore

        # EXECUTE - Inner is treated as ReadWriteProtocol structure
        # Use getattr/call for duck typing or explicit cast if we knew the type
        # But here we rely on the protocol.
        # Since _inner is 'object' typed above, we might need a cast or assume it matches.
        # But 'Protocol' implies structural typing.

        # We assume _inner has read/write.
        inner: ReadWriteProtocol = self._inner  # type: ignore
        result = inner.read(clean_key, context)
        return result

    @mantra_governed(MantraOpCode.SYS_WAKE)
    def write(self, key: str, value: object, context: Optional[SovereignContext] = None) -> None:
        # DAYA: Sanitize Input
        clean_key = self._daya.enforce_purity(key, context)  # type: ignore
        clean_value = self._daya.enforce_purity(value, context)

        inner: ReadWriteProtocol = self._inner  # type: ignore
        inner.write(str(clean_key), clean_value, context)

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        inner: ReadWriteProtocol = self._inner  # type: ignore
        return inner.exists(key, context)


class AshvamedhaSync(AshvamedhaBase, SyncProtocol):
    """Wraps Sync with SATYAM (Truth) and MANTRA (ASSERT_TRUTH)."""

    @mantra_governed(MantraOpCode.COMPILE_AST)
    def sync_state(self, context: Optional[SovereignContext] = None) -> SyncResult:
        inner: SyncProtocol = self._inner  # type: ignore
        result = inner.sync_state(context)
        # SATYAM: Verify Output
        self._satyam.enforce_truth(result)  # type: ignore
        return result

    @mantra_governed(MantraOpCode.COMPILE_AST)
    def get_sync_status(self) -> Dict[str, object]:
        inner: SyncProtocol = self._inner  # type: ignore
        return inner.get_sync_status()


# =============================================================================
# ASHVAMEDHA ENFORCE - CHECK_DHARMA (The Law)
# =============================================================================


class AshvamedhaEnforce(AshvamedhaBase, EnforceProtocol):
    """
    Wraps Enforce with DHARMA (Law) and MANTRA (CHECK_DHARMA).

    SAMKHYA MAPPING:
    - Enforce → CHECK_DHARMA (Step 11: Validate against Rules)
    - "Dharma eva hato hanti" - Dharma destroys those who destroy it.
    """

    @mantra_governed(MantraOpCode.STATE_SYNC)
    def enforce(self, action: str, context: EnforceContext) -> Verdict:
        """Enforce rules with Mantra resonance."""
        # DAYA: Sanitize action string
        clean_action = self._daya.enforce_purity(action, None)  # type: ignore

        inner: EnforceProtocol = self._inner  # type: ignore
        verdict = inner.enforce(str(clean_action), context)

        # SATYAM: Verify the verdict is legitimate
        self._satyam.enforce_truth(verdict)  # type: ignore
        return verdict

    @mantra_governed(MantraOpCode.STATE_SYNC)
    def check(self, action: str) -> bool:
        """Quick check with Mantra resonance."""
        inner: EnforceProtocol = self._inner  # type: ignore
        return inner.check(action)

    def get_rules(self) -> list:
        """Get rules (no mantra needed - read-only)."""
        inner: EnforceProtocol = self._inner  # type: ignore
        return inner.get_rules()


# =============================================================================
# ASHVAMEDHA INFER - RESOLVE_REQ (The Intellect)
# =============================================================================


class AshvamedhaInfer(AshvamedhaBase, InferProtocol):
    """
    Wraps Infer with BUDDHI (Intellect) and MANTRA (RESOLVE_REQ).

    SAMKHYA MAPPING:
    - Infer → RESOLVE_REQ (Step 6: Parse Intent / What is the true will?)
    - Buddhi discriminates between Real and Unreal.
    """

    @mantra_governed(MantraOpCode.BIND_SYMBOL)
    def infer(self, input: InferenceInput, fallback: "Inference | None" = None) -> Inference:
        """Draw inference with Mantra resonance."""
        inner: InferProtocol = self._inner  # type: ignore
        try:
            result = inner.infer(input, fallback)
            # SATYAM: Verify inference is grounded
            self._satyam.enforce_truth(result)  # type: ignore
            return result
        except Exception as e:
            if fallback:
                logger.warning(f"Infer failed, using fallback: {e}")
                return fallback
            raise

    @mantra_governed(MantraOpCode.BIND_SYMBOL)
    def classify(self, input: ClassifyInput, fallback: "Classification | None" = None) -> Classification:
        """Classify with Mantra resonance."""
        inner: InferProtocol = self._inner  # type: ignore
        try:
            result = inner.classify(input, fallback)
            return result
        except Exception as e:
            if fallback:
                logger.warning(f"Classify failed, using fallback: {e}")
                return fallback
            raise

    def evaluate(self, claim: str) -> Evaluation:
        """Evaluate truth of claim."""
        inner: InferProtocol = self._inner  # type: ignore
        return inner.evaluate(claim)


# =============================================================================
# ASHVAMEDHA STORE - COMMIT_LOG (The Memory)
# =============================================================================


class AshvamedhaStore(AshvamedhaBase, StoreRecallProtocol):
    """
    Wraps StoreRecall with SMRITI (Memory) and MANTRA (COMMIT_LOG).

    SAMKHYA MAPPING:
    - Store → COMMIT_LOG (Step 12: Write to Immutable Stone)
    - "What is written in the Akashic Record cannot be erased."
    """

    @mantra_governed(MantraOpCode.LEDGER_SIGN)
    def store(self, key: str, value: MemoryValue, context: "SovereignContext | None" = None) -> None:
        """Store with Mantra resonance - permanent inscription."""
        # DAYA: Sanitize key
        clean_key = self._daya.enforce_purity(key, context)  # type: ignore

        inner: StoreRecallProtocol = self._inner  # type: ignore
        inner.store(str(clean_key), value, context)
        logger.debug(f"🕉️  [COMMIT_LOG] Stored: {clean_key}")

    def recall(self, key: str, context: "SovereignContext | None" = None) -> "MemoryValue | None":
        """Recall from memory (no mantra needed - read-only)."""
        inner: StoreRecallProtocol = self._inner  # type: ignore
        return inner.recall(key, context)

    @mantra_governed(MantraOpCode.LEDGER_SIGN)
    def forget(self, key: str, context: "SovereignContext | None" = None) -> bool:
        """Forget (tombstone) - still requires mantra as it mutates."""
        inner: StoreRecallProtocol = self._inner  # type: ignore
        return inner.forget(key, context)
