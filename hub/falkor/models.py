from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User

class EditorType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(populate_from='name')
    image = models.CharField(max_length=200)
    urlPrefix = models.CharField(max_length=200, blank=True)
    urlSuffix = models.CharField(max_length=200, blank=True)
    settings = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        from utilities import docker_cli
        cli = docker_cli()
        try:
            img = cli.inspect_image(self.image)
            image = img['Id'] + ' ' + str(img['RepoTags'])
        except Exception as e:
            print e
            image = 'Missing'
        return '{} [image: {}]'.format(self.name, image)

class Project(models.Model):
    editor_type = models.ForeignKey(EditorType)
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from=lambda x: x.user.username+'-'+x.name, null=True, blank=True, always_update=True, editable=True)
    user = models.ForeignKey(User, related_name='created_projects')
    container_id = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (("name", "user"),)
        permissions = (
            ("can_open_ide", "Can open IDE"),
            ("can_start_stop", "Can control the container"),
            ("can_edit_shares", "Can edit shares"),
        )
    
    def __unicode__(self):
        from utilities import docker_cli
        cli = docker_cli()
        try:
            container = cli.inspect_container(self.container_id)
            return u'Project {1}/{0}   [{2}] - {3}'.format(self.name, self.user, self.slug, str(container['NetworkSettings']['Networks'].keys()))
        except:
            return u'Project {1}/{0}   [{2}] - {3}'.format(self.name, self.user, self.slug, 'Missing')
     
    @property   
    def urlPrefix(self):
        return self.editor_type.urlPrefix.format(**vars(self))
    
    @property
    def urlSuffix(self):
        return self.editor_type.urlSuffix.format(**vars(self))
        
    
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