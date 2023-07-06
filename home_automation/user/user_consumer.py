import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from home_automation.user.views import UserRegistration, UserListing

class UserConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "user",
            self.channel_name
        )

        await self.accept()
        s = "UserListing()"#pass data here
        
        await self.channel_layer.group_send("user", {
            'type': 'user_config',
            'response': s,
            'message':None
        })

    async def disconnect(self, close_code):
        logging.info('User Disconnecting...')
        self.channel_layer.group_discard("auth", self.channel_name)

    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Get the event and send the appropriate event
        """
        response = json.loads(text_data)

        # if response['opr_type'] == 'user':
        #     if response['opr'] == 'get':
        #         s = UserListing()
        #         await self.channel_layer.group_send("user", {
        #            'type': 'user_config',
        #            'response': s,
        #            'message':None
        #         }) 

        #     if response['opr'] == 'add':
        #         msg = UserRegistration(data=response['data'])
        #         s = UserListing()
        #         await self.channel_layer.group_send("user", {
        #             'type': 'user_config',
        #             'response': s,
        #             'message':msg
        #         })

            # if response['opr'] == 'del':
            #     userDelete(id=response["did"])
            #     s = userListing()
            #     await self.channel_layer.group_send("user", {
            #         'type': 'user_config',
            #         'response': s,
            #     })

            # if response['opr'] == 'update':
            #     updateUser(data=response["data"])
            #     s = userListing()
            #     await self.channel_layer.group_send("user", {
            #         'type': 'user_config',
            #         'response': s,
            #     })

    async def user_config(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "status_code": 200,
            "payload": res,
        })) 

    async def dataSender(self, data):
        logging.info("++++++++++++")
        self.channel_layer.group_send("user", {
            'type': 'send_message',
            'response': data,
        })

