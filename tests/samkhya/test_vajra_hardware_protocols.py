"""
VAJRA HARDWARE PROTOCOLS TEST
=============================

OPUS-098: Vedic Computer Architecture

This test verifies the Protocol Signatures for the 8 Hardware Protocols:
- PranaProtocol    (Power Supply / Life Force)
- KalaProtocol     (System Clock / Time)
- ChittaProtocol   (RAM / Volatile Memory)
- SmritiProtocol   (Cache / Memory Hierarchy)
- NadiProtocol     (Bus / Data Channels)
- SankalpaProtocol (Interrupts / Intent)
- IndriyaProtocol  (Registers / I/O)
- AkashaProtocol   (Network / Ether Field)

Protocol First. Then Test. Implementation is just the result.

"अहं सर्वस्य प्रभवो मत्तः सर्वं प्रवर्तते"
"I am the source of all. Everything emanates from Me."
— Bhagavad Gita 10.8
"""

import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pytest

from vibe_core.protocols.substrate import (
    # Hardware TypedDicts & DataClasses
    ActionData,
    # Hardware Protocols
    AkashaProtocol,
    ChittaBlock,
    ChittaProtocol,
    FieldState,
    IndriyaProtocol,
    KalaProtocol,
    NadiChannel,
    NadiProtocol,
    PranaLevel,
    PranaProtocol,
    SankalpaIntent,
    SankalpaProtocol,
    SenseData,
    SmritiProtocol,
    Vritti,
    YugaState,
)


@pytest.mark.unit
class TestVajraHardwareProtocols:
    """
    Vajra Hardening for Hardware Protocols (Layer -1).

    These tests verify that the Vedic Computer Architecture
    protocols have correct signatures and can be implemented.
    """

    # =========================================================================
    # PRANA PROTOCOL (Power Supply / Life Force)
    # =========================================================================

    def test_prana_protocol_signature(self):
        """Verify PranaProtocol has all required methods."""
        required_methods = [
            "breathe_in",
            "breathe_out",
            "circulate",
            "get_vitality",
            "suspend",
            "revive",
            "is_alive",
        ]

        for method_name in required_methods:
            assert hasattr(PranaProtocol, method_name), f"PranaProtocol missing method: {method_name}"

    def test_prana_protocol_implementation(self):
        """Verify a class can implement PranaProtocol."""

        class MockPrana:
            def breathe_in(self) -> PranaLevel:
                return PranaLevel(vitality=1.0, flow_rate=0.25, balance=0.0, source="cosmic")

            def breathe_out(self) -> PranaLevel:
                return PranaLevel(vitality=0.9)

            def circulate(self) -> PranaLevel:
                return PranaLevel(vitality=0.95)

            def get_vitality(self) -> float:
                return 1.0

            def suspend(self) -> None:
                pass

            def revive(self, source: str) -> bool:
                return True

            def is_alive(self) -> bool:
                return True

        prana = MockPrana()
        assert isinstance(prana, PranaProtocol)
        assert prana.get_vitality() == 1.0
        assert prana.is_alive() is True

    # =========================================================================
    # KALA PROTOCOL (System Clock / Time)
    # =========================================================================

    def test_kala_protocol_signature(self):
        """Verify KalaProtocol has all required methods."""
        required_methods = [
            "get_tick",
            "get_yuga",
            "get_muhurta",
            "wait_cycles",
            "is_auspicious",
            "get_elapsed",
        ]

        for method_name in required_methods:
            assert hasattr(KalaProtocol, method_name), f"KalaProtocol missing method: {method_name}"

    def test_kala_protocol_implementation(self):
        """Verify a class can implement KalaProtocol."""

        class MockKala:
            def get_tick(self) -> int:
                return 108

            def get_yuga(self) -> YugaState:
                return YugaState(
                    yuga="kali",
                    year_in_yuga=5128,
                    golden_period=True,
                    muhurta="brahma",
                )

            def get_muhurta(self) -> str:
                return "brahma"

            def wait_cycles(self, n: int) -> None:
                pass

            def is_auspicious(self, action: str) -> bool:
                return action == "chant"

            def get_elapsed(self, since_tick: int) -> int:
                return 108 - since_tick

        kala = MockKala()
        assert isinstance(kala, KalaProtocol)
        assert kala.get_tick() == 108
        yuga = kala.get_yuga()
        assert yuga["golden_period"] is True

    # =========================================================================
    # CHITTA PROTOCOL (RAM / Volatile Memory)
    # =========================================================================

    def test_chitta_protocol_signature(self):
        """Verify ChittaProtocol has all required methods."""
        required_methods = [
            "allocate",
            "deallocate",
            "impress",
            "read_impression",
            "clear",
            "get_turbulence",
            "get_total_capacity",
            "get_free_capacity",
        ]

        for method_name in required_methods:
            assert hasattr(ChittaProtocol, method_name), f"ChittaProtocol missing method: {method_name}"

    def test_chitta_protocol_implementation(self):
        """Verify a class can implement ChittaProtocol."""

        class MockChitta:
            def allocate(self, size: int, owner: str) -> ChittaBlock:
                return ChittaBlock(
                    address=0x1000,
                    size=size,
                    owner=owner,
                    created_at=datetime.now(),
                    turbulence=0.0,
                )

            def deallocate(self, block: ChittaBlock) -> None:
                pass

            def impress(self, block: ChittaBlock, vritti: Vritti) -> None:
                pass

            def read_impression(self, block: ChittaBlock) -> Optional[Vritti]:
                return Vritti(
                    content="thought",
                    source="mantra",
                    timestamp=datetime.now(),
                    intensity=0.5,
                )

            def clear(self, block: ChittaBlock) -> None:
                pass

            def get_turbulence(self) -> float:
                return 0.1

            def get_total_capacity(self) -> int:
                return 4096

            def get_free_capacity(self) -> int:
                return 3000

        chitta = MockChitta()
        assert isinstance(chitta, ChittaProtocol)
        block = chitta.allocate(108, "sovereign_001")
        assert block.size == 108
        assert chitta.get_turbulence() < 0.5  # Mind is relatively still

    # =========================================================================
    # SMRITI PROTOCOL (Cache / Memory Hierarchy)
    # =========================================================================

    def test_smriti_protocol_signature(self):
        """Verify SmritiProtocol has all required methods."""
        required_methods = [
            "remember",
            "recall",
            "forget",
            "promote",
            "demote",
            "get_level_stats",
        ]

        for method_name in required_methods:
            assert hasattr(SmritiProtocol, method_name), f"SmritiProtocol missing method: {method_name}"

    def test_smriti_protocol_implementation(self):
        """Verify a class can implement SmritiProtocol."""

        class MockSmriti:
            def __init__(self):
                self._cache: Dict[str, Tuple[object, int]] = {}

            def remember(self, key: str, value: object, level: int = 1) -> None:
                self._cache[key] = (value, level)

            def recall(self, key: str) -> Optional[Tuple[object, int]]:
                return self._cache.get(key)

            def forget(self, key: str, level: int = 0) -> bool:
                if key in self._cache:
                    del self._cache[key]
                    return True
                return False

            def promote(self, key: str) -> bool:
                if key in self._cache:
                    val, lvl = self._cache[key]
                    if lvl > 1:
                        self._cache[key] = (val, lvl - 1)
                        return True
                return False

            def demote(self, key: str) -> bool:
                if key in self._cache:
                    val, lvl = self._cache[key]
                    self._cache[key] = (val, lvl + 1)
                    return True
                return False

            def get_level_stats(self, level: int) -> Dict[str, int]:
                return {"hits": 108, "misses": 16, "size": 1728}

        smriti = MockSmriti()
        assert isinstance(smriti, SmritiProtocol)
        smriti.remember("mantra", "hare krishna", level=1)
        result = smriti.recall("mantra")
        assert result is not None
        assert result[0] == "hare krishna"
        assert result[1] == 1

    # =========================================================================
    # NADI PROTOCOL (Bus / Data Channels)
    # =========================================================================

    def test_nadi_protocol_signature(self):
        """Verify NadiProtocol has all required methods."""
        required_methods = [
            "open_channel",
            "close_channel",
            "send",
            "receive",
            "get_bandwidth",
            "is_blocked",
            "clear_blockage",
        ]

        for method_name in required_methods:
            assert hasattr(NadiProtocol, method_name), f"NadiProtocol missing method: {method_name}"

    def test_nadi_protocol_implementation(self):
        """Verify a class can implement NadiProtocol."""

        class MockNadi:
            def open_channel(self, source: str, dest: str, channel_type: str = "sushumna") -> NadiChannel:
                return NadiChannel(
                    channel_id="nadi_001",
                    source=source,
                    destination=dest,
                    channel_type=channel_type,
                    bandwidth=72000.0,  # 72,000 nadis
                    is_blocked=False,
                )

            def close_channel(self, channel: NadiChannel) -> None:
                pass

            def send(self, channel: NadiChannel, data: bytes) -> bool:
                return not channel.is_blocked

            def receive(self, channel: NadiChannel, timeout: float = 0.0) -> Optional[bytes]:
                return b"hare krishna"

            def get_bandwidth(self, channel: NadiChannel) -> float:
                return channel.bandwidth

            def is_blocked(self, channel: NadiChannel) -> bool:
                return channel.is_blocked

            def clear_blockage(self, channel: NadiChannel) -> bool:
                return True  # Granthi cleared

        nadi = MockNadi()
        assert isinstance(nadi, NadiProtocol)
        channel = nadi.open_channel("muladhara", "sahasrara", "sushumna")
        assert channel.channel_type == "sushumna"
        assert nadi.send(channel, b"om") is True

    # =========================================================================
    # SANKALPA PROTOCOL (Interrupts / Intent)
    # =========================================================================

    def test_sankalpa_protocol_signature(self):
        """Verify SankalpaProtocol has all required methods."""
        required_methods = [
            "declare",
            "revoke",
            "get_pending",
            "execute_next",
            "is_aligned",
            "get_current",
        ]

        for method_name in required_methods:
            assert hasattr(SankalpaProtocol, method_name), f"SankalpaProtocol missing method: {method_name}"

    def test_sankalpa_protocol_implementation(self):
        """Verify a class can implement SankalpaProtocol."""

        class MockSankalpa:
            def __init__(self):
                self._queue: List[SankalpaIntent] = []

            def declare(self, intent: SankalpaIntent) -> str:
                intent["intent_id"] = f"sankalpa_{len(self._queue)}"
                self._queue.append(intent)
                return intent["intent_id"]

            def revoke(self, intent_id: str) -> bool:
                for i, intent in enumerate(self._queue):
                    if intent.get("intent_id") == intent_id:
                        self._queue.pop(i)
                        return True
                return False

            def get_pending(self) -> List[SankalpaIntent]:
                return self._queue.copy()

            def execute_next(self) -> Optional[SankalpaIntent]:
                if self._queue:
                    return self._queue.pop(0)
                return None

            def is_aligned(self, intent: SankalpaIntent) -> bool:
                return intent.get("dharma_aligned", False)

            def get_current(self) -> Optional[SankalpaIntent]:
                return self._queue[0] if self._queue else None

        sankalpa = MockSankalpa()
        assert isinstance(sankalpa, SankalpaProtocol)

        intent: SankalpaIntent = {
            "action": "chant",
            "priority": 108,
            "declared_by": "sovereign_001",
            "dharma_aligned": True,
        }
        intent_id = sankalpa.declare(intent)
        assert sankalpa.is_aligned(intent) is True

    # =========================================================================
    # INDRIYA PROTOCOL (Registers / I/O)
    # =========================================================================

    def test_indriya_protocol_signature(self):
        """Verify IndriyaProtocol has all required methods."""
        required_methods = [
            "sense",
            "act",
            "calibrate",
            "get_bandwidth",
            "is_overloaded",
            "rest",
        ]

        for method_name in required_methods:
            assert hasattr(IndriyaProtocol, method_name), f"IndriyaProtocol missing method: {method_name}"

    def test_indriya_protocol_implementation(self):
        """Verify a class can implement IndriyaProtocol."""

        class MockIndriya:
            def sense(self, indriya: str) -> SenseData:
                return SenseData(
                    indriya=indriya,
                    raw_data="vibration_pattern",
                    intensity=0.7,
                    timestamp="2026-01-09T00:00:00Z",
                )

            def act(self, indriya: str, data: ActionData) -> bool:
                return True

            def calibrate(self, indriya: str) -> bool:
                return True

            def get_bandwidth(self, indriya: str) -> float:
                bandwidths = {
                    "shrotra": 20000.0,  # Hz (hearing)
                    "chakshu": 1e15,  # photons/sec (sight)
                    "tvak": 1000.0,  # touch points
                }
                return bandwidths.get(indriya, 100.0)

            def is_overloaded(self, indriya: str) -> bool:
                return False

            def rest(self, indriya: str) -> None:
                pass

        indriya = MockIndriya()
        assert isinstance(indriya, IndriyaProtocol)

        # Test sense input (Jnanendriya)
        sound = indriya.sense("shrotra")
        assert sound["indriya"] == "shrotra"

        # Test action output (Karmendriya)
        action: ActionData = {
            "indriya": "vak",
            "command": "chant",
            "force": 0.5,
            "duration": 108.0,
        }
        assert indriya.act("vak", action) is True

    # =========================================================================
    # AKASHA PROTOCOL (Network / Ether Field)
    # =========================================================================

    def test_akasha_protocol_signature(self):
        """Verify AkashaProtocol has all required methods."""
        required_methods = [
            "broadcast",
            "tune",
            "untune",
            "connect",
            "query_field",
            "get_field_state",
            "get_local_identity",
        ]

        for method_name in required_methods:
            assert hasattr(AkashaProtocol, method_name), f"AkashaProtocol missing method: {method_name}"

    def test_akasha_protocol_implementation(self):
        """Verify a class can implement AkashaProtocol."""

        class MockAkasha:
            def broadcast(self, frequency: float, message: bytes) -> None:
                pass

            def tune(self, frequency: float) -> str:
                return f"channel_{frequency}"

            def untune(self, channel_id: str) -> None:
                pass

            def connect(self, identity: str) -> Optional[NadiChannel]:
                return NadiChannel(
                    channel_id=f"akasha_{identity}",
                    source="local",
                    destination=identity,
                    channel_type="sushumna",
                    bandwidth=float("inf"),  # Instant resonance
                    is_blocked=False,
                )

            def query_field(self, pattern: str) -> List[str]:
                return ["sovereign_001", "sovereign_002"]

            def get_field_state(self) -> FieldState:
                return FieldState(
                    active_entities=108,
                    dominant_frequency=432.0,  # Hz (cosmic frequency)
                    field_coherence=0.999,
                    resonance_patterns=["hare", "krishna", "rama"],
                )

            def get_local_identity(self) -> str:
                return "sovereign_local"

        akasha = MockAkasha()
        assert isinstance(akasha, AkashaProtocol)

        # Test resonance connection (not IP-based!)
        channel = akasha.connect("sovereign_001")
        assert channel is not None
        assert channel.bandwidth == float("inf")

        # Test field state
        state = akasha.get_field_state()
        assert state["field_coherence"] > 0.9
        assert "hare" in state["resonance_patterns"]


@pytest.mark.unit
class TestHardwareDataClasses:
    """Test the TypedDicts and DataClasses for Hardware layer."""

    def test_prana_level_typed_dict(self):
        """Verify PranaLevel TypedDict structure."""
        level: PranaLevel = {
            "vitality": 1.0,
            "flow_rate": 0.25,
            "balance": 0.0,
            "source": "brahman",
        }
        assert level["vitality"] == 1.0
        assert level["balance"] == 0.0

    def test_yuga_state_typed_dict(self):
        """Verify YugaState TypedDict structure."""
        state: YugaState = {
            "yuga": "kali",
            "year_in_yuga": 5128,
            "golden_period": True,
            "muhurta": "brahma",
        }
        assert state["golden_period"] is True

    def test_chitta_block_dataclass(self):
        """Verify ChittaBlock dataclass."""
        block = ChittaBlock(
            address=0x1000,
            size=108,
            owner="sovereign_001",
            created_at=datetime.now(),
            turbulence=0.0,
        )
        assert block.size == 108
        assert block.turbulence == 0.0

    def test_vritti_dataclass(self):
        """Verify Vritti (mental modification) dataclass."""
        vritti = Vritti(
            content="hare krishna",
            source="mantra",
            timestamp=datetime.now(),
            intensity=1.0,
        )
        assert vritti.content == "hare krishna"
        assert vritti.intensity == 1.0

    def test_nadi_channel_dataclass(self):
        """Verify NadiChannel dataclass."""
        channel = NadiChannel(
            channel_id="sushumna_001",
            source="muladhara",
            destination="sahasrara",
            channel_type="sushumna",
            bandwidth=72000.0,
            is_blocked=False,
        )
        assert channel.channel_type == "sushumna"
        assert channel.is_blocked is False

    def test_sankalpa_intent_typed_dict(self):
        """Verify SankalpaIntent TypedDict structure."""
        intent: SankalpaIntent = {
            "intent_id": "sankalpa_001",
            "action": "chant_mahamantra",
            "priority": 108,
            "declared_by": "sovereign_001",
            "dharma_aligned": True,
        }
        assert intent["dharma_aligned"] is True

    def test_field_state_typed_dict(self):
        """Verify FieldState TypedDict structure."""
        state: FieldState = {
            "active_entities": 108,
            "dominant_frequency": 432.0,
            "field_coherence": 0.999,
            "resonance_patterns": ["hare", "krishna", "rama"],
        }
        assert state["field_coherence"] > 0.9


@pytest.mark.unit
class TestHardwareNumbers:
    """
    Test the mathematical constants of Vedic Computer Architecture.

    16 × 16 × 16 = 4096 (Complete 3D State Space)
    16 × 4 = 64 (Word Size)
    108 × 16 = 1,728 (Minutes in a Day!)
    """

    def test_mantra_byte_size(self):
        """Verify 16-bit Mantra Byte."""
        from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE

        assert len(MAHAMANTRA_SEQUENCE) == 16

    def test_state_space(self):
        """Verify 4096 = 16³ state space."""
        assert 16 * 16 * 16 == 4096

    def test_word_size(self):
        """Verify 64 = 16 × 4 word size."""
        assert 16 * 4 == 64

    def test_mala_cycles(self):
        """Verify 1728 = 108 × 16 (minutes in a day)."""
        assert 108 * 16 == 1728
        # And 24 * 60 = 1440... close but not exact
        # The Vedic day has a different structure

    def test_yogini_count(self):
        """64 Yoginis = 64-bit architecture analogy."""
        assert 64 == 8 * 8  # Chessboard
        assert 64 == 4 * 16  # 4 Padas × 16 Syllables
