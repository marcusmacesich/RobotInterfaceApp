# robot_interface/robot_interface/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import interface.routing  # Import the app-level routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        interface.routing.websocket_urlpatterns
    ),
})
