"""
STEWARD PROTOCOL - Test Configuration
=====================================

Reads test configuration from config/quality.yaml (Phoenix Config).
NO hardcoded values - everything comes from the config.

Usage:
    pytest                      # Uses default profile (fast)
    pytest --profile=full       # Uses full profile
    pytest --profile=ci         # Uses CI profile
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Configure minimal logging for tests
logging.basicConfig(level=logging.WARNING, format="%(name)s - %(levelname)s - %(message)s")


# =============================================================================
# LOAD CONFIG FROM PHOENIX (quality.yaml)
# =============================================================================


def _load_quality_config():
    """Load QualityConfig from config/quality.yaml."""
    try:
        import yaml

        from vibe_core.phoenix.sections.quality.section_main import QualityConfig

        config_path = Path(__file__).parent.parent / "config" / "quality.yaml"
        if config_path.exists():
            data = yaml.safe_load(config_path.read_text())
            return QualityConfig.from_dict(data)
    except Exception as e:
        logging.warning(f"Failed to load quality config: {e}")

    # Fallback to defaults
    from vibe_core.phoenix.sections.quality.section_main import get_default_quality_config

    return get_default_quality_config()


# Load once at module level
_quality_config = _load_quality_config()


# =============================================================================
# PYTEST HOOKS - Connect to Phoenix Config
# =============================================================================


def pytest_addoption(parser):
    """Add --test-profile option to select test profile from config."""
    parser.addoption(
        "--test-profile",
        action="store",
        default=_quality_config.test.default_profile,
        help=f"Test profile to use. Available: {_quality_config.test.list_profiles()}",
    )


def pytest_configure(config):
    """Configure pytest from quality.yaml."""
    # OPUS-312: Set VIBE_NO_LOCK to bypass Prakriti session lock in tests
    # This prevents "Session already running" errors when running tests
    os.environ["VIBE_NO_LOCK"] = "1"

    # Register markers from config
    config.addinivalue_line("markers", "fast: Quick unit tests (<1s)")
    config.addinivalue_line("markers", "slow: Slow tests (>5s)")
    config.addinivalue_line("markers", "integration: Integration tests requiring kernel")
    config.addinivalue_line("markers", "hardening: Stress/chaos/security tests")
    config.addinivalue_line("markers", "security: Penetration and crypto tests")
    config.addinivalue_line("markers", "smoke: Quick sanity check tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "fractal: Fractal pattern tests")

    # Get selected profile
    profile_name = config.getoption("--test-profile")
    profile = _quality_config.test.get_profile(profile_name)

    # Set timeout from profile
    if profile.timeout and hasattr(config, "_inicache"):
        config._inicache["timeout"] = profile.timeout


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on location."""
    for item in items:
        # Auto-mark tests in hardening/ directory
        if "hardening" in str(item.fspath):
            item.add_marker(pytest.mark.hardening)
            item.add_marker(pytest.mark.slow)

        # Auto-mark tests in integration/ directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Auto-mark tests in fractal/ directory
        if "fractal" in str(item.fspath):
            item.add_marker(pytest.mark.fractal)

        # Auto-mark tests in e2e/ directory
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)

        # Mark tests with "slow" or "stress" in name
        if "slow" in item.name.lower() or "stress" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def constitution_path(project_root: Path) -> Path:
    """Return path to CONSTITUTION.md."""
    return project_root / "CONSTITUTION.md"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory(prefix="steward_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Reset environment variables for isolated testing."""
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def mock_kernel():
    """Create a minimal mock kernel for unit tests."""

    class MinimalMockKernel:
        def __init__(self):
            self.agent_registry = {}
            self._agent_capabilities = {}
            self._task_results = {}

        def register_agent(self, agent, spawn_process=False):
            self.agent_registry[agent.agent_id] = agent

        def get_status(self):
            return {"agents": len(self.agent_registry), "status": "RUNNING"}

        def submit_task(self, task):
            return f"task_{id(task)}"

        def get_task_result(self, task_id):
            return self._task_results.get(task_id)

    return MinimalMockKernel()


# Module-level kernel cache
_kernel_cache = {}


@pytest.fixture(scope="module")
def cached_kernel():
    """Cached kernel instance shared across tests in the same module."""
    from vibe_core.kernel_impl import RealVibeKernel

    cache_key = "default"
    if cache_key not in _kernel_cache:
        kernel = RealVibeKernel(ledger_path=":memory:", test_mode=True)
        _kernel_cache[cache_key] = kernel

    return _kernel_cache[cache_key]


@pytest.fixture
def fresh_kernel():
    """Fresh kernel instance for tests that modify kernel state."""
    from vibe_core.kernel_impl import RealVibeKernel

    return RealVibeKernel(ledger_path=":memory:", test_mode=True)


def pytest_sessionfinish(session, exitstatus):
    """Clean up cached kernels at end of test session."""
    global _kernel_cache
    for kernel in _kernel_cache.values():
        try:
            if hasattr(kernel, "shutdown"):
                kernel.shutdown(reason="Test session ended")
        except Exception:
            pass
    _kernel_cache.clear()


# =============================================================================
# QUALITY CONFIG FIXTURE (for tests that need config access)
# =============================================================================


@pytest.fixture(scope="session")
def quality_config():
    """Provide access to quality config in tests."""
    return _quality_config


# =============================================================================
# STANDARDIZED TEST FIXTURES (from test_orchestration)
# =============================================================================
# USE THESE instead of creating custom mocks or direct RealVibeKernel!
# =============================================================================


# =============================================================================
# STANDARDIZED TEST FIXTURES (from test_orchestration)
# =============================================================================
# USE THESE instead of creating custom mocks or direct RealVibeKernel!
# =============================================================================


@pytest.fixture
def test_kernel():
    """
    Minimal kernel for isolated unit tests.
    Configured via quality.yaml (fixtures.kernel_presets.minimal).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    # Verify config matches expectation (optional safety check)
    # preset = _quality_config.test.fixtures.get_kernel_preset("minimal")
    return TestKernel.minimal()


@pytest.fixture
def permissive_kernel():
    """
    Kernel that allows all operations.
    Configured via quality.yaml (fixtures.kernel_presets.permissive).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.permissive()


@pytest.fixture
def governance_kernel():
    """
    Kernel with full governance stack.
    Configured via quality.yaml (fixtures.kernel_presets.governance).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.with_governance()


@pytest.fixture
def recording_kernel():
    """
    Kernel with recording plugin.
    Configured via quality.yaml (fixtures.kernel_presets.recording).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestKernel

    return TestKernel.with_recording()


@pytest.fixture
def compliant_agent():
    """
    Fully compliant agent with valid oath.
    Configured via quality.yaml (fixtures.agents.compliant).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    conf = _quality_config.test.fixtures.get_agent_config("compliant")
    return TestAgents.compliant(agent_id=conf.id_prefix, capabilities=conf.capabilities)


@pytest.fixture
def no_oath_agent():
    """
    Agent WITHOUT oath.
    Configured via quality.yaml (fixtures.agents.no_oath).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    conf = _quality_config.test.fixtures.get_agent_config("no_oath")
    return TestAgents.without_oath(agent_id=conf.id_prefix, capabilities=conf.capabilities)


@pytest.fixture
def false_oath_agent():
    """
    Agent with oath_sworn=False.
    Configured via quality.yaml (fixtures.agents.false_oath).
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestAgents

    conf = _quality_config.test.fixtures.get_agent_config("false_oath")
    return TestAgents.with_false_oath(agent_id=conf.id_prefix, capabilities=conf.capabilities)


@pytest.fixture
def test_context():
    """
    Full test context with isolation and cleanup.
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestContext

    return TestContext()


@pytest.fixture
def test_task():
    """
    Simple test task factory.
    """
    from vibe_core.plugins.test_orchestration.fixtures import TestTasks

    return TestTasks.simple


# =============================================================================
# NAGA TEST HARNESS - Protocol-Based Testing
# =============================================================================


@pytest.fixture
def naga_harness():
    """
    NAGA Test Harness - Protocol-based, no MagicMock.

    Uses NullObjects registered via ServiceRegistry.
    Same DI pattern as production code.

    Usage:
        def test_sesha_protocol(naga_harness):
            sesha = naga_harness.sesha
            assert sesha.get_top_hash() == ""  # NullSesha behavior
    """
    from vibe_core.naga.testing import NagaTestHarness

    with NagaTestHarness() as harness:
        yield harness


@pytest.fixture
def naga_harness_minimal():
    """
    Minimal NAGA harness - only core NAGAs (Sesha, Takshaka, Vasuki).

    For tests that don't need the full federation.
    """
    from vibe_core.naga.testing import NagaTestConfig, NagaTestHarness

    config = NagaTestConfig(
        enable_kaliya=False,
        enable_karkotaka=False,
        enable_kulika=False,
        enable_padma=False,
        enable_shankha=False,
        enable_narada=False,
        enable_chitragupta=False,
        enable_prahlad=False,
        enable_ananta=False,
        enable_cortex=False,
    )

    with NagaTestHarness(config) as harness:
        yield harness


@pytest.fixture
def naga_harness_orchestrator():
    """
    NAGA harness for NagaOrchestrator tests.

    Provides:
    - InMemoryLedger (harness.ledger)
    - NullCorrectionOrchestrator (harness.correction_orchestrator)

    Does NOT register NullObjects - lets Orchestrator create real NAGAs.

    Usage:
        def test_orchestrator_bootstrap(naga_harness_orchestrator):
            from vibe_core.naga import NagaOrchestrator
            naga = NagaOrchestrator.bootstrap(
                ledger=naga_harness_orchestrator.ledger,
                correction_orchestrator=naga_harness_orchestrator.correction_orchestrator,
            )
            assert naga.is_ready()
    """
    from vibe_core.naga.testing import NagaTestHarness

    with NagaTestHarness.for_orchestrator() as harness:
        yield harness


# =============================================================================
# MAHAMANTRA TEST LIFECYCLE (Gap 1 Wiring)
# =============================================================================
# Maps pytest phases to the 16-step Mahamantra cycle:
#
#   SETUP    → Phase 1: GENESIS (H K H K) - Steps 1-4
#   CALL     → Phase 2: DHARMA (K K H H) - Steps 5-8
#            → Phase 3: KARMA (H R H R) - Steps 9-12
#   TEARDOWN → Phase 4: MOKSHA (R R H H) - Steps 13-16
#
# This is the heartbeat. Every test is a Mala bead.
# =============================================================================

# Thread-local storage for current test's Mahamantra state
_mahamantra_state = {}


# =============================================================================
# GENE INJECTION (Gap 2 Wiring)
# =============================================================================
# Each test is BORN with an iGene:
#   - entropy_load: Kali Yuga stress factor (0.0-1.0)
#   - mantra_shield: Protection via MantraByte coherence
#   - mutation_vector: Bitmask for chaos injection
#
# if entropy_load > mantra_shield.coherence → FATAL (test should fail)
# =============================================================================


def _create_test_gene(test_name: str, markers: list):
    """
    Create an iGene for a test based on its markers.

    Marker → Entropy mapping:
      @pytest.mark.hardening → 0.8 (high stress)
      @pytest.mark.integration → 0.5 (medium stress)
      @pytest.mark.slow → 0.6 (elevated stress)
      @pytest.mark.smoke → 0.1 (minimal stress)
      default → 0.3 (normal)
    """
    try:
        from vibe_core.protocols.substrate.byte import MantraByte
        from vibe_core.protocols.substrate.gene import iGene
    except ImportError:
        return None

    # Determine entropy based on markers
    marker_names = [m.name for m in markers]

    if "hardening" in marker_names:
        entropy = 0.8
    elif "slow" in marker_names:
        entropy = 0.6
    elif "integration" in marker_names:
        entropy = 0.5
    elif "smoke" in marker_names:
        entropy = 0.1
    else:
        entropy = 0.3

    # Create gene with standard Mahamantra shield
    import random

    return iGene(
        entropy_load=entropy,
        mantra_shield=MantraByte.standard_16(),
        mutation_vector=random.getrandbits(32),
    )


@pytest.fixture
def test_gene(request):
    """
    Fixture: Inject an iGene into the test.

    Usage:
        def test_something(test_gene):
            assert not test_gene.is_fatal, "Test born dead!"
            print(f"Entropy: {test_gene.entropy_load}")
            print(f"Coherence: {test_gene.mantra_shield.coherence}")

    The gene is also stored in _mahamantra_state for lifecycle access.
    """
    gene = _create_test_gene(request.node.name, list(request.node.iter_markers()))

    # Store in mahamantra state
    test_id = request.node.nodeid
    if test_id in _mahamantra_state:
        _mahamantra_state[test_id]["gene"] = gene
    else:
        _mahamantra_state[test_id] = {"gene": gene}

    return gene


@pytest.fixture
def chaos_gene(request):
    """
    Fixture: High-entropy gene for chaos/stress testing.

    Usage:
        def test_under_stress(chaos_gene):
            # This test runs with 0.9 entropy (near fatal)
            assert chaos_gene.entropy_load == 0.9
    """
    try:
        import random

        from vibe_core.protocols.substrate.byte import MantraByte
        from vibe_core.protocols.substrate.gene import iGene

        return iGene(
            entropy_load=0.9,  # Near fatal
            mantra_shield=MantraByte.standard_16(),
            mutation_vector=random.getrandbits(32),
        )
    except ImportError:
        return None


@pytest.fixture
def sattva_gene(request):
    """
    Fixture: Low-entropy gene for stable/pure testing.

    Usage:
        def test_pure_path(sattva_gene):
            # This test runs with 0.1 entropy (highly stable)
            assert not sattva_gene.is_fatal
    """
    try:
        from vibe_core.protocols.substrate.byte import MantraByte
        from vibe_core.protocols.substrate.gene import iGene

        return iGene(
            entropy_load=0.1,  # Very stable
            mantra_shield=MantraByte.standard_16(),
            mutation_vector=0,  # No mutations
        )
    except ImportError:
        return None


# =============================================================================
# THE 12TH TEST: GURU GENE (3×4 Factor)
# =============================================================================
# Uses: vibe_core/protocols/substrate/mantra/acintya.py (ParamparaProtocol)
#
# The 12th test CANNOT be computed. Only RECEIVED through grace.
# =============================================================================


@pytest.fixture
def guru_gene(request):
    """
    Fixture: The 12th Test - Guru Gene with 3/37 factor.

    Uses: vibe_core/protocols/substrate/mantra/acintya.py

    ACINTYA MATHEMATICS:
        entropy = (3 / 37) × 4 = 12/37 ≈ 0.324

    The order matters:
        3×4 = Essence first (Hare-Krishna-Rama), then structure
        4×3 = Structure first, then essence (MAYAVAD - dead)

    Both equal 12. Only one lives.

    Usage:
        def test_parampara(guru_gene):
            assert guru_gene.entropy_load == 12/37
            assert guru_gene.mutation_vector % 37 == 0  # Connected
    """
    try:
        from vibe_core.protocols.substrate.byte import MantraByte
        from vibe_core.protocols.substrate.gene import iGene
        from vibe_core.protocols.substrate.mantra.acintya import GURU_ENTROPY, PARAMPARA_VECTOR

        return iGene(
            entropy_load=GURU_ENTROPY,  # 12/37 ≈ 0.324
            mantra_shield=MantraByte.standard_16(),
            mutation_vector=PARAMPARA_VECTOR,  # 444 - NOT random!
        )
    except ImportError:
        return None


@pytest.fixture
def anti_guru_gene(request):
    """
    Fixture: The WRONG order - 4×3 (structure first, MAYAVAD).

    Uses: vibe_core/protocols/substrate/mantra/acintya.py

    SAME entropy mathematically: (4 / 37) × 3 = 12/37 ≈ 0.324
    But ontologically DEAD - structure demands essence.

    Usage:
        def test_mayavad_detection(guru_gene, anti_guru_gene):
            assert guru_gene.entropy_load == anti_guru_gene.entropy_load  # Same!
            assert guru_gene.mutation_vector % 37 == 0      # Connected
            assert anti_guru_gene.mutation_vector % 37 != 0  # Disconnected
    """
    try:
        from vibe_core.protocols.substrate.byte import MantraByte
        from vibe_core.protocols.substrate.gene import iGene
        from vibe_core.protocols.substrate.mantra.acintya import GURU_ENTROPY, PARAMPARA

        # Mutation vector NOT connected to parampara
        # 36 × 12 = 432 - NOT divisible by 37!
        disconnected_vector = (PARAMPARA - 1) * 12  # 432

        return iGene(
            entropy_load=GURU_ENTROPY,  # Same 12/37 ≈ 0.324
            mantra_shield=MantraByte.standard_16(),
            mutation_vector=disconnected_vector,  # 432 - DISCONNECTED
        )
    except ImportError:
        return None


def _get_mahamantra_sequence():
    """Lazy import to avoid circular dependencies."""
    try:
        from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, MantraOpCode

        return MAHAMANTRA_SEQUENCE, MantraOpCode
    except ImportError:
        return None, None


def _emit_mantra_step(step: int, phase: str, test_name: str):
    """Emit a Mahamantra step for the current test."""
    sequence, MantraOpCode = _get_mahamantra_sequence()
    if sequence is None:
        return

    if step < 0 or step >= 16:
        return

    word, opcode = sequence[step]
    # Log at DEBUG level - visible with pytest -v or --log-level=DEBUG
    logger = logging.getLogger("MAHAMANTRA")
    logger.debug(f"[{phase}] Step {step + 1}/16: {word} → {opcode.value} | {test_name}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """
    Phase 1: GENESIS (Hare Krishna Hare Krishna)
    Steps 1-4: SYS_WAKE, LOAD_ROOT, ALLOC_MEM, BIND_CTX

    The test is BORN.
    """
    test_id = item.nodeid
    gene = _create_test_gene(item.name, list(item.iter_markers()))
    _mahamantra_state[test_id] = {"step": 0, "phase": "GENESIS", "gene": gene}

    # Execute 4 Genesis steps
    for step in range(4):
        _emit_mantra_step(step, "GENESIS", item.name)
        _mahamantra_state[test_id]["step"] = step + 1


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    """
    Phase 2: DHARMA (Krishna Krishna Hare Hare) - Steps 5-8
    Phase 3: KARMA (Hare Rama Hare Rama) - Steps 9-12

    The test EXECUTES.
    """
    test_id = item.nodeid
    if test_id not in _mahamantra_state:
        _mahamantra_state[test_id] = {"step": 4, "phase": "DHARMA"}

    # Phase 2: DHARMA (steps 5-8)
    _mahamantra_state[test_id]["phase"] = "DHARMA"
    for step in range(4, 8):
        _emit_mantra_step(step, "DHARMA", item.name)
        _mahamantra_state[test_id]["step"] = step + 1

    # Phase 3: KARMA (steps 9-12)
    _mahamantra_state[test_id]["phase"] = "KARMA"
    for step in range(8, 12):
        _emit_mantra_step(step, "KARMA", item.name)
        _mahamantra_state[test_id]["step"] = step + 1


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """
    Phase 4: MOKSHA (Rama Rama Hare Hare)
    Steps 13-16: CACHE_STATE, OPTIMIZE, YIELD_CPU, RESET_IP

    The test DIES and returns to origin.
    """
    test_id = item.nodeid
    if test_id not in _mahamantra_state:
        _mahamantra_state[test_id] = {"step": 12, "phase": "MOKSHA"}

    # Phase 4: MOKSHA (steps 13-16)
    _mahamantra_state[test_id]["phase"] = "MOKSHA"
    for step in range(12, 16):
        _emit_mantra_step(step, "MOKSHA", item.name)
        _mahamantra_state[test_id]["step"] = step + 1

    # Clean up state
    if test_id in _mahamantra_state:
        del _mahamantra_state[test_id]


# =============================================================================
# TÜV BADGE REGISTRY (Gap 3 Wiring)
# =============================================================================
# Passing tests get a TÜV badge (certification).
# Badge level based on:
#   - Gene vitality (entropy vs coherence)
#   - Test duration
#   - Coverage (if available)
#
# Levels: BRONZE (pass), SILVER (pass + low entropy), GOLD (pass + sattva)
# =============================================================================

_tuv_badges = {}  # test_id -> TuvBadge
_tuv_metadata = {}  # test_id -> scoring breakdown dict


def _rama_metrics(test_name: str) -> dict:
    """Compute RAMA coordinate metrics from test name (0.008ms/call)."""
    try:
        from vibe_core.mahamantra.substrate.varnamala_codec import encode
    except ImportError:
        return {}
    coords = encode(test_name)
    if not coords:
        return {}
    elements = [0, 0, 0, 0, 0]  # prithvi/jala/agni/vayu/akash
    shruti_count = 0
    for c in coords:
        elements[c % 5] += 1
        if (c * c) % 49 == c:
            shruti_count += 1
    el_names = ["prithvi", "jala", "agni", "vayu", "akash"]
    return {
        "coords": coords,
        "length": len(coords),
        "dominant_element": el_names[elements.index(max(elements))],
        "element_dist": elements,
        "shruti_ratio": shruti_count / len(coords),
        "harmonic_sum": sum(c * 7 % 49 for c in coords),
    }


def _mahamantra_deep_scan(test_name: str) -> dict:
    """Run full Mahamantra API for deep diagnostics (14ms/call, use sparingly)."""
    try:
        from vibe_core.mahamantra import mahamantra

        result = mahamantra(test_name)
        return {
            "vibration": result.get("vibration", {}),
            "parampara": result.get("parampara", {}),
            "guna": result.get("guna", {}),
            "chapter": result.get("chapter"),
            "chapter_significance": result.get("chapter_significance", ""),
            "quarter": result.get("quarter", ""),
            "guardian": result.get("guardian", ""),
            "position": result.get("position"),
            "holy_name": result.get("holy_name", ""),
            "cell_prana": result.get("cell", {}).get("prana", 0),
            "cell_integrity": result.get("cell", {}).get("integrity", 0),
            "cell_alive": result.get("cell", {}).get("is_alive", False),
            "execution_success": result.get("execution", {}).get("success", False),
            "kirtan_cycles": result.get("execution", {}).get("kirtan_cycles", 0),
            "smaranam_top": result.get("smaranam", [{}])[0] if result.get("smaranam") else {},
        }
    except Exception:
        return {}


def _count_report_warnings(report) -> int:
    """Count warning-level messages from report captured sections."""
    count = 0
    for name, content in getattr(report, "sections", []):
        lname = name.lower()
        if "stderr" in lname or "log" in lname:
            for line in content.splitlines():
                if "WARNING" in line or "warning" in line.split("-")[0]:
                    count += 1
    return count


def _issue_tuv_badge(test_id: str, duration: float, gene_data: dict, report=None):
    """
    Issue a TÜV badge with 6 scoring dimensions.

    Dimensions (max 1.0):
      0.30 base          — test passed
      0.20 gene quality  — entropy ≤0.3: sattva(+0.20), ≤0.5: rajas(+0.10)
      0.15 speed         — <0.1s: +0.15, <1s: +0.10, <5s: +0.05
      0.15 clean run     — 0 warnings: +0.15, ≤2: +0.10, ≤5: +0.05
      0.10 parampara     — mutation_vector % 37 == 0
      0.10 lifecycle     — all 16 maha steps completed
    """
    try:
        import hashlib
        from datetime import datetime, timedelta

        from vibe_core.protocols.naga.tuv import TuvBadge
    except ImportError:
        return None

    # --- Dimension 1: Base (passed) ---
    score = 0.30
    breakdown = {"base": 0.30}

    # --- Dimension 2: Gene quality ---
    gene_score = 0.0
    entropy = None
    gene = gene_data.get("gene") if gene_data else None
    if gene and hasattr(gene, "entropy_load"):
        entropy = gene.entropy_load
        if entropy <= 0.3:
            gene_score = 0.20  # Sattva
        elif entropy <= 0.5:
            gene_score = 0.10  # Rajas
    score += gene_score
    breakdown["gene"] = gene_score

    # --- Dimension 3: Speed ---
    speed_score = 0.0
    if duration < 0.1:
        speed_score = 0.15
    elif duration < 1.0:
        speed_score = 0.10
    elif duration < 5.0:
        speed_score = 0.05
    score += speed_score
    breakdown["speed"] = speed_score

    # --- Dimension 4: Clean execution ---
    warning_count = _count_report_warnings(report) if report else 0
    clean_score = 0.0
    if warning_count == 0:
        clean_score = 0.15
    elif warning_count <= 2:
        clean_score = 0.10
    elif warning_count <= 5:
        clean_score = 0.05
    score += clean_score
    breakdown["clean"] = clean_score

    # --- Dimension 5: Parampara connection ---
    parampara_score = 0.0
    if gene and hasattr(gene, "mutation_vector"):
        if gene.mutation_vector % 37 == 0:
            parampara_score = 0.10
    score += parampara_score
    breakdown["parampara"] = parampara_score

    # --- Dimension 6: Lifecycle completeness ---
    # Badge is issued after "call" phase (step 12). MOKSHA (13-16) = teardown.
    # Lifecycle complete = GENESIS(4) + DHARMA(8) + KARMA(12) all executed.
    lifecycle_score = 0.0
    step = gene_data.get("step", 0) if gene_data else 0
    if step >= 12:
        lifecycle_score = 0.10
    score += lifecycle_score
    breakdown["lifecycle"] = lifecycle_score

    score = min(max(score, 0.0), 1.0)

    # Create signature
    sig_data = f"{test_id}:{score}:{datetime.now().isoformat()}"
    signature = hashlib.sha256(sig_data.encode()).hexdigest()[:16]

    badge = TuvBadge(
        entity_id=test_id,
        issued_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
        score=score,
        signature=f"TÜV-{signature}",
    )

    _tuv_badges[test_id] = badge
    # RAMA coordinate analysis (0.008ms — essentially free)
    short_name = test_id.split("::")[-1] if "::" in test_id else test_id
    rama = _rama_metrics(short_name)
    _tuv_metadata[test_id] = {
        "score": score,
        "breakdown": breakdown,
        "duration": duration,
        "entropy": entropy,
        "warnings": warning_count,
        "step": step,
        "rama": rama,
    }
    return badge


def _get_badge_level(score: float) -> str:
    """Convert score to badge level."""
    if score >= 0.9:
        return "GOLD"
    elif score >= 0.7:
        return "SILVER"
    else:
        return "BRONZE"


@pytest.fixture
def tuv_badge(request):
    """
    Fixture: Access the TÜV badge for this test (after completion).

    Note: Badge is issued AFTER test passes, so this fixture
    returns a function to retrieve it post-test.

    Usage:
        def test_with_badge(tuv_badge):
            # ... test logic ...
            # Badge will be issued after test passes
    """
    test_id = request.node.nodeid

    def get_badge():
        return _tuv_badges.get(test_id)

    return get_badge


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Print TÜV badge summary with full diagnostics.
    """
    if not _tuv_badges:
        return

    total = len(_tuv_badges)
    scores = [b.score for b in _tuv_badges.values()]
    gold = sum(1 for s in scores if s >= 0.9)
    silver = sum(1 for s in scores if 0.7 <= s < 0.9)
    bronze = sum(1 for s in scores if s < 0.7)
    avg_score = sum(scores) / total

    terminalreporter.write_sep("=", "TÜV BADGE SUMMARY")
    terminalreporter.write_line(
        f"Total Badges Issued: {total}"
        f"  GOLD: {gold}  SILVER: {silver}  BRONZE: {bronze}"
        f"  Average Score: {avg_score:.2f}"
    )

    # --- Score Distribution ---
    bins = [(0.9, 1.01, "GOLD  "), (0.7, 0.9, "SILVER"), (0.5, 0.7, "BRONZE"), (0.0, 0.5, "BRONZE")]
    terminalreporter.write_line("")
    terminalreporter.write_line("SCORE DISTRIBUTION:")
    max_bar = 30
    for lo, hi, label in bins:
        count = sum(1 for s in scores if lo <= s < hi)
        if count == 0:
            continue
        bar_len = int((count / total) * max_bar) if total > 0 else 0
        bar = "\u2588" * bar_len + "\u2591" * (max_bar - bar_len)
        terminalreporter.write_line(f"  {lo:.1f}-{hi:.2f} {bar} {count:3d}  {label}")

    # --- Dimension Breakdown (aggregate) ---
    if _tuv_metadata:
        dims = {"gene": [], "speed": [], "clean": [], "parampara": [], "lifecycle": []}
        for meta in _tuv_metadata.values():
            bd = meta.get("breakdown", {})
            for dim in dims:
                dims[dim].append(bd.get(dim, 0.0))

        terminalreporter.write_line("")
        terminalreporter.write_line("SCORING DIMENSIONS (how many tests hit max):")
        dim_max = {"gene": 0.20, "speed": 0.15, "clean": 0.15, "parampara": 0.10, "lifecycle": 0.10}
        dim_labels = {
            "gene": "Gene Quality",
            "speed": "Speed",
            "clean": "Clean Run",
            "parampara": "Parampara",
            "lifecycle": "Lifecycle",
        }
        for dim, max_val in dim_max.items():
            vals = dims[dim]
            at_max = sum(1 for v in vals if v >= max_val)
            at_zero = sum(1 for v in vals if v == 0.0)
            partial = total - at_max - at_zero
            terminalreporter.write_line(
                f"  {dim_labels[dim]:<14s}  max: {at_max:3d}/{total}"
                f"  partial: {partial:3d}/{total}"
                f"  zero: {at_zero:3d}/{total}"
            )

    # --- Warning Summary ---
    if _tuv_metadata:
        warning_tests = [(tid, m["warnings"]) for tid, m in _tuv_metadata.items() if m.get("warnings", 0) > 0]
        if warning_tests:
            warning_tests.sort(key=lambda x: x[1], reverse=True)
            total_warnings = sum(w for _, w in warning_tests)
            terminalreporter.write_line("")
            terminalreporter.write_line(f"WARNINGS: {total_warnings} total across {len(warning_tests)}/{total} tests")
            for tid, wcount in warning_tests[:5]:
                short_id = tid.split("::")[-1] if "::" in tid else tid
                terminalreporter.write_line(f"  {wcount:3d} warnings  {short_id}")
            if len(warning_tests) > 5:
                terminalreporter.write_line(f"  ... and {len(warning_tests) - 5} more")

    # --- Worst Performers ---
    if _tuv_metadata and total > 3:
        sorted_badges = sorted(_tuv_badges.items(), key=lambda x: x[1].score)
        worst = sorted_badges[:5]
        best_score = sorted_badges[-1][1].score
        worst_score = sorted_badges[0][1].score

        if worst_score < best_score:
            terminalreporter.write_line("")
            terminalreporter.write_line(f"WORST PERFORMERS (range {worst_score:.2f} - {best_score:.2f}):")
            for tid, badge in worst:
                short_id = tid.split("::")[-1] if "::" in tid else tid
                meta = _tuv_metadata.get(tid, {})
                issues = []
                bd = meta.get("breakdown", {})
                if bd.get("gene", 0) == 0:
                    ent = meta.get("entropy")
                    issues.append(f"entropy={ent:.2f}" if ent is not None else "no gene")
                if bd.get("clean", 0) == 0:
                    issues.append(f"{meta.get('warnings', '?')}w")
                if bd.get("speed", 0) == 0:
                    issues.append(f"{meta.get('duration', 0):.1f}s")
                if bd.get("parampara", 0) == 0:
                    issues.append("no parampara")
                detail = ", ".join(issues) if issues else "low across dimensions"
                level = _get_badge_level(badge.score)
                terminalreporter.write_line(f"  {badge.score:.2f} {level:<6s} {short_id} ({detail})")

    # --- RAMA Coordinate Analysis (aggregate) ---
    if _tuv_metadata:
        el_totals = {"prithvi": 0, "jala": 0, "agni": 0, "vayu": 0, "akash": 0}
        shruti_sum = 0.0
        rama_count = 0
        for meta in _tuv_metadata.values():
            rama = meta.get("rama", {})
            if rama:
                el = rama.get("dominant_element", "")
                if el in el_totals:
                    el_totals[el] += 1
                shruti_sum += rama.get("shruti_ratio", 0)
                rama_count += 1
        if rama_count > 0:
            terminalreporter.write_line("")
            terminalreporter.write_line("RAMA COORDINATES (phonemic fingerprint of test names):")
            terminalreporter.write_line(
                "  Elements: " + "  ".join(f"{k}={v}" for k, v in sorted(el_totals.items(), key=lambda x: -x[1]))
            )
            terminalreporter.write_line(f"  Avg Shruti Ratio: {shruti_sum / rama_count:.3f}")

    # --- Deep Mahamantra Scan (worst 5 only — 14ms/call) ---
    if _tuv_metadata and total > 3:
        sorted_meta = sorted(_tuv_badges.items(), key=lambda x: x[1].score)
        worst_5 = sorted_meta[:5]
        terminalreporter.write_line("")
        terminalreporter.write_line("MAHAMANTRA DEEP SCAN (worst 5 tests):")
        for tid, badge in worst_5:
            short_id = tid.split("::")[-1] if "::" in tid else tid
            deep = _mahamantra_deep_scan(short_id)
            if not deep:
                terminalreporter.write_line(f"  {short_id}: [scan unavailable]")
                continue
            guna = deep.get("guna", {}).get("mode", "?")
            ch = deep.get("chapter", "?")
            ch_sig = deep.get("chapter_significance", "")
            quarter = deep.get("quarter", "?")
            guardian = deep.get("guardian", "?")
            prana = deep.get("cell_prana", 0)
            integrity = deep.get("cell_integrity", 0)
            alive = deep.get("cell_alive", False)
            word = deep.get("smaranam_top", {})
            sanskrit = word.get("sanskrit", "-")
            meaning = word.get("meaning", "-")
            terminalreporter.write_line(f"  {badge.score:.2f} {short_id}")
            terminalreporter.write_line(f"       Guna: {guna} | Ch.{ch} {ch_sig} | {quarter}/{guardian}")
            terminalreporter.write_line(
                f"       Cell: prana={prana} integrity={integrity:.3f}"
                f" {'ALIVE' if alive else 'DEAD'}"
                f' | Resonance: "{sanskrit}" ({meaning})'
            )


def pytest_runtest_logreport(report):
    """
    Log Mahamantra completion status with test result.
    Issues TÜV badge to passing tests.
    """
    if report.when == "call":
        logger = logging.getLogger("MAHAMANTRA")
        test_id = report.nodeid

        # Get gene info if available
        gene_status = ""
        gene_data = _mahamantra_state.get(test_id, {})
        if "gene" in gene_data:
            gene = gene_data["gene"]
            if gene:
                coherence = gene.mantra_shield.coherence
                entropy = gene.entropy_load
                vital = "ALIVE" if not gene.is_fatal else "FATAL"
                gene_status = f" | Gene: {vital} (E={entropy:.2f}, C={coherence:.2f})"

        # Issue badge and log result
        badge_status = ""
        if report.passed:
            badge = _issue_tuv_badge(test_id, report.duration, gene_data, report=report)
            if badge:
                level = _get_badge_level(badge.score)
                badge_status = f" | TÜV: {level} ({badge.score:.2f})"
            logger.debug(f"✓ MALA BEAD COMPLETE: {test_id}{gene_status}{badge_status}")
        elif report.failed:
            logger.debug(f"✗ APARADHA (offense): {test_id}{gene_status}")
        elif report.skipped:
            logger.debug(f"○ PRATYAHARA (withdrawal): {test_id}{gene_status}")


# =============================================================================
# TESTABLE REGISTRY → PYTEST BRIDGE (Gap 4 Wiring)
# =============================================================================
# Converts TestableRegistry's discovered TestCases into real pytest tests.
#
# The bridge works in two modes:
#   1. LAZY: Fixture-based (test_registry_cases) - for manual parametrization
#   2. EAGER: Hook-based (pytest_generate_tests) - auto-generates tests
#
# Each TestCase from the registry becomes a pytest test that:
#   - Runs the TestCase.test_func with a fresh kernel
#   - Inherits Mahamantra lifecycle (Gap 1)
#   - Gets injected with iGene (Gap 2)
#   - Receives TÜV badge on pass (Gap 3)
# =============================================================================

_testable_registry = None


def _get_testable_registry():
    """Lazy-load the global testable registry."""
    global _testable_registry
    if _testable_registry is None:
        try:
            from vibe_core.protocols.testable_registry import get_global_registry

            _testable_registry = get_global_registry()
        except ImportError:
            return None
    return _testable_registry


@pytest.fixture(scope="session")
def testable_registry():
    """
    Fixture: Access the global TestableRegistry.

    Usage:
        def test_registry_discovery(testable_registry, fresh_kernel):
            testable_registry.discover_from_kernel(fresh_kernel)
            summary = testable_registry.get_summary()
            print(f"Discovered {summary['total_testables']} components")
    """
    return _get_testable_registry()


@pytest.fixture(scope="session")
def discovered_test_cases(testable_registry, request):
    """
    Fixture: Get all discovered TestCases after kernel discovery.

    This fixture triggers discovery from a fresh kernel and returns
    all TestCase objects for parametrized testing.

    Usage:
        @pytest.mark.parametrize("case", discovered_test_cases())
        def test_discovered(case, fresh_kernel):
            result = case.test_func(fresh_kernel, {})
            assert result is True
    """
    if testable_registry is None:
        return []

    # Try to discover from a fresh kernel if available
    # This is session-scoped, so discovery happens once
    try:
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(test_mode=True, load_plugins=False, ledger_path=":memory:")
        testable_registry.discover_from_kernel(kernel)
    except Exception as e:
        logging.warning(f"Failed to discover testables: {e}")

    return testable_registry.get_all_test_cases()


def pytest_generate_tests(metafunc):
    """
    Pytest hook: Dynamically generate tests from TestableRegistry.

    If a test has a 'registry_test_case' fixture, parametrize it with
    all discovered TestCases from the registry.

    Usage:
        def test_registry_component(registry_test_case, fresh_kernel):
            # registry_test_case is a TestCase from the registry
            result = registry_test_case.test_func(fresh_kernel, {})
            assert result is True, registry_test_case.description
    """
    if "registry_test_case" in metafunc.fixturenames:
        registry = _get_testable_registry()
        if registry is None:
            # No registry available, skip parametrization
            metafunc.parametrize("registry_test_case", [], ids=[])
            return

        # Discover if not already done
        if len(registry.testables) == 0:
            try:
                from vibe_core.kernel_impl import RealVibeKernel

                kernel = RealVibeKernel(test_mode=True, load_plugins=False, ledger_path=":memory:")
                registry.discover_from_kernel(kernel)
            except Exception:
                pass

        # Get all test cases
        cases = registry.get_all_test_cases()

        # Create IDs from test case names
        ids = [case.name for case in cases]

        metafunc.parametrize("registry_test_case", cases, ids=ids)


@pytest.fixture
def registry_test_case():
    """
    Placeholder fixture for registry test cases.
    Actual value is injected via pytest_generate_tests parametrization.
    """
    return None


@pytest.fixture
def run_registry_test(fresh_kernel, test_gene):
    """
    Fixture factory: Run a TestCase from the registry.

    Provides a function that executes a TestCase with:
      - Fresh kernel instance
      - Gene-based entropy context
      - Proper timeout handling

    Usage:
        def test_my_registry_tests(run_registry_test, testable_registry):
            for case in testable_registry.get_all_test_cases():
                result = run_registry_test(case)
                assert result.success, f"{case.name} failed"
    """
    import asyncio
    from dataclasses import dataclass

    @dataclass
    class TestResult:
        success: bool
        message: str
        duration_ms: float

    def _run(test_case):
        """Execute a TestCase and return result."""
        import time

        start = time.time()

        try:
            # Handle both sync and async test functions
            test_func = test_case.test_func
            timeout_s = test_case.timeout_ms / 1000.0

            if asyncio.iscoroutinefunction(test_func):
                # Async test
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                coro = test_func(fresh_kernel, {"gene": test_gene})
                result = loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout_s))
            else:
                # Sync test
                result = test_func(fresh_kernel, {"gene": test_gene})

            duration = (time.time() - start) * 1000

            if result:
                return TestResult(True, "PASSED", duration)
            else:
                return TestResult(False, "FAILED: returned False", duration)

        except asyncio.TimeoutError:
            duration = (time.time() - start) * 1000
            return TestResult(False, f"TIMEOUT after {test_case.timeout_ms}ms", duration)
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult(False, f"ERROR: {e}", duration)

    return _run


# =============================================================================
# REGISTRY SUMMARY HOOK
# =============================================================================


def pytest_report_header(config):
    """Add TestableRegistry info to pytest header."""
    registry = _get_testable_registry()
    if registry is None:
        return []

    try:
        summary = registry.get_summary()
        if summary["total_testables"] > 0:
            return [
                f"TestableRegistry: {summary['total_testables']} components, {summary['total_tests']} generated tests"
            ]
    except Exception:
        pass

    return []
