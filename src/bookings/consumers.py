import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Booking, BookingMessage
from accounts.models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'chat_{self.booking_id}'
        self.user = self.scope['user']

        # Authenticate and authorize user
        if self.user.is_anonymous:
            await self.close()
            return

        is_authorized = await self.check_authorization(self.booking_id, self.user)
        if not is_authorized:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        new_msg = await self.save_message(self.booking_id, self.user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_username': self.user.username,
                'created_at': new_msg.created_at.strftime('%d/%m/%Y %H:%M')
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_username = event['sender_username']
        created_at = event['created_at']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'created_at': created_at
        }))

    @database_sync_to_async
    def check_authorization(self, booking_id, user):
        try:
            booking = Booking.objects.get(pk=booking_id)
            return user == booking.customer or user == booking.barbershop.owner
        except Booking.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, booking_id, sender, message):
        booking = Booking.objects.get(pk=booking_id)
        new_message = BookingMessage.objects.create(booking=booking, sender=sender, message=message)
        
        # إرسال إشعار للطرف الآخر
        from notifications.utils import create_chat_notification
        create_chat_notification(new_message)
        
        return new_message


class BarbershopTurnConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.shop_id = self.scope['url_route']['kwargs']['shop_id']
        self.room_group_name = f'barbershop_{self.shop_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This consumer is for server push only, ignore client messages
        pass

    async def booking_turn_update(self, event):
        # Send the turn update to WebSocket
        await self.send(text_data=json.dumps({
            'current_turn_number': event.get('current_turn_number'),
            'finished_bookings_count': event.get('finished_bookings_count')
        }))
