# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    re_path(r'ws/mark-question/(?P<room_name>\w+)/$', consumers.QuestionConsumer),
    re_path(r'ws/video-signal/(?P<room_name>\w+)/$', consumers.VideoConsumer),
    re_path(r'ws/log/(?P<room_name>\w+)/$', consumers.LogsConsumer),
    re_path(r'ws/test/(?P<room_name>\w+)/$', consumers.TestConsumer),
    # re_path(r'ws/consume/(?P<room_name>\w+)/$', consumers.TheConsumer),
]
