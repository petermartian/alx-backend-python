from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


# Create notification when a new message is sent
@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


# Save message history before edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.id is None:
        return  # New message, skip

    try:
        original = Message.objects.get(pk=instance.id)
    except Message.DoesNotExist:
        return

    if original.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=original.content,
            edited_by=instance.edited_by  # save who edited it
        )
        instance.edited = True


# Delete user-related data when a user is deleted
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(edited_by=instance).delete()
