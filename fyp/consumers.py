import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PinConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pin_id = self.scope['url_route']['kwargs']['pin_id']
        self.room_group_name = f'pin_{self.pin_id}'

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

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        pin_state = data['state']

        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'pin_state_update',
                'state': pin_state
            }
        )

    # Receive message from room group
    async def pin_state_update(self, event):
        pin_state = event['state']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'state': pin_state
        }))
