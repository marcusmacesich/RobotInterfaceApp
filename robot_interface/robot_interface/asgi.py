import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robot_interface.settings")

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
import robot_interface.routing  # This is your project-level routing



application = robot_interface.routing.application
