from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from gpio.models import Pins
from .models import Energy

@receiver(post_save, sender=Notification)
def create_notification_signal(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        
        # Envoi de la notification via un WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",  # Chaque utilisateur pourrait avoir son propre canal websocket
            {
                "type": "send_notification",
                "message": instance.message,
                "notification_type": instance.type,
            }
        )

@receiver(post_save, sender=Pins)
def calculate_energy(sender, instance, **kwargs):
    
    if instance.last_off and instance.last_on:
        duration = instance.last_off - instance.last_on
        hours = duration.total_seconds() / 3600  
        energy_consumed = instance.power * hours          
        
        Energy.objects.create(
            pin=instance,
            date=instance.last_off.date(),
            temps=duration
        )
