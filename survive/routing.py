from django.urls import re_path

from survive import consumers

websocket_urlpatterns = [
    re_path(r"ws/live_draft/(?P<season_id>\w+)/$", consumers.DraftConsumer.as_asgi())
]
