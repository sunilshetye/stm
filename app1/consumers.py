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

    async def disconnect(self, close_code):
        print(f'disconnect: group_name={self.user_group_name}')
        # Leave user group
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to user group
        message_type = text_data_json['message_type']
        if message_type == 'announcement_add':
            send_message = {
                'message_type': text_data_json['message_type'],
                'announcement': text_data_json['announcement'],
                'announcement_teacher': text_data_json['announcement_teacher'],
                'announcement_message': text_data_json['announcement_message'],
                'announcement_timestamp': text_data_json['announcement_timestamp'],
            }
        elif message_type == 'acknowledgement':
            send_message = {
                'message_type': text_data_json['message_type'],
                'announcement': text_data_json['announcement'],
                'student': text_data_json['student'],
                'student_name': text_data_json['student_name'],
                'acknowledgement': text_data_json['acknowledgement'],
            }
        else:
            send_message = {
                'message_type': text_data_json['message_type'],
            }
        await self.channel_layer.group_send(self.user_group_name, send_message)

    # Receive message from user group
    async def announcement_message(self, event):
        message_type = event['message_type']
        if message_type == 'announcement_add':
            send_message = {
                'message_type': event['message_type'],
                'announcement': event['announcement'],
                'announcement_teacher': event['announcement_teacher'],
                'announcement_message': event['announcement_message'],
                'announcement_timestamp': event['announcement_timestamp'],
            }
        elif message_type == 'acknowledgement':
            send_message = {
                'message_type': event['message_type'],
                'announcement': event['announcement'],
                'student': event['student'],
                'student_name': event['student_name'],
                'acknowledgement': event['acknowledgement'],
            }
        else:
            send_message = {
                'message_type': event['message_type'],
            }

        # Send message to WebSocket
        await self.send(text_data=json.dumps(send_message))
