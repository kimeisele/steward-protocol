#!/usr/bin/env python3
"""
Integration Test: VAJRA Enforcement - Enforcing Dharma from Phoenix Config
===========================================================================

Tests that:
1. VAJRA can load PhoenixConfig (Manas configuration)
2. VAJRA detects drift between State and Config
3. VAJRA enforces the Config as source of truth
4. Runtime values are corrected to match Config values
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.phoenix.config import PhoenixConfig
from vibe_core.vajra.enforcement import VajraEnforcer


def test_vajra_loads_phoenix_config():
    """Test that VAJRA can load PhoenixConfig."""
    config = PhoenixConfig.from_files()
    assert config is not None
    assert config.has_section("manas")
    manas_config = config.get_section("manas")
    assert manas_config is not None


def test_vajra_detects_manas_drift():
    """Test that VAJRA detects drift in Manas config (auto_execute_safe)."""
    # Load the authoritative config from YAML
    config = PhoenixConfig.from_files()
    manas_config = config.get_section("manas")

    # Simulate runtime state that differs from config
    # Config says auto_execute_safe=False (conservative)
    # Runtime state says auto_execute_safe=True (corrupted/drifted)
    runtime_state = {
        "auto_execute_safe": True,
        "thinking_interval_minutes": manas_config.thinking_interval_minutes,
        "idle_threshold_minutes": manas_config.idle_threshold_minutes,
    }

    # VAJRA should detect this drift
    enforcer = VajraEnforcer(config)
    has_drift = enforcer.detect_drift("manas", runtime_state)

    assert has_drift is True, "VAJRA should detect drift in auto_execute_safe"


def test_vajra_enforces_dharma():
    """Test that VAJRA corrects drift and enforces Config as law."""
    # Load the authoritative config
    config = PhoenixConfig.from_files()
    manas_config = config.get_section("manas")

    # Verify config says auto_execute_safe=False
    assert manas_config.auto_execute_safe is False, "Test config must have auto_execute_safe=False for this test"

    # Simulate corrupted runtime state
    runtime_state = {
        "auto_execute_safe": True,  # WRONG!
        "thinking_interval_minutes": manas_config.thinking_interval_minutes,
        "idle_threshold_minutes": manas_config.idle_threshold_minutes,
        "karma_auto_execute_threshold": manas_config.karma_auto_execute_threshold,
        "max_intent_buffer_size": manas_config.max_intent_buffer_size,
        "intent_expiry_hours": manas_config.intent_expiry_hours,
        "max_intents_per_tick": manas_config.max_intents_per_tick,
        "survival_first": manas_config.survival_first,
    }

    # VAJRA enforces the law
    enforcer = VajraEnforcer(config)
    corrected_state = enforcer.gloss_over("manas", runtime_state)

    # Verify the correction was applied
    assert corrected_state["auto_execute_safe"] is False, "VAJRA must correct auto_execute_safe to match config"
    assert corrected_state["auto_execute_safe"] == manas_config.auto_execute_safe


def test_vajra_respects_correct_state():
    """Test that VAJRA leaves correct state untouched."""
    # Load the authoritative config
    config = PhoenixConfig.from_files()
    manas_config = config.get_section("manas")

    # Runtime state that matches config (correct)
    runtime_state = {
        "auto_execute_safe": manas_config.auto_execute_safe,
        "thinking_interval_minutes": manas_config.thinking_interval_minutes,
        "idle_threshold_minutes": manas_config.idle_threshold_minutes,
        "karma_auto_execute_threshold": manas_config.karma_auto_execute_threshold,
        "max_intent_buffer_size": manas_config.max_intent_buffer_size,
        "intent_expiry_hours": manas_config.intent_expiry_hours,
        "max_intents_per_tick": manas_config.max_intents_per_tick,
        "survival_first": manas_config.survival_first,
    }

    # VAJRA should not report drift
    enforcer = VajraEnforcer(config)
    has_drift = enforcer.detect_drift("manas", runtime_state)
    assert has_drift is False, "No drift should be detected when state matches config"

    # VAJRA glossing over should return identical state
    corrected_state = enforcer.gloss_over("manas", runtime_state)
    assert corrected_state == runtime_state


def test_vajra_logs_enforcement(caplog):
    """Test that VAJRA logs when it enforces."""
    config = PhoenixConfig.from_files()
    manas_config = config.get_section("manas")

    # Corrupted state
    runtime_state = {
        "auto_execute_safe": True,  # WRONG!
        "thinking_interval_minutes": manas_config.thinking_interval_minutes,
        "idle_threshold_minutes": manas_config.idle_threshold_minutes,
        "karma_auto_execute_threshold": manas_config.karma_auto_execute_threshold,
        "max_intent_buffer_size": manas_config.max_intent_buffer_size,
        "intent_expiry_hours": manas_config.intent_expiry_hours,
        "max_intents_per_tick": manas_config.max_intents_per_tick,
        "survival_first": manas_config.survival_first,
    }

    # Capture logs and enforce
    import logging

    with caplog.at_level(logging.INFO, logger="VAJRA"):
        enforcer = VajraEnforcer(config)
        corrected_state = enforcer.gloss_over("manas", runtime_state)

        # Verify correction happened
        assert corrected_state["auto_execute_safe"] is False

        # Verify enforcement was logged
        assert "Enforced Dharma" in caplog.text or "Corrected" in caplog.text or len(caplog.records) > 0
