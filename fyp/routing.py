from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pins/(?P<pin_id>\d+)/$', consumers.PinConsumer.as_asgi()),
]
