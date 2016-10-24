import socket, struct
from docker import Client
from django.conf import settings

def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def docker_cli():
    return Client(version=settings.DOCKER_API, base_url='http://'+get_default_gateway_linux()+':2375')
    
    
def get_or_create_user_network(cli, user):
    network_name = 'falkor__user_{0}__'.format(user.pk)
    
    networks = cli.networks(names=[network_name])
    if len(networks) < 1:
        network = cli.create_network(network_name, 'bridge')
        network['Name'] = network_name
    else:
        network = networks[0]
        
    return network

def get_workspace_state(cli, workspace):
    workspace.state = {'status': 'Missing', 'IPAddress': 'None'}
    workspace.running = False
    if workspace.container_id:
        try:
            container = cli.inspect_container(workspace.container_id)
            workspace.state['status'] = container['State']['Status']
            workspace.running = container['State']['Status'] == 'running'
            workspace.state['IPAddress'] = container['NetworkSettings']['Networks'].items()[0][1]['IPAddress']
        except Exception as e:
            print e
            pass
    return workspace.state

def get_workspace_endpoints(cli, workspace):
    workspace.endpoints = []
    if workspace.container_id:
        container = cli.inspect_container(workspace.container_id)
        if container['State']['Status'] == 'running':
            command = cli.exec_create(workspace.container_id, 'netstat -tlnp')
            output = cli.exec_start(command['Id'])
            for line in output.split('\n')[2:-1]:
                s = line.split()
                if s[3].startswith('127.0.0.') and s[6] == '-':
                    continue
                if s[3].startswith('0.0.0.0:80') and s[6].endswith('/node'):
                    continue
                ip = container['NetworkSettings']['Networks'].items()[0][1]['IPAddress'].replace('.', '_')
                name = s[0] +'-'+ ip + '-' +s[3].split(':')[1]
                workspace.endpoints.append({'program': s[6], 'protocol': s[0], 'port': s[3], 'name': name})
    return workspace.endpoints

def get_workspace_files(cli, workspace):
    workspace.files = []
    if workspace.container_id:
        container = cli.inspect_container(workspace.container_id)
        if container['State']['Status'] == 'running':
            filter = '-maxdepth 1 -mindepth 1  ! -wholename "*.c9*" ! -wholename "*.git*"'
            command = cli.exec_create(workspace.container_id, "/bin/sh -c 'find /workspace "+filter+" -type d -printf \"%y;%p;%k KB\n\"; find /workspace "+filter+" ! -type d -printf \"%y;%p;%k KB\n\"'")
            output = cli.exec_start(command['Id']).strip()
            for line in output.split('\n'):
                file = line.strip().split(';')
                if len(file) == 3:
                    workspace.files.append({'is_file': file[0]=='f', 'name': file[1], 'size': file[2],})
    return workspace.files
    
def get_workspaces_for_user(cli, user):
    workspaces = user.created_projects.all().order_by('-created_at')
    for workspace in workspaces:
        get_workspace_state(cli, workspace)
    return workspaces