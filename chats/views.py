from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    list/retrieve/create/update conversations.
    Only returns conversations the requesting user is in.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # restrict to conversations the user participates in
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Save the conversation and ensure the creator is a participant
        convo = serializer.save()
        convo.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """
    list/retrieve/create messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally filter by conversation via ?conversation=<id>
        qs = Message.objects.filter(conversation__participants=self.request.user)
        convo_id = self.request.query_params.get('conversation')
        if convo_id:
            qs = qs.filter(conversation_id=convo_id)
        return qs

    def perform_create(self, serializer):
        # Always set the sender to the logged-in user
        serializer.save(sender=self.request.user)
