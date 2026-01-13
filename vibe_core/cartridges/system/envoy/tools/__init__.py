"""
ENVOY TOOLS - Universal Operator Interface

Tools for controlling Agent City without shell access.
Perfect for shell-less environments (Web, Mobile, LLM Operators).

All tools now Tool Protocol compliant for kernel-managed execution.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xc5acafe2"  # GenesisByte: parampara % 37 == 0

from .city_control_tool import CityControlTool, create_city_controller
from .curator_tool import CuratorTool
from .diplomacy_tool import DiplomacyTool
from .gap_report_tool import GAPReportTool
from .hil_assistant_tool import HILAssistantTool
from .run_campaign_tool import RunCampaignTool

__all__ = [
    "CityControlTool",
    "create_city_controller",
    "CuratorTool",
    "DiplomacyTool",
    "GAPReportTool",
    "HILAssistantTool",
    "RunCampaignTool",
]
