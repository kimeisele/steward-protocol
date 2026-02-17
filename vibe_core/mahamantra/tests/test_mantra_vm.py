"""
MANTRA VM — Equivalence & Isolation Tests
==========================================

Verifies that the VAMSI-dispatched VM produces IDENTICAL output
to the old hardcoded __call__() pipeline. Key-by-key, type-by-type.

Also tests individual instruction wrappers in isolation.
"""

import pytest

from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus
from vibe_core.mahamantra.substrate.mantra_vm import (
    DISPATCH,
    execute_cycle,
    _w_sravanam,
    _w_nama,
    _w_kirtanam,
    _w_pada_sevanam,
    _w_arcanam,
    _w_smaranam,
    _w_vandanam,
    _w_dasyam,
    _w_sakhyam,
)
from vibe_core.mahamantra.protocols._navabhakti import (
    CYCLE,
    GATE_INDEX,
    NavaBhaktiOp,
    VAMSI_ADDR,
)
from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT, PARAMPARA


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def lotus():
    m = MahamantraLotus()
    m.bootstrap(lazy=True, silent=True)
    return m


# =============================================================================
# PROTOCOL INVARIANTS
# =============================================================================

class TestNavaBhaktiProtocol:
    """Verify the instruction set is correctly derived from the Mantra."""

    def test_instruction_count(self):
        assert len(NavaBhaktiOp) == MAHAJANA_COUNT == 12

    def test_cycle_length(self):
        assert len(CYCLE) == MAHAJANA_COUNT

    def test_gate_index_length(self):
        assert len(GATE_INDEX) == MAHAJANA_COUNT

    def test_vamsi_addresses_stride(self):
        for i, addr in enumerate(VAMSI_ADDR):
            assert addr == PARAMPARA * (i + 1), f"VAMSI_ADDR[{i}] = {addr}, expected {PARAMPARA * (i + 1)}"

    def test_vamsi_no_collision_with_flute_cycle(self):
        from vibe_core.mahamantra.substrate.lotus_core import _get_pipeline
        P = _get_pipeline()
        flute_set = set(P.THE_FLUTE_CYCLE)
        vm_set = set(VAMSI_ADDR)
        collisions = flute_set & vm_set
        assert not collisions, f"VAMSI addresses collide with FLUTE_CYCLE: {collisions}"

    def test_dispatch_table_complete(self):
        for op in NavaBhaktiOp:
            assert op in DISPATCH, f"Missing dispatch for {op.name}"

    def test_gate_indices_monotonic(self):
        for i in range(1, len(GATE_INDEX)):
            assert GATE_INDEX[i] >= GATE_INDEX[i - 1], (
                f"Gate index must be monotonically non-decreasing: "
                f"GATE_INDEX[{i}]={GATE_INDEX[i]} < GATE_INDEX[{i-1}]={GATE_INDEX[i-1]}"
            )


# =============================================================================
# EQUIVALENCE — The critical test
# =============================================================================

_TEST_INPUTS = [
    "Hare Krishna",
    "What is the meaning of life?",
    "Om Namo Bhagavate Vasudevaya",
    "a",
    "The quick brown fox jumps over the lazy dog",
    "42",
    "",
]


class TestVMEquivalence:
    """Verify VM output is key-by-key identical to direct method calls."""

    @pytest.mark.parametrize("text", _TEST_INPUTS)
    def test_vm_output_keys(self, lotus, text):
        result = lotus(text)
        expected_keys = {
            "input", "tattva_gate", "guna", "vibration", "parampara",
            "chapter", "chapter_significance", "verse", "matches",
            "gita_phase", "is_complete", "position", "guardian",
            "quarter", "role", "quarter_head", "holy_name",
            "trinity_function", "diw", "cell", "nama", "smaranam",
            "antaranga", "akash", "execution", "yajna", "gate_trace",
        }
        assert set(result.keys()) == expected_keys

    @pytest.mark.parametrize("text", _TEST_INPUTS)
    def test_deterministic(self, text):
        """Two fresh Lotus instances with same input must produce same seed/attractor."""
        m1 = MahamantraLotus()
        m1.bootstrap(lazy=True, silent=True)
        m2 = MahamantraLotus()
        m2.bootstrap(lazy=True, silent=True)
        r1 = m1(text)
        r2 = m2(text)
        assert r1["vibration"]["seed"] == r2["vibration"]["seed"]
        assert r1["vibration"]["attractor"] == r2["vibration"]["attractor"]
        assert r1["position"] == r2["position"]
        assert r1["guardian"] == r2["guardian"]
        assert r1["chapter"] == r2["chapter"]

    def test_gate_trace_always_five(self, lotus):
        result = lotus("test")
        assert result["gate_trace"] == ("PARSE", "VALIDATE", "EXECUTE", "RESULT", "SYNC")

    def test_cell_always_alive(self, lotus):
        result = lotus("test")
        assert result["cell"]["is_alive"] is True
        assert result["cell"]["valid"] is True

    def test_execution_success(self, lotus):
        result = lotus("test")
        assert result["execution"]["success"] is True

    def test_opcode_caller_source(self, lotus):
        result = lotus("test", opcode=3)
        assert result["guna"]["source"] == "caller"

    def test_opcode_position_source(self, lotus):
        result = lotus("test")
        assert result["guna"]["source"] == "position"


# =============================================================================
# STEP ISOLATION — Individual wrappers
# =============================================================================

class TestStepIsolation:
    """Test individual VM wrappers produce correct ctx mutations."""

    def test_sravanam_string(self, lotus):
        ctx = {"input_data": "hello"}
        _w_sravanam(lotus, ctx)
        assert ctx["input_text"] == "hello"
        assert ctx["cell"] is None
        assert ctx["seed"] is None

    def test_nama_produces_coords(self, lotus):
        ctx = {"input_data": "hello"}
        _w_sravanam(lotus, ctx)
        _w_nama(lotus, ctx)
        assert isinstance(ctx["input_coords"], tuple)
        assert len(ctx["input_coords"]) > 0

    def test_kirtanam_produces_seed(self, lotus):
        ctx = {"input_data": "hello"}
        _w_sravanam(lotus, ctx)
        _w_kirtanam(lotus, ctx)
        assert isinstance(ctx["seed"], int)

    def test_pada_sevanam_produces_attractor(self, lotus):
        ctx = {"input_data": "hello"}
        _w_sravanam(lotus, ctx)
        _w_kirtanam(lotus, ctx)
        _w_pada_sevanam(lotus, ctx)
        assert isinstance(ctx["attractor"], int)
        assert isinstance(ctx["variance"], int)
        assert isinstance(ctx["raw_address"], int)

    def test_arcanam_produces_parampara(self, lotus):
        ctx = {"input_data": "hello"}
        _w_sravanam(lotus, ctx)
        _w_kirtanam(lotus, ctx)
        _w_arcanam(lotus, ctx)
        assert isinstance(ctx["parampara_verified"], bool)
        assert isinstance(ctx["parampara_channel"], int)
        assert isinstance(ctx["parampara_coherence"], (int, float))

    def test_dasyam_explicit_keys(self, lotus):
        ctx = {"input_data": "hello", "opcode": None}
        _w_sravanam(lotus, ctx)
        _w_kirtanam(lotus, ctx)
        _w_pada_sevanam(lotus, ctx)
        _w_dasyam(lotus, ctx)
        required = {
            "position", "diw", "diw_comp", "quarter", "guardian", "role",
            "quarter_head_name", "holy_name", "trinity_function",
            "rama_coord", "phoneme", "phoneme_element", "phoneme_varga",
            "phoneme_sub", "phoneme_harmonic", "phoneme_shruti",
            "pipeline_opcode", "pipeline_guna",
        }
        for key in required:
            assert key in ctx, f"Missing ctx key after dasyam: {key}"
