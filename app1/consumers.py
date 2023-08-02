import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AnnouncementConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.user_group_name = f'announcement_{self.user_name}'
        print(f'connect: group_name={self.user_group_name}')

        # Join user group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()

        # Send message to user group
        message = 'Connected'
        send_message = {
            'type': 'announcement.message',
            'message': message
        }
        await self.channel_layer.group_send(self.user_group_name, send_message)

    async def disconnect(self, close_code):
        print(f'disconnect: group_name={self.user_group_name}')
        # Leave user group
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(f'receive: group_name={self.user_group_name}')
        text_data_json = json.loads(text_data)

        # Send message to user group
        message = text_data_json['message']
        send_message = {
            'type': 'announcement.message',
            'message': message
        }
        await self.channel_layer.group_send(self.user_group_name, send_message)

    # Receive message from user group
    async def announcement_message(self, event):
        print(f'announcement_message: group_name={self.user_group_name}')
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({'message': message}))