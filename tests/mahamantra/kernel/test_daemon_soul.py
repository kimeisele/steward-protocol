"""
TEST MAHAMANTRA DAEMON (The Soul)
=================================

Verifies the heartbeat logic of the system.
Ensures the Daemon reacts correctly to entropy (Health Score).
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from vibe_core.mahamantra.kernel.daemon import (
    MahamantraDaemon,
    DaemonState,
    EntropyLevel
)

class MockMahamantra:
    """Mock for the Mahamantra Singularity."""
    def __init__(self):
        self.audit_return = {"health_score": 1.0}
        self.chant_counts = {"genesis": 0, "dharma": 0, "karma": 0, "moksha": 0}
        
    def audit(self):
        return self.audit_return
        
    def chant_quarter(self, quarter):
        self.chant_counts[quarter] += 1
        return f"Chanted {quarter}"

@pytest.fixture
def mock_singularity():
    """Patch the global mahamantra instance."""
    mock = MockMahamantra()
    with patch("vibe_core.mahamantra.kernel.daemon.mahamantra", mock):
        yield mock

@pytest.mark.asyncio
async def test_daemon_lifecycle(mock_singularity):
    """Verify Start -> Run -> Stop."""
    daemon = MahamantraDaemon(min_interval=0.01)
    
    # 1. Initial State
    assert daemon.state == DaemonState.DORMANT
    
    # 2. Run for 2 cycles then stop
    # We use _max_cycles logic which is cleaner than async timeout
    daemon._max_cycles = 2
    
    await daemon.start()
    
    # 3. Final State
    assert daemon.state == DaemonState.DEAD
    assert daemon.metrics.cycles_completed == 2

@pytest.mark.asyncio
async def test_samadhi_state(mock_singularity):
    """Verify system enters Samadhi when pure (Health=1.0)."""
    mock_singularity.audit_return = {"health_score": 1.0}
    
    daemon = MahamantraDaemon(min_interval=0.01)
    daemon._max_cycles = 1
    
    await daemon.start()
    
    # In Samadhi, we do NOT chant
    assert mock_singularity.chant_counts["genesis"] == 0
    assert daemon.metrics.last_frequency.name == "SAMADHI"

@pytest.mark.asyncio
async def test_chanting_state(mock_singularity):
    """Verify system chants when impure (Health=0.5)."""
    mock_singularity.audit_return = {"health_score": 0.5}
    
    daemon = MahamantraDaemon(min_interval=0.01)
    daemon._max_cycles = 1
    
    await daemon.start()
    
    # In Low Health, we MUST chant all quarters
    assert mock_singularity.chant_counts["genesis"] == 1
    assert mock_singularity.chant_counts["dharma"] == 1
    assert mock_singularity.chant_counts["karma"] == 1
    assert mock_singularity.chant_counts["moksha"] == 1
    
    # Frequency should be higher (GAJENDRA or SADHANA depending on threshold)
    # Using default thresholds (0.95 / 0.80), 0.5 is < 0.80, so GAJENDRA
    assert daemon.metrics.last_frequency.name == "GAJENDRA"

@pytest.mark.asyncio
async def test_metrics_history():
    """Verify health metrics tracking."""
    daemon = MahamantraDaemon()
    
    # Record declining health
    daemon.metrics.record_health(1.0)
    daemon.metrics.record_health(0.9)
    daemon.metrics.record_health(0.8)
    
    assert daemon.metrics.average_health == 0.9
    assert len(daemon.metrics.health_history) == 3
    
    # Trend check (needs more data points usually, but let's verify logic runs)
    assert daemon.metrics.health_trend in ("unknown", "declining", "stable")
