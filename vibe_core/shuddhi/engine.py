"""
SHUDDHI ENGINE - Re-export from Canonical Location
===================================================

The REAL ShuddhiEngine lives in Mahamantra (dharma/kumaras/engine.py).
This file exists for backwards compatibility with legacy imports.

CANONICAL: vibe_core.mahamantra.dharma.kumaras.engine.ShuddhiEngine
LEGACY:    vibe_core.shuddhi.engine.ShuddhiEngine (this file)

Protocol Liberation: All roads lead to Mahamantra.
"""

# Re-export from canonical location (Protocol-First)
from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine

__all__ = ["ShuddhiEngine"]
