"""
Tests for MahaCompression adapter.

Tests seed generation, compression metrics, and architectural correctness.

NOTE: MahaCompression does NOT classify intent from text content.
Guna is a property of PRAKRITI (OpCode), not KSHETRA (data).
See substrate/guna.py: "The Guna is DERIVED from the OpCode, not decorated."
"""

import pytest
from vibe_core.mahamantra.adapters import MahaCompression, IntentGuna


class TestMahaCompression:
    """Test suite for MahaCompression."""

    @pytest.fixture
    def compressor(self):
        """Create compressor instance."""
        return MahaCompression()

    # =========================================================================
    # BASIC FUNCTIONALITY
    # =========================================================================

    def test_compress_returns_result(self, compressor):
        """Compress should return a CompressionResult."""
        result = compressor.compress("Hello world")
        assert result is not None
        assert result.seed is not None
        assert result.input_size > 0

    def test_compress_deterministic(self, compressor):
        """Same input should produce same seed."""
        text = "The quick brown fox"
        result1 = compressor.compress(text)
        result2 = compressor.compress(text)
        assert result1.seed == result2.seed

    def test_compress_different_inputs(self, compressor):
        """Different inputs should produce different seeds."""
        result1 = compressor.compress("Hello")
        result2 = compressor.compress("World")
        assert result1.seed != result2.seed

    # =========================================================================
    # ARCHITECTURAL CORRECTNESS: Compression does NOT classify intent
    # =========================================================================

    def test_no_intent_from_error_text(self, compressor):
        """Compression must NOT classify 'error' text as TAMAS.

        The Guna is DERIVED from the OpCode, not from text content.
        A log line 'ERROR: DB timeout' is not inherently TAMAS.
        - If the system READS it (logging) -> SATTVA
        - If the system KILLS a process -> TAMAS
        """
        result = compressor.compress("ERROR: Database connection failed")
        assert result.intent_level is None

    def test_no_intent_from_success_text(self, compressor):
        """Compression must NOT classify 'success' text as SATTVA."""
        result = compressor.compress("SUCCESS: All tests passed")
        assert result.intent_level is None

    def test_no_intent_from_warning_text(self, compressor):
        """Compression must NOT classify 'warning' text as RAJAS."""
        result = compressor.compress("WARNING: Slow query detected")
        assert result.intent_level is None

    def test_intent_level_is_none_by_default(self, compressor):
        """All compression results should have intent_level=None.

        The calling layer sets Guna from its OpCode context.
        """
        texts = [
            "ERROR: crash",
            "SUCCESS: done",
            "TODO: fix later",
            "Unified harmonious state",
            "Hello world",
        ]
        for text in texts:
            result = compressor.compress(text)
            assert result.intent_level is None, (
                f"Compression must not assign intent to '{text}'. "
                f"Guna comes from OpCode, not text content."
            )

    def test_guna_from_opcode_not_text(self):
        """Verify that Guna classification exists in guna.py via OpCode."""
        from vibe_core.mahamantra.substrate.guna import get_guna, Guna
        from vibe_core.mahamantra.substrate.opcode import MantraOpCode

        # SATTVA operations: observation, no side effects
        assert get_guna(MantraOpCode.TYPE_CHECK) == Guna.SATTVA
        assert get_guna(MantraOpCode.LOG_EMIT) == Guna.SATTVA

        # RAJAS operations: creation, modification
        assert get_guna(MantraOpCode.EXEC_OP) == Guna.RAJAS
        assert get_guna(MantraOpCode.ALLOC_MEM) == Guna.RAJAS

        # TAMAS operations: destruction, cleanup
        assert get_guna(MantraOpCode.INIT_THREAD) == Guna.TAMAS
        assert get_guna(MantraOpCode.IO_FLUSH) == Guna.TAMAS

    # =========================================================================
    # COMPRESSION METRICS
    # =========================================================================

    def test_compression_ratio_positive(self, compressor):
        """Compression ratio should be positive."""
        result = compressor.compress("A" * 1000)
        assert result.compression_ratio > 0

    def test_compression_ratio_scales(self, compressor):
        """Larger inputs should have higher compression ratios."""
        small = compressor.compress("Hello")
        large = compressor.compress("Hello " * 100)
        assert large.compression_ratio > small.compression_ratio

    def test_output_size_fixed(self, compressor):
        """Output size should be fixed (32-bit seed)."""
        result = compressor.compress("Any text here")
        assert result.output_size == 4  # 4 bytes = 32 bits

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def test_compress_batch(self, compressor):
        """Batch compression should return list of results."""
        items = ["Error: fail", "Warning: slow", "Success: done"]
        results = compressor.compress_batch(items)
        assert len(results) == 3
        # All seeds should be different
        seeds = {r.seed for r in results}
        assert len(seeds) == 3
        # No intent classification from text
        for r in results:
            assert r.intent_level is None

    def test_compress_aggregate(self, compressor):
        """Aggregate should combine seeds and sizes."""
        items = [
            "Everything is healthy",
            "Warning: minor issue",
            "Error: critical failure",
        ]
        result = compressor.compress_aggregate(items)
        assert result.seed is not None
        assert result.input_size > 0
        assert result.intent_level is None

    # =========================================================================
    # EDGE CASES
    # =========================================================================

    def test_empty_string(self, compressor):
        """Empty string should not crash."""
        result = compressor.compress("")
        assert result.seed is not None

    def test_unicode_text(self, compressor):
        """Unicode should be handled correctly."""
        result = compressor.compress("日本語テスト 🎉")
        assert result.seed is not None

    def test_bytes_input(self, compressor):
        """Bytes input should be handled."""
        result = compressor.compress(b"Hello bytes")
        assert result.seed is not None

    def test_dict_input(self, compressor):
        """Dict input should be serialized and compressed."""
        result = compressor.compress({"key": "value", "count": 42})
        assert result.seed is not None

    # =========================================================================
    # PHYSICS VERIFICATION
    # =========================================================================

    def test_verify_physics_137(self, compressor):
        """Seed 137 should be MAHA_QUANTUM aligned."""
        result = compressor.verify_physics(137)
        assert result.is_aligned
        assert result.quantum_score == 1.0  # 137 is MAHA_QUANTUM

    def test_verify_physics_16(self, compressor):
        """Seed 16 should be aligned (WORDS)."""
        result = compressor.verify_physics(16)
        assert result.is_aligned

    def test_verify_physics_64(self, compressor):
        """Seed 64 should be aligned (QUALITIES)."""
        result = compressor.verify_physics(64)
        assert result.is_aligned


class TestIntentGuna:
    """Test IntentGuna enum."""

    def test_all_gunas_exist(self):
        """All four gunas should exist."""
        assert IntentGuna.TAMAS is not None
        assert IntentGuna.RAJAS is not None
        assert IntentGuna.SATTVA is not None
        assert IntentGuna.SUDDHA is not None

    def test_guna_values(self):
        """Guna values should be lowercase strings."""
        assert IntentGuna.TAMAS.value == "tamas"
        assert IntentGuna.RAJAS.value == "rajas"
        assert IntentGuna.SATTVA.value == "sattva"
        assert IntentGuna.SUDDHA.value == "suddha"
