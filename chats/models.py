from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(
        'User',
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        # Be careful: this will hit the database each time __str__ is called
        return ", ".join(u.username for u in self.participants.all())


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
