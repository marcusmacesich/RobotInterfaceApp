# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Program

@receiver(post_save, sender=Program)
def send_program_to_robot(sender, instance, created, **kwargs):
    # Only send if a new program is created and it is waiting to be run
    if created and instance.status == 'Waiting':
        channel_layer = get_channel_layer()
        group_name = f"robot_{instance.robot.id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "new_program",  # This calls the new_program() handler in the consumer.
                "program_id": instance.id,
                "code": instance.code,
            }
        )
