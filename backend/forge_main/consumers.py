from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from datetime import datetime, timezone
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from .models import User, Chat, Message
import json

chat_memory = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.target_user_id = self.scope["url_route"]["kwargs"]["target_user_id"]

        if not self.user.is_authenticated:
            await self.close()
            return
        
        ids = sorted([str(self.user.id), str(self.target_user_id)])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        ids = sorted([str(self.user.id), str(self.target_user_id)])
        room_name = f"chat_{ids[0]}_{ids[1]}"
        await self.channel_layer.group_discard(room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        # Get the chat and save it to db
        chat = await self.get_or_create_chat(self.user, self.target_user_id)
        await self.save_message(chat, self.user, message)

        now = datetime.now(timezone.utc)
        formatted = now.isoformat()

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_name, 
            {
                "type": "chat_message",
                "message": message,
                "from": self.user.id,
                "sent_at": formatted
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "from": event["from"]
        }))

    @database_sync_to_async
    def get_or_create_chat(self, user1, user2ID):
        ids = sorted([user1.id, int(user2ID)])
        chat, _ = Chat.objects.get_or_create(
            user1_id=ids[0],
            user2_id=ids[1],
        )

        return chat
    
    @database_sync_to_async
    def save_message(self, chat, sender, message):
        Message.objects.create(chat=chat, sender=sender, message=message)

class ChatDjangoConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'chat'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()



    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'message': event['message']
        }))