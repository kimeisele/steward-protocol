"""
OPUS-050: VEDA (The Four-Fold Knowledge) - Pipeline Tests.

TDD: These tests define the expected behavior of the VEDA pipeline.

VEDA = Sacred Knowledge, Wisdom.
The four-fold processing pipeline: Shabda → Artha → Pratyaya → Karma.

"First the word is heard, then its meaning understood,
then trust is established, and only then can action flow."
"""

from dataclasses import dataclass

import pytest

# =============================================================================
# SECTION 1: SHABDA (The Word) TESTS
# =============================================================================


class TestShabdaPhase:
    """Tests for Shabda (Input Reception) phase."""

    @pytest.fixture
    def shabda(self):
        """Create Shabda processor."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Shabda

        return Shabda()

    def test_shabda_normalizes_input(self, shabda):
        """Mutation killer: Input must be normalized to lowercase."""
        result = shabda.process("Hello WORLD")
        assert result.normalized == "hello world"

    def test_shabda_tokenizes_input(self, shabda):
        """Mutation killer: Input must be split into tokens."""
        result = shabda.process("Check the status now")
        assert result.tokens == ["check", "the", "status", "now"]

    def test_shabda_extracts_keywords(self, shabda):
        """Mutation killer: Keywords must exclude stop words."""
        result = shabda.process("Check the status of the system")
        # "the" and "of" should be filtered out
        assert "check" in result.keywords
        assert "status" in result.keywords
        assert "system" in result.keywords
        assert "the" not in result.keywords
        assert "of" not in result.keywords

    def test_shabda_detects_german(self, shabda):
        """Mutation killer: German language must be detected."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaLanguage

        result = shabda.process("Prüfe die Architektur auf Verstöße")
        assert result.language == VedaLanguage.GERMAN

    def test_shabda_detects_english(self, shabda):
        """Mutation killer: English language must be detected."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaLanguage

        # Pure English without any German-origin words
        result = shabda.process("Run the tests now")
        assert result.language == VedaLanguage.ENGLISH

    def test_shabda_detects_question(self, shabda):
        """Mutation killer: Questions must be detected via ? or question words."""
        result1 = shabda.process("What is the status?")
        result2 = shabda.process("Why is CI red")
        result3 = shabda.process("Check status")

        assert result1.is_question is True
        assert result2.is_question is True
        assert result3.is_question is False

    def test_shabda_detects_command(self, shabda):
        """Mutation killer: Commands must be detected via command words."""
        result1 = shabda.process("Run the tests")
        result2 = shabda.process("Show me the status")
        result3 = shabda.process("Is everything okay?")

        assert result1.is_command is True
        assert result2.is_command is True
        assert result3.is_command is False

    def test_shabda_counts_words(self, shabda):
        """Mutation killer: Word count must be accurate."""
        result = shabda.process("One two three four five")
        assert result.word_count == 5

    def test_shabda_preserves_hyphenated_words(self, shabda):
        """Mutation killer: Hyphenated words should stay together."""
        result = shabda.process("Check architektur-drift now")
        assert "architektur-drift" in result.tokens

    def test_shabda_handles_empty_input(self, shabda):
        """Edge case: Empty input should not crash."""
        result = shabda.process("")
        assert result.word_count == 0
        assert len(result.tokens) == 0

    def test_shabda_to_dict(self, shabda):
        """Mutation killer: to_dict must return all fields."""
        result = shabda.process("Test input")
        d = result.to_dict()

        assert "raw_input" in d
        assert "normalized" in d
        assert "tokens" in d
        assert "keywords" in d
        assert "language" in d
        assert "is_question" in d
        assert "is_command" in d
        assert "word_count" in d


# =============================================================================
# SECTION 2: ARTHA (The Meaning) TESTS
# =============================================================================


class TestArthaPhase:
    """Tests for Artha (Meaning Extraction) phase."""

    @pytest.fixture
    def shabda(self):
        """Create Shabda processor."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Shabda

        return Shabda()

    @pytest.fixture
    def artha(self):
        """Create Artha processor."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Artha

        return Artha()

    def test_artha_identifies_status_intent(self, shabda, artha):
        """Mutation killer: 'status' keyword should map to STATUS intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("What is the system status?")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.STATUS

    def test_artha_identifies_drift_intent(self, shabda, artha):
        """Mutation killer: 'drift' keyword should map to DRIFT intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        # Pure drift query without 'architecture' keyword
        s = shabda.process("Check for drift violations")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.DRIFT

    def test_artha_identifies_compliance_intent(self, shabda, artha):
        """Mutation killer: 'compliance' keyword should map to COMPLIANCE intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("What is the compliance score?")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.COMPLIANCE

    def test_artha_identifies_help_intent(self, shabda, artha):
        """Mutation killer: 'help' keyword should map to HELP intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("help")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.HELP

    def test_artha_identifies_german_drift(self, shabda, artha):
        """Mutation killer: German 'verstöße' should map to DRIFT intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("Prüfe auf Verstöße")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.DRIFT

    def test_artha_identifies_dharma_intent(self, shabda, artha):
        """Mutation killer: 'dharma' keyword should map to COMPLIANCE intent."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("Run dharma audit")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.COMPLIANCE

    def test_artha_provides_handler_route(self, shabda, artha):
        """Mutation killer: Artha must provide handler route."""
        s = shabda.process("Check status")
        result = artha.process(s)

        assert result.handler_route == "_handle_status"

    def test_artha_drift_routes_to_drift_handler(self, shabda, artha):
        """Mutation killer: Drift intent routes to _handle_drift."""
        s = shabda.process("Check drift")
        result = artha.process(s)

        assert result.handler_route == "_handle_drift"

    def test_artha_has_confidence_score(self, shabda, artha):
        """Mutation killer: Artha must provide confidence score."""
        s = shabda.process("Check status")
        result = artha.process(s)

        assert 0.0 <= result.confidence <= 1.0

    def test_artha_defaults_to_chat(self, shabda, artha):
        """Mutation killer: Unknown input should default to CHAT."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        s = shabda.process("xyz abc unknown words")
        result = artha.process(s)

        assert result.primary_intent == VedaIntent.CHAT

    def test_artha_extracts_file_paths(self, shabda, artha):
        """Mutation killer: File paths should be extracted as entities."""
        s = shabda.process("Check status of src/main.py")
        result = artha.process(s)

        assert "paths" in result.extracted_entities
        assert "src/main.py" in result.extracted_entities["paths"]

    def test_artha_generates_german_hint(self, shabda, artha):
        """Mutation killer: German input should generate respond_in_german hint."""
        s = shabda.process("Prüfe die Architektur auf Verstöße")
        result = artha.process(s)

        assert "respond_in_german" in result.context_hints

    def test_artha_generates_dharma_hint(self, shabda, artha):
        """Mutation killer: Drift-related intents should generate dharma_context_needed hint."""
        s = shabda.process("Check architecture drift")
        result = artha.process(s)

        assert "dharma_context_needed" in result.context_hints

    def test_artha_to_dict(self, shabda, artha):
        """Mutation killer: to_dict must return all fields."""
        s = shabda.process("Test input")
        result = artha.process(s)
        d = result.to_dict()

        assert "primary_intent" in d
        assert "secondary_intents" in d
        assert "confidence" in d
        assert "handler_route" in d
        assert "extracted_entities" in d
        assert "context_hints" in d


# =============================================================================
# SECTION 3: PRATYAYA (The Trust) TESTS
# =============================================================================


class TestPratyayaPhase:
    """Tests for Pratyaya (Trust/Auth) phase."""

    @pytest.fixture
    def pratyaya(self):
        """Create Pratyaya processor."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Pratyaya

        return Pratyaya()

    @pytest.fixture
    def artha_status(self):
        """Create Artha result for status query."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import (
            Artha,
            Shabda,
        )

        shabda = Shabda()
        artha = Artha()
        s = shabda.process("Check status")
        return artha.process(s)

    @pytest.fixture
    def artha_action(self):
        """Create Artha result for action request.

        OPUS-050: ACTION (KRIYA) is no longer elevated since it only creates
        intent proposals, not executes them. We use a blocked trust level instead.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import (
            Artha,
            Shabda,
        )

        shabda = Shabda()
        artha = Artha()
        s = shabda.process("Delete the file now")
        return artha.process(s)

    def test_pratyaya_authorizes_status_for_user(self, pratyaya, artha_status):
        """Mutation killer: Status queries should be authorized for users."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_status, VedaTrustLevel.USER)
        assert result.authorized is True

    def test_pratyaya_allows_action_for_user(self, pratyaya, artha_action):
        """OPUS-050: ACTION (KRIYA) is allowed for users since it only creates proposals.

        Actions don't require elevated access because they only create intent
        proposals in the CognitiveKernel. Actual execution requires separate approval.
        """
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_action, VedaTrustLevel.USER)
        assert result.authorized is True

    def test_pratyaya_allows_action_for_admin(self, pratyaya, artha_action):
        """Mutation killer: Admin should be able to perform actions."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_action, VedaTrustLevel.ADMIN)
        assert result.authorized is True

    def test_pratyaya_blocks_for_blocked_user(self, pratyaya, artha_status):
        """Mutation killer: Blocked users should always be denied."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_status, VedaTrustLevel.BLOCKED)
        assert result.authorized is False

    def test_pratyaya_warns_when_system_not_ready(self, pratyaya, artha_status):
        """Mutation killer: System not ready should generate warning."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        pratyaya.set_system_ready(False)
        result = pratyaya.process(artha_status, VedaTrustLevel.USER)

        assert "system_not_fully_ready" in result.warnings

    def test_pratyaya_tracks_trust_level(self, pratyaya, artha_status):
        """Mutation killer: Trust level must be tracked in result."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_status, VedaTrustLevel.ADMIN)
        assert result.trust_level == VedaTrustLevel.ADMIN

    def test_pratyaya_provides_reason(self, pratyaya, artha_status):
        """Mutation killer: Authorization result must include reason."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        # Test with both authorized and blocked scenarios
        result = pratyaya.process(artha_status, VedaTrustLevel.USER)
        assert result.reason is not None
        assert len(result.reason) > 0

        result_blocked = pratyaya.process(artha_status, VedaTrustLevel.BLOCKED)
        assert result_blocked.reason is not None
        assert len(result_blocked.reason) > 0

    def test_pratyaya_to_dict(self, pratyaya, artha_status):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        result = pratyaya.process(artha_status, VedaTrustLevel.USER)
        d = result.to_dict()

        assert "authorized" in d
        assert "trust_level" in d
        assert "reason" in d
        assert "preconditions_met" in d
        assert "system_ready" in d
        assert "warnings" in d


# =============================================================================
# SECTION 4: KARMA (The Action) TESTS
# =============================================================================


class TestKarmaPhase:
    """Tests for Karma (Execution) phase."""

    @pytest.fixture
    def karma(self):
        """Create Karma executor."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import Karma

        return Karma()

    @pytest.fixture
    def full_context(self):
        """Create a full VedaContext for testing."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import (
            Artha,
            Pratyaya,
            Shabda,
            VedaContext,
            VedaTrustLevel,
        )

        # Simulate message object
        @dataclass
        class MockMessage:
            content: str

        msg = MockMessage(content="Check status")

        ctx = VedaContext(original_message=msg)
        ctx.shabda = Shabda().process(msg.content)
        ctx.artha = Artha().process(ctx.shabda)
        ctx.pratyaya = Pratyaya().process(ctx.artha, VedaTrustLevel.USER)

        return ctx

    def test_karma_registers_handler(self, karma):
        """Mutation killer: Handlers must be registerable."""

        async def my_handler(ctx):
            return "test"

        karma.register_handler("_handle_test", my_handler)
        assert karma.get_handler("_handle_test") is not None

    @pytest.mark.asyncio
    async def test_karma_executes_handler(self, karma, full_context):
        """Mutation killer: Registered handler must be called."""
        called = {"value": False}

        async def my_handler(ctx):
            called["value"] = True
            return "Success!"

        karma.register_handler("_handle_status", my_handler)
        result = await karma.execute(full_context)

        assert called["value"] is True
        assert result.success is True
        assert result.content == "Success!"

    @pytest.mark.asyncio
    async def test_karma_fails_without_artha(self, karma):
        """Mutation killer: No Artha result should fail."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaContext

        @dataclass
        class MockMessage:
            content: str

        ctx = VedaContext(original_message=MockMessage(content="test"))
        # No shabda/artha/pratyaya

        result = await karma.execute(ctx)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_karma_fails_when_not_authorized(self, karma, full_context):
        """Mutation killer: Unauthorized should not execute."""
        full_context.pratyaya.authorized = False

        result = await karma.execute(full_context)
        assert result.success is False
        assert "Not authorized" in result.error

    @pytest.mark.asyncio
    async def test_karma_fails_with_missing_handler(self, karma, full_context):
        """Mutation killer: Missing handler should return error."""
        # Don't register any handler
        result = await karma.execute(full_context)

        assert result.success is False
        assert "No handler" in result.error

    @pytest.mark.asyncio
    async def test_karma_handles_handler_exception(self, karma, full_context):
        """Mutation killer: Handler exceptions should be caught."""

        async def failing_handler(ctx):
            raise ValueError("Handler crashed!")

        karma.register_handler("_handle_status", failing_handler)
        result = await karma.execute(full_context)

        assert result.success is False
        assert "Handler crashed" in result.error

    @pytest.mark.asyncio
    async def test_karma_tracks_execution_time(self, karma, full_context):
        """Mutation killer: Execution time must be tracked."""
        import asyncio

        async def slow_handler(ctx):
            await asyncio.sleep(0.01)  # 10ms
            return "Done"

        karma.register_handler("_handle_status", slow_handler)
        result = await karma.execute(full_context)

        assert result.execution_time_ms >= 10

    @pytest.mark.asyncio
    async def test_karma_tracks_action_taken(self, karma, full_context):
        """Mutation killer: Action taken must be recorded."""

        async def my_handler(ctx):
            return "Done"

        karma.register_handler("_handle_status", my_handler)
        result = await karma.execute(full_context)

        assert result.action_taken == "_handle_status"

    def test_karma_result_to_dict(self, karma):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import KarmaResult

        result = KarmaResult(
            success=True,
            content="test",
            error=None,
            execution_time_ms=10.0,
            action_taken="test",
            side_effects=[],
        )
        d = result.to_dict()

        assert "success" in d
        assert "content" in d
        assert "error" in d
        assert "execution_time_ms" in d
        assert "action_taken" in d
        assert "side_effects" in d


# =============================================================================
# SECTION 5: VEDA PIPELINE (Full Integration) TESTS
# =============================================================================


class TestVedaPipeline:
    """Tests for the full VEDA pipeline integration."""

    @pytest.fixture
    def pipeline(self):
        """Create full VEDA pipeline."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaPipeline

        return VedaPipeline()

    @pytest.mark.asyncio
    async def test_pipeline_processes_all_phases(self, pipeline):
        """Mutation killer: All four phases must execute."""

        @dataclass
        class MockMessage:
            content: str

        async def status_handler(ctx):
            return "System OK"

        pipeline.karma.register_handler("_handle_status", status_handler)

        msg = MockMessage(content="Check status")
        ctx = await pipeline.process(msg)

        assert ctx.shabda is not None
        assert ctx.artha is not None
        assert ctx.pratyaya is not None
        assert ctx.karma is not None

    @pytest.mark.asyncio
    async def test_pipeline_tracks_phase_history(self, pipeline):
        """Mutation killer: Phase history must be recorded."""

        @dataclass
        class MockMessage:
            content: str

        async def handler(ctx):
            return "OK"

        pipeline.karma.register_handler("_handle_status", handler)

        msg = MockMessage(content="Check status")
        ctx = await pipeline.process(msg)

        assert "shabda" in ctx.phase_history
        assert "artha" in ctx.phase_history
        assert "pratyaya" in ctx.phase_history
        assert "karma" in ctx.phase_history

    @pytest.mark.asyncio
    async def test_pipeline_respects_trust_level(self, pipeline):
        """Mutation killer: Trust level must be passed through."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaTrustLevel

        @dataclass
        class MockMessage:
            content: str

        msg = MockMessage(content="Delete everything")
        ctx = await pipeline.process(msg, trust_level=VedaTrustLevel.BLOCKED)

        assert ctx.pratyaya.authorized is False

    @pytest.mark.asyncio
    async def test_pipeline_handles_german_input(self, pipeline):
        """Mutation killer: German input must be processed correctly."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        @dataclass
        class MockMessage:
            content: str

        async def drift_handler(ctx):
            return "Keine Verstöße gefunden"

        pipeline.karma.register_handler("_handle_drift", drift_handler)

        msg = MockMessage(content="Prüfe auf Verstöße")
        ctx = await pipeline.process(msg)

        assert ctx.artha.primary_intent == VedaIntent.DRIFT
        assert ctx.karma.content == "Keine Verstöße gefunden"

    @pytest.mark.asyncio
    async def test_pipeline_drift_detection_flow(self, pipeline):
        """Integration: Full drift detection flow."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        @dataclass
        class MockMessage:
            content: str

        async def drift_handler(ctx):
            return "Compliance Score: 95%"

        pipeline.karma.register_handler("_handle_drift", drift_handler)

        msg = MockMessage(content="Check for drift violations")
        ctx = await pipeline.process(msg)

        assert ctx.artha.primary_intent == VedaIntent.DRIFT
        assert "dharma_context_needed" in ctx.artha.context_hints
        assert "95%" in ctx.karma.content

    def test_pipeline_shabda_only(self, pipeline):
        """Helper: process_shabda_only must work."""
        result = pipeline.process_shabda_only("Test input")
        assert result.normalized == "test input"

    def test_pipeline_artha_only(self, pipeline):
        """Helper: process_artha_only must work."""
        shabda = pipeline.process_shabda_only("Check status")
        result = pipeline.process_artha_only(shabda)

        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaIntent

        assert result.primary_intent == VedaIntent.STATUS


# =============================================================================
# SECTION 6: VEDA CONTEXT TESTS
# =============================================================================


class TestVedaContext:
    """Tests for VedaContext data model."""

    def test_context_initializes_correctly(self):
        """Mutation killer: Context must initialize with defaults."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaContext

        @dataclass
        class MockMessage:
            content: str

        ctx = VedaContext(original_message=MockMessage(content="test"))

        assert ctx.shabda is None
        assert ctx.artha is None
        assert ctx.pratyaya is None
        assert ctx.karma is None
        assert ctx.pipeline_started is False
        assert ctx.current_phase == "init"
        assert ctx.phase_history == []

    def test_context_advance_to_updates_state(self):
        """Mutation killer: advance_to must update phase tracking."""
        from vibe_core.plugins.opus_assistant.manas.cortex.veda import VedaContext

        @dataclass
        class MockMessage:
            content: str

        ctx = VedaContext(original_message=MockMessage(content="test"))
        ctx.advance_to("shabda")

        assert ctx.current_phase == "shabda"
        assert "shabda" in ctx.phase_history

        ctx.advance_to("artha")
        assert ctx.current_phase == "artha"
        assert ["shabda", "artha"] == ctx.phase_history
