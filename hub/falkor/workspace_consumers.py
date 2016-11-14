import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from guardian.shortcuts import assign_perm, remove_perm

from channels import Channel, Group
from channels.auth import channel_session_user

from .consumers import create_event, model_to_dict
from .models import Project
from .utilities import docker_cli, get_workspace_full

@channel_session_user
def shares_edit(message):
    data = json.loads(message['data'])
    workspace = get_object_or_404(Project, pk=data['workspace_id'])
    user = get_object_or_404(User, username=data['username'])
    perms = data.get('permissions', '').split(',')
    
    if not message.user.has_perm('falkor.can_edit_shares', workspace):
        return
    
    if user == workspace.user:
        Group("user-%s" % message.user.pk).send(create_event('notifications', {'level': 'info', 'message': 'you cannot change permissions of the owner'}))
        return
    
    permissions = ['can_open_ide']
    print 'ERR', user, perms
    for perm in permissions:
        if perm in perms:
            print 'Adding', perm, 'for', user
            assign_perm(perm, user, workspace)
        else:
            print 'Removing', perm, 'for', user
            remove_perm(perm, user, workspace)
    
    cli = docker_cli()
    get_workspace_full(cli, message.user, workspace)
    
    Group("user-%s" % message.user.pk).send(create_event('workspaces.select', model_to_dict(workspace)))