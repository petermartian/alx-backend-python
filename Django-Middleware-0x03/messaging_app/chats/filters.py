import django_filters as filters
from .models import Message, Conversation

class MessageFilter(filters.FilterSet):
    """
    Supports:
    - conversation: /api/messages/?conversation=1
    - sender:       /api/messages/?sender=2
    - participant:  /api/messages/?participant=2 (participant in the conversation)
    - created_at (range): /api/messages/?created_at_after=2025-08-10T00:00:00Z&created_at_before=2025-08-12T00:00:00Z
    """
    created_at = filters.IsoDateTimeFromToRangeFilter()
    conversation = filters.NumberFilter(field_name="conversation_id")
    sender = filters.NumberFilter(field_name="sender_id")
    participant = filters.NumberFilter(method="filter_participant")

    def filter_participant(self, queryset, name, value):
        return queryset.filter(conversation__participants__id=value)

    class Meta:
        model = Message
        fields = ["conversation", "sender", "created_at"]

class ConversationFilter(filters.FilterSet):
    """
    Filter conversations by participant and title:
    - participant: /api/conversations/?participant=2
    - title search via ?search= handled by SearchFilter (icontains)
    """
    participant = filters.NumberFilter(method="filter_participant")

    def filter_participant(self, queryset, name, value):
        return queryset.filter(participants__id=value)

    class Meta:
        model = Conversation
        fields = []
