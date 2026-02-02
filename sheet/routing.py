from django.urls import path

def get_websocket_urlpatterns():
    from .consumers import SheetConsumer
    return [
        path("ws/sheet/<int:club_id>/", SheetConsumer.as_asgi()),
    ]

# NEVOLAŤ FUNKCIU TU ❗
websocket_urlpatterns = []   # prázdne, aby sa to nespustilo pri importe
