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
    else:
        network = networks[0]
        
    return network
    
def get_workspaces_for_user(cli, user):
    workspaces = user.created_projects.all()
    for workspace in workspaces:
        if workspace.container_id:
            try:
                container = cli.inspect_container(workspace.container_id)
                workspace.state = {'status': container['State']['Status'], 'IPAddress': container['NetworkSettings']['Networks'].items()[0][1]['IPAddress']}
            except:
                 workspace.state = {'status': 'Missing', 'IPAddress': 'None'}
    return workspaces