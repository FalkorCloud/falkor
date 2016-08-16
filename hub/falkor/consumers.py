from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Project
import json

from django.core.serializers.json import DjangoJSONEncoder

from .utilities import get_workspaces_for_user, docker_cli, get_workspace_state, get_workspace_endpoints, get_or_create_user_network

def create_event(event_name, data):
    print 'CREATE',  event_name
    return {
        "text": json.dumps({
            "event": event_name,
            "data": data
        }, cls=DjangoJSONEncoder)
    }
    

def model_to_dict(instance):
    w = {field.name: field.value_from_object(instance) for field in instance._meta.fields}
    w.update({'state': getattr(instance, 'state', None)})
    w.update({'info': getattr(instance, 'info', None)})
    w.update({'endpoints': getattr(instance, 'endpoints', None)})
    w.update({'url': getattr(instance, 'url', lambda: None)()})
    return w

#--------------------------------------------------

def docker_events(message):
    workspace = get_object_or_404(Project, pk=message['workspace__pk'])
    cli = docker_cli()
    get_workspace_state(cli, workspace)
    Group("user-%s" % workspace.user.pk).send(create_event('workspaces.update', model_to_dict(workspace)))

        
@receiver(post_save, sender=Project)
def send_update(sender, instance, created, **kwargs):
    cli = docker_cli()
    get_workspace_state(cli, instance)
    Group("user-%s" % instance.user.pk).send(create_event('workspaces.created' if created else 'workspaces.update', model_to_dict(instance)))


@receiver(post_delete, sender=Project)
def send_delete(sender, instance, **kwargs):
    cli = docker_cli()
    Group("user-%s" % instance.user.pk).send(create_event('workspaces.deleted', model_to_dict(instance)))


@channel_session_user
def select_workspace(message):
    data = json.loads(message['data'])
    workspace = get_object_or_404(Project, pk=data['workspace_id'], user=message.user)
    
    if workspace.container_id:
        cli = docker_cli()
        container = cli.inspect_container(workspace.container_id)
        workspace.info = container
        get_workspace_endpoints(cli, workspace)
    
    Group("user-%s" % workspace.user.pk).send(create_event('workspaces.select', model_to_dict(workspace)))


@channel_session_user
def add_workspace(message):
    data = json.loads(message['data'])
    print data
    workspace_name = data.get('name', None)
    if workspace_name is None:
        return
        
    workspace = Project()
    workspace.user = message.user
    workspace.name = workspace_name
    workspace.save()
    
    cli = docker_cli()
    
    network = get_or_create_user_network(cli, message.user)
    
    name = 'falkor__user_{0}__workspace_{1}'.format(message.user.pk, slugify(workspace.name))
    
    container = cli.create_container(image='kdelfour/cloud9-docker', detach=True, stdin_open=True, tty=True, name=name, host_config=cli.create_host_config(network_mode=network['Id']))
    for proxy in cli.containers(filters={'status':'running', 'label': 'com.docker.compose.service=proxy'}):
        if network['Name'] not in proxy["NetworkSettings"]["Networks"]:
            cli.connect_container_to_network(proxy['Id'], network['Name'])

    
    workspace.container_id = container['Id']
    workspace.save()
    
    cli.start(container=container.get('Id'))
    
    
@channel_session_user_from_http
def ws_add(message):
    Group("user-%s" % message.user.pk).add(message.reply_channel)
    
    cli = docker_cli()
    workspaces = get_workspaces_for_user(cli, message.user)   
    
    Group("user-%s" % message.user.pk).send(create_event('workspaces', {"workspaces":  [model_to_dict(x) for x in workspaces],}))


@channel_session_user_from_http
def ws_keepalive(message):
    Group("user-%s" % message.user.pk).add(message.reply_channel)

    
@channel_session_user
def ws_message(message):
    text = json.loads(message['text'])
    Channel('websocket.events').send({
        'reply_channel': message.reply_channel.name,
        'event': text['event'],
        'data': json.dumps(text['data'])
        })


@channel_session_user
def ws_disconnect(message):
    Group("user-%s" % message.user.pk).discard(message.reply_channel)