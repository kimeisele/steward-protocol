
import pytest
from unittest.mock import MagicMock, patch
import logging
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import VivekaAction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_DHARMA_LIE")

class TestDharmaLie:
    def test_vairagya_ignored(self):
        """
        PROOF OF DEFECT: The Prabhupada Paradox.
        
        Vedic Law: If Confidence > VAIRAGYA_THRESHOLD (0.95), we must decay it to prevent Ego.
        Current Reality: The code ignores this law.
        
        We force the internal score to 0.99.
        We assert that the returned score is LESS than 0.99 (Decay happened).
        
        This test will FAIL on the current codebase.
        """
        action = VivekaAction()
        
        # 1. Mock SynapticMemory (to force calculation path)
        mock_memory = MagicMock()
        mock_memory.consult_dharmic.return_value = [] # No learned experience
        mock_memory = MagicMock()
        mock_memory.consult_dharmic.return_value = [] # No learned experience
        action._get_synaptic_memory = MagicMock(return_value=mock_memory)
        
        # Mock Decision Logger to avoid 'dict object has no attribute append' error
        action._decision_logger = MagicMock()
        action._decision_logger.log = MagicMock()
        
        # 2. Mock Intent
        mock_intent = MagicMock()
        mock_intent.intent_type = "test_intent"
        mock_intent.params = {}
        mock_intent.title = "High Ego Intent"
        
        # 3. Patch Akshara calculations
        # These are imported LOCALLY in _evaluate_dharmic, so we must patch them 
        # at the SOURCE (vibe_core.plugins.opus_assistant.manas.akshara)
        # OR we can Mock them if they were imported at module level, but here they are local.
        # Patching sys.modules or the source path works.
        
        with patch("vibe_core.plugins.opus_assistant.manas.akshara.calculate_dharmic_score", return_value=0.99):
            with patch("vibe_core.plugins.opus_assistant.manas.akshara.calculate_resonance", return_value=0.99):
                # We also need these enums or functions being mocked if they are imported
                mock_varga = MagicMock()
                mock_varga.name = "SATTVA"
                
                with patch("vibe_core.plugins.opus_assistant.manas.akshara.get_trigger_varga", return_value=mock_varga):
                    with patch("vibe_core.plugins.opus_assistant.manas.akshara.get_action_varga", return_value=mock_varga):
                        
                        # Act
                        decision, log = action._evaluate_dharmic(mock_intent, "action:test")
                        
                        score = log.dharmic_score
                        print(f"DEBUG: Raw Score Included=0.99. Final Score={score}")
                        
                        # ASSERTION OF TRUTH
                        # The Law says: If score > 0.95, it must decay.
                        # So Final Score must be < 0.99.
                        
                        # The Bug: It returns 0.99.
                        assert score < 0.99, f"DHARMA VIOLATION: Ego unbounded. Score {score} did not decay despite > 0.95 threshold."
