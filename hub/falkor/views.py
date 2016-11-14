from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

from guardian.shortcuts import get_objects_for_user

from django.http import HttpResponse
import json

from falkor.models import EditorType, Project
from utilities import docker_cli, get_workspaces_for_user


def login(request):
    return render(request, 'login.html')


@login_required(login_url='/login')
def home(request):
    return render(request, 'home.html', context={'request': request, 'editorTypes': EditorType.objects.all()})


@login_required(login_url='/login')
def terminal(request, user, workspace):
    workspace = get_object_or_404(Project, user__username=user, slug=workspace)
    return render(request, 'xterm.html', context={'request': request, 'workspace': workspace})

def logout(request):
    auth_logout(request)
    return redirect('/login')

    
@cache_page(1)
@cache_control(private=True)
@login_required(login_url='/login')
def workspaces(request):
    workspace_name = request.GET.get('workspace', None)

    if workspace_name:
        workspaces = get_objects_for_user(request.user, 'can_open_ide', klass=Project).filter(slug__iexact=workspace_name)
        #TODO: update last used
    else:
        workspaces = get_objects_for_user(request.user, 'can_open_ide', klass=Project).all()
    
    cli = docker_cli()
    response_data = {}
    for project in workspaces:
        if project.container_id:
            container = cli.inspect_container(project.container_id)
            state = {
                'Id': container['Id'],
                'status': container['State']['Status'], 
                'IPAddress': container['NetworkSettings']['Networks'].items()[0][1]['IPAddress']}
            response_data[project.slug] = state
        else:
            response_data[project.slug] = None

    return HttpResponse(json.dumps(response_data, indent=2), content_type="application/json")
