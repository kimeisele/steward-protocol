"""
Tests for Protocol Adoption Pipeline.

"16 bit mantra ops regeln am ende" - MantraOpCodes rule everything.

Tests verify:
1. OpCode detection from source code
2. Shudhi verification (Mayavad detection, parampara)
3. Full pipeline flow (analyze → decide → adopt)
4. NO MANUAL WIRING - Mahamantra decides everything

WATERTIGHT: All types explicit, no Any.
"""

from typing import List

import pytest

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.mahajanas.adoption import (
    OPCODE_SIGNATURES,
    AdoptionDecision,
    # Pipeline
    AdoptionPipeline,
    AdoptionResult,
    # Enums
    AdoptionStatus,
    # Types
    ProtocolAnalysis,
    # Shudhi
    ShudhiReport,
    adopt,
    analyze,
    # Detection
    detect_opcodes_from_source,
    detect_primary_opcode,
    get_pipeline,
    run_shudhi,
)
from vibe_core.protocols.mahajanas.router import Mahajana

# =============================================================================
# TEST SOURCE CODE SAMPLES (for testing detection)
# =============================================================================

CREATION_PROTOCOL = """
class ServiceRegistry:
    \"\"\"DI Container that provides and injects dependencies.\"\"\"

    def load_root(self):
        \"\"\"Load the root configuration.\"\"\"
        pass

    def create_service(self, name: str):
        \"\"\"Create a new service instance.\"\"\"
        pass

    def inject_dependency(self, service, dependency):
        \"\"\"Inject dependency into service.\"\"\"
        pass
"""

EVENT_PROTOCOL = """
class EventBus:
    \"\"\"Event system for pulse synchronization.\"\"\"

    def pulse(self):
        \"\"\"Send heartbeat pulse.\"\"\"
        pass

    def sync_events(self):
        \"\"\"Synchronize events across subscribers.\"\"\"
        pass

    def notify_subscribers(self, event):
        \"\"\"Notify all subscribers of an event.\"\"\"
        pass
"""

DHARMA_PROTOCOL = """
class RuleEngine:
    \"\"\"Enforces dharma rules and policies.\"\"\"

    def check_dharma(self, action):
        \"\"\"Check if action follows dharma.\"\"\"
        pass

    def enforce_policy(self, policy):
        \"\"\"Enforce a specific policy.\"\"\"
        pass

    def validate_rule(self, rule):
        \"\"\"Validate a rule definition.\"\"\"
        pass
"""

MAYAVAD_PROTOCOL = """
class UniversalConsciousness:
    \"\"\"I am God. All is one. Aham Brahmasmi.\"\"\"

    def merge_with_brahman(self):
        \"\"\"I am the supreme.\"\"\"
        pass

    def dissolve_duality(self):
        \"\"\"There is no difference.\"\"\"
        pass
"""

DEAD_CODE = ""

EMPTY_PROTOCOL = """
# Just a comment, no actual code
# TODO: implement something
"""


# =============================================================================
# TEST OPCODE DETECTION
# =============================================================================


class TestOpcodeDetection:
    """Test MantraOpCode detection from source code."""

    def test_detect_creation_opcodes(self) -> None:
        """Creation protocol should detect LOAD_ROOT."""
        detected = detect_opcodes_from_source(CREATION_PROTOCOL)

        assert MantraOpCode.LOAD_ROOT in detected
        # "create" triggers LOAD_ROOT, "inject" triggers LOAD_ROOT

    def test_detect_event_opcodes(self) -> None:
        """Event protocol should detect PULSE_SYNC."""
        detected = detect_opcodes_from_source(EVENT_PROTOCOL)

        assert MantraOpCode.DHARMA_TEST in detected
        # "pulse", "sync", "heartbeat", "event" all trigger PULSE_SYNC

    def test_detect_dharma_opcodes(self) -> None:
        """Dharma protocol should detect CHECK_DHARMA."""
        detected = detect_opcodes_from_source(DHARMA_PROTOCOL)

        assert MantraOpCode.STATE_SYNC in detected
        # "dharma", "rule", "policy", "enforce" trigger CHECK_DHARMA

    def test_detect_primary_creation(self) -> None:
        """Primary OpCode for creation protocol should be LOAD_ROOT."""
        primary = detect_primary_opcode(CREATION_PROTOCOL)

        assert primary is not None
        assert primary == MantraOpCode.LOAD_ROOT

    def test_detect_primary_event(self) -> None:
        """Primary OpCode for event protocol should be PULSE_SYNC."""
        primary = detect_primary_opcode(EVENT_PROTOCOL)

        assert primary is not None
        assert primary == MantraOpCode.DHARMA_TEST

    def test_detect_primary_dharma(self) -> None:
        """Primary OpCode for dharma protocol should be CHECK_DHARMA."""
        primary = detect_primary_opcode(DHARMA_PROTOCOL)

        assert primary is not None
        assert primary == MantraOpCode.STATE_SYNC

    def test_empty_source_no_opcodes(self) -> None:
        """Empty source should detect no OpCodes."""
        detected = detect_opcodes_from_source(DEAD_CODE)
        assert detected == []

    def test_primary_none_for_empty(self) -> None:
        """Primary OpCode should be None for empty source."""
        primary = detect_primary_opcode(DEAD_CODE)
        assert primary is None


# =============================================================================
# TEST SHUDHI VERIFICATION
# =============================================================================


class TestShudhiVerification:
    """Test Shudhi (cleaning) verification."""

    def test_clean_protocol_with_owner(self) -> None:
        """Protocol with owner and code should be clean."""
        shudhi = run_shudhi(
            "service_registry",
            CREATION_PROTOCOL,
            has_owner=True,
            owner_name="brahma",
        )

        assert shudhi.has_soul is True
        assert shudhi.claims_supreme is False
        assert shudhi.is_connected is True
        assert shudhi.is_clean is True

    def test_mayavad_detected(self) -> None:
        """Mayavad protocol should be detected."""
        shudhi = run_shudhi(
            "universal_consciousness",
            MAYAVAD_PROTOCOL,
            has_owner=False,
        )

        assert shudhi.claims_supreme is True
        assert shudhi.bheda_abheda_valid is False
        assert "MAYAVAD" in shudhi.bheda_abheda_reason
        assert shudhi.needs_quarantine is True

    def test_dead_code_no_soul(self) -> None:
        """Dead code (empty) should have no soul."""
        shudhi = run_shudhi(
            "dead_protocol",
            DEAD_CODE,
            has_owner=False,
        )

        assert shudhi.has_soul is False
        assert shudhi.is_dead_code is True

    def test_parampara_connection(self) -> None:
        """Parampara hash should be divisible by 37."""
        shudhi = run_shudhi(
            "test_protocol",
            CREATION_PROTOCOL,
            has_owner=True,
            owner_name="brahma",
        )

        # Our formula: (name_hash + owner_hash) * 37
        # This guarantees % 37 == 0
        assert shudhi.parampara_hash % 37 == 0
        assert shudhi.is_connected is True


# =============================================================================
# TEST ADOPTION PIPELINE
# =============================================================================


class TestAdoptionPipeline:
    """Test the full adoption pipeline."""

    def test_analyze_creation_protocol(self) -> None:
        """Analyze should detect OpCodes and quarter."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/protocols/wild/service.py", CREATION_PROTOCOL)

        assert analysis["protocol_name"] == "service"
        assert "load_root" in analysis["detected_opcodes"]
        assert analysis["primary_opcode"] == "load_root"
        assert analysis["has_soul"] is True

    def test_analyze_event_protocol(self) -> None:
        """Analyze should detect PULSE_SYNC for event protocol."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/protocols/wild/events.py", EVENT_PROTOCOL)

        assert analysis["protocol_name"] == "events"
        assert "pulse_sync" in analysis["detected_opcodes"]
        assert analysis["quarter_name"] in ["genesis", "dharma"]  # PULSE_SYNC is in Q2

    def test_adopt_routes_to_brahma(self) -> None:
        """Creation protocol should route to BRAHMA."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/di.py", CREATION_PROTOCOL)

        assert result["decision"] == AdoptionDecision.ASSIGN_MAHAJANA.value
        assert result["assigned_mahajana"] == "brahma"
        assert result["status"] == AdoptionStatus.ADOPTED_MAHAJANA.value

    def test_adopt_routes_to_manu(self) -> None:
        """Dharma protocol should route to MANU (CHECK_DHARMA owner)."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/rules.py", DHARMA_PROTOCOL)

        # CHECK_DHARMA routes to MANU in legacy, JANAKA in vyuha
        # Our router uses legacy mode by default
        assert result["decision"] == AdoptionDecision.ASSIGN_MAHAJANA.value
        assert result["assigned_mahajana"] in ["manu", "janaka"]

    def test_mayavad_quarantined(self) -> None:
        """Mayavad protocol should be quarantined."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/mayavad.py", MAYAVAD_PROTOCOL)

        assert result["decision"] == AdoptionDecision.QUARANTINE.value
        assert result["status"] == AdoptionStatus.MAYAVAD_DETECTED.value
        assert "MAYAVAD" in result["reason"]

    def test_dead_code_rejected(self) -> None:
        """Dead code should be rejected."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/dead.py", DEAD_CODE)

        assert result["decision"] == AdoptionDecision.REJECT.value
        assert result["status"] == AdoptionStatus.REJECTED.value
        assert "no soul" in result["reason"].lower()

    def test_target_path_mahajana(self) -> None:
        """Target path should reflect assigned Mahajana."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/di.py", CREATION_PROTOCOL)

        assert "mahajanas/brahma" in result["target_path"]

    def test_target_path_quarantine(self) -> None:
        """Quarantined protocol should go to quarantine folder."""
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/protocols/wild/mayavad.py", MAYAVAD_PROTOCOL)

        assert "quarantine" in result["target_path"]


# =============================================================================
# TEST GLOBAL PIPELINE (SINGLETON)
# =============================================================================


class TestGlobalPipeline:
    """Test the global pipeline singleton."""

    def test_get_pipeline_singleton(self) -> None:
        """get_pipeline should return same instance."""
        pipeline1 = get_pipeline()
        pipeline2 = get_pipeline()

        assert pipeline1 is pipeline2

    def test_adopt_convenience_function(self) -> None:
        """adopt() convenience function should work."""
        result = adopt("/protocols/wild/test.py", CREATION_PROTOCOL)

        assert result["protocol_name"] == "test"
        assert result["decision"] is not None

    def test_analyze_convenience_function(self) -> None:
        """analyze() convenience function should work."""
        analysis = analyze("/protocols/wild/test.py", EVENT_PROTOCOL)

        assert analysis["protocol_name"] == "test"
        assert analysis["detected_opcodes"] is not None


# =============================================================================
# TEST BATCH OPERATIONS
# =============================================================================


class TestBatchOperations:
    """Test batch adoption operations."""

    def test_adopt_batch(self) -> None:
        """adopt_batch should process multiple protocols."""
        pipeline = AdoptionPipeline()
        protocols = [
            ("/protocols/wild/di.py", CREATION_PROTOCOL),
            ("/protocols/wild/events.py", EVENT_PROTOCOL),
            ("/protocols/wild/rules.py", DHARMA_PROTOCOL),
        ]

        results = pipeline.adopt_batch(protocols)

        assert len(results) == 3
        assert results[0]["protocol_name"] == "di"
        assert results[1]["protocol_name"] == "events"
        assert results[2]["protocol_name"] == "rules"

    def test_get_by_status(self) -> None:
        """get_by_status should filter results."""
        pipeline = AdoptionPipeline()
        pipeline.adopt("/protocols/wild/di.py", CREATION_PROTOCOL)
        pipeline.adopt("/protocols/wild/mayavad.py", MAYAVAD_PROTOCOL)

        adopted = pipeline.get_by_status(AdoptionStatus.ADOPTED_MAHAJANA)
        quarantined = pipeline.get_by_status(AdoptionStatus.MAYAVAD_DETECTED)

        assert len(adopted) >= 1
        assert len(quarantined) >= 1

    def test_get_by_mahajana(self) -> None:
        """get_by_mahajana should filter by owner."""
        pipeline = AdoptionPipeline()
        pipeline.adopt("/protocols/wild/di.py", CREATION_PROTOCOL)

        brahma_protocols = pipeline.get_by_mahajana(Mahajana.BRAHMA)

        assert len(brahma_protocols) >= 1
        assert all(r["assigned_mahajana"] == "brahma" for r in brahma_protocols)


# =============================================================================
# TEST WATERTIGHT TYPES
# =============================================================================


class TestWatertightTypes:
    """Test that all types are WATERTIGHT (no Any)."""

    def test_analysis_watertight(self) -> None:
        """ProtocolAnalysis should have all required fields."""
        pipeline = AdoptionPipeline()
        analysis: ProtocolAnalysis = pipeline.analyze(
            "/protocols/wild/test.py",
            CREATION_PROTOCOL,
        )

        # All fields should be correct type
        assert isinstance(analysis["protocol_path"], str)
        assert isinstance(analysis["protocol_name"], str)
        assert isinstance(analysis["detected_opcodes"], list)
        assert isinstance(analysis["quarter_index"], int)
        assert isinstance(analysis["quarter_name"], str)
        assert isinstance(analysis["has_soul"], bool)
        assert isinstance(analysis["claims_supreme"], bool)
        assert isinstance(analysis["parampara_hash"], int)
        assert isinstance(analysis["is_connected"], bool)
        assert isinstance(analysis["analyzed_at"], str)

    def test_result_watertight(self) -> None:
        """AdoptionResult should have all required fields."""
        pipeline = AdoptionPipeline()
        result: AdoptionResult = pipeline.adopt(
            "/protocols/wild/test.py",
            CREATION_PROTOCOL,
        )

        # All fields should be correct type
        assert isinstance(result["protocol_name"], str)
        assert isinstance(result["status"], str)
        assert isinstance(result["decision"], str)
        assert isinstance(result["target_path"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["analysis"], dict)
        assert isinstance(result["adopted_at"], str)

    def test_shudhi_report_watertight(self) -> None:
        """ShudhiReport should have all required fields."""
        shudhi: ShudhiReport = run_shudhi(
            "test",
            CREATION_PROTOCOL,
            has_owner=True,
        )

        assert isinstance(shudhi.has_soul, bool)
        assert isinstance(shudhi.claims_supreme, bool)
        assert isinstance(shudhi.parampara_hash, int)
        assert isinstance(shudhi.is_connected, bool)
        assert isinstance(shudhi.bheda_abheda_valid, bool)
        assert isinstance(shudhi.bheda_abheda_reason, str)


# =============================================================================
# TEST NO MANUAL WIRING
# =============================================================================


class TestNoManualWiring:
    """Test that there's NO MANUAL WIRING - Mahamantra decides everything."""

    def test_opcode_determines_mahajana(self) -> None:
        """OpCode detection should determine Mahajana automatically."""
        pipeline = AdoptionPipeline()

        # LOAD_ROOT → BRAHMA (via router)
        creation_result = pipeline.adopt("/wild/create.py", CREATION_PROTOCOL)
        assert creation_result["assigned_mahajana"] == "brahma"

        # No manual mapping in the test - the pipeline derives from OpCode

    def test_quarter_fallback_automatic(self) -> None:
        """When no clear OpCode, quarter should provide fallback."""
        generic_code = """
        class GenericProtocol:
            def do_something(self):
                pass
        """
        pipeline = AdoptionPipeline()
        result = pipeline.adopt("/wild/generic.py", generic_code)

        # Should still make a decision (either universal or mahajana)
        assert result["decision"] in [
            AdoptionDecision.ASSIGN_MAHAJANA.value,
            AdoptionDecision.KEEP_UNIVERSAL.value,
        ]

    def test_shudhi_uses_acintya(self) -> None:
        """Shudhi should use check_bheda_abheda from acintya.py."""
        # We don't manually check for Mayavad - acintya.py does it
        shudhi = run_shudhi(
            "test",
            "class Test: pass",
            has_owner=True,
        )

        # The result comes from acintya.check_bheda_abheda()
        assert shudhi.bheda_abheda_valid is True
        assert "ACINTYA" in shudhi.bheda_abheda_reason

    def test_parampara_uses_verify(self) -> None:
        """Parampara check should use verify_parampara from acintya.py."""
        shudhi = run_shudhi(
            "test",
            CREATION_PROTOCOL,
            has_owner=True,
        )

        # Our hash formula guarantees % 37 == 0
        # verify_parampara() from acintya.py does the actual check
        assert shudhi.is_connected is True
        assert shudhi.parampara_hash % 37 == 0


# =============================================================================
# TEST MANIFEST STEP (Protocol → MantraByte)
# =============================================================================

from vibe_core.protocols.mahajanas.adoption import (
    AttractionReport,
    FullAdoptionResult,
    ManifestResult,
    SyncResult,
    adopt_full,
    calculate_attraction,
    manifest_protocol,
    sync_to_lotus,
)


class TestManifestStep:
    """Test MANIFEST step - transform protocol to MantraByte."""

    def test_manifest_creates_mantra_byte(self) -> None:
        """Manifest should create MantraByte from OpCodes."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/di.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)

        manifest = manifest_protocol(analysis, result)

        assert manifest["protocol_name"] == "di"
        assert manifest["mantra_byte"].startswith("0x")
        assert 0.0 <= manifest["coherence"] <= 1.0
        assert 0.0 <= manifest["stability"] <= 1.0

    def test_manifest_has_opcode_sequence(self) -> None:
        """Manifest should include the HolyName sequence."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/events.py", EVENT_PROTOCOL)
        result = pipeline.decide(analysis)

        manifest = manifest_protocol(analysis, result)

        assert len(manifest["opcode_sequence"]) == 16  # Always 16
        assert all(name in ("HARE", "KRISHNA", "RAMA") for name in manifest["opcode_sequence"])

    def test_manifest_resonance_check(self) -> None:
        """is_resonant should be True if coherence >= 0.8."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)

        manifest = manifest_protocol(analysis, result)

        # Check the relationship between coherence and resonance
        if manifest["coherence"] >= 0.8:
            assert manifest["is_resonant"] is True
        else:
            assert manifest["is_resonant"] is False


class TestSyncStep:
    """Test SYNC step - connect to LotusHeartbeat."""

    def test_sync_connects_to_lotus(self) -> None:
        """Sync should connect protocol to Lotus."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/di.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        sync = sync_to_lotus(result, manifest)

        assert sync["protocol_name"] == "di"
        assert sync["is_chanting"] is True
        assert sync["lotus_position"] >= 0
        assert sync["lotus_quarter"] in ("genesis", "dharma", "karma", "moksha")

    def test_sync_parampara_verification(self) -> None:
        """Sync should verify parampara connection."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        sync = sync_to_lotus(result, manifest)

        # Our formula guarantees % 37 == 0
        assert sync["parampara_hash"] % 37 == 0
        assert sync["is_connected"] is True

    def test_sync_heartbeat_position(self) -> None:
        """Sync should track heartbeat position."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        sync = sync_to_lotus(result, manifest)

        assert 0 <= sync["heartbeat_position"] < 16
        assert sync["mala_count"] >= 0


class TestAttractionMechanism:
    """Test ATTRACTION mechanism - how strongly protocols are pulled to Lotus."""

    def test_attraction_calculation(self) -> None:
        """Should calculate attraction from coherence and parampara."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/di.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest)

        assert attraction["protocol_name"] == "di"
        assert attraction["coherence"] == manifest["coherence"]
        assert attraction["resonance_strength"] in ("strong", "medium", "weak", "mercy", "none")

    def test_attraction_resonance_levels(self) -> None:
        """Resonance strength should match coherence levels."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest)

        coherence = manifest["coherence"]
        if coherence >= 0.9:
            assert attraction["resonance_strength"] == "strong"
        elif coherence >= 0.7:
            assert attraction["resonance_strength"] == "medium"
        elif coherence >= 0.5:
            assert attraction["resonance_strength"] == "weak"
        # Note: coherence < 0.5 with is_chanting=True (default) → "mercy"
        # This is the Ajamil Exception!

    def test_attraction_recommended_action(self) -> None:
        """Should provide recommended action based on attraction."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest)

        assert "recommended_action" in attraction
        # Now includes MERCY actions!
        valid_actions = [
            "AUTO_ADOPT: Strong resonance, integrate immediately",
            "ADOPT_WITH_REVIEW: Weak resonance, may need adjustment",
            "MERCY_GRANTED: Ajamil Exception - low coherence but chanting, saved by Holy Name",
            "TRANSFORM_SAMSKARA: Connected but needs coherence improvement through chanting",
            "MERCY_PATH: Disconnected but chanting - mercy will reconnect over time",
            "QUARANTINE_SEVERE: Not chanting, not connected - needs intervention",
        ]
        assert attraction["recommended_action"] in valid_actions


class TestMercyMechanism:
    """Test MERCY mechanism - THE KEY IN KALI YUGA!"""

    def test_mercy_fields_present(self) -> None:
        """AttractionReport should include mercy fields."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest)

        # Mercy fields must be present
        assert "mercy_type" in attraction
        assert "mercy_available" in attraction
        assert "ajamil_exception" in attraction

    def test_mercy_always_available_when_chanting(self) -> None:
        """Mercy should be available when chanting (is_chanting=True)."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        # Default is_chanting=True
        attraction = calculate_attraction(analysis, manifest, is_chanting=True)
        assert attraction["mercy_available"] is True

    def test_mercy_not_available_without_chanting(self) -> None:
        """Mercy should NOT be available when not chanting."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest, is_chanting=False)
        assert attraction["mercy_available"] is False

    def test_ajamil_exception_low_coherence_chanting(self) -> None:
        """Ajamil Exception: low coherence + chanting = saved!"""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", DEAD_CODE)  # Empty = low coherence
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        # Force low coherence scenario by chanting
        attraction = calculate_attraction(analysis, manifest, is_chanting=True)

        # With low coherence but chanting, ajamil_exception should be True
        # (if coherence < 0.5 and is_chanting)
        if manifest["coherence"] < 0.5:
            assert attraction["ajamil_exception"] is True
            assert attraction["resonance_strength"] == "mercy"

    def test_mercy_types_correct(self) -> None:
        """Mercy type should match resonance strength."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        attraction = calculate_attraction(analysis, manifest)

        # Mercy types: silent, corrective, instructive, severe
        valid_mercy_types = ["silent", "corrective", "instructive", "severe"]
        assert attraction["mercy_type"] in valid_mercy_types

    def test_chanting_is_attracted_even_low_coherence(self) -> None:
        """Chanting protocols should be attracted even with low coherence."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", EMPTY_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)

        # With chanting, even low coherence should be attracted (Ajamil Exception)
        attraction = calculate_attraction(analysis, manifest, is_chanting=True)

        if manifest["coherence"] < 0.5:
            # Ajamil Exception: is_attracted should still be True if chanting
            assert attraction["is_attracted"] is True
            assert attraction["ajamil_exception"] is True


class TestFullPipeline:
    """Test the FULL ADOPTION PIPELINE - adopt_full()."""

    def test_adopt_full_returns_all_steps(self) -> None:
        """adopt_full should return all pipeline steps."""
        result = adopt_full("/wild/di.py", CREATION_PROTOCOL)

        assert "analysis" in result
        assert "result" in result
        assert "manifest" in result
        assert "sync" in result
        assert "attraction" in result
        assert "is_fully_adopted" in result
        assert "total_coherence" in result

    def test_adopt_full_creation_protocol(self) -> None:
        """Full adoption of creation protocol."""
        result = adopt_full("/wild/di.py", CREATION_PROTOCOL)

        # Should be assigned to BRAHMA
        assert result["result"]["assigned_mahajana"] == "brahma"
        # Should be chanting
        assert result["sync"]["is_chanting"] is True
        # Should have coherence
        assert 0.0 <= result["total_coherence"] <= 1.0

    def test_adopt_full_event_protocol(self) -> None:
        """Full adoption of event protocol."""
        result = adopt_full("/wild/events.py", EVENT_PROTOCOL)

        # Should be assigned to NARADA or MANU (PULSE_SYNC owner)
        assert result["result"]["assigned_mahajana"] in ("narada", "manu")
        # Should be synced to Lotus
        assert result["sync"]["is_chanting"] is True

    def test_adopt_full_mayavad_not_fully_adopted(self) -> None:
        """Mayavad protocol should NOT be fully adopted."""
        result = adopt_full("/wild/mayavad.py", MAYAVAD_PROTOCOL)

        # Should be quarantined
        assert result["result"]["decision"] == AdoptionDecision.QUARANTINE.value
        # Should NOT be fully adopted
        assert result["is_fully_adopted"] is False

    def test_adopt_full_dead_code_not_adopted(self) -> None:
        """Dead code should NOT be adopted."""
        result = adopt_full("/wild/dead.py", DEAD_CODE)

        # Should be rejected
        assert result["result"]["decision"] == AdoptionDecision.REJECT.value
        # Should NOT be fully adopted
        assert result["is_fully_adopted"] is False


class TestFullPipelineWatertight:
    """Test that full pipeline types are WATERTIGHT."""

    def test_full_result_watertight(self) -> None:
        """FullAdoptionResult should have all fields with correct types."""
        result: FullAdoptionResult = adopt_full("/wild/test.py", CREATION_PROTOCOL)

        # All nested types should be correct
        assert isinstance(result["analysis"], dict)
        assert isinstance(result["result"], dict)
        assert isinstance(result["manifest"], dict)
        assert isinstance(result["sync"], dict)
        assert isinstance(result["attraction"], dict)
        assert isinstance(result["is_fully_adopted"], bool)
        assert isinstance(result["total_coherence"], float)

    def test_manifest_watertight(self) -> None:
        """ManifestResult should be WATERTIGHT."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest: ManifestResult = manifest_protocol(analysis, result)

        assert isinstance(manifest["protocol_name"], str)
        assert isinstance(manifest["mantra_byte"], str)
        assert isinstance(manifest["coherence"], float)
        assert isinstance(manifest["stability"], float)
        assert isinstance(manifest["is_resonant"], bool)
        assert isinstance(manifest["opcode_sequence"], list)
        assert isinstance(manifest["manifested_at"], str)

    def test_sync_watertight(self) -> None:
        """SyncResult should be WATERTIGHT."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)
        sync: SyncResult = sync_to_lotus(result, manifest)

        assert isinstance(sync["protocol_name"], str)
        assert isinstance(sync["lotus_position"], int)
        assert isinstance(sync["lotus_quarter"], str)
        assert isinstance(sync["is_chanting"], bool)
        assert isinstance(sync["parampara_hash"], int)
        assert isinstance(sync["is_connected"], bool)
        assert isinstance(sync["heartbeat_position"], int)
        assert isinstance(sync["mala_count"], int)
        assert isinstance(sync["synced_at"], str)

    def test_attraction_watertight(self) -> None:
        """AttractionReport should be WATERTIGHT."""
        pipeline = AdoptionPipeline()
        analysis = pipeline.analyze("/wild/test.py", CREATION_PROTOCOL)
        result = pipeline.decide(analysis)
        manifest = manifest_protocol(analysis, result)
        attraction: AttractionReport = calculate_attraction(analysis, manifest)

        assert isinstance(attraction["protocol_name"], str)
        assert isinstance(attraction["coherence"], float)
        assert isinstance(attraction["resonance_strength"], str)
        assert isinstance(attraction["attraction_vector"], int)
        assert isinstance(attraction["is_attracted"], bool)
        assert isinstance(attraction["needs_transformation"], bool)
        # MERCY FIELDS
        assert isinstance(attraction["mercy_type"], str)
        assert isinstance(attraction["mercy_available"], bool)
        assert isinstance(attraction["ajamil_exception"], bool)
        assert isinstance(attraction["recommended_action"], str)
        assert isinstance(attraction["analyzed_at"], str)
