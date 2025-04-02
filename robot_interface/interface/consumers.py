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

    async def receive(self, text_data):
        """
        This method is called when a message is received on this WebSocket connection.
        We assume that messages sent from the robot script include an "output" key.
        """
        try:
            data = json.loads(text_data)
            output = data.get("output")
            if output:
                # Broadcast this output to the group so all connected clients get it.
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'execution_output',
                        'output': output,
                    }
                )
        except Exception as e:
            print("Error in receive:", e)
    
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

    async def execution_output(self, event):
        # Handler for execution output messages
        output = event['output']
        await self.send(text_data=json.dumps({
            'output': output,
        }))