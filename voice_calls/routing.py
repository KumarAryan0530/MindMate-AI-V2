from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/media-stream/(?P<schedule_id>\d+)/$', consumers.MediaStreamConsumer.as_asgi()),
]
