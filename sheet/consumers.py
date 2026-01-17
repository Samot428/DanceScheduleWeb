import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
from channels.db import database_sync_to_async 
from .models import SheetCell
from main.models import Group 

class SheetConsumer(AsyncWebsocketConsumer): 
    async def connect(self): 
        self.club_id = self.scope["url_route"]["kwargs"]["club_id"] 
        await self.accept() 
    async def receive(self, text_data): 
        data = json.loads(text_data) 
        
        if data.get("type") == "cell_update": 
            await self.save_cell( 
                club_id=self.club_id, group_name=data["group"], row=data["row"], col=data["col"], value=data.get("value", ""), color=data.get("color", "") 
                ) 
                
    @database_sync_to_async 
    def save_cell(self, club_id, group_name, row, col, value, color): 
        group = Group.objects.get(name=group_name, club_id=club_id)
        SheetCell.objects.update_or_create( 
            club_id=club_id, group=group, row=row, col=col, defaults={ "value": value, "color": color } 
            )