from django.contrib import admin

# Register your models here.
from .models import Conversation, Message
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    filter_horizontal = ("participants",)
    ordering = ("-created_at",)
