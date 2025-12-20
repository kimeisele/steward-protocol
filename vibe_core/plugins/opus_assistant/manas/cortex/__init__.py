"""
MANAS Cortex - The Sensory-Motor Interface.

OPUS-041: VAK (The Voice) - ShellCortex
OPUS-042: SAMVADA (The Dialogue) - SamvadaListener/Client
OPUS-043: JNANA (The Conversation) - JnanaHandler
OPUS-050: VEDA (The Knowledge) - VedaPipeline
OPUS-051: MANDALA (The Configuration) - ConfigWeaver
OPUS-052: AKASHA (The Space) - AkashaQuery/Sync
OPUS-053: SILPA (The Craft) - SilpaArchitect
OPUS-054: SUTRA (The Thread) - SutraWeaver/Orchestrator
OPUS-055: SANKALPA (The Will) - SankalpaOrchestrator
OPUS-059: PRAMANA (The Valid Proof) - TestCortex

Additional modules:
- DHARMA: Architecture audit
- KRIYA: Intent extraction
- MUKHA: Identity/Interface generation

The cortex modules provide MANAS with interfaces to the external world:
- Processing, Configuration, Knowledge, Refactoring, Documentation
- Strategy, Architecture, Intent, Identity
- Shell, Dialogue, Conversation, Testing

"The brain alone is not enough - it needs hands to act and ears to hear."
"""

# OPUS-099: BaseSense (VEDA-4 auto-discovery)
# OPUS-041: VAK (The Voice)
# OPUS-052: AKASHA (The Cosmic Ether)
from vibe_core.plugins.opus_assistant.manas.cortex.akasha import (
    AkashaContext,
    AkashaNode,
    AkashaPort,
    AkashaQuery,
    AkashaSync,
)
from vibe_core.plugins.opus_assistant.manas.cortex.base import BaseSense

# OPUS-100: BaseAction (VEDA-4 auto-discovery)
from vibe_core.plugins.opus_assistant.manas.cortex.base_action import ActionResult, BaseAction

# DHARMA (Architecture Audit)
from vibe_core.plugins.opus_assistant.manas.cortex.dharma import (
    ArchitecturalViolation,
    DharmaAuditor,
    DriftReport,
)

# OPUS-130: DHARMA SENSE (The 2nd Sense - Ethics)
from vibe_core.plugins.opus_assistant.manas.cortex.dharma_sense import (
    DharmaSense,
)

# OPUS-043: JNANA (The Conversation)
from vibe_core.plugins.opus_assistant.manas.cortex.jnana import JnanaHandler

# OPUS-131: KARMA SENSE (The 4th Sense - Memory)
from vibe_core.plugins.opus_assistant.manas.cortex.karma_sense import (
    KarmaSense,
)

# KRIYA (Intent Extraction)
from vibe_core.plugins.opus_assistant.manas.cortex.kriya import (
    ExtractedIntent,
    KriyaBridge,
    KriyaExtractor,
)

# OPUS-051: MANDALA (The Fractal Configuration)
from vibe_core.plugins.opus_assistant.manas.cortex.mandala import (
    CapabilitySpec,
    ConfigWeaver,
    FractalManifest,
    ToolManifest,
)

# MUKHA (Identity/Interface)
from vibe_core.plugins.opus_assistant.manas.cortex.mukha import (
    AgentIdentity,
    IdentityScanner,
    MukhaGenerator,
)

# OPUS-009: PRAKRITI SENSE (Das sechste Jnanendriya)
from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import (
    GunaSummary,
    LobotomyReport,
    PrakritiSense,
    handle_prakriti_query,
)

# OPUS-166: PRANA ACTION (The Hands of Life Force)
from vibe_core.plugins.opus_assistant.manas.cortex.prana_action import (
    PranaAction,
)

# OPUS-166: PRANA SENSE (The 7th Sense - Agent Presence)
from vibe_core.plugins.opus_assistant.manas.cortex.prana_sense import (
    AgentPresence,
    PranaPerception,
    PranaSense,
    PresenceChange,
)

# OPUS-042: SAMVADA (The Dialogue)
from vibe_core.plugins.opus_assistant.manas.cortex.samvada import (
    SamvadaClient,
    SamvadaListener,
    SamvadaMessage,
    SamvadaResponse,
    chat,
    chat_sync,
)
from vibe_core.plugins.opus_assistant.manas.cortex.samvada_handler import (
    SamvadaHandler,
    create_manas_handler,
)

# OPUS-055: SANKALPA (The Will)
from vibe_core.plugins.opus_assistant.manas.cortex.sankalpa import (
    SankalpaOrchestrator,
)
from vibe_core.plugins.opus_assistant.manas.cortex.shell import (
    CommandRisk,
    ShellCortex,
    ShellResult,
)

# OPUS-053: SILPA (The Self-Architect)
from vibe_core.plugins.opus_assistant.manas.cortex.silpa import (
    RefactorRisk,
    RefactorType,
    SilpaArchitect,
    SilpaAuditor,
    SilpaPlan,
    SilpaTransformer,
)

# OPUS-054: SUTRA (The Thread)
from vibe_core.plugins.opus_assistant.manas.cortex.sutra import (
    SutraOrchestrator,
    SutraWeaver,
    WikiPage,
    WikiPageType,
    WikiSync,
)

# OPUS-131: SUTRA SENSE (The 3rd Sense - Knowledge Threads)
from vibe_core.plugins.opus_assistant.manas.cortex.sutra_sense import (
    SutraSense,
)

# OPUS-059: PRAMANA (The Valid Proof)
from vibe_core.plugins.opus_assistant.manas.cortex.test import (
    TestCortex,
    TestCortexResult,
    TestScope,
)

# OPUS-050: VEDA (The Four-Fold Knowledge)
from vibe_core.plugins.opus_assistant.manas.cortex.veda import (
    Artha,
    Karma,
    Pratyaya,
    Shabda,
    VedaContext,
    VedaIntent,
    VedaPipeline,
)

# OPUS-133: VIVEKA ACTION (The Hands of Discrimination)
from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import (
    VivekaAction,
)

# OPUS-132: VIVEKA SENSE (The 5th Sense - Discrimination)
from vibe_core.plugins.opus_assistant.manas.cortex.viveka_sense import (
    CoverageGap,
    TriagePriority,
    VivekaReport,
    VivekaSense,
)

__all__ = [
    # OPUS-099: BaseSense (VEDA-4 auto-discovery)
    "BaseSense",
    # OPUS-100: BaseAction (VEDA-4 auto-discovery)
    "BaseAction",
    "ActionResult",
    # OPUS-041: VAK (The Voice)
    "ShellCortex",
    "ShellResult",
    "CommandRisk",
    # OPUS-042: SAMVADA (The Dialogue)
    "SamvadaListener",
    "SamvadaClient",
    "SamvadaMessage",
    "SamvadaResponse",
    "SamvadaHandler",
    "chat",
    "chat_sync",
    "create_manas_handler",
    # OPUS-043: JNANA (The Conversation)
    "JnanaHandler",
    # OPUS-050: VEDA (The Four-Fold Knowledge)
    "VedaPipeline",
    "VedaIntent",
    "VedaContext",
    "Shabda",
    "Artha",
    "Pratyaya",
    "Karma",
    # OPUS-051: MANDALA (The Fractal Configuration)
    "ConfigWeaver",
    "FractalManifest",
    "CapabilitySpec",
    "ToolManifest",
    # OPUS-052: AKASHA (The Cosmic Ether)
    "AkashaQuery",
    "AkashaSync",
    "AkashaContext",
    "AkashaNode",
    "AkashaPort",
    # OPUS-053: SILPA (The Self-Architect)
    "SilpaArchitect",
    "SilpaTransformer",
    "SilpaAuditor",
    "SilpaPlan",
    "RefactorRisk",
    "RefactorType",
    # OPUS-054: SUTRA (The Thread)
    "SutraWeaver",
    "SutraOrchestrator",
    "WikiPage",
    "WikiPageType",
    "WikiSync",
    # OPUS-055: SANKALPA (The Will)
    "SankalpaOrchestrator",
    # OPUS-059: PRAMANA (The Valid Proof)
    "TestCortex",
    "TestCortexResult",
    "TestScope",
    # DHARMA (Architecture Audit)
    "DharmaAuditor",
    "DriftReport",
    "ArchitecturalViolation",
    # KRIYA (Intent Extraction)
    "KriyaExtractor",
    "KriyaBridge",
    "ExtractedIntent",
    # MUKHA (Identity/Interface)
    "MukhaGenerator",
    "IdentityScanner",
    "AgentIdentity",
    # OPUS-166: PRANA SENSE (The 7th Sense - Agent Presence)
    "PranaSense",
    "PranaPerception",
    "AgentPresence",
    "PresenceChange",
    # OPUS-009: PRAKRITI SENSE (The 1st Sense - State)
    "PrakritiSense",
    "GunaSummary",
    "LobotomyReport",
    "handle_prakriti_query",
    # OPUS-130: DHARMA SENSE (The 2nd Sense - Ethics)
    "DharmaSense",
    # OPUS-131: SUTRA SENSE (The 3rd Sense - Knowledge)
    "SutraSense",
    # OPUS-131: KARMA SENSE (The 4th Sense - Memory)
    "KarmaSense",
    # OPUS-132: VIVEKA SENSE (The 5th Sense - Discrimination)
    "VivekaSense",
    "VivekaReport",
    "CoverageGap",
    "TriagePriority",
    # OPUS-166: PRANA ACTION (The Hands of Life Force)
    "PranaAction",
    # OPUS-133: VIVEKA ACTION (The Hands of Discrimination)
    "VivekaAction",
]
