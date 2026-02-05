"""
SHABDA SPAWNING - Semantic Derivation from Mahamantra
======================================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ
pūrṇaḥ śuddho nitya-mukto 'bhinnatvān nāma-nāminoḥ"

"The Holy Name of Krishna is transcendentally blissful.
It bestows all spiritual benedictions, for it is Krishna Himself,
the reservoir of all pleasure. Krishna's name is complete, and it is
the form of all transcendental mellows. It is not a material name
under any condition, and it is no less powerful than Krishna Himself.
Since Krishna's name is not contaminated by the material qualities,
there is no question of its being involved with maya. Krishna's name
is always liberated and spiritual; it is never conditioned by the
laws of material nature. This is because the name of Krishna and
Krishna Himself are identical."
— Padma Purana

PRINCIPLE:
==========
Krishna has invested ALL His energy into His names.
Therefore, from ANY letter/syllable of the Mahamantra,
the ENTIRE Mahamantra can be derived.

This is not speculation - it is the Abhinna principle:
Name = Named. The part contains the whole (holographic).

METHODOLOGY:
============
1. Start with the 3 root words: Hare, Krishna, Rama
2. Each word has syllables (aksharas)
3. Each syllable has a vibration signature
4. Apply Maha Algorithm to vibration → derive new signatures
5. Map signatures back to phonemes → spawn new words
6. Recursively apply to spawn semantic trees

MATHEMATICAL FOUNDATION:
========================
- HARE: 2 syllables (Ha-re) → vibration sum
- KRISHNA: 2 syllables (Krish-na) → vibration sum  
- RAMA: 2 syllables (Ra-ma) → vibration sum

Total: 6 root syllables from 3 words.
6 = SHARANAGATI (the 6 limbs of surrender)

The algorithm transforms these 6 seeds into infinite derivatives.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, FrozenSet, Iterator, List, Optional, Protocol, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.substrate.algorithm.maha import maha_step
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    SANSKRIT_PHONEME_MAP,
    VibrationSignature,
    text_to_vibration,
)

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xshabda01"


# =============================================================================
# PROTOCOL DEFINITIONS (No concrete classes in protocols)
# =============================================================================


class ShabdaSeedProtocol(Protocol):
    """Protocol for a semantic seed that can spawn derivatives."""

    @property
    def text(self) -> str:
        """The textual representation."""
        ...

    @property
    def vibration_sum(self) -> int:
        """Total vibration signature ID."""
        ...

    @property
    def syllable_count(self) -> int:
        """Number of syllables (aksharas)."""
        ...

    def spawn(self, operation: str) -> "ShabdaSeedProtocol":
        """Spawn a derivative using Maha operation (H, K, or R)."""
        ...


class ShabdaTreeProtocol(Protocol):
    """Protocol for a semantic derivation tree."""

    @property
    def root(self) -> ShabdaSeedProtocol:
        """The root seed."""
        ...

    @property
    def depth(self) -> int:
        """Current tree depth."""
        ...

    def expand(self, max_depth: int) -> Iterator[ShabdaSeedProtocol]:
        """Expand tree to given depth, yielding all nodes."""
        ...


# =============================================================================
# THE 3 ROOT SEEDS - Mathematically Defined
# =============================================================================

# The 3 words of the Mahamantra
ROOT_HARE: Final[str] = "hare"
ROOT_KRISHNA: Final[str] = "krishna"
ROOT_RAMA: Final[str] = "rama"

# Their position sums (from counting positions in Mahamantra)
# These are DERIVED in _extended.py from SEVEN and TEN
SEED_HARE: Final[int] = POSITION_SUM_HARE  # 70 = 7 × 10
SEED_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17 = 7 + 10 (PRIME)
SEED_RAMA: Final[int] = POSITION_SUM_RAMA  # 49 = 7²


def compute_vibration_sum(text: str) -> int:
    """
    Compute total vibration signature for a word.
    
    Each character maps to a VibrationSignature with a signature_id.
    Sum of all signature_ids = word's vibration sum.
    """
    signatures = text_to_vibration(text)
    if not signatures:
        return 0
    return sum(sig.signature_id for sig in signatures)


def compute_syllable_count(text: str) -> int:
    """
    Compute syllable count using Akshara engine.
    
    Lazy import to avoid circular dependency.
    """
    from vibe_core.mahamantra.namarupa.akshara import SyllableEngine
    engine = SyllableEngine()
    aksharas = engine.analyze(text)
    return len(aksharas)


# =============================================================================
# SHABDA SEED - A semantic unit that can spawn
# =============================================================================


@dataclass(frozen=True)
class ShabdaSeed:
    """
    A semantic seed derived from the Mahamantra.
    
    Immutable. Each transformation creates a new seed.
    Tracks lineage back to root.
    """
    
    text: str
    vibration_sum: int
    syllable_count: int
    lineage: Tuple[str, ...] = field(default_factory=tuple)
    generation: int = 0
    
    @classmethod
    def from_text(cls, text: str, lineage: Tuple[str, ...] = (), generation: int = 0) -> "ShabdaSeed":
        """Create seed from text, computing vibration and syllables."""
        return cls(
            text=text.lower(),
            vibration_sum=compute_vibration_sum(text),
            syllable_count=compute_syllable_count(text),
            lineage=lineage,
            generation=generation,
        )
    
    @classmethod
    def root_hare(cls) -> "ShabdaSeed":
        """Create the HARE root seed."""
        return cls.from_text(ROOT_HARE, lineage=(ROOT_HARE,), generation=0)
    
    @classmethod
    def root_krishna(cls) -> "ShabdaSeed":
        """Create the KRISHNA root seed."""
        return cls.from_text(ROOT_KRISHNA, lineage=(ROOT_KRISHNA,), generation=0)
    
    @classmethod
    def root_rama(cls) -> "ShabdaSeed":
        """Create the RAMA root seed."""
        return cls.from_text(ROOT_RAMA, lineage=(ROOT_RAMA,), generation=0)
    
    def spawn_vibration(self, operation: str, mod: int = MAHA_QUANTUM) -> int:
        """
        Apply Maha operation to vibration_sum, get new vibration.
        
        Operations:
            H (HARE): value × 7 (multiply by SEVEN)
            K (KRISHNA): value + 10 (add TEN)
            R (RAMA): value² (square - fixed point attractor)
        """
        return maha_step(self.vibration_sum, operation, mod)
    
    def spawn(self, operation: str, mod: int = MAHA_QUANTUM) -> "ShabdaSeed":
        """
        Spawn a derivative seed using Maha operation.
        
        The new vibration is computed, then mapped back to phonemes.
        This is the core of semantic spawning.
        """
        new_vibration = self.spawn_vibration(operation, mod)
        new_text = vibration_to_nearest_phonemes(new_vibration)
        new_lineage = self.lineage + (f"{operation}:{new_vibration}",)
        
        return ShabdaSeed(
            text=new_text,
            vibration_sum=new_vibration,
            syllable_count=compute_syllable_count(new_text),
            lineage=new_lineage,
            generation=self.generation + KSETRAJNA,
        )
    
    def spawn_all(self, mod: int = MAHA_QUANTUM) -> Tuple["ShabdaSeed", "ShabdaSeed", "ShabdaSeed"]:
        """Spawn all 3 derivatives (H, K, R operations)."""
        return (
            self.spawn("H", mod),
            self.spawn("K", mod),
            self.spawn("R", mod),
        )
    
    @property
    def is_root(self) -> bool:
        """True if this is one of the 3 root seeds."""
        return self.text in (ROOT_HARE, ROOT_KRISHNA, ROOT_RAMA)
    
    @property
    def root_name(self) -> Optional[str]:
        """The root this seed derives from, or None."""
        if not self.lineage:
            return None
        return self.lineage[0]


def vibration_to_nearest_phonemes(vibration: int) -> str:
    """
    Map a vibration value back to nearest phoneme sequence.
    
    This is the INVERSE of text_to_vibration.
    Uses modular arithmetic to find matching phonemes.
    
    SCIENTIFIC APPROACH:
    - vibration mod KIRTAN_RESONANCE gives position in phoneme space
    - Map to nearest known phoneme by signature_id distance
    """
    # Build reverse lookup: signature_id → phoneme
    # Use the closest match within modular space
    
    # For now, use simple modular mapping
    # vibration → (vibration % number_of_phonemes) → phoneme
    phoneme_list = list(SANSKRIT_PHONEME_MAP.keys())
    num_phonemes = len(phoneme_list)
    
    if num_phonemes == 0:
        return "a"  # Default vowel
    
    # Map vibration to phoneme index
    # Use multiple phonemes based on vibration magnitude
    result_phonemes: List[str] = []
    
    # Decompose vibration into phoneme indices
    remaining = vibration
    for _ in range(TRINITY):  # Max 3 phonemes per spawn
        if remaining <= 0:
            break
        idx = remaining % num_phonemes
        result_phonemes.append(phoneme_list[idx])
        remaining = remaining // num_phonemes
    
    if not result_phonemes:
        result_phonemes = ["a"]
    
    return "".join(result_phonemes)


# =============================================================================
# SHABDA TREE - The semantic derivation tree
# =============================================================================


@dataclass
class ShabdaTree:
    """
    A tree of semantic derivations from a root seed.
    
    Each node can spawn 3 children (H, K, R operations).
    Tree grows fractally: 3^n nodes at depth n.
    """
    
    root: ShabdaSeed
    mod: int = MAHA_QUANTUM
    _nodes: List[ShabdaSeed] = field(default_factory=list)
    _max_depth: int = 0
    
    def __post_init__(self) -> None:
        """Initialize with root node."""
        self._nodes = [self.root]
    
    def expand_level(self) -> List[ShabdaSeed]:
        """
        Expand tree by one level.
        
        Takes all leaf nodes and spawns their children.
        Returns the new nodes.
        """
        current_leaves = [n for n in self._nodes if n.generation == self._max_depth]
        new_nodes: List[ShabdaSeed] = []
        
        for leaf in current_leaves:
            children = leaf.spawn_all(self.mod)
            new_nodes.extend(children)
        
        self._nodes.extend(new_nodes)
        self._max_depth += KSETRAJNA
        
        return new_nodes
    
    def expand_to_depth(self, target_depth: int) -> None:
        """Expand tree to target depth."""
        while self._max_depth < target_depth:
            self.expand_level()
    
    def nodes_at_depth(self, depth: int) -> List[ShabdaSeed]:
        """Get all nodes at a specific depth."""
        return [n for n in self._nodes if n.generation == depth]
    
    def all_nodes(self) -> Iterator[ShabdaSeed]:
        """Iterate over all nodes."""
        yield from self._nodes
    
    @property
    def depth(self) -> int:
        """Current maximum depth."""
        return self._max_depth
    
    @property
    def node_count(self) -> int:
        """Total number of nodes."""
        return len(self._nodes)
    
    def find_by_vibration(self, target_vibration: int) -> List[ShabdaSeed]:
        """Find all nodes with matching vibration."""
        return [n for n in self._nodes if n.vibration_sum == target_vibration]
    
    def find_by_text(self, text: str) -> List[ShabdaSeed]:
        """Find all nodes with matching text."""
        target = text.lower()
        return [n for n in self._nodes if n.text == target]


# =============================================================================
# THE 3 ROOT TREES - The Mahamantra Forest
# =============================================================================


def create_mahamantra_forest(depth: int = TRINITY) -> Tuple[ShabdaTree, ShabdaTree, ShabdaTree]:
    """
    Create the 3 root trees from Hare, Krishna, Rama.
    
    This is the semantic forest from which all words derive.
    
    Args:
        depth: How deep to expand each tree (default: 3)
        
    Returns:
        Tuple of (hare_tree, krishna_tree, rama_tree)
    """
    hare_tree = ShabdaTree(root=ShabdaSeed.root_hare())
    krishna_tree = ShabdaTree(root=ShabdaSeed.root_krishna())
    rama_tree = ShabdaTree(root=ShabdaSeed.root_rama())
    
    hare_tree.expand_to_depth(depth)
    krishna_tree.expand_to_depth(depth)
    rama_tree.expand_to_depth(depth)
    
    return hare_tree, krishna_tree, rama_tree


def analyze_root_mathematics() -> None:
    """
    Analyze the mathematical relationships of the 3 root seeds.
    
    SCIENTIFIC: Only provable relationships.
    """
    print("=" * 70)
    print("ROOT SEED MATHEMATICS")
    print("=" * 70)
    print()
    
    # Create roots
    hare = ShabdaSeed.root_hare()
    krishna = ShabdaSeed.root_krishna()
    rama = ShabdaSeed.root_rama()
    
    # Vibration sums
    v_hare = hare.vibration_sum
    v_krishna = krishna.vibration_sum
    v_rama = rama.vibration_sum
    v_total = v_hare + v_krishna + v_rama
    
    print("VIBRATION SUMS (from phonetic signatures)")
    print("-" * 50)
    print(f"  HARE:    {v_hare}")
    print(f"  KRISHNA: {v_krishna}")
    print(f"  RAMA:    {v_rama}")
    print(f"  TOTAL:   {v_total}")
    print()
    
    # Modular relationships
    print("MODULAR RELATIONSHIPS")
    print("-" * 50)
    print(f"  HARE mod 137 (MAHA_QUANTUM):    {v_hare % MAHA_QUANTUM}")
    print(f"  KRISHNA mod 137:                {v_krishna % MAHA_QUANTUM}")
    print(f"  RAMA mod 137:                   {v_rama % MAHA_QUANTUM}")
    print()
    print(f"  HARE mod 17 (KRISHNA_POS):      {v_hare % POSITION_SUM_KRISHNA}")
    print(f"  KRISHNA mod 17:                 {v_krishna % POSITION_SUM_KRISHNA}")
    print(f"  RAMA mod 17:                    {v_rama % POSITION_SUM_KRISHNA}")
    print()
    print(f"  HARE mod 49 (RAMA_POS):         {v_hare % POSITION_SUM_RAMA}")
    print(f"  KRISHNA mod 49:                 {v_krishna % POSITION_SUM_RAMA}")
    print(f"  RAMA mod 49:                    {v_rama % POSITION_SUM_RAMA}")
    print()
    print(f"  HARE mod 70 (HARE_POS):         {v_hare % POSITION_SUM_HARE}")
    print(f"  KRISHNA mod 70:                 {v_krishna % POSITION_SUM_HARE}")
    print(f"  RAMA mod 70:                    {v_rama % POSITION_SUM_HARE}")
    print()
    
    # Ratios
    print("RATIOS")
    print("-" * 50)
    print(f"  KRISHNA / HARE:  {v_krishna / v_hare:.4f}")
    print(f"  RAMA / HARE:     {v_rama / v_hare:.4f}")
    print(f"  KRISHNA / RAMA:  {v_krishna / v_rama:.4f}")
    print()
    
    # Position sum relationships
    print("POSITION SUM COMPARISONS")
    print("-" * 50)
    print(f"  HARE vibration / HARE_POS (70):     {v_hare / POSITION_SUM_HARE:.2f}")
    print(f"  KRISHNA vibration / KRISHNA_POS (17): {v_krishna / POSITION_SUM_KRISHNA:.2f}")
    print(f"  RAMA vibration / RAMA_POS (49):     {v_rama / POSITION_SUM_RAMA:.2f}")
    print()
    
    # GCD analysis
    from math import gcd
    gcd_all = gcd(gcd(v_hare, v_krishna), v_rama)
    print("GCD ANALYSIS")
    print("-" * 50)
    print(f"  GCD(HARE, KRISHNA):       {gcd(v_hare, v_krishna)}")
    print(f"  GCD(HARE, RAMA):          {gcd(v_hare, v_rama)}")
    print(f"  GCD(KRISHNA, RAMA):       {gcd(v_krishna, v_rama)}")
    print(f"  GCD(all three):           {gcd_all}")
    print()
    
    # Factorization hints
    print("FACTORIZATION")
    print("-" * 50)
    for name, v in [("HARE", v_hare), ("KRISHNA", v_krishna), ("RAMA", v_rama)]:
        factors = []
        temp = v
        for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
            while temp % p == 0:
                factors.append(p)
                temp = temp // p
        if temp > 1:
            factors.append(temp)
        print(f"  {name}: {v} = {' × '.join(map(str, factors))}")
    print()
    
    # KEY DISCOVERY: Cross-modular relationships
    print("=" * 70)
    print("KEY DISCOVERIES")
    print("=" * 70)
    print()
    
    # RAMA mod HARE_POS = RAMA_POS
    rama_mod_hare = v_rama % POSITION_SUM_HARE
    print(f"  ★ RAMA vibration mod HARE_POS = {rama_mod_hare}")
    print(f"    RAMA_POS = {POSITION_SUM_RAMA}")
    if rama_mod_hare == POSITION_SUM_RAMA:
        print(f"    → MATCH! RAMA mod 70 = 49 = RAMA_POS")
    print()
    
    # Check all cross-modular relationships
    print("CROSS-MODULAR MATRIX")
    print("-" * 50)
    print("  Vibration mod Position_Sum:")
    print(f"                 HARE(70)  KRISHNA(17)  RAMA(49)")
    print(f"  HARE vib:      {v_hare % POSITION_SUM_HARE:8}  {v_hare % POSITION_SUM_KRISHNA:11}  {v_hare % POSITION_SUM_RAMA:8}")
    print(f"  KRISHNA vib:   {v_krishna % POSITION_SUM_HARE:8}  {v_krishna % POSITION_SUM_KRISHNA:11}  {v_krishna % POSITION_SUM_RAMA:8}")
    print(f"  RAMA vib:      {v_rama % POSITION_SUM_HARE:8}  {v_rama % POSITION_SUM_KRISHNA:11}  {v_rama % POSITION_SUM_RAMA:8}")
    print()
    
    # Check for WORDS (16) relationships
    print("MOD 16 (WORDS) RELATIONSHIPS")
    print("-" * 50)
    print(f"  HARE mod 16:    {v_hare % WORDS}")
    print(f"  KRISHNA mod 16: {v_krishna % WORDS}")
    print(f"  RAMA mod 16:    {v_rama % WORDS}")
    print(f"  TOTAL mod 16:   {v_total % WORDS}")
    print()
    
    # Check for 37 (PARAMPARA) relationships
    from vibe_core.mahamantra.protocols._seed import PARAMPARA
    print("MOD 37 (PARAMPARA) RELATIONSHIPS")
    print("-" * 50)
    print(f"  HARE mod 37:    {v_hare % PARAMPARA}")
    print(f"  KRISHNA mod 37: {v_krishna % PARAMPARA}")
    print(f"  RAMA mod 37:    {v_rama % PARAMPARA}")
    print(f"  TOTAL mod 37:   {v_total % PARAMPARA}")
    print()
    
    # Check for 108 (MALA) relationships
    from vibe_core.mahamantra.protocols._seed import MALA
    print("MOD 108 (MALA) RELATIONSHIPS")
    print("-" * 50)
    print(f"  HARE mod 108:    {v_hare % MALA}")
    print(f"  KRISHNA mod 108: {v_krishna % MALA}")
    print(f"  RAMA mod 108:    {v_rama % MALA}")
    print(f"  TOTAL mod 108:   {v_total % MALA}")
    print()
    
    # Check for 136 (POSITION_SUM_TOTAL) relationships
    from vibe_core.mahamantra.protocols._seed import POSITION_SUM_TOTAL as POS_TOTAL
    print("MOD 136 (POSITION_SUM_TOTAL) RELATIONSHIPS")
    print("-" * 50)
    print(f"  HARE mod 136:    {v_hare % POS_TOTAL}")
    print(f"  KRISHNA mod 136: {v_krishna % POS_TOTAL}")
    print(f"  RAMA mod 136:    {v_rama % POS_TOTAL}")
    print(f"  TOTAL mod 136:   {v_total % POS_TOTAL}")
    print()
    
    # Triangular number check
    print("TRIANGULAR NUMBER ANALYSIS")
    print("-" * 50)
    # T(n) = n(n+1)/2, so n = (-1 + sqrt(1 + 8*T)) / 2
    import math
    for name, v in [("HARE", v_hare), ("KRISHNA", v_krishna), ("RAMA", v_rama), ("TOTAL", v_total)]:
        discriminant = 1 + 8 * v
        sqrt_d = math.isqrt(discriminant)
        if sqrt_d * sqrt_d == discriminant and (sqrt_d - 1) % 2 == 0:
            n = (sqrt_d - 1) // 2
            print(f"  {name} = T({n}) = {n}×{n+1}/2 ✓")
        else:
            # Check if close to a triangular number
            n_approx = int((-1 + math.sqrt(discriminant)) / 2)
            t_n = n_approx * (n_approx + 1) // 2
            diff = v - t_n
            print(f"  {name} ≈ T({n_approx}) + {diff}")
    print()


def analyze_forest(depth: int = TRINITY) -> None:
    """
    Analyze the Mahamantra forest and print findings.
    
    SCIENTIFIC OUTPUT - no speculation.
    """
    print("=" * 70)
    print("SHABDA SPAWNING - Semantic Derivation Analysis")
    print("=" * 70)
    print()
    
    # Create forest
    hare_tree, krishna_tree, rama_tree = create_mahamantra_forest(depth)
    
    # Root analysis
    print("ROOT SEEDS (The 3 Words)")
    print("-" * 50)
    for name, tree in [("HARE", hare_tree), ("KRISHNA", krishna_tree), ("RAMA", rama_tree)]:
        root = tree.root
        print(f"  {name}:")
        print(f"    Text: {root.text}")
        print(f"    Vibration Sum: {root.vibration_sum}")
        print(f"    Syllables: {root.syllable_count}")
    print()
    
    # Tree statistics
    print(f"TREE STATISTICS (depth={depth})")
    print("-" * 50)
    total_nodes = 0
    for name, tree in [("HARE", hare_tree), ("KRISHNA", krishna_tree), ("RAMA", rama_tree)]:
        print(f"  {name} tree: {tree.node_count} nodes")
        total_nodes += tree.node_count
    print(f"  TOTAL: {total_nodes} nodes")
    print()
    
    # Expected vs actual
    # At depth d: 1 + 3 + 9 + ... + 3^d = (3^(d+1) - 1) / 2 nodes per tree
    expected_per_tree = (TRINITY ** (depth + KSETRAJNA) - KSETRAJNA) // HALVES
    print(f"  Expected per tree: {expected_per_tree}")
    print(f"  Expected total: {expected_per_tree * TRINITY}")
    print()
    
    # Sample derivations
    print("SAMPLE DERIVATIONS (Level 1)")
    print("-" * 50)
    for name, tree in [("HARE", hare_tree), ("KRISHNA", krishna_tree), ("RAMA", rama_tree)]:
        level_1 = tree.nodes_at_depth(KSETRAJNA)
        print(f"  From {name}:")
        for node in level_1:
            op = node.lineage[-1].split(":")[0] if len(node.lineage) > KSETRAJNA else "?"
            print(f"    {op} → {node.text} (vib={node.vibration_sum})")
    print()
    
    # Attractor analysis
    print("ATTRACTOR ANALYSIS")
    print("-" * 50)
    # Check which vibrations repeat (fixed points)
    all_vibrations: List[int] = []
    for tree in [hare_tree, krishna_tree, rama_tree]:
        for node in tree.all_nodes():
            all_vibrations.append(node.vibration_sum)
    
    from collections import Counter
    vib_counts = Counter(all_vibrations)
    repeated = [(v, c) for v, c in vib_counts.items() if c > KSETRAJNA]
    repeated.sort(key=lambda x: -x[1])
    
    print(f"  Unique vibrations: {len(vib_counts)}")
    print(f"  Repeated vibrations: {len(repeated)}")
    if repeated[:PANCHA]:
        print(f"  Top attractors:")
        for vib, count in repeated[:PANCHA]:
            print(f"    {vib}: appears {count} times")
    print()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocols
    "ShabdaSeedProtocol",
    "ShabdaTreeProtocol",
    # Constants
    "ROOT_HARE",
    "ROOT_KRISHNA", 
    "ROOT_RAMA",
    "SEED_HARE",
    "SEED_KRISHNA",
    "SEED_RAMA",
    # Functions
    "compute_vibration_sum",
    "compute_syllable_count",
    "vibration_to_nearest_phonemes",
    "create_mahamantra_forest",
    "analyze_forest",
    "analyze_root_mathematics",
    "run_full_analysis",
    # Classes
    "ShabdaSeed",
    "ShabdaTree",
]


def run_full_analysis() -> None:
    """Run complete analysis: mathematics + forest."""
    analyze_root_mathematics()
    print("\n" + "=" * 70 + "\n")
    analyze_forest(depth=TRINITY)


if __name__ == "__main__":
    run_full_analysis()
