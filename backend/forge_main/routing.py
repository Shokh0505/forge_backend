from django.urls import re_path
from .consumers import ChatConsumer, ChatDjangoConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<target_user_id>\d+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chatSocket/?$', ChatDjangoConsumer.as_asgi())
]