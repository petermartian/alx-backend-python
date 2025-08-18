from .models import Conversation, Message
from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users who are participants of the conversation.
    - Checks authentication in `has_permission`.
    - Ensures object-level access for Conversation or Message only if the user is a participant.
    - Explicitly handles unsafe methods (POST, PUT, PATCH, DELETE).
    """
    message = "Only participants can access this resource."

    def has_permission(self, request, view):
        """Ensure the user is authenticated."""
        return bool(request.user and request.user.is_authenticated)

    def _is_participant(self, user, obj):
        """Helper method to check if the user is a participant."""
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=user.id).exists()
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(id=user.id).exists()
        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permission based on request method."""
        # Allow safe methods (GET, HEAD, OPTIONS) for participants
        if request.method in permissions.SAFE_METHODS:
            return self._is_participant(request.user, obj)

        # Allow unsafe methods (POST, PUT, PATCH, DELETE) only for participants
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return self._is_participant(request.user, obj)

        return False
