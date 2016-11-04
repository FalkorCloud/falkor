from channels.routing import route
from falkor.consumers import ws_add, ws_keepalive, ws_message, ws_disconnect, docker_events, select_workspace, control_workspace, add_workspace

from falkor import terminal_consumers

channel_routing = [
    
    route("websocket.connect", terminal_consumers.ws_add, path=r"^/workspace"),
    route("websocket.receive", terminal_consumers.ws_message, path=r"^/workspace"),
    route("websocket.keepalive", terminal_consumers.ws_keepalive, path=r"^/workspace"),
    route("websocket.disconnect", terminal_consumers.ws_disconnect, path=r"^/workspace"),
    
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
    route("websocket.connect", ws_add),
    route("websocket.keepalive", ws_keepalive),
    
    
    route("websocket.events", select_workspace, event=r'workspaces.select'),
    route("websocket.events", control_workspace, event=r'workspaces.control'),
    route("websocket.events", add_workspace, event=r'workspaces.add'),
    route('docker_events', docker_events),
]