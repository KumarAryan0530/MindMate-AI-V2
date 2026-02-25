"""
ASGI config for perplex project with WebSocket support.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perplex.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing after Django is set up
from voice_calls import routing

# Note: We don't use AllowedHostsOriginValidator or AuthMiddlewareStack here because:
# 1. Twilio Media Streams connects from Twilio's servers (not a browser)
# 2. The WebSocket connection is server-to-server, so origin validation would block it
# 3. Twilio connections aren't authenticated Django users - they use Twilio's own auth
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})
