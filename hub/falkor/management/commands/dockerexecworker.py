import sys
import time
from django.core.management.base import BaseCommand

from channels import Channel, channel_layers

import docker
from falkor.utilities import docker_cli
from falkor.models import Project
from falkor_project.asgi import channel_layer

import select
import json
from socket import error as socket_error
from socket import SHUT_RDWR

from django.utils import autoreload


import weakref

sockets = {}
reply_channels = {}
buffers = {}
exec_ids = {}
timeouts = {}

def remove_socket(socket_object):
    global sockets
    sockets = {k: v for k, v in sockets.items() if v != socket_object}
    reply_channels.pop(socket_object)
    buffers.pop(socket_object)
    exec_id = exec_ids.pop(socket_object)
    timeouts.pop(socket_object)
    try:
        socket_object.shutdown(SHUT_RDWR)
        socket_object.close()
        print cli.exec_inspect(exec_id)['State']['Pid']
        print 'REF',  sys.getrefcount(socket_object), hash(socket_object)
        print sockets, timeouts
    except Exception as e:
        print 'Remove socket', e
        pass



cli = docker_cli()


def handle_connect(message):
    user_id, workspace_id, terminal_id = message["user_id"], message["workspace_id"], message["terminal_id"]
    terminal_ref = str(user_id)+str(workspace_id)+str(terminal_id)
    if terminal_ref not in sockets:
        workspaces = list(Project.objects.filter(id=workspace_id, user__id=user_id))
        if len(workspaces):
            workspace = workspaces[0]
            try:
                exec_id = cli.exec_create(workspace.container_id, '/bin/bash', stdin=True, tty=True)
                socket_object = cli.exec_start(exec_id, tty=True, socket=True)
                print 'REF',  sys.getrefcount(socket_object)
                print 'creating', socket_object, terminal_ref
                sockets[terminal_ref] = socket_object
                reply_channels[socket_object] = message["reply_channel"]
                buffers[socket_object] = b''
                exec_ids[socket_object] = exec_id
                timeouts[socket_object] = time.time()
                print 'REF',  sys.getrefcount(socket_object), hash(socket_object)
            except docker.errors.APIError:
                Channel(message["reply_channel"]).send({'bytes': 'Workspace not running!'})
        else:
            Channel(message["reply_channel"]).send({'close': True, 'bytes': b'No Such workspace!'})
    else:
        reply_channels[sockets[terminal_ref]] = message["reply_channel"]
        Channel(message["reply_channel"]).send({'bytes': buffers[sockets[terminal_ref]]})

def handle_resize(message):
    user_id, workspace_id, terminal_id = message["user_id"], message["workspace_id"], message["terminal_id"]
    terminal_ref = str(user_id)+str(workspace_id)+str(terminal_id)
    if terminal_ref not in sockets:
        print 'WARN', 'trying to sent resize to not existing socket'
    else:
        exec_id = exec_ids[sockets[terminal_ref]]
        height = int(message["height"])
        width = int(message["width"])
        print 'RESIZE', width, height
        cli.exec_resize(exec_id, height=height, width=width)

def handle_input(message):
    user_id, workspace_id, terminal_id = message["user_id"], message["workspace_id"], message["terminal_id"]
    terminal_ref = str(user_id)+str(workspace_id)+str(terminal_id)
    if terminal_ref not in sockets:
        print 'WARN', 'trying to sent to not existing socket'
        #Channel(message["reply_channel"]).send({'close': True, 'bytes': b'Connection Lost.'})
    else:
        if message.get('input', None):
            try:
                socket_object = sockets[terminal_ref]
                socket_object.send(message.get('input'))
                timeouts[socket_object] = time.time()
            except socket_error as e:
                print 'WARN socket_error', e
                remove_socket(sockets[terminal_ref])

                            
def do_something(*args, **kwargs):
    while True:
        channel, message = channel_layer.receive_many([u'terminal.input', u'terminal.connect', u'terminal.resize'], block=False)
        if message:
            if channel == u'terminal.connect':
                handle_connect(message)
            elif channel == u'terminal.resize':
                 handle_resize(message)
            elif channel == u'terminal.input':
                handle_input(message)
            
        
        inputready,outputready,exceptready = select.select(sockets.values(), [], sockets.values(), 0)
        for s in inputready:
            data = s.recv(1024)
            #print 'OUT', data
            buffers[s] += data
            buffers[s] = buffers[s][-80*1024:]
            try:
                Channel(reply_channels[s]).send({'bytes': data})
            except channel_layer.ChannelFull as e:
                print 'WARN ChannelFull', e
                remove_socket(s)
        
        for e in exceptready:
            print 'GAAR', e
            
        now = time.time() - 5
        for socket_object, timeout in timeouts.items():
            if timeout < now:
                break
                print 'timeout', socket_object
                Channel(reply_channels[socket_object]).send({'close': True, 'bytes': b'Connection Lost.'})
                remove_socket(socket_object)

class Command(BaseCommand):
    help = 'Listen for docker events and publish them to a channel'

    def handle(self, *args, **options):
        print('This command auto reloads. No need to restart...')
        autoreload.main(do_something, args=None, kwargs=None)
                
                