import sys
from django.core.management.base import BaseCommand


from falkor.utilities import docker_cli, get_or_create_user_network
from falkor.models import Project
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Fix networks for proxy'

    def handle(self, *args, **options):
        cli = docker_cli()
        for user in User.objects.all():
            print user, '...',
            user_network = get_or_create_user_network(cli, user)
            for proxy in cli.containers(filters={'status':'running', 'label': ['com.docker.compose.service=proxy']}):
                if user_network['Name'] not in proxy["NetworkSettings"]["Networks"]:
                    cli.connect_container_to_network(proxy['Id'], user_network['Name'])
            print 'Done'