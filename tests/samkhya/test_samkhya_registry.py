from typing import Any

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.universal import ReadWriteProtocol, SyncProtocol


# Mocks
class MockConfig:
    def read(self, key):
        pass

    def write(self, k, v):
        pass

    def exists(self, k):
        pass


class MockSync:
    def sync(self):
        pass

    def get_sync_status(self):
        pass

    def is_synced(self):
        pass


class MockDual:
    """Implements BOTH"""

    def read(self, key):
        pass

    def write(self, k, v):
        pass

    def exists(self, k):
        pass

    def sync(self):
        pass

    def get_sync_status(self):
        pass

    def is_synced(self):
        pass


@pytest.fixture
def clean_registry():
    ServiceRegistry.reset()
    yield
    ServiceRegistry.reset()


def test_registry_get_all(clean_registry):
    """Verify get_all finds all matching protocols."""

    # Register mix of services
    conf1 = MockConfig()
    conf2 = MockConfig()
    sync1 = MockSync()
    dual1 = MockDual()

    # We must register them under *some* interface (doesn't matter what,
    # as get_all iterates values)
    ServiceRegistry.register(MockConfig, conf1)
    ServiceRegistry.register(object, conf2)  # Register under generic object
    ServiceRegistry.register(MockSync, sync1)
    ServiceRegistry.register(MockDual, dual1)

    # 1. Get All ReadWrite
    readers = ServiceRegistry.get_all(ReadWriteProtocol)
    assert len(readers) == 3  # conf1, conf2, dual1
    assert conf1 in readers
    assert conf2 in readers
    assert dual1 in readers
    assert sync1 not in readers

    # 2. Get All Sync
    syncers = ServiceRegistry.get_all(SyncProtocol)
    assert len(syncers) == 2  # sync1, dual1
    assert sync1 in syncers
    assert dual1 in syncers
    assert conf1 not in syncers


def test_get_all_empty(clean_registry):
    """Verify empty registry returns empty list."""
    assert ServiceRegistry.get_all(ReadWriteProtocol) == []
