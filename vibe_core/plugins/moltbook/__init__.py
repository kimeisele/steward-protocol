"""
MOLTBOOK PLUGIN
===============

"yogasthah kuru karmani sangam tyaktva dhananjaya"
"Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment to success or failure."

This plugin integrates Moltbook into the Mahamantra ecosystem as a native
Command/Event membrane, passing data via MahaCells instead of direct HTTP calls.
"""

from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

__all__ = ["MoltbookPlugin"]
