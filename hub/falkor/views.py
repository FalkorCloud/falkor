from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

from django.http import HttpResponse
import json

from utilities import docker_cli, get_workspaces_for_user


def login(request):
    return render(request, 'login.html')


@login_required(login_url='/login')
def home(request):
    cli = docker_cli()
    workspaces = get_workspaces_for_user(cli, request.user)            
    return render(request, 'home.html', context={'request': request, 'workspaces': workspaces})


def logout(request):
    auth_logout(request)
    return redirect('/login')



@cache_page(1)
@cache_control(private=True)
@login_required(login_url='/login')
def workspaces(request):
    workspace_name = request.GET.get('workspace', None)

    if workspace_name:
        workspaces = request.user.created_projects.filter(name__iexact=workspace_name)
    else:
        workspaces = request.user.created_projects.all()
    
    cli = docker_cli()
    response_data = {}
    for project in workspaces:
        if project.container_id:
            container = cli.inspect_container(project.container_id)
            state = {'status': container['State']['Status'], 'IPAddress': container['NetworkSettings']['Networks'].items()[0][1]['IPAddress']}
            response_data[project.name.lower()] = state
        else:
            response_data[project.name.lower()] = None

    return HttpResponse(json.dumps(response_data, indent=2), content_type="application/json")
