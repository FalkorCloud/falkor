from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json

from .models import Project


from utilities import docker_cli, get_or_create_user_network, get_workspaces_for_user


def login(request):
    return render(request, 'login.html')


@login_required(login_url='/login')
def home(request):
    cli = docker_cli()
    workspaces = get_workspaces_for_user(cli, request.user)            
    return render(request, 'home.html', context={'workspaces': workspaces})


def logout(request):
    auth_logout(request)
    return redirect('/login')
    
@login_required(login_url='/login')
def workspace(request, workspace_id):
    workspace = get_object_or_404(Project, pk=workspace_id, user=request.user)
    
    cli = docker_cli()
    container = cli.inspect_container(workspace.container_id)
    workspace.info = json.dumps(container, indent=2)
    
    workspace.endpoints = []
    command = cli.exec_create(workspace.container_id, 'netstat -tlnp')
    output = cli.exec_start(command['Id'])
    for line in output.split('\n')[2:-1]:
        s = line.split()
        ip = container['NetworkSettings']['Networks'].items()[0][1]['IPAddress'].replace('.', '_')
        name = s[0] +'-'+ ip + '-' +s[3].split(':')[1]
        workspace.endpoints.append({'program': s[6], 'protocol': s[0], 'port': s[3], 'name': name})
    
    if request.GET.get('_pjax', None):
        return render(request, 'fragments/workspace.html', context={'request': request, 'workspace': workspace})
    else:
        workspaces = get_workspaces_for_user(cli, request.user)            
        return render(request, 'home.html', context={'request': request, 'workspace': workspace, 'workspaces': workspaces})

from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control


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
    
    
@login_required(login_url='/login')
def workspaces_add(request):    
    workspace_name = request.POST.get('name', None)
    if workspace_name is None:
        return HttpResponse(status=304)
        
    workspace = Project()
    workspace.user = request.user
    workspace.name = workspace_name
    workspace.save()
    
    cli = docker_cli()
    
    network = get_or_create_user_network(cli, request.user)
    
    name = 'falkor__user_{0}__workspace_{1}'.format(request.user.pk, workspace.name)
    
    container = cli.create_container(image='kdelfour/cloud9-docker', detach=True, stdin_open=True, tty=True, name=name, host_config=cli.create_host_config(network_mode=network['Id']))
    for proxy in cli.containers(filters={'status':'running', 'label': 'com.docker.compose.service=proxy'}):
        if network['Name'] not in proxy["NetworkSettings"]["Networks"]:
            cli.connect_container_to_network(proxy['Id'], network['Name'])

    
    workspace.container_id = container['Id']
    workspace.save()
    
    cli.start(container=container.get('Id'))
    
    response_data = {'status': 'ok'}
    return HttpResponse(json.dumps(response_data, indent=2), content_type="application/json")
