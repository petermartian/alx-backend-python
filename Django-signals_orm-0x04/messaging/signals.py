from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

from django.db.models.signals import pre_save
from .models import Message, MessageHistory

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.id is None:
        return  # New message, skip

    try:
        original = Message.objects.get(pk=instance.id)
    except Message.DoesNotExist:
        return

    if original.content != instance.content:
        # Save history
        MessageHistory.objects.create(message=instance, old_content=original.content)
        instance.edited = True

