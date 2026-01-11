from django.urls import re_path
from .consumers import SheetConsumer

websocket_urlpatterns = [
    # re_path(r'^ws/sheet/$', SheetConsumer.as_asgi()),
    re_path(r"ws/sheet/(?P<club_id>\d+)/$", SheetConsumer.as_asgi()),
]
