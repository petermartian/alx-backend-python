from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager



class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'content', 'timestamp')


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_messages')
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    read = models.BooleanField(default=False)

    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom unread message manager

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edit_histories')

    def __str__(self):
        return f"History for Message {self.message.id}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} on message {self.message.id}"


# Optional utility for threaded replies
def get_all_replies(message):
    replies = []
    def recurse(msg):
        children = msg.replies.all()
        for child in children:
            replies.append(child)
            recurse(child)
    recurse(message)
    return replies
