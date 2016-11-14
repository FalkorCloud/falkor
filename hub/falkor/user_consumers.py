import json

from django.contrib.auth.models import User

from channels import Channel, Group
from channels.auth import channel_session_user

from .consumers import create_event


@channel_session_user
def autocomplete(message):
    data = json.loads(message['data'])
    query = data.get('username', '')
    users = User.objects.filter(username__icontains=query)
    users = [{'id': u.id, 'username': u.username} for u in users if not u.username == str(u.get_anonymous())]
    Group("user-%s" % message.user.pk).send(create_event('users.autocomplete', {'query': query, 'users': users}))