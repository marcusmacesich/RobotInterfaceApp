# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RobotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.robot_id = self.scope['url_route']['kwargs']['robot_id']
        self.group_name = f"robot_{self.robot_id}"
        
        # Add this connection to the robot's group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove this connection from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    # This handler is triggered by messages sent to the group
    async def new_program(self, event):
        # event should include the program details
        program_id = event['program_id']
        code = event['code']
        
        # Send the code to the robot
        await self.send(text_data=json.dumps({
            'program_id': program_id,
            'code': code,
        }))
