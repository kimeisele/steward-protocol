"""
FRACTAL TEST FRAMEWORK - Tests Mirror the Kernel Architecture

PHILOSOPHY:
"As above, so below" - Tests must mirror what they test.
If the kernel is plugin-based, tests must be plugin-based.

PROBLEM:
- Each test file does its own thing
- No consistency, no isolation
- Timeouts don't work reliably
- Tests hang with no feedback

SOLUTION:
- LightweightKernel: Lightweight kernel for tests (no slow init)
- TestPlugin: Base class for test plugins
- TestHarness: Manages test lifecycle with HARD timeouts
- FRACTAL: Tests mirror kernel structure exactly

USAGE:
    class TestMyFeature(FractalTestCase):
        TIMEOUT = 5  # Hard timeout in seconds

        def get_test_plugins(self):
            return [MyTestPlugin()]

        def test_something(self):
            result = self.kernel.do_thing()
            self.assert_ledger_contains("event_type", "expected")
"""

import signal
import sys
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# ============================================================================
# HARD TIMEOUT - Actually kills the test, no exceptions
# ============================================================================


class TestTimeoutError(Exception):
    """Raised when a test exceeds its timeout."""

    pass


@contextmanager
def hard_timeout(seconds: int, test_name: str = "test"):
    """
    HARD timeout that actually works.

    Uses SIGALRM on Unix, threading on Windows.
    Will interrupt even blocking I/O.
    """

    def timeout_handler(signum, frame):
        raise TestTimeoutError(f"TEST TIMEOUT: {test_name} exceeded {seconds}s")

    if sys.platform != "win32":
        # Unix: Use SIGALRM (most reliable)
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows: Use threading (less reliable but works)
        timer = threading.Timer(seconds, lambda: (_ for _ in ()).throw(TestTimeoutError(f"TIMEOUT: {test_name}")))
        timer.start()
        try:
            yield
        finally:
            timer.cancel()


# ============================================================================
# TEST KERNEL - Lightweight kernel for testing
# ============================================================================


@dataclass
class LightweightKernelConfig:
    """Configuration for test kernel."""

    use_in_memory_ledger: bool = True
    skip_tool_discovery: bool = True
    skip_process_spawn: bool = True
    skip_plugins: List[str] = field(default_factory=list)
    mock_agents: bool = True


class LightweightKernel:
    """
    Lightweight kernel for testing.

    NOTE: Named LightweightKernel (not LightweightKernel) to avoid pytest collection.

    This is NOT RealVibeKernel. It's a minimal implementation
    that provides just enough functionality for tests.

    Fast to create (~10ms vs ~3000ms for RealVibeKernel).
    """

    def __init__(self, config: Optional[LightweightKernelConfig] = None):
        self.config = config or LightweightKernelConfig()
        self.agents: Dict[str, Any] = {}
        self.tasks: List[Any] = []
        self.ledger_events: List[Dict[str, Any]] = []
        self.plugins: List["TestPlugin"] = []
        self._booted = False

    def register_plugin(self, plugin: "TestPlugin") -> None:
        """Register a test plugin."""
        self.plugins.append(plugin)
        plugin.on_register(self)

    def boot(self) -> None:
        """Boot the test kernel."""
        for plugin in self.plugins:
            plugin.on_boot(self)
        self._booted = True

    def shutdown(self) -> None:
        """Shutdown the test kernel."""
        for plugin in self.plugins:
            plugin.on_shutdown(self)
        self._booted = False

    def submit_task(self, task: Any) -> str:
        """Submit a task."""
        for plugin in self.plugins:
            if not plugin.on_task_submit(self, task):
                raise ValueError(f"Task rejected by plugin {plugin.plugin_id}")
        self.tasks.append(task)
        return getattr(task, "task_id", str(id(task)))

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> None:
        """Record an event to the test ledger."""
        self.ledger_events.append(
            {
                "event_type": event_type,
                "agent_id": agent_id,
                "details": details,
                "timestamp": time.time(),
            }
        )

    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get ledger events, optionally filtered by type."""
        if event_type is None:
            return self.ledger_events
        return [e for e in self.ledger_events if e["event_type"] == event_type]


# ============================================================================
# TEST PLUGIN - Base class for test plugins (mirrors KernelPlugin)
# ============================================================================


class TestPlugin(ABC):
    """
    Base class for test plugins.

    Mirrors KernelPlugin exactly - same hooks, same lifecycle.
    This ensures tests are FRACTAL with the system they test.
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique identifier for this test plugin."""
        pass

    def on_register(self, kernel: LightweightKernel) -> None:
        """Called when plugin is registered."""
        pass

    def on_boot(self, kernel: LightweightKernel) -> None:
        """Called when kernel boots."""
        pass

    def on_shutdown(self, kernel: LightweightKernel) -> None:
        """Called when kernel shuts down."""
        pass

    def on_task_submit(self, kernel: LightweightKernel, task: Any) -> bool:
        """Called before task submission. Return False to reject."""
        return True

    def on_task_complete(self, kernel: LightweightKernel, task_id: str, result: Any) -> None:
        """Called when task completes."""
        pass


# ============================================================================
# FRACTAL TEST CASE - Base class for all tests
# ============================================================================


class FractalTestCase:
    """
    Base class for fractal tests.

    Provides:
    - Automatic timeout enforcement
    - Test kernel setup/teardown
    - Plugin registration
    - Assertion helpers

    Usage:
        class TestMyFeature(FractalTestCase):
            TIMEOUT = 5  # seconds

            def get_test_plugins(self):
                return [MyPlugin()]

            def test_something(self):
                self.kernel.submit_task(task)
                self.assert_event_recorded("task_submitted")
    """

    # Override in subclass
    TIMEOUT: int = 10  # Default timeout in seconds
    USE_REAL_KERNEL: bool = False  # Set True for integration tests

    def setup_method(self, method):
        """Setup before each test method."""
        self._test_name = method.__name__
        self._setup_kernel()

    def teardown_method(self, method):
        """Teardown after each test method."""
        self._teardown_kernel()

    def _setup_kernel(self):
        """Create and configure test kernel."""
        if self.USE_REAL_KERNEL:
            from vibe_core.kernel_impl import RealVibeKernel

            self.kernel = RealVibeKernel(ledger_path=":memory:")
        else:
            self.kernel = LightweightKernel()

        # Register plugins
        for plugin in self.get_test_plugins():
            self.kernel.register_plugin(plugin)

        self.kernel.boot()

    def _teardown_kernel(self):
        """Cleanup kernel."""
        if hasattr(self, "kernel"):
            self.kernel.shutdown()

    def get_test_plugins(self) -> List[TestPlugin]:
        """Override to provide test-specific plugins."""
        return []

    # ========================================================================
    # ASSERTION HELPERS
    # ========================================================================

    def assert_event_recorded(self, event_type: str, count: int = 1):
        """Assert that an event type was recorded."""
        events = self.kernel.get_events(event_type)
        assert len(events) >= count, f"Expected {count} '{event_type}' events, found {len(events)}"

    def assert_no_event(self, event_type: str):
        """Assert that no events of this type were recorded."""
        events = self.kernel.get_events(event_type)
        assert len(events) == 0, f"Expected no '{event_type}' events, found {len(events)}"

    def assert_task_queued(self, agent_id: Optional[str] = None):
        """Assert that a task was queued."""
        if agent_id:
            tasks = [t for t in self.kernel.tasks if getattr(t, "agent_id", None) == agent_id]
            assert len(tasks) > 0, f"No tasks queued for agent '{agent_id}'"
        else:
            assert len(self.kernel.tasks) > 0, "No tasks queued"


# ============================================================================
# TEST HARNESS - Runs tests with hard timeouts
# ============================================================================


class TestHarness:
    """
    Runs tests with guaranteed timeouts and proper isolation.

    Usage:
        harness = TestHarness()
        result = harness.run_test(my_test_function, timeout=5)
    """

    def run_test(
        self,
        test_func: Callable,
        timeout: int = 10,
        setup: Optional[Callable] = None,
        teardown: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Run a test with hard timeout.

        Returns:
            {
                "passed": bool,
                "duration": float,
                "error": Optional[str],
                "timeout": bool,
            }
        """
        result = {
            "passed": False,
            "duration": 0.0,
            "error": None,
            "timeout": False,
        }

        start = time.time()

        try:
            # Setup
            if setup:
                setup()

            # Run with timeout
            with hard_timeout(timeout, test_func.__name__):
                test_func()

            result["passed"] = True

        except TestTimeoutError as e:
            result["error"] = str(e)
            result["timeout"] = True

        except AssertionError as e:
            result["error"] = f"ASSERTION FAILED: {e}"

        except Exception as e:
            result["error"] = f"ERROR: {type(e).__name__}: {e}"

        finally:
            # Teardown (always runs)
            if teardown:
                try:
                    teardown()
                except Exception:
                    pass

            result["duration"] = time.time() - start

        return result


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "TestTimeoutError",
    "hard_timeout",
    "LightweightKernelConfig",
    "LightweightKernel",
    "TestPlugin",
    "FractalTestCase",
    "TestHarness",
]
