from rest_framework import serializers
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "title", "participants", "created_at", "updated_at", "last_message"]

    def get_last_message(self, obj):
        m = obj.messages.order_by("-created_at").first()
        return None if not m else {
            "id": m.id,
            "sender": m.sender_id,
            "content": m.content,
            "created_at": m.created_at,
        }


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "content", "created_at", "edited_at"]

    def validate(self, attrs):
        request = self.context["request"]
        conv = attrs.get("conversation")
        if conv and not conv.participants.filter(id=request.user.id).exists():
            raise serializers.ValidationError("You are not a participant of this conversation.")
        return attrs
