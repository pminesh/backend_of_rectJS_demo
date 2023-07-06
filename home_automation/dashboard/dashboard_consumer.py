import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

live_users = []

class UserDashConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_type = self.scope['url_route']['kwargs']['user_type']

        # self.user_group = 'user_%s' % self.user_id
        self.user_group = f'user_{self.user_id}_{self.user_type}'

        print(self.user_id, self.user_group)

        # Join room groupa
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        await self.accept()
        if self.user_group not in live_users:
            live_users.append({"user_id" : self.user_id, "user_type": self.user_type, "user_group" : self.user_group})
            print(f"Connected Users Are : {str(live_users)}")

        await self.channel_layer.group_send(self.user_group, {
            'type': 'card_config',
            'response': "user_dashboard(self.user_id)",
        })

        await self.channel_layer.group_send(self.user_group, {
            'type': 'cards_type_config',
            'response': "card_opr.card_types()",
        })

        await self.channel_layer.group_send(self.user_group, {
            'type': 'site_config',
            'response': "user_site_config(self.user_id, self.role_id, self.user_type)",
        })

    async def disconnect(self, close_code):
        print('User Disconnecting...')
        self.channel_layer.group_discard(self.user_group, self.channel_name)
        for user in live_users:
            if self.user_group in user['user_group']:
                live_users.remove(user)
                print(f"Disconnectin User : {self.user_group}")
                print(f"Now Connected Users Are : {str(live_users)}")

    async def receive(self, text_data):
        print(text_data)
        """
        Receive message from WebSocket.
        Get the event and send the appropriate event
        """
        response = json.loads(text_data)
        print(response)

    async def card_config(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "status_code": 200,
            "payload": res,
        }))
    
    async def site_config(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "status_code": 200,
            "payload": res,
        }))

    async def cards_type_config(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "status_code": 200,
            "payload": res,
        }))

    async def device_json(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "status_code": 200,
            "payload": res,
        }))

    async def dataSender(self, data):
        print("++++++++++++")
        self.channel_layer.group_send(self.user_group, {
            'type': 'send_message',
            'response': data,
        })