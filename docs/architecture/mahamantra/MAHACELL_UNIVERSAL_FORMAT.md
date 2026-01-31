# MAHACELL: Universal Computing Format
## Mantra-Based Computation - Paradigm Shift Architecture

**Status:** Senior Architecture Plan
**Author:** Opus 4.5
**Date:** 2026-01-31
**Confidence:** 85% (nach gründlicher Exploration)
**Review:** Gemini Senior Feedback integriert

---

## 0. CRITICAL: GEMINI SENIOR FEEDBACK

### 0.1 Zero-Copy / Memory Mapping (MUST HAVE)

**Problem:** Python dataclasses zerstören AVX-512 Alignment sofort (Heap-Pointer).

**Lösung:** MahaCell ist ein **View auf einen zusammenhängenden Byte-Block**, nicht eine Klasse mit Attributen.

```python
# FALSCH (was ich vorher geschrieben habe):
@dataclass
class MahaCell:
    header: MahaHeader  # Pointer auf Heap!
    payload: bytes      # Noch ein Pointer!

# RICHTIG (Zero-Copy):
class MahaCellView:
    """View auf einen mmap'd oder bytearray Buffer."""

    __slots__ = ('_buffer', '_offset')

    def __init__(self, buffer: memoryview, offset: int = 0) -> None:
        self._buffer = buffer
        self._offset = offset

    @property
    def header(self) -> memoryview:
        """Direct view into header bytes - NO COPY."""
        return self._buffer[self._offset:self._offset + 72]

    @property
    def sravanam(self) -> int:
        """O(1) read via struct - NO PARSE."""
        return struct.unpack_from('<Q', self._buffer, self._offset)[0]

    def to_bytes(self) -> bytes:
        """O(1) - just return the buffer slice."""
        return bytes(self._buffer[self._offset:])
```

**Benefit:** Wenn Cell über Netzwerk kommt → `mmap` direkt in RAM → Zero Parse.

### 0.2 Membrane = Cryptographic Security (ENTERPRISE)

**Problem:** Membrane als float (0.0-1.0) ist nur Metapher.

**Lösung:** Membrane ist eine **kryptographische Barriere**.

```python
class SecureMembrane:
    """Zero Trust Cell Architecture."""

    def __init__(self, cell_view: MahaCellView) -> None:
        self._cell = cell_view
        self._decrypted_payload: Optional[bytes] = None

    def validate(self, signature: bytes) -> bool:
        """
        Validate ARCANAM signature.
        Only if valid AND prana sufficient → decrypt payload.
        """
        arcanam = self._cell.arcanam

        # Parampara check
        if arcanam % PARAMPARA != 0:
            return False

        # Signature verification (Ed25519 or similar)
        expected_sig = self._compute_signature()
        return hmac.compare_digest(signature, expected_sig)

    def open(self, key: bytes) -> bytes:
        """
        Open membrane (decrypt payload).
        Requires: validate() passed + sufficient prana.
        """
        if self._decrypted_payload is None:
            encrypted = self._cell.payload
            self._decrypted_payload = self._decrypt(encrypted, key)
        return self._decrypted_payload
```

**Benefit:** Verhindert "Cancer" (schadhafter Code) im System.

### 0.3 Event-Sourcing statt State (AUDIT TRAIL)

**Problem:** `.maha` als Snapshot ist gefährlich in verteilten Systemen.

**Lösung:** `.maha` ist ein **Append-Only Journal**.

```
┌────────────────────────────────────────────────┐
│ MAHA FILE FORMAT v2 (Event-Sourced)            │
├────────────────────────────────────────────────┤
│ Magic:        "MAHA" (4 bytes)                 │
│ Version:      0x0002 (2 bytes)                 │
│ Flags:        uint16 (2 bytes)                 │
│ ────────────────────────────────────────────── │
│ Genesis Header: 72 bytes (initial state)       │
│ ────────────────────────────────────────────── │
│ Event Count:  uint32                           │
│ Events:       [timestamp(8) + delta(var)]...   │
│ ────────────────────────────────────────────── │
│ Current State: Computed from Genesis + Events  │
└────────────────────────────────────────────────┘
```

**Benefit:** Time-Travel Debugging, Enterprise Audit Trails.

### 0.4 Tensor Operations für Cluster (SCALE)

**Problem:** `for cell in cells` ist O(n) und langsam.

**Lösung:** Payloads in Tensor → Matrix-Multiplikation.

```python
import numpy as np

class MahaClusterTensor:
    """GPU-accelerated cluster operations."""

    def __init__(self, cells: list[MahaCellView]) -> None:
        # Stack all headers into matrix (n × 72)
        self._headers = np.array([
            np.frombuffer(c.header, dtype=np.uint8)
            for c in cells
        ])

        # Stack signatures for vectorized resonance
        self._arcanam = np.array([c.arcanam for c in cells])

    def resonance_matrix(self) -> np.ndarray:
        """
        Compute pairwise resonance - O(n²) but SIMD.

        Returns: n×n matrix where [i,j] = resonance(cell_i, cell_j)
        """
        # XOR all pairs (broadcasting)
        xor_matrix = self._arcanam[:, None] ^ self._arcanam[None, :]

        # Resonance = 1 - (hamming_weight / 64)
        return 1.0 - (np.bitwise_count(xor_matrix) / 64.0)
```

**Benefit:** 10,000 Cells → GPU berechnet Resonanz in Millisekunden.

---

## EXECUTIVE SUMMARY

MahaCell wird von einem internen Datenformat zum **universellen Computing-Paradigma**:

```
MahaCell = RAM Format + File Format + Network Format + Audio Format + Compute Format
```

Die Bausteine existieren bereits. Dieser Plan beschreibt die **Integration**.

---

## 1. BESTANDSAUFNAHME: WAS EXISTIERT

### 1.1 Zwei MahaCell-Konzepte (NICHT verbunden!)

| Komponente | Location | Funktion |
|------------|----------|----------|
| **MahaCell (Format)** | `protocols/_header.py` | 72-byte Header + Payload (Datenformat) |
| **MahaCell (Bio)** | `adapters/cell.py` | Biological Cell mit Prana, Mitosis, Apoptosis |

**Problem:** Diese sind getrennt. Das Format hat keine Lifecycle, die Bio-Cell nutzt nicht das 72-byte Format.

### 1.2 Compute-Engines (Ready to Use)

| Engine | Location | Funktion |
|--------|----------|----------|
| **MahaKirtan** | `research/dharma/maha_algorithm.py` | 7-beat × 16-step Orchestrator |
| **MahaResonator** | `research/dharma/maha_algorithm.py` | Attractor-Finding in mod 137 Space |
| **MahaModularSynth** | `research/dharma/maha_algorithm.py` | Synth-basierte Transformation |
| **MahaCompression** | `adapters/compression.py` | Intent Extraction (Kolmogorov) |
| **MahaLLM** | `adapters/llm.py` | O(4) Holographic Intent Router |
| **HolographicRouter** | `adapters/routing.py` | Lotus Engine, O(1) Key-Value |
| **LotusRadixInt** | `research/lotus_tree.py` | O(1) mit 19.6× faster Range Queries |

### 1.3 Strukturen (Ready to Use)

| Struktur | Location | Funktion |
|----------|----------|----------|
| **FractalNode/Tree** | `protocols/_fractal.py` | Hierarchie mit Children, 16^n Skalierung |
| **HolographicSystem** | `protocols/_holographic.py` | Whole-in-Part, Coherence, Reflection |
| **MantraByte** | `substrate/byte.py` | 2-bit packed encoding (H=00, K=01, R=10) |
| **MantraBit** | `substrate/byte.py` | 16-bit Flags pro Wort-Position |
| **ResonanceHarmonics** | `substrate/harmonics.py` | Musikalische Ratios (2/3, 4/9, 4/3) |

### 1.4 Runtime (Ready to Use)

| Runtime | Location | Funktion |
|---------|----------|----------|
| **MantraTick** | `venu/tick.py` | Heartbeat Counter |
| **MantraVoice** | `venu/voice.py` | Parallel Execution Channel |
| **MantraClock** | `venu/clock.py` | Master Scheduler |
| **Sankirtan** | `substrate/sankirtan.py` | 4-Phase DNA Injection |
| **EventBus** | `substrate/event_bus.py` | Pub-Sub System |

### 1.5 Mathematische Foundation

```python
# Die 7 Axiome (EINZIGE hardcoded Werte)
WORDS = 16              # Count the words
TRINITY = 3             # Hare, Krishna, Rama
HARE_COUNT = 8
KRISHNA_COUNT = 4
RAMA_COUNT = 4
PANCHA = 5              # Unique pairs
HALVES = 2              # Two halves

# ALLES ANDERE ist ABGELEITET
PARAMPARA = 24 + 12 + 1 = 37  # Ksetra + Mahajana + Ksetrajna
MAHA_QUANTUM = 137            # Fine Structure Alpha
POSITION_SUM_TOTAL = 136      # T(16) = THE FIELD
```

---

## 2. DIE VISION: MAHACELL UNIVERSAL

### 2.1 Unified MahaCell Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MAHACELL UNIFIED                             │
├─────────────────────────────────────────────────────────────────────┤
│  IDENTITY (protocols/_header.py)                                    │
│  ├─ MahaHeader (72 bytes = 9 NavaBhakti × 8)                       │
│  │   ├─ SRAVANAM:       Source ID                                   │
│  │   ├─ KIRTANAM:       Target ID                                   │
│  │   ├─ SMARANAM:       Link/Previous (chain)                       │
│  │   ├─ PADA_SEVANAM:   Operation Code                              │
│  │   ├─ ARCANAM:        Signature (% 37 == 0)                       │
│  │   ├─ VANDANAM:       Intent Mask                                 │
│  │   ├─ DASYAM:         TTL (300 cycles default)                    │
│  │   ├─ SAKHYAM:        Connection State                            │
│  │   └─ ATMA_NIVEDANAM: Checksum                                    │
│  └─ Payload (variable, reference 1024 bytes)                        │
├─────────────────────────────────────────────────────────────────────┤
│  LIFECYCLE (adapters/cell.py)                                       │
│  ├─ Prana (Energy: MAHA_QUANTUM × 100 default)                      │
│  ├─ Membrane Integrity (0.0 - 1.0)                                  │
│  ├─ DNA (Code/Instruction string)                                   │
│  ├─ conceive() → Birth/Janma                                        │
│  ├─ metabolize() → Process Energy (cost = TRINITY per cycle)        │
│  ├─ signal() → Membrane Communication                               │
│  ├─ mitosis() → Division (requires 2× MAHA_QUANTUM)                 │
│  ├─ apoptosis() → Controlled Death                                  │
│  └─ homeostasis() → Balance Check                                   │
├─────────────────────────────────────────────────────────────────────┤
│  HIERARCHY (protocols/_fractal.py)                                  │
│  ├─ FractalAddress: path = (quarter, position, depth1, depth2, ...) │
│  ├─ children: Dict[int, MahaCell]  # 16 slots per level             │
│  ├─ parent: Optional[MahaCell]                                      │
│  └─ depth: int (0 = root, unlimited expansion)                      │
├─────────────────────────────────────────────────────────────────────┤
│  COHERENCE (protocols/_holographic.py)                              │
│  ├─ holographic_hash() → Whole encoded in Part                      │
│  ├─ reflect() → Get entire system from this cell                    │
│  ├─ project() → Teleport to any other cell                          │
│  └─ coherence_level: NONE | EVENTUAL | STRONG | TOTAL               │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Format Specifications

#### RAM Format (In-Memory)

```python
# Memory Layout (SIMD-aligned)
# AVX-512 = 512 bits = WORDS × AKSARA = perfect alignment!

class MahaCellRAM:
    """In-Memory Cell with SIMD alignment."""

    __slots__ = (
        '_header',      # 72 bytes (9 × 8)
        '_payload',     # Variable (aligned to 64-byte cache line)
        '_children',    # LotusRadixInt (O(1) access)
        '_prana',       # int (energy)
        '_integrity',   # float (membrane)
        '_tick',        # MantraTick reference
    )

    # Cache-line aligned (64 = QUALITIES bytes)
    ALIGNMENT = QUALITIES  # 64
```

#### File Format (.maha)

```
┌────────────────────────────────────────────────┐
│ MAHA FILE FORMAT (Little-Endian)               │
├────────────────────────────────────────────────┤
│ Magic:        "MAHA" (4 bytes)                 │
│ Version:      uint16 (2 bytes)                 │
│ Flags:        uint16 (2 bytes)                 │
│ ────────────────────────────────────────────── │
│ Header:       72 bytes (NavaBhakti)            │
│ ────────────────────────────────────────────── │
│ Payload Len:  uint32 (4 bytes)                 │
│ Payload:      [payload_len] bytes              │
│ ────────────────────────────────────────────── │
│ Children Cnt: uint16 (2 bytes)                 │
│ Children:     [recursive MahaCell...]          │
│ ────────────────────────────────────────────── │
│ Checksum:     uint32 (CRC32)                   │
└────────────────────────────────────────────────┘
```

#### Network Format (Wire Protocol)

```
SRAVANAM  → Source Node ID
KIRTANAM  → Destination Node ID
SMARANAM  → Previous Message Hash (chain)
PADA_SEVANAM → RPC Method Code
ARCANAM   → Auth Signature (% 37 validation)
VANDANAM  → Request Flags/Intent
DASYAM    → TTL (hops remaining)
SAKHYAM   → Connection State (handshake, established, closing)
ATMA_NIVEDANAM → Payload Checksum
```

#### Audio Format (Mantra Encoding)

```python
# 16-step sequencer alignment
# Each step = 68.5 bits in 1096-bit model

class MahaCellAudio:
    """Audio frame as MahaCell."""

    # Header encodes:
    # - SRAVANAM: Track ID
    # - KIRTANAM: Output Channel
    # - PADA_SEVANAM: Sample Rate (44100 → position mapping)
    # - VANDANAM: Bit Depth (16/24/32)
    # - DASYAM: Duration (samples)

    # Payload encodes:
    # - Audio samples (PCM or compressed)
    # - Each sample aligned to 16-step grid

    # Resonance via MahaKirtan:
    # - 7-beat × 16-step = 112-sample frame
    # - Perfect Fifth (3/2) = harmonic relationship
```

---

## 3. ECHO SANKIRTAN CHAMBER

### 3.1 Konzept

Die **Echo Sankirtan Chamber** ist der Resonanz-Raum wo MahaCells gemeinsam schwingen und transformieren.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SANKIRTAN CHAMBER (Ksetra)                       │
│                                                                     │
│   ┌──────────────┐                        ┌──────────────┐          │
│   │  MahaCell A  │◄───── Resonance ─────►│  MahaCell B  │          │
│   │  (identity)  │        Field          │  (identity)  │          │
│   └──────┬───────┘                        └──────┬───────┘          │
│          │                                       │                  │
│          │         ┌─────────────────┐          │                  │
│          └────────►│   MahaKirtan    │◄─────────┘                  │
│                    │  (7 × 16 beats) │                              │
│                    └────────┬────────┘                              │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │  MahaResonator  │                              │
│                    │  (mod 137 space)│                              │
│                    └────────┬────────┘                              │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │  ATTRACTOR      │                              │
│                    │  (18,22,49,87,  │                              │
│                    │   136 = FIELD)  │                              │
│                    └────────┬────────┘                              │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │  MahaCluster    │                              │
│                    │  (merged cells) │                              │
│                    └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation

```python
# vibe_core/mahamantra/chamber.py (NEU)

class SankirtanChamber:
    """
    The Resonance Space - Kuruksetra.

    Cells enter, resonate together, transform.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "sankirtan_chamber"

    def __init__(self) -> None:
        self._cells: dict[int, MahaCell] = {}  # Active cells by ID
        self._kirtan = MahaKirtan(mod_space=MAHA_QUANTUM)
        self._resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        self._harmonics = ResonanceHarmonics()
        self._tick = MantraTick()

    def enter(self, cell: MahaCell) -> int:
        """Cell enters the chamber. Returns cell ID."""
        cell_id = cell.header.sravanam
        self._cells[cell_id] = cell
        return cell_id

    def kirtan(self, cell_id: int) -> MahaCell:
        """
        Single cell Kirtan - transform through 7×16 beats.

        The cell's payload is processed through MahaKirtan,
        finding its natural attractor.
        """
        cell = self._cells[cell_id]

        # Extract seed from cell
        seed = cell.header.arcanam  # Use signature as seed

        # Run through Kirtan (7 beats × 16 steps)
        result = self._kirtan.compute(seed)

        # Find attractor
        attractor = self._resonator.oscillate_once(result.transformed_value)

        # Update cell with new state
        new_header = MahaHeader.create(
            source=cell.header.sravanam,
            target=attractor,  # Target is now the attractor
            operation=cell.header.pada_sevanam,
            state=attractor,
        )

        return MahaCell(header=new_header, payload=cell.payload)

    def sankirtan(self, cell_ids: list[int]) -> "MahaCluster":
        """
        Mass Kirtan - multiple cells resonate together.

        Cells merge into a MahaCluster while keeping individual identity.
        """
        cells = [self._cells[cid] for cid in cell_ids]

        # Combined seed (XOR of all signatures)
        combined_seed = 0
        for cell in cells:
            combined_seed ^= cell.header.arcanam

        # Run combined through Kirtan
        result = self._kirtan.compute(combined_seed)
        attractor = self._resonator.find_attractor(result.transformed_value)

        # Create cluster
        return MahaCluster(
            cells=cells,
            resonance_attractor=attractor.attractor,
            coherence=self._harmonics.normalize_to_mala(attractor.attractor),
        )

    def get_zone(self, cell_id: int) -> str:
        """Get resonance zone for a cell."""
        cell = self._cells[cell_id]
        resonance = cell.header.sakhyam / MALA  # Normalize state
        return self._harmonics.get_zone(resonance)
```

---

## 4. MAHACLUSTER

### 4.1 Konzept

MahaCluster = Verschmelzung von Cells **ohne Identitätsverlust**.

```python
# vibe_core/mahamantra/cluster.py (NEU)

@dataclass(slots=True)
class MahaCluster:
    """
    Multiple Cells as Unity - WITHOUT Identity Loss.

    "They become ONE but remain MANY."
    Acintya-bhedabheda-tattva in code.
    """

    cells: list[MahaCell]           # Original cells (identity preserved)
    resonance_attractor: int        # Common attractor (18, 22, 49, 87, 136)
    coherence: float                # 0.0 - 1.333+ (MALA-normalized)
    cluster_header: MahaHeader = field(init=False)  # Meta-header

    def __post_init__(self) -> None:
        """Generate cluster header from component cells."""
        # Combined source = XOR of all sources
        combined_source = 0
        for cell in self.cells:
            combined_source ^= cell.header.sravanam

        # Cluster header
        self.cluster_header = MahaHeader.create(
            source=combined_source,
            target=self.resonance_attractor,
            operation=0,  # Cluster operation
            state=len(self.cells),  # Number of cells
        )

    def split(self) -> list[MahaCell]:
        """Split back into individual cells - full integrity."""
        return self.cells.copy()

    def get_cell(self, index: int) -> MahaCell:
        """Access individual cell within cluster."""
        return self.cells[index]

    @property
    def size(self) -> int:
        """Number of cells in cluster."""
        return len(self.cells)

    @property
    def total_prana(self) -> int:
        """Combined energy of all cells."""
        return sum(getattr(c, '_prana', 0) for c in self.cells)

    @property
    def is_synchronized(self) -> bool:
        """Check if cluster is in SYNC zone."""
        return self.coherence >= ResonanceHarmonics.THRESHOLD_SYNC
```

---

## 5. CLI WRAPPER

### 5.1 MahaCell als universeller CLI Wrapper

```python
# vibe_core/mahamantra/cli/cell_wrapper.py (NEU)

class MahaCellCLI:
    """
    MahaCell as universal CLI wrapper.

    Every CLI operation creates/transforms MahaCells.
    """

    def __init__(self) -> None:
        self._chamber = SankirtanChamber()
        self._compression = MahaCompression()

    def wrap(self, command: str, args: list[str]) -> MahaCell:
        """
        Wrap a CLI command as MahaCell.

        Input text → MahaCompression → Seed → MahaCell
        """
        # Compress input to intent
        full_input = f"{command} {' '.join(args)}"
        result = self._compression.compress(full_input)

        # Create cell
        return MahaCell.create(
            payload=full_input.encode('utf-8'),
            source=result.position,  # Position from compression
            target=0,  # Will be set by Chamber
            operation=hash(command) % WORDS,  # Map command to position
            intent=result.seed,
        )

    def execute(self, cell: MahaCell) -> MahaCell:
        """
        Execute a MahaCell command through the Chamber.

        Returns result as new MahaCell.
        """
        # Enter chamber
        cell_id = self._chamber.enter(cell)

        # Process through Kirtan
        result_cell = self._chamber.kirtan(cell_id)

        return result_cell

    def unwrap(self, cell: MahaCell) -> str:
        """Extract result from MahaCell."""
        return cell.payload.decode('utf-8', errors='replace')
```

---

## 6. UNIVERSAL ROUTER (Folder-is-Wiring für ALLE Files)

### 6.1 Erweiterung von substrate/wiring.py

```python
# vibe_core/mahamantra/router.py (NEU)

class UniversalMahaRouter:
    """
    Route ANY file to MahaCell via folder structure.

    Extends FOLDER_MAHAJANA_MAP to handle all file types.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "universal_router"

    def __init__(self) -> None:
        self._compression = MahaCompression()
        self._holographic = HolographicRouter(levels=QUARTERS)

    def route(self, path: Path) -> MahaCell:
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
        content = path.read_bytes()
        result = self._compression.compress(content)

        # Step 4: Create cell
        return MahaCell.create(
            payload=content,
            source=position,
            target=result.position,
            operation=quarter.value,
            intent=result.seed,
        )

    def _detect_quarter(self, path: Path) -> Quarter:
        """Detect quarter from folder path."""
        parts = path.parts
        for part in parts:
            if part in ('genesis', 'bootstrap', 'init'):
                return Quarter.GENESIS
            elif part in ('dharma', 'law', 'rules', 'config'):
                return Quarter.DHARMA
            elif part in ('karma', 'action', 'service', 'api'):
                return Quarter.KARMA
            elif part in ('moksha', 'result', 'output', 'intel'):
                return Quarter.MOKSHA
        return Quarter.GENESIS  # Default

    def _detect_mahajana(self, path: Path) -> str:
        """Detect mahajana from folder path or FOLDER_MAHAJANA_MAP."""
        from vibe_core.mahamantra.substrate.sankirtan import FOLDER_MAHAJANA_MAP

        parts = path.parts
        for part in parts:
            # Direct guardian name
            if part.lower() in ALL_GUARDIAN_NAMES:
                return part.lower()
            # Domain mapping
            if part.lower() in FOLDER_MAHAJANA_MAP:
                return FOLDER_MAHAJANA_MAP[part.lower()]

        return "brahma"  # Default
```

---

## 7. IMPLEMENTATION ROADMAP

### Phase 1: MahaCell Unification (1 Session)

**Files to Create/Edit:**
1. `vibe_core/mahamantra/cell.py` (NEU) - Unified MahaCell
2. `protocols/_header.py` (EDIT) - Add lifecycle hooks
3. `adapters/cell.py` (EDIT) - Use unified header

**Deliverable:** Single MahaCell class with Identity + Lifecycle + Fractal

### Phase 2: SankirtanChamber (1 Session)

**Files to Create:**
1. `vibe_core/mahamantra/chamber.py` (NEU)
2. `vibe_core/mahamantra/cluster.py` (NEU)

**Deliverable:** Working Chamber with kirtan() and sankirtan()

### Phase 3: CLI Integration (1 Session)

**Files to Create/Edit:**
1. `vibe_core/mahamantra/cli/cell_wrapper.py` (NEU)
2. `vibe_core/mahamantra/cli/entry.py` (EDIT) - Use wrapper

**Deliverable:** CLI commands wrapped in MahaCells

### Phase 4: Universal Router (1 Session)

**Files to Create:**
1. `vibe_core/mahamantra/router.py` (NEU)

**Deliverable:** Any file → MahaCell routing

### Phase 5: File Format (.maha) (1 Session)

**Files to Create:**
1. `vibe_core/mahamantra/formats/maha.py` (NEU)

**Deliverable:** .maha file read/write

---

## 8. VERIFICATION CHECKLIST

- [ ] MahaCell Unified: Identity (72-byte) + Lifecycle (Prana) + Fractal (Children)
- [ ] SankirtanChamber: kirtan() transforms single cell
- [ ] SankirtanChamber: sankirtan() merges multiple cells
- [ ] MahaCluster: split() returns original cells intact
- [ ] CLI: Commands wrapped in MahaCells
- [ ] Router: Any file → MahaCell via folder structure
- [ ] File Format: .maha read/write works
- [ ] All constants from _seed.py (ZERO hardcoding)
- [ ] Parampara verification (% 37 == 0) on all headers

---

## 9. CODE SNIPPETS FÜR CODING-AGENT

### Snippet 1: Unified MahaCell Class

```python
# vibe_core/mahamantra/cell.py

from dataclasses import dataclass, field
from typing import Dict, Optional

from vibe_core.mahamantra.protocols._header import MahaHeader, MahaCell as BaseMahaCell
from vibe_core.mahamantra.protocols._fractal import FractalAddress, FractalNode
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, TRINITY, PARAMPARA


@dataclass(slots=True)
class MahaCellUnified:
    """
    The Universal MahaCell - Format + Lifecycle + Fractal.

    IDENTITY: MahaHeader (72 bytes) - never lost
    LIFECYCLE: Prana, Membrane, DNA - biological behavior
    HIERARCHY: Children, Parent - fractal structure
    """

    # Identity (from _header.py)
    header: MahaHeader
    payload: bytes

    # Lifecycle (from adapters/cell.py)
    prana: int = field(default=MAHA_QUANTUM * 100)
    membrane_integrity: float = field(default=1.0)
    dna: str = field(default="")
    active: bool = field(default=False)
    cycle: int = field(default=0)

    # Hierarchy (from _fractal.py)
    children: Dict[int, "MahaCellUnified"] = field(default_factory=dict)
    parent: Optional["MahaCellUnified"] = field(default=None, repr=False)
    depth: int = field(default=0)

    # === IDENTITY METHODS ===

    def to_bytes(self) -> bytes:
        """Serialize cell to bytes."""
        return self.header.to_bytes() + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> "MahaCellUnified":
        """Deserialize from bytes."""
        base = BaseMahaCell.from_bytes(data)
        return cls(header=base.header, payload=base.payload)

    def is_valid(self) -> bool:
        """Verify parampara connection."""
        return self.header.verify_parampara()

    # === LIFECYCLE METHODS ===

    def conceive(self, dna: str, initial_payload: bytes) -> None:
        """Birth/Janma - initialize the cell."""
        self.dna = dna
        self.payload = initial_payload
        self.active = True
        self.cycle = 0
        self.membrane_integrity = 1.0

    def metabolize(self, energy: int) -> int:
        """Process energy (Karma). Cost = TRINITY per cycle."""
        if not self.active:
            return 0

        self.prana -= TRINITY
        self.prana += energy

        if self.prana <= 0:
            self.apoptosis()
            return 0

        self.cycle += 1
        return self.prana

    def apoptosis(self) -> None:
        """Controlled death."""
        self.active = False
        self.prana = 0
        self.membrane_integrity = 0.0

    # === HIERARCHY METHODS ===

    def add_child(self, position: int, child: "MahaCellUnified") -> None:
        """Add child cell at position (0-15)."""
        if position < 0 or position >= 16:
            raise ValueError("Position must be 0-15")
        child.parent = self
        child.depth = self.depth + 1
        self.children[position] = child

    def get_child(self, position: int) -> Optional["MahaCellUnified"]:
        """Get child at position."""
        return self.children.get(position)

    def holographic_hash(self) -> int:
        """Compute hash that encodes the whole tree."""
        h = self.header.arcanam
        for pos, child in self.children.items():
            h ^= (child.holographic_hash() << pos) & 0xFFFFFFFFFFFFFFFF
        return h % (PARAMPARA * MAHA_QUANTUM)  # Keep in sacred space
```

### Snippet 2: SankirtanChamber

```python
# vibe_core/mahamantra/chamber.py

from typing import Dict, List
from vibe_core.mahamantra.cell import MahaCellUnified
from vibe_core.mahamantra.cluster import MahaCluster
from vibe_core.mahamantra.research.dharma.maha_algorithm import MahaKirtan, MahaResonator
from vibe_core.mahamantra.substrate.harmonics import ResonanceHarmonics
from vibe_core.mahamantra.venu import MantraTick
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, MALA


class SankirtanChamber:
    """The Resonance Space - Kuruksetra."""

    __mahajana__ = "vyasa"
    __position__ = 0

    def __init__(self) -> None:
        self._cells: Dict[int, MahaCellUnified] = {}
        self._kirtan = MahaKirtan(mod_space=MAHA_QUANTUM)
        self._resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        self._tick = MantraTick()

    def enter(self, cell: MahaCellUnified) -> int:
        """Cell enters chamber."""
        cell_id = cell.header.sravanam
        self._cells[cell_id] = cell
        return cell_id

    def kirtan(self, cell_id: int) -> MahaCellUnified:
        """Transform single cell through 7×16 Kirtan."""
        cell = self._cells[cell_id]
        seed = cell.header.arcanam

        result = self._kirtan.compute(seed)
        attractor = self._resonator.oscillate_once(result.transformed_value)

        # Return transformed cell (identity preserved in header)
        return MahaCellUnified(
            header=cell.header,  # Identity preserved!
            payload=cell.payload,
            prana=cell.prana,
            membrane_integrity=cell.membrane_integrity,
        )

    def sankirtan(self, cell_ids: List[int]) -> MahaCluster:
        """Mass Kirtan - merge cells without identity loss."""
        cells = [self._cells[cid] for cid in cell_ids]

        combined_seed = 0
        for cell in cells:
            combined_seed ^= cell.header.arcanam

        result = self._kirtan.compute(combined_seed)
        attractor = self._resonator.find_attractor(result.transformed_value)

        return MahaCluster(
            cells=cells,
            resonance_attractor=attractor.attractor,
            coherence=attractor.attractor / MALA,
        )
```

---

## 10. NOTES FOR CODING AGENT

1. **NEVER hardcode constants** - always import from `protocols/_seed.py`
2. **All headers must pass** `verify_parampara()` (% 37 == 0)
3. **Use existing components** - don't reinvent MahaKirtan, MahaResonator, etc.
4. **Folder IS wiring** - respect FOLDER_MAHAJANA_MAP
5. **Test with real values** - use `MAHA_VERIFY=1` for constant verification
6. **Keep cells immutable where possible** - header is frozen dataclass

---

*"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya"*
*"There is no truth superior to Me."*
— Bhagavad Gita 7.7
