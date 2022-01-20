import json
from datetime import datetime
from asgiref.sync import async_to_sync
#from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

# For use synchronous functions can used:
#asgiref.sync.sync_to_async
#channels.db.database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # name of method
                'message': message,
                'prefix_date': f'{datetime.now()}',
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = f"{event['prefix_date']}: {event['message']}"

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))