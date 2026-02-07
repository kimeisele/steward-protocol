"""
VENU ORCHESTRATOR - Production Test Suite
==========================================

Tests the 19-bit DIW pipeline end-to-end:
  VenuOrchestrator → THE_FLUTE_CYCLE → pack/unpack → chamber._apply_diw

ALL CONSTANTS FROM SSOT. NO MAGIC NUMBERS.
"""
from __future__ import annotations

import struct

import pytest

from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    FLUTE_HOLES_SUM,
    MAHAMANTRA_WORD_PATTERN,
    MURALI_HOLES,
    QUARTERS,
    SEVEN,
    VAMSI_HOLES,
    VENU_HOLES,
    WORDS,
)
from vibe_core.mahamantra.protocols.diw import (
    DIW_MASK,
    MURALI_MASK,
    VAMSI_MASK,
    VENU_MASK,
    pack,
    unpack,
)
from vibe_core.mahamantra.substrate.venu_orchestrator import (
    THE_FLUTE_CYCLE,
    VenuOrchestrator,
    _NAME_TO_ENCODING,
)
from vibe_core.mahamantra.protocols._venu import (
    DIWEvent,
    DIWSubscriberProtocol,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def orch() -> VenuOrchestrator:
    """Fresh orchestrator for each test."""
    return VenuOrchestrator()


# =============================================================================
# LUT INTEGRITY
# =============================================================================


class TestFluteCycleLUT:
    """THE_FLUTE_CYCLE must be structurally perfect at module load."""

    def test_lut_length(self):
        assert len(THE_FLUTE_CYCLE) == WORDS

    def test_all_entries_fit_19_bits(self):
        for i, entry in enumerate(THE_FLUTE_CYCLE):
            assert entry <= DIW_MASK, f"Position {i}: {hex(entry)} exceeds 19 bits"

    def test_all_entries_nonzero(self):
        for i, entry in enumerate(THE_FLUTE_CYCLE):
            assert entry != 0, f"Position {i} is zero (silent flute)"

    def test_all_entries_unique(self):
        assert len(set(THE_FLUTE_CYCLE)) == WORDS, "LUT has duplicate entries"

    def test_murali_encodes_quarters(self):
        """MURALI must encode quarter index: 0,0,0,0, 1,1,1,1, 2,2,2,2, 3,3,3,3."""
        quarter_size = WORDS // QUARTERS
        for i, entry in enumerate(THE_FLUTE_CYCLE):
            expected = i // quarter_size
            actual = unpack(entry).murali
            assert actual == expected, f"Position {i}: MURALI={actual}, expected {expected}"

    def test_venu_values_unique(self):
        """All 16 VENU values must be distinct (no collisions in quality space)."""
        venu_vals = [unpack(e).venu for e in THE_FLUTE_CYCLE]
        assert len(set(venu_vals)) == WORDS

    def test_vamsi_distinguishes_names(self):
        """Each name (H/K/R) must occupy a distinct VAMSI region."""
        vamsi_stride = (1 << VAMSI_HOLES) // 3  # 170
        regions_by_name: dict[int, set[int]] = {0: set(), 1: set(), 2: set()}

        for i, entry in enumerate(THE_FLUTE_CYCLE):
            encoding = _NAME_TO_ENCODING[MAHAMANTRA_WORD_PATTERN[i]]
            region = min(unpack(entry).vamsi // vamsi_stride, 2)
            regions_by_name[encoding].add(region)

        # H (encoding 0) should primarily be in region 0
        assert 0 in regions_by_name[0], "Hare must have region 0"
        # K (encoding 1) should primarily be in region 1
        assert 1 in regions_by_name[1], "Krishna must have region 1"
        # R (encoding 2) should primarily be in region 2
        assert 2 in regions_by_name[2], "Rama must have region 2"

    def test_vamsi_no_intra_name_duplicates(self):
        """Within each name, VAMSI values must be unique."""
        by_name: dict[int, list[int]] = {0: [], 1: [], 2: []}
        for i, entry in enumerate(THE_FLUTE_CYCLE):
            enc = _NAME_TO_ENCODING[MAHAMANTRA_WORD_PATTERN[i]]
            by_name[enc].append(unpack(entry).vamsi)

        for enc, vals in by_name.items():
            assert len(vals) == len(set(vals)), f"Name {enc} has duplicate VAMSI"

    def test_cycle_xor_nonzero(self):
        """Full cycle XOR must be non-zero (the flute is not silent)."""
        xor = 0
        for entry in THE_FLUTE_CYCLE:
            xor ^= entry & DIW_MASK
        assert xor != 0, "Cycle XOR is zero"
        assert xor <= DIW_MASK, "Cycle XOR exceeds 19 bits"


# =============================================================================
# STEP / CYCLE
# =============================================================================


class TestStep:
    """VenuOrchestrator.step() — O(1) LUT lookup."""

    def test_step_returns_valid_diw(self, orch: VenuOrchestrator):
        diw = orch.step()
        core = diw & DIW_MASK
        assert core <= DIW_MASK
        assert core != 0

    def test_step_advances_tick(self, orch: VenuOrchestrator):
        assert orch.tick == 0
        orch.step()
        assert orch.tick == 1

    def test_step_wraps_at_cosmic_frame(self, orch: VenuOrchestrator):
        orch._tick = COSMIC_FRAME - 1
        orch.step()
        assert orch.tick == 0

    def test_step_sequence_matches_lut(self, orch: VenuOrchestrator):
        """First WORDS steps must match THE_FLUTE_CYCLE exactly (mode=0)."""
        for i in range(WORDS):
            diw = orch.step()
            expected = THE_FLUTE_CYCLE[i]
            assert diw == expected, f"Step {i}: got {hex(diw)}, expected {hex(expected)}"

    def test_step_repeats_after_words(self, orch: VenuOrchestrator):
        """Pattern repeats every WORDS steps."""
        first_round = [orch.step() for _ in range(WORDS)]
        second_round = [orch.step() for _ in range(WORDS)]
        assert first_round == second_round

    def test_step_with_mode_injects_cluster_bits(self, orch: VenuOrchestrator):
        orch.set_mode(2)  # CHORUS
        diw = orch.step()
        # Mode should be in cluster bits (bits 23-26)
        from vibe_core.mahamantra.protocols.diw import CLUSTER_SHIFT
        cluster = (diw >> CLUSTER_SHIFT) & 0xF
        assert cluster == 2

    def test_step_mode_zero_no_cluster(self, orch: VenuOrchestrator):
        """Mode 0 (SOLO) should not set any cluster bits."""
        diw = orch.step()
        from vibe_core.mahamantra.protocols.diw import CLUSTER_SHIFT
        cluster = (diw >> CLUSTER_SHIFT) & 0xF
        assert cluster == 0


class TestCycle:
    """VenuOrchestrator.cycle() — full 16-step XOR."""

    def test_cycle_returns_nonzero(self, orch: VenuOrchestrator):
        result = orch.cycle()
        assert result != 0

    def test_cycle_fits_19_bits(self, orch: VenuOrchestrator):
        result = orch.cycle()
        assert result <= DIW_MASK

    def test_cycle_advances_tick_by_words(self, orch: VenuOrchestrator):
        orch.cycle()
        assert orch.tick == WORDS

    def test_cycle_deterministic(self, orch: VenuOrchestrator):
        r1 = orch.cycle()
        orch.reset()
        r2 = orch.cycle()
        assert r1 == r2

    def test_cycle_matches_manual_xor(self, orch: VenuOrchestrator):
        """cycle() must equal XOR of all LUT entries."""
        expected = 0
        for entry in THE_FLUTE_CYCLE:
            expected ^= entry & DIW_MASK
        assert orch.cycle() == expected


# =============================================================================
# ROUTE
# =============================================================================


class TestRoute:
    """VenuOrchestrator.route() — seed → (venu, vamsi, murali)."""

    def test_route_returns_triple(self, orch: VenuOrchestrator):
        result = orch.route(42)
        assert len(result) == 3

    def test_route_venu_fits_6_bits(self, orch: VenuOrchestrator):
        for seed in range(256):
            v, _, _ = orch.route(seed)
            assert v <= VENU_MASK, f"seed={seed}: venu={v} exceeds 6 bits"

    def test_route_vamsi_fits_9_bits(self, orch: VenuOrchestrator):
        for seed in range(256):
            _, va, _ = orch.route(seed)
            assert va <= VAMSI_MASK, f"seed={seed}: vamsi={va} exceeds 9 bits"

    def test_route_murali_fits_4_bits(self, orch: VenuOrchestrator):
        for seed in range(256):
            _, _, m = orch.route(seed)
            assert m <= MURALI_MASK, f"seed={seed}: murali={m} exceeds 4 bits"

    def test_route_deterministic(self, orch: VenuOrchestrator):
        assert orch.route(137) == orch.route(137)

    def test_route_full_murali_coverage(self, orch: VenuOrchestrator):
        """route() must reach all 16 MURALI values over a range of seeds."""
        murali_vals = {orch.route(s)[2] for s in range(256)}
        assert len(murali_vals) == (1 << MURALI_HOLES), (
            f"Only {len(murali_vals)} MURALI values reachable, need {1 << MURALI_HOLES}"
        )


# =============================================================================
# SPELL (Sanskrit → DIW)
# =============================================================================


class TestSpell:
    """VenuOrchestrator.spell() — RAMA coordinates → DIW sequence."""

    def test_spell_empty_coords(self, orch: VenuOrchestrator):
        result = orch.spell(())
        assert result == ()

    def test_spell_single_coord(self, orch: VenuOrchestrator):
        result = orch.spell((7,))
        assert len(result) == 1
        parts = unpack(result[0])
        assert parts.venu == 7  # coord & VENU_MASK

    def test_spell_length_matches_coords(self, orch: VenuOrchestrator):
        coords = tuple(range(10))
        result = orch.spell(coords)
        assert len(result) == len(coords)

    def test_spell_all_diw_fit_19_bits(self, orch: VenuOrchestrator):
        coords = tuple(range(49))  # all RAMA coordinates
        result = orch.spell(coords)
        for i, diw in enumerate(result):
            assert diw <= DIW_MASK, f"coord {i}: DIW {hex(diw)} exceeds 19 bits"

    def test_spell_venu_is_coord_masked(self, orch: VenuOrchestrator):
        """VENU field must be coord & VENU_MASK."""
        for coord in range(49):
            result = orch.spell((coord,))
            parts = unpack(result[0])
            assert parts.venu == (coord & VENU_MASK), (
                f"coord={coord}: venu={parts.venu}, expected {coord & VENU_MASK}"
            )

    def test_spell_advances_tick(self, orch: VenuOrchestrator):
        coords = tuple(range(5))
        orch.spell(coords)
        assert orch.tick == 5

    def test_spell_murali_phases_sequential(self, orch: VenuOrchestrator):
        """MURALI should encode sequential phases within the word."""
        coords = tuple(range(16))
        result = orch.spell(coords)
        quarter_size = len(coords) // QUARTERS
        for i, diw in enumerate(result):
            expected_phase = min(i // quarter_size, QUARTERS - 1)
            actual = unpack(diw).murali
            assert actual == expected_phase, (
                f"Position {i}: murali={actual}, expected phase {expected_phase}"
            )


# =============================================================================
# HARMONIZE (pack_full wrapper)
# =============================================================================


class TestHarmonize:
    """VenuOrchestrator.harmonize() — 32-bit transport word."""

    def test_harmonize_basic(self, orch: VenuOrchestrator):
        word = orch.harmonize(10, 200, 3)
        parts = unpack(word)
        assert parts.venu == 10
        assert parts.vamsi == 200
        assert parts.murali == 3

    def test_harmonize_with_velocity(self, orch: VenuOrchestrator):
        word = orch.harmonize(0, 0, 0, velocity=15)
        from vibe_core.mahamantra.protocols.diw import VELOCITY_SHIFT
        vel = (word >> VELOCITY_SHIFT) & 0xF
        assert vel == 15

    def test_harmonize_with_sunya(self, orch: VenuOrchestrator):
        word = orch.harmonize(0, 0, 0, sunya=True)
        assert orch.is_sunya(word)

    def test_harmonize_without_sunya(self, orch: VenuOrchestrator):
        word = orch.harmonize(10, 200, 3)
        assert not orch.is_sunya(word)


# =============================================================================
# VERIFY DIVINITY
# =============================================================================


class TestVerifyDivinity:
    """VenuOrchestrator.verify_divinity() — structural proof."""

    def test_verify_passes(self, orch: VenuOrchestrator):
        assert orch.verify_divinity() is True

    def test_verify_idempotent(self, orch: VenuOrchestrator):
        assert orch.verify_divinity() is True
        assert orch.verify_divinity() is True


# =============================================================================
# PERSISTENCE (to_bytes / from_bytes)
# =============================================================================


class TestPersistence:
    """Serialization round-trip."""

    def test_roundtrip_fresh(self, orch: VenuOrchestrator):
        data = orch.to_bytes()
        assert len(data) == 24  # 3 × Q (8 bytes each)

        restored = VenuOrchestrator()
        restored.from_bytes(data)
        assert restored.tick == 0
        assert restored.mode == 0

    def test_roundtrip_after_steps(self, orch: VenuOrchestrator):
        for _ in range(7):
            orch.step()
        orch.set_mode(2)

        data = orch.to_bytes()
        restored = VenuOrchestrator()
        restored.from_bytes(data)

        assert restored.tick == orch.tick
        assert restored.mode == orch.mode

    def test_from_bytes_too_short_raises(self, orch: VenuOrchestrator):
        with pytest.raises(ValueError, match="Data too short"):
            orch.from_bytes(b"\x00" * 8)

    def test_from_bytes_legacy_16_bytes(self, orch: VenuOrchestrator):
        """16-byte legacy format should restore tick+prev_state, mode=0."""
        legacy = struct.pack("<QQ", 42, 999)
        orch.from_bytes(legacy)
        assert orch.tick == 42
        assert orch.mode == 0  # Default


# =============================================================================
# RESET
# =============================================================================


class TestReset:
    def test_reset_clears_state(self, orch: VenuOrchestrator):
        for _ in range(10):
            orch.step()
        orch.set_mode(2)
        orch.reset()

        assert orch.tick == 0
        assert orch.mode == 0


# =============================================================================
# EXTRACT_DIW / IS_SUNYA (static methods)
# =============================================================================


class TestStaticMethods:
    def test_extract_diw(self, orch: VenuOrchestrator):
        full = orch.harmonize(10, 200, 3, velocity=15, cluster_route=7)
        core = orch.extract_diw(full)
        assert core == pack(10, 200, 3)

    def test_is_sunya_true(self, orch: VenuOrchestrator):
        word = orch.harmonize(0, 0, 0, sunya=True)
        assert orch.is_sunya(word) is True

    def test_is_sunya_false(self, orch: VenuOrchestrator):
        word = orch.harmonize(10, 200, 3)
        assert orch.is_sunya(word) is False


# =============================================================================
# DIW PROTOCOL (pack/unpack round-trip)
# =============================================================================


class TestDIWProtocol:
    """Verify the diw.py pack/unpack contract."""

    def test_pack_unpack_roundtrip(self):
        for v in range(0, 64, 7):
            for va in range(0, 512, 50):
                for m in range(4):
                    word = pack(v, va, m)
                    parts = unpack(word)
                    assert parts.venu == v
                    assert parts.vamsi == va
                    assert parts.murali == m

    def test_pack_masks_overflow(self):
        """Values exceeding field width should be masked."""
        word = pack(0xFF, 0xFFF, 0xFF)
        parts = unpack(word)
        assert parts.venu == 0xFF & VENU_MASK  # 63
        assert parts.vamsi == 0xFFF & VAMSI_MASK  # 511
        assert parts.murali == 0xFF & MURALI_MASK  # 15

    def test_19_bit_isomorphism(self):
        """19 = GITA_CHAPTERS(18) + KSETRAJNA(1) = VENU(6) + VAMSI(9) + MURALI(4)."""
        assert FLUTE_HOLES_SUM == VENU_HOLES + VAMSI_HOLES + MURALI_HOLES == 19


# =============================================================================
# INPUT VALIDATION (Hardening)
# =============================================================================


class TestRouteValidation:
    """route() must reject invalid inputs."""

    def test_route_rejects_negative_seed(self, orch: VenuOrchestrator):
        with pytest.raises(ValueError, match="non-negative"):
            orch.route(-1)

    def test_route_rejects_float(self, orch: VenuOrchestrator):
        with pytest.raises(TypeError, match="int"):
            orch.route(3.14)  # type: ignore

    def test_route_rejects_string(self, orch: VenuOrchestrator):
        with pytest.raises(TypeError, match="int"):
            orch.route("42")  # type: ignore

    def test_route_accepts_zero(self, orch: VenuOrchestrator):
        v, va, m = orch.route(0)
        assert v <= VENU_MASK
        assert va <= VAMSI_MASK
        assert m <= MURALI_MASK

    def test_route_accepts_large_seed(self, orch: VenuOrchestrator):
        """Large seeds should wrap via modular arithmetic, not crash."""
        v, va, m = orch.route(10**9)
        assert v <= VENU_MASK
        assert va <= VAMSI_MASK
        assert m <= MURALI_MASK


class TestSpellValidation:
    """spell() must reject invalid inputs."""

    def test_spell_rejects_negative_cycle(self, orch: VenuOrchestrator):
        with pytest.raises(ValueError, match="non-negative"):
            orch.spell((1, 2, 3), cycle=-1)

    def test_spell_large_coords_masked(self, orch: VenuOrchestrator):
        """Coords > VENU_MASK should be masked to 6 bits."""
        result = orch.spell((100,))
        parts = unpack(result[0])
        assert parts.venu == (100 & VENU_MASK)

    def test_spell_zero_coords(self, orch: VenuOrchestrator):
        """All-zero coords should produce valid DIWs."""
        result = orch.spell((0, 0, 0))
        for diw in result:
            assert diw <= DIW_MASK


class TestSetModeValidation:
    """set_mode() must reject invalid inputs."""

    def test_set_mode_rejects_negative(self, orch: VenuOrchestrator):
        with pytest.raises(ValueError):
            orch.set_mode(-1)

    def test_set_mode_rejects_too_high(self, orch: VenuOrchestrator):
        with pytest.raises(ValueError):
            orch.set_mode(3)

    def test_set_mode_rejects_float(self, orch: VenuOrchestrator):
        with pytest.raises(TypeError, match="int"):
            orch.set_mode(1.0)  # type: ignore

    def test_set_mode_rejects_string(self, orch: VenuOrchestrator):
        with pytest.raises(TypeError, match="int"):
            orch.set_mode("CHORUS")  # type: ignore


# =============================================================================
# CORRUPT STATE RECOVERY (from_bytes hardening)
# =============================================================================


class TestFromBytesHardening:
    """from_bytes() must clamp corrupt values to valid SSOT ranges."""

    def test_corrupt_tick_clamped(self, orch: VenuOrchestrator):
        """Tick exceeding COSMIC_FRAME should be wrapped via modulo."""
        from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME as CF
        corrupt = struct.pack("<QQQ", CF + 999, 0, 0)
        orch.from_bytes(corrupt)
        assert orch.tick < CF

    def test_corrupt_mode_clamped(self, orch: VenuOrchestrator):
        """Mode exceeding HALVES should be clamped."""
        corrupt = struct.pack("<QQQ", 0, 0, 999)
        orch.from_bytes(corrupt)
        from vibe_core.mahamantra.protocols._seed import HALVES as H
        assert orch.mode <= H

    def test_corrupt_prev_state_masked(self, orch: VenuOrchestrator):
        """prev_state exceeding 19 bits should be masked."""
        corrupt = struct.pack("<QQQ", 0, 0xFFFFFFFF, 0)
        orch.from_bytes(corrupt)
        # prev_state is private, verify via roundtrip
        data = orch.to_bytes()
        _, prev, _ = struct.unpack("<QQQ", data)
        assert prev <= DIW_MASK

    def test_legacy_16_bytes_clamped(self, orch: VenuOrchestrator):
        """Legacy 16-byte format should also clamp values."""
        from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME as CF
        legacy = struct.pack("<QQ", CF + 1, 0xFFFFFFFF)
        orch.from_bytes(legacy)
        assert orch.tick < CF
        assert orch.mode == 0


# =============================================================================
# DIW SUBSCRIBER DISPATCH (Krishna's Flute -> Jivas Dance)
# =============================================================================


class _MockSubscriber:
    """Test subscriber that records all DIW events."""

    def __init__(self, name: str = "mock"):
        self._name = name
        self.events: list[DIWEvent] = []

    @property
    def subscriber_name(self) -> str:
        return self._name

    def on_diw(self, event: DIWEvent) -> None:
        self.events.append(event)


class _FailingSubscriber:
    """Subscriber that raises on every event."""

    @property
    def subscriber_name(self) -> str:
        return "failing"

    def on_diw(self, event: DIWEvent) -> None:
        raise RuntimeError("I broke")


class TestDIWSubscriberProtocol:
    """DIWSubscriberProtocol must be runtime-checkable."""

    def test_mock_implements_protocol(self):
        sub = _MockSubscriber()
        assert isinstance(sub, DIWSubscriberProtocol)

    def test_plain_object_does_not_implement(self):
        assert not isinstance(object(), DIWSubscriberProtocol)


class TestSubscriberRegistration:
    """subscribe() / unsubscribe() management."""

    def test_subscribe_increments_count(self, orch: VenuOrchestrator):
        assert orch.subscriber_count == 0
        sub = _MockSubscriber()
        orch.subscribe(sub)
        assert orch.subscriber_count == 1

    def test_unsubscribe_decrements_count(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.unsubscribe(sub)
        assert orch.subscriber_count == 0

    def test_unsubscribe_idempotent(self, orch: VenuOrchestrator):
        """Unsubscribing a non-subscriber should not raise."""
        sub = _MockSubscriber()
        orch.unsubscribe(sub)  # no-op
        assert orch.subscriber_count == 0

    def test_subscribe_rejects_non_protocol(self, orch: VenuOrchestrator):
        with pytest.raises(TypeError, match="DIWSubscriberProtocol"):
            orch.subscribe(object())  # type: ignore

    def test_multiple_subscribers(self, orch: VenuOrchestrator):
        subs = [_MockSubscriber(f"sub_{i}") for i in range(5)]
        for s in subs:
            orch.subscribe(s)
        assert orch.subscriber_count == 5

    def test_reset_preserves_subscribers(self, orch: VenuOrchestrator):
        """Subscribers are wiring, not state. reset() must preserve them."""
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.reset()
        assert orch.subscriber_count == 1


class TestDIWDispatch:
    """step() must dispatch DIWEvent to all subscribers."""

    def test_step_dispatches_event(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.step()
        assert len(sub.events) == 1

    def test_event_has_all_fields(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.step()
        event = sub.events[0]
        assert "diw" in event
        assert "tick" in event
        assert "position" in event
        assert "phase" in event
        assert "venu" in event
        assert "vamsi" in event
        assert "murali" in event
        assert "mode" in event

    def test_event_diw_matches_lut(self, orch: VenuOrchestrator):
        """The DIW in the event must match THE_FLUTE_CYCLE[tick]."""
        sub = _MockSubscriber()
        orch.subscribe(sub)
        for i in range(WORDS):
            orch.step()
        for i, event in enumerate(sub.events):
            expected = THE_FLUTE_CYCLE[i] & DIW_MASK
            assert event["diw"] == expected, f"tick {i}: {event['diw']} != {expected}"

    def test_event_components_match_unpack(self, orch: VenuOrchestrator):
        """venu/vamsi/murali in event must match unpack(diw)."""
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.step()
        event = sub.events[0]
        parts = unpack(event["diw"])
        assert event["venu"] == parts.venu
        assert event["vamsi"] == parts.vamsi
        assert event["murali"] == parts.murali

    def test_event_position_is_tick_mod_words(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        for _ in range(WORDS * 2):
            orch.step()
        for event in sub.events:
            assert event["position"] == event["tick"] % WORDS

    def test_event_phase_matches_quarter(self, orch: VenuOrchestrator):
        """phase must equal MURALI = position // (WORDS // QUARTERS)."""
        sub = _MockSubscriber()
        orch.subscribe(sub)
        for _ in range(WORDS):
            orch.step()
        for event in sub.events:
            expected_quarter = event["position"] // (WORDS // QUARTERS)
            assert event["phase"] == expected_quarter

    def test_event_mode_reflects_set_mode(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        orch.set_mode(2)  # Chorus
        orch.step()
        assert sub.events[0]["mode"] == 2

    def test_multiple_subscribers_all_receive(self, orch: VenuOrchestrator):
        subs = [_MockSubscriber(f"s{i}") for i in range(3)]
        for s in subs:
            orch.subscribe(s)
        orch.step()
        for s in subs:
            assert len(s.events) == 1
            assert s.events[0]["diw"] == subs[0].events[0]["diw"]

    def test_no_subscribers_no_crash(self, orch: VenuOrchestrator):
        """step() with zero subscribers must still work."""
        diw = orch.step()
        assert diw > 0

    def test_full_cycle_deterministic(self, orch: VenuOrchestrator):
        """Two orchestrators with same state must produce identical events."""
        sub1 = _MockSubscriber("a")
        sub2 = _MockSubscriber("b")
        orch1 = VenuOrchestrator()
        orch2 = VenuOrchestrator()
        orch1.subscribe(sub1)
        orch2.subscribe(sub2)
        for _ in range(WORDS):
            orch1.step()
            orch2.step()
        for i in range(WORDS):
            assert sub1.events[i] == sub2.events[i], f"Divergence at tick {i}"


class TestDIWDispatchErrorIsolation:
    """A failing subscriber must not stop the flute or other subscribers."""

    def test_failing_subscriber_does_not_stop_flute(self, orch: VenuOrchestrator):
        bad = _FailingSubscriber()
        orch.subscribe(bad)
        diw = orch.step()  # must not raise
        assert diw > 0

    def test_failing_subscriber_does_not_block_others(self, orch: VenuOrchestrator):
        good = _MockSubscriber("good")
        bad = _FailingSubscriber()
        orch.subscribe(bad)
        orch.subscribe(good)
        orch.step()
        assert len(good.events) == 1  # good still received the event

    def test_tick_advances_despite_failure(self, orch: VenuOrchestrator):
        bad = _FailingSubscriber()
        orch.subscribe(bad)
        orch.step()
        assert orch.tick == 1  # tick advanced


class TestSpellDispatch:
    """spell() must also dispatch DIW events per phoneme."""

    def test_spell_dispatches_per_coord(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        coords = (10, 20, 30, 40)
        orch.spell(coords)
        assert len(sub.events) == len(coords)

    def test_spell_events_have_correct_venu(self, orch: VenuOrchestrator):
        sub = _MockSubscriber()
        orch.subscribe(sub)
        coords = (5, 15, 48)
        orch.spell(coords)
        for i, event in enumerate(sub.events):
            assert event["venu"] == (coords[i] & VENU_MASK)
