import sys
from django.core.management.base import BaseCommand

from channels import Channel, channel_layers

from falkor.utilities import docker_cli
from falkor.models import Project
import json

class Command(BaseCommand):
    help = 'Listen for docker events and publish them to a channel'

    def handle(self, *args, **options):
        c = Channel('docker_events', channel_layer=channel_layers['default'])
        cli = docker_cli()
        for container in cli.containers():
            workspaces = list(Project.objects.filter(container_id=container["Id"]))
            if len(workspaces):
                workspace = workspaces[0]
                c.send({
                        "user__pk":  workspace.user.pk,
                        "status":  container['State'],
                        "workspace__pk":  workspace.pk,
                        })
            
        events = cli.events()
        for event in events:
            event = json.loads(event)
            skip = False
            for prefix in [u'exec_', u'kill', u'die']:
                if event.get('status', u'exec_default').startswith(prefix):
                    skip = True
                    break
            if not skip:
                workspaces = list(Project.objects.filter(container_id=event["id"]))
                if len(workspaces):
                    workspace = workspaces[0]
                    print event
                    c.send({
                            "user__pk":  workspace.user.pk,
                            "status":  event["status"],
                            "workspace__pk":  workspace.pk,
                            })
        events.close()