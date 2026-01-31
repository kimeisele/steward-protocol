"""
VIMANA - The Celestial Chariot
==============================

"Networked Sankirtan"

Transport layer for moving MahaCellUnified instances across the network (TCP).
Protocol: Length-prefixed binary.
    [4 bytes: Length (Big Endian)] [N bytes: Serialized Cell]
"""

import asyncio
import struct
import logging
from typing import Optional, Callable, Awaitable

from vibe_core.mahamantra.cell import MahaCellUnified
from vibe_core.mahamantra.chamber import SankirtanChamber

logger = logging.getLogger("vimana")

# Default Port (108 names * 100)
DEFAULT_PORT = 10800

class VimanaProtocol(asyncio.Protocol):
    """
    AsyncIO Protocol for receiving Cells.
    """
    def __init__(self, chamber: SankirtanChamber, on_cell: Optional[Callable[[MahaCellUnified], None]] = None):
        self.chamber = chamber
        self.on_cell = on_cell
        self._buffer = bytearray()
        self._header_size = 4
        self._expected_len = -1

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"Vimana Connection Accepted: {transport.get_extra_info('peername')}")

    def data_received(self, data):
        self._buffer.extend(data)
        
        while True:
            # 1. Read Length Header
            if self._expected_len == -1:
                if len(self._buffer) >= self._header_size:
                    self._expected_len = struct.unpack(">I", self._buffer[:4])[0]
                    del self._buffer[:4]
                else:
                    break # Wait for more data
            
            # 2. Read Payload
            if self._expected_len != -1:
                if len(self._buffer) >= self._expected_len:
                    payload = self._buffer[:self._expected_len]
                    del self._buffer[:self._expected_len]
                    
                    # Process Cell
                    self._process_payload(payload)
                    
                    # Reset for next packet
                    self._expected_len = -1
                else:
                    break # Wait for more data

    def _process_payload(self, data: bytes):
        try:
            cell, _ = MahaCellUnified.from_bytes(data)
            
            # Interact with Chamber (The main purpose)
            # We treat incoming cells as visitors engaging in "dance"
            result_cell = self.chamber.dance(cell)
            
            if self.on_cell:
                self.on_cell(result_cell)
                
            logger.debug(f"Received & Danced: {cell.header.dna} -> Res: {self.chamber.resonance_count}")
            
        except Exception as e:
            logger.error(f"Failed to process Vimana payload: {e}")
            # Close connection on error? Or just log?
            # For resilience, just log.

    def connection_lost(self, exc):
        logger.info("Vimana Connection Closed")


class VimanaServer:
    """
    TCP Server listening for Cells.
    """
    def __init__(self, host: str, port: int, chamber: SankirtanChamber):
        self.host = host
        self.port = port
        self.chamber = chamber
        self.server: Optional[asyncio.AbstractServer] = None

    async def start(self):
        loop = asyncio.get_running_loop()
        self.server = await loop.create_server(
            lambda: VimanaProtocol(self.chamber),
            self.host, self.port
        )
        logger.info(f"Vimana Server listening on {self.host}:{self.port}")
        
    async def serve_forever(self):
        if not self.server:
            await self.start()
        async with self.server:
            await self.server.serve_forever()


class VimanaClient:
    """
    TCP Client for sending Cells.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.writer: Optional[asyncio.StreamWriter] = None
        self.reader: Optional[asyncio.StreamReader] = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        logger.info(f"Connected to Vimana at {self.host}:{self.port}")

    async def send(self, cell: MahaCellUnified) -> None:
        if not self.writer:
            await self.connect()
            
        data = cell.to_bytes()
        length = len(data)
        
        # [Length][Payload]
        packet = struct.pack(">I", length) + data
        
        self.writer.write(packet)
        await self.writer.drain()

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
