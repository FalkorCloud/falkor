import re
from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http

WORKSPACE_PATH = re.compile(r'^/workspace/(?P<workspace_id>[0-9]+)/(?P<terminal_id>[0-9]+)/?')

def get_ids(message):
    match = WORKSPACE_PATH.match(message['path'])
    workspace_id = match.group('workspace_id')
    terminal_id = match.group('terminal_id')
    return workspace_id, terminal_id

@channel_session
@channel_session_user_from_http
def ws_add(message):
    print 'ws_add_terminal', message['path']
    workspace_id, terminal_id = get_ids(message)
    c = Channel('terminal.connect')
    c.send({
        'reply_channel': message.reply_channel.name,
        'user_id': message.user.id,
        'workspace_id': workspace_id,
        'terminal_id': terminal_id,
        })
    
@channel_session_user_from_http
def ws_keepalive(message):
    pass

@channel_session_user
def ws_disconnect(message):
    print 'disconnect'
    pass

@channel_session
@channel_session_user
def ws_message(message):
    print 'terminal_input', message
    workspace_id, terminal_id = get_ids(message)
    if message['text'].startswith('@@RESIZE@@'):
        data = message['text'].split('@@RESIZE@@')[1].split(':')
        c = Channel('terminal.resize')
        c.send({
            'reply_channel': message.reply_channel.name,
            'user_id': message.user.id,
            'workspace_id': workspace_id,
            'terminal_id': terminal_id,
            'width': data[0],
            'height': data[1]
            })
    else:
        c = Channel('terminal.input')
        c.send({
            'reply_channel': message.reply_channel.name,
            'user_id': message.user.id,
            'workspace_id': workspace_id,
            'terminal_id': terminal_id,
            'input': message['text']
            })