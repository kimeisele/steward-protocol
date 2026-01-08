"""
ASHVAMEDHA WRAPPERS (The Golden Armor)
=====================================
Layer: -1 (Naga Loka / Substrate Enforcement)

Strict Mode: No Any.
"""

from typing import Dict, Generic, Optional, TypeVar, Union

# Defense Implementations
from vibe_core.naga.defenses.daya import DataSanitizer
from vibe_core.naga.defenses.satyam import OutputVerifier
from vibe_core.protocols.substrate import MantraOpCode, mantra_governed
from vibe_core.protocols.universal import (
    EnforceContext,
    EnforceProtocol,
    Inference,
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

    @mantra_governed(MantraOpCode.ASSERT_TRUTH)
    def sync_state(self, context: Optional[SovereignContext] = None) -> SyncResult:
        inner: SyncProtocol = self._inner  # type: ignore
        result = inner.sync_state(context)
        # SATYAM: Verify Output
        self._satyam.enforce_truth(result)  # type: ignore
        return result

    @mantra_governed(MantraOpCode.ASSERT_TRUTH)
    def get_sync_status(self) -> Dict[str, object]:
        inner: SyncProtocol = self._inner  # type: ignore
        return inner.get_sync_status()
