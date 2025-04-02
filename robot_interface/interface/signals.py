# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Program

@receiver(pre_save, sender=Program)
def store_old_status(sender, instance, **kwargs):
    if instance.pk:
        # Fetch the current record from the database before saving changes.
        old_instance = Program.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    else:
        instance._old_status = None

@receiver(post_save, sender=Program)
def send_program_to_robot(sender, instance, created, **kwargs):
    # Determine if we should send the program:
    #   - Always send on creation if status is "Waiting".
    #   - On update, send if the status changed to "Waiting".
    if instance.status == 'Waiting' and (created or instance._old_status != 'Waiting'):
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