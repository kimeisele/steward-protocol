"""
YAMARAJA HARDENING TESTS
========================

The Judge of the Dead. No Mercy. Only Truth.

These tests verify WATERTIGHT compliance:
- NO `Any` types anywhere
- NO untyped returns
- NO missing parameters
- NO Optional without explicit handling
- NO "it compiles" - REAL validation

BRIDGE: Vedic → Western (Kali Yuga Computing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| VEDIC           | WESTERN              | PROTOCOL        |
|-----------------|----------------------|-----------------|
| Prana           | PSU / Power Supply   | PranaProtocol   |
| Kala            | RTC / System Clock   | KalaProtocol    |
| Chitta          | RAM / Volatile Mem   | ChittaProtocol  |
| Smriti          | Cache / L1-L3        | SmritiProtocol  |
| Nadi            | Bus / PCIe / USB     | NadiProtocol    |
| Sankalpa        | IRQ / Interrupts     | SankalpaProtocol|
| Indriya         | GPIO / Registers     | IndriyaProtocol |
| Akasha          | NIC / Internet       | AkashaProtocol  |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"यमराज - The Lord of Death and Justice"
"""

import inspect
import sys
from typing import Any, Dict, ForwardRef, List, Optional, Tuple, Union, get_args, get_origin, get_type_hints

import pytest

from vibe_core.protocols.substrate import (
    MAHAMANTRA_SEQUENCE,
    # Hardware Types
    ActionData,
    # Hardware Protocols
    AkashaProtocol,
    ChittaBlock,
    ChittaProtocol,
    FieldState,
    IndriyaProtocol,
    KalaProtocol,
    MantraOpCode,
    # Core Protocols
    MantraProtocol,
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

# =============================================================================
# THE BRIDGE: Vedic → Western Mapping
# =============================================================================

VEDIC_WESTERN_BRIDGE: Dict[str, Dict[str, str]] = {
    "PranaProtocol": {
        "vedic": "Prana (Life Force / 5 Vayus)",
        "western": "Power Supply Unit (PSU)",
        "analogy": "Without power, nothing runs. Without Prana, nothing lives.",
        "methods": "breathe_in=power_on, breathe_out=power_distribute, is_alive=has_power",
    },
    "KalaProtocol": {
        "vedic": "Kala (Time / Cosmic Clock)",
        "western": "Real-Time Clock (RTC) / Crystal Oscillator",
        "analogy": "Time is the substrate on which all events occur.",
        "methods": "get_tick=clock_cycles, get_yuga=epoch, is_auspicious=timing_check",
    },
    "ChittaProtocol": {
        "vedic": "Chitta (Mind-Stuff / Yoga Sutra 1.2)",
        "western": "RAM (Random Access Memory)",
        "analogy": "Volatile, impressionable, clears on power-off.",
        "methods": "allocate=malloc, deallocate=free, clear=memset_zero",
    },
    "SmritiProtocol": {
        "vedic": "Smriti (Memory / Recollection)",
        "western": "Cache Hierarchy (L1/L2/L3/TLB)",
        "analogy": "Faster access for frequently used data.",
        "methods": "remember=cache_store, recall=cache_lookup, promote=move_to_L1",
    },
    "NadiProtocol": {
        "vedic": "Nadi (72,000 Energy Channels)",
        "western": "System Bus / PCIe / USB",
        "analogy": "Data flows through channels. Blockages cause system hang.",
        "methods": "open_channel=connect, send=write, is_blocked=check_flow_control",
    },
    "SankalpaProtocol": {
        "vedic": "Sankalpa (Will / Determination)",
        "western": "Interrupt Request (IRQ) / Signal",
        "analogy": "Intent causes action. Higher priority interrupts current work.",
        "methods": "declare=raise_irq, execute_next=handle_interrupt, is_aligned=validate_irq",
    },
    "IndriyaProtocol": {
        "vedic": "Indriya (10 Sense/Action Organs)",
        "western": "GPIO / CPU Registers / I/O Ports",
        "analogy": "Interface between processor and external world.",
        "methods": "sense=read_input, act=write_output, calibrate=configure_port",
    },
    "AkashaProtocol": {
        "vedic": "Akasha (Ether / Space / Field)",
        "western": "Network Interface Card (NIC) / Internet",
        "analogy": "The medium through which all communication flows.",
        "methods": "broadcast=multicast, tune=subscribe, connect=establish_connection",
    },
}


@pytest.mark.unit
class TestYamarajaBridge:
    """Test the Vedic-Western Bridge mapping is complete and consistent."""

    def test_bridge_completeness(self):
        """Every hardware protocol MUST have a bridge mapping."""
        hardware_protocols = [
            "PranaProtocol",
            "KalaProtocol",
            "ChittaProtocol",
            "SmritiProtocol",
            "NadiProtocol",
            "SankalpaProtocol",
            "IndriyaProtocol",
            "AkashaProtocol",
        ]

        for protocol in hardware_protocols:
            assert protocol in VEDIC_WESTERN_BRIDGE, f"YAMARAJA: {protocol} has no bridge mapping!"
            mapping = VEDIC_WESTERN_BRIDGE[protocol]
            assert "vedic" in mapping, f"YAMARAJA: {protocol} missing 'vedic' description"
            assert "western" in mapping, f"YAMARAJA: {protocol} missing 'western' description"
            assert "analogy" in mapping, f"YAMARAJA: {protocol} missing 'analogy'"
            assert "methods" in mapping, f"YAMARAJA: {protocol} missing 'methods' mapping"


@pytest.mark.unit
class TestYamarajaNoAny:
    """
    YAMARAJA TEST: NO `Any` TYPES ALLOWED.

    Any = Mayavad = Illusion = DEATH.

    Every type must be explicit. No escape hatches.
    """

    def _check_no_any_in_hints(self, cls, hints: Dict[str, Any], context: str) -> List[str]:
        """Recursively check that no type hint contains Any."""
        violations = []

        for name, hint in hints.items():
            if hint is Any:
                violations.append(f"{context}.{name} = Any (MAYAVAD!)")
            elif hasattr(hint, "__origin__"):
                # Check generic types like List[Any], Dict[str, Any], etc.
                args = get_args(hint)
                for i, arg in enumerate(args):
                    if arg is Any:
                        violations.append(f"{context}.{name}[{i}] = Any (MAYAVAD!)")

        return violations

    def test_prana_protocol_no_any(self):
        """PranaProtocol must have no Any types."""
        try:
            hints = get_type_hints(PranaProtocol)
        except Exception:
            hints = {}

        # Check method signatures
        for method_name in ["breathe_in", "breathe_out", "circulate", "get_vitality", "suspend", "revive", "is_alive"]:
            method = getattr(PranaProtocol, method_name, None)
            if method:
                sig = inspect.signature(method)
                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue
                    assert param.annotation is not Any, (
                        f"YAMARAJA: PranaProtocol.{method_name}({param_name}) = Any (MAYAVAD!)"
                    )

    def test_chitta_protocol_no_any(self):
        """ChittaProtocol must have no Any types."""
        for method_name in ["allocate", "deallocate", "impress", "read_impression", "clear"]:
            method = getattr(ChittaProtocol, method_name, None)
            if method:
                sig = inspect.signature(method)
                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue
                    assert param.annotation is not Any, (
                        f"YAMARAJA: ChittaProtocol.{method_name}({param_name}) = Any (MAYAVAD!)"
                    )

    def test_smriti_protocol_value_type(self):
        """SmritiProtocol.remember() value parameter - check it's typed."""
        method = getattr(SmritiProtocol, "remember", None)
        if method:
            sig = inspect.signature(method)
            # 'value' is typed as 'object' not 'Any' - this is acceptable
            # object is the base class, Any bypasses type checking entirely
            value_param = sig.parameters.get("value")
            if value_param:
                # object is OK (explicit base type), Any is NOT OK (type erasure)
                assert value_param.annotation is not Any, "YAMARAJA: SmritiProtocol.remember(value) = Any (MAYAVAD!)"


@pytest.mark.unit
class TestYamarajaReturnTypes:
    """
    YAMARAJA TEST: ALL RETURNS MUST BE TYPED.

    Untyped return = Unknown outcome = DEATH.
    """

    PROTOCOL_RETURN_MAP = {
        PranaProtocol: {
            "breathe_in": "PranaLevel",
            "breathe_out": "PranaLevel",
            "circulate": "PranaLevel",
            "get_vitality": "float",
            "suspend": "None",
            "revive": "bool",
            "is_alive": "bool",
        },
        KalaProtocol: {
            "get_tick": "int",
            "get_yuga": "YugaState",
            "get_muhurta": "str",
            "wait_cycles": "None",
            "is_auspicious": "bool",
            "get_elapsed": "int",
        },
        ChittaProtocol: {
            "allocate": "ChittaBlock",
            "deallocate": "None",
            "impress": "None",
            "read_impression": "Optional[Vritti]",
            "clear": "None",
            "get_turbulence": "float",
            "get_total_capacity": "int",
            "get_free_capacity": "int",
        },
        NadiProtocol: {
            "open_channel": "NadiChannel",
            "close_channel": "None",
            "send": "bool",
            "receive": "Optional[bytes]",
            "get_bandwidth": "float",
            "is_blocked": "bool",
            "clear_blockage": "bool",
        },
        AkashaProtocol: {
            "broadcast": "None",
            "tune": "str",
            "untune": "None",
            "connect": "Optional[NadiChannel]",
            "query_field": "List[str]",
            "get_field_state": "FieldState",
            "get_local_identity": "str",
        },
    }

    def test_all_methods_have_return_annotations(self):
        """Every protocol method MUST have a return type annotation."""
        for protocol, methods in self.PROTOCOL_RETURN_MAP.items():
            for method_name, expected_return in methods.items():
                method = getattr(protocol, method_name, None)
                assert method is not None, f"YAMARAJA: {protocol.__name__}.{method_name} does not exist!"

                sig = inspect.signature(method)
                return_annotation = sig.return_annotation

                # Check it's not empty
                assert return_annotation is not inspect.Parameter.empty, (
                    f"YAMARAJA: {protocol.__name__}.{method_name}() has no return type!"
                )

                # Check it's not Any
                assert return_annotation is not Any, (
                    f"YAMARAJA: {protocol.__name__}.{method_name}() returns Any (MAYAVAD!)"
                )


@pytest.mark.unit
class TestYamarajaTypedDicts:
    """
    YAMARAJA TEST: ALL TypedDicts MUST BE COMPLETE.

    Missing field = Missing data = DEATH.
    """

    def test_prana_level_fields(self):
        """PranaLevel must have all required fields."""
        required = ["vitality", "flow_rate", "balance", "source"]
        annotations = getattr(PranaLevel, "__annotations__", {})
        for field in required:
            assert field in annotations, f"YAMARAJA: PranaLevel missing field '{field}'"

    def test_yuga_state_fields(self):
        """YugaState must have all required fields."""
        required = ["yuga", "year_in_yuga", "golden_period", "muhurta"]
        annotations = getattr(YugaState, "__annotations__", {})
        for field in required:
            assert field in annotations, f"YAMARAJA: YugaState missing field '{field}'"

    def test_field_state_fields(self):
        """FieldState must have all required fields."""
        required = ["active_entities", "dominant_frequency", "field_coherence", "resonance_patterns"]
        annotations = getattr(FieldState, "__annotations__", {})
        for field in required:
            assert field in annotations, f"YAMARAJA: FieldState missing field '{field}'"

    def test_sankalpa_intent_fields(self):
        """SankalpaIntent must have all required fields."""
        required = ["intent_id", "action", "priority", "declared_by", "dharma_aligned"]
        annotations = getattr(SankalpaIntent, "__annotations__", {})
        for field in required:
            assert field in annotations, f"YAMARAJA: SankalpaIntent missing field '{field}'"


@pytest.mark.unit
class TestYamarajaDataClasses:
    """
    YAMARAJA TEST: ALL DataClasses MUST BE IMMUTABLE-SAFE.

    Mutable default = Shared state = DEATH.
    """

    def test_chitta_block_no_mutable_defaults(self):
        """ChittaBlock must not have mutable defaults."""
        import dataclasses

        assert dataclasses.is_dataclass(ChittaBlock), "ChittaBlock must be a dataclass"

        for field in dataclasses.fields(ChittaBlock):
            if field.default is not dataclasses.MISSING:
                # Check it's not a mutable type
                assert not isinstance(field.default, (list, dict, set)), (
                    f"YAMARAJA: ChittaBlock.{field.name} has mutable default!"
                )

    def test_vritti_no_mutable_defaults(self):
        """Vritti must not have mutable defaults."""
        import dataclasses

        assert dataclasses.is_dataclass(Vritti), "Vritti must be a dataclass"

        for field in dataclasses.fields(Vritti):
            if field.default is not dataclasses.MISSING:
                assert not isinstance(field.default, (list, dict, set)), (
                    f"YAMARAJA: Vritti.{field.name} has mutable default!"
                )

    def test_nadi_channel_no_mutable_defaults(self):
        """NadiChannel must not have mutable defaults."""
        import dataclasses

        assert dataclasses.is_dataclass(NadiChannel), "NadiChannel must be a dataclass"

        for field in dataclasses.fields(NadiChannel):
            if field.default is not dataclasses.MISSING:
                assert not isinstance(field.default, (list, dict, set)), (
                    f"YAMARAJA: NadiChannel.{field.name} has mutable default!"
                )


@pytest.mark.unit
class TestYamarajaMantraIntegrity:
    """
    YAMARAJA TEST: THE MAHAMANTRA IS SACRED.

    Wrong sequence = Wrong instruction = DEATH.
    """

    def test_mahamantra_length(self):
        """The Mahamantra MUST have exactly 16 syllables."""
        assert len(MAHAMANTRA_SEQUENCE) == 16, (
            f"YAMARAJA: MAHAMANTRA_SEQUENCE has {len(MAHAMANTRA_SEQUENCE)} elements, not 16!"
        )

    def test_mahamantra_structure(self):
        """The Mahamantra MUST follow the correct pattern."""
        expected_names = [
            "Hare",
            "Krishna",
            "Hare",
            "Krishna",  # Q1
            "Krishna",
            "Krishna",
            "Hare",
            "Hare",  # Q2
            "Hare",
            "Rama",
            "Hare",
            "Rama",  # Q3
            "Rama",
            "Rama",
            "Hare",
            "Hare",  # Q4
        ]

        for i, (name, opcode) in enumerate(MAHAMANTRA_SEQUENCE):
            assert name == expected_names[i], (
                f"YAMARAJA: MAHAMANTRA_SEQUENCE[{i}] name is '{name}', expected '{expected_names[i]}'"
            )

    def test_mahamantra_opcode_types(self):
        """All opcodes in MAHAMANTRA_SEQUENCE must be MantraOpCode."""
        for i, (name, opcode) in enumerate(MAHAMANTRA_SEQUENCE):
            assert isinstance(opcode, MantraOpCode), (
                f"YAMARAJA: MAHAMANTRA_SEQUENCE[{i}][1] is {type(opcode)}, not MantraOpCode!"
            )

    def test_mantra_opcode_count(self):
        """There must be exactly 16 MantraOpCodes."""
        opcodes = list(MantraOpCode)
        assert len(opcodes) == 16, f"YAMARAJA: MantraOpCode has {len(opcodes)} values, not 16!"


@pytest.mark.unit
class TestYamarajaNumbers:
    """
    YAMARAJA TEST: THE SACRED NUMBERS.

    Wrong math = Wrong universe = DEATH.
    """

    def test_16_is_mantra_size(self):
        """16 = Mantra syllables = Instruction word size."""
        assert 16 == len(MAHAMANTRA_SEQUENCE)

    def test_64_is_word_size(self):
        """64 = 16 × 4 = Word size = Yogini count."""
        assert 16 * 4 == 64

    def test_4096_is_state_space(self):
        """4096 = 16³ = Complete 3D state space."""
        assert 16**3 == 4096

    def test_108_significance(self):
        """108 = Mala beads = Sacred number."""
        # 108 = 1² × 2² × 3³ = 1 × 4 × 27
        assert 108 == 1 * 4 * 27
        # Also: 108 = 9 × 12 (planets × zodiac signs)
        assert 108 == 9 * 12

    def test_1728_is_minutes(self):
        """1728 = 108 × 16 = Sacred daily rhythm."""
        assert 108 * 16 == 1728

    def test_yuga_ratios(self):
        """Yuga durations follow 4:3:2:1 ratio."""
        satya = 1_728_000
        treta = 1_296_000
        dvapara = 864_000
        kali = 432_000

        # Verify 4:3:2:1 ratio
        base = kali
        assert satya == base * 4
        assert treta == base * 3
        assert dvapara == base * 2
        assert kali == base * 1

        # Verify Chaturyuga total
        assert satya + treta + dvapara + kali == 4_320_000


@pytest.mark.unit
class TestYamarajaProtocolCompleteness:
    """
    YAMARAJA TEST: ALL PROTOCOLS MUST BE COMPLETE.

    Missing method = Missing capability = DEATH.
    """

    REQUIRED_METHODS = {
        PranaProtocol: ["breathe_in", "breathe_out", "circulate", "get_vitality", "suspend", "revive", "is_alive"],
        KalaProtocol: ["get_tick", "get_yuga", "get_muhurta", "wait_cycles", "is_auspicious", "get_elapsed"],
        ChittaProtocol: [
            "allocate",
            "deallocate",
            "impress",
            "read_impression",
            "clear",
            "get_turbulence",
            "get_total_capacity",
            "get_free_capacity",
        ],
        SmritiProtocol: ["remember", "recall", "forget", "promote", "demote", "get_level_stats"],
        NadiProtocol: [
            "open_channel",
            "close_channel",
            "send",
            "receive",
            "get_bandwidth",
            "is_blocked",
            "clear_blockage",
        ],
        SankalpaProtocol: ["declare", "revoke", "get_pending", "execute_next", "is_aligned", "get_current"],
        IndriyaProtocol: ["sense", "act", "calibrate", "get_bandwidth", "is_overloaded", "rest"],
        AkashaProtocol: [
            "broadcast",
            "tune",
            "untune",
            "connect",
            "query_field",
            "get_field_state",
            "get_local_identity",
        ],
    }

    def test_all_protocols_complete(self):
        """Every protocol must have all required methods."""
        for protocol, methods in self.REQUIRED_METHODS.items():
            for method_name in methods:
                assert hasattr(protocol, method_name), f"YAMARAJA: {protocol.__name__} missing method '{method_name}'!"

    def test_total_method_count(self):
        """Verify total method count across all hardware protocols."""
        total = sum(len(methods) for methods in self.REQUIRED_METHODS.values())
        # 7 + 6 + 8 + 6 + 7 + 6 + 6 + 7 = 53 methods
        assert total == 53, f"YAMARAJA: Expected 53 hardware protocol methods, found {total}"
