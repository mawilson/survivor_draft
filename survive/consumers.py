import json

from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore[import-untyped]

class DraftConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.season_id = self.scope["url_route"]["kwargs"]["season_id"]
        self.season_group_id = f"draft_{self.season_id}"

        # Join season group
        await self.channel_layer.group_add(self.season_group_id, self.channel_name)

        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave season group
        await self.channel_layer.group_discard(self.season_group_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to season group
        await self.channel_layer.group_send(
            self.season_group_id, {"type": "draft.message", "message": message}
        )

    async def draft_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))