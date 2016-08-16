from channels.routing import route
from falkor.consumers import ws_add, ws_keepalive, ws_message, ws_disconnect, docker_events, select_workspace, add_workspace

channel_routing = [
    route("websocket.connect", ws_add),
    route("websocket.keepalive", ws_keepalive),
    route("websocket.events", select_workspace, event=r'workspaces.select'),
    route("websocket.events", add_workspace, event=r'workspaces.add'),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
    route('docker_events', docker_events),
]