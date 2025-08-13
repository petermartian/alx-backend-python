from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import ConversationFilter, MessageFilter
from .pagination import MessagesPagination

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """Return conversations where the requesting user is a participant."""
        return Conversation.objects.filter(participants=self.request.user).select_related('participants')

    def perform_create(self, serializer):
        """Create a new conversation and add the requesting user as a participant."""
        convo = serializer.save()
        convo.participants.add(self.request.user)

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation.
        POST /api/conversations/<id>/add_participant/ { "user_id": 2 }
        """
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        convo = self.get_object()
        convo.participants.add(user)
        return Response({"detail": f"Added user {user_id}"}, status=status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagesPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["content"]
    ordering_fields = ["created_at", "edited_at", "id"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return messages for conversations where the requesting user is a participant."""
        qs = Message.objects.filter(conversation__participants=self.request.user).select_related('conversation__participants', 'sender')
        convo_id = self.request.query_params.get("conversation")
        return qs.filter(conversation_id=convo_id) if convo_id else qs

    def perform_create(self, serializer):
        """Create a new message and set the sender to the requesting user."""
        serializer.save(sender=self.request.user)