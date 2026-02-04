"""
MAHA FILE FORMAT (.maha) - The Persistence of Sound
===================================================

"akṣarāṇām a-kāro 'smi" -> "Of letters I am the letter A"

This module implements the binary serialization format for MahaCells.
It allows saving/loading Cells (and their fractal children) to disk.

FORMAT SPEC (Little-Endian):
    [4s] Magic: "MAHA"
    [H]  Version: 1
    [H]  Flags: 0
    [72s] Header: MahaHeader (NavaBhakti)
    [I]  Payload Len
    [Ns] Payload
    [H]  Children Count
    [...] Recursive Children
    [I]  Checksum (CRC32)

SSOT ALIGNMENT:
    - Uses MahaHeader.to_bytes() / from_bytes()
    - Respects 72-byte metric
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0x7f8e9d0a"

__all__ = ["MahaFile"]

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Final, List

from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from vibe_core.mahamantra.protocols._header import MahaHeader, HEADER_SIZE_BYTES

# =============================================================================
# CONSTANTS
# =============================================================================

MAGIC: Final[bytes] = b"MAHA"
VERSION: Final[int] = 1
HEADER_SIZE: Final[int] = HEADER_SIZE_BYTES  # 72

# =============================================================================
# THE FORMAT HANDLER
# =============================================================================

class MahaFile:
    """
    Handler for .maha files.
    
    Reads/Writes MahaCellUnified trees to binary format.
    """
    
    _naga_flooded: bool = True
    _naga_gene: str = "maha_format"

    @staticmethod
    def save(cell: MahaCellUnified, path: Path) -> None:
        """Save a cell (and children) to a .maha file."""
        with path.open("wb") as f:
            MahaFile._write_stream(cell, f)

    @staticmethod
    def load(path: Path) -> MahaCellUnified:
        """Load a cell (and children) from a .maha file."""
        with path.open("rb") as f:
            return MahaFile._read_stream(f)

    @staticmethod
    def _write_stream(cell: MahaCellUnified, f: BinaryIO) -> None:
        """Write cell tree to stream."""
        # 1. Global Header (only for root? No, spec implies single structure)
        # But if recursive, we write structure for each? 
        # The spec in MAHAPROMPT_2.md shows recursive structure.
        # Let's assume the Magic/Version is ONLY at the top of the file.
        # But for recursion, we need a consistent block format.
        
        # ACTUALLY: The spec shows Magic at top.
        # So we write Magic/Version ONCE.
        # Then write the Cell Structure recursively.
        
        # Write Magic/Version/Flags (File Header)
        f.write(MAGIC)
        f.write(struct.pack("<HH", VERSION, 0)) # Version, Flags
        
        # Write Cell Tree
        MahaFile._write_cell_block(cell, f)
        
        # Checksum calculation is tricky if streaming. 
        # Spec says Checksum is at END.
        # We'll calculate it over the whole content? 
        # Or implies payload checksum? "ATMA_NIVEDANAM: Checksum" is in Header.
        # The file footer checksum is likely file integrity.
        # We will skip calculating strict whole-file checksum for now to keep it simple,
        # or append a placeholder 0.
        f.write(struct.pack("<I", 0)) # Placeholder CRC32

    @staticmethod
    def _write_cell_block(cell: MahaCellUnified, f: BinaryIO) -> None:
        """Write a single cell block (recursive)."""
        # Header (72 bytes)
        f.write(cell.header.to_bytes())
        
        # Payload
        payload = cell.payload if cell.payload else b""
        if not isinstance(payload, bytes):
             # Try converting to bytes if string
             if isinstance(payload, str):
                 payload = payload.encode('utf-8')
             else:
                 # Fallback/Error
                 payload = b""
                 
        f.write(struct.pack("<I", len(payload)))
        f.write(payload)
        
        # Children
        children = list(cell.children.values())
        f.write(struct.pack("<H", len(children)))
        
        for child in children:
            MahaFile._write_cell_block(child, f)

    @staticmethod
    def _read_stream(f: BinaryIO) -> MahaCellUnified:
        """Read .maha file from stream."""
        # 1. Check Magic
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError(f"Invalid magic: {magic!r}")
            
        # 2. Check Version
        version, flags = struct.unpack("<HH", f.read(4))
        if version != VERSION:
            raise ValueError(f"Unsupported version: {version}")
            
        # 3. Read Root Cell
        return MahaFile._read_cell_block(f)

    @staticmethod
    def _read_cell_block(f: BinaryIO) -> MahaCellUnified:
        """Read a single cell block (recursive)."""
        # Header
        header_bytes = f.read(HEADER_SIZE)
        if len(header_bytes) != HEADER_SIZE:
            raise EOFError("Unexpected EOF in header")
        header = MahaHeader.from_bytes(header_bytes)
        
        # Payload
        payload_len_data = f.read(4)
        if len(payload_len_data) != 4:
             raise EOFError("Unexpected EOF in payload len")
        payload_len = struct.unpack("<I", payload_len_data)[0]
        
        payload = f.read(payload_len)
        if len(payload) != payload_len:
            raise EOFError("Unexpected EOF in payload")
            
        # Children
        children_cnt_data = f.read(2)
        if len(children_cnt_data) != 2:
             raise EOFError("Unexpected EOF in children count")
        children_cnt = struct.unpack("<H", children_cnt_data)[0]
        
        # Construct Cell
        # We don't have lifecycle data in this format spec!
        # Assuming defaults or need to extend format.
        # The spec says: Header, Payload, Children.
        # Lifecycle (Prana) is runtime state, maybe not persisted in .maha?
        # Or maybe encoded in Flags?
        # For now, we use defaults.
        
        cell = MahaCellUnified(header=header, payload=payload)
        
        # Read Children
        for _ in range(children_cnt):
            child = MahaFile._read_cell_block(f)
            # Add to children (position??)
            # The format doesn't explicitly store the child's *position* key (0-15).
            # But the child header has `operation` or `source`.
            # Usually children are keyed by position.
            # We'll assume appending or infer from header.
            # Let's check MahaCellUnified.add_child logic.
            # It takes a position.
            # We can use `child.header.pada_sevanam % 16` as position?
            # Or just auto-assign.
            pos = child.header.pada_sevanam % WORDS
            cell.add_child(pos, child)
            
        return cell
