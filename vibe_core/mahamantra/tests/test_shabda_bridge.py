"""
Tests for Shabda Bridge v2 — Prabhupada Continuous Acoustic Stream
===================================================================
"""

import json

import pytest

from vibe_core.mahamantra.protocols._seed import POSITION_SUM_RAMA, WORDS
from vibe_core.mahamantra.substrate._paths import DATA_DIR
from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
    _MAHAMANTRA_SYLLABLES,
    _ensure_loaded,
    acoustic_score,
    acoustic_signature,
    get_meta,
    prabhupada_salt,
    stream_frame,
    stream_length,
    syllable_at_position,
    unpack_frame,
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
        required = {"meta", "stream", "syllables", "harmonic_series", "mahamantra_coords"}
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

    def test_bake_version_is_2(self):
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)
        assert data["meta"]["bake_version"] == 2


# =============================================================================
# LOADING
# =============================================================================


class TestLoading:
    def test_ensure_loaded(self):
        _ensure_loaded()

    def test_meta_has_vibration_id(self):
        meta = get_meta()
        assert "vibration_id" in meta

    def test_meta_has_source(self):
        meta = get_meta()
        assert "source" in meta
        assert "Prabhupada" in meta["source"]

    def test_meta_has_n_frames(self):
        meta = get_meta()
        assert meta["n_frames"] > 0

    def test_meta_has_chant_boundaries(self):
        meta = get_meta()
        assert "chant_start_frame" in meta
        assert "chant_end_frame" in meta
        assert meta["chant_end_frame"] > meta["chant_start_frame"]


# =============================================================================
# CONTINUOUS STREAM
# =============================================================================


class TestContinuousStream:
    def test_stream_length_positive(self):
        assert stream_length() > 0

    def test_stream_length_matches_meta(self):
        meta = get_meta()
        assert stream_length() == meta["n_frames"]

    def test_stream_frame_valid(self):
        frame = stream_frame(0)
        assert isinstance(frame, int)
        assert frame >= 0

    def test_stream_frame_out_of_range(self):
        assert stream_frame(-1) == 0
        assert stream_frame(999999) == 0

    def test_all_frames_are_uint32(self):
        """Every frame must fit in 32 bits."""
        for i in range(stream_length()):
            f = stream_frame(i)
            assert 0 <= f < (1 << 32), f"Frame {i} out of uint32 range: {f}"

    def test_stream_fits_antaranga(self):
        """638 frames × 4 bytes = 2,552 bytes < 16 KB Antaranga."""
        assert stream_length() * 4 <= 16384


# =============================================================================
# FRAME UNPACKING
# =============================================================================


class TestUnpackFrame:
    def test_unpack_returns_4_tuple(self):
        packed = prabhupada_salt(0)
        result = unpack_frame(packed)
        assert len(result) == 4

    def test_unpack_rms_range(self):
        for i in range(32):
            rms, _, _, _ = unpack_frame(prabhupada_salt(i))
            assert 0 <= rms <= 255

    def test_unpack_varga_range(self):
        for i in range(32):
            _, varga, _, _ = unpack_frame(prabhupada_salt(i))
            assert 0 <= varga <= 4

    def test_unpack_f0_range(self):
        for i in range(32):
            _, _, f0_x10, _ = unpack_frame(prabhupada_salt(i))
            assert 0 <= f0_x10 <= 4095

    def test_unpack_centroid_range(self):
        for i in range(32):
            _, _, _, centroid_100 = unpack_frame(prabhupada_salt(i))
            assert 0 <= centroid_100 <= 511

    def test_pack_unpack_roundtrip(self):
        """Verify unpack matches the bake script's packing."""
        for i in range(min(50, stream_length())):
            packed = stream_frame(i)
            rms, varga, f0_x10, cent = unpack_frame(packed)
            repacked = rms | (varga << 8) | (f0_x10 << 11) | (cent << 23)
            assert packed == repacked, f"Frame {i}: {packed} != {repacked}"


# =============================================================================
# PRABHUPADA SALT (CORE)
# =============================================================================


class TestPrabhupadaSalt:
    def test_returns_int(self):
        assert isinstance(prabhupada_salt(0), int)

    def test_32_positions(self):
        """All 32 Mahamantra syllable positions return a value."""
        for i in range(32):
            salt = prabhupada_salt(i)
            assert salt >= 0, f"Position {i} returned negative: {salt}"

    def test_wraps_modulo(self):
        """Position 32 wraps to position 0."""
        assert prabhupada_salt(32) == prabhupada_salt(0)
        assert prabhupada_salt(33) == prabhupada_salt(1)

    def test_voiced_positions_have_energy(self):
        """Most positions in the chant should have nonzero RMS."""
        voiced = 0
        for i in range(32):
            rms, _, _, _ = unpack_frame(prabhupada_salt(i))
            if rms > 10:
                voiced += 1
        assert voiced > 20, f"Only {voiced}/32 positions have RMS > 10"

    def test_different_syllables_have_different_salt(self):
        """At least some positions differ — not all the same value."""
        values = {prabhupada_salt(i) for i in range(32)}
        assert len(values) > 10, f"Only {len(values)} unique salt values out of 32"


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

    def test_signature_has_n_frames(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            assert "n_frames" in sig
            assert isinstance(sig["n_frames"], int)
            assert sig["n_frames"] >= 0

    def test_signature_has_avg_features(self):
        for syl in EXPECTED_SYLLABLES:
            sig = acoustic_signature(syl)
            for key in ("avg_rms", "avg_f0_x10", "avg_centroid_100"):
                assert key in sig, f"{syl} missing {key}"
                assert isinstance(sig[key], int)


# =============================================================================
# SYLLABLE AT POSITION
# =============================================================================


class TestSyllableAtPosition:
    def test_32_positions_cover_mahamantra(self):
        syllables = [syllable_at_position(i) for i in range(32)]
        assert len(syllables) == 32

    def test_first_syllable_is_ha(self):
        assert syllable_at_position(0) == "ha"

    def test_second_syllable_is_re(self):
        assert syllable_at_position(1) == "re"

    def test_wraps(self):
        assert syllable_at_position(32) == syllable_at_position(0)

    def test_mahamantra_word_count(self):
        """32 syllable positions = WORDS × 2 (two lines)."""
        assert len(_MAHAMANTRA_SYLLABLES) == WORDS * 2


# =============================================================================
# VIBRATION ALIGNMENT
# =============================================================================


class TestVibrationAlignment:
    def test_fundamental_high_score(self):
        meta = get_meta()
        vid = meta["vibration_id"]
        score = vibration_alignment(vid)
        assert score >= 0.9, f"Fundamental VibID {vid} should score high, got {score}"

    def test_harmonic_positive(self):
        path = DATA_DIR / "shabda_bridge.json"
        with open(path) as f:
            data = json.load(f)
        h2 = data["harmonic_series"]["vibration_ids"][1]
        assert vibration_alignment(h2) > 0.5

    def test_non_harmonic_low(self):
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
        score = acoustic_score("hare krishna", "nonexistent_hex")
        assert 0.0 <= score <= 1.0


# =============================================================================
# NO HEAVY DEPS AT IMPORT
# =============================================================================


class TestNoDeps:
    def test_no_numpy_at_import(self):
        """Importing shabda_bridge must NOT trigger numpy/scipy."""
        import importlib

        mod = importlib.import_module("vibe_core.mahamantra.substrate.encoding.shabda_bridge")
        source = open(mod.__file__).read()
        assert "import numpy" not in source
        assert "import scipy" not in source
        assert "from numpy" not in source
        assert "from scipy" not in source
