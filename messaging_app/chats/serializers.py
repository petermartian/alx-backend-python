from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
        ]


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.UUIDField(read_only=True)
    # Explicit CharField so we can validate it
    message_body = serializers.CharField()
    sent_at     = serializers.DateTimeField(read_only=True)
    sender      = UserSerializer(read_only=True)
    sender_id   = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'sender_id',
            'message_body',
            'sent_at',
        ]

    def validate_message_body(self, value):
        """
        Ensure the body isn’t just whitespace.
        """
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    conversation_id   = serializers.UUIDField(read_only=True)
    conversation_name = serializers.CharField()
    participants      = UserSerializer(many=True, read_only=True)
    participant_ids   = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='participants',
        write_only=True
    )
    created_at        = serializers.DateTimeField(read_only=True)
    messages          = MessageSerializer(many=True, read_only=True)
    # SerializerMethodField to include an extra nested statistic
    message_count     = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'conversation_name',
            'participants',
            'participant_ids',
            'created_at',
            'messages',
            'message_count',
        ]

    def get_message_count(self, obj):
        return obj.messages.count()
