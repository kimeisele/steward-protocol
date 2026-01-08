from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, HolyName, MantraOpCode, MantraProtocol

from .bhagavan import Bhaga, BhagaTestResult, BhagavanProtocol
from .enforce import EnforceProtocol
from .infer import InferProtocol
from .krishna import IdentityStatus, KrishnaProtocol
from .om import OmProtocol
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
from .store_recall import StoreRecallProtocol
from .sync import SyncProtocol
from .types import (
    AccessDeniedError,
    AlignmentScore,
    Classification,
    ClassifyInput,
    DriftContext,
    EnforceContext,
    Evaluation,
    Inference,
    InferenceInput,
    KeyNotFoundError,
    MemoryValue,
    ProtocolError,
    ReadResult,
    Resonance,
    Rule,
    SovereignContext,
    SyncResult,
    SyncStatus,
    Verdict,
)
from .union import EntityStatus, UnionProtocol
from .yamaraja import DharmaVerdict, YamarajaProtocol

# NOTE: MantraInstruction has been replaced by MantraOpCode from substrate.py
# Use MantraOpCode (directly from vibe_core.protocols.substrate)
