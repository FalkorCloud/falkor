from django.conf.urls import include, url
from django.contrib import admin

from falkor import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^login$', views.login),
    url(r'^$', views.home),
    url(r'^(?P<user>[-\w]+)/(?P<workspace>[-\w]+)/terminal/$', views.terminal),
    url(r'^logout/$', views.logout),
    
    url(r'^workspaces/$', views.workspaces),
]
