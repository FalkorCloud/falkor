from django.core.management.base import BaseCommand

from channels import Channel, channel_layers

from falkor.utilities import docker_cli
from falkor.models import Project
import json

class Command(BaseCommand):
    help = 'Listen for docker events and publish them to a channel'

    def handle(self, *args, **options):
        '''
        import time
        toggle = True
        while True:
            toggle = not toggle
            c = Channel('docker_events', channel_layer=channel_layers['default'])
            c.send({"user__pk": 1, "status": "unpause" if toggle else "pause", "workspace__pk": 4})
            time.sleep(1)
        #------------------
        '''
        c = Channel('docker_events', channel_layer=channel_layers['default'])
        cli = docker_cli()
        events = cli.events()
        for event in events:
            print json.dumps(event, indent=2)
            event = json.loads(event)
            skip = False
            for prefix in [u'exec_', u'kill', u'die']:
                if event.get('status', u'exec_default').startswith(prefix):
                    skip = True
                    break
            if not skip:
                print 'SKIP', json.dumps(event, indent=2)
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