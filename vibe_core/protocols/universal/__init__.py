# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xf582f957"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.substrate import (
    MAHAMANTRA_SEQUENCE,
    AlignmentScore,
    DriftContext,
    HolyName,
    MantraOpCode,
    MantraProtocol,
    Resonance,
)

from .autobahn import AutobahnProtocol, GermanAutobahn, Lane, VajraPacket
from .bhagavan import Bhaga, BhagaTestResult, BhagavanProtocol
from .bridge import MayavadError, SetuBandha
from .cli import AnantaResponse, AnantaShesha, ShellProtocol
from .dharma import DharmaGuard, DharmaVerdict, UniversalDharma
from .enforce import EnforceProtocol
from .infer import InferProtocol
from .jagannath import JagannathDeity, JagannathProtocol, PuriTemple, RathaYatra
from .krishna import IdentityStatus, KrishnaProtocol
from .mantra import MantraProtocol

# PRABHUPADA is in substrate/mantra/ - where he belongs (near the Mahamantra)
from vibe_core.protocols.substrate.mantra.prabhupada import (
    PRABHUPADA,
    PrabhupadaVani,
    SrilaPrabhupada,
    VaniInstruction,
)
from .rama import RamaProtocol
from .ramanujan import RamanujanProtocol
from .read_write import ReadWriteProtocol
from .resonance import (
    AcintyaState,
    NullResonance,
    Quality,
    ResonanceProtocol,
    SemanticVibration,
    StructuralIntegrity,
    SystemAction,
    create_structure,
    create_substance,
    get_quality_from_vector,
)
from .steward import StewardProtocol, VedicSteward
from .store_recall import StoreRecallProtocol
from .sync import SyncProtocol
from .types import (
    AccessDeniedError,
    Classification,
    ClassifyInput,
    EnforceContext,
    Evaluation,
    Inference,
    InferenceInput,
    KeyNotFoundError,
    MemoryValue,
    ProtocolError,
    ReadResult,
    Rule,
    SovereignContext,
    SyncResult,
    SyncStatus,
    TranscendentalQuality,  # The 64 Qualities
    ProtectedMemory,
    SankhyaDualism,
    KarmaCounter,
    VisvarupaSnapshot,
)
from .types import (
    Verdict as TypeVerdict,
)
from .types import Verdict  # Direct export for backward compatibility
from .union import EntityStatus, UnionProtocol
# from .yamaraja import Judgment, Verdict, YamarajaGate

# NOTE: MantraInstruction has been replaced by MantraOpCode from substrate.py
# Use MantraOpCode (directly from vibe_core.protocols.substrate)
