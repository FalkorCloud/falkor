from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.SlugField(max_length=200)
    user = models.ForeignKey(User, related_name='created_projects')
    container_id = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (("name", "user"),)
    
    def __unicode__(self):
        from utilities import docker_cli
        cli = docker_cli()
        try:
            container = cli.inspect_container(self.container_id)
            return 'Project {1}/{0}   [{2}] - {3}'.format(self.name, self.user, self.container_id, str(container['NetworkSettings']['Networks'].keys()))
        except:
            return 'Project {1}/{0}   [{2}] - {3}'.format(self.name, self.user, self.container_id, 'Missing')
        
    def url(self):
        return '{0}.workspaces'.format(self.name)
        
    
class Container(models.Model):
    project = models.ForeignKey(Project)
    name = models.SlugField(max_length=200)
    image = models.CharField(max_length=200)
    container_id = models.CharField(max_length=200, null=True, blank=True)
    settings = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (("project", "name"),)