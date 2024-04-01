import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class DraftConsumer(WebsocketConsumer):
    def connect(self):
        self.season_id = self.scope["url_route"]["kwargs"]["season_id"]
        self.season_group_id = f"draft_{self.season_id}"

        # Join season group
        async_to_sync(self.channel_layer.group_add)(
            self.season_group_id, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave season group
        async_to_sync(self.channel_layer.group_discard)(
            self.season_group_id, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to season group
        async_to_sync(self.channel_layer.group_send)(
            self.season_group_id, {"type": "draft.message", "message": message}
        )

    # Receive message from season group
    def draft_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))