import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SheetCell

class SheetConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.club_id = self.scope["url_route"]["kwargs"]["club_id"]
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "cell_update":
            await self.save_cell(
                club_id=self.club_id,
                row=data["row"],
                col=data["col"],
                value=data["value"],
                color=data.get("color", "")
            )

    @database_sync_to_async
    def save_cell(self, club_id, row, col, value, color):
        SheetCell.objects.update_or_create(
            club_id=club_id,
            row=row,
            col=col,
            defaults={
                "value": value or "",
                "color": color
            }
        )


# class SheetConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.accept()
#         print("WS CONNECTED")

#     async def disconnect(self, close_code):
#         print("WS DISCONNECTED")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         print("WS DATA:", data)

#         if data.get("type") == "cell_update":
#             await self.save_cell(
#                 row=data["row"],
#                 col=data["col"],
#                 value=data["value"],
#                 color=data.get("color", "")
#             )

#     @database_sync_to_async
#     def save_cell(self, row, col, value, color=""):
#         SheetCell.objects.update_or_create(
#             row=row,
#             col=col,
#             defaults={
#                 "value": value or "",
#                 "color": color
#             }
#         )