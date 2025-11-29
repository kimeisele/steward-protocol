#!/usr/bin/env python3
"""
CANTO 10: LIVE DARSHAN (The Live Vision)

Terminal-based dashboard that visualizes the Dance of the Agents in real-time.
Connects to ws://localhost:8000/v1/pulse and displays:

1. The Bhu-mandala (concentric circles with agent positions)
2. Real-time event stream with color-coded events
3. System heartbeat indicator
4. Agent activity ticker tape
5. System state indicator (HEALTHY/DEGRADED/EMERGENCY)

Usage:
    python scripts/live_darshan.py [--url ws://localhost:8000/v1/pulse]
"""

import argparse
import asyncio
import json
import logging
import signal
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    print("❌ websockets library required: pip install websockets")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DARSHAN")


# ANSI Color codes
class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"

    # Special
    CLEAR_SCREEN = "\033[2J\033[H"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"


@dataclass
class PulseData:
    """Current heartbeat state"""

    cycle_id: int = 0
    system_state: str = "HEALTHY"
    active_agents: List[str] = None
    queue_depth: int = 0
    frequency: float = 1.0
    timestamp: str = ""

    def __post_init__(self):
        if self.active_agents is None:
            self.active_agents = []


class BhuMandala:
    """
    Renders the Sacred Geometry of Agent Positions

    Based on Srimad Bhagavata Purana topology with 5 concentric circles.
    Each agent flashes when emitting events.
    """

    AGENT_POSITIONS = {
        # Ring 1 (Center)
        "civic": (0, 0, "N"),
        # Ring 2
        "herald": (2, 0, "E"),
        "temple": (0, 2, "N"),
        # Ring 3
        "artisan": (3, 1, "SE"),
        "engineer": (1, 3, "SW"),
        # Ring 4
        "science": (4, 0, "S"),
        "lens": (0, 4, "W"),
        # Ring 5
        "forum": (3, 3, "SW"),
        "pulse": (3, -3, "NW"),
        # Boundary
        "watchman": (5, 0, "E"),
        "auditor": (4, 2, "SE"),
        "archivist": (2, 4, "SW"),
    }

    def __init__(self):
        self.flashing_agents: Dict[str, int] = {}  # agent -> flash_count
        self.event_colors: Dict[str, str] = {}

    def update_flash(self, agent_id: str, color: str):
        """Flash an agent when it emits an event"""
        if agent_id:
            self.flashing_agents[agent_id] = 3  # Flash 3 cycles
            self.event_colors[agent_id] = color

    def render(self, width: int = 40) -> str:
        """Render ASCII Bhu-mandala"""
        lines = []
        lines.append(ANSI.BOLD + "🕉️  BHU-MANDALA (Agent Topology)" + ANSI.RESET)
        lines.append("")

        # Create canvas
        canvas = [[" " for _ in range(width)] for _ in range(width)]
        center = width // 2

        # Draw concentric circles and agents
        for radius in [1, 3, 5, 7, 9]:
            for i in range(width):
                for j in range(width):
                    dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
                    if abs(dist - radius) < 0.5:
                        if canvas[j][i] == " ":
                            canvas[j][i] = "·"

        # Place agents
        for agent_name, (x, y, direction) in self.AGENT_POSITIONS.items():
            px = center + x
            py = center + y

            if 0 <= px < width and 0 <= py < width:
                # Determine symbol based on flashing
                is_flashing = agent_name in self.flashing_agents and self.flashing_agents[agent_name] > 0
                symbol = "◉" if is_flashing else "●"

                # Get color
                color = self.event_colors.get(agent_name, ANSI.WHITE)

                # Render
                if is_flashing:
                    canvas[py][px] = f"{ANSI.BG_RED}{ANSI.BOLD}{symbol}{ANSI.RESET}"
                else:
                    canvas[py][px] = f"{color}{symbol}{ANSI.RESET}"

        # Render canvas
        for row in canvas:
            lines.append("  " + "".join(row))

        # Decrease flash counters
        for agent in list(self.flashing_agents.keys()):
            self.flashing_agents[agent] -= 1
            if self.flashing_agents[agent] <= 0:
                del self.flashing_agents[agent]

        return "\n".join(lines)


class LiveDarshan:
    """Main terminal dashboard"""

    def __init__(self, ws_url: str = "ws://localhost:8000/v1/pulse"):
        self.ws_url = ws_url
        self.ws: Optional[WebSocketClientProtocol] = None
        self.running = True
        self.pulse = PulseData()
        self.mandala = BhuMandala()
        self.event_history: List[Dict] = []
        self.max_events = 10

        # Color mapping for events
        self.event_colors = {
            "31": "🔴 ERROR",
            "32": "🟢 ACTION",
            "33": "🟡 MERCY",
            "34": "🔵 THOUGHT",
            "35": "🟣 VIOLATION",
            "36": "🔷 PRAYER_RECEIVED",
            "37": "⚪ COMPLETED",
        }

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            logger.info(f"🔌 Connecting to {self.ws_url}...")
            self.ws = await websockets.connect(self.ws_url)
            logger.info("✅ Connected!")
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect gracefully"""
        self.running = False
        if self.ws:
            await self.ws.close()

    async def receive_messages(self):
        """Listen for messages from WebSocket"""
        try:
            while self.running and self.ws:
                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
                    await self.process_message(message)
                except asyncio.TimeoutError:
                    # Send keep-alive
                    try:
                        await self.ws.send("ping")
                    except:
                        pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Receive error: {e}")

    async def process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "pulse":
                self.process_pulse(data.get("data", {}))
            elif msg_type == "event":
                self.process_event(data.get("data", {}))
            elif msg_type == "system":
                logger.info(f"📡 {data.get('message')}")
        except json.JSONDecodeError:
            logger.warning(f"⚠️  Invalid JSON: {message[:50]}")
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")

    def process_pulse(self, data: Dict):
        """Process pulse packet"""
        self.pulse = PulseData(
            cycle_id=data.get("cycle_id", 0),
            system_state=data.get("system_state", "HEALTHY"),
            active_agents=data.get("active_agents", []),
            queue_depth=data.get("queue_depth", 0),
            frequency=data.get("frequency", 1.0),
            timestamp=data.get("timestamp", ""),
        )

    def process_event(self, data: Dict):
        """Process agent event"""
        color = data.get("color", "37")
        event_type = data.get("event_type", "UNKNOWN")
        agent_id = data.get("agent_id", "?")
        message = data.get("message", "")

        # Flash agent in mandala
        self.mandala.update_flash(agent_id, color)

        # Add to history
        self.event_history.append(
            {
                "timestamp": data.get("timestamp", ""),
                "agent": agent_id,
                "type": event_type,
                "message": message,
                "color": color,
            }
        )

        # Keep history size limited
        if len(self.event_history) > self.max_events:
            self.event_history.pop(0)

    def render_ui(self):
        """Render the complete dashboard"""
        lines = []

        # Header
        lines.append(ANSI.BOLD + "=" * 80 + ANSI.RESET)
        lines.append(ANSI.BOLD + ANSI.CYAN + "✨ LIVE DARSHAN - VibeOS Real-Time Dashboard ✨" + ANSI.RESET)
        lines.append(ANSI.BOLD + "=" * 80 + ANSI.RESET)
        lines.append("")

        # Bhu-mandala
        lines.append(self.mandala.render())
        lines.append("")

        # System Status
        state_color = {
            "HEALTHY": ANSI.GREEN,
            "DEGRADED": ANSI.YELLOW,
            "EMERGENCY": ANSI.RED,
        }.get(self.pulse.system_state, ANSI.WHITE)

        lines.append(ANSI.BOLD + "📊 System Status" + ANSI.RESET)
        lines.append(f"  State: {state_color}{self.pulse.system_state}{ANSI.RESET}")
        lines.append(f"  Heartbeat: {self.pulse.frequency}Hz (Cycle #{self.pulse.cycle_id})")
        lines.append(f"  Active Agents: {len(self.pulse.active_agents)}")
        lines.append(f"  Queue Depth: {self.pulse.queue_depth}")
        lines.append("")

        # Event Ticker
        lines.append(ANSI.BOLD + "📡 Event Stream (Recent 10)" + ANSI.RESET)
        if not self.event_history:
            lines.append("  (waiting for events...)")
        else:
            for event in self.event_history[-10:]:
                color_code = event.get("color", "37")
                agent = event.get("agent", "?")
                event_type = event.get("type", "?")
                message = event.get("message", "")

                # Format: [HH:MM:SS] AGENT_ID EVENT_TYPE: message
                timestamp = event.get("timestamp", "").split("T")[1][:8] if event.get("timestamp") else "??:??:??"

                color_str = f"\033[{color_code}m"
                lines.append(
                    f"  {timestamp} {ANSI.BOLD}{agent}{ANSI.RESET} {color_str}{event_type}{ANSI.RESET}: {message}"
                )

        lines.append("")
        lines.append(ANSI.DIM + "Press Ctrl+C to exit" + ANSI.RESET)

        return "\n".join(lines)

    async def render_loop(self):
        """Render UI periodically"""
        try:
            while self.running:
                print(ANSI.CLEAR_SCREEN)
                print(self.render_ui())
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Render error: {e}")

    async def run(self):
        """Main event loop"""
        await self.connect()

        # Create tasks
        receive_task = asyncio.create_task(self.receive_messages())
        render_task = asyncio.create_task(self.render_loop())

        try:
            await asyncio.gather(receive_task, render_task)
        except KeyboardInterrupt:
            logger.info("⏹️  Shutting down...")
            await self.disconnect()
        finally:
            print(ANSI.SHOW_CURSOR)


async def main():
    parser = argparse.ArgumentParser(description="Live Darshan - VibeOS Real-Time Dashboard")
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/v1/pulse",
        help="WebSocket URL (default: ws://localhost:8000/v1/pulse)",
    )
    args = parser.parse_args()

    print(ANSI.HIDE_CURSOR)

    try:
        darshan = LiveDarshan(ws_url=args.url)
        await darshan.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        print(ANSI.SHOW_CURSOR)


if __name__ == "__main__":
    asyncio.run(main())
