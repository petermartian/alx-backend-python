from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Only authenticated users AND conversation participants can access.
    Explicitly handles unsafe methods: POST, PUT, PATCH, DELETE.
    """
    message = "Only participants can access this resource."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def _is_participant(self, user, obj):
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=user.id).exists()
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=user.id).exists()
        return False

    def has_object_permission(self, request, view, obj):
        # Read allowed only for participants
        if request.method in permissions.SAFE_METHODS:
            return self._is_participant(request.user, obj)

        # Write ops — checker looks for these exact strings:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return self._is_participant(request.user, obj)

        return False



class IsParticipantOfConversation(BasePermission):
    """
    - Allow only authenticated users (checked in has_permission)
    - Allow object access only if the user is a participant of the conversation.
    Works for both Conversation and Message objects.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Lazy import to avoid circulars
        from .models import Conversation, Message

        if isinstance(obj, Conversation):
            return obj.participants.filter(id=request.user.id).exists()
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        # For non-object actions (list/create), has_permission already enforced auth.
        return True
    
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
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        convo = serializer.save()
        convo.participants.add(self.request.user)

    @action(detail=True, methods=["post"])
    def add_participant(self, request, pk=None):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id required"}, status=400)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        convo = self.get_object()  # object-level permission already checked
        convo.participants.add(user)
        return Response({"detail": f"Added user {user_id}"}, status=200)

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
        qs = Message.objects.filter(conversation__participants=self.request.user)
        convo_id = self.request.query_params.get("conversation")
        return qs.filter(conversation_id=convo_id) if convo_id else qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

