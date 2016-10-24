from django.contrib import admin

from .models import Project, Container
from django.contrib.auth.models import User

from guardian.admin import GuardedModelAdmin

from .utilities import docker_cli, get_or_create_user_network


class WorkspaceAdmin(GuardedModelAdmin):
    actions = ['delete_and_remove', 'fix_networks', 'claim_workspaces']
    
    def get_actions(self, request):
        actions = super(WorkspaceAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
        
    def delete_and_remove(self, request, queryset):
        cli = docker_cli()
        for workspace in queryset.all():
            try:
                cli.remove_container(workspace.container_id, force=True)
            except:
                pass
            workspace.delete()
            
    delete_and_remove.short_description = "Delete and remove containers"
    
    def fix_networks(self, request, queryset):
        cli = docker_cli()
        for workspace in queryset.all():
            user_network = get_or_create_user_network(cli, workspace.user)
            print user_network
            container = cli.inspect_container(workspace.container_id)
            for name, network in container["NetworkSettings"]["Networks"].items():
                if user_network['Name'] != name:
                    cli.disconnect_container_from_network(container['Id'], name)
            if user_network['Name'] not in container["NetworkSettings"]["Networks"]:
                cli.connect_container_to_network(container['Id'], user_network['Name'])
            for proxy in cli.containers(filters={'status':'running', 'label': ['com.docker.compose.service=proxy']}):
                if user_network['Name'] not in proxy["NetworkSettings"]["Networks"]:
                    cli.connect_container_to_network(proxy['Id'], user_network['Name'])
            workspace.save()
    
    def claim_workspaces(self, request, queryset):   
        cli = docker_cli()
        for container in cli.containers(filters={'ancestor': 'kdelfour/cloud9-docker'}):
            if container['Names'][0].startswith('/falkor__user_'):
                if Project.objects.filter(container_id=container['Id']).count() == 0:
                    workspace = Project()
                    workspace.user = User.objects.get(username='sueastside')
                    workspace.name = container['Names'][0].split('__workspace_', 1)[1]
                    while Project.objects.filter(name__iexact=workspace.name, user=workspace.user).count():
                        workspace.name = workspace.name + '_'
                    workspace.container_id = container['Id']
                    workspace.save()
    claim_workspaces.short_description = "Claim workspaces"        

admin.site.register(Project, WorkspaceAdmin)
admin.site.register(Container)