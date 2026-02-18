# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class WhiteboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"whiteboard_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Broadcast draw or clear to entire group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "whiteboard_message",
                "data": data
            }
        )

    async def whiteboard_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))


# Notification Consumer (No Change Needed)
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.user_group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "meeting_invite",
            "room_name": event["room_name"]
        }))