from django.conf import settings
from django.db import models


class Conversation(models.Model):
    title = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Conversation #{self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="messages_sent", on_delete=models.CASCADE
    )
    content = models.TextField(blank=True)  # allow empty string; null=False by default
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        content = (self.content or "").strip()
        if not content:
            preview = "[empty]"
        else:
            preview = content[:30] + ("..." if len(content) > 30 else "")
        return f"{self.sender} → {self.conversation_id}: {preview}"
