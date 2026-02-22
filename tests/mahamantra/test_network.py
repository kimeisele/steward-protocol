"""
TEST VIMANA - Networked Sankirtan
=================================

Verifies TCP Transport Layer for Cell Transmission.
"""

import pytest
import asyncio
from vibe_core.mahamantra.net.vimana import VimanaServer, VimanaClient
from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from vibe_core.mahamantra.substrate.chamber import SankirtanChamber
from vibe_core.mahamantra.net.vimana import VimanaServer, VimanaClient

PORT = 10888  # Test port


@pytest.mark.asyncio
async def test_vimana_transmission():
    # 1. Setup Server Chamber
    server_chamber = SankirtanChamber.create()

    # 2. Start Server
    server = VimanaServer("127.0.0.1", PORT, server_chamber)
    await server.start()

    # 3. Create Client and Cell
    client = VimanaClient("127.0.0.1", PORT)
    cell = MahaCellUnified.create(source=1, target=2, operation=3)

    # 4. Transmit
    await client.connect()
    await client.send(cell)
    await client.send(cell)  # Send twice to test stream handling
    await client.close()

    # 5. Verify Reception
    # We need to wait a moment for async processing
    await asyncio.sleep(0.1)

    # Server chamber should have processed cells
    # Note: Processing might not mean resonance unless registry collides.
    # But resonance_count might remain 0 if no collision.
    # However, active_cells should increase if valid.
    # Wait, simple dance(cell) puts it in registry.
    # Sending valid cell twice same spot -> Resonance?
    # Source=1, Target=2.
    # Registry index depends on DIW (Orchestrator).
    # Orchestrator is deterministic.
    # Actually, we just want to ensure NO ERROR and maybe active cells > 0.

    assert len(server_chamber.active_cells) > 0
    # If we sent same cell twice, they might merge (resonance)
    # But it depends on Vamsi hash.

    # Clean up
    server.server.close()
    await server.server.wait_closed()
