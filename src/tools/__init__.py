# MCP tools for home-display-agent
from src.tools.audio_id import register_audio_id_tools
from src.tools.image_opt import register_image_opt_tools
from src.tools.overlay import register_overlay_tools
from src.tools.dispatcher import register_dispatcher_tools
from src.tools.monitor import register_monitor_tools

__all__ = [
    "register_audio_id_tools",
    "register_image_opt_tools",
    "register_overlay_tools",
    "register_dispatcher_tools",
    "register_monitor_tools",
]
