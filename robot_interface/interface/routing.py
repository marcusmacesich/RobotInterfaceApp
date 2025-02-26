# interface/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/robot/(?P<robot_id>\w+)/$', consumers.RobotConsumer.as_asgi()),
]
