from django.urls import re_path

def get_websocket_urlpatterns():
    from .consumers import SheetConsumer
    return [
        re_path(r"ws/sheet/(?P<club_id>\d+)/$", SheetConsumer.as_asgi()),
    ]

# nechaj prázdne, aby sa import nespustil pri načítaní modulu
websocket_urlpatterns = []
