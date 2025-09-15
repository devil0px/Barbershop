from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<booking_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/barbershop/(?P<shop_id>\d+)/$", consumers.BarbershopTurnConsumer.as_asgi()),
]
