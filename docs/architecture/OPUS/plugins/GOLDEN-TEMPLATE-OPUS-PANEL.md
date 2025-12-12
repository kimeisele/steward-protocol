# Golden Template: OPUS Panel Plugin

> **Status**: DRAFT
> **Purpose**: Reference template for creating new OPUS panels
> **Example**: `prakriti_state.py` (17 tests, working)

---

## 1. File Structure

```
vibe_core/plugins/interface/renderers/opus/panels/
├── __init__.py           # BasePanel class + discovery
├── your_panel.py         # Your panel implementation
└── ...

tests/unit/
└── test_your_panel.py    # Unit tests (REQUIRED)
```

## 2. Panel Implementation

```python
"""
Your Panel - Brief description

What it displays:
- Item 1
- Item 2
"""

from typing import TYPE_CHECKING, Any, Dict, Optional
from . import BasePanel

if TYPE_CHECKING:
    pass


class YourPanel(BasePanel):
    """One-line description."""

    @property
    def panel_id(self) -> str:
        return "your_panel"  # Used in <!-- @LIVE:your_panel -->

    @property
    def title(self) -> str:
        return "Your Panel Title"

    @property
    def priority(self) -> int:
        return 50  # Lower = shown first (0-100)

    def render(self) -> str:
        """Render panel content as markdown."""
        lines = [f"## {self.title}", ""]

        # Your logic here
        data = self._get_data()

        if not data:
            lines.append("_No data available_")
            return "\n".join(lines)

        # Render as table
        lines.append("| Key | Value |")
        lines.append("| --- | --- |")
        for k, v in data.items():
            lines.append(f"| {k} | {v} |")

        return "\n".join(lines)

    def _get_data(self) -> Optional[Dict[str, Any]]:
        """Get data with error handling."""
        try:
            # Access kernel, prakriti, or other sources
            return {"example": "value"}
        except Exception:
            return None
```

## 3. Test Structure (REQUIRED)

```python
"""Tests for YourPanel."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


class TestYourPanel:
    """Test suite for YourPanel."""

    @pytest.fixture
    def mock_kernel(self):
        """Create mock kernel."""
        kernel = MagicMock()
        # Setup kernel mocks
        return kernel

    @pytest.fixture
    def panel(self, mock_kernel):
        """Create panel instance."""
        from vibe_core.plugins.interface.renderers.opus.panels.your_panel import YourPanel
        panel = YourPanel(mock_kernel)
        panel._root = Path(".")
        return panel

    def test_panel_id(self, panel):
        assert panel.panel_id == "your_panel"

    def test_panel_title(self, panel):
        assert "Your Panel" in panel.title

    def test_render_with_data(self, panel):
        """Panel should render data correctly."""
        with patch.object(panel, "_get_data", return_value={"key": "value"}):
            content = panel.render()
        assert "key" in content
        assert "value" in content

    def test_render_without_data(self, panel):
        """Panel should handle missing data gracefully."""
        with patch.object(panel, "_get_data", return_value=None):
            content = panel.render()
        assert "No data" in content or "not available" in content.lower()

    def test_error_handling(self, panel):
        """Panel should not crash on errors."""
        with patch.object(panel, "_get_data", side_effect=Exception("Test error")):
            # Should not raise
            content = panel.render()
        assert content  # Should return something
```

## 4. Container Compatibility (OPUS-015)

Panels are auto-discovered by `PanelLoader`. For container compatibility:

1. **No hardcoded paths** - Use `self._root` from BasePanel
2. **Lazy imports** - Import heavy deps inside methods
3. **Graceful degradation** - Return placeholder if deps missing

```python
def _get_external_data(self):
    """Example of container-safe external access."""
    try:
        # Lazy import
        from some_heavy_module import HeavyClass
        return HeavyClass().get_data()
    except ImportError:
        # Graceful degradation in container
        return {"status": "module_unavailable"}
```

## 5. Checklist

Before merging a new panel:

- [ ] `panel_id` is unique
- [ ] `priority` is reasonable (0-100)
- [ ] `render()` returns valid markdown
- [ ] Error handling in all data methods
- [ ] Unit tests exist (`tests/unit/test_*.py`)
- [ ] Tests pass: `pytest tests/unit/test_your_panel.py -v`
- [ ] No hardcoded paths
- [ ] Works without kernel running (graceful degradation)

## 6. Reference Implementation

See `prakriti_state.py`:
- **17 tests** covering all states
- **Error handling** in each layer method
- **Graceful degradation** without Prakriti
- **Clean markdown output**

---

*Golden Template v1.0 - 2025-12-12*
