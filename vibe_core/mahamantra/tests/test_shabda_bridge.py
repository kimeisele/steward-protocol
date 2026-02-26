"""
Tests for Shabda Bridge — Prabhupada Acoustic Signatures
=========================================================
"""

import json
import sys

import pytest

from vibe_core.mahamantra.protocols._seed import PANCHA, POSITION_SUM_RAMA
from vibe_core.mahamantra.substrate._paths import DATA_DIR
from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
    _ensure_loaded,
    acoustic_score,
    acoustic_signature,
    get_meta,
    segment_at,
    vibration_alignment,
)


# =============================================================================
# DATA FILE
# =============================================================================


class TestDataFile:
    def test_data_file_exists(self):
        path = DATA_DIR / "shabda_bridge.json"
        assert path.exists(), f"shabda_bridge.json not found at {path}"

    def test_data_file_valid_json(self):
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_data_file_has_required_keys(self):
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)
        required = {"meta", "syllables", "segments", "harmonic_series", "aggregate", "mahamantra_coords"}
        assert required <= set(data.keys())

    def test_data_file_no_floats(self):
        """All values must be integers — no floats leaked from bake."""
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)

        def check(obj, path=""):
            if isinstance(obj, float):
                pytest.fail(f"Float at {path}: {obj}")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    check(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check(v, f"{path}[{i}]")

        check(data)


# =============================================================================
# LOADING
# =============================================================================


class TestLoading:
    def test_ensure_loaded(self):
        _ensure_loaded()
        # Should not raise

    def test_meta_has_vibration_id(self):
        meta = get_meta()
        assert "vibration_id" in meta

    def test_meta_has_source(self):
        meta = get_meta()
        assert "source" in meta
        assert "Prabhupada" in meta["source"]

    def test_meta_segments_positive(self):
        meta = get_meta()
        assert meta["n_segments"] > 0


# =============================================================================
# SYLLABLE SIGNATURES
# =============================================================================


EXPECTED_SYLLABLES = ["ha", "re", "kṛ", "ṣṇa", "rā", "ma"]


class TestSyllableSignatures:
    def test_six_syllable_types(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert sig is not None, f"Missing syllable: {syl}"

    def test_unknown_syllable_returns_none(self):
        assert acoustic_signature("xyz") is None
        assert acoustic_signature("") is None

    def test_signature_has_rama_coords(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert "rama_coords" in sig
            assert isinstance(sig["rama_coords"], list)
            assert len(sig["rama_coords"]) > 0

    def test_rama_coords_in_valid_range(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            for c in sig["rama_coords"]:
                assert 0 <= c < POSITION_SUM_RAMA, f"{syl}: coord {c} out of range"

    def test_rama_coords_match_varnamala_codec(self):
        from vibe_core.mahamantra.substrate.encoding.varnamala_codec import encode

        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            expected = list(encode(syl))
            assert sig["rama_coords"] == expected, f"{syl}: {sig['rama_coords']} != {expected}"

    def test_signature_has_articulation(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert "articulation" in sig
            assert isinstance(sig["articulation"], int)

    def test_signature_has_voicing(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert "voicing" in sig
            assert isinstance(sig["voicing"], int)

    def test_signature_has_acoustic_features(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            for key in ("centroid_hz_x10", "f0_hz_x10", "rms_x1000"):
                assert key in sig, f"{syl} missing {key}"
                assert isinstance(sig[key], int)

    def test_element_histogram_length(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert "element_histogram" in sig
            assert len(sig["element_histogram"]) == PANCHA


# =============================================================================
# SEGMENTS
# =============================================================================


class TestSegments:
    def test_segment_at_zero(self):
        seg = segment_at(0)
        assert seg is not None
        assert "syllable" in seg
        assert "onset_ms" in seg

    def test_segment_at_out_of_range(self):
        assert segment_at(-1) is None
        assert segment_at(9999) is None

    def test_segments_have_valid_rama_coords(self):
        meta = get_meta()
        for i in range(meta["n_segments"]):
            seg = segment_at(i)
            for c in seg.get("rama_coords", []):
                assert 0 <= c < POSITION_SUM_RAMA

    def test_segments_have_vibration_ids(self):
        meta = get_meta()
        for i in range(meta["n_segments"]):
            seg = segment_at(i)
            assert "vibration_id" in seg
            assert isinstance(seg["vibration_id"], int)

    def test_segments_chronological(self):
        meta = get_meta()
        prev_ms = 0
        for i in range(meta["n_segments"]):
            seg = segment_at(i)
            assert seg["onset_ms"] >= prev_ms, f"Segment {i} not chronological"
            prev_ms = seg["onset_ms"]


# =============================================================================
# VIBRATION ALIGNMENT
# =============================================================================


class TestVibrationAlignment:
    def test_fundamental_max_score(self):
        meta = get_meta()
        vid = meta["vibration_id"]
        score = vibration_alignment(vid)
        assert score >= 0.9, f"Fundamental VibID {vid} should score high, got {score}"

    def test_harmonic_positive(self):
        # H2 should score positively
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)
        h2 = data["harmonic_series"]["vibration_ids"][1]
        assert vibration_alignment(h2) > 0.5

    def test_non_harmonic_low(self):
        # Very far from any harmonic
        score = vibration_alignment(9999)
        assert score < 0.1

    def test_range_zero_to_one(self):
        for vid in range(0, 500, 7):
            score = vibration_alignment(vid)
            assert 0.0 <= score <= 1.0, f"VibID {vid}: score {score} out of range"


# =============================================================================
# ACOUSTIC SCORE
# =============================================================================


class TestAcousticScore:
    def test_empty_inputs(self):
        assert acoustic_score("", "") == 0.0
        assert acoustic_score("test", "") == 0.0

    def test_score_range(self):
        # Can't easily test with real packed_hex without full infrastructure,
        # but verify the function runs without error
        score = acoustic_score("hare krishna", "nonexistent_hex")
        assert 0.0 <= score <= 1.0


# =============================================================================
# NO HEAVY DEPS AT IMPORT
# =============================================================================


class TestNoDeps:
    def test_no_numpy_at_import(self):
        """Importing shabda_bridge must NOT trigger numpy/scipy."""
        # Re-import and check
        import importlib

        mod = importlib.import_module("vibe_core.mahamantra.substrate.encoding.shabda_bridge")
        source = open(mod.__file__).read()
        assert "import numpy" not in source
        assert "import scipy" not in source
        assert "from numpy" not in source
        assert "from scipy" not in source
