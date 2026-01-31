"""
UNIVERSAL ROUTER - Folder-is-Wiring for ANY File
================================================

"yathā yathā hi puruṣaḥ" -> "As a man surrenders..."

This router converts ANY file (code, text, binary) into a MahaCell
based purely on its location in the Holographic Structure.

PRINCIPLE:
    - Folder = Context (Quarter/Mahajana)
    - File = Content (Payload)
    - Path = Address (Fractal)

IT USES:
    - MahaCompression (for Intent/Seed)
    - HolographicRouter (for O(1) Lookup)
    - FOLDER_MAHAJANA_MAP (for Identity)

SSOT ALIGNMENT:
    - Derived from _seed.py
"""

from pathlib import Path
from typing import Final, Optional

from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.adapters.routing import HolographicRouter
from vibe_core.mahamantra.protocols._seed import (
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.substrate.sankirtan import FOLDER_MAHAJANA_MAP
from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

# Quarter Enum (from Adhikara or just string mapping)
from vibe_core.mahamantra.protocols._adhikara import Quarter


class UniversalMahaRouter:
    """
    Route ANY file to MahaCell via folder structure.

    Extends FOLDER_MAHAJANA_MAP to handle all file types.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "universal_router"

    def __init__(self) -> None:
        self._compression = MahaCompression()
        # Initialize HolographicRouter for internal routing logic if needed
        # (Though this class mostly does path parsing)
        self._holographic = HolographicRouter(levels=QUARTERS)

    def route(self, path: Path) -> MahaCellUnified:
        """
        Convert ANY file to MahaCell.

        1. Detect quarter from folder
        2. Detect mahajana from folder or content
        3. Compress content to seed
        4. Generate header
        5. Return MahaCell
        """
        # Step 1: Quarter from folder
        quarter = self._detect_quarter(path)

        # Step 2: Mahajana from folder
        mahajana = self._detect_mahajana(path)
        position = self._mahajana_to_position(mahajana)

        # Step 3: Read and compress
        # Handle missing files gracefully
        if not path.exists():
             raise FileNotFoundError(f"File not found: {path}")
             
        content = path.read_bytes()
        result = self._compression.compress(content)

        # Step 4: Create cell
        # Source: The file's inherent position
        # Target: The compressed intent (Seed)
        # Operation: The Quarter (Action type)
        return MahaCellUnified.create(
            source=position,
            target=result.position, # Target based on content analysis
            operation=quarter.value, # 0, 1, 2, 3
            dna=str(path), # Store path as DNA
            initial_state=content # Payload is file content
        )

    def _detect_quarter(self, path: Path) -> Quarter:
        """Detect quarter from folder path."""
        parts = path.parts
        for part in parts:
            p_lower = part.lower()
            if p_lower in ('genesis', 'bootstrap', 'init'):
                return Quarter.GENESIS
            elif p_lower in ('dharma', 'law', 'rules', 'config', 'protocols'):
                return Quarter.DHARMA
            elif p_lower in ('karma', 'action', 'service', 'api', 'substrate', 'adapters'):
                return Quarter.KARMA
            elif p_lower in ('moksha', 'result', 'output', 'intel', 'research'):
                return Quarter.MOKSHA
        return Quarter.GENESIS  # Default

    def _detect_mahajana(self, path: Path) -> str:
        """Detect mahajana from folder path or FOLDER_MAHAJANA_MAP."""
        parts = path.parts
        
        # Check explicit guardian names
        # ALL_GUARDIANS is a tuple/list of strings
        guardian_names = set(g.lower() for g in ALL_GUARDIANS)
        
        for part in parts:
            p_lower = part.lower()
            # Direct guardian name
            if p_lower in guardian_names:
                return p_lower
            # Domain mapping
            if p_lower in FOLDER_MAHAJANA_MAP:
                return FOLDER_MAHAJANA_MAP[p_lower]

        return "brahma"  # Default

    def _mahajana_to_position(self, mahajana: str) -> int:
        """Convert mahajana name to position index (0-15)."""
        # Linear search in ALL_GUARDIANS (size 16, O(1))
        try:
            return ALL_GUARDIANS.index(mahajana)
        except ValueError:
            return 0 # Default to Brahma
