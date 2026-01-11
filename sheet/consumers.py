import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SheetCell


class SheetConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print("WS CONNECTED")

    async def disconnect(self, close_code):
        print("WS DISCONNECTED")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("WS DATA:", data)

        if data.get("type") == "cell_update":
            await self.save_cell(
                row=data["row"],
                col=data["col"],
                value=data["value"],
                color=data.get("color", "")
            )

    @database_sync_to_async
    def save_cell(self, row, col, value, color=""):
        SheetCell.objects.update_or_create(
            row=row,
            col=col,
            defaults={
                "value": value or "",
                "color": color
            }
        )




# class SheetConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room = "sheet"
#         await self.channel_layer.group_add(self.room, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         if data['type'] == 'cell_edit':
#             await self.save_cell(data)

#         await self.channel_layer.group_send(
#             self.room,
#             {
#                 "type": "broadcast",
#                 "data": data
#             }
#         )

#     async def broadcast(self, event):
#         await self.send(text_data=json.dumps(event['data']))

#     @sync_to_async
#     def save_cell(self, data):
#         Cell.objects.update_or_create(
#             row=int(data['row']),
#             col=int(data['col']),
#             defaults={
#                 'value': data.get('value', ''),
#                 'bg_color': data.get('bgColor', '')
#             }
#         )
