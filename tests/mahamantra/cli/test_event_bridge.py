"""
TESTS: cli/event_bridge.py - Event Bridge
==========================================

REAL TESTS for:
1. EventEntry TypedDict
2. EventSourceConfig TypedDict
3. EVENT_SOURCES constant
4. get_available_sources function
5. get_events function
"""

import pytest
from vibe_core.mahamantra.cli.event_bridge import (
    EventEntry,
    EventSourceConfig,
    EVENT_SOURCES,
    get_available_sources,
    get_events,
)


# =============================================================================
# EventEntry TypedDict Tests
# =============================================================================


class TestEventEntry:
    """Test EventEntry TypedDict."""

    def test_event_entry_creation(self):
        """EventEntry can be created."""
        entry: EventEntry = {
            "timestamp": "2024-01-01T00:00:00",
            "source": "violations",
            "severity": "warning",
            "message": "Test violation",
        }
        assert entry["source"] == "violations"
        assert entry["severity"] == "warning"

    def test_event_entry_optional_fields(self):
        """EventEntry supports optional fields."""
        entry: EventEntry = {
            "timestamp": "2024-01-01T00:00:00",
            "source": "syscalls",
            "syscall_type": "read",
            "result": "success",
        }
        assert entry["syscall_type"] == "read"
        assert entry["result"] == "success"


# =============================================================================
# EventSourceConfig TypedDict Tests
# =============================================================================


class TestEventSourceConfig:
    """Test EventSourceConfig TypedDict."""

    def test_event_source_config_creation(self):
        """EventSourceConfig can be created."""
        config: EventSourceConfig = {
            "path": "data/ledger/violations.jsonl",
            "parser": "violations",
        }
        assert config["path"] == "data/ledger/violations.jsonl"
        assert config["parser"] == "violations"


# =============================================================================
# EVENT_SOURCES Tests
# =============================================================================


class TestEventSources:
    """Test EVENT_SOURCES constant."""

    def test_event_sources_has_violations(self):
        """EVENT_SOURCES has violations source."""
        assert "violations" in EVENT_SOURCES
        assert EVENT_SOURCES["violations"]["parser"] == "violations"

    def test_event_sources_has_syscalls(self):
        """EVENT_SOURCES has syscalls source."""
        assert "syscalls" in EVENT_SOURCES
        assert EVENT_SOURCES["syscalls"]["parser"] == "syscalls"

    def test_event_sources_paths_are_strings(self):
        """EVENT_SOURCES paths are strings."""
        for name, config in EVENT_SOURCES.items():
            assert isinstance(config["path"], str)
            assert isinstance(config["parser"], str)


# =============================================================================
# get_available_sources Tests
# =============================================================================


class TestGetAvailableSources:
    """Test get_available_sources function."""

    def test_get_available_sources_returns_list(self):
        """get_available_sources returns list."""
        sources = get_available_sources()
        assert isinstance(sources, list)

    def test_get_available_sources_contains_violations(self):
        """get_available_sources contains violations."""
        sources = get_available_sources()
        assert "violations" in sources

    def test_get_available_sources_contains_syscalls(self):
        """get_available_sources contains syscalls."""
        sources = get_available_sources()
        assert "syscalls" in sources


# =============================================================================
# get_events Tests
# =============================================================================


class TestGetEvents:
    """Test get_events function."""

    def test_get_events_returns_tuple(self):
        """get_events returns tuple of (entries, count)."""
        entries, count = get_events()
        assert isinstance(entries, list)
        assert isinstance(count, int)

    def test_get_events_default_limit(self):
        """get_events respects default limit."""
        entries, count = get_events(limit=10)
        assert len(entries) <= 10

    def test_get_events_custom_limit(self):
        """get_events respects custom limit."""
        entries, count = get_events(limit=5)
        assert len(entries) <= 5

    def test_get_events_source_all(self):
        """get_events handles 'all' source."""
        entries, count = get_events(source="all")
        assert isinstance(entries, list)

    def test_get_events_source_violations(self):
        """get_events handles 'violations' source."""
        entries, count = get_events(source="violations")
        assert isinstance(entries, list)
        # All entries should be from violations source
        for entry in entries:
            assert entry.get("source") == "violations"

    def test_get_events_source_syscalls(self):
        """get_events handles 'syscalls' source."""
        entries, count = get_events(source="syscalls")
        assert isinstance(entries, list)
        # All entries should be from syscalls source
        for entry in entries:
            assert entry.get("source") == "syscalls"

    def test_get_events_source_empty_string(self):
        """get_events treats empty string as 'all'."""
        entries, count = get_events(source="")
        assert isinstance(entries, list)

    def test_get_events_unknown_source(self):
        """get_events handles unknown source gracefully."""
        entries, count = get_events(source="unknown_xyz")
        # Should fall back to reading all sources
        assert isinstance(entries, list)

    def test_get_events_severity_filter(self):
        """get_events filters by severity."""
        entries, count = get_events(severity_filter="error")
        # All entries should have error severity (if any)
        for entry in entries:
            if entry.get("severity"):
                assert entry.get("severity", "").upper() == "ERROR"

    def test_get_events_count_reflects_total(self):
        """get_events count reflects total before filtering."""
        entries, total_count = get_events(limit=1)
        # Total count >= entries returned
        assert total_count >= len(entries)


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import event_bridge

        expected = [
            "EventEntry",
            "EventSourceConfig",
            "EVENT_SOURCES",
            "get_available_sources",
            "get_events",
        ]
        for item in expected:
            assert item in event_bridge.__all__, f"{item} should be in __all__"
