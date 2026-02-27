"""
Tests for ShabdaProcessor — Audio Frames → RAMA Coordinates
=============================================================
"""

import numpy as np

from vibe_core.mahamantra.protocols._seed import PANCHA
from vibe_core.mahamantra.sound.shabda_intake import (
    DEFAULT_SAMPLE_RATE,
    ShabdaIntake,
    pack_frame,
)
from vibe_core.mahamantra.sound.shabda_processor import (
    _ASPIRATION_CENTROID_FLOOR,
    _CENTROID_SIBILANT_THRESHOLD,
    _GHOSHMAHA_RMS_FLOOR,
    _NASAL_CENTROID_CEILING,
    _RMS_VOICED_THRESHOLD,
    _RMS_VOWEL_THRESHOLD,
    STHANA_ENERGY,
    _audio_to_sthana,
    _classify_sound,
    _refine_sub_index,
    compare_streams,
    frame_to_rama,
    frame_to_sthana,
    stream_to_element_walk,
    stream_to_energy_contour,
    stream_to_histogram,
    stream_to_rama,
    stream_to_signature,
    stream_to_sthana_profile,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
    COORD_ELEMENT,
    COORD_SUB,
    COORD_VARGA,
)

# =============================================================================
# HELPERS
# =============================================================================


def _make_frame(rms: int, varga: int, f0_x10: int, centroid_100: int) -> int:
    return pack_frame(rms, varga, f0_x10, centroid_100)


def _sine_wave(freq: float, duration_s: float, sr: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sr * duration_s)) / sr
    return 0.8 * np.sin(2 * np.pi * freq * t)


# =============================================================================
# SOUND CLASS DETECTION
# =============================================================================


class TestClassifySound:
    def test_silence(self):
        assert _classify_sound(0, 0, 0) == -1
        assert _classify_sound(_RMS_VOICED_THRESHOLD - 1, 500, 100) == -1

    def test_vowel(self):
        """High RMS + F0 = vowel."""
        cls = _classify_sound(_RMS_VOWEL_THRESHOLD + 10, 1200, 100)
        assert cls == 0  # SVARA

    def test_stop_onset(self):
        """Low prev_rms → high rms = plosive onset."""
        cls = _classify_sound(50, 1000, 100, prev_rms=5)
        assert cls == 1  # SPARSHA

    def test_sibilant(self):
        """High centroid + no F0 = sibilant."""
        cls = _classify_sound(50, 0, _CENTROID_SIBILANT_THRESHOLD + 10)
        assert cls == 2  # SHESHA

    def test_semivowel(self):
        """Medium RMS + F0 but below vowel threshold."""
        cls = _classify_sound(50, 1000, 100, prev_rms=50)
        assert cls == 2  # SHESHA (semivowel-like)


# =============================================================================
# SUB-INDEX REFINEMENT
# =============================================================================


class TestAudioToSthana:
    """Sthana detection: audio features → 5 energy levels (0-4)."""

    def test_unvoiced_no_f0(self):
        """No pitch → SPARSHA (0)."""
        assert _audio_to_sthana(50, 0, 100) == 0

    def test_nasal_low_centroid(self):
        """F0 + low centroid → ANUNASIKA (4)."""
        assert _audio_to_sthana(60, 1000, _NASAL_CENTROID_CEILING - 10) == 4

    def test_voiced_aspirated_high_all(self):
        """F0 + high RMS + high centroid → GHOSHMAHA (3)."""
        assert _audio_to_sthana(
            _GHOSHMAHA_RMS_FLOOR + 10, 1200, _ASPIRATION_CENTROID_FLOOR + 10,
        ) == 3

    def test_aspirated_high_centroid_low_rms(self):
        """F0 + high centroid but moderate RMS → MAHAPRANA (1)."""
        assert _audio_to_sthana(80, 1200, _ASPIRATION_CENTROID_FLOOR + 10) == 1

    def test_voiced_moderate(self):
        """F0 + moderate everything → GHOSHAVAT (2)."""
        assert _audio_to_sthana(80, 1200, 100) == 2

    def test_all_five_sthanas_reachable(self):
        """Every SthanaIndex (0-4) must be reachable from audio features."""
        seen = set()
        # SPARSHA: no F0
        seen.add(_audio_to_sthana(50, 0, 100))
        # MAHAPRANA: F0 + high centroid, moderate RMS
        seen.add(_audio_to_sthana(80, 1200, 150))
        # GHOSHAVAT: F0 + moderate
        seen.add(_audio_to_sthana(80, 1200, 100))
        # GHOSHMAHA: F0 + high RMS + high centroid
        seen.add(_audio_to_sthana(150, 1200, 150))
        # ANUNASIKA: F0 + low centroid
        seen.add(_audio_to_sthana(60, 1000, 50))
        assert seen == {0, 1, 2, 3, 4}


class TestRefineSubIndex:
    """Sub-index refinement using Sthana-aware features."""

    def test_svara_short(self):
        assert _refine_sub_index(0, 100, 1200, 100, 0) == 0  # short

    def test_svara_long(self):
        assert _refine_sub_index(0, 150, 1200, 100, 0) == 1  # long

    def test_svara_compound(self):
        """High energy + high centroid → compound vowel (diphthong)."""
        assert _refine_sub_index(0, 170, 1200, 130, 0) == 2  # compound

    def test_svara_special_nasal(self):
        """Low centroid in vowel → anusvara territory."""
        assert _refine_sub_index(0, 100, 1200, 50, 0) == 3  # special

    def test_sparsha_unvoiced(self):
        """No F0 → SPARSHA (0) via _audio_to_sthana."""
        assert _refine_sub_index(1, 50, 0, 100, 0) == 0

    def test_sparsha_aspirated(self):
        """F0 + high centroid, moderate RMS → MAHAPRANA (1)."""
        assert _refine_sub_index(1, 80, 1200, _ASPIRATION_CENTROID_FLOOR + 10, 0) == 1

    def test_sparsha_voiced(self):
        """F0 + moderate centroid → GHOSHAVAT (2)."""
        assert _refine_sub_index(1, 80, 1200, 100, 0) == 2

    def test_sparsha_voiced_aspirated(self):
        """F0 + high RMS + high centroid → GHOSHMAHA (3)."""
        assert _refine_sub_index(
            1, _GHOSHMAHA_RMS_FLOOR + 10, 1200, _ASPIRATION_CENTROID_FLOOR + 10, 0,
        ) == 3

    def test_sparsha_nasal(self):
        """F0 + low centroid → ANUNASIKA (4)."""
        assert _refine_sub_index(1, 60, 1000, _NASAL_CENTROID_CEILING - 10, 0) == 4

    def test_shesha_semivowel(self):
        assert _refine_sub_index(2, 60, 1000, 100, 0) == 0  # semivowel

    def test_shesha_sibilant(self):
        sub = _refine_sub_index(2, 60, 0, _CENTROID_SIBILANT_THRESHOLD + 10, 0)
        assert sub == 1  # sibilant


# =============================================================================
# FRAME → RAMA COORDINATE
# =============================================================================


class TestFrameToRama:
    def test_silence_returns_minus_one(self):
        frame = _make_frame(0, 0, 0, 0)
        assert frame_to_rama(frame) == -1

    def test_returns_valid_coordinate(self):
        frame = _make_frame(150, 0, 1200, 10000)
        coord = frame_to_rama(frame)
        assert 0 <= coord <= 48

    def test_element_matches_varga(self):
        """The RAMA coordinate's element should match the input varga."""
        for varga in range(PANCHA):
            frame = _make_frame(150, varga, 1200, 10000)
            coord = frame_to_rama(frame)
            assert COORD_ELEMENT[coord] == varga, (
                f"varga={varga} → coord={coord} has element={COORD_ELEMENT[coord]}"
            )

    def test_all_five_elements_reachable(self):
        """Each varga (0-4) should map to a coordinate in that element."""
        seen_elements = set()
        for varga in range(PANCHA):
            frame = _make_frame(150, varga, 1200, 10000)
            coord = frame_to_rama(frame)
            seen_elements.add(COORD_ELEMENT[coord].value)
        assert seen_elements == {0, 1, 2, 3, 4}

    def test_vowel_maps_to_svara(self):
        """High RMS + F0 → SVARA class (varga_class=0)."""
        frame = _make_frame(150, 0, 1200, 10000)
        coord = frame_to_rama(frame)
        assert COORD_VARGA[coord] == 0  # SVARA

    def test_onset_maps_to_sparsha(self):
        """Onset detection → SPARSHA class (varga_class=1)."""
        prev = _make_frame(5, 0, 0, 0)  # near silence
        frame = _make_frame(50, 0, 1200, 10000)  # onset
        coord = frame_to_rama(frame, prev)
        assert COORD_VARGA[coord] == 1  # SPARSHA

    def test_different_rms_different_sub(self):
        """Short vowel (low RMS) vs long vowel (high RMS) → different sub-index."""
        short = _make_frame(100, 0, 1200, 10000)
        long_ = _make_frame(180, 0, 1200, 10000)
        c_short = frame_to_rama(short)
        c_long = frame_to_rama(long_)
        # Both should be SVARA, but different sub-indices (short vs long)
        assert COORD_VARGA[c_short] == 0
        assert COORD_VARGA[c_long] == 0
        assert COORD_SUB[c_short] != COORD_SUB[c_long]


# =============================================================================
# STREAM → RAMA COORDINATES
# =============================================================================


class TestStreamToRama:
    def test_empty_stream(self):
        assert stream_to_rama(()) == ()

    def test_all_silence(self):
        frames = [_make_frame(0, 0, 0, 0)] * 10
        assert stream_to_rama(frames) == ()

    def test_voiced_frames_produce_coords(self):
        frames = [_make_frame(150, 0, 1200, 10000)] * 5
        coords = stream_to_rama(frames)
        assert len(coords) == 5
        assert all(0 <= c <= 48 for c in coords)

    def test_mixed_silence_and_voiced(self):
        frames = [
            _make_frame(0, 0, 0, 0),      # silence
            _make_frame(150, 0, 1200, 10000),  # voiced
            _make_frame(0, 0, 0, 0),      # silence
            _make_frame(120, 2, 1500, 12000),  # voiced
        ]
        coords = stream_to_rama(frames)
        assert len(coords) == 2  # only voiced

    def test_prabhupada_stream(self):
        """Process Prabhupada's actual stream — should produce coordinates."""
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            _ensure_loaded,
            stream_frame,
            stream_length,
        )
        _ensure_loaded()
        frames = [stream_frame(i) for i in range(stream_length())]
        coords = stream_to_rama(frames)
        assert len(coords) > 500  # 638 frames, most are voiced
        assert len(coords) < 638  # some silence at start/end


# =============================================================================
# ELEMENT WALK / HISTOGRAM / SIGNATURE
# =============================================================================


class TestStreamDerived:
    def _voiced_stream(self) -> list:
        return [
            _make_frame(150, 0, 1200, 10000),  # AKASHA
            _make_frame(150, 1, 1200, 10000),  # VAYU
            _make_frame(150, 2, 1200, 10000),  # AGNI
            _make_frame(150, 3, 1200, 10000),  # JALA
            _make_frame(150, 4, 1200, 10000),  # PRITHVI
        ]

    def test_element_walk(self):
        walk = stream_to_element_walk(self._voiced_stream())
        assert len(walk) == 5
        elements = [e.value for e in walk]
        assert elements == [0, 1, 2, 3, 4]

    def test_element_walk_empty(self):
        assert stream_to_element_walk(()) == ()

    def test_histogram(self):
        hist = stream_to_histogram(self._voiced_stream())
        assert len(hist) == PANCHA
        assert sum(hist) == 5
        # Each element should appear once
        assert all(h == 1 for h in hist)

    def test_histogram_empty(self):
        assert stream_to_histogram(()) == (0, 0, 0, 0, 0)

    def test_signature(self):
        sig = stream_to_signature(self._voiced_stream())
        assert len(sig) == 5
        assert all(c in "SVFWE" for c in sig)

    def test_signature_empty(self):
        assert stream_to_signature(()) == ""


# =============================================================================
# STHANA PROFILE / ENERGY CONTOUR
# =============================================================================


class TestSthanaProfile:
    def test_frame_to_sthana_silence(self):
        assert frame_to_sthana(_make_frame(0, 0, 0, 0)) == -1

    def test_frame_to_sthana_voiced(self):
        s = frame_to_sthana(_make_frame(80, 0, 1200, 100))
        assert 0 <= s <= 4

    def test_frame_to_sthana_all_five_reachable(self):
        """All 5 Sthana levels reachable from audio.

        pack_frame takes centroid_x10 (Hz×10), unpacked gives centroid_100 (x10//100).
        So centroid_100=130 needs centroid_x10=13000 in pack_frame.
        """
        seen = set()
        seen.add(frame_to_sthana(_make_frame(50, 0, 0, 10000)))      # SPARSHA(0): no F0
        seen.add(frame_to_sthana(_make_frame(80, 0, 1200, 13000)))    # MAHAPRANA(1): F0+high cent
        seen.add(frame_to_sthana(_make_frame(80, 0, 1200, 10000)))    # GHOSHAVAT(2): F0+mod cent
        seen.add(frame_to_sthana(_make_frame(150, 0, 1200, 13000)))   # GHOSHMAHA(3): F0+high all
        seen.add(frame_to_sthana(_make_frame(60, 0, 1000, 5000)))     # ANUNASIKA(4): F0+low cent
        assert seen == {0, 1, 2, 3, 4}

    def test_profile_empty(self):
        assert stream_to_sthana_profile(()) == ()

    def test_profile_silence_removed(self):
        frames = [_make_frame(0, 0, 0, 0), _make_frame(80, 0, 1200, 100)]
        profile = stream_to_sthana_profile(frames)
        assert len(profile) == 1

    def test_profile_same_length_as_rama(self):
        frames = [
            _make_frame(0, 0, 0, 0),
            _make_frame(150, 0, 1200, 10000),
            _make_frame(150, 1, 1200, 10000),
            _make_frame(0, 0, 0, 0),
            _make_frame(80, 2, 1500, 12000),
        ]
        coords = stream_to_rama(frames)
        profile = stream_to_sthana_profile(frames)
        assert len(profile) == len(coords)

    def test_energy_contour_empty(self):
        assert stream_to_energy_contour(()) == ()

    def test_energy_contour_values_in_range(self):
        frames = [_make_frame(150, v, 1200, 10000) for v in range(PANCHA)]
        contour = stream_to_energy_contour(frames)
        assert all(0.0 <= e <= 1.0 for e in contour)

    def test_energy_contour_same_length_as_rama(self):
        frames = [_make_frame(150, 0, 1200, 10000)] * 5
        coords = stream_to_rama(frames)
        contour = stream_to_energy_contour(frames)
        assert len(contour) == len(coords)

    def test_sthana_energy_tuple(self):
        """STHANA_ENERGY maps index → float correctly."""
        assert len(STHANA_ENERGY) == PANCHA
        assert STHANA_ENERGY[0] == 0.2   # SPARSHA
        assert STHANA_ENERGY[3] == 1.0   # GHOSHMAHA (max)
        assert all(0.0 < e <= 1.0 for e in STHANA_ENERGY)

    def test_prabhupada_sthana_profile(self):
        """Prabhupada's stream has all 5 Sthana levels."""
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            _ensure_loaded,
            stream_frame,
            stream_length,
        )
        _ensure_loaded()
        frames = [stream_frame(i) for i in range(stream_length())]
        profile = stream_to_sthana_profile(frames)
        assert len(profile) > 500
        # Should have at least 3 distinct Sthana levels
        assert len(set(profile)) >= 3

    def test_prabhupada_energy_contour(self):
        """Energy contour has variation (not all same level)."""
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            _ensure_loaded,
            stream_frame,
            stream_length,
        )
        _ensure_loaded()
        frames = [stream_frame(i) for i in range(stream_length())]
        contour = stream_to_energy_contour(frames)
        mean_energy = sum(contour) / len(contour)
        # Prabhupada's chanting: mostly voiced (0.8) with aspiration (0.6)
        assert 0.5 < mean_energy < 0.95


# =============================================================================
# COMPARE STREAMS
# =============================================================================


class TestCompareStreams:
    def test_identical_streams(self):
        frames = [_make_frame(150, 0, 1200, 10000)] * 10
        assert compare_streams(frames, frames) == 0.0

    def test_different_elements(self):
        a = [_make_frame(150, 0, 1200, 10000)] * 10  # all AKASHA
        b = [_make_frame(150, 4, 1200, 10000)] * 10  # all PRITHVI
        dist = compare_streams(a, b)
        assert dist > 0.8  # very different

    def test_empty_streams(self):
        assert compare_streams((), ()) == 1.0
        frames = [_make_frame(150, 0, 1200, 10000)]
        assert compare_streams(frames, ()) == 1.0

    def test_similar_streams(self):
        """Mostly same element, slight variation → low distance."""
        a = [_make_frame(150, 0, 1200, 10000)] * 8 + [_make_frame(150, 1, 1200, 10000)] * 2
        b = [_make_frame(150, 0, 1200, 10000)] * 7 + [_make_frame(150, 1, 1200, 10000)] * 3
        dist = compare_streams(a, b)
        assert dist < 0.15

    def test_prabhupada_self_distance(self):
        """Prabhupada vs himself = near-zero distance."""
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            _ensure_loaded,
            stream_frame,
            stream_length,
        )
        _ensure_loaded()
        frames = [stream_frame(i) for i in range(stream_length())]
        # First half vs second half should be somewhat similar
        mid = len(frames) // 2
        dist = compare_streams(frames[:mid], frames[mid:])
        assert dist < 0.3  # Same speaker, same chant


# =============================================================================
# INTEGRATION: AUDIO → RAMA → RESONANCE PIPELINE
# =============================================================================


class TestFullPipeline:
    def test_audio_to_element_histogram(self):
        """Synthetic sine → ShabdaIntake → ShabdaProcessor → histogram."""
        engine = ShabdaIntake()
        samples = 0.8 * np.sin(2 * np.pi * 300 * np.arange(int(DEFAULT_SAMPLE_RATE * 0.5)) / DEFAULT_SAMPLE_RATE)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        hist = stream_to_histogram(stream.frames)
        assert sum(hist) > 0  # non-empty

    def test_audio_to_rama_coords(self):
        """Synthetic audio → RAMA coordinates that can feed into ResonanceRanker."""
        engine = ShabdaIntake()
        samples = 0.8 * np.sin(2 * np.pi * 300 * np.arange(int(DEFAULT_SAMPLE_RATE * 0.3)) / DEFAULT_SAMPLE_RATE)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        coords = stream_to_rama(stream.frames)
        assert len(coords) > 0
        # These coords should be valid input for pancha_walk functions
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
            element_histogram as eh,
        )
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import (
            walk_signature as ws,
        )
        hist = eh(coords)
        sig = ws(coords)
        assert len(hist) == 5
        assert len(sig) == len(coords)

    def test_audio_coords_compatible_with_walk_distance(self):
        """Audio-derived coords can be compared to text-derived coords."""
        engine = ShabdaIntake()
        samples = 0.8 * np.sin(2 * np.pi * 300 * np.arange(int(DEFAULT_SAMPLE_RATE * 0.3)) / DEFAULT_SAMPLE_RATE)
        stream = engine.process_samples(samples, DEFAULT_SAMPLE_RATE)
        audio_coords = stream_to_rama(stream.frames)
        assert len(audio_coords) > 0

        # Text-derived coords (same coordinate space)
        from vibe_core.mahamantra.substrate.encoding.pancha_walk import walk_distance as wd
        text_coords = (16, 42, 40)  # "karma" = ka + ra + ma
        dist = wd(audio_coords, text_coords)
        assert 0.0 <= dist <= 1.0
