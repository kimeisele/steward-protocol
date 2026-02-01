"""
Tests for MahaCompression adapter.

Tests intent classification, seed generation, and compression metrics.
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
    # INTENT CLASSIFICATION
    # =========================================================================

    def test_classify_tamas_error(self, compressor):
        """Error messages should classify as TAMAS."""
        result = compressor.compress("ERROR: Database connection failed")
        assert result.intent_level.guna == IntentGuna.TAMAS

    def test_classify_tamas_crash(self, compressor):
        """Crash messages should classify as TAMAS."""
        result = compressor.compress("FATAL: Application crashed with segfault")
        assert result.intent_level.guna == IntentGuna.TAMAS

    def test_classify_rajas_warning(self, compressor):
        """Warning messages should classify as RAJAS."""
        result = compressor.compress("WARNING: Slow query detected, retry in progress")
        assert result.intent_level.guna == IntentGuna.RAJAS

    def test_classify_rajas_todo(self, compressor):
        """TODO comments should classify as RAJAS."""
        result = compressor.compress("TODO: Fix this workaround later")
        assert result.intent_level.guna == IntentGuna.RAJAS

    def test_classify_sattva_success(self, compressor):
        """Success messages should classify as SATTVA."""
        result = compressor.compress("SUCCESS: All tests passed, deployment complete")
        assert result.intent_level.guna == IntentGuna.SATTVA

    def test_classify_sattva_healthy(self, compressor):
        """Health messages should classify as SATTVA."""
        result = compressor.compress("System healthy and stable, all services verified")
        assert result.intent_level.guna == IntentGuna.SATTVA

    def test_classify_suddha_transcend(self, compressor):
        """Transcendental terms should classify as SUDDHA."""
        result = compressor.compress("Unified system achieved optimal harmonious state")
        assert result.intent_level.guna == IntentGuna.SUDDHA

    def test_tamas_priority_over_sattva(self, compressor):
        """TAMAS should take priority when both keywords present."""
        # This has both "error" (TAMAS) and "success" (SATTVA)
        result = compressor.compress("Error occurred but partial success achieved")
        assert result.intent_level.guna == IntentGuna.TAMAS

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
        assert results[0].intent_level.guna == IntentGuna.TAMAS
        assert results[1].intent_level.guna == IntentGuna.RAJAS
        assert results[2].intent_level.guna == IntentGuna.SATTVA

    def test_compress_aggregate(self, compressor):
        """Aggregate should return worst-case intent."""
        items = [
            "Everything is healthy",
            "Warning: minor issue",
            "Error: critical failure",
        ]
        result = compressor.compress_aggregate(items)
        # Worst case (TAMAS) should surface
        assert result.intent_level.guna == IntentGuna.TAMAS

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
