"""
ASGI config for DANCE_CALENDAR_WEB project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import sheet.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DANCE_CALENDAR_WEB.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(   # 👈 DÔLEŽITÉ
        URLRouter(
            sheet.routing.websocket_urlpatterns
        )
    ),
})

