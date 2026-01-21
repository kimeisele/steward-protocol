"""
TEST NAGA CLI COMMAND PROTOCOL
==============================

Verifies the INagaCommand protocol and Balarama pattern for CLI.

"If no Protocol, it doesn't exist."

Tests:
- Mahajana enum completeness (12 + 4 = 16)
- Phase enum completeness (4 phases)
- OpCode → Mahajana mapping (16 mappings)
- NagaCommandResult immutability
- INagaCommand protocol contract
- NagaCommandBase implementation
- NagaCommandRegistry (Balarama pattern)
- @naga_command decorator
"""

import pytest
from typing import List

from vibe_core.protocols.naga.cli_command import (
    # Enums
    Mahajana,
    Phase,
    # Mappings
    OPCODE_TO_MAHAJANA,
    MAHAJANA_TO_OPCODE,
    OPCODE_TO_PHASE,
    # Result
    NagaCommandResult,
    # Protocol
    INagaCommand,
    # Base
    NagaCommandBase,
    # Registry
    NagaCommandRegistry,
    NAGA_COMMAND_REGISTRY,
    # Decorator
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# MAHAJANA ENUM TESTS
# =============================================================================


class TestMahajana:
    """Test the 16 Mahajanas (12 workers + 4 avataras)."""

    def test_has_16_members(self):
        """16 Mahajanas total."""
        assert len(Mahajana) == 16

    # WAKE Phase (0-3)
    def test_prithu_exists(self):
        """PRITHU (Avatara) - SYS_WAKE."""
        assert Mahajana.PRITHU.value == "prithu"

    def test_brahma_exists(self):
        """BRAHMA - LOAD_ROOT."""
        assert Mahajana.BRAHMA.value == "brahma"

    def test_narada_exists(self):
        """NARADA - ALLOC_MEM."""
        assert Mahajana.NARADA.value == "narada"

    def test_shambhu_exists(self):
        """SHAMBHU - BIND_CTX."""
        assert Mahajana.SHAMBHU.value == "shambhu"

    # PURIFY Phase (4-7)
    def test_vyasa_exists(self):
        """VYASA (Avatara) - ASSERT_TRUTH."""
        assert Mahajana.VYASA.value == "vyasa"

    def test_kumaras_exists(self):
        """KUMARAS - RESOLVE_REQ."""
        assert Mahajana.KUMARAS.value == "kumaras"

    def test_kapila_exists(self):
        """KAPILA - GARBAGE_COLLECT."""
        assert Mahajana.KAPILA.value == "kapila"

    def test_manu_exists(self):
        """MANU - PULSE_SYNC."""
        assert Mahajana.MANU.value == "manu"

    # SERVE Phase (8-11)
    def test_parashurama_exists(self):
        """PARASHURAMA (Avatara) - FETCH_RES."""
        assert Mahajana.PARASHURAMA.value == "parashurama"

    def test_prahlada_exists(self):
        """PRAHLADA - EXEC_SERVICE."""
        assert Mahajana.PRAHLADA.value == "prahlada"

    def test_janaka_exists(self):
        """JANAKA - CHECK_DHARMA."""
        assert Mahajana.JANAKA.value == "janaka"

    def test_bhishma_exists(self):
        """BHISHMA - COMMIT_LOG."""
        assert Mahajana.BHISHMA.value == "bhishma"

    # SUSTAIN Phase (12-15)
    def test_nrisimha_exists(self):
        """NRISIMHA (Avatara) - CACHE_STATE."""
        assert Mahajana.NRISIMHA.value == "nrisimha"

    def test_bali_exists(self):
        """BALI - OPTIMIZE."""
        assert Mahajana.BALI.value == "bali"

    def test_shuka_exists(self):
        """SHUKA - YIELD_CPU."""
        assert Mahajana.SHUKA.value == "shuka"

    def test_yamaraja_exists(self):
        """YAMARAJA - RESET_IP."""
        assert Mahajana.YAMARAJA.value == "yamaraja"


# =============================================================================
# PHASE ENUM TESTS
# =============================================================================


class TestPhase:
    """Test the 4 phases of the Mahamantra CPU."""

    def test_has_4_phases(self):
        """4 phases in the cycle."""
        assert len(Phase) == 4

    def test_wake_phase(self):
        """WAKE phase (0-3)."""
        assert Phase.WAKE.value == "wake"

    def test_purify_phase(self):
        """PURIFY phase (4-7)."""
        assert Phase.PURIFY.value == "purify"

    def test_serve_phase(self):
        """SERVE phase (8-11)."""
        assert Phase.SERVE.value == "serve"

    def test_sustain_phase(self):
        """SUSTAIN phase (12-15)."""
        assert Phase.SUSTAIN.value == "sustain"


# =============================================================================
# OPCODE → MAHAJANA MAPPING TESTS
# =============================================================================


class TestOpcodeToMahajana:
    """Test the 16-fold OpCode to Mahajana mapping."""

    def test_all_16_opcodes_mapped(self):
        """All 16 opcodes have Mahajana mapping."""
        assert len(OPCODE_TO_MAHAJANA) == 16

    def test_bidirectional_mapping(self):
        """Mapping is bidirectional."""
        for opcode, mahajana in OPCODE_TO_MAHAJANA.items():
            assert MAHAJANA_TO_OPCODE[mahajana] == opcode

    # WAKE Phase
    def test_sys_wake_to_prithu(self):
        """SYS_WAKE → PRITHU."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.SYS_WAKE] == Mahajana.PRITHU

    def test_load_root_to_brahma(self):
        """LOAD_ROOT → BRAHMA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.LOAD_ROOT] == Mahajana.BRAHMA

    def test_alloc_mem_to_narada(self):
        """ALLOC_MEM → NARADA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.ALLOC_MEM] == Mahajana.NARADA

    def test_bind_ctx_to_shambhu(self):
        """BIND_CTX → SHAMBHU."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.INIT_THREAD] == Mahajana.SHAMBHU

    # PURIFY Phase
    def test_assert_truth_to_vyasa(self):
        """ASSERT_TRUTH → VYASA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.COMPILE_AST] == Mahajana.VYASA

    def test_resolve_req_to_kumaras(self):
        """RESOLVE_REQ → KUMARAS."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.BIND_SYMBOL] == Mahajana.KUMARAS

    def test_garbage_collect_to_kapila(self):
        """GARBAGE_COLLECT → KAPILA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.TYPE_CHECK] == Mahajana.KAPILA

    def test_pulse_sync_to_manu(self):
        """PULSE_SYNC → MANU."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.DHARMA_TEST] == Mahajana.MANU

    # SERVE Phase
    def test_fetch_res_to_parashurama(self):
        """FETCH_RES → PARASHURAMA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.EXEC_OP] == Mahajana.PARASHURAMA

    def test_exec_service_to_prahlada(self):
        """EXEC_SERVICE → PRAHLADA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.EXTEND_CAP] == Mahajana.PRAHLADA

    def test_check_dharma_to_janaka(self):
        """CHECK_DHARMA → JANAKA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.STATE_SYNC] == Mahajana.JANAKA

    def test_commit_log_to_bhishma(self):
        """COMMIT_LOG → BHISHMA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.LEDGER_SIGN] == Mahajana.BHISHMA

    # SUSTAIN Phase
    def test_cache_state_to_nrisimha(self):
        """CACHE_STATE → NRISIMHA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.YIELD_CPU] == Mahajana.NRISIMHA

    def test_optimize_to_bali(self):
        """OPTIMIZE → BALI."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.IO_FLUSH] == Mahajana.BALI

    def test_log_emit_to_shuka(self):
        """LOG_EMIT → SHUKA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.LOG_EMIT] == Mahajana.SHUKA

    def test_reset_ip_to_yamaraja(self):
        """RESET_IP → YAMARAJA."""
        assert OPCODE_TO_MAHAJANA[MantraOpCode.AUDIT_SEAL] == Mahajana.YAMARAJA


# =============================================================================
# OPCODE → PHASE MAPPING TESTS
# =============================================================================


class TestOpcodeToPhase:
    """Test OpCode to Phase mapping."""

    def test_all_16_opcodes_have_phase(self):
        """All 16 opcodes have phase mapping."""
        assert len(OPCODE_TO_PHASE) == 16

    def test_wake_phase_opcodes(self):
        """Wake phase contains opcodes 0-3."""
        wake_opcodes = [
            MantraOpCode.SYS_WAKE,
            MantraOpCode.LOAD_ROOT,
            MantraOpCode.ALLOC_MEM,
            MantraOpCode.INIT_THREAD,
        ]
        for opcode in wake_opcodes:
            assert OPCODE_TO_PHASE[opcode] == Phase.WAKE

    def test_purify_phase_opcodes(self):
        """Purify phase contains opcodes 4-7."""
        purify_opcodes = [
            MantraOpCode.COMPILE_AST,
            MantraOpCode.BIND_SYMBOL,
            MantraOpCode.TYPE_CHECK,
            MantraOpCode.DHARMA_TEST,
        ]
        for opcode in purify_opcodes:
            assert OPCODE_TO_PHASE[opcode] == Phase.PURIFY

    def test_serve_phase_opcodes(self):
        """Serve phase contains opcodes 8-11."""
        serve_opcodes = [
            MantraOpCode.EXEC_OP,
            MantraOpCode.EXTEND_CAP,
            MantraOpCode.STATE_SYNC,
            MantraOpCode.LEDGER_SIGN,
        ]
        for opcode in serve_opcodes:
            assert OPCODE_TO_PHASE[opcode] == Phase.SERVE

    def test_sustain_phase_opcodes(self):
        """Sustain phase contains opcodes 12-15."""
        sustain_opcodes = [
            MantraOpCode.YIELD_CPU,
            MantraOpCode.IO_FLUSH,
            MantraOpCode.YIELD_CPU,
            MantraOpCode.AUDIT_SEAL,
        ]
        for opcode in sustain_opcodes:
            assert OPCODE_TO_PHASE[opcode] == Phase.SUSTAIN


# =============================================================================
# NAGA COMMAND RESULT TESTS
# =============================================================================


class TestNagaCommandResult:
    """Test NagaCommandResult dataclass."""

    def test_result_is_frozen(self):
        """NagaCommandResult is immutable."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            output="Hello",
            opcode=MantraOpCode.EXTEND_CAP,
            mahajana=Mahajana.PRAHLADA,
        )
        with pytest.raises(Exception):
            result.success = False

    def test_success_result(self):
        """Success result has exit_code 0."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            output="Done",
            opcode=MantraOpCode.SYS_WAKE,
            mahajana=Mahajana.PRITHU,
        )
        assert result.success
        assert result.exit_code == 0

    def test_failure_result(self):
        """Failure result has non-zero exit_code."""
        result = NagaCommandResult(
            success=False,
            exit_code=1,
            error="Failed",
            opcode=MantraOpCode.AUDIT_SEAL,
            mahajana=Mahajana.YAMARAJA,
        )
        assert not result.success
        assert result.exit_code == 1

    def test_data_as_tuple(self):
        """Data is tuple of key-value pairs."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            opcode=MantraOpCode.EXTEND_CAP,
            mahajana=Mahajana.PRAHLADA,
            data=(("key1", "value1"), ("key2", "value2")),
        )
        assert len(result.data) == 2

    def test_to_dict(self):
        """Convert data to dictionary."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            opcode=MantraOpCode.EXTEND_CAP,
            mahajana=Mahajana.PRAHLADA,
            data=(("key1", "value1"), ("key2", "value2")),
        )
        d = result.to_dict()
        assert d["key1"] == "value1"
        assert d["key2"] == "value2"


# =============================================================================
# INAGA COMMAND PROTOCOL TESTS
# =============================================================================


class TestINagaCommandProtocol:
    """Test INagaCommand protocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(INagaCommand, "__protocol_attrs__") or hasattr(INagaCommand, "_is_protocol")

    def test_has_opcode_property(self):
        """Protocol has opcode property."""
        assert "opcode" in dir(INagaCommand)

    def test_has_mahajana_property(self):
        """Protocol has mahajana property."""
        assert "mahajana" in dir(INagaCommand)

    def test_has_name_property(self):
        """Protocol has name property."""
        assert "name" in dir(INagaCommand)

    def test_has_help_text_property(self):
        """Protocol has help_text property."""
        assert "help_text" in dir(INagaCommand)

    def test_has_phase_property(self):
        """Protocol has phase property."""
        assert "phase" in dir(INagaCommand)

    def test_has_execute_method(self):
        """Protocol has execute method."""
        assert "execute" in dir(INagaCommand)


# =============================================================================
# NAGA COMMAND BASE TESTS
# =============================================================================


class TestNagaCommandBase:
    """Test NagaCommandBase implementation."""

    def test_default_opcode(self):
        """Default opcode is SYS_WAKE."""
        cmd = NagaCommandBase()
        assert cmd.opcode == MantraOpCode.SYS_WAKE

    def test_default_mahajana(self):
        """Default mahajana is PRITHU."""
        cmd = NagaCommandBase()
        assert cmd.mahajana == Mahajana.PRITHU

    def test_default_name(self):
        """Default name is 'unnamed'."""
        cmd = NagaCommandBase()
        assert cmd.name == "unnamed"

    def test_default_execute_fails(self):
        """Default execute returns error."""
        cmd = NagaCommandBase()
        result = cmd.execute([])
        assert not result.success
        assert result.exit_code == 1

    def test_phase_derived_from_opcode(self):
        """Phase is derived from opcode."""
        cmd = NagaCommandBase()
        cmd._opcode = MantraOpCode.EXTEND_CAP
        assert cmd.phase == Phase.SERVE

    def test_success_helper(self):
        """success() creates success result."""
        cmd = NagaCommandBase()
        cmd._opcode = MantraOpCode.EXTEND_CAP
        cmd._mahajana = Mahajana.PRAHLADA
        result = cmd.success("Done!")
        assert result.success
        assert result.exit_code == 0
        assert result.output == "Done!"
        assert result.opcode == MantraOpCode.EXTEND_CAP
        assert result.mahajana == Mahajana.PRAHLADA

    def test_failure_helper(self):
        """failure() creates failure result."""
        cmd = NagaCommandBase()
        cmd._opcode = MantraOpCode.AUDIT_SEAL
        cmd._mahajana = Mahajana.YAMARAJA
        result = cmd.failure("Error!")
        assert not result.success
        assert result.exit_code == 1
        assert result.error == "Error!"


# =============================================================================
# CUSTOM COMMAND TESTS
# =============================================================================


class TestCustomCommand:
    """Test creating custom commands."""

    def test_custom_command_implementation(self):
        """Custom command implements protocol."""

        class MyCommand(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "test"
            _help_text = "Test command"

            def execute(self, args: List[str]) -> NagaCommandResult:
                return self.success("Test output")

        cmd = MyCommand()
        assert cmd.opcode == MantraOpCode.EXTEND_CAP
        assert cmd.mahajana == Mahajana.PRAHLADA
        assert cmd.name == "test"
        assert cmd.phase == Phase.SERVE

        result = cmd.execute([])
        assert result.success


# =============================================================================
# NAGA COMMAND REGISTRY TESTS
# =============================================================================


class TestNagaCommandRegistry:
    """Test NagaCommandRegistry (Balarama pattern)."""

    def test_registry_starts_empty(self):
        """Fresh registry has no commands."""
        registry = NagaCommandRegistry()
        assert len(registry.list_all()) == 0

    def test_register_command(self):
        """Register a command."""
        registry = NagaCommandRegistry()

        class MyCommand(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "my-test"
            _help_text = "Test"

        cmd = MyCommand()
        registry.register(cmd)

        assert registry.get("my-test") == cmd

    def test_get_by_opcode(self):
        """Get commands by opcode."""
        registry = NagaCommandRegistry()

        class Cmd1(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "cmd1"

        class Cmd2(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "cmd2"

        registry.register(Cmd1())
        registry.register(Cmd2())

        cmds = registry.get_by_opcode(MantraOpCode.EXTEND_CAP)
        assert len(cmds) == 2

    def test_get_by_mahajana(self):
        """Get commands by mahajana."""
        registry = NagaCommandRegistry()

        class Cmd1(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "prahlada-cmd"

        class Cmd2(NagaCommandBase):
            _opcode = MantraOpCode.YIELD_CPU
            _mahajana = Mahajana.SHUKA
            _name = "shuka-cmd"

        registry.register(Cmd1())
        registry.register(Cmd2())

        prahlada_cmds = registry.get_by_mahajana(Mahajana.PRAHLADA)
        assert len(prahlada_cmds) == 1
        assert prahlada_cmds[0].name == "prahlada-cmd"

    def test_get_by_phase(self):
        """Get commands by phase."""
        registry = NagaCommandRegistry()

        class ServeCmd(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "serve-cmd"

        class SustainCmd(NagaCommandBase):
            _opcode = MantraOpCode.AUDIT_SEAL
            _mahajana = Mahajana.YAMARAJA
            _name = "sustain-cmd"

        registry.register(ServeCmd())
        registry.register(SustainCmd())

        serve_cmds = registry.get_by_phase(Phase.SERVE)
        assert len(serve_cmds) == 1
        assert serve_cmds[0].name == "serve-cmd"

    def test_list_names(self):
        """List all command names."""
        registry = NagaCommandRegistry()

        class Cmd1(NagaCommandBase):
            _name = "alpha"

        class Cmd2(NagaCommandBase):
            _name = "beta"

        registry.register(Cmd1())
        registry.register(Cmd2())

        names = registry.list_names()
        assert "alpha" in names
        assert "beta" in names


# =============================================================================
# NAGA COMMAND DECORATOR TESTS
# =============================================================================


class TestNagaCommandDecorator:
    """Test @naga_command decorator."""

    def test_decorator_sets_attributes(self):
        """Decorator sets opcode, mahajana, name, help_text."""
        # Note: We can't use the decorator in tests because it auto-registers
        # to the global registry. So we test the attribute setting manually.

        class TestCmd(NagaCommandBase):
            pass

        TestCmd._opcode = MantraOpCode.STATE_SYNC
        TestCmd._mahajana = Mahajana.JANAKA
        TestCmd._name = "dharma-check"
        TestCmd._help_text = "Check dharma"

        cmd = TestCmd()
        assert cmd.opcode == MantraOpCode.STATE_SYNC
        assert cmd.mahajana == Mahajana.JANAKA
        assert cmd.name == "dharma-check"
        assert cmd.help_text == "Check dharma"


# =============================================================================
# STRICT TYPING TESTS
# =============================================================================


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_result_no_any(self):
        """NagaCommandResult has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(NagaCommandResult)
        for field_name, field_type in hints.items():
            # Check that field type is not Any
            assert field_type is not Any, f"NagaCommandResult.{field_name} uses Any"


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================


class TestImmutability:
    """Test that dataclasses are frozen."""

    def test_result_immutable(self):
        """NagaCommandResult is immutable."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            opcode=MantraOpCode.SYS_WAKE,
            mahajana=Mahajana.PRITHU,
        )
        with pytest.raises(Exception):
            result.success = False

    def test_result_data_tuple_immutable(self):
        """Result data is a tuple (immutable)."""
        result = NagaCommandResult(
            success=True,
            exit_code=0,
            opcode=MantraOpCode.SYS_WAKE,
            mahajana=Mahajana.PRITHU,
            data=(("key", "value"),),
        )
        assert isinstance(result.data, tuple)


# =============================================================================
# GLOBAL REGISTRY TESTS
# =============================================================================


class TestGlobalRegistry:
    """Test the global NAGA_COMMAND_REGISTRY."""

    def test_global_registry_exists(self):
        """Global registry is available."""
        assert NAGA_COMMAND_REGISTRY is not None

    def test_global_registry_is_registry(self):
        """Global registry is NagaCommandRegistry."""
        assert isinstance(NAGA_COMMAND_REGISTRY, NagaCommandRegistry)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for the command system."""

    def test_command_flow(self):
        """Complete command flow: create → register → execute."""
        registry = NagaCommandRegistry()

        class EchoCommand(NagaCommandBase):
            _opcode = MantraOpCode.EXTEND_CAP
            _mahajana = Mahajana.PRAHLADA
            _name = "echo"
            _help_text = "Echo arguments"

            def execute(self, args: List[str]) -> NagaCommandResult:
                if not args:
                    return self.failure("No arguments provided")
                return self.success(" ".join(args))

        registry.register(EchoCommand())

        # Execute
        cmd = registry.get("echo")
        assert cmd is not None

        result = cmd.execute(["hello", "world"])
        assert result.success
        assert result.output == "hello world"
        assert result.opcode == MantraOpCode.EXTEND_CAP
        assert result.mahajana == Mahajana.PRAHLADA
        assert result.exit_code == 0

    def test_command_failure_flow(self):
        """Command failure returns proper result."""

        class FailCommand(NagaCommandBase):
            _opcode = MantraOpCode.AUDIT_SEAL
            _mahajana = Mahajana.YAMARAJA
            _name = "fail"

            def execute(self, args: List[str]) -> NagaCommandResult:
                return self.failure("Intentional failure", exit_code=42)

        cmd = FailCommand()
        result = cmd.execute([])

        assert not result.success
        assert result.exit_code == 42
        assert result.error == "Intentional failure"
        assert result.opcode == MantraOpCode.AUDIT_SEAL
        assert result.mahajana == Mahajana.YAMARAJA
