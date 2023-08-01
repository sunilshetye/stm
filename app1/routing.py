from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/announcement/(?P<user_name>\w+)/$', consumers.AnnouncementConsumer.as_asgi()),
]
