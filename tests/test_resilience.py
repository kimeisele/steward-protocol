#!/usr/bin/env python3
"""
HERALD Resilience Testing Suite (Chaos Monkey)

Tests that HERALD degrades gracefully under failure:
- Brain Lobotomy (LLM API down)
- Blind Researcher (Tavily down)
- Blind Artist (Image generation down)
- Toxic Input (Governance blocks content)

Philosophy: A system that crashes is a bug.
A system that falls back gracefully is enterprise-grade.
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.brain import HeraldBrain, ResearchEngine, SeniorEditor
from examples.herald.artist import HeraldArtist
from examples.herald.aligner import VibeAligner


class TestHeraldResilience:
    """Chaos tests for HERALD system."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        """Inject fake API keys for testing."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-openrouter")
        monkeypatch.setenv("TAVILY_API_KEY", "test-key-tavily")
        monkeypatch.setenv("TWITTER_API_KEY", "test-key-twitter")

    # ========== TEST GROUP 1: Brain Resilience ==========

    def test_brain_lobotomy_fallback(self):
        """
        Scenario: OpenRouter API returns 500 (complete failure).
        Expected: Brain should NOT crash. Should fallback to hardcoded content.
        """
        brain = HeraldBrain()

        # Kill the LLM client
        brain.client = MagicMock()
        brain.client.chat.completions.create.side_effect = Exception(
            "API Overload - 500 Internal Server Error"
        )

        # Generate content with broken LLM
        content = brain.generate_insight()

        # Assertions
        assert content is not None, "Brain returned None instead of fallback"
        assert len(content) > 10, "Content too short"
        assert "#StewardProtocol" in content, "Missing #StewardProtocol tag"

        # Verify it's actually fallback content (has specific markers)
        valid_fallbacks = [
            "Identity is the missing layer",
            "Agents without keys",
            "Trust but verify",
            "Docker solved",
            "Kubernetes solved"
        ]
        matches = [f for f in valid_fallbacks if f in content]
        assert len(matches) > 0, f"Content doesn't match fallback patterns: {content}"

    def test_brain_editor_unavailable(self):
        """
        Scenario: Editor (quality gate) is not initialized.
        Expected: Brain should skip editor, continue to aligner.
        """
        brain = HeraldBrain()
        brain.editor = None  # Kill the editor

        # Should still generate content (without editorial review)
        content = brain.generate_insight()

        assert content is not None, "Brain failed without editor"
        assert len(content) > 0, "Content is empty"

    def test_brain_aligner_rejects(self):
        """
        Scenario: Content passes editor but aligner rejects (toxic input).
        Expected: Brain should fallback to safe spec-reading content.
        """
        brain = HeraldBrain()

        # Mock the aligner to always reject
        brain.aligner = MagicMock()
        brain.aligner.align.return_value = None

        content = brain.generate_insight()

        # Should fallback, not return None
        assert content is not None, "Brain crashed on aligner rejection"
        assert "#StewardProtocol" in content, "Fallback missing tag"

    # ========== TEST GROUP 2: Research Resilience ==========

    def test_researcher_api_down(self):
        """
        Scenario: Tavily API is completely down.
        Expected: ResearchEngine returns None, brain continues.
        """
        engine = ResearchEngine()
        engine.client = MagicMock()
        engine.client.search.side_effect = Exception("Connection refused")

        result = engine.scan_market()

        assert result is None, "Should return None on API failure"

    def test_researcher_no_results(self):
        """
        Scenario: Tavily returns empty results.
        Expected: Should handle gracefully.
        """
        engine = ResearchEngine()
        engine.client = MagicMock()
        engine.client.search.return_value = {"results": [], "answer": None}

        result = engine.scan_market()

        assert result is None, "Should return None on no results"

    # ========== TEST GROUP 3: Artist Resilience ==========

    def test_artist_api_down(self):
        """
        Scenario: Image generation API (Pollinations) is down.
        Expected: Artist returns None, publisher falls back to text-only.
        """
        artist = HeraldArtist()

        # Mock requests.get to fail
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection timeout")

            image_path = artist.generate_visual("Test prompt", style="cyberpunk")

            assert image_path is None, "Artist should return None on API failure"

    def test_artist_invalid_response(self):
        """
        Scenario: Image API returns invalid response.
        Expected: Should handle gracefully.
        """
        artist = HeraldArtist()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"invalid-image-data"
            mock_get.return_value = mock_response

            # Depending on implementation, might return None or crash
            try:
                image_path = artist.generate_visual("Test prompt")
                # If it doesn't crash, that's good
                assert image_path is None or isinstance(
                    image_path, str
                ), "Should return path or None"
            except Exception as e:
                pytest.fail(f"Artist crashed on invalid response: {e}")

    # ========== TEST GROUP 4: Governance Resilience ==========

    def test_aligner_hype_detection(self):
        """
        Scenario: Content contains banned hype words.
        Expected: Aligner should reject or null-out the content.
        """
        aligner = VibeAligner()

        toxic_content = "This is REVOLUTIONARY and will change the GAME! 🚀🚀🚀"

        # The aligner should either reject (None) or clean it
        result = aligner.align(toxic_content, platform="twitter", client=None)

        # Either it rejects or returns cleaned version (but not original toxic)
        if result is not None:
            assert "REVOLUTIONARY" not in result, "Hype word not filtered"
            assert "🚀🚀🚀" not in result, "Rocket spam not filtered"

    def test_aligner_missing_tags(self):
        """
        Scenario: Twitter content missing required tags.
        Expected: Aligner should return it as-is (Brain responsibility to add tags).
        """
        aligner = VibeAligner()

        incomplete_content = "This is some content but missing tags"

        result = aligner.align(incomplete_content, platform="twitter", client=None)

        # Aligner doesn't add tags (that's Brain's job)
        # It just checks if hype is within bounds
        assert result is not None, "Aligner should not reject non-hype content"

    # ========== TEST GROUP 5: End-to-End Degradation ==========

    def test_full_pipeline_all_systems_down(self):
        """
        Scenario: Everything is broken (LLM, Tavily, Artist).
        Expected: System should still return valid fallback content.
        """
        brain = HeraldBrain()

        # Break everything
        brain.client = MagicMock()
        brain.client.chat.completions.create.side_effect = Exception("LLM down")
        brain.researcher.client = MagicMock()
        brain.researcher.client.search.side_effect = Exception("Tavily down")

        # Artist is already broken in this test context

        # Should still generate something
        content = brain.generate_insight()

        assert content is not None, "System crashed with all APIs down"
        assert "#StewardProtocol" in content, "Content missing protocol tag"

    def test_generation_completes_under_partial_failure(self):
        """
        Scenario: Text generation works, artist fails.
        Expected: Should return content (text-only for publishing).
        """
        brain = HeraldBrain()
        artist = HeraldArtist()

        # Brain works fine
        # Artist will fail (no mock needed, it gracefully fails)

        text = brain.generate_insight()
        image = artist.generate_visual(text) if text else None

        # Assertion: Can publish text even if image failed
        assert text is not None, "Text generation failed"
        # image can be None, that's fine


# ========== PERFORMANCE & LIMITS TESTS ==========

class TestHeraldLimits:
    """Test that HERALD respects constraints."""

    def test_twitter_length_limit(self):
        """Twitter content must be <= 250 chars."""
        brain = HeraldBrain()

        # Even with broken LLM, fallback should respect length
        content = brain._fallback_content()

        assert len(content) <= 250, f"Content too long: {len(content)} chars"

    def test_fallback_content_validity(self):
        """Fallback content should always have protocol tag."""
        brain = HeraldBrain()
        content = brain._fallback_content()

        assert content is not None, "Fallback returned None"
        assert "#StewardProtocol" in content, "Fallback missing protocol tag"
        assert len(content) > 0, "Fallback is empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
