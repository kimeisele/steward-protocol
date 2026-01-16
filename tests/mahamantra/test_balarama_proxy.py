"""
TEST BALARAMA PROXY
===================

Verifies proxy.py Balarama Proxy pattern:
- Services wrapped without code changes
- Mahamantra context injected
- Path operations routed through bridge
- WATERTIGHT (no hardcoded shit)
"""

import sys
import tempfile
import types
from pathlib import Path

import pytest

from vibe_core.mahamantra.substrate.proxy import (
    BalaramaProxy,
    wrap_service,
)


class TestBalaramaProxyBasics:
    """Test basic proxy functionality."""

    def setup_method(self):
        """Create a test service module."""
        # Create test module code
        test_code = """
from pathlib import Path

def get_path_class():
    return Path

def write_file(path_str, content):
    path = Path(path_str)
    path.write_text(content)
    return True
"""
        # Create module
        self.test_mod = types.ModuleType("test_service_basic")
        exec(test_code, self.test_mod.__dict__)
        sys.modules["test_service_basic"] = self.test_mod

    def teardown_method(self):
        """Clean up test module."""
        if "test_service_basic" in sys.modules:
            del sys.modules["test_service_basic"]

    def test_proxy_creation(self):
        """Proxy can wrap a module."""
        proxy = BalaramaProxy("test_service_basic")

        assert proxy is not None
        assert proxy.module_name == "test_service_basic"
        assert proxy.is_wrapped is True

    def test_mahamantra_injected(self):
        """Mahamantra is injected into service namespace."""
        proxy = BalaramaProxy("test_service_basic")

        # Check mahamantra in module dict
        assert "mahamantra" in proxy.module.__dict__

        # Verify it's the real mahamantra (SANKIRTAN PATTERN)
        mahamantra = proxy.module.__dict__["mahamantra"]
        assert hasattr(mahamantra, "shadow")  # ShadowReactorFactory
        assert hasattr(mahamantra, "execute")  # Execute command
        assert hasattr(mahamantra, "resonate")  # Resonance routing

    def test_path_replaced(self):
        """pathlib.Path replaced with _GovernedPath."""
        proxy = BalaramaProxy("test_service_basic")

        # Check Path class
        path_class = proxy.module.__dict__.get("Path")
        assert path_class is not None
        assert path_class.__name__ == "_GovernedPath"

    def test_transparent_access(self):
        """Proxy provides transparent access to module attributes."""
        proxy = BalaramaProxy("test_service_basic")

        # Access module function through proxy
        assert hasattr(proxy, "get_path_class")
        path_cls = proxy.get_path_class()
        assert path_cls.__name__ == "_GovernedPath"


class TestGovernedPathWrites:
    """Test _GovernedPath routing through bridge."""

    def setup_method(self):
        """Create test module with write operations."""
        test_code = '''
from pathlib import Path

def write_text_file(path_str, content):
    """Write text file using Path."""
    path = Path(path_str)
    return path.write_text(content)

def write_bytes_file(path_str, content_bytes):
    """Write bytes file using Path."""
    path = Path(path_str)
    return path.write_bytes(content_bytes)
'''
        self.test_mod = types.ModuleType("test_service_writes")
        exec(test_code, self.test_mod.__dict__)
        sys.modules["test_service_writes"] = self.test_mod

    def teardown_method(self):
        """Clean up."""
        if "test_service_writes" in sys.modules:
            del sys.modules["test_service_writes"]

    def test_write_text_routes_through_bridge(self):
        """write_text() routes through bridge.offer()."""
        proxy = BalaramaProxy("test_service_writes")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            # This should route through bridge
            result = proxy.write_text_file(temp_path, "test content")

            # Write should succeed (bridge approves file_flush)
            assert result > 0

            # Verify file written
            assert Path(temp_path).exists()
            assert Path(temp_path).read_text() == "test content"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_write_bytes_routes_through_bridge(self):
        """write_bytes() routes through bridge.offer()."""
        proxy = BalaramaProxy("test_service_writes")

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
            temp_path = f.name

        try:
            # This should route through bridge
            result = proxy.write_bytes_file(temp_path, b"binary content")

            # Write should succeed
            assert result > 0

            # Verify file written
            assert Path(temp_path).exists()
            assert Path(temp_path).read_bytes() == b"binary content"
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestWrapServiceFunction:
    """Test wrap_service() convenience function."""

    def setup_method(self):
        """Create test module."""
        test_code = """
def hello():
    return "world"
"""
        self.test_mod = types.ModuleType("test_service_wrap")
        exec(test_code, self.test_mod.__dict__)
        sys.modules["test_service_wrap"] = self.test_mod

    def teardown_method(self):
        """Clean up."""
        if "test_service_wrap" in sys.modules:
            del sys.modules["test_service_wrap"]

    def test_wrap_service_convenience(self):
        """wrap_service() creates BalaramaProxy."""
        service = wrap_service("test_service_wrap")

        assert isinstance(service, BalaramaProxy)
        assert service.is_wrapped is True
        assert service.hello() == "world"


class TestProxyErrorHandling:
    """Test proxy error handling."""

    def test_invalid_module_raises_import_error(self):
        """Wrapping non-existent module raises ImportError."""
        with pytest.raises(ImportError):
            BalaramaProxy("nonexistent.module.name")

    def test_module_without_path_import(self):
        """Module without Path import doesn't break."""
        test_code = """
def foo():
    return 42
"""
        test_mod = types.ModuleType("test_no_path")
        exec(test_code, test_mod.__dict__)
        sys.modules["test_no_path"] = test_mod

        try:
            # Should not crash
            proxy = BalaramaProxy("test_no_path")
            assert proxy.is_wrapped is True
            assert proxy.foo() == 42
        finally:
            del sys.modules["test_no_path"]


class TestContextInjection:
    """Test mahamantra context injection patterns."""

    def setup_method(self):
        """Create service that uses mahamantra (SANKIRTAN PATTERN)."""
        test_code = '''
def use_mahamantra_shadow():
    """Use mahamantra shadow reactor if available."""
    if 'mahamantra' in globals():
        reactor = mahamantra.shadow.spawn()
        return {"reactor_id": reactor.reactor_id, "position": reactor.position}
    return None

def use_mahamantra_execute():
    """Use mahamantra execute."""
    if 'mahamantra' in globals():
        result = mahamantra.execute("test")
        return result.output if hasattr(result, 'output') else str(result)
    return None
'''
        self.test_mod = types.ModuleType("test_service_context")
        exec(test_code, self.test_mod.__dict__)
        sys.modules["test_service_context"] = self.test_mod

    def teardown_method(self):
        """Clean up."""
        if "test_service_context" in sys.modules:
            del sys.modules["test_service_context"]

    def test_service_can_use_mahamantra(self):
        """Service can use injected mahamantra (SANKIRTAN PATTERN)."""
        proxy = BalaramaProxy("test_service_context")

        # Service can now use shadow reactor
        shadow_result = proxy.use_mahamantra_shadow()
        assert shadow_result is not None
        assert "reactor_id" in shadow_result

        # Service can use execute
        execute_result = proxy.use_mahamantra_execute()
        assert execute_result is not None


class TestProxyTransparency:
    """Test that proxy is transparent (service acts normal)."""

    def setup_method(self):
        """Create service with various attributes."""
        test_code = """
CONSTANT = 42

class ServiceClass:
    def method(self):
        return "method_result"

def function():
    return "function_result"

value = "value_result"
"""
        self.test_mod = types.ModuleType("test_service_transparent")
        exec(test_code, self.test_mod.__dict__)
        sys.modules["test_service_transparent"] = self.test_mod

    def teardown_method(self):
        """Clean up."""
        if "test_service_transparent" in sys.modules:
            del sys.modules["test_service_transparent"]

    def test_proxy_exposes_constants(self):
        """Proxy exposes module constants."""
        proxy = BalaramaProxy("test_service_transparent")
        assert proxy.CONSTANT == 42

    def test_proxy_exposes_classes(self):
        """Proxy exposes module classes."""
        proxy = BalaramaProxy("test_service_transparent")
        instance = proxy.ServiceClass()
        assert instance.method() == "method_result"

    def test_proxy_exposes_functions(self):
        """Proxy exposes module functions."""
        proxy = BalaramaProxy("test_service_transparent")
        assert proxy.function() == "function_result"

    def test_proxy_exposes_variables(self):
        """Proxy exposes module variables."""
        proxy = BalaramaProxy("test_service_transparent")
        assert proxy.value == "value_result"
